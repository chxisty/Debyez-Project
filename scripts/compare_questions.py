import json

with open("data/evaluation/evaluation_results_23.json", "r", encoding="utf-8") as f:
    eval_data = json.load(f)

items = eval_data.get("itemized_question_results", [])
print(f"Total items in evaluation_results_23.json: {len(items)}\n")

for item in items:
    qid = item.get("question_id")
    qtext = item.get("question")
    ans = item.get("expected_answer")
    gen_ans = item.get("generated_direct_answer")
    status = item.get("expected_verification_status")
    abst = item.get("expected_abstention_category")
    print(f"{qid}:")
    print(f"  Q: {qtext}")
    print(f"  Expected: {ans[:100]}...")
    print(f"  Status: {status} | Abstention: {abst}")
