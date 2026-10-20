"""Existing tests whose stubs follow the 0.2.8230 lookups; keeps each region's own line endings. usage: <root>"""
import pathlib, sys

ROOT = pathlib.Path(sys.argv[1])


def edit(rel, ops):
    path = ROOT / rel
    data = path.read_bytes().decode("utf-8")
    for anchor, new, count in ops:
        crlf_anchor = anchor.replace("\n", "\r\n")
        if data.count(crlf_anchor) == count:
            data = data.replace(crlf_anchor, new.replace("\n", "\r\n"))
        elif data.count(anchor) == count:
            data = data.replace(anchor, new)
        else:
            raise SystemExit(f"{rel}: anchor x{data.count(crlf_anchor)}/{data.count(anchor)} (want {count}): "
                             f"{anchor[:80]!r}")
    path.write_bytes(data.encode("utf-8"))
    print(f"{rel}: {len(ops)} edits")


edit("tests/unit/melder/aether/conduit/conduit_ward/contract/test_details.py", [
    ("""        Returns a MagicMock with a prepopulated version map.
""", """        Returns a MagicMock with a prepopulated version map; its membership probe answers from
        that map.
""", 1),
    ("""    mock = MagicMock(spec=SpellIndex)
    mock._spells_in_index = {"sha123": "version_data"}
    return mock
""", """    mock = MagicMock(spec=SpellIndex)
    mock._spells_in_index = {"sha123": "version_data"}
    # Detail.has_spell asks the index through its cleanup-safe probe (0.2.8230): answer the probe
    # from whatever member map the test sets, read at call time.
    mock._has_spell_unless_cleaned.side_effect = lambda spell_id: spell_id in mock._spells_in_index
    return mock
""", 1),
])

edit("tests/unit/melder/aether/conduit/test_conduit_facade.py", [
    ("""    spell_index = SpellIndex("sha-1")
    spellbook_stub._spells = {spell_index: _make_spell("sha-1", permissions=Permissions.create)}

    result = conduit_lesser.get_spell_permissions("sha-1")

    assert result == "create"
""", """    spell = _make_spell("sha-1", permissions=Permissions.create)
    # The lineage lookup is the Book's id-map lookup (0.2.8230), not a walk of its index map.
    spellbook_stub.find_spell_by_id.side_effect = {"sha-1": spell}.get

    result = conduit_lesser.get_spell_permissions("sha-1")

    assert result == "create"
    spellbook_stub.find_spell_by_id.assert_called_once_with("sha-1")
""", 1),
    ("""    spell_index = SpellIndex("sha-2")
    spellbook_stub._spells = {spell_index: _make_spell("sha-2", permissions=Permissions.read)}

    with pytest.raises(RuntimeError, match="not found"):
""", """    # The Book knows only "sha-2", so its id-map lookup misses "sha-1" (0.2.8230).
    spellbook_stub.find_spell_by_id.side_effect = {
        "sha-2": _make_spell("sha-2", permissions=Permissions.read),
    }.get

    with pytest.raises(RuntimeError, match="not found"):
""", 1),
])

edit("tests/unit/melder/aether/test_command_system_direct.py", [
    ("""    class _SpellIndex:
        def __init__(self, version_id: str) -> None:
            self._version_id = version_id

        def has_spell(self, version_id: str) -> bool:
            return self._version_id == version_id

    command_system, viewer, _ = _make_command_system()

    with pytest.raises(ValueError, match="spell_index_id cannot be empty"):
""", """    command_system, viewer, _ = _make_command_system()

    with pytest.raises(ValueError, match="spell_index_id cannot be empty"):
""", 1),
    ("""                _spellbook=SimpleNamespace(
                    _spells={_SpellIndex("other-version"): object()},
                )
""", """                _spellbook=SimpleNamespace(
                    # The owner Book's id-map lookup knows another version only (0.2.8230).
                    find_spell_by_id={"other-version": object()}.get,
                )
""", 1),
])

edit("tests/unit/melder/aether/test_nexus.py", [
    ("""    class _SpellIndex:
        def has_spell(self, version_id: str) -> bool:
            return version_id == "sha-1"

    owner_conduit = SimpleNamespace(
        _spellbook=SimpleNamespace(
            _spells={_SpellIndex(): spell},
        )
    )
""", """    owner_conduit = SimpleNamespace(
        _spellbook=SimpleNamespace(
            # The owner Book answers the lineage lookup from its id maps (0.2.8230).
            find_spell_by_id={"sha-1": spell}.get,
        )
    )
""", 1),
])

edit("tests/unit/melder/spellbook/test_spellbook.py", [
    ("""from melder.aether.spellbook.configuration.system_state import SystemState
""", """from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.spellbook.configuration.system_state import SystemState
""", 1),
    ("""        Provide a minimal SpellIndex stub with version tracking.
    Contract:
        Exposes has_spell and cleanup for Spellbook internals.
""", """        Provide a minimal SpellIndex stub with version tracking.
    Contract:
        Exposes has_spell, the cleanup-safe membership probe and cleanup for Spellbook internals.
""", 1),
    ("""        return version_id in self._spells_in_index

    def _set_owner_conduit_id(self, conduit_id):
""", """        return version_id in self._spells_in_index

    def _has_spell_unless_cleaned(self, version_id):
        \"\"\"
        Purpose:
            Mirror SpellIndex._has_spell_unless_cleaned for walks over indexes the caller does not own.
        Contract:
            Returns False once the stub is cleaned; otherwise the has_spell answer.
        Args:
            version_id: Version id to check.
        Returns:
            bool: True when the live stub registers version_id.
        \"\"\"
        if self._cleaned:
            return False
        return self.has_spell(version_id)

    def _set_owner_conduit_id(self, conduit_id):
""", 1),
    ("""    sb = Spellbook()
    sb._contracted_spells = {"c": {DummySpellIndex(versions={"v1"}): DummySpell()}}
    assert sb._find_contracted_spell_by_id("v2", "c") is None
""", """    sb = Spellbook()
    sb._contracted_spells = {"c": {DummySpellIndex(versions={"v1"}): DummySpell()}}
    assert sb._find_contracted_spell_by_id("v2", "c") is None


def test_find_contracted_spell_by_id_skips_an_index_its_owner_cleaned():
    \"\"\"
    Purpose:
        Ensure a contracted lookup treats an index its owner cleaned as holding nothing.
    Contract:
        _find_contracted_spell_by_id returns None instead of raising when the only index that held
        the version was cleaned while the contracted map still referenced it (0.2.8230; before, the
        index's has_spell raised RuntimeError or AttributeError).
    Returns:
        None.
    Raises:
        AssertionError: If a spell is returned or the cleaned index raises.
    \"\"\"
    sb = Spellbook()
    idx = SpellIndex("v1")
    idx.cleanup()
    sb._contracted_spells = {"c": {idx: DummySpell()}}
    assert sb._find_contracted_spell_by_id("v1", "c") is None
""", 1),
])
