from fastapi import APIRouter, HTTPException
from app.models.schemas import BodyFeedbackRequest, UpdatedProfile
from app.services.store import store

router = APIRouter()


@router.post('/feedback', response_model=dict)
def update_body_profile(payload: BodyFeedbackRequest):
    updated = store.apply_feedback(payload.user_id, payload.dict())
    return {
        'decision_id': f"feedback:{payload.user_id}:{payload.item_id}",
        'updated_profile': UpdatedProfile(**updated).dict(),
        'note': 'feedback loop marked; more advanced inference requires multimodal model integration',
    }
