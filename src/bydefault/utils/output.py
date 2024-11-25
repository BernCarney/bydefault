"""Terminal output formatting utilities."""

import rich_click as click
from rich.console import Console

# One Dark theme colors
CHALKY = "#e5c07b"  # Light yellow
CORAL = "#e06c75"  # Light red
CYAN = "#56b6c2"  # Cyan
MALIBU = "#61afef"  # Light blue
SAGE = "#98c379"  # Light green
VIOLET = "#c678dd"  # Purple
STONE = "#5c6370"  # Gray
IVORY = "#abb2bf"  # Light gray

# Configure rich-click styling using One Dark colors
click.rich_click.USE_RICH_MARKUP = True
click.rich_click.USE_MARKDOWN = True

# Command and options styling
click.rich_click.STYLE_COMMAND = f"bold {MALIBU}"  # Commands in light blue
click.rich_click.STYLE_OPTION = f"bold {CYAN}"  # Options in cyan
click.rich_click.STYLE_SWITCH = f"bold {SAGE}"  # Switches in light green
click.rich_click.STYLE_METAVAR = CHALKY  # Metavars in light yellow
click.rich_click.STYLE_METAVAR_SEPARATOR = STONE  # Separators in gray

# Help text styling
click.rich_click.STYLE_HELPTEXT = IVORY  # Help text in light gray
click.rich_click.STYLE_HEADER_TEXT = f"bold {IVORY}"  # Headers in bold light gray

# Error styling
click.rich_click.STYLE_ERRORS_MESSAGE = f"bold {CORAL}"  # Errors in light red
click.rich_click.STYLE_ERRORS_SUGGESTION = STONE  # Suggestions in gray
click.rich_click.STYLE_ERRORS_CMD = MALIBU  # Error commands in light blue


def print_step_result(console: Console, success: bool, end: str = "\n") -> None:
    """Print a step result indicator.

    Args:
        console: Rich console instance for output
        success: Whether the step succeeded
        end: String appended after the output (default: newline)
    """
    symbol = "[success]✓[/success]" if success else "[error]✗[/error]"
    console.print(symbol, end=end)


def print_validation_error(
    console: Console, line_number: int, message: str, indent: int = 2
) -> None:
    """Print a validation error message.

    Args:
        console: Rich console instance for output
        line_number: Line number where error occurred
        message: Error message to display
        indent: Number of spaces to indent (default: 2)
    """
    console.print(
        " "
        * indent
        + f"[bullet]•[/bullet] Line [line_number]{line_number}[/line_number]: "
        f"[message]{message}[/message]"
    )


def format_error(message: str, context: str | None = None) -> str:
    """Format an error message with optional context.

    Args:
        message: The main error message
        context: Optional context information

    Returns:
        str: Formatted error message
    """
    if context:
        return f"Error: {message}\n  {context}"
    return f"Error: {message}"
