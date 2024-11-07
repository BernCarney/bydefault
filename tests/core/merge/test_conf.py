import pytest
from pathlib import Path
from bydefault.core.merge.conf import process_merge

def test_process_merge_invalid_path():
    """Test process_merge raises Exception for invalid TA path."""
    with pytest.raises(Exception, match="TA path not found:"):
        process_merge(Path("nonexistent/ta"))

def test_process_merge_none_path():
    """Test process_merge accepts None path."""
    # Should not raise any exception
    process_merge(None)
