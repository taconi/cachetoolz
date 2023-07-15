SRC := cache_tools/

.PHONY: install
install:
	poetry install --with dev --with test

.PHONY: check
check:
	@ poetry run flake8 $(SRC)
	@ poetry run isort --check-only --diff $(SRC)
	@ poetry run black --check --diff $(SRC)
	@ poetry run docformatter -r $(SRC)

.PHONY: fmt
fmt:
	@ poetry run autoflake --in-place -r $(SRC)
	@ poetry run isort $(SRC)
	@ poetry run black $(SRC)
	@ poetry run docformatter --in-place -r $(SRC)

.PHONY: tests
tests:
	@ coverage run -m ward test
	@ coverage report
	@ coverage html
