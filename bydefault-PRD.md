# byDefault Project PRD

## Overview

byDefault is a Python-based CLI tool for Splunk 9.2.2 Technology Add-on (TA) development and maintenance, focusing on configuration file management and standardization.

## Developer Workflow

The following example demonstrates how byDefault integrates into a typical development workflow:

```bash
# Create and switch to new feature branch
$ git checkout -b feat/new-dashboard

# Start Splunk and make changes in the GUI
$ splunk start
... make changes in Splunk Web UI ...
$ splunk stop

# Check what changes were made
$ bydefault scan
Changes detected in: my_custom_ta
  Modified files:
    local/props.conf
      [new_sourcetype] - New stanza
      [existing_sourcetype] - Modified
    local/transforms.conf
      [lookup_transform] - New stanza
    local/data/lookups/new_lookup.csv - New file

# Merge changes to default directory
$ bydefault merge
Merging changes in: my_custom_ta
  ✓ props.conf: 2 stanzas merged
  ✓ transforms.conf: 1 stanza merged
  ✓ data/lookups/new_lookup.csv copied

# Review sorted configurations
$ bydefault sort default/props.conf
Sorting: default/props.conf
  ✓ Stanzas reordered: 5
  ✓ Settings sorted: 23

# Bump version across all TAs
$ bydefault bumpver --minor
Updating versions:
  my_custom_ta: 1.2.0 -> 1.3.0
  another_ta: 2.1.0 -> 2.2.0

# Commit changes and create PR
$ git add .
$ git commit -m "feat: add new sourcetype and lookup

- Added new sourcetype configuration
- Created lookup transform
- Added lookup table
- Bumped TA versions"
$ git push origin feat/new-dashboard
```

## Requirements

### Core Functionality

1. Phased Implementation Approach:

   **Scope Note**: The project is divided into four distinct phases, each building upon the previous. Upon completion of each phase, the tool should be functional with the core requirements of the phase. Later phases should be modular and extend the functionality of previous phases. The phases are as follows:

   - **P1: Basic CLI Structure**
     - Setup command-line interface framework
     - Define all commands and their options
     - Implement help text and documentation
     - Create output formatting templates
     - Setup error message formatting
     - Implement verbosity controls

   - **P2: File Detection**
     - TA directory validation
     - Change detection and reporting
     - Local/default file comparison
     - Status display system

   - **P3: Configuration Sorting**
     - Stanza sorting by type and priority
     - Setting organization within stanzas
     - Structure and comment preservation
     - Format maintenance

   - **P4: Configuration Merging**
     - Local to default file merging
     - Conflict detection and resolution
     - Format and structure preservation
     - Backup mechanisms

2. Command Structure:

   ```bash

    $ bydefault --help
    Usage: bydefault [OPTIONS] COMMAND [ARGS]...

    CLI tools for Splunk TA development and maintenance.

    Options:
    --verbose    Enable detailed output
    --dry-run    Show what would be done without making changes
    --version    Show version information
    --help       Show this message and exit

    Commands:
    scan      Detect and report configuration changes
        --recursive    Scan subdirectories for TAs
        --show-diff    Show detailed changes
        --include-meta Include metadata file changes

    sort      Sort configuration files maintaining structure
        --backup      Create backup before sorting
        --verify      Verify file structure after sort

    merge     Merge local configurations into default
        --conflict    Specify conflict resolution strategy
        --backup      Create backup before merging

    validate  Verify configuration structure and syntax
        --strict      Enable strict validation rules
        --report      Generate validation report

    bumpver   Update version numbers across TAs
        --major       Increment major version (X.0.0)
        --minor       Increment minor version (0.X.0)
        --patch       Increment patch version (0.0.X)
        --set VERSION Set specific version (X.Y.Z)

   ```

### Technical Requirements

1. Project Structure:

   ```bash
   bydefault/
   ├── src/
   │   └── bydefault/
   │       ├── __init__.py
   │       ├── cli.py              # Main CLI entry point and group definitions
   │       ├── commands/           # Command implementations
   │       │   ├── __init__.py
   │       │   ├── scan.py
   │       │   ├── sort.py
   │       │   ├── merge.py
   │       │   ├── validate.py
   │       │   └── version.py
   │       ├── core/              # Core business logic
   │       │   ├── __init__.py
   │       │   ├── scanner.py     # File detection logic
   │       │   ├── sorter.py      # Sorting implementation
   │       │   ├── merger.py      # Merge logic
   │       │   └── validator.py   # Validation rules
   │       ├── models/            # Data models
   │       │   ├── __init__.py
   │       │   ├── stanza.py
   │       │   └── changes.py
   │       └── utils/             # Shared utilities
   │           ├── __init__.py
   │           ├── config.py      # Configuration handling
   │           ├── files.py       # File operations
   │           └── output.py      # Terminal output formatting
   ├── tests/
   │   ├── conftest.py
   │   ├── test_commands/        # Command-specific tests
   │   ├── test_core/           # Core logic tests
   │   ├── test_models/         # Model tests
   │   └── test_utils/          # Utility tests
   └── [core config files]
   ```

2. Component Responsibilities:

   a. Commands (`commands/`):
      - Handles CLI argument parsing and validation
      - Manages user interaction and feedback
      - Formats and displays output
      - Provides error handling for users
      - Thin wrapper around core functionality

   b. Core Logic (`core/`):
      - Implements business logic in isolation
      - Processes data without user interaction
      - Returns structured data (no printing/output)
      - Can be used programmatically
      - Handles complex operations

   c. Data Models (`models/`):
      - Defines data structures used throughout application
      - Provides type hints and validation
      - Ensures consistent data representation
      - Handles data transformations
      - Documents data relationships

   d. Utilities (`utils/`):
      - Implements shared functionality
      - Provides common operations
      - Handles cross-cutting concerns
      - Maintains consistent interfaces
      - Reusable across components

3. Dependencies:
   - Python >= 3.11

   - Standard Library:
     - configparser >= 5.3.0 (INI file handling)
       - [Documentation](https://docs.python.org/3/library/configparser.html)
       - Native .conf file parsing
       - Preserves file structure
       - Handles multi-line values
       - Standard library integration

   - External Core Libraries:
     - click >= 8.1.0 (CLI framework)
       - [Documentation](https://click.palletsprojects.com/)
       - Provides robust CLI interface
       - Includes file handling utilities
       - Built-in help text generation
       - Type validation and conversion

     - rich >= 13.0.0 (Terminal formatting)
       - [Documentation](https://rich.readthedocs.io/)
       - Clear status output
       - Structured error messages
       - Progress indicators
       - Consistent formatting

   - External Development and Distribution:
     - uv >= 0.1.0 (Package and environment management)
       - [Documentation](https://docs.astral.sh/uv/)
       - Virtual environment management
       - Package installation and management
       - Tool distribution
       - Dependency resolution

     - ruff >= 0.2.0 (Linting and formatting)
       - [Documentation](https://docs.astral.sh/ruff/)
       - Code formatting
       - Import sorting
       - Code linting
       - Style enforcement

   - External Testing Tools:
     - pytest >= 7.0.0 (Testing framework)
       - [Documentation](https://docs.pytest.org/)
       - Test discovery and execution
       - Fixture management
       - Assertion introspection

     - pytest-cov >= 4.1.0 (Coverage reporting)
       - [Documentation](https://pytest-cov.readthedocs.io/)
       - Coverage measurement
       - Report generation
       - Coverage enforcement

     - pytest-mock >= 3.12.0 (Mocking in tests)
       - [Documentation](https://pytest-mock.readthedocs.io/)
       - Function/method mocking
       - Call verification
       - Return value simulation

4. Interface Requirements:
   - CLI Framework (Click):
     - Automatic help text generation
     - Command grouping and nesting
     - Type validation and conversion
     - Error handling and reporting
   - Global Options:
     - --verbose: Enable detailed output
     - --dry-run: Show changes without applying
     - --version: Show version information
   - Output Formatting:
     - Consistent status indicators
     - Color-coded output (when supported)
     - Progress indicators for long operations
     - Clear error messages

5. Performance Targets:
   - Startup time < 100ms
   - Scan operation < 1s for single TA
   - Memory usage < 100MB for typical operations
   - Responsive CLI feedback for all operations

### Implementation Rules

   Example Project Structure:

   ```bash
   main_splunk_application/             # Root project directory
   ├── TA-example-main/                 # Primary TA with full structure
   │   ├── README.md
   │   ├── default/
   │   │   ├── app.conf                 # Required TA configuration
   │   │   ├── props.conf               # Source type definitions
   │   │   ├── transforms.conf          # Data transformations
   │   │   ├── eventtypes.conf          # Event type definitions
   │   │   ├── tags.conf                # Tag configurations
   │   │   └── data/
   │   │       └── lookups/             # Default lookup files
   │   │           ├── example.csv
   │   │           └── mappings.csv
   │   ├── local/                       # Local overwrites
   │   │   ├── props.conf
   │   │   └── transforms.conf
   │   ├── metadata/
   │   │   ├── local.meta               # Local metadata
   │   │   └── default.meta             # Default metadata
   │   ├── bin/
   │   │   └── scripts/                 # TA-specific scripts
   │   │       ├── __init__.py
   │   │       └── example.py
   │   └── static/                      # Static assets
   │       └── appIcon.png
   │
   ├── TA-example-secondary/            # Additional TA (minimal structure)
   │
   └── TA-example-dev/                  # Development TA (minimal structure)
   │
   └── TA-example-other-TA/             # Other TA (minimal structure)
   │
   └── SA-example-with-diff-name/       # Source-type TA with different name
   │
   └── SA-example-with-diff-name-2/     # Source-type TA with different name
   │
   └── DA-example-diff-name/            # Destination-type TA with different name
   ```

1. Phase-Aligned Processing:

   a. P1 - Basic CLI Structure:
      1. Command Framework:
         - Define root command structure
         - Setup global options (--verbose, --dry-run, --version)
         - Implement subcommand scaffolding
         - Create help text templates

      2. Output Formatting:
         - Define status message templates
         - Setup color schemes for different message types
         - Create progress indicator formats
         - Implement verbosity output levels:
           - Default: Summary information only
           - Verbose: Detailed operation information

   b. P2 - File Detection:
      1. TA Structure Validation:
         - Verify app.conf presence and basic structure
         - Validate required directory presence (local/default)
         - Check for metadata directory
         - Report structural issues

      2. Change Detection:
         - Scan for local/ directories and local.meta files
         - Check .gitignore for local directory exceptions
         - Report changes at TA level:
           - Default: Show files and stanzas changed
           - Verbose: Option to display file contents
         - Track detected changes:
           - File presence in local/
           - Stanza presence in local files
           - Basic change summary

   c. P3 - Configuration Sorting:
      1. Stanza Classification and Order:
         - Primary Order (Highest to Lowest Priority):
           - Global settings (no stanza header)
           - Default stanza: Exact match "[default]"
           - Global wildcard stanzas: Match pattern "[*::attribute]"
           - Specific type stanzas: All "[type::*]" and "[type::attribute]" patterns

         - Secondary Order (within specific type groups):
           - Wildcard attribute "[type::*]"
           - Wildcard-prefixed attribute "[type::*-attribute]"
           - Specific attribute "[type::attribute]"

         ```# TODO: Add specific sorting rules for settings within stanzas```

      2. Comment Preservation Rules:
         - Comments directly above stanza: Associated with stanza
         - Comments after stanza header: Prompt for association
         - Comments directly above key=value: Associated with that pair
         - Inline value comments: Move with the value
         - Comments followed by blank line and another stanza: Associated with previous stanza block

         Example Comment Associations:

         ```ini
         # Comment for stanza1
         [stanza1]
         # This comment could be for the stanza or for setting1 - prompt user
         setting1 = value1  # inline comment
         setting2 = value2

         # This comment belongs to stanza1 because it's followed by a blank line
         # and another stanza
         
         [stanza2]
         setting1 = value1
         ```

         ```# TODO: Add more complex comment association examples```

      3. Processing Scope:
         - Support both single file and full TA sorting
         - Apply to configuration and metadata files only
         - Maintain consistent sorting across all TAs
         - Run automatically after merge operations

   d. P4 - Configuration Merging:
      1. Pre-merge Validation:
         - Verify file compatibility
         - Check for conflicts
         - Validate stanza integrity
         - Ensure backup availability

      2. Merge Process:
         - Create versioned backup
         - Apply changes incrementally
         - Validate each modification
         - Maintain audit trail

2. Safety Requirements:

   a. File Operations:
      - Read-only for initial operations
      - Atomic writes for modifications
      - Automatic backup creation
      - Rollback capability

   b. Validation Rules:
      - UTF-8 encoding required
      - Valid stanza format
      - Proper key-value syntax
      - Structural integrity

3. Processing Standards:

   a. Configuration Files:
      - Maintain original formatting
      - Preserve comments
      - Keep stanza grouping
      - Handle special characters

   b. Operation Logging:
      - Track all modifications
      - Record validation results
      - Log error conditions
      - Maintain operation history

4. Error Handling:

   a. Recovery Process:
      - Automatic backup restoration
      - Clear error reporting
      - Detailed failure logs
      - User guidance

   b. Validation Failures:
      - Stop on first error
      - Report specific issue
      - Suggest resolution
      - Maintain original state

### Testing Requirements

1. Test Cases:
   - Command-line interface
   - File operations
   - Configuration processing
   - Error conditions
   - Edge cases

2. Validation:
   - Input validation
   - Output verification
   - Operation correctness
   - Error handling

### Documentation Requirements

1. Code Documentation:
   - Comprehensive docstrings
   - Type hints
   - Implementation notes
   - Performance considerations

2. User Documentation:
   - Installation guide
   - Command reference
   - Usage examples
   - Best practices

### Error Handling Requirements

1. Error Categories:
   - CLIErrors: Command usage issues
   - FileErrors: File operations
   - ConfigErrors: Configuration processing
   - ValidationErrors: Data validation
   - ProcessingErrors: Operation failures

2. Recovery Behavior:
   - Automatic backups
   - Rollback on failure
   - Detailed error messages
   - Operation logging

### Performance Requirements

1. Resource Management:
   - Efficient file handling
   - Memory-conscious processing
   - Scalable operations

2. Operation Limits:
   - Maximum file sizes
   - Directory depth restrictions
   - Processing timeouts
   - Memory constraints

## Future Considerations

- Configuration templates
- Batch processing
- Remote operations
- Integration with Splunk Cloud

## Success Criteria

1. Functional:
   - Reliable file operations
   - Accurate configuration processing
   - Consistent results
   - User-friendly interface

2. Technical:
   - Clean code architecture
   - Comprehensive test coverage
   - Clear documentation
   - Efficient performance

3. Integration:
   - Works with Splunk 9.2.2
   - Supports standard TA structures
   - Handles all valid configurations
   - Provides clear feedback

## Development Phases

### P1: Basic CLI (Initial Release)

**Core Implementation:**

- Command-line interface framework
- File I/O operations (read-only)
- Basic file type detection
- Project structure setup

**Success Criteria:**

1. CLI Framework
   - All commands return proper help text
   - Global flags work as expected (--verbose, --dry-run)
   - Command structure matches specification
   - Error messages are clear and actionable

2. File Operations
   - Can identify Splunk configuration files
   - Can read file contents without parsing
   - Supports recursive directory scanning
   - Handles file access errors gracefully

3. Testing
   - CLI commands have 100% test coverage
   - File operations have error handling tests
   - Help text verification tests
   - Flag behavior tests

### P2: File Detection

**Core Implementation:**

- TA directory validation
- Change detection and reporting
- Local/default file comparison
- Status display system

**Success Criteria:**

1. Change Detection
   - Identifies new files in local directory
   - Detects modified stanzas
   - Reports untracked files
   - Shows metadata changes when requested

2. Status Output
   - Clear, git-style status display
   - Grouped by TA when multiple present
   - Shows file-level changes
   - Shows stanza-level changes

3. Testing
   - Tests for all change scenarios
   - Directory structure validation tests
   - Status output format tests
   - Error condition tests

### P3: Configuration Sorting

**Core Implementation:**

- Stanza sorting by type and priority
- Setting organization within stanzas
- Structure and comment preservation
- Format maintenance

**Success Criteria:**

1. Stanza Sorting
   - Follows defined sort order:
     1. Global settings (no stanza)
     2. [default] stanza
     3. Global wildcards [*::attribute]
     4. Type-specific stanzas
   - Maintains stanza grouping
   - Preserves comments and spacing

2. Setting Organization
   - Consistent key-value pair ordering
   - Preserves multi-line values
   - Maintains inline comments
   - Keeps original formatting

3. Testing
   - Sort order verification tests
   - Format preservation tests
   - Comment handling tests
   - Edge case handling tests

### P4: Configuration Merging

**Core Implementation:**

- Local to default file merging
- Conflict detection and resolution
- Format and structure preservation
- Backup system

**Success Criteria:**

1. Merge Operations
   - Successfully merges local changes to default
   - Handles conflicting changes
   - Preserves file structure
   - Creates reliable backups

2. Conflict Resolution
   - Identifies merge conflicts
   - Provides resolution options
   - Maintains data integrity
   - Logs all merge decisions

3. Testing
   - Merge scenario tests
   - Conflict resolution tests
   - Backup system tests
   - Recovery scenario tests
