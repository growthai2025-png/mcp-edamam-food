//mcp-edamam/inspector-ui/src/api.ts

import { McpMeta, JsonRpcRequest, JsonRpcResponse } from './types';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export async function fetchSchema(): Promise<McpMeta> {
  const res = await fetch(`${API_BASE}/v1/mcp/schema`);
  if (!res.ok) {
    throw new Error(`Schema fetch failed: ${res.status}`);
  }
  return res.json();
}

let nextId = 1;
function getNextId() {
  return nextId++;
}

// --- JSON-RPC ADAPTER ---

export async function jsonRpcCall(method: string, params?: any): Promise<JsonRpcResponse> {
  const body: JsonRpcRequest = {
    jsonrpc: '2.0',
    method,
    params,
    id: getNextId()
  };

  const res = await fetch(`${API_BASE}/v1/rpc/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(body)
  });

  if (!res.ok) {
    throw new Error(`JSON-RPC HTTP error: ${res.status}`);
  }

  return res.json();
}

/**
 * По-удобен helper за tools/call, защото твоят rpc_router го очаква така:
 * { jsonrpc:"2.0", method:"tools/call", params:{ name, arguments }, id }
 */
export async function callTool(name: string, args: Record<string, any>): Promise<JsonRpcResponse> {
  return jsonRpcCall('tools/call', {
    name,
    arguments: args
  });
}

// --- REST ADAPTER ---

export async function restCall(method: string, params?: any): Promise<any> {
  switch (method) {
    case 'search_food': {
      const q = params?.query ?? '';
      const limit = params?.limit ?? 5;
      const url = `${API_BASE}/v1/food/search?q=${encodeURIComponent(q)}&limit=${limit}`;
      const res = await fetch(url);
      if (!res.ok) throw new Error(`REST error ${res.status}`);
      return res.json();
    }

    case 'get_nutrition_from_image': {
      const res = await fetch(`${API_BASE}/v1/food/analyze-image`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          image: params?.image_url
        })
      });
      if (!res.ok) throw new Error(`REST error ${res.status}`);
      return res.json();
    }

    case 'get_food_nutrition': {
      const res = await fetch(`${API_BASE}/v1/ai/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          intent: 'get_food_nutrition',
          parameters: params
        })
      });
      if (!res.ok) throw new Error(`REST error ${res.status}`);
      return res.json();
    }

    default:
      throw new Error(`Unknown REST method: ${method}`);
  }
}

// --- UNIFIED CALL ---

export async function executeCall(
  transport: 'jsonrpc' | 'rest',
  method: string,
  params: any
) {
  if (transport === 'jsonrpc') {
    return callTool(method, params);
  }
  if (transport === 'rest') {
    return restCall(method, params);
  }
}
