# app/main.py
import os
from fastapi import FastAPI
from dotenv import load_dotenv

# Зареждаме .env още преди каквито и да било други import-и
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

from app.routers.ai_router import router as ai_router
from app.routers.food_router import router as food_router
from app.routers.meta_router import router as meta_router

app = FastAPI(docs_url="/docs", redoc_url=None, openapi_url="/openapi.json")

app.include_router(ai_router, prefix="/v1/ai")
app.include_router(food_router, prefix="/v1/food")
app.include_router(meta_router, prefix="/v1/mcp")

@app.get("/", include_in_schema=False)
async def root():
    return {"status": "ok"}
