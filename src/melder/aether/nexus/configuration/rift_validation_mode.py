from enum import Enum

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg


class RiftValidationMode(Enum):
    """
    Internal

    Validation posture for Rift codegen/runtime execution.

    Members:
        strict:
            Apply the full validation posture and fail on contract violations.
        relaxed:
            Apply a lighter validation posture that tolerates some non-fatal
            issues while still checking core contracts.
        unsafe:
            Minimize validation barriers for trusted/internal flows that need
            maximum freedom over safety checks.
    """

    __melder_internal__ = _mrg.sentinel
    strict = "strict"
    relaxed = "relaxed"
    unsafe = "unsafe"
