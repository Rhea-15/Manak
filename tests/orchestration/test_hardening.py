import time

from src.orchestration.services.search_service import run_with_timeout


def test_run_with_timeout_returns_fallback_on_timeout():
    def slow():
        time.sleep(0.25)
        return {"done": True}

    result = run_with_timeout(slow, timeout_seconds=0.05, fallback={"status": "fallback"})

    assert result == {"status": "fallback"}


def test_run_with_timeout_returns_value_when_fast():
    result = run_with_timeout(lambda: {"done": True}, timeout_seconds=0.5, fallback={"status": "fallback"})

    assert result == {"done": True}
