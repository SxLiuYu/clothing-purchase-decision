import base64
import hashlib
from abc import ABC, abstractmethod
from typing import Optional


class ImageStorage(ABC):
    """图片存储接口"""

    @abstractmethod
    def upload(self, file_bytes: bytes, filename: str, content_type: str = 'image/jpeg') -> str:
        """上传图片，返回 URL"""
        ...


class MockImageStorage(ImageStorage):
    """Mock 实现：返回模拟 URL"""

    BASE_URL = 'https://mock-storage.example.com/images'

    def upload(self, file_bytes: bytes, filename: str, content_type: str = 'image/jpeg') -> str:
        file_hash = hashlib.md5(file_bytes).hexdigest()[:8]
        return f'{self.BASE_URL}/{file_hash}_{filename}'


class S3ImageStorage(ImageStorage):
    """S3/MinIO 存储（预留）"""

    def __init__(self, bucket: str = 'wardrobe-images', region: str = 'us-east-1'):
        self.bucket = bucket
        self.region = region

    def upload(self, file_bytes: bytes, filename: str, content_type: str = 'image/jpeg') -> str:
        raise NotImplementedError("S3ImageStorage not yet implemented")


# 全局实例（当前使用 mock，后续可替换为 S3）
storage = MockImageStorage()