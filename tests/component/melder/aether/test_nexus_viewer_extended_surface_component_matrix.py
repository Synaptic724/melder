import pytest

from melder.aether.nexus.acl.frame_acl_compiler import FrameACLCompiler
from melder.aether.nexus.acl.frame_acl_configuration import FrameACLConfiguration
from melder.aether.nexus.acl.configurations.frame_acl_view_configuration import (
    FrameACLViewConfiguration,
)
from melder.aether.nexus.acl.configurations.profiles.rules.frame_acl_ruleset import FrameACLRuleSet
from melder.aether.nexus.acl.configurations.profiles.view.frame_acl_view_profile import (
    FrameACLViewProfile,
)
from melder.aether.nexus.frame_acl_manager import FrameACLManager
from melder.aether.nexus.rift.frame_viewer.frame_viewer import FrameViewer
from tests._nexus_viewer_matrix_support import build_descriptor


def _profile_by_name(profile_name: str) -> FrameACLViewProfile:
    if profile_name == "safe":
        return FrameACLViewProfile.create_safe()
    if profile_name == "hybrid":
        return FrameACLViewProfile.create_hybrid()
    if profile_name == "permissive":
        return FrameACLViewProfile.create_permissive()
    raise ValueError(profile_name)


def _build_configuration(profile_name: str) -> FrameACLConfiguration:
    configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        FrameACLConfiguration.create_default("ops"),
        reason="extended_matrix",
    )
    configuration.set_view_configuration(
        FrameACLViewConfiguration.from_profile(
            _profile_by_name(profile_name),
            frame_override_ruleset=FrameACLRuleSet(
                "{0}_frame_override".format(profile_name),
                rules=[],
            ),
            conduit_override_ruleset=FrameACLRuleSet(
                "{0}_conduit_override".format(profile_name),
                rules=[],
            ),
            spell_override_ruleset=FrameACLRuleSet(
                "{0}_spell_override".format(profile_name),
                rules=[],
            ),
        )
    )
    configuration.finalize()
    return configuration


def _build_component_viewer(profile_name: str, payload_type: str) -> FrameViewer:
    manager = FrameACLManager()
    compiler = FrameACLCompiler(manager.frame_acl_profile_builder)
    descriptor = build_descriptor(
        "ops",
        spell_payload_types=(payload_type,),
        conduit_count=2,
        include_detail_dunders=(payload_type == "detailed"),
    )
    configuration = _build_configuration(profile_name)
    compiled_surface = compiler.compile_frame_access_surface(
        descriptor,
        configuration,
    )
    return FrameViewer(
        frame_descriptors_by_name={"ops": descriptor},
        frame_acl_configurations_by_frame_name={"ops": configuration},
        compiled_access_surfaces_by_frame_name={"ops": compiled_surface},
        default_view_frame_name="ops",
    )


def _build_component_kwargs(viewer: FrameViewer, method_name: str) -> dict[str, object]:
    conduit_id = viewer.execute_method(
        "list_targets",
        frame_name="ops",
        source_kind="conduit",
    )[0].source_id
    spell_source_id = viewer.execute_method(
        "list_targets",
        frame_name="ops",
        source_kind="spell",
    )[0].source_id
    if method_name in {
        "list_frame_ids",
        "list_nexus_contracts",
        "count_conduit_records",
        "count_spellbooks",
        "list_origin_spellbook_ids",
        "list_spell_record_ids",
        "list_spell_names",
        "list_binding_names",
        "list_lineage_ids",
        "list_permissions",
        "list_existence_kinds",
        "describe_descriptor_inventory",
    }:
        return {}
    if method_name in {
        "describe_descriptor_topology",
        "describe_conduit_records",
        "describe_spell_records",
        "describe_visible_surface",
        "describe_visible_inventory_by_kind",
        "describe_frame_topology",
    }:
        return {"frame_name": "ops"}
    if method_name == "describe_spell_record":
        return {"spell_source_id": spell_source_id}
    if method_name in {
        "describe_conduit_inventory",
        "describe_conduit_relationships",
        "describe_conduit_access_summary",
    }:
        return {"frame_name": "ops", "conduit_id": conduit_id}
    if method_name in {
        "describe_spell_identity",
        "describe_spell_origin",
        "describe_spell_lineage",
        "describe_spell_binding",
        "describe_spell_resolution",
        "describe_spell_metadata",
        "describe_spell_class_profile",
        "describe_spell_callable_profile",
        "describe_spell_instance_members",
        "describe_spell_dynamic_access",
        "describe_spell_dunder_members",
        "describe_spell_access_summary",
    }:
        return {"frame_name": "ops", "spell_source_id": spell_source_id}
    raise ValueError(method_name)


COMPONENT_METHOD_CASES = [
    ("list_frame_ids", "list"),
    ("list_nexus_contracts", "list"),
    ("count_conduit_records", "int"),
    ("count_spellbooks", "int"),
    ("list_origin_spellbook_ids", "list"),
    ("list_spell_record_ids", "list"),
    ("list_spell_names", "list"),
    ("list_binding_names", "list"),
    ("list_lineage_ids", "list"),
    ("list_permissions", "list"),
    ("list_existence_kinds", "list"),
    ("describe_descriptor_inventory", "dict"),
    ("describe_descriptor_topology", "dict"),
    ("describe_conduit_records", "list"),
    ("describe_spell_records", "list"),
    ("describe_spell_record", "dict"),
    ("describe_visible_surface", "dict"),
    ("describe_visible_inventory_by_kind", "dict"),
    ("describe_frame_topology", "dict"),
    ("describe_conduit_inventory", "dict"),
]

COMPONENT_SCENARIOS = [
    ("safe", "general"),
    ("hybrid", "general"),
    ("hybrid", "detailed"),
    ("permissive", "detailed"),
]


@pytest.mark.parametrize(("method_name", "expected_type"), COMPONENT_METHOD_CASES)
@pytest.mark.parametrize(("profile_name", "payload_type"), COMPONENT_SCENARIOS)
def test_component_viewer_extended_surface_matrix(
        method_name: str,
        expected_type: str,
        profile_name: str,
        payload_type: str,
) -> None:
    viewer = _build_component_viewer(profile_name, payload_type)

    result = viewer.execute_method(
        method_name,
        **_build_component_kwargs(viewer, method_name),
    )

    if expected_type == "dict":
        assert isinstance(result, dict)
    elif expected_type == "list":
        assert isinstance(result, list)
    elif expected_type == "int":
        assert isinstance(result, int)
    else:
        raise AssertionError(expected_type)
