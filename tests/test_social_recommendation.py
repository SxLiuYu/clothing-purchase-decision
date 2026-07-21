import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.social_fetcher import MockSocialMediaFetcher
from app.services.item_analyzer import MockItemAnalyzer
from app.services.social_recommendation import SocialRecommendationEngine

client = TestClient(app)


def test_mock_fetcher_returns_posts():
    fetcher = MockSocialMediaFetcher()
    posts = fetcher.fetch_posts('oval', 'rectangle', 'warm', 'formal', 3)
    assert len(posts) == 3
    assert posts[0]['post_id'] == 'mock-001'


def test_mock_analyzer_returns_items():
    analyzer = MockItemAnalyzer()
    items = analyzer.analyze_items({'post_id': 'mock-001'})
    assert len(items) == 2
    assert items[0]['item_id'] == 'mock-item-001'


def test_recommendation_engine_match_score():
    engine = SocialRecommendationEngine(MockSocialMediaFetcher(), MockItemAnalyzer())
    result = engine.recommend('user-1', {
        'face_shape': 'oval', 'body_shape': 'rectangle', 'skin_tone': 'warm',
    }, 'formal', 2)
    assert len(result['recommendations']) == 2
    assert result['recommendations'][0]['post']['post_id'] == 'mock-001'
    assert result['recommendations'][0]['match_score'] >= 0.7


def test_recommendation_no_profile():
    engine = SocialRecommendationEngine(MockSocialMediaFetcher(), MockItemAnalyzer())
    result = engine.recommend('user-2', {}, 'casual', 3)
    assert len(result['recommendations']) == 3
    assert result['recommendations'][0]['rationale'] == '热门穿搭推荐'


def test_recommendation_sorted_by_score():
    engine = SocialRecommendationEngine(MockSocialMediaFetcher(), MockItemAnalyzer())
    result = engine.recommend('user-3', {
        'face_shape': 'round', 'body_shape': 'pear', 'skin_tone': 'cool',
    }, 'casual', 5)
    scores = [r['score'] for r in result['recommendations']]
    assert scores == sorted(scores, reverse=True)


def test_api_social_recommend():
    """完整 API 链路测试"""
    user_id = 'user-social-1'
    # 录入体态档案
    client.post('/api/v3/body/profile', json={
        'user_id': user_id,
        'face_shape': 'oval',
        'body_shape': 'rectangle',
        'skin_tone': 'warm',
        'height': 175,
        'weight': 72,
    })
    # 请求社媒推荐
    resp = client.post('/api/v3/social/recommend', json={
        'user_id': user_id,
        'occasion': 'formal',
        'limit': 3,
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body['user_id'] == user_id
    assert body['total_count'] >= 1
    recs = body['recommendations']
    assert len(recs) == 3
    # 验证推荐结构
    for rec in recs:
        assert 'rank' in rec
        assert 'score' in rec
        assert 'match_score' in rec
        assert 'reproducibility' in rec
        assert 'sentiment' in rec
        assert 'post' in rec
        assert 'items' in rec
        assert 'rationale' in rec
    # 第一个推荐应该是 mock-001（匹配度最高）
    assert recs[0]['post']['post_id'] == 'mock-001'
    assert recs[0]['match_score'] >= 0.7


def test_api_social_recommend_cold_start():
    """冷启动：无体态档案时也能推荐"""
    user_id = 'user-social-cold'
    resp = client.post('/api/v3/social/recommend', json={
        'user_id': user_id,
        'occasion': 'daily',
        'limit': 2,
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body['total_count'] >= 1
    # 冷启动推荐理由应为默认
    assert body['recommendations'][0]['rationale'] == '热门穿搭推荐'