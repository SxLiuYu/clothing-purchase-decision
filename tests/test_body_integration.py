# 【P0-2】集成测试：体态路由接入 ContinuousFeedbackAnalyzer

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_body_feedback_uses_continuous_analyzer():
    """单次反馈应记录并返回敏感区域"""
    client.post("/api/v3/wardrobe/items", json={
        "user_id": "fb-1", "item_id": "fb-item-1",
        "category": "bottom", "style": "slim", "season": "summer",
        "occasion": "daily", "color": "black",
    })
    resp = client.post("/api/v3/body/feedback", json={
        "user_id": "fb-1", "item_id": "fb-item-1",
        "fit_feedback": "tight_waist", "visual_comfort": "exposed_belly",
        "occasion": "daily",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert "tight_waist" in body["updated_profile"]["sensitive_areas"]
    assert "exposed_belly" in body["updated_profile"]["sensitive_areas"]


def test_consecutive_rejection_triggers_decay():
    """连续3次拒绝应触发全局权重下降"""
    user_id = "fb-consec"
    client.post("/api/v3/wardrobe/items", json={
        "user_id": user_id, "item_id": "fb-c-item",
        "category": "bottom", "style": "slim", "season": "summer",
        "occasion": "daily", "color": "black",
    })
    # 连续3次反馈修身不适
    for _ in range(3):
        resp = client.post("/api/v3/body/feedback", json={
            "user_id": user_id, "item_id": "fb-c-item",
            "fit_feedback": "tight_waist", "occasion": "daily",
        })
        assert resp.status_code == 200
    # 第3次后应触发连续拒绝分析
    body = resp.json()
    assert "consecutive_analysis" in body
    assert body["consecutive_analysis"]["consecutive_count"] >= 1
    assert body["consecutive_analysis"]["needs_global_decay"] is True


def test_feedback_backward_compat_sensitive_areas():
    """保持向后兼容：sensitive_areas 仍包含反馈部位"""
    user_id = "fb-compat"
    client.post("/api/v3/wardrobe/items", json={
        "user_id": user_id, "item_id": "fb-cp-1",
        "category": "bottom", "style": "slim", "season": "summer",
        "occasion": "daily", "color": "black",
    })
    resp = client.post("/api/v3/body/feedback", json={
        "user_id": user_id, "item_id": "fb-cp-1",
        "fit_feedback": "tight_waist", "visual_comfort": "exposed_belly",
        "occasion": "daily",
    })
    assert resp.status_code == 200
    assert "tight_waist" in resp.json()["updated_profile"]["sensitive_areas"]


def test_feedback_fit_preference_recorded():
    """fit_preference 应记录单品反馈"""
    user_id = "fb-pref"
    client.post("/api/v3/wardrobe/items", json={
        "user_id": user_id, "item_id": "fb-pref-1",
        "category": "bottom", "style": "slim", "season": "summer",
        "occasion": "daily", "color": "black",
    })
    resp = client.post("/api/v3/body/feedback", json={
        "user_id": user_id, "item_id": "fb-pref-1",
        "fit_feedback": "comfortable", "occasion": "daily",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert "fb-pref-1" in body["updated_profile"]["fit_preference"]
    assert body["updated_profile"]["fit_preference"]["fb-pref-1"] == "comfortable"
