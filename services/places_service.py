from math import radians, sin, cos, sqrt, atan2
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import Place, Review, BestTime

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371000  # bán kính trái đất (mét)
    dLat = radians(lat2 - lat1)
    dLon = radians(lon2 - lon1)
    a = sin(dLat/2) * sin(dLat/2) + cos(radians(lat1)) * cos(radians(lat2)) * sin(dLon/2) * sin(dLon/2)
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

async def get_nearby_places(db: AsyncSession, lat: float, lng: float, radius: float = 5000, japanese_only: bool = False):
    result = await db.execute(select(Place))
    places = result.scalars().all()

    nearby = []
    for place in places:
        dist = calculate_distance(lat, lng, place.lat, place.lng)
        if dist <= radius:
            place.distance = round(dist)
            nearby.append(place)

    if japanese_only:
        jp_places  = sorted([p for p in nearby if p.has_japanese_support],  key=lambda p: p.distance)
        other_places = sorted([p for p in nearby if not p.has_japanese_support], key=lambda p: p.distance)

        # Bổ sung kết quả khác nếu có ít hơn 3 địa điểm JP
        result_list = []
        for p in jp_places:
            p.is_priority = True
            result_list.append(p)

        if other_places:
            # Chèn separator giữa 2 nhóm
            result_list.append({"is_separator": True, "label": "── Địa điểm khác ──"})
            for p in other_places:
                p.is_priority = False
                result_list.append(p)

        return result_list
    else:
        nearby.sort(key=lambda p: p.distance)
        for p in nearby:
            p.is_priority = False
        return nearby


async def get_place_detail(db: AsyncSession, place_id: int):
    result = await db.execute(select(Place).where(Place.id == place_id))
    place = result.scalar_one_or_none()
    if not place:
        return None
        
    rev_res = await db.execute(
        select(Review)
        .where(Review.place_id == place_id)
        .order_by(Review.created_at.desc())
        .limit(10)
    )
    place.reviews = rev_res.scalars().all()
    
    bt_res = await db.execute(
        select(BestTime)
        .where(BestTime.place_id == place_id)
    )
    best_times_list = bt_res.scalars().all()
    
    grouped_bt = {}
    for bt in best_times_list:
        if bt.day_of_week not in grouped_bt:
            grouped_bt[bt.day_of_week] = []
        grouped_bt[bt.day_of_week].append(bt)
        
    place.best_times = grouped_bt
    return place

async def search_places(db: AsyncSession, q: str, lat: float, lng: float):
    q_lower = f"%{q.lower()}%"
    result = await db.execute(
        select(Place).where(
            (Place.name.ilike(q_lower)) | (Place.address.ilike(q_lower))
        )
    )
    places = result.scalars().all()
    
    for place in places:
        place.distance = round(calculate_distance(lat, lng, place.lat, place.lng))
        
    places.sort(key=lambda p: p.distance)
    return places[:5]
