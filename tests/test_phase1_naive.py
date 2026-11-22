import sys
import json
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipelines.pipeline_a.naive_pipeline import NaiveRAGPipeline

def test_phase1_naive():
    print("=" * 70)
    print("TEST GATE 1: PIPELINE A (NAIVE RAG BASELINE) VERIFICATION")
    print("=" * 70)

    benchmark_path = Path("data/benchmark/gold_benchmark.json")
    assert benchmark_path.exists(), "Benchmark dataset must exist before testing Phase 1"

    with open(benchmark_path, "r", encoding="utf-8") as f:
        benchmark_data = json.load(f)

    queries = benchmark_data["queries"]
    print(f"[INIT] Loaded {len(queries)} gold-standard queries for baseline testing.")

    pipeline = NaiveRAGPipeline(
        corpus_dir="data/corpus",
        persist_db="data/vectorstore_pipeline_a.json"
    )
    pipeline.initialize(force_reload=True)
    print(f"[PASS] Pipeline A initialized and vector store indexed.")

    results = []
    total_latency = 0.0

    print(f"[RUN] Executing 50 baseline queries through Pipeline A...")
    for q in queries:
        q_id = q["query_id"]
        q_text = q["query_text"]
        q_type = q["query_type"]

        out = pipeline.query(q_text, top_k=4)
        total_latency += out["metrics"]["total_latency_ms"]

        assert "answer" in out and len(out["answer"]) > 0, f"Query {q_id} produced empty answer"
        assert len(out["retrieved_contexts"]) > 0, f"Query {q_id} retrieved no contexts"

        results.append({
            "query_id": q_id,
            "query_type": q_type,
            "query_text": q_text,
            "reference_answer": q["reference_answer"],
            "generated_answer": out["answer"],
            "retrieved_contexts": out["retrieved_contexts"],
            "retrieved_metadata": out["retrieved_chunk_metadata"],
            "metrics": out["metrics"]
        })

    avg_latency = round(total_latency / len(queries), 2)
    print(f"[PASS] All {len(queries)} queries executed successfully with zero runtime failures.")
    print(f"       - Average Pipeline A Latency: {avg_latency} ms / query")

    # Save output for comparative evaluation in Phase 4
    Path("eval").mkdir(exist_ok=True)
    out_file = Path("eval/baseline_results.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({
            "pipeline": "pipeline_a",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_queries": len(results),
            "average_latency_ms": avg_latency,
            "results": results
        }, f, indent=2)

    print(f"[SAVED] Persisted baseline predictions to {out_file}")
    print("=" * 70)
    print("ALL GATE 1 CRITERIA MET: 100% PASS")
    print("=" * 70)

if __name__ == "__main__":
    test_phase1_naive()

