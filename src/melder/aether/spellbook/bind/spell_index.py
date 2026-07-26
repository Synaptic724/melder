import threading
from types import TracebackType
from typing import TYPE_CHECKING, Optional, Dict, Tuple, ClassVar

# Melder Imports
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.ulid_factory import new_ulid
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

    Contract:
        - Hash and equality derive ONLY from the immutable ULID.
        - `selected_spell_id` is mutable and thread-safe to update.
        - The index owns its member spell ids; it does NOT own lookup-map
          propagation to owning or contracted Spellbooks - that is the
          Spellbook's notch seam.

    Threading:
        The selected-spell pointer is updated under lock, so a repoint is safe
        while the index sits in a dictionary.

    Registration:
        MELDER KERNEL - guarded. Created by `Bind`; users receive indexes rather
        than constructing them.

    Subsystem Context:
        The stable identity spells are organized under. `Spell` is one version;
        the index is the lineage. Version HISTORY belongs to MutationResearch,
        not here.

    System Context:
        The design note names the real problem this solves: the MUTABLE
        DICTIONARY KEY. Identity must stay stable so the object keeps its place
        in every map that holds it, while the thing it POINTS AT must be free to
        change. Hashing on the immutable ULID and mutating only the pointer is
        what makes a notch possible at all - repointing an index cannot corrupt
        the maps it lives in.
        That split ripples outward. Contracts carry BOTH a `Detail` (a captured
        spell_id, the answer at grant time) and an `IndexDetail` (a subscription
        to this index, following the head), so a notch updates every borrower
        without renegotiating a single contract. The crystallizer records index
        MEMBERSHIP as its own twin (`SpellIndexCrystal`) for the same reason -
        membership is lineage truth, distinct from any one spell's custody.
        The explicit non-ownership of lookup-map propagation is the boundary
        that keeps this class small: the index organizes ids, the spell_id
        resolves, and the Spellbook is what republishes lookups on a notch.

    AGENT_ACCESS: public

    AGENT_PURPOSE:
        access: public. The stable lineage identity (immutable ULID) pointing at a mutable
        selected spell. Hash/equality use only the ULID, so a notch can repoint the active
        member without breaking any map. Version history belongs to MutationResearch.
    """
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

        Returns:
            None.
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

        Returns:
            None.
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

        Contract:
            - SELECTS a new current spell id AND adds it to the member set, so
              selection always implies membership.
            - DOES NOT RETIRE THE PREVIOUS ID. The superseded version stays a
              MEMBER, which is exactly why `Spellbook.find_spell_by_id` still
              resolves a parked id to the live spell. The member set is the
              lineage; the selected id is only the current head.

        Threading:
            Reads and writes under `self._lock`, so the result is a coherent
            snapshot rather than a torn read.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the object has been cleaned.

        Returns:
            None.
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

        Contract:
            - Adds to the lineage WITHOUT changing the selected id, so it grows the
              version set without promoting anything.
            - Set semantics: re-adding an existing id is a silent no-op.

        Threading:
            Reads and writes under `self._lock`, so the result is a coherent
            snapshot rather than a torn read.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the object has been cleaned.

        Returns:
            None.
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

        Contract:
            - Uses `discard`, so removing an id that was never a member is a SILENT
              NO-OP rather than an error. Absence of an exception is not proof the
              id was present.
            - CAN REMOVE THE CURRENTLY SELECTED ID. Nothing here re-points the
              selection, so afterwards `selected_spell_id` may name an id that is no
              longer a member. Callers retiring the head must select a new one.

        Threading:
            Reads and writes under `self._lock`, so the result is a coherent
            snapshot rather than a torn read.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the object has been cleaned.

        Returns:
            None.
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

        Contract:
            - Tests MEMBERSHIP OF THE LINEAGE, not equality with the selected id, so a
              superseded or parked version still answers True. This is the check
              spellbook lookups rely on to resolve old ids to the live spell.

        Threading:
            Reads and writes under `self._lock`, so the result is a coherent
            snapshot rather than a torn read.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the object has been cleaned.

        Returns:
            bool: True if `spell_id` is in the member set, False otherwise.
        """
        self.check_cleaned()
        with self._lock:
            return spell_id in self._spells_in_index

    def is_empty(self) -> bool:
        """
        Return whether this index has no members.

        O(1): tests the live member set directly without copying it.

        Contract:
            - Reports that the MEMBER SET is empty. It says nothing about the selected
              id, which member removal does not clear - an index can be empty and
              still carry a stale selected id.

        Threading:
            Reads and writes under `self._lock`, so the result is a coherent
            snapshot rather than a torn read.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the object has been cleaned.

        Returns:
            bool: True if the member set is empty.
        """
        self.check_cleaned()
        with self._lock:
            return not self._spells_in_index

    def is_sole_member(self, spell_id: str) -> bool:
        """
        Return whether `spell_id` is this index's only member.

        O(1): a length test plus a membership test on the live set; no copy and
        no set construction (unlike `spells_in_index() == {spell_id}`).

        Args:
            spell_id (str): The spell id to test as the sole member.

        Contract:
            - True only when the member set has exactly one entry AND that entry is the
              supplied id; a different lone member returns False rather than raising.
            - The usual "is this the last version" test before a destructive step.

        Threading:
            Reads and writes under `self._lock`, so the result is a coherent
            snapshot rather than a torn read.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the object has been cleaned.

        Returns:
            bool: True iff the member set is exactly {spell_id}.
        """
        self.check_cleaned()
        with self._lock:
            members = self._spells_in_index
            return len(members) == 1 and spell_id in members

    @property
    def id(self) -> str:
        """
        Return the immutable ULID that defines this index's stable identity.

        Contract:
            - This value never changes for the lifetime of the index.
            - Hashing and equality are derived from this id, not from the
              mutable selected-spell pointer.

        Returns:
            str: The immutable ULID. Hash and equality derive from this alone, which
                is what lets the selected spell move without breaking dictionary placement.
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
        Contract:
            - Hashes on index IDENTITY ONLY, never on contents, so the hash is stable
              while membership changes. That is what allows a live index to be a dict
              key while its lineage evolves.
            - DELIBERATELY NOT `check_cleaned()` GUARDED, so a cleaned index stays
              hashable and can still be removed from the collections holding it.

        Threading:
            Reads a write-once slot without taking the lock; safe from any thread.

        Lifecycle / Cleanup:
            Remains valid after cleanup, by design.

        """
        return hash(self._id)

    def __eq__(self, other: object) -> bool:
        """
        Compare two `SpellIndex` objects by immutable SpellIndex identity only.

        This guarantees that key equality is stable and not affected
        by selected-spell changes.
        Contract:
            - Compares index IDENTITY ONLY. Two indexes with identical membership are
              NOT equal, and an index stays equal to itself across every mutation.
            - Returns False for non-`SpellIndex` operands rather than raising.
            - Not `check_cleaned()` guarded, matching `__hash__` so the pair stays
              consistent for collection removal after cleanup.

        Threading:
            Reads a write-once slot without taking the lock; safe from any thread.

        Lifecycle / Cleanup:
            Remains valid after cleanup, by design.

        """
        return isinstance(other, SpellIndex) and self._id == other._id

    # ------------------------------------------------------------
    # Debug
    # ------------------------------------------------------------
    def __repr__(self) -> str:
        """
        Return a developer-facing snapshot of identity and selected spell.
        Contract:
            - GUARDED BY `check_cleaned()` AND TAKES THE LOCK, which is unusual for a
              repr: printing or logging a CLEANED index RAISES rather than degrading
              to a placeholder. Take care with debugger watches and log statements
              that may run after teardown.
            - Shows identity and the currently selected id, not the membership set.

        Threading:
            Reads and writes under `self._lock`, so the result is a coherent
            snapshot rather than a torn read.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the object has been cleaned.

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
        Contract:
            - Releases unconditionally, including when the block raised. Exception
              arguments are accepted and IGNORED, and the falsy return means no
              exception is suppressed here.
            - Exactly one release per `__enter__`; the lock is reentrant, so nested
              `with` blocks are legal and each level must exit.

        Threading:
            Releases the index lock acquired by `__enter__`.

        Lifecycle / Cleanup:
            Performs no cleaned-state check - it is purely the unlock half.

        Raises:
            RuntimeError: If called without a matching `__enter__` on this thread.

        """
        self._lock.release()
