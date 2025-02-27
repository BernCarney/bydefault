# Test TA Environment

This directory contains generated Splunk TA (Technology Add-on) test configurations used for testing byDefault's functionality.

## Important Notes

- **DO NOT COMMIT** these files to the repository
- Files are excluded via `.git/info/exclude` rather than `.gitignore` to maintain visibility in Cursor IDE
- The environment can be regenerated at any time with `./scripts/create_test_tas.sh`

## Test Cases Included

- Basic validation with valid TA configurations
- Syntax errors and invalid configurations
- Duplicate stanzas
- Invalid encodings
- Empty files
- Invalid file extensions
- Local overrides
- Metadata files
- TA with no local directory
- TA with identical local and default
- TA with local-only conf files
- TA with complex stanza changes

## Regenerating the Environment

If you need to reset the test environment:

```bash
$ ./scripts/create_test_tas.sh
```

This will prompt you to confirm if you want to remove the existing environment. 