from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

from app.services.store import store
from app.services.social_recommendation import engine

router = APIRouter()


class SocialRecommendRequest(BaseModel):
    user_id: str
    occasion: str = 'daily'
    limit: int = Field(default=5, ge=1, le=20)


@router.post('/recommend', response_model=dict)
def recommend_social(payload: SocialRecommendRequest):
    user = store.get_or_create_user(payload.user_id)
    body_profile = user.get('body_profile', {})
    result = engine.recommend(
        payload.user_id,
        body_profile,
        payload.occasion,
        payload.limit,
    )
    return result