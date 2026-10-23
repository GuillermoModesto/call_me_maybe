"""Vocabulary: token <-> id maps and byle-level decoding
for Qwen's BPE"""

import json
from pathlib import Path


def bytes_to_unicode() -> dict[int, str]:
    """Map every byte (0-255) to a printable
        unicode character (GPT-2 scheme)."""
    bs = (
        list(range(ord("!"), ord("~") + 1))
        + list(range(ord("¡"), ord("¬") + 1))
        + list(range(ord("®"), ord("ÿ") + 1))
    )
    cs = bs[:]
    n = 0
    for b in range(256):
        if b not in bs:
            bs.append(b)
            cs.append(256 + n)
            n += 1
    return {b: chr(c) for b, c in zip(bs, cs)}


class Vocabulary:
    """Holds the token/id maps and decodes token to real text"""

    def __init__(self, vocab_path: Path) -> None:
        with open(vocab_path, encoding="utf-8") as f:
            self.token_to_id: dict[str, int] = json.load(f)
        self.id_to_token: dict[int, str] = {
            idx: tok for tok, idx in self.token_to_id.items()
        }
        byte_encoder = bytes_to_unicode()
        self.byte_decoder: dict[str, int] = {
            ch: b for b, ch in byte_encoder.items()
        }

    def token_text(self, token_id: int) -> str:
        """Return the real text of a token id
            (bytes decoded, Ġ -> space), ...)"""
        token_str = self.id_to_token[token_id]
        byte_values = [self.byte_decoder[ch] for ch in token_str]
        return bytes(byte_values).decode("utf8", errors="replace")
