# mcp-edamam/app/routers/meta_router.py

from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter(
    tags=["MCP-Meta"]
)

# =====================================================================
# FINAL MCP META — NEW OPENAI TOOLS FORMAT (100% correct)
# =====================================================================

MCP_META: Dict[str, Any] = {

    "mcp_name": "mcp-edamam",
    "mcp_version": "1.0.0",
    "description": (
        "Machine Component Processor for food/nutrition tasks. "
        "Exposes function schema and system prompt for LLM integration."
    ),

    # -----------------------------------------------------------------
    # OPENAI TOOLS (including UPC support)
    # -----------------------------------------------------------------
    "functions": [

        # -------------------------------------------------------------
        # 1) get_food_nutrition
        # -------------------------------------------------------------
        {
            "type": "function",
            "function": {
                "name": "get_food_nutrition",
                "description": (
                    "Return nutrition facts for ONE food item and quantity in grams. "
                    "Supports: free-text food names, Edamam foodId, UPC/EAN/PLU codes. "
                    "If the user mentions MULTIPLE foods, call this function ONCE PER FOOD."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": (
                                "Food name, UPC, EAN, PLU or general query. "
                                "If UPC/EAN/PLU is provided, Edamam automatically "
                                "performs barcode lookup."
                            )
                        },
                        "foodId": {
                            "type": "string",
                            "description": "Optional Edamam foodId"
                        },
                        "quantity": {
                            "type": "number",
                            "description": "Quantity in grams",
                            "default": 100
                        }
                    },
                    "required": []
                }
            }
        },

        # -------------------------------------------------------------
        # 2) get_nutrition_from_image
        # -------------------------------------------------------------
        {
            "type": "function",
            "function": {
                "name": "get_nutrition_from_image",
                "description": (
                    "Analyze a food image and return ingredients and nutrition."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "image_url": {
                            "type": "string",
                            "description": "Direct URL of food image"
                        }
                    },
                    "required": ["image_url"]
                }
            }
        },

        # -------------------------------------------------------------
        # 3) search_food
        # -------------------------------------------------------------
        {
            "type": "function",
            "function": {
                "name": "search_food",
                "description": "Search Edamam parser. Supports food names and UPC codes.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string"
                        },
                        "limit": {
                            "type": "integer",
                            "default": 5
                        }
                    },
                    "required": ["query"]
                }
            }
        }
    ],

    # -----------------------------------------------------------------
    # SYSTEM PROMPT
    # -----------------------------------------------------------------
    "system_prompt": (
        "You are a nutrition-focused assistant connected to an MCP module.\n"
        "The MCP provides:\n"
        "- Food nutrition facts\n"
        "- Image-based food analysis\n"
        "- Food search\n\n"

        "────────────────────────────────────────\n"
        " WHEN TO CALL MCP (mandatory)\n"
        "────────────────────────────────────────\n"
        "Call MCP when the user asks for ANY numeric nutrition data...\n"
        "• barcode / UPC queries MUST call get_food_nutrition.\n"
        "• calories (kcal)\n"
        "• protein, fat, carbs, fiber, sugar, net carbs\n"
        "• vitamins, minerals, cholesterol, sodium, potassium\n"
        "• macros or totals across multiple foods\n"
        "• full nutrition label / breakdown\n"
        "• nutrition for specific quantities (e.g. 50g almonds)\n"
        "• follow-up questions requiring numeric nutrition\n\n"

        "────────────────────────────────────────\n"
        " WHEN NOT TO CALL MCP\n"
        "────────────────────────────────────────\n"
        "Do NOT call MCP for non-numeric topics:\n"
        "• taste, cooking tips, culture, origin\n"
        "• ingredients list\n"
        "• allergies (unless numeric data needed)\n"
        "• diet rules not requiring numbers\n\n"

        "────────────────────────────────────────\n"
        " FUNCTION SELECTION RULES\n"
        "────────────────────────────────────────\n"
        "• Image URL (.jpg/.jpeg/.png/.webp) → get_nutrition_from_image\n"
        "• Food text → get_food_nutrition\n"
        "• General lookup → search_food\n\n"
        "• If MULTIPLE foods appear, call get_food_nutrition ONCE PER FOOD.\n"
        "  Example: '200g chicken and 100g rice' → two calls.\n\n"

        "────────────────────────────────────────\n"
        " POST-PROCESSING RULES (CRITICAL)\n"
        "────────────────────────────────────────\n"
        "• NEVER return raw MCP JSON to the user unless asked.\n"
        "• After each MCP tool call, CONTINUE reasoning.\n"
        "• Always produce final natural-language output.\n"
        "• If asked for ONE nutrient, extract ONLY that nutrient.\n"
        "• If asked for TOTAL values, SUM across foods.\n"
        "• Summarize long MCP outputs cleanly.\n"
    ),

    # -----------------------------------------------------------------
    # Examples
    # -----------------------------------------------------------------
    "examples": [
        {
            "user": "Calories in 100g banana",
            "recommended_function": "get_food_nutrition",
            "arguments": {"query": "banana", "quantity": 100}
        },
        {
            "user": "Scan this barcode: 737628064502",
            "recommended_function": "get_food_nutrition",
            "arguments": {"query": "737628064502"}
        },
        {
            "user": "Show me nutrition for this image: https://example.com/food.jpg",
            "recommended_function": "get_nutrition_from_image",
            "arguments": {"image_url": "https://example.com/food.jpg"}
        }
    ]
}


# =====================================================================
# GET /schema
# =====================================================================

@router.get(
    "/schema",
    summary="Retrieve MCP metadata & function schema",
    description="Returns the full MCP definition used by the LLM."
)
async def get_schema():
    return MCP_META
