"""Command implementations for byDefault.

Available commands:
    - validate: Verify Splunk TA configuration structure and syntax
    - scan: Scan Splunk TA directories for configuration changes
    - sort: Sort configuration files maintaining structure and comments
    - merge: Merge changes from local directory into default directory
"""

__all__ = ["validator", "scan", "sort", "merge"]  # Add commands to exports
