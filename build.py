#!/usr/bin/env python3
"""Build index.html from index.template.html by inlining the datasets.
Usage: python3 build.py
Reads:  index.template.html, data/curated_opportunities.json, data/jhu_opportunities.json,
        user_profile CV (for the demo profile).
Writes: index.html
"""
import json, re, glob, subprocess, os

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

def cv_excerpt():
    pdfs = glob.glob("user_profile/*.pdf")
    if not pdfs:
        return ""
    txt = subprocess.run(["pdftotext", "-layout", pdfs[0], "-"],
                         capture_output=True, text=True).stdout
    i = txt.find("RELATED EXPERIENCE")
    j = txt.find("Selected PUBLICATIONS", i + 1)
    exp = txt[i:j] if i >= 0 and j >= 0 else txt[:3000]
    exp = re.sub(r'[ \t]+', ' ', exp)
    exp = re.sub(r'\n{2,}', '\n', exp).strip()
    return exp[:2600]

demo = {
    "name": "Eric Minwei Liu", "careerStage": "postdoc",
    "citizenship": "pending", "phdYear": 2019, "prMonth":"[redacted]", "nationality":"[redacted]",
    "topics": ["Computational oncology", "Machine learning", "Cancer genomics",
               "Single-cell RNA-seq", "T-cell lymphoma", "Immunotherapy",
               "Risk stratification", "Multi-omics integration"],
    "focus": ["blood cancer/hematology", "AI/computational", "genomics/omics",
              "cancer immunology", "oncology"],
    "cvText": cv_excerpt(),
}
curated = json.load(open("data/curated_opportunities.json"))
jhu = json.load(open("data/jhu_updated.json"))   # web-refreshed 2026-2027 deadlines
# Real Grants.gov opportunities, inlined as an offline fallback if the live API is unreachable.
fedseed = json.load(open("data/federal_seed.json")) if os.path.exists("data/federal_seed.json") else []
# Precomputed Claude fit reasoning for the demo profile, keyed by grant id (see worker/precompute_rerank.py).
claude_cache = json.load(open("data/claude_rerank_cache.json")) if os.path.exists("data/claude_rerank_cache.json") else {}

# Annotate records with the eligibility-audit verdicts (per the applicant profile in the audit workflow).
# Match on the distinctive NAME (parentheticals stripped); use funder only to break ties, since the
# audit and the data sometimes spell the funder differently (e.g. "NIH / NCI" vs "NIH — NCI, NHLBI, …").
import os
def _nname(name):
    return re.sub(r'[^a-z0-9]', '', re.sub(r'\([^)]*\)', ' ', (name or '').lower()))[:44]
def _nfunder(funder):
    return re.sub(r'[^a-z0-9]', '', re.sub(r'\([^)]*\)', ' ', (funder or '').lower()))[:16]
audit_by_name = {}
if os.path.exists("data/audit_ineligible.json"):
    for a in json.load(open("data/audit_ineligible.json")):
        if a.get("confidence") in ("high", "medium"):
            audit_by_name.setdefault(_nname(a["name"]), []).append(a)
annot = 0
for rec in curated + jhu:
    cands = audit_by_name.get(_nname(rec["name"]), [])
    a = None
    if len(cands) == 1:
        a = cands[0]                                  # unique name → match regardless of funder spelling
    elif cands:
        rf = _nfunder(rec["funder"])
        a = next((c for c in cands if _nfunder(c["funder"])[:8] == rf[:8] or rf in _nfunder(c["funder"]) or _nfunder(c["funder"]) in rf), None)
    if a:
        rec["auditCode"] = a["reasonCode"]
        rec["auditReason"] = a["reason"]
        annot += 1

# Guard: every pooled grant must get a UNIQUE runtime id, or Save + the Claude-fit cache
# would smear one entry across distinct cards. This replicates the app's NAME-first slugId
# (index.template.html slugId) and fails the build on any collision.
def _slug(prefix, funder, name):
    s = re.sub(r'-+$', '', re.sub(r'^-+', '', re.sub(r'[^a-z0-9]+', '-', ((name or "") + "-" + (funder or "")).lower())))[:48]
    return prefix + "-" + s
_ids = {}
for _prefix, _recs in (("cur", curated), ("jhu", jhu)):
    for _r in _recs:
        _id = _slug(_prefix, _r.get("funder", ""), _r.get("name", ""))
        if _id in _ids:
            raise SystemExit("DUPLICATE grant id %r:\n  A: %s\n  B: %s\nReconcile the duplicate rows in data/*.json." % (_id, _ids[_id], _r.get("funder","")+" | "+_r.get("name","")))
        _ids[_id] = _r.get("funder","") + " | " + _r.get("name","")
# Every Claude-cache id must resolve to a real pooled grant (no orphaned reasoning).
for _pk, _pc in (claude_cache.items() if isinstance(claude_cache, dict) and claude_cache and all(isinstance(v, dict) for v in claude_cache.values()) and not any("fitScore" in (v or {}) for v in claude_cache.values()) else []):
    _orphans = [i for i in _pc if i not in _ids]
    if _orphans:
        raise SystemExit("Claude cache profile %r has %d orphaned ids (no matching grant): %s" % (_pk, len(_orphans), _orphans[:5]))

def safe(v):
    return json.dumps(v, ensure_ascii=False).replace("</", "<\\/")

html = open("index.template.html", encoding="utf-8").read()
for marker, val in [("DEMO", demo), ("CURATED", curated), ("JHU", jhu), ("FEDSEED", fedseed), ("CLAUDECACHE", claude_cache)]:
    pat = re.compile(re.escape("/*__" + marker + "__*/") + r'(\{\}|\[\])')
    if not pat.search(html):
        raise SystemExit("marker not found: " + marker)
    repl = "/*__" + marker + "__*/" + safe(val)
    html = pat.sub(lambda m, r=repl: r, html, count=1)

# Safety: a real Anthropic key must NEVER be baked into the shipped static file.
# (The literal placeholder "sk-ant-…" in the connect-modal input is fine; match only key-shaped tokens.)
if re.search(r'sk-ant-[A-Za-z0-9_-]{20,}', html):
    raise SystemExit("REFUSING TO BUILD: a real 'sk-ant-' key is present in the output. Keys belong on the Worker, never in index.html.")

import sys
if "--check" in sys.argv:
    # CI / pre-commit guard: fail if the committed index.html doesn't match the template output,
    # so the shipped artifact can never silently lag index.template.html.
    current = open("index.html", encoding="utf-8").read() if os.path.exists("index.html") else ""
    if current != html:
        raise SystemExit("index.html is STALE — run `python3 build.py` and commit the result.")
    print("index.html is up to date with the template.")
    sys.exit(0)

open("index.html", "w", encoding="utf-8").write(html)
_cc = sum(len(v) for v in claude_cache.values()) if isinstance(claude_cache, dict) and claude_cache and all(isinstance(v, dict) for v in claude_cache.values()) and not any("fitScore" in (v or {}) for v in claude_cache.values()) else len(claude_cache)
print(f"built index.html  |  curated={len(curated)} jhu={len(jhu)} fedseed={len(fedseed)} claude_cache={_cc} ({','.join(f'{k}:{len(v)}' for k,v in claude_cache.items()) if isinstance(claude_cache,dict) else ''}) cv={len(demo['cvText'])} chars | audit-annotated={annot}")
