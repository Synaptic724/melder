import json

import pytest

from melder.aether.nexus.acl.configurations.frame_acl_command_configuration import (
    FrameACLCommandConfiguration,
)
from melder.aether.nexus.acl.frame_acl_configuration import FrameACLConfiguration
from melder.aether.nexus.acl.configurations.frame_acl_codegen_configuration import (
    FrameACLCodegenConfiguration,
)
from melder.aether.nexus.acl.configurations.profiles.codegen.frame_acl_codegen_profile import (
    FrameACLCodegenProfile,
)
from melder.aether.nexus.acl.configurations.profiles.rules.frame_acl_ruleset import (
    FrameACLRuleSet,
)
from melder.aether.nexus.acl.configurations.profiles.view.frame_acl_view_profile import (
    FrameACLViewProfile,
)
from melder.aether.nexus.acl.configurations.frame_acl_view_configuration import (
    FrameACLViewConfiguration,
)


def test_frame_acl_configuration_create_default_sets_safe_typed_baseline() -> None:
    """
    Verify default configuration builds a typed safe ACL baseline.

    Returns:
        None.
    """
    configuration = FrameACLConfiguration.create_default("ops")

    payload = configuration.to_json_dict()

    assert configuration.frame_name == "ops"
    assert configuration.previous_configuration_id is None
    assert configuration.view_configuration.profile_name == "safe"
    assert configuration.command_configuration.profile_name == "safe"
    assert configuration.codegen_configuration.profile_name == "safe"
    assert payload["frame_name"] == "ops"
    assert payload["view_configuration"]["profile_name"] == "safe"
    assert payload["command_configuration"]["profile_name"] == "safe"
    assert payload["codegen_configuration"]["profile_name"] == "safe"


def test_frame_acl_configuration_from_json_reconstructs_typed_children() -> None:
    """
    Verify JSON payloads rebuild the typed child configuration objects.

    Returns:
        None.
    """
    json_payload = json.dumps(
        {
            "frame_name": "ops",
            "view_configuration": {
                "profile_name": "hybrid",
                "profile_version": "0.0.1",
                "minimum_spell_payload_type": "detailed",
                "frame_override_ruleset": {"name": "frame_override", "rules": []},
                "conduit_override_ruleset": {"name": "conduit_override", "rules": []},
                "spell_override_ruleset": {"name": "spell_override", "rules": []},
                "member_override_ruleset": {"name": "member_override", "rules": []},
            },
            "command_configuration": {
                "profile_name": "strict_command",
                "profile_version": "0.0.1",
                "frame_override_ruleset": {"name": "frame_override", "rules": []},
                "conduit_override_ruleset": {"name": "conduit_override", "rules": []},
                "spell_override_ruleset": {"name": "spell_override", "rules": []},
                "member_override_ruleset": {"name": "member_override", "rules": []},
            },
            "codegen_configuration": {
                "profile_name": "permissive",
                "profile_version": "0.0.1",
                "frame_override_ruleset": {"name": "frame_override", "rules": []},
                "conduit_override_ruleset": {"name": "conduit_override", "rules": []},
                "spell_override_ruleset": {"name": "spell_override", "rules": []},
                "capability_override_ruleset": {"name": "capability_override", "rules": []},
            },
        },
        sort_keys=True,
    )

    configuration = FrameACLConfiguration.from_json_configuration_string(
        frame_name="ops",
        json_configuration_string=json_payload,
        source_configuration_id=None,
        previous_configuration_id="cfg-1",
        reason="from-json",
        locked=True,
    )

    assert configuration.previous_configuration_id == "cfg-1"
    assert configuration.reason == "from-json"
    assert configuration.locked is True
    assert configuration.view_configuration.profile_name == "hybrid"
    assert configuration.command_configuration.profile_name == "strict_command"
    assert configuration.codegen_configuration.profile_name == "permissive"


def test_frame_acl_configuration_init_rejects_invalid_inputs() -> None:
    """
    Verify configuration construction rejects invalid frame and child types.

    Returns:
        None.
    """
    with pytest.raises(ValueError, match="frame_name cannot be empty"):
        FrameACLConfiguration(
            frame_name="",
            view_configuration=FrameACLViewConfiguration.from_profile(
                FrameACLViewProfile.create_default()
            ),
            command_configuration=FrameACLCommandConfiguration.create_default(),
            codegen_configuration=FrameACLCodegenConfiguration.from_profile(
                FrameACLCodegenProfile.create_default()
            ),
            source_configuration_id=None,
            previous_configuration_id=None,
            reason="invalid",
            locked=True,
        )

    with pytest.raises(TypeError, match="view_configuration must be a FrameACLViewConfiguration"):
        FrameACLConfiguration(
            frame_name="ops",
            view_configuration=None,
            command_configuration=FrameACLCommandConfiguration.create_default(),
            codegen_configuration=FrameACLCodegenConfiguration.from_profile(
                FrameACLCodegenProfile.create_default()
            ),
            source_configuration_id=None,
            previous_configuration_id=None,
            reason="invalid",
            locked=True,
        )

    with pytest.raises(TypeError, match="codegen_configuration must be a FrameACLCodegenConfiguration"):
        FrameACLConfiguration(
            frame_name="ops",
            view_configuration=FrameACLViewConfiguration.from_profile(
                FrameACLViewProfile.create_default()
            ),
            command_configuration=FrameACLCommandConfiguration.create_default(),
            codegen_configuration=None,
            source_configuration_id=None,
            previous_configuration_id=None,
            reason="invalid",
            locked=True,
        )

    with pytest.raises(TypeError, match="command_configuration must be a FrameACLCommandConfiguration"):
        FrameACLConfiguration(
            frame_name="ops",
            view_configuration=FrameACLViewConfiguration.from_profile(
                FrameACLViewProfile.create_default()
            ),
            command_configuration=None,
            codegen_configuration=FrameACLCodegenConfiguration.from_profile(
                FrameACLCodegenProfile.create_default()
            ),
            source_configuration_id=None,
            previous_configuration_id=None,
            reason="invalid",
            locked=True,
        )


def test_frame_acl_configuration_from_json_rejects_invalid_payloads() -> None:
    """
    Verify JSON-loading rejects invalid payload types and malformed JSON.

    Returns:
        None.
    """
    with pytest.raises(TypeError, match="json_configuration_string must be a string"):
        FrameACLConfiguration.from_json_configuration_string(
            frame_name="ops",
            json_configuration_string=None,
            source_configuration_id=None,
            previous_configuration_id=None,
            reason="invalid",
            locked=False,
        )

    with pytest.raises(ValueError, match="must be valid JSON"):
        FrameACLConfiguration.from_json_configuration_string(
            frame_name="ops",
            json_configuration_string="{not-json}",
            source_configuration_id=None,
            previous_configuration_id=None,
            reason="invalid",
            locked=False,
        )

    with pytest.raises(ValueError, match="must decode to a JSON object"):
        FrameACLConfiguration.from_json_configuration_string(
            frame_name="ops",
            json_configuration_string="[]",
            source_configuration_id=None,
            previous_configuration_id=None,
            reason="invalid",
            locked=False,
        )


def test_frame_acl_configuration_create_new_from_acl_configuration_copies_children() -> None:
    """
    Verify create_new_from_acl_configuration clones the typed child objects.

    Returns:
        None.
    """
    source = FrameACLConfiguration.create_default("ops")

    copied = FrameACLConfiguration.create_new_from_acl_configuration(
        source,
        reason="copy",
    )

    assert copied.frame_name == "ops"
    assert copied.source_configuration_id == source.configuration_id
    assert copied.previous_configuration_id is None
    assert copied.locked is False
    assert copied.view_configuration is not source.view_configuration
    assert copied.command_configuration is not source.command_configuration
    assert copied.codegen_configuration is not source.codegen_configuration
    assert copied.to_json_string() == source.to_json_string()


def test_frame_acl_configuration_create_new_rejects_invalid_source() -> None:
    """
    Verify create_new_from_acl_configuration rejects non-configuration inputs.

    Returns:
        None.
    """
    with pytest.raises(TypeError, match="must be a FrameACLConfiguration"):
        FrameACLConfiguration.create_new_from_acl_configuration(
            None,
            reason="copy",
        )


def test_frame_acl_configuration_finalize_and_previous_pointer_rules() -> None:
    """
    Verify finalize locks the config and previous-pointer updates are only
    allowed before locking.

    Returns:
        None.
    """
    configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        FrameACLConfiguration.create_default("ops"),
        reason="draft",
    )

    configuration.set_previous_configuration_id("cfg-1")
    assert configuration.previous_configuration_id == "cfg-1"

    configuration.finalize()
    assert configuration.locked is True

    with pytest.raises(RuntimeError, match="Cannot change previous_configuration_id"):
        configuration.set_previous_configuration_id("cfg-2")


def test_frame_acl_configuration_set_json_configuration_string_rebuilds_children() -> None:
    """
    Verify mutable configs can rebuild typed child configs from JSON before
    finalize.

    Returns:
        None.
    """
    configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        FrameACLConfiguration.create_default("ops"),
        reason="draft",
    )

    configuration.set_json_configuration_string(
        json.dumps(
            {
                "frame_name": "ops",
                "view_configuration": {
                    "profile_name": "hybrid",
                    "profile_version": "0.0.1",
                    "minimum_spell_payload_type": "detailed",
                    "frame_override_ruleset": {"name": "frame_override", "rules": []},
                    "conduit_override_ruleset": {"name": "conduit_override", "rules": []},
                    "spell_override_ruleset": {"name": "spell_override", "rules": []},
                    "member_override_ruleset": {"name": "member_override", "rules": []},
                },
                "command_configuration": {
                    "profile_name": "strict_command",
                    "profile_version": "0.0.1",
                    "frame_override_ruleset": {"name": "frame_override", "rules": []},
                    "conduit_override_ruleset": {"name": "conduit_override", "rules": []},
                    "spell_override_ruleset": {"name": "spell_override", "rules": []},
                    "member_override_ruleset": {"name": "member_override", "rules": []},
                },
                "codegen_configuration": {
                    "profile_name": "permissive",
                    "profile_version": "0.0.1",
                    "frame_override_ruleset": {"name": "frame_override", "rules": []},
                    "conduit_override_ruleset": {"name": "conduit_override", "rules": []},
                    "spell_override_ruleset": {"name": "spell_override", "rules": []},
                    "capability_override_ruleset": {"name": "capability_override", "rules": []},
                },
            },
            sort_keys=True,
        )
    )

    assert configuration.view_configuration.profile_name == "hybrid"
    assert configuration.command_configuration.profile_name == "strict_command"
    assert configuration.codegen_configuration.profile_name == "permissive"


def test_frame_acl_configuration_set_typed_children_requires_mutable_state() -> None:
    """
    Verify typed child replacement only works while the config is mutable.

    Returns:
        None.
    """
    configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        FrameACLConfiguration.create_default("ops"),
        reason="draft",
    )
    new_view_configuration = FrameACLViewConfiguration.from_profile(
        FrameACLViewProfile.create_hybrid()
    )
    new_command_configuration = FrameACLCommandConfiguration(
        profile_name="strict_command",
        profile_version="0.0.1",
    )
    new_codegen_configuration = FrameACLCodegenConfiguration.from_profile(
        FrameACLCodegenProfile.create_permissive()
    )

    configuration.set_view_configuration(new_view_configuration)
    configuration.set_command_configuration(new_command_configuration)
    configuration.set_codegen_configuration(new_codegen_configuration)

    assert configuration.view_configuration is new_view_configuration
    assert configuration.command_configuration is new_command_configuration
    assert configuration.codegen_configuration is new_codegen_configuration

    configuration.finalize()

    with pytest.raises(RuntimeError, match="Cannot change view_configuration"):
        configuration.set_view_configuration(
            FrameACLViewConfiguration.from_profile(
                FrameACLViewProfile.create_safe()
            )
        )

    with pytest.raises(RuntimeError, match="Cannot change codegen_configuration"):
        configuration.set_codegen_configuration(
            FrameACLCodegenConfiguration.from_profile(
                FrameACLCodegenProfile.create_safe()
            )
        )

    with pytest.raises(RuntimeError, match="Cannot change command_configuration"):
        configuration.set_command_configuration(
            FrameACLCommandConfiguration.create_default()
        )


def test_frame_acl_configuration_set_typed_children_reject_invalid_types() -> None:
    """
    Verify mutable child replacement still enforces the typed child contract.

    Returns:
        None.
    """
    configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        FrameACLConfiguration.create_default("ops"),
        reason="draft",
    )

    with pytest.raises(TypeError, match="view_configuration must be a FrameACLViewConfiguration"):
        configuration.set_view_configuration(None)

    with pytest.raises(TypeError, match="command_configuration must be a FrameACLCommandConfiguration"):
        configuration.set_command_configuration(None)

    with pytest.raises(TypeError, match="codegen_configuration must be a FrameACLCodegenConfiguration"):
        configuration.set_codegen_configuration(None)


def test_frame_acl_configuration_normalized_json_and_created_at_are_exposed() -> None:
    """
    Verify public metadata/accessor properties expose the node snapshot cleanly.

    Returns:
        None.
    """
    configuration = FrameACLConfiguration.create_default("ops")

    assert configuration.created_at.endswith("Z")
    assert configuration.normalized_json_configuration_string == configuration.to_json_string()


def test_frame_acl_configuration_set_json_requires_mutable_state() -> None:
    """
    Verify JSON payload replacement is blocked once the config is locked.

    Returns:
        None.
    """
    configuration = FrameACLConfiguration.create_default("ops")

    with pytest.raises(RuntimeError, match="Cannot change JSON payload on a locked configuration"):
        configuration.set_json_configuration_string("{}")


def test_frame_acl_configuration_child_config_objects_are_serializable() -> None:
    """
    Verify typed child configs serialize their profile identity and overrides.

    Returns:
        None.
    """
    view_configuration = FrameACLViewConfiguration.from_profile(
        FrameACLViewProfile.create_safe(),
        frame_override_ruleset=FrameACLRuleSet("frame_override"),
    )
    command_configuration = FrameACLCommandConfiguration(
        profile_name="strict_command",
        profile_version="0.0.1",
        spell_override_ruleset=FrameACLRuleSet("spell_override"),
    )
    codegen_configuration = FrameACLCodegenConfiguration.from_profile(
        FrameACLCodegenProfile.create_hybrid(),
        capability_override_ruleset=FrameACLRuleSet("capability_override"),
    )

    assert view_configuration.to_json_dict()["profile_name"] == "safe"
    assert command_configuration.to_json_dict()["profile_name"] == "strict_command"
    assert codegen_configuration.to_json_dict()["profile_name"] == "hybrid"


def test_frame_acl_configuration_cleanup_clears_fields() -> None:
    """
    Verify cleanup nulls all owned configuration fields.

    Returns:
        None.
    """
    configuration = FrameACLConfiguration.create_default("ops")
    view_configuration = configuration.view_configuration
    command_configuration = configuration.command_configuration
    codegen_configuration = configuration.codegen_configuration

    configuration.cleanup()

    assert configuration.cleaned is True
    assert view_configuration.cleaned is True
    assert command_configuration.cleaned is True
    assert codegen_configuration.cleaned is True
    assert configuration._configuration_id is None
    assert configuration._frame_name is None
    assert configuration._source_configuration_id is None
    assert configuration._previous_configuration_id is None
    assert configuration._created_at is None
    assert configuration._reason is None
    assert configuration._locked is None
    assert configuration._view_configuration is None
    assert configuration._command_configuration is None
    assert configuration._codegen_configuration is None


def test_frame_acl_configuration_cleanup_is_idempotent() -> None:
    """
    Verify cleanup can be called repeatedly.

    Returns:
        None.
    """
    configuration = FrameACLConfiguration.create_default("ops")

    configuration.cleanup()
    configuration.cleanup()

    assert configuration.cleaned is True


def test_frame_acl_configuration_init_rejects_empty_reason_and_non_bool_locked() -> None:
    """
    Verify node construction enforces reason and locked type requirements.

    Returns:
        None.
    """
    view_configuration = FrameACLViewConfiguration.from_profile(
        FrameACLViewProfile.create_default()
    )
    codegen_configuration = FrameACLCodegenConfiguration.from_profile(
        FrameACLCodegenProfile.create_default()
    )

    with pytest.raises(ValueError, match="reason cannot be empty"):
        FrameACLConfiguration(
            frame_name="ops",
            view_configuration=view_configuration,
            command_configuration=FrameACLCommandConfiguration.create_default(),
            codegen_configuration=codegen_configuration,
            source_configuration_id=None,
            previous_configuration_id=None,
            reason="",
            locked=True,
        )

    with pytest.raises(TypeError, match="locked must be a bool"):
        FrameACLConfiguration(
            frame_name="ops",
            view_configuration=FrameACLViewConfiguration.from_profile(
                FrameACLViewProfile.create_default()
            ),
            command_configuration=FrameACLCommandConfiguration.create_default(),
            codegen_configuration=FrameACLCodegenConfiguration.from_profile(
                FrameACLCodegenProfile.create_default()
            ),
            source_configuration_id=None,
            previous_configuration_id=None,
            reason="invalid",
            locked=None,
        )
