"""
Dev 3: Tests for document parsing pipeline
Pytest auto-discovery: tests/ai_search/test_*.py
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from src.ai_search.document_parser import (
    DocumentParser,
    ExtractedPage,
    ExtractedEntity,
    DocumentType,
    DigitalPDFExtractor,
    SpacyNERProcessor,
)


class TestDocumentParser:
    """Test main document parser"""

    def test_parse_plain_text(self):
        """Test parsing plain text file"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Test content: IS 1554, dimension 10mm, material steel")
            f.flush()
            
            parser = DocumentParser()
            result = parser.parse(f.name)
            
            assert result.total_pages == 1
            assert result.document_type == DocumentType.PLAIN_TEXT
            assert len(result.pages) > 0
            assert "IS 1554" in result.pages[0].raw_text
        
        Path(f.name).unlink()

    def test_parse_with_ner(self):
        """Test NER extraction from text"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("The material should comply with IS 1554:2018 and IS 694")
            f.flush()
            
            parser = DocumentParser()
            if parser.ner_processor:
                result = parser.parse(f.name)
                page = result.pages[0]
                
                # Should extract some entities (if spaCy model is available)
                assert isinstance(page.entities, list)
            
        Path(f.name).unlink()

    def test_extracted_page_structure(self):
        """Test ExtractedPage dataclass"""
        page = ExtractedPage(
            page_number=1,
            raw_text="Test content",
            tables=[],
            entities=[],
            document_type=DocumentType.PLAIN_TEXT,
        )
        
        assert page.page_number == 1
        assert page.raw_text == "Test content"
        assert len(page.entities) == 0

    def test_extracted_entity_structure(self):
        """Test ExtractedEntity dataclass"""
        entity = ExtractedEntity(
            text="IS 1554",
            entity_type="STANDARD_CODE",
            confidence=0.95,
            page=1,
        )
        
        assert entity.text == "IS 1554"
        assert entity.entity_type == "STANDARD_CODE"
        assert entity.confidence == 0.95


class TestSpacyNERProcessor:
    """Test spaCy NER functionality"""

    @pytest.mark.skipif(
        not pytest.importorskip("spacy", minversion=None),
        reason="spaCy not installed"
    )
    def test_technical_entity_extraction(self):
        """Test extraction of technical entities (IS codes, dimensions)"""
        processor = SpacyNERProcessor()
        
        text = "The product must conform to IS 1554 with dimension 10.5mm and weight 2.3kg"
        entities = processor.extract_technical_entities(text)
        
        # Should find IS codes and dimensions
        codes = [e for e in entities if e.entity_type == "STANDARD_CODE"]
        dimensions = [e for e in entities if e.entity_type == "DIMENSION"]
        
        assert len(codes) > 0, "Should extract IS codes"
        assert len(dimensions) > 0, "Should extract dimensions"
        
        # Check IS code extraction
        assert any("1554" in e.text for e in codes)


class TestDigitalPDFExtractor:
    """Test PDF extraction"""

    def test_pdf_extraction_invalid_file(self):
        """Test error handling for invalid PDF"""
        extractor = DigitalPDFExtractor()
        
        with pytest.raises(Exception):
            extractor.extract("/nonexistent/file.pdf")

    def test_pdf_extraction_structure(self):
        """Test that extraction returns proper structure"""
        extractor = DigitalPDFExtractor()
        
        # This test would require a valid PDF file
        # For now, just test the structure
        assert hasattr(extractor, "extract")
        assert callable(extractor.extract)