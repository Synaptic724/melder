from enum import Enum

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg


class RiftValidationMode(Enum):
    """
    Internal

    Validation posture for Rift codegen/runtime execution.
    """

    __melder_internal__ = _mrg.sentinel
    strict = "strict"
    relaxed = "relaxed"
    unsafe = "unsafe"

