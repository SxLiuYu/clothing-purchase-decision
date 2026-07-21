from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class SimilarityEngine(ABC):
    """相似度计算接口"""

    @abstractmethod
    def calculate_similarity(self, item_a: Dict, item_b: Dict) -> float:
        """计算两件衣物的相似度，返回 0.0~1.0"""
        ...


class MockSimilarityEngine(SimilarityEngine):
    """基于属性重叠的简化相似度计算"""

    WEIGHTS = {'category': 0.4, 'color': 0.3, 'style': 0.2, 'material': 0.1}

    def calculate_similarity(self, item_a: Dict, item_b: Dict) -> float:
        score = 0.0
        for attr, weight in self.WEIGHTS.items():
            a_val = item_a.get(attr)
            b_val = item_b.get(attr)
            if a_val and b_val and a_val == b_val:
                score += weight
        return round(min(1.0, score), 2)


class CLIPSimilarityEngine(SimilarityEngine):
    """基于 CLIP 模型的视觉相似度计算（预留）"""

    def calculate_similarity(self, item_a: Dict, item_b: Dict) -> float:
        raise NotImplementedError("CLIPSimilarityEngine not yet implemented")


# 全局实例（当前使用 mock，后续可替换为 CLIP）
engine = MockSimilarityEngine()