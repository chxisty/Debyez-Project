import urllib.request
import ssl
import re

ctx = ssl.create_default_context()
base_url = "https://debyez.vercel.app"

req = urllib.request.Request(base_url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
    html = response.read().decode("utf-8")

scripts = re.findall(r'src="([^"]+\.js)"', html)
print(f"Total scripts in index: {len(scripts)}")

backend_candidates = set()
localhost_found = False

for s in scripts:
    s_url = s if s.startswith("http") else base_url + s
    try:
        req_s = urllib.request.Request(s_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req_s, context=ctx, timeout=10) as resp_s:
            js_content = resp_s.read().decode("utf-8")
            if "localhost:8000" in js_content:
                localhost_found = True
                print(f"CRITICAL: Found 'localhost:8000' in {s}!")
            # Find any onrender.com or other backend URLs
            matches = re.findall(r'https?://[a-zA-Z0-9_\-\.]+\.onrender\.com[a-zA-Z0-9_\-\./]*', js_content)
            for m in matches:
                backend_candidates.add(m)
            # Find any /api/chat or similar
            if "/api/chat" in js_content:
                print(f"Found '/api/chat' referenced in {s}")
    except Exception as e:
        print(f"Error fetching script {s}: {e}")

print(f"Localhost:8000 found in client bundle: {localhost_found}")
print(f"Render backend URLs found in client bundle: {backend_candidates}")
