import json
import logging
from pathlib import Path
from typing import Any

from rag.engine import AdvancedRAGEngine
from rag.evaluation.evaluator import RAGEvaluator

logger = logging.getLogger("PredictX.RAGBenchmark")


class RAGBenchmarkSuite:
    """
    Automated Benchmark Suite for industrial RAG evaluation.
    Computes Hit Rate@K, Mean Reciprocal Rank (MRR), and RAG Triad metrics across golden datasets.
    """

    def __init__(self, evaluator: RAGEvaluator | None = None):
        self.evaluator = evaluator or RAGEvaluator()

    def run_benchmark(
        self,
        rag_engine: AdvancedRAGEngine,
        dataset_path: str | Path,
        generator: Any | None = None,
        top_k: int = 3,
    ) -> dict[str, Any]:
        """
        Executes benchmark against a golden evaluation dataset.
        """
        path = Path(dataset_path)
        if not path.exists():
            raise FileNotFoundError(f"Evaluation dataset not found at {dataset_path}")

        with open(path, encoding="utf-8") as f:
            dataset = json.load(f)

        results = []
        hits_at_1 = 0
        hits_at_k = 0
        reciprocal_ranks = []
        faithfulness_scores = []
        context_relevance_scores = []
        answer_relevance_scores = []

        logger.info(f"Running RAG benchmark across {len(dataset)} evaluation queries...")

        for item in dataset:
            query = item["query"]
            target_doc_id = item.get("ground_truth_doc_id", "")

            # 1. Retrieval Evaluation
            retrieved_docs = rag_engine.retrieve(query, top_k=top_k)
            retrieved_ids = [d.get("document_id") or d.get("parent_id") or d.get("id", "") for d in retrieved_docs]

            # Check matching target id (substring or exact)
            rank = None
            for idx, doc_id in enumerate(retrieved_ids):
                if target_doc_id and (target_doc_id in doc_id or doc_id in target_doc_id):
                    rank = idx + 1
                    break

            is_hit_1 = (rank == 1)
            is_hit_k = (rank is not None)
            rr = 1.0 / rank if rank else 0.0

            if is_hit_1:
                hits_at_1 += 1
            if is_hit_k:
                hits_at_k += 1
            reciprocal_ranks.append(rr)

            # 2. Generation & Triad Evaluation (if generator provided or using mock synthesis)
            if generator:
                gen_res = generator.generate(query=query, context_docs=retrieved_docs, telemetry={}, predictions={})
                answer = gen_res.get("answer", "")
            else:
                # Default answer constructed from top context
                answer = retrieved_docs[0]["text"] if retrieved_docs else "No answer"

            triad = self.evaluator.evaluate_rag_triad(query, retrieved_docs, answer)
            context_relevance_scores.append(triad["context_relevance"])
            faithfulness_scores.append(triad["faithfulness"])
            answer_relevance_scores.append(triad["answer_relevance"])

            results.append({
                "id": item.get("id"),
                "query": query,
                "target_doc_id": target_doc_id,
                "retrieved_ids": retrieved_ids,
                "rank": rank,
                "hit_at_k": is_hit_k,
                "reciprocal_rank": rr,
                "triad_scores": triad,
            })

        total_queries = len(dataset)
        summary = {
            "total_queries": total_queries,
            "top_k": top_k,
            "hit_rate_at_1": round(hits_at_1 / total_queries, 4),
            "hit_rate_at_k": round(hits_at_k / total_queries, 4),
            "mean_reciprocal_rank_mrr": round(sum(reciprocal_ranks) / total_queries, 4),
            "mean_context_relevance": round(sum(context_relevance_scores) / total_queries, 4),
            "mean_faithfulness": round(sum(faithfulness_scores) / total_queries, 4),
            "mean_answer_relevance": round(sum(answer_relevance_scores) / total_queries, 4),
            "detailed_results": results,
        }

        logger.info(
            f"Benchmark Complete! MRR: {summary['mean_reciprocal_rank_mrr']}, "
            f"Hit@{top_k}: {summary['hit_rate_at_k']}, "
            f"Faithfulness: {summary['mean_faithfulness']}"
        )
        return summary
