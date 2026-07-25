from enum import Enum, auto

class Permissions(Enum):
    """
    Capability ceiling for a spell lineage in ward-local and contracted views.

    `ConduitWard` uses this enum in two related places:

    - on the spell itself, as the local maximum capability the owning conduit
      is willing to expose
    - on each contract detail, as the capability actually granted to a peer for
      that lineage

    The values are ordered by how much downstream behavior they permit, and the
    ward logic deliberately never escalates a contracted lineage beyond the
    spell's own local permission.

    - `read`:
      the lineage may be resolved and inspected through a contract, but it
      cannot be used as a creation-capable dependency when propagating work
      into another conduit.

    - `create`:
      the lineage may participate in creation-capable dependency resolution and
      therefore also implies ordinary read/resolve access.

    - `block`:
      the lineage should not be contractable in normal flows. The ward treats
      this as a hard stop unless a broader override policy such as
      `Policies.whitelist_all` explicitly allows exposure.

    Registration:
        MELDER KERNEL - guarded, but USER-FACING as a value. A user passes
        `Permissions.create` into `Spellbook.bind(...)` by value; the sentinel
        only prevents binding the enum CLASS itself as a spell.

    Subsystem Context:
        The PER-LINEAGE half of the ward vocabulary, paired with `Policies`
        (the ward-level directional gate). The non-escalation rule stated above
        is the load-bearing invariant: a contracted lineage is never granted
        MORE than the spell's own local permission, so a peer can only ever
        receive a capability the owner already holds. `ContractTypes` labels
        which side of the relationship a `Detail` was written from, and
        `DetailReason` records whether the entry was a root grant or a
        transitive dependency pull.

    System Context:
        The `read` / `create` split is not about inspection versus mutation -
        it is about DEPENDENCY PROPAGATION. `read` resolves and inspects, but
        the lineage cannot act as a creation-capable dependency when work
        propagates into another conduit; `create` admits it into that
        resolution path and implies read. That is why cluster auto-sharing
        defaults to the spell's own `permissions` with a `create` fallback:
        a cluster exists precisely so members can construct from each other's
        lineages, and a `read`-only default would make the cluster inert.
    """
    __ast_helper_access__: str = "public"
    __agent_purpose__: str = (
        "access: public. Capability ceiling for a lineage: read (resolve/inspect only), create "
        "(creation-capable, implies read), block (hard stop). Pass to Spellbook.bind(...). A contract "
        "never grants more than the spell's own permission."
    )
    read = auto()   # Allows read/resolve access only.
    create = auto() # Allows creation-capable use and implies read.
    block = auto()  # Blocks sharing/contracting in normal flows.
