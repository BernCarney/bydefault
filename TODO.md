# byDefault Development TODO

## Current Focus: Phase 1 - Generic .conf File Handling

### File Detection (In Progress)

- [x] Scan for .conf files in local/
- [x] Match with default/ files
- [x] Create basic file detection utilities
- [x] Add TA directory validation
- [x] Handle root-level and single TA scenarios
- [x] Handle metadata files (local.meta → default.meta)

### File Processing (Next)

- [ ] Parse .conf files into common structure
- [ ] Implement hybrid sorting:
  - [ ] [default] stanza first
  - [ ] Group by stanza type/prefix
  - [ ] Sort alphabetically within groups
- [ ] Validate .conf structure
- [ ] Handle comments and continuation lines

### Merge Logic

- [ ] Merge local stanzas into default
- [ ] Preserve existing default values
- [ ] Handle new/modified stanzas
- [ ] Handle deleted keys

### Validation & Safety

- [ ] Validate merged content
- [ ] Create backups
- [x] Implement logging
- [ ] Report issues/conflicts

## Future Phases

### Phase 2 - Dashboard and Navigation

- [ ] XML file handling in views/
- [ ] XML-specific merge strategies
- [ ] Special case XML handling

### Phase 3 - Advanced Configurations

- [ ] Special case handlers for specific .conf files
- [ ] Complex merge scenarios
- [ ] Conflict resolution

## Completed Items

- [x] Project Restructuring
  - [x] Create modular directory structure (cli/, core/, utils/)
  - [x] Move CLI entry point to cli/__init__.py
  - [x] Separate core logic into merge and version modules
  - [x] Add utility modules for shared functionality
  - [x] Remove old file structure
  - [x] Update imports and references
  - [x] Add Click as CLI framework
  - [x] Set up basic logging
- [x] File Detection Implementation
  - [x] Working directory validation
  - [x] Git repository detection
  - [x] Multiple TA discovery
  - [x] Metadata file handling

## Notes

- Current focus: Moving from File Detection to File Processing phase
- Using pathlib for file operations
- Implementing validation before processing
- Testing each component in isolation
