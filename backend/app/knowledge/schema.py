"""
Intermediate Knowledge Representation (IKR) Schema
Pydantic models for Documents, Components, Facts, Relationships, Conflicts, and Provenance.
"""
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field

class VerificationStatus(str, Enum):
    VERIFIED = "VERIFIED"
    PARTIALLY_VERIFIED = "PARTIALLY VERIFIED"
    CONFLICTING = "CONFLICTING"
    NOT_FOUND = "NOT FOUND"
    EXTRACTION_FAILED = "EXTRACTION FAILED"

class ProvenanceRecord(BaseModel):
    source_document: str
    page_number: int = 1
    section_name: Optional[str] = None
    cell_or_bbox: Optional[str] = None  # e.g., 'Sheet: Components, Cell: D3' or '[187.2, 231.8, 230.4, 324.0]'
    extraction_method: str = "deterministic"  # 'deterministic', 'rapidocr_onnx', 'vector_geometry', 'openpyxl'
    confidence: float = 1.0

class DocumentEntity(BaseModel):
    document_id: str
    filename: str
    document_type: str
    source_category: str
    revision: Optional[str] = None
    publication_date: Optional[str] = None
    effective_date: Optional[str] = None
    trust_level: int = Field(..., description="1 (Master/ECN) to 6 (Noise)")
    is_active: bool = True
    is_archived: bool = False
    archived_at: Optional[str] = None
    archival_reason: Optional[str] = None
    sha256_hash: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ComponentEntity(BaseModel):
    component_id: str  # Canonical ID (e.g., 'PS-04A', 'IV-21', 'PLC-03')
    canonical_name: str
    aliases: List[str] = Field(default_factory=list)
    component_type: str  # 'sensor', 'valve', 'controller', 'reservoir', 'power_unit', 'electrical', 'alarm'
    description: Optional[str] = None
    location: Optional[str] = None
    status: str = "Active"  # 'Active', 'Superseded', 'Planned'
    source_references: List[str] = Field(default_factory=list)
    provenance: ProvenanceRecord

class FactEntity(BaseModel):
    fact_id: str
    subject: str  # Canonical Component ID or Topic
    predicate: str  # e.g., 'normal_operating_pressure', 'startup_required_state', 'alarm_threshold'
    object_value: str  # e.g., '200', 'OPEN', '150'
    unit: Optional[str] = None  # e.g., 'bar', 'seconds', 'V', 'mA'
    fact_type: str = "specified_setpoint"  # 'specified_setpoint', 'historical_setpoint', 'observed_measurement', 'rule', etc.
    applicable_revision_start: Optional[str] = None  # e.g., '3.2'
    applicable_revision_end: Optional[str] = None  # e.g., '3.2' or None (open-ended)
    is_current: bool = True  # Distinguishes current vs historical values
    is_archived: bool = False
    provenance: ProvenanceRecord
    verification_status: VerificationStatus = VerificationStatus.VERIFIED
    notes: Optional[str] = None

class RelationshipEntity(BaseModel):
    rel_id: str
    source_component: str
    relationship_type: str  # 'controls', 'senses', 'wires_to', 'supplies_fluid_to', 'interconnects', 'powers'
    target_component: str
    line_type: Optional[str] = None  # 'solid_purple', 'solid_grey', 'solid_tan', 'wiring_lead'
    endpoints: Optional[str] = None  # e.g., '(230.4, 231.8) -> (187.2, 324.0)'
    drawing_reference: Optional[str] = None  # e.g., 'AEG-DWG-H01'
    is_archived: bool = False
    provenance: ProvenanceRecord
    notes: Optional[str] = None

class ConflictResolutionType(str, Enum):
    RESOLVED_BY_REVISION = "RESOLVED_BY_REVISION"
    RESOLVED_BY_SOURCE_TRUST = "RESOLVED_BY_SOURCE_TRUST"
    MEASUREMENT_VS_SPECIFICATION = "MEASUREMENT_VS_SPECIFICATION"
    UNRESOLVED_DISCREPANCY = "UNRESOLVED_DISCREPANCY"

class ConflictEntity(BaseModel):
    conflict_id: str
    fact_1_id: str
    fact_2_id: str
    conflicting_parameter: str
    value_1: str
    value_2: str
    affected_revision: str
    resolution_status: ConflictResolutionType
    explanation: str
    source_1: str
    source_2: str

class IKRExport(BaseModel):
    export_version: str = "1.0"
    export_timestamp: str
    total_documents: int
    total_components: int
    total_facts: int
    total_relationships: int
    total_conflicts: int
    documents: List[DocumentEntity]
    components: List[ComponentEntity]
    facts: List[FactEntity]
    relationships: List[RelationshipEntity]
    conflicts: List[ConflictEntity]
