from app.ai.contracts.schemas import AgentRequest, AgentResult
from app.modules.ai_admin.models import ModelCallLog


def build_model_call_log(
    request: AgentRequest,
    result: AgentResult,
    latency_ms: int,
    request_id: str,
    error_message: str = "",
) -> ModelCallLog:
    return ModelCallLog(
        request_id=request_id,
        user_id=request.user_id,
        conversation_id=request.conversation_id,
        message_id=request.message_id,
        provider=result.provider,
        model=result.model,
        mode=result.mode,
        prompt_scene=request.prompt_scene,
        prompt_version=result.prompt_version,
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
        estimated_cost=result.estimated_cost,
        latency_ms=latency_ms,
        status=result.status,
        error_message=error_message,
        fallback_used=result.fallback_used,
    )
