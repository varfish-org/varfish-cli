.PHONY: all
all: black

.PHONY: black
black:
	black -l 100 .

.PHONY: test
test:
	black -l 100 --check .

.PHONY: pytest
pytest:
	pytest .

.PHONY: lint-all
lint-all: bandit pyflakes pep257 prospector

.PHONY: bandit
bandit:
	bandit -c bandit.yml -r varfish_cli

.PHONY: pyflakes
pyflakes:
	pyflakes varfish_cli tests

.PHONY: pep257
pep257:
	pep257

.PHONY: flake8
flake8:
	flake8

.PHONY: isort
isort:
	isort --force-sort-within-sections --profile=black .
