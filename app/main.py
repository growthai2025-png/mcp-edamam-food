# mcp-edamam/app/main.py

import os
from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware  # ← Added

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

from app.routers.ai_router import router as ai_router
from app.routers.food_router import router as food_router
from app.routers.meta_router import router as meta_router
from app.routers.rpc_router import router as rpc_router   # ← НОВО

app = FastAPI(docs_url="/docs", redoc_url=None, openapi_url="/openapi.json")

# CORS for Local Inspector
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ai_router, prefix="/v1/ai")
app.include_router(food_router, prefix="/v1/food")
app.include_router(meta_router, prefix="/v1/mcp")
app.include_router(rpc_router, prefix="/v1/rpc")

@app.get("/", include_in_schema=False)
async def root():
    return {"status": "ok"}

@app.on_event("startup")
async def show_routes():
    print("\n===== ACTIVE ROUTES =====")
    for r in app.router.routes:
        print(r.path, r.methods)
    print("=========================\n")
