#!/usr/bin/env python3
"""Local bridge — run Grantboard's Claude calls through the Claude Code CLI.

The dashboard normally calls a Cloudflare Worker that forwards to the Anthropic
Messages API (needs an API key). This bridge is an alternative for LOCAL use: it
speaks the same request shape the app sends, but internally runs `claude -p`, so
every call uses your existing Claude Code auth (your Claude subscription) — no API
key, no Cloudflare, no per-call billing beyond your plan.

Usage:
    python3 worker/claude_code_bridge.py            # serves http://localhost:8788
    # then in the app: click the ⚙ gear, set "Worker URL" = http://localhost:8788

Env:
    BRIDGE_PORT   (default 8788)
    BRIDGE_MODEL  (force one model alias, e.g. "sonnet"; default maps by request)

Notes:
- Local demo path only — it is not reachable by remote judges. For a hosted demo
  use the Cloudflare Worker (worker/worker.js) instead.
- Each call spawns a Claude Code turn, so it's slower than the raw API.
"""
import json, os, re, shutil, subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT   = int(os.environ.get("BRIDGE_PORT", "8788"))
CLAUDE = shutil.which("claude") or "claude"
FORCE  = os.environ.get("BRIDGE_MODEL", "").strip()

def model_alias(m):
    if FORCE: return FORCE
    m = (m or "").lower()
    if "haiku" in m: return "haiku"
    # keep opus/sonnet requests on sonnet so a single turn returns inside the app's timeouts
    return "sonnet"

def run_claude(system, prompt, model):
    cmd = [CLAUDE, "-p", "--output-format", "json", "--model", model_alias(model)]
    if system:
        cmd += ["--system-prompt", system]
    p = subprocess.run(cmd, input=prompt or "", capture_output=True, text=True, timeout=100)
    if p.returncode != 0:
        raise RuntimeError("claude cli exit %d: %s" % (p.returncode, (p.stderr or "")[:300]))
    env = json.loads(p.stdout)
    if env.get("is_error"):
        raise RuntimeError("claude error: %s" % str(env.get("result"))[:300])
    return env.get("result", "")

def extract_json(text):
    t = (text or "").strip()
    t = re.sub(r"^```(?:json)?\s*", "", t)
    t = re.sub(r"\s*```$", "", t).strip()
    i, j = t.find("{"), t.rfind("}")
    if i >= 0 and j > i:
        t = t[i:j + 1]
    return json.loads(t)

def user_text(messages):
    parts = []
    for m in messages or []:
        c = m.get("content")
        if isinstance(c, str):
            parts.append(c)
        elif isinstance(c, list):
            for b in c:
                if isinstance(b, dict) and b.get("type") == "text":
                    parts.append(b.get("text", ""))
    return "\n\n".join(parts)

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, x-demo-token")

    def do_OPTIONS(self):
        self.send_response(204); self._cors(); self.end_headers()

    def _json(self, code, obj):
        data = json.dumps(obj).encode()
        self.send_response(code); self._cors()
        self.send_header("Content-Type", "application/json"); self.end_headers()
        try: self.wfile.write(data)
        except BrokenPipeError: pass

    def do_POST(self):
        try:
            n = int(self.headers.get("Content-Length", "0"))
            body = json.loads(self.rfile.read(n) or "{}")
        except Exception:
            return self._json(400, {"error": "bad json body"})

        system  = body.get("system") or ""
        prompt  = user_text(body.get("messages"))
        model   = body.get("model")
        tools   = body.get("tools")
        stream  = bool(body.get("stream"))

        try:
            if tools:  # forced structured JSON -> synthesize a Messages tool_use response
                schema = (tools[0] or {}).get("input_schema", {})
                sysj = (system + "\n\n" if system else "") + \
                    "Respond with ONLY a single JSON object — no prose, no markdown fences — valid against this JSON Schema:\n" + json.dumps(schema)
                obj = extract_json(run_claude(sysj, prompt, model))
                return self._json(200, {"content": [{"type": "tool_use", "id": "emit_1", "name": "emit", "input": obj}], "stop_reason": "tool_use"})

            txt = run_claude(system, prompt, model)
            if stream:  # emit SSE deltas the app's stream parser understands
                self.send_response(200); self._cors()
                self.send_header("Content-Type", "text/event-stream"); self.end_headers()
                try:
                    for k in range(0, len(txt), 40):
                        ev = {"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": txt[k:k+40]}}
                        self.wfile.write(("data: " + json.dumps(ev) + "\n\n").encode()); self.wfile.flush()
                    self.wfile.write(b'data: {"type":"message_stop"}\n\n'); self.wfile.flush()
                except BrokenPipeError:
                    pass
            else:
                return self._json(200, {"content": [{"type": "text", "text": txt}], "stop_reason": "end_turn"})
        except Exception as e:
            return self._json(502, {"error": str(e)[:400]})

if __name__ == "__main__":
    print("Claude Code bridge → http://localhost:%d   (CLI: %s)" % (PORT, CLAUDE), flush=True)
    print("In the app: ⚙ gear → Worker URL = http://localhost:%d" % PORT, flush=True)
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
