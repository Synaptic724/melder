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
    A stable SpellIndex identity that points to a mutable selected-spell id.

    Design:
    This class solves the "mutable dictionary key" problem. It provides a
    stable, hashable SpellIndex identity via an immutable ULID, while simultaneously
    tracking a mutable selected-spell pointer (the SHA256 id of the selected spell).

    - Hashing and equality are based *only* on the immutable ULID.
    - The selected-spell pointer can be safely updated (mutated) in a thread-safe
      manner without breaking its location in a dictionary.
    - The index can be attached to owning and contracted Spellbooks so
      selected-spell changes can update spell_id lookup maps.
    """
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = (
        "_id",          # The immutable ULID. Used for hashing and equality.
        "_selected_spell_id",  # The selected spell's id (a SHA256).
        "_lock",        # RLock for thread-safe reads/writes to _selected_spell_id.
        "_cleaned",     # Flag for Cleanable interface.
        "_spells_in_index",    # Set of all spell ids seen in this index.
        "_owner_spellbook",
        "_selected_spell",
        "_owner_conduit_id",
        "_contracted_spellbooks",
    )

    def __init__(self, initial_id: str):
        """
        Initialize the SpellIndex with its permanent identity and initial selected spell.

        Purpose:
            Provide a stable, hashable SpellIndex identity with a mutable selected-spell pointer
            and optional Spellbook attachments for update propagation.

        Contract:
            - The ULID identity never changes.
            - The selected-spell pointer is mutable and guarded by the lock.
            - Attachments are optional and may be added later.

        Args:
            initial_id (str):
                The SHA256 spell id this index initially selects.

        Threading:
            - Initializes the internal RLock used for all mutations.

        Lifecycle:
            - Attachments are cleared during cleanup.
        """
        super().__init__()
        # The permanent, hashable identity for this key.
        self._id: str = new_ulid()
        self._lock: threading.RLock = threading.RLock()
        # The dynamic pointer to the selected spell, which can be updated.
        self._selected_spell_id: str = initial_id
        self._spells_in_index: set = {initial_id}  # Track all spell ids seen in this index.
        self._owner_spellbook: Optional[Spellbook] = None
        self._selected_spell: Optional[Spell] = None
        self._owner_conduit_id: Optional[str] = None #Owner root conduit
        self._contracted_spellbooks: Dict[Tuple[Spellbook, str], Spell] = {}

    # ------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------
    def cleanup(self) -> None:
        """
        Release attachments and mark this index as cleaned.

        Contract:
            - Idempotent and lock-guarded.
            - Clears the spell-id history and all spellbook / spell attachments
              before dropping the lock reference.
            - Leaves future callers to fail through `check_cleaned()`.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            # Nullify the pointer and release the lock object.
            self._cleaned = True
            self._spells_in_index.clear()
            self._contracted_spellbooks.clear()

            del self._spells_in_index
            del self._owner_spellbook
            del self._selected_spell
            del self._owner_conduit_id
            del self._contracted_spellbooks
            del self._selected_spell_id

    # ------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------
    @property
    def selected_spell_id(self) -> str:
        """
        Return the selected spell's id for this SpellIndex.

        Returns:
            str: The selected spell's id.

        Contract:
            - Returns the live selected-spell pointer, not a historical value.
            - Lock-free read: the pointer is one attribute holding one string
              reference, so a reader observes either the previous or the new
              id, never a torn value. `update(...)` still serializes writers
              and lookup-map propagation under the instance lock; that
              composite update was never atomic for readers of this property,
              so dropping the read lock does not weaken the visible contract.

        Threading:
            - Safe on free-threaded builds; attribute reference loads are
              atomic. This property is the hottest fingerprint read in the
              compiler phases (thousands of reads per conjure), and the
              per-read RLock acquire/release dominated its cost on nogil.
        """
        return self._selected_spell_id

    def update(self, new_id: str) -> None:
        """
        Atomically updates the pointer to a new selected-spell id.

        This operation is thread-safe and does not affect the
        object's hash or its location in a dictionary.

        When the index is attached to Spellbooks, this method also
        propagates the selected-spell change to spell_id lookup maps for
        owned and contracted spellbooks.

        Args:
            new_id (str): The new SHA256 spell id.

        Raises:
            RuntimeError: If an attached Spellbook or spell is missing.
        """
        self.check_cleaned()
        with self._lock:
            old_id = self._selected_spell_id
            if old_id == new_id:
                return
            self._selected_spell_id = new_id
            self._spells_in_index.add(new_id)
            owner_spellbook = self._owner_spellbook
            active_spell = self._selected_spell
            # Capture attachments to avoid calling into Spellbook while holding this lock.
            contracted_items = list(self._contracted_spellbooks.items())

        # Commented out as not fully sure how mutations will work and if original spell is substituted or not
        # we could even take a codegen version of the spell and store it and substitute, I
        # am not sure how I plan to do this.
        # if active_spell is not None:
        #     active_spell.spell_id = new_id
        # for (_, _), spell in contracted_items:
        #     spell.spell_id = new_id

        if owner_spellbook is not None:
            if active_spell is None:
                raise RuntimeError("Owner spellbook is set but active spell is missing.")
            owner_spellbook._update_owned_spell_id(old_id, new_id, active_spell)

        for (spellbook, conduit_id), spell in contracted_items:
            spellbook._update_contracted_spell_id(conduit_id, old_id, new_id, spell)


    def _attach_owner(self, spellbook: Spellbook, spell: Spell) -> None:
        """
        Attach this SpellIndex to an owning Spellbook and register the current
        spell_id in the Spellbook's owned id map.

        Contract:
            - A SpellIndex may only have one owning Spellbook.
            - Reattaching to a different owner raises.
            - The current spell id is registered into the owner spellbook after
              the attachment is recorded locally.

        Args:
            spellbook (ISpellbook): Owning Spellbook for this index.
            spell (Spell): The owned spell instance for this SpellIndex.

        Raises:
            RuntimeError: If a different owner is already attached.
        """
        with self._lock:
            if self._owner_spellbook is not None and self._owner_spellbook is not spellbook:
                raise RuntimeError("Owner spellbook already attached for this SpellIndex.")
            if self._selected_spell is not None and self._selected_spell is not spell:
                raise RuntimeError("Active spell already attached for this SpellIndex.")
            self._owner_spellbook = spellbook
            self._selected_spell = spell
            spell_id = self._selected_spell_id

        # Call Spellbook update outside the lock to avoid lock inversion.
        spellbook._register_owned_spell_id(spell_id, spell)


    def _set_owner_conduit_id(self, conduit_id: str) -> None:
        """
        Record the owning conduit identifier for this SpellIndex.

        This is the SpellIndex-side memory of which conduit currently owns the
        spellbook attachment. It is used as attachment metadata, not as part of
        hash/equality identity.

        Args:
            conduit_id (str): Identifier for the owning conduit.
        Contract:
            - The owner conduit id may be set once and then repeated with the
              same value.
            - Rebinding to a different owner conduit id raises immediately.

        Raises:
            RuntimeError: If an owner conduit id is already set to a different value.
        """
        with self._lock:
            if self._owner_conduit_id is not None and self._owner_conduit_id != conduit_id:
                raise RuntimeError("Owner conduit id already set for this SpellIndex.")
            self._owner_conduit_id = conduit_id


    def _attach_contracted(self, spellbook: Spellbook, conduit_id: str, spell: Spell) -> None:
        """
        Attach this SpellIndex to a contracted Spellbook and register the
        current spell_id in the contracted id map for the given conduit.

        Contract:
            - Contract attachments are keyed by `(spellbook, conduit_id)`.
            - Reattaching the same key to a different spell instance raises.
            - The contracted spell id mapping is registered after local
              attachment state is updated.

        Args:
            spellbook (ISpellbook): The Spellbook receiving the contracted spell.
            conduit_id (str): The peer conduit id for the contract.
            spell (Spell): The contracted spell instance.

        Raises:
            RuntimeError: If the same contract attachment already exists with a different spell.
        """
        key = (spellbook, conduit_id)
        with self._lock:
            existing = self._contracted_spellbooks.get(key)
            if existing is not None and existing is not spell:
                raise RuntimeError("Contract attachment already exists for this SpellIndex.")
            self._contracted_spellbooks[key] = spell
            spell_id = self._selected_spell_id

        # Call Spellbook update outside the lock to avoid lock inversion.
        spellbook._register_contracted_spell_id(conduit_id, spell_id, spell)


    def _detach_contracted(self, spellbook: Spellbook, conduit_id: str) -> None:
        """
        Detach this SpellIndex from a contracted Spellbook and remove the
        current spell_id mapping for the given conduit.

        Contract:
            - Removes the local contract attachment first, then unregisters the
              contracted spell id mapping.
            - Missing attachments are treated as an error because the caller is
              attempting to tear down a contract that this index does not hold.

        Args:
            spellbook (ISpellbook): The Spellbook removing the contract entry.
            conduit_id (str): The peer conduit id for the contract.

        Raises:
            RuntimeError: If the contract attachment is missing.
        """
        key = (spellbook, conduit_id)
        with self._lock:
            spell = self._contracted_spellbooks.pop(key, None)
            spell_id = self._selected_spell_id

        # Call Spellbook update outside the lock to avoid lock inversion.
        if spell is None:
            raise RuntimeError("Contract attachment is missing for this SpellIndex.")
        spellbook._unregister_contracted_spell_id(conduit_id, spell_id, spell)

    def spells_in_index(self) -> set:
        """
        Return a snapshot of every spell id seen by this SpellIndex.

        Returns:
            set: A set of all spell ids seen in this index.

        Contract:
            - Returns a detached set copy.
            - Includes the initial spell id and every later id accepted by
              `update(...)`.
        """
        self.check_cleaned()
        with self._lock:
            return set(self._spells_in_index)


    def has_spell(self, spell_id: str) -> bool:
        """
        Return whether `spell_id` is a known spell id of this SpellIndex.

        Args:
            spell_id (str): The spell id to check.
        Returns:
            bool: True if the spell id has been seen, False otherwise.

        Contract:
            - Checks against the full historical spell-id set, not only the
              current pointer.
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

        # We lock here to ensure a consistent snapshot for repr
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
