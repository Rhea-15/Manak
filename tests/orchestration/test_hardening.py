import time

from src.orchestration.services.search_service import run_with_timeout


def test_run_with_timeout_returns_fallback_on_timeout():
    """A slow callable returns the supplied fallback after the deadline."""
    def slow():
        """Take longer than the timeout before returning a value."""
        time.sleep(0.25)
        return {"done": True}

    result = run_with_timeout(slow, timeout_seconds=0.05, fallback={"status": "fallback"})

    assert result == {"status": "fallback"}


def test_run_with_timeout_returns_value_when_fast():
    """A callable that finishes before the deadline returns its value."""
    result = run_with_timeout(lambda: {"done": True}, timeout_seconds=0.5, fallback={"status": "fallback"})

    assert result == {"done": True}
