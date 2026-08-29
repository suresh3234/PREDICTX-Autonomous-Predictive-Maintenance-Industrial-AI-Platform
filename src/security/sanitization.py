import re
import html
from typing import Any


class InputSanitizer:
    """
    Industrial Input Sanitization and Prompt Injection Defense Engine.
    """

    PROMPT_INJECTION_PATTERNS = [
        r"ignore\s+(all\s+)?(previous|prior)\s+instructions",
        r"disregard\s+(all\s+)?(previous|prior)\s+instructions",
        r"system\s+override",
        r"you\s+are\s+now\s+(in\s+)?(developer\s+mode|dan)",
        r"jailbreak",
        r"reveal\s+your\s+system\s+prompt",
        r"print\s+your\s+hidden\s+instructions",
    ]

    SQL_INJECTION_PATTERNS = [
        r"(--|\#|\/\*)",
        r"(;\s*drop\s+table)",
        r"(union\s+select)",
        r"(or\s+1\s*=\s*1)",
    ]

    @classmethod
    def sanitize_text(cls, text: str) -> str:
        """Escapes dangerous HTML entities and trims excessive whitespace."""
        if not isinstance(text, str):
            return str(text)
        # Escape HTML entities
        escaped = html.escape(text.strip())
        # Remove null bytes
        return escaped.replace("\x00", "")

    @classmethod
    def detect_prompt_injection(cls, query: str) -> bool:
        """
        Detects adversarial prompt injection attempts.
        """
        if not query:
            return False
        q_lower = query.lower()
        for pattern in cls.PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, q_lower):
                return True
        return False

    @classmethod
    def detect_sql_injection(cls, query: str) -> bool:
        """
        Detects potential SQL injection signatures in user input.
        """
        if not query:
            return False
        q_lower = query.lower()
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, q_lower):
                return True
        return False
