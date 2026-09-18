"""
Dev 3: Document Parsing Module
Handles PDF, scanned PDFs, and BOQ extraction using PyMuPDF, PaddleOCR, and spaCy NER
"""

import logging
from typing import List, Dict, Tuple, Any
from pathlib import Path
import json
from dataclasses import dataclass, asdict
from enum import Enum

import fitz  # PyMuPDF
import cv2
import numpy as np
from PIL import Image
import io

try:
    from paddleocr import PaddleOCR
except ImportError:
    PaddleOCR = None

import spacy
from spacy.tokens import Doc

logger = logging.getLogger(__name__)


class DocumentType(Enum):
    """Enum for supported document types"""
    PDF_DIGITAL = "pdf_digital"
    PDF_SCANNED = "pdf_scanned"
    BOQ_EXCEL = "boq_excel"
    PLAIN_TEXT = "plain_text"
    IMAGE = "image"


@dataclass
class ExtractedEntity:
    """Single extracted entity from document"""
    text: str
    entity_type: str  # e.g., MATERIAL, DIMENSION, STANDARD_CODE
    confidence: float
    page: int
    bbox: Tuple[float, float, float, float] = None  # (x0, y0, x1, y1)


@dataclass
class ExtractedPage:
    """Page-level extraction result"""
    page_number: int
    raw_text: str
    tables: List[List[List[str]]]  # List of tables, each table is list of rows
    entities: List[ExtractedEntity]
    document_type: DocumentType
    layout_info: Dict[str, Any] = None


@dataclass
class DocumentExtractionResult:
    """Complete document extraction result"""
    file_path: str
    document_type: DocumentType
    pages: List[ExtractedPage]
    total_pages: int
    language_detected: str
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "file_path": self.file_path,
            "document_type": self.document_type.value,
            "total_pages": self.total_pages,
            "language_detected": self.language_detected,
            "pages": [
                {
                    "page_number": p.page_number,
                    "raw_text": p.raw_text[:500],  # Truncate for preview
                    "entity_count": len(p.entities),
                    "table_count": len(p.tables),
                    "entities": [asdict(e) for e in p.entities],
                }
                for p in self.pages
            ],
            "metadata": self.metadata,
        }


class DigitalPDFExtractor:
    """Extract text and layout from digital (non-scanned) PDFs"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def extract(self, pdf_path: str) -> List[ExtractedPage]:
        """Extract text and tables from digital PDF"""
        pages = []
        
        try:
            doc = fitz.open(pdf_path)
            
            for page_num, page in enumerate(doc):
                # Extract text with layout preservation
                text = page.get_text()
                
                # Extract tables (basic detection via text blocks)
                blocks = page.get_text("blocks")
                tables = self._detect_tables_from_blocks(blocks)
                
                # Extract images for potential OCR
                images = page.get_images()
                
                layout_info = {
                    "width": page.rect.width,
                    "height": page.rect.height,
                    "image_count": len(images),
                }
                
                extracted_page = ExtractedPage(
                    page_number=page_num + 1,
                    raw_text=text,
                    tables=tables,
                    entities=[],  # Will be populated by NER
                    document_type=DocumentType.PDF_DIGITAL,
                    layout_info=layout_info,
                )
                
                pages.append(extracted_page)
            
            doc.close()
            self.logger.info(f"Extracted {len(pages)} pages from {pdf_path}")
            
        except Exception as e:
            self.logger.error(f"Error extracting digital PDF: {e}")
            raise
        
        return pages

    def _detect_tables_from_blocks(self, blocks: List) -> List[List[List[str]]]:
        """Simple table detection from text blocks"""
        tables = []
        current_table = []
        
        for block in blocks:
            if block[6] == 1:  # Text block type
                # This is a simplified approach; full table detection is complex
                pass
        
        return tables


class ScannedPDFExtractor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ocr = None  # Lazy initialize instead

    def extract(self, pdf_path: str) -> List[ExtractedPage]:
        if PaddleOCR is None:
            self.logger.error("PaddleOCR not installed. Install with: pip install paddleocr")
            raise RuntimeError("PaddleOCR required for scanned PDF extraction")
        
        if self.ocr is None:  # Initialize only when needed
            self.ocr = PaddleOCR(use_angle_cls=True, lang="en")

    def extract(self, pdf_path: str) -> List[ExtractedPage]:
        """Extract text from scanned PDF using OCR"""
        if not self.ocr:
            self.logger.error("PaddleOCR not installed. Install with: pip install paddleocr")
            raise RuntimeError("PaddleOCR required for scanned PDF extraction")
        
        pages = []
        
        try:
            doc = fitz.open(pdf_path)
            
            for page_num, page in enumerate(doc):
                # Convert page to image
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better OCR
                img_data = pix.tobytes("ppm")
                img = Image.open(io.BytesIO(img_data))
                img_array = np.array(img)
                
                # Run OCR
                ocr_result = self.ocr.ocr(img_array, cls=True)
                
                # Parse OCR results
                text_lines = []
                detected_tables = []
                
                for line in ocr_result:
                    if line:
                        for word_info in line:
                            text_lines.append(word_info[1][0])  # Extract text
                
                full_text = " ".join(text_lines)
                
                extracted_page = ExtractedPage(
                    page_number=page_num + 1,
                    raw_text=full_text,
                    tables=detected_tables,
                    entities=[],  # Will be populated by NER
                    document_type=DocumentType.PDF_SCANNED,
                    layout_info={"ocr_confidence": 0.85},
                )
                
                pages.append(extracted_page)
            
            doc.close()
            self.logger.info(f"OCR extracted {len(pages)} pages from {pdf_path}")
            
        except Exception as e:
            self.logger.error(f"Error extracting scanned PDF: {e}")
            raise
        
        return pages


class BOQExtractor:
    """Extract Bill of Quantities from Excel or tabular formats"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def extract(self, file_path: str) -> List[ExtractedPage]:
        """Extract BOQ items from Excel file"""
        try:
            import pandas as pd
        except ImportError:
            self.logger.error("pandas required. Install with: pip install pandas openpyxl")
            raise
        
        pages = []
        
        try:
            excel_file = pd.ExcelFile(file_path)
            
            for page_number, sheet_name in enumerate(excel_file.sheet_names, start=1):
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                
                # Convert DataFrame to table format
                table = [
                    df.columns.tolist(),
                    *[[str(cell) for cell in row] for row in df.values.tolist()]
                ]
                
                extracted_page = ExtractedPage(
                    page_number=page_number,
                    raw_text=df.to_string(),
                    tables=[table],
                    entities=[],
                    document_type=DocumentType.BOQ_EXCEL,
                    layout_info={"sheet_name": sheet_name, "rows": len(df)},
                )
                
                pages.append(extracted_page)
            
            self.logger.info(f"Extracted {len(pages)} sheets from BOQ file")
            
        except Exception as e:
            self.logger.error(f"Error extracting BOQ: {e}")
            raise
        
        return pages


class SpacyNERProcessor:
    """Process text through spaCy NER for entity extraction"""

    def __init__(self, model_name: str = "en_core_web_sm"):
        self.logger = logging.getLogger(__name__)
        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            self.logger.error(
                f"spaCy model '{model_name}' not found. "
                f"Install with: python -m spacy download {model_name}"
            )
            raise

    def extract_entities(self, pages: List[ExtractedPage]) -> List[ExtractedPage]:
        """Extract NER entities from all pages"""
        for page in pages:
            doc = self.nlp(page.raw_text)
            
            entities = []
            for ent in doc.ents:
                entity = ExtractedEntity(
                    text=ent.text,
                    entity_type=ent.label_,
                    confidence=0.9,  # spaCy doesn't provide confidence
                    page=page.page_number,
                    bbox=None,
                )
                entities.append(entity)
            
            page.entities = entities
            self.logger.debug(f"Page {page.page_number}: extracted {len(entities)} entities")
        
        return pages

    def extract_technical_entities(self, text: str) -> List[ExtractedEntity]:
        """
        Extract custom technical entities (IS codes, dimensions, materials).
        This is a base implementation; can be extended with custom patterns.
        """
        import re
        
        entities = []
        
        # Pattern: IS XXXX or IS/IEC XXXXX
        is_pattern = r'\b(IS|IS/IEC|IS:)\s*(\d{4,5})\b'
        for match in re.finditer(is_pattern, text, re.IGNORECASE):
            entities.append(
                ExtractedEntity(
                    text=match.group(0),
                    entity_type="STANDARD_CODE",
                    confidence=0.95,
                    page=0,
                )
            )
        
        # Pattern: dimensions (e.g., 10mm, 5cm, 3.5kg)
        dimension_pattern = r'\b(\d+(?:\.\d+)?)\s*(mm|cm|m|kg|g|l|ml)\b'
        for match in re.finditer(dimension_pattern, text, re.IGNORECASE):
            entities.append(
                ExtractedEntity(
                    text=match.group(0),
                    entity_type="DIMENSION",
                    confidence=0.85,
                    page=0,
                )
            )
        
        return entities


class DocumentParser:
    """Main orchestrator for document parsing"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.digital_extractor = DigitalPDFExtractor()
        self.scanned_extractor = ScannedPDFExtractor()
        self.boq_extractor = BOQExtractor()
        
        try:
            self.ner_processor = SpacyNERProcessor()
        except OSError:
            self.logger.warning("spaCy model not available; NER disabled")
            self.ner_processor = None

    def parse(self, file_path: str, max_file_size_mb: int = 100) -> DocumentExtractionResult:
        """Main entry point: parse any supported document"""
        file_path = str(file_path)
        file_size_mb = Path(file_path).stat().st_size / (1024 * 1024)
        if file_size_mb > max_file_size_mb:
            raise ValueError(
                f"File size ({file_size_mb:.1f} MB) exceeds maximum ({max_file_size_mb} MB)"
            )
        suffix = Path(file_path).suffix.lower()
        
        self.logger.info(f"Starting parse: {file_path}")
        
        # Determine document type and extract
        if suffix == ".pdf":
            try:
                pages = self.digital_extractor.extract(file_path)
                # Check if extraction was meaningful
                if pages and any(p.raw_text.strip() for p in pages):
                    doc_type = DocumentType.PDF_DIGITAL
                else:
                    # Fall back to scanned PDF if digital extraction yielded no text
                    self.logger.warning("Digital PDF extraction returned no meaningful text, attempting OCR")
                    pages = self.scanned_extractor.extract(file_path)
                    doc_type = DocumentType.PDF_SCANNED
            except Exception as e:
                self.logger.warning(f"Digital extraction failed, trying OCR: {e}")
                pages = self.scanned_extractor.extract(file_path)
                doc_type = DocumentType.PDF_SCANNED
        
        elif suffix in [".xlsx", ".xls"]:
            pages = self.boq_extractor.extract(file_path)
            doc_type = DocumentType.BOQ_EXCEL
        
        elif suffix == ".txt":
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
            pages = [
                ExtractedPage(
                    page_number=1,
                    raw_text=text,
                    tables=[],
                    entities=[],
                    document_type=DocumentType.PLAIN_TEXT,
                )
            ]
            doc_type = DocumentType.PLAIN_TEXT
        
        else:
            raise ValueError(f"Unsupported file type: {suffix}")
        
        # Run NER & Technical Entity Extraction if available
        if self.ner_processor:
            pages = self.ner_processor.extract_entities(pages)
            for page in pages:
                technical_entities = self.ner_processor.extract_technical_entities(page.raw_text)
                for entity in technical_entities:
                    entity.page = page.page_number
                page.entities.extend(technical_entities)

        # Build result
        result = DocumentExtractionResult(
            file_path=file_path,
            document_type=doc_type,
            pages=pages,
            total_pages=len(pages),
            language_detected="en",
            metadata={
                "extraction_timestamp": str(Path(file_path).stat().st_mtime),
                "file_size_kb": Path(file_path).stat().st_size / 1024,
            },
        )
        
        self.logger.info(
            f"Parse complete: {len(pages)} pages, {sum(len(p.entities) for p in pages)} entities"
        )
        
        return result