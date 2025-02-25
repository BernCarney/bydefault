# Scan Command Documentation

## Overview

The `scan` command is designed to detect and report configuration changes in Splunk Technology Add-ons (TAs). It helps Splunk developers identify differences between TA versions or track changes over time.

## Features

- Automatic detection of valid Splunk TA directories
- Recursive searching through directory structures
- Configuration file analysis and comparison
- Change detection at file, stanza, and setting levels
- Summary and detailed reporting options
- Baseline comparison functionality

## Usage

```bash
$ bydefault scan [OPTIONS] PATHS...
```

### Arguments

- `PATHS`: One or more paths to scan (directories or individual TA directories)

### Options

- `-b, --baseline PATH`: Baseline TA to compare against
- `-r, --recursive`: Recursively search for TAs in the specified directories
- `-s, --summary`: Show only a summary of changes
- `-d, --details`: Show detailed changes (default)
- `--help`: Show help message and exit

## Examples

### Scan a Single TA

To scan a single TA directory:

```bash
$ bydefault scan path/to/ta
```

The command will analyze the TA structure and report all configuration settings.

### Compare with Baseline

To compare a TA with a baseline version:

```bash
$ bydefault scan -b baseline_ta path/to/ta
```

This will report all differences between the target TA and the baseline TA.

### Scan Multiple TAs

To scan multiple TAs:

```bash
$ bydefault scan path/to/ta1 path/to/ta2
```

### Recursive Scanning

To recursively search for TAs in a directory:

```bash
$ bydefault scan -r directory_containing_tas
```

### Summary View

To show only a summary of changes:

```bash
$ bydefault scan -s path/to/ta
```

## How It Works

### TA Detection

The scan command first validates the provided paths and identifies valid Splunk TA structures. A valid TA must have:

1. A `default` directory
2. Either an `app.conf` file in the default directory OR at least one `.conf` file

### Change Detection

When scanning a single TA without a baseline, the command reports all configuration files and their settings.

When comparing with a baseline, the command detects:

1. **Added Files**: Configuration files present in the target TA but not in the baseline
2. **Removed Files**: Configuration files present in the baseline but not in the target TA
3. **Modified Files**: Configuration files with different content between the two TAs

For modified files, the command further analyzes:

1. **Added Stanzas**: Stanzas present in the target TA but not in the baseline
2. **Removed Stanzas**: Stanzas present in the baseline but not in the target TA
3. **Modified Stanzas**: Stanzas with changes to settings between the two TAs

Within modified stanzas, the command identifies:

1. **Added Settings**: Settings present in the target TA but not in the baseline
2. **Removed Settings**: Settings present in the baseline but not in the target TA
3. **Modified Settings**: Settings with different values between the two TAs

### Results Display

Results can be displayed in two formats:

1. **Summary Mode**: Shows counts of changes at file, stanza, and setting levels
2. **Details Mode**: Shows specific changes, including added/removed/modified items with their values

## Integration with Other Commands

The scan command can be used in conjunction with other byDefault commands:

- Use before `merge` to identify configuration differences
- Use with `validate` to ensure configurations are valid before comparison

## Error Handling

The scan command handles several error conditions:

- Non-existent paths
- Invalid TA structures
- Binary files
- Malformed configuration files
- Access permission issues

Errors are reported with clear messages and do not terminate the scanning process.

## Using in Development Workflows

### For Initial TA Development

During initial development, scan a TA without a baseline to inventory all configuration settings:

```bash
$ bydefault scan -d path/to/new_ta
```

### For TA Updates

When updating a TA, compare with the previous version to understand changes:

```bash
$ bydefault scan -b path/to/old_version path/to/new_version
```

### For Multiple TA Management

When managing multiple TAs, recursively scan a directory containing all TAs:

```bash
$ bydefault scan -r -s path/to/ta_collection
```

## Technical Details

The scan command uses several components:

- `scanner.py`: For detecting valid TA structures
- `change_detection.py`: For identifying differences between configurations
- Models: For representing different types of changes

These components are designed to be modular and reusable in other parts of the byDefault tool. 