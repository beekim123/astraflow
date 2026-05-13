from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import forbidden, not_found
from app.modules.chat.models import ChatConversation


async def get_conversation_for_user(session: AsyncSession, conversation_id: str, user_id: str) -> ChatConversation:
    result = await session.execute(select(ChatConversation).where(ChatConversation.id == conversation_id))
    conversation = result.scalar_one_or_none()
    if conversation is None:
        raise not_found("conversation not found")
    if conversation.user_id != user_id:
        raise forbidden("conversation forbidden")
    return conversation
