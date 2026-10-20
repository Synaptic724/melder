"""melder_0, 2026-10-18: S1's batch for test_spellbook_component_bind.py. The inspector takes only the target now: the
spell_id is the class's code, so the inspector given the class alone answers the id bind gave. The comment that
explained the old parity (resolved name, existence and disposal names passed through) is rewritten, not dropped."""

COMPONENT_BIND = "tests/component/melder/spellbook/test_spellbook_component_bind.py"

OLD = (
    "        # The fingerprint composes bind-time facts: _bind_logic hashes the\n"
    "        # RESOLVED spell name (derived from the class), the lookup signature,\n"
    "        # existence, and resolved disposal metadata. The inspector passes its\n"
    "        # inputs through unresolved, so parity requires supplying the same\n"
    "        # resolved facts the bind computed.\n"
    "        assert Bind.spell_id_inspector(\n"
    "            BasicService,\n"
    "            spell_name=spell.spell_name,\n"
    "            existence=spell.existence,\n"
    "            disposal_method_names=spell.disposal_method_names,\n"
    "        ) == spell.spell_id\n"
)
NEW = (
    "        # The spell_id is the class's code (S1 of EPIC-2026-10-18-spell_identity_is_the_code): no bind-time\n"
    "        # fact enters it - the resolved name, the existence and the disposal names belong to the Spell's\n"
    "        # binding manifest - so the inspector, given the class alone, answers the id bind gave.\n"
    "        assert Bind.spell_id_inspector(BasicService) == spell.spell_id\n"
)


def apply(applier) -> None:
    """The component-bind batch."""
    # One LF line (103, inside the replaced assertion) in a CRLF file, mixed in git's index too: written all CRLF.
    applier.normalize_mixed[COMPONENT_BIND] = "\r\n"
    applier.edit(COMPONENT_BIND, [(OLD, NEW)], "component bind")
