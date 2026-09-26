import logging
import os
import tempfile
import uuid
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from src.ai_search.document_parser import DocumentParser
from src.backend.database import get_db
from src.backend.rbac import require_role
from src.backend.storage import delete_file, upload_file
from src.db_graph.models import TenderDocument

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["Documents"])

MAX_FILE_SIZE = 25 * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".csv", ".txt"}
PARSER_SUPPORTED_EXTENSIONS = {".pdf", ".txt"}
CONTENT_TYPES = {
    ".pdf": "application/pdf",
    ".docx": (
        "application/vnd.openxmlformats-officedocument."
        "wordprocessingml.document"
    ),
    ".csv": "text/csv",
    ".txt": "text/plain",
}


@router.post("/upload", status_code=201)
async def upload_document(
    file: Annotated[UploadFile, File(...)],
    current_role: Annotated[str, Depends(require_role("EXECUTIVE"))],
    db: Annotated[Session, Depends(get_db)],
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    original_name = Path(file.filename).name
    extension = Path(original_name).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail="Supported formats are PDF, DOCX, CSV and TXT",
        )

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File size must not exceed 25 MB",
        )
    if extension == ".pdf" and not contents.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is not a valid PDF",
        )

    document_id = str(uuid.uuid4())
    object_name = f"tenders/{document_id}/{original_name}"
    content_type = CONTENT_TYPES[extension]
    temp_path = None
    storage_result = None
    extracted_data = None
    parse_status = "not_supported"

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as temp_file:
            temp_file.write(contents)
            temp_path = temp_file.name

        storage_result = await run_in_threadpool(
            upload_file, object_name, temp_path, content_type
        )

        if extension in PARSER_SUPPORTED_EXTENSIONS:
            try:
                parser = DocumentParser()
                parse_result = await run_in_threadpool(parser.parse, temp_path)
                extracted_data = parse_result.to_dict()
                parse_status = "completed"
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "Failed to parse document %s: %s",
                    object_name,
                    exc,
                    exc_info=True,
                )
                parse_status = "failed"

        document_record = TenderDocument(
            document_id=document_id,
            filename=original_name,
            object_name=storage_result["object_name"],
            bucket=storage_result["bucket"],
            content_type=content_type,
            size_bytes=len(contents),
            uploaded_by_role=current_role,
            parse_status=parse_status,
        )
        db.add(document_record)
        db.commit()
        db.refresh(document_record)

        return {
            "document_id": document_record.document_id,
            "filename": document_record.filename,
            "size_bytes": document_record.size_bytes,
            "content_type": document_record.content_type,
            "uploaded_by_role": document_record.uploaded_by_role,
            "storage": {
                "bucket": document_record.bucket,
                "object_name": document_record.object_name,
            },
            "parse_status": document_record.parse_status,
            "extracted_data": extracted_data,
            "created_at": document_record.created_at,
        }
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        if storage_result:
            try:
                await run_in_threadpool(delete_file, storage_result["object_name"])
            except Exception as cleanup_exc:  # noqa: BLE001
                logger.warning(
                    "Failed to delete orphaned object %s: %s",
                    storage_result["object_name"],
                    cleanup_exc,
                    exc_info=True,
                )
        raise HTTPException(
            status_code=500,
            detail="Failed to upload document or save metadata",
        ) from exc
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
        await file.close()


@router.get("")
def list_documents(
    current_role: Annotated[str, Depends(require_role("EXECUTIVE"))],
    db: Annotated[Session, Depends(get_db)],
):
    documents = (
        db.query(TenderDocument)
        .order_by(TenderDocument.created_at.desc())
        .all()
    )
    return {
        "total": len(documents),
        "documents": [
            {
                "document_id": document.document_id,
                "filename": document.filename,
                "object_name": document.object_name,
                "bucket": document.bucket,
                "content_type": document.content_type,
                "size_bytes": document.size_bytes,
                "uploaded_by_role": document.uploaded_by_role,
                "parse_status": document.parse_status,
                "created_at": document.created_at,
            }
            for document in documents
        ],
    }
