import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.similarity import MockSimilarityEngine, CLIPSimilarityEngine

client = TestClient(app)


def test_mock_similarity_same_category():
    engine = MockSimilarityEngine()
    score = engine.calculate_similarity(
        {'category': 'outwear', 'color': 'white'},
        {'category': 'outwear', 'color': 'black'},
    )
    assert score == 0.4  # 仅 category 相同


def test_mock_similarity_all_match():
    engine = MockSimilarityEngine()
    score = engine.calculate_similarity(
        {'category': 'outwear', 'color': 'white', 'style': 'formal', 'material': 'cotton'},
        {'category': 'outwear', 'color': 'white', 'style': 'formal', 'material': 'cotton'},
    )
    assert score == 1.0


def test_mock_similarity_no_match():
    engine = MockSimilarityEngine()
    score = engine.calculate_similarity(
        {'category': 'outwear', 'color': 'white'},
        {'category': 'bottom', 'color': 'black'},
    )
    assert score == 0.0


def test_clip_not_implemented():
    engine = CLIPSimilarityEngine()
    with pytest.raises(NotImplementedError):
        engine.calculate_similarity({}, {})


def test_roi_uses_similarity_engine():
    """验证 ROI 分析使用相似度引擎计算冲突"""
    user_id = 'roi-sim-user'
    # 录入一件衣物
    client.post('/api/v3/wardrobe/items', json={
        'user_id': user_id, 'item_id': 'existing-1',
        'category': 'outwear', 'color': 'white', 'style': 'formal', 'material': 'cotton',
    })
    # 请求 ROI：新物品与已有衣物完全相同
    resp = client.post('/api/v3/shop/roi-analysis', json={
        'user_id': user_id,
        'new_item': {
            'category': 'outwear', 'color': 'white', 'style': 'formal', 'material': 'cotton',
        },
    })
    assert resp.status_code == 200
    body = resp.json()
    # 应该检测到冲突（相似度 = 1.0）
    assert len(body['conflicts']) >= 1
    assert body['conflicts'][0]['existing_item'] == 'existing-1'
    assert body['similarity']['verdict'] == 'almost_same'


def test_roi_no_conflict_for_different_items():
    """验证不同物品不产生冲突"""
    user_id = 'roi-sim-diff'
    client.post('/api/v3/wardrobe/items', json={
        'user_id': user_id, 'item_id': 'diff-1',
        'category': 'outwear', 'color': 'white', 'style': 'formal',
    })
    resp = client.post('/api/v3/shop/roi-analysis', json={
        'user_id': user_id,
        'new_item': {
            'category': 'bottom', 'color': 'black', 'style': 'casual',
        },
    })
    assert resp.status_code == 200
    body = resp.json()
    assert len(body['conflicts']) == 0
    assert body['similarity']['verdict'] == 'unique'


def test_roi_returns_top_similarities():
    """验证返回多个相似度结果并按分数排序"""
    user_id = 'roi-sim-multi'
    # 录入多件衣物
    for i, (cat, col) in enumerate([('outwear', 'white'), ('outwear', 'black'), ('bottom', 'white')]):
        client.post('/api/v3/wardrobe/items', json={
            'user_id': user_id, 'item_id': f'multi-{i}',
            'category': cat, 'color': col,
        })
    resp = client.post('/api/v3/shop/roi-analysis', json={
        'user_id': user_id,
        'new_item': {'category': 'outwear', 'color': 'white'},
    })
    assert resp.status_code == 200
    body = resp.json()
    items = body['similarity']['items']
    # 应该返回多个相似度结果
    assert len(items) >= 2
    # 按分数降序排列
    scores = [item['score'] for item in items]
    assert scores == sorted(scores, reverse=True)
    # 第一个应该是完全匹配的
    assert items[0]['score'] == 0.7  # category(0.4) + color(0.3)