from fastapi import APIRouter, HTTPException
from app.models.schemas import BodyFeedbackRequest, BodyProfileRequest, UpdatedProfile
from app.services.store import store
from datetime import datetime, timezone

router = APIRouter()


@router.post('/feedback', response_model=dict)
def update_body_profile(payload: BodyFeedbackRequest):
    updated = store.apply_feedback(payload.user_id, payload.model_dump())
    return {
        'decision_id': f"feedback:{payload.user_id}:{payload.item_id}",
        'updated_profile': UpdatedProfile(**updated).model_dump(),
        'note': 'feedback loop marked; more advanced inference requires multimodal model integration',
    }


@router.post('/profile', response_model=dict)
def set_body_profile(payload: BodyProfileRequest):
    updated = store.set_body_profile(payload.user_id, payload.model_dump(exclude_none=True))
    return {
        'decision_id': f"profile:{payload.user_id}:{datetime.now(timezone.utc).isoformat()}",
        'updated_profile': UpdatedProfile(**updated).model_dump(),
        'note': '体态档案已更新，将在下次穿搭推荐中生效',
    }
