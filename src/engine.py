"""Constrained decoding engine: mask illegal tokens and pick the best."""

import math

from llm_sdk import Small_LLM_Model

from .name_selector import NameSelector
from .vocab import Vocabulary
from .value_types import ValueType


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


def generate_value(
        model: Small_LLM_Model,
        vocab: Vocabulary,
        value_type: ValueType,
        terminators: set[str],
        token_ids: list[int],
        max_len: int = 100
) -> str:
    """Generate one value char by char;
    stop when the model picks a terminator"""
    terminator_ids = {
        vocab.text_to_id[t] for t in terminators if t in vocab.text_to_id
    }
    value = ""
    while len(value) < max_len:
        allowed_ids = {
            vocab.text_to_id[ch]
            for ch in value_type.allowed_next_chars(value)
            if ch in vocab.text_to_id
        }
        if value_type.is_complete(value):
            allowed_ids |= terminator_ids
        logits = model.get_logits_from_input_ids(token_ids)
        next_id = pick_allowed(logits, allowed_ids)
        if next_id in terminator_ids:
            return value
        value += vocab.token_text(next_id)
        token_ids.append(next_id)
    return value
