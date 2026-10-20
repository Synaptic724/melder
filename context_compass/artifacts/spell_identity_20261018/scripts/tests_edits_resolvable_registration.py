"""melder_0, 2026-10-18: S1's batch for test_spellbook_component_resolvable_registration.py. The capability is part
of the binding (its manifest), the spell_id the class's code, and one object is one spell: the inspector case reads
the id from the class alone and the capability from the manifest; the inspector half of the reflection case retires
(the inspector takes only the target); a second registration of the class - another capability at the same address
or another - is refused as a collision; the fluent case binds a class per registration; the parked cases stage a
second version of the class."""

RESOLVABLE = "tests/component/melder/spellbook/test_spellbook_component_resolvable_registration.py"

IMPORT_ANCHOR = "from melder.aether.spellbook.spellbook import Spellbook\n"
NEW_IMPORTS = (
    "from melder.aether.spellbook.spellbook import Spellbook\n"
    "from tests.component.melder.spellbook.test_ordered_disposal_binding import second_version_of\n"
)
CLASS_ANCHOR = (
    "class RegistrationService:\n"
    "    \"\"\"Ordinary class whose registration needs no constructor execution.\"\"\"\n"
)
NEW_CLASSES = CLASS_ANCHOR + (
    "\n\n"
    "class SecondRegistrationService:\n"
    "    \"\"\"A second ordinary class: one object is one spell, so each registration of a case binds its own.\"\"\"\n"
    "\n\n"
    "class ThirdRegistrationService:\n"
    "    \"\"\"A third ordinary class, for the same reason.\"\"\"\n"
)
OLD_INSPECTOR = (
    "def test_inspector_and_real_bind_agree_on_effective_inputs(book: Spellbook, resolvable: bool) -> None:\n"
    "    \"\"\"The inspector uses the same capability and effective naming inputs as a real bind.\"\"\"\n"
    "    expected = Bind.spell_id_inspector(\n"
    "        RegistrationService, spell_name=\"RegistrationService\", spellframe=\"services\",\n"
    "        binding_name=\"sample\", existence=Existence.unique, resolvable=resolvable,\n"
    "    )\n"
    "    actual = book.bind(\n"
    "        spell=RegistrationService, spellframe=\"services\", binding_name=\"sample\",\n"
    "        existence=\"unique\", resolvable=resolvable,\n"
    "    )\n"
    "    assert actual == expected\n"
)
NEW_INSPECTOR = (
    "def test_inspector_and_real_bind_agree_whatever_the_binding(book: Spellbook, resolvable: bool) -> None:\n"
    "    \"\"\"\n"
    "    The inspector, given the class alone, answers the id a real bind gives under any name, frame or capability:\n"
    "    the spell_id is the class's code, and the capability is recorded in the binding manifest (S1 of\n"
    "    EPIC-2026-10-18-spell_identity_is_the_code).\n"
    "    \"\"\"\n"
    "    actual = book.bind(\n"
    "        spell=RegistrationService, spellframe=\"services\", binding_name=\"sample\",\n"
    "        existence=\"unique\", resolvable=resolvable,\n"
    "    )\n"
    "    assert actual == Bind.spell_id_inspector(RegistrationService)\n"
    "    assert active_spell(book, actual).binding_manifest.resolvable is resolvable\n"
)
OLD_REFLECTION_HEAD = (
    "@pytest.mark.parametrize(\"inspector\", [False, True])\n"
    "def test_invalid_capability_is_rejected_before_user_reflection(book: Spellbook, inspector: bool) -> None:\n"
    "    \"\"\"Independent bind and inspection reject invalid policy before observing a user's object.\"\"\"\n"
)
NEW_REFLECTION_HEAD = (
    "def test_invalid_capability_is_rejected_before_user_reflection(book: Spellbook) -> None:\n"
    "    \"\"\"\n"
    "    Bind rejects an invalid policy before observing a user's object. The inspector takes only the target since S1\n"
    "    of EPIC-2026-10-18-spell_identity_is_the_code, so it has no policy to reject.\n"
    "    \"\"\"\n"
)
OLD_REFLECTION_BODY = (
    "    with pytest.raises(TypeError, match=\"resolvable.*bool\"):\n"
    "        if inspector:\n"
    "            Bind.spell_id_inspector(target, resolvable=0)\n"
    "        else:\n"
    "            book.bind(spell=target, existence=\"unique\", resolvable=0)\n"
)
NEW_REFLECTION_BODY = (
    "    with pytest.raises(TypeError, match=\"resolvable.*bool\"):\n"
    "        book.bind(spell=target, existence=\"unique\", resolvable=0)\n"
)
OLD_FLUENT = (
    "        second_id = binder.bind(RegistrationService, binding_name=\"second\").finalize()\n"
)
NEW_FLUENT = (
    "        second_id = binder.bind(SecondRegistrationService, binding_name=\"second\").finalize()\n"
)
OLD_FLUENT_THIRD = (
    "        third_id = binder.bind(RegistrationService, binding_name=\"third\").finalize()\n"
)
NEW_FLUENT_THIRD = (
    "        third_id = binder.bind(ThirdRegistrationService, binding_name=\"third\").finalize()\n"
)
OLD_PARKED = (
    "    parked_id = surface.bind_inactive(\n"
    "        spell=RegistrationService, spell_index=selected.spell_index,\n"
    "        existence=\"unique\", resolvable=not active_mode,\n"
    "    )\n"
)
NEW_PARKED = (
    "    # One object is one spell (S1 of EPIC-2026-10-18-spell_identity_is_the_code): the parked member is a second\n"
    "    # version of the class, not the class again.\n"
    "    parked_id = surface.bind_inactive(\n"
    "        spell=second_version_of(RegistrationService), spell_index=selected.spell_index,\n"
    "        existence=\"unique\", resolvable=not active_mode,\n"
    "    )\n"
)
OLD_SLOT = (
    "def test_false_does_not_create_another_active_binding_slot(book: Spellbook) -> None:\n"
    "    \"\"\"Distinct capability fingerprints still obey the existing active signature claim.\"\"\"\n"
    "    original_id = book.bind(spell=RegistrationService, existence=\"unique\")\n"
    "    with pytest.raises(RuntimeError, match=\"Binding signature already active\"):\n"
    "        book.bind(spell=RegistrationService, existence=\"unique\", resolvable=False)\n"
    "    assert active_spell(book, original_id).resolvable is True\n"
    "    definition_id = book.bind(\n"
    "        spell=RegistrationService, existence=\"unique\", binding_name=\"definition\", resolvable=False,\n"
    "    )\n"
    "    assert {row[\"spell_id\"] for row in book.describe_spells_in_spellbook()} == {original_id, definition_id}\n"
)
NEW_SLOT = (
    "def test_false_does_not_register_the_same_class_again(book: Spellbook) -> None:\n"
    "    \"\"\"\n"
    "    One object is one spell (S1 of EPIC-2026-10-18-spell_identity_is_the_code): another capability, at the same\n"
    "    address or under another binding name, is the same spell_id and is refused as a collision. Until S1 the\n"
    "    capability changed the fingerprint and only the address claim refused the first case.\n"
    "    \"\"\"\n"
    "    original_id = book.bind(spell=RegistrationService, existence=\"unique\")\n"
    "    with pytest.raises(RuntimeError, match=\"already registered as spell_id \" + original_id):\n"
    "        book.bind(spell=RegistrationService, existence=\"unique\", resolvable=False)\n"
    "    with pytest.raises(RuntimeError, match=\"already registered as spell_id \" + original_id):\n"
    "        book.bind(spell=RegistrationService, existence=\"unique\", binding_name=\"definition\", resolvable=False)\n"
    "    assert active_spell(book, original_id).resolvable is True\n"
    "    assert {row[\"spell_id\"] for row in book.describe_spells_in_spellbook()} == {original_id}\n"
)
OLD_DEFAULTS = (
    "    parked_id = surface.bind_inactive(\n"
    "        spell=RegistrationService, spell_index=selected.spell_index, existence=\"unique\",\n"
    "    )\n"
)
NEW_DEFAULTS = (
    "    parked_id = surface.bind_inactive(\n"
    "        spell=second_version_of(RegistrationService), spell_index=selected.spell_index, existence=\"unique\",\n"
    "    )\n"
)


def apply(applier) -> None:
    """The resolvable-registration batch."""
    applier.edit(RESOLVABLE, [
        (IMPORT_ANCHOR, NEW_IMPORTS),
        (CLASS_ANCHOR, NEW_CLASSES),
        (OLD_INSPECTOR, NEW_INSPECTOR),
        (OLD_REFLECTION_HEAD, NEW_REFLECTION_HEAD),
        (OLD_REFLECTION_BODY, NEW_REFLECTION_BODY),
        (OLD_FLUENT, NEW_FLUENT),
        (OLD_FLUENT_THIRD, NEW_FLUENT_THIRD),
        (OLD_PARKED, NEW_PARKED),
        (OLD_SLOT, NEW_SLOT),
        (OLD_DEFAULTS, NEW_DEFAULTS),
    ], "resolvable registration")
