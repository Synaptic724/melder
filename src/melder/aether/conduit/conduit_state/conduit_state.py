from enum import Enum, auto


class ConduitState(Enum):
    """
    Enum representing the state of a Conduit.
    """
    normal = auto()
    lesser = auto()
    sealed = auto()