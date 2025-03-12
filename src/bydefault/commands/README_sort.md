# Sort Command Documentation

## Overview

The `sort` command organizes Splunk configuration files according to Splunk's logical priority order while preserving comments and structure. This command is essential for maintaining consistent and readable configuration files across Splunk Technology Add-ons (TAs).

## Features

- Stanza sorting according to Splunk's logical priority order
- Alphabetical sorting of settings within stanzas
- Complete comment preservation with relationship tracking
- Multi-line value handling with backslash continuation
- Support for all Splunk stanza types
- Dry-run and backup options for safe operations

## Usage

```bash
$ bydefault sort [OPTIONS] FILES...
```

### Arguments

- `FILES`: One or more configuration files to sort

### Options

- `-v, --verbose`: Show detailed output during sorting
- `-n, --dry-run`: Show what would be done without making changes
- `-b, --backup`: Create backup before sorting
- `-c, --verify`: Verify file structure after sort
- `--help`: Show help message and exit

## Examples

### Sort a Single File

To sort a single configuration file:

```bash
bydefault sort props.conf
```

### Sort with Backup

To create a backup before sorting:

```bash
bydefault sort --backup props.conf transforms.conf
```

### Dry Run with Verbose Output

To preview changes without modifying files:

```bash
bydefault sort -nv props.conf
```

### Sort and Verify

To verify file structure after sorting:

```bash
bydefault sort -c props.conf
```

## How It Works

### Stanza Classification

The sort command classifies stanzas into types:

1. Global settings (outside any stanza)
2. Empty stanza `[]`
3. Star stanza `[*]`
4. Default stanza `[default]`
5. App-specific stanzas (e.g., `[perfmon]`)
6. Global wildcard stanzas (e.g., `[*::http]`)
7. Type-specific stanzas:
   - Type wildcard (e.g., `[host::*]`)
   - Type wildcard prefix (e.g., `[host::*-webserver]`)
   - Type specific (e.g., `[host::webserver1]`)

### Comment Preservation

Comments are preserved with their relationships:

1. File-level comments at the top
2. Stanza comments before stanza headers
3. Setting comments before settings
4. Inline comments on setting lines
5. Multi-line value comments

### Multi-line Value Handling

The command properly handles multi-line values:

1. Values using backslash continuation
2. Complex SPL queries
3. Nested case statements
4. Regular expressions
5. Values with embedded comments

## Integration with Other Commands

The sort command works with other byDefault commands:

- Use before `validate` to ensure sorted files are valid
- Use after `scan` to organize detected changes
- Future integration with `merge` command

## Error Handling

The sort command handles several error conditions:

- Invalid file paths
- Unsupported file types
- Permission issues
- Encoding problems
- Malformed configuration files

Errors are reported with clear messages and do not terminate batch processing.

## Using in Development Workflows

### For Individual Files

During development, sort configuration files for readability:

```bash
$ bydefault sort -v props.conf
```

### For Multiple Files

When organizing multiple configuration files:

```bash
$ bydefault sort -b *.conf
```

### In CI/CD Pipelines

Integrate sorting into automation:

```bash
# Example GitHub Actions step
- name: Sort Splunk Configs
  run: |
    bydefault sort --verify default/*.conf
```

## Technical Details

The sort command uses several components:

- `sort.py`: Main command implementation
- `sort_models.py`: Data models for sorting operations
- `parser.py`: Comment-aware configuration parser
- `sort_utils.py`: Core sorting functionality
- `writer.py`: Structure-preserving file writer

These components work together to provide reliable and consistent sorting while maintaining file integrity.

## Best Practices

1. Always use `--backup` when sorting important files
2. Use `--dry-run` to preview changes
3. Use `--verify` to ensure file validity after sorting
4. Review sorted files when they contain complex multi-line values
5. Keep a consistent sorting strategy across all TAs
6. Sort configuration files before committing changes

## Notes

- The sort command is non-destructive when used with `--backup`
- Empty configuration files are considered valid
- Comments and blank lines are preserved
- Console output uses rich formatting for improved readability
- Implementation follows modular design principles
- Sort functions accept console instance for consistent output formatting 