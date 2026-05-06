from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from services.aqi_service import get_aqi

router = APIRouter()

@router.get("/aqi")
async def get_aqi_endpoint(lat: float, lng: float, db: AsyncSession = Depends(get_db)):
    result = await get_aqi(lat, lng, db)
    if not result:
        raise HTTPException(status_code=404, detail="Không có dữ liệu AQI khu vực này")
    return result
