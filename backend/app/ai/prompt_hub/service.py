from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ai_admin.models import PromptTemplate

DEFAULT_PROMPTS = {
    "chat-general": "你是 AstraFlow 企业 AI 工作台助手，请用清晰、简洁、可执行的方式回答用户。",
    "file-analysis": "请分析用户上传的文件，输出摘要、关键字段、风险点和待办事项。",
    "image-analysis": "请分析用户上传的图片，输出图片说明、可见文字、风险点和建议。",
    "ticket-draft": "请根据用户输入生成工单草稿，包含标题、分类、优先级和处理建议。",
}


async def render_prompt(session: AsyncSession, scene: str, variables: dict) -> tuple[str, str]:
    result = await session.execute(
        select(PromptTemplate)
        .where(PromptTemplate.scene == scene, PromptTemplate.enabled.is_(True))
        .order_by(PromptTemplate.created_at.desc())
    )
    template = result.scalars().first()
    content = template.content if template else DEFAULT_PROMPTS.get(scene, DEFAULT_PROMPTS["chat-general"])
    version = template.version if template else "v1"
    for key, value in variables.items():
        content = content.replace("{{" + key + "}}", str(value))
    return content, version
