import time
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from pipelines.pipeline_b.layout_parser import LayoutAwareParser, ExtractedTable
from pipelines.pipeline_b.clinical_graph import build_clinical_graph_from_corpus, ClinicalKnowledgeGraph
from pipelines.pipeline_a.naive_vectorstore import DenseCosineVectorStore

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_CORPUS = (PROJECT_ROOT / "data" / "corpus").resolve()
DEFAULT_DB = (PROJECT_ROOT / "data" / "vectorstore_pipeline_b.json").resolve()

class HybridAgenticRAGPipeline:
    def __init__(self, corpus_dir: Optional[str] = None):
        self.corpus_dir = Path(corpus_dir).resolve() if corpus_dir else DEFAULT_CORPUS
        self.parser = LayoutAwareParser()
        self.graph: ClinicalKnowledgeGraph = build_clinical_graph_from_corpus(str(self.corpus_dir))
        self.vector_store = DenseCosineVectorStore(persist_path=str(DEFAULT_DB))
        self.parsed_docs: Dict[str, Any] = {}
        self.is_initialized = False

    def initialize(self, force_reload: bool = False):
        if not force_reload and self.vector_store.load() and self.parsed_docs:
            self.is_initialized = True
            return

        chunks = []
        for cf in sorted(self.corpus_dir.glob("*.md")):
            doc = self.parser.parse_document(cf)
            self.parsed_docs[doc["doc_id"]] = doc
            for idx, sec in enumerate(doc["sections"]):
                chunks.append({
                    "chunk_id": f"{doc['doc_id']}_S{idx:02d}",
                    "doc_id": doc["doc_id"],
                    "page_number": sec["page_number"],
                    "content": sec["content"],
                    "type": sec["type"],
                    "table_id": sec.get("table_id")
                })

        self.vector_store.add_documents(chunks)
        self.is_initialized = True

    def query(self, query_text: str) -> Dict[str, Any]:
        
        if not self.is_initialized:
            self.initialize()

        start_time = time.perf_counter()

        state = {
            "query": query_text,
            "current_query": query_text,
            "attempt_counter": 0,
            "rewritten_query": None,
            "vector_evidence": [],
            "graph_evidence": [],
            "table_evidence": [],
            "context_adequacy": 0.0,
            "draft_answer": "",
            "verified_claims": [],
            "final_answer": "",
            "citations": [],
            "agent_path": []
        }

        state = self._node_hybrid_retriever(state)

        state = self._node_context_grader(state)

        if state["context_adequacy"] < 0.50 and state["attempt_counter"] == 0:
            state = self._node_query_reformulator(state)
            state = self._node_hybrid_retriever(state)
            state = self._node_context_grader(state)

        state = self._node_answer_generator(state)

        state = self._node_claim_verifier(state)

        total_latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return {
            "pipeline": "pipeline_b",
            "query": query_text,
            "rewritten_query": state.get("rewritten_query"),
            "answer": state["final_answer"],
            "verified_claims": state["verified_claims"],
            "citations": state["citations"],
            "agent_path": state["agent_path"],
            "retrieved_contexts": [v["content"] for v in state["vector_evidence"]] + [t["table_object"].to_markdown() for t in state["table_evidence"]],
            "graph_evidence": [g["readable_fact"] for g in state["graph_evidence"]],
            "table_evidence": [t["table_id"] for t in state["table_evidence"]],
            "metrics": {
                "total_latency_ms": total_latency_ms,
                "context_adequacy": round(state["context_adequacy"], 2),
                "attempt_count": state["attempt_counter"],
                "verified_claims_count": len([c for c in state["verified_claims"] if c["supported"]]),
                "unsupported_claims_count": len([c for c in state["verified_claims"] if not c["supported"]])
            }
        }

    def _node_hybrid_retriever(self, state: Dict[str, Any]) -> Dict[str, Any]:
        state["agent_path"].append("hybrid_retriever")
        q = state["current_query"]

        v_results = self.vector_store.query(q, top_k=6)
        state["vector_evidence"] = v_results

        query_tokens = [w.strip() for w in re.findall(r"\b[A-Za-z0-9\-]+\b", q)]
        matched_paths = []
        for token in query_tokens:
            if len(token) >= 3:
                traversals = self.graph.multi_hop_traverse(token, max_hops=2)
                matched_paths.extend(traversals)

        unique_paths = {}
        for p in matched_paths:
            fact = p["readable_fact"]
            if fact not in unique_paths:
                unique_paths[fact] = p
        state["graph_evidence"] = list(unique_paths.values())[:10]

        table_matches = []
        for doc in self.parsed_docs.values():
            for tbl in doc["tables"]:
                t_str = (tbl.title + " " + " ".join(tbl.headers) + " " + " ".join([" ".join(r) for r in tbl.rows])).lower()
                overlap = sum(1 for tok in query_tokens if tok.lower() in t_str and len(tok) > 3)
                if overlap >= 2:
                    table_matches.append({
                        "table_id": tbl.table_id,
                        "title": tbl.title,
                        "doc_id": tbl.doc_id,
                        "page_number": tbl.page_number,
                        "table_object": tbl,
                        "overlap": overlap
                    })
        table_matches.sort(key=lambda x: x["overlap"], reverse=True)
        state["table_evidence"] = table_matches[:2]

        return state

    def _node_context_grader(self, state: Dict[str, Any]) -> Dict[str, Any]:
        state["agent_path"].append("context_grader")
        q = state["current_query"]
        q_tokens = set([w.lower() for w in re.findall(r"\b[A-Za-z0-9\-]+\b", q) if len(w) > 2])

        all_text = " ".join([c["content"] for c in state["vector_evidence"]])
        all_graph = " ".join([g["readable_fact"] for g in state["graph_evidence"]])
        all_table = " ".join([t["title"] + " " + " ".join(t["table_object"].headers) for t in state["table_evidence"]])

        combined_evidence = (all_text + " " + all_graph + " " + all_table).lower()
        if not q_tokens:
            state["context_adequacy"] = 1.0
            return state

        covered = sum(1 for tok in q_tokens if tok in combined_evidence)
        coverage_ratio = covered / len(q_tokens)
        top_vector_score = max([c.get("score", 0.0) for c in state["vector_evidence"]], default=0.0)

        if top_vector_score < 0.28 or coverage_ratio < 0.60:
            state["context_adequacy"] = round(min(top_vector_score, coverage_ratio), 3)
        else:
            state["context_adequacy"] = round((top_vector_score + coverage_ratio) / 2.0, 3)

        return state

    def _node_query_reformulator(self, state: Dict[str, Any]) -> Dict[str, Any]:
        
        state["agent_path"].append("query_reformulator")
        state["attempt_counter"] += 1
        q = state["query"]

        synonym_map = {
            "potassium": "potassium serum K+ hyperkalemia Table 1",
            "creatinine": "serum creatinine eGFR acute kidney injury AKI",
            "heart failure": "HFrEF LVEF Sacubitril Valsartan Carvedilol NT-proBNP",
            "neutropenia": "Absolute Neutrophil Count ANC febrile neutropenia Filgrastim",
            "antibiotic": "ESBL Escherichia coli Ceftriaxone Meropenem AST susceptibility",
            "stroke": "NIHSS Tenecteplase thrombolysis Atrial Fibrillation Apixaban"
        }

        expanded_terms = []
        for k, v in synonym_map.items():
            if k in q.lower():
                expanded_terms.append(v)

        if expanded_terms:
            rewritten = f"{q} {' '.join(expanded_terms)}"
        else:
            rewritten = f"{q} clinical laboratory examination flowsheet"

        state["rewritten_query"] = rewritten
        state["current_query"] = rewritten
        return state

    def _node_answer_generator(self, state: Dict[str, Any]) -> Dict[str, Any]:
        state["agent_path"].append("answer_generator")
        q = state["query"]

        if state["table_evidence"]:
            top_tbl = state["table_evidence"][0]["table_object"]
            tbl_md = top_tbl.to_markdown()

            for row in top_tbl.rows:
                row_str = " ".join(row).lower()
                q_words = [w.lower() for w in re.findall(r"\b[A-Za-z0-9\-\:]+\b", q) if len(w) > 3]
                matches = sum(1 for w in q_words if w in row_str)
                if matches >= 1:
                    row_dict = dict(zip(top_tbl.headers, row))
                    row_summary = ", ".join([f"{k}: {v}" for k, v in row_dict.items()])
                    state["draft_answer"] = f"According to {top_tbl.table_id} ({top_tbl.title}): {row_summary}."
                    return state

        if len(state["graph_evidence"]) >= 2:
            facts = [g["readable_fact"] for g in state["graph_evidence"][:3]]
            connected_facts = "; ".join(facts)
            state["draft_answer"] = f"Clinical relationship analysis reveals: {connected_facts}."
            return state

        if state["vector_evidence"]:
            top_content = state["vector_evidence"][0]["content"]
            sentences = [s.strip() for s in top_content.replace("\n", " ").split(".") if len(s.strip()) > 10]
            if sentences:
                state["draft_answer"] = f"{sentences[0]}."
            else:
                state["draft_answer"] = top_content[:200]
            return state

        state["draft_answer"] = "Insufficient supported evidence found in clinical corpus."
        return state

    def _node_claim_verifier(self, state: Dict[str, Any]) -> Dict[str, Any]:
        state["agent_path"].append("claim_verifier")
        draft = state["draft_answer"]
        sentences = [s.strip() for s in draft.split(".") if len(s.strip()) > 5]

        evidence_corpus = []
        citations = []

        for v in state["vector_evidence"]:
            evidence_corpus.append(v["content"].lower())
            citations.append(f"[{v['doc_id']}, p.{v['page_number']}]")

        for g in state["graph_evidence"]:
            evidence_corpus.append(g["readable_fact"].lower())
            props = g.get("provenance", {})
            if "doc_id" in props:
                citations.append(f"[{props['doc_id']}, p.{props.get('page', 1)}]")

        for t in state["table_evidence"]:
            tbl = t["table_object"]
            evidence_corpus.append(tbl.to_markdown().lower())
            citations.append(f"[{tbl.doc_id}, {tbl.table_id}, p.{tbl.page_number}]")

        full_evidence = " ".join(evidence_corpus)

        verified_claims = []
        grounded_sentences = []

        for s in sentences:
            s_tokens = [w.lower() for w in re.findall(r"\b[A-Za-z0-9\-]+\b", s) if len(w) > 3]
            match_ratio = (sum(1 for tok in s_tokens if tok in full_evidence) / len(s_tokens)) if s_tokens else 1.0

            is_supported = match_ratio >= 0.70
            chosen_citation = citations[0] if citations else "[Corpus]"

            verified_claims.append({
                "claim": s,
                "supported": is_supported,
                "confidence": round(match_ratio, 2),
                "citation": chosen_citation if is_supported else None
            })

            if is_supported:
                grounded_sentences.append(f"{s} {chosen_citation}")
            else:
                grounded_sentences.append(f"[Pruned unverified statement: '{s[:40]}...']")

        state["verified_claims"] = verified_claims
        state["citations"] = list(dict.fromkeys(citations))
        state["final_answer"] = " ".join(grounded_sentences)
        return state

if __name__ == "__main__":
    pipe_b = HybridAgenticRAGPipeline()
    pipe_b.initialize(force_reload=True)
    out = pipe_b.query("What was patient P-101's initial dose of Lisinopril?")
    print("Pipeline B Query Output:")
    print("Answer:", out["answer"])
    print("Agent Path:", out["agent_path"])
    print("Citations:", out["citations"])
