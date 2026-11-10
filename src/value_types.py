"""Per-type character-level constraints for argument values"""

DIGITS = set("0123456789")


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
