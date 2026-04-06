import json

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.aether.nexus.nexus import Nexus
from melder.spellbook.configuration.configuration import Configuration
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicService


@pytest.fixture(autouse=True)
def reset_singletons_for_frame_acl_chain_integration() -> None:
    """
    Reset singleton state around each integration test.

    Returns:
        None.
    """
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _make_rift_publishable_configuration(
        *,
        aetheric_frame: str,
) -> Configuration:
    """
    Build one Spellbook configuration that publishes Nexus passive state.

    Args:
        aetheric_frame:
            Target frame name.

    Returns:
        Configuration:
            Spellbook configuration suitable for passive Nexus publication.
    """
    configuration = Configuration(aether_frame=aetheric_frame)
    configuration.automatic_defaults()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    configuration.set_property("rift_enabled", True)
    return configuration


def _build_typed_json_payload(
        frame_name: str,
        *,
        view_profile_name: str = "safe",
        codegen_profile_name: str = "safe",
        marker: str = "integration",
) -> str:
    """
    Build one typed ACL JSON payload for integration chain tests.

    Args:
        frame_name:
            Frame name stored in the JSON payload.
        view_profile_name:
            Reusable view profile name for the payload.
        codegen_profile_name:
            Reusable codegen profile name for the payload.
        marker:
            Small marker used to vary the override ruleset name.

    Returns:
        str:
            JSON payload string that matches the live typed ACL contract.
    """
    return json.dumps(
        {
            "frame_name": frame_name,
            "view_configuration": {
                "profile_name": view_profile_name,
                "profile_version": "0.0.1",
                "minimum_spell_payload_type": "detailed",
                "frame_override_ruleset": {
                    "name": "frame_override_{0}".format(marker),
                    "rules": [],
                },
                "conduit_override_ruleset": {
                    "name": "conduit_override",
                    "rules": [],
                },
                "spell_override_ruleset": {
                    "name": "spell_override",
                    "rules": [],
                },
                "member_override_ruleset": {
                    "name": "member_override",
                    "rules": [],
                },
            },
            "codegen_configuration": {
                "profile_name": codegen_profile_name,
                "profile_version": "0.0.1",
                "frame_override_ruleset": {
                    "name": "frame_override",
                    "rules": [],
                },
                "conduit_override_ruleset": {
                    "name": "conduit_override",
                    "rules": [],
                },
                "spell_override_ruleset": {
                    "name": "spell_override",
                    "rules": [],
                },
                "capability_override_ruleset": {
                    "name": "capability_override",
                    "rules": [],
                },
            },
        },
        sort_keys=True,
    )


def test_integration_passive_publish_provisions_acl_container_and_default_chain() -> None:
    """
    Verify passive Nexus publish leaves the frame with a default ACL container
    and default chain state.

    Returns:
        None.
    """
    configuration = _make_rift_publishable_configuration(aetheric_frame="ops")
    spellbook = Spellbook(aetheric_frame="ops", configuration=configuration)
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        nexus = Nexus()
        container = nexus._frame_acl_manager._get_required_frame_acl_container("ops")

        assert container.frame_name == "ops"
        assert container.frame_acl_configuration_chain.count_configurations() == 1
        assert nexus.get_current_frame_acl_configuration("ops") is container.frame_acl_configuration
        assert nexus.get_frame_acl_builder("ops") is container.frame_acl_builder
    finally:
        conduit.cleanup()


def test_integration_nexus_facade_can_commit_and_rollback_chain_state_after_conjure() -> None:
    """
    Verify real runtime setup still allows the ACL chain to commit and roll
    back through the Nexus facade.

    Returns:
        None.
    """
    configuration = _make_rift_publishable_configuration(aetheric_frame="ops")
    spellbook = Spellbook(aetheric_frame="ops", configuration=configuration)
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        nexus = Nexus()
        original = nexus.get_current_frame_acl_configuration("ops")
        draft = nexus.create_new_from_acl_configuration(
            "ops",
            original.configuration_id,
            reason="integration-copy",
        )
        draft.set_json_configuration_string(
            _build_typed_json_payload(
                "ops",
                view_profile_name="hybrid",
                codegen_profile_name="permissive",
                marker="integration",
            )
        )
        draft.finalize()

        inserted = nexus.insert_head_frame_acl_configuration(
            "ops",
            draft,
            select_as_current=True,
        )
        selected = nexus.select_current_frame_acl_configuration(
            "ops",
            original.configuration_id,
        )
        rolled_back = nexus.rollback_frame_acl_configuration(
            "ops",
            inserted.configuration_id,
        )

        assert selected is original
        assert rolled_back is inserted
        assert nexus.get_head_frame_acl_configuration("ops") is inserted
        assert nexus.get_current_frame_acl_configuration("ops") is inserted
    finally:
        conduit.cleanup()


def test_integration_frame_detach_removes_acl_container_after_chain_activity() -> None:
    """
    Verify frame-detach cleanup removes a populated ACL container after real
    runtime setup and passive Nexus publication.

    Returns:
        None.
    """
    configuration = _make_rift_publishable_configuration(aetheric_frame="ops")
    spellbook = Spellbook(aetheric_frame="ops", configuration=configuration)
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    nexus = Nexus()
    system_configuration = nexus.create_system_configuration()
    system_configuration.with_rift_creation_enabled(True)
    system_configuration.with_direct_rift_access(True)
    nexus.enable(system_configuration)
    original = nexus.get_current_frame_acl_configuration("ops")
    draft = nexus.create_new_from_acl_configuration(
        "ops",
        original.configuration_id,
        reason="detach-copy",
    )
    draft.set_json_configuration_string(
        _build_typed_json_payload(
            "ops",
            view_profile_name="hybrid",
            codegen_profile_name="safe",
            marker="detach",
        )
    )
    draft.finalize()
    nexus.insert_head_frame_acl_configuration("ops", draft, select_as_current=True)
    container = nexus._frame_acl_manager._get_required_frame_acl_container("ops")
    frame = Aether()._ensure_frame("ops")

    try:
        frame.cleanup()

        assert container.cleaned is True
        assert "ops" not in nexus._frame_acl_manager.frame_acl_containers_by_name
    finally:
        conduit.cleanup()

