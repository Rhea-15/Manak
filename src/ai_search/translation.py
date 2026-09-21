"""
Dev 3: IndicTrans2 Multilingual Translation
Supports translating regional Indian language queries to English
"""

import logging

logger = logging.getLogger(__name__)

# Supported languages
SUPPORTED_LANGUAGES = {
    "hi": "Hindi",
    "ta": "Tamil",
    "te": "Telugu",
    "kn": "Kannada",
    "ml": "Malayalam",
    "mr": "Marathi",
    "gu": "Gujarati",
    "bn": "Bengali",
}


class IndicTrans2Translator:
    """Wrapper around IndicTrans2 model for Indian language translation"""

    def __init__(self, model_name: str = "ai4bharat/indic-trans-v2-all-gpu"):
        """
        Initialize IndicTrans2 model.
        
        Args:
            model_name: HuggingFace model name (IndicTrans2 variants)
        """
        self.logger = logging.getLogger(__name__)
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        
        try:
            from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            self.logger.info(f"Loaded IndicTrans2 model: {model_name}")
        except (ImportError, OSError) as e:
            self.logger.warning(f"Could not load IndicTrans2: {e}")
            self.logger.warning("Running in mock mode for testing")
            self.model = None

    def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str = "eng_Latn",
    ) -> str:
        """
        Translate text between languages.
        
        Args:
            text: Text to translate
            source_lang: Source language code (e.g., 'hin_Deva' for Hindi)
            target_lang: Target language code (default: 'eng_Latn' for English)
        
        Returns:
            Translated text
        """
        if not text or not text.strip():
            return ""
        
        if self.model is None:
            # Mock mode for testing
            return self._mock_translate(text)
        
        try:
            import torch
            from IndicTransToolkit.processor import IndicProcessor

            processor = IndicProcessor(inference=True)
            input_batch = processor.preprocess_batch(
                [text],
                src_lang=source_lang,
                tgt_lang=target_lang,
            )
            
            # Tokenize
            inputs = self.tokenizer(
                input_batch,
                truncation=True,
                padding="longest",
                return_tensors="pt",
                return_attention_mask=True,
            )
            
            # Generate translation
            with torch.no_grad():
                generated_ids = self.model.generate(
                    **inputs,
                    max_length=512,
                    num_beams=4,
                )
            
            # Decode
            translated = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)
            return translated[0]
        
        except (ImportError, RuntimeError, ValueError, KeyError) as e:
            self.logger.error(f"Translation error: {e}")
            return text  # Return original on error

    def _mock_translate(self, text: str) -> str:
        """
        Generate deterministic mock translation for testing.
        Used when model not available (Windows compatibility).
        """
        # Mock: return text as-is with indicator
        return text

    def detect_language(self, text: str) -> str | None:
        """
        Detect language of input text.
        
        Args:
            text: Text to detect language for
        
        Returns:
            Language code (e.g., 'hin_Deva') or None
        """
        if not text:
            return None
        
        try:
            from langdetect import LangDetectException, detect
        except ImportError as e:
            self.logger.debug(f"langdetect not available: {e}")
            return None

        try:
            lang_code = detect(text)
            
            # Map to IndicTrans2 format
            lang_mapping = {
                "hi": "hin_Deva",
                "ta": "tam_Tamil",
                "te": "tel_Telu",
                "kn": "kan_Knda",
                "ml": "mal_Mlym",
                "mr": "mar_Deva",
                "gu": "guj_Gujr",
                "bn": "ben_Beng",
            }
            
            return lang_mapping.get(lang_code)
        
        except LangDetectException as e:
            self.logger.debug(f"Language detection failed: {e}")
            return None

    def is_indian_language(self, text: str) -> bool:
        """Check if text is in an Indian language"""
        detected = self.detect_language(text)
        if detected:
            mapped_indic_codes = {
                "hin", "tam", "tel", "kan", 
                "mal", "mar", "guj", "ben"
            }
            return detected.split("_")[0] in mapped_indic_codes
        return False


class TranslationPipeline:
    """Orchestrate translation for search queries"""

    def __init__(self):
        """Initialize translation pipeline"""
        self.logger = logging.getLogger(__name__)
        self.translator = IndicTrans2Translator()

    def normalize_query(self, query: str) -> dict[str, str | bool]:
        """
        Normalize query by detecting language and translating if needed.
        
        Args:
            query: User query (may be in Indian language)
        
        Returns:
            {
                "original": original query,
                "normalized": English version,
                "language": detected language,
                "is_translation": whether translation occurred
            }
        """
        lang = self.translator.detect_language(query)
        
        if lang and lang != "eng_Latn":
            # Translate to English
            translated = self.translator.translate(
                query,
                source_lang=lang,
                target_lang="eng_Latn"
            )
            return {
                "original": query,
                "normalized": translated,
                "language": lang,
                "is_translation": True,
            }
        else:
            # Already English or couldn't detect
            return {
                "original": query,
                "normalized": query,
                "language": "eng_Latn",
                "is_translation": False,
            }

    def supported_languages(self) -> list[str]:
        """Get list of supported languages"""
        return list(SUPPORTED_LANGUAGES.values())

    def get_language_name(self, lang_code: str) -> str | None:
        """Get friendly name for language code"""
        return SUPPORTED_LANGUAGES.get(lang_code)