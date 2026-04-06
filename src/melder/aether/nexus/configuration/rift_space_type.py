from enum import Enum

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg


class RiftSpaceType(Enum):
    """
    Internal

    Supported top-level room types for a Rift.

    Members:
        static:
            The Rift exposes a stable room surface with fixed local structure.
        dynamic:
            The Rift exposes a room surface intended for mutable or evolving
            local state/layout.
    """

    __melder_internal__ = _mrg.sentinel
    static = "static"
    dynamic = "dynamic"
