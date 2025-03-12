#!/usr/bin/env bash

# Function to confirm directory removal
confirm_cleanup() {
    if [ -d "test_tas" ]; then
        read -r -p "test_tas directory exists. Remove and recreate? (y/N) " choice
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

# Function to generate a random version number
generate_version() {
    echo "$((RANDOM % 5)).$((RANDOM % 10)).$((RANDOM % 20))"
}

# Function to generate a random date in the past (up to 3 years)
generate_date() {
    # Days in the past (up to 3 years)
    days=$((RANDOM % 1095))
    date -d "$days days ago" +"%Y-%m-%d"
}

# Function to generate a random timestamp
generate_timestamp() {
    echo "$((1500000000 + RANDOM * 100)).000000000"
}

# Main script
confirm_cleanup

# Create base test directory
ensure_dir "test_tas"

# Define a more realistic set of TAs
TAS=(
    # Original test TAs
    "TA_valid"
    "TA_invalid"
    "TA_no_local"
    "TA_identical"
    "TA_local_only_files"
    "TA_stanza_changes"
    
    # Realistic Splunk TA examples
    "Splunk_TA_windows"
    "Splunk_TA_nix"
    "Splunk_TA_microsoft-cloudservices"
    "TA_aws_cloudwatch"
    "TA_microsoft_ad"
    "TA_cisco_networks"
    "Splunk_TA_oracle"
    "Splunk_TA_juniper"
    "Splunk_TA_kafka"
    "Splunk_TA_vmware"
    "TA_palo-alto_networks"
    "SA_gdpr_audit"
)

# Common configuration files in TAs
CONF_FILES=(
    "props.conf"
    "transforms.conf"
    "inputs.conf"
    "outputs.conf"
    "server.conf"
    "savedsearches.conf"
    "macros.conf"
    "eventtypes.conf"
    "tags.conf"
    "fields.conf"
    "limits.conf"
    "alert_actions.conf"
)

echo "Creating enhanced test environment with realistic TAs..."

# Create all TAs with standard structure
for ta in "${TAS[@]}"; do
    # Skip TA_no_local for special handling later
    if [ "$ta" == "TA_no_local" ]; then
        continue
    fi
    
    # Skip TA_invalid for special handling later
    if [ "$ta" == "TA_invalid" ]; then
        continue
    fi
    
    # Create standard Splunk TA directory structure
    ensure_dir "test_tas/$ta/bin"
    ensure_dir "test_tas/$ta/default"
    ensure_dir "test_tas/$ta/local"
    ensure_dir "test_tas/$ta/metadata"
    
    # Add a README
    cat >test_tas/$ta/README.md <<EOF
# $ta

This is a test TA for validating byDefault functionality.
Version: $(generate_version)
Created: $(generate_date)
EOF
    
    # Create app.conf in default (always present)
    cat >test_tas/$ta/default/app.conf <<EOF
[install]
state = enabled
build = $((RANDOM % 100 + 1))
is_configured = true

[package]
id = $ta
check_for_updates = 0

[ui]
is_visible = ${RANDOM:0:1}
label = ${ta//_/ }
EOF
    
    # Create app.conf in local (common in real TAs)
    cat >test_tas/$ta/local/app.conf <<EOF
[install]
state = enabled

[ui]
is_visible = 1
EOF
    
    # Create metadata files
    cat >test_tas/$ta/metadata/default.meta <<EOF
[]
access = read : [ * ], write : [ admin ]
export = system
version = ${RANDOM:0:1}.${RANDOM:0:1}.${RANDOM:0:1}
modtime = $(generate_timestamp)
EOF
    
    cat >test_tas/$ta/metadata/local.meta <<EOF
[app/ui]
version = 8.1.0
modtime = $(generate_timestamp)
EOF
    
    # Randomly create some of the common conf files
    for conf_file in "${CONF_FILES[@]}"; do
        # Skip some files randomly for realism
        if (( RANDOM % 3 == 0 )); then
            continue
        fi
        
        # Always create some default files for common configs
        if [[ "$conf_file" =~ ^(props|transforms|inputs|server)\.conf$ ]] || (( RANDOM % 2 == 0 )); then
            if [ "$conf_file" == "props.conf" ]; then
                cat >test_tas/$ta/default/$conf_file <<EOF
# Standard sourcetype definitions for $ta
[source::${ta}_logs]
SHOULD_LINEMERGE = false
LINE_BREAKER = ([\r\n]+)
TRANSFORMS-${ta}1 = ${ta}_transform1
TIME_PREFIX = timestamp=
TRUNCATE = 10000
MAX_TIMESTAMP_LOOKAHEAD = 40

[source::${ta}_events]
SHOULD_LINEMERGE = true
MAX_EVENTS = 1000
TRANSFORMS-first = ${ta}_transform_one
TRANSFORMS-second = ${ta}_transform_two
DATETIME_CONFIG = CURRENT
KV_MODE = json
CHECK_FOR_HEADER = true
SEDCMD-normalize = s/ERROR/Error/g
EOF
            elif [ "$conf_file" == "transforms.conf" ]; then
                cat >test_tas/$ta/default/$conf_file <<EOF
# Transform configurations for $ta
[${ta}_transform1]
REGEX = (.*)
FORMAT = $1
SOURCE_KEY = _raw
DEST_KEY = _raw
KEEP_EMPTY = false

[${ta}_transform_one]
REGEX = (?<field1>.*?)\|(?<field2>.*?)
FORMAT = $1::$2
WRITE_META = true
DEST_KEY = _meta

[${ta}_transform_two]
REGEX = (?<timestamp>\d{4}-\d{2}-\d{2})
FORMAT = timestamp::$1
DEST_KEY = MetaData:Time
MV_ADD = true
EOF
            elif [ "$conf_file" == "inputs.conf" ]; then
                cat >test_tas/$ta/default/$conf_file <<EOF
[monitor:///var/log/system.log]
index = main
sourcetype = system
disabled = 0
followTail = 1
crcSalt = <SOURCE>

[monitor:///var/log/application.log]
index = ${ta,,}_logs
sourcetype = application
disabled = 0
EOF
            elif [ "$conf_file" == "server.conf" ]; then
                cat >test_tas/$ta/default/$conf_file <<EOF
[general]
serverName = splunk-$(date +%s%N | sha256sum | head -c 8)
pass4SymmKey = $(< /dev/urandom tr -dc A-Za-z0-9 | head -c 24)
site = site1

[sslConfig]
enableSplunkdSSL = true
useClientSSLCompression = true
sslVersions = tls1.2
cipherSuite = TLSv1.2:!eNULL:!aNULL
EOF
            elif [ "$conf_file" == "savedsearches.conf" ]; then
                cat >test_tas/$ta/default/$conf_file <<EOF
[Detect ${ta} Errors]
search = index=${ta,,}_logs sourcetype=${ta}_events "error" OR "fail" OR "exception"
cron_schedule = 0 * * * *
dispatch.earliest_time = -4h
dispatch.latest_time = now
alert_type = email
alert_comparator = greater than
alert_threshold = 0
alert.severity = 4
alert.suppress = 0
alert.track = 1
action.email = 1
action.email.to = alerts@example.com
action.email.subject = $ta Alert: Errors Detected

[${ta} Performance Summary]
search = index=${ta,,}_logs sourcetype=${ta}_metrics | timechart avg(response_time) as avg_response
cron_schedule = 0 6 * * *
dispatch.earliest_time = -1d@d
dispatch.latest_time = @d
EOF
            elif [ "$conf_file" == "macros.conf" ]; then
                cat >test_tas/$ta/default/$conf_file <<EOF
[${ta}_filter]
definition = index=${ta,,}_logs (sourcetype=${ta}_events OR sourcetype=${ta}_logs)
iseval = 0

[${ta}_performance_metrics]
definition = index=${ta,,}_logs sourcetype=${ta}_metrics | eval response_time=round(response_time,2)
iseval = 0

[${ta}_critical_errors]
definition = index=${ta,,}_logs sourcetype=${ta}_events severity="critical"
iseval = 0
EOF
            elif [ "$conf_file" == "eventtypes.conf" ]; then
                cat >test_tas/$ta/default/$conf_file <<EOF
[${ta}_error]
search = index=${ta,,}_logs sourcetype=${ta}_events severity=error OR level=error

[${ta}_warning]
search = index=${ta,,}_logs sourcetype=${ta}_events severity=warning OR level=warning

[${ta}_info]
search = index=${ta,,}_logs sourcetype=${ta}_events severity=info OR level=info
EOF
            elif [ "$conf_file" == "tags.conf" ]; then
                cat >test_tas/$ta/default/$conf_file <<EOF
[eventtype=${ta}_error]
error = enabled
security = enabled

[eventtype=${ta}_warning]
warning = enabled
performance = enabled

[eventtype=${ta}_info]
info = enabled
EOF
            elif [ "$conf_file" == "fields.conf" ]; then
                cat >test_tas/$ta/default/$conf_file <<EOF
[response_time]
INDEXED = true
INDEXED_VALUE = true

[user_id]
INDEXED = true

[session_id]
INDEXED = true
EOF
            elif [ "$conf_file" == "limits.conf" ]; then
                cat >test_tas/$ta/default/$conf_file <<EOF
[realtime]
indexed_realtime_use_by_default = false

[search]
dispatch_dir_warning_size = 5000
EOF
            elif [ "$conf_file" == "alert_actions.conf" ]; then
                cat >test_tas/$ta/default/$conf_file <<EOF
[email]
ttl = 600
from = splunk@example.com
mailserver = smtp.example.com:25
use_ssl = 0
use_tls = 1

[webhook]
ttl = 600
EOF
            else
                # Generic conf file with a few stanzas
                cat >test_tas/$ta/default/$conf_file <<EOF
[default]
setting1 = value1
setting2 = value2

[${ta}_specific]
option1 = true
option2 = 42
option3 = "string value"
EOF
            fi
        fi
        
        # Create some local overrides
        if (( RANDOM % 2 == 0 )); then
            if [ "$conf_file" == "props.conf" ]; then
                cat >test_tas/$ta/local/$conf_file <<EOF
# Local overrides for props.conf
[source::${ta}_logs]
MAX_EVENTS = 500
KV_MODE = auto

# This stanza only exists in local, not in default
[source::${ta}_local_logs]
SHOULD_LINEMERGE = false
LINE_BREAKER = ([\r\n]+)
TRANSFORMS-local = ${ta}_local_transform
EOF
            elif [ "$conf_file" == "transforms.conf" ]; then
                cat >test_tas/$ta/local/$conf_file <<EOF
# Override an existing transform
[${ta}_transform1]
REGEX = (.*?)
FORMAT = modified::$1
SOURCE_KEY = _raw

# Add a new transform that only exists in local
[${ta}_local_transform]
REGEX = (?<field1>local_.*?)
FORMAT = local::$1
SOURCE_KEY = _raw
EOF
            elif [ "$conf_file" == "savedsearches.conf" ]; then
                cat >test_tas/$ta/local/$conf_file <<EOF
[${ta} Performance Summary]
cron_schedule = 0 12 * * *
dispatch.earliest_time = -7d@d
dispatch.latest_time = @d
EOF
            else
                # Generic local override
                cat >test_tas/$ta/local/$conf_file <<EOF
# Local overrides
[${ta}_specific]
option1 = false
option4 = "new value only in local"
EOF
            fi
        fi
    done
    
    # Create some Python scripts in bin
    cat >test_tas/$ta/bin/setup.py <<EOF
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json
import logging
from splunklib import client

def setup():
    """Initial setup for $ta"""
    logging.info("Setting up $ta...")
    
    # Setup code would go here
    
    return True

if __name__ == "__main__":
    setup()
EOF
    
    # Make scripts executable
    chmod +x test_tas/$ta/bin/setup.py
done

# Special cases for specific TAs

# 1. TA with no local directory
ensure_dir "test_tas/TA_no_local/default"
ensure_dir "test_tas/TA_no_local/bin"
ensure_dir "test_tas/TA_no_local/metadata"

cat >test_tas/TA_no_local/default/app.conf <<EOF
[install]
state = enabled

[package]
id = TA_no_local
check_for_updates = 0

[ui]
is_visible = 0
EOF

# 2. TA with identical local and default
ensure_dir "test_tas/TA_identical/default"
ensure_dir "test_tas/TA_identical/local"
ensure_dir "test_tas/TA_identical/bin"

cat >test_tas/TA_identical/default/app.conf <<EOF
[install]
state = enabled

[package]
id = TA_identical
check_for_updates = 0
EOF

# Copy the exact same content to local
cp test_tas/TA_identical/default/app.conf test_tas/TA_identical/local/app.conf

# 3. TA with invalid configurations 
ensure_dir "test_tas/TA_invalid/bin"
ensure_dir "test_tas/TA_invalid/default"
ensure_dir "test_tas/TA_invalid/local"
ensure_dir "test_tas/TA_invalid/metadata"

cat >test_tas/TA_invalid/default/app.conf <<EOF
[install]
state = enabled
build = 1

[package]
id = TA_invalid
check_for_updates = 0

[ui]
is_visible = 0
label = Test TA Invalid
EOF

# Create invalid props.conf
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

# Create malformed transforms.conf with syntax errors
cat >test_tas/TA_invalid/default/transforms.conf <<EOF
# Missing equals sign
[transform1]
REGEX (.*?)
FORMAT = $1

# Missing value
[transform2]
REGEX = 
SOURCE_KEY = 

# Invalid directive
[transform3]
NOTAVALIDKEY = somevalue
EOF

# Create a non-UTF8 file
echo -e "[\xFF\xFE]invalid_encoding" >test_tas/TA_invalid/default/limits.conf

# Create empty files
touch test_tas/TA_invalid/default/empty.conf
touch test_tas/TA_invalid/default/macros.conf

# Create a file with invalid extension
cp test_tas/TA_valid/default/props.conf test_tas/TA_invalid/default/props.txt

# Create a savedsearches.conf with too many searches (performance issue)
for i in {1..100}; do
    echo "[Heavy Search $i]" >> test_tas/TA_invalid/default/savedsearches.conf
    echo "search = index=* | stats count by host, source, sourcetype" >> test_tas/TA_invalid/default/savedsearches.conf
    echo "cron_schedule = */$((i % 5 + 1)) * * * *" >> test_tas/TA_invalid/default/savedsearches.conf
    echo "" >> test_tas/TA_invalid/default/savedsearches.conf
done

# 4. Create a simulated complex Splunk_TA_windows with extensive configuration
mkdir -p test_tas/Splunk_TA_windows/local
cat >test_tas/Splunk_TA_windows/local/inputs.conf <<EOF
[WinEventLog:Security]
disabled = 0
index = windows
start_from = oldest
current_only = 0

[WinEventLog:System]
disabled = 0
index = windows
start_from = oldest
current_only = 0

[WinEventLog:Application]
disabled = 0
index = windows
start_from = oldest
current_only = 0

[perfmon://CPU]
disabled = 0
counters = % Processor Time;% User Time;% Privileged Time
instances = _Total
interval = 10
object = Processor
index = perfmon
EOF

cat >test_tas/Splunk_TA_windows/local/props.conf <<EOF
[source::WinEventLog:Security]
TRANSFORMS-nullqueue = setnull
TRANSFORMS-commentary = commentary

[source::WinEventLog:Application]
TRANSFORMS-set_source = source_adjustment
TRANSFORMS-extract_ids = extract_event_ids

[perfmon]
TRANSFORMS-clean = clean_perfmon_data
KV_MODE = none
REPORT-fields = extract_perfmon_fields
FIELDALIAS-app = object AS application
LOOKUP-severity = severity_lookup severity OUTPUT urgency
EOF

# 5. Create a TA with lots of local modifications (common in customer environments)
ensure_dir "test_tas/TA_heavy_customization/default"
ensure_dir "test_tas/TA_heavy_customization/local"
ensure_dir "test_tas/TA_heavy_customization/bin"
ensure_dir "test_tas/TA_heavy_customization/metadata"

# Create standard default configurations
for conf_file in "${CONF_FILES[@]:0:6}"; do
    # Create a simple default with minimal settings
    cat >test_tas/TA_heavy_customization/default/$conf_file <<EOF
# Default $conf_file configuration
[default]
setting1 = original_value
setting2 = original_value
EOF

    # Create a heavily modified local version
    cat >test_tas/TA_heavy_customization/local/$conf_file <<EOF
# Heavily customized $conf_file
[default]
setting1 = customized_value
setting3 = new_setting
setting4 = new_setting

[custom_stanza_1]
param1 = value1
param2 = value2
param3 = value3

[custom_stanza_2]
config1 = option1
config2 = option2

[custom_stanza_3]
setting = true
mode = advanced
option = special
EOF
done

# Add to .git/info/exclude if not already there
mkdir -p .git/info
if ! grep -q "test_tas/" .git/info/exclude; then
    echo "test_tas/" >> .git/info/exclude
    echo "Added test_tas/ to .git/info/exclude to prevent git tracking"
fi

# Print summary
echo "Enhanced test TAs created in test_tas/ directory"
echo "Created $(find test_tas -type f | wc -l) files across ${#TAS[@]} TAs"
echo "Directory has been added to local git exclude (NOT .gitignore)"
echo
echo "Test cases available:"
echo "- Standard TAs with realistic configuration"
echo "- TAs with various common configuration files"
echo "- TA with no local directory"
echo "- TA with identical local and default"
echo "- TA with invalid configurations"
echo "- TA with heavy local customization"
echo "- Realistic TAs modeled after common Splunk add-ons"
