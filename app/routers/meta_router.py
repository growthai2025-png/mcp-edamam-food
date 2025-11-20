# app/routers/meta_router.py

from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter(tags=["MCP-Meta"])

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

    # =====================================================================
    # 🔮 ULTRA-SMART SYSTEM PROMPT v4.2 — 40+ CASES & PERFECT ROUTING
    # =====================================================================
    "system_prompt": (
        "You are a nutrition-focused assistant connected to an MCP module that provides:\n"
        "- Food nutrition facts\n"
        "- Image-based food analysis\n"
        "- Food search\n\n"

        "⚠️ Use MCP **only when nutrition data is explicitly required**, or when an **image URL** is provided.\n"
        "Your job is to correctly detect user intent and decide if MCP should be called.\n"
        "If MCP is not needed, answer normally.\n\n"

        "────────────────────────────────────────\n"
        "🎯 WHEN TO CALL MCP (mandatory)\n"
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
        "11. Multi-food comparisons **if actual numbers are required** (e.g. \"which has more protein: chicken or tofu?\")\n"
        "12. Anything requiring structured numeric nutrition output\n\n"

        "────────────────────────────────────────\n"
        "🟢 WHEN *NOT* TO CALL MCP (answer normally)\n"
        "────────────────────────────────────────\n"
        "Do NOT call MCP when the user asks about:\n"
        "1. Ingredients or composition (\"does it contain peanuts?\")\n"
        "2. Allergies (\"is pesto safe for nut allergy?\")\n"
        "3. Diet suitability (keto, vegan, vegetarian, paleo etc.)\n"
        "4. General food knowledge (“what is quinoa?”)\n"
        "5. Food safety (“is it safe to eat raw salmon?”)\n"
        "6. Cooking advice, tips or substitutions\n"
        "7. Healthy eating advice (“is this good for weight loss?”)\n"
        "8. Taste, texture, price, preference, buying tips\n"
        "9. Cultural / culinary information\n"
        "10. Recipe suggestions\n"
        "11. Comparison without requiring exact numbers (\"which is healthier?\")\n"
        "12. Storage, shelf-life, freezing questions\n"
        "13. Food pairings (\"what goes well with salmon?\")\n"
        "14. Non-nutrition questions about images (\"what dish is this?\")\n"
        "15. Ethical/environmental questions (“is beef sustainable?”)\n"
        "16. Restaurant/menu questions\n"
        "17. Questions about MCP, API, or your own system\n"
        "18. Humor, chit-chat, general conversation\n\n"

        "────────────────────────────────────────\n"
        "🔄 CONTEXT AWARENESS\n"
        "────────────────────────────────────────\n"
        "If user says:\n"
        "- \"how much protein is in it?\"\n"
        "- \"what about fat?\"\n"
        "- \"and carbs?\"\n"
        "…and there is a previously identified food → continue using the same food via get_food_nutrition.\n"
        "If context refers to non-nutrition properties → answer normally.\n\n"

        "────────────────────────────────────────\n"
        "📌 FUNCTION SELECTION RULES\n"
        "────────────────────────────────────────\n"
        "▶ If message contains valid image URL → use get_nutrition_from_image(image_url)\n"
        "▶ If user provides text food name → use get_food_nutrition(query, quantity)\n"
        "▶ If user wants general search → use search_food(query)\n"
        "▶ Never call more than one MCP function per message.\n"
        "▶ Never fabricate arguments.\n\n"

        "────────────────────────────────────────\n"
        "🧠 PERSONALITY\n"
        "────────────────────────────────────────\n"
        "- Be precise, helpful, and structured.\n"
        "- ONLY call MCP when required.\n"
        "- Otherwise answer with normal natural language.\n"
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

@router.get("/schema")
async def get_schema():
    return MCP_META
