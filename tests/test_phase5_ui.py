import sys
import re
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from web.app import app

def test_phase5_ui():
    print("=" * 70)
    print("TEST GATE 5: BENCHMARK CONSOLE & DESIGN VERIFICATION")
    print("=" * 70)

    client = TestClient(app)

    # 1. Test Endpoint: Root HTML & Health
    print("[TEST 1/6] Checking GET / and GET /api/health endpoints...")
    resp = client.get("/")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    assert "Clinical Intelligence Benchmark Console" in resp.text

    resp_h = client.get("/api/health")
    assert resp_h.status_code == 200, f"Expected 200, got {resp_h.status_code}"
    assert resp_h.json()["status"] == "healthy"
    print("[PASS] Root console HTML and health check endpoint verified.")

    # 2. Test Endpoint: API Queries
    print("[TEST 2/6] Checking GET /api/queries endpoint...")
    resp_q = client.get("/api/queries")
    assert resp_q.status_code == 200
    queries_data = resp_q.json()
    assert len(queries_data["queries"]) == 50
    print(f"[PASS] /api/queries returned {len(queries_data['queries'])} validated benchmark questions.")

    # 3. Test Endpoint: Summary RAGAS Metrics
    print("[TEST 3/6] Checking GET /api/summary endpoint...")
    resp_s = client.get("/api/summary")
    assert resp_s.status_code == 200
    summary_data = resp_s.json()
    assert "summary" in summary_data
    assert "faithfulness" in summary_data["summary"]["overall"]["pipeline_b"]
    print("[PASS] /api/summary returned empirical RAGAS matrix.")

    # 4. Test Live Dual-Pipeline Execution: POST /api/run
    print("[TEST 4/6] Checking POST /api/run live execution...")
    run_payload = {
        "query_text": "What was the initial dosage of Lisinopril prescribed to patient P-101?",
        "target_pipeline": "both"
    }
    resp_run = client.post("/api/run", json=run_payload)
    assert resp_run.status_code == 200
    run_data = resp_run.json()
    assert "pipeline_a" in run_data and "pipeline_b" in run_data
    assert len(run_data["pipeline_b"]["citations"]) > 0

    # Pipeline A Evidence Passages Data Contract Verification
    print("       - Checking Pipeline A evidence retrieval & passage data contract...")
    pipe_a_chunks = run_data["pipeline_a"].get("retrieved_chunk_metadata", [])
    assert len(pipe_a_chunks) == 4, f"Expected top-k=4 chunks for Pipeline A, got {len(pipe_a_chunks)}"
    for idx, c in enumerate(pipe_a_chunks):
        assert c["rank"] == idx + 1, f"Expected rank {idx + 1}, got {c.get('rank')}"
        assert c["doc_id"].startswith("DOC-EHR-"), f"Invalid doc_id format: {c.get('doc_id')}"
        assert isinstance(c["page_number"], int), f"Invalid page_number: {c.get('page_number')}"
        assert "chunk_id" in c and len(c["chunk_id"]) > 0
        assert "score" in c and isinstance(c["score"], (int, float))
        assert "content" in c and len(c["content"]) > 0
        assert c["content"] == run_data["pipeline_a"]["retrieved_contexts"][idx]
    print(f"       - Verified Pipeline A returns 4 complete retrieved passages with score, rank, doc_id, page, and raw content.")

    # Regression Verification: Knowledge Graph Triples Data Integrity (8 Scenarios)
    print("       - Checking Knowledge Graph triple parsing & data contract (8 scenarios)...")

    # Helper replicating frontend parseGraphTriple logic to verify test scenarios 1-6
    def parse_graph_triple(item):
        if not item:
            return None
        s, p, o, raw = None, None, None, None
        if isinstance(item, dict):
            s = item.get("subject") or item.get("source") or item.get("from")
            p = item.get("predicate") or item.get("relation") or item.get("relationship")
            o = item.get("object") or item.get("target") or item.get("to") or item.get("connected_fact")
        elif isinstance(item, (list, tuple)) and len(item) >= 3:
            s, p, o = item[0], item[1], item[2]
        elif isinstance(item, str):
            raw = item.strip()
            m = re.match(r"^\(?\s*(?:[A-Za-z0-9_]+:)?([^\)]+?)\s*\)?\s*-\[:?([A-Za-z0-9_\-]+)\]->\s*\(?\s*(?:[A-Za-z0-9_]+:)?([^\)]+?)\s*\)?$", raw)
            if m:
                s, p, o = m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
            else:
                arrow_m = re.match(r"^(.*?)\s*(?:-\[:?([A-Za-z0-9_\-]+)\]->|->)\s*(.*?)$", raw)
                if arrow_m:
                    s = arrow_m.group(1).replace("(", "").replace(")", "").strip()
                    p = arrow_m.group(2).strip() if arrow_m.group(2) else "CONNECTED_TO"
                    o = arrow_m.group(3).replace("(", "").replace(")", "").strip()

        if not s or not p or not o or s == "undefined" or p == "undefined" or o == "undefined":
            return None
        return {"subject": s, "predicate": p, "object": o}

    # Scenario 1: Readable relationship strings
    s1 = parse_graph_triple("(Patient:P-102) -[:DIAGNOSED_WITH]-> (Diagnosis:HFrEF NYHA Class III)")
    assert s1 is not None and s1["subject"] == "P-102" and s1["predicate"] == "DIAGNOSED_WITH" and "HFrEF" in s1["object"]

    # Scenario 2: Structured relationship objects
    s2 = parse_graph_triple({"subject": "Patient:P-102", "predicate": "DIAGNOSED_WITH", "object": "Diagnosis:HFrEF NYHA Class III"})
    assert s2 is not None and s2["subject"] == "Patient:P-102" and s2["predicate"] == "DIAGNOSED_WITH"

    # Scenario 3: Multiple relationships
    s3_list = [
        "(Patient:P-102) -[:DIAGNOSED_WITH]-> (Diagnosis:HFrEF NYHA Class III)",
        "(Patient:P-102) -[:PRESCRIBED]-> (Medication:Carvedilol 3.125mg)"
    ]
    s3_parsed = [parse_graph_triple(x) for x in s3_list]
    assert all(p is not None for p in s3_parsed) and len(s3_parsed) == 2

    # Scenario 4: Empty graph evidence
    s4_list = []
    s4_parsed = [parse_graph_triple(x) for x in s4_list if parse_graph_triple(x)]
    assert len(s4_parsed) == 0

    # Scenario 5: Malformed relationship strings (safely rejected as None, never outputs undefined)
    assert parse_graph_triple("just a random non-triple string") is None
    assert parse_graph_triple("((incomplete syntax") is None

    # Scenario 6: Missing subject/predicate/object or literal undefined (safely rejected)
    assert parse_graph_triple("(undefined)-[:undefined]->(undefined)") is None
    assert parse_graph_triple({"subject": "P-101"}) is None
    assert parse_graph_triple({}) is None
    assert parse_graph_triple(None) is None

    # Scenario 7: Unrelated query returns clean empty list
    resp_empty = client.post("/api/run", json={"query_text": "What is the capital of France?", "target_pipeline": "pipeline_b"})
    assert resp_empty.status_code == 200
    assert len(resp_empty.json()["pipeline_b"]["graph_evidence"]) == 0

    # Scenario 8: Valid query for correct patient returns valid facts for that patient
    # Test P-101
    graph_evidence_p101 = run_data["pipeline_b"].get("graph_evidence", [])
    assert len(graph_evidence_p101) > 0
    assert any("P-101" in fact for fact in graph_evidence_p101)
    for fact in graph_evidence_p101:
        assert isinstance(fact, str)
        assert "undefined" not in fact.lower()
        parsed = parse_graph_triple(fact)
        assert parsed is not None

    # Test P-102 live query
    resp_p102 = client.post("/api/run", json={
        "query_text": "Explain how the echocardiographic finding for patient P-102 determined the selection of neurohormonal discharge medications.",
        "target_pipeline": "pipeline_b"
    })
    assert resp_p102.status_code == 200
    graph_evidence_p102 = resp_p102.json()["pipeline_b"].get("graph_evidence", [])
    assert len(graph_evidence_p102) > 0
    assert any("P-102" in fact for fact in graph_evidence_p102)
    for fact in graph_evidence_p102:
        assert isinstance(fact, str)
        assert "undefined" not in fact.lower()
        parsed = parse_graph_triple(fact)
        assert parsed is not None

    print(f"[PASS] Live query executed across both pipelines (Latency: Pipe A={run_data['pipeline_a']['metrics']['total_latency_ms']}ms, Pipe B={run_data['pipeline_b']['metrics']['total_latency_ms']}ms).")
    print(f"       - Verified Knowledge Graph triples integrity across all 8 test scenarios: 0 undefined values.")

    # 5. Test Document Retrieval Security & Path Traversal Prevention
    print("[TEST 5/6] Checking GET /api/document/{doc_id} security...")
    # Normal access
    resp_doc = client.get("/api/document/DOC-EHR-001")
    assert resp_doc.status_code == 200
    assert "DOC-EHR-001" in resp_doc.json()["doc_id"]
    # Citation format normal access
    resp_cite = client.get("/api/document/[DOC-EHR-001, p.2]")
    assert resp_cite.status_code == 200
    # Traversal blocking
    resp_trav = client.get("/api/document/..%2F..%2FPLAN")
    assert resp_trav.status_code in [400, 403], f"Expected 400 or 403, got {resp_trav.status_code}"
    # Missing doc
    resp_missing = client.get("/api/document/DOC-EHR-999")
    assert resp_missing.status_code == 404
    print("[PASS] Document endpoint securely validates IDs and prevents path traversal.")

    # 6. UI Styling Compliance Verification
    print("[TEST 6/6] Verifying UI styling and typography specifications...")
    css_content = Path("web/static/console.css").read_text(encoding="utf-8")
    html_content = Path("web/templates/index.html").read_text(encoding="utf-8")

    # Check A: No Purple/Indigo gradients
    banned_gradient_pattern = re.compile(r"gradient.*(indigo|purple|violet|pink)", re.IGNORECASE)
    assert not banned_gradient_pattern.search(css_content), "VIOLATION: Detected purple/indigo gradient in console.css!"
    print("       - Check A: Zero purple/indigo/pink gradients verified.")

    # Check B: No Glassmorphism backdrop blurs
    assert "backdrop-filter: blur" not in css_content.lower(), "VIOLATION: Detected glassmorphism backdrop blur in console.css!"
    print("       - Check B: Zero glassmorphism frosted glass panels verified.")

    # Check C: No generic SaaS marketing copy
    banned_copy = ["magic", "supercharge", "unleash", "empower your workflow", "rocket", "next-gen ai"]
    for word in banned_copy:
        assert word not in html_content.lower(), f"VIOLATION: Detected generic marketing buzzword '{word}' in index.html!"
    print("       - Check C: Zero generic marketing clichés in UI copy verified.")

    # Check D: High data density and monospace font present
    assert "JetBrains Mono" in css_content or "SF Mono" in css_content or "font-mono" in css_content
    print("       - Check D: Data-dense monospace telemetry typography verified.")

    print("=" * 70)
    print("ALL GATE 5 CRITERIA MET: 100% PASS (DESIGN SYSTEM & BACKEND VERIFIED)")
    print("=" * 70)

if __name__ == "__main__":
    test_phase5_ui()

