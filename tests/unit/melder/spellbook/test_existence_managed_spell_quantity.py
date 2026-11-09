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


def test_historical_numeric_values_reconstruct_the_same_members() -> None:
    """
    Purpose:
        Preserve the original number-to-member mapping after string migration.
    Contract:
        Direct values equal member names; old numbers 1-7 still reconstruct the
        same six original members and appended managed member.
    """
    assert Existence(1) is Existence.unique
    assert Existence(2) is Existence.unique_per_conduit
    assert Existence(3) is Existence.many
    assert Existence(4) is Existence.unique_per_conduit_cluster
    assert Existence(5) is Existence.unique_per_conduit_lineage
    assert Existence(6) is Existence.unique_per_spell_space
    assert Existence(7) is Existence.managed_spell_quantity
    assert all(member.value == member.name for member in Existence)
