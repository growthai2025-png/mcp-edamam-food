# Changelog

## v1.0.0 — Stable Release

This is the first fully stable release of the **Edamam MCP (Machine Connector Processor)**.

It introduces a unified, LLM-friendly interface for food search, nutrition lookups, and food image analysis — all backed by the Edamam Food Database API.

---

### Added

#### Backend
- REST execution endpoint: `/v1/ai/query`
- JSON-RPC MCP endpoint: `/v1/rpc`
- MCP schema discovery endpoint: `/v1/mcp/schema`
- Support for all core operations:
  - `get_food_nutrition`
  - `search_food`
  - `analyze_food_image`
  - `get_nutrition_from_image` (alias)
- Automatic redirect from text → image intent when a URL is detected
- Unified error handling (400/404/500)
- Structured logging via `mcp_logger`

#### Inspector UI
- Transport selector (REST / JSON-RPC)
- Dynamic form generation from schema
- Save / Load Presets
- Request History + Replay
- Copy as cURL (for RPC and REST)
- Auto Retry
- Response panel with JSON formatting
- UI layout and styling improvements

#### Documentation
- Updated README with workflow diagrams and examples
- Extended API reference
- Realistic request/response examples
- LLM integration guide
- New `05-inspector.md` user manual

---

### Improvements

- Consistent schemas between REST, MCP, and JSON-RPC
- Input normalization for image analysis
- More reliable Edamam API handling
- Cleaner router separation
- Robust validation across all transports

---

### Known Limitations

- Streaming responses not yet implemented
- Inspector does not include an embedded AI agent (planned for v2)
- Single MCP backend (multi-MCP support planned)

---

### Status: **Production-Ready**
