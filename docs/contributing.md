# Contributor Guide

Thank you for your interest in improving this project.
This project is open-source under the [MIT](https://opensource.org/license/mit/) license and welcomes contributions in the form of bug reports, feature requests, and pull requests.

Here is a list of important resources for contributors:

* [Source Code](https://github.com/taconi/cachetoolz)
* [Documentation](https://taconi.github.io/cachetoolz)
* [Issue Tracker](https://github.com/taconi/cachetoolz/issues)
* [Code of Conduct]()

## How to report a bug
Report bugs on the [Issue Tracker](https://github.com/taconi/cachetoolz/issues).

When filing an issue, make sure to answer these questions:

* Which operating system and Python version are you using?
* Which version of this project are you using?
* What did you do?
* What did you expect to see?
* What did you see instead?

The best way to get your bug fixed is to provide a test case, and/or steps to reproduce the issue.

## How to set up your development environment

You need Python 3.8+, [Poetry](https://python-poetry.org) and optionally [GNU Make](https://www.gnu.org/software/make/).

Install the package with development requirements:
=== "With Make"
    ```bash
    make install
    ```
=== "Without Make"
    ```bash
	poetry install --with dev --with test --with ci --with docs -E redis -E mongo
	poetry run pre-commit install
	poetry run gitlint install-hook
    ```

You can now run an interactive Python session, or Nox with nox-poetry:
```bash
poetry run python
poetry run nox
```

## How to test the project
Run the full test suite:
=== "With Make"
    ```bash
    NOXSESSION=tests make nox
    ```
=== "Without Make"
    ```bash
    poetry run nox -s tests
    ```

List the available Nox sessions:
```bash
poetry run nox --list-sessions
```

You can also run a specific Nox session. For example, invoke the unit test suite like this:
=== "With Make"
    ```bash
    NOXSESSION=fmt make nox
    ```
=== "Without Make"
    ```bash
    poetry run nox -s fmt
    ```

Unit tests are located in the tests directory, and are written using the [ward](https://ward.readthedocs.io) testing framework.

## How to submit changes

Open a [pull request](https://github.com/taconi/cachetoolz/pulls) to submit changes to this project.

Your pull request needs to meet the following guidelines for acceptance:

* The Nox test suite must pass without errors and warnings.
* Include unit tests. This project maintains code coverage.
* If your changes add functionality, update the documentation accordingly.

Feel free to submit early, though—we can always iterate on this.
