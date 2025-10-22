from nox import Session, options, project
from nox_uv import session

options.default_venv_backend = "uv"

# MANDATORY CHECKS


@session(uv_groups=["test"])
def test(s: Session) -> None:
    s.run("python", "-m", "pytest", *s.posargs)


@session(uv_groups=["types"])
def types(s: Session) -> None:
    s.run("mypy", "--no-namespace-packages", *s.posargs)


@session(uv_only_groups=["lint_format"])
def lint(s: Session) -> None:
    s.run("ruff", "check", *s.posargs)
    s.run("ruff", "format", "--check")


@session(uv_only_groups=["security"])
def security(s: Session) -> None:
    pyproject = project.load_toml("pyproject.toml")
    s.run(
        "bandit",
        "-c",
        "pyproject.toml",
        "-r",
        *pyproject["tool"]["nox"]["bandit"]["files_to_scan"],
        *s.posargs,
    )


# SHORTHANDS


@session(uv_only_groups=["lint_format"], default=False)
def fix(s: Session) -> None:
    s.run("ruff", "format")
    s.run("ruff", "check", "--fix")


@session(python=False, default=False)
def build(s: Session) -> None:
    s.run("uv", "build", "--all-packages", *s.posargs)


@session(python=False, default=False)
def sync(s: Session) -> None:
    s.run("uv", "sync", "--all-packages", *s.posargs)
