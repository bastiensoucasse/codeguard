"""Command-line interface."""

from __future__ import annotations

from pathlib import Path

import rich_click as click

from . import __doc__ as app_doc
from .checker import Checker


@click.command(help=app_doc, context_settings={"show_default": True})
@click.argument("project_dir", type=Path, required=False, default=None)
@click.argument("modules_dir_name", type=str, required=False, default=None)
@click.option("--src-dir-name", type=str, default="src")
@click.option("--tests-dir-name", type=str, default="tests")
@click.option("--docs-dir-name", type=str, default="docs")
@click.option("--ref-dir-name", type=str, default="reference")
@click.option("--fix", is_flag=True, default=False)
@click.option("--rm", is_flag=True, default=False)
def cli(  # noqa: PLR0913
    project_dir: Path | None = None,
    modules_dir_name: str | None = None,
    *,
    src_dir_name: str = "src",
    tests_dir_name: str = "tests",
    docs_dir_name: str = "docs",
    ref_dir_name: str = "reference",
    fix: bool = False,
    rm: bool = False,
) -> None:
    """Runs the command-line interface."""
    checker = Checker.from_project(
        project_dir,
        modules_dir_name,
        src_dir_name=src_dir_name,
        tests_dir_name=tests_dir_name,
        docs_dir_name=docs_dir_name,
        ref_dir_name=ref_dir_name,
        auto_fix=fix,
        auto_remove=rm,
    )
    checker.check()
