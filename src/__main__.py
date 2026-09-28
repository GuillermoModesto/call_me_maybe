"""Phase 0 smoke test — throwaway.

Checks that the ``llm_sdk`` wrapper and the model are wired up correctly:
it encodes a bit of text, asks the model for the next-token logits, and
prints how many were returned (this count should equal the vocabulary size).

Delete this file once ``src/__main__.py`` becomes the real entry point.

Run with::

    make run          # i.e. uv run python -m src
"""

import os
from typing import Any, List

from llm_sdk import Small_LLM_Model


def _to_int_list(token_ids: Any) -> List[int]:
    """Flatten whatever ``encode()`` returns into a flat list of ints.

    ``encode()`` returns a tensor that may be 1-D (``[seq]``) or 2-D
    (``[1, seq]``). We avoid importing torch (forbidden) and rely on the
    tensor's ``.tolist()`` method, then flatten one level if needed.

    Args:
        token_ids: The value returned by ``model.encode(...)``.

    Returns:
        A flat list of integer token IDs.
    """
    raw = token_ids.tolist() if hasattr(token_ids, "tolist") else token_ids
    flat: List[int] = []
    for item in raw:
        if isinstance(item, list):
            flat.extend(int(x) for x in item)
        else:
            flat.append(int(item))
    return flat


def main() -> None:
    """Run the smoke test and report the number of logits."""
    prompt = "What is the sum of 2 and 3?"
    try:
        # If the constructor needs the model name, pass it explicitly, e.g.
        # Small_LLM_Model("Qwen/Qwen3-0.6B").
        model = Small_LLM_Model()
        token_ids = _to_int_list(model.encode(prompt))
        logits = model.get_logits_from_input_ids(token_ids)
        vocab_path = model.get_path_to_vocab_file()
    except Exception as exc:
        print(f"[smoke test] FAILED: {type(exc).__name__}: {exc}")
        return

    print(f"[smoke test] prompt      : {prompt!r}")
    print(f"[smoke test] token count : {len(token_ids)}")
    print(f"[smoke test] first ids   : {token_ids[:10]}")
    print(f"[smoke test] vocab file  : {vocab_path} "
          f"(exists={os.path.exists(vocab_path)})")
    print(f"[smoke test] logits count: {len(logits)}  "
          f"(should be the vocab size)")
    print("[smoke test] OK — environment and SDK are wired up correctly.")


if __name__ == "__main__":
    main()
