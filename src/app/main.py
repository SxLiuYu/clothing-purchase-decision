from fastapi import FastAPI
from app.routes import outfits, roi, body, wardrobe, social

app = FastAPI(title="Clothing Purchase Decision")

app.include_router(wardrobe.router, prefix="/api/v3/wardrobe", tags=["wardrobe"])
app.include_router(outfits.router, prefix="/api/v3/decisions", tags=["decisions"])
app.include_router(roi.router, prefix="/api/v3/shop", tags=["shop"])
app.include_router(body.router, prefix="/api/v3/body", tags=["body"])
app.include_router(social.router, prefix="/api/v3/social", tags=["social"])


@app.get("/health")
def health():
    return {"status": "ok"}
