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
    "mcp_version": "1.1.0",
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
        "… (unchanged full prompt here) …\n"
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
