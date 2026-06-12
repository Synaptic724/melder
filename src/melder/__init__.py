

"""
melder
Lightweight dependency injection system designed for high-performance modular Python systems like ThreadFactory.
"""

import sys
import warnings

from melder.__melder_registration_guard__ import MelderRegistrationGuard
from melder.__version__ import __version__ as base_version
from melder.aether.aether_configuration import AetherConfiguration
from melder.aether.aether_configuration_builder import AetherConfigurationBuilder
from melder.aether.aetheric_frame.aetheric_frame_configuration import AethericFrameConfiguration
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.aether.spellbook.bind.scan import Scan
from melder.nexus.nexus import Nexus
from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)
from melder.aether.spellbook.configuration.system_state import SystemState
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbinder import SpellBinder
from melder.aether.spellbook.spellbook import Spellbook
from melder.utilities.ai_native_support_tools.protocol_crafter import ProtocolCrafter
from melder.aether.conduit.conduit import Conduit
from melder.aether.aether import Aether

# Eagerly instantiate the registration guard at package import time (internal use).
__melder_registration_guard__ = MelderRegistrationGuard()
Aether()


DEBUG_MODE = True
# 🔧 Append "-dev" in DEBUG_MODE without mutating original
__version__ = base_version + "-dev" if DEBUG_MODE else base_version


# ✅ Soft warning if not optimized Python version
if sys.version_info < (3, 13, 0):
    warnings.warn(
        (
            "melder is optimized for Python 3.13+ (no-GIL). "
            f"You are running Python {sys.version_info.major}."
            f"{sys.version_info.minor}.{sys.version_info.micro}. "
            "Functionality will still work on older Pythons, but performance may be significantly degraded."
        ),
        category=UserWarning,
        stacklevel=2,
    )

def _detect_nogil_mode() -> None:
    """
    Warn if we're not on a Python 3.13+ no-GIL build.
    """
    try:
        GIL_ENABLED = sys._is_gil_enabled()
    except AttributeError:
        GIL_ENABLED = True  # Assume legacy build with GIL

    if GIL_ENABLED:
        warnings.warn(
            "⚠️ Python 3.13+ detected, but running in GIL-enabled mode.\n"
            "melder is optimized for Python built with --disable-gil (PEP 703).\n"
            "Performance may be degraded.",
            UserWarning
        )

_detect_nogil_mode()


# --------------------------------------------------------------------------
# Lazy package metadata (PEP 562).
#
# The static system documents (__architecture__, __components__, the graph
# documents) pull in the json/document stack, which costs real milliseconds
# on the cold import path while serving zero runtime traffic. They are now
# resolved on first attribute access and cached in the module dict, so the
# second access is a plain global read. `from melder import *` still exports
# them (star-import resolves __all__ names through this hook).
# --------------------------------------------------------------------------
_LAZY_METADATA = {
    "__architecture__": ("melder.__architecture__", "__architecture__"),
    "__author__": ("melder.__author__", "CREATOR"),
    "__components__": ("melder.__components__", "__components__"),
    "__description__": ("melder.__description__", "__description__"),
    "__graph_details__": ("melder.__graph_details__", "__graph_details__"),
    "__graph_network__": ("melder.__graph_network__", "__graph_network__"),
    "__license__": ("melder.__license__", "__license__"),
}


def __getattr__(name: str):
    """
    Resolve lazy package-metadata attributes on first access (PEP 562).
    """
    target = _LAZY_METADATA.get(name)
    if target is None:
        raise AttributeError(f"module 'melder' has no attribute {name!r}")
    import importlib

    value = getattr(importlib.import_module(target[0]), target[1])
    globals()[name] = value
    return value


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
    "AetherConfiguration",
    "AetherConfigurationBuilder",
    "AethericFrameConfiguration",
    "SpellbookConfiguration",
    "Existence",
    "Policies",
    "Permissions",
    "SystemState",
    "ProtocolCrafter",
    "Scan"
]

