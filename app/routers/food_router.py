# mcp-edamam/app/routers/food_router.py

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from app.services.edamam_service import search_food, get_nutrition_from_image

router = APIRouter(
    tags=["Food"]
)

class ImageRequest(BaseModel):
    image: str  # URL или base64 data URI

@router.get("/search")
async def food_search(q: str = Query(..., description="Food to search for")):
    result = await search_food(q)
    if not result:
        raise HTTPException(status_code=404, detail="Food not found")
    return result

@router.post("/analyze-image")
async def analyze_image(payload: ImageRequest):
    try:
        result = await get_nutrition_from_image(payload.image)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
