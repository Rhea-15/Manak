from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.backend.database import Base
from src.db_graph.models import DataSource, Standard, StandardVersion
from src.db_graph.version_diff import compare_versions
from src.db_graph.versioning import create_new_version, validate_standard_status


def _make_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    return Session()


def test_standard_version_tracks_data_source():
    assert "source_id" in StandardVersion.__table__.columns


def test_create_new_version_marks_previous_version_superseded():
    session = _make_session()
    standard = Standard(
        standard_number="IS 1234",
        title="Sample standard",
        status="active",
    )
    session.add(standard)
    session.commit()

    first = create_new_version(session, standard.id, "1.0", date(2024, 1, 1))
    second = create_new_version(session, standard.id, "2.0", date(2025, 1, 1))

    session.refresh(first)
    session.refresh(second)

    assert first.status == "superseded"
    assert second.status == "active"

    validation = validate_standard_status(session, standard.id)
    assert validation["status"] == "active"
    assert validation["active_version"] == "2.0"


def test_compare_versions_reports_source_changes():
    session = _make_session()
    source_old = DataSource(source_name="Old source", source_type="GOVERNMENT", source_url="https://old.example")
    source_new = DataSource(source_name="New source", source_type="GOVERNMENT", source_url="https://new.example")
    session.add_all([source_old, source_new])
    session.commit()

    standard = Standard(
        standard_number="IS 4321",
        title="Version comparison standard",
        status="active",
    )
    session.add(standard)
    session.commit()

    old_version = StandardVersion(
        standard_id=standard.id,
        source_id=source_old.id,
        version_number="1.0",
        effective_date=date(2024, 1, 1),
        status="active",
    )
    new_version = StandardVersion(
        standard_id=standard.id,
        source_id=source_new.id,
        version_number="2.0",
        effective_date=date(2025, 1, 1),
        status="active",
    )
    session.add_all([old_version, new_version])
    session.commit()

    diff = compare_versions(session, old_version.id, new_version.id)

    assert diff["differences"]["source_id"]["old"] == source_old.id
    assert diff["differences"]["source_id"]["new"] == source_new.id
