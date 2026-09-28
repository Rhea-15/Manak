"""Live smoke test for the MANAK orchestration API.

Usage:
    python ping_endpoints.py                      # http://127.0.0.1:8001
    python ping_endpoints.py http://localhost:8000
    python ping_endpoints.py --strict             # DEGRADED also fails the run
    python ping_endpoints.py --wait=180           # allow a slow startup (default 90 s)

Each endpoint ends in one of three verdicts:
    PASS      200 OK, expected keys present, real (non-fallback) data.
    DEGRADED  The API answered correctly but a backing service (Qdrant,
              Postgres, Neo4j, Redis) is down, so it returned its designed
              fallback. This is an environment problem, not a code bug.
    FAIL      Wrong status, missing keys, timeout, or server unreachable.
              This is the one to fix.
"""

import json
import socket
import sys
import time
import urllib.error
import urllib.request
from urllib.parse import urlparse

ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
STRICT = "--strict" in sys.argv
WAIT_SECONDS = next((int(a.split("=", 1)[1]) for a in sys.argv if a.startswith("--wait=")), 90)
BASE_URL = ARGS[0] if ARGS else "http://127.0.0.1:8001"
# On Windows, "localhost" tries IPv6 first and each call pays ~2 s before falling
# back to IPv4, so the default is the literal IPv4 address.
TIMEOUT_SECONDS = 10

# Bypass any system/corporate proxy: a proxy answering for "localhost" shows up
# as a bogus 502/503 on every endpoint at once.
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))

DEPENDENCIES = [
    ("PostgreSQL", "127.0.0.1", 5432),
    ("Redis", "127.0.0.1", 6379),
    ("Qdrant", "127.0.0.1", 6333),
    ("Neo4j", "127.0.0.1", 7687),
]


def _search_degraded(body: dict) -> str | None:
    if body.get("status") == "fallback":
        return "search returned status=fallback (Qdrant/Postgres/embedding model not ready)"
    return None


def _recommendation_degraded(body: dict) -> str | None:
    if body.get("ai_suggested_spec") == "Verification required":
        return "recommendation fell back (no IS code matched, or Postgres has no such standard)"
    return None


ENDPOINTS = [
    {
        "name": "Health Check",
        "method": "GET",
        "path": "/health",
        "payload": None,
        "expected_keys": ["status"],
    },
    {
        "name": "Search API",
        "method": "POST",
        "path": "/api/v1/search",
        "payload": {"query": "fireproof wire", "language": "en", "top_k": 3},
        "expected_keys": ["query", "results", "vector_results_found", "source"],
        "degraded": _search_degraded,
    },
    {
        "name": "Recommendation API",
        "method": "POST",
        "path": "/api/v1/recommendation",
        # The IS pattern needs "IS <number>:<year>"; "IS 694" alone can never
        # reach the real lookup path, it always falls back.
        "payload": {
            "item_id": "item-1",
            "original_spec": "PVC Insulated Wires as per IS 694:2010",
        },
        "expected_keys": ["item_id", "original_spec", "ai_suggested_spec", "compliant", "source"],
        "degraded": _recommendation_degraded,
    },
    {
        "name": "Quality Score API",
        "method": "POST",
        "path": "/api/v1/score",
        "payload": {"tender_id": "TND/2026/0431"},
        "expected_keys": ["tender_id", "score", "verdict", "critical_alerts"],
    },
    {
        "name": "Graph API",
        "method": "GET",
        "path": "/api/v1/graph/IS%20694",
        "payload": None,
        "expected_keys": ["graph"],
        "degraded_status": (503, "graph_service_unavailable", "Neo4j unreachable or timed out"),
    },
]


def port_open(host: str, port: int) -> bool:
    """Return True if a TCP connection to host:port succeeds within 1.5 s."""
    try:
        with socket.create_connection((host, port), timeout=1.5):
            return True
    except OSError:
        return False


def call(case: dict) -> tuple[int | None, object, float, str | None]:
    """Perform one request. Returns (status, body, seconds, transport_error)."""
    data = json.dumps(case["payload"]).encode("utf-8") if case["payload"] else None
    request = urllib.request.Request(
        BASE_URL + case["path"],
        data=data,
        method=case["method"],
        headers={"Content-Type": "application/json"},
    )
    start = time.perf_counter()
    try:
        with OPENER.open(request, timeout=TIMEOUT_SECONDS) as response:
            status, raw = response.getcode(), response.read()
    except urllib.error.HTTPError as exc:  # 4xx/5xx still carry a useful body
        status, raw = exc.code, exc.read()
    except OSError as exc:  # refused, DNS, timeout
        return None, None, time.perf_counter() - start, str(exc)

    elapsed = time.perf_counter() - start
    try:
        body: object = json.loads(raw)
    except ValueError:
        body = raw.decode("utf-8", errors="replace")
    return status, body, elapsed, None


def judge(case: dict, status: int | None, body: object, error: str | None) -> tuple[str, str]:
    """Classify one response as PASS, DEGRADED or FAIL, with a reason."""
    if error is not None:
        return "FAIL", f"no response: {error}"

    degraded_status = case.get("degraded_status")
    if degraded_status and isinstance(body, dict):
        code, detail, reason = degraded_status
        if status == code and body.get("detail") == detail:
            return "DEGRADED", reason

    if status != 200:
        return "FAIL", f"HTTP {status}: {str(body)[:300]}"
    if not isinstance(body, dict):
        return "FAIL", f"200 but body is not a JSON object: {str(body)[:200]}"

    missing = [key for key in case["expected_keys"] if key not in body]
    if missing:
        return "FAIL", f"200 but missing keys {missing}; got keys {sorted(body)}"

    degraded = case.get("degraded")
    reason = degraded(body) if degraded else None
    if reason:
        return "DEGRADED", reason
    return "PASS", "200 OK, schema valid"


def wait_until_ready() -> bool:
    """Poll /health until the app answers; heavy ML imports can take a while at startup."""
    deadline = time.monotonic() + WAIT_SECONDS
    announced = False
    while time.monotonic() < deadline:
        request = urllib.request.Request(BASE_URL + "/health")
        try:
            with OPENER.open(request, timeout=3) as response:
                if response.getcode() == 200:
                    return True
        except OSError:
            pass
        if not announced:
            print(f"Port is open but /health is not answering yet; waiting up to {WAIT_SECONDS}s")
            print("(the server may still be importing torch/spaCy/PaddleOCR, or it crashed on")
            print(" import -- check the uvicorn window for 'Application startup complete.')\n")
            announced = True
        time.sleep(2)
    return False


def main() -> int:
    parsed = urlparse(BASE_URL)
    host, port = parsed.hostname or "127.0.0.1", parsed.port or 80
    print(f"MANAK API smoke test -> {BASE_URL}\n")

    if not port_open(host, port):
        print(f"[FAIL] Nothing is listening on {host}:{port}.")
        print("       Start the API from the repo root, with the venv active:")
        print("       uvicorn src.orchestration.main:app --port 8001 --reload")
        print("       (or pass the real port: python ping_endpoints.py http://localhost:8000)")
        return 1

    if not wait_until_ready():
        print(f"[FAIL] /health did not answer within {WAIT_SECONDS}s.")
        print("       The uvicorn process is holding the port but not serving requests.")
        print("       Read the uvicorn terminal for a traceback, or run:")
        print('       python -c "import src.orchestration.main"')
        return 1

    print("Backing services (TCP reachability only):")
    for name, dep_host, dep_port in DEPENDENCIES:
        state = "UP  " if port_open(dep_host, dep_port) else "DOWN"
        print(f"  {state} {name} ({dep_host}:{dep_port})")
    print()

    counts = {"PASS": 0, "DEGRADED": 0, "FAIL": 0}
    for case in ENDPOINTS:
        status, body, elapsed, error = call(case)
        verdict, reason = judge(case, status, body, error)
        counts[verdict] += 1
        print(f"[{verdict:<8}] {case['name']}  ({case['method']} {case['path']})  {elapsed:.2f}s")
        print(f"           {reason}\n")

    print(f"Summary: {counts['PASS']} pass, {counts['DEGRADED']} degraded, {counts['FAIL']} fail")
    if counts["FAIL"] or (STRICT and counts["DEGRADED"]):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())