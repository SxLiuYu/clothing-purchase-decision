# Superpower 修复验证测试

import pytest
from src.app.services.feedback_analyzer import (
    ContinuousFeedbackAnalyzer,
    DynamicFitPreferenceEngine
)
from src.app.services.combination_calculator import CombinationGapCalculator
from src.app.services.multi_objective_optimizer import MultiObjectiveOptimizer, ObjectiveType


class TestSuperpower2ContinuousFeedback:
    """Superpower 2: Dynamic Body Profile - Continuous Feedback Tests"""
    
    def test_consecutive_rejection_detection(self):
        analyzer = ContinuousFeedbackAnalyzer()
        
        feedback_records = [
            {'fit_feedback': 'tight_waist', 'area': 'waist'},
            {'fit_feedback': 'too_tight', 'area': 'waist'},
            {'fit_feedback': 'slim_fit', 'area': 'waist'},
        ]
        
        result = analyzer.analyze_consecutive_rejections('user_001', feedback_records)
        
        assert result['consecutive_count'] == 3
        assert result['needs_global_decay'] == True
        assert 'waist' in result['affected_areas']
    
    def test_global_weight_decay(self):
        analyzer = ContinuousFeedbackAnalyzer()
        
        current_weights = {
            'slim_fit_preference': 0.8,
            'loose_fit_preference': 0.2
        }
        
        result = analyzer.apply_global_weight_decay('user_001', current_weights)
        
        assert result['decay_applied'] == True
        assert result['updated_weights']['slim_fit_preference'] < 0.8
        assert result['updated_weights']['loose_fit_preference'] > 0.2
    
    def test_weight_change_detection(self):
        analyzer = ContinuousFeedbackAnalyzer()
        
        needs_recal, ratio = analyzer.check_weight_change(85, 80, 0.05)
        assert needs_recal == True
        assert ratio > 5
        
        needs_recal, ratio = analyzer.check_weight_change(81, 80, 0.05)
        assert needs_recal == False
    
    def test_profile_recalibration_trigger(self):
        analyzer = ContinuousFeedbackAnalyzer()
        
        body_profile = {
            'weight': 75,
            'fit_preferences': {'waist': 'slim'}
        }
        
        result = analyzer.trigger_profile_recalibration(
            'user_001', 
            body_profile, 
            'consecutive_rejection'
        )
        
        assert result['recalibration_triggered'] == True
        assert len(result['actions_required']) > 0


class TestSuperpower3CombinationGap:
    """Superpower 3: Wardrobe ROI - Combination Gap Tests"""
    
    def test_combination_increment_calculation(self):
        calculator = CombinationGapCalculator()
        
        new_item = {
            'item_id': 'new_001',
            'category': 'blazer',
            'style': 'formal',
            'season': 'fall',
            'occasion': ['formal', 'daily']
        }
        
        wardrobe_items = [
            {'item_id': 'item_001', 'style': 'formal', 'season': 'fall', 'occasion': ['formal']},
            {'item_id': 'item_002', 'style': 'casual', 'season': 'summer', 'occasion': ['casual']},
        ]
        
        result = calculator.calculate_combination_increment(
            new_item, wardrobe_items, []
        )
        
        assert 'new_combinations' in result
        assert 'combination_score' in result
    
    def test_old_item_activation(self):
        calculator = CombinationGapCalculator()
        
        new_item = {
            'item_id': 'new_001',
            'style': 'formal',
            'season': 'fall',
            'occasion': ['formal']
        }
        
        wardrobe_items = [
            {'item_id': 'idle_001', 'style': 'formal', 'season': 'fall', 'occasion': ['formal']},
            {'item_id': 'idle_002', 'style': 'casual', 'season': 'summer', 'occasion': ['casual']},
        ]
        
        result = calculator.calculate_old_item_activation(
            new_item, wardrobe_items, ['idle_001', 'idle_002']
        )
        
        assert 'reactivated_items' in result
        assert 'activation_rate' in result
    
    def test_scenario_coverage_calculation(self):
        calculator = CombinationGapCalculator()
        
        new_item = {
            'item_id': 'new_001',
            'occasion': ['formal', 'date']
        }
        
        current_coverage = {
            'formal': 0.3,
            'casual': 0.8,
            'sport': 0.0
        }
        
        result = calculator.calculate_scenario_coverage(
            new_item, current_coverage, []
        )
        
        assert 'coverage_delta' in result
        assert 'filled_gaps' in result
        assert 'new_overall_coverage' in result
    
    def test_roi_score_calculation(self):
        calculator = CombinationGapCalculator()
        
        new_item = {
            'item_id': 'new_001',
            'category': 'blazer',
            'style': 'formal',
            'season': 'fall',
            'occasion': ['formal', 'daily'],
            'price': 500
        }
        
        wardrobe_items = [
            {'item_id': 'item_001', 'style': 'formal', 'season': 'fall', 'occasion': ['formal']},
        ]
        
        result = calculator.calculate_roi_score(
            new_item, wardrobe_items, [], [], {}
        )
        
        assert 'roi_score' in result
        assert 'recommendation' in result
        assert result['roi_score'] >= 0
        assert result['recommendation'] in ['recommend', 'reconsider']
    
    def test_alternative_suggestions(self):
        calculator = CombinationGapCalculator()
        
        new_item = {'item_id': 'new_001', 'occasion': ['formal']}
        roi_result = {
            'breakdown': {'scenario_coverage': {'improvement': 0.05}},
            'details': {'new_combinations': 1}
        }
        
        suggestions = calculator.generate_alternative_suggestions(
            new_item, roi_result, []
        )
        
        assert isinstance(suggestions, list)


class TestSuperpower1MultiObjectiveOptimization:
    """Superpower 1: Style Decision Copilot - Multi-Objective Tests"""
    
    def test_optimizer_initialization(self):
        optimizer = MultiObjectiveOptimizer()
        
        assert optimizer.weights is not None
        assert sum(optimizer.weights.values()) == pytest.approx(1.0)
    
    def test_outfit_optimization(self):
        optimizer = MultiObjectiveOptimizer()
        
        candidates = [
            {
                'items': [
                    {'category': 'outwear', 'style': 'formal', 'fit_feedback': 'comfortable'},
                    {'category': 'bottom', 'style': 'formal', 'fit_feedback': 'comfortable'},
                ]
            },
            {
                'items': [
                    {'category': 'hoodie', 'style': 'casual', 'fit_feedback': 'loose'},
                    {'category': 'jeans', 'style': 'casual', 'fit_feedback': 'loose'},
                ]
            }
        ]
        
        user_profile = {
            'fit_preferences': {},
            'wardrobe_graph': {'nodes': []}
        }
        
        weather = {'temperature': 20}
        constraints = {'occasion': 'formal'}
        
        result = optimizer.optimize_outfit(candidates, user_profile, weather, constraints)
        
        assert len(result) == 2
        assert result[0]['optimization'].score >= result[1]['optimization'].score
    
    def test_weight_adjustment(self):
        optimizer = MultiObjectiveOptimizer()
        
        new_weights = optimizer.adjust_weights('more_aesthetic')
        
        assert ObjectiveType.AESTHETIC in new_weights
        assert new_weights[ObjectiveType.AESTHETIC] > optimizer.DEFAULT_WEIGHTS[ObjectiveType.AESTHETIC]
    
    def test_pareto_dominance(self):
        optimizer = MultiObjectiveOptimizer()
        
        good_result = optimizer._check_pareto_dominant(90, 0.8, 0.9, 0.95)
        bad_result = optimizer._check_pareto_dominant(50, 0.3, 0.4, 0.5)
        
        assert good_result == True
        assert bad_result == False


class TestIntegration:
    """Integration Tests"""
    
    def test_full_feedback_loop(self):
        analyzer = ContinuousFeedbackAnalyzer()
        
        feedback_records = [
            {'fit_feedback': 'tight_waist', 'area': 'waist'},
            {'fit_feedback': 'too_tight', 'area': 'waist'},
            {'fit_feedback': 'slim_fit', 'area': 'waist'},
        ]
        
        result = analyzer.analyze_consecutive_rejections('user_001', feedback_records)
        
        if result['needs_global_decay']:
            weights = {'slim_fit_preference': 0.8, 'loose_fit_preference': 0.2}
            decay_result = analyzer.apply_global_weight_decay('user_001', weights)
            assert decay_result['decay_applied'] == True
    
    def test_wardrobe_roi_integration(self):
        calculator = CombinationGapCalculator()
        
        new_item = {
            'item_id': 'new_blazer',
            'category': 'blazer',
            'style': 'formal',
            'season': 'fall',
            'occasion': ['formal', 'daily'],
            'price': 800
        }
        
        wardrobe_items = [
            {'item_id': 'trouser_001', 'style': 'formal', 'season': 'fall', 'occasion': ['formal']},
            {'item_id': 'shirt_001', 'style': 'formal', 'season': 'fall', 'occasion': ['formal', 'casual']},
            {'item_id': 'tshirt_001', 'style': 'casual', 'season': 'summer', 'occasion': ['casual']},
        ]
        
        roi_result = calculator.calculate_roi_score(
            new_item, wardrobe_items, [], ['tshirt_001'], {'formal': 0.5, 'casual': 0.8}
        )
        
        assert roi_result['roi_score'] > 0
        assert roi_result['details']['new_combinations'] >= 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
