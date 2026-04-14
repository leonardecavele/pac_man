# colors
GREEN := \e[0;32m
RESET := \e[0m

# helpers
FLAKE8_SUCCESS := printf '%b\n' "$(GREEN)Success: flake8$(RESET)"

# structure
SRC_DIRECTORIES := display parsing gameplay entity
DIRS := . src $(addprefix src/,$(SRC_DIRECTORIES))
MAIN := src.main
ARGS ?= config.json
VENV := .venv
VENV_STAMP := $(VENV)/stamp

POETRY_LOCK := poetry.lock
PYPROJECT_TOML := pyproject.toml

PYCACHES = $(addsuffix /__pycache__,$(DIRS))
MYPYCACHES = $(addsuffix /.mypy_cache,$(DIRS))
EXCLUDE = --exclude $(VENV)

# tools
PYTHON := $(VENV)/bin/python3
FLAKE8 := $(PYTHON) -m flake8 $(EXCLUDE)
MYPY := $(PYTHON) -m mypy $(EXCLUDE)
PIP := $(PYTHON) -m pip
POETRY := POETRY_VIRTUALENVS_IN_PROJECT=true $(PYTHON) -m poetry

# flags
MYPY_FLAGS := \
		--check-untyped-defs \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--warn-return-any \
		--disallow-untyped-defs

# rules
install: $(VENV_STAMP) $(POETRY_LOCK) | $(PYTHON)
	$(POETRY) install --no-root

install-dev: $(VENV_STAMP) $(POETRY_LOCK) | $(PYTHON)
	$(POETRY) install --with dev --no-root

run: install
	@$(PYTHON) -m $(MAIN) $(ARGS)

build: install-dev
	rm -drf dist
	$(POETRY) run python -m nuitka \
		--standalone \
		--onefile \
		--output-filename=pac-man \
		--output-dir=dist \
		--include-data-dir=assets=assets \
		src/main.py

clean:
	rm -rf $(PYCACHES) $(MYPYCACHES)
	rm -rf $(VENV)

debug: install-dev
	@$(PYTHON) -m $(MAIN) $(ARGS)
	@$(PYTHON) -m pdb -m $(MAIN) $(ARGS)

lint: install-dev
	@$(FLAKE8) && $(FLAKE8_SUCCESS)
	@$(MYPY) . $(MYPY_FLAGS)

$(PYTHON):
	@python3 -m venv $(VENV)
	@touch $(VENV_STAMP)
	@$(PIP) install -U pip
	@$(PIP) install -U poetry

$(POETRY_LOCK): $(PYPROJECT_TOML) | $(PYTHON)
	@$(POETRY) lock

$(VENV_STAMP): $(PYPROJECT_TOML)
	@rm -rf $(VENV)

# miscellaneous
.PHONY: install run debug lint clean
