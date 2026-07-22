from typing import Dict, List

from app.models.schemas import ROIRequest, ROIResponse
from app.services.store import store
from app.services.combination_calculator import combination_calculator
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


def _extract_wardrobe_items(user: Dict) -> List[Dict]:
    """从用户衣橱图谱提取完整物品列表"""
    nodes = user.get('wardrobe_graph', {}).get('nodes', []) if user.get('wardrobe_graph') else []
    # 从 store.items 回补完整属性
    items = []
    for node in nodes:
        item_id = node.get('item_id')
        item = store.items.get(item_id, {})
        if item:
            items.append(item)
    return items


def _extract_idle_items(user: Dict) -> List[str]:
    """识别衣橱中闲置衣物（本期简化：返回最近未活动的 item_id）"""
    # TODO: 从穿着记录里算闲置，可先简化返回空列表
    return []


def _get_existing_combinations(user: Dict) -> List[tuple]:
    """获取现有搭配组合"""
    # TODO: 从用户组合历史里获取，目前返回空
    return []


def _get_scenario_coverage(user: Dict) -> Dict[str, float]:
    """获取当前场景覆盖率"""
    # TODO: 基于衣橱实际场景分布计算，简化返回默认值
    return {
        'formal': 0.3, 'casual': 0.5, 'sport': 0.2,
        'outdoor': 0.1, 'date': 0.1, 'daily': 0.4
    }


@router.post('/roi-analysis', response_model=ROIResponse)
def analyze_roi(payload: ROIRequest):
    user = store.get_or_create_user(payload.user_id)
    wardrobe_items = _extract_wardrobe_items(user)
    nodes = user.get('wardrobe_graph', {}).get('nodes', []) if user.get('wardrobe_graph') else []
    new_item = payload.new_item or {}

    # 1. 相似度（通过 similarity_engine 计算，后续可接入 CLIP）
    new_attrs = {k: new_item.get(k) for k in _ATTRIBUTE_KEYS if new_item.get(k)}
    similarity_items = []
    conflicts = []
    if new_attrs and nodes:
        for n in nodes:
            sim = similarity_engine.calculate_similarity(new_attrs, _to_attrs(n))
            similarity_items.append({'item_id': n.get('item_id') or 'unknown', 'score': round(sim, 2)})
            if sim >= 0.9:
                conflicts.append({'existing_item': n.get('item_id') or 'unknown', 'reason': 'redundant', 'similarity': str(round(sim, 2))})
        similarity_items.sort(key=lambda x: -x['score'])
        candidate_score = similarity_items[0]['score'] if similarity_items else float(new_item.get('score', 0.75))
    else:
        candidate_score = float(new_item.get('score', 0.75))

    # 2. 调用 CombinationGapCalculator 计算 ROI
    idle_items = _extract_idle_items(user)
    existing_combinations = _get_existing_combinations(user)
    current_coverage = _get_scenario_coverage(user)

    roi_result = combination_calculator.calculate_roi_score(
        new_item=new_item,
        wardrobe_items=wardrobe_items,
        existing_combinations=existing_combinations,
        idle_items=idle_items,
        current_coverage=current_coverage,
    )

    # 3. 生成建议
    suggestions = []
    scenario_coverage = roi_result.get('breakdown', {}).get('scenario_coverage', {}).get('improvement', 0)
    if scenario_coverage < 0.18:
        suggestions.append({'item_category': 'outerwear', 'reason': 'increase_roi'})
        suggestions.append({'item_category': 'scene_matching_accessory', 'reason': 'close_coverage_gap'})

    # 4. 记录与返回
    store.record_roi(payload.user_id, {
        'request': payload.model_dump(),
        'roi_score': roi_result['roi_score'],
        'recommendation': roi_result['recommendation'],
    })

    max_similarity = similarity_items[0]['score'] if similarity_items else 0.0

    return ROIResponse(
        roi_score=roi_result['roi_score'],
        recommendation=roi_result['recommendation'],
        similarity={
            'items': similarity_items[:5],
            'verdict': _similarity_verdict(max_similarity),
            'verification': 'duplicate check ok' if max_similarity >= 0.9 else 'new combination likely',
        },
        combination_gap={
            'new_combinations': roi_result['details']['new_combinations'],
            'reactivated_items': roi_result['breakdown']['old_item_activation']['count'],
            'scenario_coverage_delta': roi_result['breakdown']['scenario_coverage']['improvement'],
        },
        conflicts=conflicts,
        suggestions=suggestions,
    )
