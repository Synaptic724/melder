from enum import Enum

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg


class AethericRiftSystemFrameMode(Enum):
    """
    Internal

    Topology mode for ARS-owned internal system frames.

    Purpose:
        Define how many internal ARS system frames exist and how new workspaces
        obtain them.

    Members:
        single:
            One shared ARS-owned system frame is used for all workspaces.
        indexed:
            ARS may manage multiple internal system frames from an indexed set.
        one_per_workspace:
            Each workspace receives its own ARS-owned internal system frame.
    """

    __melder_internal__ = _mrg.sentinel
    single = "single"
    indexed = "indexed"
    one_per_workspace = "one_per_workspace"
