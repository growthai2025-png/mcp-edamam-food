# Examples

## Example 1 – Get nutrition for 50g almonds

**Request**

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
```

**Response (simplified)**

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

## Example 2 – Analyze a food image

```json
{
  "intent": "analyze_food_image",
  "parameters": {
    "image": "https://example.com/image.jpg"
  }
}
```

Response (simplified) contains detected food label, ingredients list, serving weight and nutrients.
