from enum import Enum, auto
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class Policies(Enum):
    """
    Runtime policy mode for conduit-to-conduit contracting.

    These policies primarily matter in dynamic mode, where wards are allowed to
    form and sever contracts at runtime. They describe how permissive a ward is
    about three different control surfaces:

    - whether this conduit may initiate outbound grants
    - whether it may accept inbound borrowed lineages
    - whether normal per-spell permission and whitelist checks are enforced or
      bypassed

    The policy is therefore broader than a simple visibility flag. It changes
    whether contracts can be formed at all, whether direction is restricted,
    and whether a spell marked as blocked can still become visible under an
    explicit permissive mode.

    Modes:
        - `default`:
          normal contracting behavior. Outbound and inbound flows are both
          allowed, but every spell still has to satisfy its own permission and
          whitelist rules.
        - `whitelist_all`:
          expose local lineages without requiring per-spell whitelist flags and
          allow otherwise blocked entries to pass the normal ward gate.
        - `block_all`:
          reject dynamic contracting attempts from this ward surface entirely.
        - `inbound_only`:
          allow borrowed inbound contracts, but refuse attempts to initiate new
          outbound contracts from this ward.
        - `outbound_only`:
          allow this ward to grant outward, but reject inbound borrowing
          requests initiated by peers.
    """
    __melder_internal__ = _mrg.sentinel
    default = auto()
    whitelist_all = auto()
    block_all = auto()
    inbound_only = auto()
    outbound_only = auto()
