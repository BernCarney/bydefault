"""Common test fixtures."""

import pytest


@pytest.fixture
def complete_ta_structure(tmp_path):
    """Create a complete TA structure with all common file types."""
    ta_root = tmp_path / "TA-test"

    # Create standard directories
    dirs = {
        "local": ta_root / "local",
        "default": ta_root / "default",
        "metadata": ta_root / "metadata",
        "lookups": ta_root / "lookups",
        "bin": ta_root / "bin",
        "appserver": ta_root / "appserver" / "static",
        "views": ta_root / "default" / "data" / "ui" / "views",
    }

    for dir_path in dirs.values():
        dir_path.mkdir(parents=True, exist_ok=True)

    # Create configuration files in local/
    local_configs = {
        "props.conf": """
[test_sourcetype]
TRANSFORMS-test = test_transform
SHOULD_LINEMERGE = false
TIME_PREFIX = timestamp=
MAX_TIMESTAMP_LOOKAHEAD = 40
        """,
        "transforms.conf": """
[test_transform]
REGEX = timestamp=(\d{10}\.\d{3})
FORMAT = timestamp::$1
DEST_KEY = _time

[test_lookup]
filename = test_lookup.csv
        """,
        "inputs.conf": """
[monitor:///var/log/test/*.log]
sourcetype = test_sourcetype
index = main
disabled = 0
        """,
        "fields.conf": """
[test_field]
INDEXED = true
        """,
        "eventtypes.conf": """
[test_eventtype]
search = sourcetype=test_sourcetype error
        """,
        "tags.conf": """
[eventtype=test_eventtype]
incident = enabled
        """,
        "macros.conf": """
[test_macro(1)]
args = field
definition = sourcetype=test_sourcetype | where $field$="test"
        """,
        "web.conf": """
[settings]
enableSplunkWebSSL = true
        """,
    }

    for conf_name, content in local_configs.items():
        (dirs["local"] / conf_name).write_text(content.strip())
        # Create empty default files
        (dirs["default"] / conf_name).touch()

    # Create app.conf in default/
    app_conf = """
[install]
state = enabled

[package]
id = TA-test
check_for_updates = 0

[launcher]
version = 1.0.0
author = Test Author

[ui]
is_visible = 1
label = Test TA
        """
    (dirs["default"] / "app.conf").write_text(app_conf.strip())

    # Create local.meta
    local_meta = """
[props/test_sourcetype]
access = read : [ * ], write : [ admin ]
owner = admin
version = 8.0.0

[transforms/test_transform]
access = read : [ * ], write : [ admin ]
owner = admin
version = 8.0.0
        """
    (dirs["metadata"] / "local.meta").write_text(local_meta.strip())
    (dirs["metadata"] / "default.meta").touch()

    # Create a sample dashboard
    dashboard_xml = """
<dashboard>
    <label>Test Dashboard</label>
    <row>
        <panel>
            <title>Test Panel</title>
            <chart>
                <search>
                    <query>sourcetype=test_sourcetype | timechart count</query>
                    <earliest>-24h</earliest>
                    <latest>now</latest>
                </search>
                <option name="charting.chart">line</option>
            </chart>
        </panel>
    </row>
</dashboard>
        """
    (dirs["views"] / "test_dashboard.xml").write_text(dashboard_xml.strip())

    # Create sample lookup files
    lookup_csv = """field1,field2,field3
value1,value2,value3
value4,value5,value6
        """
    (dirs["lookups"] / "test_lookup.csv").write_text(lookup_csv.strip())

    # Create a sample binary file
    (dirs["bin"] / "test_script.py").write_text(
        """
#!/usr/bin/env python
print("Test script")
        """.strip()
    )

    return ta_root
