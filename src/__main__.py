"""Program entry point: load inputs, generate results, write output."""

import argparse
import sys
from pathlib import Path

from .loaders import InputError, load_function_definitions, load_prompts
from .models import FunctionCallResult
from .writer import write_results


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Constrained function calling.")
    parser.add_argument(
        "--functions",
        type=Path,
        default=Path("data/input/functions_definition.json"),
        help="Path to the function definitions JSON file.",
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/input/function_calling_tests.json"),
        help="Path to the test prompts JSON file.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/output/function_calling_results.json"),
        help="Path where the results JSON will be written.",
    )
    return parser.parse_args()


def fake_generate(prompt: str) -> FunctionCallResult:
    """Placeholder generator; returns a fixed result.
        Replaced in later phases."""
    return FunctionCallResult(
        prompt=prompt,
        name="fn_placeholder",
        parameters={},
    )


def main() -> None:
    """Orchestrate the full input -> process -> output flow."""
    args = parse_args()
    try:
        load_function_definitions(args.functions)
        prompts = load_prompts(args.input)
    except InputError as exc:
        print(exc)
        sys.exit(1)

    results = [fake_generate(prompt) for prompt in prompts]
    write_results(results, args.output)
    print(f"Wrote {len(results)} results to {args.output}")


if __name__ == "__main__":
    main()
