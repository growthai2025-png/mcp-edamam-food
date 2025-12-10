# Overview

`edamam-mcp` is a FastAPI-based service that wraps the **Edamam Food Database API**
and exposes a **dual-transport, LLM-friendly interface**:

- ✅ REST (classic HTTP)
- ✅ JSON-RPC (MCP / tool-based execution)

The core endpoints are:

- `GET /v1/mcp/schema` – metadata endpoint for LLM discovery
- `POST /v1/ai/query` – unified REST execution endpoint
- `POST /v1/rpc` – JSON-RPC / MCP transport

The goal is to allow an LLM or agent to:

- look up nutrition for foods (`get_food_nutrition`),
- search for candidate foods (`search_food`),
- analyze food images (`get_nutrition_from_image`),

without exposing the full complexity of Edamam’s native REST API.