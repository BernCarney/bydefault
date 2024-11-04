# byDefault Development TODO

## Current Focus: Phase 1 - Generic .conf File Handling

### Phase 1 Tasks

- [ ] File Detection
  - [ ] Scan for .conf files in local/
  - [ ] Match with default/ files
  - [ ] Create new default files if needed
  - [ ] Handle root-level and single TA scenarios

- [ ] File Processing
  - [ ] Parse .conf files into common structure
  - [ ] Implement hybrid sorting:
    - [ ] [default] stanza first
    - [ ] Group by stanza type/prefix
    - [ ] Sort alphabetically within groups
  - [ ] Validate .conf structure
  - [ ] Handle comments and continuation lines

- [ ] Merge Logic
  - [ ] Merge local stanzas into default
  - [ ] Preserve existing default values
  - [ ] Handle new/modified stanzas
  - [ ] Handle deleted keys

- [ ] Validation & Safety
  - [ ] Validate merged content
  - [ ] Create backups
  - [ ] Implement logging
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

- None yet

## Notes

- Current approach: Generic .conf file handling first
- Hybrid sorting strategy chosen for stanza organization
- Focus on completing each phase fully before moving to next
