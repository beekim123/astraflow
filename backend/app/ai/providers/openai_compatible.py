from collections.abc import AsyncIterator
from typing import Any
import json

import httpx

from app.ai.contracts.schemas import AgentRequest, AgentResult, AgentStreamChunk
from app.ai.providers.base import AiProvider
from app.core.config import settings


class OpenAICompatibleProvider(AiProvider):
    provider_name = "openai-compatible"

    async def run(self, request: AgentRequest, prompt: str) -> AgentResult:
        # 非流式调用，保留给普通接口或测试使用；聊天主流程主要走 stream。
        # effective_llm_* 会优先读通用 LLM 配置，也兼容你现在的 ARK_* 配置。
        base_url = settings.effective_llm_base_url
        api_key = settings.effective_llm_api_key
        if not base_url or not api_key:
            raise RuntimeError("LLM_BASE_URL/LLM_API_KEY or ARK_BASE_URL/ARK_API_KEY is not configured")

        model = request.model or settings.effective_llm_model
        if not model:
            raise RuntimeError("LLM_MODEL or ARK_CHAT_MODEL is not configured")

        text = str(request.payload.get("content") or request.payload.get("text") or "")
        # OpenAI-compatible 接口的核心请求体：model + messages + temperature + max_tokens。
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": text},
            ],
            "temperature": _normalize_temperature(request.temperature),
            "max_tokens": request.max_tokens,
            "stream": False,
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=settings.llm_timeout_seconds) as client:
            # 非流式请求一次性等模型返回完整 JSON。
            response = await client.post(_chat_completions_url(base_url), json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

        content = _extract_content(data)
        reasoning_summary = _extract_reasoning_summary(data)
        usage = data.get("usage") or {}
        return AgentResult(
            task_type=request.task_type,
            status="success",
            summary=content,
            provider=self.provider_name,
            model=model,
            mode=request.mode,
            prompt_version=request.payload.get("prompt_version", "v1"),
            input_tokens=int(usage.get("prompt_tokens") or usage.get("input_tokens") or 0),
            output_tokens=int(usage.get("completion_tokens") or usage.get("output_tokens") or 0),
            estimated_cost=0,
            reasoning_summary=reasoning_summary or "真实模型已根据当前 Prompt、用户输入和路由配置生成回答。",
            process_steps=[
                f"选择 OpenAI-compatible Provider：{self.provider_name}",
                f"调用模型：{model}",
                f"Prompt 场景：{request.prompt_scene}",
                "解析模型返回内容和 token 用量",
            ],
            data={
                "content": content,
                "artifacts": _build_artifacts(request.task_type, content),
                "tool_logs": [{"name": self.provider_name, "status": "success"}],
                "evidence": [],
            },
        )

    async def stream(self, request: AgentRequest, prompt: str) -> AsyncIterator[AgentStreamChunk]:
        # 真实流式调用：兼容 Ark/OpenAI 风格的 /chat/completions 接口。
        # 这里只做“对接外部模型”，不处理业务落库、用户权限、前端 SSE。
        base_url = settings.effective_llm_base_url
        api_key = settings.effective_llm_api_key
        if not base_url or not api_key:
            raise RuntimeError("LLM_BASE_URL/LLM_API_KEY or ARK_BASE_URL/ARK_API_KEY is not configured")

        model = request.model or settings.effective_llm_model
        if not model:
            raise RuntimeError("LLM_MODEL or ARK_CHAT_MODEL is not configured")

        text = str(request.payload.get("content") or request.payload.get("text") or "")
        # system 放业务 Prompt，user 放用户输入；第三阶段 RAG 证据也会被注入到 prompt 中。
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": text},
            ],
            "temperature": _normalize_temperature(request.temperature),
            "max_tokens": request.max_tokens,
            "stream": True,
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=settings.llm_timeout_seconds) as client:
            # client.stream 会让我们边接收模型输出边处理，而不是等完整回复结束。
            async with client.stream("POST", _chat_completions_url(base_url), json=payload, headers=headers) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    # 模型流式响应也是 SSE：data: {...} 多次返回，最后 data: [DONE]。
                    raw = line.strip()
                    if not raw or not raw.startswith("data:"):
                        continue
                    data_line = raw.removeprefix("data:").strip()
                    if data_line == "[DONE]":
                        break
                    try:
                        data = json.loads(data_line)
                    except json.JSONDecodeError:
                        # 有些服务可能夹杂非 JSON 行，跳过即可，不让一次脏数据中断整条流。
                        continue
                    delta = _extract_stream_delta(data)
                    reasoning = _normalize_content(delta.get("reasoning_content") or delta.get("reasoning") or "")
                    content = _normalize_content(delta.get("content") or "")
                    # Provider 只产出统一 chunk，具体怎么展示由 gateway/router/frontend 处理。
                    if reasoning:
                        yield AgentStreamChunk(type="reasoning_delta", content=reasoning)
                    if content:
                        yield AgentStreamChunk(type="answer_delta", content=content)


def _chat_completions_url(base_url: str) -> str:
    # 配置可以写到 /api/v3，也可以直接写完整 /chat/completions，这里统一补齐。
    normalized = base_url.rstrip("/")
    if normalized.endswith("/chat/completions"):
        return normalized
    return f"{normalized}/chat/completions"


def _normalize_temperature(value: int) -> float:
    # 管理台里温度用 70 这种百分制保存，调用模型时要转成 0.7。
    if value > 2:
        return min(value, 200) / 100
    return float(value)


def _extract_content(data: dict[str, Any]) -> str:
    choices = data.get("choices") or []
    if not choices:
        return ""
    message = choices[0].get("message") or {}
    return _normalize_content(message.get("content") or "")


def _extract_reasoning_summary(data: dict[str, Any]) -> str:
    choices = data.get("choices") or []
    if not choices:
        return ""
    message = choices[0].get("message") or {}
    return _normalize_content(message.get("reasoning_content") or message.get("reasoning") or "")


def _extract_stream_delta(data: dict[str, Any]) -> dict[str, Any]:
    # 流式返回一般在 choices[0].delta；少数兼容接口可能放在 message。
    choices = data.get("choices") or []
    if not choices:
        return {}
    choice = choices[0] or {}
    return choice.get("delta") or choice.get("message") or {}


def _normalize_content(content: Any) -> str:
    # 兼容纯字符串和多模态 content 数组两种返回格式。
    if isinstance(content, list):
        return "".join(str(item.get("text", "")) if isinstance(item, dict) else str(item) for item in content)
    return str(content)


def _build_artifacts(task_type: str, content: str) -> list[dict[str, Any]]:
    # 普通聊天只需要消息；文件分析/工单草稿这类任务才额外生成 artifact。
    if task_type == "chat-general":
        return []
    return [
        {
            "artifact_type": "report",
            "title": "AI 生成结果",
            "content_markdown": content,
            "content_json": {"source": "openai-compatible", "task_type": task_type},
        }
    ]
