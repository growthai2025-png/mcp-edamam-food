# mcp-edamam/app/routers/meta_router.py

from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter(
    tags=["MCP-Meta"]
)

# -------------------------------------------------------------------------
# FULL MCP META (unchanged content exactly as provided by you)
# -------------------------------------------------------------------------

MCP_META: Dict[str, Any] = {
    "mcp_name": "mcp-edamam",
    "mcp_version": "1.0.2",
    "description": "Machine Component Processor for food/nutrition tasks. Exposes function schema and system prompt for LLM integration.",
    "functions": [
        {
            "name": "get_food_nutrition",
            "description": "Return nutrition facts for a food item. Use 'query' (free text) OR 'foodId' from parser.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search term, e.g. 'banana'"},
                    "foodId": {"type": "string", "description": "Optional Edamam foodId from parser"},
                    "quantity": {"type": "number", "description": "Quantity in grams", "default": 100}
                },
                "required": []
            }
        },
        {
            "name": "get_nutrition_from_image",
            "description": "Analyze a food image and return detected ingredients and nutrition information. Use when the user provides an image URL (e.g. ending with .jpg, .png).",
            "parameters": {
                "type": "object",
                "properties": {
                    "image_url": {
                        "type": "string",
                        "description": "The direct URL of the food image provided by the user (e.g. https://example.com/food.jpg)."
                    }
                },
                "required": ["image_url"]
            }
        },
        {
            "name": "search_food",
            "description": "Search food parser and return candidate food objects (label, foodId, nutrients).",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search term"},
                    "limit": {"type": "integer", "description": "Max results", "default": 5}
                },
                "required": ["query"]
            }
        }
    ],

    # ------------------------- Ultra Smart System Prompt -------------------------
    "system_prompt": (
        "You are a nutrition-focused assistant connected to an MCP module that provides:\n"
        "- Food nutrition facts\n"
        "- Image-based food analysis\n"
        "- Food search\n\n"

        "Use MCP **only when nutrition data is explicitly required**, or when an **image URL** is provided.\n"
        "Your job is to correctly detect user intent and decide if MCP should be called.\n"
        "If MCP is not needed, answer normally.\n\n"

        "────────────────────────────────────────\n"
        " WHEN TO CALL MCP (mandatory)\n"
        "────────────────────────────────────────\n"
        "Call MCP when the user asks for:\n"
        "1. Calories (kcal)\n"
        "2. Protein, fat, carbs, fiber, sugar, net carbs\n"
        "3. Vitamins, minerals, cholesterol, sodium, potassium\n"
        "4. Any numeric or factual nutrition data\n"
        "5. Nutrition for specific quantity (e.g. 50g almonds)\n"
        "6. Full nutrition breakdown / nutrition label\n"
        "7. Nutrition of a specific recipe or dish\n"
        "8. Image URL ending with .jpg, .jpeg, .png, .webp → ALWAYS use get_nutrition_from_image\n"
        "9. Follow-up questions requiring nutrition, referencing previous food (\"how much fat is in it\")\n"
        "10. Questions like \"is this high in protein\", \"is it low carb\", \"how many macros does it have\"\n"
        "11. Multi-food comparisons requiring exact numbers\n"
        "12. Anything requiring structured numeric nutrition output\n\n"

        "────────────────────────────────────────\n"
        " WHEN *NOT* TO CALL MCP (answer normally)\n"
        "────────────────────────────────────────\n"
        "Do NOT call MCP when the user asks about:\n"
        "• Ingredients\n"
        "• Allergies\n"
        "• Diet rules (keto/vegan)\n"
        "• Food safety\n"
        "• Cooking tips\n"
        "• Taste, price, culture, etc.\n"
        "• Anything not requiring numeric nutrition\n\n"

        "────────────────────────────────────────\n"
        " CONTEXT AWARENESS RULES\n"
        "────────────────────────────────────────\n"
        "Follow-up questions must inherit the previously identified food.\n"
        "If context is not nutrition-related → answer normally.\n\n"

        "────────────────────────────────────────\n"
        " FUNCTION SELECTION\n"
        "────────────────────────────────────────\n"
        "- Image URL → get_nutrition_from_image\n"
        "- Food text → get_food_nutrition\n"
        "- General lookup → search_food\n"
        "- Only ONE function call per request.\n"
    ),

    "examples": [
        {
            "user": "Show me nutrition for this image: https://example.com/food.jpg",
            "recommended_function": "get_nutrition_from_image",
            "arguments": {"image_url": "https://example.com/food.jpg", "quantity": 100}
        },
        {
            "user": "How many calories in 100g banana?",
            "recommended_function": "get_food_nutrition",
            "arguments": {"query": "banana", "quantity": 100}
        },
        {
            "user": "Does chicken enchilada contain peanuts?",
            "recommended_function": "none",
            "arguments": {}
        }
    ]
}

# -------------------------------------------------------------------------
# GET /schema — with proper Swagger documentation
# -------------------------------------------------------------------------

@router.get(
    "/schema",
    summary="Retrieve MCP metadata & function schema",
    description=(
        "Returns the full MCP definition used by the LLM.\n\n"
        "Includes:\n"
        "- Function list\n"
        "- Parameter definitions\n"
        "- Ultra-smart system prompt\n"
        "- Example calls\n\n"
        "This endpoint should be fetched ONCE during LLM initialization."
    ),
    responses={
        200: {
            "description": "Successfully returned the MCP schema",
            "content": {
                "application/json": {
                    "example": {
                        "mcp_name": "mcp-edamam",
                        "mcp_version": "1.0.2",
                        "functions": [
                            {"name": "get_food_nutrition"},
                            {"name": "get_nutrition_from_image"},
                            {"name": "search_food"}
                        ]
                    }
                }
            }
        }
    }
)
async def get_schema():
    return MCP_META
