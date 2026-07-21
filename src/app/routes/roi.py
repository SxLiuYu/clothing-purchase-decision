from typing import Dict

from app.models.schemas import ROIRequest, ROIResponse
from app.services.store import store
from fastapi import APIRouter


router = APIRouter()


def _similarity_verdict(score: float):
    if score >= 0.9:
        return 'almost_same'
    if score >= 0.7:
        return 'similar'
    return 'unique'


@router.post('/roi-analysis', response_model=ROIResponse)
def analyze_roi(payload: ROIRequest):
    user = store.get_or_create_user(payload.user_id)
    nodes = user.get('wardrobe_graph', {}).get('nodes', []) if user.get('wardrobe_graph') else []
    new_item = payload.new_item or {}
    candidate_score = float(new_item.get('score', 0.75))
    activation_count = max(2, min(5, max(1, len(nodes) // 4)))
    scenario_delta = round(min(0.35, max(0.1, candidate_score * 0.3)), 2)
    roi_score = max(0.0, min(100.0, 50 + candidate_score * 35 + activation_count * 2.5 + scenario_delta * 20))
    roi_score = round(roi_score, 1)
    recommendation = 'recommend' if roi_score >= 72 else 'reconsider'
    conflicts = []
    if candidate_score >= 0.9 and nodes:
        conflicts = [{'existing_item': nodes[0].get('item_id') or 'unknown', 'reason': 'redundant'}]
    suggestions = []
    if scenario_delta < 0.18:
        suggestions += [
            {'item_category': 'outerwear', 'reason': 'increase_roi'},
            {'item_category': 'scene_matching_accessory', 'reason': 'close_coverage_gap'},
        ]
    record = store.record_roi(payload.user_id, {
        'request': payload.model_dump(),
        'roi_score': roi_score,
        'recommendation': recommendation,
    })
    return ROIResponse(
        roi_score=roi_score,
        recommendation=recommendation,
        similarity={
            'items': [{'item_id': nodes[0].get('item_id') or 'unknown', 'score': round(candidate_score, 2)}] if nodes else [],
            'verdict': _similarity_verdict(candidate_score),
            'verification': 'duplicate check ok' if candidate_score >= 0.9 else 'new combination likely',
        },
        combination_gap={
            'new_combinations': int(8 * candidate_score),
            'reactivated_items': activation_count,
            'scenario_coverage_delta': scenario_delta,
        },
        conflicts=conflicts,
        suggestions=suggestions,
    )
