import importlib
from typing import Dict

import pytest

from melder.aether.aether import Aether
from melder.aether.aetheric_frame import AethericFrame
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.conduit_ward.conduit_ward import ConduitWard
from melder.aether.conduit.conduit_ward.contract.contract import Contract
from melder.aether.conduit.conduit_ward.contract.details import Detail
from melder.aether.conduit.creations.creations import Creations
from melder.aether.conduit.meld.meld import Meld
from melder.aether.conduit.spell_space.spell_space import SpellSpace
from melder.aether.conduit_cloud import ConduitCloud
from melder.aether.dev_ops.change_control_manager.change_control_manager import ChangeControlManager
from melder.aether.dev_ops.dev_ops_manager import DevOpsManager
from melder.aether.dev_ops.incident_manager.incident_manager import IncidentManager
from melder.aether.dev_ops.spell_system_states.conduit_resolution_state import ConduitResolutionState
from melder.aether.dev_ops.spell_system_states.spell_system_states import SpellSystemStates
from melder.spellbook.bind.bind import Bind
from melder.spellbook.bind.spell_index import SpellIndex
from melder.spellbook.configuration.configuration import Configuration
from melder.spellbook.spell import Spell
from melder.spellbook.spellbook import Spellbook
from melder.utilities.interfaces.assets.icleanable import ICleanable as AssetICleanable
from melder.utilities.interfaces.interfaces import (
    IAether,
    IAethericFrame,
    IBind,
    IChangeControlManager,
    ICleanable,
    IConduit,
    IConduitCloud,
    IConduitResolutionState,
    IConduitWard,
    IContract,
    ICreations,
    IDetail,
    IDevOpsManager,
    IIncidentManager,
    IConfiguration,
    IMeld,
    ISafeLogger,
    ISpell,
    ISpellbook,
    ISpellIndex,
    ISpellSpace,
    ISpellSystemStates,
)
from melder.utilities.logger.safe_logger import SafeLogger


_INTERFACE_MAP: Dict[type, type] = {
    IAether: Aether,
    IAethericFrame: AethericFrame,
    IBind: Bind,
    IChangeControlManager: ChangeControlManager,
    IConduit: Conduit,
    IConduitCloud: ConduitCloud,
    IConduitResolutionState: ConduitResolutionState,
    IConduitWard: ConduitWard,
    IContract: Contract,
    ICreations: Creations,
    IDetail: Detail,
    IDevOpsManager: DevOpsManager,
    IIncidentManager: IncidentManager,
    IConfiguration: Configuration,
    IMeld: Meld,
    ISafeLogger: SafeLogger,
    ISpell: Spell,
    ISpellbook: Spellbook,
    ISpellIndex: SpellIndex,
    ISpellSpace: SpellSpace,
    ISpellSystemStates: SpellSystemStates,
}


def test_interfaces_aggregator_exports_asset_icleanable() -> None:
    """
    Verify `interfaces.py` re-exports the asset-backed `ICleanable` contract.

    Returns:
        None.
    """
    assert ICleanable is AssetICleanable


def test_interfaces_star_import_surface_matches___all__() -> None:
    """
    Verify the interfaces aggregator can populate a namespace from `__all__`.

    Returns:
        None.
    """
    interfaces_module = importlib.import_module(
        "melder.utilities.interfaces.interfaces"
    )
    namespace = {}
    exec(
        "from melder.utilities.interfaces.interfaces import *",
        {},
        namespace,
    )

    for exported_name in interfaces_module.__all__:
        assert exported_name in namespace


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
