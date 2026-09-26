import os

from minio import Minio
from minio.error import S3Error


MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv(
    "MINIO_ACCESS_KEY",
    os.getenv("MINIO_ROOT_USER"),
)
MINIO_SECRET_KEY = os.getenv(
    "MINIO_SECRET_KEY",
    os.getenv("MINIO_ROOT_PASSWORD"),
)
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "manak-documents")
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"


def get_minio_client():
    if not MINIO_ACCESS_KEY or not MINIO_SECRET_KEY:
        raise RuntimeError("MinIO credentials are not configured")

    return Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=MINIO_SECURE,
    )


def ensure_bucket(client):
    if not client.bucket_exists(MINIO_BUCKET):
        client.make_bucket(MINIO_BUCKET)


def upload_file(
    object_name: str,
    file_path: str,
    content_type: str,
):
    client = get_minio_client()
    ensure_bucket(client)

    client.fput_object(
        MINIO_BUCKET,
        object_name,
        file_path,
        content_type=content_type,
    )

    return {
        "bucket": MINIO_BUCKET,
        "object_name": object_name,
    }


def delete_file(object_name: str):
    client = get_minio_client()

    try:
        client.remove_object(MINIO_BUCKET, object_name)
    except S3Error:
        raise