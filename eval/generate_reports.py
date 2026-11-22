import json
import csv
from pathlib import Path

def generate_reports():
    metrics_path = Path("eval/comparative_metrics.json")
    if not metrics_path.exists():
        print("eval/comparative_metrics.json does not exist. Run Phase 4 evaluation first.")
        return

    with open(metrics_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    summary = data["summary"]
    items = data["query_evaluations"]

    # 1. Generate Academic CSV Export for Analysis & Plotting
    csv_path = Path("eval/benchmark_detailed_results.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Query_ID", "Query_Type", "Query_Text",
            "PipeA_Faithfulness", "PipeA_ContextRecall", "PipeA_ContextPrecision", "PipeA_AnswerRelevancy",
            "PipeB_Faithfulness", "PipeB_ContextRecall", "PipeB_ContextPrecision", "PipeB_AnswerRelevancy",
            "Delta_Faithfulness", "Delta_ContextRecall"
        ])

        for q in items:
            mA = q["pipeline_a"]["metrics"]
            mB = q["pipeline_b"]["metrics"]
            writer.writerow([
                q["query_id"],
                q["query_type"],
                q["query_text"],
                mA["faithfulness"], mA["context_recall"], mA["context_precision"], mA["answer_relevancy"],
                mB["faithfulness"], mB["context_recall"], mB["context_precision"], mB["answer_relevancy"],
                round(mB["faithfulness"] - mA["faithfulness"], 4),
                round(mB["context_recall"] - mA["context_recall"], 4)
            ])

    print(f"[EXPORT] Generated detailed CSV evaluation dataset: {csv_path}")

    # 2. Generate LaTeX Table Snippets for B.Tech Final Thesis / Project Report
    latex_path = Path("eval/latex_evaluation_tables.tex")
    latex_code = f"""% =========================================================================
% DUAL-PIPELINE CLINICAL INTELLIGENCE ENGINE: COMPARATIVE RAGAS RESULTS
% Auto-generated for VMSB UTU Final Year B.Tech Project Report
% =========================================================================

\\begin{{table}}[htbp]
\\centering
\\caption{{Empirical RAGAS Performance Comparison Across 50 Matched Benchmark Queries}}
\\label{{tab:ragas_comparison}}
\\begin{{tabular}}{{lcccc}}
\\hline
\\textbf{{Evaluation Metric}} & \\textbf{{Pipeline A (Naive)}} & \\textbf{{Pipeline B (Graph-Agentic)}} & \\textbf{{Delta ($\\Delta$)}} & \\textbf{{Relative Gain}} \\\\
\\hline
Faithfulness          & {summary['overall']['pipeline_a']['faithfulness']*100:.1f}\\% & {summary['overall']['pipeline_b']['faithfulness']*100:.1f}\\% & +{(summary['overall']['pipeline_b']['faithfulness'] - summary['overall']['pipeline_a']['faithfulness'])*100:.1f}\\% & +{((summary['overall']['pipeline_b']['faithfulness'] - summary['overall']['pipeline_a']['faithfulness'])/summary['overall']['pipeline_a']['faithfulness'])*100:.1f}\\% \\\\
Context Recall        & {summary['overall']['pipeline_a']['context_recall']*100:.1f}\\% & {summary['overall']['pipeline_b']['context_recall']*100:.1f}\\% & +{(summary['overall']['pipeline_b']['context_recall'] - summary['overall']['pipeline_a']['context_recall'])*100:.1f}\\% & +{((summary['overall']['pipeline_b']['context_recall'] - summary['overall']['pipeline_a']['context_recall'])/summary['overall']['pipeline_a']['context_recall'])*100:.1f}\\% \\\\
Context Precision     & {summary['overall']['pipeline_a']['context_precision']*100:.1f}\\% & {summary['overall']['pipeline_b']['context_precision']*100:.1f}\\% & {(summary['overall']['pipeline_b']['context_precision'] - summary['overall']['pipeline_a']['context_precision'])*100:.1f}\\% & --- \\\\
Answer Relevancy      & {summary['overall']['pipeline_a']['answer_relevancy']:.4f} & {summary['overall']['pipeline_b']['answer_relevancy']:.4f} & +{(summary['overall']['pipeline_b']['answer_relevancy'] - summary['overall']['pipeline_a']['answer_relevancy']):.4f} & +{((summary['overall']['pipeline_b']['answer_relevancy'] - summary['overall']['pipeline_a']['answer_relevancy'])/summary['overall']['pipeline_a']['answer_relevancy'])*100:.1f}\\% \\\\
\\hline
\\end{{tabular}}
\\end{{table}}

\\begin{{table}}[htbp]
\\centering
\\caption{{Sub-Category Retrieval Performance by Clinical Query Complexity}}
\\label{{tab:subcategory_breakdown}}
\\begin{{tabular}}{{llccc}}
\\hline
\\textbf{{Query Category}} & \\textbf{{Metric}} & \\textbf{{Pipeline A}} & \\textbf{{Pipeline B}} & \\textbf{{$\\Delta$}} \\\\
\\hline
\\multirow{{2}}{{*}}{{Single-Hop Factual ($N=20$)}} 
  & Context Recall & {summary['single_hop']['pipeline_a']['context_recall']*100:.1f}\\% & {summary['single_hop']['pipeline_b']['context_recall']*100:.1f}\\% & +{(summary['single_hop']['pipeline_b']['context_recall'] - summary['single_hop']['pipeline_a']['context_recall'])*100:.1f}\\% \\\\
  & Faithfulness   & {summary['single_hop']['pipeline_a']['faithfulness']*100:.1f}\\% & {summary['single_hop']['pipeline_b']['faithfulness']*100:.1f}\\% & +{(summary['single_hop']['pipeline_b']['faithfulness'] - summary['single_hop']['pipeline_a']['faithfulness'])*100:.1f}\\% \\\\
\\hline
\\multirow{{2}}{{*}}{{Multi-Hop Relational ($N=20$)}} 
  & Context Recall & {summary['multi_hop']['pipeline_a']['context_recall']*100:.1f}\\% & {summary['multi_hop']['pipeline_b']['context_recall']*100:.1f}\\% & +{(summary['multi_hop']['pipeline_b']['context_recall'] - summary['multi_hop']['pipeline_a']['context_recall'])*100:.1f}\\% \\\\
  & Faithfulness   & {summary['multi_hop']['pipeline_a']['faithfulness']*100:.1f}\\% & {summary['multi_hop']['pipeline_b']['faithfulness']*100:.1f}\\% & +{(summary['multi_hop']['pipeline_b']['faithfulness'] - summary['multi_hop']['pipeline_a']['faithfulness'])*100:.1f}\\% \\\\
\\hline
\\multirow{{2}}{{*}}{{Structured Tables ($N=10$)}} 
  & Context Recall & {summary['table_extraction']['pipeline_a']['context_recall']*100:.1f}\\% & {summary['table_extraction']['pipeline_b']['context_recall']*100:.1f}\\% & {(summary['table_extraction']['pipeline_b']['context_recall'] - summary['table_extraction']['pipeline_a']['context_recall'])*100:.1f}\\% \\\\
  & Faithfulness   & {summary['table_extraction']['pipeline_a']['faithfulness']*100:.1f}\\% & {summary['table_extraction']['pipeline_b']['faithfulness']*100:.1f}\\% & +{(summary['table_extraction']['pipeline_b']['faithfulness'] - summary['table_extraction']['pipeline_a']['faithfulness'])*100:.1f}\\% \\\\
\\hline
\\end{{tabular}}
\\end{{table}}
"""

    with open(latex_path, "w", encoding="utf-8") as f:
        f.write(latex_code)

    print(f"[EXPORT] Generated publication-ready LaTeX tables: {latex_path}")

if __name__ == "__main__":
    generate_reports()

