from enum import Enum
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg



class RiftSpaceType(Enum):
    """
    Internal

    Supported top-level room types for a Rift.

    Members:
        static:
            The Rift exposes the lower-risk room surface with live-only
            spell-facing behavior and no runtime topology mutation.
        capability:
            The Rift exposes broad manual runtime and object access without
            codegen while still honoring lower Melder frame truth.
        codegen:
            The Rift exposes the richer room surface intended for mutable local
            state and later codegen-oriented differentiation. It currently
            shares the same broad manual-runtime posture as capability.
        dynamic:
            Legacy alias for `codegen`. Retained temporarily so older AR
            configuration inputs can still normalize during the room rename.
    """

    __melder_internal__ = _mrg.sentinel
    static = "static"
    capability = "capability"
    codegen = "codegen"
    dynamic = codegen
