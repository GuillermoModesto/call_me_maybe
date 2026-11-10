"""Constrained decoding engine: mask illegal tokens and pick the best."""

import math

from llm_sdk import Small_LLM_Model

from .name_selector import NameSelector
from .vocab import Vocabulary


def pick_allowed(logits: list[float], allowed_ids: set[int]) -> int:
    """Return the id of the highest-logit token among the allowed ones"""
    best_id = -1
    best_logit = -math.inf
    for token_id in allowed_ids:
        if logits[token_id] > best_logit:
            best_logit = logits[token_id]
            best_id = token_id
    return best_id


def select_function_name(
        model: Small_LLM_Model,
        vocab: Vocabulary,
        selector: NameSelector,
        prompt_ids: list[int]
) -> str:
    """Generate one valid function name under the trie constraint"""
    token_ids = list(prompt_ids)
    prefix = ""
    while True:
        allowed = selector.allowed_token_ids(prefix)
        if not allowed:
            break
        logits = model.get_logits_from_input_ids(token_ids)
        next_id = pick_allowed(logits, allowed)
        token_ids.append(next_id)
        prefix += vocab.token_text(next_id)
    return prefix
