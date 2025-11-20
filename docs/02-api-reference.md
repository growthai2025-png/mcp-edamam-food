# API Reference

## `GET /v1/mcp/schema`

Returns MCP metadata for LLM integration:

```json
{
  "mcp_name": "mcp-edamam",
  "mcp_version": "1.0.1",
  "description": "...",
  "functions": [ ... ],
  "system_prompt": "You are connected to a Modular Connector ...",
  "examples": [ ... ]
}
```

## `POST /v1/ai/query`

Main execution endpoint.

### Request body

```json
{
  "intent": "get_food_nutrition" | "search_food" | "analyze_food_image",
  "parameters": {
    "...": "..."
  }
}
```

### Intents

See the root `README.md` for detailed schema examples of each intent.
