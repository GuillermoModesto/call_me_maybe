"""Constrained decoding engine: mask illegal tokens and pick the best."""

import math

from llm_sdk import Small_LLM_Model

from .name_selector import NameSelector
from .vocab import Vocabulary

from typing import Any

from .models import FunctionDefinition, ParamType
from .value_types import BooleanType, NumberType, ValueType


_TYPE_OBJECTS: dict[ParamType, ValueType] = {
    ParamType.NUMBER: NumberType(),
    ParamType.BOOLEAN: BooleanType()
}


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


def generate_string(
    model: Small_LLM_Model,
    vocab: Vocabulary,
    token_ids: list[int],
    max_len: int = 200,
) -> str:
    """Generate a string value allowing multi-char content tokens."""
    quote_id = vocab.text_to_id['"']
    allowed = vocab.string_content_ids | {quote_id}
    value: str = ""
    while len(value) < max_len:
        logits = model.get_logits_from_input_ids(token_ids)
        next_id = pick_allowed(logits, allowed)
        if next_id == quote_id:
            return value
        value += vocab.token_text(next_id)
        token_ids.append(next_id)

        period = _looping_period(value)
        if period:
            unit = value[-period:]
            while value.endswith(unit + unit):
                value = value[:-period]
            return value
    return value


def _looping_period(value: str, repeats: int = 3) -> int:
    """Return the period of a tail unit repeated `repeats` times, or 0."""
    n = len(value)
    for period in range(1, n // repeats + 1):
        if value[-period * repeats:] == value[-period:] * repeats:
            return period
    return 0


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


def _emit(model: Small_LLM_Model, token_ids: list[int], text: str) -> None:
    """Append the tokens of fixed scaffolding text to the context"""
    token_ids.extend(model.encode(text).tolist()[0])


def _parse_value(text: str, ptype: ParamType) -> Any:
    """Convert the generated value string to its Python type"""
    if ptype == ParamType.NUMBER:
        return float(text) if "." in text else int(text)
    if ptype == ParamType.BOOLEAN:
        return text == "true"
    return text


def fill_arguments(
        model: Small_LLM_Model,
        vocab: Vocabulary,
        function: FunctionDefinition,
        prompt_ids: list[int]
) -> dict[str, Any]:
    """Generate the arguments object field by field, valid by construction"""
    token_ids = list(prompt_ids)
    result: dict[str, Any] = {}

    items = list(function.parameters.items())
    if not items:
        return result

    _emit(model, token_ids, "{")
    for index, (name, spec), in enumerate(items):
        is_last = index == len(items) - 1
        _emit(model, token_ids, '"' + name + '": ')

        if spec.type == ParamType.STRING:
            _emit(model, token_ids, '"')
            value = generate_string(model, vocab, token_ids)
            _emit(model, token_ids, '"')
        else:
            value_type = _TYPE_OBJECTS[spec.type]
            terminator = {"}"} if is_last else {","}
            value = generate_value(
                model, vocab, value_type, terminator, token_ids
            )

        result[name] = _parse_value(value, spec.type)
        _emit(model, token_ids, "}" if is_last else ", ")

    return result
