"""melder_0, 2026-10-18: S1's batch for test_inherited_disposal_binding.py. The disposal policy is the binding's (its
manifest), the spell_id the class's code: the retained-cleanup case reads the id from the inspector given the class
alone and the policy from the binding manifest; the identity case is reversed by the owner's ruling (base-class code
counts), so a method added to the base moves the child's spell_id; the staged case stages a second version of the
class, since staging the class itself again is refused (one object, one spell)."""

INHERITED = "tests/component/melder/spellbook/test_inherited_disposal_binding.py"

OLD_RETAINED = (
    "        assert spell_id == Bind.spell_id_inspector(\n"
    "            InheritedCleanup, spell_name=spell.spell_name,\n"
    "            existence=Existence.many, disposal_method_names=[\"cleanup\"],\n"
    "        )\n"
)
NEW_RETAINED = (
    "        assert spell.binding_manifest.disposal_method_names == (\"cleanup\",)\n"
    "        assert spell_id == Bind.spell_id_inspector(InheritedCleanup)\n"
)
OLD_IDENTITY = (
    "def test_unrequested_base_callable_does_not_change_binding_identity(monkeypatch: pytest.MonkeyPatch) -> None:\n"
    "    \"\"\"Preserving the shallow profile avoids unrelated ID drift from expanding inherited members.\"\"\"\n"
    "    before = Bind.spell_id_inspector(InheritedCleanup, existence=Existence.many)\n\n"
    "    def unrelated_method(self: CleanupBase) -> None:\n"
    "        \"\"\"Supply an unrequested base method whose existence must not affect the child fingerprint.\"\"\"\n"
    "        return\n\n"
    "    monkeypatch.setattr(CleanupBase, \"unrelated_operation\", unrelated_method, raising=False)\n"
    "    after = Bind.spell_id_inspector(InheritedCleanup, existence=Existence.many)\n"
    "    assert after == before\n"
)
NEW_IDENTITY = (
    "def test_a_method_added_to_the_base_moves_the_child_spell_id(monkeypatch: pytest.MonkeyPatch) -> None:\n"
    "    \"\"\"\n"
    "    A base class's code is part of its subclasses' code (the owner's ruling, S1 of\n"
    "    EPIC-2026-10-18-spell_identity_is_the_code): an unrequested base method added is a new spell_id for the\n"
    "    child. Until S1 the shallow profile kept the child's fingerprint unchanged here.\n"
    "    \"\"\"\n"
    "    before = Bind.spell_id_inspector(InheritedCleanup)\n\n"
    "    def unrelated_method(self: CleanupBase) -> None:\n"
    "        \"\"\"Supply an unrequested base method; it is code, so the child's spell_id moves with it.\"\"\"\n"
    "        return\n\n"
    "    monkeypatch.setattr(CleanupBase, \"unrelated_operation\", unrelated_method, raising=False)\n"
    "    after = Bind.spell_id_inspector(InheritedCleanup)\n"
    "    assert after != before\n"
)
OLD_STAGED = (
    "def test_inactive_binding_resolves_inherited_cleanup_before_fingerprinting() -> None:\n"
    "    \"\"\"A staged member receives its own inherited disposal policy without changing the active one.\"\"\"\n"
    "    with configured_book([], dynamic=True) as book:\n"
    "        active_id = book.bind(spell=InheritedCleanup, existence=\"many\")\n"
    "        active = book.find_spell_by_spell_id(active_id)\n"
    "        assert active is not None\n"
    "        staged_id = book.bind_inactive(\n"
    "            spell=InheritedCleanup, spell_index=active.spell_index, existence=\"many\",\n"
)
NEW_STAGED = (
    "def test_inactive_binding_resolves_inherited_cleanup_for_the_staged_version() -> None:\n"
    "    \"\"\"\n"
    "    A staged version receives its own inherited disposal policy without changing the active one.\n\n"
    "    One object is one spell (S1 of EPIC-2026-10-18-spell_identity_is_the_code): staging InheritedCleanup itself\n"
    "    again is refused, so the staged member is a second version - the same name and base, one class-level value\n"
    "    more - which inherits `cleanup` from the same base.\n"
    "    \"\"\"\n"
    "    second_version = type(\n"
    "        \"InheritedCleanup\", (CleanupBase,),\n"
    "        {\"__module__\": __name__, \"__qualname__\": \"InheritedCleanup\", \"version\": 2},\n"
    "    )\n"
    "    with configured_book([], dynamic=True) as book:\n"
    "        active_id = book.bind(spell=InheritedCleanup, existence=\"many\")\n"
    "        active = book.find_spell_by_spell_id(active_id)\n"
    "        assert active is not None\n"
    "        staged_id = book.bind_inactive(\n"
    "            spell=second_version, spell_index=active.spell_index, existence=\"many\",\n"
)


def apply(applier) -> None:
    """The inherited-disposal batch."""
    applier.edit(INHERITED, [
        ("from melder.aether.spellbook.existence.existence import Existence\n", ""),
        (OLD_RETAINED, NEW_RETAINED),
        (OLD_IDENTITY, NEW_IDENTITY),
        (OLD_STAGED, NEW_STAGED),
    ], "inherited disposal")
