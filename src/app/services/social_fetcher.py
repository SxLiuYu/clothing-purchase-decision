from abc import ABC, abstractmethod
from typing import Dict, List


class SocialMediaFetcher(ABC):
    """社媒数据获取接口"""

    @abstractmethod
    def fetch_posts(
        self,
        face_shape: str,
        body_shape: str,
        skin_tone: str,
        occasion: str,
        limit: int = 10,
    ) -> List[Dict]:
        ...


class MockSocialMediaFetcher(SocialMediaFetcher):
    """Mock 实现：返回预置示例数据"""

    MOCK_POSTS = [
        {
            'post_id': 'mock-001',
            'title': '正式通勤穿搭推荐',
            'source': 'mock',
            'author': '穿搭达人',
            'image_url': None,
            'tags': ['formal', 'commute', 'rectangle', 'oval'],
            'face_shape': 'oval',
            'body_shape': 'rectangle',
            'skin_tone': 'warm',
            'sentiment': 0.95,
        },
        {
            'post_id': 'mock-002',
            'title': '休闲日常穿搭分享',
            'source': 'mock',
            'author': '时尚博主',
            'image_url': None,
            'tags': ['casual', 'daily', 'pear', 'round'],
            'face_shape': 'round',
            'body_shape': 'pear',
            'skin_tone': 'cool',
            'sentiment': 0.88,
        },
        {
            'post_id': 'mock-003',
            'title': '约会穿搭灵感',
            'source': 'mock',
            'author': '搭配师小王',
            'image_url': None,
            'tags': ['date', 'heart', 'hourglass'],
            'face_shape': 'heart',
            'body_shape': 'hourglass',
            'skin_tone': 'neutral',
            'sentiment': 0.92,
        },
        {
            'post_id': 'mock-004',
            'title': '运动休闲街头风',
            'source': 'mock',
            'author': '运动达人',
            'image_url': None,
            'tags': ['sport', 'outdoor', 'square', 'inverted-triangle'],
            'face_shape': 'square',
            'body_shape': 'inverted-triangle',
            'skin_tone': 'olive',
            'sentiment': 0.85,
        },
        {
            'post_id': 'mock-005',
            'title': '职场新人穿搭指南',
            'source': 'mock',
            'author': '职场穿搭',
            'image_url': None,
            'tags': ['formal', 'daily', 'diamond', 'rectangle'],
            'face_shape': 'diamond',
            'body_shape': 'rectangle',
            'skin_tone': 'warm',
            'sentiment': 0.90,
        },
    ]

    def fetch_posts(
        self,
        face_shape: str,
        body_shape: str,
        skin_tone: str,
        occasion: str,
        limit: int = 10,
    ) -> List[Dict]:
        return self.MOCK_POSTS[:limit]


class XiaoHongShuFetcher(SocialMediaFetcher):
    """小红书爬取实现（预留）"""

    def fetch_posts(
        self,
        face_shape: str,
        body_shape: str,
        skin_tone: str,
        occasion: str,
        limit: int = 10,
    ) -> List[Dict]:
        raise NotImplementedError("XiaoHongShuFetcher not yet implemented")


class WeiBoFetcher(SocialMediaFetcher):
    """微博爬取实现（预留）"""

    def fetch_posts(
        self,
        face_shape: str,
        body_shape: str,
        skin_tone: str,
        occasion: str,
        limit: int = 10,
    ) -> List[Dict]:
        raise NotImplementedError("WeiBoFetcher not yet implemented")


# 全局实例（当前使用 mock，后续可替换为真实实现）
fetcher = MockSocialMediaFetcher()