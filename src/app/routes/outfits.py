from typing import Any, Dict, List

from fastapi import APIRouter
from app.models.schemas import OutfitPlan, OutfitRequest, OutfitResponse, Item
from app.services.store import store

router = APIRouter()


class ColdWarmLayerRule:
    rule_id = "HC001"
    name = "cold_must_wear_warm_layers"
    layer_types = ["coat", "sweater", "thermal"]
    deny_categories = ["tank_top", "shorts", "sandals"]
    penalty = 12

    def evaluate(self, payload: Dict) -> bool:
        weather = payload.get("weather") or {}
        return isinstance(weather.get("temperature_c"), (int, float)) and weather["temperature_c"] < 10


class FormalExcludeRule:
    rule_id = "HC002"
    name = "formal_exclude_sneakers_shorts_hoodie"
    deny_categories = ["sneakers", "shorts", "hoodie"]
    penalty = 18

    def evaluate(self, payload: Dict) -> bool:
        return str(payload.get("constraints", {}).get("occasion", "")).lower() == "formal"


class RainExcludeRule:
    rule_id = "HC003"
    name = "rain_exclude_sneakers_canvas"
    deny_categories = ["sneakers", "canvas"]
    penalty = 15

    def evaluate(self, payload: Dict) -> bool:
        weather = payload.get("weather") or {}
        return str(weather.get("condition", "")).lower() in {"rain", "heavy rain"}


class HotFormalBreathableRule:
    rule_id = "HC004"
    name = "hot_formal_prefer_breathable"
    allow_categories = ["linen", "breathable"]
    penalty = 6

    def evaluate(self, payload: Dict) -> bool:
        weather = payload.get("weather") or {}
        return (
            isinstance(weather.get("temperature_c"), (int, float))
            and weather["temperature_c"] >= 35
            and str(payload.get("constraints", {}).get("occasion", "")).lower() == "formal"
        )


HARD_CONSTRAINT_RULES = [
    ColdWarmLayerRule(),
    FormalExcludeRule(),
    RainExcludeRule(),
    HotFormalBreathableRule(),
]


def _parse_weather(payload: OutfitRequest) -> Dict:
    return payload.weather or {}


def _evaluate_hard_constraints(payload: OutfitRequest) -> List[Any]:
    payload_dict = {"weather": _parse_weather(payload), "constraints": payload.constraints or {}}
    return [rule for rule in HARD_CONSTRAINT_RULES if rule.evaluate(payload_dict)]


def _category_hard_score(category: str, active_rules: List[Any]) -> float:
    score = 100.0
    penalties = []
    for rule in active_rules:
        if category in getattr(rule, "deny_categories", []):
            score -= getattr(rule, "penalty", 10)
            penalties.append(getattr(rule, "name"))
        if category in getattr(rule, "layer_types", []) or category in getattr(rule, "allow_categories", []):
            score += 2
    return max(score, 10), penalties


def _apply_body_feedback_bias(score: float, fit_feedback: str) -> float:
    bias = 0.0
    if fit_feedback in {"tight_waist", "exposed_belly", "too_tight"}:
        bias = -6.0
    elif fit_feedback in {"comfortable", "relaxed", "loose"}:
        bias = 2.0
    return max(score + bias, 10)


def _risks_for_item(name: str, weather: Dict, duration_hours: int) -> List[str]:
    risks = []
    condition = str(weather.get("condition", "")).lower()
    if name == "light_blue_dress_shirt" and condition in {"rain", "heavy rain", "light_rain"}:
        risks.append("low_contrast_in_rain")
    if name == "dark_gray_straight_trousers" and duration_hours >= 6:
        risks.append("long_sitting_knee_bulge")
    if name == "blue_oxford_shirt":
        risks.append("high_similarity_to_primary")
    return risks


def _build_example_candidates(active_rules: List[Any], weather: Dict, constraints: Dict, top_rank: int) -> List[Dict[str, Any]]:
    candidates = []
    items = [
        {"category": "outwear", "name": "light_blue_dress_shirt", "base_score": 92, "fit_feedback": "comfortable", "rationale": "Meets formal commute while remaining breathable."},
        {"category": "bottom", "name": "dark_gray_straight_trousers", "base_score": 90, "fit_feedback": "comfortable", "rationale": "High-waist reuse-friendly bottom suitable for formal settings."},
        {"category": "shoes", "name": "brown_derby", "base_score": 91, "fit_feedback": "comfortable", "rationale": "Formal and safer than sneakers for commute."},
        {"category": "outwear", "name": "blue_oxford_shirt", "base_score": 82, "fit_feedback": "comfortable", "rationale": "Alternative formal option with lower similarity risk."},
    ]
    duration_hours = int(weather.get("duration_hours", 0) or 0)
    for idx, item in enumerate(items, start=1):
        category_score, penalties = _category_hard_score(item["category"], active_rules)
        score = round(min(item["base_score"], (item["base_score"] + category_score) / 2), 1)
        score = round(_apply_body_feedback_bias(score, item["fit_feedback"]), 1)
        name = item["name"]
        if score <= 55:
            name += " (rejected)"
        item_risks = _risks_for_item(item["name"], weather, duration_hours)
        if str(weather.get("condition", "")).lower() in {"rain", "heavy rain", "light_rain"}:
            item_risks = item_risks + ["switch_to_waterproof_chelsea_boots_60s"]
        candidates.append({
            "rank": idx,
            "score": score,
            "confidence": max(round(min(0.95, score / 100 + 0.12), 2), 0.45),
            "items": [
                {
                    "item_id": None,
                    "category": item["category"],
                    "name": name,
                    "rationale": item["rationale"],
                    "risk_flags": item_risks,
                    "score": score,
                    "hard_constraint_penalties": penalties,
                }
            ],
            "rationale": "Hard constraints first, then body-fit preference and reuse optimization.",
            "risk_flags": item_risks,
            "alternatives": {
                "rain": {
                    "score": max(score - 1, 60),
                    "swap": ["brown_waterproof_chelsea_boot"],
                    "delta_reason": "+1 weather adaptation; rest unchanged.",
                }
            },
            "switch_options": [],
        })
    candidates.sort(key=lambda record: (-record["score"], -record["confidence"], record["rank"]))
    for rank, candidate in enumerate(candidates, start=1):
        candidate["rank"] = rank
    top_candidates = candidates[:max(1, top_rank)]
    switch_map = {candidate["rank"]: candidate for candidate in top_candidates}
    for candidate in top_candidates:
        candidate["switch_options"] = [
            {
                "rank": other["rank"],
                "score": other["score"],
                "name": other["items"][0]["name"],
                "rationale": other["rationale"],
                "risk_flags": other["risk_flags"],
                "delta_reason": other["alternatives"].get("rain", {}).get("delta_reason"),
            }
            for other in top_candidates
            if other["rank"] != candidate["rank"] and other["score"] >= 65
        ]
    return top_candidates


@router.post("/outfit", response_model=OutfitResponse)
def recommend_outfit(payload: OutfitRequest):
    active_rules = _evaluate_hard_constraints(payload)
    candidates = _build_example_candidates(active_rules, _parse_weather(payload), payload.constraints or {}, top_rank=3)
    record = store.record_decision(payload.user_id, {
        "request": payload.dict(),
        "active_rules": [getattr(rule, "name", str(rule)) for rule in active_rules],
        "candidates": candidates,
    })
    return OutfitResponse(
        decision_id=str(record["generated_at"]),
        confidence=round(sum(candidate["confidence"] for candidate in candidates) / len(candidates), 2),
        outfits=[OutfitPlan(**candidate) for candidate in candidates],
    )
