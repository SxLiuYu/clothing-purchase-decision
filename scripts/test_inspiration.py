import httpx
import json

r = httpx.post('http://localhost:8000/api/v3/inspiration/similar-outfits', json={
    'user_id': 'test',
    'body_profile': {'height': 175, 'weight': 70, 'body_shape': 'athletic'},
    'occasion': 'formal',
    'style': 'minimalist'
})
print('Status:', r.status_code)
print(json.dumps(r.json(), indent=2, ensure_ascii=False))
