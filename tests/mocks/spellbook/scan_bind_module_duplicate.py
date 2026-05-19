"""
Duplicate scan_bind mock module for integration tests.

Defines two decorated classes with identical binding keys to trigger collisions.
"""
from melder.aether.spellbook.bind.scan import scan_bind
from melder.aether.spellbook.existence.existence import Existence


@scan_bind(
    existence=Existence.unique,
    permissions="create",
    spellframe="scan_dup",
    binding_name="primary",
)
class ScanDuplicateAlpha:
    """
    Purpose:
        Provide a duplicate binding target for collision tests.
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
    spellframe="scan_dup",
    binding_name="primary",
)
class ScanDuplicateBeta:
    """
    Purpose:
        Provide a second duplicate binding target for collision tests.
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
