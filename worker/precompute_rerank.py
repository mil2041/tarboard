#!/usr/bin/env python3
"""Precompute Claude fit reasoning for the demo (Eric Liu) profile across the curated+JHU
grant pool, and cache it to data/claude_rerank_cache.json keyed by the SAME grant id the
app computes. The app seeds this instantly when the example profile is loaded, so the
"Claude fit" callout appears with no runtime re-rank wait.

Run the bridge first (python3 worker/claude_code_bridge.py), then:
    python3 worker/precompute_rerank.py
Saves progressively; safe to re-run.
"""
import json, re, os, urllib.request

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BRIDGE = os.environ.get("BRIDGE_URL", "http://localhost:8788")
MODEL  = os.environ.get("PRECOMPUTE_MODEL", "claude-haiku-4-5")
TARGET = int(os.environ.get("PRECOMPUTE_N", "130"))   # >= 100
BATCH  = 12

# Mirror the app's profileSummary() for the demo profile.
PROFILE = ("Field: computational oncology / cancer genomics\n"
  "Topics: T-cell lymphoma, computational oncology, machine learning, cancer genomics, single-cell RNA-seq, "
  "immunotherapy, risk stratification, multi-omics integration\n"
  "Focus: blood cancer/hematology, AI/computational, genomics/omics, cancer immunology, oncology\n"
  "Expertise: single-cell rna-seq, atac-seq, tcr-seq, spatial metabolomics, multiplexed imaging, machine "
  "learning, multi-omics integration, survival modeling\n"
  "Career stage: postdoc; PhD 2019\n"
  "Citizenship: pending (permanent residence ~[redacted])")

def slug_id(prefix, g, i):
    s = re.sub(r'[^a-z0-9]+', '-', ((g.get('funder') or '') + '-' + (g.get('name') or '')).lower()).strip('-')[:48]
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
    "specific research and career stage to what the funder supports. Return via emit.")

def batch_call(grants):
    payload = [{"id": g['id'], "name": g.get('name'), "funder": g.get('funder'),
                "focusAreas": ", ".join(g.get('focusAreas') or []), "amount": g.get('awardAmount') or "",
                "deadline": g.get('deadlineInfo') or g.get('closeDate') or "",
                "desc": (g.get('description') or g.get('relevanceToUser') or "")[:160]} for g in grants]
    body = {"model": MODEL, "max_tokens": 4000, "system": SYSTEM,
            "messages": [{"role": "user", "content": "Applicant:\n" + PROFILE + "\n\nGrants (JSON array):\n"
                          + json.dumps(payload) + "\n\nFor EACH id above return a fitScore 0-100 and a why of "
                          "TWO OR THREE natural, complete sentences explaining specifically why it does (or "
                          "doesn't) fit this applicant."}],
            "tools": [{"name": "emit", "input_schema": SCHEMA}], "tool_choice": {"type": "tool", "name": "emit"}}
    req = urllib.request.Request(BRIDGE, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        d = json.load(r)
    tu = next(b for b in d['content'] if b.get('type') == 'tool_use')
    return tu['input']['rankings']

def main():
    pool = load_pool()
    pool.sort(key=relevance, reverse=True)
    target = pool[:TARGET]
    ids = {g['id'] for g in target}
    cache = {}
    if os.path.exists("data/claude_rerank_cache.json"):
        try: cache = json.load(open("data/claude_rerank_cache.json"))
        except Exception: cache = {}
    todo = [g for g in target if g['id'] not in cache]
    print(f"pool={len(pool)} target={len(target)} already_cached={len(cache)} todo={len(todo)}", flush=True)
    for i in range(0, len(todo), BATCH):
        batch = todo[i:i + BATCH]
        for attempt in (1, 2):
            try:
                for r in batch_call(batch):
                    if r['id'] in ids:
                        cache[r['id']] = {"fitScore": max(0, min(100, int(r['fitScore']))), "why": str(r['why'])[:500]}
                print(f"batch {i//BATCH+1}/{(len(todo)+BATCH-1)//BATCH}: total cached {len(cache)}", flush=True)
                break
            except Exception as e:
                print(f"batch {i//BATCH+1} attempt {attempt} failed: {str(e)[:160]}", flush=True)
        json.dump(cache, open("data/claude_rerank_cache.json", "w"), ensure_ascii=False, indent=0)
    print(f"DONE. cached {len(cache)} grants -> data/claude_rerank_cache.json", flush=True)

main()
