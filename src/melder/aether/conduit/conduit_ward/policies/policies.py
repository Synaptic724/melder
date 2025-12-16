from enum import Enum, auto
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class Policies(Enum):
    """
    Access policies (evaluated only when system_state is dynamic):

    - default: normal per-spell rules/whitelist metadata.
    - whitelist_all: expose all local spells regardless of per-spell whitelist flags.
    - block_all: expose only spells explicitly marked with `meta["whitelist"] = True`.
    - inbound_only: accept inbound links/borrows but do not initiate outbound links.
    - outbound_only: initiate outbound links but reject inbound link requests.
    """
    __melder_internal__ = _mrg.sentinel
    default = auto()
    whitelist_all = auto()
    block_all = auto()
    inbound_only = auto()
    outbound_only = auto()
