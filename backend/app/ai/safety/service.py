from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ai_admin.models import ForbiddenWord


@dataclass(frozen=True)
class SafetyResult:
    allowed: bool
    matched_words: list[str]
    action: str = "block"


async def check_text(session: AsyncSession, text: str) -> SafetyResult:
    if not text:
        return SafetyResult(allowed=True, matched_words=[])

    result = await session.execute(select(ForbiddenWord).where(ForbiddenWord.enabled.is_(True)))
    words = list(result.scalars().all())
    lowered = text.lower()
    matched = [item.word for item in words if item.word.lower() in lowered]
    if matched:
        return SafetyResult(allowed=False, matched_words=matched, action="block")
    return SafetyResult(allowed=True, matched_words=[])
