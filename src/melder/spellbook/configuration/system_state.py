#    Copyright [2025] [Mark Thomas Geleta]
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0

from enum import Enum, auto


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
    automatic = auto()
    dynamic = auto()