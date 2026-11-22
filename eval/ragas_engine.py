import json
import math
import re
from pathlib import Path
from typing import Dict, Any, List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class RagasEvaluator:
    """
    RAGAS Evaluation Framework:
    Implements mathematical definitions of Faithfulness, Context Recall, Context Precision, and Answer Relevancy.
    Evaluates Pipeline A (Naive baseline) vs. Pipeline B (Graph-Agentic) over identical gold benchmarks.
    """
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english', norm='l2')

    def evaluate_faithfulness(self, generated_answer: str, retrieved_contexts: List[str]) -> float:
        """
        Faithfulness(a, C) = |{s in Claims(a) : C supports s}| / |Claims(a)|
        """
        if not generated_answer or not retrieved_contexts:
            return 0.0

        # Atomic claim decomposition
        sentences = [s.strip() for s in generated_answer.split(".") if len(s.strip()) > 5]
        # Remove citation annotations like [DOC-EHR-001, p.2] for claim verification
        clean_sentences = [re.sub(r"\[.*?\]", "", s).strip() for s in sentences]
        clean_sentences = [s for s in clean_sentences if len(s) > 5]

        if not clean_sentences:
            return 1.0

        full_context = " ".join(retrieved_contexts).lower()

        supported_count = 0
        for claim in clean_sentences:
            tokens = [w.lower() for w in re.findall(r"\b[A-Za-z0-9\-]+\b", claim) if len(w) > 3]
            if not tokens:
                supported_count += 1
                continue
            matched = sum(1 for t in tokens if t in full_context)
            if (matched / len(tokens)) >= 0.65:
                supported_count += 1

        return round(supported_count / len(clean_sentences), 4)

    def evaluate_context_recall(self, reference_claims: List[str], retrieved_contexts: List[str]) -> float:
        """
        Context Recall(G, C) = |{g_j in G : C supports g_j}| / |G|
        """
        if not reference_claims:
            return 1.0
        if not retrieved_contexts:
            return 0.0

        full_context = " ".join(retrieved_contexts).lower()
        supported_count = 0

        for g in reference_claims:
            tokens = [w.lower() for w in re.findall(r"\b[A-Za-z0-9\-]+\b", g) if len(w) > 3]
            if not tokens:
                supported_count += 1
                continue
            matched = sum(1 for t in tokens if t in full_context)
            if (matched / len(tokens)) >= 0.60:
                supported_count += 1

        return round(supported_count / len(reference_claims), 4)

    def evaluate_context_precision(self, retrieved_contexts: List[str], reference_answer: str) -> float:
        """
        Context Precision(C, G) = [sum_{i=1}^k (P@i * rel_i)] / [sum_{i=1}^k rel_i]
        """
        if not retrieved_contexts:
            return 0.0

        ref_tokens = set([w.lower() for w in re.findall(r"\b[A-Za-z0-9\-]+\b", reference_answer) if len(w) > 3])
        if not ref_tokens:
            return 1.0

        rel_flags = []
        for c in retrieved_contexts:
            c_tokens = set([w.lower() for w in re.findall(r"\b[A-Za-z0-9\-]+\b", c) if len(w) > 3])
            overlap = len(ref_tokens & c_tokens)
            rel_flags.append(1 if overlap >= 2 else 0)

        total_rel = sum(rel_flags)
        if total_rel == 0:
            return 0.0

        cumulative_precisions = []
        rel_so_far = 0
        for i, rel in enumerate(rel_flags, start=1):
            if rel == 1:
                rel_so_far += 1
                cumulative_precisions.append(rel_so_far / i)

        return round(sum(cumulative_precisions) / total_rel, 4)

    def evaluate_answer_relevancy(self, query: str, generated_answer: str) -> float:
        """
        Answer Relevancy(q, a) = cosine similarity between question embedding and answer representation.
        """
        if not query or not generated_answer:
            return 0.0

        clean_ans = re.sub(r"\[.*?\]", "", generated_answer).strip()
        try:
            tfidf = self.vectorizer.fit_transform([query, clean_ans])
            sim = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
            # Normalization scale
            score = 0.5 + (float(sim) * 0.5) if sim > 0 else 0.5
            return round(min(score, 1.0), 4)
        except Exception:
            return 0.5

    def evaluate_item(self, query_item: Dict[str, Any], result_item: Dict[str, Any]) -> Dict[str, float]:
        q_text = query_item["query_text"]
        ref_ans = query_item["reference_answer"]
        ref_claims = query_item.get("reference_claims", [ref_ans])

        gen_ans = result_item.get("generated_answer", result_item.get("answer", ""))
        contexts = result_item.get("retrieved_contexts", [])

        # Include table representations and graph facts if present in Pipeline B
        if "graph_evidence" in result_item and result_item["graph_evidence"]:
            contexts = contexts + result_item["graph_evidence"]

        faithfulness = self.evaluate_faithfulness(gen_ans, contexts)
        context_recall = self.evaluate_context_recall(ref_claims, contexts)
        context_precision = self.evaluate_context_precision(contexts, ref_ans)
        answer_relevancy = self.evaluate_answer_relevancy(q_text, gen_ans)

        return {
            "faithfulness": faithfulness,
            "context_recall": context_recall,
            "context_precision": context_precision,
            "answer_relevancy": answer_relevancy
        }

def run_comparative_benchmark(
    benchmark_file: str = "data/benchmark/gold_benchmark.json",
    baseline_file: str = "eval/baseline_results.json",
    advanced_file: str = "eval/advanced_results.json",
    out_file: str = "eval/comparative_metrics.json"
) -> Dict[str, Any]:
    with open(benchmark_file, "r", encoding="utf-8") as f:
        benchmark = json.load(f)["queries"]
    with open(baseline_file, "r", encoding="utf-8") as f:
        baseline_results = json.load(f)["results"]
    with open(advanced_file, "r", encoding="utf-8") as f:
        advanced_results = json.load(f)["results"]

    evaluator = RagasEvaluator()

    baseline_map = {r["query_id"]: r for r in baseline_results}
    advanced_map = {r["query_id"]: r for r in advanced_results}

    item_evaluations = []

    # Category accumulators
    cat_metrics = {
        "overall": {"pipeline_a": [], "pipeline_b": []},
        "single-hop": {"pipeline_a": [], "pipeline_b": []},
        "multi-hop": {"pipeline_a": [], "pipeline_b": []},
        "table-extraction": {"pipeline_a": [], "pipeline_b": []}
    }

    for q in benchmark:
        qid = q["query_id"]
        qtype = q["query_type"]

        res_a = baseline_map.get(qid, {})
        res_b = advanced_map.get(qid, {})

        metrics_a = evaluator.evaluate_item(q, res_a)
        metrics_b = evaluator.evaluate_item(q, res_b)

        item_evaluations.append({
            "query_id": qid,
            "query_type": qtype,
            "query_text": q["query_text"],
            "pipeline_a": {
                "generated_answer": res_a.get("generated_answer", ""),
                "metrics": metrics_a
            },
            "pipeline_b": {
                "generated_answer": res_b.get("generated_answer", ""),
                "citations": res_b.get("citations", []),
                "metrics": metrics_b
            }
        })

        cat_metrics["overall"]["pipeline_a"].append(metrics_a)
        cat_metrics["overall"]["pipeline_b"].append(metrics_b)
        cat_metrics[qtype]["pipeline_a"].append(metrics_a)
        cat_metrics[qtype]["pipeline_b"].append(metrics_b)

    def compute_averages(m_list: List[Dict[str, float]]) -> Dict[str, float]:
        if not m_list:
            return {"faithfulness": 0.0, "context_recall": 0.0, "context_precision": 0.0, "answer_relevancy": 0.0}
        n = len(m_list)
        return {
            "faithfulness": round(sum(m["faithfulness"] for m in m_list) / n, 4),
            "context_recall": round(sum(m["context_recall"] for m in m_list) / n, 4),
            "context_precision": round(sum(m["context_precision"] for m in m_list) / n, 4),
            "answer_relevancy": round(sum(m["answer_relevancy"] for m in m_list) / n, 4)
        }

    summary_report = {
        "summary": {
            "overall": {
                "pipeline_a": compute_averages(cat_metrics["overall"]["pipeline_a"]),
                "pipeline_b": compute_averages(cat_metrics["overall"]["pipeline_b"])
            },
            "single_hop": {
                "pipeline_a": compute_averages(cat_metrics["single-hop"]["pipeline_a"]),
                "pipeline_b": compute_averages(cat_metrics["single-hop"]["pipeline_b"])
            },
            "multi_hop": {
                "pipeline_a": compute_averages(cat_metrics["multi-hop"]["pipeline_a"]),
                "pipeline_b": compute_averages(cat_metrics["multi-hop"]["pipeline_b"])
            },
            "table_extraction": {
                "pipeline_a": compute_averages(cat_metrics["table-extraction"]["pipeline_a"]),
                "pipeline_b": compute_averages(cat_metrics["table-extraction"]["pipeline_b"])
            }
        },
        "query_evaluations": item_evaluations
    }

    Path(out_file).parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(summary_report, f, indent=2)

    return summary_report

if __name__ == "__main__":
    report = run_comparative_benchmark()
    print("Comparative RAGAS Benchmark Complete.")
    print("Overall Pipeline A vs Pipeline B:")
    print(json.dumps(report["summary"]["overall"], indent=2))

