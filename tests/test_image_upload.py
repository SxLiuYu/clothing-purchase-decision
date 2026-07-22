import pytest
import io
from fastapi.testclient import TestClient
from app.main import app
from app.services.image_storage import MockImageStorage, S3ImageStorage

client = TestClient(app)


def test_mock_storage_returns_url():
    storage = MockImageStorage()
    url = storage.upload(b'test-image-bytes', 'shirt.jpg')
    assert url.startswith('https://mock-storage.example.com/images/')
    assert 'shirt.jpg' in url


def test_mock_storage_deterministic_hash():
    storage = MockImageStorage()
    url1 = storage.upload(b'same-bytes', 'a.jpg')
    url2 = storage.upload(b'same-bytes', 'a.jpg')
    assert url1 == url2


def test_s3_not_implemented():
    storage = S3ImageStorage()
    with pytest.raises(NotImplementedError):
        storage.upload(b'bytes', 'test.jpg')


def test_api_upload_image():
    """测试图片上传 API"""
    user_id = 'upload-user'
    fake_image = io.BytesIO(b'fake-image-content-for-testing')
    resp = client.post(
        f'/api/v3/wardrobe/users/{user_id}/upload',
        files={'file': ('test-shirt.jpg', fake_image, 'image/jpeg')},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body['user_id'] == user_id
    assert body['filename'] == 'test-shirt.jpg'
    assert 'url' in body
    assert body['url'].startswith('https://mock-storage.example.com/images/')
    assert body['size'] > 0


def test_api_upload_image_png():
    """测试上传 PNG 图片"""
    user_id = 'upload-png'
    fake_image = io.BytesIO(b'png-image-data')
    resp = client.post(
        f'/api/v3/wardrobe/users/{user_id}/upload',
        files={'file': ('photo.png', fake_image, 'image/png')},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body['filename'] == 'photo.png'
    assert 'png' in body['url']