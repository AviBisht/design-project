import json
import os
import math
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class DenseCosineVectorStore:
    
    def __init__(self, persist_path: str = "data/vectorstore_pipeline_a.json"):
        self.persist_path = Path(persist_path)
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words='english',
            norm='l2',
            sublinear_tf=True
        )
        self.documents: List[Dict[str, Any]] = []
        self.doc_vectors = None
        self.is_indexed = False

    def add_documents(self, chunks: List[Dict[str, Any]]) -> int:
        if not chunks:
            return 0
        self.documents = chunks
        corpus_texts = [c["content"] for c in chunks]
        self.doc_vectors = self.vectorizer.fit_transform(corpus_texts)
        self.is_indexed = True
        self.save()
        return len(chunks)

    def query(self, query_text: str, top_k: int = 4) -> List[Dict[str, Any]]:
        if not self.is_indexed or self.doc_vectors is None or len(self.documents) == 0:
            if self.persist_path.exists():
                self.load()
            else:
                return []

        q_vec = self.vectorizer.transform([query_text])
        similarities = cosine_similarity(q_vec, self.doc_vectors).flatten()

        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for rank, idx in enumerate(top_indices, start=1):
            score = float(similarities[idx])
            doc_data = dict(self.documents[idx])
            doc_data["score"] = round(score, 4)
            doc_data["rank"] = rank
            results.append(doc_data)

        return results

    def save(self):
        try:
            self.persist_path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "documents": self.documents,
                "vocabulary": list(self.vectorizer.vocabulary_.keys()) if hasattr(self.vectorizer, 'vocabulary_') else []
            }
            with open(self.persist_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except (OSError, PermissionError):
            pass

    def load(self):
        if not self.persist_path.exists():
            return False
        with open(self.persist_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.documents = data.get("documents", [])
        if self.documents:
            corpus_texts = [c["content"] for c in self.documents]
            self.doc_vectors = self.vectorizer.fit_transform(corpus_texts)
            self.is_indexed = True
        return True

if __name__ == "__main__":
    store = DenseCosineVectorStore()
    sample_docs = [
        {"chunk_id": "C1", "content": "Patient received Lisinopril for hypertension."},
        {"chunk_id": "C2", "content": "Emergency admission for severe chest pain and heart failure."}
    ]
    store.add_documents(sample_docs)
    res = store.query("Lisinopril dosage", top_k=1)
    print("Test retrieval result:", res)

