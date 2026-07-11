# Grantboard — Design Style **v0** ("Academic Broadsheet")

The original design language: an **editorial / academic-newspaper** identity — warm parchment paper,
a double-rule masthead, serif display type, and saturated jewel accents. This document is the reference
for that style **and a restore point**: `design_style/index.template.v0.html` is a verbatim snapshot of
the template at v0.

> **To revert to v0:** `cp design_style/index.template.v0.html index.template.html && python3 build.py`
> (git also holds it — the commit tagged in the log as the v0 snapshot).

---

## Identity
Editorial newspaper / academic broadsheet — high-contrast, textured, formal. Confident and characterful,
but visually "loud" (dotted paper texture, crimson accents, double rules, animated chips).

## Typography
| Role | Family | Notes |
|---|---|---|
| Display / brand / section headings / **card titles** | **Fraunces** (serif) | `--serif: 'Fraunces',Georgia,'Times New Roman',serif` |
| Body / UI | **IBM Plex Sans** | `--sans: 'IBM Plex Sans',system-ui,-apple-system,sans-serif` |
| Labels / meta / badges / scores | **IBM Plex Mono** | `--mono: 'IBM Plex Mono',ui-monospace,'SF Mono',Menlo,monospace` |

- Brand `h1` (`.brand h1`): Fraunces 600, 31px, with a crimson italic separator dot.
- Result card titles (`.gc-title`): **Fraunces 600, 19px** (decorative, editorial).
- Results header (`.results-top .h`): Fraunces 600, 24px.
- Kickers / meta keys: IBM Plex Mono, uppercase, wide letter-spacing (`.28em` kicker, `.12–.16em` labels).

## Color tokens — light (`:root`)
```css
--paper:#f4f0e7; --paper-2:#faf7f0; --card:#fffdf8;
--ink:#1b1a16; --ink-soft:#514d43; --ink-faint:#8a8477;
--line:#e2dccc; --line-strong:#cfc7b2;
--teal:#0f5f5c; --teal-bright:#12817b; --teal-wash:#e6efec;   /* primary action */
--crimson:#a4243b; --crimson-wash:#f6e7e6;                     /* accent + blockers */
--amber:#b26a1f; --amber-wash:#f6ecd9;                         /* gated / warn */
--green:#3f6f3a; --green-wash:#e8efdf;                         /* open / eligible */
```

## Color tokens — dark (`:root[data-theme="dark"]`)
```css
--paper:#101109; --paper-2:#14160e; --card:#191c13;
--ink:#ece7d7; --ink-soft:#b4ae9c; --ink-faint:#7f7a69;
--line:#2a2e20; --line-strong:#3a3f2d;
--teal:#4fd0c4; --teal-bright:#63e0d4; --teal-wash:#12241f;
--crimson:#e8637a; --crimson-wash:#2a1519; --amber:#d99a4b; --amber-wash:#2a2110;
--green:#8fc07a; --green-wash:#1a2413;
```

## Signature visual devices (what makes v0 "v0")
- **Dotted paper texture** on `body`:
  `background-image:radial-gradient(circle at 1px 1px, color-mix(in srgb,var(--ink) 5%,transparent) 1px, transparent 0); background-size:22px 22px;`
- **Double-rule masthead**: `.masthead{ border-bottom:3px double var(--ink); }` (broadsheet feel).
- **Warm parchment** paper (`#f4f0e7`) with cream cards (`#fffdf8`).
- **Crimson accents** used generously (brand dot, foundation badge, blocked chips, "from your CV" evidence chips).
- Elevation: `--shadow:0 1px 2px rgba(40,34,20,.05), 0 8px 26px -14px rgba(40,34,20,.22)`;
  `--shadow-lg:0 24px 60px -30px rgba(40,34,20,.42)`.

## Components
- **Cards** (`.gcard`): 14px radius, `1px solid var(--line)`, `var(--shadow)`; **hover lifts** `translateY(-2px)` to `--shadow-lg`; entrance `animation:rise .5s` with a per-card `animation-delay` stagger (≤600ms).
- **Card body order (v0):** title → funder line **(with eligibility chips + confidence chip inline)** → focus tags → Claude fit callout → award/deadline/stage → description → expand.
- **Badges** (`.badge`): mono, uppercase, per funder type — federal (teal wash), foundation (crimson wash), society (amber wash), industry (green wash).
- **Eligibility chips** (`.echip`): mono, uppercase; `gc`=amber, `blk`=crimson, `warn`=amber, `win`=green; sit **inline on the funder line**.
- **Score** (`.score .pct`): Fraunces 31px; meter bar `width:104px; height:5px` with a teal→teal-bright gradient fill.
- **Chips** (`.chip`): pill, `--paper-2` bg, teal on-state; suggestion chips dashed.
- **Trust strip / results bar / eligibility summary**: green/amber/crimson dots.

## Eligibility label wording (v0)
Direct/clinical: `U.S. citizens only`, `Needs citizen / PR`, `Requires faculty position`,
`past {N}-yr post-PhD window`, `For finishing PhD students`, `Not eligible — see details`.
(v1 softens several of these.)

## Feel
Confident, editorial, high-contrast. Downsides for an anxious grant-seeker: textured/busy background,
frequent crimson "alerts", dense card tops, and decorative serif titles that trade scannability for flair —
which is exactly what **v1** ("calm research workspace") sets out to quiet.
