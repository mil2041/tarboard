# Grantboard — Pitch Script
**Built with Claude: Life Sciences · Development Track · ~3 minutes · 6 slides**

Deck: open `project_pitch/pitch_deck.html`. Navigate **← / →** (or click), **F** fullscreen, **S** toggles
these speaker notes on-screen (they mirror this file). Aim ~30s per slide.

> Condensed from 8 → 6 slides: Why-now folded into a compact bridge on the Problem slide; Why-Claude folded
> into How-it-works (the loop already shows Claude's steps; its trust strip moved there). Lead with the
> outcome; land the close slowly. See `scorecard.md` for the iterative-improvement log.

---

## Slide 1 — Title  (~25s)
> "Hi — I'm building **Grantboard**, a grant-fit copilot for scientists. As a computational-oncology postdoc
> at [redacted], I spent **100+ hours** on proposals — and routinely chased grants I turned out to be **ineligible**
> for. So I built the tool I wished I had: it reads your **CV** and returns only the funding you can actually
> **win** — ranked, reasoned, ready to apply. Built with Claude Code."

## Slide 2 — The problem: fragmentation  (~35s)
**On screen:** the shattered-bar figure (Federal = one block; Beyond-federal = 111 shards).
> "The money is there — it's just **scattered**. There's $50B+ a year in U.S. research funding, but most of
> what a scientist can actually apply to **isn't federal**. Federal is the easy part — one Grants.gov portal.
> Everything else is **194 programs across 111 separate funders**, each its own site, deadline, and
> eligibility. One portal covers the government; **nothing covers the rest.** And *why now?* — Claude can
> finally read this fragmented fine print, a CV *and* 100+ funders' rules, and the APIs just opened.
> Impossible 18 months ago."

## Slide 3 — How it works: Claude is the engine  (~35s)
**On screen:** the 5-step loop + two-stage engine + trust strip.
> "One loop, and Claude is the **engine, not a chatbot**. **One:** drop your CV — Claude reads it into a
> structured profile and the dashboard configures itself. **Two:** it **unifies the scattered** — 268
> verified programs across 111 funders plus live Grants.gov, one ranked list. **Three:** Claude re-ranks with
> a reason on every match. **Four:** deterministic rules say what's actually **apply-able**. **Five:** it
> drafts your pitch angle, competitive landscape, and aims. And the trust line — the whole game for a funding
> tool: **Claude never authors a deadline, amount, or eligibility verdict.** Rules decide; Claude explains."

## Slide 4 — It works (proof)  (~30s)
**On screen:** recreated 88/100 result card + eligibility bar.
> "And it works — my own CV, live. **73 matches** I'm actually eligible for, each with a cited reason. This
> card is the money shot: **88/100** Claude fit, and it tells me *why* it suits me — my NK/T-cell lymphoma
> work, my stage — grounded in my real record. The eligibility engine did the gatekeeping: 73 open, 25 ruled
> out, each with a reason. Precomputed, so it's instant on stage; live it's ~15 cents. And because Claude
> parses any CV, the same engine generalizes to any field."

## Slide 5 — Why it's hard to copy (moat)  (~25s)
**On screen:** 3 pillars + flywheel figure.
> "Why is this hard to copy? The moat is the **verified corpus** — 268 programs web-verified to 2026–27 plus
> 165 audited eligibility rulings; slow data a weekend clone won't build. Trust is **architectural, not a
> prompt** — a 'wrap an LLM' competitor hallucinates a deadline; ours structurally can't. And it **compounds**:
> every ruling a user audits feeds the corpus, so the dataset grows with each user. The unfair advantage —
> I'm a scientist building the tool I need."

## Slide 6 — Vision & the ask  (~25s)
**On screen:** cost figure (~15¢ vs $300–500/hr) + the ask.
> "So the vision: **every scientist deserves a fundraising strategist** — for the price of a coffee, not a
> $500 consultant. Grantboard reads your record, surfaces only what you can **win**, and tells you **how**.
> My ask: **try the live demo**, and I'm looking for **early users and a collaborator** to take it across
> every field of science. Thank you."

---

## Optional live-demo beats (~60s if time allows)
1. **★ Load example** → the dashboard self-configures ("Claude read a CV and built a funding profile").
2. **Search** → results reshuffle under **Ranked by Claude**; open a top card's **"why this suits you."**
3. Expand a federal card → **"Ask Claude: can I apply?"** → verdict + the quoted clause beside the rule chips.
4. **Competitive landscape** on a shortlisted grant → real NIH PIs as suggested collaborators.

## Likely judge questions
- **Hallucinated grants/deadlines?** Claude only ranks/explains over retrieved objects by id; invented ids
  are dropped; deadlines/amounts/eligibility always render from source data.
- **Non-oncology?** Claude parses any CV; the corpus is hem–onc today and expanding to other fields.
- **Eligibility trust?** A deterministic rules engine (citizenship, post-PhD window, MD-only, nationality) —
  auditable and separate from the LLM, which only explains it.
- **Traction?** Honest: n=1 (my own CV) today; the immediate ask is early users to reach n>1.
