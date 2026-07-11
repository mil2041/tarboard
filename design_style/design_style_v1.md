# Grantboard — Design Style **v1** ("Calm Research Workspace")

Direction: **editorial newspaper → calm research workspace.** Grant-seekers are already anxious; the UI
should feel quiet, clinical, and trustworthy — "here is what's worth your time, here is what isn't, and
nothing is hidden." References: NIH/research-admin calm, Notion readability, Linear restraint, soft
biomedical palette.

Kept from v0: serif brand/logo character, **teal** as the primary action color, clear eligibility chips,
card-based results. Applied on top of all v0 features (nothing functional removed).

> **Revert to v0:** `cp design_style/index.template.v0.html index.template.html && python3 build.py`
> (see `design_style_v0.md`). v1 is additive/stylistic; the v0 snapshot restores the old look exactly.

---

## ⚑ Shipped palette (v1.1): v1 layout + **v0 warm color theme**
Per preference, the shipped build keeps this doc's **layout/structure** (flat background, single-rule
masthead, sans titles, calmer cards, chips on their own line, softened wording) but uses the **v0 warm
"broadsheet" palette** — parchment paper, cream cards, saturated teal/crimson/amber/green (see the exact
values in `design_style_v0.md`). Only the shadows were kept soft (v1) but re-warmed to sit on parchment:
```css
/* light :root, as shipped */
--paper:#f4f0e7; --paper-2:#faf7f0; --card:#fffdf8; --ink:#1b1a16; --ink-soft:#514d43;
--ink-faint:#8a8477; --line:#e2dccc; --line-strong:#cfc7b2;
--teal:#0f5f5c; --teal-bright:#12817b; --teal-wash:#e6efec;
--crimson:#a4243b; --crimson-wash:#f6e7e6; --amber:#b26a1f; --amber-wash:#f6ecd9;
--green:#3f6f3a; --green-wash:#e8efdf;
--shadow:0 1px 2px rgba(40,34,20,.04), 0 4px 14px -10px rgba(40,34,20,.15);   /* v1 softness, warm tint */
--shadow-lg:0 16px 40px -26px rgba(40,34,20,.30);
```

## Original v1 cool palette (NOT shipped — kept for reference)
```css
--paper:#f7f8f5; --paper-2:#fbfcfa; --card:#ffffff; --ink:#20231f; --ink-soft:#5c6258;
--ink-faint:#8a9185; --line:#e1e6dc; --line-strong:#cbd4c5;
--teal:#2f766d; --teal-bright:#348b80; --teal-wash:#edf6f3;
--crimson:#a44a5b; --crimson-wash:#f8ecef; --amber:#9a6a2f; --amber-wash:#f7f0e3;
--green:#557a4b; --green-wash:#eef5ea;
```
Dark theme (`:root[data-theme="dark"]`) is unchanged from v0.

## Changes from v0
| Area | v0 | v1 |
|---|---|---|
| Background | dotted radial-gradient paper texture | **flat** (texture removed) |
| Paper / cards | warm parchment `#f4f0e7` / cream `#fffdf8` | near-white `#f7f8f5` / white `#ffffff` |
| Masthead rule | `3px double var(--ink)` (broadsheet) | `1px solid var(--line)` (quiet) |
| Card titles | Fraunces serif 19px (decorative) | **IBM Plex Sans** 17.5px (scannable) |
| Card hover | lift `translateY(-2px)` + `--shadow-lg` | no lift, shadow stays `--shadow` |
| Card radius / padding / gap | 14px / 16×18 / 14px | 12px / 18×20 / 16px (more breathing room) |
| Score | Fraunces 31px + 104×5 gradient meter | 26px + 84×4 flat teal meter (opacity .85) |
| Eligibility chips | inline on the funder line (crowded top) | **own line** below Award/Deadline (`.gc-elig`) |
| Palette mood | saturated jewel tones | desaturated, lower-contrast |

## Softer, less-alarming eligibility wording (and less crimson)
| v0 | v1 | Color |
|---|---|---|
| `U.S. citizens only` | `Needs U.S. citizenship` | crimson (hard) |
| `Needs citizen / PR` | `Needs PR / citizenship` | crimson (hard) |
| `Permanent residence unlocks ~…` | `Future target · unlocks with PR ~…` | amber |
| `past {N}-yr post-PhD window` | `Verify timing · past {N} window` | amber |
| `Requires faculty position` (crimson) | `Future target · faculty stage` | **amber** (was crimson) |
| `Not eligible — see details` | `Not currently eligible` | crimson (hard) |

Crimson is now reserved for true hard ineligibility (citizenship, physician-only, nationality); "future
target" and "verify" states moved to amber. The muted v1 crimson also lowers overall alert-stress.

## Typography (v1)
- **Fraunces** — brand logo + major section headings (`.results-top .h`, eligibility summary). Not card titles.
- **IBM Plex Sans** — body, UI, and now **result card titles** (clarity over flair).
- **IBM Plex Mono** — labels, meta, badges, scores.

## Result card order (v1)
Title → Funder + source (+ confidence) → **Fit reason (Claude callout)** → Award / Deadline / Stage →
**Eligibility status (own line)** → Description → Actions.

## Not changed (deliberately)
Teal as primary action, the Claude fit callout treatment, trust strip content, badges' per-funder washes,
the eligibility engine's logic (only the wording/colour of its chips changed), and all functionality.
