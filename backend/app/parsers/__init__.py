"""
Parsers Module Package
"""
from backend.app.parsers.base_parser import BaseParser, ExtractedDocument, DocumentBlock, TableBlock, TopologicalConnection, BlockType
from backend.app.parsers.pdf_parser import DigitalPdfParser
from backend.app.parsers.ocr_parser import ScanOcrParser
from backend.app.parsers.diagram_parser import DiagramParser
from backend.app.parsers.tabular_parser import TabularParser
from backend.app.parsers.office_parser import OfficeParser
from backend.app.parsers.html_parser import LegacyHtmlParser

__all__ = [
    "BaseParser",
    "ExtractedDocument",
    "DocumentBlock",
    "TableBlock",
    "TopologicalConnection",
    "BlockType",
    "DigitalPdfParser",
    "ScanOcrParser",
    "DiagramParser",
    "TabularParser",
    "OfficeParser",
    "LegacyHtmlParser"
]

