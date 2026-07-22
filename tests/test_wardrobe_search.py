import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def _add_items(user_id, items):
    for item in items:
        client.post('/api/v3/wardrobe/items', json={
            'user_id': user_id, **item
        })


def test_search_by_category():
    user_id = 'search-cat'
    _add_items(user_id, [
        {'item_id': 's1', 'category': 'outwear', 'color': 'white', 'style': 'formal', 'season': 'winter'},
        {'item_id': 's2', 'category': 'bottom', 'color': 'black', 'style': 'casual', 'season': 'summer'},
        {'item_id': 's3', 'category': 'outwear', 'color': 'blue', 'style': 'casual', 'season': 'spring'},
    ])
    resp = client.post('/api/v3/wardrobe/search', json={
        'user_id': user_id, 'category': 'outwear',
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body['count'] == 2
    assert all(item['attributes']['category'] == 'outwear' for item in body['items'])


def test_search_by_color():
    user_id = 'search-color'
    _add_items(user_id, [
        {'item_id': 'c1', 'category': 'outwear', 'color': 'white'},
        {'item_id': 'c2', 'category': 'bottom', 'color': 'black'},
        {'item_id': 'c3', 'category': 'outwear', 'color': 'white'},
    ])
    resp = client.post('/api/v3/wardrobe/search', json={
        'user_id': user_id, 'color': 'white',
    })
    assert resp.status_code == 200
    assert resp.json()['count'] == 2


def test_search_combined():
    user_id = 'search-combo'
    _add_items(user_id, [
        {'item_id': 'm1', 'category': 'outwear', 'color': 'white', 'style': 'formal', 'season': 'winter'},
        {'item_id': 'm2', 'category': 'outwear', 'color': 'white', 'style': 'casual', 'season': 'summer'},
        {'item_id': 'm3', 'category': 'bottom', 'color': 'black', 'style': 'formal', 'season': 'winter'},
    ])
    resp = client.post('/api/v3/wardrobe/search', json={
        'user_id': user_id, 'category': 'outwear', 'color': 'white',
    })
    assert resp.status_code == 200
    assert resp.json()['count'] == 2


def test_search_keyword():
    user_id = 'search-kw'
    _add_items(user_id, [
        {'item_id': 'k1', 'category': 'outwear', 'color': 'white', 'style': 'formal'},
        {'item_id': 'k2', 'category': 'bottom', 'color': 'black', 'style': 'casual'},
    ])
    resp = client.post('/api/v3/wardrobe/search', json={
        'user_id': user_id, 'keyword': 'formal',
    })
    assert resp.status_code == 200
    assert resp.json()['count'] == 1
    assert resp.json()['items'][0]['item_id'] == 'k1'


def test_search_empty():
    user_id = 'search-empty'
    _add_items(user_id, [
        {'item_id': 'e1', 'category': 'outwear', 'color': 'white'},
    ])
    resp = client.post('/api/v3/wardrobe/search', json={
        'user_id': user_id, 'category': 'shoes',
    })
    assert resp.status_code == 200
    assert resp.json()['count'] == 0
    assert resp.json()['items'] == []


def test_search_limit():
    user_id = 'search-limit'
    for i in range(10):
        _add_items(user_id, [
            {'item_id': f'l{i}', 'category': 'outwear', 'color': 'white'},
        ])
    resp = client.post('/api/v3/wardrobe/search', json={
        'user_id': user_id, 'limit': 3,
    })
    assert resp.status_code == 200
    assert resp.json()['count'] == 10
    assert len(resp.json()['items']) == 3
