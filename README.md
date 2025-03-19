# byDefault

[![CI](https://github.com/BernCarney/bydefault/actions/workflows/ci.yml/badge.svg)](https://github.com/BernCarney/bydefault/actions)
[![codecov](https://codecov.io/gh/BernCarney/bydefault/branch/main/graph/badge.svg)](https://codecov.io/gh/BernCarney/bydefault)
![Python](https://img.shields.io/badge/python-≥3.11-blue)

CLI tools for Splunk 9.2.2 TA development and maintenance.

## Features

Currently Implementing:

- **P1: Basic CLI Structure** ✓
  - Command-line interface framework
  - Help text and documentation
  - Output formatting templates
  - Error message formatting
  - Verbosity controls

- **P2: Basic Validation** ✓
  - Core validation rules
  - Validation command structure
  - Validation reporting
  - Error handling

- **P3: File Detection** ✓
  - TA directory validation
  - Change detection and reporting
  - Local/default file comparison
  - Status display system

- **P4: Configuration Sorting** ✓
  - Stanza sorting by type and priority
  - Setting organization within stanzas
  - Structure and comment preservation
  - Format maintenance

- **P5: Configuration Merging** ✓
  - Local to default file merging
  - Conflict detection and resolution
  - Format and structure preservation
  - Backup mechanisms

Coming Soon:

- **P6: Version Management**
  - Bump version numbers
  - Tag releases
  - Create release notes

## Command Documentation

### validate

Validates Splunk configuration files for syntax errors and structural issues.

```bash
bydefault validate [OPTIONS] FILES...
```

Options:

- `--verbose, -v` - Show detailed validation output
- `--recursive, -r` - Recursively scan directories for configuration files

Example:

```bash
bydefault validate default/*.conf
default/props.conf ✓
default/inputs.conf ✓
default/transforms.conf ✗
  Line 15: Invalid stanza format
```

### scan

Scans Splunk TA directories to detect configuration changes between local and default.

```bash
bydefault scan [OPTIONS] PATHS...
```

Options:

- `--baseline, -b` - Baseline TA to compare against
- `--recursive, -r` - Recursively search for TAs in directories
- `--verbose, -v` - Show more detailed output
- `--summary, -s` - Show only a summary of changes
- `--details, -d` - Show detailed changes (default)

Example:

```bash
bydefault scan path/to/ta
TA-example:
  Changes detected: 3 files modified, 1 file added
  Modified: local/props.conf
  Modified: local/transforms.conf
  Modified: local/macros.conf
  Added: local/indexes.conf
```

### sort

Sorts stanzas and settings in Splunk configuration files while preserving structure and comments.

```bash
bydefault sort [OPTIONS] FILES...
```

Options:

- `--verbose, -v` - Show detailed output
- `--dry-run, -n` - Show what would be done without making changes
- `--backup, -b` - Create backup before sorting
- `--verify, -c` - Verify file structure after sort

Example:

```bash
bydefault sort --backup default/props.conf
Sorted default/props.conf (backup created)
```

### merge

Merges changes from Splunk TA's local directory into the default directory while preserving structure and comments.

```bash
bydefault merge [OPTIONS] PATHS...
```

Options:

- `--verbose, -v` - Show detailed output
- `--dry-run, -n` - Show what would be done without making changes
- `--no-backup` - Skip creating backup (backup is created by default)
- `--mode` - How to handle local changes (`merge` or `replace`, default: `merge`)
- `--recursive, -r` - Recursively search for TAs in the specified directories

Example:

```bash
bydefault merge path/to/ta
Created backup: path/to/ta/default.20240317_123456.bak
Merge completed successfully!
```

## References

- **Project Links**
  - [byDefault Repository](https://github.com/BernCarney/bydefault)
  - [CI Status](https://github.com/BernCarney/bydefault/actions)
  - [Code Coverage](https://codecov.io/gh/BernCarney/bydefault)

- **Documentation**
  - [UV Package Manager](https://docs.astral.sh/uv/)
  - [Ruff Linter & Formatter](https://docs.astral.sh/ruff/)
  - [Splunk 9.2.2 Documentation](https://docs.splunk.com/Documentation/Splunk/9.2.2)

## Overview

byDefault provides a suite of command-line tools to assist Splunk developers in creating and maintaining Technology Add-ons (TAs) for Splunk 9.2.2. The tools are designed with security and maintainability in mind.

## Requirements

- UV package manager
- ~/.local/bin in PATH (or appropriate UV tools directory)

Note: Python is not required to be pre-installed. UV will automatically manage Python versions as needed.

## Installation

### Installing UV

UV is a fast, reliable, and feature-rich Python package installer and resolver.

Choose one of the following installation methods:

1. Install UV:

    **macOS (Recommended)**

    ```bash
    brew install uv
    ```

    **Linux/macOS (Alternative)**

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

    **Windows**

    ```powershell
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

2. The installation scripts automatically add UV to your PATH. Verify the installation:

    ```bash
    uv --version
    ```

### Installing byDefault

1. Install from GitHub Release (Recommended):

    ```bash
      # Install from wheel file
      uv tool install https://github.com/BernCarney/bydefault/releases/download/v0.1.0/bydefault-0.1.0-py3-none-any.whl

      # Or latest release
      uv tool install git+https://github.com/BernCarney/bydefault.git@v0.1.0

      # Or latest from main branch
      uv tool install git+https://github.com/BernCarney/bydefault.git

      # Or build from source
      uv tool install https://github.com/BernCarney/bydefault/releases/download/v0.1.0/bydefault-0.1.0.tar.gz
    ```

2. If you receive an error when installing byDefault saying you don't have the required python version, you can install the correct version of python using the following command:

    ```bash
    uv python install 3.11
    ```

3. Make sure UV's tool directory is added to your path:

    ```bash
    uv tool update-shell
    ```

4. Verify installation:

   ```bash
    # After restarting your shell
    bydefault --version
    bydefault, version 0.3.0
   ```

### Usage

Detect configuration changes:

  ```bash
    $ bydefault scan
    Changes detected in: my_custom_ta
      Modified files:
        local/props.conf
        local/transforms.conf
  ```

Sort configuration files:

  ```bash
    $ bydefault sort default/props.conf
    Sorting: default/props.conf
      ✓ Stanzas reordered: 5
      ✓ Settings sorted: 23
  ```

Merge local changes to default:

  ```bash
    $ bydefault merge
    Merging changes in: my_custom_ta
      ✓ props.conf: 2 stanzas merged
      ✓ transforms.conf: 1 stanza merged
  ```

Update TA versions:

  ```bash
    $ bydefault bumpver --minor
    Updating versions:
      my_custom_ta: 1.2.0 -> 1.3.0
  ```

## Development

1. Clone the repository:

    ```bash
    git clone <repository-url>
    cd bydefault
    ```

2. Create and activate a virtual environment:

    ```bash
    uv venv
    source .venv/bin/activate  # On Unix/macOS
    ```

3. Install development dependencies:

    ```bash
    uv sync --all-extras
    ```

4. Run tests:

    ```bash
    pytest
    ```

5. Run linting:

    ```bash
    ruff check .
    ```

6. Run formatting:

    ```bash
    ruff format .
    ```

### Test Environment

The project uses a generated Splunk TA (Technology Add-on) test environment for validation and testing. To set up this environment:

```bash
./scripts/create_test_tas.sh
```

This creates a `test_tas` directory with various test configurations. The directory is excluded from Git tracking via `.git/info/exclude` rather than `.gitignore` to maintain visibility in Cursor IDE.

**Important:** Do not commit the `test_tas` directory to the repository.

## Project Structure

```bash
bydefault/
├── src/
│   └── bydefault/
│       ├── __init__.py
│       ├── cli.py              # Main CLI entry point
│       ├── commands/           # Command implementations
│       ├── core/              # Core business logic
│       ├── models/            # Data models
│       └── utils/             # Shared utilities
├── tests/
│   ├── conftest.py
│   ├── test_commands/
│   ├── test_core/
│   ├── test_models/
│   └── test_utils/
└── [core config files]
```

## Security

- Keep your Python environment up to date
- Review all dependencies before installation
- Use appropriate access controls for any generated files
- Back up configurations before performing merges

## License

GNU General Public License v3.0 or later

## Development Status

Currently implementing Phase 4: Configuration Sorting

Visit the [Project Board](https://github.com/users/BernCarney/projects/1/views/1) for detailed task tracking.
