"""Prefix constraint over the allowed function names."""

from .vocab import Vocabulary


class NameSelector:
    """Produces the set of allowed token ids to spell one of the names"""
    def __init__(self, names: list[str], vocab: Vocabulary) -> None:
        self.names = names
        self.vocab = vocab

    def allowed_token_ids(self, prefix: str) -> set[int]:
        """Token ids whose text keeps 'prefix' a valid start of some name"""
        allowed: set[int] = set()
        for name in self.names:
            if name.startswith(prefix) and len(name) > len(prefix):
                remaining = name[len(prefix):]
                for length in range(1, len(remaining) + 1):
                    piece = remaining[:length]
                    token_id = self.vocab.text_to_id.get(piece)
                    if token_id is not None:
                        allowed.add(token_id)
        return allowed
