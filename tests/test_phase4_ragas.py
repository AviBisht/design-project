import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from eval.ragas_engine import run_comparative_benchmark

def test_phase4_ragas():
    print("=" * 70)
    print("TEST GATE 4: COMPARATIVE RAGAS EVALUATION HARNESS VERIFICATION")
    print("=" * 70)

    report = run_comparative_benchmark(
        benchmark_file="data/benchmark/gold_benchmark.json",
        baseline_file="eval/baseline_results.json",
        advanced_file="eval/advanced_results.json",
        out_file="eval/comparative_metrics.json"
    )

    metrics_file = Path("eval/comparative_metrics.json")
    assert metrics_file.exists(), "eval/comparative_metrics.json was not created"
    print(f"[PASS] Successfully generated comparative evaluation metrics: {metrics_file}")

    summary = report["summary"]
    overall_a = summary["overall"]["pipeline_a"]
    overall_b = summary["overall"]["pipeline_b"]

    print("\nOVERALL METRIC COMPARISON (50 GOLD-STANDARD BENCHMARK QUERIES):")
    print(f"{'Metric':<20} | {'Pipeline A (Naive)':<20} | {'Pipeline B (Graph-Agentic)':<26} | {'Delta':<10}")
    print("-" * 82)
    for m in ["faithfulness", "context_recall", "context_precision", "answer_relevancy"]:
        val_a = overall_a[m]
        val_b = overall_b[m]
        delta = round(val_b - val_a, 4)
        sign = "+" if delta > 0 else ""
        print(f"{m.replace('_', ' ').title():<20} | {val_a:<20} | {val_b:<26} | {sign}{delta}")
        assert val_a > 0.0, f"Pipeline A metric {m} is 0.0"
        assert val_b > 0.0, f"Pipeline B metric {m} is 0.0"

    print("\nSUB-CATEGORY BREAKDOWN:")
    for cat in ["single_hop", "multi_hop", "table_extraction"]:
        c_a = summary[cat]["pipeline_a"]
        c_b = summary[cat]["pipeline_b"]
        print(f"[{cat.upper()}]")
        print(f"  - Context Recall: Pipeline A={c_a['context_recall']:.3f} vs Pipeline B={c_b['context_recall']:.3f}")
        print(f"  - Faithfulness:   Pipeline A={c_a['faithfulness']:.3f} vs Pipeline B={c_b['faithfulness']:.3f}")

    # Empirical hypothesis check: Pipeline B must improve Context Recall on relational and tabular queries
    assert summary["multi_hop"]["pipeline_b"]["context_recall"] >= summary["multi_hop"]["pipeline_a"]["context_recall"], \
        "Expected Pipeline B graph retrieval to improve multi-hop recall"
    assert summary["table_extraction"]["pipeline_b"]["context_recall"] >= summary["table_extraction"]["pipeline_a"]["context_recall"], \
        "Expected Pipeline B layout-aware parsing to improve table recall"

    print("\n[PASS] Empirical hypotheses validated against matched ground truth.")
    print("=" * 70)
    print("ALL GATE 4 CRITERIA MET: 100% PASS")
    print("=" * 70)

if __name__ == "__main__":
    test_phase4_ragas()

