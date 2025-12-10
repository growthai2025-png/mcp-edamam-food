# edamam-mcp

Machine Connector Processor (MCP) for the **Edamam Food Database API**.

This project exposes a **unified, LLM-friendly interface** over Edamam, supporting:

- ✅ REST API (classic HTTP)
- ✅ JSON-RPC (MCP / tool transport)
- ✅ MCP schema discovery for LLMs
- ✅ Visual testing via MCP Inspector UI

Supported capabilities:

- Looking up nutrition for foods (`get_food_nutrition`)
- Searching foods and getting candidate matches (`search_food`)
- Analyzing food images and returning ingredients + nutrition (`get_nutrition_from_image`)

---

## Repository layout

```text
edamam-mcp/
  app/
    main.py               # FastAPI entrypoint
    routers/
      ai_router.py        # /v1/ai/query – REST execution
      meta_router.py      # /v1/mcp/schema – MCP metadata for LLMs
      rpc_router.py       # /v1/rpc – JSON-RPC (MCP transport)
    services/
      edamam_service.py   # Edamam API wrappers
    utils/
      logger.py           # Shared logging helpers

  inspector-ui/           # React MCP Inspector UI

  docs/
    01-overview.md
    02-api-reference.md
    03-examples.md
    04-llm-integration.md
    05-inspector.md

  requirements.txt
  .gitignore
  README.md
````

---

## Quickstart (Backend)

1. (Optional) Create and activate a virtual environment
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set environment variables:

```bash
export EDAMAM_APP_ID=...
export EDAMAM_APP_KEY=...
# optional:
# export EDAMAM_FOODDB_BASE_URL=https://api.edamam.com/api/food-database/v2
```

4. Run the API:

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

5. Open:

* Swagger UI:
  [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

* MCP schema:
  [http://127.0.0.1:8000/v1/mcp/schema](http://127.0.0.1:8000/v1/mcp/schema)

* JSON-RPC endpoint:
  [http://127.0.0.1:8000/v1/rpc](http://127.0.0.1:8000/v1/rpc)

---

## MCP Inspector UI

The project includes a local **MCP Inspector** for visual testing of:

* REST calls
* JSON-RPC tool calls
* Presets
* History + replay
* Copy as cURL
* Auto Retry

Start it with:

```bash
cd inspector-ui
npm install
npm run dev
```

Open:

```
http://localhost:5173
```

See `/docs/05-inspector.md` for full usage.

---

## Transports Overview

| Transport  | Endpoint         | Purpose                         |
| ---------- | ---------------- | ------------------------------- |
| REST       | `/v1/ai/query`   | Standard HTTP execution         |
| REST       | `/v1/food/*`     | Direct Edamam-style endpoints   |
| JSON-RPC   | `/v1/rpc`        | MCP / tool-based execution      |
| MCP Schema | `/v1/mcp/schema` | LLM discovery & tool definition |

---

## REST API

### `POST /v1/ai/query`

Unified execution endpoint.

```json
{
  "intent": "get_food_nutrition" | "search_food" | "analyze_food_image",
  "parameters": { "...": "..." }
}
```

---

## JSON-RPC (MCP Transport)

### `POST /v1/rpc`

Example:

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "search_food",
    "arguments": {
      "query": "banana",
      "limit": 5
    }
  },
  "id": 1
}
```

---

## LLM Integration Summary

1. Fetch `/v1/mcp/schema`
2. Inject `system_prompt`
3. Register `functions` as tools
4. Execute via:

   * `/v1/ai/query` (REST)
   * `/v1/rpc` (JSON-RPC)

Full flow is documented in `/docs/04-llm-integration.md`.

---

## Documentation Index

* `01-overview.md` – System overview
* `02-api-reference.md` – REST + MCP API reference
* `03-examples.md` – REST & JSON-RPC examples
* `04-llm-integration.md` – LLM tool integration
* `05-inspector.md` – MCP Inspector UI guide

---

## Status

Current version: **Stable v1**

* Production-ready core API
* Stable Inspector UI for QA & dev
* Streaming, agents, multi-MCP planned for v2+

---

## License

MIT (or internal)
