# Dual-Pipeline Clinical Intelligence Engine
**A Controlled Proof-of-Concept Comparative Study of Chunk-Based Lexical Retrieval vs. Graph-Assisted Retrieval for Synthetic Longitudinal Clinical Records**  
*Submitted in partial fulfillment of the requirements for the degree of Bachelor of Technology (B.Tech.) in Computer Science and Engineering*  
**Department of Computer Science and Engineering, VMSB Uttarakhand Technical University, Dehradun**  
**Academic Session:** 2026–2027  
**Authors:** Kush Garg (230000101053) & Avi Bisht (230000101027)

---

## 1. Research Objective & Scope (Phase-I)

### 1.1 Objective Statement
The primary objective of this Phase-I study is:
> *"To implement and demonstrate the feasibility of two retrieval architectures for synthetic longitudinal clinical records: a conventional chunk-based RAG pipeline and a structured, graph-assisted retrieval pipeline. The study examines how document structure, manually curated clinical relationships, and multi-step retrieval affect evidence retrieval and answer construction under controlled experimental conditions."*

### 1.2 Clinical Problem Context
Electronic Health Records (EHRs) contain fragmented longitudinal patient histories, complex laboratory flowsheets, and multi-visit clinical notes. Conventional chunk-based retrieval systems face three documented engineering challenges when handling EHR documents:
1. **Relational Context Disconnect:** Arbitrary character-based chunking splits clinical event sequences across separate text passages, breaking the connection between symptoms, subsequent diagnoses, and prescribed therapies across longitudinal encounters.
2. **Table & Flowsheet Disruption:** Plain text extraction flattens multi-column laboratory tables, isolating numerical results from column headers, physiological reference intervals, and unit labels.
3. **Attribution & Provenance Verification:** Single-pass retrieval lacks claim-level provenance anchoring back to primary encounter records and specific flowsheet tables.

### 1.3 Nature of the Implementation & Proof-of-Concept Boundary
This Phase-I implementation serves as a **controlled feasibility prototype and preliminary comparative study**, comparing two distinct retrieval paradigms over an identical synthetic clinical corpus:
* **Pipeline A (Baseline Naive RAG):** Fixed-size character-based chunking (500 chars with 50-char overlap), serialized TF-IDF sparse lexical vector indexing, top-$k$ ($k=4$) cosine similarity retrieval, and deterministic heuristic sentence selection.
* **Pipeline B (Structured Graph-Assisted Prototype):** Layout-aware Markdown section and table parsing, an in-memory clinical knowledge graph traversal engine (with Cypher DDL/DML export for future Neo4j integration), a native Python bounded agent state machine (context grading $\to$ bounded query rewriting $\le 1$ retry $\to$ deterministic answer formatting), and token-level citation attachment.

### 1.4 Methodology Note on Knowledge Graph Construction
> **Methodology and Limitations Disclosure:**  
> In Phase I, the clinical knowledge graph was manually populated using predefined entities and relationships associated with five synthetic patient records. This was an intentional proof-of-concept decision to validate the graph representation, relationship traversal, and agent workflow under controlled conditions. However, this approach does not demonstrate automatic knowledge extraction or generalization to unseen patient records. These capabilities are planned for subsequent development and independent evaluation.

---

## 2. System Architecture

```
                            ┌───────────────────────────────────┐
                            │    Clinical Document Corpus       │
                            │ (5 Synthetic De-identified EHRs)  │
                            └─────────────────┬─────────────────┘
                                               │
               ┌───────────────────────────────┴───────────────────────────────┐
               ▼                                                               ▼
    [ PIPELINE A: Naive Baseline ]                                [ PIPELINE B: Graph-Assisted ]
  ┌───────────────────────────────────────┐                    ┌───────────────────────────────────────┐
  │ • Fixed character chunking (500 char) │                    │ • Layout-aware parser (Markdown tables)│
  │ • TF-IDF sparse lexical vector index  │                    │ • In-memory clinical graph (manual)   │
  │ • Top-k cosine similarity retrieval   │                    │ • Multi-hop relationship traversal    │
  │ • Deterministic sentence extraction   │                    │ • Native Python bounded state machine │
  └───────────────────┬───────────────────┘                    │ • Token-level claim verification      │
                      │                                        └───────────────────┬───────────────────┘
                      │                                                            │
                      └────────────────────────┬───────────────────────────────────┘
                                               ▼
                              ┌───────────────────────────────────┐
                              │     Shared Evaluation Engine      │
                              │ (Custom RAGAS-Inspired Metrics)   │
                              └────────────────┬─────────────────┘
                                               ▼
                              ┌───────────────────────────────────┐
                              │     Clinical Research Console     │
                              │  (Data-Dense Zero-AI Web UI)      │
                              └───────────────────────────────────┘
```

---

## 3. Strict "No-AI Design" User Interface

The web interface is engineered as an **Instrumentation & Audit Workbench** (modeled after scientific interfaces such as NCBI PubMed, Epic Hyperspace, UpToDate, and Grafana), strictly rejecting generic "AI-generated SaaS" marketing aesthetics:

| Banned "AI Slop" Anti-Patterns | Enforced Scientific / Clinical Design Tokens |
| :--- | :--- |
| ❌ No purple-to-indigo/cyan gradients (`from-indigo-500 to-purple-600`) | ✅ High-contrast neutral dark zinc foundation (`#09090b` / `#18181b`, borders `#27272a`) |
| ❌ No floating glassmorphism frosted panels (`backdrop-filter: blur`) | ✅ Crisp solid panels with sharp 1px structural borders |
| ❌ No generic marketing copy (*"AI magic ✨"*) | ✅ Clinical telemetry headers, patient identifiers, and latency metrics |
| ❌ No empty 3-card bento grids with generic icons | ✅ High information entropy: dual side-by-side terminal inspection columns |
| ❌ No bouncy hover micro-animations or glowing borders | ✅ Functional semantic status tokens only (Emerald `#059669` verified, Amber `#d97706` rewrite) |
| ❌ No proportional sans-serif for numerical data | ✅ Strict tabular monospace (`JetBrains Mono`, `ui-monospace`) for lab values and Cypher paths |

---

## 4. Repository Structure

```
design_project/
├── PLAN.md                               # Master engineering execution plan & test gate tracker
├── README.md                             # Comprehensive project documentation
├── run_console.py                        # Single-command launcher for the web dashboard
├── data/
│   ├── eval_schema.py                    # Pydantic data contracts for queries and provenance
│   ├── build_clinical_dataset.py         # Generator for corpus and 50 gold-standard queries
│   ├── neo4j_ingest.cypher               # Generated Neo4j Cypher DDL/DML ingestion script
│   ├── vectorstore_pipeline_a.json       # Serialized local TF-IDF index for Pipeline A
│   ├── vectorstore_pipeline_b.json       # Serialized local TF-IDF index for Pipeline B
│   ├── corpus/                           # Structured clinical documents (DOC-EHR-001 to 005)
│   └── benchmark/
│       └── gold_benchmark.json           # 50 validated gold-standard Q&A pairs with provenance
├── pipelines/
│   ├── pipeline_a/
│   │   ├── naive_loader.py               # Character-based flat document chunker
│   │   ├── naive_vectorstore.py          # TF-IDF sparse lexical vector indexing & cosine similarity
│   │   └── naive_pipeline.py             # Single-pass deterministic baseline extraction pipeline
│   └── pipeline_b/
│       ├── layout_parser.py              # Layout-aware parser preserving markdown tables
│       ├── clinical_graph.py             # In-memory clinical ontology & multi-hop traversal (manual triples)
│       └── hybrid_agent_pipeline.py      # Native Python bounded agent state machine & claim verification
├── eval/
│   ├── ragas_engine.py                   # Custom mathematical RAGAS-inspired evaluator (heuristic metrics)
│   ├── baseline_results.json             # 50 query predictions from Pipeline A
│   ├── advanced_results.json             # 50 query predictions from Pipeline B
│   ├── comparative_metrics.json          # Complete head-to-head evaluation matrix
│   ├── benchmark_detailed_results.csv    # Query-level tabular dataset for analysis
│   └── latex_evaluation_tables.tex       # LaTeX tables for project thesis
├── web/
│   ├── app.py                            # FastAPI backend REST service
│   ├── static/
│   │   ├── console.css                   # Anti-AI clinical design system stylesheet
│   │   ├── console.js                    # Side-by-side execution & citation drill-down
│   │   └── hero-clinical-bg.jpg          # Editorial background imagery
│   └── templates/
│       └── index.html                    # Data-dense dual-column research console
└── tests/
    ├── run_all_tests.py                  # Master test runner executing all 6 gates
    ├── test_path_traversal.py            # Path traversal security regression tests
    ├── test_phase0_corpus.py             # Test Gate 0: Schema & corpus integrity
    ├── test_phase1_naive.py              # Test Gate 1: Baseline pipeline verification
    ├── test_phase2_graph.py              # Test Gate 2: Table preservation & graph traversals
    ├── test_phase3_agent.py              # Test Gate 3: Bounded agent loop & citation checks
    ├── test_phase4_ragas.py              # Test Gate 4: Comparative metric evaluation
    └── test_phase5_ui.py                 # Test Gate 5: Web API & security regression audit
```

---

## 5. Environment Configuration

Application configuration variables are read from the execution environment using `os.getenv` with safe local defaults.
* **Important:** Automatic `.env` file loading is not enabled at runtime in this Phase 1 prototype. Environment variables must be supplied externally via your shell or deployment environment if overriding defaults.
* See `.env.example` for the full reference list of supported runtime variables (`HOST`, `PORT`, `DEBUG`, `CORS_ALLOWED_ORIGINS`, `DATA_CORPUS_DIR`, `GOLD_BENCHMARK_PATH`, `COMPARATIVE_METRICS_PATH`) and planned Semester 8 integration placeholders (`NEO4J_URI`, `OLLAMA_BASE_URL`).

---

## 6. Preliminary Heuristic Evaluation Results (N=50 Benchmark Queries)

Evaluation of both pipelines across the 50 gold-standard questions yielded the following preliminary heuristic measurements. These metrics were calculated using custom mathematical functions modeling RAGAS metric definitions via token overlap and TF-IDF cosine similarity:

$$\text{Faithfulness}(a, C) = \frac{|\{s \in \text{Claims}(a) : C \text{ supports } s\}|}{|\text{Claims}(a)|}$$

$$\text{Context Recall}(G, C) = \frac{|\{g_j \in G : C \text{ supports } g_j\}|}{|G|}$$

$$\text{Context Precision}(C, G) = \frac{\sum_{i=1}^k (P@i \times \text{rel}_i)}{\sum_{i=1}^k \text{rel}_i}$$

$$\text{Answer Relevancy}(q, a) = 0.5 + 0.5 \times \text{CosineSimilarity}(\text{TFIDF}(q), \text{TFIDF}(a))$$

### 6.1 Performance Matrix Summary
| Metric | Pipeline A (Naive Baseline) | Pipeline B (Graph-Assisted Prototype) | Delta ($\Delta$) | Nature of Metric & Interpretation |
| :--- | :---: | :---: | :---: | :--- |
| **Faithfulness** | 48.0% | **97.0%** | **+49.0%** | Token-level containment of answer sentences within retrieved context pool. (See Section 6.2 for limitations). |
| **Context Recall** | 70.7% | **77.5%** | **+6.8%** | Token-level containment of gold claims within retrieved contexts. Pipeline B pulls broader context volume. |
| **Context Precision** | **85.9%** | 53.0% | **-32.9%** | Precision of retrieved evidence ranks. **Pipeline A outperforms Pipeline B** due to compact, focused top-k chunks. |
| **Answer Relevancy** | 0.5497 | **0.5742** | **+0.0245** | TF-IDF question-answer similarity. The observed difference is small and does not establish a meaningful improvement in semantic answer relevancy. (Metric has an artificial baseline floor of 0.50). |

### 6.2 Critical Methodological Limitations & Integrity Analysis
The reported metrics must be interpreted strictly within their technical implementation boundaries:
1. **Token Overlap vs. Natural Language Inference:** Faithfulness and claim verification are measured via token-set containment ($\ge 65\%$ token presence in context), not semantic NLI entailment. The metric cannot verify propositional truth or negation (e.g., "Patient has no AKI" matches "Patient has AKI" at 100% token overlap).
2. **Evaluative Circularity in Pipeline B:** Pipeline B synthesizes answers by formatting matched table rows or graph triples. The faithfulness evaluator then verifies those same formatted tokens against the retrieved evidence pool. This structural circularity artificially guarantees near-100% token containment.
3. **Penalization of Baseline Refusal:** When Pipeline A's similarity score is low, it responsibly outputs: `"Based on the retrieved baseline context, insufficient evidence was found to answer this question."` Because these meta-words do not appear in the clinical document, the token-containment formula scores this safe refusal as **0.0000 Faithfulness**, penalizing responsible fallback as hallucination.
4. **Context Volume Disparity:** Pipeline A is restricted to 4 small 500-character chunks ($k=4$). Pipeline B retrieves up to 6 sections, 2 full tables, and 10 graph triples. The expanded evidence pool aids recall but severely depresses context precision (falling from 85.9% to 53.0%).
5. **Absence of Negative Controls:** The 50 benchmark queries do not include unanswerable negative controls or conflicting clinical records; thus, the current setup evaluates retrieval coverage rather than clinical discrimination or generalization.

---

## 7. Quickstart & Verification Commands

> **Software Verification Scope Disclosure:** Passing the six regression gates demonstrates software-level verification under the implemented tests, not research validity, generalization, clinical accuracy, or superiority of either pipeline.

### Step 1: Run the Automated Master Test Gates & Security Regression
```powershell
python tests/test_path_traversal.py   # Verify Path Traversal Security & Confinement
python tests/run_all_tests.py         # Execute Master Test Gate Harness (Gates 0 to 5)
```
Or execute individual test scripts:
```powershell
python tests/test_phase0_corpus.py   # Verify Corpus & 50 Gold Queries
python tests/test_phase1_naive.py    # Verify Baseline Naive RAG (TF-IDF Indexing)
python tests/test_phase2_graph.py    # Verify Table Parser & In-Memory Graph
python tests/test_phase3_agent.py    # Verify Bounded Agent State Machine & Citations
python tests/test_phase4_ragas.py    # Verify Custom Metric Evaluation
python tests/test_phase5_ui.py       # Verify Web Console & Design Audit
```

### Step 2: Launch the Clinical Research Console
```powershell
python run_console.py
```
Open **`http://127.0.0.1:8000`** in any web browser to inspect side-by-side retrieval, latency telemetry, and provenance verification.

### Step 3: Export LaTeX & CSV Tables
```powershell
python -m eval.generate_reports
```
Generates `eval/benchmark_detailed_results.csv` and `eval/latex_evaluation_tables.tex`.

---

## 8. Phase-II Planned Research Directions (Semester 8)

The following items represent planned subsequent development and evaluation, not completed functionality:
1. **Automated Clinical Knowledge Graph Extraction:** Replace manually authored Python triples with automated entity and relation extraction (e.g., biomedical NER and relation models) capable of ingesting arbitrary unstructured clinical text.
2. **Generalized Query Reformulation:** Remove case-specific hardcoded synonyms (e.g., patient-specific drug names and Table IDs) in favor of standard medical ontology mappings (UMLS / SNOMED CT subsets).
3. **Corpus Generalization & Held-Out Testing:** Evaluate the system on independently created synthetic patient records (Track C) that were not seen during rule or graph development.
4. **Query Robustness & Paraphrase Evaluation:** Test on unseen query paraphrases, clinical abbreviations, and colloquial phrasing (Track B).
5. **Negative-Control & Conflict Evaluation:** Incorporate queries where evidence is missing or contradictory to evaluate whether the pipeline appropriately refuses to answer.
6. **Defensible Evaluation Harness:** Introduce standardized NLI entailment models (e.g., DeBERTa-MNLI) and enforce fixed context token budgets across both pipelines for unbiased comparative benchmarking.
