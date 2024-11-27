"""Models for validation results and error reporting."""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Sequence


class IssueType(Enum):
    """Types of validation issues."""

    ENCODING = "encoding"  # File encoding issues
    SYNTAX = "syntax"  # Basic syntax issues
    STRUCTURE = "structure"  # Stanza/section structure issues
    DUPLICATE = "duplicate"  # Duplicate keys/stanzas
    PERMISSION = "permission"  # File permission issues
    WARNING = "warning"  # Non-error validation issues


@dataclass
class ValidationIssue:
    """Single validation issue found during processing.

    Args:
        type: Type of validation issue
        line_number: Line number where issue was found (0 for file-level issues)
        message: Description of the issue
        context: Relevant line content or additional context
    """

    type: IssueType
    line_number: int
    message: str
    context: str


@dataclass
class ValidationResult:
    """Results from validating a configuration file.

    Args:
        file_path: Path to the validated file
        is_valid: Whether the file passed validation
        issues: List of validation issues found
        stats: Optional statistics about the file (stanza count, etc.)
    """

    file_path: Path
    is_valid: bool
    issues: Sequence[ValidationIssue]
    stats: dict[str, int] = None  # Optional stats like stanza count, line count
