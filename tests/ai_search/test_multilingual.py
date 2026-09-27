"""
Dev 3 — Day 9: Multilingual Stress Testing
Stress-tests IndicTrans2Translator / TranslationPipeline against Hindi, Tamil,
and Marathi procurement-domain queries: language detection accuracy,
translation robustness, code-switched/edge-case input handling, and
config-driven generation parameters (no hardcoded max_length / num_beams).

Run: pytest tests/ai_search/test_multilingual.py -v
"""
import logging

import pytest

from src.ai_search.config import settings
from src.ai_search.translation import (
    SUPPORTED_LANGUAGES,
    IndicTrans2Translator,
    TranslationPipeline,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Domain-representative stress dataset: procurement / Indian Standards queries
# in Hindi, Tamil, and Marathi. Each entry maps to the ISO-639-1 family
# detect_language() is expected to resolve to (via its hi/ta/mr ->
# hin_Deva/tam_Taml/mar_Deva mapping).
# ---------------------------------------------------------------------------
MULTILINGUAL_DATASET: list[dict[str, str]] = [
    # Hindi
    {"lang": "hi", "expected_prefix": "hin", "text": "आईएस 1554 मानक क्या है"},
    {"lang": "hi", "expected_prefix": "hin", "text": "अग्निरोधी तांबे के तार की विशिष्टता बताइए"},
    {"lang": "hi", "expected_prefix": "hin", "text": "क्यूसीओ प्रमाणन अनिवार्य है या नहीं"},
    {"lang": "hi", "expected_prefix": "hin", "text": "बिजली की स्थापना के लिए सुरक्षा मानक"},
    # Tamil
    {"lang": "ta", "expected_prefix": "tam", "text": "தரநிலை IS 694 என்றால் என்ன"},
    {"lang": "ta", "expected_prefix": "tam", "text": "மின் கம்பியின் பாதுகாப்பு விவரக்குறிப்பு"},
    {"lang": "ta", "expected_prefix": "tam", "text": "ஐஎஸ்ஐ சான்றிதழ் தேவையா"},
    {"lang": "ta", "expected_prefix": "tam", "text": "குழாய் பொருட்களுக்கான தர சோதனை முறை"},
    # Marathi
    {"lang": "mr", "expected_prefix": "mar", "text": "आयएस १५५४ मानक म्हणजे काय"},
    {"lang": "mr", "expected_prefix": "mar", "text": "अग्निरोधक तांब्याच्या तारेची तपशील"},
    {"lang": "mr", "expected_prefix": "mar", "text": "क्यूसीओ प्रमाणपत्र सक्तीचे आहे का"},
    {"lang": "mr", "expected_prefix": "mar", "text": "विद्युत तपासणीसाठी सुरक्षा मानके"},
]

# langdetect is a statistical/heuristic detector, so short-query detection
# is never perfect. Stress-test at the dataset level with a minimum
# aggregate accuracy, so one ambiguous string doesn't fail the whole build.
MIN_DETECTION_ACCURACY = 0.6


def _detection_accuracy(translator: IndicTrans2Translator, dataset):
    """Run detect_language() over the dataset and return (accuracy, mismatches)."""
    mismatches = []
    correct = 0

    for sample in dataset:
        detected = translator.detect_language(sample["text"])
        if detected and detected.startswith(sample["expected_prefix"]):
            correct += 1
        else:
            mismatches.append({**sample, "detected": detected})

    accuracy = correct / len(dataset) if dataset else 0.0
    return accuracy, mismatches


@pytest.fixture(scope="module")
def translator():
    return IndicTrans2Translator()


@pytest.fixture(scope="module")
def pipeline():
    return TranslationPipeline()


class TestLanguageDetectionStress:
    """Language detection accuracy across Hindi, Tamil, Marathi."""

    def test_detection_accuracy_meets_threshold(self, translator):
        accuracy, mismatches = _detection_accuracy(translator, MULTILINGUAL_DATASET)
        if mismatches:
            logger.warning(
                "Language detection mismatches (%d/%d): %s",
                len(mismatches), len(MULTILINGUAL_DATASET), mismatches,
            )
        assert accuracy >= MIN_DETECTION_ACCURACY, (
            f"Detection accuracy {accuracy:.0%} below required "
            f"{MIN_DETECTION_ACCURACY:.0%} threshold. Mismatches: {mismatches}"
        )

    @pytest.mark.parametrize("lang_code", ["hi", "ta", "mr"])
    def test_per_language_accuracy_meets_threshold(self, translator, lang_code):
        subset = [s for s in MULTILINGUAL_DATASET if s["lang"] == lang_code]
        accuracy, mismatches = _detection_accuracy(translator, subset)
        assert accuracy >= MIN_DETECTION_ACCURACY, (
            f"{lang_code} detection accuracy {accuracy:.0%} below "
            f"{MIN_DETECTION_ACCURACY:.0%}. Mismatches: {mismatches}"
        )

    @pytest.mark.parametrize("sample", MULTILINGUAL_DATASET, ids=lambda s: s["text"][:20])
    def test_is_indian_language_returns_bool(self, translator, sample):
        result = translator.is_indian_language(sample["text"])
        assert isinstance(result, bool)


class TestTranslationRobustnessStress:
    """translate() must not crash and must return a usable string for every sample."""

    @pytest.mark.parametrize("sample", MULTILINGUAL_DATASET, ids=lambda s: s["text"][:20])
    def test_translate_returns_nonempty_string(self, translator, sample):
        detected = translator.detect_language(sample["text"]) or f"{sample['expected_prefix']}_Deva"
        result = translator.translate(sample["text"], source_lang=detected)
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.parametrize("sample", MULTILINGUAL_DATASET, ids=lambda s: s["text"][:20])
    def test_translate_is_deterministic(self, translator, sample):
        """Same input translated twice should give the same output (regression guard)."""
        first = translator.translate(sample["text"], source_lang="hin_Deva")
        second = translator.translate(sample["text"], source_lang="hin_Deva")
        assert first == second

    def test_code_switched_hindi_english_query(self, translator):
        """Common real-world procurement search pattern: mixed script query."""
        text = "IS 1554 का cable specification क्या है"
        result = translator.translate(text, source_lang="hin_Deva")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_standard_code_heavy_query(self, translator):
        text = "आईएस 1554:2018 आवश्यकताएँ"
        result = translator.translate(text, source_lang="hin_Deva")
        assert isinstance(result, str)

    def test_long_paragraph_near_max_length(self, translator):
        """A paragraph long enough to approach settings.translation_max_length
        should still translate without raising."""
        long_text = ("अग्निरोधी तांबे के तार की सुरक्षा विशिष्टता " * 30).strip()
        result = translator.translate(long_text, source_lang="hin_Deva")
        assert isinstance(result, str)

    def test_whitespace_only_text(self, translator):
        result = translator.translate("   \n\t  ", source_lang="hin_Deva")
        assert result == ""

    def test_empty_text(self, translator):
        result = translator.translate("", source_lang="hin_Deva")
        assert result == ""

    def test_special_characters_and_numbers(self, translator):
        text = "IS-1554/2018 §४.२ — विद्युत तार (₹500/मीटर)"
        result = translator.translate(text, source_lang="hin_Deva")
        assert isinstance(result, str)
        assert len(result) > 0


class TestNormalizeQueryPipelineStress:
    """End-to-end normalize_query() across all three languages."""

    @pytest.mark.parametrize("sample", MULTILINGUAL_DATASET, ids=lambda s: s["text"][:20])
    def test_normalize_query_structure(self, pipeline, sample):
        result = pipeline.normalize_query(sample["text"])
        assert set(result.keys()) == {"original", "normalized", "language", "is_translation"}
        assert result["original"] == sample["text"]
        assert isinstance(result["normalized"], str)
        assert isinstance(result["is_translation"], bool)

    def test_normalize_english_query_not_translated(self, pipeline):
        result = pipeline.normalize_query("fire retardant copper wire specification")
        assert result["is_translation"] is False
        assert result["normalized"] == result["original"]

    def test_supported_languages_cover_dataset(self, pipeline):
        names = pipeline.supported_languages()
        expected = {SUPPORTED_LANGUAGES[s["lang"]] for s in MULTILINGUAL_DATASET}
        assert expected.issubset(set(names))


class TestGenerationConfigNoHardcoding:
    """Day 9 rectification: max_length / num_beams must come from settings,
    not literals baked into translate(), so tuning doesn't require a
    code-edit-restart cycle mid-hackathon."""

    def test_settings_expose_generation_params(self):
        assert hasattr(settings, "translation_max_length")
        assert hasattr(settings, "translation_num_beams")
        assert settings.translation_max_length > 0
        assert settings.translation_num_beams > 0

    def test_generate_called_with_configured_params(self, monkeypatch):
        """Force the real-model branch with stub tokenizer/model and assert
        generate() receives settings-driven max_length/num_beams."""
        import contextlib
        import sys
        import types

        translator = IndicTrans2Translator()
        captured = {}

        class _StubTensor:
            def to(self, *_args, **_kwargs):
                return self

        class _StubTokenizer:
            def __call__(self, *_args, **_kwargs):
                return {"input_ids": _StubTensor()}

            def batch_decode(self, _ids, **_kwargs):
                return ["stub translation"]

        class _StubModel:
            def generate(self, **kwargs):
                captured.update(kwargs)
                return ["stub-ids"]

        class _StubProcessor:
            def __init__(self, *_args, **_kwargs):
                pass

            def preprocess_batch(self, texts, **_kwargs):
                return texts

            def postprocess_batch(self, texts, **_kwargs):
                return texts

        translator.tokenizer = _StubTokenizer()
        translator.model = _StubModel()

        # Capture initial values before mutation
        previous_max_length = settings.translation_max_length
        previous_num_beams = settings.translation_num_beams

        # Patch settings imported in translation module using object.__setattr__
        # to bypass the dataclass frozen restriction
        object.__setattr__(settings, "translation_max_length", 128)
        object.__setattr__(settings, "translation_num_beams", 2)

        try:
            stub_pkg = types.ModuleType("IndicTransToolkit")
            stub_module = types.ModuleType("IndicTransToolkit.processor")
            stub_module.IndicProcessor = _StubProcessor
            monkeypatch.setitem(sys.modules, "IndicTransToolkit", stub_pkg)
            monkeypatch.setitem(sys.modules, "IndicTransToolkit.processor", stub_module)

            stub_torch = types.ModuleType("torch")
            stub_torch.no_grad = contextlib.contextmanager(lambda: iter([None]))
            monkeypatch.setitem(sys.modules, "torch", stub_torch)

            translator.translate("आईएस 1554 मानक", source_lang="hin_Deva")

            assert captured.get("max_length") == 128
            assert captured.get("num_beams") == 2
        finally:
            # Restore original values captured before the test run
            object.__setattr__(settings, "translation_max_length", previous_max_length)
            object.__setattr__(settings, "translation_num_beams", previous_num_beams)
    def test_rejects_nonpositive_max_length(self):
        import os

        from src.ai_search.config import AISearchSettings

        os.environ["TRANSLATION_MAX_LENGTH"] = "0"
        try:
            with pytest.raises(ValueError, match="TRANSLATION_MAX_LENGTH"):
                AISearchSettings()
        finally:
            del os.environ["TRANSLATION_MAX_LENGTH"]

    def test_rejects_negative_num_beams(self):
        import os

        from src.ai_search.config import AISearchSettings

        os.environ["TRANSLATION_NUM_BEAMS"] = "-1"
        try:
            with pytest.raises(ValueError, match="TRANSLATION_NUM_BEAMS"):
                AISearchSettings()
        finally:
            del os.environ["TRANSLATION_NUM_BEAMS"]