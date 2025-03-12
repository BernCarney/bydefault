"""Command implementations for byDefault.

Available commands:
    - validate: Verify Splunk TA configuration structure and syntax
    - scan: Scan Splunk TA directories for configuration changes
    - sort: Sort configuration files maintaining structure and comments
"""

__all__ = ["validator", "scan", "sort"]  # Add commands to exports
