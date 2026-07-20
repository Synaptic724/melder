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

    Registration:
        MELDER KERNEL - guarded, but USER-FACING as a value. Guarding and using
        are orthogonal here: a user passes `Policies.default` into
        `Spellbook.conjure(...)` by value all the time; the sentinel only stops
        someone binding the enum CLASS itself as a spell, which is never a
        meaningful thing to do.

    Subsystem Context:
        One of the four ward vocabularies. This one is the WARD-LEVEL gate
        (may a contract form at all, and in which direction), while
        `Permissions` is the PER-LINEAGE ceiling (what a peer may do with a
        spell once a contract exists). `ContractTypes` then labels each stored
        `Detail` by perspective and `DetailReason` records why it exists. A
        contract only grants when the ward policy admits the direction AND the
        lineage's own permission allows the capability.

    System Context:
        Policy is only half-live: these modes "primarily matter in dynamic
        mode" because contracting itself is gated on it. A `dynamic=False`
        conjure admits ONLY `Policies.default`, and `Conduit.link(...)` /
        `sever_link(...)` raise outside dynamic mode - so in an automatic-mode
        world the other four values are unreachable rather than merely unused.
        `whitelist_all` is the one mode that can OVERRIDE a per-spell decision:
        it lets a lineage marked `Permissions.block` pass the ward gate. That
        makes it the widest authority in the conduit layer and the value to
        reach for last, not first.
    """
    __ast_helper_access__: str = "public"
    __agent_purpose__: str = (
        "access: public. Ward contracting mode: default, whitelist_all, block_all, inbound_only, "
        "outbound_only. Pass to conjure(...). Only default is legal when dynamic=False. whitelist_all "
        "is the one mode that can override a per-spell block."
    )
    __melder_internal__ = _mrg.sentinel
    default = auto()
    whitelist_all = auto()
    block_all = auto()
    inbound_only = auto()
    outbound_only = auto()
