from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime
from models.place import PlaceCategory

class ReviewResponse(BaseModel):
    id: int
    user_name: str
    rating: int
    comment: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class BestTimeResponse(BaseModel):
    id: int
    day_of_week: int
    hour: int
    score: int
    
    model_config = ConfigDict(from_attributes=True)

class PlaceNearbyResponse(BaseModel):
    id: int
    name: str
    name_ja: Optional[str] = None
    lat: float
    lng: float
    category: PlaceCategory
    rating: float
    distance: int
    has_japanese_support: bool
    is_indoor: bool
    
    model_config = ConfigDict(from_attributes=True)

class PlaceDetailResponse(BaseModel):
    id: int
    name: str
    name_ja: Optional[str] = None
    address: Optional[str] = None
    lat: float
    lng: float
    category: PlaceCategory
    is_indoor: bool
    has_japanese_support: bool
    opening_hours: Optional[Any] = None
    phone: Optional[str] = None
    rating: float
    reviews: List[ReviewResponse]
    best_times: Dict[int, List[BestTimeResponse]]
    
    model_config = ConfigDict(from_attributes=True)
