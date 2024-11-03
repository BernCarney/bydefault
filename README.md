# byDefault

CLI tools for Splunk 9.2.2 TA development and maintenance.

## Overview

byDefault provides a suite of command-line tools to assist Splunk developers in creating and maintaining Technology Add-ons (TAs) for Splunk 9.2.2. The tools are designed with security and maintainability in mind.

## Features

- **Configuration Management**
  - Merge local configurations into default configurations
  - Supports common Splunk configuration files (props.conf, transforms.conf, etc.)
  - Handles metadata merging (local.meta to default.meta)

- **Version Management**
  - Update version numbers across multiple TAs
  - Automatic version detection and validation

## Requirements

- Python 3.8 or higher
- UV package manager

## Installation

1. Clone the repository:

    ```bash
    git clone <repository-url>
    cd bydefault
    ```

2. Create and activate a virtual environment using UV:

    ```bash
    uv venv
    source .venv/bin/activate  # On Unix/macOS
    # or
    .venv\Scripts\activate  # On Windows
    ```

3. Install dependencies:

    ```bash
    uv pip install -r requirements.txt
    ```

## Usage

### Merging Local Configurations

To merge local configurations into default:

```bash
bydefault merge
```

This will:

- Merge all supported configuration files from `local/` into `default/`
- Merge `metadata/local.meta` into `metadata/default.meta`
- Preserve existing default configurations while updating with local changes

### Managing Versions

To update the version across all TAs in the current directory:

```bash
bydefault version <new_version>
```

Example:

```bash
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

## Development

1. Install development dependencies:

    ```bash
    uv pip install -e ".[dev]"
    ```

2. Run tests:

    ```bash
    pytest
    ```

3. Run linting:

    ```bash
    ruff check .
    ```

4. Run formatting:

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
