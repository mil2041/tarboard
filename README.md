# TARBoard — Targeted Award Radar for Biomedical Oncology Research
A single-file web dashboard that matches a researcher's **CV + research topics** against **U.S. funding opportunities** in AI / computational oncology / blood cancer, and ranks them by fit. Built for a senior postdoc planning the transition to independence.

**Two-stage engine:** deterministic rules decide **eligibility** (citizenship / PR, post-PhD window, MD-only, nationality — auditable and never hallucinated), and **Claude** provides the judgment on top — it reads your CV into a structured profile, re-ranks the matches with a reason for each, reads federal eligibility prose, and drafts a CV-grounded pitch angle for any grant. Every Claude output is grounded strictly on the retrieved data (it never invents a grant, deadline, or amount), and the whole app **degrades gracefully to lexical matching when Claude isn't connected**. Built with Claude Code.

## Open it

Just open **`index.html`** in a browser (double-click, or `open index.html`). No build step or server needed to use it.

- If your browser restricts the live federal search over `file://`, serve locally instead:
  ```bash
  python3 -m http.server 8912 --directory .
  # then visit http://localhost:8912/index.html
  ```

## What it does

- **Upload a CV** (PDF or text) or paste it — keywords are extracted client-side. Click **★ Load example — Jordan Bennett** to try it with an example profile.
- **Add research topics** (blood-cancer subtypes, AI methods) as chips.
- **Search** returns opportunities ranked by a match score, each showing award size, deadline (with day-countdown), eligibility, career stage, U.S.-citizen flags, and *why* it matched.
- **Save** opportunities to a shortlist (persisted in your browser) and **export** to CSV/JSON.
- Light/dark themes.

## Connecting Claude

The dashboard is a static file, so it can't hold an API key. Two ways to give it one:

1. **Cloudflare Worker proxy (recommended).** Deploy the ~90-line proxy in `worker/` (holds the key as a
   secret; model allowlist + CORS + optional per-IP cap). See `worker/README.md` — it's a 2-minute
   `wrangler deploy`. Then click the **⚙** button in the app and paste the Worker URL.
2. **Paste-your-own-key dev mode.** For local rehearsal only: ⚙ → paste an Anthropic key (stays in your
   browser, calls the API directly). Never ship a page with a key baked in — `build.py` refuses to build if
   one is present.
3. **Claude Code bridge (no key, uses your Claude subscription).** For a local demo, run
   `python3 worker/claude_code_bridge.py` and point ⚙ at `http://localhost:8788`; it runs the app's Claude
   calls through the `claude -p` CLI on your existing login. See `worker/README.md`. Local-only and slower
   than the API, but zero setup — good for developing/demoing on a laptop.

Without either, the app still runs fully on the deterministic/lexical path. Models are pinned in one
`CONFIG` object (`claude-opus-4-8` workhorse, `claude-haiku-4-5` fast path); ~$0.15–0.25 per session.

## Data sources

| Source | Count | How |
|---|---|---|
| **Grants.gov** (NIH, NSF, DOD/CDMRP, ARPA-H) | live | Queried in real time from the official Search2 API |
| **Curated foundations/societies/industry** | 187 | `data/curated_opportunities.json` — see `FOUNDATIONS.md` |
| **JHU list (refreshed 2026)** | 81 | Seeded from the JHU `data/JHU_*.xlsx` files, then every program's deadline/amount/eligibility was **web-verified to 2026-2027** (`data/jhu_updated.json`); discontinued programs dropped |

**Eligibility & sorting:** the top bar takes **PhD year** and **citizenship** into account. Results default to **soonest-deadline** order (upcoming first; closed ones sink to the bottom), match your **career stage**, and — for profiles without U.S. citizenship/permanent residence — **hide awards that require it** (counted separately; reveal with "Show citizenship-locked"). Awards past a hard post-PhD window (e.g. K99's 4-year limit) are flagged.

`FOUNDATIONS.md` is the human-readable catalog of the curated non-federal funders (computational / blood cancer / rare disease), grouped by theme with senior-postdoc guidance. It and the dashboard's "Curated foundations" source are the same dataset.

## Rebuilding after data changes

The dataset JSON is inlined into `index.html` at build time from `index.template.html`:

```bash
python3 build.py     # regenerates index.html from the template + data/*.json + user_profile CV
```

Edit `index.template.html` for app/UI changes and `data/*.json` for data changes, then re-run `build.py`.

## Files

- `index.html` — the built, self-contained app (open this)
- `index.template.html` — source template with data placeholders
- `build.py` — inlines data into the template (and asserts no API key is baked in)
- `worker/` — Cloudflare Worker Claude proxy + deploy guide
- `IMPLEMENTATION_PLAN.md` — the Claude-integration build plan / spec
- `FOUNDATIONS.md` — curated funder catalog (127 non-federal programs + federal appendix)
- `data/curated_opportunities.json`, `data/jhu_updated.json` — normalized data
- `data/federal_seed.json` — real Grants.gov snapshot used as an offline fallback
- `user_profile/` — example CV

> ⚠️ Award amounts, deadlines, and eligibility change frequently. Always confirm on the funder's own page before applying.
