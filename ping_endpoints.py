import urllib.request
import urllib.error
import json
import sys

BASE_URL = "http://localhost:8001"

# Define the endpoints and payloads based on your orchestration schemas
ENDPOINTS_TO_TEST = [
    {
        "name": "Health Check",
        "method": "GET",
        "url": f"{BASE_URL}/health",
        "payload": None,
        "expected_keys": ["status"]
    },
    {
        "name": "Search API",
        "method": "POST",
        "url": f"{BASE_URL}/api/v1/search",
        "payload": {"query": "fireproof wire", "language": "en", "top_k": 3},
        "expected_keys": ["query", "results", "vector_results_found", "source"]
    },
    {
        "name": "Recommendation API",
        "method": "POST",
        "url": f"{BASE_URL}/api/v1/recommendation",
        "payload": {"item_id": "item-1", "original_spec": "PVC Insulated Wires as per IS 694"},
        "expected_keys": ["item_id", "original_spec", "ai_suggested_spec", "compliant", "source"]
    },
    {
        "name": "Quality Score API",
        "method": "POST",
        "url": f"{BASE_URL}/api/v1/score",
        "payload": {"tender_id": "TND/2026/0431"},
        "expected_keys": ["tender_id", "score", "verdict", "critical_alerts"]
    },
    {
        "name": "Graph API (Day 5)",
        "method": "GET",
        "url": f"{BASE_URL}/api/v1/graph/IS%20694",
        "payload": None,
        "expected_keys": ["graph"]
    }
]

def ping_endpoint(test_case):
    req = urllib.request.Request(test_case["url"], method=test_case["method"])
    req.add_header('Content-Type', 'application/json')
    
    data = None
    if test_case["payload"]:
        data = json.dumps(test_case["payload"]).encode('utf-8')

    try:
        with urllib.request.urlopen(req, data=data, timeout=5) as response:
            status = response.getcode()
            body = json.loads(response.read().decode('utf-8'))
            
            if status != 200:
                return False, f"Failed: HTTP {status}"
                
            missing_keys = [key for key in test_case["expected_keys"] if key not in body]
            if missing_keys:
                return False, f"Failed: Missing keys in response -> {missing_keys}"
                
            return True, "Passed (200 OK & Schema Valid)"
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        return False, f"Failed: HTTP {e.code} - {error_body}"
    except Exception as e:
        return False, f"Failed: Connection Error ({str(e)})"

def run_all():
    print(f"Pinging MANAK Orchestration APIs at {BASE_URL}...\n")
    all_passed = True
    
    for test in ENDPOINTS_TO_TEST:
        print(f"Testing {test['name']} ({test['method']} {test['url']})...")
        passed, message = ping_endpoint(test)
        
        if passed:
            print(f"  [SUCCESS] {message}\n")
        else:
            print(f"  [ERROR] {message}\n")
            all_passed = False
            
    if all_passed:
        print("🎉 All endpoints are live and returning the correct data shapes!")
        sys.exit(0)
    else:
        print("⚠️ Some endpoints failed. Check your live server logs for errors.")
        sys.exit(1)

if __name__ == "__main__":
    run_all()