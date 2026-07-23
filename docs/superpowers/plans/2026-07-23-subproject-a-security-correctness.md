# 子项目 A：安全与正确性修复 实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 删除 4 个含明文密码的脚本，修复组合计算器的季节兼容判断 bug，扩展 spring↔fall 互斥规则。

**架构：** 
- 密码泄露：删除 4 个临时调试脚本，保留 `deploy_server.py`（已用环境变量）
- 季节 bug：重写 `_can_combine` 方法的季节判断逻辑，用 `'summer' in seasons1` 替代 `{'summer'} in seasons1`，新增 spring↔fall 互斥
- 测试：新增 `test_season_compatibility` 方法到 `TestSuperpower3CombinationGap` 类

**技术栈：** Python 3.9+, FastAPI, pytest

---

### 任务 1：删除含明文密码的脚本

**文件：**
- 删除：`scripts/check_logs.py`
- 删除：`scripts/deploy_test.py`
- 删除：`scripts/fix_run.py`
- 删除：`scripts/view_run.py`

- [ ] **步骤 1：删除 4 个脚本**

```bash
git rm scripts/check_logs.py scripts/deploy_test.py scripts/fix_run.py scripts/view_run.py
```

预期：4 个文件从工作区和 git 跟踪中移除

- [ ] **步骤 2：验证删除**

```bash
ls scripts/check_logs.py scripts/deploy_test.py scripts/fix_run.py scripts/view_run.py 2>&1
```

预期：每个文件报 `ls: cannot access... No such file or directory`

- [ ] **步骤 3：运行测试确认不影响**

```bash
python -m pytest --tb=short -q
```

预期：140 passed，无 FAIL/ERROR

- [ ] **步骤 4：Commit**

```bash
git add .
git commit -m "fix: 删除含明文密码的4个临时调试脚本"
```

---

### 任务 2：修复季节兼容判断 bug

**文件：**
- 修改：`src/app/services/combination_calculator.py:319-340`
- 修改：`tests/test_superpower_fixes.py:120-130`（在 `TestSuperpower3CombinationGap` 类中新增测试方法）

- [ ] **步骤 1：编写失败的测试**

在 `tests/test_superpower_fixes.py` 的 `TestSuperpower3CombinationGap` 类中，在 `test_scenario_coverage_calculation` 方法之后添加新测试方法：

```python
    def test_season_compatibility(self):
        """测试季节互斥规则：summer↔winter, spring↔fall"""
        calculator = CombinationGapCalculator()

        # summer + winter 不能搭配
        assert not calculator._can_combine(
            {'season': 'summer'}, {'season': 'winter'}
        )

        # winter + summer 不能搭配
        assert not calculator._can_combine(
            {'season': 'winter'}, {'season': 'summer'}
        )

        # spring + fall 不能搭配
        assert not calculator._can_combine(
            {'season': 'spring'}, {'season': 'fall'}
        )

        # fall + spring 不能搭配
        assert not calculator._can_combine(
            {'season': 'fall'}, {'season': 'spring'}
        )

        # 多季节：spring,summer + fall,winter 不能搭配（spring vs fall）
        assert not calculator._can_combine(
            {'season': 'spring,summer'}, {'season': 'fall,winter'}
        )

        # 多季节：spring + fall,summer 不能搭配（spring vs fall）
        assert not calculator._can_combine(
            {'season': 'spring'}, {'season': 'fall,summer'}
        )

        # 空 season 可以搭配
        assert calculator._can_combine(
            {'season': ''}, {'season': 'summer'}
        )

        # 多季节：spring,summer + fall 可以搭配（spring vs fall 互斥，但对方无 spring）
        # spring,summer 含 spring，fall 不含 spring，不触发 spring↔fall 互斥
        assert calculator._can_combine(
            {'season': 'spring,summer'}, {'season': 'fall'}
        )

        # 多季节：summer + fall,winter 不能搭配（summer vs winter）
        assert not calculator._can_combine(
            {'season': 'summer'}, {'season': 'fall,winter'}
        )
```

- [ ] **步骤 2：运行测试验证失败**

```bash
python -m pytest tests/test_superpower_fixes.py::TestSuperpower3CombinationGap::test_season_compatibility -v --tb=short
```

预期：FAIL — `_can_combine` 返回 True 但预期 False（因为当前 bug 导致 summer+winter 被错误放行）

- [ ] **步骤 3：修复 `_can_combine` 方法**

将 `src/app/services/combination_calculator.py` 第 319-340 行的 `_can_combine` 方法替换为：

```python
    def _can_combine(self, item1: Dict, item2: Dict) -> bool:
        """判断两件衣物是否可以搭配"""
        # 季节兼容性
        seasons1 = set((item1.get('season') or '').split(','))
        seasons2 = set((item2.get('season') or '').split(','))
        
        # 移除空字符串（当 season 为空时 split 会返回 ['']）
        seasons1.discard('')
        seasons2.discard('')
        
        # 季节互斥规则：
        # - summer ↔ winter（面料/厚度差异大）
        # - spring ↔ fall（春秋季服装重量差异大）
        if ('summer' in seasons1 and 'winter' in seasons2) or \
           ('winter' in seasons1 and 'summer' in seasons2):
            return False
        if ('spring' in seasons1 and 'fall' in seasons2) or \
           ('fall' in seasons1 and 'spring' in seasons2):
            return False
        
        # 场合兼容性
        occasions1 = set(item1.get('occasion') or [])
        occasions2 = set(item2.get('occasion') or [])
        
        # 至少有一个共同场合
        if occasions1 and occasions2 and not (occasions1 & occasions2):
            # 但如果一件是通用场合，可以搭配
            if 'daily' not in occasions1 and 'daily' not in occasions2:
                return False
        
        return True
```

- [ ] **步骤 4：运行测试验证通过**

```bash
python -m pytest tests/test_superpower_fixes.py::TestSuperpower3CombinationGap::test_season_compatibility -v --tb=short
```

预期：PASS

- [ ] **步骤 5：运行全部测试确认回归**

```bash
python -m pytest --tb=short -q
```

预期：141 passed（新增 1 个测试）

- [ ] **步骤 6：Commit**

```bash
git add src/app/services/combination_calculator.py tests/test_superpower_fixes.py
git commit -m "fix: 修复季节兼容判断bug，扩展spring↔fall互斥规则"
```

---

### 任务 3：添加安全提示到 README

**文件：**
- 修改：`README.md`

- [ ] **步骤 1：在 README 部署章节添加安全提示**

在 `README.md` 的末尾添加一个安全提示段落：

```markdown
## 安全提示

- **部署凭据**：必须通过环境变量传入，禁止在脚本中硬编码密码
- **部署脚本**：`scripts/deploy_server.py` 是唯一部署入口，使用 `DEPLOY_HOST`、`DEPLOY_USER`、`DEPLOY_PASSWORD` 环境变量
- **示例配置**：参见 `.env.example` 文件
```

- [ ] **步骤 2：Commit**

```bash
git add README.md
git commit -m "docs: 添加安全提示，部署凭据必须通过环境变量传入"
```

---

### 验证清单

- [ ] 4 个含密码脚本已删除且不在 git 跟踪中
- [ ] 新测试 `test_season_compatibility` 通过
- [ ] 全部 141 个测试通过
- [ ] README 包含安全提示
- [ ] 3 个 commit 已提交