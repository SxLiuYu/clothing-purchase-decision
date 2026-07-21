# store.py - SQLite-backed persistent store
# Replaces MemoryStore with zero-dependency persistence.
# DB path from STORE_DB_PATH env var, defaults to :memory:.
import json
import os
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, Optional

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
                    'color': record.get('color'),
                    'material': record.get('material'),
                    'price': record.get('price'),
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
        generated_at = datetime.now(timezone.utc).isoformat() + 'Z'
        self._conn.execute(
            "INSERT INTO decisions (user_id, generated_at, payload) VALUES (?, ?, ?)",
            (user_id, generated_at, json.dumps(payload))
        )
        self._conn.commit()
        return {'user_id': user_id, 'generated_at': generated_at, 'payload': payload}

    def record_roi(self, user_id: str, payload: Dict) -> Dict:
        generated_at = datetime.now(timezone.utc).isoformat() + 'Z'
        self._conn.execute(
            "INSERT INTO roi_analyses (user_id, generated_at, payload) VALUES (?, ?, ?)",
            (user_id, generated_at, json.dumps(payload))
        )
        self._conn.commit()
        return {'user_id': user_id, 'generated_at': generated_at, 'payload': payload}

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
        for key in ['height', 'weight', 'shoulder_width', 'waistline', 'leg_type', 'body_shape', 'face_shape', 'skin_tone']:
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


# 全局实例（默认 :memory:，可通过环境变量 STORE_DB_PATH 覆盖）
store = SQLiteStore()