"""Unit tests for the seventh Existence member, `managed_spell_quantity` (STORY-2026-10-15-managed_existence_member)."""

from melder.aether.spellbook.existence.existence import Existence


def test_managed_spell_quantity_is_a_member_named_by_its_bare_name() -> None:
    """
    Purpose:
        The member exists and formats as its bare name, as every Existence member does.
    Contract:
        `str(Existence.managed_spell_quantity)` round-trips through `Existence[...]`.
    """
    member = Existence.managed_spell_quantity

    assert str(member) == "managed_spell_quantity"
    assert Existence[str(member)] is member


def test_managed_spell_quantity_is_appended_after_the_six_existing_members() -> None:
    """
    Purpose:
        The member is appended last, so no existing member's position moves.
    Contract:
        Declaration order is the six original members, then managed_spell_quantity.
    """
    assert [member.name for member in Existence] == [
        "unique",
        "unique_per_conduit",
        "many",
        "unique_per_conduit_cluster",
        "unique_per_conduit_lineage",
        "unique_per_spell_space",
        "managed_spell_quantity",
    ]


def test_existing_member_values_are_unchanged_by_the_seventh_member() -> None:
    """
    Purpose:
        Appending the member leaves every existing `auto()` value where it was.
    Contract:
        The six original members keep the values 1-6; the new member takes 7.
    """
    assert Existence.unique.value == 1
    assert Existence.unique_per_conduit.value == 2
    assert Existence.many.value == 3
    assert Existence.unique_per_conduit_cluster.value == 4
    assert Existence.unique_per_conduit_lineage.value == 5
    assert Existence.unique_per_spell_space.value == 6
    assert Existence.managed_spell_quantity.value == 7
