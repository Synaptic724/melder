from melder.spellbook.existence.existence import Existence
from melder.spellbook.resolution_style_matrix import ResolutionStyleMatrix
from melder.spellbook.spell_types.spell_types import SpellType


def test_resolution_style_matrix_validate_has_no_errors() -> None:
    """
    Purpose:
        Validate the canonical resolution matrix against current enum surfaces.
    Contract:
        - validate() returns no errors for current matrix state.
    """
    assert ResolutionStyleMatrix.validate() == ()


def test_resolution_style_matrix_has_entry_for_every_spell_type() -> None:
    """
    Purpose:
        Verify each SpellType is represented exactly once in the matrix.
    Contract:
        - Matrix keys match SpellType names.
    """
    matrix_names = set(ResolutionStyleMatrix.get_matrix_by_spell_type().keys())
    enum_names = {spell_type.name for spell_type in SpellType}
    assert matrix_names == enum_names


def test_resolution_style_matrix_classifies_all_existence_modes_per_entry() -> None:
    """
    Purpose:
        Verify each matrix entry fully classifies Existence names.
    Contract:
        - supported + unsupported covers all existence names.
        - supported and unsupported do not overlap.
    """
    expected_names = {existence.name for existence in Existence}
    for entry in ResolutionStyleMatrix.get_matrix_by_spell_type().values():
        supported = set(entry["supported"])
        unsupported = set(entry["unsupported"])
        assert supported.isdisjoint(unsupported)
        assert supported.union(unsupported) == expected_names


def test_resolution_style_matrix_spell_type_view_is_derived_projection() -> None:
    """
    Purpose:
        Keep SpellType matrix as a family-policy projection, not source-of-truth.
    Contract:
        - Snapshot and generated SpellType views are equal.
    """
    derived = ResolutionStyleMatrix.get_matrix_by_spell_type()
    assert ResolutionStyleMatrix.MATRIX_BY_SPELL_TYPE == derived


def test_resolution_style_matrix_contract_status_f_is_unsupported() -> None:
    """
    Purpose:
        Lock F-section support status to unsupported.
    Contract:
        - Contract item F is explicitly tracked as unsupported.
    """
    assert ResolutionStyleMatrix.get_contract_item_status("F") == "unsupported"


def test_resolution_style_matrix_contract_status_out_of_scope_items() -> None:
    """
    Purpose:
        Lock explicit out-of-scope contract items.
    Contract:
        - B4 and C2 remain out_of_scope.
    """
    assert ResolutionStyleMatrix.get_contract_item_status("B4") == "out_of_scope"
    assert ResolutionStyleMatrix.get_contract_item_status("C2") == "out_of_scope"


def test_resolution_style_matrix_family_policy_clarifies_class_vs_unique_only() -> None:
    """
    Purpose:
        Ensure family-level policy avoids misleading row-count interpretations.
    Contract:
        - Class family supports all Existence modes.
        - Callable and existing-object families are unique-only.
    """
    class_policy = ResolutionStyleMatrix.get_family_policy("class_based")
    callable_policy = ResolutionStyleMatrix.get_family_policy("callable_based")
    existing_policy = ResolutionStyleMatrix.get_family_policy("existing_object_based")

    all_existence_names = {existence.name for existence in Existence}
    assert set(class_policy["supported"]) == all_existence_names
    assert set(class_policy["unsupported"]) == set()
    assert set(callable_policy["supported"]) == {"unique"}
    assert set(existing_policy["supported"]) == {"unique"}
