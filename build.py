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

# Annotate records with the eligibility-audit verdicts (per the applicant profile in the audit workflow)
import os
def _key(name, funder):
    return (re.sub(r'[^a-z0-9]', '', (name or '').lower())[:45],
            re.sub(r'[^a-z0-9]', '', (funder or '').lower())[:26])
audit_map = {}
if os.path.exists("data/audit_ineligible.json"):
    for a in json.load(open("data/audit_ineligible.json")):
        if a.get("confidence") in ("high", "medium"):
            audit_map[_key(a["name"], a["funder"])] = a
annot = 0
for rec in curated + jhu:
    a = audit_map.get(_key(rec["name"], rec["funder"]))
    if a:
        rec["auditCode"] = a["reasonCode"]
        rec["auditReason"] = a["reason"]
        annot += 1

def safe(v):
    return json.dumps(v, ensure_ascii=False).replace("</", "<\\/")

html = open("index.template.html", encoding="utf-8").read()
for marker, val in [("DEMO", demo), ("CURATED", curated), ("JHU", jhu)]:
    pat = re.compile(re.escape("/*__" + marker + "__*/") + r'(\{\}|\[\])')
    if not pat.search(html):
        raise SystemExit("marker not found: " + marker)
    repl = "/*__" + marker + "__*/" + safe(val)
    html = pat.sub(lambda m, r=repl: r, html, count=1)

open("index.html", "w", encoding="utf-8").write(html)
print(f"built index.html  |  curated={len(curated)} jhu={len(jhu)} cv={len(demo['cvText'])} chars | audit-annotated={annot}")
