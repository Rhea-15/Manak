"""
Dev 3: Tests for IndicTrans2 Multilingual Support
"""

from src.ai_search.translation import (
    IndicTrans2Translator,
    TranslationPipeline,
)


class TestIndicTrans2Translator:
    """Test IndicTrans2 translator"""

    def test_initialization(self):
        """Test translator initialization"""
        translator = IndicTrans2Translator()
        assert translator.model_name is not None

    def test_mock_translate(self):
        """Test mock translation (when model not available)"""
        translator = IndicTrans2Translator()
        
        # In mock mode, should return text
        result = translator.translate("hello world", "eng_Latn")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_detect_language_english(self):
        """Test language detection for English"""
        translator = IndicTrans2Translator()
        
        lang = translator.detect_language("this is an english sentence")
        # Should detect as English or return None (depending on langdetect)
        assert lang is None or "eng" in lang.lower()

    def test_is_indian_language(self):
        """Test checking if text is in Indian language"""
        translator = IndicTrans2Translator()
        
        # English should return False
        assert translator.is_indian_language("hello world") is False

    def test_empty_text(self):
        """Test handling of empty text"""
        translator = IndicTrans2Translator()
        
        result = translator.translate("", "hin_Deva")
        assert result == ""
        
        lang = translator.detect_language("")
        assert lang is None


class TestTranslationPipeline:
    """Test translation pipeline"""

    def test_initialization(self):
        """Test pipeline initialization"""
        pipeline = TranslationPipeline()
        assert pipeline.translator is not None

    def test_normalize_english_query(self):
        """Test normalizing English query"""
        pipeline = TranslationPipeline()
        
        result = pipeline.normalize_query("fire retardant copper wire")
        
        assert result["original"] == "fire retardant copper wire"
        assert result["normalized"] == "fire retardant copper wire"
        assert result["is_translation"] is False

    def test_supported_languages(self):
        """Test getting supported languages"""
        pipeline = TranslationPipeline()
        
        langs = pipeline.supported_languages()
        
        assert isinstance(langs, list)
        assert len(langs) > 0
        assert "Hindi" in langs
        assert "Tamil" in langs

    def test_get_language_name(self):
        """Test getting friendly language name"""
        pipeline = TranslationPipeline()
        
        name = pipeline.get_language_name("hi")
        assert name == "Hindi"
        
        name = pipeline.get_language_name("ta")
        assert name == "Tamil"
        
        name = pipeline.get_language_name("xx")
        assert name is None

    def test_normalize_query_structure(self):
        """Test that normalized query has correct structure"""
        pipeline = TranslationPipeline()
        
        result = pipeline.normalize_query("test query")
        
        assert "original" in result
        assert "normalized" in result
        assert "language" in result
        assert "is_translation" in result
        assert isinstance(result["original"], str)
        assert isinstance(result["normalized"], str)
        assert isinstance(result["is_translation"], bool)

    def test_empty_query(self):
        """Test handling of empty query"""
        pipeline = TranslationPipeline()
        
        result = pipeline.normalize_query("")
        
        assert result["original"] == ""
        assert result["normalized"] == ""