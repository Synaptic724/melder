from enum import Enum, auto

class ContractTypes(Enum):
    """
    Perspective label for a `Detail` stored inside one side of a `Contract`.

    The ward contract model is symmetric at the pair level, but it is not a
    single shared detail table. Each participating ward stores its own detail
    map describing which spell lineages it exposed or borrowed in that
    relationship. `ContractTypes` marks the meaning of one detail entry from
    the perspective of the ward that owns that map.

    This matters during reconciliation and rollback because the same lineage
    can appear with opposite labels across the two peers:

    - `initiated`:
      the owning ward is the source of the lineage. This detail records a
      spell the ward granted outward into the contract.

    - `received`:
      the owning ward is the borrower. This detail records a lineage that came
      from the peer and is now visible locally through the contract.

    Registration:
        MELDER KERNEL - guarded. This label is written by `ConduitWard` when it
        stores a `Detail`; callers read contract state through ward verbs
        rather than constructing these entries themselves.

    Subsystem Context:
        The PERSPECTIVE half of the detail vocabulary, paired with
        `DetailReason` (which records WHY an entry exists rather than which
        side wrote it). Both annotate a `Detail` living in one ward's own map;
        `Policies` and `Permissions` govern whether that entry could be created
        at all.

    System Context:
        The asymmetry documented above is the point: the contract is symmetric
        at the PAIR level but each ward keeps its OWN detail map, so a single
        lineage appears as `initiated` on the granting side and `received` on
        the borrowing side. Two rows, one relationship. Reconciliation and
        rollback depend on that - unwinding a contract means each ward retiring
        its own view, and a ward must never assume its label matches its peer's.
        The same split survives into the record: `ContractCrystal` stores both
        endpoints with per-side `Detail` / `IndexDetail` projections rather than
        one shared table, which is why the crystallizer's `contract_peer`
        preflight row warns when only one side of a pair is present in a bundle.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Perspective label for a `Detail` stored inside one side of a "
        "`Contract`. Melder kernel machinery: read it to understand the runtime, do not drive it "
        "directly."
    )
    initiated = auto()
    received = auto()
