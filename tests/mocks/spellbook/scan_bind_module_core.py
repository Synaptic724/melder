"""
Core scan_bind mock module for integration tests.

This module defines a mix of decorated and undecorated objects to validate
scan selection behavior and binding outcomes.
"""
from melder.spellbook.bind.scan import scan_bind
from melder.spellbook.existence.existence import Existence


@scan_bind(
    existence=Existence.unique,
    permissions="create",
    spellframe="scan_core",
    binding_name="alpha",
)
class ScanCoreAlpha:
    """
    Purpose:
        Provide a decorated class spell for scan_bind integration tests.
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
        self.marker = "alpha"


@scan_bind(
    existence=Existence.unique,
    permissions="create",
    spellframe="scan_core",
    binding_name="beta",
)
class ScanCoreBeta:
    """
    Purpose:
        Provide a second decorated class spell for scan_bind tests.
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
        self.marker = "beta"


@scan_bind(
    existence=Existence.unique,
    permissions="create",
    spellframe="scan_factory",
    binding_name="message_factory",
)
def build_message() -> str:
    """
    Purpose:
        Provide a decorated factory function for scan_bind tests.
    Contract:
        Returns a stable string value.
    Returns:
        str: The stable message string.
    """
    return "hello"


class ScanCoreIgnored:
    """
    Purpose:
        Provide an undecorated object to verify scan skips non-marked entries.
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
        self.marker = "ignored"
