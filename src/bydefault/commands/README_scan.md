# Scan Command Documentation

## Overview

The `scan` command is designed to detect and report configuration changes between the `local` and `default` directories within Splunk Technology Add-ons (TAs). This is an essential part of the Splunk development workflow, where changes are first made in the `local` directory during development and testing, and later need to be merged into the `default` directory for version control.

## Features

- Automatic detection of valid Splunk TA directories
- Recursive searching through directory structures
- Configuration file analysis to identify local changes
- Change detection at file, stanza, and setting levels
- Summary and detailed reporting options
- Baseline comparison functionality for advanced use cases

## Usage

```bash
bydefault scan [OPTIONS] PATHS...
```

### Arguments

- `PATHS`: One or more paths to scan (directories or individual TA directories)

### Options

- `-b, --baseline PATH`: Optional baseline TA to compare against (advanced use case)
- `-r, --recursive`: Recursively search for TAs in the specified directories
- `-s, --summary`: Show only a summary of changes
- `-d, --details`: Show detailed changes (default)
- `--help`: Show help message and exit

## Examples

### Scan a Single TA

To scan a single TA directory for changes between local and default:

```bash
bydefault scan path/to/ta
```

The command will identify configuration changes in the local directory compared to the default directory.

### Scan Multiple TAs

To scan multiple TAs:

```bash
bydefault scan path/to/ta1 path/to/ta2
```

### Recursive Scanning

To recursively search for TAs in a directory:

```bash
bydefault scan -r directory_containing_tas
```

### Summary View

To show only a summary of changes:

```bash
bydefault scan -s path/to/ta
```

## How It Works

### TA Detection

The scan command first validates the provided paths and identifies valid Splunk TA structures. A valid TA must have:

1. A `default` directory
2. Either an `app.conf` file in the default directory OR at least one `.conf` file

### Change Detection

The scan command identifies differences between configuration files in the `local` and `default` directories of each TA:

1. **Added Files**: Configuration files present in `local` but not in `default`
2. **Modified Files**: Configuration files present in both directories but with different content

For files that exist in both locations, the command further analyzes:

1. **Added Stanzas**: Stanzas present in `local` but not in `default`
2. **Modified Stanzas**: Stanzas present in both but with different settings

Within modified stanzas, the command identifies:

1. **Added Settings**: Settings present in `local` but not in `default`
2. **Modified Settings**: Settings with different values between the two directories

### Results Display

Results can be displayed in two formats:

1. **Summary Mode**: Shows counts of changes at file, stanza, and setting levels
2. **Details Mode**: Shows specific changes, including added and modified items with their values

## Integration with Other Commands

The scan command is designed to work with future byDefault commands:

- Use before `merge` to identify local changes that need to be merged into default
- Use with `validate` to ensure configurations are valid before merging

## Error Handling

The scan command handles several error conditions:

- Non-existent paths
- Invalid TA structures
- Binary files
- Malformed configuration files
- Access permission issues

Errors are reported with clear messages and do not terminate the scanning process.

## Using in Development Workflows

### For Splunk TA Development

During development, use the scan command to identify changes made in local:

```bash
bydefault scan -d path/to/ta
```

Review the changes to ensure they're intended before merging them to default.

### For Multiple TA Management

When managing multiple TAs in a development environment:

```bash
bydefault scan -r -s path/to/ta_collection
```

This helps identify which TAs have local changes that might need attention.

### Advanced Use: Compare Against Baseline

For special cases, you can compare against a baseline TA:

```bash
bydefault scan -b baseline_ta path/to/ta
```

This is useful when comparing against a reference implementation rather than just local vs. default.

## Technical Details

The scan command uses several components:

- `scanner.py`: For detecting valid TA structures
- `change_detection.py`: For identifying differences between local and default configurations
- Models: For representing different types of changes

These components are designed to be modular and reusable in other parts of the byDefault tool.
