# byDefault

[![CI](https://github.com/username/bydefault/actions/workflows/ci.yml/badge.svg)](https://github.com/username/bydefault/actions)
[![codecov](https://codecov.io/gh/username/bydefault/branch/main/graph/badge.svg)](https://codecov.io/gh/username/bydefault)
![Python](https://img.shields.io/badge/python-≥3.11-blue)

CLI tools for Splunk 9.2.2 TA development and maintenance.

## Features

Currently Implementing:

- **P1: Basic CLI Structure**
  - Command-line interface framework
  - Help text and documentation
  - Output formatting templates
  - Error message formatting
  - Verbosity controls

Coming Soon:

- **P2: Basic Validation**
  - Core validation rules
  - Validation command structure
  - Validation reporting
  - Error handling

- **P3: File Detection**
  - TA directory validation
  - Change detection and reporting
  - Local/default file comparison
  - Status display system

- **P4: Configuration Sorting**
  - Stanza sorting by type and priority
  - Setting organization within stanzas
  - Structure and comment preservation
  - Format maintenance

- **P5: Configuration Merging**
  - Local to default file merging
  - Conflict detection and resolution
  - Format and structure preservation
  - Backup mechanisms

## References

- **Project Links**
  - [byDefault Repository](https://github.com/username/bydefault)
  - [CI Status](https://github.com/username/bydefault/actions)
  - [Code Coverage](https://codecov.io/gh/username/bydefault)

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

TODO: Update with actual installation instructions once package is published

## Usage

TODO: Update with actual command examples once implemented

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

Proprietary - All rights reserved

## Development Status

Currently implementing Phase 1: Basic CLI Structure

Visit the [Project Board](https://github.com/username/bydefault/projects/1) for detailed task tracking.
