# Grantboard — Pitch Script
**Built with Claude: Life Sciences · Development Track · ~3.5–4 minutes · 8 slides**

Deck: open `project_pitch/pitch_deck.html`. Navigate **← / →** (or click), **F** fullscreen, **S** toggles
these speaker notes on-screen (they mirror this file). Aim ~25–30s per slide.

> Structure follows the VC arc (YC / a16z / Sequoia): **hook → problem → why now → solution → proof →
> product → moat → vision/ask.** One idea per slide; lead with the outcome; land the close slowly.
> See `scorecard.md` for the iterative-improvement log (baseline 61 → 84).

---

## Slide 1 — Title  (~25s)
> "Hi — I'm building **Grantboard**, a grant-fit copilot for scientists. Here's the problem I lived: as a
> computational-oncology postdoc at [redacted], I spent **100+ hours** on proposals — and routinely chased grants I
> turned out to be **ineligible** for. So I built the tool I wished I had: it reads your **CV** and returns
> only the funding you can actually **win** — ranked, reasoned, and ready to apply. Built with Claude Code."

## Slide 2 — The problem  (~30s)
> "The stakes: **over $50 billion** in U.S. federal research grants every year — and a scientist has **no
> reliable way** to see which ones they can actually win. It's 100-plus hours per proposal, much of it on
> grants the applicant was never eligible for. Why? A search engine can't read your CV — or a **40-page
> eligibility clause**. And miss the fit and you don't just lose the grant — you lose **a year**."

## Slide 3 — Why now  (~30s)
> "Why now — because this was **impossible 18 months ago**. Two things changed. One: models like Claude can
> finally read the unstructured stuff — a two-column CV *and* a 40-page federal FOA in one pass — the exact
> problem that broke every prior grant tool. Two: the **data opened up** — Grants.gov and NIH RePORTER now
> expose APIs. That timing unlocks the whole idea: **deterministic rules** decide eligibility, **Claude** does
> the judgment."

## Slide 4 — How it works  (~35s)
> "One loop. **One:** drop your CV — Claude reads it into a structured profile and the dashboard configures
> itself. **Two:** matches render instantly — 268 verified programs plus live Grants.gov. **Three:** Claude
> re-ranks with a reason on every match. **Four:** the deterministic engine says what's actually
> **apply-able**. **Five:** it drafts your pitch angle, competitive landscape, and specific aims. And the
> engine paints local results instantly and streams federal in — **never a frozen screen**."

## Slide 5 — It works (proof)  (~30s)
> "And it works — my own CV, live. **73 matches** I'm actually eligible for, each with a cited reason. This
> card is the money shot: **88 / 100** Claude fit, and the callout tells me *why* it suits me — my NK/T-cell
> lymphoma work, my career stage — grounded in my real record. The eligibility engine did the gatekeeping:
> 73 open, 25 ruled out, each with a reason. Precomputed, so it's **instant** on stage; live it's ~15 cents."

## Slide 6 — Why it's a Built-with-Claude project  (~30s)
> "This is where it earns 'Built with Claude' — Claude as the **engine, not a chatbot**. It reads any CV into
> **JSON**. It **ranks with citations** — your CV against the grant — and never invents a grant, deadline, or
> amount. It **reads the fine print** — 'can I apply?' with the exact quoted clause. Plus a competitive
> landscape and a drafted aims skeleton. The trust line — the whole game for a funding tool: **Claude never
> authors a deadline, amount, or eligibility verdict.** Rules decide; Claude explains."

## Slide 7 — Why it's hard to copy (moat)  (~25s)
> "Why is this hard to copy? The moat is the **verified corpus** — 268 programs web-verified to 2026–27 plus
> 165 audited eligibility rulings; slow, unglamorous data a weekend clone won't build. Trust is
> **architectural, not a prompt** — a 'wrap an LLM' competitor hallucinates a deadline; ours structurally
> can't. And it **compounds with use**. The unfair advantage: I'm a scientist building the tool I need —
> founder-market fit you can't fake."

## Slide 8 — Vision & the ask  (~25s)
> "So the vision: **every scientist deserves a fundraising strategist** in their corner — for the price of a
> coffee, not a $500 consultant. Grantboard reads your record, surfaces only what you can **win**, and tells
> you **how**. It runs on real 2026 data, and because Claude parses any CV, it generalizes to every field.
> My ask: **try the live demo**, and I'm looking for **early users and a collaborator** to take it across all
> of science. Thank you."

---

## Optional live-demo beats (~60s if time allows)
1. **★ Load example** → the dashboard self-configures ("Claude read a CV and built a funding profile").
2. **Search** → results reshuffle under **Ranked by Claude**; open a top card's **"why this suits you."**
3. Expand a federal card → **"Ask Claude: can I apply?"** → verdict + the quoted clause beside the rule chips.
4. **Competitive landscape** on a shortlisted grant → real NIH PIs as suggested collaborators.

## Likely judge questions
- **Hallucinated grants/deadlines?** Claude only ranks/explains over retrieved objects by id; invented ids
  are dropped; deadlines/amounts/eligibility always render from source data.
- **Non-oncology?** Claude parses any CV; out-of-domain CVs relax the cancer filter and lean on live federal.
- **Eligibility trust?** A deterministic rules engine (citizenship, post-PhD window, MD-only, nationality) —
  auditable and separate from the LLM, which only explains it.
