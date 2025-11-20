# mcp-edamam/app/routers/ai_router.py

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

@router.post(
    "/query",
    summary="Execute an AI/MCP intent",
    description=(
        "Main unified endpoint for the MCP. Accepts an intent and a set of parameters.\n\n"
        "**Supported intents:**\n"
        "- `get_food_nutrition`: Nutrition by food name or foodId\n"
        "- `analyze_food_image`: Nutrition from image URL\n"
        "- Auto-redirect: if a text query is detected to be an image, the MCP will redirect automatically\n\n"
        "**Returns:**\n"
        "- Fully structured nutrition results\n"
        "- Image-based vision analysis (ingredients + nutrition)\n"
    ),
    responses={
        200: {
            "description": "Successful MCP response",
            "content": {
                "application/json": {
                    "examples": {
                        "text_query": {
                            "summary": "Nutrition for 100g banana",
                            "value": {
                                "food": "Banana",
                                "quantity": 100,
                                "nutrients": {
                                    "ENERC_KCAL": {"label": "Energy", "quantity": 89, "unit": "kcal"},
                                    "PROCNT": {"label": "Protein", "quantity": 1.1, "unit": "g"}
                                }
                            }
                        },
                        "image_query": {
                            "summary": "Nutrition from food image",
                            "value": {
                                "analysis_type": "image",
                                "source": "https://example.com/food.jpg",
                                "food": "Chicken Salad",
                                "ingredients_list": "Chicken, lettuce, mayo",
                                "serving_weight_grams": 210,
                                "nutrients": {},
                                "recipe": {}
                            }
                        }
                    }
                }
            }
        },
        400: {"description": "Invalid intent or missing parameters"},
        404: {"description": "Food not found"},
        500: {"description": "Internal MCP error"}
    }
)
async def ai_query(payload: AIQuery):
    mcp_logger.info(f"[LLM→MCP] Intent: {payload.intent}, Parameters: {payload.parameters}")
    logging.info(f"AI request: {payload.dict()}")

    try:
        result = None

        if payload.intent == "get_food_nutrition":
            query = payload.parameters.get("query")
            quantity = payload.parameters.get("quantity", 100)

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
            image = payload.parameters.get("image") or payload.parameters.get("image_url")
            if not image:
                raise HTTPException(status_code=400, detail="Missing 'image' or 'image_url' parameter")

            vision_data = await get_nutrition_from_image(image)

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

        mcp_logger.info(f"[MCP→LLM] Response: {str(result)[:500]}")
        return result

    except HTTPException as e:
        mcp_logger.error(f"[MCP ERROR] {e.detail} for intent={payload.intent}")
        raise e

    except Exception as e:
        mcp_logger.exception(f"[MCP ERROR] Exception for intent={payload.intent}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
