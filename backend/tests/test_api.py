"""
Pytest Test Suite for FastAPI Backend Endpoints
Verifies endpoint responses, status codes, payload validations, and schema compliance.
"""
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

def test_health_endpoint(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["database"]["status"] == "connected"
    assert data["database"]["total_documents"] == 20
    assert data["retrieval_engine"]["embedding_model"] == "BAAI/bge-small-en-v1.5"
    assert data["retrieval_engine"]["indexed_chunks"] >= 300

def test_chat_endpoint_core_technical_qa(client):
    payload = {
        "query": "What must be true before starting the Hydraulic Power Unit?",
        "force_offline": True
    }
    res = client.post("/api/chat", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "IV-21" in data["direct_answer"]
    assert "sight glass" in data["direct_answer"] or "fluid level" in data["direct_answer"].lower()
    assert len(data["citations"]) >= 1
    assert data["verification_status"] == "VERIFIED"
    assert data["abstention_category"] == "NONE"

def test_chat_endpoint_epistemic_abstention_false_premise(client):
    payload = {
        "query": "What is the calibration interval for the electrical system diagram's voltage sensor?",
        "force_offline": True
    }
    res = client.post("/api/chat", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["abstention_category"] == "FALSE_PREMISE"
    assert data["verification_status"] == "NOT FOUND"
    assert "false premise" in data["direct_answer"].lower()

def test_chat_endpoint_revision_aware_historical_query(client):
    payload = {
        "query": "What was the operating pressure threshold before software revision 3.2, and what changed it?",
        "force_offline": True
    }
    res = client.post("/api/chat", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "180 bar" in data["direct_answer"]
    assert "ECN-1042" in data["direct_answer"]

def test_documents_endpoint(client):
    res = client.get("/api/documents")
    assert res.status_code == 200
    docs = res.json()
    assert len(docs) == 20
    filenames = [d["filename"] for d in docs]
    assert "operator_manual.pdf" in filenames
    assert "system_diagram_hydraulic.pdf" in filenames
    assert "ECN-1042.pdf" in filenames
    # Verify hash integrity field
    for d in docs:
        assert len(d["sha256_hash"]) == 64
        assert d["trust_tier"] in [1, 2, 3, 4, 5, 6]

def test_components_endpoint(client):
    res = client.get("/api/components")
    assert res.status_code == 200
    comps = res.json()
    assert len(comps) >= 14
    comp_ids = [c["component_id"] for c in comps]
    assert "PS-04" in comp_ids
    assert "PS-04A" in comp_ids
    assert "PS-40" in comp_ids
    assert "IV-21" in comp_ids
    assert "PLC-03" in comp_ids

def test_component_detail_endpoint_success(client):
    res = client.get("/api/components/IV-21")
    assert res.status_code == 200
    data = res.json()
    assert data["component_id"] == "IV-21"
    assert "Hydraulic Module" in data["location"]
    assert len(data["facts"]) > 0
    assert len(data["relationships"]) > 0

def test_component_detail_endpoint_not_found(client):
    res = client.get("/api/components/NON_EXISTENT_COMPONENT")
    assert res.status_code == 404

def test_facts_endpoint_with_filters(client):
    # Filter by component
    res_comp = client.get("/api/facts?component_id=HPU")
    assert res_comp.status_code == 200
    facts_hpu = res_comp.json()
    assert len(facts_hpu) > 0
    assert all(f["subject"] == "HPU" for f in facts_hpu)

    # Filter by fact_type
    res_type = client.get("/api/facts?fact_type=specified_setpoint")
    assert res_type.status_code == 200
    facts_type = res_type.json()
    assert len(facts_type) > 0
    assert all(f["fact_type"] == "specified_setpoint" for f in facts_type)

def test_revisions_endpoint(client):
    res = client.get("/api/revisions")
    assert res.status_code == 200
    revs = res.json()
    assert len(revs) == 4
    rev_names = [r["software_revision"] for r in revs]
    assert "3.0" in rev_names
    assert "3.1" in rev_names
    assert "3.2" in rev_names
    assert "3.2.1" in rev_names

    # Check setpoint progression
    r30 = [r for r in revs if r["software_revision"] == "3.0"][0]
    r32 = [r for r in revs if r["software_revision"] == "3.2"][0]
    assert r30["operating_pressure_bar"] == 180
    assert r30["active_pressure_sensor"] == "PS-04"
    assert r32["operating_pressure_bar"] == 200
    assert r32["active_pressure_sensor"] == "PS-04A"

def test_evaluation_summary_endpoint(client):
    res = client.get("/api/evaluation/summary")
    assert res.status_code == 200
    data = res.json()
    assert "aggregate_metrics" in data
    assert "itemized_question_results" in data
    assert len(data["itemized_question_results"]) == 23
    assert data["aggregate_metrics"]["answer_metrics"]["answer_correctness_accuracy"] == 1.0

def test_diagram_endpoint(client):
    res = client.get("/api/diagram")
    assert res.status_code == 200
    data = res.json()
    assert data["drawing_id"] == "AEG-DWG-H01"
    assert len(data["elements"]) >= 7
    # Verify purple control line to PS-04A and IV-21
    purple_conns = [c for c in data["connections"] if "purple" in c["line_type"]]
    assert len(purple_conns) >= 2
    targets = [c["target"] for c in purple_conns]
    assert "PS-04A" in targets
    assert "IV-21" in targets
    # Verify tan line to Auxiliary Reservoir
    tan_conns = [c for c in data["connections"] if "tan" in c["line_type"]]
    assert tan_conns
    assert any(c["target"] == "AUX_RESERVOIR" for c in tan_conns)

def test_raw_document_endpoint_success(client):
    res = client.get("/api/documents/ECN-1042.pdf/raw")
    assert res.status_code == 200
    assert len(res.content) > 1000

def test_raw_document_endpoint_not_found(client):
    res = client.get("/api/documents/non_existent_file.pdf/raw")
    assert res.status_code == 404



