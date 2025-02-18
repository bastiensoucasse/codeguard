"""Exception."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


# region Directory Exceptions


class DirError(Exception):
    """Exception raised for errors related to directories."""


class DirNotFoundError(FileNotFoundError, DirError):
    """Exception raised when a directory is not found."""

    def __init__(self, directory: Path, *, kind: str | None = None) -> None:
        """Initializes a directory not found error.

        Args:
            directory: Path to the directory.
            kind: Kind of directory.
        """
        super().__init__(f"Could not find{f' {kind}' if kind else ''} directory {directory}.")


# endregion


# region Module File Exceptions


class ModuleFileError(Exception):
    """Exception raised for errors related to module files."""


class ModuleFileNotFoundError(FileNotFoundError, ModuleFileError):
    """Exception raised when a module file is not found."""

    def __init__(self, module_file: Path) -> None:
        """Initializes a module file not found error.

        Args:
            module_file: Path to the module file.
        """
        super().__init__(f"Could not find module file {module_file}.")


class ModuleFileReadingError(OSError, ModuleFileError):
    """Exception raised when a module file can't be read."""

    def __init__(self, module_file: Path) -> None:
        """Initializes a module file reading error.

        Args:
            module_file: Path to the module file.
        """
        super().__init__(f"Could not read module file {module_file}.")


class ModuleFileMissingDocstringError(ValueError, ModuleFileError):
    """Exception raised when a module file docstring is missing."""

    def __init__(self, module_file: Path) -> None:
        """Initializes a module file missing docstring error.

        Args:
            module_file: Path to the module file.
        """
        super().__init__(f"Missing docstring in module file {module_file}.")


# endregion


# region Test File Exceptions


class TestFileError(Exception):
    """Exception raised for errors related to test files."""


class TestFileNotFoundError(FileNotFoundError, TestFileError):
    """Exception raised when a test file is not found."""

    def __init__(self, test_file: Path) -> None:
        """Initializes a test file not found error.

        Args:
            test_file: Path to the test file.
        """
        super().__init__(f"Could not find test file {test_file}.")


class TestFileReadingError(OSError, TestFileError):
    """Exception raised when a test file can't be read."""

    def __init__(self, test_file: Path) -> None:
        """Initializes a test file reading error.

        Args:
            test_file: Path to the test file.
        """
        super().__init__(f"Could not read test file {test_file}.")


class TestFileDocstringError(ValueError, TestFileError):
    """Exception raised when a test file docstring is missing or invalid."""

    def __init__(self, test_file: Path, expected_docstring: str, found_docstring: str | None = None) -> None:
        """Initializes a test file docstring error.

        Args:
            test_file: Path to the test file.
            expected_docstring: Expected test docstring.
            found_docstring: Found test docstring. \
                If `None`, indicates that no test docstring was found.
        """
        if not found_docstring:
            super().__init__(
                f"Missing docstring in test file {test_file}.\n  Expected: {expected_docstring}",
            )
        else:
            super().__init__(
                f"Docstring mismatch in test file {test_file}.\n"
                f"  Expected: {expected_docstring}\n"
                f"  Found: {found_docstring}",
            )


# endregion


# region API Reference Documentation File Exceptions


class RefFileError(Exception):
    """Exception raised for errors related to API reference documentation files."""


class RefFileNotFoundError(FileNotFoundError, RefFileError):
    """Exception raised when an API reference documentation file is not found."""

    def __init__(self, ref_file: Path) -> None:
        """Initializes an API reference documentation file not found error.

        Args:
            ref_file: Path to the API reference documentation file.
        """
        super().__init__(f"Could not find API reference documentation file {ref_file}.")


class RefFileReadingError(OSError, RefFileError):
    """Exception raised when an API reference documentation file can't be read."""

    def __init__(self, ref_file: Path) -> None:
        """Initializes an API reference documentation file reading error.

        Args:
            ref_file: Path to the API reference documentation file.
        """
        super().__init__(f"Could not read API reference documentation file {ref_file}.")


class RefFileContentError(ValueError, RefFileError):
    """Exception raised when an API reference documentation file content is invalid."""

    def __init__(self, ref_file: Path, expected_content: str, found_content: str) -> None:
        """Initializes an API reference documentation file content error.

        Args:
            ref_file: Path to the API reference documentation file.
            expected_content: Expected API reference documentation content.
            found_content: Found API reference documentation content.
        """
        super().__init__(
            f"Content mismatch in API reference documentation file {ref_file}.\n"
            f"  Expected:\n{expected_content}\n"
            f"  Found:\n{found_content}",
        )


# endregion
