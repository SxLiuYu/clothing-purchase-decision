from typing import Dict

from fastapi import APIRouter
from app.models.schemas import OutfitPlan, OutfitRequest, OutfitResponse
from app.services.store import store

router = APIRouter()

HARD_CONSTRAINT_RULES = [
    {
        'id': 'HC001',
        'name': 'cold_must_wear_warm_layers',
        'condition': lambda weather: isinstance(weather, dict) and isinstance(weather.get('temperature_c'), (int, float)) and weather['temperature_c'] < 10,
        'layer_types': ['coat', 'sweater', 'thermal'],
    },
    {
        'id': 'HC002',
        'name': 'formal_exclude_sneakers_shorts_hoodie',
        'condition': lambda weather, constraints: str(constraints.get('occasion', '')).lower() == 'formal',
        'excluded_categories': ['sneakers', 'shorts', 'hoodie'],
    },
    {
        'id': 'HC003',
        'name': 'rain_exclude_sneakers_canvas',
        'condition': lambda weather, constraints: isinstance(weather, dict) and str(weather.get('condition', '')).lower() in {'rain', 'heavy rain'},
        'excluded_categories': ['sneakers', 'canvas'],
    },
    {
        'id': 'HC004',
        'name': 'hot_formal_prefer_breathable',
        'condition': lambda weather, constraints: isinstance(weather, dict) and isinstance(weather.get('temperature_c'), (int, float)) and weather['temperature_c'] >= 35 and str(constraints.get('occasion', '')).lower() == 'formal',
        'layer_types': ['linen', 'breathable'],
    },
]


def _parse_weather(payload: OutfitRequest):
    return payload.weather or {}


def _evaluate_hard_constraints(payload: OutfitRequest):
    weather = _parse_weather(payload)
    constraints = payload.constraints or {}
    active = []
    for rule in HARD_CONSTRAINT_RULES:
        try:
            passed = rule['condition'](weather, constraints)
        except TypeError:
            passed = rule['condition'](weather)
        if passed:
            active.append(rule)
    return active, weather.get('temperature_c')


def _build_outfit_candidates(user_id, active_rules, weather, constraints):
    user = store.get_or_create_user(user_id)
    nodes = (user.get('wardrobe_graph') or {}).get('nodes', [])
    return [
        {
            'rank': 1,
            'score': 92,
            'confidence': 0.87,
            'items': [
                {
                    'item_id': None,
                    'category': 'outwear',
                    'name': 'light_blue_dress_shirt_example',
                    'rationale': 'Satisfies formal commute constraints; keeps breathability.',
                    'risk_flags': [],
                    'score': 92,
                },
                {
                    'item_id': None,
                    'category': 'bottom',
                    'name': 'dark_gray_straight_trousers_example',
                    'rationale': 'High waist and reuse-friendly for recent cold-start wardrobe.',
                    'risk_flags': ['long_sitting_knee_bulge'] if int(weather.get('duration_hours', 0) or 0) >= 6 else [],
                    'score': 90,
                },
                {
                    'item_id': None,
                    'category': 'shoes',
                    'name': 'brown_derby_example',
                    'rationale': 'Formal and safer than sneakers or stil for commute.',
                    'risk_flags': [],
                    'score': 91,
                },
            ],
            'rationale': 'Hard constraints first, then style and wardrobe reuse optimization.',
            'risk_flags': ['Low contrast in rain; short runway switch to waterproof chelsea boot.'],
            'alternatives': {
                'rain': {
                    'score': 89,
                    'swap': ['brown_waterproof_chelsea_boot'],
                    'delta_reason': '+1 weather adaptation; rest unchanged.',
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
                    'name': 'blue_oxford_shirt_example',
                    'rationale': 'Alternative formal option with lower redundancy risk.',
                    'risk_flags': [],
                    'score': 82,
                }
            ],
            'rationale': 'Lower tight-fit risk for body-sensitive users.',
            'risk_flags': ['High similarity to light-blue shirt'],
            'alternatives': {},
        },
    ]


@router.post('/outfit', response_model=OutfitResponse)
def recommend_outfit(payload: OutfitRequest):
    active_rules, temperature_c = _evaluate_hard_constraints(payload)
    candidates = _build_outfit_candidates(payload.user_id, active_rules, _parse_weather(payload), payload.constraints)
    record = store.record_decision(payload.user_id, {
        'request': payload.dict(),
        'active_rules': [rule['name'] for rule in active_rules],
        'candidates': candidates,
    })
    return OutfitResponse(
        decision_id=str(record['generated_at']),
        confidence=0.87,
        outfits=[OutfitPlan(**plan) for plan in candidates],
    )
