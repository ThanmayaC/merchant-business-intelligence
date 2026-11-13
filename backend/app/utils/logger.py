"""
logger.py — one shared logger, so every message has the same format.
Using a logger is better than print(): it adds time + level (INFO/ERROR).
"""

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("merchant_bi")
