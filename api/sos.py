from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models.sos_channel import SOSChannel

router = APIRouter()

@router.get("/sos/channels")
async def get_sos_channels(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SOSChannel))
    channels = result.scalars().all()
    return [{"id": ch.id, "name": ch.name, "name_ja": ch.name_ja, "phone": ch.phone, "type": ch.type.value} for ch in channels]
