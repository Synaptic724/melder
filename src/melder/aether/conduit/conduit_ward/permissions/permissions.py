from enum import StrEnum
from typing import Optional

class Permissions(StrEnum):
    """
    Capability ceiling for a spell in ward-local and contracted views.

    `ConduitWard` uses this enum in two related places:

    - on the spell itself, as the local maximum capability the owning conduit
      is willing to expose
    - on each contract detail, as the capability actually granted to a peer for
      that spell

    The members describe how much downstream behavior they permit, and the
    ward logic deliberately never escalates a contracted spell beyond the
    spell's own local permission. Values are exact member-name strings; the
    historical numeric values 1-3 remain readable by value and in old pickles.

    - `read`:
      the spell may be resolved and inspected through a contract, but it
      cannot be used as a creation-capable dependency when propagating work
      into another conduit.

    - `create`:
      the spell may participate in creation-capable dependency resolution and
      therefore also implies ordinary read/resolve access.

    - `block`:
      the spell should not be contractable in normal flows. The ward treats
      this as a hard stop unless a broader override policy such as
      `Policies.whitelist_all` explicitly allows exposure.

    Registration:
        MELDER KERNEL, USER-FACING as a value. A user passes `Permissions.create` into
        `Spellbook.bind(...)` by value; only binding the enum CLASS itself is refused.

    Subsystem Context:
        The PER-SPELL half of the ward vocabulary, paired with `Policies`
        (the ward-level directional gate). The non-escalation rule stated above
        is the load-bearing invariant: a contracted spell is never granted
        MORE than the spell's own local permission, so a peer can only ever
        receive a capability the owner already holds. `ContractTypes` labels
        which side of the relationship a `Detail` was written from, and
        `DetailReason` records whether the entry was a root grant or a
        transitive dependency pull.

    System Context:
        The `read` / `create` split is not about inspection versus mutation -
        it is about DEPENDENCY PROPAGATION. `read` resolves and inspects, but
        the spell cannot act as a creation-capable dependency when work
        propagates into another conduit; `create` admits it into that
        resolution path and implies read. That is why cluster auto-sharing
        defaults to the spell's own `permissions` with a `create` fallback:
        a cluster exists precisely so members can construct from each other's
        spells, and a `read`-only default would make the cluster inert.

    AGENT_ACCESS: public

    AGENT_PURPOSE:
        access: public. Capability ceiling for a spell: read (resolve/inspect only), create
        (creation-capable, implies read), block (hard stop). Pass to Spellbook.bind(...). A
        contract never grants more than the spell's own permission.
    """
    read = "read"   # Allows read/resolve access only.
    create = "create" # Allows creation-capable use and implies read.
    block = "block"  # Blocks sharing/contracting in normal flows.

    @classmethod
    def _missing_(cls, value: object) -> Optional[Permissions]:
        """
        Resolve a historical numeric permission to its original member.

        Current names use ordinary enum lookup. Values equal to the old
        integer values remain readable; unknown or unhashable inputs return
        None so enum construction raises its normal ValueError.
        """
        legacy_values: dict[object, Permissions] = {
            1: cls.read,
            2: cls.create,
            3: cls.block,
        }
        try:
            return legacy_values.get(value)
        except TypeError:
            return None
