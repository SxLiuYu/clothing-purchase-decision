from typing import Dict, List, Optional

from app.models.schemas import ROIRequest, ROIResponse
from app.services.store import store
from app.services.similarity import engine as similarity_engine
from fastapi import APIRouter


router = APIRouter()

_ATTRIBUTE_KEYS = ['category', 'style', 'season', 'color', 'material']


def _to_attrs(node: Dict) -> Dict:
    """将衣橱节点转换为 similarity_engine 可用的属性字典"""
    attrs = node.get('attributes', {})
    return {k: attrs.get(k) for k in _ATTRIBUTE_KEYS if attrs.get(k)}


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

    # 使用相似度引擎计算 candidate_score
    new_attrs = {k: new_item.get(k) for k in _ATTRIBUTE_KEYS if new_item.get(k)}
    if new_attrs and nodes:
        max_sim = max(similarity_engine.calculate_similarity(new_attrs, _to_attrs(n)) for n in nodes)
        candidate_score = max_sim
    else:
        candidate_score = float(new_item.get('score', 0.75))

    activation_count = max(2, min(5, max(1, len(nodes) // 4)))
    scenario_delta = round(min(0.35, max(0.1, candidate_score * 0.3)), 2)
    roi_score = max(0.0, min(100.0, 50 + candidate_score * 35 + activation_count * 2.5 + scenario_delta * 20))
    roi_score = round(roi_score, 1)
    recommendation = 'recommend' if roi_score >= 72 else 'reconsider'

    conflicts = []
    if nodes:
        for n in nodes:
            sim = similarity_engine.calculate_similarity(new_attrs, _to_attrs(n))
            if sim >= 0.9:
                conflicts.append({'existing_item': n.get('item_id') or 'unknown', 'reason': 'redundant', 'similarity': str(round(sim, 2))})
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

    # 构建相似度信息
    similarity_items = []
    if nodes:
        for n in nodes:
            sim = similarity_engine.calculate_similarity(new_attrs, _to_attrs(n))
            similarity_items.append({'item_id': n.get('item_id') or 'unknown', 'score': round(sim, 2)})
        similarity_items.sort(key=lambda x: -x['score'])

    max_similarity = similarity_items[0]['score'] if similarity_items else 0.0

    return ROIResponse(
        roi_score=roi_score,
        recommendation=recommendation,
        similarity={
            'items': similarity_items[:5],
            'verdict': _similarity_verdict(max_similarity),
            'verification': 'duplicate check ok' if max_similarity >= 0.9 else 'new combination likely',
        },
        combination_gap={
            'new_combinations': int(8 * candidate_score),
            'reactivated_items': activation_count,
            'scenario_coverage_delta': scenario_delta,
        },
        conflicts=conflicts,
        suggestions=suggestions,
    )
