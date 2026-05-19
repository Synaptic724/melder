from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_validity import SpellValidity


def test_spell_validity_exposes_the_full_expected_member_set() -> None:
    """
    Verify the enum exposes the full documented validity vocabulary.

    Contract:
    - All six documented validity states exist.
    - No extra incidental members are present.
    """
    assert tuple(SpellValidity.__members__.keys()) == (
        "unknown",
        "valid",
        "gated",
        "invalid",
        "disabled",
        "cleaned",
    )


def test_spell_validity_terminal_states_are_distinct_enum_members() -> None:
    """
    Verify the terminal policy states remain distinct.

    Contract:
    - `disabled` and `cleaned` are separate terminal states, not aliases.
    - Each enum member keeps a unique value.
    """
    values = {member.value for member in SpellValidity}

    assert SpellValidity.disabled is not SpellValidity.cleaned
    assert SpellValidity.disabled.value != SpellValidity.cleaned.value
    assert len(values) == len(list(SpellValidity))
