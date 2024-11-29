# Validate Command

The validate command checks Splunk configuration files for structural and syntax validity.

## Command Usage

### Basic Validation

Validate a single configuration file:

```bash
$ bydefault validate path/to/props.conf
path/to/props.conf ✓
```

Validate multiple files:

```bash
$ bydefault validate props.conf transforms.conf
props.conf ✓
transforms.conf ✗
  • Line 12: Invalid stanza format
```

Use wildcards to validate all configs:

```bash
$ bydefault validate default/*.conf
default/props.conf ✓
default/transforms.conf ✓
default/inputs.conf ✗
  • Line 23: Duplicate key 'index' in stanza [monitor://var/log]
```

### Options

#### Verbose Output (--verbose)

Shows detailed validation progress with status indicators:

```bash
$ bydefault validate --verbose props.conf
Validating props.conf...
Checking file extension... ✓
Checking file encoding... ✓
Reading file... ✓
Found 12 stanzas
props.conf ✓

Validating transforms.conf...
Checking file extension... ✓
Checking file encoding... ✓
Reading file... ✓
Checking syntax... ✗
• Line 45: Invalid stanza format
```

## Programmatic Usage

The validate command can be used programmatically by other commands:

```python
from pathlib import Path
from bydefault.commands.validator import validate_file

# Basic validation
result = validate_file(Path("props.conf"))
if result.is_valid:
    print("Configuration is valid")
else:
    for issue in result.issues:
        print(f"Error on line {issue.line_number}: {issue.message}")

# Get validation statistics
stats = result.stats
print(f"Found {stats['stanzas']} stanzas in {stats['lines']} lines")
```

## Common Use Cases

1. Pre-commit Validation

   ```bash
   # Validate all modified conf files before commit
   $ git diff --cached --name-only | grep '\.conf$' | xargs bydefault validate
   ```

2. Bulk TA Validation

   ```bash
   # Validate all configs in a TA
   $ bydefault validate TA_example/default/*.conf TA_example/local/*.conf
   ```

3. CI/CD Pipeline

   ```bash
   # Example GitHub Actions step
   - name: Validate Splunk Configs
     run: |
       bydefault validate --report etc/apps/*/default/*.conf > validation-report.txt
   ```

## Validation Rules

The validator checks for:

1. File-level validation:
   - Valid file extension (.conf or .meta)
   - UTF-8 encoding
   - Basic file access

2. Syntax validation:
   - Valid stanza format `[stanza_name]`
   - Valid key-value pairs `key = value`
   - Special Splunk sections (`[]`, `[*]`, `[default]`)

3. Structure validation:
   - No duplicate stanzas
   - No duplicate keys within stanzas
   - Valid section hierarchy
   - Line count tracking
   - Stanza count statistics

## Output Styling

The validator uses the following status indicators:

- ✓ (green checkmark): Successful validation
- ✗ (red X): Validation failure
- ⚠ (yellow warning): Warning or caution
- • (yellow bullet): Error or warning details

All status indicators are color-coded using the One Dark theme:

- Success messages in green
- Error messages in red
- Warnings in yellow
- File paths and general information in default terminal color

## Error Messages

Common error messages and their meaning:

| Message | Description | Example Fix |
|---------|-------------|-------------|
| Invalid file extension | File must end in .conf or .meta | Rename file to .conf |
| File is not valid UTF-8 | File encoding issue | Resave file as UTF-8 |
| Duplicate stanza | Same stanza appears multiple times | Remove duplicate stanza |
| Invalid line format | Line doesn't follow key = value format | Fix syntax to use = |
| No section headers | File missing stanza definitions | Add `[stanza_name]` |

## Notes

- The validator is non-destructive and never modifies files
- Empty configuration files are considered valid
- Comments and blank lines are ignored
- Console output uses rich formatting for improved readability
- Implementation follows modular design with separate validation steps
- Validation functions accept console instance for consistent output formatting
