# mcp-edamam/app/services/edamam_service.py

import os
import httpx
from app.utils.logger import mcp_logger

FOOD_SEARCH_URL = "https://api.edamam.com/api/food-database/v2/parser"
NUTRIENTS_URL = "https://api.edamam.com/api/food-database/v2/nutrients"
NUTRIENTS_FROM_IMAGE_URL = "https://api.edamam.com/api/food-database/v2/nutrients-from-image"


async def get_nutrition_from_image(image: str):
    app_id = os.getenv("EDAMAM_APP_ID")
    app_key = os.getenv("EDAMAM_APP_KEY")
    if not app_id or not app_key:
        raise ValueError("EDAMAM_APP_ID or EDAMAM_APP_KEY not set in environment")

    # Fix: API изисква "image_url" за URL-ове, а не "image"
    payload = {"image_url": image}

    params = {
        "app_id": app_id,
        "app_key": app_key,
        "beta": "true",  # Vision API изисква beta=true
    }

    mcp_logger.info(f"[MCP→Edamam] Nutrients-from-image: {image[:100]}")
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.post(NUTRIENTS_FROM_IMAGE_URL, params=params, json=payload)
        mcp_logger.info(
            f"[Edamam→MCP] Status: {resp.status_code}, Response: {resp.text[:400]}"
        )

        resp.raise_for_status()
        return resp.json()


async def search_food(query: str):
    app_id = os.getenv("EDAMAM_APP_ID")
    app_key = os.getenv("EDAMAM_APP_KEY")
    if not app_id or not app_key:
        raise ValueError("EDAMAM_APP_ID or EDAMAM_APP_KEY not set in environment")

    params = {"ingr": query, "app_id": app_id, "app_key": app_key, "nutrition-type": "logging"}

    mcp_logger.info(f"[MCP→Edamam] Search food: '{query}'")
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(FOOD_SEARCH_URL, params=params)
        mcp_logger.info(
            f"[Edamam→MCP] Status: {resp.status_code}, Response: {resp.text[:400]}"
        )

        resp.raise_for_status()
        data = resp.json()
        food = None
        if data.get("parsed"):
            food = data["parsed"][0]["food"]
        elif data.get("hints"):
            food = data["hints"][0]["food"]
        if not food:
            return None
        return {
            "foodId": food.get("foodId"),
            "label": food.get("label"),
            "category": food.get("category"),
            "nutrients": food.get("nutrients"),
            "image": food.get("image"),
        }


async def get_food_nutrition(food_id: str, quantity: float):
    app_id = os.getenv("EDAMAM_APP_ID")
    app_key = os.getenv("EDAMAM_APP_KEY")
    if not app_id or not app_key:
        raise ValueError("EDAMAM_APP_ID or EDAMAM_APP_KEY not set in environment")

    payload = {
        "ingredients": [
            {
                "quantity": quantity,
                "measureURI": "http://www.edamam.com/ontologies/edamam.owl#Measure_gram",
                "foodId": food_id,
            }
        ]
    }

    mcp_logger.info(f"[MCP→Edamam] Nutrients for foodId={food_id}, quantity={quantity}")
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(
            f"{NUTRIENTS_URL}?app_id={app_id}&app_key={app_key}",
            json=payload,
        )
        mcp_logger.info(
            f"[Edamam→MCP] Status: {resp.status_code}, Response: {resp.text[:400]}"
        )

        resp.raise_for_status()
        return resp.json()
