"""
Dev 3: Tests for Validation Rules Engine
"""

import pytest
from src.ai_search.validation import RulesEngine, ValidationError


class TestRulesEngine:
    """Test validation rules engine"""

    def test_initialization(self):
        """Test engine initialization"""
        engine = RulesEngine()
        assert engine.rules is not None
        assert "code" in engine.rules
        assert "title" in engine.rules

    def test_validate_valid_standard(self):
        """Test validation of valid standard"""
        engine = RulesEngine()
        
        standard = {
            "code": "IS 1554",
            "title": "Fire-retardant copper wires",
            "definition": "This standard specifies requirements for fire-retardant copper wires",
            "year": 2018,
        }
        
        result = engine.validate_standard(standard)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert result.score > 0

    def test_validate_invalid_code(self):
        """Test validation with invalid standard code"""
        engine = RulesEngine()
        
        standard = {
            "code": "INVALID 123",  # Wrong format
            "title": "Fire-retardant copper wires",
            "definition": "This standard specifies requirements",
        }
        
        result = engine.validate_standard(standard)
        
        assert result.is_valid is False
        assert len(result.errors) > 0

    def test_validate_missing_required_field(self):
        """Test validation with missing required field"""
        engine = RulesEngine()
        
        standard = {
            "code": "IS 1554",
            # Missing title
            "definition": "This standard specifies requirements",
        }
        
        result = engine.validate_standard(standard)
        
        assert result.is_valid is False
        assert any(e.field == "title" for e in result.errors)

    def test_validate_short_title(self):
        """Test validation with title too short"""
        engine = RulesEngine()
        
        standard = {
            "code": "IS 1554",
            "title": "Short",  # Too short (< 10 chars)
            "definition": "This standard specifies requirements",
        }
        
        result = engine.validate_standard(standard)
        
        assert result.is_valid is False
        assert any(e.field == "title" for e in result.errors)

    def test_validate_with_year(self):
        """Test validation with year field"""
        engine = RulesEngine()
        
        standard = {
            "code": "IS 1554",
            "title": "Fire-retardant copper wires",
            "definition": "This standard specifies requirements",
            "year": 2018,
        }
        
        result = engine.validate_standard(standard)
        assert result.is_valid is True
        
        # Invalid year
        standard["year"] = 1900  # Too old
        result = engine.validate_standard(standard)
        assert result.is_valid is False

    def test_validate_qco_requirement(self):
        """Test validation of QCO requirement"""
        engine = RulesEngine()
        
        standard = {
            "code": "IS 1554",
            "title": "Fire-retardant copper wires",
            "definition": "This standard specifies requirements",
            "qco_required": True,
            # Missing qco_code
        }
        
        result = engine.validate_standard(standard)
        
        assert result.is_valid is False
        assert any("qco" in e.field.lower() for e in result.errors)

    def test_validate_isi_requirement(self):
        """Test validation of ISI mark requirement"""
        engine = RulesEngine()
        
        standard = {
            "code": "IS 1554",
            "title": "Fire-retardant copper wires",
            "definition": "This standard specifies requirements",
            "isi_required": True,
            # Missing isi_mark
        }
        
        result = engine.validate_standard(standard)
        
        assert result.is_valid is False
        assert any("isi" in e.field.lower() for e in result.errors)

    def test_get_validation_summary(self):
        """Test getting validation summary"""
        engine = RulesEngine()
        
        standard = {
            "code": "INVALID",
            "title": "Short",
        }
        
        result = engine.validate_standard(standard)
        summary = engine.get_validation_summary(result)
        
        assert "valid" in summary
        assert "score" in summary
        assert "error_count" in summary
        assert summary["valid"] is False

    def test_code_pattern_variations(self):
        """Test different valid code formats"""
        engine = RulesEngine()
        
        valid_codes = [
            "IS 1554",
            "IS1554",
            "IS 1554:2018",
            "IS1554:2018",
        ]
        
        for code in valid_codes:
            standard = {
                "code": code,
                "title": "Fire-retardant copper wires",
                "definition": "This standard specifies requirements",
            }
            result = engine.validate_standard(standard)
            assert result.is_valid is True, f"Code '{code}' should be valid"