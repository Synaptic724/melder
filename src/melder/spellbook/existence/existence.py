from enum import Enum, auto

class Existence(Enum):
    """
    Enum representing the existence/lifecycle pattern of a service in Melder.
    """
    unique = auto()               # Single instance across all of Aether
    unique_per_conduit = auto()    # One instance per conduit
    many = auto()                  # New instance every time
    dynamic = auto()               # Instance that can mutate/upgrade at runtime

    def __str__(self):
        return self.name
