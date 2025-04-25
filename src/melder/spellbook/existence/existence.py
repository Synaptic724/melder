from enum import Enum, auto

class Existence(Enum):
    """
    Enum representing the existence/lifecycle pattern of a service in Melder.
    """
    unique = auto()               # Single instance across all of Aether
    unique_per_conduit = auto()    # One instance per conduit
    many = auto()                  # New instance every time
    unique_per_conduit_cluster = auto()  # One instance per conduit cluster, users can cluster conduits into their own desired groups owned by the aether
    unique_per_conduit_lineage = auto()  # One instance per conduit lineage, a lineage is a tree of conduits from child to parent
#    dynamic = auto()               # Instance that can mutate/upgrade at runtime   // Not really sure what usecase we got here for this

    def __str__(self):
        return self.name
