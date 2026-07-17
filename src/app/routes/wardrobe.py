from uuid import uuid4
from datetime import datetime

from fastapi import APIRouter, HTTPException
from app.models.schemas import Item, Relationship
from app.services.store import store

router = APIRouter()


@router.post("/items", response_model=dict)
def add_item(payload: Item):
    record = store.add_item(payload)
    return {"status": "indexed", "item": record}


@router.get("/users/{user_id}/items")
def list_items(user_id: str):
    user = store.get_or_create_user(user_id)
    nodes = user.get('wardrobe_graph', {}).get('nodes', [])
    return {"user_id": user_id, "count": len(nodes), "nodes": nodes}


@router.post("/relationships", response_model=dict)
def add_relationship(payload: Relationship):
    if payload.user_id in store.users:
        record = store.add_relationship(payload)
        return {"status": "added", "relationship": record}
    raise HTTPException(status_code=404, detail="user not found")
