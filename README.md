*This project has been created as part of the 42 curriculum by guantino.*

# call me maybe — Function calling in LLMs

## Description

This project turns a small local LLM (Qwen3-0.6B, served through the provided
`llm_sdk`) into a reliable function-calling engine using **constrained
decoding**. Given a set of function definitions and a list of natural-language
prompts, the program must, for each prompt, choose the right function and fill
its arguments, producing output that is **always structurally valid** — never
malformed JSON, never an unknown function name, never an argument of the wrong
type.

The reliability does not come from asking the model nicely for JSON and hoping.
It comes from intervening in the token-by-token generation: at every step we
look at the model's logits, mask out every token that would make the output
invalid, and only then let the model pick among the legal options. Validity is
enforced by construction, not checked afterwards.

## Instructions

```bash
make install     # uv sync — creates .venv and installs everything
make run         # uv run python -m src  (uses default input/output paths)
make run ARGS="--input data/input/function_calling_tests.json \
               --output data/output/function_calling_results.json"
make lint        # flake8 + mypy with the required flags
make clean       # remove caches and build artifacts (keeps uv.lock)
make fclean      # clean + remove .venv
```

Inputs live in `data/input/` (`functions_definition.json` and
`function_calling_tests.json`). Output is written to `data/output/`, which is
generated at runtime and is **not** committed.

## Algorithm explanation

*(Planned — not yet implemented. Kept here so the intended approach is on
record.)*

1. Generation is token by token. At each step `get_logits_from_input_ids`
   returns one logit per vocabulary token (151,936 of them).
2. Before choosing, set the logit of every *illegal* token to `-inf`, so the
   argmax can never pick it.
3. "Legal" is defined by a small state machine describing what a valid output
   looks like at this point.
4. Two sub-problems:
   - **Choosing the function**: the name must be exactly one of the defined
     ones → modelled with a *trie* over the allowed names. The LLM still
     chooses (by its logits) among legal continuations, but cannot invent a
     name.
   - **Filling the arguments**: each value must match its type
     (`number` / `string` / `boolean`) → a small DFA per type, generated field
     by field while the structural scaffolding (`{`, `"a": `, `, `, `}`) is
     emitted by us.

## Design decisions

- **`uv` with `llm_sdk` as a local path dependency.** The SDK ships as a full
  installable project (its own `pyproject.toml` + build backend), so it is
  declared under `[tool.uv.sources]` as `llm-sdk = { path = "llm_sdk" }`. This
  makes `uv sync` alone sufficient for the reviewer, and `torch` /
  `transformers` / `huggingface-hub` come in transitively — our code never
  imports them directly.
- **Pydantic models as the single source of truth for shapes** (`src/models.py`).
  Input models use `extra="forbid"` so any unexpected key in an input file is a
  hard error, not a silent drop. The output model has no `forbid`: we build it
  ourselves, and declaring exactly three fields (`prompt`, `name`,
  `parameters`) already guarantees the required output schema.
- **`ParamType` as a `str`-backed `Enum`.** The `type` field only accepts
  `number` / `string` / `boolean`; anything else fails validation for free.
- **Input/output isolated from logic** (planned). A dedicated `loaders.py`
  raises a custom `InputError` on any problem (missing file, invalid JSON,
  failed validation); the entry point decides the policy (print a clear
  message, exit non-zero). The subject requires the program to never crash with
  a traceback.

## Performance analysis

*(TODO — once the engine runs: accuracy on the test prompts, per-prompt latency,
and the effect of caching the vocab maps.)*

## Challenges faced

*(TODO — filled as they come up. So far: resolving the nested `llm_sdk` package
layout, and stopping flake8 from recursing into `.venv`.)*

## Testing strategy

*(Planned.)* Each layer is validated before the next is built. The I/O layer is
exercised end to end with a *fake* generator returning a fixed result, so the
plumbing is trusted before any LLM logic exists. Unit tests target the loaders
(missing file, invalid JSON, schema violations) and, later, the trie and the
type DFAs.

## Example usage

*(TODO — add a real run with sample output once the pipeline is complete.)*

## Resources

*(TODO — references on constrained decoding + a note on how AI was used and for
which parts.)*

---

## Development log

A running, chronological record of progress so the project can be picked up
again after a break. Most recent first. *(Working aid; trim before final
submission if desired.)*

### Phase 1 — I/O plumbing and data models *(in progress)*

- **Done — `src/models.py`.** Defined `ParamType` (enum), `ParamSpec`,
  `FunctionDefinition`, `FunctionCallResult` and `PromptEntry`. Input models
  carry `extra="forbid"`; the output model declares exactly the three required
  keys. Passes `make lint`.
  - *Why:* lock down the exact shape of every input/output object in one place,
    so validation is automatic and the rest of the code can trust the data.
- **Done — `src/loaders.py`.** Custom `InputError`, a private `_read_json`
  helper (open + parse, raising `InputError` on missing file / invalid JSON),
  and `load_function_definitions` / `load_prompts`, which validate the parsed
  data with a pydantic `TypeAdapter` and translate any `ValidationError` into
  `InputError`. Verified by hand: valid file loads and validates; a missing
  file raises `InputError` with a clear message (no raw traceback).
  - *Why / how:* the loader *detects and describes* every input problem; the
    entry point will *decide the policy* (print, exit non-zero). Exceptions
    propagate on their own, so only the validation step re-wraps its error —
    `_read_json`'s `InputError` just bubbles up untouched.
- **Next — `src/writer.py`:** write a `list[FunctionCallResult]` to JSON
  (create the output dir, `model_dump()` so no extra keys, `ensure_ascii=False`).
- **Next — `src/__main__.py`:** wire argument parsing + a *fake* generator to
  prove the whole input → output flow before touching the LLM.

### Phase 0 — scaffolding and environment *(done)*

- Project laid out (`src/`, `data/input`, `data/output`, `llm_sdk/`) and the
  `uv` environment wired up: `pyproject.toml`, `Makefile` and `.flake8` all on
  `uv`; `uv.lock` committed.
- `llm_sdk` installed as a local path dependency (see Design decisions).
- Smoke test confirmed the model loads and `get_logits_from_input_ids` returns
  **151,936** logits (the full Qwen3 vocabulary). Throwaway smoke test then
  removed; `src/__main__.py` left empty for the real entry point.
  - *Why:* prove the environment and SDK are correctly connected before writing
    any real logic.