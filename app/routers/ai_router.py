# app/routers/ai_router.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging
from app.services.edamam_service import search_food, get_food_nutrition, get_nutrition_from_image
from app.utils.logger import mcp_logger

router = APIRouter(
    tags=["AI"]
)

class AIQuery(BaseModel):
    intent: str
    parameters: dict

@router.post("/query")
async def ai_query(payload: AIQuery):
    mcp_logger.info(f"[LLM→MCP] Intent: {payload.intent}, Parameters: {payload.parameters}")
    logging.info(f"AI request: {payload.dict()}")

    try:
        result = None

        if payload.intent == "get_food_nutrition":
            query = payload.parameters.get("query")
            quantity = payload.parameters.get("quantity", 100)

            # Auto-redirect if the query is an image URL
            if isinstance(query, str) and any(ext in query.lower() for ext in [".jpg", ".jpeg", ".png", ".webp"]):
                mcp_logger.info("[MCP] Auto-redirected text query to get_nutrition_from_image")
                return await ai_query(AIQuery(intent="analyze_food_image", parameters={"image_url": query}))

            food = await search_food(query)
            if not food:
                raise HTTPException(status_code=404, detail="Food not found")

            nutrition = await get_food_nutrition(food["foodId"], quantity)
            result = {
                "food": food["label"],
                "quantity": quantity,
                "nutrients": nutrition.get("totalNutrients", {})
            }

        elif payload.intent == "analyze_food_image":
            # Accept 'image' or 'image_url'
            image = payload.parameters.get("image") or payload.parameters.get("image_url")
            if not image:
                raise HTTPException(status_code=400, detail="Missing 'image' or 'image_url' parameter")

            vision_data = await get_nutrition_from_image(image)

            # Parse data from vision response
            parsed = vision_data.get("parsed", {})
            recipe = vision_data.get("recipe", {})
            food_label = parsed.get("food", {}).get("label")
            ingredients = parsed.get("food", {}).get("foodContentsLabel")
            measure = parsed.get("measure", {})
            quantity = parsed.get("quantity", 1)
            weight_per_unit = measure.get("weight", 1)
            
            result = {
                "analysis_type": "image",
                "source": image,
                "food": food_label,
                "ingredients_list": ingredients,
                "serving_weight_grams": round(quantity * weight_per_unit, 2),
                "nutrients": parsed.get("food", {}).get("nutrients", {}),
                "recipe": recipe,
            }

        else:
            raise HTTPException(status_code=400, detail=f"Unknown intent: {payload.intent}")

        # Log result and return
        mcp_logger.info(f"[MCP→LLM] Response: {str(result)[:500]}")
        return result

    except HTTPException as e:
        mcp_logger.error(f"[MCP ERROR] {e.detail} for intent={payload.intent}")
        raise e

    except Exception as e:
        mcp_logger.exception(f"[MCP ERROR] Exception for intent={payload.intent}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
