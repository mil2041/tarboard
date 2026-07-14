#!/usr/bin/env python3
"""Precompute Claude fit reasoning for each EXAMPLE profile across the curated+JHU grant
pool, cached to data/claude_rerank_cache.json keyed by profile, then by the SAME grant id
the app computes. The app seeds this instantly when an example profile is loaded, so the
"Claude fit" callout appears with no runtime re-rank wait.

All example profiles are FICTIONAL — the cached reasoning is published inside index.html,
so it must never describe a real person (name, employer, nationality, immigration status).

Run the bridge first (python3 worker/claude_code_bridge.py), then:
    python3 worker/precompute_rerank.py            # all profiles
    PROFILE_KEY=jordan python3 worker/precompute_rerank.py   # just one
Saves progressively; safe to re-run.
"""
import json, re, os, sys, urllib.request

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BRIDGE = os.environ.get("BRIDGE_URL", "http://localhost:8788")
# Precompute offline with the strong model (quality over latency); the shipped
# data/claude_rerank_cache.json is opus-generated, and the "precomputed" chip in the
# app names this model. The live in-app re-rank uses the fast model for responsiveness.
MODEL  = os.environ.get("PRECOMPUTE_MODEL", "claude-opus-4-8")
BATCH  = 12

# Mirror the app's profileSummary() for each example profile (index.template.html EXAMPLES).
PROFILES = {
  "jordan": dict(n=264, text=(
    "Applicant: Jordan Bennett, PhD (he/him)\n"
    "Field: computational oncology / cancer genomics\n"
    "Topics: T-cell lymphoma, computational oncology, machine learning, cancer genomics, single-cell RNA-seq, "
    "immunotherapy, risk stratification, multi-omics integration\n"
    "Focus: blood cancer/hematology, AI/computational, genomics/omics, cancer immunology, oncology\n"
    "Expertise: single-cell rna-seq, atac-seq, tcr-seq, spatial metabolomics, multiplexed imaging, machine "
    "learning, multi-omics integration, survival modeling\n"
    "Career stage: senior postdoc (mentored, not faculty; no independent lab); PhD 2019, ~7 years out\n"
    "Institution: a private research university in Boston, MA (not NCI-designated)\n"
    "Citizenship: U.S. citizen — no immigration or work-authorization constraints of any kind")),
  "md": dict(n=32, text=(
    "Applicant: Sarah Mitchell, MD (she/her)\n"
    "Field: clinical/translational hematology-oncology\n"
    "Topics: lymphoma, CAR-T therapy, immunotherapy, clinical trials\n"
    "Focus: blood cancer/hematology, cancer immunology, clinical/translational, oncology\n"
    "Expertise: CAR-T cell therapy, immunotherapy resistance in DLBCL, investigator-initiated trials, "
    "correlative studies\n"
    "Career stage: physician-scientist, Instructor/Assistant Professor; MD 2016, fellowship completed 2022\n"
    "Citizenship: U.S. citizen")),
  "junior": dict(n=32, text=(
    "Applicant: Ryan Walker, PhD (he/him)\n"
    "Field: machine learning for cancer genomics\n"
    "Topics: acute myeloid leukemia (AML), machine learning, single-cell RNA-seq, deep learning\n"
    "Focus: blood cancer/hematology, AI/computational, genomics/omics, oncology\n"
    "Expertise: python, pytorch, deep learning, genomics, statistical modeling\n"
    "Career stage: 2nd-year postdoc; PhD in Computer Science 2024\n"
    "Citizenship: non-U.S. national on a work visa; U.S. permanent residence expected ~2028-06")),
}

# The generated cache is published inside index.html, so it must never describe the real author.
# Patterns come from .identity_denylist ([profile] scope), which is gitignored — this repo is
# public, so committing the names here would leak exactly what the guard exists to prevent.
def _banned():
    pats, cur = [], None
    if os.path.exists(".identity_denylist"):
        for line in open(".identity_denylist", encoding="utf-8"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("[") and line.endswith("]"):
                cur = line[1:-1]
            elif cur == "profile":
                pats.append(line)
    # Superseded example-profile names must not resurface either.
    pats += [r'\bMaria\b', r'\bChen\b', r'\bJun Park\b']
    return re.compile("|".join(pats), re.I) if pats else re.compile(r'(?!)')

BANNED = _banned()

def slug_id(prefix, g, i):
    # NAME-first, byte-for-byte identical to the app's slugId (index.template.html) and
    # build.py's _slug — so this script reproduces the exact ids used in the shipped cache.
    s = re.sub(r'[^a-z0-9]+', '-', ((g.get('name') or '') + '-' + (g.get('funder') or '')).lower()).strip('-')[:48]
    return prefix + '-' + (s or str(i))

def load_pool():
    cur = json.load(open("data/curated_opportunities.json"))
    jhu = json.load(open("data/jhu_updated.json"))
    pool = []
    for i, g in enumerate(cur): pool.append({**g, 'source': g.get('source') or 'curated', 'id': g.get('id') or slug_id('cur', g, i)})
    for i, g in enumerate(jhu): pool.append({**g, 'source': 'jhu', 'id': g.get('id') or slug_id('jhu', g, i)})
    # dedupe by name+funder, prefer the JHU copy (mirrors the app's dedupePool)
    seen = {}
    for g in pool:
        k = re.sub(r'[^a-z0-9|]', '', ((g.get('name') or '') + '|' + (g.get('funder') or '')).lower())
        prev = seen.get(k)
        if not prev or (g.get('source') == 'jhu' and prev.get('source') != 'jhu'):
            seen[k] = g
    return list(seen.values())

def relevance(g):
    hay = ((g.get('name') or '') + ' ' + (g.get('funder') or '') + ' ' + (g.get('description') or '') + ' '
           + ' '.join(g.get('focusAreas') or []) + ' ' + (g.get('relevanceToUser') or '')).lower()
    terms = ['leukemia', 'lymphoma', 'myeloma', 'hematolog', 'blood cancer', 'mds', 'marrow', 't-cell',
             'single-cell', 'single cell', 'genomic', 'computational', 'machine learning',
             'artificial intelligence', 'immunother', 'oncolog', 'cancer', 'data science']
    s = sum(1 for t in terms if t in hay)
    for f in (g.get('focusAreas') or []):
        if f in ['blood cancer/hematology', 'AI/computational', 'genomics/omics', 'cancer immunology', 'oncology']:
            s += 1
    return s

SCHEMA = {"type": "object", "additionalProperties": False, "required": ["rankings"], "properties": {"rankings": {
    "type": "array", "items": {"type": "object", "additionalProperties": False, "required": ["id", "fitScore", "why"],
    "properties": {"id": {"type": "string"}, "fitScore": {"type": "integer"}, "why": {"type": "string"}}}}}}
SYSTEM = ("You are a grants-matching expert briefing a scientist on how each funding opportunity fits them. "
    "You may ONLY reference the grant objects provided, by their exact id. Never invent grants, deadlines, "
    "amounts, or eligibility. Judge scientific topic/method alignment and career-stage fit; a grant dedicated "
    "to a disease the applicant does not study is a poor fit even if the method (AI, genomics) matches. Write "
    "each 'why' as TWO OR THREE complete, natural sentences in a warm, advisory tone that connect the applicant's "
    "specific research and career stage to what the funder supports. Refer to the applicant by the first name "
    "given in the Applicant block. Rely ONLY on the applicant facts given — do not invent an employer, a "
    "nationality, or an immigration status, and never name a specific university as the applicant's own. "
    "Return via emit.")

def batch_call(grants, profile_text):
    payload = [{"id": g['id'], "name": g.get('name'), "funder": g.get('funder'),
                "focusAreas": ", ".join(g.get('focusAreas') or []), "amount": g.get('awardAmount') or "",
                "deadline": g.get('deadlineInfo') or g.get('closeDate') or "",
                "desc": (g.get('description') or g.get('relevanceToUser') or "")[:160]} for g in grants]
    body = {"model": MODEL, "max_tokens": 4000, "system": SYSTEM,
            "messages": [{"role": "user", "content": profile_text + "\n\nGrants (JSON array):\n"
                          + json.dumps(payload) + "\n\nFor EACH id above return a fitScore 0-100 and a why of "
                          "TWO OR THREE natural, complete sentences explaining specifically why it does (or "
                          "doesn't) fit this applicant."}],
            "tools": [{"name": "emit", "input_schema": SCHEMA}], "tool_choice": {"type": "tool", "name": "emit"}}
    req = urllib.request.Request(BRIDGE, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        d = json.load(r)
    tu = next(b for b in d['content'] if b.get('type') == 'tool_use')
    return tu['input']['rankings']

def main():
    pool = load_pool()
    pool.sort(key=relevance, reverse=True)

    cache = {}
    if os.path.exists("data/claude_rerank_cache.json"):
        try: cache = json.load(open("data/claude_rerank_cache.json"))
        except Exception: cache = {}

    only = os.environ.get("PROFILE_KEY")
    keys = [only] if only else list(PROFILES)
    for key in keys:
        spec = PROFILES[key]
        target = pool[:spec["n"]]
        ids = {g['id'] for g in target}
        pc = cache.setdefault(key, {})
        todo = [g for g in target if g['id'] not in pc]
        print(f"\n=== profile {key}: target={len(target)} cached={len(pc)} todo={len(todo)}", flush=True)
        for i in range(0, len(todo), BATCH):
            batch = todo[i:i + BATCH]
            for attempt in (1, 2, 3):
                try:
                    for r in batch_call(batch, spec["text"]):
                        if r['id'] in ids:
                            why = str(r['why'])[:500]
                            bad = BANNED.search(why)
                            if bad:
                                raise ValueError(f"identity leak in generated text: {bad.group(0)!r}")
                            pc[r['id']] = {"fitScore": max(0, min(100, int(r['fitScore']))), "why": why}
                    print(f"  {key} batch {i//BATCH+1}/{(len(todo)+BATCH-1)//BATCH}: cached {len(pc)}", flush=True)
                    break
                except Exception as e:
                    print(f"  {key} batch {i//BATCH+1} attempt {attempt} failed: {str(e)[:160]}", flush=True)
            json.dump(cache, open("data/claude_rerank_cache.json", "w"), ensure_ascii=False, indent=0)

    leaks = {k: sum(1 for v in pc.values() if BANNED.search(v.get("why", ""))) for k, pc in cache.items()}
    print(f"\nDONE. {({k: len(v) for k, v in cache.items()})} -> data/claude_rerank_cache.json")
    print(f"identity leaks per profile: {leaks}")
    if any(leaks.values()):
        sys.exit("FAILED: generated cache still contains real-identity tokens.")

main()
