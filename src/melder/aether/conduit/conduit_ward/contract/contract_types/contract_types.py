from enum import Enum, auto
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class ContractTypes(Enum):
    """
    Direction label for one `Detail` inside a symmetric contract.

    A `Contract` is symmetric, but each ward keeps its own detail map. This
    enum tells you how to interpret one detail from the perspective of the ward
    that owns that map:

    - `initiated`:
      this ward granted one of its own spell lineages outward to the peer.

    - `received`:
      this ward is the borrower and the detail represents a lineage granted by
      the peer.
    """
    __melder_internal__ = _mrg.sentinel
    initiated = auto()
    received = auto()
