from enum import Enum, auto
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class SystemState(Enum):
    """
    High-level runtime posture for a spellbook/system.

    `SystemState` selects how aggressively the runtime is allowed to perform
    dynamic behaviors.

    Contract:
    - `automatic` is the safer default posture for normal managed runtime
      behavior.
    - `dynamic` enables the more permissive runtime posture required by
      AI-native and other advanced dynamic behaviors.
    - Configuration validation may enforce semantic relationships between this
      enum and other flags such as `ai_native_enabled`.

    States:
    - automatic: managed/default runtime posture
    - dynamic: advanced dynamic runtime posture
    """
    __melder_internal__ = _mrg.sentinel
    automatic = auto()
    dynamic = auto()
