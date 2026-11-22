import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from web.app import app

def test_path_traversal_regression():
    print("=" * 70)
    print("REGRESSION TEST: /api/document/{doc_id} PATH TRAVERSAL REMEDIATION")
    print("=" * 70)

    client = TestClient(app)

    # 1. Normal valid document request
    print("[TEST 1/7] Normal valid document ID: DOC-EHR-001...")
    resp = client.get("/api/document/DOC-EHR-001")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    data = resp.json()
    assert data["doc_id"] == "DOC-EHR-001"
    assert "CLINICAL ENCOUNTER SUMMARY" in data["content"]
    print("       - PASS: Successfully loaded DOC-EHR-001.")

    # 2. Normal document ID with citation brackets and page suffix
    print("[TEST 2/7] Document ID with citation format: [DOC-EHR-001, p.2]...")
    resp = client.get("/api/document/[DOC-EHR-001, p.2]")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    data = resp.json()
    assert data["doc_id"] == "DOC-EHR-001"
    print("       - PASS: Correctly normalized citation token to DOC-EHR-001.")

    # 3. Path traversal attempt using relative path syntax
    print("[TEST 3/7] Traversal attempt: ../../PLAN...")
    resp = client.get("/api/document/..%2F..%2FPLAN")
    assert resp.status_code in [400, 403], f"Expected 400 or 403, got {resp.status_code}"
    assert "PLAN" not in resp.text or resp.status_code != 200
    print(f"       - PASS: Traversal blocked with HTTP {resp.status_code} ({resp.json().get('detail')}).")

    # 4. Traversal attempt with slash and dots
    print("[TEST 4/7] Subpath traversal attempt: data/../PLAN...")
    resp = client.get("/api/document/data%2F..%2FPLAN")
    assert resp.status_code in [400, 403], f"Expected 400 or 403, got {resp.status_code}"
    print(f"       - PASS: Subpath traversal blocked with HTTP {resp.status_code} ({resp.json().get('detail')}).")

    # 5. Absolute path attempt
    print("[TEST 5/7] Absolute path attempt: /etc/passwd or C:/Windows...")
    resp = client.get("/api/document//etc/passwd")
    assert resp.status_code in [400, 403, 404], f"Expected rejection, got {resp.status_code}"
    print(f"       - PASS: Absolute path blocked with HTTP {resp.status_code}.")

    # 6. Malicious shell / injection characters
    print("[TEST 6/7] Invalid characters: DOC-EHR-001;rm -rf /...")
    resp = client.get("/api/document/DOC-EHR-001;rm")
    assert resp.status_code == 400, f"Expected 400 for invalid format, got {resp.status_code}"
    print(f"       - PASS: Invalid format blocked with HTTP 400 ({resp.json().get('detail')}).")

    # 7. Nonexistent document ID (valid format, but file does not exist)
    print("[TEST 7/7] Nonexistent document ID: DOC-EHR-999...")
    resp = client.get("/api/document/DOC-EHR-999")
    assert resp.status_code == 404, f"Expected 404 for missing doc, got {resp.status_code}"
    print(f"       - PASS: Missing document returned HTTP 404 ({resp.json().get('detail')}).")

    print("=" * 70)
    print("ALL 7 PATH TRAVERSAL REGRESSION TESTS PASSED")
    print("=" * 70)

if __name__ == "__main__":
    test_path_traversal_regression()
