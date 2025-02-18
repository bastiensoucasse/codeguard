"""Python module."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .exceptions import (
    ModuleFileMissingDocstringError,
    ModuleFileNotFoundError,
    ModuleFileReadingError,
    RefFileContentError,
    RefFileNotFoundError,
    RefFileReadingError,
    TestFileDocstringError,
    TestFileNotFoundError,
    TestFileReadingError,
)

if TYPE_CHECKING:
    from pathlib import Path

MODULE_NAME_EXCEPTIONS: dict[str, str] = {
    "Cli": "CLI",
    "Geotiff": "GeoTIFF",
}


class Module:
    """Python module."""

    module_file: Path
    """Path to the module file."""

    name: str
    """Formatted name."""

    qualname: str
    """Fully qualified name (i.e., import path)."""

    cli: bool
    """Whether the module is a CLI module."""

    test_file: Path
    """Path to the test file."""

    ref_file: Path
    """Path to the API reference documentation file."""

    module_docstring: str
    """Module docstring line, stripped of quotes."""

    test_docstring: str
    """Test docstring."""

    ref_content: str
    """API reference documentation content."""

    def read_module_docstring(self) -> str:
        """Reads the docstring line from the module file, stripped of quotes.

        Returns:
            module_docstring: Module docstring line, stripped of quotes.

        Raises:
            ModuleFileReadingError: If the module file can't be read.
            ModuleFileMissingDocstringError: If the module docstring is missing.
        """
        try:
            with self.module_file.open(encoding="utf-8") as f:
                line = f.readline()
        except OSError as e:
            raise ModuleFileReadingError(self.module_file) from e

        module_docstring = line.strip()
        if not module_docstring.startswith('"""') and not module_docstring.startswith("'''"):
            raise ModuleFileMissingDocstringError(self.module_file)

        return module_docstring.removeprefix('"""').removeprefix("'''").removesuffix('"""').removesuffix("'''").strip()

    def generate_test_docstring(self) -> str:
        """Generates the docstring for the test file.

        Returns:
            test_docstring: Test docstring.
        """
        docstring = self.module_docstring
        return f'"""Tests: {docstring}"""'

    def generate_ref_content(self) -> str:
        """Generates the content for the API reference documentation file.

        Returns:
            ref_content: API reference documentation content.
        """
        if self.cli:
            return (
                f"# {self.name}\n"
                "\n"
                "::: mkdocs-click\n"
                "    :module: rrod.cli\n"
                "    :command: cli\n"
                "    :prog_name: rrod\n"
                "    :style: table"
            )

        return f"# {self.name}\n\n::: {self.qualname}"

    def __init__(self, module_file: Path, *, modules_dir: Path, tests_dir: Path, ref_dir: Path) -> None:
        """Initializes a Python module.

        Args:
            module_file: Path to the module file.
            modules_dir: Path to the modules source directory.
            tests_dir: Path to the tests directory.
            ref_dir: Path to the API reference documentation directory.

        Raises:
            ModuleFileNotFoundError: If the module file is not found.
        """
        module_file = module_file.resolve()
        if not module_file.is_file():
            raise ModuleFileNotFoundError(module_file)
        self.module_file = module_file

        modules_dir = modules_dir.resolve()
        tests_dir = tests_dir.resolve()
        ref_dir = ref_dir.resolve()

        name = module_file.stem.replace("_", " ").title()
        self.name = MODULE_NAME_EXCEPTIONS.get(name, name)
        self.qualname = module_file.relative_to(modules_dir.parent).with_suffix("").as_posix().replace("/", ".")
        self.cli = module_file.stem == "cli"
        self.test_file = tests_dir / module_file.relative_to(modules_dir).with_name(f"test_{module_file.name}")
        self.ref_file = ref_dir / module_file.relative_to(modules_dir).with_suffix(".md")
        self.module_docstring = self.read_module_docstring()
        self.test_docstring = self.generate_test_docstring()
        self.ref_content = self.generate_ref_content()

    def check_test_file(self) -> None:
        """Checks if the test file for the module exists and has a valid docstring.

        Raises:
            TestFileNotFoundError: If the test file is not found.
            TestFileReadingError: If the test file can't be read.
            TestFileDocstringError: If the test docstring is missing or invalid.
        """
        if self.cli:
            return

        if not self.test_file.is_file():
            raise TestFileNotFoundError(self.test_file)

        try:
            with self.test_file.open(encoding="utf-8") as f:
                line = f.readline()
        except OSError as e:
            raise TestFileReadingError(self.test_file) from e

        found_docstring = line.strip()
        if not found_docstring.startswith('"""') and not found_docstring.startswith("'''"):
            raise TestFileDocstringError(self.test_file, self.test_docstring)

        if found_docstring != self.test_docstring:
            raise TestFileDocstringError(self.test_file, self.test_docstring, found_docstring)

    def check_ref_file(self) -> None:
        """Checks if the API reference documentation file for the module exists and has valid content.

        Raises:
            RefFileNotFoundError: If the API reference documentation file is not found.
            RefFileReadingError: If the API reference documentation file can't be read.
            RefFileContentError: If the API reference documentation content is invalid.
        """
        if not self.ref_file.is_file():
            raise RefFileNotFoundError(self.ref_file)

        try:
            text = self.ref_file.read_text(encoding="utf-8")
        except OSError as e:
            raise RefFileReadingError(self.ref_file) from e

        found_content = text.strip()
        if found_content != self.ref_content:
            raise RefFileContentError(self.ref_file, self.ref_content, found_content)

    def fix_missing_test_file(self) -> None:
        """Creates the missing test file with the expected docstring and no additional content."""
        self.test_file.parent.mkdir(parents=True, exist_ok=True)
        self.test_file.write_text(self.test_docstring + "\n", encoding="utf-8")

    def fix_test_file_docstring(self) -> None:
        """Edits the test file so its docstring matches the expected one."""
        content = self.test_file.read_text(encoding="utf-8")

        if lines := content.splitlines():
            lines[0] = self.test_docstring
            new_content = "\n".join(lines)
        else:
            new_content = self.test_docstring

        self.test_file.write_text(new_content + "\n", encoding="utf-8")

    def fix_missing_ref_file(self) -> None:
        """Creates the missing API reference documentation file with the expected content."""
        self.ref_file.parent.mkdir(parents=True, exist_ok=True)
        self.ref_file.write_text(self.ref_content + "\n", encoding="utf-8")

    def fix_ref_file_content(self) -> None:
        """Overwrites the invalid API reference documentation file so its content matches the expected one."""
        self.ref_file.write_text(self.ref_content + "\n", encoding="utf-8")
