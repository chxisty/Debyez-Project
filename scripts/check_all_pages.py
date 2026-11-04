import urllib.request
import ssl
import re

ctx = ssl.create_default_context()
base = "https://debyez.vercel.app"

pages = [
    "/",
    "/chat",
    "/documents",
    "/components",
    "/revisions",
    "/evidence",
    "/evaluation",
    "/diagram"
]

print(f"Auditing all 8 pages on {base}...\n")
for p in pages:
    url = f"{base}{p}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            content = resp.read().decode("utf-8")
            # Check for error indicators
            has_error = "Application error" in content or "Internal Server Error" in content or "404" in content
            title_m = re.search(r"<title>(.*?)</title>", content)
            title = title_m.group(1) if title_m else "No title"
            print(f"PAGE: {p}")
            print(f"  Status: {resp.status}")
            print(f"  Title: {title}")
            print(f"  Length: {len(content)} bytes")
            print(f"  Error strings detected: {has_error}")
            # Look for API calls or localhost references
            if "localhost:8000" in content:
                print("  WARNING: 'localhost:8000' found in page HTML!")
    except urllib.error.HTTPError as he:
        print(f"PAGE: {p} -> HTTP ERROR {he.code}: {he.reason}")
    except Exception as e:
        print(f"PAGE: {p} -> FAILED: {e}")
    print()

