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
	@ poetry run nox --report reports/nox.json
