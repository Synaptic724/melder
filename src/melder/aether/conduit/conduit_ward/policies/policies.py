from melder.utilities.interfaces import IPolicy


class Policies(IPolicy):
    """
    This class is a placeholder for policies related to the conduit ward.
    These strategy objects will create behaviours that objects will use for contract
    behaviours.

    Such as the following:
    - Lesser Conduit: This policy will only allow a full copy from its parent in read mode.
    """
    pass