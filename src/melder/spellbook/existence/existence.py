from enum import Enum, auto


class Existence(Enum):
    """
    Enum representing the lifecycle pattern (existence mode) of a spell within the Melder framework.

    This defines how and where instances of a spell are managed across the system. Lifecycle scopes
    range from per-frame uniqueness to fully dynamic instancing, allowing for precise memory and
    control flow behavior across Aetheric Frames and conduit networks.
    """
    unique = auto()
    """
    A **true Aether-level singleton** (one instance per Aether).

    - Intended scope: a single instance shared by every frame/conduit in the owning Aether.
    - Ownership/cleanup: managed centrally by Aether (planned wiring; current hot-path reuse
      is still per-frame via ``unique_per_aetheric_frame``).
    - Suitable for truly global services (e.g., process-wide config/telemetry) once the
      Aether registry is hooked in.
    """

    unique_per_aetheric_frame = auto()
    """
    One instance per **Aetheric Frame**.

    By default, there is only a single Aetheric Frame, making this functionally 
    equivalent to a traditional singleton unless multiple frames are defined.

    - Behaves like a traditional singleton, but scoped to the current Aetheric Frame.
    - All conduits within the same frame share the same instance (current default singleton behavior).
    - Ideal for frame-local global services (e.g., config, orchestrators) while full
      Aether-level singleton support is being wired.
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
    One instance per **conduit cluster**.

    - Users can define clusters of conduits (e.g., by function or domain).
    - All conduits in the same cluster share the instance.
    - Enables controlled sharing across related conduits.
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

    def __str__(self):
        return self.name
