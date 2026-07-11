/**
 * Grantboard → Claude proxy (Cloudflare Worker)
 * ------------------------------------------------
 * The dashboard is a static file, so it cannot hold an Anthropic API key.
 * This ~90-line Worker holds the key as a secret and forwards ONLY a tight
 * allowlist of /v1/messages calls, with CORS + a per-IP daily cap.
 *
 * Deploy:  see worker/README.md   (npx wrangler deploy + wrangler secret put ANTHROPIC_API_KEY)
 *
 * Secrets / vars (wrangler):
 *   ANTHROPIC_API_KEY   (secret, required)
 *   DEMO_TOKEN          (var, optional shared token the page sends as x-demo-token)
 *   ALLOW_ORIGIN        (var, optional exact origin to allow in addition to "null"; default "*")
 *   RATE_KV             (KV namespace binding, optional — enables the per-IP daily cap)
 */

const ANTHROPIC_URL = "https://api.anthropic.com/v1/messages";
const ALLOWED_MODELS = new Set(["claude-opus-4-8", "claude-haiku-4-5"]);
const MAX_TOKENS_CAP = 4096;
const DAILY_CAP = 400; // requests per IP per UTC day (only enforced if RATE_KV is bound)

function cors(env, origin) {
  const allow = origin === "null" ? "null" : (env.ALLOW_ORIGIN || "*");
  return {
    "Access-Control-Allow-Origin": allow,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, x-demo-token",
    "Access-Control-Max-Age": "86400",
    "Vary": "Origin",
  };
}
const json = (obj, status, headers) =>
  new Response(JSON.stringify(obj), { status, headers: { "Content-Type": "application/json", ...headers } });

export default {
  async fetch(request, env) {
    const origin = request.headers.get("Origin") || "*";
    const ch = cors(env, origin);

    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: ch });
    if (request.method !== "POST") return json({ error: "POST only" }, 405, ch);

    if (env.DEMO_TOKEN && request.headers.get("x-demo-token") !== env.DEMO_TOKEN)
      return json({ error: "bad or missing x-demo-token" }, 401, ch);

    let body;
    try { body = await request.json(); }
    catch { return json({ error: "invalid JSON body" }, 400, ch); }

    // ---- allowlist / clamp ----
    if (!ALLOWED_MODELS.has(body.model))
      return json({ error: "model not allowed", allowed: [...ALLOWED_MODELS] }, 400, ch);
    if (typeof body.max_tokens !== "number" || body.max_tokens > MAX_TOKENS_CAP)
      body.max_tokens = Math.min(body.max_tokens || 1024, MAX_TOKENS_CAP);
    // Opus 4.8 rejects these — strip defensively.
    delete body.temperature;
    delete body.top_p;

    // ---- optional per-IP daily cap ----
    if (env.RATE_KV) {
      const ip = request.headers.get("CF-Connecting-IP") || "anon";
      const day = new Date().toISOString().slice(0, 10);
      const key = `rl:${ip}:${day}`;
      const n = parseInt((await env.RATE_KV.get(key)) || "0", 10);
      if (n >= DAILY_CAP) return json({ error: "daily limit reached" }, 429, ch);
      await env.RATE_KV.put(key, String(n + 1), { expirationTtl: 172800 });
    }

    // ---- forward ----
    const upstream = await fetch(ANTHROPIC_URL, {
      method: "POST",
      headers: {
        "x-api-key": env.ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    // Stream SSE straight through; JSON responses pass through too.
    return new Response(upstream.body, {
      status: upstream.status,
      headers: {
        "Content-Type": upstream.headers.get("Content-Type") || "application/json",
        ...ch,
      },
    });
  },
};
