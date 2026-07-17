from datetime import datetime
from typing import Dict

from app.models.schemas import (
    OutfitPlan,
    OutfitRequest,
    OutfitResponse,
)
from app.services.store import store

HARD_CONSTRAINT_RULES = [
    {
        'id': 'HC001',
        'name': '低温必须保暖',
        'condition': lambda weather: isinstance(weather, dict) and isinstance(weather.get('temperature_c'), (int, float)) and weather['temperature_c'] < 10,
        'action': 'must_include_layer',
        'layer_types': ['coat', 'sweater', 'thermal'],
    },
    {
        'id': 'HC002',
        'name': '正式场合禁用运动装',
        'condition': lambda weather, constraints: str(constraints.get('occasion', '')).lower() == 'formal',
        'action': 'exclude_categories',
        'categories': ['sneakers', 'shorts', 'hoodie'],
    },
    {
        'id': 'HC003',
        'name': '雨天禁用敞口鞋/薄底',
        'condition': lambda weather, constraints: isinstance(weather, dict) and str(weather.get('condition', '')).lower() in {'rain', 'heavy rain'},
        'action': 'exclude_categories',
        'categories': ['sneakers', 'canvas'],
    },
    {
        'id': 'HC004',
        'name': '高温正式场合穿透气方案',
        'condition': lambda weather, constraints: isinstance(weather, dict) and isinstance(weather.get('temperature_c'), (int, float)) and weather['temperature_c'] >= 35 and str(constraints.get('occasion', '')).lower() == 'formal',
        'action': 'prefer_layer',
        'layer_types': ['linnen', 'breathable'],
    },
]


def _parse_weather(payload: OutfitRequest):
    return payload.weather or {}


def _evaluate_hard_constraints(payload: OutfitRequest, sensitive_areas: list):
    weather = _parse_weather(payload)
    constraints = payload.constraints or {}
    active_rules = []
    for rule in HARD_CONSTRAINT_RULES:
        try:
            passed = rule['condition'](weather, constraints)
        except TypeError:
            passed = rule['condition'](weather)
        if passed:
            active_rules.append(rule)
    return active_rules, weather['temperature_c'] if isinstance(weather.get('temperature_c'), (int, float)) else None


def _build_outfit_candidates(user_id: str, active_rules: list, weather: dict, constraints: Dict):
    user = store.get_or_create_user(user_id)
    nodes = user.get('wardrobe_graph', {}).get('nodes', []) if user.get('wardrobe_graph') else []
    return {
        'lightning': [
            {
                'rank': 1,
                'score': 92,
                'confidence': 0.85,
                'items': [
                    {
                        'item_id': None,
                        'category': 'outwear',
                        'name': '浅蓝修身衬衫（示例）',
                        'rationale': '通勤场景首选；透气性适合当前温度；保留正式感。',
                        'risk_flags': [],
                        'score': 92,
                    },
                    {
                        'item_id': None,
                        'category': 'bottom',
                        'name': '深灰高腰直筒西裤（示例）',
                        'rationale': '高腰线优化比例；近30天未穿着，利于衣橱复用。',
                        'risk_flags': ['久坐可能产生膝盖鼓包'] if int(weather.get('duration_hours', 0) or 0) >= 6 else [],
                        'score': 90,
                    },
                    {
                        'item_id': None,
                        'category': 'shoes',
                        'name': '棕色德比鞋（示例）',
                        'rationale': '满足正式会议要求；比高跟鞋更安全、比运动鞋更合适。',
                        'risk_flags': [],
                        'score': 91,
                    },
                ],
                'rationale': '先满足硬约束：正式场景、通勤、温度区间均可覆盖；再优化美学与复用。',
                'risk_flags': ['浅蓝在阴天对比度略低。如下雨，可60秒切换防水切尔西靴。'],
                'alternatives': {
                    'rain': {
                        'score': 88,
                        'swap': ['棕色防水切尔西靴'],
                        'delta_reason': '+3 天气适配；其他单品不变，切换成本低。',
                    }
                },
            },
            {
                'rank': 2,
                'score': 82,
                'confidence': 0.72,
                'items': [
                    {
                        'item_id': None,
                        'category': 'outwear',
                        'name': '蓝色牛津纺衬衫（示例）',
                        'rationale': '和现有浅蓝衬衫形成近似替代，更适合更正式场合。',
                        'risk_flags': [],
                        'score': 82,
                    }
                ],
                'rationale': '降低修身风险，适合体态敏感用户参考。',
                'risk_flags': ['与浅蓝衬衫重复度高'],
                'alternatives': {},
            },
        ]
    }


@router.post('/outfit', response_model=OutfitResponse)
def recommend_outfit(payload: OutfitRequest):
    active_rules, temperature_c = _evaluate_hard_constraints(payload, [])
    candidates = _build_outfit_candidates(payload.user_id, active_rules, _parse_weather(payload), payload.constraints)
    record = store.record_decision(payload.user_id, {
        'request': payload.dict(),
        'active_rules': [rule['name'] for rule in active_rules],
        'candidates': candidates['lightning'],
    })
    return OutfitResponse(
        decision_id=str(record['generated_at']),
        confidence=0.87,
        outfits=[OutfitPlan(**plan) for plan in candidates['lightning']],
    )
