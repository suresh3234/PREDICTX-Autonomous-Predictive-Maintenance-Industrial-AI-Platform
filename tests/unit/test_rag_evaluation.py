import pytest
from pathlib import Path
from rag.engine import AdvancedRAGEngine
from rag.evaluation.evaluator import RAGEvaluator
from rag.evaluation.benchmark import RAGBenchmarkSuite


def test_context_relevance_metric():
    evaluator = RAGEvaluator()
    query = "How to replace defective ball bearings on high vibration?"
    
    relevant_context = [
        {"text": "Abnormal vibration exceeding 3.5 mm/s requires immediate bearing replacement and lubrication."}
    ]
    irrelevant_context = [
        {"text": "The corporate cafeteria opens at 8:00 AM on weekdays."}
    ]

    rel_score = evaluator.evaluate_context_relevance(query, relevant_context)
    irrel_score = evaluator.evaluate_context_relevance(query, irrelevant_context)

    assert rel_score > irrel_score
    assert rel_score >= 0.60


def test_faithfulness_metric():
    evaluator = RAGEvaluator()
    context = [
        {"text": "Clean external radiator fins and check coolant levels when temperature exceeds 75C."}
    ]

    grounded_answer = "When temperature exceeds 75C, clean the external radiator fins and check coolant levels."
    hallucinated_answer = "Install a high-voltage turbojet thruster and pour liquid nitrogen into the battery container."

    grounded_score = evaluator.evaluate_faithfulness(grounded_answer, context)
    hallucinated_score = evaluator.evaluate_faithfulness(hallucinated_answer, context)

    assert grounded_score > hallucinated_score
    assert grounded_score >= 0.80
    assert hallucinated_score <= 0.40


def test_answer_relevance_metric():
    evaluator = RAGEvaluator()
    query = "What is the recommended bolt torque for pressure housing?"
    
    relevant_answer = "Retorque all loose bolts on the pressure housing to 120 Nm."
    irrelevant_answer = "Today is Tuesday and the weather is partly cloudy."

    rel_score = evaluator.evaluate_answer_relevance(query, relevant_answer)
    irrel_score = evaluator.evaluate_answer_relevance(query, irrelevant_answer)

    assert rel_score > irrel_score
    assert rel_score >= 0.60


def test_rag_triad_evaluation():
    evaluator = RAGEvaluator()
    query = "Bearing wear troubleshooting procedure"
    context = [
        {"text": "Shut down the machine immediately and replace defective ball bearings with lithium grease."}
    ]
    answer = "Shut down the machine and replace defective ball bearings using lithium grease."

    triad = evaluator.evaluate_rag_triad(query, context, answer)
    assert triad["context_relevance"] > 0.3
    assert triad["faithfulness"] >= 0.8
    assert triad["answer_relevance"] > 0.3
    assert "PASSED" in triad["status"] or "ACCEPTABLE" in triad["status"]


def test_benchmark_suite_execution():
    root = Path(__file__).resolve().parents[2]
    manuals_path = root / "data" / "knowledge" / "manuals.json"
    dataset_path = root / "data" / "knowledge" / "golden_rag_eval.json"

    # Index manuals into Advanced RAG Engine
    engine = AdvancedRAGEngine()
    engine.index_file_or_directory(manuals_path)

    # Execute benchmark suite
    suite = RAGBenchmarkSuite()
    summary = suite.run_benchmark(rag_engine=engine, dataset_path=dataset_path, top_k=3)

    assert summary["total_queries"] == 5
    assert summary["hit_rate_at_k"] == 1.0  # All 5 queries find their target document in top-3
    assert summary["mean_reciprocal_rank_mrr"] >= 0.80
    assert summary["mean_faithfulness"] >= 0.70
