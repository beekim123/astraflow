from app.ai.contracts.schemas import AgentRequest, AgentResult
from app.ai.providers.base import AiProvider


class MockProvider(AiProvider):
    provider_name = "mock"

    async def run(self, request: AgentRequest, prompt: str) -> AgentResult:
        text = str(request.payload.get("content") or request.payload.get("text") or "")
        mode = request.mode or "mock"
        summary = self._summary_for(request.task_type, text)
        return AgentResult(
            task_type=request.task_type,
            status="success",
            summary=summary,
            provider=self.provider_name,
            model="mock-assistant",
            mode=mode,
            prompt_version=request.payload.get("prompt_version", "v1"),
            input_tokens=max(1, len(prompt) // 4),
            output_tokens=max(1, len(summary) // 4),
            estimated_cost=0,
            reasoning_summary="Mock Provider 按任务类型生成演示回复，未调用真实大模型。",
            process_steps=[
                f"识别任务类型：{request.task_type}",
                f"选择模式：{mode}",
                "使用 MockProvider 生成演示结果",
            ],
            data={
                "content": summary,
                "artifacts": [
                    {
                        "artifact_type": "report",
                        "title": "AI 工作台 Mock 分析报告",
                        "content_markdown": f"## Mock 分析结果\n\n{summary}\n\n> 当前为第二阶段 Mock Provider。",
                        "content_json": {"source": "mock", "mode": mode},
                    }
                ],
                "tool_logs": [{"name": "mock-provider", "status": "success"}],
                "evidence": [],
            },
        )

    def _summary_for(self, task_type: str, text: str) -> str:
        if task_type == "image-analysis":
            return "已完成图片理解 Mock：识别到一张业务图片，可提取可见文字、风险点和改进建议。"
        if task_type == "file-analysis":
            return "已完成文件分析 Mock：生成摘要、关键字段、风险点和待办事项。"
        if task_type == "video-task":
            return "已创建视频任务 Mock：返回摘要、关键帧说明和完成状态，不执行真实转码或抽帧。"
        if task_type.endswith("-draft"):
            return "已生成业务草稿 Mock：可作为后续工单、审核或营销模块的预览数据。"
        return f"Mock AI 回复：{text or '请输入问题或上传资料。'}"
