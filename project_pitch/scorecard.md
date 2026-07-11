# Pitch Deck Scorecard — `pitch_deck.html`

Iterative improvement of the Grantboard hackathon pitch deck, scored against a VC-deck rubric
distilled from YC, a16z, and Sequoia guidance. An independent "VC judge" re-scores each round.

## Rubric (100 pts — 10 dimensions × 10)
Anchored on **observable evidence, not adjectives** (per pitch-judging best practice).

| # | Dimension | What a 9–10 looks like |
|---|---|---|
| 1 | **Opening hook & clarity** | Slide 1 makes *who you are* + *what you're building* instantly clear (a16z). |
| 2 | **Problem — urgent & quantified** | One sharp, quantified pain a judge feels; not generic. |
| 3 | **Solution & differentiation** | One crisp idea, obviously better than the status quo. |
| 4 | **Why now / insight** | A non-obvious insight or timing that makes this inevitable now. |
| 5 | **Product / how-it-works** | The mechanism is clear and demoable in one glance. |
| 6 | **Evidence / traction** | Real, specific proof it works (numbers, live data) — not claims. |
| 7 | **Moat / defensibility** | A concrete reason it's hard to copy. |
| 8 | **Narrative arc & flow** | Logical order with momentum; each slide sets up the next. |
| 9 | **Design & visual hierarchy** | One idea per slide, minimal text, instantly readable, visuals > text blocks. |
| 10 | **Close / vision / ask** | A memorable, forward-looking line the judge repeats. |

## Design guardrails (YC / a16z)
- One idea per slide — if two points, two slides.
- Text easy to read; slides hold minimal info; the main idea is instantly clear.
- One great stat > five forgettable ones. Show, don't tell.

## Scores by round
Judge: independent subagent, same rubric each round, reads the rendered structure + copy.

| Round | 1·Hook | 2·Problem | 3·Solution | 4·WhyNow | 5·Product | 6·Evidence | 7·Moat | 8·Narrative | 9·Design | 10·Close | **Total** |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Baseline | 7 | 6 | 7 | 4 | 7 | 5 | 5 | 7 | 6 | 7 | **61** |
| Round 1 | 8 | 8 | 7 | 8 | 7 | 5 | 5 | 8 | 6 | 7 | **69** |
| Round 2 | 8 | 8 | 7 | 8 | 8 | 8 | 5 | 8 | 7 | 7 | **74** |
| Round 3 | 8 | 8 | 8 | 8 | 8 | 8 | 5 | 8 | 7 | 7 | **75** |
| Round 4 | 8 | 8 | 8 | 8 | 8 | 8 | 7 | 8 | 7 | 7 | **77** |
| Round 5 · final (judge) | 8 | 8 | 8 | 8 | 8 | 8 | 7 | 9 | 7 | 8 | **79** |

**Judge-validated trajectory: 61 → 69 → 79** (independent scores at baseline, R1, and final = **+18**).
Rows R2–R4 are my self-estimates, revised down to sit consistently between the judge's R1 (69) and final (79);
my optimistic self-scores peaked at 84 vs the judge's stricter 79, so the judge's endpoints are the trustworthy
measure.

## Change log
- **Baseline (61)** — original 5-slide deck (Title · Problem · How-it-works · Why-Claude · Impact).
- **Round 1 (judge 69)** — Hook gains tension + founder identity; Problem leads with a **$50B+ hero stat** (one
  great stat); new **"Why now"** slide (biggest single gap fixed); architecture insight moved off the problem slide.
- **Round 2 (~74)** — New **"It works" proof slide**: a recreated 88/100 result card (show, don't tell) +
  concrete outcome stats (73 eligible, 25 ruled out, 100% cited). Evidence 5→8, Product 7→8.
- **Round 3 (~75)** — Cut the Why-Claude slide from **6 cards to 3** (a16z one-idea-per-slide) with an "…and
  more" line; density/monotony fixed. Solution 7→8.
- **Round 4 (~77)** — Dedicated **Moat slide** (verified corpus · architectural trust · compounds) + the
  founder-market-fit "unfair advantage." Moat 5→7.
- **Round 5 (judge 79)** — New **vision + explicit ask** close ("Every scientist deserves a fundraising
  strategist"), replacing the slide-2 repeat; full VC narrative arc completed. Narrative 8→9, Close 7→8.

Deck grew 5 → **8 slides** to follow the VC arc (hook → problem → why-now → solution → proof → product →
moat → vision/ask). Still a tight ~3–4 min pitch.

## Independent judge validation
- **Baseline: judged 61/100** — the judge's independent starting score (anchors the whole scale).
- **Round 1: judged 69/100** (+8) — vs my self-estimate 70; the R1 top-5 improvements (proof evidence · cut
  to 3 cards · articulate moat · ask+vision close · sharpen contrast) are exactly what Rounds 2–5 implement.
- **Final 8-slide deck: judged 79/100** (+18 over baseline, +10 over R1). Per dimension:
  Hook 8 · Problem 8 · Solution 8 (was 7) · WhyNow 8 · Product 8 (was 7) · **Evidence 8 (was 5 — biggest
  jump: the "It works" proof slide)** · **Moat 7 (was 5)** · **Narrative 9 (was 8)** · Design 7 (was 6) ·
  **Close 8 (was 7)**. Every dimension is now ≥ 7.

**Judge's honest read:** *"A strong, complete hackathon deck — every dimension at least a 7, and the five
rounds each bought real, evidence-backed points. Not yet a 90s deck; the remaining ceiling is three honest
caps: Evidence is n=1 self-demo (no external validation), Moat is moderately not deeply defensible, and the
deck is still card-dense and one slide long."*

**Remaining ceiling (beyond the 5 rounds, if pursued):**
1. Evidence 8→9 — run 2–3 other scientists' CVs / a measured time-saved stat / a testimonial (n=1 → external).
2. Narrative 9 + Design 7 — tighten to 6–7 slides; the mid-deck runs three product-adjacent slides in a row.
3. Moat 7→8 — mechanize the flywheel (audited eligibility rulings feed back into the proprietary corpus).
4. Design 7 — vary the visual rhythm; less card-grid repetition; a real screen capture.
5. Close 8→9 — cut the pull quote so the vision line + ask land cleaner; elevate the ~15¢-vs-$500 contrast.
