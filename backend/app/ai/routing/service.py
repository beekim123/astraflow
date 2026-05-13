from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.ai_admin.models import ModelRouteRule

HEALTH_RANK = {
    "healthy": 0,
    "unknown": 1,
    "degraded": 2,
    "down": 3,
}


@dataclass(frozen=True)
class RouteDecision:
    # RouteDecision 是“本次请求实际可用的模型候选项”，由数据库配置 ModelRouteRule 转换而来。
    # 用 dataclass 是为了让后续 AI 网关只关心调用参数，不直接依赖 ORM 模型。
    id: str | None
    mode: str
    display_name: str
    provider: str
    model: str
    temperature: int
    max_tokens: int
    priority: int
    fallback_enabled: bool
    health_status: str


async def choose_route(session: AsyncSession, mode: str) -> RouteDecision:
    # 兼容只需要一个模型的旧调用场景；新流式链路使用 choose_route_candidates 支持 fallback。
    candidates = await choose_route_candidates(session, mode)
    if not candidates:
        raise RuntimeError(f"no enabled model route for mode: {mode}")
    return candidates[0]


async def choose_route_candidates(session: AsyncSession, mode: str) -> list[RouteDecision]:
    normalized = mode or "mock"
    # mode 对应聊天页选择的模型模式，例如 mock、real、deep；具体模型来自管理台配置。
    result = await session.execute(
        select(ModelRouteRule).where(ModelRouteRule.mode == normalized, ModelRouteRule.enabled.is_(True))
    )
    rules = list(result.scalars().all())
    if not rules and normalized == "mock":
        # 本地没有配置 mock 时给一个内置兜底，方便开发环境不依赖外部 LLM。
        return [
            RouteDecision(
                id=None,
                mode="mock",
                display_name="开发 Mock",
                provider="mock",
                model="mock-assistant",
                temperature=70,
                max_tokens=2048,
                priority=100,
                fallback_enabled=True,
                health_status="healthy",
            )
        ]

    # 排序规则：健康模型优先，其次 priority 小的优先，再按创建时间稳定排序。
    rules.sort(key=lambda item: (HEALTH_RANK.get(item.health_status, 1), item.priority, item.created_at))
    # 正常情况下过滤掉 down 的模型；如果所有模型都是 down，仍返回它们，让网关给出明确失败日志。
    return [
        RouteDecision(
            id=item.id,
            mode=item.mode,
            display_name=item.display_name or item.model,
            provider=item.provider,
            model=item.model,
            temperature=item.temperature,
            max_tokens=item.max_tokens,
            priority=item.priority,
            fallback_enabled=item.fallback_enabled,
            health_status=item.health_status,
        )
        for item in rules
        if item.health_status != "down"
    ] or [
        RouteDecision(
            id=item.id,
            mode=item.mode,
            display_name=item.display_name or item.model,
            provider=item.provider,
            model=item.model,
            temperature=item.temperature,
            max_tokens=item.max_tokens,
            priority=item.priority,
            fallback_enabled=item.fallback_enabled,
            health_status=item.health_status,
        )
        for item in rules
    ]


async def mark_route_success(session: AsyncSession, route: RouteDecision) -> None:
    # 调用成功后清空失败状态，让后续请求继续优先使用这个模型。
    if not route.id:
        return
    item = await session.get(ModelRouteRule, route.id)
    if item is None:
        return
    item.health_status = "healthy"
    item.failure_count = 0
    item.last_error = ""
    item.last_checked_at = datetime.now(UTC)
    # 这里只 flush，不 commit；提交由外层聊天流程统一完成。
    await session.flush()


async def mark_route_failure(session: AsyncSession, route: RouteDecision, error_message: str) -> None:
    # 调用失败会累计 failure_count，连续失败后标记 down，后续路由会自动降低优先级。
    if not route.id:
        return
    item = await session.get(ModelRouteRule, route.id)
    if item is None:
        return
    item.failure_count += 1
    item.health_status = "down" if item.failure_count >= 3 else "degraded"
    item.last_error = error_message[:2000]
    item.last_checked_at = datetime.now(UTC)
    # 这里只 flush，不 commit；如果后续整个聊天事务回滚，路由状态也会一起回滚。
    await session.flush()
