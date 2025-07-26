import nox

PYTHON_TESTING_VERSIONS = ["3.12", "3.13"]


@nox.session(venv_backend="uv", python=PYTHON_TESTING_VERSIONS)
def test_sqlalchemy(session: nox.Session) -> None:
    session.run(
        "uv",
        "sync",
        "--extra=test",
        "--extra=sqlalchemy",
        f"--python={session.virtualenv.location}",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )
    session.run("pytest")


@nox.session(venv_backend="uv", python=PYTHON_TESTING_VERSIONS)
def test_pymongo(session: nox.Session) -> None:
    session.run(
        "uv",
        "sync",
        "--extra=test",
        "--extra=pymongo",
        f"--python={session.virtualenv.location}",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )
    session.run("pytest")
