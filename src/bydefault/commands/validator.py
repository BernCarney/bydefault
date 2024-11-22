"""Implementation of the validate command for Splunk TA configurations."""

from configparser import ConfigParser
from configparser import Error as ConfigParserError
from pathlib import Path

from ..models.validation_results import IssueType, ValidationIssue, ValidationResult


def _is_splunk_special_section(line: str) -> bool:
    """Check if a line is a valid Splunk special section."""
    return line.strip() in {"[]", "[*]", "[default]"}


def _get_unique_section_name(line: str) -> str:
    """Get a unique section name for special sections."""
    if line == "[]":
        return "global_default"
    elif line == "[*]":
        return "wildcard"
    elif line == "[default]":
        return "explicit_default"
    return line.strip("[]")


def validate_file(file_path: Path) -> ValidationResult:
    """Validate a Splunk configuration file."""
    parser = ConfigParser()
    issues = []
    stats = {"stanzas": 0, "lines": 0}
    seen_sections = {}

    # Check file extension
    if file_path.suffix not in [".conf", ".meta"]:
        issues.append(
            ValidationIssue(
                type=IssueType.STRUCTURE,
                line_number=0,
                message="Invalid file extension - must be .conf or .meta",
                context=str(file_path),
            )
        )
        return ValidationResult(
            file_path=file_path, is_valid=False, issues=issues, stats=stats
        )

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.readlines()
            stats["lines"] = len(content)

            # Pre-process to check for unclosed stanzas and duplicates
            for lineno, line in enumerate(content, 1):
                line = line.strip()
                if not line or line.startswith(("#", ";")):
                    continue

                # Check for stanza start
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

            # Only proceed with ConfigParser if no syntax errors found
            if not any(issue.type == IssueType.SYNTAX for issue in issues):
                # Process content for special sections
                processed_content = []
                for line in content:
                    line = line.strip()
                    if _is_splunk_special_section(line):
                        section_name = _get_unique_section_name(line)
                        processed_content.append(f"[{section_name}]")
                    else:
                        processed_content.append(line)

                # Try parsing with processed content
                parser.read_string("\n".join(processed_content))
                stats["stanzas"] = len(parser.sections())

                # Check for duplicate keys
                seen_keys = {}
                for section in parser.sections():
                    for key in parser.options(section):
                        full_key = f"{section}/{key}"
                        if full_key in seen_keys:
                            issues.append(
                                ValidationIssue(
                                    type=IssueType.DUPLICATE,
                                    line_number=next(
                                        (
                                            i + 1
                                            for i, line in enumerate(content)
                                            if key in line
                                        ),
                                        0,
                                    ),
                                    message=f"Duplicate key '{key}' "
                                    f"in stanza [{section}]",
                                    context=full_key,
                                )
                            )
                        seen_keys[full_key] = True

    except UnicodeDecodeError:
        issues.append(
            ValidationIssue(
                type=IssueType.ENCODING,
                line_number=0,
                message="File is not valid UTF-8",
                context=str(file_path),
            )
        )
    except ConfigParserError as e:
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

    return ValidationResult(
        file_path=file_path,
        is_valid=len(issues) == 0,
        issues=issues,
        stats=stats,
    )
