# mcp-edamam/app/routers/ai_router.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging
from typing import Optional
from app.services.edamam_service import search_food, get_food_nutrition, get_nutrition_from_image
from app.utils.logger import mcp_logger

router = APIRouter(
    tags=["AI"]
)

# ======================================================
# PARAMETER SCHEMAS (Swagger needs this to show UPC)
# ======================================================

class FoodNutritionParams(BaseModel):
    query: Optional[str] = None   # Food name, UPC, EAN, PLU or text
    foodId: Optional[str] = None  # Optional Edamam ID
    quantity: Optional[float] = 100


class ImageAnalysisParams(BaseModel):
    image: Optional[str] = None
    image_url: Optional[str] = None


class AIQuery(BaseModel):
    intent: str
    parameters: dict  # dynamic, but Swagger will pull schema via examples


# ======================================================
# ROUTER
# ======================================================

@router.post(
    "/query",
    summary="Execute an AI/MCP intent",
    description=(
        "Main unified endpoint for the MCP. Accepts an intent and a set of parameters.\n\n"
        "**Supported intents:**\n"
        "- `get_food_nutrition`: Nutrition by food name, foodId, UPC/EAN/PLU\n"
        "- `analyze_food_image`: Nutrition from image URL\n"
        "- Auto-redirect: if a text query looks like an image URL → auto-switch to analyze_food_image\n\n"
        "**Parameters for get_food_nutrition:**\n"
        "- `query`: Food name, UPC, EAN, PLU (MUST be provided unless foodId is used)\n"
        "- `quantity`: grams (default: 100)\n\n"
        "**Parameters for analyze_food_image:**\n"
        "- `image_url`: Direct URL of an image\n\n"
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
                        "upc_query": {
                            "summary": "Search by UPC barcode",
                            "value": {
                                "intent": "get_food_nutrition",
                                "parameters": {
                                    "query": "0745178450003",
                                    "quantity": 100
                                }
                            }
                        },
                        "name_query": {
                            "summary": "Search by food name",
                            "value": {
                                "intent": "get_food_nutrition",
                                "parameters": {
                                    "query": "banana",
                                    "quantity": 100
                                }
                            }
                        },
                        "image_query": {
                            "summary": "Image-based nutrition",
                            "value": {
                                "intent": "analyze_food_image",
                                "parameters": {
                                    "image_url": "https://example.com/food.jpg"
                                }
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

        # ======================================================
        # get_food_nutrition
        # ======================================================
        if payload.intent == "get_food_nutrition":
            query = payload.parameters.get("query")
            quantity = payload.parameters.get("quantity", 100)

            # Image URL auto-redirect
            if isinstance(query, str) and any(ext in query.lower() for ext in [".jpg", ".jpeg", ".png", ".webp"]):
                mcp_logger.info("[MCP] Auto-redirect text query → analyze_food_image")
                return await ai_query(AIQuery(intent="analyze_food_image", parameters={"image_url": query}))

            # UPC / EAN / PLU / normal text: handled inside search_food()
            food = await search_food(query)
            if not food:
                raise HTTPException(status_code=404, detail="Food not found")

            nutrition = await get_food_nutrition(food["foodId"], quantity)
            result = {
                "food": food["label"],
                "quantity": quantity,
                "nutrients": nutrition.get("totalNutrients", {})
            }

        # ======================================================
        # analyze_food_image
        # ======================================================
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

        # ======================================================
        # search_food
        # ======================================================
        elif payload.intent == "search_food":
            query = payload.parameters.get("query")
            limit = payload.parameters.get("limit", 5)

            if not query:
                raise HTTPException(status_code=400, detail="Missing 'query' parameter")

            # Perform Edamam search (supports UPC / text)
            results = await search_food(query)

            if not results:
                raise HTTPException(status_code=404, detail="No results found")

            # Normalize single dict → list of results
            # because search_food() returns only the top match today
            normalized = [results] if isinstance(results, dict) else results

            # Limit results if needed
            normalized = normalized[:limit]

            result = {
                "query": query,
                "results": normalized
            }

        # ======================================================
        # Unknown
        # ======================================================
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
