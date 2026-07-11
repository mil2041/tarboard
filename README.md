# Grantboard — Career Development Grant Finder

A single-file web dashboard that matches a researcher's **CV + research topics** against **U.S. funding opportunities** in AI / computational oncology / blood cancer, and ranks them by fit. Built for a senior postdoc planning the transition to independence.

## Open it

Just open **`index.html`** in a browser (double-click, or `open index.html`). No build step or server needed to use it.

- If your browser restricts the live federal search over `file://`, serve locally instead:
  ```bash
  python3 -m http.server 8912 --directory .
  # then visit http://localhost:8912/index.html
  ```

## What it does

- **Upload a CV** (PDF or text) or paste it — keywords are extracted client-side. Click **★ Load example — Eric Liu ([redacted])** to try it with a real profile.
- **Add research topics** (blood-cancer subtypes, AI methods) as chips.
- **Search** returns opportunities ranked by a match score, each showing award size, deadline (with day-countdown), eligibility, career stage, U.S.-citizen flags, and *why* it matched.
- **Save** opportunities to a shortlist (persisted in your browser) and **export** to CSV/JSON.
- Light/dark themes.

## Data sources

| Source | Count | How |
|---|---|---|
| **Grants.gov** (NIH, NSF, DOD/CDMRP, ARPA-H) | live | Queried in real time from the official Search2 API |
| **Curated foundations/societies/industry** | 187 | `data/curated_opportunities.json` — see `FOUNDATIONS.md` |
| **JHU list (refreshed 2026)** | 81 | Seeded from the JHU `data/JHU_*.xlsx` files, then every program's deadline/amount/eligibility was **web-verified to 2026-2027** (`data/jhu_updated.json`); discontinued programs dropped |

**Eligibility & sorting:** the top bar takes **PhD year** and **citizenship** into account. Results default to **soonest-deadline** order (upcoming first; closed ones sink to the bottom), match your **career stage**, and — because you don't have a [redacted] yet — **hide awards requiring U.S. citizenship/PR** (counted separately; reveal with "Show citizenship-locked"). Awards past a hard post-PhD window (e.g. K99's 4-year limit) are flagged.

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
- `build.py` — inlines data into the template
- `FOUNDATIONS.md` — curated funder catalog (127 non-federal programs + federal appendix)
- `data/curated_opportunities.json`, `data/jhu_opportunities.json` — normalized data
- `user_profile/` — example CV

> ⚠️ Award amounts, deadlines, and eligibility change frequently. Always confirm on the funder's own page before applying.
