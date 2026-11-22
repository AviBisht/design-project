# MAJOR PROJECT PHASE-I INTERIM REPORT (40% MILESTONE)
## Dual-Pipeline Clinical Intelligence Engine: Comparative Study of Naive Vector RAG vs. Multimodal Knowledge-Graph Agentic RAG

**Submitted in partial fulfillment of the requirements for the degree of**  
### Bachelor of Technology (B.Tech.) in Computer Science and Engineering  
**Department of Computer Science and Engineering**  
**Faculty of Technology**  
**Veer Madho Singh Bhandari Uttarakhand Technical University (VMSB UTU), Dehradun**  
**Academic Session:** 2026–2027  

**Submitted by:**  
* Kush Garg — Roll No: 230000101053  
* Avi Bisht — Roll No: 230000101027  

**Under the Guidance of:**  
* Project Incharge / Supervisor, Department of Computer Science & Engineering  

---

## CANDIDATE'S DECLARATION

We hereby certify that the work presented in this interim report entitled **"Dual-Pipeline Clinical Intelligence Engine"** in partial fulfillment of the requirements for the award of the degree of **Bachelor of Technology in Computer Science and Engineering**, submitted in the Department of Computer Science and Engineering, Faculty of Technology, VMSB Uttarakhand Technical University, Dehradun, is an authentic record of our own work carried out during the 7th Semester under the supervision of our Project Incharge.

The matter embodied in this report has not been submitted for the award of any other degree.

**Kush Garg (230000101053)**  
**Avi Bisht (230000101027)**  
Date: November 2026 | Dehradun  

---

## 1. ABSTRACT & INTRODUCTION

Electronic Health Records (EHRs) consolidate narrative clinical notes, multi-visit discharge summaries, medication orders, and laboratory telemetry flowsheets. Traditional Retrieval-Augmented Generation (RAG) models built on character-based flat chunking suffer from three critical bottlenecks:
1. **Relational Context Disconnect:** Semantic vector similarity retrieves passages based on lexical overlap rather than clinical relationships, missing multi-hop evidence across separate patient visits.
2. **Table & Chart Blindness:** Standard PDF parsing flattens structured laboratory tables, detaching numerical values from their test headers, normal reference bounds, and metric units.
3. **Hallucination Persistence:** Direct single-pass generation produces fluent but unverified claims when retrieved evidence is ambiguous.

This capstone project implements and empirically assesses two independent retrieval pipelines over an identical synthetic clinical corpus:
* **Pipeline A (Baseline Naive RAG):** Character-based chunking (500 chars), TF-IDF sparse lexical vector similarity indexing, and deterministic baseline sentence extraction.
* **Pipeline B (Multimodal Graph-Agentic Prototype):** Layout-aware parsing, in-memory clinical knowledge graph traversal with Cypher script export, native Python bounded state machine, and claim-to-source citation verification (live Neo4j cluster and local LLM generative integration scheduled for Semester 8).

---

## 2. PHASE-I (40% MILESTONE) WORK COMPLETED (SEMESTER 7)

During the 7th Semester, the project team achieved the declared Phase-I milestones:

### 2.1 Dataset Collection, Governance & Curation (Phase 0)
* Assembled a standardized clinical corpus comprising 5 longitudinal patient case cohorts (Type 2 Diabetes Nephropathy, HFrEF Heart Failure, NSCLC Oncology, ESBL E. coli Urosepsis, and Acute Ischemic Stroke) formatted with strict page delimiters and multi-column flowsheets.
* Curated a formal **50-query gold-standard benchmark** partitioned across three clinical complexity tiers:
  * 20 Single-Hop Factual Queries (e.g., initial dosage, chief complaints).
  * 20 Multi-Hop Relational Queries (e.g., drug-induced adverse events, treatment contraindications).
  * 10 Structured Table Extraction Queries (e.g., AST antibiograms, serial biomarker trends, NIHSS trajectories).
* Implemented strict Pydantic v2 data contracts (`data/eval_schema.py`) ensuring 100% provenance traceability (`doc_id`, `page_numbers`, `table_id`, `reference_claims`).

### 2.2 Complete Implementation of Baseline Pipeline A (Phase 1)
* Built `pipelines/pipeline_a/naive_loader.py` implementing 500-character fixed-window chunking with 50-character sliding overlap.
* Built `pipelines/pipeline_a/naive_vectorstore.py` providing TF-IDF sparse lexical vector indexing, serialized local JSON storage, and top-$k$ ($k=4$) cosine similarity search.
* Built `pipelines/pipeline_a/naive_pipeline.py` executing deterministic single-pass baseline sentence extraction with sub-5ms retrieval latency logging.
* Evaluated all 50 benchmark queries on Pipeline A; results persisted in `eval/baseline_results.json`.

### 2.3 Clinical Knowledge Graph Schema & Ingestion Protocol (Phase 2A)
* Formulated the clinical knowledge graph ontology consisting of 6 core node labels (`:Patient`, `:Encounter`, `:Diagnosis`, `:Medication`, `:LabTest`, `:Observation`) and 7 typed clinical relationships (`:PRESCRIBED`, `:DIAGNOSED_WITH`, `:INDICATES`, `:MEASURED`, `:CAUSED_ADVERSE_EVENT`, `:SWITCHED_TO`, `:SUSCEPTIBLE_TO`).
* Implemented in-memory graph construction and multi-hop traversal in `pipelines/pipeline_b/clinical_graph.py`.
* Generated production Neo4j Cypher DDL/DML scripts (`data/neo4j_ingest.cypher`) enforcing uniqueness constraints on entity IDs for planned Semester 8 database integration.

### 2.4 Clinical Research Console UI (Zero-AI Design System) (Phase 5A)
* Implemented a professional, data-dense clinical research console using FastAPI and standard web design tokens.
* Strictly rejected generic "AI-generated slop" design tropes (zero purple/indigo gradients, zero glassmorphism blurs, zero marketing clichés).
* Delivered a split-screen comparative workbench with real-time latency telemetry, chunk inspection, and a clickable provenance audit drawer.

---

## 3. PRELIMINARY EMPIRICAL COMPARISON (CUSTOM RAGAS-INSPIRED EVALUATION)

The project executed custom mathematical implementations of RAGAS metric formulations (token-overlap and TF-IDF cosine similarity) on the 50 matched benchmark queries:

The project executed the mathematical RAGAS evaluation harness on the 50 matched benchmark queries:

$$\text{Faithfulness}(a, C) = \frac{|\{s \in \text{Claims}(a) : C \text{ supports } s\}|}{|\text{Claims}(a)|}$$

$$\text{Context Recall}(G, C) = \frac{|\{g_j \in G : C \text{ supports } g_j\}|}{|G|}$$

### Table 1: Phase-I Empirical RAGAS Scorecard (50 Matched Benchmark Queries)
| Metric | Pipeline A (Naive Baseline) | Pipeline B (Prototype) | Delta ($\Delta$) | Status |
| :--- | :---: | :---: | :---: | :---: |
| **Faithfulness** | 48.0% | **97.0%** | **+49.0%** | Verified Gain |
| **Context Recall** | 70.7% | **77.5%** | **+6.8%** | Verified Gain |
| **Context Precision** | 85.9% | 53.0% | -32.9% | Trade-off (Hybrid Breadth) |
| **Answer Relevancy** | 0.5497 | **0.5742** | **+0.0245** | Verified Gain |

### Key Observation for Viva Panel:
Pipeline A failed significantly on **Multi-Hop Queries (25.0% Faithfulness)** due to fact fragmentation across chunks. Pipeline B achieved **95.0% Faithfulness** on multi-hop questions by utilizing relationship traversals.

---

## 4. PHASE-II (60% WORK) SCHEDULED FOR SEMESTER 8

The remaining 60% of the project scope is scheduled across the 8th Semester as follows:

| Month / Period | Planned Work Package | Deliverable / Milestone |
| :--- | :--- | :--- |
| **Month 1 (Weeks 1–4)** | **Neo4j Production Cluster & Dynamic Scaling:** Connect the graph engine to an active Neo4j Community / Aura instance; implement real-time APOC bulk loading. | Live Neo4j Graph DB Integration |
| **Month 2 (Weeks 5–8)** | **LangGraph Agent Refinement:** Expand the query reformulator with medical ontology lookups (UMLS / SNOMED CT subsets) and dynamic retry controls. | Advanced Self-Correcting Agent |
| **Month 3 (Weeks 9–11)** | **Comprehensive Component Ablation Study:** Run isolation tests evaluating the exact independent contributions of: (i) Graph traversal alone, (ii) Layout parser alone, (iii) Agentic loop alone. | Empirical Ablation Report & Plots |
| **Month 4 (Weeks 12–14)** | **Corpus Scale-Up & Final Dissertation:** Ingest 100+ multi-page clinical trials from PubMed Central Open Access; complete B.Tech thesis and conference paper submission. | Final B.Tech Dissertation Defense |

---

## 5. CONCLUSION (PHASE-I)

Phase-I successfully delivered a reproducible, fully verified baseline RAG system, an annotated 50-query clinical benchmark, and an operational non-AI research console. The empirical baseline confirms that naive vector search is insufficient for relational and tabular EHR queries. The project is strictly on schedule for full completion in Semester 8.

---

**Certified by Supervisor:**  
Name: ____________________________  
Designation: _____________________  
Signature: _______________________  
Date: ___________________________  

