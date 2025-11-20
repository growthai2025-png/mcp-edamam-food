# Overview

`edamam-mcp` is a small FastAPI service that wraps the **Edamam Food Database API**
and exposes an LLM‑friendly interface via two main endpoints:

- `GET /v1/mcp/schema` – a metadata endpoint that returns:
  - a ready‑to‑use system prompt, and
  - an array of function definitions (`functions`) compatible with OpenAI Chat Completions.
- `POST /v1/ai/query` – a unified execution endpoint that takes an `intent` and `parameters`.

The goal is to make it trivial for an LLM to:

- look up nutrition for foods by text (`get_food_nutrition`),
- search for candidate foods (`search_food`),
- analyze food images (`analyze_food_image`),

without exposing the full complexity of Edamam’s REST API.
