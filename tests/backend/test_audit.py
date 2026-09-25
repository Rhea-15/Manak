from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.backend.audit import create_audit_log, get_audit_logs
from src.backend.database import Base


def _make_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


def test_get_audit_logs_returns_entries():
    session = _make_session()

    entry = create_audit_log(
        user_id="admin",
        endpoint="/audit/logs",
        action="GET_LOGS",
        details="Audit fetch",
        db=session,
    )

    logs = get_audit_logs(session)

    assert len(logs) == 1
    assert logs[0].id == entry.id
    assert logs[0].endpoint == "/audit/logs"
