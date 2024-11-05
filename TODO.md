# byDefault Development TODO

## Current Focus: Phase 1 - Generic .conf File Handling

### File Detection (Complete)

- [x] Scan for .conf files in local/ (2024-11-04)
- [x] Match with default/ files (2024-11-04)
- [x] Create basic file detection utilities (2024-11-04)
- [x] Add TA directory validation (2024-11-04)
- [x] Handle root-level and single TA scenarios (2024-11-04)
- [x] Handle metadata files (local.meta → default.meta) (2024-11-04)
- [x] Working directory validation (2024-11-04)
- [x] Git repository detection (2024-11-04)
- [x] Multiple TA discovery (2024-11-04)
- [x] Metadata file handling (2024-11-04)

### File Processing (In Progress)

- [x] Parse .conf files into common structure (2024-11-04)
  - [x] Implement dataclass-based file representation (2024-11-04)
  - [x] Handle line numbers and positioning (2024-11-04)
  - [x] Support comments and blank lines (2024-11-04)
  - [x] Handle continuation lines and escaping (2024-11-04)
- [ ] Implement hybrid sorting:
  - [ ] Create core/sort module structure
  - [ ] Implement stanza classification system
    - [ ] Global settings detection
    - [ ] Default stanza handling
    - [ ] Wildcard pattern matching
    - [ ] Type-based grouping
  - [ ] Develop sorting logic
    - [ ] Primary ordering implementation
    - [ ] Secondary ordering within types
    - [ ] Comment and whitespace preservation
  - [ ] Add error handling
    - [ ] Input validation
    - [ ] Recovery mechanisms
    - [ ] Logging integration
  - [ ] Performance optimization
    - [ ] Memory usage management
    - [ ] Processing efficiency
    - [ ] Resource constraints
  - [ ] Testing implementation
    - [ ] Unit test suite
    - [ ] Integration tests
    - [ ] Performance tests
  - [ ] Documentation
    - [ ] API documentation
    - [ ] Usage examples
    - [ ] Implementation notes

### Merge Logic (Next)

- [ ] Merge local stanzas into default
- [ ] Preserve existing default values
- [ ] Handle new/modified stanzas
- [ ] Handle deleted keys

### Validation & Safety (In Progress)

- [ ] Validate merged content
- [ ] Create backups
- [x] Implement logging (2024-11-04)
- [ ] Report issues/conflicts

### Project Structure (Complete)

- [x] Create modular directory structure (cli/, core/, utils/) (2024-11-04)
- [x] Move CLI entry point to cli/__init__.py (2024-11-04)
- [x] Separate core logic into merge and version modules (2024-11-04)
- [x] Add utility modules for shared functionality (2024-11-04)
- [x] Remove old file structure (2024-11-04)
- [x] Update imports and references (2024-11-04)
- [x] Add Click as CLI framework (2024-11-04)
- [x] Set up basic logging (2024-11-04)

## Future Phases

### Phase 2 - Dashboard and Navigation (Next)

- [ ] XML file handling in views/
- [ ] XML-specific merge strategies
- [ ] Special case XML handling

### Phase 3 - Advanced Configurations

- [ ] Special case handlers for specific .conf files
- [ ] Complex merge scenarios
- [ ] Conflict resolution

### Phase 4 - Documentation Migration

- [ ] Evaluate documentation hosting options
  - [ ] Research enterprise GitHub Pages availability
  - [ ] Consider MkDocs vs Sphinx tradeoffs
  - [ ] Plan migration of existing documentation
- [ ] Documentation Infrastructure
  - [ ] Set up automated doc builds
  - [ ] Migrate inline documentation
  - [ ] Add CLI command reference
  - [ ] Create troubleshooting guide

## Notes

- Current focus: Moving from File Detection to File Processing phase
- Using pathlib for file operations
- Implementing validation before processing
- Testing each component in isolation
