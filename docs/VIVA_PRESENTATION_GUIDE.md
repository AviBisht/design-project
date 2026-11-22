# B.Tech Major Project Phase-I: Viva Voce & Presentation Defense Guide
**Project:** Dual-Pipeline Clinical Intelligence Engine  
**Candidates:** Kush Garg (230000101053) & Avi Bisht (230000101027)  
**Affiliation:** VMSB Uttarakhand Technical University (UTU), Dehradun  

---

## 1. The 2-Minute Elevator Pitch (Opening Statement for Panel)

> *"Good morning respected evaluators and supervisor. Our project is the **Dual-Pipeline Clinical Intelligence Engine**.  
> In modern healthcare, Electronic Health Records (EHRs) contain fragmented notes, medication histories, and complex lab tables. Standard vector RAG systems suffer from three major flaws: **relational context disconnect** (splitting multi-hop facts), **table blindness** (flattening lab numbers away from headers), and **hallucination persistence**.  
> 
> For our **Phase-I (40% milestone)** in Semester 7, our objective was to establish a rigorous, reproducible empirical baseline:  
> 1. We assembled a 5-patient longitudinal clinical corpus and curated a gold-standard **50-query benchmark** with strict Pydantic provenance contracts.  
> 2. We built a fully operational **Naive RAG baseline (Pipeline A)** using 500-character chunking and TF-IDF sparse lexical vector indexing.  
> 3. We formalized our **clinical ontology**, built an in-memory graph traversal engine, and generated prototype Neo4j Cypher ingestion scripts.  
> 4. We engineered a **data-dense, clinical research console** with zero AI gimmicks.  
> 
> Our preliminary evaluation using custom RAGAS-inspired metric formulations proves that Pipeline A struggles severely with multi-hop queries (only 25% faithfulness), motivating our upcoming 8th Semester Phase-II work on live Neo4j database integration, local LLM deployment, and comprehensive component ablations."*

---

## 2. Live Demo Script (What to Show on `http://127.0.0.1:8000`)

1. **Step 1: Show the Benchmark Rail (Left Pane)**
   * Show the 50 queries categorized into **Single-Hop (20)**, **Multi-Hop (20)**, and **Table Extraction (10)**.
   * Explain: *"Every single query has reference claims and exact page/table provenance in `data/benchmark/gold_benchmark.json`."*
2. **Step 2: Demonstrate Pipeline A (Center-Left Column)**
   * Click a single-hop query (e.g., `Q-001: Lisinopril initial dosage`).
   * Show that Pipeline A finds the chunk and answers in ~3ms.
   * Explain: *"Pipeline A works well on direct keyword/semantic matches, functioning as our benchmark control."*
3. **Step 3: Demonstrate Multi-Hop Failure in Pipeline A vs. Pipeline B (Center-Right Column)**
   * Click a multi-hop query (e.g., `Q-021: Lisinopril adverse reaction leading to urgent intervention`).
   * Show how Pipeline A gets confused or returns incomplete facts.
   * Show Pipeline B traversing: `(Patient:P-101)-[:PRESCRIBED]->(Lisinopril)-[:CAUSED_ADVERSE_EVENT]->(Hyperkalemia)`.
   * Point out the **citation pill**: `[DOC-EHR-001, Table 1, p.3]`.
4. **Step 4: Show the Provenance Audit Drawer (Right Pane)**
   * Click the citation pill. Show how it immediately opens the original clinical encounter note and highlighted flowsheet table.
   * Highlight: *"No black box answers. Every clinical claim is traceable to an exact document and page."*

---

## 3. Top 8 Technical Viva Questions & Winning Answers

### Q1: *"Why did you use both Vector Search and Knowledge Graph? Why not just vector search?"*
**Your Answer:**  
> *"Vector search relies on semantic similarity in embedding space, which is excellent for finding loosely related prose. However, clinical logic requires **relational chains** across multiple encounters—for instance, connecting a medication prescribed on Day 1 to a critical potassium value on Day 7 and an emergency drug switch. Vector chunks isolate these facts. A knowledge graph explicitly encodes typed triples `(Drug)-[:CAUSED]->(Condition)` allowing multi-hop traversal that vectors cannot guarantee."*

### Q2: *"Why are you using a bounded state machine instead of simple linear chains?"*
**Your Answer:**  
> *"Linear chains follow a rigid, unidirectional pipeline. Clinical retrieval requires dynamic control flow: if retrieved evidence is inadequate, the system must grade the context, reformulate the query, and re-retrieve under a **bounded state machine**. In Phase-I, we implemented this cyclic control flow using a deterministic native Python state machine with strict halting guardrails (max 1 retry), preventing infinite loops. In Semester 8, this architecture will be migrated to the formal LangGraph DAG framework."*

### Q3: *"What is RAGAS and how does it evaluate your system?"*
**Your Answer:**  
> *"RAGAS is an industry-standard evaluation framework for RAG systems. For our Phase-I prototype, we implemented custom mathematical functions modeling its core metric formulations:  
> 1. **Faithfulness:** Proportion of generated sentence claims supported by retrieved context.  
> 2. **Context Recall:** Proportion of reference gold claims captured in context.  
> 3. **Context Precision:** Signal-to-noise ratio of retrieved evidence.  
> 4. **Answer Relevancy:** TF-IDF cosine similarity between question and answer text.  
> This allows fully deterministic, offline evaluation without reliance on external paid LLM judge endpoints."*

### Q4: *"Why did you design the web interface this way? Why not use modern gradient cards?"*
**Your Answer:**  
> *"We conducted research into clinical and scientific UI standards (such as NCBI PubMed, UpToDate, and Epic Systems). Generic 'AI-generated templates' rely on purple/indigo gradients and translucent glassmorphism that impair contrast and readability in high-stakes environments. We engineered a data-dense, dark zinc console with tabular monospace fonts, split-screen inspection, and functional status colors (Emerald for verified claims, Amber for rewrites, Carmine for hallucinations)."*

### Q5: *"Is this system intended to diagnose patients in a hospital?"*
**Your Answer:**  
> *"No, sir/ma'am. We explicitly state that this is an **information retrieval and clinical research-assistance system**, not a diagnostic medical device. It assists clinicians and researchers in querying dense EHR documents with verified source citations."*

### Q6: *"How did you handle patient privacy and HIPAA compliance?"*
**Your Answer:**  
> *"All clinical records in our corpus are fully de-identified synthetic cohorts. The current Phase-I prototype runs entirely locally with zero external network transmission, storing serialized local TF-IDF indexes and in-memory graphs. Local LLM inference via Ollama is scheduled for Semester 8."*

### Q7: *"What exactly have you completed for this 7th Semester, and what is left for the 8th Semester?"*
**Your Answer:**  
> *"In accordance with the 40% Phase-I requirement, we completed:  
> 1. Clinical corpus curation and 50 gold-standard evaluation benchmarks with Pydantic contracts.  
> 2. The full working Naive RAG baseline (Pipeline A) with serialized local TF-IDF vector indexing.  
> 3. The clinical ontology design, in-memory traversal engine, and Neo4j Cypher ingestion scripts.  
> 4. The research console UI prototype.  
> For the remaining 60% in Semester 8, we will connect to an active Neo4j cluster, deploy local quantized LLMs, conduct formal component ablations, scale the corpus to 100+ records from MIMIC-IV, and author our final thesis."*

### Q8: *"Why did Context Precision decrease in Pipeline B in your preliminary table?"*
**Your Answer:**  
> *"That is an honest, mathematically sound trade-off. Pipeline B performs hybrid retrieval—combining dense vectors with multi-hop graph triples and structured tables. Because it retrieves broader contextual evidence to ensure complete multi-hop coverage (boosting Faithfulness from 48% to 97%), the denominator in precision is larger. In Semester 8, we will optimize rank fusion (RRF) to prune non-critical hops and balance precision."*

