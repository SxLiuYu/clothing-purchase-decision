from abc import ABC, abstractmethod
from typing import Dict, List


class ItemAnalyzer(ABC):
    """从图片/文本中提取单品信息"""

    @abstractmethod
    def analyze_items(self, post: Dict) -> List[Dict]:
        ...


class MockItemAnalyzer(ItemAnalyzer):
    """Mock 实现：返回预置示例单品"""

    MOCK_ITEMS = {
        'mock-001': [
            {'item_id': 'mock-item-001', 'category': 'outwear', 'name': '白色修身衬衫', 'brand': '示例品牌', 'price': 299.0},
            {'item_id': 'mock-item-002', 'category': 'bottom', 'name': '深灰直筒西裤', 'brand': '示例品牌', 'price': 399.0},
        ],
        'mock-002': [
            {'item_id': 'mock-item-003', 'category': 'outwear', 'name': '米色宽松针织衫', 'brand': '示例品牌', 'price': 259.0},
            {'item_id': 'mock-item-004', 'category': 'bottom', 'name': '浅蓝直筒牛仔裤', 'brand': '示例品牌', 'price': 329.0},
        ],
        'mock-003': [
            {'item_id': 'mock-item-005', 'category': 'outwear', 'name': '黑色修身连衣裙', 'brand': '示例品牌', 'price': 459.0},
        ],
        'mock-004': [
            {'item_id': 'mock-item-006', 'category': 'outwear', 'name': '速干运动T恤', 'brand': '示例品牌', 'price': 199.0},
            {'item_id': 'mock-item-007', 'category': 'bottom', 'name': '弹力运动短裤', 'brand': '示例品牌', 'price': 249.0},
        ],
        'mock-005': [
            {'item_id': 'mock-item-008', 'category': 'outwear', 'name': '浅蓝牛津衬衫', 'brand': '示例品牌', 'price': 279.0},
            {'item_id': 'mock-item-009', 'category': 'bottom', 'name': '卡其色休闲裤', 'brand': '示例品牌', 'price': 349.0},
        ],
    }

    def analyze_items(self, post: Dict) -> List[Dict]:
        post_id = post.get('post_id', '')
        return self.MOCK_ITEMS.get(post_id, [
            {'item_id': 'mock-item-000', 'category': 'unknown', 'name': '示例单品', 'price': None}
        ])


class VisionItemAnalyzer(ItemAnalyzer):
    """基于多模态模型的单品分析（预留）"""

    def analyze_items(self, post: Dict) -> List[Dict]:
        raise NotImplementedError("VisionItemAnalyzer not yet implemented")


# 全局实例
analyzer = MockItemAnalyzer()