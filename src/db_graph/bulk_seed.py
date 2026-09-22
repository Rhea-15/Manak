import csv
import hashlib
from datetime import date
from pathlib import Path

from src.backend.database import SessionLocal
from src.db_graph.models import DataSource, Standard, StandardVersion

DATA_FILE = Path(__file__).resolve().parent / "data" / "standards_import.csv"


REQUIRED_COLUMNS = {
    "standard_number",
    "title",
    "description",
    "status",
    "version_number",
    "effective_date",
    "source_name",
    "source_url",
    "authoritative",
}


ALLOWED_STATUS = {
    "active",
    "published",
    "superseded",
    "withdrawn",
    "draft",
}


def parse_date(value):
    if not value:
        return None

    value = value.strip()

    if not value:
        return None

    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def calculate_file_hash():
    sha256 = hashlib.sha256()

    with open(DATA_FILE, "rb") as file:
        for chunk in iter(lambda: file.read(8192), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def normalize_boolean(value):
    if value is None:
        return False

    value = str(value).strip().lower()

    return value in {
        "true",
        "1",
        "yes",
        "y",
        "authoritative",
    }


def read_csv():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"CSV file not found: {DATA_FILE}")

    with open(DATA_FILE, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError("CSV file does not contain a header.")

        missing_columns = REQUIRED_COLUMNS - set(reader.fieldnames)

        if missing_columns:
            raise ValueError(
                "Missing CSV columns: " + ", ".join(sorted(missing_columns))
            )

        rows = list(reader)

    return rows


def validate_rows(rows):
    errors = []

    seen_standard_numbers = set()

    for line_number, row in enumerate(rows, start=2):
        standard_number = (row.get("standard_number") or "").strip()

        title = (row.get("title") or "").strip()

        status = (row.get("status") or "").strip().lower()

        source_name = (row.get("source_name") or "").strip()

        source_url = (row.get("source_url") or "").strip()

        version_number = (row.get("version_number") or "").strip()

        effective_date = (row.get("effective_date") or "").strip()

        authoritative = normalize_boolean(row.get("authoritative"))

        if not standard_number:
            errors.append(f"Line {line_number}: standard_number is empty")

        if not title:
            errors.append(f"Line {line_number}: title is empty")

        if not status:
            errors.append(f"Line {line_number}: status is empty")
        elif status not in ALLOWED_STATUS:
            errors.append(f"Line {line_number}: invalid status '{status}'")

        if standard_number:
            if standard_number in seen_standard_numbers:
                errors.append(
                    f"Line {line_number}: duplicate standard_number "
                    f"'{standard_number}'"
                )

            seen_standard_numbers.add(standard_number)

        if source_name == "":
            errors.append(f"Line {line_number}: source_name is empty")

        if source_url == "":
            errors.append(f"Line {line_number}: source_url is empty")

        if effective_date and parse_date(effective_date) is None:
            errors.append(
                f"Line {line_number}: invalid effective_date '{effective_date}'"
            )

        if authoritative and not source_url:
            errors.append(
                f"Line {line_number}: authoritative source requires source_url"
            )

        if version_number:
            try:
                float(version_number)
            except ValueError:
                pass

    return errors


def get_existing_standard(db, standard_number):
    return (
        db.query(Standard).filter(Standard.standard_number == standard_number).first()
    )


def get_existing_source(db, source_name, source_url):
    return (
        db.query(DataSource)
        .filter(
            DataSource.source_name == source_name, DataSource.source_url == source_url
        )
        .first()
    )


def create_data_source(db, source_name, source_url, authoritative):
    source = get_existing_source(db, source_name, source_url)

    if source:
        return source

    source = DataSource(
        source_name=source_name,
        source_url=source_url,
        source_type="GOVERNMENT",
        is_authoritative=authoritative,
        source_hash=None,
    )

    db.add(source)
    db.flush()

    return source


def create_standard(db, row, source):
    standard_number = (row.get("standard_number") or "").strip()

    title = (row.get("title") or "").strip()

    description = (row.get("description") or "").strip()

    status = (row.get("status") or "").strip().lower()

    standard = Standard(
        standard_number=standard_number,
        title=title,
        description=description,
        status=status,
    )

    db.add(standard)
    db.flush()

    version_number = (row.get("version_number") or "").strip()

    effective_date_value = (row.get("effective_date") or "").strip()

    parsed_effective_date = parse_date(effective_date_value)

    if version_number:
        version = StandardVersion(
            standard_id=standard.id,
            version_number=version_number,
            effective_date=parsed_effective_date,
            status=status,
            source_id=source.id,
        )

        db.add(version)

    return standard


def seed_database():
    print("MANAK STANDARDS IMPORT")
    print("----------------------")

    rows = read_csv()

    print(f"Rows found: {len(rows)}")

    validation_errors = validate_rows(rows)

    if validation_errors:
        print(f"Validation errors: {len(validation_errors)}")

        for error in validation_errors:
            print(error)

        return False

    print("Validation passed.")

    file_hash = calculate_file_hash()

    db = SessionLocal()

    inserted_standards = 0
    skipped_standards = 0
    inserted_versions = 0
    inserted_sources = 0

    try:
        for row in rows:
            standard_number = (row.get("standard_number") or "").strip()

            source_name = (row.get("source_name") or "").strip()

            source_url = (row.get("source_url") or "").strip()

            authoritative = normalize_boolean(row.get("authoritative"))

            existing_standard = get_existing_standard(db, standard_number)

            if existing_standard:
                skipped_standards += 1
                continue

            existing_source = get_existing_source(db, source_name, source_url)

            if existing_source:
                source = existing_source
            else:
                source = create_data_source(
                    db, source_name, source_url, authoritative
                )
                inserted_sources += 1

            create_standard(db, row, source)

            inserted_standards += 1

            if row.get("version_number"):
                inserted_versions += 1

        db.commit()

        print(f"Inserted standards: {inserted_standards}")

        print(f"Inserted versions: {inserted_versions}")

        print(f"Inserted sources: {inserted_sources}")

        print(f"Skipped existing standards: {skipped_standards}")

        print(f"Source SHA-256: {file_hash}")

        print("Import completed successfully.")

        return True

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()