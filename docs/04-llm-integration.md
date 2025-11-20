# LLM Integration

A typical OpenAI Chat Completions loop with MCP looks like this:

1. Fetch MCP schema
2. Call OpenAI with system prompt + functions
3. If the model returns a function/tool call:
   - Call `/v1/ai/query`
   - Feed result back as a tool/function message
   - Ask OpenAI for a final natural‑language answer

See the **edamam-mcp-client** repository for a complete FastAPI + WebSocket example.
