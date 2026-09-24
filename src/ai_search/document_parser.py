"""
Dev 3: Document Parsing Module
Handles PDF, scanned PDFs, and BOQ extraction using PyMuPDF, PaddleOCR, and spaCy NER
"""

import io
import logging
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any

import fitz  # PyMuPDF
import numpy as np
import spacy
from PIL import Image

from src.ai_search.config import settings

try:
    from paddleocr import PaddleOCR
except ImportError:
    PaddleOCR = None

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
    bbox: tuple[float, float, float, float] | None = None  # (x0, y0, x1, y1)


@dataclass
class ExtractedPage:
    """Page-level extraction result"""

    page_number: int
    raw_text: str
    tables: list[list[list[str]]]  # List of tables, each table is list of rows
    entities: list[ExtractedEntity]
    document_type: DocumentType
    layout_info: dict[str, Any] | None = None


@dataclass
class DocumentExtractionResult:
    """Complete document extraction result"""

    file_path: str
    document_type: DocumentType
    pages: list[ExtractedPage]
    total_pages: int
    language_detected: str
    metadata: dict[str, Any]

    def to_dict(self) -> dict:
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

    def extract(self, pdf_path: str) -> list[ExtractedPage]:
        """Extract text and tables from digital PDF"""
        pages = []

        try:
            doc = fitz.open(pdf_path)

            for page_num, page in enumerate(doc):
                text = page.get_text()

                blocks = page.get_text("blocks")
                tables = self._detect_tables_from_blocks(blocks)

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
                    entities=[],
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

    def _detect_tables_from_blocks(self, blocks: list) -> list[list[list[str]]]:
        """Simple table detection from text blocks (placeholder — full table
        detection is complex and not yet implemented)."""
        return []


class ScannedPDFExtractor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ocr = None  # Lazy initialize instead

    def extract(self, pdf_path: str) -> list[ExtractedPage]:
        if PaddleOCR is None:
            self.logger.error(
                "PaddleOCR not installed. Install with: pip install paddleocr"
            )
            raise RuntimeError("PaddleOCR required for scanned PDF extraction")

        if self.ocr is None:
            self.ocr = PaddleOCR(use_angle_cls=True, lang="en")

        pages = []

        try:
            doc = fitz.open(pdf_path)

            for page_num, page in enumerate(doc):
                pix = page.get_pixmap(
                    matrix=fitz.Matrix(2, 2)
                )  # 2x zoom for better OCR
                img_data = pix.tobytes("ppm")
                img_bytes = io.BytesIO(img_data)
                img = Image.open(img_bytes)
                img_array = np.array(img)

                img.close()
                img_bytes.close()

                ocr_result = self.ocr.ocr(img_array, cls=True)

                text_lines = []
                detected_tables = []

                if ocr_result and ocr_result[0]:
                    for line in ocr_result[0]:
                        if line and len(line) >= 2:
                            text_lines.append(line[1][0])

                full_text = " ".join(text_lines)

                extracted_page = ExtractedPage(
                    page_number=page_num + 1,
                    raw_text=full_text,
                    tables=detected_tables,
                    entities=[],
                    document_type=DocumentType.PDF_SCANNED,
                    layout_info={"ocr_confidence": 0.85},
                )

                pages.append(extracted_page)

            doc.close()
            self.logger.info(f"OCR extracted {len(pages)} pages from {pdf_path}")

        except Exception as e:
            self.logger.error("Error extracting scanned PDF: %s", e)
            raise

        return pages


class BOQExtractor:
    """Extract Bill of Quantities from Excel or tabular formats"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def extract(self, file_path: str) -> list[ExtractedPage]:
        """Extract BOQ items from Excel file"""
        try:
            import pandas as pd
        except ImportError:
            self.logger.error(
                "pandas required. Install with: pip install pandas openpyxl"
            )
            raise

        pages = []

        try:
            excel_file = pd.ExcelFile(file_path)

            for page_number, sheet_name in enumerate(excel_file.sheet_names, start=1):
                df = pd.read_excel(file_path, sheet_name=sheet_name)

                table = [
                    df.columns.tolist(),
                    *[[str(cell) for cell in row] for row in df.values.tolist()],
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

    def __init__(self, model_name: str = settings.spacy_model):
        """Load the configured spaCy model for entity extraction.

        Args:
            model_name: spaCy model to load; defaults to the configured SPACY_MODEL.

        Raises:
            OSError: If spaCy cannot load the model.
        """
        self.logger = logging.getLogger(__name__)
        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            self.logger.error(
                f"spaCy model '{model_name}' not found. "
                f"Install with: python -m spacy download {model_name}"
            )
            raise

    def extract_entities(self, pages: list[ExtractedPage]) -> list[ExtractedPage]:
        """Extract NER entities from all pages"""
        for page in pages:
            doc = self.nlp(page.raw_text)

            entities = []
            for ent in doc.ents:
                entity = ExtractedEntity(
                    text=ent.text,
                    entity_type=ent.label_,
                    confidence=0.9,
                    page=page.page_number,
                    bbox=None,
                )
                entities.append(entity)

            page.entities = entities
            self.logger.debug(
                f"Page {page.page_number}: extracted {len(entities)} entities"
            )

        return pages

    def extract_technical_entities(self, text: str) -> list[ExtractedEntity]:
        """
        Extract custom technical entities (IS codes, dimensions, materials).
        This is a base implementation; can be extended with custom patterns.
        """
        import re

        entities = []

        is_pattern = r"\b(IS|IS/IEC|IS:)\s*(\d{4,5})\b"
        for match in re.finditer(is_pattern, text, re.IGNORECASE):
            entities.append(
                ExtractedEntity(
                    text=match.group(0),
                    entity_type="STANDARD_CODE",
                    confidence=0.95,
                    page=0,
                )
            )

        dimension_pattern = r"\b(\d+(?:\.\d+)?)\s*(mm|cm|m|kg|g|l|ml)\b"
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

    def parse(
        self, file_path: str, max_file_size_mb: int = settings.max_upload_file_size_mb
    ) -> DocumentExtractionResult:
        """Extract pages from a PDF, Excel workbook, or UTF-8 text file.

        PDFs without extracted text and failed digital PDF reads are retried
        with OCR. Entities are added when the spaCy model loaded successfully.

        Args:
            file_path: Path to a .pdf, .xls, .xlsx, or .txt file.
            max_file_size_mb: Maximum size in MiB; files at the limit are
                accepted. Defaults to the configured MAX_UPLOAD_FILE_SIZE_MB.

        Returns:
            Pages and metadata for the document. The language_detected field
            is currently always "en".

        Raises:
            ValueError: If the file exceeds the limit or has an unsupported suffix.
            OSError: If the file cannot be accessed.
            RuntimeError: If OCR is needed but PaddleOCR is unavailable.
            ImportError: If an Excel parsing dependency is unavailable.

        OCR, Excel, and entity extraction errors otherwise propagate to callers.
        """
        file_path = str(file_path)
        file_size_mb = Path(file_path).stat().st_size / (1024 * 1024)
        if file_size_mb > max_file_size_mb:
            raise ValueError(
                f"File size ({file_size_mb:.1f} MB) exceeds maximum ({max_file_size_mb} MB)"
            )
        suffix = Path(file_path).suffix.lower()

        self.logger.info(f"Starting parse: {file_path}")

        if suffix == ".pdf":
            try:
                pages = self.digital_extractor.extract(file_path)
                if pages and any(p.raw_text.strip() for p in pages):
                    doc_type = DocumentType.PDF_DIGITAL
                else:
                    self.logger.warning(
                        "Digital PDF extraction returned no meaningful text, attempting OCR"
                    )
                    pages = self.scanned_extractor.extract(file_path)
                    doc_type = DocumentType.PDF_SCANNED
            except Exception as e:  # noqa: BLE001 — intentional: any extraction failure falls back to OCR
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

        if self.ner_processor:
            pages = self.ner_processor.extract_entities(pages)
            for page in pages:
                technical_entities = self.ner_processor.extract_technical_entities(
                    page.raw_text
                )
                for entity in technical_entities:
                    entity.page = page.page_number
                page.entities.extend(technical_entities)

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
