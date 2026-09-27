"""Tests for the Day 3 document ingestion feature.

Two layers are tested separately, matching the ownership split in the
Day 3 playbook:

  * ``TestIngestionServiceAdapter`` — unit tests for
    ``src/orchestration/services/ingestion.py``. ``DocumentParser`` (Dev
    3's code) is mocked here so these tests exercise only Dev 4's temp-file
    lifecycle, singleton caching, and payload shaping.

  * ``TestIngestEndpoint`` / ``TestRouteRegistration`` — tests for
    ``src/orchestration/routers/ingest.py`` via FastAPI's ``TestClient``.
    ``ingestion_service`` is mocked here so these tests exercise only the
    HTTP boundary: extension/size/empty guards, exception-to-status-code
    mapping, and response-schema shape. They do not require Dev 3's
    ``DocumentParser`` or PaddleOCR/pandas to be installed.

Run with: ``pytest tests/orchestration/test_ingest.py -v``
"""

import io
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

import src.orchestration.routers.ingest as ingest_router
import src.orchestration.services.ingestion as ingestion_module
from src.ai_search.config import settings
from src.orchestration.main import app
from src.orchestration.services.ingestion import SUPPORTED_SUFFIXES

client = TestClient(app)

ENDPOINT = "/api/v1/ingest"


# ---------------------------------------------------------------------------
# Shared fixtures / helpers
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _reset_parser_singleton():
    """Ensure the module-level DocumentParser cache doesn't leak across tests."""
    ingestion_module._parser = None
    yield
    ingestion_module._parser = None


def _sample_parsed_payload(document_type: str = "digital_pdf", total_pages: int = 1) -> dict:
    """A dict shaped like DocumentExtractionResult.to_dict(), plus took_ms.

    Mirrors what ``ingestion_service`` returns to the router: the parser's
    output merged with timing, still carrying ``file_path`` (which the
    router is responsible for stripping before it reaches the client).
    """
    return {
        "file_path": "/tmp/should-never-reach-the-client.pdf",
        "document_type": document_type,
        "total_pages": total_pages,
        "language_detected": "en",
        "pages": [
            {
                "page_number": 1,
                "raw_text": "Sample extracted text",
                "entity_count": 2,
                "table_count": 0,
                "entities": [
                    {
                        "text": "M25 concrete",
                        "entity_type": "MATERIAL",
                        "confidence": 0.91,
                        "page": 1,
                        "bbox": None,
                    },
                    {
                        "text": "500 sq.m",
                        "entity_type": "QUANTITY",
                        "confidence": 0.88,
                        "page": 1,
                        "bbox": None,
                    },
                ],
            }
        ],
        "metadata": {"source": "unit-test"},
        "took_ms": 42,
    }


def _upload(filename: str, content: bytes = b"dummy content", language: str | None = "en"):
    files = {"file": (filename, io.BytesIO(content), "application/octet-stream")}
    data = {"language": language} if language is not None else {}
    return client.post(ENDPOINT, files=files, data=data)


# ---------------------------------------------------------------------------
# Config sanity check — the 100MB decision (Section 7) is now confirmed
# ---------------------------------------------------------------------------


class TestMaxSizeConfig:
    def test_configured_max_upload_size_is_100mb(self):
        """Team decision: settings.max_upload_file_size_mb is the single
        authoritative limit (resolves the 50MB/25MB/100MB conflict)."""
        assert settings.max_upload_file_size_mb == 100


# ---------------------------------------------------------------------------
# Service adapter (services/ingestion.py) — DocumentParser mocked
# ---------------------------------------------------------------------------


class TestIngestionServiceAdapter:
    def _install_fake_parser(self, monkeypatch, *, to_dict_result=None, side_effect=None):
        fake_result = MagicMock()
        fake_result.to_dict.return_value = to_dict_result or {
            "file_path": "placeholder",
            "document_type": "digital_pdf",
            "total_pages": 1,
            "language_detected": "en",
            "pages": [],
            "metadata": {},
        }

        fake_parser_instance = MagicMock()
        if side_effect is not None:
            fake_parser_instance.parse.side_effect = side_effect
        else:
            fake_parser_instance.parse.return_value = fake_result

        fake_parser_cls = MagicMock(return_value=fake_parser_instance)
        monkeypatch.setattr(ingestion_module, "DocumentParser", fake_parser_cls)
        return fake_parser_cls, fake_parser_instance

    def test_returns_parser_payload_plus_took_ms(self, monkeypatch):
        fake_cls, fake_instance = self._install_fake_parser(monkeypatch)

        result = ingestion_module.ingest_document(b"%PDF-1.4 fake bytes", ".pdf", 100)

        assert result["document_type"] == "digital_pdf"
        assert result["total_pages"] == 1
        assert "took_ms" in result
        assert isinstance(result["took_ms"], int)
        assert result["took_ms"] >= 0
        fake_instance.parse.assert_called_once()

    def test_parser_constructed_once_and_reused(self, monkeypatch):
        """Singleton pattern: DocumentParser() should be instantiated at
        most once across multiple ingest_document() calls."""
        fake_cls, _ = self._install_fake_parser(monkeypatch)

        ingestion_module.ingest_document(b"a", ".txt", 100)
        ingestion_module.ingest_document(b"b", ".txt", 100)
        ingestion_module.ingest_document(b"c", ".txt", 100)

        fake_cls.assert_called_once()

    def test_temp_file_written_with_requested_suffix_and_parsed_by_path(self, monkeypatch):
        seen_paths = []

        def _capture_parse(path, max_file_size_mb):  # noqa: ANN001
            seen_paths.append(path)
            result = MagicMock()
            result.to_dict.return_value = {"document_type": "boq_excel"}
            return result

        fake_parser_instance = MagicMock()
        fake_parser_instance.parse.side_effect = _capture_parse
        monkeypatch.setattr(
            ingestion_module, "DocumentParser", MagicMock(return_value=fake_parser_instance)
        )

        ingestion_module.ingest_document(b"col_a,col_b", ".xlsx", 100)

        assert len(seen_paths) == 1
        assert seen_paths[0].endswith(".xlsx")

    def test_temp_file_cleaned_up_on_success(self, monkeypatch):
        captured_path: dict[str, Path] = {}

        def _capture_and_check(path, max_file_size_mb):  # noqa: ANN001
            p = Path(path)
            assert p.exists(), "temp file should exist while parse() runs"
            captured_path["path"] = p
            result = MagicMock()
            result.to_dict.return_value = {"document_type": "digital_pdf"}
            return result

        fake_parser_instance = MagicMock()
        fake_parser_instance.parse.side_effect = _capture_and_check
        monkeypatch.setattr(
            ingestion_module, "DocumentParser", MagicMock(return_value=fake_parser_instance)
        )

        ingestion_module.ingest_document(b"hello", ".txt", 100)

        assert not captured_path["path"].exists(), "temp file must be removed after parse()"

    @pytest.mark.parametrize(
        "exc",
        [
            ValueError("file exceeds max_file_size_mb"),
            OSError("cannot access file"),
            RuntimeError("PaddleOCR unavailable"),
            ImportError("pandas/openpyxl missing"),
        ],
    )
    def test_temp_file_cleaned_up_even_when_parse_raises(self, monkeypatch, exc):
        captured_path: dict[str, Path] = {}

        def _capture_and_raise(path, max_file_size_mb):  # noqa: ANN001
            captured_path["path"] = Path(path)
            raise exc

        fake_parser_instance = MagicMock()
        fake_parser_instance.parse.side_effect = _capture_and_raise
        monkeypatch.setattr(
            ingestion_module, "DocumentParser", MagicMock(return_value=fake_parser_instance)
        )

        with pytest.raises(type(exc)):
            ingestion_module.ingest_document(b"bad", ".pdf", 100)

        assert not captured_path["path"].exists(), (
            "temp file must be removed even when parse() raises"
        )

    def test_exceptions_from_parser_propagate_unwrapped(self, monkeypatch):
        """The service adapter must not swallow or re-wrap exceptions —
        that mapping is the router's job (Section 5)."""
        self._install_fake_parser(monkeypatch, side_effect=RuntimeError("PaddleOCR unavailable"))

        with pytest.raises(RuntimeError):
            ingestion_module.ingest_document(b"scan", ".pdf", 100)


# ---------------------------------------------------------------------------
# Router / HTTP boundary (routers/ingest.py) — ingestion_service mocked
# ---------------------------------------------------------------------------


class TestIngestEndpoint:
    # --- Happy paths -------------------------------------------------

    @pytest.mark.parametrize(
        "filename,document_type",
        [
            ("Tender_Draft_AIIMS_2026.pdf", "digital_pdf"),
            ("BOQ_estimate.xlsx", "boq_excel"),
            ("BOQ_estimate.xls", "boq_excel"),
            ("notes.txt", "text"),
        ],
    )
    def test_valid_upload_returns_200(self, monkeypatch, filename, document_type):
        mock_service = MagicMock(
            return_value=_sample_parsed_payload(document_type=document_type)
        )
        monkeypatch.setattr(ingest_router, "ingestion_service", mock_service)

        response = _upload(filename)

        assert response.status_code == 200
        body = response.json()
        assert body["document_type"] == document_type
        assert body["status"] == "parsed"
        assert body["filename"] == filename
        mock_service.assert_called_once()

    def test_scanned_pdf_upload_passes_through_document_type(self, monkeypatch):
        """Exercises the same HTTP boundary for the OCR-fallback path.
        Note: this mocks ingestion_service, so it does NOT require
        PaddleOCR to be installed — the real OCR fallback is covered by
        Dev 3's own test_document_parser.py, not this suite."""
        mock_service = MagicMock(
            return_value=_sample_parsed_payload(document_type="scanned_pdf")
        )
        monkeypatch.setattr(ingest_router, "ingestion_service", mock_service)

        response = _upload("scanned_tender.pdf")

        assert response.status_code == 200
        assert response.json()["document_type"] == "scanned_pdf"

    def test_response_schema_has_all_documented_fields(self, monkeypatch):
        mock_service = MagicMock(return_value=_sample_parsed_payload())
        monkeypatch.setattr(ingest_router, "ingestion_service", mock_service)

        response = _upload("tender.pdf")

        assert response.status_code == 200
        body = response.json()
        for field in (
            "upload_id",
            "filename",
            "document_type",
            "status",
            "total_pages",
            "language_detected",
            "pages",
            "metadata",
            "took_ms",
        ):
            assert field in body, f"missing documented field: {field}"

    def test_upload_id_is_generated_and_unique_per_request(self, monkeypatch):
        mock_service = MagicMock(return_value=_sample_parsed_payload())
        monkeypatch.setattr(ingest_router, "ingestion_service", mock_service)

        first = _upload("tender.pdf").json()["upload_id"]
        second = _upload("tender.pdf").json()["upload_id"]

        assert first != second

    def test_response_never_leaks_temp_file_path(self, monkeypatch):
        mock_service = MagicMock(return_value=_sample_parsed_payload())
        monkeypatch.setattr(ingest_router, "ingestion_service", mock_service)

        response = _upload("tender.pdf")

        assert "file_path" not in response.json()

    def test_filename_is_sanitized_to_basename(self, monkeypatch):
        """Guards against path traversal: only the basename should be
        echoed back, never any directory components the client sent."""
        mock_service = MagicMock(return_value=_sample_parsed_payload())
        monkeypatch.setattr(ingest_router, "ingestion_service", mock_service)

        files = {
            "file": (
                "../../etc/passwd.txt",
                io.BytesIO(b"irrelevant"),
                "text/plain",
            )
        }
        response = client.post(ENDPOINT, files=files, data={"language": "en"})

        assert response.status_code == 200
        assert response.json()["filename"] == "passwd.txt"

    def test_language_field_is_optional_and_defaults(self, monkeypatch):
        mock_service = MagicMock(return_value=_sample_parsed_payload())
        monkeypatch.setattr(ingest_router, "ingestion_service", mock_service)

        response = _upload("tender.pdf", language=None)

        assert response.status_code == 200

    # --- Client-error paths (validation before the parser is called) --

    def test_unsupported_file_type_returns_400(self, monkeypatch):
        mock_service = MagicMock()
        monkeypatch.setattr(ingest_router, "ingestion_service", mock_service)

        response = _upload("scan.png")

        assert response.status_code == 400
        assert "Unsupported file type" in response.json()["detail"]
        mock_service.assert_not_called()

    def test_empty_file_returns_400(self, monkeypatch):
        mock_service = MagicMock()
        monkeypatch.setattr(ingest_router, "ingestion_service", mock_service)

        response = _upload("empty.pdf", content=b"")

        assert response.status_code == 400
        assert "empty" in response.json()["detail"].lower()
        mock_service.assert_not_called()

    def test_oversized_file_returns_413(self, monkeypatch):
        mock_service = MagicMock()
        monkeypatch.setattr(ingest_router, "ingestion_service", mock_service)
        # Shrink the limit instead of building a real 100MB+ payload.
        monkeypatch.setattr(ingest_router, "_MAX_FILE_SIZE_BYTES", 10)

        response = _upload("tender.pdf", content=b"well over ten bytes of content")

        assert response.status_code == 413
        mock_service.assert_not_called()

    def test_missing_file_field_returns_422(self, monkeypatch):
        mock_service = MagicMock()
        monkeypatch.setattr(ingest_router, "ingestion_service", mock_service)

        response = client.post(ENDPOINT, data={"language": "en"})

        assert response.status_code == 422
        mock_service.assert_not_called()

    # --- Server-error paths: exception -> status-code mapping (Section 5) --

    @pytest.mark.parametrize(
        "exc,expected_status",
        [
            (ValueError("unsupported suffix"), 400),
            (OSError("cannot access temp file"), 500),
            (RuntimeError("PaddleOCR unavailable"), 500),
            (ImportError("pandas/openpyxl missing"), 500),
            (Exception("unexpected NER failure"), 500),
        ],
    )
    def test_parser_exceptions_map_to_documented_status_codes(
        self, monkeypatch, exc, expected_status
    ):
        mock_service = MagicMock(side_effect=exc)
        monkeypatch.setattr(ingest_router, "ingestion_service", mock_service)

        response = _upload("tender.pdf")

        assert response.status_code == expected_status
        if expected_status == 500:
            # No internal exception text/traceback leaked to the client.
            assert str(exc) not in response.text
            assert response.json()["detail"] == "ingestion_failed"

    def test_500_does_not_leak_internal_exception_details(self, monkeypatch):
        mock_service = MagicMock(side_effect=RuntimeError("PaddleOCR binary not found at /opt/x"))
        monkeypatch.setattr(ingest_router, "ingestion_service", mock_service)

        response = _upload("scanned.pdf")

        assert response.status_code == 500
        assert "/opt/x" not in response.text
        assert "PaddleOCR" not in response.text


# ---------------------------------------------------------------------------
# Wiring
# ---------------------------------------------------------------------------


class TestRouteRegistration:
    def test_ingest_route_registered_as_post(self):
        # app.routes' internal shape (flat APIRoute vs. a lazily-resolved
        # wrapper) varies across FastAPI versions, so check the OpenAPI
        # schema instead — it's the stable, version-independent contract
        # for "is this path+method actually being served".
        schema = app.openapi()
        assert ENDPOINT in schema["paths"], f"{ENDPOINT} not found in OpenAPI schema"
        assert "post" in schema["paths"][ENDPOINT], f"POST {ENDPOINT} not found in OpenAPI schema"

    def test_supported_suffixes_matches_contract(self):
        assert SUPPORTED_SUFFIXES == frozenset({".pdf", ".xlsx", ".xls", ".txt"})