"""Tests for validation result models."""

from pathlib import Path

from bydefault.models.validation_results import (
    IssueType,
    ValidationIssue,
    ValidationResult,
)


def test_validation_issue_creation():
    """Test ValidationIssue creation and attributes."""
    issue = ValidationIssue(
        type=IssueType.SYNTAX,
        line_number=42,
        message="Test error",
        context="[test]",
    )

    assert issue.type == IssueType.SYNTAX
    assert issue.line_number == 42
    assert issue.message == "Test error"
    assert issue.context == "[test]"


def test_validation_result_creation():
    """Test ValidationResult creation and attributes."""
    issues = [
        ValidationIssue(
            type=IssueType.SYNTAX,
            line_number=1,
            message="Error 1",
            context="test",
        ),
        ValidationIssue(
            type=IssueType.DUPLICATE,
            line_number=2,
            message="Error 2",
            context="test",
        ),
    ]
    stats = {"lines": 10, "stanzas": 2}

    result = ValidationResult(
        file_path=Path("test.conf"),
        is_valid=False,
        issues=issues,
        stats=stats,
    )

    assert not result.is_valid
    assert len(result.issues) == 2
    assert result.stats["lines"] == 10
    assert result.stats["stanzas"] == 2
    assert isinstance(result.file_path, Path)


def test_validation_result_empty_stats():
    """Test ValidationResult with no stats provided."""
    result = ValidationResult(
        file_path=Path("test.conf"),
        is_valid=True,
        issues=[],
    )

    assert result.is_valid
    assert not result.issues
    assert result.stats is None


def test_issue_type_values():
    """Test IssueType enum values."""
    assert IssueType.ENCODING.value == "encoding"
    assert IssueType.SYNTAX.value == "syntax"
    assert IssueType.STRUCTURE.value == "structure"
    assert IssueType.DUPLICATE.value == "duplicate"
    assert IssueType.PERMISSION.value == "permission"
