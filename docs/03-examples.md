# Examples

This section shows real-world usage examples for both
**REST** and **JSON-RPC (MCP)** transports.

---

## Example 1 – Get nutrition for 50g almonds (REST)

```http
POST /v1/ai/query
Content-Type: application/json

{
  "intent": "get_food_nutrition",
  "parameters": {
    "query": "almonds",
    "quantity": 50
  }
}
````

Response (simplified):

```json
{
  "food": "Nuts, Almonds",
  "quantity": 50,
  "nutrients": {
    "ENERC_KCAL": { "label": "Energy", "quantity": 289.5, "unit": "kcal" },
    "PROCNT": { "label": "Protein", "quantity": 10.6, "unit": "g" }
  }
}
```

---

## Example 2 – Analyze a food image (REST)

```http
POST /v1/ai/query
Content-Type: application/json

{
  "intent": "analyze_food_image",
  "parameters": {
    "image": "https://example.com/image.jpg"
  }
}
```

---

## Example 3 – Search food (JSON-RPC)

```http
POST /v1/rpc
Content-Type: application/json

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

## Example 4 – Get nutrition (JSON-RPC)

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "get_food_nutrition",
    "arguments": {
      "query": "banana",
      "quantity": 100
    }
  },
  "id": 2
}
```
