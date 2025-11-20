# edamam-mcp

Machine Connector Processor (MCP) for the **Edamam Food Database API**.
This service exposes a small, LLM‑friendly interface for:

- Looking up nutrition for foods by free‑text query (`get_food_nutrition`)
- Searching foods and getting candidate matches (`search_food`)
- Analyzing food images and returning ingredients + nutrition (`get_nutrition_from_image`)

It is designed to be discovered at runtime by an LLM through a `/v1/mcp/schema`
endpoint that returns a function schema and a system prompt.

## Repository layout

```text
edamam-mcp/
  app/
    main.py               # FastAPI entrypoint
    routers/
      ai_router.py        # /v1/ai/query – main MCP endpoint
      meta_router.py      # /v1/mcp/schema – MCP metadata for LLMs
    services/
      edamam_service.py   # Thin wrapper(s) around Edamam Food Database API
    utils/
      logger.py           # Shared logging helpers
  docs/
    01-overview.md
    02-api-reference.md
    03-examples.md
    04-llm-integration.md
  requirements.txt  (or pyproject.toml)
  .gitignore
  README.md
```

## Quickstart

1. Create and activate a virtual environment (optional but recommended).
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Export the required environment variables:

   ```bash
   export EDAMAM_APP_ID=...
   export EDAMAM_APP_KEY=...
   # optionally:
   # export EDAMAM_FOODDB_BASE_URL=https://api.edamam.com/api/food-database/v2
   ```

4. Run the API:

   ```bash
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```

5. Open:

   - Swagger UI: `http://127.0.0.1:8000/docs`
   - MCP schema: `http://127.0.0.1:8000/v1/mcp/schema`

## MCP endpoints

- `GET /v1/mcp/schema`  
  Returns a JSON object containing:

  - `system_prompt` – text to inject as the LLM system message
  - `functions` – OpenAI‑style function schema definitions
  - optional `examples` – example user queries + suggested function and arguments

- `POST /v1/ai/query`  
  Main MCP execution endpoint. It accepts payloads of the form:

  ```json
  {
    "intent": "get_food_nutrition" | "search_food" | "analyze_food_image",
    "parameters": {
      "...": "..."
    }
  }
  ```

### Supported intents

1. **`get_food_nutrition`**

   Input parameters (in `parameters`):

   - `query` (string, optional) – free text like `"100g chicken breast"` or `"banana"`
   - `foodId` (string, optional) – Edamam `foodId` if already known
   - `quantity` (number, default `100`) – amount in grams

   Output (example shape):

   ```json
   {
     "food": "Cooked Chicken Breast",
     "quantity": 100,
     "nutrients": {
       "ENERC_KCAL": { "label": "Energy", "quantity": 165, "unit": "kcal" },
       "PROCNT": { "label": "Protein", "quantity": 31, "unit": "g" },
       "...": {}
     }
   }
   ```

2. **`search_food`**

   Input parameters:

   - `query` (string, required) – search term, e.g. `"almonds"`
   - `limit` (integer, default `5`) – max number of candidates

   Output (example shape):

   ```json
   {
     "query": "almonds",
     "results": [
       {
         "label": "Nuts, Almonds",
         "foodId": "food_bq4d2wras281i0br37nrnaglo3yc",
         "category": "Generic foods",
         "nutrients": {
           "ENERC_KCAL": 579,
           "PROCNT": 21.2,
           "FAT": 49.9
         },
         "image": "https://..."
       }
     ]
   }
   ```

3. **`analyze_food_image`**

   Input parameters:

   - `image` (string, required) – direct URL to a food image

   Output (example shape):

   ```json
   {
     "analysis_type": "image",
     "source": "https://.../food.jpg",
     "food": "Grilled Chicken Breast With Lemon and Herbs",
     "ingredients_list": "Boneless, skinless chicken breast, Olive oil, herbs, ...",
     "serving_weight_grams": 195.33,
     "nutrients": {
       "ENERC_KCAL": { "label": "Energy", "quantity": 336.5, "unit": "kcal" },
       "...": {}
     },
     "recipe": {
       "uri": "http://www.edamam.com/ontologies/edamam.owl#recipe_...",
       "calories": 336,
       "totalWeight": 195.33,
       "dietLabels": [...],
       "healthLabels": [...],
       "cautions": [...]
     }
   }
   ```

## LLM integration

The typical integration pattern is:

1. At startup, the client fetches `/v1/mcp/schema`.
2. It injects the provided `system_prompt` into the LLM system message.
3. It passes the `functions` array as `functions` (or `tools`) to the LLM API.
4. When the model responds with a function/tool call:
   - Map `function.name` to one of the intents.
   - Call `POST /v1/ai/query` with `{ "intent": ..., "parameters": ... }`.
   - Feed the JSON result back to the LLM as a tool/function result message.

See the companion **edamam-mcp-client** repository for a working example using FastAPI + WebSocket + OpenAI Chat Completions.
