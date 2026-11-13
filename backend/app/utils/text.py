"""
text.py — small text helpers shared by the search code.
"""

import re

# \w+ = runs of letters, digits or underscore. Underscore matters:
# "BANK_TIMEOUT" stays ONE token instead of splitting into "bank" + "timeout".
_TOKEN_PATTERN = re.compile(r"\w+")

# STOPWORDS: very common words that carry no topic ("the", "to", "why").
# Without this, BM25 would match "a payment take TOO long TO..." against any
# chunk that also contains "to" and rank the wrong passages first.
STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "of", "to", "in", "on", "at", "by",
    "for", "with", "from", "as", "is", "are", "was", "were", "be", "been", "it",
    "its", "this", "that", "these", "those", "what", "which", "who", "why", "how",
    "when", "where", "do", "does", "did", "can", "could", "should", "would", "might",
    "may", "will", "i", "we", "you", "they", "our", "your", "their", "not", "no",
    "too", "so", "than", "then", "there", "about", "into", "only", "also", "more",
}


def tokenize(text: str) -> list[str]:
    """'Why is BANK_TIMEOUT slow?' -> ['bank_timeout', 'slow']"""
    return [t for t in _TOKEN_PATTERN.findall(text.lower()) if t not in STOPWORDS]
