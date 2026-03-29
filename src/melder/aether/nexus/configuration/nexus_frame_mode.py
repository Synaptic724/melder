from enum import Enum

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg


class NexusFrameMode(Enum):
    """
    Internal

    Topology mode for Nexus-assigned internal frames.

    Purpose:
        Define how many internal Nexus frames exist and how new workspaces
        obtain them.

    Members:
        single:
            One shared Nexus-assigned frame is used for all workspaces.
        indexed:
            Nexus may manage multiple internal frames from an indexed set.
        one_per_workspace:
            Each workspace receives its own Nexus-assigned internal frame.
    """

    __melder_internal__ = _mrg.sentinel
    single = "single"
    indexed = "indexed"
    one_per_workspace = "one_per_workspace"
