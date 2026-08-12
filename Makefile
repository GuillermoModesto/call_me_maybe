VENV        = .venv
PYTHON      = $(VENV)/bin/python
PIP         = $(VENV)/bin/pip
MAIN        = call_me_maybe.py

EXCLUDE     = .venv,build,dist,__pycache__
FLAKE_FLAGS = --exclude=$(EXCLUDE) --extend-ignore=W191,E101
MYPY_FLAGS  = --exclude '(\.venv|build|dist)' \
              --warn-return-any \
              --warn-unused-ignores \
              --ignore-missing-imports \
              --disallow-untyped-defs \
              --check-untyped-defs

.DEFAULT_GOAL := run
.PHONY: install run debug lint lint-strict clean fclean

$(VENV)/bin/python:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -q flake8 mypy
	@echo "venv ready. Activate with: source $(VENV)/bin/activate"

install: $(VENV)/bin/python
	$(PIP) install --upgrade pip
	# or: $(PIP) install -r requirements.txt

run: $(VENV)/bin/python
	$(PYTHON) $(MAIN)

debug: $(VENV)/bin/python
	$(PYTHON) -m pdb $(MAIN)

lint: $(VENV)/bin/python
	@fail=0; \
	$(VENV)/bin/flake8 $(FLAKE_FLAGS) . || fail=1; \
	$(VENV)/bin/mypy . $(MYPY_FLAGS) || fail=1; \
	exit $$fail

lint-strict: $(VENV)/bin/python
	@fail=0; \
	$(VENV)/bin/flake8 $(FLAKE_FLAGS) . || fail=1; \
	$(VENV)/bin/mypy . --exclude '(\.venv|build|dist)' --strict || fail=1; \
	exit $$fail

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf build/ dist/ .coverage htmlcov/ .pytest_cache/

fclean: clean
	rm -rf $(VENV)
