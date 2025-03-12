# Sort Command Examples

This document showcases the various sorting capabilities of the `sort` command in the byDefault CLI tool. All examples use actual configuration files from our test environment with real command outputs.

## Table of Contents

- [Basic Usage](#basic-usage)
- [Command Options](#command-options)
- [Sorting Examples](#sorting-examples)
  - [Stanza Ordering](#stanza-ordering)
  - [Settings Sorting](#settings-sorting)
  - [Comment Preservation](#comment-preservation)
  - [Special Stanza Types](#special-stanza-types)
  - [Multi-line Value Handling](#multi-line-value-handling)
- [Error Handling](#error-handling)
- [Best Practices](#best-practices)

## Basic Usage

The sort command organizes stanzas and settings within Splunk configuration files while preserving comments and structure.

```bash
bydefault sort [OPTIONS] FILES...
```

## Command Options

| Option | Short | Description |
|--------|-------|-------------|
| `--verbose` | `-v` | Show detailed output |
| `--dry-run` | `-n` | Show what would be done without making changes |
| `--backup` | `-b` | Create backup before sorting |
| `--verify` | `-c` | Verify file structure after sort |

Options can be used individually or chained together (e.g., `-vb` for verbose output with backup).

## Sorting Examples

### Stanza Ordering

The sort command arranges stanzas in a specific order:

1. Global settings (settings outside of any stanza at the top of the file)
2. Empty stanza `[]` (if present)
3. Star stanza `[*]` (if present)
4. `[default]` stanza
5. App-specific stanzas (like `[perfmon]`, `[sourcetype]`) sorted alphabetically
6. The remaining stanzas are grouped by type and sorted alphabetically within each group:
   - `[host::]` stanzas
   - `[source::]` stanzas
   - `[sourcetype::]` stanzas
   - Other type-specific stanzas

If multiple global stanza types are detected (global settings, `[]`, `[*]`, `[default]`), a warning will be displayed as this may cause unexpected behavior in Splunk.

#### Example - Before Sorting

Here's an example configuration file with stanzas in a random order:

```ini
# This is a complex config file with multiple types of stanzas and comments

# Global settings comment
[default]
zSetting = first alphabetically but should be at bottom
aSetting = should be first alphabetically
# Comment inside default stanza
cSetting = third alphabetically

# Section divider for source types
# With multiple lines
[source::wildcard*]
TRANSFORMS-zzz = last_setting
# Inline comment for first setting
TRANSFORMS-aaa = first_setting
TRANSFORMS-mmm = middle_setting

# Another comment
[sourcetype::specific]
FIELDALIAS-first = should_be_first
param2 = value2
param1 = value1
EVAL-computed = case(field="value", 1, 1=1, 0)
# Comment for a specific setting
REPORT-last = should_be_last

[host::example]
ip = 192.168.1.1
alias = test-server
role = application
```

#### Example - Sorting Command

```bash
$ bydefault sort -v example_sort.conf
Processing global settings...
  ✓ 0 settings reordered
Positioning  stanza...
  ✓ Stanza moved to position 0
Sorting wildcard stanzas...
Sorting specific stanzas...
  ✓ host group sorted
  ✓ source group sorted
  ✓ sourcetype group sorted
Preserving comments...
  ✓ 8 comment blocks maintained
Stanzas reordered: 3
Settings sorted: 14
Comments preserved: 8
Success: Sorted: example_sort.conf
```

#### Example - After Sorting

```ini
# This is a complex config file with multiple types of stanzas and comments
# Global settings comment
[default]
aSetting = should be first alphabetically
# Comment inside default stanza
cSetting = third alphabetically
zSetting = first alphabetically but should be at bottom


[host::example]
alias = test-server
ip = 192.168.1.1
role = application

# Section divider for source types
# With multiple lines
[source::wildcard*]
# Inline comment for first setting
TRANSFORMS-aaa = first_setting
TRANSFORMS-mmm = middle_setting
TRANSFORMS-zzz = last_setting


# Another comment
[sourcetype::specific]
EVAL-computed = case(field="value", 1, 1=1, 0)
FIELDALIAS-first = should_be_first
# Comment for a specific setting
REPORT-last = should_be_last
param1 = value1
param2 = value2
```

Notice how:

- The `[default]` stanza moved to the top
- Stanzas are grouped by type and sorted alphabetically
- Comments remain associated with their respective sections

### Settings Sorting

Within each stanza, settings are sorted alphabetically, with special handling for certain prefixes like `TRANSFORMS-`, `EVAL-`, `FIELDALIAS-`, etc.

#### Example - Windows TA Props.conf Before Sorting

```ini
[source::WinEventLog:Security]
TRANSFORMS-commentary = commentary
TRANSFORMS-nullqueue = setnull

[source::WinEventLog:Application]
TRANSFORMS-set_source = source_adjustment
TRANSFORMS-extract_ids = extract_event_ids

[perfmon]
TRANSFORMS-clean = clean_perfmon_data
KV_MODE = none
REPORT-fields = extract_perfmon_fields
FIELDALIAS-app = object AS application
LOOKUP-severity = severity_lookup severity OUTPUT urgency
```

#### Example - Sorting Command

```bash
$ bydefault sort -v Splunk_TA_windows/local/props.conf
Created backup: Splunk_TA_windows/local/props.conf.bak
Processing global settings...
  ✓ 0 settings reordered
Positioning  stanza...
  ✓ No  stanza found
Sorting wildcard stanzas...
Sorting specific stanzas...
  ✓ source group sorted
Preserving comments...
  ✓ 0 comment blocks maintained
Stanzas reordered: 2
Settings sorted: 9
Comments preserved: 0
Success: Sorted: Splunk_TA_windows/local/props.conf
```

#### Example - After Sorting

```ini
[perfmon]
FIELDALIAS-app = object AS application
KV_MODE = none
LOOKUP-severity = severity_lookup severity OUTPUT urgency
REPORT-fields = extract_perfmon_fields
TRANSFORMS-clean = clean_perfmon_data

[source::WinEventLog:Application]
TRANSFORMS-extract_ids = extract_event_ids
TRANSFORMS-set_source = source_adjustment

[source::WinEventLog:Security]
TRANSFORMS-commentary = commentary
TRANSFORMS-nullqueue = setnull
```

Notice how:

- The `[perfmon]` stanza (app-specific) moves to the top
- Source stanzas are grouped together and sorted alphabetically
- Settings within each stanza are sorted alphabetically

### Comment Preservation

The sort command carefully preserves comments throughout the sorting process, maintaining their association with the appropriate stanzas and settings.

#### Example - Before Sorting

```ini
# Top level file comment
# Second line of comment

# Comment for first stanza
[source::example]
# Comment for setting1
setting1 = value1
setting2 = value2 # Inline comment
# Comment for setting3
setting3 = value3

# Comment for second stanza
[host::server]
# Comment for host setting
host_setting = value
```

#### Example - After Sorting

```ini
# Top level file comment
# Second line of comment

# Comment for second stanza
[host::server]
# Comment for host setting
host_setting = value

# Comment for first stanza
[source::example]
# Comment for setting1
setting1 = value1
# Comment for setting3
setting3 = value3
setting2 = value2 # Inline comment
```

Notice how:

- Top-level file comments remain at the top
- Comments for stanzas stay with their stanzas even when reordered
- Comments for settings remain with their settings
- Inline comments (on the same line as a setting) are preserved
- The overall comment structure is maintained despite reordering

### Special Stanza Types

The sort command handles various special stanza types, including global stanzas and wildcard stanzas.

#### Global Stanza Types

Splunk configuration files can have multiple forms of global settings:

- Settings outside any stanza (at the top of the file)
- Empty stanza `[]`
- Star stanza `[*]`
- Default stanza `[default]`

While all of these are valid in Splunk, using multiple types in the same file may cause unexpected behavior. The sort command will preserve all types but issue a warning:

```ini
# Global settings outside stanzas
global_setting1 = value1
global_setting2 = value2

# Empty stanza
[]
empty_setting1 = value1
empty_setting2 = value2

# Star stanza
[*]
star_setting1 = value1
star_setting2 = value2

# Default stanza
[default]
default_setting1 = value1
default_setting2 = value2
```

#### Wildcard Stanza Types

The sort command supports various wildcard stanza patterns that Splunk uses:

1. **Global Wildcard Stanzas** (`[*::attribute]`):
   These stanzas apply to all types with a specific attribute.

   ```ini
   [*::http]
   SHOULD_LINEMERGE = false
   category = web
   ```

2. **Type Wildcard Stanzas** (`[type::*]`):
   These stanzas apply to all attributes of a specific type.

   ```ini
   [host::*]
   SHOULD_LINEMERGE = false
   TRUNCATE = 10000
   ```

3. **Type Wildcard Prefix Stanzas** (`[type::*-attribute]` or `[type::*suffix]`):
   These stanzas apply to all attributes of a specific type with a specific prefix or suffix.

   ```ini
   [source::*-access_log]
   sourcetype = access_combined
   SHOULD_LINEMERGE = false
   ```

   ```ini
   [host::*abc123]
   role = application
   priority = high
   ```

   ```ini
   [source::*.log]
   SHOULD_LINEMERGE = false
   category = logs
   ```

4. **Type Specific Stanzas** (`[type::attribute]`):
   These stanzas apply to a specific attribute of a specific type.

   ```ini
   [source::apache_access]
   sourcetype = access_combined
   SHOULD_LINEMERGE = false
   MAX_TIMESTAMP_LOOKAHEAD = 40
   ```

#### Sorting Order Example

When all these stanza types are present in a file, the sort command organizes them in this order:

```ini
# Global settings outside stanzas
global_setting1 = value1

# Empty stanza
[]
empty_setting1 = value1

# Star stanza
[*]
star_setting1 = value1

# Default stanza
[default]
default_setting1 = value1

# App-specific stanzas
[perfmon]
interval = 60

# Global wildcard stanzas
[*::http]
SHOULD_LINEMERGE = false

# Type wildcard stanzas
[host::*]
TRUNCATE = 10000

# Type wildcard prefix stanzas
[host::*-webserver]
category = web

# Type specific stanzas
[host::webserver1]
ip = 192.168.1.1
```

### Multi-line Value Handling

Splunk configuration files often include multi-line values that use backslashes (`\`) at the end of each line to indicate continuation. The sort command properly preserves these multi-line values during sorting.

#### Example - Before Sorting

```ini
# Simple test file for multi-line values

[source::test]
# Multi-line SPL query
search = index=main \
sourcetype=test \
| stats count by field

# Multi-line eval
EVAL-test = case( \
    field1="value1", "result1", \
    field2="value2", "result2", \
    1=1, "default" \
)

[perfmon]
# Simple settings
interval = 60
disabled = 0

# Multi-line transforms
TRANSFORMS-test = s/pattern/replacement/g \
| s/another/pattern/g
```

#### Example - Sorting Command

```bash
$ bydefault sort -v simple_multiline.conf
Stanza Types:
  source::test: StanzaType.TYPE_SPECIFIC
  perfmon: StanzaType.APP_SPECIFIC
Processing global settings...
  ✓ 0 settings reordered
Positioning  stanza...
  ✓ No  stanza found
Sorting wildcard stanzas...
Sorting specific stanzas...
  ✓ source group sorted
Preserving comments...
  ✓ 5 comment blocks maintained
Stanzas reordered: 2
Settings sorted: 5
Comments preserved: 5
Success: Sorted: simple_multiline.conf
```

#### Example - After Sorting

```ini
[perfmon]
# Multi-line transforms
TRANSFORMS-test = s/pattern/replacement/g \
| s/another/pattern/g
disabled = 0
# Simple settings
interval = 60

[source::test]
# Multi-line eval
EVAL-test = case( \
    field1="value1", "result1", \
    field2="value2", "result2", \
    1=1, "default" \
)
# Multi-line SPL query
search = index=main \
sourcetype=test \
| stats count by field
```

Notice how:

- The multi-line values are preserved with their backslashes intact
- All lines of the multi-line value remain grouped together
- The indentation and formatting of the multi-line values is maintained
- The standard sorting rules still apply (app-specific stanzas first, then alphabetical grouping)

#### Example - Complex Multi-line Values with Embedded Comments

Splunk configurations can include complex multi-line values with embedded comments. The sort command properly handles these too:

```ini
[sourcetype::log]
# Multi-line transform with embedded comments
TRANSFORMS-extract = index=main sourcetype=log \
# This comment explains the source pattern \
source="/var/log/*" \
# This comment explains the regex being used \
| rex field=_raw "(?<field>\w+)=(?<value>[^,]+)"

# Complex nested case statement
EVAL-severity = case( \
    match(source, ".*error.*"), \
        # First level match for errors \
        case( \
            # Nested conditions for error severity \
            match(message, ".*critical.*"), "P1", \
            match(message, ".*warning.*"), "P2", \
            # Default for all other errors \
            1==1, "P3" \
        ), \
    # Default for non-errors \
    1==1, "info" \
)
```

Multi-line values can be complex and include various patterns:

1. **Simple continuation** - Basic multi-line values with backslashes
2. **SPL queries** - Search queries that span multiple lines
3. **Case statements** - Complex conditional expressions with multiple clauses
4. **Regular expressions** - Multi-line pattern matching expressions
5. **Embedded comments** - Comments within multi-line values, prefixed with `#` and ended with backslashes

The sort command properly handles all these variations while maintaining readability and preserving the semantic meaning of the configuration.

## Error Handling

The sort command handles errors gracefully. If a file cannot be read or sorted, it will display an error message and exit.

## Best Practices

- Always back up your configuration files before sorting.
- Use the `--verify` option to ensure that the file structure is preserved after sorting.
- Use the `--dry-run` option to see what would be done without making changes.
- For complex files with multi-line values, inspect the output carefully to ensure all parts of the multi-line values are preserved correctly.
- When manually editing multi-line values, ensure each continuing line ends with a backslash (`\`).
- For multi-line values with embedded comments, ensure comments also end with backslashes to be properly recognized as part of the multi-line value.

### Complete Example with All Stanza Types

Here's a comprehensive example showing how the sort command processes a configuration file with all stanza types:

```ini
# Example configuration with all stanza types
setting1 = value1

[source::specific]
SHOULD_LINEMERGE = false

[default]
default_setting = value

[*]
star_setting = value

[host::*]
host_wildcard_setting = value

[*::http]
global_wildcard_setting = value

[host::*-webserver]
prefix_setting = value

[]
empty_setting = value

[perfmon]
interval = 60

[host::webserver1]
ip = 192.168.1.1
```

When sorting this file using the verbose option:

```bash
$ bydefault sort -v all_stanza_types.conf
Processing global settings...
  ✓ 1 settings reordered
Positioning [] stanza...
  ✓ Stanza moved to position 0
Positioning [*] stanza...
  ✓ Stanza moved to position 1
Positioning [default] stanza...
  ✓ Stanza moved to position 2
Sorting app-specific stanzas...
  ✓ App-specific stanzas sorted alphabetically
Sorting global wildcard stanzas...
  ✓ [*::http] moved to position 4
Sorting specific stanzas...
  ✓ host group sorted
  ✓ source group sorted
Preserving comments...
  ✓ 1 comment blocks maintained

Warnings:
Warning:   ! Multiple global stanza types detected: *, [], [*], [default]. This may cause unexpected behavior in Splunk.
Stanzas reordered: 9
Settings sorted: 10
Comments preserved: 1
Success: Sorted: all_stanza_types.conf
```

The resulting sorted file:

```ini
# Example configuration with all stanza types
setting1 = value1

[]
empty_setting = value

[*]
star_setting = value

[default]
default_setting = value

[perfmon]
interval = 60

[*::http]
global_wildcard_setting = value

[host::*]
host_wildcard_setting = value

[host::*-webserver]
prefix_setting = value

[host::webserver1]
ip = 192.168.1.1

[source::specific]
SHOULD_LINEMERGE = false
```

This example demonstrates the complete sorting order:

1. Global settings
2. Empty stanza `[]`
3. Star stanza `[*]`
4. Default stanza `[default]`
5. App-specific stanzas (alphabetically)
6. Global wildcard stanzas
7. Type-specific groups, each containing:
   - Type wildcard stanzas
   - Type wildcard prefix stanzas
   - Type specific stanzas

### Basic Command Output Example

For a simpler file, the command output might look like this:

```bash
$ bydefault sort -v example_sort.conf
Processing global settings...
  ✓ 0 settings reordered
Positioning  stanza...
  ✓ Stanza moved to position 0
Sorting wildcard stanzas...
Sorting specific stanzas...
  ✓ host group sorted
  ✓ source group sorted
  ✓ sourcetype group sorted
Preserving comments...
  ✓ 8 comment blocks maintained
Stanzas reordered: 3
Settings sorted: 14
Comments preserved: 8
Success: Sorted: example_sort.conf
```
