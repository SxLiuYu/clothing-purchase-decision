from typing import Dict, List, Optional
from app.services.social_fetcher import fetcher
from app.services.item_analyzer import analyzer


class SocialRecommendationEngine:
    """
    社媒推荐引擎

    排序：综合分 = 可复现度 × 匹配度 × 正向情感分
    """

    def __init__(self, fetcher, analyzer):
        self.fetcher = fetcher
        self.analyzer = analyzer

    def recommend(
        self,
        user_id: str,
        body_profile: Dict,
        occasion: str,
        limit: int = 5,
    ) -> Dict:
        face_shape = body_profile.get('face_shape', '')
        body_shape = body_profile.get('body_shape', '')
        skin_tone = body_profile.get('skin_tone', '')

        # 获取社媒帖子
        posts = self.fetcher.fetch_posts(face_shape, body_shape, skin_tone, occasion, limit)

        recommendations = []
        for post in posts:
            # 特征匹配度计算
            match_score = self._calculate_match_score(post, face_shape, body_shape, skin_tone)

            # 可复现度（基于帖子标签数量估算）
            reproducibility = self._calculate_reproducibility(post, body_profile)

            # 正向情感分
            sentiment = post.get('sentiment', 0.5)

            # 综合分 = 可复现度 × 匹配度 × 正向情感分
            score = round(reproducibility * match_score * sentiment * 100, 1)

            # 分析单品
            items = self.analyzer.analyze_items(post)

            recommendations.append({
                'rank': 0,
                'score': score,
                'match_score': round(match_score, 2),
                'reproducibility': round(reproducibility, 2),
                'sentiment': round(sentiment, 2),
                'post': {
                    'post_id': post.get('post_id', ''),
                    'title': post.get('title', ''),
                    'source': post.get('source', 'mock'),
                    'author': post.get('author', ''),
                    'image_url': post.get('image_url'),
                },
                'items': items,
                'rationale': self._generate_rationale(post, face_shape, body_shape, skin_tone),
            })

        # 按综合分排序
        recommendations.sort(key=lambda r: -r['score'])
        for rank, rec in enumerate(recommendations, 1):
            rec['rank'] = rank

        return {
            'user_id': user_id,
            'recommendations': recommendations[:limit],
            'total_count': len(recommendations),
        }

    def _calculate_match_score(
        self, post: Dict, face_shape: str, body_shape: str, skin_tone: str
    ) -> float:
        score = 0.5  # 基础分
        # 脸型匹配 +0.2
        if face_shape and post.get('face_shape') == face_shape:
            score += 0.2
        # 体型匹配 +0.2
        if body_shape and post.get('body_shape') == body_shape:
            score += 0.2
        # 肤色匹配 +0.1
        if skin_tone and post.get('skin_tone') == skin_tone:
            score += 0.1
        return min(1.0, score)

    def _calculate_reproducibility(self, post: Dict, body_profile: Dict) -> float:
        # 简化：基于帖子标签数量估算可复现度
        tags = post.get('tags', [])
        return min(1.0, max(0.3, 1.0 - len(tags) * 0.08))

    def _generate_rationale(
        self, post: Dict, face_shape: str, body_shape: str, skin_tone: str
    ) -> str:
        parts = []
        if face_shape and post.get('face_shape') == face_shape:
            parts.append(f'同脸型（{face_shape}）')
        if body_shape and post.get('body_shape') == body_shape:
            parts.append(f'同体型（{body_shape}）')
        if skin_tone and post.get('skin_tone') == skin_tone:
            parts.append(f'同肤色（{skin_tone}）')
        if not parts:
            return '热门穿搭推荐'
        return ' + '.join(parts)


# 全局实例
engine = SocialRecommendationEngine(fetcher, analyzer)