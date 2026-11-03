"""
FastAPI Route Handlers
Implements all required backend REST endpoints for the Aegis Knowledge System.
"""
import os
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from backend.app.config import DOCUMENT_METADATA_REGISTRY, DATA_DIR
from backend.app.knowledge.database import KnowledgeDatabase
from backend.app.answer_generation.engine import AnswerEngine
from backend.app.answer_generation.schema import GroundedAnswer
from backend.app.answer_generation.llm_adapters import LLMAdapter
from backend.app.retrieval.chunk_indexer import ChunkIndexer
from backend.app.api.schemas import (
    ChatRequest,
    HealthResponse,
    DocumentListItem,
    ComponentDetailResponse,
    RevisionItem,
    DiagramResponse,
    DiagramElement,
    DiagramConnection
)

router = APIRouter()

# Shared singleton instances
_db = KnowledgeDatabase()
_engine = AnswerEngine()
_chunks = ChunkIndexer.load_chunks()

@router.get("/health", response_model=HealthResponse, tags=["System Health"])
def get_health() -> HealthResponse:
    """Returns system status, database health, vector cache size, and LLM availability."""
    docs = _db.get_all_documents()
    comps = _db.get_all_components()
    facts = _db.get_all_facts()
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0 (Phase 7 Full-Stack)",
        database={
            "status": "connected",
            "database_type": "SQLite 3",
            "total_documents": len(docs),
            "total_components": len(comps),
            "total_facts": len(facts)
        },
        retrieval_engine={
            "embedding_model": "BAAI/bge-small-en-v1.5",
            "embedding_dimension": 384,
            "indexed_chunks": len(_chunks),
            "channels": ["structured_sql", "dense_semantic", "bm25"],
            "fusion": "Reciprocal Rank Fusion (k=60) with Trust Tier Weighting"
        },
        llm_status={
            "available": LLMAdapter.can_run(),
            "provider": "Groq / OpenAI (Auto-fallback to Deterministic Offline Engine)",
            "deterministic_fallback_ready": True
        }
    )

@router.post("/api/chat", response_model=GroundedAnswer, tags=["Question Answering"])
def chat(request: ChatRequest) -> GroundedAnswer:
    """
    Executes hybrid retrieval, grounded answer generation, textual citation audit,
    and epistemic abstention detection.
    """
    try:
        ans = _engine.answer_question(
            query=request.query,
            target_revision=request.target_revision,
            force_offline=request.force_offline
        )
        return ans
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")

@router.get("/api/documents", response_model=List[DocumentListItem], tags=["Document Explorer"])
def list_documents() -> List[DocumentListItem]:
    """Lists all 20 ingested documents with trust tiers, hashes, and archival statuses."""
    docs = _db.get_all_documents()
    items = []
    for doc in docs:
        c_count = sum(1 for c in _chunks if c.filename == doc.filename)
        meta = DOCUMENT_METADATA_REGISTRY.get(doc.filename, {})
        title = meta.get("title", doc.filename) if isinstance(meta, dict) else getattr(meta, "title", doc.filename)
        system = meta.get("system", "Aegis Series-7 HCS") if isinstance(meta, dict) else getattr(meta, "system", "Aegis Series-7 HCS")
        revision = meta.get("revision", doc.revision or "Current") if isinstance(meta, dict) else getattr(meta, "revision", doc.revision or "Current")
        items.append(DocumentListItem(
            document_id=doc.document_id,
            filename=doc.filename,
            title=title,
            system=system,
            document_type=doc.document_type,
            revision=revision or "Current",
            trust_tier=doc.trust_level,
            sha256_hash=doc.sha256_hash or "",
            is_archived=doc.is_archived,
            archival_reason=doc.archival_reason,
            chunk_count=c_count
        ))
    items.sort(key=lambda x: (x.trust_tier, x.filename))
    return items

@router.get("/api/documents/{filename}/raw", tags=["Document Explorer"])
def get_raw_document(filename: str):
    """Serves the actual raw source file from aegis-dataset for direct inspection."""
    for p in DATA_DIR.rglob(filename):
        if p.is_file():
            return FileResponse(p)
    raise HTTPException(status_code=404, detail=f"File '{filename}' not found in dataset")


@router.get("/api/components", tags=["Component Explorer"])
def list_components() -> List[Dict[str, Any]]:
    """Lists all canonical components, common names, aliases, and locations."""
    comps = _db.get_all_components()
    return [c.model_dump() for c in comps]

@router.get("/api/components/{component_id}", response_model=ComponentDetailResponse, tags=["Component Explorer"])
def get_component_detail(component_id: str) -> ComponentDetailResponse:
    """Returns canonical component details, active facts, topological relationships, and conflicts."""
    cid_upper = component_id.strip().upper()
    comps = [c for c in _db.get_all_components() if c.component_id.upper() == cid_upper]
    if not comps:
        raise HTTPException(status_code=404, detail=f"Component '{component_id}' not found.")
    comp = comps[0]

    all_facts = _db.get_all_facts()
    all_rels = _db.get_all_relationships()
    all_confs = _db.get_all_conflicts()

    comp_facts = [f.model_dump() for f in all_facts if f.subject.upper() == cid_upper]
    comp_rels = [
        r.model_dump() for r in all_rels 
        if r.source_component.upper() == cid_upper or r.target_component.upper() == cid_upper
    ]
    comp_confs = [
        c.model_dump() for c in all_confs 
        if cid_upper in c.conflicting_parameter.upper() or cid_upper in c.conflict_id.upper()
    ]

    return ComponentDetailResponse(
        component_id=comp.component_id,
        canonical_name=comp.canonical_name,
        component_type=comp.component_type,
        description=comp.description,
        aliases=comp.aliases,
        location=comp.location,
        status=comp.status,
        facts=comp_facts,
        relationships=comp_rels,
        conflicts=comp_confs
    )

@router.get("/api/facts", tags=["Knowledge Facts"])
def list_facts(
    revision: Optional[str] = Query(None, description="Filter facts by applicable software revision"),
    verification_status: Optional[str] = Query(None, description="Filter by status (VERIFIED, PARTIALLY VERIFIED, etc.)"),
    component_id: Optional[str] = Query(None, description="Filter by canonical component ID"),
    fact_type: Optional[str] = Query(None, description="Filter by fact type (specified_setpoint, historical_setpoint, observed_measurement)")
) -> List[Dict[str, Any]]:
    """Queries facts with dynamic revision, component, fact-type, and verification status filters."""
    facts = _db.get_active_facts_for_revision(revision)
    
    if verification_status:
        v_upper = verification_status.strip().upper()
        facts = [
            f for f in facts 
            if (hasattr(f.verification_status, "value") and f.verification_status.value == v_upper) or str(f.verification_status) == v_upper
        ]

    if component_id:
        c_upper = component_id.strip().upper()
        facts = [f for f in facts if f.subject.upper() == c_upper]

    if fact_type:
        f_type_lower = fact_type.strip().lower()
        facts = [f for f in facts if f.fact_type.lower() == f_type_lower]

    return [f.model_dump() for f in facts]

@router.get("/api/revisions", response_model=List[RevisionItem], tags=["Revision Comparison"])
def get_revisions() -> List[RevisionItem]:
    """
    Returns the authoritative software revision timeline.
    Clarifies the distinction between software revisions (3.0, 3.1, 3.2, 3.2.1)
    and document publication editions (Rev 1, Rev 2, Rev 4, Rev 5).
    """
    return [
        RevisionItem(
            software_revision="3.0",
            effective_date="2023-01-15",
            operating_pressure_bar=180,
            active_pressure_sensor="PS-04",
            governing_ecn=None,
            summary_of_changes="Initial production release of Aegis Series-7 Hydraulic Control System.",
            status="Superseded"
        ),
        RevisionItem(
            software_revision="3.1",
            effective_date="2024-06-20",
            operating_pressure_bar=180,
            active_pressure_sensor="PS-04",
            governing_ecn=None,
            summary_of_changes="Maintenance and minor diagnostic routines update. Operating pressure setpoint retained at 180 bar.",
            status="Superseded"
        ),
        RevisionItem(
            software_revision="3.2",
            effective_date="2025-09-30",
            operating_pressure_bar=200,
            active_pressure_sensor="PS-04A",
            governing_ecn="ECN-1042",
            summary_of_changes="Replaced pressure sensor PS-04 with PS-04A to eliminate 18-month drift. Increased normal operating pressure setpoint from 180 bar to 200 bar for units manufactured after 2024.",
            status="Active"
        ),
        RevisionItem(
            software_revision="3.2.1",
            effective_date="2026-01-10",
            operating_pressure_bar=200,
            active_pressure_sensor="PS-04A",
            governing_ecn="ECN-1058",
            summary_of_changes="Documentation correction: clarified Alarm A17 reference to active sensor PS-04A. Operating setpoint retained at 200 bar.",
            status="Current Active"
        )
    ]

@router.get("/api/evaluation/summary", tags=["Evaluation Dashboard"])
def get_evaluation_summary() -> Dict[str, Any]:
    """Returns the full 23-question benchmark results, retrieval/answer metrics, and itemized results."""
    eval_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
        "data", "evaluation", "evaluation_results_23.json"
    )
    if not os.path.exists(eval_file):
        raise HTTPException(status_code=404, detail="Evaluation results not found. Run evaluation harness first.")
    
    with open(eval_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

@router.get("/api/diagram", response_model=DiagramResponse, tags=["Hydraulic Diagram"])
def get_diagram_data() -> DiagramResponse:
    """Returns the exact extracted hydraulic schematic vector geometry and topology without fabricated connections."""
    rels = _db.get_all_relationships()
    dwg_rels = [r for r in rels if r.drawing_reference == "AEG-DWG-H01" and not r.is_archived]
    
    connections = []
    for r in dwg_rels:
        color = "#8a4b9c" if "purple" in r.line_type else ("#b08a4e" if "tan" in r.line_type else "#555555")
        connections.append(DiagramConnection(
            rel_id=r.rel_id,
            source=r.source_component,
            target=r.target_component,
            connection_type=r.relationship_type,
            line_type=r.line_type,
            color=color,
            endpoints=r.endpoints or "",
            description=r.notes or f"{r.source_component} to {r.target_component}"
        ))

    elements = [
        DiagramElement(
            id="PLC-03",
            label="PLC-03",
            sublabel="HCS Controller",
            type="controller",
            bbox=[230.4, 201.6, 374.4, 244.8],
            fill_color="#1e293b",
            border_color="#8a4b9c"
        ),
        DiagramElement(
            id="PS-04A",
            label="PS-04A",
            sublabel="Pressure Sensor",
            type="sensor",
            bbox=[72.0, 302.4, 187.2, 345.6],
            fill_color="#1e293b",
            border_color="#38bdf8"
        ),
        DiagramElement(
            id="HPU",
            label="HPU",
            sublabel="Hydraulic Power Unit",
            type="power_unit",
            bbox=[230.4, 302.4, 374.4, 345.6],
            fill_color="#1e293b",
            border_color="#64748b"
        ),
        DiagramElement(
            id="IV-21",
            label="IV-21",
            sublabel="Isolation Valve",
            type="valve",
            bbox=[388.8, 302.4, 504.0, 345.6],
            fill_color="#1e293b",
            border_color="#8a4b9c"
        ),
        DiagramElement(
            id="MAIN_RESERVOIR",
            label="Main Reservoir",
            sublabel="Primary Storage (250L)",
            type="reservoir",
            bbox=[230.4, 403.2, 374.4, 446.4],
            fill_color="#1e293b",
            border_color="#64748b"
        ),
        DiagramElement(
            id="AUX_RESERVOIR",
            label="Auxiliary Reservoir",
            sublabel="Peak Top-up (Line 4/5)",
            type="aux_reservoir",
            bbox=[410.4, 403.2, 525.6, 446.4],
            fill_color="#292524",
            border_color="#b08a4e"
        ),
        DiagramElement(
            id="PRESS_CIRCUIT",
            label="Press Circuit",
            sublabel="Downstream Actuators",
            type="circuit",
            bbox=[230.4, 504.0, 374.4, 547.2],
            fill_color="#1e293b",
            border_color="#64748b"
        )
    ]

    legend = [
        {
            "color": "#8a4b9c",
            "type": "Solid Purple",
            "meaning": "Control/signal connections directly to PLC-03 (PS-04A transducer & IV-21 solenoid driver)"
        },
        {
            "color": "#555555",
            "type": "Solid Grey",
            "meaning": "Hydraulic fluid path (Suction, discharge, and press supply lines)"
        },
        {
            "color": "#b08a4e",
            "type": "Solid Tan",
            "meaning": "Reservoir interconnect line (Main Reservoir to Auxiliary Reservoir peak top-up)"
        }
    ]

    return DiagramResponse(
        drawing_id="AEG-DWG-H01",
        title="Aegis Series-7 HCS – Hydraulic Schematic",
        document_source="system_diagram_hydraulic.pdf",
        viewbox=[50.0, 160.0, 550.0, 580.0],
        elements=elements,
        connections=connections,
        legend=legend
    )

