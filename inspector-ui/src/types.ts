//mcp-edamam/inspector-ui/src/types.ts

export interface McpFunction {
    type: 'function';
    function: {
      name: string;
      description: string;
      parameters: McpParameters;
    };
}
  
export interface McpParameters {
    type: 'object';
    properties: Record<string, McpProperty>;
    required?: string[];
}

export interface McpProperty {
    type: 'string' | 'number' | 'integer' | 'boolean';
    description?: string;
    default?: any;
}

export interface McpMeta {
    mcp_name: string;
    mcp_version: string;
    description: string;
    functions: McpFunction[];
    system_prompt?: string;
}

export interface JsonRpcRequest {
    jsonrpc: '2.0';
    method: string;
    params?: any;
    id: number | string;
}

export interface JsonRpcError {
    code: number;
    message: string;
    data?: any;
}

export interface JsonRpcResponse {
    jsonrpc: '2.0';
    result?: any;
    error?: JsonRpcError;
    id?: number | string | null;
}

export type TransportType = 'jsonrpc' | 'rest';

export interface InspectorPreset {
  name: string;
  transport: TransportType;
  method: string;
  params: any;
}

export interface HistoryItem {
  id: number;
  time: string;
  transport: TransportType;
  method: string;
  params: any;
  response: any;
  error?: string;
}
