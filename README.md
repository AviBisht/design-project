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


ble IDs) in favor of standard medical ontology mappings (UMLS / SNOMED CT subsets).
3. **Corpus Generalization & Held-Out Testing:** Evaluate the system on independently created synthetic patient records (Track C) that were not seen during rule or graph development.
4. **Query Robustness & Paraphrase Evaluation:** Test on unseen query paraphrases, clinical abbreviations, and colloquial phrasing (Track B).
5. **Negative-Control & Conflict Evaluation:** Incorporate queries where evidence is missing or contradictory to evaluate whether the pipeline appropriately refuses to answer.
6. **Defensible Evaluation Harness:** Introduce standardized NLI entailment models (e.g., DeBERTa-MNLI) and enforce fixed context token budgets across both pipelines for unbiased comparative benchmarking.
