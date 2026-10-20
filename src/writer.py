"""Writing of the program's JSON output file."""

import json
from pathlib import Path

from .models import FunctionCallResult


def write_results(
        results: list[FunctionCallResult],
        path: Path) -> None:
    """Write the list of results to `path` as a JSON array."""
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [result.model_dump() for result in results]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
