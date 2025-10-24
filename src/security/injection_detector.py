# src/security/injection_detector.py
"""
Injection detector for SQL queries.

Provides both functional and class-based interfaces:
- detect_sql_injection(query) -> (bool, reason)
- score_sql_risk(query) -> float in [0.0, 1.0]
- InjectionDetector class for compatibility
"""

import re
from typing import Tuple

# Patterns that strongly indicate injection-like content
_STRONG_PATTERNS = [
    r"\bUNION\b\s+\bSELECT\b",
    r"(;|\b--\b|\b/\*\b|\b\*/\b)",        # delimiters/comments
    r"\bOR\b\s+['\"]?\d+['\"]?\s*=\s*['\"]?\d+['\"]?",  # OR 1=1 etc
    r"\bAND\b\s+['\"]?\d+['\"]?\s*=\s*['\"]?\d+['\"]?",
    r"\bDROP\b\s+\bTABLE\b",
    r"\bDELETE\b\s+\bFROM\b",
    r"\bINSERT\b\s+\bINTO\b.*\bSELECT\b",  # suspicious complex insert-select
    r"sleep\s*\(",                         # timing attack
    r"benchmark\s*\(",                     # MySQL benchmark
    r"\bEXEC(UTE)?\b",
]

# Weaker suspicious tokens
_WEAK_PATTERNS = [
    r"\bINFORMATION_SCHEMA\b",
    r"\bPG_SLEEP\b",
    r"0x[0-9a-f]{6,}",    # hex blobs often in obfuscation
    r"char\(",            # obfuscation techniques
    r"cast\(",            # type casts often used in payloads
]

RE_STRONG = [re.compile(p, re.IGNORECASE) for p in _STRONG_PATTERNS]
RE_WEAK = [re.compile(p, re.IGNORECASE) for p in _WEAK_PATTERNS]


def detect_sql_injection(query: str) -> Tuple[bool, str]:
    """
    Return (is_injection, reason_string)
    """
    if not query or not isinstance(query, str):
        return False, ""

    q = query.strip()

    # Multiple statements (simple heuristic)
    if ";" in q:
        cnt = q.count(";")
        if cnt >= 1:
            return True, "Multiple statements or semicolon found"

    # Strong patterns -> immediate detection
    for r in RE_STRONG:
        if r.search(q):
            return True, f"Strong pattern matched: {r.pattern}"

    # Weak patterns increase suspicion
    for r in RE_WEAK:
        if r.search(q):
            return True, f"Weak pattern matched: {r.pattern}"

    # Always-true boolean conditions
    if re.search(r"\bOR\b\s+['\"]?\d+['\"]?\s*=\s*['\"]?\d+", q, re.IGNORECASE):
        return True, "Always-true OR condition detected"

    return False, ""


def score_sql_risk(query: str) -> float:
    """
    Return a float in [0.0, 1.0] estimating likelihood of injection.
    """
    if not query or not isinstance(query, str):
        return 0.0
    
    q = query.strip()
    score = 0.0

    # semicolon / multiple statements
    if ";" in q:
        score += 0.5

    for r in RE_STRONG:
        if r.search(q):
            score += 0.6
    
    for r in RE_WEAK:
        if r.search(q):
            score += 0.2

    if re.search(r"\bOR\b\s+['\"]?\d+['\"]?\s*=\s*['\"]?\d+", q, re.IGNORECASE):
        score += 0.6

    # cap at 1.0
    if score > 1.0:
        score = 1.0
    
    return round(score, 3)


class InjectionDetector:
    """
    Class-based interface for SQL injection detection.
    Provides compatibility with existing firewall code.
    """
    
    def __init__(self):
        """Initialize the injection detector"""
        pass
    
    def detect_sql_injection(self, query: str) -> Tuple[bool, str]:
        """
        Detect SQL injection patterns in a query.
        
        Args:
            query: SQL query string to analyze
            
        Returns:
            Tuple of (is_injection, reason)
        """
        return detect_sql_injection(query)
    
    def score_sql_risk(self, query: str) -> float:
        """
        Score the risk level of a SQL query.
        
        Args:
            query: SQL query string to analyze
            
        Returns:
            Risk score between 0.0 and 1.0
        """
        return score_sql_risk(query)