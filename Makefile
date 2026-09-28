# ---- Configuration --------------------------------------------------------
PKG        = src
# Flags required by the subject for the `lint` rule.
MYPY_FLAGS = --warn-return-any \
             --warn-unused-ignores \
             --ignore-missing-imports \
             --disallow-untyped-defs \
             --check-untyped-defs

.DEFAULT_GOAL := run
.PHONY: install run debug lint lint-strict clean fclean

# ---- Environment ----------------------------------------------------------
# The reviewer and the moulinette only run `uv sync`.
install:
	uv sync

# ---- Execution ------------------------------------------------------------
# Usage: make run
#        make run ARGS="--input data/input/tests.json --output data/output/out.json"
run:
	uv run python -m $(PKG) $(ARGS)

# Run the package under the pdb debugger (Python 3.10+ supports `pdb -m module`).
debug:
	uv run python -m pdb -m $(PKG)

# ---- Quality --------------------------------------------------------------
# `uv run` only ensures flake8/mypy run inside the project environment.
# Exclusions come from .flake8 and from [tool.mypy] in pyproject.toml.
lint:
	@fail=0; \
	uv run flake8 src || fail=1; \
	uv run mypy . $(MYPY_FLAGS) || fail=1; \
	exit $$fail

lint-strict:
	@fail=0; \
	uv run flake8 src || fail=1; \
	uv run mypy . --strict || fail=1; \
	exit $$fail

# ---- Cleanup --------------------------------------------------------------
# NOTE: do NOT delete *.lock here — uv.lock must stay and is committed.
clean:
	find . -type d -name "__pycache__"   -not -path "./.venv/*" -exec rm -rf {} +
	find . -type d -name ".mypy_cache"   -not -path "./.venv/*" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -not -path "./.venv/*" -exec rm -rf {} +
	find . -type f -name "*.py[co]"      -not -path "./.venv/*" -delete
	rm -rf build/ dist/ .coverage htmlcov/

fclean: clean
	rm -rf .venv
