from uuid import uuid4
from datetime import datetime

from fastapi import APIRouter, HTTPException
from app.models.schemas import Item, Relationship, WardrobeSearchRequest
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


@router.post('/search')
def search_wardrobe(payload: WardrobeSearchRequest):
    user = store.get_or_create_user(payload.user_id)
    nodes = user.get('wardrobe_graph', {}).get('nodes', [])

    results = []
    for node in nodes:
        attrs = node.get('attributes', {})
        # 精确匹配
        if payload.category and attrs.get('category') != payload.category:
            continue
        if payload.color and attrs.get('color') != payload.color:
            continue
        if payload.style and attrs.get('style') != payload.style:
            continue
        if payload.season and attrs.get('season') != payload.season:
            continue
        if payload.occasion and attrs.get('occasion') != payload.occasion:
            continue
        # 模糊搜索
        if payload.keyword:
            kw = payload.keyword.lower()
            searchable = f"{node.get('item_id', '')} {attrs.get('category', '')} {attrs.get('color', '')} {attrs.get('style', '')}".lower()
            if kw not in searchable:
                continue
        results.append(node)

    return {
        'user_id': payload.user_id,
        'count': len(results),
        'items': results[:payload.limit],
    }
