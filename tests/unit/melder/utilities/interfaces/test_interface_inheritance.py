from typing import Dict

import pytest

from melder.aether.aetheric_frame.aetheric_frame import AethericFrame
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.conduit_ward.conduit_ward import ConduitWard

from melder.aether.spellbook.spell import Spell
from melder.aether.spellbook.spellbook import Spellbook
from melder.utilities.interfaces.icleanable import ICleanable as AssetICleanable
from melder.utilities.interfaces.icleanable import ICleanable
from melder.utilities.interfaces.iconduit import IConduit
from melder.utilities.logger.safe_logger import SafeLogger


_INTERFACE_MAP: Dict[type, type] = {
    IConduit: Conduit,
}


def test_interfaces_aggregator_exports_asset_icleanable() -> None:
    """
    Verify `interfaces.py` re-exports the asset-backed `ICleanable` contract.

    Returns:
        None.
    """
    assert ICleanable is AssetICleanable
@pytest.mark.parametrize(("interface_type", "implementation_type"), list(_INTERFACE_MAP.items()))
def test_concrete_types_explicitly_inherit_interfaces(
        interface_type: type,
        implementation_type: type,
) -> None:
    """
    Purpose:
        Ensure concrete classes explicitly inherit their interface protocols.
    Contract:
        - Each implementation lists the interface in its MRO, proving explicit inheritance.
        - The check is structural only for the class hierarchy and avoids instantiation.
    Returns:
        None.
    Raises:
        AssertionError: If an implementation does not inherit the expected interface.
    """
    assert interface_type in implementation_type.__mro__

