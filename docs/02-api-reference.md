# API Reference

## GET /v1/mcp/schema

Returns MCP metadata for LLM integration.

```json
{
  "mcp_name": "mcp-edamam",
  "mcp_version": "1.0.1",
  "description": "...",
  "functions": [ ... ],
  "system_prompt": "You are connected to a Modular Connector ...",
  "examples": [ ... ]
}
````

---

## POST /v1/ai/query (REST)

Main unified execution endpoint.

### Request body

```json
{
  "intent": "get_food_nutrition" | "search_food" | "analyze_food_image",
  "parameters": {
    "...": "..."
  }
}
```

---

## POST /v1/rpc (JSON-RPC / MCP)

Tool-based execution endpoint.

### tools/list

```json
{
  "jsonrpc": "2.0",
  "method": "tools/list",
  "id": 1
}
```

### tools/call

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

## Supported Intents / Tools

* `get_food_nutrition`
* `search_food`
* `get_nutrition_from_image`

Detailed schemas are defined in `/v1/mcp/schema`.