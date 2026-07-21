# store.py - fixed to match UpdatedProfile schema
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List

from app.models.schemas import Item, Relationship


class MemoryStore:
    def __init__(self) -> None:
        self.users: Dict[str, Dict] = {}
        self.items: Dict[str, Dict] = {}
        self.relationships: Dict[str, List[Dict]] = defaultdict(list)
        self.decisions: List[Dict] = []
        self.roi_analyses: List[Dict] = []

    def get_or_create_user(self, user_id: str) -> Dict:
        if user_id not in self.users:
            self.users[user_id] = {
                'user_id': user_id,
                'body_profile': {},
                'preferences': {},
                'wardrobe_graph': {'nodes': [], 'edges': []},
            }
        return self.users[user_id]

    def add_item(self, item: Item) -> Dict:
        record = item.model_dump()
        self.items[item.item_id] = record
        self._index_item(item.user_id, record)
        return record

    def add_relationship(self, relationship: Relationship) -> Dict:
        record = relationship.model_dump()
        self.relationships[relationship.from_item_id].append(record)
        return record

    def record_decision(self, user_id: str, payload: Dict) -> Dict:
        record = {
            'user_id': user_id,
            'generated_at': datetime.now(timezone.utc).isoformat() + 'Z',
            'payload': payload,
        }
        self.decisions.append(record)
        return record

    def record_roi(self, user_id: str, payload: Dict) -> Dict:
        record = {
            'user_id': user_id,
            'generated_at': datetime.now(timezone.utc).isoformat() + 'Z',
            'payload': payload,
        }
        self.roi_analyses.append(record)
        return record

    def apply_feedback(self, user_id: str, payload: Dict) -> Dict:
        user = self.get_or_create_user(user_id)
        profile = user.setdefault('body_profile', {})
        sensitive_areas = set(profile.get('sensitive_areas', []))
        fit_preference = dict(profile.get('fit_preference', {}))  # Changed to fit_preference
        if payload.get('fit_feedback'):
            sensitive_areas.add(payload['fit_feedback'])
            fit_preference[payload.get('item_id', 'global')] = payload.get('fit_feedback')
        if payload.get('visual_comfort'):
            sensitive_areas.add(payload['visual_comfort'])
        profile['sensitive_areas'] = sorted(sensitive_areas)
        profile['fit_preference'] = fit_preference  # Changed to fit_preference
        return profile

    def set_body_profile(self, user_id: str, payload: Dict) -> Dict:
        user = self.get_or_create_user(user_id)
        profile = user.setdefault('body_profile', {})
        for key in ['height', 'weight', 'shoulder_width', 'waistline', 'leg_type', 'body_shape']:
            if key in payload and payload[key] is not None:
                profile[key] = payload[key]
        # fit_preference 在 body_profile 中以 dict 形式存储（与 apply_feedback 一致）
        if payload.get('fit_preference') is not None:
            fit_pref = dict(profile.get('fit_preference', {}))
            fit_pref['global'] = payload['fit_preference']
            profile['fit_preference'] = fit_pref
        if payload.get('weight') is not None:
            profile['recorded_weight'] = payload['weight']
            profile['weight_recorded_at'] = datetime.now(timezone.utc).isoformat()
        return profile

    def _index_item(self, user_id: str, record: Dict) -> None:
        user = self.get_or_create_user(user_id)
        if record['item_id'] not in [node['item_id'] for node in user['wardrobe_graph'].get('nodes', [])]:
            user['wardrobe_graph'].setdefault('nodes', []).append({
                'item_id': record['item_id'],
                'attributes': {
                    'category': record.get('category'),
                    'style': record.get('style'),
                    'season': record.get('season'),
                    'occasion': record.get('occasion'),
                    'score': record.get('score', 0),
                },
            })


store = MemoryStore()
