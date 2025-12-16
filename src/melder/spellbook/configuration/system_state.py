from enum import Enum, auto
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class SystemState(Enum):
    """
    Enum representing the state of the system.

    This enum defines the various states that the system can be in, which
    can affect how conduits and spells behave within the system.

    States:
    - automatic 🔒: The system operates in a fully automatic mode,
        where conduits are managed without user intervention.
    - dynamic 🔓: The system allows for dynamic behavior, enabling
        custom runtime evaluations and linking of conduits.
    This state is useful for advanced behaviors like selective linking
    and custom spell access decisions.

    """
    __melder_internal__ = _mrg.sentinel
    automatic = auto()
    dynamic = auto()