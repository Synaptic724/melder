"""melder_0, 2026-10-18: S1's batch for test_ordered_disposal_binding.py. The disposal order is the binding's (its
manifest and hash), the spell_id the class's code. The inspector cases read the id from the class alone and the order
from the manifest; the two-binding case binds a second class, the staged case stages a second version (one object is
one spell); the order-and-hash case is reversed by the design: the order moves the binding hash, never the spell_id."""

ORDERED = "tests/component/melder/spellbook/test_ordered_disposal_binding.py"

HELPER_ANCHOR = (
    "def service_factory() -> OrderedDisposalService:\n"
    "    \"\"\"Return a service through the existing non-class binding family.\"\"\"\n"
    "    return OrderedDisposalService()\n"
)
HELPER = HELPER_ANCHOR + (
    "\n\n"
    "def second_version_of(cls: type) -> type:\n"
    "    \"\"\"\n"
    "    Return a second version of `cls`: the same name, qualname and module, one class-level value more.\n\n"
    "    One object is one spell (S1 of EPIC-2026-10-18-spell_identity_is_the_code): staging the class itself again\n"
    "    is refused, so a staged member is new code under the same address. It inherits every disposal method.\n"
    "    \"\"\"\n"
    "    return type(cls.__name__, (cls,), {\"__module__\": cls.__module__, \"__qualname__\": cls.__qualname__,\n"
    "                                       \"version\": 2})\n"
)
OLD_COMBINES = (
    "        assert spell.has_disposal_methods is True\n"
    "        assert Bind.spell_id_inspector(\n"
    "            OrderedDisposalService,\n"
    "            spell_name=spell.spell_name,\n"
    "            existence=spell.existence,\n"
    "            disposal_method_names=spell.disposal_method_names,\n"
    "        ) == spell_id\n"
)
NEW_COMBINES = (
    "        assert spell.has_disposal_methods is True\n"
    "        assert spell.binding_manifest.disposal_method_names == tuple(expected)\n"
    "        assert Bind.spell_id_inspector(OrderedDisposalService) == spell_id\n"
)
OLD_EACH = (
    "        second_id = book.bind(\n"
    "            spell=OrderedDisposalService, existence=\"many\", binding_name=\"second\",\n"
    "            disposal_method_names=[\"stop\"],\n"
    "        )\n"
)
NEW_EACH = (
    "        # One object is one spell (S1 of EPIC-2026-10-18-spell_identity_is_the_code): the second binding\n"
    "        # registers another class with the same methods.\n"
    "        second_id = book.bind(\n"
    "            spell=InheritedOnlyDisposal, existence=\"many\", binding_name=\"second\",\n"
    "            disposal_method_names=[\"stop\"],\n"
    "        )\n"
)
OLD_STAGED = (
    "        staged_id = book.bind_inactive(\n"
    "            spell=OrderedDisposalService, spell_index=active.spell_index, existence=\"many\",\n"
    "            disposal_method_names=[\"flush\", \"stop\", \"flush\"],\n"
    "        )\n"
)
NEW_STAGED = (
    "        staged_id = book.bind_inactive(\n"
    "            spell=second_version_of(OrderedDisposalService), spell_index=active.spell_index, existence=\"many\",\n"
    "            disposal_method_names=[\"flush\", \"stop\", \"flush\"],\n"
    "        )\n"
)
OLD_RESOLVED = (
    "def test_resolved_order_changes_sha_but_unmatched_names_do_not() -> None:\n"
    "    \"\"\"Only retained order contributes to the disposal portion of the bind fingerprint.\"\"\"\n"
    "    identities: list[str] = []\n"
    "    for number, names in enumerate(([\"flush\", \"close\"], [\"close\", \"flush\"], [\"flush\", \"missing\", \"close\"])):\n"
    "        with configured_book(names, frame=f\"disposal-hash-{number}\") as book:\n"
    "            identities.append(book.bind(spell=OrderedDisposalService, existence=\"many\"))\n"
    "    assert identities[0] != identities[1]\n"
    "    assert identities[0] == identities[2]\n"
)
NEW_RESOLVED = (
    "def test_resolved_order_changes_the_binding_hash_but_unmatched_names_do_not() -> None:\n"
    "    \"\"\"\n"
    "    Only the retained order is part of the binding: it moves the binding hash, and unmatched names do not.\n"
    "    The spell_id is the class's code and never moves (S1 of EPIC-2026-10-18-spell_identity_is_the_code; until\n"
    "    then the order moved the bind fingerprint).\n"
    "    \"\"\"\n"
    "    spell_ids: list[str] = []\n"
    "    binding_hashes: list[str] = []\n"
    "    for number, names in enumerate(([\"flush\", \"close\"], [\"close\", \"flush\"], [\"flush\", \"missing\", \"close\"])):\n"
    "        with configured_book(names, frame=f\"disposal-hash-{number}\") as book:\n"
    "            spell_id = book.bind(spell=OrderedDisposalService, existence=\"many\")\n"
    "            spell = book.find_spell_by_spell_id(spell_id)\n"
    "            assert spell is not None\n"
    "            spell_ids.append(spell_id)\n"
    "            binding_hashes.append(spell.binding_hash)\n"
    "    assert len(set(spell_ids)) == 1\n"
    "    assert binding_hashes[0] != binding_hashes[1]\n"
    "    assert binding_hashes[0] == binding_hashes[2]\n"
)
OLD_BOOK_OWNS = (
    "def test_book_owns_shared_name_order_and_fingerprint(\n"
    "        priority: bool,\n"
    "        spell_names: list[str],\n"
    ") -> None:\n"
    "    \"\"\"Shared names follow the book block, so their explicit order cannot change the bind SHA.\"\"\"\n"
)
NEW_BOOK_OWNS = (
    "def test_book_owns_shared_name_order_and_binding(\n"
    "        priority: bool,\n"
    "        spell_names: list[str],\n"
    ") -> None:\n"
    "    \"\"\"\n"
    "    Shared names follow the book block, so their explicit order cannot change the binding (its manifest, and so\n"
    "    its hash); the spell_id is the class's code.\n"
    "    \"\"\"\n"
)
OLD_BOOK_OWNS_ASSERT = (
    "        assert spell_id == Bind.spell_id_inspector(\n"
    "            OrderedDisposalService, spell_name=spell.spell_name, existence=spell.existence,\n"
    "            disposal_method_names=[\"flush\", \"close\"],\n"
    "        )\n"
)
NEW_BOOK_OWNS_ASSERT = (
    "        assert spell.binding_manifest.disposal_method_names == (\"flush\", \"close\")\n"
    "        assert spell_id == Bind.spell_id_inspector(OrderedDisposalService)\n"
)


def apply(applier) -> None:
    """The ordered-disposal batch."""
    applier.edit(ORDERED, [
        (HELPER_ANCHOR, HELPER),
        (OLD_COMBINES, NEW_COMBINES),
        (OLD_EACH, NEW_EACH),
        (OLD_STAGED, NEW_STAGED),
        (OLD_RESOLVED, NEW_RESOLVED),
        (OLD_BOOK_OWNS, NEW_BOOK_OWNS),
        (OLD_BOOK_OWNS_ASSERT, NEW_BOOK_OWNS_ASSERT),
    ], "ordered disposal")
