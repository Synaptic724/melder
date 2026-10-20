"""melder_0, 2026-10-18: S1's batch for test_binding_profile_strategy.py. Its one test of the bind fingerprint keeps
its property on the code digest: a field typed with a TYPE_CHECKING-only name still counts in the spell_id, and
equal classes still get equal ids; it reads the id through `Bind.spell_id_inspector` instead of the removed
`Bind.sha256_profile`."""

STRATEGY = "tests/unit/melder/spellbook/spell_crafter/spell_examiner/strategies/test_binding_profile_strategy.py"

OLD = (
    "def test_bind_fingerprint_counts_fields_typed_with_type_checking_names() -> None:\n"
    "    \"\"\"\n"
    "    Purpose:\n"
    "        Verify the bind fingerprint changes when a TYPE_CHECKING-typed field is added.\n"
    "    Contract:\n"
    "        - Before 2026-09-26 both classes profiled with no annotations and hashed equal.\n"
    "        - Equal classes still hash equal.\n"
    "    Returns:\n"
    "        None.\n"
    "    \"\"\"\n"
    "    strategy = BindingProfileStrategy()\n\n"
    "    plain = Bind.sha256_profile(strategy._build_class_profile(_priced_class(False)))\n"
    "    again = Bind.sha256_profile(strategy._build_class_profile(_priced_class(False)))\n"
    "    extended = Bind.sha256_profile(strategy._build_class_profile(_priced_class(True)))\n"
)
NEW = (
    "def test_the_spell_id_counts_fields_typed_with_type_checking_names() -> None:\n"
    "    \"\"\"\n"
    "    Purpose:\n"
    "        Verify the spell_id changes when a TYPE_CHECKING-typed field is added.\n"
    "    Contract:\n"
    "        - Before 2026-09-26 both classes profiled with no annotations and hashed equal; since S1 of\n"
    "          EPIC-2026-10-18-spell_identity_is_the_code the spell_id is the class's code, which counts the\n"
    "          field without evaluating its annotation.\n"
    "        - Equal classes still get equal ids.\n"
    "    Returns:\n"
    "        None.\n"
    "    \"\"\"\n"
    "    plain = Bind.spell_id_inspector(_priced_class(False))\n"
    "    again = Bind.spell_id_inspector(_priced_class(False))\n"
    "    extended = Bind.spell_id_inspector(_priced_class(True))\n"
)


def apply(applier) -> None:
    """The binding-profile-strategy batch."""
    applier.edit(STRATEGY, [(OLD, NEW)], "profile strategy")
