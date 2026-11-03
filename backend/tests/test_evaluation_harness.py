"""
Pytest Test Suite for Phase 6 Comprehensive Evaluation Harness
Verifies end-to-end execution, retrieval metrics, answer accuracy,
citation precision, and mandatory epistemic abstention cases across all 23 evaluation questions.
"""
import pytest
import os
import json

from backend.app.evaluation.harness import AegisEvaluationHarness

@pytest.fixture(scope="module")
def eval_report():
    harness = AegisEvaluationHarness()
    report = harness.evaluate_all(top_k=25)
    return report

def test_ground_truth_integrity(eval_report):
    """Verifies that ground truth contains all 23 questions with full metadata."""
    assert eval_report["metadata"]["total_questions_evaluated"] == 23
    assert len(eval_report["itemized_question_results"]) == 23

def test_aggregate_retrieval_performance(eval_report):
    """Verifies retrieval MRR and Hit Rates exceed industrial benchmarks."""
    ret_metrics = eval_report["aggregate_metrics"]["retrieval_metrics"]
    assert ret_metrics["mean_reciprocal_rank_mrr"] >= 0.90
    assert ret_metrics["hit_rate_at_5"] == 1.0
    assert ret_metrics["hit_rate_at_10"] == 1.0
    assert ret_metrics["hit_rate_at_25"] == 1.0

def test_aggregate_answer_accuracy_and_grounding(eval_report):
    """Verifies that answers are grounded, correct, and completely free of hallucinations."""
    ans_metrics = eval_report["aggregate_metrics"]["answer_metrics"]
    assert ans_metrics["answer_correctness_accuracy"] >= 0.95
    assert ans_metrics["citation_precision"] == 1.0
    assert ans_metrics["claim_level_evidence_support"] == 1.0
    assert ans_metrics["hallucination_rate"] == 0.0
    assert ans_metrics["unsupported_claim_rate"] == 0.0

def test_aggregate_abstention_accuracy(eval_report):
    """Verifies zero false abstentions and 100% correct abstention detection."""
    abs_metrics = eval_report["aggregate_metrics"]["abstention_metrics"]
    assert abs_metrics["correct_abstention_rate"] == 1.0
    assert abs_metrics["false_abstention_rate"] == 0.0
    assert abs_metrics["missing_information_detection_accuracy_cat_a"] == 1.0
    assert abs_metrics["false_premise_detection_accuracy_cat_b"] == 1.0
    assert abs_metrics["partial_verification_classification_accuracy_cat_c_d"] == 1.0

def test_mandatory_special_cases(eval_report):
    """Explicitly audits mandatory test cases stipulated by the user."""
    item_map = {item["question_id"]: item for item in eval_report["itemized_question_results"]}

    # Q19: PS-04A operating temperature is genuinely absent
    q19 = item_map["Q19"]
    assert q19["generated_abstention_category"] == "GENUINELY_ABSENT"
    assert q19["generated_verification_status"] == "NOT FOUND"
    assert "insufficient evidence" in q19["generated_direct_answer"].lower()

    # Q20: Voltage sensor is a false premise
    q20 = item_map["Q20"]
    assert q20["generated_abstention_category"] == "FALSE_PREMISE"
    assert q20["generated_verification_status"] == "NOT FOUND"
    assert "false premise" in q20["generated_direct_answer"].lower()

    # Q21: ECN-1058 approver is blank / omitted companion
    q21 = item_map["Q21"]
    assert q21["generated_abstention_category"] == "OMITTED_COMPANION_DOCUMENT"
    assert q21["generated_verification_status"] == "PARTIALLY VERIFIED"
    assert "blank" in q21["generated_direct_answer"].lower()

    # Q22: IV-21 MTBF is genuinely absent
    q22 = item_map["Q22"]
    assert q22["generated_abstention_category"] == "GENUINELY_ABSENT"
    assert q22["generated_verification_status"] == "NOT FOUND"
    assert "insufficient evidence" in q22["generated_direct_answer"].lower()

    # Q23: 400V supply compatibility is unconfirmed
    q23 = item_map["Q23"]
    assert q23["generated_abstention_category"] == "PARTIALLY_VERIFIED"
    assert q23["generated_verification_status"] == "PARTIALLY VERIFIED"
    assert "480v" in q23["generated_direct_answer"].lower()
    assert "unstated" in q23["generated_direct_answer"].lower()

    # Q04: PS-04 != PS-04A
    q04 = item_map["Q04"]
    assert q04["is_answer_correct"] is True
    assert "not the same" in q04["generated_direct_answer"].lower()

    # Q17: PS-04 != PS-40
    q17 = item_map["Q17"]
    assert q17["is_answer_correct"] is True
    assert "completely different" in q17["generated_direct_answer"].lower()

    # Q09 & Q18: 180 bar historical setpoint
    q09 = item_map["Q09"]
    assert q09["is_answer_correct"] is True
    assert "180 bar" in q09["generated_direct_answer"]

    q18 = item_map["Q18"]
    assert q18["is_answer_correct"] is True
    assert "180 bar" in q18["generated_direct_answer"]

    # Q03 & Q07: Alarm A17
    q03 = item_map["Q03"]
    assert q03["is_answer_correct"] is True
    assert "150 bar" in q03["generated_direct_answer"]

    q07 = item_map["Q07"]
    assert q07["is_answer_correct"] is True
    assert "shutdown procedure 4.7" in q07["generated_direct_answer"].lower()

    # Q06: Hydraulic schematic direct connections
    q06 = item_map["Q06"]
    assert q06["is_answer_correct"] is True
    assert "ps-04a" in q06["generated_direct_answer"].lower()
    assert "iv-21" in q06["generated_direct_answer"].lower()

    # Q12: Auxiliary Reservoir in training slides
    q12 = item_map["Q12"]
    assert q12["is_answer_correct"] is True
    assert "auxiliary reservoir" in q12["generated_direct_answer"].lower()

