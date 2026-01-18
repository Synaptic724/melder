"""
Corrupt scan_bind metadata mock module for integration tests.

Defines a target object with an invalid scan_bind metadata payload.
"""


class BadMetadataTarget:
    """
    Purpose:
        Provide a target with corrupted scan_bind metadata.
    Contract:
        - Constructs without arguments.
        - Exposes a stable marker value.
    """
    def __init__(self) -> None:
        """
        Purpose:
            Initialize the marker attribute.
        Contract:
            Sets marker to a stable value for assertions.
        Returns:
            None.
        """
        self.marker = "bad_metadata"


BadMetadataTarget.__melder_scan_bind__ = "corrupted"
