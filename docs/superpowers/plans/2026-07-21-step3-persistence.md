# 持久化存储 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans

**Goal:** 将 MemoryStore 替换为 SQLite 持久化存储，重启数据不丢失

**Architecture:** 使用 Python 内置 `sqlite3` 模块（零依赖），保持与 MemoryStore 完全相同的 API 接口，所有 104 项测试通过

**Tech Stack:** Python 3.14, sqlite3 (stdlib), FastAPI

## Global Constraints

- 所有原有测试必须保持通过
- `store` 的公有接口不变（`get_or_create_user`, `add_item`, `add_relationship`, `record_decision`, `record_roi`, `apply_feedback`, `set_body_profile`）
- 返回数据结构与 MemoryStore 一致（Dict）
- 数据库路径由环境变量 `STORE_DB_PATH` 控制，默认 `:memory:`

---

### Task 1: 实现 SQLiteStore

**Files:**
- Rewrite: `src/app/services/store.py`（MemoryStore → SQLiteStore）
- Modify: 无（接口不变，调用方无需修改）
- Test: 所有现有测试（104 项，接口不变）

**Interfaces:**
- 完全相同：`store.get_or_create_user(user_id) -> Dict`
- 完全相同：`store.add_item(item: Item) -> Dict`
- 完全相同：`store.add_relationship(relationship: Relationship) -> Dict`
- 完全相同：`store.record_decision(user_id, payload) -> Dict`
- 完全相同：`store.record_roi(user_id, payload) -> Dict`
- 完全相同：`store.apply_feedback(user_id, payload) -> Dict`
- 完全相同：`store.set_body_profile(user_id, payload) -> Dict`

- [ ] **Step 1: 验证当前测试全部通过**

```bash
cd /Users/sxliuyu/orca/clothing-purchase-decision
source .venv/bin/activate
python -m pytest -q
```

Expected: `104 passed`

- [ ] **Step 2: 重写 store.py 为 SQLiteStore**

```python
"""
SQLite-backed persistent store.
Replaces MemoryStore with zero-dependency persistence.
DB path from STORE_DB_PATH env var, defaults to :memory:.
"""
import json
import os
import sqlite3
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.models.schemas import Item, Relationship


class SQLiteStore:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or os.environ.get("STORE_DB_PATH", ":memory:")
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self):
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                body_profile TEXT NOT NULL DEFAULT '{}',
                preferences TEXT NOT NULL DEFAULT '{}',
                wardrobe_graph TEXT NOT NULL DEFAULT '{"nodes":[],"edges":[]}'
            );

            CREATE TABLE IF NOT EXISTS items (
                item_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                category TEXT,
                style TEXT,
                season TEXT,
                occasion TEXT,
                color TEXT,
                material TEXT,
                attributes TEXT NOT NULL DEFAULT '{}',
                price REAL
            );

            CREATE TABLE IF NOT EXISTS relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                from_item_id TEXT NOT NULL,
                to_item_id TEXT NOT NULL,
                relation_type TEXT NOT NULL,
                score REAL NOT NULL DEFAULT 0.0,
                context TEXT,
                times_worn_together INTEGER NOT NULL DEFAULT 0,
                user_rating REAL NOT NULL DEFAULT 0.0
            );

            CREATE TABLE IF NOT EXISTS decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                generated_at TEXT NOT NULL,
                payload TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS roi_analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                generated_at TEXT NOT NULL,
                payload TEXT NOT NULL
            );
        """)
        self._conn.commit()

    def get_or_create_user(self, user_id: str) -> Dict:
        cur = self._conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        if row is not None:
            return {
                'user_id': row['user_id'],
                'body_profile': json.loads(row['body_profile']),
                'preferences': json.loads(row['preferences']),
                'wardrobe_graph': json.loads(row['wardrobe_graph']),
            }
        # Create user
        default = {
            'user_id': user_id,
            'body_profile': {},
            'preferences': {},
            'wardrobe_graph': {'nodes': [], 'edges': []},
        }
        self._conn.execute(
            "INSERT INTO users (user_id, body_profile, preferences, wardrobe_graph) VALUES (?, ?, ?, ?)",
            (user_id, '{}', '{}', '{"nodes":[],"edges":[]}')
        )
        self._conn.commit()
        return default

    def _save_user(self, user_id: str, body_profile: Dict, preferences: Dict, wardrobe_graph: Dict):
        self._conn.execute(
            "UPDATE users SET body_profile=?, preferences=?, wardrobe_graph=? WHERE user_id=?",
            (json.dumps(body_profile), json.dumps(preferences), json.dumps(wardrobe_graph), user_id)
        )
        self._conn.commit()

    def add_item(self, item: Item) -> Dict:
        record = item.model_dump()
        self._conn.execute(
            "INSERT OR REPLACE INTO items (item_id, user_id, category, style, season, occasion, color, material, attributes, price) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (record['item_id'], record['user_id'], record.get('category'),
             record.get('style'), record.get('season'), record.get('occasion'),
             record.get('color'), record.get('material'),
             json.dumps(record.get('attributes', {})), record.get('price'))
        )
        self._conn.commit()
        self._index_item(record['user_id'], record)
        return record

    def _index_item(self, user_id: str, record: Dict) -> None:
        user = self.get_or_create_user(user_id)
        nodes = user['wardrobe_graph']['nodes']
        if record['item_id'] not in [n['item_id'] for n in nodes]:
            nodes.append({
                'item_id': record['item_id'],
                'attributes': {
                    'category': record.get('category'),
                    'style': record.get('style'),
                    'season': record.get('season'),
                    'occasion': record.get('occasion'),
                    'score': record.get('score', 0),
                },
            })
            self._save_user(user_id, user['body_profile'], user['preferences'], user['wardrobe_graph'])

    def add_relationship(self, relationship: Relationship) -> Dict:
        record = relationship.model_dump()
        self._conn.execute(
            "INSERT INTO relationships (user_id, from_item_id, to_item_id, relation_type, score, context, times_worn_together, user_rating) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (record['user_id'], record['from_item_id'], record['to_item_id'],
             record['relation_type'], record['score'], record.get('context'),
             record.get('times_worn_together', 0), record.get('user_rating', 0.0))
        )
        self._conn.commit()
        return record

    def record_decision(self, user_id: str, payload: Dict) -> Dict:
        record = {
            'user_id': user_id,
            'generated_at': datetime.now(timezone.utc).isoformat() + 'Z',
            'payload': payload,
        }
        self._conn.execute(
            "INSERT INTO decisions (user_id, generated_at, payload) VALUES (?, ?, ?)",
            (user_id, record['generated_at'], json.dumps(payload))
        )
        self._conn.commit()
        return record

    def record_roi(self, user_id: str, payload: Dict) -> Dict:
        record = {
            'user_id': user_id,
            'generated_at': datetime.now(timezone.utc).isoformat() + 'Z',
            'payload': payload,
        }
        self._conn.execute(
            "INSERT INTO roi_analyses (user_id, generated_at, payload) VALUES (?, ?, ?)",
            (user_id, record['generated_at'], json.dumps(payload))
        )
        self._conn.commit()
        return record

    def apply_feedback(self, user_id: str, payload: Dict) -> Dict:
        user = self.get_or_create_user(user_id)
        profile = user['body_profile']
        sensitive_areas = set(profile.get('sensitive_areas', []))
        fit_preference = dict(profile.get('fit_preference', {}))
        if payload.get('fit_feedback'):
            sensitive_areas.add(payload['fit_feedback'])
            fit_preference[payload.get('item_id', 'global')] = payload.get('fit_feedback')
        if payload.get('visual_comfort'):
            sensitive_areas.add(payload['visual_comfort'])
        profile['sensitive_areas'] = sorted(sensitive_areas)
        profile['fit_preference'] = fit_preference
        self._save_user(user_id, profile, user['preferences'], user['wardrobe_graph'])
        return profile

    def set_body_profile(self, user_id: str, payload: Dict) -> Dict:
        user = self.get_or_create_user(user_id)
        profile = user['body_profile']
        for key in ['height', 'weight', 'shoulder_width', 'waistline', 'leg_type', 'body_shape']:
            if key in payload and payload[key] is not None:
                profile[key] = payload[key]
        if payload.get('fit_preference') is not None:
            fit_pref = dict(profile.get('fit_preference', {}))
            fit_pref['global'] = payload['fit_preference']
            profile['fit_preference'] = fit_pref
        if payload.get('weight') is not None:
            profile['recorded_weight'] = payload['weight']
            profile['weight_recorded_at'] = datetime.now(timezone.utc).isoformat()
        self._save_user(user_id, profile, user['preferences'], user['wardrobe_graph'])
        return profile

    @property
    def users(self) -> Dict[str, Dict]:
        """兼容 MemoryStore.users 属性，用于部分测试访问"""
        cur = self._conn.execute("SELECT user_id FROM users")
        result = {}
        for row in cur.fetchall():
            result[row['user_id']] = self.get_or_create_user(row['user_id'])
        return result

    @property
    def items(self) -> Dict[str, Dict]:
        """兼容 MemoryStore.items 属性"""
        cur = self._conn.execute("SELECT * FROM items")
        result = {}
        for row in cur.fetchall():
            result[row['item_id']] = dict(row)
        return result


# 全局实例（默认 :memory:，可通过环境变量覆盖）
store = SQLiteStore()
```

- [ ] **Step 3: 运行测试**

Run: `python -m pytest -q`
Expected: `104 passed`

- [ ] **Step 4: 验证持久化功能**

```python
# 测试：写入文件数据库，重启后数据仍在
import tempfile, os
from app.services.store import SQLiteStore

tmp = tempfile.mktemp(suffix='.db')
s = SQLiteStore(tmp)
s.get_or_create_user('test-persist')
s.add_item(Item(user_id='test-persist', item_id='p1', category='outwear', color='blue'))

# 重建实例，验证数据保留
s2 = SQLiteStore(tmp)
user = s2.get_or_create_user('test-persist')
assert len(user['wardrobe_graph']['nodes']) == 1
assert s2.items['p1']['item_id'] == 'p1'
os.remove(tmp)
print('持久化验证通过')
```

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat: 用 SQLiteStore 替换 MemoryStore，实现持久化存储

- 使用 Python 内置 sqlite3 模块，零额外依赖
- 保持与 MemoryStore 完全相同的公有接口
- 数据库路径由 STORE_DB_PATH 环境变量控制，默认 :memory:
- 全部 104 项测试通过"
```