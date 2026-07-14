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
    # The shipped demo profile is FICTIONAL (data/demo_cv.txt — tracked, so the build is
    # reproducible from a clean clone). NEVER read a real CV out of user_profile/ (gitignored,
    # holds PII): index.html is published, so anything inlined here becomes public.
    txt = open("data/demo_cv.txt", encoding="utf-8").read()
    txt = re.sub(r'[ \t]+', ' ', txt)
    txt = re.sub(r'\n{2,}', '\n', txt).strip()
    return txt[:2600]

demo = {
    "name": "Jordan Bennett", "careerStage": "postdoc",
    "citizenship": "us", "phdYear": 2019, "prMonth": "", "nationality": "",
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

# Safety: index.html is PUBLISHED. The demo personas are fictional; the real author's identity
# (name, nationality, immigration status, employer) must never reach the shipped artifact.
# Patterns live in .identity_denylist, which is GITIGNORED — this repo is public, so committing
# the denylist would publish the very names it protects. Two scopes:
#   [global]  never anywhere in index.html
#   [profile] never in the applicant-describing payloads (demo profile + Claude cache). The same
#             tokens are legitimate in grant data (facts about a funder) and in the eligibility
#             code (where "green card" is a rule being matched), so they are NOT banned globally.
def _denylist(path=".identity_denylist"):
    scopes, cur = {"global": [], "profile": []}, None
    if not os.path.exists(path):
        print("WARNING: .identity_denylist missing — skipping the real-identity guard.")
        return scopes
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            cur = line[1:-1]
        elif cur in scopes:
            scopes[cur].append(line)
    return scopes

_scopes = _denylist()
_profile_blob = json.dumps([demo, claude_cache], ensure_ascii=False)
for _scope, _hay, _where in (("global", html, "index.html"),
                             ("profile", _profile_blob, "the demo profile / Claude cache")):
    _hits = sorted({m.group(0) for p in _scopes[_scope] for m in re.finditer(p, _hay, re.I)})
    if _hits:
        raise SystemExit("REFUSING TO BUILD: real-identity tokens found in %s: %s\n"
                         "The demo personas must stay fictional (see user_profile/demo_cv.txt)." % (_where, _hits))

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
