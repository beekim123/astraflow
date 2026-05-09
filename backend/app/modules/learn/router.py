from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.core.responses import success
from app.db.session import get_session
from app.modules.identity.models import User
from app.modules.learn import service

learn_router = APIRouter(prefix="/api/learn", tags=["learn"])


@learn_router.get("/getInfo")
async def getInfo(current_user: User = Depends(get_current_user)):
    return success((await service.getInfo(current_user)).model_dump())


@learn_router.get("/getInfoFromDb")
async def getInfoFromDb(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return success((await service.getInfoFromDb(session, current_user.id)).model_dump())
