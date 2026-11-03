import os
import subprocess
import shutil

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
temp_dir = os.environ.get("TEMP", r"C:\Users\DELL\AppData\Local\Temp")
dest_dir = os.path.join(os.getcwd(), "reports", "screenshots")
os.makedirs(dest_dir, exist_ok=True)

pages = {
    "01_dashboard.png": "http://localhost:3000",
    "02_chat.png": "http://localhost:3000/chat",
    "03_documents.png": "http://localhost:3000/documents",
    "04_components.png": "http://localhost:3000/components",
    "05_revisions.png": "http://localhost:3000/revisions",
    "06_evidence.png": "http://localhost:3000/evidence",
    "07_evaluation.png": "http://localhost:3000/evaluation",
    "08_diagram.png": "http://localhost:3000/diagram",
    "09_chat_answered.png": "http://localhost:3000/chat?q=What%20is%20the%20normal%20operating%20pressure%20under%20Revision%203.2%3F&rev=3.2"
}

for name, url in pages.items():
    tmp_path = os.path.join(temp_dir, name)
    user_data = os.path.join(temp_dir, "chrome_tmp_scr")
    args = [
        chrome_path,
        "--headless",
        "--no-sandbox",
        f"--user-data-dir={user_data}",
        f"--screenshot={tmp_path}",
        "--window-size=1440,960",
        "--virtual-time-budget=4000",
        url
    ]
    res = subprocess.run(args, capture_output=True, text=True)
    if os.path.exists(tmp_path):
        target = os.path.join(dest_dir, name)
        shutil.copy2(tmp_path, target)
        print(f"Captured {name}: {os.path.getsize(target)} bytes")
    else:
        print(f"Failed {name}: {res.stderr}")

print("Done screenshot capture.")
