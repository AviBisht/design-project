import sys
import json
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipelines.pipeline_b.hybrid_agent_pipeline import HybridAgenticRAGPipeline

def test_phase3_agent():
    print("=" * 70)
    print("TEST GATE 3: PIPELINE B (HYBRID GRAPH-AGENTIC RAG) VERIFICATION")
    print("=" * 70)

    # 1. Initialize Pipeline B
    pipeline = HybridAgenticRAGPipeline(corpus_dir="data/corpus")
    pipeline.initialize(force_reload=True)
    print("[PASS] Pipeline B initialized with Hybrid Vector + Graph + Table indexes.")

    # 2. Test Bounded State Machine (Infinite loop protection)
    print("[TEST 1/3] Testing Bounded Loop & Query Reformulator Guardrails...")
    ambiguous_query = "what pills were prescribed for water retention and high blood pressure?"
    res_ambiguous = pipeline.query(ambiguous_query)
    agent_path = res_ambiguous["agent_path"]
    attempts = res_ambiguous["metrics"]["attempt_count"]
    print(f"       - Agent Path: {' -> '.join(agent_path)}")
    print(f"       - Attempt count: {attempts}")
    assert attempts <= 1, f"Loop exceeded maximum bounded attempt limit: {attempts}"
    assert "query_reformulator" in agent_path, "Expected reformulator to trigger on low context query"
    print("[PASS] Bounded loop guardrail verified (strictly <= 1 retry attempt).")

    # 3. Test Claim Verification & Provenance Citation Engine
    print("[TEST 2/3] Testing Claim Verification and Provenance Citations...")
    res_table = pipeline.query("Extract the exact serum potassium and creatinine values for patient P-101 on 2026-03-19 from Table 1.")
    assert len(res_table["citations"]) > 0, "No citations generated for table query"
    assert any("DOC-EHR-001" in c for c in res_table["citations"]), "Failed to cite correct source document"
    print(f"       - Table Citations Generated: {res_table['citations']}")
    print(f"       - Verified Claims Count: {res_table['metrics']['verified_claims_count']}")
    assert res_table["metrics"]["verified_claims_count"] >= 1, "Expected at least 1 verified claim"
    print("[PASS] Citation & Claim Verification verified.")

    # 4. Run All 50 Benchmark Queries through Pipeline B
    print("[TEST 3/3] Executing 50 benchmark queries through Pipeline B...")
    benchmark_path = Path("data/benchmark/gold_benchmark.json")
    with open(benchmark_path, "r", encoding="utf-8") as f:
        benchmark_data = json.load(f)

    queries = benchmark_data["queries"]
    results = []
    total_latency = 0.0

    for q in queries:
        out = pipeline.query(q["query_text"])
        total_latency += out["metrics"]["total_latency_ms"]

        assert "answer" in out and len(out["answer"]) > 0, f"Query {q['query_id']} produced empty answer"

        results.append({
            "query_id": q["query_id"],
            "query_type": q["query_type"],
            "query_text": q["query_text"],
            "reference_answer": q["reference_answer"],
            "generated_answer": out["answer"],
            "retrieved_contexts": out.get("retrieved_contexts", []),
            "graph_evidence": out.get("graph_evidence", []),
            "table_evidence": out.get("table_evidence", []),
            "citations": out["citations"],
            "agent_path": out["agent_path"],
            "metrics": out["metrics"]
        })

    avg_latency = round(total_latency / len(queries), 2)
    print(f"[PASS] All {len(queries)} queries executed successfully through Pipeline B.")
    print(f"       - Average Pipeline B Latency: {avg_latency} ms / query")

    # Persist results to eval/advanced_results.json
    out_file = Path("eval/advanced_results.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({
            "pipeline": "pipeline_b",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_queries": len(results),
            "average_latency_ms": avg_latency,
            "results": results
        }, f, indent=2)

    print(f"[SAVED] Persisted advanced pipeline predictions to {out_file}")
    print("=" * 70)
    print("ALL GATE 3 CRITERIA MET: 100% PASS")
    print("=" * 70)

if __name__ == "__main__":
    test_phase3_agent()
