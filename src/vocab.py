"""Vocabulary: token <-> id maps and byte-level decoding
for Qwen's BPE"""

import json
from pathlib import Path
import unicodedata


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


def _is_string_content(text: str) -> bool:
    """True if `text` can appear inside a JSON string value unescaped."""
    if not text:
        return False
    for ch in text:
        if ch in '"\\' or ch == "\ufffd":
            return False
        if unicodedata.category(ch).startswith("C"):  # control chars
            return False
    return True


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
        self.text_to_id: dict[str, int] = {}
        self.string_content_ids: set[int] = set()
        for token_id in self.id_to_token:
            text = self.token_text(token_id)
            self.text_to_id[text] = token_id
            if _is_string_content(text):
                self.string_content_ids.add(token_id)

    def token_text(self, token_id: int) -> str:
        """Return the real text of a token id
            (bytes decoded, Ġ -> space), ...)"""
        token_str = self.id_to_token[token_id]
        byte_values = [self.byte_decoder[ch] for ch in token_str]
        return bytes(byte_values).decode("utf8", errors="replace")
