# Grantboard → Grant-Fit Copilot: Implementation Plan

**Goal:** Put Claude at the center of the product for the *Built with Claude: Life Sciences* hackathon
(Development Track). The app is currently a beautiful but **zero-Claude** keyword matcher. A multi-lens
review + adversarial judge scored the current build **47/100** and the post-sprint build **79/100**; the
entire gap is the two heaviest rubric criteria — **Relevancy (meaningful Claude use)** and **Technical
Innovation (use of the Claude API)**.

> **Thesis for the pitch:** *Deterministic guardrails decide eligibility — auditable, free, and impossible
> to hallucinate. Claude makes it useful: it reads your CV, re-ranks real 2026 funding with reasons, explains
> the eligibility prose no regex can, and drafts your pitch angle.* Shipped as one static HTML file + a
> ~50-line Cloudflare Worker.

Deadline reality: hackathon ends **2026-07-13**. This is a ~2-day sprint. Ship the **core Claude loop first**,
harden it, then layer. **Never ship five features at 80%.**

---

## Architecture (what changes, what stays)

```
CV / paste ─▶ [Claude: CV→profile]* ─▶ state.focus / topics / phdYear / careerStage / searchQueries
                                              │
curated(187)+JHU(81) ─▶ scoreGrant (lexical recall) ─┐
Grants.gov live (+ cached seed) ─────────────────────┤
                                              ▼
                                   top-20 by _score ─▶ [Claude: re-rank + reasons]* ─▶ feed
                                              │
                          regex eligibility() (deterministic guardrails, UNCHANGED)
                                              │
                    shortlist card ─▶ [Claude: streamed fit brief]*  (replaces canned ANGLE map)
                    federal expand ─▶ [Claude: "can I apply?" second opinion]*
```
`*` = new Claude call, routed through `askClaude()` → Worker proxy (or paste-your-own-key dev mode).
Every Claude call **degrades gracefully** to the existing lexical/regex/canned behavior when offline.

**Keep, do not replace:** `scoreGrant` (reframed as *retrieval layer*), the whole regex eligibility engine
(`citizenshipReq`/`degreeWindow`/`nationalityRestriction`/`requiresPhysicianOnly`/`requiresCompletingPhD` —
reframed as *deterministic guardrails Claude never overrides*), the single-file + build.py design, live
Grants.gov.

**Files:** `index.template.html` (all app logic), `build.py` (inliner), `data/*.json`, new `worker/worker.js`.

---

## Non-negotiable rules (trust = the whole pitch)

For a **funding** tool, one fabricated deadline/amount/eligibility fact scores *worse* than the honest
deterministic version — it destroys the HHH axis that is weighted most. Therefore:

1. **Claude never authors a deadline, amount, eligibility status, or URL that renders as fact.** Those always
   come from the dataset object. Claude may *rank*, *explain*, and *quote provided text* only.
2. **Grounding prompt on every ranking/brief call:** *"You may only reference grant objects provided here by
   id. Never invent grants, deadlines, amounts, eligibility, or URLs. If a fact is not in the object, say
   'see funder page'."*
3. **Client-side id filter:** drop any grant id Claude returns that is not in the payload map.
4. **Never gate rendering on a network call.** Paint deterministic results instantly; patch Claude output in
   asynchronously. No `await` on Grants.gov or Claude before first paint.
5. **Never embed the API key in `index.html`.** `build.py` asserts the output contains no `sk-ant`.
6. **Never fake a "Claude" badge** before the call is actually wired — judges probe.

---

## Model / API config

- Default workhorse: **`claude-opus-4-8`**. Latency escape hatch: **`claude-haiku-4-5`** (same
  structured-output support; flip one CONFIG line if demo pacing needs it). Do **not** use Sonnet/Fable here
  unless rerank latency bites.
- Opus 4.8 caveat: **do not send `temperature` or `budget_tokens`** (both 400). Use
  `thinking:{type:'adaptive'}` where useful.
- Structured output: use `output_config.format = {type:'json_schema', schema:{... additionalProperties:false,
  required:[...]}}` so JSON is guaranteed parseable.
- Cost: ~**$0.15–0.25 / session** on Opus. Cache every call by a stable hash (CV bytes; profile+ids;
  grant-id+profile) in `localStorage` so re-filtering and rehearsals don't re-bill.

---

## Task breakdown (ordered by score-per-hour; keep app runnable at every step)

### T2 — Cloudflare Worker proxy `worker/worker.js` (~2–3h) — PREREQUISITE
- `OPTIONS` → 204 + CORS headers. Allow origin `null` (file://) **and** the deployed host, gated by a shared
  demo token (`x-demo-token`).
- `POST` → parse JSON; enforce allowlist: `model ∈ {claude-opus-4-8, claude-haiku-4-5}`, `max_tokens ≤ 4096`,
  streaming ok. Forward to `https://api.anthropic.com/v1/messages` with `x-api-key: env.ANTHROPIC_API_KEY`,
  `anthropic-version: 2023-06-01`. Pipe body back (SSE or JSON) with CORS headers. Per-IP daily cap.
- Deploy: `npx wrangler deploy`; `wrangler secret put ANTHROPIC_API_KEY`. Doc in `worker/README.md`.
- **Acceptance:** `curl` the Worker with a tiny messages payload returns a completion; OPTIONS returns CORS.

### T3 — `askClaude()` client helper + CONFIG + key UI (~1h, folds into T2)
- `CONFIG = { workerUrl, demoToken, model:'claude-opus-4-8', fastModel:'claude-haiku-4-5' }`.
- `async askClaude(payload, {onToken, timeoutMs=8000, stream=false})`: routes to Worker (or direct
  `api.anthropic.com` with `anthropic-dangerous-direct-browser-access:true` when a user key is set);
  `AbortController` timeout for JSON calls, no timeout for streams; parses SSE `content_block_delta`/
  `text_delta` for streaming; returns parsed JSON for `output_config` calls. Throws on failure so callers
  fall back.
- `claudeReady()` → true if Worker configured or user key present. Gate all Claude UI on it (else show the
  deterministic behavior silently).
- Settings gear (masthead) → paste-your-own-key field saved to `localStorage` (`gb_userkey`); enables direct
  browser calls for dev/demo insurance.
- **Acceptance:** with a pasted key, a trivial `askClaude` round-trips; with none, `claudeReady()` is false
  and nothing breaks.

### T4 — Freeze-proof `runSearch` + timeouts + dedup + seed fallback (~4h) — pure client, no key needed
- Split `runSearch`: score + render **local (curated+JHU) immediately**; then patch federal in when
  `fetchFederal` resolves. Never block first paint.
- Wrap `ggSearch` (`index.template.html:857`) and `fetchFederalDetail` (`:899`) fetches in `AbortController`
  with **7s** timeout. On abort/reject: `fedStatus.err=true`, show offline pill.
- **Seed fallback:** `build.py` inlines `data/federal_seed.json` (already generated, 40 real oppHits) as
  `FEDERAL_SEED`. On federal failure, map the seed through the same `mapHit()` used for live hits; relabel the
  pill **"Grants.gov (cached snapshot)"**.
- Empty-state guard before `feed.innerHTML` (`:1211`) using `emptyHTML`.
- Dedup `localPool` (`:921`) by normalized `name+funder` key (≈5 curated/JHU dupes render twice today);
  prefer the JHU record.
- **Acceptance:** with network blocked, search still renders curated + seed instantly; no frozen panel; no
  empty feed; no duplicate cards.

### T5 — Claude CV → structured profile in `ingestCV` (~4–6h) — CORE
- In `handleFile`/`ingestCV` (`:639`/`:578`): send extracted CV text (uniform across pdf/paste/txt) to
  `askClaude` with `output_config` schema:
  ```
  PROFILE_SCHEMA = { researchAreas[], techniques[], focusAreas(enum FOCUS_AREAS),
    diseaseSubtypes(enum SUBTYPES keys), careerStage, phdYear(int|null),
    citizenshipSignals(string), field(freeform), searchQueries[4-6] }
  ```
  (Enhancement if time: native PDF `document` block from the ArrayBuffer in `handleFile` — better on
  two-column CVs. Text path is the reliable default.)
- On success: overwrite `state.cvKeywords`/`state.focus`/`state.subtypes`; autofill `#phdYear`/`#careerStage`
  (then `saveProfile`); prepend `searchQueries` into `buildFederalQueries` (`:850`).
- **Out-of-domain CV:** if `field` ∉ hem/onc, relax `focusPass` to keep AI/computational + general-biomedical
  + live-federal results, and show an honest banner ("outside our hem/onc curated set — showing N live
  federal matches"). This defuses the #1 demo landmine (a judge's non-oncology CV currently returns
  confidently-wrong blood-cancer results).
- Cache by CV-text hash. Fall back to `extractKeywords()` on failure. Staged `#cvStat`: "Claude is reading
  your CV… → found N methods → drafting M federal queries".
- **Acceptance:** demo CV self-configures focus/PhD-year/stage; a non-onc CV yields non-empty, non-wrong
  results; offline → old lexicon path.

### T6 — Claude re-rank of lexical top-20 in `runSearch` (~4–5h) — BIGGEST SINGLE DELTA
- After instant lexical render, take top 20 by `_score`; **one** `askClaude` call: profile summary + 20
  compact lines `(id, name, funder, focusAreas, description[:250], amount, deadline)` → schema
  `{rankings:[{id, fitScore 0-100, why(≤20 words)}]}`, `effort:'medium'`.
- Apply grounding guards (rules #2–#3). On resolve: set `g._claudeScore`/`g._claudeWhy`, re-sort with a
  visible reshuffle under a **"Re-ranked by Claude"** badge, replace the matched-term chips in `gc-why`
  (`:1126`) with the `why` line. **Deadlines/amounts still render from dataset fields.**
- Add a **lexical ↔ Claude toggle** by the sort control (doubles as the judges' before/after).
- Cache by `hash(profile+ids)`. Default Opus; one-line switch to Haiku. Never gate the feed or disable Search
  on this promise.
- **Demo money-shot:** the hand-coded prostate-grant exclusion comment (`:963-969`) vs. Claude demoting that
  grant live *with a stated reason*.
- **Acceptance:** results reshuffle with per-grant reasons; unknown ids dropped; offline → lexical order,
  no error.

### T7 — Streamed Claude fit brief, replacing canned ANGLE map (~4–5h) — WOW MOMENT
- In `suggestFor` (`:1083`) / `.gc-fit` and expanded cards: **"Draft my pitch angle — Claude"** button →
  `stream:true` memo (parse SSE into the panel with a blinking caret, never spinner-then-dump).
- Payload: `cvText(≤4k)`, topics, careerStage, phdYear, citizenship, grant fields, and the deterministic
  `eligibility(g)` flags **as facts**. Prompt: cite specific CV evidence verbatim; **never contradict the
  deterministic verdict** ("guardrails decide, Claude explains"); ≤120 words = 2 sentences why-you-fit + one
  suggested aim + one honest watch-out. Label **"AI-generated — verify against the program page."**
- For federal grants, `await fetchFederalDetail` first so the prompt has the real synopsis. Cache per
  `grant-id + profile-hash`. Keep ANGLE map as offline fallback.
- **Acceptance:** memo streams, quotes real CV specifics, never contradicts eligibility chips; offline →
  canned ANGLE text.

### T8 — Claude eligibility second opinion on federal expand (~3h) — cut first if time collapses
- In `toggleExpand` federal branch (`:1252`) after `fetchFederalDetail` returns `applicantEligibilityDesc`:
  **"Ask Claude: can I apply?"** → schema `{verdict ∈ [eligible, gated_until_PR, ineligible, unclear],
  quotedClause, note}`, applicant facts ([redacted], [redacted] ~[redacted], PhD 2019) passed in. Render verdict
  + exact quoted sentence beside the regex chips, labeled "rule-based" vs "Claude read the synopsis".
- Also: stop hard-hiding regex-blocked grants in `eligFilter` (`:1021`) — render greyed with the reason chip
  (auditable, not vanished).
- **Acceptance:** federal card shows Claude verdict + quoted clause next to deterministic chips.

### T9 — Data-trust polish + visible Claude presence (~2–3h) — low risk, ship regardless
- Surface `g.confidence` as a chip in `cardHTML` (currently buried in the expanded table `:1071`).
- `deadlineChip` (`:530`): when parsed date is past AND text matches `/annual|recur|cycle/`, render
  **"Cycle closed — recurs annually · verify"**; when `parseDeadline` had to infer the year (`:522`
  rollover), use `unk` style ("recurs ~Mon"), not a fake countdown.
- Add "Snapshot 2026 — confirm on funder page" stamp linking `bestUrl(g)`. Add `deadlineISO` to the ~10
  on-stage grants. Relabel curated pill → **"Curated: hematology/oncology"** (honest scope).
- Visible Claude: `b-claude` badge class on any card whose reason/brief came from Claude; rename fit header
  to **"Claude's read on this grant"** (only once real output exists); footer line **"Matching:
  deterministic engine · Analysis: Claude"**; "offline mode — lexical matching" pill near `#resSub` whenever
  a Claude call falls back.

### T10 — build.py + rebuild + verify (~1h)
- `build.py`: add `FEDSEED` marker inlining `data/federal_seed.json`; **assert** output has no `sk-ant`.
- Rebuild `index.html`; load headlessly, confirm no console errors, lexical path + offline fallbacks work.
- Update `README.md` with the architecture story (single file + Worker, guardrails-vs-Claude, ~$0.2/session).

---

## Do NOT do (scope traps with ~2 days left)
- No embeddings/vector DB (Anthropic has no embeddings endpoint; lexical recall + Claude re-rank is the right
  two-stage design).
- No full-corpus LLM scoring (never re-rank all 268 or call per keystroke — one batched top-20 call).
- No chat interface (a bolted-on chatbot reads as generic; embedded per-grant memos are more original).
- No replacing `scoreGrant` or the regex eligibility engine — reframe them.
- No backend/DB/accounts/auth; keep single-file + one Worker.
- No LOI/cover-letter drafter in the core sprint (one memo per grant is the right, defensible scope).
- No dataset expansion / CSV / mobile / dark-mode edge cases.

## Cut order if the buffer burns down
Cut **T8** first, then **T7**. **Never** cut the hardening (T4), the CV parse (T5), or the re-rank (T6).
Freeze scope after core demos flawlessly; **warm all caches 30 min before presenting; record a backup
screen capture the night before.**

## 3-minute demo script
1. **0:00–0:20** Problem: postdocs burn weeks on grants they're ineligible for; search can't read a CV or an
   eligibility clause. "Built for my own job: AI + blood cancer at [redacted], [redacted] pending."
2. **0:20–0:50** Drop the real CV → staged "Claude is reading your CV…"; topics/focus/PhD-year 2019/stage
   self-fill. "The eligibility engine just configured itself from my CV." Contrast: v1 did substring matching
   against a hardcoded lexicon.
3. **0:50–1:30** Search: curated paints instantly, live Grants.gov loads, list visibly reshuffles under
   "Re-ranked by Claude" with reasons. Show the before/after toggle, then the kill shot — the source comment
   hand-excluding a prostate grant next to Claude demoting it live with a reason. "That comment was my
   confession. Claude is the fix."
4. **1:30–2:10** Expand a live federal opp: deterministic chips ("14 open to me, 9 citizenship-locked, 3
   unlock when my [redacted] arrives 2027" — auditable, never hallucinated). Click "Ask Claude: can I apply?"
   → verdict + the exact quoted clause, beside the rule-based chips.
5. **2:10–2:40** Shortlist a foundation grant → "Draft my pitch angle" streams a memo citing a real CV
   project against the funder's priorities + one honest gap, labeled AI-generated.
6. **2:40–3:00** Close on architecture: one static HTML file + a 50-line Worker; guardrails decide, Claude
   explains; graceful offline fallback; because Claude parses the CV, the blood-cancer lexicon is now just a
   fallback — **works for any researcher, any field**. Real 2026 deadlines, live federal data, ~15¢/session.
