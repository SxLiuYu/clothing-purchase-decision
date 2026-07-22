# Combination Gap Calculator for Superpower 3
# Wardrobe ROI - 真实组合缺口计算

from typing import Dict, List, Optional, Set, Tuple
from collections import defaultdict
import math


class CombinationGapCalculator:
    """
    组合缺口计算器
    
    功能：
    - 基于衣橱图谱计算新衣激活组合
    - 评估场景覆盖度变化
    - 生成替代方案建议
    """
    
    # 权重配置
    WEIGHTS = {
        'combination_increment': 0.40,  # 组合增量权重
        'old_item_activation': 0.25,    # 旧衣激活率权重
        'scenario_coverage': 0.20,      # 场景覆盖权重
        'price_utility': 0.15          # 价格效用比权重
    }
    
    def __init__(self):
        self.scenario_definitions = {
            'formal': ['suit', 'dress_shirt', 'trousers', 'blazer', 'derby'],
            'casual': ['t-shirt', 'jeans', 'sneakers', 'hoodie', 'polo'],
            'sport': ['sportswear', 'running_shoes', 'shorts', 'sports_top'],
            'outdoor': ['jacket', 'boots', 'fleece', 'cargo'],
            'date': ['shirt', 'dress', 'heels', 'blazer'],
            'daily': ['casual_shirt', 'chino', 'loafers', 'cardigan']
        }
        
    def calculate_combination_increment(
        self,
        new_item: Dict,
        wardrobe_items: List[Dict],
        existing_combinations: List[Tuple[str, str]]
    ) -> Dict:
        """
        计算新衣物带来的组合增量
        
        1. 找出新衣物可以搭配的现有衣物
        2. 计算新增的搭配数量
        3. 评估组合多样性提升
        """
        if not wardrobe_items:
            return {
                'new_combinations': 0,
                'combinable_items': [],
                'diversity_delta': 0.0,
                'combination_score': 0
            }
        
        new_item_category = new_item.get('category', '')
        new_item_attributes = {
            'style': new_item.get('style', ''),
            'season': new_item.get('season', ''),
            'color': new_item.get('color', ''),
            'occasion': new_item.get('occasion', [])
        }
        
        combinable_items = []
        new_combination_count = 0
        
        # 检查每件现有衣物是否可以与新衣搭配
        for item in wardrobe_items:
            item_id = item.get('item_id', '')
            item_attributes = {
                'style': item.get('style', ''),
                'season': item.get('season', ''),
                'color': item.get('color', ''),
                'occasion': item.get('occasion', [])
            }
            
            if self._can_combine(new_item_attributes, item_attributes):
                combinable_items.append({
                    'item_id': item_id,
                    'category': item.get('category', ''),
                    'score': self._compatibility_score(new_item_attributes, item_attributes)
                })
                
                # 检查是否是新组合
                pair = tuple(sorted([new_item.get('item_id', 'new'), item_id]))
                if pair not in existing_combinations:
                    new_combination_count += 1
        
        # 计算多样性提升
        existing_diversity = len(set(c[0] for c in existing_combinations) | set(c[1] for c in existing_combinations))
        new_diversity = len(set([new_item.get('item_id', 'new')] + [c['item_id'] for c in combinable_items]))
        diversity_delta = (new_diversity - existing_diversity) / max(existing_diversity, 1)
        
        return {
            'new_combinations': new_combination_count,
            'combinable_items': combinable_items,
            'diversity_delta': round(diversity_delta, 2),
            'combination_score': self._combination_score(new_combination_count, len(wardrobe_items))
        }
    
    def calculate_old_item_activation(
        self,
        new_item: Dict,
        wardrobe_items: List[Dict],
        idle_items: List[str]
    ) -> Dict:
        """
        计算旧衣激活率
        
        新衣物可以激活多少件闲置衣物
        """
        if not idle_items:
            return {
                'reactivated_items': 0,
                'reactivated_ids': [],
                'activation_rate': 0.0
            }
        
        new_item_attributes = {
            'style': new_item.get('style', ''),
            'season': new_item.get('season', ''),
            'occasion': new_item.get('occasion', [])
        }
        
        reactivated_ids = []
        
        for item in wardrobe_items:
            if item.get('item_id') in idle_items:
                item_attributes = {
                    'style': item.get('style', ''),
                    'season': item.get('season', ''),
                    'occasion': item.get('occasion', [])
                }
                
                if self._can_combine(new_item_attributes, item_attributes):
                    reactivated_ids.append(item.get('item_id'))
        
        activation_rate = len(reactivated_ids) / max(len(idle_items), 1)
        
        return {
            'reactivated_items': len(reactivated_ids),
            'reactivated_ids': reactivated_ids,
            'activation_rate': round(activation_rate, 2)
        }
    
    def calculate_scenario_coverage(
        self,
        new_item: Dict,
        current_coverage: Dict[str, float],
        wardrobe_items: List[Dict]
    ) -> Dict:
        """
        计算场景覆盖变化
        
        新衣物填补了哪些场景缺口
        """
        item_occasions = set(new_item.get('occasion', []))
        
        coverage_delta = {}
        filled_gaps = []
        partial_gaps = []
        
        for scenario, required_items in self.scenario_definitions.items():
            current_scenario_items = [
                item for item in wardrobe_items 
                if any(occ in (item.get('occasion') or []) for occ in required_items)
            ]
            
            # 计算新衣是否填补场景缺口
            if item_occasions & set(required_items):
                # 评估填补程度
                new_contribution = len(item_occasions & set(required_items)) / max(len(required_items), 1)
                current_coverage_rate = current_coverage.get(scenario, 0.0)
                
                # 如果当前覆盖率低，新衣填补效果更明显
                if current_coverage_rate < 0.5:
                    coverage_delta[scenario] = new_contribution * (1 - current_coverage_rate)
                    filled_gaps.append(scenario)
                else:
                    coverage_delta[scenario] = new_contribution * 0.2
                    partial_gaps.append(scenario)
        
        # 计算总体覆盖提升
        total_delta = sum(coverage_delta.values())
        new_overall_coverage = {
            scenario: min(1.0, current_coverage.get(scenario, 0.0) + delta)
            for scenario, delta in coverage_delta.items()
        }
        
        return {
            'coverage_delta': {k: round(v, 2) for k, v in coverage_delta.items()},
            'filled_gaps': filled_gaps,
            'partial_gaps': partial_gaps,
            'new_overall_coverage': {k: round(v, 2) for k, v in new_overall_coverage.items()},
            'total_coverage_improvement': round(total_delta, 2)
        }
    
    def calculate_roi_score(
        self,
        new_item: Dict,
        wardrobe_items: List[Dict],
        existing_combinations: List[Tuple[str, str]],
        idle_items: List[str],
        current_coverage: Dict[str, float]
    ) -> Dict:
        """
        综合计算 ROI 评分
        
        组合增量 40% + 旧衣激活 25% + 场景覆盖 20% + 价格效用 15%
        """
        # 1. 组合增量
        combo_result = self.calculate_combination_increment(
            new_item, wardrobe_items, existing_combinations
        )
        
        # 2. 旧衣激活
        activation_result = self.calculate_old_item_activation(
            new_item, wardrobe_items, idle_items
        )
        
        # 3. 场景覆盖
        scenario_result = self.calculate_scenario_coverage(
            new_item, current_coverage, wardrobe_items
        )
        
        # 4. 价格效用
        price = new_item.get('price', 0)
        price_utility = self._calculate_price_utility(price, combo_result['new_combinations'])
        
        # 综合评分
        roi_score = (
            combo_result['combination_score'] * self.WEIGHTS['combination_increment'] +
            activation_result['activation_rate'] * 100 * self.WEIGHTS['old_item_activation'] +
            scenario_result['total_coverage_improvement'] * 100 * self.WEIGHTS['scenario_coverage'] +
            price_utility * self.WEIGHTS['price_utility']
        )
        
        roi_score = min(100.0, max(0.0, roi_score))
        
        # 推荐决策
        recommendation = 'recommend' if roi_score >= 72 else 'reconsider'
        
        return {
            'roi_score': round(roi_score, 1),
            'recommendation': recommendation,
            'breakdown': {
                'combination_increment': {
                    'score': combo_result['combination_score'],
                    'weight': self.WEIGHTS['combination_increment'],
                    'contribution': round(combo_result['combination_score'] * self.WEIGHTS['combination_increment'], 1)
                },
                'old_item_activation': {
                    'count': activation_result['reactivated_items'],
                    'rate': activation_result['activation_rate'],
                    'weight': self.WEIGHTS['old_item_activation'],
                    'contribution': round(activation_result['activation_rate'] * 100 * self.WEIGHTS['old_item_activation'], 1)
                },
                'scenario_coverage': {
                    'improvement': scenario_result['total_coverage_improvement'],
                    'weight': self.WEIGHTS['scenario_coverage'],
                    'contribution': round(scenario_result['total_coverage_improvement'] * 100 * self.WEIGHTS['scenario_coverage'], 1)
                },
                'price_utility': {
                    'score': price_utility,
                    'weight': self.WEIGHTS['price_utility'],
                    'contribution': round(price_utility * self.WEIGHTS['price_utility'], 1)
                }
            },
            'details': {
                'new_combinations': combo_result['new_combinations'],
                'reactivated_items': activation_result['reactivated_ids'],
                'filled_scenarios': scenario_result['filled_gaps'],
                'price': price
            }
        }
    
    def generate_alternative_suggestions(
        self,
        new_item: Dict,
        roi_result: Dict,
        wardrobe_items: List[Dict]
    ) -> List[Dict]:
        """
        生成替代方案建议
        
        当 ROI 较低时，提供替代购买建议
        """
        suggestions = []
        
        # 如果场景覆盖不足
        if roi_result['breakdown']['scenario_coverage']['improvement'] < 0.1:
            # 建议购买填补场景的衣物
            current_scenarios = set()
            for item in wardrobe_items:
                current_scenarios.update(item.get('occasion', []))
            
            for scenario, items in self.scenario_definitions.items():
                if scenario not in current_scenarios:
                    suggestions.append({
                        'item_category': items[0] if items else None,
                        'scenario': scenario,
                        'reason': 'increase_roi',
                        'suggestion': f'建议购买 {scenario} 场景的基础单品'
                    })
        
        # 如果组合增量不足
        if roi_result['details']['new_combinations'] < 3:
            # 建议购买百搭款
            suggestions.append({
                'item_category': 'neutral_accessory',
                'reason': 'increase_combinations',
                'suggestion': '建议购买中性色基础款，增加搭配灵活性'
            })
        
        return suggestions[:3]  # 最多返回3条建议
    
    def _can_combine(self, item1: Dict, item2: Dict) -> bool:
        """判断两件衣物是否可以搭配"""
        # 季节兼容性
        seasons1 = set((item1.get('season') or '').split(','))
        seasons2 = set((item2.get('season') or '').split(','))
        
        # 完全相反的季节不能搭配
        incompatible = ({'spring', 'fall'} & seasons1) and ({'summer', 'winter'} & seasons2)
        if incompatible:
            incompatible = ({'summer'} in seasons1 and {'winter'} in seasons2) or \
                          ({'winter'} in seasons1 and {'summer'} in seasons2)
        
        # 场合兼容性
        occasions1 = set(item1.get('occasion') or [])
        occasions2 = set(item2.get('occasion') or [])
        
        # 至少有一个共同场合
        if occasions1 and occasions2 and not (occasions1 & occasions2):
            # 但如果一件是通用场合，可以搭配
            if 'daily' not in occasions1 and 'daily' not in occasions2:
                return False
        
        return True
    
    def _compatibility_score(self, item1: Dict, item2: Dict) -> float:
        """计算搭配兼容度分数"""
        score = 50.0  # 基础分
        
        # 风格一致性
        if item1.get('style') == item2.get('style'):
            score += 15
        
        # 季节重叠
        seasons1 = set((item1.get('season') or '').split(','))
        seasons2 = set((item2.get('season') or '').split(','))
        season_overlap = len(seasons1 & seasons2)
        score += season_overlap * 10
        
        # 场合匹配
        occasions1 = set(item1.get('occasion') or [])
        occasions2 = set(item2.get('occasion') or [])
        if occasions1 & occasions2:
            score += 15
        
        return min(100.0, score)
    
    def _combination_score(self, new_count: int, total_items: int) -> float:
        """计算组合得分"""
        if total_items == 0:
            return 0
        
        # 理想情况：新衣能与 30% 的现有衣物搭配
        expected_count = total_items * 0.3
        ratio = new_count / max(expected_count, 1)
        
        return min(100.0, ratio * 70)
    
    def _calculate_price_utility(self, price: float, combinations: int) -> float:
        """计算价格效用比"""
        if price <= 0 or combinations <= 0:
            return 0
        
        # 理想情况：每10元换一个组合
        utility = (combinations * 10) / price
        
        return min(100.0, utility * 50)


# 全局实例
combination_calculator = CombinationGapCalculator()
