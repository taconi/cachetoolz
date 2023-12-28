"""Modules to automate commands."""
from os import environ

import nox
from nox_poetry import Session, session

nox.options.report = 'reports/nox.json'
nox.options.stop_on_first_error = True
nox.options.reuse_existing_virtualenvs = True
nox.options.error_on_missing_interpreters = True

SRC = 'cachetoolz'
PYTHON_VERSIONS = ['3.8', '3.9', '3.10', '3.11', '3.12']


@session
def fmt(session: Session):
    """Format code."""
    session.run_always(*'poetry  install --with dev'.split(), external=True)

    session.run('autoflake', '--in-place', '-r', SRC)
    session.run('isort', SRC)
    session.run('black', SRC)
    session.run('docformatter', '--in-place', '-r', SRC)


@session
def check(session: Session):
    """Static check."""
    session.run_always(*'poetry  install --with dev'.split(), external=True)

    session.run('flake8', SRC)
    session.run('isort', '--check-only', '--diff', SRC)
    session.run('black', '--check', '--diff', SRC)
    session.run('docformatter', '-r', SRC)


@session(python=PYTHON_VERSIONS)
def tests(session: Session):
    """Run tests."""
    session.run_always(
        *'poetry  install --with test -E redis -E mongo'.split(), external=True
    )

    session.run('coverage', 'run', '-m', 'ward', 'test')
    session.run('coverage', 'report')
    session.run('coverage', 'xml')
    session.run('coverage', 'html')


@session
def docs(session: Session):
    """Serve documentation."""
    session.run_always(*'poetry install --only docs'.split(), external=True)

    session.run('mkdocs', 'serve')


@session
def publish_docs(session: Session):
    """Publish documentation."""
    session.run_always(*'poetry install --only docs'.split(), external=True)

    session.run('mkdocs', 'gh-deploy')


@session
def publish_pkg(session: Session):
    """Publish package."""
    session.run(
        'poetry',
        'publish',
        '--build',
        f'--username={environ.get("CACHETOOLZ_PYPI_USARNAME", "taconi")}',
        f'--password={environ["CACHETOOLZ_PYPI_PASSWORD"]}',
    )
