import time
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from pipelines.pipeline_a.naive_loader import NaiveDocumentLoader
from pipelines.pipeline_a.naive_vectorstore import DenseCosineVectorStore

class NaiveRAGPipeline:
    
    def __init__(self, corpus_dir: str = "data/corpus", persist_db: str = "data/vectorstore_pipeline_a.json"):
        self.corpus_dir = Path(corpus_dir)
        self.loader = NaiveDocumentLoader(chunk_size=500, chunk_overlap=50)
        self.vector_store = DenseCosineVectorStore(persist_path=persist_db)
        self.is_initialized = False

    def initialize(self, force_reload: bool = False):
        if not force_reload and self.vector_store.load():
            self.is_initialized = True
            return
        chunks = self.loader.load_corpus(self.corpus_dir)
        self.vector_store.add_documents(chunks)
        self.is_initialized = True

    def query(self, query_text: str, top_k: int = 4) -> Dict[str, Any]:
        if not self.is_initialized:
            self.initialize()

        start_time = time.perf_counter()
        retrieved_chunks = self.vector_store.query(query_text, top_k=top_k)
        retrieval_latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        context_text = "\n\n".join([f"[Source: {c['chunk_id']} | Doc: {c['doc_id']} Page: {c['page_number']}]\n{c['content']}" for c in retrieved_chunks])

        gen_start = time.perf_counter()
        answer = self._generate_answer(query_text, context_text, retrieved_chunks)
        generation_latency_ms = round((time.perf_counter() - gen_start) * 1000, 2)

        return {
            "pipeline": "pipeline_a",
            "query": query_text,
            "answer": answer,
            "retrieved_contexts": [c["content"] for c in retrieved_chunks],
            "retrieved_chunk_metadata": [
                {
                    "chunk_id": c["chunk_id"],
                    "doc_id": c["doc_id"],
                    "page_number": c["page_number"],
                    "score": c.get("score", 0.0),
                    "rank": c.get("rank", idx + 1),
                    "content": c["content"]
                }
                for idx, c in enumerate(retrieved_chunks)
            ],
            "metrics": {
                "retrieval_latency_ms": retrieval_latency_ms,
                "generation_latency_ms": generation_latency_ms,
                "total_latency_ms": round(retrieval_latency_ms + generation_latency_ms, 2),
                "chunks_retrieved_count": len(retrieved_chunks)
            }
        }

    def _generate_answer(self, query: str, context: str, chunks: List[Dict[str, Any]]) -> str:
        
        if not chunks or max([c.get("score", 0.0) for c in chunks], default=0) < 0.15:
            return "Based on the retrieved baseline context, insufficient evidence was found to answer this question."

        top_chunk = chunks[0]["content"]
        sentences = [s.strip() for s in top_chunk.replace("\n", " ").split(".") if s.strip()]
        query_words = set(query.lower().split())
        best_sentence = sentences[0] if sentences else top_chunk[:150]
        max_overlap = -1
        for s in sentences:
            overlap = len(set(s.lower().split()) & query_words)
            if overlap > max_overlap:
                max_overlap = overlap
                best_sentence = s

        return f"{best_sentence}."

if __name__ == "__main__":
    pipeline = NaiveRAGPipeline()
    pipeline.initialize(force_reload=True)
    res = pipeline.query("What was patient P-101's initial dose of Lisinopril?")
    print("Baseline Query Output:")
    print(json.dumps(res, indent=2))

