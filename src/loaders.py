"""Loading and validation of the program's JSON input files."""

import json
from pathlib import Path

from pydantic import TypeAdapter, ValidationError

from .models import FunctionDefinition, PromptEntry

from typing import Any


class InputError(Exception):
    """Raised when an input file is missing,
        invalid JSON, or fails validation."""
    def __init__(self, msg: str) -> None:
        super().__init__(msg)


def load_function_definitions(path: Path) -> list[FunctionDefinition]:
    """Checks for correct file path, json and type formats. Returns
        constructed and typed objects using TypeAdapter
        from the raw json load"""
    raw_data = _read_json(path)

    adapter = TypeAdapter(list[FunctionDefinition])
    try:
        return adapter.validate_python(raw_data)
    except ValidationError as e:
        raise InputError(f"Invalid input structure in {path}: {e}")


def load_prompts(path: Path) -> list[PromptEntry]:
    raw_data = _read_json(path)

    adapter = TypeAdapter(list[PromptEntry])
    entries = adapter.validate_python(raw_data)
    try:
        return [entry.prompt for entry in entries]
    except ValidationError as e:
        raise InputError(f"Invalid structure in {path}: {e}")


def _read_json(path: Path) -> Any:
    try:
        with open(path, encoding="utf-8") as f:
            raw_text = f.read()
    except FileNotFoundError:
        raise InputError(f"File not found: {path}")
    except OSError as e:
        raise InputError(f"There was an error reading the file {path}: {e}")

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise InputError(f"Invalid JSON {path}: {e}")