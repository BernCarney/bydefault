# byDefault

CLI tools for Splunk 9.2.2 TA development and maintenance.

## Features

Currently Implemented:

- **File Detection**
  - Find and validate Splunk TA directories
  - Locate configuration files in local/default directories
  - Match local configurations with default counterparts

Coming Soon:

- **Configuration Management**
  - Merge local configurations into default configurations
  - Support common Splunk configuration files (props.conf, transforms.conf, etc.)
  - Handle metadata merging (local.meta to default.meta)

- **Version Management**
  - Update version numbers across multiple TAs
  - Automatic version detection and validation

## References

- **Project Links**
  - [byDefault Repository](https://github.com/your-org/bydefault)
  - [CI Status](https://github.com/your-org/bydefault/actions/workflows/ci.yml)
  - [Code Coverage](https://codecov.io/gh/your-org/bydefault)

- **Documentation**
  - [UV Package Manager](https://docs.astral.sh/uv/)
  - [Ruff Linter & Formatter](https://docs.astral.sh/ruff/)
  - [Splunk 9.2.2 Documentation](https://docs.splunk.com/Documentation/Splunk/9.2.2)

## Overview

byDefault provides a suite of command-line tools to assist Splunk developers in creating and maintaining Technology Add-ons (TAs) for Splunk 9.2.2. The tools are designed with security and maintainability in mind.

## Requirements

- Python 3.8 or higher
- UV package manager
- ~/.local/bin in PATH (or appropriate UV tools directory)

## Installation

### Installing UV

UV is a fast, reliable, and feature-rich Python package installer and resolver. It serves as a drop-in replacement for pip/pip-tools with significant performance improvements.

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

For additional setup options, including shell completion for `uv` and `uvx` commands and uninstallation instructions, please refer to the [UV Installation Guide](https://docs.astral.sh/uv/getting-started/installation/).

### Installing byDefault

Install byDefault as a system tool:

```bash
uv tool install "git+https://github.com/your-org/bydefault.git"
```

This makes the `bydefault` command available directly in your PATH.

### Upgrading

#### Upgrading UV

```bash
uv self update
```

#### Upgrading byDefault

```bash
uv tool upgrade bydefault
```

UV remembers the installation source, so you don't need to specify the repository URL again when upgrading.

## Usage

```bash
# Merge configurations
bydefault merge

# Update versions
bydefault version 2.0.0
```

## Supported Configuration Files

- props.conf
- transforms.conf
- inputs.conf
- app.conf
- eventtypes.conf
- tags.conf
- fields.conf
- macros.conf
- web.conf

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
    # or
    .venv\Scripts\activate  # On Windows
    ```

3. Install development dependencies:

    ```bash
    uv pip install -e ".[dev]"
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

## Security

This tool is designed to work in environments containing sensitive information. Please follow these security guidelines:

- Keep your Python environment up to date
- Review all dependencies before installation
- Do not store sensitive information in configuration files
- Use appropriate access controls for any generated files
- Back up configurations before performing merges

## License

Proprietary - All rights reserved
