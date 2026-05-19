from enum import Enum, auto
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class Existence(Enum):
    """
    Lifecycle mode for a spell binding.

    `Existence` answers the core runtime question for a spell binding:
    "where does instance reuse stop and where does fresh construction begin?"
    The selected member determines which ownership boundary holds created
    instances, how widely they may be shared, and which control-plane features
    participate in that sharing.

    Contract:
    - The enum does not perform caching by itself; it is a declarative mode
      interpreted by `Meld`, `Creations`, conduit sharing, and spellspace
      control flow.
    - Member docstrings describe the reuse boundary and operational semantics
      for each mode.
    - The same spell may behave very differently under different `Existence`
      values even when every other binding detail is unchanged.
    """
    __melder_internal__ = _mrg.sentinel
    unique = auto()
    """
    One instance per **Aetheric Frame**.

    By default, there is only a single Aetheric Frame, making this functionally 
    equivalent to a traditional singleton unless multiple frames are defined.

    - Behaves like a traditional singleton, but scoped to the current Aetheric Frame.
    - All conduits within the same frame share the same instance.
    - Ideal for global services within a single system (e.g., config, orchestrators).
    """

    unique_per_conduit = auto()
    """
    One instance per **conduit**.

    - Each conduit gets its own independent version of the spell.
    - Reuse only occurs within the same conduit scope.
    - Suitable for conduit-local caching or services.
    """

    many = auto()
    """
    A new instance is created **every time** the spell is cast.

    - No caching or reuse.
    - Guarantees fresh instantiation.
    - Best for stateless or short-lived services.
    """

    unique_per_conduit_cluster = auto()
    """
    Shared instance across a **conduit cluster** via contracts.

    - The instance is stored in the owning conduit creations map.
    - Cluster members access it through ConduitCluster sharing contracts.
    - There is no per-cluster instance key; sharing is contract-scoped.
    """

    unique_per_conduit_lineage = auto()
    """
    One instance per **conduit lineage tree**.

    - A lineage is a parent-child hierarchy of conduits.
    - All descendants of the same lineage share the spell instance.
    - Useful for inheritance-based sharing across dynamic creation trees.
    """

    unique_per_spell_space = auto()
    """
    One instance per **spell space**.

    - A spell space is a scoped, semaphore like zone for controlled casting.
    - Created and closed manually (e.g., "start spell space", "close spell space").
    - Optimized for temporary casting contexts where init/reset locking is needed.
    - Spell spaces are versioned and resettable.
    """

    def __str__(self) -> str:
        """
        Return the enum member name.

        This keeps logging and configuration surfaces readable without
        requiring callers to reach through `.name` directly.
        """
        return self.name
