from enum import Enum

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg


class RiftSpaceType(Enum):
    """
    Internal

    Supported top-level room types for a Rift.
    """

    __melder_internal__ = _mrg.sentinel
    static = "static"
    dynamic = "dynamic"

