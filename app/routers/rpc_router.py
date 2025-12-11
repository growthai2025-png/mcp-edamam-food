# mcp-edamam/app/routers/rpc_router.py

from typing import Any, Dict, Optional, Union, List, Literal
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
import logging

from app.services.edamam_service import (
    search_food,
    get_food_nutrition,
    get_nutrition_from_image,
)
from app.routers.meta_router import MCP_META
from app.utils.logger import mcp_logger

router = APIRouter(
    tags=["MCP-JSONRPC"]
)

logger = logging.getLogger("mcp_jsonrpc")

# ============================================================
# JSON-RPC MODELS (Pydantic v2)
# ============================================================

class JSONRPCRequest(BaseModel):
    jsonrpc: Literal["2.0"] = "2.0"
    method: str
    params: Optional[Dict[str, Any]] = None
    id: Optional[Union[int, str]] = None


class JSONRPCError(BaseModel):
    code: int
    message: str
    data: Optional[Any] = None


class JSONRPCResponse(BaseModel):
    jsonrpc: Literal["2.0"] = "2.0"
    result: Optional[Any] = None
    error: Optional[JSONRPCError] = None
    id: Optional[Union[int, str]] = None


# ============================================================
# HELPERS
# ============================================================

def _error(req_id, code, msg, data=None):
    return JSONRPCResponse(
        id=req_id,
        error=JSONRPCError(code=code, message=msg, data=data)
    ).model_dump()


async def _call_tool(name: str, args: Dict[str, Any]):
    """Executes real Edamam-backed MCP functions."""
    if name == "get_food_nutrition":
        q = args.get("query")
        qty = float(args.get("quantity", 100))
        if not q:
            raise ValueError("Missing 'query'")

        # Redirect if image
        if isinstance(q, str) and any(ext in q.lower() for ext in [".jpg", ".jpeg", ".png", ".webp"]):
            return await _call_tool("analyze_food_image", {"image_url": q})

        food = await search_food(q)
        if not food:
            raise ValueError("Food not found")

        nut = await get_food_nutrition(food["foodId"], qty)
        return {
            "food": food["label"],
            "quantity": qty,
            "nutrients": nut.get("totalNutrients", {})
        }

    #if name == "analyze_food_image":
    if name in ["analyze_food_image", "get_nutrition_from_image"]:
        img = args.get("image") or args.get("image_url")
        if not img:
            raise ValueError("Missing image/image_url")

        v = await get_nutrition_from_image(img)
        parsed = v.get("parsed", {})
        recipe = v.get("recipe", {})

        food_label = parsed.get("food", {}).get("label")
        measure = parsed.get("measure", {})
        qty = parsed.get("quantity", 1)
        weight = measure.get("weight", 1)

        return {
            "analysis_type": "image",
            "source": img,
            "food": food_label,
            "serving_weight_grams": round(qty * weight, 2),
            "nutrients": parsed.get("food", {}).get("nutrients", {}),
            "recipe": recipe
        }

    if name == "search_food":
        q = args.get("query")
        if not q:
            raise ValueError("Missing 'query'")
        limit = int(args.get("limit", 5))

        f = await search_food(q)
        if not f:
            raise ValueError("No results found")

        return {
            "query": q,
            "results": [f][:limit]
        }

    if name == "get_mcp_schema":
        return MCP_META

    raise ValueError(f"Unknown tool: {name}")


# ============================================================
# MCP-SPEC HANDLERS
# ============================================================

async def handle_initialize(req: JSONRPCRequest):
    return {
        "protocolVersion": "1.0",
        "serverInfo": {
            "name": "mcp-edamam",
            "version": MCP_META["mcp_version"],
            "description": MCP_META["description"]
        },
        "capabilities": {
            "tools": True
        }
    }


async def handle_client_caps(req: JSONRPCRequest):
    return {"status": "ok"}


async def handle_tools_list(req: JSONRPCRequest):
    tools = []
    for fn in MCP_META["functions"]:
        tools.append({
            "name": fn["function"]["name"],
            "description": fn["function"]["description"],
            "inputSchema": fn["function"]["parameters"]
        })
    return {"tools": tools}


async def handle_tools_call(req: JSONRPCRequest):
    params = req.params or {}
    name = params.get("name")
    args = params.get("arguments", {})

    try:
        result = await _call_tool(name, args)
        return {"result": result}
    except Exception as e:
        return _error(req.id, -32002, "Tool execution failed", str(e))


# ============================================================
# OPTIONS handler for CORS preflight
# ============================================================

@router.options("/", include_in_schema=False)
async def rpc_options():
    return {
        "Allow": "POST, OPTIONS",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS"
    }


# ============================================================
# ✅ JSON-RPC ENTRYPOINT (RAW BODY – NO FASTAPI VALIDATION)
# ============================================================

@router.post("/")
async def jsonrpc_entry(request: Request):
    try:
        body = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")

    # ------------------------
    # Batch support
    # ------------------------
    if isinstance(body, list):
        responses = []
        for item in body:
            try:
                req = JSONRPCRequest.model_validate(item)
                responses.append(await handle_request(req))
            except Exception as e:
                responses.append(_error(None, -32600, "Invalid Request", str(e)))
        return responses

    # ------------------------
    # Single request
    # ------------------------
    try:
        req = JSONRPCRequest.model_validate(body)
        return await handle_request(req)
    except Exception as e:
        return _error(None, -32600, "Invalid Request", str(e))


# ============================================================
# METHOD ROUTING
# ============================================================

async def handle_request(req: JSONRPCRequest):

    mcp_logger.info(f"[JSONRPC] method={req.method}, params={req.params}")

    try:
        if req.method == "initialize":
            return JSONRPCResponse(id=req.id, result=await handle_initialize(req)).model_dump()

        if req.method == "client/capabilities":
            return JSONRPCResponse(id=req.id, result=await handle_client_caps(req)).model_dump()

        if req.method == "tools/list":
            return JSONRPCResponse(id=req.id, result=await handle_tools_list(req)).model_dump()

        if req.method == "tools/call":
            return JSONRPCResponse(id=req.id, result=await handle_tools_call(req)).model_dump()

        if req.method in ["get_food_nutrition", "get_nutrition_from_image", "analyze_food_image", "search_food", "get_mcp_schema"]:
        #if req.method in ["get_food_nutrition", "analyze_food_image", "search_food", "get_mcp_schema"]:
            return JSONRPCResponse(
                id=req.id,
                result=await _call_tool(req.method, req.params or {})
            ).model_dump()

        return _error(req.id, -32601, f"Method not found: {req.method}")

    except Exception as e:
        return _error(req.id, -32603, "Internal error", str(e))
