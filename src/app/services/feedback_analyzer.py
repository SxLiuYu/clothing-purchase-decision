# Continuous Feedback Analyzer for Superpower 2
# 动态体态档案 - 连续反馈模式识别

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import math


class ContinuousFeedbackAnalyzer:
    """
    连续反馈模式识别器
    
    功能：
    - 检测连续拒绝模式（默认阈值：3次）
    - 动态调整全局偏好权重
    - 触发体态档案重新校准
    """
    
    # 连续拒绝触发阈值
    CONSECUTIVE_REJECT_THRESHOLD = 3
    
    # 权重下降步长
    WEIGHT_DECAY_STEP = 0.15
    
    # 体重变化阈值（百分比）
    WEIGHT_CHANGE_THRESHOLD = 0.05
    
    # 敏感区域与版型偏好映射
    AREA_TO_FIT_MAPPING = {
        'waist': {'tight': 'loose', 'slim': 'regular'},
        'hip': {'tight': 'loose', 'slim': 'regular'},
        'shoulder': {'tight': 'loose', 'slim': 'regular'},
        'chest': {'tight': 'loose', 'slim': 'regular'},
        'thigh': {'tight': 'loose', 'slim': 'regular'},
        'arm': {'tight': 'loose', 'slim': 'regular'},
        'neck': {'tight': 'loose', 'slim': 'regular'},
    }
    
    def __init__(self):
        self.rejection_history: Dict[str, List[Dict]] = defaultdict(list)
        self.preference_weights: Dict[str, Dict] = {}
        self.last_weight_record: Optional[datetime] = None
        
    def analyze_consecutive_rejections(
        self, 
        user_id: str,
        feedback_records: List[Dict]
    ) -> Dict:
        """
        分析连续拒绝模式
        
        返回：
        - 连续拒绝次数
        - 受影响区域
        - 建议的版型调整
        - 是否需要全局权重下降
        """
        if not feedback_records:
            return {
                'consecutive_count': 0,
                'affected_areas': [],
                'suggested_adjustments': {},
                'needs_global_decay': False,
                'decay_reason': None
            }
        
        # 统计连续拒绝
        consecutive_count = 0
        affected_areas = set()
        suggested_adjustments = {}
        
        for record in feedback_records[-self.CONSECUTIVE_REJECT_THRESHOLD:]:
            if record.get('fit_feedback') in ['tight_waist', 'too_tight', 'slim_fit']:
                consecutive_count += 1
                if 'area' in record:
                    affected_areas.add(record['area'])
                    
        # 生成版型调整建议
        for area in affected_areas:
            if area in self.AREA_TO_FIT_MAPPING:
                current_fit = self.preference_weights.get(user_id, {}).get('fit_preferences', {}).get(area, 'slim')
                suggested_adjustments[area] = self.AREA_TO_FIT_MAPPING[area].get(current_fit, 'regular')
        
        # 判断是否需要全局权重下降
        needs_global_decay = consecutive_count >= self.CONSECUTIVE_REJECT_THRESHOLD
        
        return {
            'consecutive_count': consecutive_count,
            'affected_areas': list(affected_areas),
            'suggested_adjustments': suggested_adjustments,
            'needs_global_decay': needs_global_decay,
            'decay_reason': f'连续{consecutive_count}次拒绝，触发全局权重下降' if needs_global_decay else None
        }
    
    def apply_global_weight_decay(
        self,
        user_id: str,
        current_weights: Dict
    ) -> Dict:
        """
        应用全局权重下降
        
        当连续拒绝达到阈值时，降低修身款偏好权重
        """
        decay_factor = 1.0 - self.WEIGHT_DECAY_STEP
        
        # 降低修身偏好权重
        if 'slim_fit_preference' in current_weights:
            current_weights['slim_fit_preference'] *= decay_factor
        
        # 提高宽松款偏好权重
        if 'loose_fit_preference' not in current_weights:
            current_weights['loose_fit_preference'] = 0.3
        else:
            current_weights['loose_fit_preference'] = min(
                1.0, 
                current_weights['loose_fit_preference'] + self.WEIGHT_DECAY_STEP
            )
        
        # 记录权重变化
        self.preference_weights[user_id] = current_weights.copy()
        
        return {
            'updated_weights': current_weights,
            'decay_applied': True,
            'decay_factor': decay_factor
        }
    
    def check_weight_change(
        self,
        current_weight: float,
        recorded_weight: Optional[float],
        threshold: float = WEIGHT_CHANGE_THRESHOLD
    ) -> Tuple[bool, Optional[float]]:
        """
        检查体重变化是否超过阈值
        
        返回：
        - 是否需要重新校准
        - 变化百分比
        """
        if recorded_weight is None or recorded_weight == 0:
            return False, None
        
        change_ratio = abs(current_weight - recorded_weight) / recorded_weight
        
        if change_ratio > threshold:
            return True, round(change_ratio * 100, 1)
        
        return False, round(change_ratio * 100, 1)
    
    def trigger_profile_recalibration(
        self,
        user_id: str,
        body_profile: Dict,
        trigger_reason: str
    ) -> Dict:
        """
        触发体态档案重新校准
        
        当检测到：
        - 体重变化 > 5%
        - 连续拒绝达到阈值
        
        触发档案重新校准
        """
        recalibration_actions = []
        
        if 'weight_change' in trigger_reason:
            recalibration_actions.append({
                'action': 'recalculate_body_measurements',
                'reason': '体重显著变化',
                'priority': 'high'
            })
            
        if 'consecutive_rejection' in trigger_reason:
            recalibration_actions.append({
                'action': 'adjust_fit_preferences',
                'reason': '连续拒绝模式检测',
                'priority': 'medium'
            })
            recalibration_actions.append({
                'action': 'flag_for_review',
                'reason': '需要用户确认偏好变化',
                'priority': 'low'
            })
        
        # 生成新的推荐
        return {
            'recalibration_triggered': True,
            'trigger_reason': trigger_reason,
            'actions_required': recalibration_actions,
            'recommendations': self._generate_recalibration_recommendations(body_profile)
        }
    
    def _generate_recalibration_recommendations(self, body_profile: Dict) -> List[str]:
        """生成重新校准建议"""
        recommendations = []
        
        if body_profile.get('weight'):
            recommendations.append('建议重新测量身体尺寸')
            
        if body_profile.get('fit_preferences'):
            recommendations.append('建议审核并更新版型偏好')
            
        recommendations.append('下次穿搭时注意观察穿着感受')
        recommendations.append('如有需要可重新上传体态照片')
        
        return recommendations


class DynamicFitPreferenceEngine:
    """
    动态版型偏好引擎
    
    基于用户反馈持续更新版型偏好
    """
    
    def __init__(self):
        self.analyzer = ContinuousFeedbackAnalyzer()
        self.preference_cache: Dict[str, Dict] = {}
        
    def update_preference(
        self,
        user_id: str,
        feedback: Dict,
        body_profile: Dict
    ) -> Dict:
        """
        基于单次反馈更新偏好
        
        同时检查是否需要触发连续反馈分析
        """
        # 更新敏感区域
        sensitive_areas = set(body_profile.get('sensitive_areas', []))
        if feedback.get('visual_comfort'):
            sensitive_areas.add(feedback['visual_comfort'])
        if feedback.get('fit_feedback'):
            sensitive_areas.add(feedback['fit_feedback'])
        
        # 更新版型偏好
        fit_preferences = dict(body_profile.get('fit_preferences', {}))
        if feedback.get('fit_feedback'):
            item_id = feedback.get('item_id', 'global')
            fit_preferences[item_id] = feedback['fit_feedback']
        
        # 检查连续反馈模式
        feedback_history = self.preference_cache.get(user_id, {}).get('feedback_history', [])
        feedback_history.append(feedback)
        
        consecutive_analysis = self.analyzer.analyze_consecutive_rejections(
            user_id, 
            feedback_history
        )
        
        # 如果需要全局权重下降
        if consecutive_analysis['needs_global_decay']:
            current_weights = self.preference_cache.get(user_id, {}).get('weights', {})
            weight_update = self.analyzer.apply_global_weight_decay(user_id, current_weights)
        else:
            weight_update = {'decay_applied': False}
        
        # 更新缓存
        self.preference_cache[user_id] = {
            'feedback_history': feedback_history[-10:],  # 保留最近10条
            'sensitive_areas': sorted(sensitive_areas),
            'fit_preferences': fit_preferences,
            'weights': weight_update.get('updated_weights', {}),
            'last_update': datetime.utcnow().isoformat()
        }
        
        return {
            'updated_profile': {
                'sensitive_areas': sorted(sensitive_areas),
                'fit_preferences': fit_preferences
            },
            'consecutive_analysis': consecutive_analysis,
            'weight_update': weight_update,
            'needs_recalibration': consecutive_analysis['needs_global_decay']
        }
    
    def get_fit_score_adjustment(
        self,
        user_id: str,
        item_category: str,
        item_fit: str
    ) -> float:
        """
        获取版型评分调整
        
        根据用户偏好动态调整物品版型评分
        """
        cache = self.preference_cache.get(user_id, {})
        weights = cache.get('weights', {})
        
        # 获取该品类的宽松偏好权重
        loose_preference = weights.get('loose_fit_preference', 0.5)
        slim_preference = weights.get('slim_fit_preference', 0.5)
        
        adjustment = 0.0
        
        # 如果用户偏好宽松款，但物品是修身款，降低评分
        if item_fit == 'slim' and loose_preference > slim_preference:
            adjustment = -5.0 * (loose_preference - slim_preference)
        # 如果用户偏好修身款，但物品是宽松款，降低评分
        elif item_fit == 'loose' and slim_preference > loose_preference:
            adjustment = -5.0 * (slim_preference - loose_preference)
        # 如果物品符合偏好
        elif item_fit == 'loose' and loose_preference >= slim_preference:
            adjustment = 3.0
        elif item_fit == 'slim' and slim_preference >= loose_preference:
            adjustment = 3.0
            
        return round(adjustment, 1)


# 全局实例
feedback_analyzer = ContinuousFeedbackAnalyzer()
fit_preference_engine = DynamicFitPreferenceEngine()
