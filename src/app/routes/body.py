from fastapi import APIRouter
from app.models.schemas import BodyFeedbackRequest, UpdatedProfile
from app.services.store import store
from app.services.feedback_analyzer import fit_preference_engine

router = APIRouter()


@router.post('/feedback', response_model=dict)
def update_body_profile(payload: BodyFeedbackRequest):
    # 1. 基础反馈记录（保持向后兼容）
    user = store.get_or_create_user(payload.user_id)
    profile = user.setdefault('body_profile', {})
    sensitive_areas = set(profile.get('sensitive_areas', []))
    fit_preference = dict(profile.get('fit_preference', {}))
    if payload.fit_feedback:
        sensitive_areas.add(payload.fit_feedback)
        fit_preference[payload.item_id or 'global'] = payload.fit_feedback
    if payload.visual_comfort:
        sensitive_areas.add(payload.visual_comfort)
    profile['sensitive_areas'] = sorted(sensitive_areas)
    profile['fit_preference'] = fit_preference

    # 2. 调用 DynamicFitPreferenceEngine 实现连续反馈分析
    feedback_dict = payload.model_dump()
    engine_result = fit_preference_engine.update_preference(
        user_id=payload.user_id,
        feedback=feedback_dict,
        body_profile=profile,
    )

    # 3. 合并引擎结果到用户档案
    updated_profile = engine_result.get('updated_profile', {})
    if 'sensitive_areas' in updated_profile:
        profile['sensitive_areas'] = updated_profile['sensitive_areas']
    if 'fit_preferences' in updated_profile:
        # 引擎用 fit_preferences（复数），store 用 fit_preference（单数）
        profile['fit_preference'].update(updated_profile['fit_preferences'])

    consecutive_analysis = engine_result.get('consecutive_analysis', {})
    weight_update = engine_result.get('weight_update', {})

    return {
        'decision_id': f"feedback:{payload.user_id}:{payload.item_id}",
        'updated_profile': UpdatedProfile(**{
            'sensitive_areas': profile.get('sensitive_areas', []),
            'fit_preference': profile.get('fit_preference', {}),
        }).model_dump(),
        'consecutive_analysis': consecutive_analysis,
        'weight_update': weight_update,
        'needs_recalibration': engine_result.get('needs_recalibration', False),
        'note': 'feedback loop marked; continuous feedback analyzer engaged',
    }
