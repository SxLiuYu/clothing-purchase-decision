from uuid import uuid4
from datetime import datetime
from fastapi import APIRouter, HTTPException
from app.models.schemas import InspirationRequest, InspirationResponse, InspirationItem

router = APIRouter()

DEMO_INSPIRATIONS = [
    {
        "source": "pinterest",
        "image_url": "https://i.pinimg.com/400x/fashion_1.jpg",
        "title": "Minimalist Business Casual",
        "description": "Clean lines and neutral tones for the modern professional",
        "body_shape_match": "athletic",
        "style_tags": ["minimalist", "business", "smart-casual"],
        "url": "https://pinterest.com/example/1"
    },
    {
        "source": "instagram",
        "image_url": "https://i.imgur.com/fashion_2.jpg",
        "title": "Streetwear Smart",
        "description": "Urban style with refined details",
        "body_shape_match": "slim",
        "style_tags": ["streetwear", "urban", "trendy"],
        "url": "https://instagram.com/p/example2"
    },
    {
        "source": "fashion_blog",
        "image_url": "https://i.imgur.com/fashion_3.jpg",
        "title": "Classic Office Look",
        "description": "Timeless pieces that never go out of style",
        "body_shape_match": "average",
        "style_tags": ["classic", "office", "timeless"],
        "url": "https://fashionblog.com/example3"
    },
    {
        "source": "pinterest",
        "image_url": "https://i.pinimg.com/400x/fashion_4.jpg",
        "title": "Summer Casual Friday",
        "description": "Relaxed yet put-together weekend style",
        "body_shape_match": "athletic",
        "style_tags": ["casual", "summer", "relaxed"],
        "url": "https://pinterest.com/example/4"
    },
    {
        "source": "instagram",
        "image_url": "https://i.imgur.com/fashion_5.jpg",
        "title": "Date Night Elegance",
        "description": "Sophisticated looks for special occasions",
        "body_shape_match": "curvy",
        "style_tags": ["elegant", "date-night", "sophisticated"],
        "url": "https://instagram.com/p/example5"
    },
]

STYLE_OCCASION_MAP = {
    "formal": ["minimalist", "classic", "elegant", "business"],
    "casual": ["casual", "relaxed", "streetwear", "urban"],
    "date": ["elegant", "date-night", "sophisticated", "trendy"],
    "party": ["trendy", "elegant", "streetwear", "sophisticated"],
    "sport": ["athletic", "casual", "relaxed"],
}

BODY_SHAPE_COMPATIBILITY = {
    "slim": ["slim", "athletic"],
    "athletic": ["athletic", "average", "slim"],
    "average": ["average", "athletic", "curvy"],
    "curvy": ["curvy", "average", "athletic"],
    "stocky": ["stocky", "average"],
}


def match_inspirations(request, max_results=5):
    body_shape = request.body_profile.body_shape or "average"
    occasion = request.occasion.lower()
    style = request.style.lower() if request.style else None
    
    compatible_shapes = BODY_SHAPE_COMPATIBILITY.get(body_shape, [body_shape])
    occasion_styles = STYLE_OCCASION_MAP.get(occasion, [])
    if style:
        occasion_styles = [style] + occasion_styles
    
    matches = []
    for item in DEMO_INSPIRATIONS:
        score = 0
        
        if item["body_shape_match"] in compatible_shapes:
            score += 60
        
        item_tags = item["style_tags"]
        matching_tags = sum(1 for tag in occasion_styles if tag in item_tags)
        if matching_tags > 0:
            score += min(40, matching_tags * 20)
        
        if request.color_preference:
            score += 10
        
        if score > 30:
            matches.append((item, score))
    
    matches.sort(key=lambda x: x[1], reverse=True)
    return [item for item, score in matches[:max_results]]


@router.post("/similar-outfits", response_model=InspirationResponse)
def recommend_similar_outfits(payload: InspirationRequest):
    matches = match_inspirations(payload)
    
    items = [
        InspirationItem(
            source=m["source"],
            image_url=m["image_url"],
            title=m["title"],
            description=m["description"],
            body_shape_match=m["body_shape_match"],
            style_tags=m["style_tags"],
            url=m["url"]
        )
        for m in matches
    ]
    
    return InspirationResponse(
        request_id=f"insp-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:6]}",
        matches=items,
        total_found=len(items),
        note="Based on your body shape and style preferences, curated from fashion communities."
    )
