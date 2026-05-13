from collections.abc import AsyncIterator

from app.ai.contracts.client import AgentClient
from app.ai.contracts.schemas import AgentRequest, AgentResult


class MockAgentClient(AgentClient):
    async def run(self, request: AgentRequest) -> AgentResult:
        return AgentResult(
            task_type=request.task_type,
            status="mocked",
            summary="第一阶段 Mock AI 结果，后续会替换为 ai-gateway / MCP 调用。",
            data={"echo": request.payload},
        )

    async def stream(self, request: AgentRequest) -> AsyncIterator[dict]:
        result = await self.run(request)
        yield {"type": "answer_delta", "content": result.summary, "data": {}}
        yield {"type": "_result", "result": result}
