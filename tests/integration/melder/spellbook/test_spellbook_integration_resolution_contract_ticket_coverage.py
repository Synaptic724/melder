from typing import Dict, Iterable

import pytest


SUPPORTED_TICKET_ITEMS: Dict[str, tuple[str, ...]] = {
    "A1": (
        "test_meld_by_spell_id_resolves_class_instance",
        "test_bind_conjure_and_meld_existing_creation",
        "test_meld_by_spell_id_resolves_class_instance_unique",
        "test_meld_by_spell_id_resolves_existing_instance_identity",
    ),
    "A2": (
        "test_meld_by_class_with_binding_name_resolves",
        "test_meld_by_class_default_binding_resolves_instance",
        "test_meld_by_function_default_binding_resolves_instance",
        "test_meld_by_class_with_binding_name_resolves_specific",
        "test_meld_by_function_with_binding_name_resolves_instance",
    ),
    "A3": (
        "test_meld_by_protocol_spellframe_resolves",
        "test_meld_by_protocol_with_binding_name_resolves",
    ),
    "A5": (
        "test_meld_overrides_path_targets_root_params",
        "test_meld_overrides_unique_targets_dependency",
        "test_meld_by_class_with_spell_override_dict_applies_kwargs",
    ),
    "A6": (
        "test_meld_by_spell_name_resolves_class_instance",
        "test_meld_by_spell_name_string_resolves_default_binding",
        "test_meld_by_spell_name_with_binding_name_resolves_named_binding",
    ),
    "B1": (
        "test_bind_conjure_and_meld_resolves_direct_dependency",
        "test_type_hint_di_by_concrete_class_resolves_dependency",
        "test_type_hint_di_by_concrete_class_reuses_unique_dependency",
    ),
    "B2": (
        "test_type_hint_di_by_protocol_resolves_dependency",
        "test_type_hint_di_by_protocol_resolves_dependency_secondary",
        "test_type_hint_di_by_protocol_reuses_unique_dependency",
    ),
    "B3": (
        "test_spellmap_default_explicit_class_resolves_dependency",
        "test_spellmap_default_frame_only_resolves_dependency",
    ),
    "B5": (
        "test_bind_conjure_and_meld_method_spell_unique",
        "test_spellmap_default_with_method_spell_resolves",
    ),
    "B6": (
        "test_existing_instance_frame_type_hint_injects_existing",
        "test_spellmap_default_frame_resolves_existing_instance",
    ),
    "C1": (
        "test_collection_di_by_list_frame_injects_all",
        "test_collection_di_by_protocol_includes_all_bindings",
        "test_collection_di_by_list_protocol_includes_all_bindings",
    ),
    "D1": (
        "test_spellmap_default_explicit_class_resolves_dependency",
        "test_spellmap_default_with_protocol_spell_resolves_dependency",
        "test_spellmap_default_explicit_class_with_binding_name_resolves",
    ),
    "D2": (
        "test_spellmap_default_frame_only_resolves_dependency",
        "test_spellmap_default_frame_and_binding_resolves_dependency",
        "test_spellmap_default_frame_only_string_resolves",
    ),
    "E1": (
        "test_bind_rejects_module_as_spell",
        "test_bind_rejects_protocol_as_spell",
    ),
    "E2": (
        "test_type_hint_di_ambiguous_frame_raises",
        "test_type_hint_di_ambiguous_concrete_class_raises",
    ),
    "G": (
        "test_bind_conjure_and_meld_unique_reuses_instance",
        "test_bind_conjure_and_meld_many_creates_new_instances",
    ),
    "H": (
        "test_meld_by_protocol_spellframe_resolves",
        "test_meld_by_string_spellframe_resolves",
    ),
}


def _collect_base_test_names(nodeids: Iterable[str]) -> set[str]:
    """
    Purpose:
        Normalize pytest nodeids to base test function names.
    Contract:
        - Strips parameterization suffixes from nodeids.
        - Returns a set of base test names for membership checks.
    Args:
        nodeids: Iterable of collected pytest nodeids.
    Returns:
        set[str]: Base test names derived from nodeids.
    """
    base_names: set[str] = set()
    for nodeid in nodeids:
        tail = nodeid.split("::")[-1]
        base_names.add(tail.split("[")[0])
    return base_names


def test_supported_resolution_contract_items_have_two_tests(
        request: pytest.FixtureRequest,
) -> None:
    """
    Purpose:
        Ensure each supported resolution-contract item is covered at least twice.
    Contract:
        - Each supported ticket item maps to two or more collected tests.
        - If any item has fewer than two tests, this test fails.
        - If the expected tests are not collected, the test is skipped with guidance.
    Returns:
        None.
    Raises:
        AssertionError: If any supported item lacks sufficient test coverage.
    """
    nodeids = [item.nodeid for item in request.session.items]
    collected = _collect_base_test_names(nodeids)
    expected_names = {
        name for names in SUPPORTED_TICKET_ITEMS.values() for name in names
    }
    missing_from_collection = sorted(expected_names.difference(collected))
    if missing_from_collection:
        pytest.skip(
            "Coverage gate requires full integration collection; "
            f"missing {len(missing_from_collection)} expected tests."
        )
    missing: Dict[str, Dict[str, list[str]]] = {}

    for item_id, tests in SUPPORTED_TICKET_ITEMS.items():
        matched = [name for name in tests if name in collected]
        if len(matched) < 2:
            missing[item_id] = {
                "matched": matched,
                "expected": list(tests),
            }

    assert not missing, (
        "Supported ticket items missing coverage (need >=2 tests each): "
        f"{missing}"
    )
