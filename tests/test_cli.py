"""Tests for CLI functionality."""

from bydefault.cli import main


def test_main_no_args():
    """Test CLI with no arguments."""
    result = main([])
    assert result == 1


def test_main_invalid_command():
    """Test CLI with invalid command."""
    result = main(["invalid"])
    assert result == 1


def test_merge_command(complete_ta_structure, monkeypatch):
    """Test merge command."""
    monkeypatch.chdir(complete_ta_structure)
    result = main(["merge"])
    assert result == 0


def test_version_command_no_version(tmp_path, complete_ta_structure, monkeypatch):
    """Test version command without version argument."""
    # Create a second TA for version testing
    ta2_path = tmp_path / "TA-test2"
    ta2_path.mkdir(parents=True)
    (ta2_path / "default").mkdir(parents=True)
    app_conf = ta2_path / "default" / "app.conf"
    app_conf.write_text(
        """
[launcher]
version = 1.0.0

[package]
id = TA-test2
    """.strip()
    )

    # Move complete_ta_structure to tmp_path
    complete_ta_structure.rename(tmp_path / complete_ta_structure.name)

    monkeypatch.chdir(tmp_path)
    result = main(["version"])
    assert result == 1


def test_version_command(tmp_path, complete_ta_structure, monkeypatch):
    """Test version command."""
    # Create a second TA for version testing
    ta2_path = tmp_path / "TA-test2"
    ta2_path.mkdir(parents=True)
    (ta2_path / "default").mkdir(parents=True)
    app_conf = ta2_path / "default" / "app.conf"
    app_conf.write_text(
        """
[launcher]
version = 1.0.0

[package]
id = TA-test2
    """.strip()
    )

    # Move complete_ta_structure to tmp_path
    complete_ta_structure.rename(tmp_path / complete_ta_structure.name)

    monkeypatch.chdir(tmp_path)
    result = main(["version", "2.0.0"])
    assert result == 0

    # Verify version was updated in both TAs
    for ta_name in ["TA-test", "TA-test2"]:
        app_conf = tmp_path / ta_name / "default" / "app.conf"
        with open(app_conf) as f:
            content = f.read()
            assert "version = 2.0.0" in content


def test_merge_command_no_local_configs(tmp_path, monkeypatch):
    """Test merge command with no local configurations."""
    monkeypatch.chdir(tmp_path)
    result = main(["merge"])
    assert result == 1  # Should fail because no TA structure exists


def test_merge_command_with_no_meta(complete_ta_structure, monkeypatch):
    """Test merge command when local.meta doesn't exist."""
    monkeypatch.chdir(complete_ta_structure)
    (complete_ta_structure / "metadata" / "local.meta").unlink()  # Remove local.meta
    result = main(["merge"])
    assert result == 0  # Missing meta is not a failure
