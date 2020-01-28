.PHONY: default black flake8 mypy test test-v test-vv coverage_html

default: black flake8 mypy test coverage_html

black:
	black -l 100 .

black-check:
	black -l 100 --check .

flake8:
	flake8 .

mypy:
	mypy varfish_cli

test:
	pytest --disable-pytest-warnings

test-v:
	pytest -v --disable-pytest-warnings

test-vv:
	pytest -vv --disable-pytest-warnings
