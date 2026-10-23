"""Unconstrained greedy generation loop (Phase 2 scaffolding)."""

from llm_sdk import Small_LLM_Model


def argmax(values: list[float]) -> int:
    """Return the index of the largest value."""
    return max(range(len(values)), key=values.__getitem__)


def greedy_generate(
        model: Small_LLM_Model,
        prompt: str,
        max_new_tokens: int = 30
) -> list[int]:
    """Generate up to max_new_tokens by always picking the argmax token."""
    token_ids: list[int] = model.encode(prompt).tolist()[0]
    generated: list[int] = []

    for _ in range(max_new_tokens):
        logits = model.get_logits_from_input_ids(token_ids)
        next_id = argmax(logits)
        token_ids.append(next_id)
        generated.append(next_id)

    return generated
