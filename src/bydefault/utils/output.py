"""Terminal output formatting utilities."""

from rich.console import Console
from rich.theme import Theme

# Define custom theme for consistent styling
THEME = Theme(
    {
        "info": "cyan",
        "warning": "yellow",
        "error": "red bold",
        "success": "green",
    }
)


def create_console() -> Console:
    """Create a configured console instance.

    Returns:
        Console: Configured Rich console instance
    """
    return Console(theme=THEME)


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
