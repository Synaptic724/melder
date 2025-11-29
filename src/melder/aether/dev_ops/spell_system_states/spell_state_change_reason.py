from enum import auto, Enum


class SpellStateChangeReason(Enum):
    """
    Last event that *changed* the state of a lineage.

    This is a single, coarse-grained "why did this change" tag that is easy to
    surface in TOON snapshots and incidents. Detailed context still lives in
    the SpellStateFlag set and Incident details.
    """
    new_lineage = auto()
    register_or_rebind = auto()
    structure_changed = auto()
    dependencies_changed = auto()
    dependency_changed = auto()
    contract_violation = auto()
    mutation_promoted = auto()
    mutation_rolled_back = auto()
    explicit_mark = auto()
    other = auto()   # generic catch-all; use Incident.details to explain