
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
from melder.aether.spellbook.bind.scan import Scan
from melder.aether.spellbook.spellbinder import SpellBinder
from melder.aether.spellbook.spellbook import Spellbook
from melder.crystallizer.crystallizer import Crystallizer
from melder.mutation_research.mutation_research import MutationResearch
from melder.nexus.nexus import Nexus

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
from melder.mutation_research.research_set.research_lane import LaneType
from melder.nexus.configuration.nexus_frame_mode import NexusFrameMode
from melder.nexus.configuration.rift_space_type import RiftSpaceType

# ---- DI descriptors ----
from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.conduit.meld.contracts.spell_map import SpellMap

# ---- agent/tooling helpers ----
from melder.utilities.ai_native_support_tools.protocol_crafter import ProtocolCrafter

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
]
