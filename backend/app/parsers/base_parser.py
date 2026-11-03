"""
Base Parser Interface & Extracted Data Structures
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field

class BlockType(str, Enum):
    TEXT = "text"
    HEADING = "heading"
    TABLE = "table"
    LIST_ITEM = "list_item"
    WARNING = "warning"
    OCR_TEXT = "ocr_text"
    DIAGRAM_ELEMENT = "diagram_element"
    METADATA = "metadata"

class DocumentBlock(BaseModel):
    block_id: str
    block_type: BlockType
    text: str
    page_number: int = 1
    section_name: Optional[str] = None
    bbox: Optional[List[float]] = None  # [x0, y0, x1, y1]
    confidence: float = 1.0
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TableBlock(BaseModel):
    table_id: str
    headers: List[str]
    rows: List[List[Any]]
    page_number: int = 1
    caption: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TopologicalConnection(BaseModel):
    source_component: str
    target_component: str
    connection_type: str  # e.g., 'controls', 'senses', 'fluid_path', 'wires_to'
    line_color_rgb: Optional[List[float]] = None
    source_document: str
    page_number: int = 1
    confidence: float = 1.0
    notes: Optional[str] = None

class ExtractedDocument(BaseModel):
    filename: str
    file_type: str
    doc_id: str
    trust_tier: int
    revision: Optional[str] = None
    effective_date: Optional[str] = None
    blocks: List[DocumentBlock] = Field(default_factory=list)
    tables: List[TableBlock] = Field(default_factory=list)
    connections: List[TopologicalConnection] = Field(default_factory=list)
    raw_text: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)
    extraction_errors: List[str] = Field(default_factory=list)

class BaseParser(ABC):
    """Abstract Base Class for all document parsers."""
    
    @abstractmethod
    def parse(self, file_path: Path) -> ExtractedDocument:
        """Parse given file into standardized ExtractedDocument representation."""
        pass

