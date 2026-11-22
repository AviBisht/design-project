import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipelines.pipeline_b.layout_parser import LayoutAwareParser
from pipelines.pipeline_b.clinical_graph import build_clinical_graph_from_corpus

def test_phase2_graph():
    print("=" * 70)
    print("TEST GATE 2: LAYOUT PARSING & CLINICAL KNOWLEDGE GRAPH VERIFICATION")
    print("=" * 70)

    # 1. Test Layout-Aware Parser on all 5 documents
    parser = LayoutAwareParser()
    corpus_files = sorted(Path("data/corpus").glob("*.md"))
    assert len(corpus_files) >= 5, "Corpus documents missing"

    total_tables = 0
    print(f"[TEST 1/3] Parsing {len(corpus_files)} documents with LayoutAwareParser...")
    for cf in corpus_files:
        doc = parser.parse_document(cf)
        assert len(doc["sections"]) > 0, f"No sections parsed from {cf.name}"
        total_tables += len(doc["tables"])
        for tbl in doc["tables"]:
            assert len(tbl.headers) >= 3, f"Table {tbl.table_id} headers malformed"
            assert len(tbl.rows) >= 2, f"Table {tbl.table_id} missing rows"
            print(f"       - Parsed {cf.name}: {tbl.table_id} '{tbl.title}' ({len(tbl.rows)} rows, {len(tbl.headers)} cols)")

    assert total_tables == 5, f"Expected 5 structured clinical tables, found {total_tables}"
    print(f"[PASS] All 5 tables extracted with intact column alignment.")

    # 2. Test Table Cell Value Preservation (Anti-Flattening test)
    doc_1 = parser.parse_document(Path("data/corpus/DOC-EHR-001.md"))
    tbl_1 = doc_1["tables"][0]
    potassium_val = tbl_1.find_cell(row_filter_key="2026-03-19", target_col="Result")
    potassium_flag = tbl_1.find_cell(row_filter_key="2026-03-19", target_col="Flag")
    print(f"[TEST 2/3] Checking Table 1 cell integrity: Result={potassium_val}, Flag={potassium_flag}")
    assert potassium_val == "5.7", f"Expected 5.7, got {potassium_val}"
    assert potassium_flag == "CRITICAL_HIGH", f"Expected CRITICAL_HIGH, got {potassium_flag}"
    print(f"[PASS] Table 1 preserved cell headers and critical laboratory flag.")

    # 3. Test Clinical Knowledge Graph & Multi-Hop Traversal
    print(f"[TEST 3/3] Building and traversing Clinical Knowledge Graph...")
    kg = build_clinical_graph_from_corpus()
    assert len(kg.nodes) >= 20, f"Insufficient graph nodes: {len(kg.nodes)}"
    assert len(kg.edges) >= 20, f"Insufficient graph edges: {len(kg.edges)}"
    print(f"[PASS] Graph successfully built: {len(kg.nodes)} nodes, {len(kg.edges)} edges.")

    # Multi-hop test: Lisinopril -> Hyperkalemia -> Lokelma
    paths = kg.multi_hop_traverse("Lisinopril", max_hops=2)
    assert len(paths) > 0, "No traversal paths found for Lisinopril"
    found_hyperkalemia = any("Hyperkalemia" in p["readable_fact"] for p in paths)
    found_lokelma = any("Lokelma" in p["readable_fact"] for p in paths)
    print(f"       - 2-hop traversal paths from 'Lisinopril': {len(paths)} found.")
    assert found_hyperkalemia, "Graph failed to link Lisinopril to Hyperkalemia"
    assert found_lokelma, "Graph failed to link Hyperkalemia to Lokelma (2-hop link)"
    print(f"[PASS] Multi-hop relationship path verified: Lisinopril -> Hyperkalemia -> Lokelma")

    # Check Cypher script export
    cypher_path = Path("data/neo4j_ingest.cypher")
    kg.export_cypher_script(str(cypher_path))
    assert cypher_path.exists(), "Neo4j ingestion script failed to export"
    cypher_content = cypher_path.read_text(encoding="utf-8")
    assert "CREATE CONSTRAINT" in cypher_content
    assert "MERGE" in cypher_content
    print(f"[PASS] Neo4j Cypher DDL/DML script generated ({len(cypher_content.splitlines())} lines).")

    print("=" * 70)
    print("ALL GATE 2 CRITERIA MET: 100% PASS")
    print("=" * 70)

if __name__ == "__main__":
    test_phase2_graph()

