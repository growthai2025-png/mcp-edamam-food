# MCP Inspector UI

The MCP Inspector is a local web interface for testing:

- ✅ REST endpoints
- ✅ JSON-RPC (MCP) tools
- ✅ Presets
- ✅ Request history
- ✅ Replay
- ✅ Copy as cURL
- ✅ Auto Retry

---

## Starting the Inspector

```bash
cd inspector-ui
npm install
npm run dev
````

Open:

```
http://localhost:5173
```

---

## Transport Selector

The Inspector supports two transports:

* **JSON-RPC** → calls `/v1/rpc`
* **REST** → calls:

  * `/v1/ai/query`
  * `/v1/food/search`
  * `/v1/food/analyze-image`

You can switch transport at any time.

---

## Executing a Call

1. Select a function from the left sidebar
2. Fill in the arguments
3. Choose transport (REST or JSON-RPC)
4. Click **Execute**

The raw request and response are displayed on the right.

---

## Presets

* Click ⭐ **Save Preset** to store a request
* Use **Load Preset** to restore it later
* Presets are stored in `localStorage`

---

## History & Replay

* Every executed request is added to **History**
* You can:

  * ▶ Replay a call
  * 📋 Copy params
  * 📋 Copy result

---

## Copy as cURL

The **Copy as cURL** button generates a ready-to-run `curl` command
for the current request, matching the selected transport.

---

## Auto Retry

Enable **Auto Retry (2x)** to automatically retry failed requests.

---

## Intended Use

The Inspector is intended for:

* Backend development
* QA and debugging
* Prompt & tool testing
* MCP integration validation
