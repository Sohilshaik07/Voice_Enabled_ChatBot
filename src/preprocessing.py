"""Shared text preprocessing used during training and inference."""
import re

MAX_SEQUENCE_LENGTH = 20


def normalize_text(text: str) -> str:
    """Lowercase and retain words/numbers/apostrophes for consistent tokenization."""
    if not isinstance(text, str):
        return ""
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9'\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()
