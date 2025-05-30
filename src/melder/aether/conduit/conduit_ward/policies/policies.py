from enum import Enum, auto

class Policies(Enum):
    """
    Defines conduit policy behaviors within the conduit ward system.

    These policies determine how a conduit handles spell access, inheritance,
    and enforcement of permissions.

    Available Policies:

    - automatic: Delegates access resolution to the parent conduit or source link.
                 Used for reflective/spawned conduits that inherit behavior.

    - dynamic: Enables runtime decision-making; policy evaluation may be
               delegated to external logic or context-aware resolution.

    - whitelist_all: Allows all spells without checking the spell's 'whitelist' flag.

    - block_all: Blocks all spell access unless a spell explicitly opts into access
                 via 'meta["whitelist"] = True'.

    - delegate: Allows a lesser conduit to act as a delegate for the parent conduit, technically this would just inherit the parents policy by default so delegate should just point to the parent.
    this is specifically for dynamic system mode.
    """
    automatic = auto()
    dynamic = auto()
    whitelist_all = auto()
    block_all = auto()
    delegate = auto()
