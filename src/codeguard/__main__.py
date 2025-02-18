"""Entry point."""

from __future__ import annotations

if __name__ == "__main__":
    import sys

    from .cli import cli

    sys.exit(cli())
