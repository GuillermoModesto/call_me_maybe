"""Pipeline: turn a user prompt into a validated FunctionCallResult."""

from llm_sdk import Small_LLM_Model

from .engine import fill_arguments, select_function_name
from .models import FunctionCallResult, FunctionDefinition
from .name_selector import NameSelector
from .vocab import Vocabulary


def _name_prompt(user_prompt: str, names: list[str]) -> str:
    """Prompt that primes the model to pick a function name"""
    return (
        "You select which function to call for the user request.\n"
        "Functions: " + ", ".join(names) + ".\n"
        "Request: " + user_prompt + "\n"
        "Function name: "
    )


def _args_prompt(user_prompt: str, function: FunctionDefinition) -> str:
    """Prompt that primes the model to extract the arguments."""
    prompt: str = (
        "Extract the arguments for " + function.name
        + " (" + function.description + ").\n"
        "Copy values exactly and fully from the request.\n"
        'Example - Request: Greet Alice -> {"name": "Alice"}\n'
        "Request: " + user_prompt + "\n"
        "Arguments as JSON: "
    )
    return prompt


def process_prompt(
        model: Small_LLM_Model,
        vocab: Vocabulary,
        selector: NameSelector,
        functions_by_name: dict[str, FunctionDefinition],
        user_prompt: str
) -> FunctionCallResult:
    """Select the function and fill its arguments for one user prompt"""
    names = list(functions_by_name)
    name_ids = model.encode(_name_prompt(user_prompt, names)).tolist()[0]
    name = select_function_name(model, vocab, selector, name_ids)

    function = functions_by_name[name]
    args_ids = model.encode(_args_prompt(user_prompt, function)).tolist()[0]
    parameters = fill_arguments(model, vocab, function, args_ids)

    return FunctionCallResult(
        prompt=user_prompt,
        name=name,
        parameters=parameters
    )
