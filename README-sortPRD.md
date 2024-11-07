# Sorting Module PRD

## Overview

Core module for sorting Splunk configuration files with a focus on maintainable, predictable sorting behavior.

## Requirements

### Core Functionality

1. Sort configuration files while preserving existing structure:

   **Scope Note**: While both merge and sort modules handle file structure preservation,
   their contexts differ:

   - **Sort Module**: Focuses on maintaining structure during reordering
     - Preserves existing line continuations (using ConfValue)
     - Maintains comment associations during stanza reordering
     - Keeps whitespace patterns between sorted groups
     - Ensures stanza relationships remain intact during sorting

   - **Merge Module**: Focuses on structure during file combination
     - Handles parsing of line continuations
     - Manages comment conflicts between files
     - Resolves whitespace during file merging
     - Creates new continuations when needed

   The sort module leverages the existing ConfFile structures but focuses
   specifically on maintaining these elements during the reordering process.

2. Sorting Order (Priority):

   ```text
   1. Global settings (no stanza header)
   2. [default] stanza
   3. Type-based stanzas [type::*] alphabetically
   4. Attribute stanzas [type::attribute] alphabetically within type
   ```

### Technical Requirements

1. Module Structure:

   ```bash
   core/sort/
   ├── __init__.py      # Public interface
   ├── sorter.py        # Core sorting implementation
   └── rules.py         # Static sorting rules
   ```

2. Interface Requirements:
   - Provide both file-based and in-memory sorting
   - Support sorting single stanzas and entire files
   - Maintain existing ConfFile structure compatibility
   - Clear error handling and validation

### Implementation Rules

1. Stanza Classification and Order:

   a. Primary Order (Highest to Lowest Priority):
      1. Global settings (no stanza header)
      2. Default stanza: Exact match "[default]"
      3. Global wildcard stanzas: Match pattern "[*::attribute]"
      4. Specific type stanzas: All "[type::*]" and "[type::attribute]" patterns

   b. Secondary Order (within specific type groups):
      1. Wildcard attribute "[type::*]"
      2. Wildcard-prefixed attribute "[type::*-attribute]"
      3. Specific attribute "[type::attribute]"

   Example Sort Order:

   ```ini
   # Global settings (no stanza header)
   setting = value

   [default]

   # Global wildcard stanzas
   [*::a-attribute]
   [*::b-attribute]

   # Specific type: a-type
   [a-type::*]
   [a-type::*-attribute]
   [a-type::a-attribute]
   [a-type::b-attribute]

   # Specific type: b-type
   [b-type::*]
   [b-type::*-attribute]
   [b-type::a-attribute]
   [b-type::b-attribute]
   ```

   **Note**: Global wildcard stanzas (`[*::attribute]`) are processed before any
   specific type stanzas to ensure proper configuration precedence.

2. Comment Handling:
   - Preserve comments above stanzas
   - Maintain inline comments
   - Keep relative comment positioning

3. Whitespace Rules:
   - Preserve blank lines between stanzas
   - Maintain indentation in continued values
   - Keep original formatting where possible

### Testing Requirements

1. Test Cases:
   - Empty files
   - Files with only global settings
   - Mixed stanza types
   - Complex continuation values
   - Comment preservation
   - Whitespace handling

2. Validation:
   - Input file integrity
   - Output file correctness
   - Sort order compliance
   - Structure preservation

### Documentation Requirements

1. Code Documentation:
   - Comprehensive docstrings
   - Clear type hints
   - Implementation notes
   - Performance considerations

2. Usage Documentation:
   - Basic usage examples
   - Common patterns
   - Error handling
   - Best practices

### Error Handling Requirements

1. Validation Errors:
   - Invalid stanza format detection
   - Malformed type::attribute patterns
   - Duplicate stanza detection
   - File permission issues

2. Recovery Behavior:
   - Preserve original file on error
   - Provide detailed error context
   - Support dry-run operations
   - Log validation failures

3. Error Categories:
   - FileErrors: Permission, not found, etc.
   - FormatErrors: Invalid syntax, malformed stanzas
   - ValidationErrors: Duplicate stanzas, invalid patterns
   - SortErrors: Issues during sort operations

### Performance Requirements

1. Memory Usage:
   - Efficient handling of large files
   - Minimize in-memory copies
   - Smart buffer management

2. Processing Efficiency:
   - Single-pass stanza classification
   - Optimized sort operations
   - Minimal file I/O

3. Resource Constraints:
   - Maximum file size handling
   - Memory usage limits
   - Processing timeout handling

## Future Considerations

- Configurable sorting rules
- Custom stanza type patterns
- Alternative sorting strategies
- Performance optimizations

## Success Criteria

1. Functional:
   - Correct sorting order
   - Structure preservation
   - No data loss
   - Predictable output

2. Technical:
   - Clean, maintainable code
   - Comprehensive test coverage
   - Clear documentation
   - Efficient performance

3. Integration:
   - Works with existing ConfFile class
   - Supports CLI interface
   - Handles all valid .conf files
   - Provides clear error messages
