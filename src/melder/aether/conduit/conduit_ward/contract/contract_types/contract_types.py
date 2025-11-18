from enum import Enum, auto


class ContractTypes(Enum):
    """
    Describes the role of a Detail within a Contract from the
    perspective of the ward that OWNS the Detail map.

    - initiated: this ward is the one that initiated the grant
      (it is granting its own spells out to a peer).

    - received: this ward is the one that received the grant
      (it is the borrower of spells from a peer).
    """

    initiated = auto()
    received = auto()
