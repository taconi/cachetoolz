"""Modules to automate commands."""
from os import environ

from nox_poetry import Session, session

SRC = 'cachetoolz'
PYTHON_VERSIONS = ['3.8', '3.9', '3.10', '3.11']


@session(reuse_venv=True)
def fmt(session: Session):
    """Format code."""
    session.run_always(*'poetry  install --with dev'.split(), external=True)

    session.run('autoflake', '--in-place', '-r', SRC)
    session.run('isort', SRC)
    session.run('black', SRC)
    session.run('docformatter', '--in-place', '-r', SRC)


@session(reuse_venv=True)
def check(session: Session):
    """Static check."""
    session.run_always(*'poetry  install --with dev'.split(), external=True)

    session.run('flake8', SRC)
    session.run('isort', '--check-only', '--diff', SRC)
    session.run('black', '--check', '--diff', SRC)
    session.run('docformatter', '-r', SRC)


@session(python=PYTHON_VERSIONS, reuse_venv=True)
def tests(session: Session):
    """Run tests."""
    session.run_always(
        *'poetry  install --with test -E redis -E mongo'.split(), external=True
    )

    session.run('coverage', 'run', '-m', 'ward', 'test')
    session.run('coverage', 'report')
    session.run('coverage', 'xml')
    session.run('coverage', 'html')


@session(reuse_venv=True)
def docs(session: Session):
    """Serve documentation."""
    session.run_always(*'poetry install --only docs'.split(), external=True)

    session.run('mkdocs', 'serve')


@session(reuse_venv=True)
def publish_docs(session: Session):
    """Publish documentation."""
    session.run_always(*'poetry install --only docs'.split(), external=True)

    session.run('mkdocs', 'gh-deploy')


@session(reuse_venv=True)
def publish_pkg(session: Session):
    """Publish package."""
    session.run(
        'poetry',
        'publish',
        '--build',
        f'--username={environ.get("CACHETOOLZ_PYPI_USARNAME", "taconi")}',
        f'--password={environ["CACHETOOLZ_PYPI_PASSWORD"]}',
    )
