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

## Demo insurance (no Worker needed)

The app also supports a **paste-your-own-key dev mode** (same ⚙ gear). It calls `api.anthropic.com`
directly from the browser with the `anthropic-dangerous-direct-browser-access: true` header. Use this only
for local rehearsal — **never ship a page with a key in it**. `build.py` asserts the built `index.html`
contains no `sk-ant`.
