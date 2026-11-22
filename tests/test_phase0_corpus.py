import os
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from data.eval_schema import BenchmarkDataset, QueryType

def test_phase0_corpus():
    print("=" * 70)
    print("TEST GATE 0: CLINICAL CORPUS & GOLD BENCHMARK VERIFICATION")
    print("=" * 70)

    corpus_dir = Path("data/corpus")
    benchmark_file = Path("data/benchmark/gold_benchmark.json")

    # Check 1: Corpus directory exists and has files
    assert corpus_dir.exists() and corpus_dir.is_dir(), "data/corpus directory missing"
    corpus_files = list(corpus_dir.glob("*.md"))
    assert len(corpus_files) >= 5, f"Expected at least 5 clinical documents, found {len(corpus_files)}"
    print(f"[PASS] Found {len(corpus_files)} clinical corpus documents:")
    for cf in corpus_files:
        content = cf.read_text(encoding="utf-8")
        assert len(content) > 300, f"Document {cf.name} is too short ({len(content)} bytes)"
        assert "--- PAGE" in content, f"Document {cf.name} missing page break markers"
        print(f"       - {cf.name} ({len(content)} characters, {content.count('--- PAGE')} pages)")

    # Check 2: Benchmark file exists and parses against Pydantic schema
    assert benchmark_file.exists(), "data/benchmark/gold_benchmark.json missing"
    with open(benchmark_file, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    benchmark = BenchmarkDataset.model_validate(raw_data)
    print(f"[PASS] Benchmark JSON parsed against Pydantic schema successfully.")
    assert benchmark.total_queries == 50, f"Expected 50 queries, found {benchmark.total_queries}"
    assert len(benchmark.queries) == 50, f"Queries array length mismatch: {len(benchmark.queries)}"

    # Check 3: Query type distribution
    counts = {
        QueryType.SINGLE_HOP: 0,
        QueryType.MULTI_HOP: 0,
        QueryType.TABLE_EXTRACTION: 0
    }
    for q in benchmark.queries:
        counts[q.query_type] += 1
        # Check that provenance doc exists in corpus
        doc_filename = f"{q.provenance.doc_id.split(',')[0].strip()}.md"
        doc_path = corpus_dir / doc_filename
        assert doc_path.exists(), f"Query {q.query_id} references non-existent doc: {doc_filename}"
        assert len(q.reference_claims) >= 1, f"Query {q.query_id} has no reference claims"

    print(f"[PASS] Query Type Distribution Verified:")
    print(f"       - Single-Hop Factual Queries: {counts[QueryType.SINGLE_HOP]} / 20")
    print(f"       - Multi-Hop Relational Queries: {counts[QueryType.MULTI_HOP]} / 20")
    print(f"       - Table-Extraction Queries: {counts[QueryType.TABLE_EXTRACTION]} / 10")
    assert counts[QueryType.SINGLE_HOP] == 20
    assert counts[QueryType.MULTI_HOP] == 20
    assert counts[QueryType.TABLE_EXTRACTION] == 10

    print("=" * 70)
    print("ALL GATE 0 CRITERIA MET: 100% PASS")
    print("=" * 70)

if __name__ == "__main__":
    test_phase0_corpus()

