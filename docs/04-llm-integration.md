# LLM Integration

The `edamam-mcp` service is designed for direct integration with LLMs
using the **MCP (Machine Connector Processor)** pattern.

---

## Typical Tool Loop

1. Fetch MCP schema:

````

GET /v1/mcp/schema

```

2. Inject `system_prompt` into the system message  
3. Register `functions` as available tools  
4. Let the model choose a tool  
5. Execute the call via:
   - `/v1/ai/query` (REST)  
   - `/v1/rpc` (JSON-RPC)  
6. Return the result as a tool/function response  
7. Ask the model for a final natural-language answer

---

## Supported Patterns

- Single-step tool calls
- Multi-step reasoning
- Tool chaining
- Agent-style orchestration (v2+)

---

A full working example is available in the **edamam-mcp-client** repository.