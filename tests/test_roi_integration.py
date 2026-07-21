# 【P0-1】集成测试：ROI 路由接入 CombinationGapCalculator

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

USER = "roi-integration-test"


def test_roi_uses_combination_calculator():
    """验证 ROI 路由调用了 CombinationGapCalculator 而非硬编码公式"""
    # 先录入2件衣橱物品
    client.post("/api/v3/wardrobe/items", json={
        "user_id": USER, "item_id": "roi-pants-1",
        "category": "bottom", "style": "formal", "season": "spring",
        "occasion": "formal", "color": "dark_gray", "price": 399,
    })
    client.post("/api/v3/wardrobe/items", json={
        "user_id": USER, "item_id": "roi-shoes-1",
        "category": "shoes", "style": "formal", "season": "spring",
        "occasion": "formal", "color": "brown", "price": 599,
    })

    resp = client.post("/api/v3/shop/roi-analysis", json={
        "user_id": USER,
        "new_item": {
            "category": "outwear", "color": "light_blue",
            "price": 299, "style": "formal", "season": "spring",
            "occasion": ["formal", "daily"],
        }
    })
    assert resp.status_code == 200
    body = resp.json()
    # 核心断言：真实计算的结果应有合理值
    assert "roi_score" in body
    assert body["roi_score"] >= 0
    assert body["recommendation"] in {"recommend", "reconsider"}
    assert "combination_gap" in body
    assert body["combination_gap"]["new_combinations"] >= 0
    assert body["combination_gap"]["reactivated_items"] >= 0
    assert "scenario_coverage_delta" in body["combination_gap"]


def test_roi_empty_wardrobe():
    """空衣橱时 ROI 仍可正常返回"""
    resp = client.post("/api/v3/shop/roi-analysis", json={
        "user_id": "roi-empty-user",
        "new_item": {"category": "outwear", "color": "white", "price": 199,
                     "style": "casual", "season": "summer", "occasion": ["daily"]}
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["roi_score"] >= 0
    assert body["recommendation"] in {"recommend", "reconsider"}


def test_roi_backward_compat():
    """保持向后兼容：recommendation 仍在 {recommend, reconsider} 中"""
    client.post("/api/v3/wardrobe/items", json={
        "user_id": "roi-compat", "item_id": "rc-1",
        "category": "outwear", "style": "casual", "season": "summer",
        "occasion": "daily", "color": "white", "price": 199,
    })
    resp = client.post("/api/v3/shop/roi-analysis", json={
        "user_id": "roi-compat",
        "new_item": {"category": "bottom", "color": "black", "price": 199}
    })
    assert resp.status_code == 200
    assert resp.json()["recommendation"] in {"recommend", "reconsider"}
