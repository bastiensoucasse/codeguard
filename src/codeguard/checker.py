"""Python project checker."""

from __future__ import annotations

from pathlib import Path

from rich import print  # noqa: A004

from .exceptions import (
    DirError,
    DirNotFoundError,
    RefFileContentError,
    RefFileError,
    RefFileNotFoundError,
    TestFileDocstringError,
    TestFileError,
    TestFileNotFoundError,
)
from .module import Module


class Checker:
    """Python project checker."""

    modules_dir: Path
    """Path to the modules source directory."""

    tests_dir: Path
    """Path to the tests directory."""

    ref_dir: Path
    """Path to the API reference documentation directory."""

    auto_fix: bool
    """Whether the checker should try auto-fixing issues in test and API reference documentation files."""

    auto_remove: bool
    """Whether the checker should try auto-removing unexpected files."""

    modules: list[Module]
    """List of modules found in the modules source directory."""

    def __init__(
        self,
        modules_dir: Path,
        tests_dir: Path,
        ref_dir: Path,
        *,
        auto_fix: bool = False,
        auto_remove: bool = False,
    ) -> None:
        """Initializes a Python project checker.

        Args:
            modules_dir: Path to the modules source directory.
            tests_dir: Path to the tests directory.
            ref_dir: Path to the API reference documentation directory.
            auto_fix: Whether the checker should try auto-fixing issues in test and API reference documentation files.
            auto_remove: Whether the checker should try auto-removing unexpected files.
        """
        self.modules_dir = modules_dir.resolve()
        self.tests_dir = tests_dir.resolve()
        self.ref_dir = ref_dir.resolve()
        self.auto_fix = auto_fix
        self.auto_remove = auto_remove

        self.modules = [
            Module(mf, modules_dir=self.modules_dir, tests_dir=self.tests_dir, ref_dir=self.ref_dir)
            for mf in self.modules_dir.rglob("*.py")
            if not mf.name.startswith("_")
        ]

    def check_module_test_file(self, module: Module) -> str | None:
        """Checks the test file of a given module and handles any errors that occur.

        Args:
            module: Module whose test file is to be checked.

        Returns:
            msg: Message indicating the result of the test file check, \
                or `None` if no issues are found.
        """
        try:
            module.check_test_file()
        except TestFileError as e:
            if self.auto_fix:
                fix_msg = f"[green]Fixed: {str(e).replace('\n', '\n  ')}."
                if isinstance(e, TestFileNotFoundError):
                    module.fix_missing_test_file()
                    return fix_msg
                if isinstance(e, TestFileDocstringError):
                    module.fix_test_file_docstring()
                    return fix_msg
            return f"[red]{e!s}"
        return None

    def check_module_ref_file(self, module: Module) -> str | None:
        """Checks the API reference documentation file of a given module and handles any errors that occur.

        Args:
            module: Module whose API reference documentation file is to be checked.

        Returns:
            msg: Message indicating the result of the API reference documentation file check, \
                or `None` if no issues are found.
        """
        try:
            module.check_ref_file()
        except RefFileError as e:
            if self.auto_fix:
                fix_msg = f"[green]Fixed: {str(e).replace('\n', '\n  ')}."
                if isinstance(e, RefFileNotFoundError):
                    module.fix_missing_ref_file()
                    return fix_msg
                if isinstance(e, RefFileContentError):
                    module.fix_ref_file_content()
                    return fix_msg
            return f"[red]{e!s}"
        return None

    def check_module(self, module: Module) -> list[str]:
        """Checks the specified module for its test file and API reference documentation file.

        Args:
            module: Module to check.

        Returns:
            msgs: List of messages indicating the result of the checks.
        """
        test_msg = self.check_module_test_file(module)
        ref_msg = self.check_module_ref_file(module)
        return [msg for msg in (test_msg, ref_msg) if msg]

    def check_modules(self) -> dict[Module, list[str]]:
        """Checks all modules in the project.

        Returns:
            module_msgs: Dictionary mapping each module to a list of messages indicating issues or actions taken.
        """
        return {module: msgs for module in self.modules if (msgs := self.check_module(module))}

    def _check_unexpected_files(self) -> list[str]:
        msgs: list[str] = []
        valid_module_files = {m.module_file for m in self.modules}

        for test_file in self.tests_dir.rglob("test_*.py"):
            mf = self.modules_dir / test_file.relative_to(self.tests_dir).with_name(
                test_file.name.removeprefix("test_"),
            )
            if mf not in valid_module_files:
                msg = f"Unexpected test file {test_file}."
                if self.auto_remove:
                    try:
                        test_file.unlink()
                        msgs.append(f"[green]Removed: {msg}")
                        continue
                    except OSError as e:
                        msgs.append(f"[red]Error removing: {msg}\n  {e!s}")
                        continue
                msgs.append(f"[red]{msg}")

        for ref_file in self.ref_dir.rglob("*.md"):
            mf = self.modules_dir / ref_file.relative_to(self.ref_dir).with_suffix(".py")
            if mf not in valid_module_files:
                msg = f"Unexpected API reference documentation file {ref_file}."
                if self.auto_remove:
                    try:
                        ref_file.unlink()
                        msgs.append(f"[green]Removed: {msg}")
                        continue
                    except OSError as e:
                        msgs.append(f"[red]Error removing: {msg}\n  {e!s}")
                        continue
                msgs.append(f"[red]{msg}")

        return msgs

    def check(self) -> bool:
        """Checks for errors in test files and API reference documentation files, as well as unexpected files.

        Returns:
            overall_errors: `True` if any errors are found; otherwise, `False`.
        """
        overall_errors = False

        if module_msgs := self.check_modules():
            overall_errors = True
            for module, msgs in module_msgs.items():
                print(f"[bold]{module.qualname}:")
                for msg in msgs:
                    print(f"- {msg}")

        if msgs := self._check_unexpected_files():
            overall_errors = True
            print("[bold]Unexpected files:")
            for msg in msgs:
                print(f"- {msg}")

        if not overall_errors:
            print("[bold green]All checks passed!")

        return overall_errors

    @classmethod
    def _validate_project_dir(cls, project_dir: Path | None) -> Path:
        if not project_dir:
            return Path.cwd()

        project_dir = project_dir.resolve()
        if not project_dir.is_dir():
            raise DirNotFoundError(project_dir, kind="project")
        return project_dir

    @classmethod
    def _infer_modules_dir(cls, src_dir: Path) -> Path:
        src_dir_subdirs = [p for p in src_dir.iterdir() if p.is_dir()]
        if (count := len(src_dir_subdirs)) != 1:
            msg = f"Expected a single modules source directory in source directory {src_dir} (found {count})."
            raise DirError(msg)
        return src_dir_subdirs[0]

    @classmethod
    def _find_modules_dir(cls, project_dir: Path, src_dir_name: str, modules_dir_name: str | None) -> Path:
        src_dir = project_dir / src_dir_name
        if not src_dir.is_dir():
            raise DirNotFoundError(src_dir, kind="source")

        if not modules_dir_name:
            return cls._infer_modules_dir(src_dir)

        modules_dir = src_dir / modules_dir_name
        if not modules_dir.is_dir():
            raise DirNotFoundError(modules_dir, kind="modules source")
        return modules_dir

    @classmethod
    def _find_tests_dir(cls, project_dir: Path, tests_dir_name: str) -> Path:
        tests_dir = project_dir / tests_dir_name
        if not tests_dir.is_dir():
            raise DirNotFoundError(tests_dir, kind="test")
        return tests_dir

    @classmethod
    def _find_ref_dir(cls, project_dir: Path, docs_dir_name: str, ref_dir_name: str) -> Path:
        docs_dir = project_dir / docs_dir_name
        if not docs_dir.is_dir():
            raise DirNotFoundError(docs_dir, kind="documentation")

        ref_dir = docs_dir / ref_dir_name
        if not ref_dir.is_dir():
            raise DirNotFoundError(ref_dir, kind="API reference documentation")
        return ref_dir

    @classmethod
    def from_project(  # noqa: PLR0913
        cls,
        project_dir: Path | None = None,
        modules_dir_name: str | None = None,
        *,
        src_dir_name: str = "src",
        tests_dir_name: str = "tests",
        docs_dir_name: str = "docs",
        ref_dir_name: str = "reference",
        auto_fix: bool = False,
        auto_remove: bool = False,
    ) -> Checker:
        """Creates a checker from a project directory.

        Args:
            project_dir: Path to the project directory. \
                If `None`, uses the current directory.
            modules_dir_name: Name of the modules source directory. \
                If `None`, tries to infer its name.
            src_dir_name: Name of the source directory.
            tests_dir_name: Name of the tests directory.
            docs_dir_name: Name of the documentation directory.
            ref_dir_name: Name of the API reference documentation directory.
            auto_fix: Whether the checker should try auto-fixing issues.
            auto_remove: Whether the checker should try auto-removing unexpected files.

        Returns:
            checker: Project checker for the source, test, and API reference documentation directories.
        """
        project_dir = cls._validate_project_dir(project_dir)
        modules_dir = cls._find_modules_dir(project_dir, src_dir_name, modules_dir_name)
        tests_dir = cls._find_tests_dir(project_dir, tests_dir_name)
        ref_dir = cls._find_ref_dir(project_dir, docs_dir_name, ref_dir_name)
        return cls(modules_dir, tests_dir, ref_dir, auto_fix=auto_fix, auto_remove=auto_remove)
