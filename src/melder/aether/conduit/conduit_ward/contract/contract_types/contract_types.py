from enum import Enum, auto
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class ContractTypes(Enum):
    """
    Describes the role of a Detail within a Contract from the
    perspective of the ward that OWNS the Detail map.

    - initiated: this ward is the one that initiated the grant
      (it is granting its own spells out to a peer).

    - received: this ward is the one that received the grant
      (it is the borrower of spells from a peer).
    """
    __melder_internal__ = _mrg.sentinel
    initiated = auto()
    received = auto()
