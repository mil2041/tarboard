# Grantboard Claude proxy (Cloudflare Worker)

The dashboard is a static file and **cannot hold an API key**. This Worker holds `ANTHROPIC_API_KEY`
as a secret and forwards a tight allowlist of `/v1/messages` calls (model allowlist, `max_tokens` cap,
CORS, optional per-IP daily cap, optional shared demo token). Streaming (SSE) passes straight through.

## Deploy (2 minutes)

```bash
cd worker
npm i -g wrangler            # or: npx wrangler ...
wrangler login
wrangler secret put ANTHROPIC_API_KEY     # paste your Anthropic key
# optional hardening:
wrangler secret put DEMO_TOKEN            # a random string; the page sends it as x-demo-token
wrangler deploy
```

`wrangler deploy` prints a URL like `https://grantboard-claude.<you>.workers.dev`.

## Wire it into the app

Open the dashboard, click the **⚙ gear** in the masthead, and paste the Worker URL (and demo token if you
set one). It's stored in `localStorage`. Alternatively hard-code it in `index.template.html`:

```js
const CONFIG = { workerUrl: "https://grantboard-claude.<you>.workers.dev", demoToken: "", ... };
```

## Test

```bash
curl -s https://grantboard-claude.<you>.workers.dev \
  -H 'Content-Type: application/json' -H 'x-demo-token: <token-if-set>' \
  -d '{"model":"claude-opus-4-8","max_tokens":64,"messages":[{"role":"user","content":"say hi in 3 words"}]}'
```

## Option C — run on your Claude subscription via Claude Code (no API key, no Cloudflare)

For a **local** demo you can skip the Worker/key entirely and route the app's Claude calls through the
Claude Code CLI, using your existing Claude Code login (your Claude subscription):

```bash
python3 worker/claude_code_bridge.py        # serves http://localhost:8788
# then in the app: ⚙ gear → Worker URL = http://localhost:8788
```

The bridge speaks the same request shape the app sends and internally runs `claude -p`, mapping the
result back into the Messages-API response the client expects (forced-JSON → a `tool_use` block; streaming
→ SSE deltas). Verified end-to-end: CV parse (~18s), 20-grant re-rank (~10s), streamed fit brief (~7s).
Caveats: it's **local-only** (remote judges can't reach it), each call pays Claude Code's cold-start so
it's slower than the raw API, and rapid repeated searches can leave `claude -p` workers running briefly.
For a hosted/shared demo, use the Cloudflare Worker above. Env: `BRIDGE_PORT`, `BRIDGE_MODEL`.

## Demo insurance (no Worker needed)

The app also supports a **paste-your-own-key dev mode** (same ⚙ gear). It calls `api.anthropic.com`
directly from the browser with the `anthropic-dangerous-direct-browser-access: true` header. Use this only
for local rehearsal — **never ship a page with a key in it**. `build.py` asserts the built `index.html`
contains no `sk-ant`.
