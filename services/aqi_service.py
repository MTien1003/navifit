import httpx
import os
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.aqi_cache import AQICache

AQI_COLOR_MAP = [
  (50,  "Tốt",                    "#00E400"),
  (100, "Trung bình",             "#FFFF00"),
  (150, "Không tốt (nhạy cảm)",  "#FF7E00"),
  (200, "Không tốt",             "#FF0000"),
  (300, "Rất không tốt",         "#8F3F97"),
  (999, "Nguy hiểm",             "#7E0023"),
]

async def get_aqi(lat: float, lng: float, db: AsyncSession) -> dict | None:
  # 1. Kiểm tra cache: tìm record gần (±0.05 độ), fetched_at trong 1 giờ
  one_hour_ago = datetime.utcnow() - timedelta(hours=1)
  cached = await db.execute(
    select(AQICache).where(
      AQICache.lat.between(lat-0.05, lat+0.05),
      AQICache.lng.between(lng-0.05, lng+0.05),
      AQICache.fetched_at >= one_hour_ago
    ).order_by(AQICache.fetched_at.desc()).limit(1)
  )
  row = cached.scalar_one_or_none()
  if row:
    return {"aqi_value": row.aqi_value, "category": row.category,
            "color_code": row.color_code, "fetched_at": row.fetched_at.isoformat()}

  # 2. Gọi IQAir API
  try:
    async with httpx.AsyncClient(timeout=10) as client:
      r = await client.get("https://api.airvisual.com/v2/nearest_city",
        params={"lat": lat, "lon": lng, "key": os.getenv("IQAIR_API_KEY")})
      data = r.json()
    
    if data.get("status") != "success":
      return None
    
    aqi_val = data["data"]["current"]["pollution"]["aqius"]
    
    # Map sang category + color
    category, color = "Không xác định", "#AAAAAA"
    for threshold, cat, clr in AQI_COLOR_MAP:
      if aqi_val <= threshold:
        category, color = cat, clr
        break
    
    # 3. Lưu cache
    cache_entry = AQICache(lat=lat, lng=lng, aqi_value=aqi_val,
                           category=category, color_code=color,
                           fetched_at=datetime.utcnow())
    db.add(cache_entry)
    await db.commit()
    
    return {"aqi_value": aqi_val, "category": category, "color_code": color,
            "fetched_at": datetime.utcnow().isoformat()}
  except Exception as e:
    print(f"Error fetching AQI: {e}")
    return None
