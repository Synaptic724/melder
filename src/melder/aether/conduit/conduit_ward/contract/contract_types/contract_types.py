from enum import Enum, auto
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

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
    """
    __melder_internal__ = _mrg.sentinel
    initiated = auto()
    received = auto()
