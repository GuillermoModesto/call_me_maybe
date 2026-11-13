"""Per-type character-level constraints for argument values"""
import string as _string
from typing import Protocol

DIGITS = set("0123456789")
STRING_CHARS = (
    set(_string.ascii_letters + _string.digits + _string.punctuation + " ")
    - {'"', '\\'}
)


class NumberType:
    """Constraint for a JSON number: -?[0-9]+(\\.[0-9]+)?"""
    def allowed_next_chars(self, value: str) -> set[str]:
        if value == "":
            return DIGITS | {"-"}
        if value == "-":
            return DIGITS
        if "." in value:
            return DIGITS
        return DIGITS | {"."}

    def is_complete(self, value: str) -> bool:
        """True if 'value' is a complete, valid number"""
        if value == "" or value == "-" or value.endswith("."):
            return False
        return True


class BooleanType:
    """Constraint for a JSON boolean: exactly 'true' or 'false'"""
    LITERALS = ("true", "false")

    def allowed_next_chars(self, value: str) -> set[str]:
        """Next chars that keep 'value' a prefix of 'true' or 'false'"""
        chars: set[str] = set()
        for literal in self.LITERALS:
            if literal.startswith(value) and len(literal) > len(value):
                chars.add(literal[len(value)])
        return chars

    def is_complete(self, value: str) -> bool:
        """True if 'value' is exactly 'true' or 'false'"""
        return value in self.LITERALS


class StringType:
    """Constraint for a JSON string's content
    (quotes handled by the engine)."""
    def allowed_next_chars(self, value: str) -> set[str]:
        """Any printable char except the quote and backslash."""
        return STRING_CHARS

    def is_complete(self, value: str) -> bool:
        """A string content of any length (including empty) can be closed."""
        return True


class ValueType(Protocol):
    """Common interface of a value contraint"""

    def allowed_next_chars(self, value: str) -> set[str]: ...

    def is_complete(self, value: str) -> bool: ...
