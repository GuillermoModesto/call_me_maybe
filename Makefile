# ---- Configuration --------------------------------------------------------
PKG        = src
# Flags exigidos por el enunciado para la regla `lint`.
MYPY_FLAGS = --warn-return-any \
             --warn-unused-ignores \
             --ignore-missing-imports \
             --disallow-untyped-defs \
             --check-untyped-defs

.DEFAULT_GOAL := run
.PHONY: install run debug lint lint-strict clean fclean

# ---- Environment ----------------------------------------------------------
# El corrector y la moulinette solo ejecutan `uv sync`.
install:
	uv sync

# ---- Execution ------------------------------------------------------------
# Uso: make run
#      make run ARGS="--input data/input/tests.json --output data/output/out.json"
run:
	uv run python -m $(PKG) $(ARGS)

# Ejecuta el paquete bajo el depurador pdb (Python 3.10+ admite `pdb -m modulo`).
debug:
	uv run python -m pdb -m $(PKG)

# ---- Quality --------------------------------------------------------------
# `uv run` solo garantiza que flake8/mypy se ejecuten dentro del entorno del
# proyecto. Las exclusiones salen de .flake8 y de [tool.mypy] en pyproject.toml.
lint:
	@fail=0; \
	uv run flake8 . || fail=1; \
	uv run mypy . $(MYPY_FLAGS) || fail=1; \
	exit $$fail

lint-strict:
	@fail=0; \
	uv run flake8 . || fail=1; \
	uv run mypy . --strict || fail=1; \
	exit $$fail

# ---- Cleanup --------------------------------------------------------------
# OJO: NO borrar *.lock aquí — uv.lock debe permanecer y va commiteado.
clean:
	find . -type d -name "__pycache__"   -not -path "./.venv/*" -exec rm -rf {} +
	find . -type d -name ".mypy_cache"   -not -path "./.venv/*" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -not -path "./.venv/*" -exec rm -rf {} +
	find . -type f -name "*.py[co]"      -not -path "./.venv/*" -delete
	rm -rf build/ dist/ .coverage htmlcov/

fclean: clean
	rm -rf .venv
