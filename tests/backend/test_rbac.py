from src.backend.rbac import check_permission


def test_admin_upload():
    assert check_permission("ADMIN", "/documents/upload", "POST")


def test_manager_upload():
    assert check_permission("MANAGER", "/documents/upload", "POST")


def test_executive_upload():
    assert check_permission("EXECUTIVE", "/documents/upload", "POST")


def test_admin_quality_score():
    assert check_permission("ADMIN", "/quality-score/1", "GET")


def test_manager_quality_score():
    assert check_permission("MANAGER", "/quality-score/1", "GET")


def test_executive_quality_score():
    assert check_permission("EXECUTIVE", "/quality-score/1", "GET")


def test_admin_compliance():
    assert check_permission("ADMIN", "/compliance/1", "GET")


def test_manager_compliance():
    assert check_permission("MANAGER", "/compliance/1", "GET")


def test_executive_compliance():
    assert check_permission("EXECUTIVE", "/compliance/1", "GET")


def test_admin_unified():
    assert check_permission("ADMIN", "/unified/standard/1", "GET")


def test_manager_unified():
    assert check_permission("MANAGER", "/unified/standard/1", "GET")


def test_executive_unified():
    assert check_permission("EXECUTIVE", "/unified/standard/1", "GET")


def test_unknown_role_denied():
    assert not check_permission("UNKNOWN", "/unified/standard/1", "GET")


def test_wrong_method_denied():
    assert not check_permission("MANAGER", "/quality-score/1", "POST")


def test_unknown_endpoint_denied():
    assert not check_permission("MANAGER", "/secret/internal", "GET")
