from collections import defaultdict
from datetime import datetime
from typing import Dict, List

from app.models.schemas import BodyProfile, Item, Relationship


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
        record = item.dict()
        self.items[item.item_id] = record
        self._index_item(item.user_id, record)
        return record

    def add_relationship(self, relationship: Relationship) -> Dict:
        record = relationship.dict()
        self.relationships[relationship.from_item_id].append(record)
        return record

    def record_decision(self, user_id: str, payload: Dict) -> Dict:
        record = {
            'user_id': user_id,
            'generated_at': datetime.utcnow().isoformat() + 'Z',
            'payload': payload,
        }
        self.decisions.append(record)
        return record

    def record_roi(self, user_id: str, payload: Dict) -> Dict:
        record = {
            'user_id': user_id,
            'generated_at': datetime.utcnow().isoformat() + 'Z',
            'payload': payload,
        }
        self.roi_analyses.append(record)
        return record

    def apply_feedback(self, user_id: str, payload: Dict) -> Dict:
        user = self.get_or_create_user(user_id)
        profile = user.setdefault('body_profile', {})
        sensitive_areas = set(profile.get('sensitive_areas', []))
        fit_preferences = dict(profile.get('fit_preferences', {}))
        if payload.get('fit_feedback'):
            sensitive_areas.add(payload['fit_feedback'])
            fit_preferences[payload.get('item_id', 'global')] = payload.get('fit_feedback')
        if payload.get('visual_comfort'):
            sensitive_areas.add(payload['visual_comfort'])
        profile['sensitive_areas'] = sorted(sensitive_areas)
        profile['fit_preferences'] = fit_preferences
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
