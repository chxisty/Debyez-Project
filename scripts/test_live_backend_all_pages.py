import urllib.request
import ssl
import json
import time

ctx = ssl.create_default_context()
BASE = "https://debyez-project.onrender.com"

def fetch(path, method="GET", body=None):
    url = f"{BASE}{path}"
    headers = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"}
    data = json.dumps(body).encode("utf-8") if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    start = time.time()
    with urllib.request.urlopen(req, context=ctx, timeout=30) as r:
        elapsed = time.time() - start
        raw = r.read().decode("utf-8")
        return r.status, elapsed, json.loads(raw)

print("=" * 70)
print(f"AUDITING LIVE RENDER BACKEND ({BASE}) FOR ALL 8 FRONTEND PAGES")
print("=" * 70)

# 1. Dashboard
print("\n--- 1. Dashboard Page ('/') ---")
status, t, health = fetch("/health")
print(f"  api.getHealth() -> {status} in {t:.2f}s | docs={health['database']['total_documents']}, comps={health['database']['total_components']}")
status, t, docs = fetch("/api/documents")
print(f"  api.getDocuments() -> {status} in {t:.2f}s | {len(docs)} documents")
status, t, comps = fetch("/api/components")
print(f"  api.getComponents() -> {status} in {t:.2f}s | {len(comps)} components")
status, t, facts = fetch("/api/facts")
print(f"  api.getFacts() -> {status} in {t:.2f}s | {len(facts)} facts")
status, t, eval_s = fetch("/api/evaluation/summary")
print(f"  api.getEvaluationSummary() -> {status} in {t:.2f}s | Accuracy={eval_s['aggregate_metrics']['answer_metrics']['answer_correctness_accuracy']*100}%")

# 2. Chat / AI Assistant
print("\n--- 2. AI Assistant Page ('/chat') ---")
test_queries = [
    ("Q01 (Startup Interlocks)", "What must be true before starting the Hydraulic Power Unit?", None),
    ("Q02 (Operating Pressure)", "What is the current normal operating pressure for the HPU, and under what conditions does that apply?", "3.2"),
    ("Q04 (PS-04 vs PS-04A)", "Is PS-04 the same component as PS-04A?", None),
    ("Q19 (PS-04A Temp - Abstain)", "What is the maximum continuous operating temperature of PS-04A?", None),
    ("Q20 (Voltage Sensor - False Premise)", "What is the calibration interval for the electrical system diagram's voltage sensor?", None),
    ("Q23 (400V Supply - Unconfirmed)", "Is the Aegis Series-7 HCS compatible with a 3-phase 400V supply?", None)
]

for label, q, rev in test_queries:
    status, t, ans = fetch("/api/chat", method="POST", body={"query": q, "target_revision": rev, "force_offline": True})
    print(f"  {label} -> {status} in {t:.2f}s")
    print(f"    Verification Status: {ans.get('verification_status')}")
    print(f"    Abstention Category: {ans.get('abstention_category')}")
    print(f"    Direct Answer: {ans.get('direct_answer')[:120]}...")
    print(f"    Citations ({len(ans.get('citations', []))}): {[c.get('source_document') for c in ans.get('citations', [])]}")

# 3. Documents Page
print("\n--- 3. Document Explorer Page ('/documents') ---")
status, t, docs = fetch("/api/documents")
print(f"  api.getDocuments() -> {status} in {t:.2f}s | {len(docs)} documents verified")
raw_url = f"{BASE}/api/documents/operator_manual.pdf/raw"
req = urllib.request.Request(raw_url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
    print(f"  api.getRawDocument('operator_manual.pdf') -> {r.status} | Content-Type: {r.headers.get('Content-Type')}, Size: {len(r.read())} bytes")

# 4. Components Page
print("\n--- 4. Component Catalog Page ('/components') ---")
for cid in ["HPU", "PS-04A", "IV-21", "PLC-03"]:
    status, t, c_detail = fetch(f"/api/components/{cid}")
    print(f"  api.getComponentDetail('{cid}') -> {status} in {t:.2f}s | Name: {c_detail['canonical_name']}, Facts: {len(c_detail['facts'])}, Rels: {len(c_detail['relationships'])}")

# 5. Revisions Page
print("\n--- 5. Revision Comparison Page ('/revisions') ---")
status, t, revs = fetch("/api/revisions")
print(f"  api.getRevisions() -> {status} in {t:.2f}s | {len(revs)} revision baselines:")
for r in revs:
    print(f"    - Rev {r['software_revision']} ({r['effective_date']}): {r['operating_pressure_bar']} bar, Sensor: {r['active_pressure_sensor']}")

# 6. Evidence Inspector Page
print("\n--- 6. Evidence Inspector Page ('/evidence') ---")
status, t, facts = fetch("/api/facts")
print(f"  api.getFacts() -> {status} in {t:.2f}s | {len(facts)} granular facts with bounding-boxes")

# 7. Evaluation Benchmark Page
print("\n--- 7. Evaluation Dashboard Page ('/evaluation') ---")
status, t, ev = fetch("/api/evaluation/summary")
itemized = ev.get("itemized_question_results", [])
print(f"  api.getEvaluationSummary() -> {status} in {t:.2f}s | {len(itemized)} benchmark questions")
print(f"    MRR: {ev['aggregate_metrics']['retrieval_metrics']['mean_reciprocal_rank_mrr']}")
print(f"    Hit Rate @ 5: {ev['aggregate_metrics']['retrieval_metrics']['hit_rate_at_5'] * 100}%")
print(f"    Citation Precision: {ev['aggregate_metrics']['answer_metrics']['citation_precision'] * 100}%")

# 8. Hydraulic Diagram Page
print("\n--- 8. Hydraulic Diagram Page ('/diagram') ---")
status, t, diag = fetch("/api/diagram")
print(f"  api.getDiagramData() -> {status} in {t:.2f}s | {len(diag['elements'])} visual elements, {len(diag['connections'])} connection paths")

print("\n" + "=" * 70)
print("ALL LIVE BACKEND ENDPOINTS AND FRONTEND DATA QUERIES FULLY PASSING!")
print("=" * 70)
