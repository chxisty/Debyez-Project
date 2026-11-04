import urllib.request
import ssl
import re

ctx = ssl.create_default_context()
base_url = "https://debyez.vercel.app"

req = urllib.request.Request(base_url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
    html = response.read().decode("utf-8")

# Find all scripts
scripts = re.findall(r'src="([^"]+\.js)"', html)
print(f"Total scripts: {len(scripts)}")

for s in scripts:
    s_url = s if s.startswith("http") else base_url + s
    req_s = urllib.request.Request(s_url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req_s, context=ctx, timeout=10) as resp_s:
        js = resp_s.read().decode("utf-8")
        # Search for API_BASE_URL or any URL
        if "http://localhost:8000" in js:
            print(f"FOUND 'http://localhost:8000' in {s}!")
        if "aegis-backend.onrender.com" in js:
            print(f"FOUND 'aegis-backend.onrender.com' in {s}!")
        if "debyez-project.onrender.com" in js:
            print(f"FOUND 'debyez-project.onrender.com' in {s}!")
