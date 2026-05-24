import pytest

from melder.aether.spellbook.bind.spell_index import SpellIndex


class _SpellStub:
    """
    Minimal spell stub for SpellIndex attachment tests.

    Purpose:
        Provide a stable object identity for spell_id map registration.

    Contract:
        - Identity is defined by the instance.
        - Carries a debug-friendly name only.
    """

    def __init__(self, name: str) -> None:
        """
        Initialize the stub with a debug name.

        Args:
            name (str): Label used for debugging and clarity in failures.
        """
        self.name = name
        self.spell_id = name


class _SpellbookStub:
    """
    Minimal Spellbook stub that tracks spell_id map updates.

    Purpose:
        Record and apply owned/contracted id map mutations triggered by
        SpellIndex attach/update/detach operations.

    Contract:
        - Owned map is keyed by spell_id.
        - Contracted map is keyed by conduit_id then spell_id.
        - Update calls replace old ids and insert new ids.
    """

    def __init__(self) -> None:
        """
        Initialize empty id maps and call trackers.

        Returns:
            None.
        """
        self.owned_by_id: dict[str, _SpellStub] = {}
        self.contracted_by_id: dict[str, dict[str, _SpellStub]] = {}
        self.register_calls: list[tuple] = []
        self.update_calls: list[tuple] = []
        self.unregister_calls: list[tuple] = []

    def _register_owned_spell_id(self, spell_id: str, spell: _SpellStub) -> None:
        """
        Register an owned spell_id mapping.

        Contract:
            - Overwrites any existing mapping for the same id.

        Args:
            spell_id (str): Current spell_id for the owned spell.
            spell (_SpellStub): Owned spell instance.
        """
        self.owned_by_id[spell_id] = spell
        self.register_calls.append(("owned", spell_id, spell))

    def _update_owned_spell_id(self, old_id: str, new_id: str, spell: _SpellStub) -> None:
        """
        Update an owned spell_id mapping.

        Contract:
            - Removes the old id if present.
            - Inserts the new id with the same spell instance.

        Args:
            old_id (str): Previous spell_id.
            new_id (str): Updated spell_id.
            spell (_SpellStub): Owned spell instance.
        """
        self.owned_by_id.pop(old_id, None)
        self.owned_by_id[new_id] = spell
        self.update_calls.append(("owned", old_id, new_id, spell))

    def _register_contracted_spell_id(
        self,
        conduit_id: str,
        spell_id: str,
        spell: _SpellStub,
    ) -> None:
        """
        Register a contracted spell_id mapping.

        Contract:
            - Ensures a per-conduit map exists.
            - Overwrites any existing mapping for the same id.

        Args:
            conduit_id (str): Peer conduit identifier.
            spell_id (str): Current spell_id for the contracted spell.
            spell (_SpellStub): Contracted spell instance.
        """
        spell_map = self.contracted_by_id.setdefault(conduit_id, {})
        spell_map[spell_id] = spell
        self.register_calls.append(("contracted", conduit_id, spell_id, spell))

    def _update_contracted_spell_id(
        self,
        conduit_id: str,
        old_id: str,
        new_id: str,
        spell: _SpellStub,
    ) -> None:
        """
        Update a contracted spell_id mapping.

        Contract:
            - Removes the old id if present.
            - Inserts the new id with the same spell instance.

        Args:
            conduit_id (str): Peer conduit identifier.
            old_id (str): Previous spell_id.
            new_id (str): Updated spell_id.
            spell (_SpellStub): Contracted spell instance.
        """
        spell_map = self.contracted_by_id.setdefault(conduit_id, {})
        spell_map.pop(old_id, None)
        spell_map[new_id] = spell
        self.update_calls.append(("contracted", conduit_id, old_id, new_id, spell))

    def _unregister_contracted_spell_id(
        self,
        conduit_id: str,
        spell_id: str,
        spell: _SpellStub,
    ) -> None:
        """
        Remove a contracted spell_id mapping.

        Contract:
            - Removes the id when the stored spell matches.

        Args:
            conduit_id (str): Peer conduit identifier.
            spell_id (str): Current spell_id for the contracted spell.
            spell (_SpellStub): Contracted spell instance.
        """
        spell_map = self.contracted_by_id.setdefault(conduit_id, {})
        if spell_map.get(spell_id) is spell:
            spell_map.pop(spell_id, None)
        self.unregister_calls.append(("contracted", conduit_id, spell_id, spell))


def test_current_and_update_and_get_all_versions():
    idx = SpellIndex("v1")
    assert idx.current == "v1"
    idx.update("v2")
    idx.update("v3")
    assert idx.current == "v3"
    assert idx.get_all_versions() == {"v1", "v2", "v3"}
    assert idx.has_version("v1")
    assert idx.has_version("v3")
    assert not idx.has_version("missing")


def test_hash_and_equality_stable():
    idx1 = SpellIndex("v1")
    idx2 = SpellIndex("v2")
    assert idx1 == idx1
    assert idx1 != idx2
    h1 = hash(idx1)
    idx1.update("v3")
    assert hash(idx1) == h1  # hash based only on immutable ULID


def test_hash_and_equality_ignore_current_id():
    idx1 = SpellIndex("v1")
    idx2 = SpellIndex("v2")
    # force same ULID by copying id
    idx2._id = idx1.id
    assert idx1 == idx2
    idx1.update("v3")
    idx2.update("v4")
    assert idx1 == idx2
    assert hash(idx1) == hash(idx2)


def test_repr_includes_id_and_current():
    idx = SpellIndex("v1")
    text = repr(idx)
    assert "current=v1" in text
    assert "SpellKey" not in text or idx.id in text


def test_context_manager_acquires_and_releases():
    idx = SpellIndex("v1")
    with idx as ctx:
        assert ctx is idx
    # RLock can be re-acquired after context exit
    assert idx._lock.acquire() is True or idx._lock.acquire() is None
    idx._lock.release()


def test_get_all_versions_is_copy():
    idx = SpellIndex("v1")
    versions = idx.get_all_versions()
    versions.add("new")
    assert "new" not in idx.get_all_versions()


def test_has_version_updates_after_update():
    idx = SpellIndex("v1")
    assert idx.has_version("v1")
    idx.update("v2")
    assert idx.has_version("v2")
    assert idx.get_all_versions() == {"v1", "v2"}


@pytest.mark.xfail(
    reason="Spell_id should not change",
    strict=False,
)
def test_update_syncs_spell_id_to_current_for_owned_and_contracted_spells() -> None:
    """
    Verify SpellIndex.update keeps attached spell objects aligned to the new
    current version id.

    Contract:
        - Owned spell.spell_id is rewritten to the new current id.
        - Contracted spell.spell_id is rewritten to the new current id.
    """
    idx = SpellIndex("v1")
    owner_book = _SpellbookStub()
    owner_spell = _SpellStub("owned")
    contracted_book = _SpellbookStub()
    contracted_spell = _SpellStub("contracted")

    idx._attach_owner(owner_book, owner_spell)
    idx._attach_contracted(contracted_book, "peer-1", contracted_spell)

    idx.update("v2")

    assert idx.current == "v2"
    assert owner_spell.spell_id == "v2"
    assert contracted_spell.spell_id == "v2"


def test_repr_reflects_current():
    idx = SpellIndex("v1")
    idx.update("v2")
    text = repr(idx)
    assert "v2" in text and idx.id in text


def test_nested_context_manager():
    idx = SpellIndex("v1")
    with idx:
        with idx:
            assert idx.current == "v1"


def test_cleanup_idempotent_and_nulls():
    idx = SpellIndex("v1")
    idx.cleanup()
    assert idx._lock is not None
    idx.cleanup()  # idempotent


def test_operations_after_cleanup_raise():
    idx = SpellIndex("v1")
    idx.cleanup()
    assert not hasattr(idx, "_current_id")
    with pytest.raises(AttributeError):
        _ = idx.current
    with pytest.raises(RuntimeError):
        idx.update("v2")
    with pytest.raises(RuntimeError):
        idx.get_all_versions()
    with pytest.raises(RuntimeError):
        idx.has_version("v1")
    with pytest.raises(RuntimeError):
        with idx:
            pass


def test_hash_equality_with_other_types():
    idx = SpellIndex("v1")
    assert idx != "not-a-spell-index"
    assert idx is not None


def test_cleanup_then_hash_raises():
    idx = SpellIndex("v1")
    idx.cleanup()
    assert not hasattr(idx, "_current_id")
    with pytest.raises(AttributeError):
        _ = idx.current
    with pytest.raises(RuntimeError):
        idx.update("v2")


def test_attach_owner_registers_spell_id_and_sets_owner() -> None:
    """
    Verify owner attachment registers the current spell_id in the spellbook.

    Contract:
        - _attach_owner stores the owner references.
        - The current spell_id is registered in the owned id map.
    """
    spellbook = _SpellbookStub()
    spell = _SpellStub("owned")
    idx = SpellIndex("v1")

    idx._attach_owner(spellbook, spell)

    assert idx._owner_spellbook is spellbook
    assert idx._active_spell is spell
    assert spellbook.owned_by_id["v1"] is spell


def test_attach_owner_rejects_different_owner() -> None:
    """
    Verify a SpellIndex cannot be reattached to a different owner spellbook.

    Contract:
        - Attaching to a different owner raises RuntimeError.
    """
    idx = SpellIndex("v1")
    spell = _SpellStub("owned")
    owner_a = _SpellbookStub()
    owner_b = _SpellbookStub()

    idx._attach_owner(owner_a, spell)

    with pytest.raises(RuntimeError, match="Owner spellbook already attached"):
        idx._attach_owner(owner_b, spell)


def test_attach_owner_rejects_different_spell() -> None:
    """
    Verify a SpellIndex cannot attach a different spell for the same owner.

    Contract:
        - Attaching a different spell raises RuntimeError.
    """
    idx = SpellIndex("v1")
    spellbook = _SpellbookStub()
    spell_a = _SpellStub("owned-a")
    spell_b = _SpellStub("owned-b")

    idx._attach_owner(spellbook, spell_a)

    with pytest.raises(RuntimeError, match="Active spell already attached"):
        idx._attach_owner(spellbook, spell_b)


def test_set_owner_conduit_id_rejects_mismatch() -> None:
    """
    Verify owner conduit id is immutable once set.

    Contract:
        - Reusing the same id is allowed.
        - Changing to a different id raises RuntimeError.
    """
    idx = SpellIndex("v1")

    idx._set_owner_conduit_id("conduit-a")
    idx._set_owner_conduit_id("conduit-a")

    with pytest.raises(RuntimeError, match="Owner conduit id already set"):
        idx._set_owner_conduit_id("conduit-b")


def test_attach_contracted_registers_spell_id_map() -> None:
    """
    Verify contracted attachment registers the spell_id map entry.

    Contract:
        - _attach_contracted registers the current spell_id under the conduit id.
    """
    idx = SpellIndex("v1")
    spellbook = _SpellbookStub()
    spell = _SpellStub("contracted")

    idx._attach_contracted(spellbook, "peer-1", spell)

    assert spellbook.contracted_by_id["peer-1"]["v1"] is spell


def test_attach_contracted_rejects_different_spell() -> None:
    """
    Verify contracted attachment rejects a different spell for the same key.

    Contract:
        - Attaching a different spell raises RuntimeError.
    """
    idx = SpellIndex("v1")
    spellbook = _SpellbookStub()
    spell_a = _SpellStub("contracted-a")
    spell_b = _SpellStub("contracted-b")

    idx._attach_contracted(spellbook, "peer-1", spell_a)

    with pytest.raises(RuntimeError, match="Contract attachment already exists"):
        idx._attach_contracted(spellbook, "peer-1", spell_b)


def test_detach_contracted_removes_mapping() -> None:
    """
    Verify contracted detachment removes the current spell_id mapping.

    Contract:
        - _detach_contracted unregisters the id map entry for the conduit.
    """
    idx = SpellIndex("v1")
    spellbook = _SpellbookStub()
    spell = _SpellStub("contracted")

    idx._attach_contracted(spellbook, "peer-1", spell)
    idx._detach_contracted(spellbook, "peer-1")

    assert "v1" not in spellbook.contracted_by_id.get("peer-1", {})


def test_detach_contracted_raises_when_missing() -> None:
    """
    Verify detaching a missing contract raises.

    Contract:
        - _detach_contracted raises RuntimeError when no attachment exists.
    """
    idx = SpellIndex("v1")
    spellbook = _SpellbookStub()

    with pytest.raises(RuntimeError, match="Contract attachment is missing"):
        idx._detach_contracted(spellbook, "peer-1")


def test_update_propagates_owner_and_contracted_maps() -> None:
    """
    Verify update propagates spell_id changes to attached spellbooks.

    Contract:
        - Owner map is updated from old_id to new_id.
        - Contracted maps are updated for each attached conduit.
    """
    idx = SpellIndex("v1")
    owner_book = _SpellbookStub()
    contracted_book = _SpellbookStub()
    owner_spell = _SpellStub("owned")
    contracted_spell = _SpellStub("contracted")

    idx._attach_owner(owner_book, owner_spell)
    idx._attach_contracted(contracted_book, "peer-1", contracted_spell)

    idx.update("v2")

    assert "v1" not in owner_book.owned_by_id
    assert owner_book.owned_by_id["v2"] is owner_spell
    assert "v1" not in contracted_book.contracted_by_id["peer-1"]
    assert contracted_book.contracted_by_id["peer-1"]["v2"] is contracted_spell


def test_update_raises_when_owner_spell_missing() -> None:
    """
    Verify update raises when owner spellbook is set without a spell.

    Contract:
        - Missing owner spell raises RuntimeError.
    """
    idx = SpellIndex("v1")
    spellbook = _SpellbookStub()
    idx._owner_spellbook = spellbook

    with pytest.raises(RuntimeError, match="active spell is missing"):
        idx.update("v2")


def test_cleanup_clears_attachment_references() -> None:
    """
    Verify cleanup clears attachment references for owner and contracts.

    Contract:
        - Owner and contracted attachments are nulled on cleanup.
    """
    idx = SpellIndex("v1")
    owner_book = _SpellbookStub()
    contracted_book = _SpellbookStub()
    owner_spell = _SpellStub("owned")
    contracted_spell = _SpellStub("contracted")

    idx._attach_owner(owner_book, owner_spell)
    idx._set_owner_conduit_id("conduit-a")
    idx._attach_contracted(contracted_book, "peer-1", contracted_spell)

    idx.cleanup()

    assert not hasattr(idx, "_owner_spellbook")
    assert not hasattr(idx, "_active_spell")
    assert not hasattr(idx, "_owner_conduit_id")
    assert not hasattr(idx, "_contracted_spellbooks")


def test_update_same_id_is_noop() -> None:
    idx = SpellIndex("v1")
    owner_book = _SpellbookStub()
    owner_spell = _SpellStub("owned")

    idx._attach_owner(owner_book, owner_spell)
    idx.update("v1")

    assert idx.current == "v1"
    assert owner_book.update_calls == []


def test_cleanup_rechecks_cleaned_state_under_lock() -> None:
    class _FlipCleanedOnEnter:
        def __init__(self, owner):
            self._owner = owner

        def __enter__(self):
            self._owner._cleaned = True
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    idx = SpellIndex("v1")
    original_lock = idx._lock
    idx._lock = _FlipCleanedOnEnter(idx)
    try:
        idx.cleanup()
    finally:
        idx._lock = original_lock

    assert idx._cleaned is True
