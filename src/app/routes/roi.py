from typing import Dict, List
from app.models.schemas import ROIRequest, ROIResponse
from app.services.store import store
from app.services.combination_calculator import combination_calculator
from fastapi import APIRouter

router = APIRouter()


def _similarity_verdict(score: float):
    if score >= 0.9:
        return 'almost_same'
    if score >= 0.7:
        return 'similar'
    return 'unique'


def _extract_wardrobe_items(user: Dict) -> List[Dict]:
    """从用户衣橱图谱提取完整物品列表"""
    nodes = user.get('wardrobe_graph', {}).get('nodes', [])
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
    new_item = payload.new_item or {}

    # 1. 相似度（保留原逻辑，后续可接入 CLIP）
    candidate_score = float(new_item.get('score', 0.75))
    similarity_items = []
    conflicts = []
    if wardrobe_items and candidate_score >= 0.9:
        conflicts = [{'existing_item': wardrobe_items[0].get('item_id', 'unknown'), 'reason': 'redundant'}]

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

    return ROIResponse(
        roi_score=roi_result['roi_score'],
        recommendation=roi_result['recommendation'],
        similarity={
            'items': [{'item_id': wardrobe_items[0].get('item_id', 'unknown'), 'score': round(candidate_score, 2)}] if wardrobe_items else [],
            'verdict': _similarity_verdict(candidate_score),
            'verification': 'duplicate check ok' if candidate_score >= 0.9 else 'new combination likely',
        },
        combination_gap={
            'new_combinations': roi_result['details']['new_combinations'],
            'reactivated_items': roi_result['breakdown']['old_item_activation']['count'],
            'scenario_coverage_delta': roi_result['breakdown']['scenario_coverage']['improvement'],
        },
        conflicts=conflicts,
        suggestions=suggestions,
    )
