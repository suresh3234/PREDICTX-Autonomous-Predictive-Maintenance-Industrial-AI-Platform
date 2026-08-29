import json
import os

from openai import OpenAI

from rag.vector_store import HybridRetriever


class RAGGenerator:
    """
    RAG Generator that connects the Hybrid Retrieval context, real-time sensor metrics,
    and model predictions with an LLM to generate precise, grounded troubleshooting guides.
    """

    def __init__(
        self,
        retriever: HybridRetriever,
        api_key: str = None,
        model: str = "gpt-4o-mini",
    ):
        self.retriever = retriever
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model

        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        else:
            self.client = None
            print(
                "WARNING: No OPENAI_API_KEY found. RAG Generator will run in OFFLINE MOCK mode."
            )

    def _assemble_prompt(
        self, query: str, context: list[dict], telemetry: dict, predictions: dict
    ) -> str:
        # Format context documents retrieved from manuals
        context_str = ""
        for doc in context:
            context_str += f"\n- Document [{doc['document_id']}] (Source: {doc['metadata'].get('source', 'Unknown')}):\n  {doc['text']}\n"

        # Format system telemetry metrics and predictions
        telemetry_str = json.dumps(telemetry, indent=2)
        predictions_str = json.dumps(predictions, indent=2)

        prompt = f"""You are a Senior Reliability Engineer and Maintenance Intelligence Assistant.
Your task is to analyze machine anomalies, explain why the fault is developing, and provide step-by-step troubleshooting actions.

RELIABILITY MANUALS CONTEXT:
{context_str}

REAL-TIME MACHINE TELEMETRY STATE:
{telemetry_str}

PREDICTIVE MODELS ANALYSIS STATE:
{predictions_str}

USER QUERY / COMMAND:
"{query}"

Please provide a structured troubleshooting response. Ground your recommendations strictly in the RELIABILITY MANUALS CONTEXT provided. If the context does not contain enough information, use your engineering knowledge but explicitly state that you are doing so.
Your response MUST include:
1. Operational Risk Assessment (Normal, Low, Medium, High, Critical) based on telemetry and predictions.
2. Root Cause Analysis (explain how the telemetry matches the manuals).
3. Step-by-Step Corrective Actions (actions to resolve the issue safely).
"""
        return prompt

    def generate_response(
        self, query: str, telemetry: dict, predictions: dict, top_k: int = 2
    ) -> dict:
        """
        Assembles context and telemetry, calls the LLM (or mock fallback), and returns the advice.
        """
        # 1. Retrieve relevant manual context
        context = self.retriever.retrieve(query, top_k=top_k, alpha=0.5)

        # 2. Assemble prompt
        prompt = self._assemble_prompt(query, context, telemetry, predictions)

        # 3. Call LLM or run Mock fallback
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert predictive maintenance assistant.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.2,
                )
                generated_text = response.choices[0].message.content
                is_mock = False
            except Exception as e:
                print(f"Error calling OpenAI API: {e}. Falling back to mock generator.")
                generated_text = self._mock_generator(
                    query, context, telemetry, predictions
                )
                is_mock = True
        else:
            generated_text = self._mock_generator(
                query, context, telemetry, predictions
            )
            is_mock = True

        return {
            "query": query,
            "response": generated_text,
            "retrieved_documents": [doc["document_id"] for doc in context],
            "is_mock": is_mock,
        }

    def _mock_generator(
        self, query: str, context: list[dict], telemetry: dict, predictions: dict
    ) -> str:
        """
        Offline rules-based generator that yields grounded maintenance summaries
        when no OpenAI API key is configured.
        """
        assess = predictions.get("anomaly_severity", "NORMAL")
        fail_type = predictions.get("failure_type", "General Failure")
        rul = predictions.get("predicted_rul", 24.0)

        best_doc = context[0]["text"] if context else "No manual available."
        doc_source = context[0]["metadata"].get("source", "N/A") if context else "N/A"

        mock_response = f"""### 🛠️ Maintenance Troubleshooting Advisory (OFFLINE MODE)

**1. Operational Risk Assessment:**
* **Severity Alert Level**: {assess}
* **Predicted Failure Target**: {fail_type}
* **Estimated Remaining Useful Life (RUL)**: {rul:.1f} hours

**2. Root Cause Analysis:**
The machine telemetry indicates active degradation. Based on the retrieved manual *({doc_source})*:
> "{best_doc}"
The current reading levels (Temperature: {telemetry.get('temperature', 0):.1f}°C, Vibration: {telemetry.get('vibration', 0):.2f} mm/s) suggest that this condition is aligned with a developing {fail_type}.

**3. Step-by-Step Corrective Actions:**
1. **Shutdown Protocol**: Initiate scheduled machine isolation if RUL is under 12 hours.
2. **Inspection**: Perform physical check based on reference manual recommendations:
   * Verify all housing bolts and foundation mounts are torqued properly.
   * Check fluid levels, O-ring gaskets, or winding resistances.
3. **Component Refurbishment**: Replace worn bearings or components before RUL reaches 0.
4. **Validation**: Restart the machine and confirm that vibration levels drop back below 1.5 mm/s.
"""
        return mock_response
