# Release Checklist — v1.0.0 (Stable)

This checklist ensures the MCP backend and Inspector UI are stable, consistent, and ready for external testers or production use.

---

## 1. Backend (FastAPI)

- [x] `/v1/ai/query` endpoint is fully functional
- [x] Supported intents:
  - [x] `get_food_nutrition`
  - [x] `search_food`
  - [x] `analyze_food_image`
- [x] Auto-redirect for image URLs → `analyze_food_image`
- [x] Proper handling of 400 / 404 / 500 responses
- [x] Logging via `mcp_logger`
- [x] No remaining 422 validation errors
- [x] No debug or leftover development endpoints

---

## 2. MCP / JSON-RPC

- [x] `/v1/rpc` accepts raw JSON-RPC 2.0 requests
- [x] `tools/list` works and returns valid schemas
- [x] `tools/call` executes all supported tools
- [x] Aliases supported:
  - [x] `get_nutrition_from_image` → image analyzer
- [x] Batch JSON-RPC requests supported
- [x] CORS preflight (`OPTIONS`) works as expected

---

## 3. MCP Schema (`/v1/mcp/schema`)

- [x] `mcp_name`, `mcp_version`, `description`
- [x] `system_prompt` included
- [x] Full `functions` array with parameter schemas
- [x] No invalid or missing properties
- [x] Version updated to `1.0.0`

---

## 4. Swagger / OpenAPI

- [x] Accurate descriptions for all intents
- [x] Realistic request examples for:
  - [x] name query
  - [x] UPC / barcode lookup
  - [x] image analysis
- [x] Error responses documented
- [x] No JSON-RPC artifacts in Swagger

---

## 5. Inspector UI (React)

- [x] Transport selector (REST / JSON-RPC)
- [x] Real-time request builder
- [x] Presets (save/load)
- [x] History + replay
- [x] Copy as cURL
- [x] Auto Retry support
- [x] Response preview panel
- [x] UI visual cleanup (spacing, colors, typography)
- [x] No console errors in dev tools

---

## 6. Environment & Config

- [x] `EDAMAM_APP_ID` defined
- [x] `EDAMAM_APP_KEY` defined
- [x] `.env` excluded via `.gitignore`
- [x] `requirements.txt` up-to-date
- [x] No unused dependencies

---

## 7. Documentation

- [x] Updated `README.md`
- [x] Updated:
  - [x] `docs/01-overview.md`
  - [x] `docs/02-api-reference.md`
  - [x] `docs/03-examples.md`
  - [x] `docs/04-llm-integration.md`
- [x] Added:
  - [x] `docs/05-inspector.md` (Inspector UI manual)
- [x] REST + JSON-RPC usage examples validated

---

## 8. Final Sanity Check

- [x] No stray print/debug statements
- [x] No development URLs or local paths
- [x] Routes list is clean (no leftover `/rpc-test`)
- [x] Version bump completed everywhere
- [x] App starts with no warnings or errors

---

### Ready for tagging and publishing as **v1.0.0**
