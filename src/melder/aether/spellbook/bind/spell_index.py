import threading
from types import TracebackType
from typing import TYPE_CHECKING, Optional, Dict, Tuple, ClassVar

# Melder Imports
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.ulid_factory import new_ulid
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spellbook import Spellbook

class SpellIndex(Cleanable):
    """
    A stable SpellIndex identity that points to a mutable selected-spell id and
    holds the set of member spell ids that belong to this index.

    Design:
    This class solves the "mutable dictionary key" problem. It provides a
    stable, hashable SpellIndex identity via an immutable ULID, while tracking
    both a mutable selected-spell pointer (the SHA256 id of the active spell)
    and the set of member spell ids the index contains.

    - Hashing and equality are based *only* on the immutable ULID.
    - The selected-spell pointer can be safely updated (mutated) in a thread-safe
      manner without breaking its location in a dictionary.
    - The index can hold multiple member spell ids; `selected_spell_id` is the
      one currently active. The index organizes its member ids; the spell_id
      resolves. Lookup-map propagation to owning/contracted Spellbooks is the
      Spellbook's responsibility (the notch seam), not the index's.
    """
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = (
        "_id",          # The immutable ULID. Used for hashing and equality.
        "_selected_spell_id",  # The active spell's id (a SHA256).
        "_lock",        # RLock for thread-safe reads/writes.
        "_cleaned",     # Flag for Cleanable interface.
        "_spells_in_index",    # Set of all member spell ids in this index.
    )

    def __init__(self, initial_id: str):
        """
        Initialize the SpellIndex with its permanent identity and initial member.

        Purpose:
            Provide a stable, hashable SpellIndex identity with a mutable
            selected-spell pointer and the set of member spell ids.

        Contract:
            - The ULID identity never changes.
            - The selected-spell pointer is mutable and guarded by the lock.
            - The member set starts with the initial spell id.

        Args:
            initial_id (str):
                The SHA256 spell id this index initially selects and contains.

        Threading:
            - Initializes the internal RLock used for all mutations.
        """
        super().__init__()
        # The permanent, hashable identity for this key.
        self._id: str = new_ulid()
        self._lock: threading.RLock = threading.RLock()
        # The active spell pointer, which can be updated.
        self._selected_spell_id: str = initial_id
        # The set of member spell ids this index contains.
        self._spells_in_index: set = {initial_id}

    # ------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------
    def cleanup(self) -> None:
        """
        Release the member set and pointer and mark this index as cleaned.

        Contract:
            - Idempotent and lock-guarded.
            - Clears and drops the member set and the selected-spell pointer.
            - Leaves future callers to fail through `check_cleaned()`.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._spells_in_index.clear()
            del self._spells_in_index
            del self._selected_spell_id

    # ------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------
    @property
    def selected_spell_id(self) -> str:
        """
        Return the active spell's id for this SpellIndex.

        Returns:
            str: The active spell's id.

        Contract:
            - Returns the live selected-spell pointer, not a historical value.
            - Lock-free read: the pointer is one attribute holding one string
              reference, so a reader observes either the previous or the new
              id, never a torn value. `update(...)` still serializes writers
              under the instance lock.

        Threading:
            - Safe on free-threaded builds; attribute reference loads are
              atomic. This property is the hottest fingerprint read in the
              compiler phases (thousands of reads per conjure), and the
              per-read RLock acquire/release dominated its cost on nogil.
        """
        return self._selected_spell_id

    def update(self, new_id: str) -> None:
        """
        Set the active spell id and add it to the index's member set.

        This is a pure index-side repoint: it changes which member is active
        and records `new_id` in the member set, and nothing else. Owning and
        contracted Spellbook lookup-map propagation is the Spellbook's
        responsibility (the notch seam), not the index's. Thread-safe; does not
        affect the object's hash or its dictionary location.

        Args:
            new_id (str): The new SHA256 spell id to select and add as a member.
        """
        self.check_cleaned()
        with self._lock:
            self._selected_spell_id = new_id
            self._spells_in_index.add(new_id)

    def add_member(self, spell_id: str) -> None:
        """
        Add `spell_id` to this index's member set without selecting it.

        Used to stage an inactive candidate (`Spellbook.bind_inactive`): the id
        becomes a member visible to `spells_in_index()` / `has_spell()`, but the
        active `selected_spell_id` is left unchanged. Promotion to active happens
        later via `notch`.

        Args:
            spell_id (str): The candidate member spell id to record.
        """
        self.check_cleaned()
        with self._lock:
            self._spells_in_index.add(spell_id)

    def remove_member(self, spell_id: str) -> None:
        """
        Remove `spell_id` from this index's member set.

        Idempotent; does not touch the selected pointer. Used when a member is
        moved out of this index (`add_to_spell_index`).

        Args:
            spell_id (str): The member spell id to remove.
        """
        self.check_cleaned()
        with self._lock:
            self._spells_in_index.discard(spell_id)

    def spells_in_index(self) -> set:
        """
        Return a snapshot of every member spell id in this index.

        Returns:
            set: A detached copy of the member spell ids.

        Contract:
            - Includes the initial spell id and every id added via `update(...)`.
        """
        self.check_cleaned()
        with self._lock:
            return set(self._spells_in_index)

    def has_spell(self, spell_id: str) -> bool:
        """
        Return whether `spell_id` is a member of this index.

        Args:
            spell_id (str): The spell id to check.

        Returns:
            bool: True if `spell_id` is in the member set, False otherwise.
        """
        self.check_cleaned()
        with self._lock:
            return spell_id in self._spells_in_index

    @property
    def id(self) -> str:
        """
        Return the immutable ULID that defines this index's stable identity.

        Contract:
            - This value never changes for the lifetime of the index.
            - Hashing and equality are derived from this id, not from the
              mutable selected-spell pointer.
        """
        return self._id

    # ------------------------------------------------------------
    # Dict-safety (Hashing and Equality)
    # ------------------------------------------------------------
    def __hash__(self) -> int:
        """
        Hash this index by immutable SpellIndex identity only.

        This ensures the hash is stable, even if _selected_spell_id changes,
        making it safe for use as a dictionary key.
        """
        return hash(self._id)

    def __eq__(self, other: object) -> bool:
        """
        Compare two `SpellIndex` objects by immutable SpellIndex identity only.

        This guarantees that key equality is stable and not affected
        by selected-spell changes.
        """
        return isinstance(other, SpellIndex) and self._id == other._id

    # ------------------------------------------------------------
    # Debug
    # ------------------------------------------------------------
    def __repr__(self) -> str:
        """
        Return a developer-facing snapshot of identity and selected spell.
        """
        self.check_cleaned()
        with self._lock:
            return f"<SpellIndex id={self._id} current={self._selected_spell_id}>"

    def __enter__(self) -> "SpellIndex":
        """
        Acquire the internal lock and return this index.

        Contract:
            - Intended for rare manual critical sections around multiple reads
              on the same `SpellIndex`.
            - Must be paired with `__exit__` to release the lock.
        """
        self.check_cleaned()
        self._lock.acquire()
        return self

    def __exit__(
            self,
            exc_type: type[BaseException] | None,
            exc_value: BaseException | None,
            traceback: TracebackType | None,
    ) -> None:
        """
        Release the internal lock acquired by `__enter__`.
        """
        self._lock.release()
