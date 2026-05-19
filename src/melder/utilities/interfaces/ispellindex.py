from types import TracebackType
from typing import Any, Dict, Optional, Protocol, Set, Tuple, runtime_checkable
from melder.utilities.interfaces.icleanable import ICleanable

@runtime_checkable
class ISpellIndex(ICleanable, Protocol):
    """
    Interface for a **SpellIndex**: a stable, hashable dictionary key that
    points to a mutable version ID (e.g., a SHA256 commit or spell version).

    Design:
        * Hashing and equality are based **only** on an immutable ULID.
        * The "current" version pointer is mutable and thread-safe.
        * The object is safe to use as a dictionary key even while the
          version pointer changes over time.
        * Tracks the full set of versions via an internal version set.

    Typical usage:
        * As a key into spell registries:
              Dict[SpellIndex, ISpell]
        * As a stable SpellIndex handle for spell mutation/versioning.
        * As a synchronization primitive when multiple threads need to
          reason about "which version is active" without breaking key
          identity in maps.
    """

    # ------------------------------------------------------------------
    # Core backing fields (shape only; concrete type lives in impl)
    # ------------------------------------------------------------------
    _id: str
    _current_id: Optional[str]
    _lock: Any
    _cleaned: bool
    _versions: Optional[Set[str]]
    _owner_spellbook: Optional[object]
    _owner_spell: Optional[object]
    _owner_conduit_id: Optional[str]
    _contracted_spellbooks: Dict[Tuple[object, str], object]

    # ------------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------------
    @property
    def current(self) -> Optional[str]:
        """
        Gets the currently active version ID (e.g., SHA256) this index points to.

        Returns:
            Optional[str]:
                The current version ID, or ``None`` if the index has
                been cleaned.
        """
        ...

    def update(self, new_id: str) -> None:
        """
        Atomically updates the pointer to a new version ID.

        This operation is thread-safe and does **not** affect the
        object's hash or its location in any dictionary.

        Args:
            new_id:
                The new version ID (e.g., SHA256 commit ID) to point to.
        """
        ...

    def get_all_versions(self) -> Set[str]:
        """
        Retrieves all version IDs that this index has ever pointed to.

        Returns:
            Set[str]:
                A copy of the internal set of all version IDs seen for
                this SpellIndex.
        """
        ...

    def has_version(self, version_id: str) -> bool:
        """
        Checks whether this index has ever pointed to the specified
        version ID.

        Args:
            version_id:
                The version ID to check for.

        Returns:
            bool:
                ``True`` if the version ID is present in the SpellIndex
                set, ``False`` otherwise.
        """
        ...

    @property
    def id(self) -> str:
        """
        Returns the immutable, unique ULID that serves as the stable
        identity for this index.

        This is the only value used for hashing and equality.
        """
        ...

    # ------------------------------------------------------------------
    # Dict-safety / identity semantics
    # ------------------------------------------------------------------
    def __hash__(self) -> int:
        """
        Produces a hash based **only** on the immutable ULID.

        This guarantees a stable hash even when the current version
        pointer changes, making the object safe as a dictionary key.
        """
        ...

    def __eq__(self, other: object) -> bool:
        """
        Compares two SpellIndex instances based solely on their
        immutable ULIDs.

        Args:
            other:
                Another object to compare to.

        Returns:
            bool:
                ``True`` if ``other`` is a SpellIndex/ISpellIndex with
                the same ULID; otherwise ``False``.
        """
        ...

    def __repr__(self) -> str:
        """
        Returns a developer-friendly representation of the index state,
        typically including the ULID and current version ID.
        """
        ...

    # ------------------------------------------------------------------
    # Context manager support
    # ------------------------------------------------------------------
    def __enter__(self) -> "ISpellIndex":
        """
        Context manager entry.

        Typical behavior in the concrete implementation:
            * Performs a cleaned check.
            * Acquires the internal lock.
            * Returns ``self``.
        """
        ...

    def __exit__(
            self,
            exc_type: type[BaseException] | None,
            exc_value: BaseException | None,
            traceback: TracebackType | None,
    ) -> None:
        """
        Context manager exit.

        Typical behavior in the concrete implementation:
            * Releases the internal lock regardless of outcome.
        """
        ...

    def _attach_owner(self, spellbook: Any, spell: object) -> None:
        """
        Attach the owning spellbook and spell to this lineage.
        """
        ...

    def _attach_contracted(
            self,
            spellbook: Any,
            conduit_id: str,
            spell: object,
    ) -> None:
        """
        Attach one contracted spellbook/conduit view to this lineage.
        """
        ...

    def _detach_contracted(self, spellbook: Any, conduit_id: str) -> None:
        """
        Remove one contracted spellbook/conduit attachment from this lineage.
        """
        ...

    def _set_owner_conduit_id(self, conduit_id: str) -> None:
        """
        Record the owning conduit identifier for this lineage.
        """
        ...
