# Merge Command Documentation

## Overview

The `merge` command combines changes from Splunk TA's `local` directory into the `default` directory while preserving structure and comments. This is a critical part of the Splunk development workflow, where changes initially made in the `local` directory need to be incorporated into the versioned `default` directory.

## Features

- Intelligent merging of local configurations into default
- Two merge modes: `merge` (default) and `replace`
- Automatic backup creation before applying changes
- Preservation of comments and file structure
- Comprehensive change tracking and reporting
- Dry-run capability for previewing changes
- Integration with ConfigSorter for maintaining sorting order

## Usage

```bash
bydefault merge [OPTIONS] TA_PATH
```

### Arguments

- `TA_PATH`: Path to the Splunk TA directory containing local and default subdirectories

### Options

- `-v, --verbose`: Show detailed output of merge operations
- `-n, --dry-run`: Show what would be done without making changes
- `--no-backup`: Skip creating backup (backup is created by default)
- `--mode [merge|replace]`: How to handle local changes (default: merge)
- `--help`: Show help message and exit

## Examples

### Basic Merging

To merge changes with default behavior (creates backup automatically):

```bash
bydefault merge path/to/ta
```

### Replace Mode

To completely replace default stanzas with local ones:

```bash
bydefault merge --mode=replace path/to/ta
```

### Dry Run with Verbose Output

To preview changes without modifying files:

```bash
bydefault merge --dry-run --verbose path/to/ta
```

### Merge Without Backup

To merge changes without creating a backup:

```bash
bydefault merge --no-backup path/to/ta
```

## How It Works

### Merge Modes

The merge command supports two operation modes:

1. **Merge Mode (default)**:
   - Preserves the structure of default files
   - Updates values from local
   - Keeps default settings not present in local
   - Preserves comments according to setting origin

2. **Replace Mode**:
   - Takes structure from local files
   - Completely replaces default stanzas with local ones
   - Only keeps settings present in local
   - Uses comments from local files

### Processing Logic

The merge command follows these steps:

1. **Validation**: Verifies the TA directory structure
2. **Backup**: Creates a timestamped backup of the default directory (unless disabled)
3. **Analysis**: Identifies configuration files in local directory
4. **Processing**: For each file:
   - Parses both local and default versions
   - Applies the selected merge strategy
   - Tracks changes at stanza and setting levels
5. **Output**: Writes merged configurations to default directory (in non-dry-run mode)
6. **Reporting**: Displays summary or detailed report of changes

### Content Preservation

The command preserves:

- File-level comments
- Stanza comments
- Setting-level comments
- Blank lines between stanzas
- Original file encoding and line endings

## Integration with Other Commands

The merge command builds upon other byDefault commands:

- **scan**: Use first to identify changes between local and default
- **sort**: Merged configurations maintain sorting order through ConfigSorter integration
- **validate**: Can be used after merging to verify configuration validity

Workflow example:

```bash
bydefault scan path/to/ta       # Identify changes
bydefault merge --dry-run path/to/ta  # Preview merge
bydefault merge path/to/ta      # Apply changes
bydefault validate path/to/ta/default/*.conf  # Verify results
```

## Error Handling

The merge command handles several error conditions:

- Invalid TA directory structure
- Missing local or default directories
- Backup creation failures
- File parsing errors
- Writing permission issues

Errors are reported with clear messages and the command exits with non-zero status in case of failure.

## Using in Development Workflows

### For Splunk App Development

During development lifecycle:

```bash
# Make changes in local during development
# When ready to commit:
bydefault scan path/to/ta
bydefault merge path/to/ta
git add path/to/ta/default
git commit -m "feat: merge local changes to default"
```

### For Managing Multiple TAs

When handling multiple TAs with similar changes:

```bash
# For each TA:
bydefault merge --verbose path/to/ta1
bydefault merge --verbose path/to/ta2
```

### For Release Preparation

Before packaging a TA for release:

```bash
bydefault merge path/to/ta
bydefault validate path/to/ta/default/*.conf
# Additional release steps...
```

## Technical Details

The merge command uses several components:

- `merge.py`: Main command implementation
- `merge_models.py`: Data models for merge operations
- `merge_utils.py`: Core merging functionality
- `backup.py`: Backup creation utility
- `ConfigMerger`: Primary class handling the merge process
- `MergeResult`: Data structure tracking operation results

Key classes and models:

- `MergeMode`: Enum for merge strategies (MERGE, REPLACE)
- `FileMergeResult`: Tracks changes at file level
- `StanzaMergeResult`: Tracks changes at stanza level
- `MergeResult`: Overall operation results

## Best Practices

1. Always run `scan` before merging to understand changes
2. Use `--dry-run` to preview changes before applying
3. Keep the default backup enabled for important TAs
4. Verify merged configurations with `validate`
5. When in doubt, use `merge` mode instead of `replace`
6. Consider the implications of each merge mode:
   - `merge`: Safer, preserves more content
   - `replace`: Complete replacement, may remove settings

## Notes

- Stanzas only in default are always preserved
- New stanzas from local are always added
- File-level comments are always preserved
- The command handles multi-line values properly
- Backup files use timestamp format: default.YYYYMMDD_HHMMSS.bak
- Implementation leverages and extends ConfigSorter from the sort command
