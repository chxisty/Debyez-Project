"""
API Request and Response Models
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

from backend.app.answer_generation.schema import GroundedAnswer

class ChatRequest(BaseModel):
    query: str = Field(..., description="Technical engineering question", min_length=2)
    target_revision: Optional[str] = Field(None, description="Requested software revision context (e.g. '3.0', '3.2', 'Current')")
    force_offline: bool = Field(False, description="Whether to bypass external LLM and use deterministic offline generator")

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    database: Dict[str, Any]
    retrieval_engine: Dict[str, Any]
    llm_status: Dict[str, Any]

class DocumentListItem(BaseModel):
    document_id: str
    filename: str
    title: str
    system: str
    document_type: str
    revision: str
    trust_tier: int
    sha256_hash: str
    is_archived: bool
    archival_reason: Optional[str]
    chunk_count: int

class ComponentDetailResponse(BaseModel):
    component_id: str
    canonical_name: str
    component_type: Optional[str]
    description: Optional[str]
    aliases: List[str]
    location: Optional[str]
    status: str
    facts: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    conflicts: List[Dict[str, Any]]

class RevisionItem(BaseModel):
    software_revision: str
    effective_date: str
    operating_pressure_bar: int
    active_pressure_sensor: str
    governing_ecn: Optional[str]
    summary_of_changes: str
    status: str

class DiagramElement(BaseModel):
    id: str
    label: str
    sublabel: Optional[str] = None
    type: str
    bbox: List[float]
    fill_color: str
    border_color: str

class DiagramConnection(BaseModel):
    rel_id: str
    source: str
    target: str
    connection_type: str
    line_type: str
    color: str
    endpoints: str
    description: str

class DiagramResponse(BaseModel):
    drawing_id: str
    title: str
    document_source: str
    viewbox: List[float]
    elements: List[DiagramElement]
    connections: List[DiagramConnection]
    legend: List[Dict[str, str]]

