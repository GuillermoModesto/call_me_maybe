"""Program entry point: load inputs, generate results, write output."""

import argparse
import sys
from pathlib import Path

from llm_sdk import Small_LLM_Model

from .loaders import InputError, load_function_definitions, load_prompts
from .models import FunctionCallResult
from .name_selector import NameSelector
from .pipeline import process_prompt
from .vocab import Vocabulary
from .writer import write_results


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Constrained function calling.")
    parser.add_argument(
        "--functions_definition",
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
        default=Path("data/output/function_calls.json"),
        help="Path where the results JSON will be written.",
    )
    return parser.parse_args()


def main() -> None:
    """Orchestrate the full input -> process -> output flow."""
    args = parse_args()
    try:
        functions = load_function_definitions(args.functions_definition)
        prompts = load_prompts(args.input)
    except InputError as exc:
        print(exc)
        sys.exit(1)

    model = Small_LLM_Model()
    vocab = Vocabulary(Path(model.get_path_to_vocab_file()))
    functions_by_name = {f.name: f for f in functions}
    selector = NameSelector(list(functions_by_name), vocab)

    results: list[FunctionCallResult] = []
    for index, prompt in enumerate(prompts, start=1):
        print(f"[{index}/{len(prompts)}] {prompt}")
        results.append(
            process_prompt(model, vocab, selector, functions_by_name, prompt)
        )

    write_results(results, args.output)
    print(f"Wrote {len(results)} results to {args.output}")


if __name__ == "__main__":
    main()
