# Configuration Structures

This module provides data structures for parsing and manipulating Splunk .conf files.

## Overview

The module uses dataclasses to represent different components of a .conf file:

- `ConfValue`: Individual configuration values
- `ConfStanza`: Configuration stanzas containing key-value pairs
- `ConfLine`: Single line in a .conf file (stanza, value, comment, or blank)
- `ConfFile`: Complete .conf file representation

## Usage Examples

### Basic Configuration File

```python
from pathlib import Path
from bydefault.core.merge.conf_structures import ConfFile, ConfStanza, ConfValue

# Create a new conf file representation
props_conf = ConfFile(Path("props.conf"))

# Add lines with content
props_conf.add_line(1, comment_text="# Configuration for Apache logs")
props_conf.add_line(2, is_blank=True)

# Add a stanza
apache_stanza = ConfStanza("[apache_access]")
props_conf.add_line(3, content=apache_stanza)

# Add settings (automatically appends to end of stanza)
props_conf.add_setting_to_stanza("[apache_access]", "SHOULD_LINEMERGE", "false")
props_conf.add_setting_to_stanza("[apache_access]", "LINE_BREAKER", "([\r\n]+)")

# Add setting to start of stanza when needed
props_conf.add_setting_to_stanza(
    "[apache_access]", 
    "DATETIME_CONFIG", 
    "CURRENT", 
    position="start"
)
```

### Real-world Examples

#### 1. Props.conf with Comments

```python
# Input file:
#   # Apache log settings
#   [apache_access]
#   SHOULD_LINEMERGE = false
#   LINE_BREAKER = ([\r\n]+)
#   # Complex regex for timestamp
#   TIME_PREFIX = \[
#   TIME_FORMAT = %d/%b/%Y:%H:%M:%S %z

conf_file = ConfFile(Path("props.conf"))
conf_file.add_line(1, comment_text="# Apache log settings")
conf_file.add_line(2, is_blank=True)

apache_stanza = ConfStanza("[apache_access]")
conf_file.add_line(3, content=apache_stanza)

# Settings are added to the end by default
conf_file.add_setting_to_stanza("[apache_access]", "SHOULD_LINEMERGE", "false")
conf_file.add_setting_to_stanza("[apache_access]", "LINE_BREAKER", "([\r\n]+)")
conf_file.add_line(6, comment_text="# Complex regex for timestamp")
conf_file.add_setting_to_stanza("[apache_access]", "TIME_PREFIX", "\\[")
conf_file.add_setting_to_stanza("[apache_access]", "TIME_FORMAT", "%d/%b/%Y:%H:%M:%S %z")
```

### Continuation Lines

```python
# Input file:
#   [apache_access]
#   EXTRACT = \
#       user=(?P<user>[^\s]+)\s+ \
#       ip=(?P<ip>\d+\.\d+\.\d+\.\d+)\s+ \
#       status=(?P<status>\d+)

conf_file = ConfFile(Path("transforms.conf"))
conf_file.add_line(1, content=ConfStanza("[apache_access]"))

# Add multi-line value with continuations
result = ConfValueParser.parse(
    "EXTRACT = user=(?P<user>[^\s]+)\\",
    [
        "    ip=(?P<ip>\\d+\\.\\d+\\.\\d+\\.\\d+)\\",
        "    status=(?P<status>\\d+)",
    ]
)
conf_file.add_line(2, content=ConfValue.from_parsed_value(result))
```

Key features of continuation handling:

- Preserves indentation and formatting
- Handles escaped backslashes correctly
- Maintains inline comments
- Supports multiple continuation lines

## Key Features

1. **Line Number Management**
   - Automatic line number calculation
   - Maintains file structure
   - Supports insertion at start or end of stanzas

2. **Comment Preservation**
   - Maintains file comments
   - Preserves blank lines
   - Keeps formatting intact

3. **Validation**
   - Validates stanza names
   - Ensures sequential line numbers
   - Verifies file existence and type

## Common Operations

```python
# Get all stanzas
stanzas = conf_file.stanzas

# Find specific stanza
apache_stanza = conf_file.get_stanza("[apache_access]")

# Check for [default] stanza
if conf_file.default_stanza:
    print("Default stanza exists")

# Add settings (defaults to end of stanza)
apache_stanza.add_setting("TRUNCATE", "0")
```

## Best Practices

1. Use `add_setting_to_stanza()` for adding new settings (handles line numbers automatically)
2. Only specify position when you need a setting at the start of a stanza
3. Use the provided helper methods instead of direct attribute access
4. Validate conf files before processing them

## Notes

- Line numbers start at 1
- Comments and blank lines are preserved
- Stanza names must be enclosed in square brackets
- The [default] stanza is handled specially
- Settings are added to the end of stanzas by default
