import re
from typing import Optional


class QueryExpander:
    """
    Industrial domain-specific query expander.
    Translates informal operator descriptions into technical engineering terminology.
    """

    # Domain symptom to technical keyword ontology
    DOMAIN_SYNONYMS = {
        "shaking": ["vibration", "bearing wear", "shaft misalignment", "mechanical looseness"],
        "shaky": ["vibration", "bearing degradation", "foundation bolts"],
        "vibrating": ["vibration amplitude", "bearing housing", "rotor imbalance"],
        "noise": ["acoustic squeal", "bearing wear", "gear mesh failure"],
        "loud": ["acoustic emission", "defective ball bearings", "cavitation"],
        "hot": ["overheating", "thermal dissipation", "coolant radiator"],
        "overheating": ["temperature threshold", "cooling fan failure", "radiator clog"],
        "burning": ["thermal breakdown", "winding insulation damage"],
        "leak": ["pressure drop", "hydraulic seal rupture", "o-ring gasket"],
        "leaking": ["fluid seal", "pipe coupling", "pressure leak"],
        "drops": ["pressure drop", "hydraulic failure"],
        "spark": ["electrical short-circuit", "winding insulation failure"],
        "smoke": ["electrical thermal overload", "bearing seizure"],
        "rpm": ["spindle speed", "rotational frequency", "motor drive"],
    }

    def __init__(self, custom_synonyms: Optional[dict] = None):
        self.synonyms = {**self.DOMAIN_SYNONYMS, **(custom_synonyms or {})}

    def expand(self, query: str) -> str:
        """
        Expands the user query by appending relevant engineering terms.
        """
        words = [w.lower().strip(".,?!;:") for w in query.split()]
        added_terms = []

        for word in words:
            if word in self.synonyms:
                for syn in self.synonyms[word]:
                    if syn.lower() not in query.lower() and syn not in added_terms:
                        added_terms.append(syn)

        if added_terms:
            return f"{query} ({', '.join(added_terms)})"
        return query

    def generate_sub_queries(self, query: str) -> list[str]:
        """
        Generates multi-perspective sub-queries (e.g., Root Cause vs Remediation SOP).
        """
        expanded = self.expand(query)
        return [
            query,
            expanded,
            f"Remediation and repair SOP for: {query}",
        ]
