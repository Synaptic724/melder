import pytest

from tests._nexus_viewer_matrix_support import build_spell_record_key, build_viewer


def _visible_viewer(*, include_dunders: bool = False):
    return build_viewer(
        "ops",
        spell_payload_types=("general", "detailed"),
        conduit_count=2,
        visible_conduit_ids=("ops-conduit-1", "ops-conduit-2"),
        visible_spell_keys=(
            build_spell_record_key("ops", 1),
            build_spell_record_key("ops", 2),
        ),
        conduit_sections_by_id={
            "ops-conduit-1": (
                "conduit_name",
                "conduit_state",
                "policy",
                "peer_conduit_ids",
            ),
            "ops-conduit-2": (
                "conduit_name",
                "conduit_state",
                "policy",
                "peer_conduit_ids",
            ),
        },
        spell_sections_by_key={
            build_spell_record_key("ops", 1): (
                "binding_payload",
                "resolution_payload",
                "metadata",
            ),
            build_spell_record_key("ops", 2): (
                "binding_payload",
                "resolution_payload",
                "metadata",
                "class_profile",
                "callable_profile",
                "instance_members",
                "dynamic_access",
            ),
        },
        frame_payload_fields=(
            "system_state",
            "rift_enabled",
            "ai_native_enabled",
            "root_conduit_count",
            "conduit_cloud_entry_count",
        ),
        include_detail_dunders=include_dunders,
    )


FRAME_COLLECTION_CASES = [
    ("list_visible_conduit_ids", (), ["ops-conduit-1", "ops-conduit-2"]),
    ("list_visible_spell_source_ids", (), ["ops-spellbook:ops-spell-1", "ops-spellbook:ops-spell-2"]),
    ("list_visible_binding_names", (), ["ops_spell_1", "ops_spell_2"]),
    ("list_visible_spell_names", (), ["OpsSpell1", "OpsSpell2"]),
    ("list_visible_spellframes", (), []),
    ("list_visible_lineage_ids", (), ["ops-lineage-1", "ops-lineage-2"]),
    ("list_visible_target_ids", (), [
        "ops:frame:ops-frame",
        "ops:conduit:ops-conduit-1",
        "ops:conduit:ops-conduit-2",
        "ops:spell:ops-spellbook:ops-spell-1",
        "ops:spell:ops-spellbook:ops-spell-2",
    ]),
    ("list_visible_target_ids", ("conduit",), ["ops:conduit:ops-conduit-1", "ops:conduit:ops-conduit-2"]),
    ("list_visible_target_ids", ("spell",), ["ops:spell:ops-spellbook:ops-spell-1", "ops:spell:ops-spellbook:ops-spell-2"]),
]


@pytest.mark.parametrize(("method_name", "args", "expected"), FRAME_COLLECTION_CASES)
def test_view_frame_collection_matrix(method_name, args, expected) -> None:
    view_frame = _visible_viewer().get_selected_profile_for_frame("ops").view_frame

    result = getattr(view_frame, method_name)(source_kind=args[0]) if method_name == "list_visible_target_ids" and len(args) == 1 else getattr(view_frame, method_name)()

    assert result == expected


FRAME_DICT_CASES = [
    (
        "list_visible_target_ids_by_kind",
        {
            "conduit": ("ops:conduit:ops-conduit-1", "ops:conduit:ops-conduit-2"),
            "frame": ("ops:frame:ops-frame",),
            "spell": (
                "ops:spell:ops-spellbook:ops-spell-1",
                "ops:spell:ops-spellbook:ops-spell-2",
            ),
        },
    ),
    (
        "describe_visible_spell_ownership",
        {
            "ops-conduit-1": ("ops-spellbook:ops-spell-1",),
            "ops-conduit-2": ("ops-spellbook:ops-spell-2",),
        },
    ),
    (
        "describe_visible_conduit_tree",
        {
            "ops-conduit-1": ("ops-conduit-1",),
            "ops-conduit-2": ("ops-conduit-2",),
        },
    ),
]


@pytest.mark.parametrize(("method_name", "expected"), FRAME_DICT_CASES)
def test_view_frame_dict_methods_matrix(method_name, expected) -> None:
    view_frame = _visible_viewer().get_selected_profile_for_frame("ops").view_frame

    assert getattr(view_frame, method_name)() == expected


FRAME_SEARCH_CASES = [
    ("search_targets_contains", {"text": "ops"}, ["frame", "conduit", "conduit", "spell", "spell"]),
    ("search_targets_contains", {"text": "spell"}, ["spell", "spell"]),
    ("search_targets_contains", {"text": "conduit-1"}, ["conduit"]),
    ("search_targets_contains", {"text": "root_1"}, ["conduit"]),
    ("search_targets_contains", {"text": "ops_spell_2"}, ["spell"]),
    ("search_targets_contains", {"text": "spell", "source_kind": "spell"}, ["spell", "spell"]),
    ("search_targets_contains", {"text": "root", "source_kind": "conduit"}, ["conduit", "conduit"]),
    ("search_targets_prefix", {"prefix": "ops"}, ["frame", "conduit", "conduit", "spell", "spell"]),
    ("search_targets_prefix", {"prefix": "ops-spellbook"}, ["spell", "spell"]),
    ("search_targets_prefix", {"prefix": "root", "source_kind": "conduit"}, ["conduit", "conduit"]),
    ("search_targets_prefix", {"prefix": "ops_spell_1", "source_kind": "spell"}, ["spell"]),
    ("search_targets_prefix", {"prefix": "ops-frame"}, ["frame"]),
]


@pytest.mark.parametrize(("method_name", "kwargs", "expected_kinds"), FRAME_SEARCH_CASES)
def test_view_frame_search_matrix(method_name, kwargs, expected_kinds) -> None:
    view_frame = _visible_viewer().get_selected_profile_for_frame("ops").view_frame

    results = getattr(view_frame, method_name)(**kwargs)

    assert [result.source_kind for result in results] == expected_kinds


FRAME_SEARCH_FILTER_CASES = [
    ("search_targets_contains", {"text": "ops", "source_kind": "frame"}, ["frame"]),
    ("search_targets_contains", {"text": "ops", "source_kind": "conduit"}, ["conduit", "conduit"]),
    ("search_targets_contains", {"text": "ops", "source_kind": "spell"}, ["spell", "spell"]),
    ("search_targets_contains", {"text": "root_1", "source_kind": "conduit"}, ["conduit"]),
    ("search_targets_contains", {"text": "spell-2", "source_kind": "spell"}, ["spell"]),
    ("search_targets_prefix", {"prefix": "ops", "source_kind": "frame"}, ["frame"]),
    ("search_targets_prefix", {"prefix": "ops", "source_kind": "conduit"}, ["conduit", "conduit"]),
    ("search_targets_prefix", {"prefix": "ops", "source_kind": "spell"}, ["spell", "spell"]),
    ("search_targets_prefix", {"prefix": "root_2", "source_kind": "conduit"}, ["conduit"]),
    ("search_targets_prefix", {"prefix": "ops_spell_2", "source_kind": "spell"}, ["spell"]),
]


@pytest.mark.parametrize(("method_name", "kwargs", "expected_kinds"), FRAME_SEARCH_FILTER_CASES)
def test_view_frame_search_filtered_matrix(method_name, kwargs, expected_kinds) -> None:
    view_frame = _visible_viewer().get_selected_profile_for_frame("ops").view_frame

    results = getattr(view_frame, method_name)(**kwargs)

    assert [result.source_kind for result in results] == expected_kinds


FRAME_IDENTITY_CASES = [
    ("frame", "ops-frame", "ops", None),
    ("conduit", "ops-conduit-1", "root_1", None),
    ("conduit", "ops-conduit-2", "root_2", None),
    ("spell", "ops-spellbook:ops-spell-1", "ops_spell_1", "general"),
    ("spell", "ops-spellbook:ops-spell-2", "ops_spell_2", "detailed"),
]


@pytest.mark.parametrize(("source_kind", "source_id", "display_name", "payload_type"), FRAME_IDENTITY_CASES)
def test_view_frame_identity_matrix(source_kind, source_id, display_name, payload_type) -> None:
    view_frame = _visible_viewer(include_dunders=True).get_selected_profile_for_frame("ops").view_frame

    identity = view_frame.describe_target_identity(
        source_kind=source_kind,
        source_id=source_id,
    )

    assert identity["source_kind"] == source_kind
    assert identity["source_id"] == source_id
    assert identity["display_name"] == display_name
    if payload_type is not None:
        assert identity["payload_type"] == payload_type


FRAME_SUMMARY_CASES = [
    ("describe_visible_surface", "frame_name", "ops"),
    ("describe_visible_surface", "access_contract", "dict"),
    ("describe_visible_surface", "visible_root_conduit_ids", ("ops-conduit-1", "ops-conduit-2")),
    ("describe_visible_inventory_by_kind", "frame", 1),
    ("describe_visible_inventory_by_kind", "conduit", 2),
    ("describe_visible_inventory_by_kind", "spell", 2),
    ("describe_frame_topology", "root_conduit_ids", ("ops-conduit-1", "ops-conduit-2")),
    ("describe_frame_topology", "visible_spell_source_ids", ("ops-spellbook:ops-spell-1", "ops-spellbook:ops-spell-2")),
]


@pytest.mark.parametrize(("method_name", "key", "expected"), FRAME_SUMMARY_CASES)
def test_view_frame_summary_matrix(method_name, key, expected) -> None:
    view_frame = _visible_viewer().get_selected_profile_for_frame("ops").view_frame
    result = getattr(view_frame, method_name)()

    if expected == "dict":
        assert isinstance(result[key], dict)
    elif isinstance(result[key], dict):
        assert result[key]["count"] == expected
    else:
        assert result[key] == expected


CONDUIT_CASES = [
    ("list_root_conduits", (), ["ops-conduit-1", "ops-conduit-2"]),
    ("is_root_conduit", ("ops-conduit-1",), True),
    ("is_root_conduit", ("ops-conduit-2",), True),
    ("get_root_conduit_id", ("ops-conduit-1",), "ops-conduit-1"),
    ("get_root_conduit_id", ("ops-conduit-2",), "ops-conduit-2"),
    ("list_conduits_by_root_id", ("ops-conduit-1",), ["ops-conduit-1"]),
    ("list_conduits_by_root_id", ("ops-conduit-2",), ["ops-conduit-2"]),
    ("list_conduits_by_policy", ("default",), ["ops-conduit-1", "ops-conduit-2"]),
    ("list_conduits_by_state", ("normal",), ["ops-conduit-1", "ops-conduit-2"]),
    ("list_peer_conduit_ids", ("ops-conduit-1",), ("ops-conduit-2",)),
    ("list_peer_conduit_ids", ("ops-conduit-2",), ("ops-conduit-1",)),
    ("list_spell_source_ids_for_conduit", ("ops-conduit-1",), ("ops-spellbook:ops-spell-1",)),
    ("list_spell_source_ids_for_conduit", ("ops-conduit-2",), ("ops-spellbook:ops-spell-2",)),
    ("list_binding_names_for_conduit", ("ops-conduit-1",), ("ops_spell_1",)),
    ("list_binding_names_for_conduit", ("ops-conduit-2",), ("ops_spell_2",)),
    ("list_spell_names_for_conduit", ("ops-conduit-1",), ("OpsSpell1",)),
    ("list_spell_names_for_conduit", ("ops-conduit-2",), ("OpsSpell2",)),
]


@pytest.mark.parametrize(("method_name", "args", "expected"), CONDUIT_CASES)
def test_view_conduit_collection_matrix(method_name, args, expected) -> None:
    view_conduit = _visible_viewer().get_selected_profile_for_frame("ops").view_conduit

    result = getattr(view_conduit, method_name)(*args)

    if isinstance(result, list) and len(result) > 0 and hasattr(result[0], "source_id"):
        assert [item.source_id for item in result] == expected
    else:
        assert result == expected


CONDUIT_SUMMARY_CASES = [
    ("describe_conduit_inventory", "ops-conduit-1", "spell_count", 1),
    ("describe_conduit_inventory", "ops-conduit-1", "peer_count", 1),
    ("describe_conduit_inventory", "ops-conduit-2", "spell_count", 1),
    ("describe_conduit_inventory", "ops-conduit-2", "peer_count", 1),
    ("describe_conduit_relationships", "ops-conduit-1", "root_conduit_id", "ops-conduit-1"),
    ("describe_conduit_relationships", "ops-conduit-1", "spell_source_ids", ("ops-spellbook:ops-spell-1",)),
    ("describe_conduit_relationships", "ops-conduit-2", "root_conduit_id", "ops-conduit-2"),
    ("describe_conduit_relationships", "ops-conduit-2", "spell_source_ids", ("ops-spellbook:ops-spell-2",)),
    ("describe_conduit_access_summary", "ops-conduit-1", "conduit_id", "ops-conduit-1"),
    ("describe_conduit_access_summary", "ops-conduit-2", "conduit_id", "ops-conduit-2"),
]


@pytest.mark.parametrize(("method_name", "conduit_id", "key", "expected"), CONDUIT_SUMMARY_CASES)
def test_view_conduit_summary_matrix(method_name, conduit_id, key, expected) -> None:
    view_conduit = _visible_viewer().get_selected_profile_for_frame("ops").view_conduit

    result = getattr(view_conduit, method_name)(conduit_id)

    assert result[key] == expected


CONDUIT_EXTRA_CASES = [
    ("list_peer_conduits", "ops-conduit-1", ["ops-conduit-2"]),
    ("list_peer_conduits", "ops-conduit-2", ["ops-conduit-1"]),
    ("list_conduit_spells", "ops-conduit-1", ["ops-spellbook:ops-spell-1"]),
    ("list_conduit_spells", "ops-conduit-2", ["ops-spellbook:ops-spell-2"]),
    ("find_conduit_by_name", "root_1", ["ops-conduit-1"]),
    ("find_conduit_by_name", "root_2", ["ops-conduit-2"]),
    ("explain_conduit_access", "ops-conduit-1", True),
    ("explain_conduit_access", "ops-conduit-2", True),
]


@pytest.mark.parametrize(("method_name", "arg", "expected"), CONDUIT_EXTRA_CASES)
def test_view_conduit_extra_matrix(method_name, arg, expected) -> None:
    view_conduit = _visible_viewer().get_selected_profile_for_frame("ops").view_conduit

    result = getattr(view_conduit, method_name)(arg)

    if isinstance(expected, list):
        assert [item.source_id for item in result] == expected
    else:
        assert result["visible"] is expected


SPELL_SIMPLE_CASES = [
    ("describe_spell_identity", "ops-spellbook:ops-spell-1", "payload_type", "general"),
    ("describe_spell_identity", "ops-spellbook:ops-spell-2", "payload_type", "detailed"),
    ("describe_spell_origin", "ops-spellbook:ops-spell-1", "owner_conduit_id", "ops-conduit-1"),
    ("describe_spell_origin", "ops-spellbook:ops-spell-2", "owner_conduit_id", "ops-conduit-2"),
    ("describe_spell_lineage", "ops-spellbook:ops-spell-1", "spell_index_id", "ops-lineage-1"),
    ("describe_spell_lineage", "ops-spellbook:ops-spell-2", "spell_index_id", "ops-lineage-2"),
    ("describe_spell_binding", "ops-spellbook:ops-spell-1", "binding_name", "ops_spell_1"),
    ("describe_spell_binding", "ops-spellbook:ops-spell-2", "binding_name", "ops_spell_2"),
    ("describe_spell_resolution", "ops-spellbook:ops-spell-1", "requirement_count", 1),
    ("describe_spell_resolution", "ops-spellbook:ops-spell-2", "requirement_count", 1),
    ("describe_spell_metadata", "ops-spellbook:ops-spell-1", "metadata_visible", True),
    ("describe_spell_metadata", "ops-spellbook:ops-spell-2", "metadata_visible", True),
]


@pytest.mark.parametrize(("method_name", "spell_source_id", "key", "expected"), SPELL_SIMPLE_CASES)
def test_view_spell_identity_origin_matrix(method_name, spell_source_id, key, expected) -> None:
    view_spell = _visible_viewer(include_dunders=True).get_selected_profile_for_frame("ops").view_spell

    result = getattr(view_spell, method_name)(spell_source_id)

    assert result[key] == expected


SPELL_FILTER_CASES = [
    ("list_spells_by_owner_conduit", ("ops-conduit-1",), ["ops-spellbook:ops-spell-1"]),
    ("list_spells_by_owner_conduit", ("ops-conduit-2",), ["ops-spellbook:ops-spell-2"]),
    ("list_spells_by_spellbook_id", ("ops-spellbook",), ["ops-spellbook:ops-spell-1", "ops-spellbook:ops-spell-2"]),
    ("list_spells_by_lineage_id", ("ops-lineage-1",), ["ops-spellbook:ops-spell-1"]),
    ("list_spells_by_lineage_id", ("ops-lineage-2",), ["ops-spellbook:ops-spell-2"]),
    ("list_spells_by_permission", ("create",), ["ops-spellbook:ops-spell-1", "ops-spellbook:ops-spell-2"]),
    ("list_spells_by_existence", ("unique",), ["ops-spellbook:ops-spell-1", "ops-spellbook:ops-spell-2"]),
    ("list_spells_by_spell_name", ("OpsSpell1",), ["ops-spellbook:ops-spell-1"]),
    ("list_spells_by_spell_name", ("OpsSpell2",), ["ops-spellbook:ops-spell-2"]),
    ("list_spells_by_spellframe", ("LogicFrame",), []),
    ("find_spell_by_binding_name", ("ops_spell_1",), ["ops-spellbook:ops-spell-1"]),
    ("find_spell_by_binding_name", ("ops_spell_2",), ["ops-spellbook:ops-spell-2"]),
    ("list_spells_by_payload_type", ("general",), ["ops-spellbook:ops-spell-1"]),
    ("list_spells_by_payload_type", ("detailed",), ["ops-spellbook:ops-spell-2"]),
    ("search_spells_contains", ("ops",), ["ops-spellbook:ops-spell-1", "ops-spellbook:ops-spell-2"]),
    ("search_spells_contains", ("spell-1",), ["ops-spellbook:ops-spell-1"]),
    ("search_spells_contains", ("OpsSpell2",), ["ops-spellbook:ops-spell-2"]),
    ("search_spells_prefix", ("ops",), ["ops-spellbook:ops-spell-1", "ops-spellbook:ops-spell-2"]),
    ("search_spells_prefix", ("ops_spell_1",), ["ops-spellbook:ops-spell-1"]),
    ("search_spells_prefix", ("ops-spellbook:ops-spell-2",), ["ops-spellbook:ops-spell-2"]),
]


@pytest.mark.parametrize(("method_name", "args", "expected_source_ids"), SPELL_FILTER_CASES)
def test_view_spell_filter_matrix(method_name, args, expected_source_ids) -> None:
    view_spell = _visible_viewer(include_dunders=True).get_selected_profile_for_frame("ops").view_spell

    results = getattr(view_spell, method_name)(*args)

    assert [result.source_id for result in results] == expected_source_ids


SPELL_DETAIL_CASES = [
    ("describe_spell_class_profile", "ops-spellbook:ops-spell-1", "reason", "payload_not_detailed"),
    ("describe_spell_class_profile", "ops-spellbook:ops-spell-2", "detail_available", True),
    ("describe_spell_callable_profile", "ops-spellbook:ops-spell-1", "reason", "payload_not_detailed"),
    ("describe_spell_callable_profile", "ops-spellbook:ops-spell-2", "detail_available", True),
    ("describe_spell_instance_members", "ops-spellbook:ops-spell-1", "reason", "payload_not_detailed"),
    ("describe_spell_instance_members", "ops-spellbook:ops-spell-2", "detail_available", True),
    ("describe_spell_dynamic_access", "ops-spellbook:ops-spell-1", "reason", "payload_not_detailed"),
    ("describe_spell_dynamic_access", "ops-spellbook:ops-spell-2", "detail_available", True),
    ("describe_spell_access_summary", "ops-spellbook:ops-spell-1", "identity", "dict"),
    ("describe_spell_access_summary", "ops-spellbook:ops-spell-2", "detail", "dict"),
]


@pytest.mark.parametrize(("method_name", "spell_source_id", "key", "expected"), SPELL_DETAIL_CASES)
def test_view_spell_detail_matrix(method_name, spell_source_id, key, expected) -> None:
    view_spell = _visible_viewer(include_dunders=True).get_selected_profile_for_frame("ops").view_spell

    result = getattr(view_spell, method_name)(spell_source_id)

    if expected == "dict":
        assert isinstance(result[key], dict)
    else:
        assert result[key] == expected


def test_view_spell_dunder_methods_surface_visible_dunders() -> None:
    view_spell = _visible_viewer(include_dunders=True).get_selected_profile_for_frame("ops").view_spell

    assert view_spell.describe_spell_dunder_members("ops-spellbook:ops-spell-2") == {
        "source_id": "ops-spellbook:ops-spell-2",
        "detail_available": True,
        "class_member_names": ("__dict__",),
        "class_method_names": ("__enter__",),
        "instance_member_names": ("__dict__",),
    }
    assert view_spell.list_spell_dunder_member_names("ops-spellbook:ops-spell-2") == (
        "__dict__",
        "__enter__",
    )


SPELL_SECTION_CASES = [
    ("describe_spell_class_profile", "ops-spellbook:ops-spell-2", "payload", "member_names", ("__dict__", "state")),
    ("describe_spell_class_profile", "ops-spellbook:ops-spell-2", "payload", "method_names", ("__enter__", "run")),
    ("describe_spell_class_profile", "ops-spellbook:ops-spell-2", "payload", "dunder_member_names", ("__dict__",)),
    ("describe_spell_class_profile", "ops-spellbook:ops-spell-2", "payload", "dunder_method_names", ("__enter__",)),
    ("describe_spell_callable_profile", "ops-spellbook:ops-spell-2", "payload", "signature", "() -> None"),
    ("describe_spell_instance_members", "ops-spellbook:ops-spell-2", "payload", "__dict__", {"type": "dict", "is_dunder": True}),
    ("describe_spell_instance_members", "ops-spellbook:ops-spell-2", "payload", "state", {"type": "str", "is_dunder": False}),
    ("describe_spell_dynamic_access", "ops-spellbook:ops-spell-2", "payload", "has_getattr", False),
]


@pytest.mark.parametrize(("method_name", "spell_source_id", "section_name", "field_name", "expected"), SPELL_SECTION_CASES)
def test_view_spell_detail_section_matrix(method_name, spell_source_id, section_name, field_name, expected) -> None:
    view_spell = _visible_viewer(include_dunders=True).get_selected_profile_for_frame("ops").view_spell

    result = getattr(view_spell, method_name)(spell_source_id)

    assert result[section_name][field_name] == expected


ROUTE_CASES = [
    ("list_frame_ids", {}, "list"),
    ("list_nexus_contracts", {}, "list"),
    ("count_conduit_records", {}, "int"),
    ("describe_descriptor_inventory", {}, "dict"),
    ("describe_descriptor_topology", {"frame_name": "ops"}, "dict"),
    ("describe_conduit_records", {"frame_name": "ops"}, "list"),
    ("describe_spell_records", {"frame_name": "ops"}, "list"),
    ("describe_spell_record", {"spell_source_id": "ops-spellbook:ops-spell-1"}, "dict"),
    ("describe_visible_surface", {"frame_name": "ops"}, "dict"),
    ("describe_visible_inventory_by_kind", {"frame_name": "ops"}, "dict"),
    ("describe_frame_topology", {"frame_name": "ops"}, "dict"),
    ("search_targets_contains", {"frame_name": "ops", "text": "spell"}, "list"),
    ("describe_target_identity", {"frame_name": "ops", "source_kind": "spell", "source_id": "ops-spellbook:ops-spell-1"}, "dict"),
    ("describe_conduit_inventory", {"frame_name": "ops", "conduit_id": "ops-conduit-1"}, "dict"),
    ("describe_conduit_relationships", {"frame_name": "ops", "conduit_id": "ops-conduit-1"}, "dict"),
    ("describe_conduit_access_summary", {"frame_name": "ops", "conduit_id": "ops-conduit-1"}, "dict"),
    ("describe_spell_identity", {"frame_name": "ops", "spell_source_id": "ops-spellbook:ops-spell-1"}, "dict"),
    ("describe_spell_origin", {"frame_name": "ops", "spell_source_id": "ops-spellbook:ops-spell-1"}, "dict"),
    ("describe_spell_lineage", {"frame_name": "ops", "spell_source_id": "ops-spellbook:ops-spell-1"}, "dict"),
    ("describe_spell_binding", {"frame_name": "ops", "spell_source_id": "ops-spellbook:ops-spell-1"}, "dict"),
    ("describe_spell_resolution", {"frame_name": "ops", "spell_source_id": "ops-spellbook:ops-spell-1"}, "dict"),
    ("describe_spell_metadata", {"frame_name": "ops", "spell_source_id": "ops-spellbook:ops-spell-1"}, "dict"),
    ("describe_spell_class_profile", {"frame_name": "ops", "spell_source_id": "ops-spellbook:ops-spell-2"}, "dict"),
    ("describe_spell_callable_profile", {"frame_name": "ops", "spell_source_id": "ops-spellbook:ops-spell-2"}, "dict"),
    ("describe_spell_instance_members", {"frame_name": "ops", "spell_source_id": "ops-spellbook:ops-spell-2"}, "dict"),
    ("describe_spell_dynamic_access", {"frame_name": "ops", "spell_source_id": "ops-spellbook:ops-spell-2"}, "dict"),
    ("describe_spell_dunder_members", {"frame_name": "ops", "spell_source_id": "ops-spellbook:ops-spell-2"}, "dict"),
    ("list_spell_dunder_member_names", {"frame_name": "ops", "spell_source_id": "ops-spellbook:ops-spell-2"}, "tuple"),
    ("describe_spell_access_summary", {"frame_name": "ops", "spell_source_id": "ops-spellbook:ops-spell-2"}, "dict"),
]


@pytest.mark.parametrize(("method_name", "kwargs", "expected_type"), ROUTE_CASES * 2)
def test_execute_method_extended_route_matrix(method_name, kwargs, expected_type) -> None:
    viewer = _visible_viewer(include_dunders=True)

    result = viewer.execute_method(method_name, **kwargs)

    if expected_type == "dict":
        assert isinstance(result, dict)
    elif expected_type == "list":
        assert isinstance(result, list)
    elif expected_type == "tuple":
        assert isinstance(result, tuple)
    elif expected_type == "int":
        assert isinstance(result, int)
    else:
        raise AssertionError(expected_type)


HOST_ROUTE_CASES = [
    ("list_frame_ids", {}, "list"),
    ("list_nexus_contracts", {}, "list"),
    ("count_conduit_records", {}, "int"),
    ("count_spellbooks", {}, "int"),
    ("list_origin_spellbook_ids", {}, "list"),
    ("list_spell_record_ids", {}, "list"),
    ("list_spell_names", {}, "list"),
    ("list_binding_names", {}, "list"),
    ("list_lineage_ids", {}, "list"),
    ("list_permissions", {}, "list"),
    ("list_existence_kinds", {}, "list"),
    ("describe_descriptor_inventory", {}, "dict"),
    ("describe_descriptor_topology", {"frame_name": "ops"}, "dict"),
    ("describe_conduit_records", {"frame_name": "ops"}, "list"),
    ("describe_spell_records", {"frame_name": "ops"}, "list"),
    ("describe_spell_record", {"spell_source_id": "ops-spellbook:ops-spell-1"}, "dict"),
    ("list_spells_by_owner_conduit", {"conduit_id": "ops-conduit-1"}, "list"),
    ("list_spells_by_spellbook_id", {"spellbook_id": "ops-spellbook"}, "list"),
    ("list_spells_by_permission", {"permission_name": "create"}, "list"),
    ("list_spells_by_existence", {"existence_name": "unique"}, "list"),
    ("list_spells_by_spellframe", {"spellframe_name": "LogicFrame"}, "list"),
]


@pytest.mark.parametrize(("method_name", "kwargs", "expected_type"), HOST_ROUTE_CASES * 2)
def test_execute_method_host_route_matrix(method_name, kwargs, expected_type) -> None:
    viewer = _visible_viewer(include_dunders=True)

    result = viewer.execute_method(method_name, **kwargs)

    if expected_type == "dict":
        assert isinstance(result, dict)
    elif expected_type == "list":
        assert isinstance(result, list)
    elif expected_type == "int":
        assert isinstance(result, int)
    else:
        raise AssertionError(expected_type)
