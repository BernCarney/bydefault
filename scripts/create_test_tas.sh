#!/bin/bash

# Function to confirm directory removal
confirm_cleanup() {
    if [ -d "test_tas" ]; then
        read -p "test_tas directory exists. Remove and recreate? (y/N) " choice
        case "$choice" in
        y | Y)
            echo "Removing existing test_tas directory..."
            rm -rf test_tas
            return 0
            ;;
        *)
            echo "Keeping existing directory. New files may overwrite existing ones."
            return 1
            ;;
        esac
    fi
    return 0
}

# Function to ensure directory exists
ensure_dir() {
    mkdir -p "$1"
}

# Main script
confirm_cleanup

# Create test directory structure for both TAs
for ta in TA_valid TA_invalid; do
    # Create standard Splunk TA directory structure
    ensure_dir "test_tas/$ta/bin"
    ensure_dir "test_tas/$ta/default"
    ensure_dir "test_tas/$ta/local"
    ensure_dir "test_tas/$ta/metadata"

    # Create README.txt file
    cat >test_tas/$ta/README <<EOF
This is a test TA for validating byDefault functionality.
EOF

    # Create app.conf in default
    cat >test_tas/$ta/default/app.conf <<EOF
[install]
state = enabled
build = 1

[package]
id = $ta
check_for_updates = 0

[ui]
is_visible = 0
label = Test TA $ta
EOF

    # Create app.conf in local (common in real TAs)
    cat >test_tas/$ta/local/app.conf <<EOF
[install]
state = enabled

[ui]
is_visible = 1
EOF

    # Create metadata/default.meta
    cat >test_tas/$ta/metadata/default.meta <<EOF
[]
access = read : [ * ], write : [ admin ]
export = system
EOF

    # Create metadata/local.meta
    cat >test_tas/$ta/metadata/local.meta <<EOF
[app/ui]
version = 8.1.0
modtime = 1615430400.000000000
EOF
done

# Valid TA Configuration Files
cat >test_tas/TA_valid/default/props.conf <<EOF
# Standard sourcetype definition
[source::test_logs]
SHOULD_LINEMERGE = false
LINE_BREAKER = ([\r\n]+)
TRANSFORMS-test = test_transform
TIME_PREFIX = timestamp=

# Nested sourcetype with multiple transforms
[source::complex_logs]
SHOULD_LINEMERGE = true
MAX_EVENTS = 1000
TRANSFORMS-first = transform_one
TRANSFORMS-second = transform_two
DATETIME_CONFIG = CURRENT
EOF

# Create a local override for props.conf
cat >test_tas/TA_valid/local/props.conf <<EOF
[source::test_logs]
MAX_EVENTS = 500
EOF

cat >test_tas/TA_valid/default/transforms.conf <<EOF
# Basic transform
[test_transform]
REGEX = (.*)
FORMAT = $1
SOURCE_KEY = _raw

# Complex transform with multiple rules
[transform_one]
REGEX = (?<field1>.*?)\|(?<field2>.*?)
FORMAT = $1 $2
WRITE_META = true

[transform_two]
REGEX = (?<timestamp>\d{4}-\d{2}-\d{2})
FORMAT = timestamp::$1
DEST_KEY = MetaData:Time
EOF

# Invalid TA Configuration Files
cat >test_tas/TA_invalid/default/props.conf <<EOF
# Missing closing bracket
[source::bad_stanza
SHOULD_LINEMERGE = false

# Duplicate stanza
[source::duplicate]
key = value1

[source::duplicate]
key = value2

# Invalid key format
[source::invalid_keys]
BAD KEY = value
TRANSFORMS test = invalid
EOF

# Create a non-UTF8 file
echo -e "[\xFF\xFE]invalid_encoding" >test_tas/TA_invalid/default/limits.conf

# Create empty files that should be validated
touch test_tas/TA_invalid/default/empty.conf
touch test_tas/TA_invalid/default/macros.conf

# Create a file with invalid extension
cp test_tas/TA_valid/default/props.conf test_tas/TA_invalid/default/props.txt

# Add to .gitignore if not already there
if ! grep -q "test_tas/" .gitignore; then
    echo "test_tas/" >>.gitignore
fi

echo "Test TAs updated in test_tas/ directory"
echo "Directory has been added to .gitignore"
echo
echo "Test cases available:"
echo "- Basic validation"
echo "- Syntax errors"
echo "- Duplicate stanzas"
echo "- Invalid encodings"
echo "- Empty files"
echo "- Invalid file extensions"
echo "- Local overrides"
echo "- Metadata files"
