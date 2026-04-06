from enum import Enum, auto
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class Policies(Enum):
    """
    Runtime policy mode for conduit-to-conduit contracting.

    These policies only matter in dynamic mode, where conduits are allowed to
    form and sever contracts at runtime. They describe how permissive the ward
    should be about outbound grants, inbound borrowing, and whole-spellbook
    visibility.

    Modes:
        - `default`:
          normal per-spell permission and whitelist rules.
        - `whitelist_all`:
          expose all local spells without requiring per-spell whitelist flags.
        - `block_all`:
          expose nothing except explicitly whitelisted spell entries.
        - `inbound_only`:
          accept inbound links/borrows but do not initiate outbound links.
        - `outbound_only`:
          initiate outbound links but reject inbound link requests.
    """
    __melder_internal__ = _mrg.sentinel
    default = auto()
    whitelist_all = auto()
    block_all = auto()
    inbound_only = auto()
    outbound_only = auto()
