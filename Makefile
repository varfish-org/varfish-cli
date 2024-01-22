.PHONY: default
default: help

.PHONY: help
help:
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@echo "  format        Format code with isort and black"
	@echo "  lint          Lint code with flake8, isort and black"
	@echo "  format-black  Format code with black"
	@echo "  lint-black    Lint code with black"
	@echo "  format-isort  Format code with isort"
	@echo "  lint-isort    Lint code with isort"
	@echo "  lint-flake8   Lint code with flake8"
	@echo "  test          Run tests"
	@echo "  test-update-snapshots"
	@echo "                Run tests and update snapshots"

.PHONY: format
format: format-isort format-black

.PHONY: lint
lint: lint-flake8 lint-isort lint-black

.PHONY: format-black
black:
	black -l 100 .

.PHONY: lint-black
black-check:
	black -l 100 --check .

.PHONY: format-isort
format-isort:
	isort --force-sort-within-sections --profile=black .

.PHONY: lint-isort
lint-isort:
	isort --force-sort-within-sections --profile=black --check .

.PHONY: lint-flake8
lint-flake8:
	flake8

.PHONY: test
test:
	TZ=UTC LC_ALL=C pytest .

.PHONY: test-update-snapshots
test-update-snapshots:
	TZ=UTC LC_ALL=C pytest --snapshot-update .
