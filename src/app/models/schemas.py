from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional


class Item(BaseModel):
    user_id: str
    item_id: str
    category: str
    style: Optional[str] = None
    season: Optional[str] = None
    occasion: Optional[str] = None
    color: str
    material: Optional[str] = None
    attributes: Dict[str, Any] = Field(default_factory=dict)
    price: Optional[float] = None


class Relationship(BaseModel):
    user_id: str
    from_item_id: str
    to_item_id: str
    relation_type: str
    score: float = Field(ge=0.0, le=1.0)
    context: Optional[str] = None
    times_worn_together: int = 0
    user_rating: float = Field(ge=0.0, le=5.0, default=0.0)


class OutfitRequest(BaseModel):
    user_id: str
    occasion: str
    datetime: str
    location: Optional[Dict[str, float]] = None
    weather: Optional[Dict[str, Any]] = None
    constraints: Dict[str, Any] = Field(default_factory=dict)


class OutfitItem(BaseModel):
    item_id: Optional[str] = None
    category: str
    name: str
    rationale: str
    risk_flags: List[str] = Field(default_factory=list)
    score: float


class OutfitPlan(BaseModel):
    rank: int
    score: float
    confidence: float
    items: List[OutfitItem]
    rationale: str
    risk_flags: List[str] = Field(default_factory=list)
    alternatives: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    switch_options: List[Dict[str, Any]] = Field(default_factory=list)


class OutfitResponse(BaseModel):
    decision_id: str
    confidence: float
    outfits: List[OutfitPlan]


class ROIRequest(BaseModel):
    user_id: str
    new_item: Dict[str, Any]


class ROIResponse(BaseModel):
    roi_score: float
    recommendation: str
    similarity: Dict[str, Any]
    combination_gap: Dict[str, Any]
    conflicts: List[Dict[str, str]] = Field(default_factory=list)
    suggestions: List[Dict[str, str]] = Field(default_factory=list)


class BodyFeedbackRequest(BaseModel):
    user_id: str
    item_id: str
    fit_feedback: Optional[str] = None
    visual_comfort: Optional[str] = None
    occasion: Optional[str] = None


class BodyProfileRequest(BaseModel):
    user_id: str
    height: Optional[float] = None
    weight: Optional[float] = None
    shoulder_width: Optional[float] = None
    waistline: Optional[float] = None
    leg_type: Optional[str] = None
    body_shape: Optional[str] = None
    fit_preference: Optional[str] = None
    face_shape: Optional[str] = None
    skin_tone: Optional[str] = None


class UpdatedProfile(BaseModel):
    sensitive_areas: List[str] = Field(default_factory=list)
    fit_preference: Dict[str, str] = Field(default_factory=dict)
