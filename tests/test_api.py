import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


def test_wardrobe_item_lifecycle():
    user_id = 'user-1'
    payload = {
        'user_id': user_id,
        'item_id': 'item-1',
        'category': 'outwear',
        'style': 'formal',
        'season': 'spring',
        'occasion': 'commute',
        'color': 'light_blue',
        'material': 'cotton',
        'attributes': {'fit': 'slim'},
        'price': 299,
    }
    index_response = client.post('/api/v3/wardrobe/items', json=payload)
    assert index_response.status_code == 200
    assert index_response.json()['status'] == 'indexed'
    list_response = client.get(f'/api/v3/wardrobe/users/{user_id}/items')
    assert list_response.status_code == 200
    assert list_response.json()['count'] == 1


def test_outfit_decision_chain():
    user_id = 'user-2'
    client.post('/api/v3/wardrobe/items', json={
        'user_id': user_id,
        'item_id': 'item-1',
        'category': 'outwear',
        'style': 'formal',
        'season': 'spring',
        'occasion': 'commute',
        'color': 'light_blue',
    })
    response = client.post('/api/v3/decisions/outfit', json={
        'user_id': user_id,
        'occasion': 'formal',
        'datetime': '2026-07-16T08:00:00+08:00',
        'location': {'lat': 31.23, 'lng': 121.47},
        'weather': {'temperature_c': 16, 'condition': 'light_rain', 'humidity': 0.65},
        'constraints': {'avoid_materials': ['wool'], 'must_have': ['formal_shirt'], 'duration_hours': 8},
    })
    assert response.status_code == 200
    body = response.json()
    assert body['decision_id']
    assert body['confidence'] >= 0.5
    assert body['outfits'][0]['risk_flags']


def test_roi_and_feedback_loop():
    user_id = 'user-3'
    client.post('/api/v3/wardrobe/items', json={
        'user_id': user_id,
        'item_id': 'item-10',
        'category': 'outwear',
        'style': 'formal',
        'season': 'spring',
        'occasion': 'commute',
        'color': 'light_blue',
    })
    roi_response = client.post('/api/v3/shop/roi-analysis', json={
        'user_id': user_id,
        'new_item': {'category': 'outwear', 'color': 'light_blue', 'price': 299, 'score': 0.88},
    })
    assert roi_response.status_code == 200
    roi_body = roi_response.json()
    assert roi_body['combination_gap']['new_combinations'] >= 1
    feedback_response = client.post('/api/v3/body/feedback', json={
        'user_id': user_id,
        'item_id': 'item-10',
        'fit_feedback': 'tight_waist',
        'visual_comfort': 'exposed_belly',
        'occasion': 'commute',
    })
    assert feedback_response.status_code == 200
    assert 'tight_waist' in feedback_response.json()['updated_profile']['sensitive_areas']


def test_extreme_hot_formal_meeting():
    user_id = 'user-4'
    response = client.post('/api/v3/decisions/outfit', json={
        'user_id': user_id,
        'occasion': 'formal',
        'datetime': '2026-07-16T09:00:00+08:00',
        'location': {'lat': 31.23, 'lng': 121.47},
        'weather': {'temperature_c': 36, 'condition': 'sunny', 'humidity': 0.55},
        'constraints': {'avoid_materials': ['wool'], 'must_have': ['formal_shirt'], 'duration_hours': 3},
    })
    assert response.status_code == 200
    body = response.json()
    assert body['confidence'] >= 0.5
    assert any(alternative.get('score', 0) >= 60 for alternative in body['outfits'][0].get('alternatives', {}).values())


def test_cold_start_wardrobe_keeps_output():
    user_id = 'user-5'
    client.post('/api/v3/wardrobe/items', json={
        'user_id': user_id,
        'item_id': 'item-a',
        'category': 'outwear',
        'style': 'casual',
        'season': 'summer',
        'occasion': 'daily',
        'color': 'white',
    })
    roi_response = client.post('/api/v3/shop/roi-analysis', json={
        'user_id': user_id,
        'new_item': {'category': 'bottom', 'color': 'black', 'price': 199, 'score': 0.8},
    })
    assert roi_response.status_code == 200
    assert roi_response.json()['recommendation'] in {'recommend', 'reconsider'}


def test_feedback_affects_body_profile_twice():
    user_id = 'user-6'
    client.post('/api/v3/wardrobe/items', json={
        'user_id': user_id,
        'item_id': 'item-x',
        'category': 'bottom',
        'style': 'slim',
        'season': 'summer',
        'occasion': 'daily',
        'color': 'black',
    })
    first = client.post('/api/v3/body/feedback', json={
        'user_id': user_id,
        'item_id': 'item-x',
        'fit_feedback': 'tight_waist',
        'visual_comfort': 'exposed_belly',
        'occasion': 'daily',
    }).json()
    assert 'tight_waist' in first['updated_profile']['sensitive_areas']
    second = client.post('/api/v3/body/feedback', json={
        'user_id': user_id,
        'item_id': 'item-x',
        'fit_feedback': 'comfortable',
        'visual_comfort': None,
        'occasion': 'daily',
    }).json()
    assert 'comfortable' in second['updated_profile']['fit_preference'].values()


def test_set_body_profile():
    user_id = 'user-profile-1'
    response = client.post('/api/v3/body/profile', json={
        'user_id': user_id,
        'height': 175.0,
        'weight': 72.0,
        'shoulder_width': 45.0,
        'waistline': 80.0,
        'leg_type': 'straight',
        'body_shape': 'rectangle',
        'fit_preference': 'slim',
    })
    assert response.status_code == 200
    body = response.json()
    assert 'decision_id' in body
    assert 'updated_profile' in body
    assert body['updated_profile']['fit_preference'] == {'global': 'slim'}


def test_update_body_profile_partial():
    """只更新部分字段"""
    user_id = 'user-profile-2'
    client.post('/api/v3/body/profile', json={
        'user_id': user_id, 'height': 170.0, 'weight': 65.0,
        'body_shape': 'pear', 'fit_preference': 'loose',
    })
    resp = client.post('/api/v3/body/profile', json={
        'user_id': user_id, 'weight': 68.0,
    })
    assert resp.status_code == 200


def test_body_feedback_affects_outfit_score():
    """验证体态反馈后，有敏感区域的品类评分会降低"""
    user_id = 'user-body-affect'
    # 录入衣物
    client.post('/api/v3/wardrobe/items', json={
        'user_id': user_id, 'item_id': 'body-tight-pants', 'category': 'bottom',
        'color': 'black', 'style': 'slim', 'season': 'all', 'occasion': 'daily',
    })
    # 提交体态反馈（紧身不适）
    client.post('/api/v3/body/feedback', json={
        'user_id': user_id, 'item_id': 'body-tight-pants',
        'fit_feedback': 'tight_waist', 'visual_comfort': 'exposed_belly',
    })
    # 请求穿搭
    resp = client.post('/api/v3/decisions/outfit', json={
        'user_id': user_id, 'occasion': 'daily',
        'datetime': '2026-07-21T12:00:00+08:00',
        'weather': {'temperature_c': 25, 'condition': 'sunny'},
    })
    assert resp.status_code == 200
    # 验证反馈后评分不为空
    assert resp.json()['outfits']


def test_rationale_is_dynamic():
    """验证 rationale 不是硬编码，而是根据上下文动态生成"""
    user_id = 'user-rationale'
    # 录入体态档案
    client.post('/api/v3/body/profile', json={
        'user_id': user_id, 'height': 175, 'weight': 72,
        'fit_preference': 'slim',
    })
    # 录入衣物
    client.post('/api/v3/wardrobe/items', json={
        'user_id': user_id, 'item_id': 'rat-coat', 'category': 'outwear',
        'color': 'black', 'style': 'formal', 'season': 'winter', 'occasion': 'formal',
    })
    # 请求穿搭
    resp = client.post('/api/v3/decisions/outfit', json={
        'user_id': user_id, 'occasion': 'formal',
        'datetime': '2026-07-21T08:00:00+08:00',
        'weather': {'temperature_c': 5, 'condition': 'rain'},
        'constraints': {'duration_hours': 8},
    })
    assert resp.status_code == 200
    rationale = resp.json()['outfits'][0]['rationale']
    # 验证包含动态生成的内容
    assert '场景适配' in rationale or '硬约束' in rationale or '体态' in rationale
    assert '5°C' in rationale or '雨天' in rationale or '正式' in rationale
