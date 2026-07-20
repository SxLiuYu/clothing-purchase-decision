# Multi-Objective Optimizer for Superpower 1
# 穿搭决策中枢 - 多目标优化

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import math


class ObjectiveType(Enum):
    AESTHETIC = "aesthetic"
    REUSE = "reuse"
    SCENARIO = "scenario"
    BODY_FIT = "body_fit"


@dataclass
class OptimizationResult:
    score: float
    objectives_met: Dict[str, float]
    weights: Dict[str, float]
    pareto_dominant: bool = False


class MultiObjectiveOptimizer:
    """
    多目标优化器
    
    优化目标：
    - 美学评分
    - 衣橱复用率
    - 场景覆盖率
    - 身体适配度
    """
    
    # 默认权重
    DEFAULT_WEIGHTS = {
        ObjectiveType.AESTHETIC: 0.30,
        ObjectiveType.REUSE: 0.25,
        ObjectiveType.SCENARIO: 0.25,
        ObjectiveType.BODY_FIT: 0.20
    }
    
    # 目标阈值
    TARGETS = {
        ObjectiveType.AESTHETIC: 85.0,
        ObjectiveType.REUSE: 0.7,
        ObjectiveType.SCENARIO: 0.8,
        ObjectiveType.BODY_FIT: 0.9
    }
    
    def __init__(self, custom_weights: Optional[Dict] = None):
        self.weights = custom_weights or self.DEFAULT_WEIGHTS.copy()
        self._normalize_weights()
    
    def _normalize_weights(self):
        """标准化权重"""
        total = sum(self.weights.values())
        if total > 0:
            for key in self.weights:
                self.weights[key] /= total
    
    def optimize_outfit(
        self,
        outfit_candidates: List[Dict],
        user_profile: Dict,
        weather: Dict,
        constraints: Dict
    ) -> List[Dict]:
        """
        优化穿搭方案
        
        对候选方案进行多目标优化排序
        """
        if not outfit_candidates:
            return []
        
        optimized = []
        
        for candidate in outfit_candidates:
            # 计算每个目标的得分
            aesthetic_score = self._calculate_aesthetic_score(candidate)
            reuse_score = self._calculate_reuse_score(candidate, user_profile)
            scenario_score = self._calculate_scenario_score(candidate, constraints)
            body_fit_score = self._calculate_body_fit_score(candidate, user_profile)
            
            # 综合得分
            total_score = (
                aesthetic_score * self.weights[ObjectiveType.AESTHETIC] +
                reuse_score * self.weights[ObjectiveType.REUSE] +
                scenario_score * self.weights[ObjectiveType.SCENARIO] +
                body_fit_score * self.weights[ObjectiveType.BODY_FIT]
            )
            
            # 检查Pareto最优
            pareto_dominant = self._check_pareto_dominant(
                aesthetic_score, reuse_score, scenario_score, body_fit_score
            )
            
            result = OptimizationResult(
                score=total_score,
                objectives_met={
                    'aesthetic': aesthetic_score,
                    'reuse': reuse_score,
                    'scenario': scenario_score,
                    'body_fit': body_fit_score
                },
                weights=self.weights,
                pareto_dominant=pareto_dominant
            )
            
            optimized_candidate = candidate.copy()
            optimized_candidate['optimization'] = result
            optimized.append(optimized_candidate)
        
        # 按总分排序
        optimized.sort(key=lambda x: x['optimization'].score, reverse=True)
        
        return optimized
    
    def _calculate_aesthetic_score(self, candidate: Dict) -> float:
        """计算美学评分"""
        # 基于颜色搭配、风格一致性、比例搭配等
        items = candidate.get('items', [])
        
        if not items:
            return 50.0
        
        total_score = 0.0
        count = 0
        
        for item in items:
            score = 0.0
            
            # 风格一致性
            styles = [i.get('style', '') for i in items]
            style_match = len([s for s in styles if s]) / len(styles) if styles else 0
            score += style_match * 30
            
            # 颜色搭配（简化处理）
            colors = [i.get('color', '') for i in items]
            if len(set(colors)) <= 2:  # 1-2 种颜色为佳
                score += 25
            
            # 品类搭配
            categories = [i.get('category', '') for i in items]
            if 'outwear' in categories and 'bottom' in categories:
                score += 20
            if len(categories) >= 2:
                score += 15
            
            total_score += min(100.0, score)
            count += 1
        
        return total_score / count if count > 0 else 50.0
    
    def _calculate_reuse_score(self, candidate: Dict, user_profile: Dict) -> float:
        """计算衣橱复用率"""
        wardrobe_graph = user_profile.get('wardrobe_graph', {})
        nodes = wardrobe_graph.get('nodes', [])
        
        items = candidate.get('items', [])
        used_item_ids = [i.get('item_id') for i in items if i.get('item_id')]
        
        if not nodes:
            return 0.5  # 无衣橱时给予中等分数
        
        # 计算已有衣橱中被使用的比例
        used_count = sum(1 for node in nodes if node.get('item_id') in used_item_ids)
        reuse_rate = used_count / len(nodes)
        
        # 加权：鼓励高复用
        return min(1.0, reuse_rate * 1.5)
    
    def _calculate_scenario_score(self, candidate: Dict, constraints: Dict) -> float:
        """计算场景覆盖率"""
        items = candidate.get('items', [])
        occasions = set()
        
        for item in items:
            item_occasions = item.get('occasion', [])
            if isinstance(item_occasions, list):
                occasions.update(item_occasions)
            elif isinstance(item_occasions, str):
                occasions.add(item_occasions)
        
        constraint_occasion = constraints.get('occasion', '')
        if constraint_occasion:
            occasions.add(constraint_occasion)
        
        # 评估场景匹配度
        if not occasions:
            return 0.5
        
        # 理想情况：覆盖 2-3 个场景
        if 2 <= len(occasions) <= 3:
            return 0.9
        elif len(occasions) == 1:
            return 0.7
        else:
            return min(1.0, 0.8 + (len(occasions) - 3) * 0.05)
    
    def _calculate_body_fit_score(self, candidate: Dict, user_profile: Dict) -> float:
        """计算身体适配度"""
        fit_preferences = user_profile.get('fit_preferences', {})
        sensitive_areas = set(user_profile.get('sensitive_areas', []))
        
        items = candidate.get('items', [])
        if not items:
            return 0.5
        
        total_score = 0.0
        
        for item in items:
            item_fit = item.get('fit_feedback', 'comfortable')
            item_id = item.get('item_id', '')
            
            # 检查该物品的版型偏好
            item_preference = fit_preferences.get(item_id, 'comfortable')
            
            # 计算匹配度
            if item_fit == item_preference:
                total_score += 1.0
            elif item_fit in ['tight_waist', 'exposed_belly'] and item_preference in ['loose', 'relaxed']:
                total_score += 0.6
            elif item_fit in ['comfortable', 'relaxed'] and item_preference in ['tight', 'slim']:
                total_score += 0.6
            else:
                total_score += 0.8
        
        return total_score / len(items)
    
    def _check_pareto_dominant(
        self, 
        aesthetic: float, 
        reuse: float, 
        scenario: float, 
        body_fit: float
    ) -> bool:
        """
        检查该方案是否在Pareto前沿
        
        对于简化处理，只有当所有目标都达到理想值时才算Pareto最优
        """
        scores = [aesthetic, reuse * 100, scenario * 100, body_fit * 100]
        targets = [self.TARGETS[ObjectiveType.AESTHETIC], 
                   self.TARGETS[ObjectiveType.REUSE] * 100,
                   self.TARGETS[ObjectiveType.SCENARIO] * 100,
                   self.TARGETS[ObjectiveType.BODY_FIT] * 100]
        
        # 至少有 3 项接近目标
        near_target = sum(1 for s, t in zip(scores, targets) if abs(s - t) < 15)
        
        return near_target >= 3
    
    def adjust_weights(
        self,
        feedback: str,
        current_weights: Optional[Dict] = None
    ) -> Dict:
        """
        基于用户反馈调整权重
        """
        weights = current_weights or self.DEFAULT_WEIGHTS.copy()
        
        if feedback == 'more_aesthetic':
            weights[ObjectiveType.AESTHETIC] = min(0.5, weights[ObjectiveType.AESTHETIC] + 0.1)
        elif feedback == 'more_reuse':
            weights[ObjectiveType.REUSE] = min(0.4, weights[ObjectiveType.REUSE] + 0.1)
        elif feedback == 'more_scenario':
            weights[ObjectiveType.SCENARIO] = min(0.4, weights[ObjectiveType.SCENARIO] + 0.1)
        elif feedback == 'more_body_fit':
            weights[ObjectiveType.BODY_FIT] = min(0.35, weights[ObjectiveType.BODY_FIT] + 0.1)
        
        self._normalize_weights()
        return weights.copy()


class ParetoFrontOptimizer:
    """
    Pareto 前沿优化器
    
    用于找出所有非劣解
    """
    
    def __init__(self):
        self.optimizer = MultiObjectiveOptimizer()
    
    def find_pareto_front(
        self,
        candidates: List[Dict],
        user_profile: Dict,
        weather: Dict,
        constraints: Dict
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        找出Pareto前沿
        
        返回：
        - Pareto 前沿解
        - 被支配的解
        """
        optimized = self.optimizer.optimize_outfit(
            candidates, user_profile, weather, constraints
        )
        
        pareto_front = []
        dominated = []
        
        for candidate in optimized:
            if candidate.get('optimization', {}).get('pareto_dominant', False):
                pareto_front.append(candidate)
            else:
                dominated.append(candidate)
        
        return pareto_front, dominated


# 全局实例
optimizer = MultiObjectiveOptimizer()
pareto_optimizer = ParetoFrontOptimizer()
