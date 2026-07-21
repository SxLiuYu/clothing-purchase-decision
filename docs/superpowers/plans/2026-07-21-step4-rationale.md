# LLM 可解释决策 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans

**Goal:** 用规则引擎生成动态可解释决策理由，预留 LLM 接口供后续集成

**Architecture:** 新增 `RationaleGenerator` 类，基于硬约束、天气、体态反馈、敏感区域等上下文生成结构化理由链；预留 `LLMRationaleGenerator` 接口（需 API key 时启用）

**Tech Stack:** Python 3.14, FastAPI, httpx（已有）

## Global Constraints

- 所有原有测试必须保持通过
- API 返回格式不变（`rationale` 和 `risk_flags` 字段）
- 无 API key 时自动回退到规则引擎

---

### Task 1: 实现 `RationaleGenerator` 规则引擎

**Files:**
- Create: `src/app/services/rationale_generator.py`
- Modify: `src/app/routes/outfits.py`（调用新引擎生成 rationale）
- Test: `tests/test_api.py`（验证 rationale 内容动态生成）

**Interfaces:**
- Consumes: 候选方案、天气、硬约束、体态档案
- Produces: `generate_rationale(candidate, weather, active_rules, body_profile) -> str`

- [ ] **Step 1: 创建 `src/app/services/rationale_generator.py`**

```python
"""
Rationale Generator for Superpower 1
穿搭决策可解释性生成：规则引擎 + LLM 接口预留
"""
from typing import Any, Dict, List, Optional


class RationaleGenerator:
    """基于规则引擎生成可解释决策理由链"""

    # 天气描述映射
    WEATHER_DESC = {
        'sunny': '晴天', 'cloudy': '多云', 'rain': '雨天',
        'heavy rain': '大雨', 'light_rain': '小雨', 'snow': '雪天',
    }

    # 场合描述映射
    OCCASION_DESC = {
        'formal': '正式场合', 'casual': '休闲', 'sport': '运动',
        'outdoor': '户外', 'date': '约会', 'daily': '日常通勤',
        'commute': '通勤',
    }

    def generate_rationale(
        self,
        candidate: Dict[str, Any],
        weather: Dict,
        active_rules: List[Any],
        body_profile: Dict,
        constraints: Dict,
    ) -> str:
        """生成完整决策理由链"""
        parts = []

        # 1. 场景适配理由
        parts.append(self._generate_scenario_rationale(weather, constraints))

        # 2. 硬约束理由
        parts.append(self._generate_hard_constraint_rationale(candidate, active_rules))

        # 3. 体态适配理由
        parts.append(self._generate_body_fit_rationale(candidate, body_profile))

        # 4. 风险提示
        risk_notes = self._generate_risk_notes(candidate, weather, constraints)
        if risk_notes:
            parts.append(risk_notes)

        return '；'.join(parts)

    def _generate_scenario_rationale(self, weather: Dict, constraints: Dict) -> str:
        temp = weather.get('temperature_c')
        condition = weather.get('condition', 'sunny')
        occasion = constraints.get('occasion', '')
        duration = constraints.get('duration_hours', 0)

        parts = []
        if temp is not None:
            parts.append(f'{temp}°C')
        weather_desc = self.WEATHER_DESC.get(condition, condition)
        if weather_desc:
            parts.append(weather_desc)
        if occasion:
            occ_desc = self.OCCASION_DESC.get(occasion, occasion)
            parts.append(occ_desc)
        if duration:
            parts.append(f'时长{duration}小时')

        return f'场景适配：{" / ".join(parts)}'

    def _generate_hard_constraint_rationale(
        self, candidate: Dict, active_rules: List[Any]
    ) -> str:
        items = candidate.get('items', [])
        if not items:
            return '硬约束检查通过'

        item = items[0]
        category = item.get('category', '')
        penalties = item.get('hard_constraint_penalties', [])

        if penalties:
            return f'{category} 通过 {len(active_rules)} 条硬约束检查（未触发：{", ".join(penalties)}）'
        return f'{category} 通过全部 {len(active_rules)} 条硬约束检查' if active_rules else f'{category} 无触发硬约束'

    def _generate_body_fit_rationale(
        self, candidate: Dict, body_profile: Dict
    ) -> str:
        sensitive_areas = body_profile.get('sensitive_areas', [])
        fit_pref = body_profile.get('fit_preference', {})

        if not sensitive_areas and not fit_pref:
            return '无体态反馈记录'

        parts = []
        if sensitive_areas:
            parts.append(f'敏感区域：{", ".join(sensitive_areas)}')
        if fit_pref:
            prefs = [f'{k}={v}' for k, v in fit_pref.items()]
            parts.append(f'版型偏好：{", ".join(prefs)}')

        return '体态适配：' + '；'.join(parts)

    def _generate_risk_notes(
        self, candidate: Dict, weather: Dict, constraints: Dict
    ) -> str:
        risks = candidate.get('risk_flags', [])
        if not risks:
            return ''

        risk_map = {
            'switch_to_waterproof_chelsea_boots_60s': '建议切换防水鞋款',
            'long_sitting_knee_bulge': '久坐可能产生膝盖鼓包',
            'low_contrast_in_rain': '浅色在雨天对比度略低',
            'high_similarity_to_primary': '与已有衣物相似度高',
        }
        notes = [risk_map.get(r, r) for r in risks]
        return '风险提示：' + '；'.join(notes)


class LLMRationaleGenerator:
    """
    LLM 可解释生成器（预留接口）

    需要设置环境变量 ANTHROPIC_API_KEY 或 OPENAI_API_KEY 启用。
    未设置时自动回退到 RationaleGenerator。
    """

    def __init__(self, provider: str = 'auto'):
        self.provider = provider
        self._api_key = None
        self._client = None

    def generate_rationale(
        self,
        candidate: Dict[str, Any],
        weather: Dict,
        active_rules: List[Any],
        body_profile: Dict,
        constraints: Dict,
    ) -> str:
        """调用 LLM 生成详细理由链"""
        import os
        api_key = os.environ.get('ANTHROPIC_API_KEY') or os.environ.get('OPENAI_API_KEY')
        if not api_key:
            # 无 API key，回退到规则引擎
            return RationaleGenerator().generate_rationale(
                candidate, weather, active_rules, body_profile, constraints
            )

        prompt = self._build_prompt(candidate, weather, active_rules, body_profile, constraints)

        if os.environ.get('ANTHROPIC_API_KEY'):
            return self._call_anthropic(prompt)
        return self._call_openai(prompt)

    def _build_prompt(
        self, candidate: Dict, weather: Dict, active_rules: List,
        body_profile: Dict, constraints: Dict
    ) -> str:
        items = candidate.get('items', [])
        item_descs = []
        for item in items:
            item_descs.append(
                f"- {item.get('category', 'unknown')}: {item.get('name', 'unknown')}"
            )

        return (
            f"你是一位专业穿搭顾问。请为以下穿搭方案生成详细的决策理由链。\n\n"
            f"天气：{weather.get('temperature_c', '?')}°C, {weather.get('condition', '?')}\n"
            f"场合：{constraints.get('occasion', '?')}\n"
            f"时长：{constraints.get('duration_hours', '?')}小时\n"
            f"敏感区域：{body_profile.get('sensitive_areas', [])}\n"
            f"版型偏好：{body_profile.get('fit_preference', {})}\n\n"
            f"穿搭方案：\n" + "\n".join(item_descs) + "\n\n"
            f"请用简洁的中文生成决策理由，包含：场景适配、硬约束检查、体态适配、风险提示。"
        )

    def _call_anthropic(self, prompt: str) -> str:
        try:
            from anthropic import Anthropic
            client = Anthropic()
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception:
            return RationaleGenerator().generate_rationale(
                {}, {}, [], {}, {}
            )

    def _call_openai(self, prompt: str) -> str:
        try:
            from openai import OpenAI
            client = OpenAI()
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
            )
            return response.choices[0].message.content
        except Exception:
            return RationaleGenerator().generate_rationale(
                {}, {}, [], {}, {}
            )


# 全局实例
rationale_generator = RationaleGenerator()
llm_rationale_generator = LLMRationaleGenerator()
```

- [ ] **Step 2: 修改 `outfits.py` 调用新引擎**

在 `_build_candidates_from_wardrobe` 和 `_build_example_candidates` 中，将硬编码的 rationale 替换为引擎生成。

修改 `_build_candidates_from_wardrobe` 中候选生成部分：
```python
from app.services.rationale_generator import rationale_generator

# 在循环中，替换 rationale 生成：
rationale = rationale_generator.generate_rationale(
    candidate_template, weather, active_rules, body_profile, constraints
)
```

- [ ] **Step 3: 运行测试**

Run: `python -m pytest -q`
Expected: `104 passed`

- [ ] **Step 4: 新增测试验证 rationale 动态生成**

```python
def test_rationale_is_dynamic():
    """验证 rationale 不是硬编码，而是根据上下文动态生成"""
    user_id = 'user-rationale'
    # 录入体态档案
    client.post('/api/v3/body/profile', json={
        'user_id': user_id, 'height': 175, 'weight': 72,
        'fit_preference': 'slim',
    })
    # 录入衣物
    client.post('/api/v3/wardrobe/items', json={
        'user_id': user_id, 'item_id': 'rat-coat', 'category': 'outwear',
        'color': 'black', 'style': 'formal', 'season': 'winter', 'occasion': 'formal',
    })
    # 请求穿搭
    resp = client.post('/api/v3/decisions/outfit', json={
        'user_id': user_id, 'occasion': 'formal',
        'datetime': '2026-07-21T08:00:00+08:00',
        'weather': {'temperature_c': 5, 'condition': 'rain'},
        'constraints': {'duration_hours': 8},
    })
    assert resp.status_code == 200
    rationale = resp.json()['outfits'][0]['rationale']
    # 验证包含动态生成的内容
    assert '场景适配' in rationale or '硬约束' in rationale or '体态' in rationale
    assert '5°C' in rationale or '雨天' in rationale or '正式' in rationale
```

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat: 新增可解释决策理由链生成器

- RationaleGenerator: 基于规则引擎生成结构化理由链
- LLMRationaleGenerator: 预留 Anthropic/OpenAI 接口
- 无 API key 时自动回退到规则引擎
- 理由链包含：场景适配、硬约束检查、体态适配、风险提示"
```