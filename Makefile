.PHONY: install
install:
	echo 'Installing dependencies'
	@ poetry install --with dev --with test --with ci --with docs -E redis -E mongo
	echo 'Installing pre-commit'
	@ poetry run pre-commit install
	echo 'Installing gitlint'
	@ poetry run gitlint install-hook


.PHONY: nox
nox:
	@ poetry run nox

.PHONY: clear
clear:
	@ find . -name '*.pyc' -exec rm -rf {} \;
	@ find . -name '__pycache__' -exec rm -rf {} \;
	@ rm -f coverage.xml
	@ rm -f .coverage
	@ rm -rf .nox/
	@ rm -rf .cache/
	@ rm -rf .mypy_cache/
	@ rm -rf dist/
	@ rm -rf build/
	@ rm -rf site/
	@ rm -rf reports/nox.json
	@ rm -rf reports/coverage/
	@ rm -rf reports/flake8/
