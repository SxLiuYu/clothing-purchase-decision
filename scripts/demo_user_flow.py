# Demo User Flow Test Script
import httpx

BASE = "http://localhost:8000"
user_id = "demo-user-001"

print("=== User Story Demo: Smart Wardrobe + AI Stylist ===")
print()

# Step 1: Add items
print("[Step 1] Add items to wardrobe")
items = [
    {"user_id": user_id, "item_id": "shirt-001", "category": "top", "color": "light_blue", "material": "cotton"},
    {"user_id": user_id, "item_id": "pants-001", "category": "bottom", "color": "dark_gray", "material": "wool"},
    {"user_id": user_id, "item_id": "shoes-001", "category": "shoes", "color": "brown", "material": "leather"},
]
for item in items:
    r = httpx.post(f"{BASE}/api/v3/wardrobe/items", json=item)
    print(f"  + {item['color']} {item['category']}: {r.json()['status']}")

# Step 2: Get outfit decision
print()
print("[Step 2] Request outfit decision")
r = httpx.post(f"{BASE}/api/v3/decisions/outfit", json={
    "user_id": user_id, "occasion": "formal",
    "datetime": "2026-07-22T09:00:00+08:00",
    "weather": {"temperature_c": 18, "condition": "cloudy"},
})
print(f"  + Decision ID: {r.json()['decision_id']}")
print(f"  + Confidence: {r.json()['confidence']}")

# Step 3: ROI analysis
print()
print("[Step 3] ROI buy analysis")
r = httpx.post(f"{BASE}/api/v3/shop/roi-analysis", json={
    "user_id": user_id, "new_item": {"category": "top", "color": "white", "price": 499}
})
print(f"  + ROI Score: {r.json()['roi_score']}")
print(f"  + Recommend: {r.json()['recommendation']}")

# Step 4: Body feedback
print()
print("[Step 4] Submit body feedback")
r = httpx.post(f"{BASE}/api/v3/body/feedback", json={
    "user_id": user_id, "item_id": "shirt-001", "fit_feedback": "tight_collar", "occasion": "formal"
})
print(f"  + Sensitive areas: {r.json()['updated_profile']['sensitive_areas']}")

print()
print("=== All flows completed successfully! ===")
