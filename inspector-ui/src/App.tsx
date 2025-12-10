//mcp-edamam/inspector-ui/src/App.tsx

import { useEffect, useState } from 'react';
import { fetchSchema, executeCall } from './api';
import { McpMeta, McpFunction } from './types';
import { InspectorPreset, HistoryItem, TransportType } from './types';

import './App.css';


function pretty(obj: any) {
  if (obj === undefined) return '';
  try {
    return JSON.stringify(obj, null, 2);
  } catch {
    return String(obj);
  }
}

function getDefaultValue(type: string, prop: any) {
  if (prop?.default !== undefined) return prop.default;
  switch (type) {
    case 'number':
    case 'integer':
      return '';
    case 'boolean':
      return false;
    default:
      return '';
  }
}

function toCurlJsonRpc(method: string, params: any) {
  const payload = {
    jsonrpc: '2.0',
    method: 'tools/call',
    params: {
      name: method,
      arguments: params
    },
    id: 1
  };

  return `curl -X POST http://localhost:8000/v1/rpc \\
  -H "Content-Type: application/json" \\
  -d '${JSON.stringify(payload)}'`;
}

function toCurlRest(method: string, params: any) {
  switch (method) {
    case 'search_food': {
      const q = params?.query ?? '';
      const limit = params?.limit ?? 5;
      return `curl "http://localhost:8000/v1/food/search?q=${encodeURIComponent(q)}&limit=${limit}"`;
    }

    case 'get_nutrition_from_image': {
      return `curl -X POST http://localhost:8000/v1/food/analyze-image \\
  -H "Content-Type: application/json" \\
  -d '${JSON.stringify({ image: params?.image_url })}'`;
    }

    case 'get_food_nutrition': {
      return `curl -X POST http://localhost:8000/v1/ai/query \\
  -H "Content-Type: application/json" \\
  -d '${JSON.stringify({
        intent: 'get_food_nutrition',
        parameters: params
      })}'`;
    }

    default:
      return 'No REST cURL template available.';
  }
}

function App() {
  const [meta, setMeta] = useState<McpMeta | null>(null);
  const [selected, setSelected] = useState<McpFunction | null>(null);
  const [args, setArgs] = useState<Record<string, any>>({});
  const [rawRequest, setRawRequest] = useState<any>(null);
  const [response, setResponse] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [transport, setTransport] = useState<'jsonrpc' | 'rest'>('jsonrpc');
  const [presets, setPresets] = useState<InspectorPreset[]>([]);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [activeTab, setActiveTab] = useState<'response' | 'history'>('response');
  const [autoRetry, setAutoRetry] = useState(false);


  // Зареждаме MCP schema при стартиране
  useEffect(() => {
    fetchSchema()
      .then((schema) => {
        setMeta(schema);
        if (schema.functions && schema.functions.length > 0) {
          setSelected(schema.functions[0]);
        }
      })
      .catch((e) => setError(e.message));
  }, []);

  // При смяна на функция – генерираме начални аргументи
  useEffect(() => {
    if (!selected) return;
    const params = selected.function.parameters;
    const initial: Record<string, any> = {};
    Object.entries(params.properties || {}).forEach(([name, prop]: any) => {
      initial[name] = getDefaultValue(prop.type, prop);
    });
    setArgs(initial);
    setRawRequest(null);
    setResponse(null);
    setError(null);
  }, [selected]);

  // Load presets & history from localStorage
  useEffect(() => {
    try {
      const p = localStorage.getItem('mcp_presets');
      const h = localStorage.getItem('mcp_history');
      if (p) setPresets(JSON.parse(p));
      if (h) setHistory(JSON.parse(h));
    } catch {}
  }, []);

  useEffect(() => {
    localStorage.setItem('mcp_presets', JSON.stringify(presets));
  }, [presets]);

  useEffect(() => {
    localStorage.setItem('mcp_history', JSON.stringify(history));
  }, [history]);

  async function withRetry<T>(fn: () => Promise<T>, retries: number): Promise<T> {
    try {
      return await fn();
    } catch (err) {
      if (retries <= 0) throw err;
      return withRetry(fn, retries - 1);
    }
  }  

  const savePreset = () => {
    if (!selected) return;
    const name = prompt('Preset name?');
    if (!name) return;
  
    const preset: InspectorPreset = {
      name,
      transport,
      method: selected.function.name,
      params: args
    };
  
    setPresets(prev => [preset, ...prev]);
  };
  
  const loadPreset = (p: InspectorPreset) => {
    const fn = meta?.functions.find(f => f.function.name === p.method);
    if (!fn) return;
  
    setSelected(fn);
    setTransport(p.transport);
    setArgs(p.params);
    setRawRequest(null);
    setResponse(null);
    setError(null);
  };

  const handleArgChange = (name: string, type: string, value: string | boolean) => {
    setArgs((prev) => {
      let v: any = value;
      if (type === 'number' || type === 'integer') {
        v = value === '' ? '' : Number(value);
      }
      if (type === 'boolean') {
        v = Boolean(value);
      }
      return { ...prev, [name]: v };
    });
  };

  const handleExecute = async () => {
    if (!selected) return;
    setLoading(true);
    setError(null);
    setResponse(null);
  
    const funcName = selected.function.name;
  
    // Preview за JSON-RPC
    if (transport === 'jsonrpc') {
      const requestPreview = {
        jsonrpc: '2.0',
        method: 'tools/call',
        params: {
          name: funcName,
          arguments: args
        },
        id: 'preview'
      };
      setRawRequest(requestPreview);
    } else {
      setRawRequest({
        transport: 'rest',
        method: funcName,
        params: args
      });
    }
  
    try {
      const callFn = () => executeCall(transport, funcName, args);

      const res = autoRetry
        ? await withRetry(callFn, 2)
        : await callFn();

      setResponse(res);
  
      setHistory(prev => [
        {
          id: Date.now(),
          time: new Date().toLocaleTimeString(),
          transport,
          method: funcName,
          params: args,
          response: res,
          error: res?.error ? `${res.error.code}: ${res.error.message}` : undefined
        },
        ...prev
      ]);      

      if (res?.error) {
        setError(`${res.error.code}: ${res.error.message}`);
      }
    } catch (e: any) {
      setError(e.message || String(e));
    } finally {
      setLoading(false);
    }
  };
  

  if (error && !meta) {
    return (
      <div className="app">
        <div className="fatal">
          <h1>MCP Inspector</h1>
          <p>Не успях да заредя /v1/mcp/schema</p>
          <pre>{error}</pre>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <h1>MCP Inspector</h1>
        {meta && (
          <>
            <div className="meta">
              <div><strong>Name:</strong> {meta.mcp_name}</div>
              <div><strong>Version:</strong> {meta.mcp_version}</div>
            </div>
            <h2>Functions</h2>
            <ul className="func-list">
              {meta.functions.map((fn) => (
                <li
                  key={fn.function.name}
                  className={selected?.function.name === fn.function.name ? 'active' : ''}
                  onClick={() => setSelected(fn)}
                >
                  <div className="func-name">{fn.function.name}</div>
                  <div className="func-desc">{fn.function.description}</div>
                </li>
              ))}
            </ul>
          </>
        )}
      </aside>

      <main className="main">
        {selected && (
          <div className="content">
            <section className="section">
              <h2>{selected.function.name}</h2>
              <p>{selected.function.description}</p>

              <h3>Arguments</h3>
              <div className="form">
                {Object.entries(selected.function.parameters.properties || {}).map(
                  ([name, prop]: any) => {
                    const isRequired = selected.function.parameters.required?.includes(name);
                    const type = prop.type || 'string';

                    return (
                      <div key={name} className="field">
                        <label>
                          <span className="field-name">
                            {name}
                            {isRequired && <span className="required">*</span>}
                            <span className="field-type">({type})</span>
                          </span>
                          {prop.description && (
                            <span className="field-desc">{prop.description}</span>
                          )}
                        </label>

                        {type === 'boolean' ? (
                          <input
                            type="checkbox"
                            checked={Boolean(args[name])}
                            onChange={(e) => handleArgChange(name, type, e.target.checked)}
                          />
                        ) : (
                          <input
                            type={type === 'number' || type === 'integer' ? 'number' : 'text'}
                            value={args[name] ?? ''}
                            onChange={(e) => handleArgChange(name, type, e.target.value)}
                          />
                        )}
                      </div>
                    );
                  }
                )}
              </div>

              <div style={{ display: 'flex', gap: 12, marginBottom: 12 }}>

                <div style={{
                  marginBottom: 12,
                  padding: '8px 10px',
                  borderRadius: 10,
                  border: '1px solid #1f2937',
                  background: '#020617',
                  fontSize: 12,
                  color: '#9ca3af'
                }}>
                  {transport === 'jsonrpc' ? (
                    <>
                      <div><strong>JSON-RPC Endpoint:</strong></div>
                      <div>POST /v1/rpc</div>
                      <div>Schema: GET /v1/mcp/schema</div>
                    </>
                  ) : (
                    <>
                      <div><strong>REST Endpoints:</strong></div>
                      <div>GET /v1/food/search</div>
                      <div>POST /v1/food/analyze-image</div>
                      <div>POST /v1/ai/query</div>
                    </>
                  )}
                </div>

                <label>
                  <input
                    type="radio"
                    checked={transport === 'jsonrpc'}
                    onChange={() => setTransport('jsonrpc')}
                  /> JSON-RPC
                </label>

                <label>
                  <input
                    type="radio"
                    checked={transport === 'rest'}
                    onChange={() => setTransport('rest')}
                  /> REST
                </label>

                <label style={{ marginBottom: 12, display: 'block' }}>
                  <input
                    type="checkbox"
                    checked={autoRetry}
                    onChange={(e) => setAutoRetry(e.target.checked)}
                  />{' '}
                  Auto Retry (2x)
                </label>

              </div>

              <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
                <button onClick={savePreset}>⭐ Save Preset</button>

                {presets.length > 0 && (
                  <select onChange={(e) => loadPreset(presets[Number(e.target.value)])}>
                    <option>▼ Load Preset</option>
                    {presets.map((p, i) => (
                      <option key={i} value={i}>
                        {p.name} ({p.transport})
                      </option>
                    ))}
                  </select>
                )}
              </div>

              <button className="execute" onClick={handleExecute} disabled={loading}>
                {loading ? 'Изпълнява...' : 'Execute tools/call'}
              </button>
              {error && (
                <div className="error">
                  <strong>Грешка:</strong> {error}
                </div>
              )}
            </section>

            <section className="section">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h3>{transport === 'jsonrpc' ? 'JSON-RPC Request' : 'REST Request'}</h3>

                <button
                  onClick={() => {
                    if (!selected) return;
                    const curl =
                      transport === 'jsonrpc'
                        ? toCurlJsonRpc(selected.function.name, args)
                        : toCurlRest(selected.function.name, args);

                    navigator.clipboard.writeText(curl);
                  }}
                >
                  📋 Copy as cURL
                </button>
              </div>

              <pre className="code">{pretty(rawRequest)}</pre>
            </section>

            <section className="section">
              <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
                <button style={{
                  background: activeTab === 'response' ? '#2563eb' : '#020617'
                }} onClick={() => setActiveTab('response')}>
                  Response
                </button>

                <button style={{
                  background: activeTab === 'history' ? '#2563eb' : '#020617'
                }} onClick={() => setActiveTab('history')}>
                  History
                </button>
              </div>

              {activeTab === 'response' && (
                <>
                  <h3>{transport === 'jsonrpc' ? 'JSON-RPC Response' : 'REST Response'}</h3>
                  <pre className="code">{pretty(response)}</pre>
                  <button onClick={() => navigator.clipboard.writeText(pretty(response))}>
                  📋 Copy JSON
                  </button>
                </>
              )}

              {activeTab === 'history' && (
                <>
                  <h3>History</h3>

                  {history.length === 0 && <div>No history yet.</div>}

                  {history.map(item => (
                    <div key={item.id} style={{ marginBottom: 12, paddingBottom: 8, borderBottom: '1px solid #1f2937' }}>
                      <div>
                        <strong>{item.time}</strong> — {item.method} ({item.transport})
                      </div>

                      <div style={{ display: 'flex', gap: 8, marginTop: 6 }}>
                        <button
                          onClick={() => {
                            setTransport(item.transport);
                            const fn = meta?.functions.find(f => f.function.name === item.method);
                            if (fn) setSelected(fn);
                            setArgs(item.params);
                          }}
                        >
                          ▶ Replay
                        </button>

                        <button
                          onClick={() => navigator.clipboard.writeText(JSON.stringify(item.params, null, 2))}
                        >
                          📋 Copy Params
                        </button>

                        <button
                          onClick={() => navigator.clipboard.writeText(JSON.stringify(item.response, null, 2))}
                        >
                          📋 Copy Result
                        </button>
                      </div>
                    </div>
                  ))}
                </>
              )}
            </section>

          </div>
        )}
      </main>
    </div>
  );
}

export default App;
