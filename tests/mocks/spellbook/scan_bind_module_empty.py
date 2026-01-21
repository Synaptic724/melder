"""
Empty scan_bind mock module for integration tests.

Contains no scan_bind-decorated objects.
"""


class EmptyModuleMarker:
    """
    Purpose:
        Provide a marker class without scan_bind decoration.
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
        self.marker = "empty"
