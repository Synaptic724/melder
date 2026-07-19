
"""
melder

The Melder Dependency Graph Runtime (DGR): bind classes, functions, and
instances into Spellbooks, conjure Conduits, and meld live object graphs
with runtime validation, contracts, persistence, and governed evolution.

Usage:
    import melder as md

    book = md.Spellbook()
    book.bind(spell=MyService, existence=md.Existence.unique)
    conduit = book.conjure(dynamic=True, name="root")
    service = conduit.meld(spell=MyService)

The root namespace is deliberately LOADED: every front-facing runtime
object, configuration surface, enum vocabulary, and DI descriptor is
importable from here so `md.<name>` reaches the whole public system.
Internals never import from this facade (concrete-path law), so the root
can stay flat and eager without cycles.

Requires Python 3.14+ free-threading (no-GIL) for full performance; the
import-time warnings below call out degraded environments honestly.
"""

import sys
import warnings

# ---- package metadata (single version truth: melder.__version__) ----
from melder.__architecture__ import __architecture__
from melder.__author__ import CREATOR as __author__
from melder.__components__ import __components__
from melder.__description__ import __description__
from melder.__graph_details__ import __graph_details__
from melder.__graph_network__ import __graph_network__
from melder.__license__ import __license__
from melder.__melder_registration_guard__ import MelderRegistrationGuard
from melder.__version__ import __version__

# ---- core runtime objects ----
from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.bind.scan import Scan, scan_bind
from melder.aether.spellbook.spellbinder import SpellBinder
from melder.aether.spellbook.spellbook import Spellbook
from melder.crystallizer.crystallizer import Crystallizer
from melder.mutation_research.mutation_research import MutationResearch
from melder.nexus.nexus import Nexus

# ---- user-held work surfaces (returned by the objects above; exported so
# ---- user code can type, isinstance, and discover them from the root) ----
from melder.aether.aetheric_frame.conduit_cloud import ConduitCloud
from melder.aether.conduit.spell_space.spell_space import SpellSpace
from melder.aether.spellbook.spell_compiler.spell_examiner.spell_examiner import (
    SpellExaminer,
)
from melder.crystallizer.asset_management.external_persistence_manager import (
    ExternalPersistenceManager,
)
from melder.crystallizer.asset_management.external_persistence_manager_configuration import (
    ExternalPersistenceManagerConfiguration,
)
from melder.crystallizer.crystal_loader_system.bootstrap_loader import (
    CrystallizerBootstrap,
)
from melder.mutation_research.diff.diff_engine import DiffEngine
from melder.mutation_research.research_set.research_set import ResearchSet
from melder.nexus.rift.frame_viewer.frame_viewer import FrameViewer
from melder.nexus.rift.frame_viewer.view_conduit import ViewConduit
from melder.nexus.rift.frame_viewer.view_frame import ViewFrame
from melder.nexus.rift.frame_viewer.view_multiframe import ViewMultiFrame
from melder.nexus.rift.frame_viewer.view_spell import ViewSpell
from melder.nexus.rift.rift import Rift
from melder.nexus.rift.rift_space.rift_space import RiftSpace
from melder.nexus.rift.rift_space.workstation import Workstation

# ---- configuration surfaces ----
from melder.aether.aether_configuration import AetherConfiguration
from melder.aether.aether_configuration_builder import AetherConfigurationBuilder
from melder.aether.aetheric_frame.aetheric_frame_configuration import AethericFrameConfiguration
from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)
from melder.crystallizer.configuration.crystallizer_configuration import (
    CrystallizerConfiguration,
)
from melder.crystallizer.configuration.crystallizer_configuration_builder import (
    CrystallizerConfigurationBuilder,
)
from melder.mutation_research.mutation_configuration import (
    MutationResearchConfiguration,
)
from melder.mutation_research.mutation_configuration_builder import (
    MutationResearchConfigurationBuilder,
)
from melder.nexus.configuration.nexus_configuration import NexusConfiguration
from melder.nexus.configuration.rift_configuration import RiftConfiguration

# ---- front-facing enum vocabularies ----
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.aether.spellbook.configuration.system_state import SystemState
from melder.aether.spellbook.existence.existence import Existence
from melder.mutation_research.research_set.research_lane import LaneState, LaneType
from melder.nexus.configuration.nexus_frame_mode import NexusFrameMode
from melder.nexus.configuration.rift_space_type import RiftSpaceType

# ---- DI descriptors ----
from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.conduit.meld.contracts.spell_map import SpellMap

# ---- user-catchable error vocabulary (raised through public verbs) ----
from melder.utilities.custom_exceptions.dead_reference_error import DeadReferenceError
from melder.utilities.custom_exceptions.hook_execution_error import HookExecutionError
from melder.utilities.custom_exceptions.internal_registration_error import (
    InternalRegistrationError,
)
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
from melder.utilities.custom_exceptions.phase_execution_error import PhaseExecutionError
from melder.utilities.custom_exceptions.phase_scheduler_error import PhaseSchedulerError
from melder.utilities.custom_exceptions.phase_timeout_error import PhaseTimeoutError
from melder.utilities.custom_exceptions.spell_space_scope_error import (
    SpellSpaceScopeError,
)
from melder.utilities.custom_exceptions.spellbook_validation_error import (
    SpellbookValidationError,
)

# ---- agent/tooling helpers ----
from melder.utilities.ai_native_support_tools.protocol_crafter import ProtocolCrafter
from melder.utilities.helpers.class_wraps import class_wraps

# Eagerly instantiate the registration guard at package import time: the
# sentinel must exist before ANY internal object can be offered for
# registration (owner ruling 2026-07-19: Aether's boot also guarantees it,
# but the guard is a sentinel and the redundancy is intentional).
__melder_registration_guard__ = MelderRegistrationGuard()
Aether()


# Soft warning if not an optimized Python version.
if sys.version_info < (3, 14, 0):
    warnings.warn(
        (
            "melder requires Python 3.14+ (no-GIL). "
            f"You are running Python {sys.version_info.major}."
            f"{sys.version_info.minor}.{sys.version_info.micro}. "
            "This interpreter is below the supported floor; behavior and performance are unsupported."
        ),
        category=UserWarning,
        stacklevel=2,
    )

def _detect_nogil_mode() -> None:
    """
    Warn if we're not on a Python 3.14+ no-GIL build.
    """
    try:
        GIL_ENABLED = sys._is_gil_enabled()
    except AttributeError:
        GIL_ENABLED = True  # Assume legacy build with GIL

    if GIL_ENABLED:
        warnings.warn(
            "Python 3.14+ detected, but running in GIL-enabled mode.\n"
            "melder is optimized for Python built with --disable-gil (PEP 703).\n"
            "Performance may be degraded.",
            UserWarning
        )

_detect_nogil_mode()



__all__ = [
    "__version__",
    "__author__",
    "__license__",
    "__description__",
    "__architecture__",
    "__components__",
    "__graph_network__",
    "__graph_details__",
    "Aether",
    "Nexus",
    "Spellbook",
    "SpellBinder",
    "Conduit",
    "Crystallizer",
    "MutationResearch",
    "Scan",
    "ProtocolCrafter",
    "AetherConfiguration",
    "AetherConfigurationBuilder",
    "AethericFrameConfiguration",
    "SpellbookConfiguration",
    "CrystallizerConfiguration",
    "CrystallizerConfigurationBuilder",
    "MutationResearchConfiguration",
    "MutationResearchConfigurationBuilder",
    "NexusConfiguration",
    "RiftConfiguration",
    "Existence",
    "Policies",
    "Permissions",
    "SystemState",
    "LaneType",
    "NexusFrameMode",
    "RiftSpaceType",
    "SpellMap",
    "SpellContract",
    "Rift",
    "RiftSpace",
    "FrameViewer",
    "Workstation",
    "SpellSpace",
    "ConduitCloud",
    "ResearchSet",
    "SpellExaminer",
    "CrystallizerBootstrap",
    "ExternalPersistenceManager",
    "ExternalPersistenceManagerConfiguration",
    "scan_bind",
    "SpellbookValidationError",
    "MeldExecutionError",
    "SpellSpaceScopeError",
    "HookExecutionError",
    "InternalRegistrationError",
    "PhaseSchedulerError",
    "PhaseExecutionError",
    "PhaseTimeoutError",
    "DeadReferenceError",
    "ViewFrame",
    "ViewConduit",
    "ViewSpell",
    "ViewMultiFrame",
    "DiffEngine",
    "LaneState",
    "class_wraps",
]
