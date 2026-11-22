import sys
import time
import subprocess
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

TEST_SCRIPTS = [
    ("Gate 0: Corpus Curation & Gold Benchmark", "tests/test_phase0_corpus.py"),
    ("Gate 1: Pipeline A Baseline Naive RAG", "tests/test_phase1_naive.py"),
    ("Gate 2: Layout Parsing & In-memory Clinical Graph", "tests/test_phase2_graph.py"),
    ("Gate 3: Native Python Agent & Citations", "tests/test_phase3_agent.py"),
    ("Gate 4: Custom Comparative Metrics", "tests/test_phase4_ragas.py"),
    ("Gate 5: Clinical Research Console UI", "tests/test_phase5_ui.py"),
]

def run_all_test_gates():
    print("=" * 78)
    print("DUAL-PIPELINE CLINICAL INTELLIGENCE ENGINE: MASTER TEST GATE HARNESS")
    print("VMSB UTU B.Tech Capstone 2026-27 | Kush Garg & Avi Bisht")
    print("=" * 78)

    results = []
    total_start = time.perf_counter()

    for idx, (label, script_path) in enumerate(TEST_SCRIPTS):
        print(f"\n[{idx+1}/{len(TEST_SCRIPTS)}] Executing {label} ({script_path})...")
        t0 = time.perf_counter()
        
        proc = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
        elapsed = round(time.perf_counter() - t0, 2)
        
        passed = (proc.returncode == 0)
        results.append({
            "gate": f"Gate {idx}",
            "label": label,
            "script": script_path,
            "passed": passed,
            "elapsed_s": elapsed,
            "stdout": proc.stdout,
            "stderr": proc.stderr
        })

        if passed:
            print(f"       ✅ PASS ({elapsed}s)")
        else:
            print(f"       ❌ FAIL ({elapsed}s) with exit code {proc.returncode}")
            print("--- Output ---")
            print(proc.stdout)
            print(proc.stderr)
            print("--------------")

    total_time = round(time.perf_counter() - total_start, 2)

    print("\n" + "=" * 78)
    print("MASTER TEST SUITE EXECUTION SUMMARY")
    print("=" * 78)
    print(f"{'Test Gate':<10} | {'Milestone Description':<40} | {'Time (s)':<10} | {'Status':<10}")
    print("-" * 78)

    all_passed = True
    for r in results:
        status_str = "PASS ✅" if r["passed"] else "FAIL ❌"
        if not r["passed"]:
            all_passed = False
        print(f"{r['gate']:<10} | {r['label']:<40} | {r['elapsed_s']:<10} | {status_str}")

    print("-" * 78)
    print(f"Total Execution Time: {total_time}s | Result: {'ALL 6 GATES PASSED (100%)' if all_passed else 'TEST FAILURES DETECTED'}")
    print("=" * 78)

    if not all_passed:
        sys.exit(1)

if __name__ == "__main__":
    run_all_test_gates()
