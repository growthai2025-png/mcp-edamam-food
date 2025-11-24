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
    "description": "Machine Component Processor for food/nutrition tasks. Exposes function schema and system prompt for LLM integration.",

    # -----------------------------------------------------------------
    # OPENAI TOOLS FORMAT (CRITICAL)
    # -----------------------------------------------------------------
    "functions": [
        {
            "type": "function",
            "function": {
                "name": "get_food_nutrition",
                "description": (
                    "Return nutrition facts for ONE food item and quantity in grams. "
                    "Use 'query' (free text) OR 'foodId'. "
                    "If the user mentions MULTIPLE foods, call this function ONCE PER FOOD."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Food name or description"},
                        "foodId": {"type": "string", "description": "Optional Edamam foodId"},
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
        {
            "type": "function",
            "function": {
                "name": "get_nutrition_from_image",
                "description": (
                    "Analyze a food image and return ingredients and nutrition. "
                    "Use ONLY when the user provides an image URL."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "image_url": {
                            "type": "string",
                            "description": "Direct URL of food image (jpg/png/webp)."
                        }
                    },
                    "required": ["image_url"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "search_food",
                "description": "Search Edamam parser for foods.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "limit": {"type": "integer", "default": 5}
                    },
                    "required": ["query"]
                }
            }
        }
    ],

    # =====================================================================
    # SYSTEM PROMPT — FINAL VERSION (100% STRING, NO TUPLES, NO SPLIT BUGS)
    # =====================================================================
    "system_prompt": (
        "You are a nutrition-focused assistant connected to an MCP module.\n"
        "The MCP provides:\n"
        "- Food nutrition facts\n"
        "- Image-based food analysis\n"
        "- Food search\n\n"

        "────────────────────────────────────────\n"
        " WHEN TO CALL MCP (mandatory)\n"
        "────────────────────────────────────────\n"
        "Call MCP when the user asks for ANY numeric nutrition data:\n"
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

    # Optional examples (safe to leave unchanged)
    "examples": [
        {
            "user": "How many calories in 100g banana?",
            "recommended_function": "get_food_nutrition",
            "arguments": {"query": "banana", "quantity": 100}
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
    description=(
        "Returns the full MCP definition used by the LLM.\n"
        "Includes tools, parameter definitions, system prompt and examples."
    )
)
async def get_schema():
    return MCP_META
