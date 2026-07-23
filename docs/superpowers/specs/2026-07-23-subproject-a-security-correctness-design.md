# 子项目 A：安全与正确性修复设计

> 日期：2026-07-23
> 范围：密码泄露清理 + 组合计算季节 bug 修复
> 优先级：P0（最紧急）

---

## 一、问题描述

### 1.1 明文密码泄露（安全 🔴）

4 个脚本含真实服务器密码 `'YuJin#Ze$12'`，已提交到 git 历史：

| 文件 | 密码位置 | 用途 |
|------|---------|------|
| `scripts/check_logs.py` | 第 3 行 | SSH 查看日志 |
| `scripts/deploy_test.py` | 第 3 行 | SSH 连接测试 |
| `scripts/fix_run.py` | 第 3 行 | SSH 修复部署 |
| `scripts/view_run.py` | 第 3 行 | SSH 查看状态 |

**风险**：git 历史中永久保留密码，任何 clone 仓库的人都能获取服务器 root 权限。

### 1.2 季节兼容判断 bug（正确性 🔴）

`combination_calculator.py` 第 328 行：

```python
# 错误写法：检查 set 是否是元素（永远为 False）
incompatible = ({'summer'} in seasons1 and {'winter'} in seasons2) or \
              ({'winter'} in seasons1 and {'summer'} in seasons2)
```

**影响**：`_can_combine` 方法中，当 `incompatible` 为 truthy 时（第 326 行），第 328 行的季节互斥检查永远返回 False，导致本应被拒绝的季节搭配（如 summer + winter）被错误放行。

**注意**：第 326 行的 `incompatible` 初始值检查 `({'spring', 'fall'} & seasons1) and ({'summer', 'winter'} & seasons2)` 本身也有问题——它检查的是"一件是春秋 + 另一件是夏冬"，但夏冬本身不是互斥的（winter 和 summer 不会同时出现在同一件衣服上）。逻辑混乱。

---

## 二、修复方案

### 2.1 密码泄露修复

**方案：删除 4 个脚本，保留 `deploy_server.py` 作为唯一部署入口**

理由：
- `check_logs.py`、`deploy_test.py`、`fix_run.py`、`view_run.py` 都是临时调试脚本，功能已被 `deploy_server.py` 覆盖
- `deploy_server.py` 已正确使用环境变量（`os.environ.get('DEPLOY_PASSWORD', '')`）
- 删除比修改更安全——即使修改了密码，git 历史中仍有旧密码

**补充措施**：
- 不在 `.gitignore` 中添加 `*.py` 排除规则（会影响正常代码）
- 在 `README.md` 部署章节添加安全提示：部署凭据必须通过环境变量传入，禁止硬编码

**git 历史清理（本次不做，记录为后续事项）**：
- 密码已提交到 git 历史，仅删除文件无法清除历史中的密码
- 本次只做文件删除（个人项目，密码可能已更换）
- 如需彻底清理历史，后续可用 `git filter-branch` 或 BFG Repo-Cleaner，并强制 force push

### 2.2 季节兼容 bug 修复

**修复 `_can_combine` 方法的季节判断逻辑**：

```python
def _can_combine(self, item1: Dict, item2: Dict) -> bool:
    """判断两件衣物是否可以搭配"""
    seasons1 = set((item1.get('season') or '').split(','))
    seasons2 = set((item2.get('season') or '').split(','))
    
    # 移除空字符串（当 season 为空时 split 会返回 ['']）
    seasons1.discard('')
    seasons2.discard('')
    
    # 季节互斥：夏天和冬天不能搭配
    if 'summer' in seasons1 and 'winter' in seasons2:
        return False
    if 'winter' in seasons1 and 'summer' in seasons2:
        return False
    
    # 场合兼容性（保持不变）
    occasions1 = set(item1.get('occasion') or [])
    occasions2 = set(item2.get('occasion') or [])
    
    if occasions1 and occasions2 and not (occasions1 & occasions2):
        if 'daily' not in occasions1 and 'daily' not in occasions2:
            return False
    
    return True
```

**关键变更**：
1. 移除第 326-329 行混乱的 `incompatible` 逻辑
2. 直接用 `'summer' in seasons1` 替代 `{'summer'} in seasons1`
3. 添加 `discard('')` 处理空 season 字符串

---

## 三、测试计划

### 3.1 季节兼容性测试（新增）

```python
def test_season_compatibility():
    calc = CombinationGapCalculator()
    
    # summer + winter 不能搭配
    assert not calc._can_combine(
        {'season': 'summer'}, {'season': 'winter'}
    )
    
    # winter + summer 不能搭配
    assert not calc._can_combine(
        {'season': 'winter'}, {'season': 'summer'}
    )
    
    # spring + fall 可以搭配
    assert calc._can_combine(
        {'season': 'spring'}, {'season': 'fall'}
    )
    
    # 空 season 可以搭配
    assert calc._can_combine(
        {'season': ''}, {'season': 'summer'}
    )
    
    # 多季节：spring,summer + fall 可以搭配
    assert calc._can_combine(
        {'season': 'spring,summer'}, {'season': 'fall'}
    )
    
    # 多季节：summer + fall,winter 不能搭配（summer vs winter）
    assert not calc._can_combine(
        {'season': 'summer'}, {'season': 'fall,winter'}
    )
```

### 3.2 回归测试

确保现有 140 个测试全部通过。

---

## 四、实施步骤

1. 删除 4 个含密码的脚本
2. 修复 `combination_calculator.py` 季节判断逻辑
3. 新增季节兼容性测试
4. 运行全部测试验证
5. Commit

---

*设计文档版本：v1.0 | 2026-07-23*
