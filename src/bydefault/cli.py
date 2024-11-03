"""Command-line interface for byDefault."""

import sys
from typing import List, Optional


def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the byDefault CLI.

    Args:
        args: Command line arguments (defaults to sys.argv[1:])

    Returns:
        int: Exit code (0 for success, non-zero for failure)
    """
    if args is None:
        args = sys.argv[1:]

    # TODO: Implement CLI logic
    print("byDefault CLI - Version 0.1.0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
