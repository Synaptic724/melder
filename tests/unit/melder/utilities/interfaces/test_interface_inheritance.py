from typing import Dict

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_configuration import AetherConfiguration
from melder.aether.aether_configuration_builder import AetherConfigurationBuilder
from melder.aether.aetheric_frame.aetheric_frame import AethericFrame
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.conduit_ward.conduit_ward import ConduitWard
from melder.aether.conduit.conduit_ward.contract.contract import Contract
from melder.aether.conduit.conduit_ward.contract.details import Detail
from melder.aether.conduit.creations.creations import Creations
from melder.aether.conduit.meld.meld import Meld
from melder.aether.conduit.spell_space.spell_space import SpellSpace
from melder.aether.aetheric_frame.conduit_cloud import ConduitCloud
from melder.aether.aetheric_frame.dev_ops.change_control_manager.change_control_manager import ChangeControlManager
from melder.aether.aetheric_frame.dev_ops.dev_ops_manager import DevOpsManager
from melder.aether.aetheric_frame.dev_ops.incident_manager.incident_manager import IncidentManager
from melder.aether.aetheric_frame.dev_ops.spell_system_states.conduit_resolution_state import ConduitResolutionState
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_states import SpellSystemStates
from melder.aether.spellbook.bind.bind import Bind
from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.spell import Spell
from melder.aether.spellbook.spellbook import Spellbook
from melder.utilities.interfaces.icleanable import ICleanable as AssetICleanable
from melder.utilities.interfaces.iaethericframe import IAethericFrame
from melder.utilities.interfaces.icleanable import ICleanable
from melder.utilities.interfaces.iconduit import IConduit
from melder.utilities.interfaces.iconduitward import IConduitWard
from melder.utilities.interfaces.iconfiguration import IConfiguration
from melder.utilities.interfaces.isafelogger import ISafeLogger
from melder.utilities.interfaces.ispell import ISpell
from melder.utilities.interfaces.ispellbook import ISpellbook
from melder.utilities.logger.safe_logger import SafeLogger


_INTERFACE_MAP: Dict[type, type] = {
    IAethericFrame: AethericFrame,
    IConduit: Conduit,
    IConduitWard: ConduitWard,
    IConfiguration: SpellbookConfiguration,
    ISafeLogger: SafeLogger,
    ISpell: Spell,
    ISpellbook: Spellbook,
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
