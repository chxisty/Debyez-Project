import urllib.request
import ssl
import json

ctx = ssl.create_default_context()
backend_base = "https://debyez-project.onrender.com"

endpoints = [
    "/health",
    "/api/documents",
    "/api/components",
    "/api/components/HPU",
    "/api/components/PS-04A",
    "/api/facts",
    "/api/revisions",
    "/api/diagram",
    "/api/evaluation/summary"
]

print("=== TESTING RENDER BACKEND ENDPOINTS ===")
for ep in endpoints:
    url = f"{backend_base}{ep}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            data = resp.read().decode("utf-8")
            parsed = json.loads(data)
            count = len(parsed) if isinstance(parsed, list) else len(parsed.keys())
            print(f"GET {ep} -> {resp.status} OK (items/keys: {count})")
    except Exception as e:
        print(f"GET {ep} -> FAILED: {e}")

# Test Chat POST
print("\n=== TESTING CHAT POST ENDPOINT ===")
chat_url = f"{backend_base}/api/chat"
payload = {
    "query": "What is the normal operating pressure of the HPU in Rev 3.2?",
    "target_revision": "3.2",
    "force_offline": True
}
try:
    req = urllib.request.Request(
        chat_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(req, context=ctx, timeout=20) as resp:
        data = resp.read().decode("utf-8")
        res = json.loads(data)
        print("POST /api/chat -> 200 OK")
        print("  Direct answer:", res.get("direct_answer"))
        print("  Status:", res.get("verification_status"))
        print("  Citations count:", len(res.get("citations", [])))
        for c in res.get("citations", []):
            print(f"    - {c.get('source_document')} p.{c.get('page_number')}")
except Exception as e:
    print(f"POST /api/chat -> FAILED: {e}")
