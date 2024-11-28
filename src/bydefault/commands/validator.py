"""Implementation of the validate command for Splunk TA configurations."""

from configparser import ConfigParser
from configparser import Error as ConfigParserError
from enum import Enum
from pathlib import Path

from rich.console import Console

from ..models.validation_results import IssueType, ValidationIssue, ValidationResult
from ..utils.output import print_step_result, print_validation_error


class ValidationType(Enum):
    """Types of validation to perform."""

    NONE = "none"  # Skip validation entirely
    BASIC = "basic"  # Basic checks only (encoding, permissions)
    FULL = "full"  # Full validation (syntax, structure, etc.)


def _is_splunk_special_section(line: str) -> bool:
    """Check if a line contains a valid Splunk special section.

    Args:
        line: The line to check for special section syntax.
            Valid special sections are: [], [*], and [default]

    Returns:
        bool: True if line is a special section, False otherwise
    """
    return line.strip() in {"[]", "[*]", "[default]"}


def _get_unique_section_name(line: str) -> str:
    """Convert Splunk special section names to unique identifiers.

    Args:
        line: The special section line to convert.
            [] -> global_default
            [*] -> wildcard
            [default] -> explicit_default

    Returns:
        str: A unique identifier for the section that's compatible with ConfigParser
    """
    if line == "[]":
        return "global_default"
    elif line == "[*]":
        return "wildcard"
    elif line == "[default]":
        return "explicit_default"
    return line.strip("[]")


def _get_validation_type(file_path: Path) -> ValidationType:
    """Determine validation type based on file extension.

    Args:
        file_path: Path to validate

    Returns:
        ValidationType indicating level of validation to perform
    """
    suffix = file_path.suffix
    stem_suffix = Path(file_path.stem).suffix  # For double extensions like .conf.spec

    # Full validation for .conf and .meta files
    if suffix in [".conf", ".meta"]:
        return ValidationType.FULL

    # Basic validation for .conf.spec, dashboard, and data files
    if stem_suffix == ".conf" and suffix == ".spec":  # .conf.spec files
        return ValidationType.BASIC
    if suffix in [".dashboard", ".lookup", ".csv", ".tsv"]:
        return ValidationType.BASIC

    # No validation for other files
    return ValidationType.NONE


def _validate_file_extension(
    file_path: Path, verbose: bool, console: Console
) -> tuple[ValidationType, list[ValidationIssue]]:
    """Validate file extension.

    Args:
        file_path: Path to validate
        verbose: Whether to show detailed output
        console: Console instance for output

    Returns:
        Tuple of (validation_type, list of issues)
    """
    if verbose:
        console.print("Checking file extension...", end=" ")

    issues = []
    validation_type = _get_validation_type(file_path)

    if validation_type == ValidationType.NONE:
        if verbose:
            print_step_result(console, "warning")
        issues.append(
            ValidationIssue(
                type=IssueType.WARNING,
                line_number=0,
                message="Skipping validation - not a recognized Splunk file type",
                context=str(file_path),
            )
        )
    elif verbose:
        print_step_result(console, True)

    return validation_type, issues


def _validate_encoding(
    file_path: Path, verbose: bool, console: Console
) -> tuple[bool, list[ValidationIssue]]:
    """Validate file encoding is UTF-8.

    Args:
        file_path: Path to validate
        verbose: Whether to show detailed output
        console: Console instance for output

    Returns:
        Tuple of (is_valid, list of issues)
    """
    if verbose:
        console.print("Checking file encoding...", end=" ")

    issues = []
    is_valid = True

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            f.read()
        if verbose:
            print_step_result(console, True)
    except UnicodeDecodeError:
        is_valid = False
        if verbose:
            print_step_result(console, False)
        issues.append(
            ValidationIssue(
                type=IssueType.ENCODING,
                line_number=0,
                message="File is not valid UTF-8",
                context=str(file_path),
            )
        )

    return is_valid, issues


def _read_file_content(
    file_path: Path, verbose: bool, console: Console
) -> tuple[list[str], dict]:
    """Read file content and collect stats.

    Args:
        file_path: Path to read
        verbose: Whether to show detailed output
        console: Console instance for output

    Returns:
        Tuple of (content lines, stats dict)
    """
    if verbose:
        console.print("Reading file...", end=" ")

    stats = {"lines": 0, "stanzas": 0}

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.readlines()
        stats["lines"] = len(content)

    if verbose:
        print_step_result(console, True)

    return content, stats


def _validate_stanzas(
    content: list[str], verbose: bool, console: Console
) -> tuple[dict, list[ValidationIssue]]:
    """Validate stanza syntax and check for duplicates.

    Args:
        content: File content lines
        verbose: Whether to show detailed output
        console: Console instance for output

    Returns:
        Tuple of (seen sections dict, list of issues)
    """
    issues = []
    seen_sections = {}

    for lineno, line in enumerate(content, 1):
        line = line.strip()
        if not line or line.startswith(("#", ";")):
            continue

        if line.startswith("["):
            if not line.endswith("]"):
                issues.append(
                    ValidationIssue(
                        type=IssueType.SYNTAX,
                        line_number=lineno,
                        message="Unclosed stanza bracket",
                        context=line,
                    )
                )
                continue

            section = line[1:-1]
            if section in seen_sections:
                issues.append(
                    ValidationIssue(
                        type=IssueType.DUPLICATE,
                        line_number=lineno,
                        message=f"Duplicate stanza [{section}]",
                        context=line,
                    )
                )
            seen_sections[section] = lineno

    return seen_sections, issues


def validate_file(file_path: Path, verbose: bool, console: Console) -> ValidationResult:
    """Validate a Splunk configuration file.

    Performs validation based on file type:
    - .conf and .meta: Full validation (syntax, structure, etc.)
    - .conf.spec, .dashboard, .lookup, .csv, .tsv: Basic validation (encoding)
    - Other files: No validation (skipped with warning)

    Args:
        file_path: Path to the configuration file to validate
        verbose: Whether to show detailed progress and results
        console: Rich Console instance for formatted output

    Returns:
        ValidationResult containing:
        - Validation status (is_valid)
        - List of any issues found
        - File statistics (line count, stanza count)
        - Original file path
    """
    parser = ConfigParser()
    issues = []
    stats = {"stanzas": 0, "lines": 0}

    if verbose:
        console.print(f"Validating {file_path}...")

    # Check file extension and determine validation type
    validation_type, extension_issues = _validate_file_extension(
        file_path, verbose, console
    )
    if validation_type == ValidationType.NONE:
        result = ValidationResult(
            file_path=file_path,
            is_valid=True,  # Non-Splunk files are considered valid
            issues=extension_issues,
            stats=stats,
        )
        if verbose:
            console.print(f"[path]{file_path}[/path] ", end="")
            print_step_result(console, "warning")
            console.print()
        return result
    issues.extend(extension_issues)

    # Basic validation for all recognized file types
    is_valid, encoding_issues = _validate_encoding(file_path, verbose, console)
    if not is_valid:
        result = ValidationResult(
            file_path=file_path, is_valid=False, issues=encoding_issues, stats=stats
        )
        if verbose:
            console.print(f"[path]{file_path}[/path] ", end="")
            print_step_result(console, False)
            console.print()
        return result
    issues.extend(encoding_issues)

    # Only proceed with full validation for .conf and .meta files
    if validation_type != ValidationType.FULL:
        result = ValidationResult(
            file_path=file_path,
            is_valid=True,
            issues=issues,
            stats=stats,
        )
        if verbose:
            console.print(f"[path]{file_path}[/path] ", end="")
            print_step_result(console, True)
            console.print()
        return result

    # Full validation continues here
    content, file_stats = _read_file_content(file_path, verbose, console)
    stats.update(file_stats)

    seen_sections, stanza_issues = _validate_stanzas(content, verbose, console)
    issues.extend(stanza_issues)

    syntax_valid = True
    if not any(issue.type == IssueType.SYNTAX for issue in issues):
        try:
            processed_content = []
            for line in content:
                line = line.strip()
                if _is_splunk_special_section(line):
                    section_name = _get_unique_section_name(line)
                    processed_content.append(f"[{section_name}]")
                else:
                    processed_content.append(line)

            parser.read_string("\n".join(processed_content))
            stats["stanzas"] = len(parser.sections())
            if verbose:
                console.print(f"Found {stats['stanzas']} stanzas")
        except ConfigParserError as e:
            syntax_valid = False
            if verbose:
                console.print("Checking syntax... ", end="")
                print_step_result(console, False)
            issues.append(
                ValidationIssue(
                    type=IssueType.SYNTAX,
                    line_number=next(
                        (i + 1 for i, line in enumerate(content) if str(e) in line),
                        0,
                    ),
                    message=str(e),
                    context=str(file_path),
                )
            )

    # Create result
    result = ValidationResult(
        file_path=file_path,
        is_valid=len(issues) == 0,
        issues=issues,
        stats=stats,
    )

    # Print final result if verbose
    if verbose and (not result.is_valid or validation_type == ValidationType.FULL):
        if not syntax_valid:
            console.print()  # Add newline before error output
        console.print(f"[path]{file_path}[/path] ", end="")
        print_step_result(console, result.is_valid)
        if not result.is_valid:
            for issue in result.issues:
                print_validation_error(console, issue.line_number, issue.message)
        console.print()  # Add newline after each file's output

    return result
