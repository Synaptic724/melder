import threading
import ulid
# Melder Imports
from melder.utilities.general_base.cleanable import Cleanable


class SpellKey(Cleanable):
    """
    A stable dictionary key that points to a mutable version ID.

    Design:
    This class solves the "mutable dictionary key" problem. It provides a
    stable, hashable identity via an immutable ULID, while simultaneously
    tracking a mutable "current version" pointer (e.g., a SHA256 commit ID).

    - Hashing and equality are based *only* on the immutable ULID.
    - The version pointer can be safely updated (mutated) in a thread-safe
      manner without breaking its location in a dictionary.
    """

    __slots__ = (
        "_id",          # The immutable ULID. Used for hashing and equality.
        "_current_id",  # The mutable pointer to the active version (e.g., a SHA256).
        "_lock",        # RLock for thread-safe reads/writes to _current_id.
        "_cleaned",     # Flag for Cleanable interface.
    )

    def __init__(self, initial_id: str):
        """
        Initializes the SpellKey with its permanent identity and initial version.

        Args:
            initial_id (str): The SHA256 commit ID or version string
                              this key initially points to.
        """
        super().__init__()
        # The permanent, hashable identity for this key.
        self._id: str = str(ulid.ULID())

        # The dynamic pointer to the version, which can be updated.
        self._current_id: str = initial_id

        self._lock = threading.RLock()

    # ------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------
    def cleanup(self) -> None:
        """
        Releases resources and marks the key as cleaned.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            # Nullify the pointer and release the lock object.
            self._cleaned = True
            self._current_id = None
            self._lock = None

    # ------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------
    @property
    def current(self) -> str:
        """
        Gets the currently active version ID (e.g., SHA256) this key points to.

        Returns:
            str: The current version ID, or None if cleaned.
        """
        self.check_cleaned()
        with self._lock:
            return self._current_id

    def update(self, new_id: str) -> None:
        """
        Atomically updates the pointer to a new version ID.

        This operation is thread-safe and does not affect the
        object's hash or its location in a dictionary.

        Args:
            new_id (str): The new SHA256 or version ID.
        """
        self.check_cleaned()
        with self._lock:
            self._current_id = new_id

    @property
    def id(self) -> str:
        """
        Returns the immutable, unique ULID that serves as the
        object's stable identity.
        """
        return self._id

    # ------------------------------------------------------------
    # Dict-safety (Hashing and Equality)
    # ------------------------------------------------------------
    def __hash__(self) -> int:
        """
        Generates the hash based *only* on the immutable ULID.

        This ensures the hash is stable, even if _current_id changes,
        making it safe for use as a dictionary key.
        """
        return hash(self._id)

    def __eq__(self, other) -> bool:
        """
        Compares two SpellKeys based *only* on their immutable ULID.

        This guarantees that key equality is stable and not affected
        by version changes.
        """
        return isinstance(other, SpellKey) and self._id == other._id

    # ------------------------------------------------------------
    # Debug
    # ------------------------------------------------------------
    def __repr__(self) -> str:
        """
        Provides a developer-friendly representation of the key's state.
        """
        self.check_cleaned()

        # We lock here to ensure a consistent snapshot for repr
        with self._lock:
            return f"<SpellKey id={self._id} current={self._current_id}>"


    def __enter__(self) -> 'SpellKey':
        """
        Context manager entry. Returns self.
        """
        self.check_cleaned()
        self._lock.acquire()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """
        Context manager exit. Releases the lock.
        """
        self._lock.release()