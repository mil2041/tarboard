# Grantboard — Pitch Script
**Built with Claude: Life Sciences · Development Track · ~3 minutes**

Deck: open `project_pitch/pitch_deck.html` in a browser. Navigate with **← / →** (or click), **F** for
fullscreen, **S** to toggle these speaker notes on-screen. Aim ~30–40s per slide.

> Delivery tip: lead every slide with the outcome, not the mechanism. Land the closing line slowly.

---

## Slide 1 — Title  (~30s)
**On screen:** Grantboard · "A grant-fit copilot for scientists."

> "Hi — I'm building **Grantboard**, a grant-fit copilot for scientists.
> Here's the problem I lived: as a computational-oncology postdoc at [redacted], I burned **weeks** hunting for
> funding — and half the awards I found, it turned out I wasn't even eligible for.
> So I built the tool I wished I had. You upload your **CV** and your **research aim**, and you get a
> **ranked, evidence-backed grant shortlist** — with eligibility checks, competitiveness signals, and an
> application plan. And it's **built with Claude Code**."

---

## Slide 2 — The problem & the thesis  (~35s)
**On screen:** three failure points → the thesis pull-quote → "rules + Claude" insight.

> "Scientists lose weeks to this, and it's high-stakes — miss a deadline or misjudge eligibility and you
> wait a **whole year**.
> The core issue: a search engine can't read your CV, and it definitely can't read a dense federal
> **eligibility clause**. Most grant tools stop at 'here's a list.'
> Our thesis is different: **don't just find grants — tell a scientist whether they're competitive, why,
> and what to fix.**
> And the way we do that *safely* is the insight at the bottom: **deterministic rules decide eligibility**
> — auditable, impossible to hallucinate — while **Claude provides the judgment** on top."

---

## Slide 3 — How it works: one loop  (~40s)
**On screen:** 5-step flow (Claude marked on 1, 3, 5) + two-stage engine.

> "Here's the whole product in one loop.
> **One:** you drop your CV, and Claude reads it into a structured profile — research areas, methods,
> career stage — and the entire dashboard, including the eligibility engine, **configures itself**.
> **Two:** matches render **instantly** — 268 verified foundation and society programs plus **live
> Grants.gov** federal results.
> **Three:** Claude **re-ranks** the top matches and writes two or three sentences on **why each one fits
> you**.
> **Four:** the deterministic engine tells you what's actually **apply-able** — open now, a future target,
> or needs citizenship.
> **Five:** for any grant, Claude drafts a **pitch angle**, shows the **competitive landscape** from real
> NIH-funded projects, and sketches your **specific aims**.
> The architecture is a reliability win too: local results paint instantly, federal streams in, then Claude
> re-ranks — **never a frozen screen**."

---

## Slide 4 — Why it's a Built-with-Claude project  (~40s)
**On screen:** six Claude-powered features + the trust strip.

> "This is where it earns 'Built with Claude.' We use Claude for **structured reasoning, not a chatbot**.
> It turns a CV into strict **JSON**. It **re-ranks** grants and cites your actual work against the grant's
> actual text. It **reads messy federal eligibility prose** and quotes the clause it relied on. It pulls the
> **competitive landscape** from real NIH-funded awards — and the collaborators it suggests are **real
> principal investigators** from those awards, never invented.
> Now the trust line — the whole game for a funding tool: **Claude never authors a deadline, an amount, or
> an eligibility verdict.** Those always come from source data. Rules decide eligibility; Claude explains.
> And on the plumbing: it's a single static HTML file plus a **fifty-line Cloudflare Worker** — or it runs
> entirely on your **Claude subscription through Claude Code**."

---

## Slide 5 — Impact & close  (~35s)
**On screen:** stats row → closing pull-quote → chips.

> "To land it: this runs on **real 2026 data** — live Grants.gov, 268 curated programs web-verified to
> 2026–27, and real NIH RePORTER awards. Because Claude parses **any** CV, it generalizes beyond my niche —
> a neuroscientist or a plant biologist gets real matches too.
> The impact is simple: it turns weeks of anxious searching into **minutes**, and it gives scientists
> **eligibility they can trust**.
> So the one line I'd leave you with: **Grantboard doesn't just find grants — it tells you whether you can
> win, why, and what to fix.**
> Thank you — happy to demo it live."

---

## Optional live-demo beats (if you have an extra ~60s after slide 5)
1. Click **★ Load example** → the dashboard self-configures; "Claude read a CV and built a funding profile."
2. **Search** → results reshuffle under **Ranked by Claude**; open a top card's **"why this suits you."**
3. Expand a federal card → **"Ask Claude: can I apply?"** → verdict + the quoted clause beside the rule-based chips.
4. **Competitive landscape** on a shortlisted grant → real NIH PIs as suggested collaborators.

## Fielding likely judge questions
- **"How do you stop hallucinated grants/deadlines?"** Claude only ranks/explains over retrieved objects by
  id; any invented id is dropped client-side; deadlines/amounts/eligibility always render from source data.
- **"Does it work for non-oncology?"** Yes — Claude parses any CV; out-of-domain CVs relax the cancer filter
  and lean on live federal + general-biomedical results.
- **"Is the eligibility trustworthy?"** It's a deterministic rules engine (citizenship, post-PhD window,
  MD-only, nationality) — auditable and separate from the LLM, which only explains it.
