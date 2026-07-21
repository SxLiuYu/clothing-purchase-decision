# 【P0-3】集成测试：决策路由接入 MultiObjectiveOptimizer

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_outfit_uses_multi_objective_optimizer():
    """决策路由应调用 MultiObjectiveOptimizer 排序候选"""
    user_id = "outfit-opt"
    for i, cat in enumerate(["outwear", "bottom", "shoes"], start=1):
        client.post("/api/v3/wardrobe/items", json={
            "user_id": user_id, "item_id": f"opt-{i}",
            "category": cat, "style": "formal", "season": "spring",
            "occasion": "formal", "color": "light_blue",
        })
    resp = client.post("/api/v3/decisions/outfit", json={
        "user_id": user_id, "occasion": "formal",
        "datetime": "2026-07-21T09:00:00+08:00",
        "weather": {"temperature_c": 18, "condition": "cloudy"},
        "constraints": {"duration_hours": 8},
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["decision_id"]
    assert body["confidence"] >= 0.5
    assert len(body["outfits"]) >= 1
    # 候选应按分数降序
    scores = [o["score"] for o in body["outfits"]]
    assert scores == sorted(scores, reverse=True)


def test_outfit_backward_compat_confidence():
    """保持向后兼容：confidence >= 0.5，outfits 非空"""
    resp = client.post("/api/v3/decisions/outfit", json={
        "user_id": "outfit-compat", "occasion": "formal",
        "datetime": "2026-07-21T09:00:00+08:00",
        "weather": {"temperature_c": 16, "condition": "light_rain"},
        "constraints": {"duration_hours": 8},
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["confidence"] >= 0.5
    assert len(body["outfits"]) >= 1
    assert body["outfits"][0]["risk_flags"] is not None


def test_outfit_extreme_hot_formal():
    """极端炎热+正式会议仍可返回候选"""
    resp = client.post("/api/v3/decisions/outfit", json={
        "user_id": "outfit-hot", "occasion": "formal",
        "datetime": "2026-07-21T09:00:00+08:00",
        "weather": {"temperature_c": 36, "condition": "sunny"},
        "constraints": {"duration_hours": 3},
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["confidence"] >= 0.5
    assert len(body["outfits"]) >= 1
