import threading
import ulid
from typing import Optional, Dict, Tuple
# Melder Imports
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.interfaces import ISpellIndex, ISpellbook, ISpell
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class SpellIndex(Cleanable, ISpellIndex):
    """
    A stable dictionary key that points to a mutable version ID.

    Design:
    This class solves the "mutable dictionary key" problem. It provides a
    stable, hashable identity via an immutable ULID, while simultaneously
    tracking a mutable "current version" pointer (e.g., a SHA256 commit ID).

    - Hashing and equality are based *only* on the immutable ULID.
    - The version pointer can be safely updated (mutated) in a thread-safe
      manner without breaking its location in a dictionary.
    - The index can be attached to owning and contracted Spellbooks so
      version changes can update spell_id lookup maps.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = (
        "_id",          # The immutable ULID. Used for hashing and equality.
        "_current_id",  # The mutable pointer to the active version (e.g., a SHA256).
        "_lock",        # RLock for thread-safe reads/writes to _current_id.
        "_cleaned",     # Flag for Cleanable interface.
        "_versions",    # Set of all versions seen.
        "_owner_spellbook",
        "_owner_spell",
        "_owner_conduit_id",
        "_contracted_spellbooks",
    )

    def __init__(self, initial_id: str):
        """
        Initialize the SpellIndex with its permanent identity and initial version.

        Purpose:
            Provide a stable, hashable lineage key with a mutable version pointer
            and optional Spellbook attachments for update propagation.

        Contract:
            - The ULID identity never changes.
            - The current version pointer is mutable and guarded by the lock.
            - Attachments are optional and may be added later.

        Args:
            initial_id (str):
                The SHA256 commit ID or version string this key initially points to.

        Threading:
            - Initializes the internal RLock used for all mutations.

        Lifecycle:
            - Attachments are cleared during cleanup.
        """
        super().__init__()
        # The permanent, hashable identity for this key.
        self._id: str = str(ulid.ULID())
        self._lock: threading.RLock = threading.RLock()
        # The dynamic pointer to the version, which can be updated.
        self._current_id: str = initial_id
        self._versions: set = {initial_id}  # Optional: Track all versions seen.
        self._owner_spellbook: Optional[ISpellbook] = None
        self._owner_spell: Optional[ISpell] = None
        self._owner_conduit_id: Optional[str] = None
        self._contracted_spellbooks: Dict[Tuple[ISpellbook, str], ISpell] = {}

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
            self._versions.clear()
            self._versions = None
            self._owner_spellbook = None
            self._owner_spell = None
            self._owner_conduit_id = None
            self._contracted_spellbooks.clear()
            self._contracted_spellbooks = None
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

        When the index is attached to Spellbooks, this method also
        propagates the version change to spell_id lookup maps for
        owned and contracted spellbooks.

        Args:
            new_id (str): The new SHA256 or version ID.

        Raises:
            RuntimeError: If an attached Spellbook or spell is missing.
        """
        self.check_cleaned()
        with self._lock:
            old_id = self._current_id
            if old_id == new_id:
                return
            self._current_id = new_id
            self._versions.add(new_id)
            owner_spellbook = self._owner_spellbook
            owner_spell = self._owner_spell
            # Capture attachments to avoid calling into Spellbook while holding this lock.
            contracted_items = list(self._contracted_spellbooks.items())

        # Commented out as not fully sure how mutations will work and if original spell is substituted or not
        # we could even take a codegen version of the spell and store it and substitute, I
        # am not sure how I plan to do this.
        # if owner_spell is not None:
        #     owner_spell.spell_id = new_id
        # for (_, _), spell in contracted_items:
        #     spell.spell_id = new_id

        if owner_spellbook is not None:
            if owner_spell is None:
                raise RuntimeError("Owner spellbook is set but owner spell is missing.")
            owner_spellbook._update_owned_spell_id(old_id, new_id, owner_spell)

        for (spellbook, conduit_id), spell in contracted_items:
            spellbook._update_contracted_spell_id(conduit_id, old_id, new_id, spell)


    def _attach_owner(self, spellbook: ISpellbook, spell: ISpell) -> None:
        """
        Internal

        Attach this SpellIndex to an owning Spellbook and register the current
        spell_id in the Spellbook's owned id map.

        Contract:
            - A SpellIndex may only have one owning Spellbook.
            - Reattaching to a different owner raises.

        Args:
            spellbook (ISpellbook): Owning Spellbook for this index.
            spell (ISpell): The owned spell instance for this lineage.

        Raises:
            RuntimeError: If a different owner is already attached.
        """
        self.check_cleaned()
        with self._lock:
            if self._owner_spellbook is not None and self._owner_spellbook is not spellbook:
                raise RuntimeError("Owner spellbook already attached for this SpellIndex.")
            if self._owner_spell is not None and self._owner_spell is not spell:
                raise RuntimeError("Owner spell already attached for this SpellIndex.")
            self._owner_spellbook = spellbook
            self._owner_spell = spell
            spell_id = self._current_id

        # Call Spellbook update outside the lock to avoid lock inversion.
        spellbook._register_owned_spell_id(spell_id, spell)


    def _set_owner_conduit_id(self, conduit_id: str) -> None:
        """
        Internal

        Record the owning conduit identifier for this SpellIndex.

        Args:
            conduit_id (str): Identifier for the owning conduit.

        Raises:
            RuntimeError: If an owner conduit id is already set to a different value.
        """
        self.check_cleaned()
        with self._lock:
            if self._owner_conduit_id is not None and self._owner_conduit_id != conduit_id:
                raise RuntimeError("Owner conduit id already set for this SpellIndex.")
            self._owner_conduit_id = conduit_id


    def _attach_contracted(self, spellbook: ISpellbook, conduit_id: str, spell: ISpell) -> None:
        """
        Internal

        Attach this SpellIndex to a contracted Spellbook and register the
        current spell_id in the contracted id map for the given conduit.

        Args:
            spellbook (ISpellbook): The Spellbook receiving the contracted spell.
            conduit_id (str): The peer conduit id for the contract.
            spell (ISpell): The contracted spell instance.

        Raises:
            RuntimeError: If the same contract attachment already exists with a different spell.
        """
        self.check_cleaned()
        key = (spellbook, conduit_id)
        with self._lock:
            existing = self._contracted_spellbooks.get(key)
            if existing is not None and existing is not spell:
                raise RuntimeError("Contract attachment already exists for this SpellIndex.")
            self._contracted_spellbooks[key] = spell
            spell_id = self._current_id

        # Call Spellbook update outside the lock to avoid lock inversion.
        spellbook._register_contracted_spell_id(conduit_id, spell_id, spell)


    def _detach_contracted(self, spellbook: ISpellbook, conduit_id: str) -> None:
        """
        Internal

        Detach this SpellIndex from a contracted Spellbook and remove the
        current spell_id mapping for the given conduit.

        Args:
            spellbook (ISpellbook): The Spellbook removing the contract entry.
            conduit_id (str): The peer conduit id for the contract.

        Raises:
            RuntimeError: If the contract attachment is missing.
        """
        self.check_cleaned()
        key = (spellbook, conduit_id)
        with self._lock:
            spell = self._contracted_spellbooks.pop(key, None)
            spell_id = self._current_id

        # Call Spellbook update outside the lock to avoid lock inversion.
        if spell is None:
            raise RuntimeError("Contract attachment is missing for this SpellIndex.")
        spellbook._unregister_contracted_spell_id(conduit_id, spell_id, spell)

    def get_all_versions(self) -> set:
        """
        Retrieves all version IDs that this key has pointed to.

        Returns:
            set: A set of all version IDs seen.
        """
        self.check_cleaned()
        with self._lock:
            return set(self._versions)


    def has_version(self, version_id: str) -> bool:
        """
        Checks if the key has ever pointed to the specified version ID.

        Args:
            version_id (str): The version ID to check.
        Returns:
            bool: True if the version ID has been seen, False otherwise.
        """
        self.check_cleaned()
        with self._lock:
            return version_id in self._versions

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
        return isinstance(other, SpellIndex) and self._id == other._id

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


    def __enter__(self) -> 'SpellIndex':
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
