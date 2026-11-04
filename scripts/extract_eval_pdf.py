import fitz

doc = fitz.open("evaluation-questions.pdf")
print(f"Total pages in evaluation-questions.pdf: {len(doc)}")
for i, page in enumerate(doc):
    print(f"\n--- PAGE {i+1} ---")
    print(page.get_text())

