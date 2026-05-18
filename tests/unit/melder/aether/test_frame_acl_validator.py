import pytest

from melder.aether.nexus.acl.configurations.profiles.codegen.frame_acl_codegen_profile import (
    FrameACLCodegenProfile,
)
from melder.aether.nexus.acl.configurations.profiles.rules.frame_acl_rule import (
    FrameACLRule,
)
from melder.aether.nexus.acl.configurations.profiles.rules.frame_acl_ruleset import (
    FrameACLRuleSet,
)
from melder.aether.nexus.acl.configurations.profiles.view.frame_acl_view_profile import (
    FrameACLViewProfile,
)
from melder.aether.nexus.acl.configurations.frame_acl_command_configuration import (
    FrameACLCommandConfiguration,
)
from melder.aether.nexus.acl.frame_acl_configuration import FrameACLConfiguration
from melder.aether.nexus.acl.validator.frame_acl_validator import FrameACLValidator
from melder.aether.nexus.acl.configurations.frame_acl_view_configuration import (
    FrameACLViewConfiguration,
)
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.aether.nexus.frame_descriptor.conduit_descriptor_payload import (
    ConduitDescriptorPayload,
)
from melder.aether.nexus.frame_descriptor.conduit_record import ConduitRecord
from melder.aether.nexus.frame_descriptor.frame_descriptor import FrameDescriptor
from melder.aether.nexus.frame_descriptor.frame_descriptor_payload import (
    FrameDescriptorPayload,
)
from melder.aether.nexus.frame_descriptor.frame_record import FrameRecord
from melder.aether.nexus.frame_descriptor.spell_descriptor_payload import (
    SpellDescriptorPayload,
)
from melder.aether.nexus.frame_descriptor.spell_record import SpellRecord
from melder.spellbook.configuration.system_state import SystemState
from melder.spellbook.existence.existence import Existence


def _build_descriptor(
        *,
        nexus_version: str = "0.0.1",
        frame_payload_version: str = "0.0.1",
        conduit_payload_version: str = "0.0.1",
        spell_payload_type: str = "detailed",
        spell_payload_version: str = "0.0.1",
) -> FrameDescriptor:
    """
    Build one descriptor populated with frame, conduit, and spell payloads.

    Args:
        frame_payload_version:
            Frame payload contract version.
        conduit_payload_version:
            Conduit payload contract version.
        spell_payload_type:
            Spell payload detail type.
        spell_payload_version:
            Spell payload contract version.

    Returns:
        FrameDescriptor: Populated descriptor.
    """
    descriptor = FrameDescriptor("ops")
    descriptor.set_frame_overview(
        FrameRecord(
            nexus_version=nexus_version,
            frame_name="ops",
            frame_id="ops-frame",
            config_origin_spellbook_id="ops-spellbook",
            payload=FrameDescriptorPayload(
                system_state=SystemState.dynamic,
                ai_native_enabled=True,
                rift_enabled=True,
                root_conduit_count=1,
                root_conduit_ids=("ops-conduit",),
                named_root_conduits=(("ops-conduit", "root"),),
                conduit_cloud_entry_count=1,
                conduit_cloud_names=("root",),
                cluster_count=0,
                cluster_names=tuple(),
                payload_version=frame_payload_version,
            ),
        )
    )
    descriptor.upsert_conduit_record(
        ConduitRecord(
            nexus_version=nexus_version,
            conduit_id="ops-conduit",
            root_conduit_id="ops-conduit",
            frame_name="ops",
            origin_spellbook_id="ops-spellbook",
            payload=ConduitDescriptorPayload(
                conduit_name="root",
                conduit_state=ConduitState.normal,
                policy=Policies.default,
                peer_conduit_ids=tuple(),
                payload_version=conduit_payload_version,
            ),
        )
    )
    descriptor.upsert_spell_record(
        SpellRecord(
            nexus_version=nexus_version,
            origin_spellbook_id="ops-spellbook",
            frame_name="ops",
            owner_conduit_id="ops-conduit",
            spell_id="ops-spell",
                spell_index_id="ops-lineage",
            spell_name="OpsSpell",
            spellframe=None,
            binding_name="ops_spell",
            permissions=Permissions.create,
            existence=Existence.unique,
            payload=SpellDescriptorPayload(
                payload_type=spell_payload_type,
                payload_version=spell_payload_version,
                binding_payload={"kind": "class"},
                resolution_payload={"requirements": []},
                class_profile=None,
                callable_profile=None,
                metadata={},
                instance_members={},
                dynamic_access={},
            ),
        )
    )
    return descriptor


def test_frame_acl_validator_accepts_matching_configuration() -> None:
    """
    Verify validator accepts a configuration targeting the same frame.

    Returns:
        None.
    """
    validator = FrameACLValidator("ops")
    configuration = FrameACLConfiguration.create_default("ops")

    assert validator.validate_configuration(configuration) is True
    assert validator.last_validated_configuration_id == configuration.configuration_id


def test_frame_acl_validator_rejects_invalid_inputs() -> None:
    """
    Verify validator rejects non-config inputs and wrong-frame configs.

    Returns:
        None.
    """
    validator = FrameACLValidator("ops")
    finance_configuration = FrameACLConfiguration.create_default("finance")

    with pytest.raises(TypeError, match="configuration must satisfy IFrameACLConfiguration"):
        validator.validate_configuration(None)

    with pytest.raises(ValueError, match="targets frame 'finance', expected 'ops'"):
        validator.validate_configuration(finance_configuration)

    with pytest.raises(TypeError, match="frame_descriptor must be a FrameDescriptor"):
        validator.validate_configuration_against_descriptor(
            FrameACLConfiguration.create_default("ops"),
            None,
        )

    with pytest.raises(ValueError, match="FrameDescriptor targets frame 'finance', expected 'ops'"):
        validator.validate_configuration_against_descriptor(
            FrameACLConfiguration.create_default("ops"),
            FrameDescriptor("finance"),
        )


def test_frame_acl_validator_init_rejects_empty_frame_name() -> None:
    """
    Verify validator requires a non-empty frame name.

    Returns:
        None.
    """
    with pytest.raises(ValueError, match="frame_name cannot be empty"):
        FrameACLValidator("")


def test_frame_acl_validator_cleanup_clears_state() -> None:
    """
    Verify cleanup nulls validator state.

    Returns:
        None.
    """
    validator = FrameACLValidator("ops")
    configuration = FrameACLConfiguration.create_default("ops")
    validator.validate_configuration(configuration)

    validator.cleanup()

    assert validator.cleaned is True
    assert not hasattr(validator, '_frame_name')
    assert not hasattr(validator, '_last_validated_configuration_id')


def test_frame_acl_validator_cleanup_is_idempotent() -> None:
    """
    Verify validator cleanup can be called repeatedly.

    Returns:
        None.
    """
    validator = FrameACLValidator("ops")

    validator.cleanup()
    validator.cleanup()

    assert validator.cleaned is True


def test_frame_acl_validator_properties_return_expected_values() -> None:
    """
    Verify validator properties expose the owning frame and last validated id.

    Returns:
        None.
    """
    validator = FrameACLValidator("ops")
    configuration = FrameACLConfiguration.create_default("ops")

    assert validator.frame_name == "ops"
    assert validator.last_validated_configuration_id is None

    validator.validate_configuration(configuration)

    assert validator.last_validated_configuration_id == configuration.configuration_id


def test_frame_acl_validator_rejects_unsupported_spell_payload_floor() -> None:
    """
    Verify validator rejects unsupported spell payload floor values.

    Returns:
        None.
    """
    validator = FrameACLValidator("ops")
    configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        FrameACLConfiguration.create_default("ops"),
        reason="draft",
    )
    configuration.set_view_configuration(
        FrameACLViewConfiguration(
            profile_name="custom",
            profile_version="0.0.1",
            minimum_spell_payload_type="unknown_floor",
        )
    )
    configuration.finalize()

    with pytest.raises(ValueError, match="Unsupported minimum_spell_payload_type"):
        validator.validate_configuration(configuration)

    configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        FrameACLConfiguration.create_default("ops"),
        reason="draft",
    )
    configuration.set_view_configuration(
        FrameACLViewConfiguration(
            profile_name="custom",
            profile_version="0.0.1",
            minimum_spell_payload_type="general",
            minimum_spell_payload_version="9.9.9",
        )
    )
    configuration.finalize()

    with pytest.raises(ValueError, match="Unsupported minimum_spell_payload_version"):
        validator.validate_configuration(configuration)

    with pytest.raises(TypeError, match="view_configuration must satisfy IFrameACLViewConfiguration"):
        validator._validate_view_configuration(None)

    configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        FrameACLConfiguration.create_default("ops"),
        reason="draft",
    )
    configuration.set_view_configuration(
        FrameACLViewConfiguration(
            profile_name="custom",
            profile_version="0.0.1",
            required_nexus_label="legacy",
            required_nexus_version="9.9.9",
            minimum_spell_payload_type="general",
        )
    )
    configuration.finalize()

    with pytest.raises(ValueError, match="Unsupported required Nexus record contract 'legacy:9.9.9'"):
        validator.validate_configuration(configuration)


def test_frame_acl_validator_accepts_matching_descriptor_payload_contracts() -> None:
    """
    Verify descriptor-aware validation accepts matching payload contracts.

    Returns:
        None.
    """
    validator = FrameACLValidator("ops")
    configuration = FrameACLConfiguration.create_default("ops")
    descriptor = _build_descriptor()

    assert (
        validator.validate_configuration_against_descriptor(
            configuration,
            descriptor,
        )
        is True
    )


def test_frame_acl_validator_rejects_missing_frame_overview() -> None:
    """
    Verify descriptor-aware validation rejects descriptors with no overview.

    Returns:
        None.
    """
    validator = FrameACLValidator("ops")
    configuration = FrameACLConfiguration.create_default("ops")
    descriptor = FrameDescriptor("ops")

    with pytest.raises(ValueError, match="has no frame_overview for record-contract validation"):
        validator.validate_configuration_against_descriptor(
            configuration,
            descriptor,
        )


def test_frame_acl_validator_rejects_frame_payload_contract_mismatch() -> None:
    """
    Verify descriptor-aware validation rejects frame payload mismatches.

    Returns:
        None.
    """
    validator = FrameACLValidator("ops")
    configuration = FrameACLConfiguration.create_default("ops")
    descriptor = _build_descriptor(nexus_version="9.9.9")

    with pytest.raises(
            ValueError,
            match="Descriptor frame record Nexus contract 'default:9.9.9' does not match required ACL contract 'default:0.0.1' for frame 'ops'",
    ):
        validator.validate_configuration_against_descriptor(
            configuration,
            descriptor,
        )


def test_frame_acl_validator_rejects_spell_payload_contract_below_floor() -> None:
    """
    Verify descriptor-aware validation rejects spell payloads below the ACL floor.

    Returns:
        None.
    """
    validator = FrameACLValidator("ops")
    configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        FrameACLConfiguration.create_default("ops"),
        reason="detailed_floor",
    )
    configuration.set_view_configuration(
        FrameACLViewConfiguration(
            profile_name="custom",
            profile_version="0.0.1",
            required_nexus_label="default",
            required_nexus_version="0.0.1",
            minimum_spell_payload_type="detailed",
            minimum_spell_payload_version="0.0.1",
        )
    )
    configuration.finalize()
    descriptor = _build_descriptor(spell_payload_type="general")

    with pytest.raises(
            ValueError,
            match="Descriptor spell payload type 'general:0.0.1' does not satisfy minimum ACL spell payload contract 'detailed:0.0.1' for frame 'ops'",
    ):
        validator.validate_configuration_against_descriptor(
            configuration,
            descriptor,
        )


def test_frame_acl_validator_rejects_spell_payload_version_mismatch() -> None:
    """
    Verify descriptor-aware validation rejects spell payload version mismatch.

    Returns:
        None.
    """
    validator = FrameACLValidator("ops")
    configuration = FrameACLConfiguration.create_default("ops")
    descriptor = _build_descriptor(spell_payload_version="9.9.9")

    with pytest.raises(
            ValueError,
            match="Descriptor spell payload version '9.9.9' does not match required ACL spell payload version '0.0.1' for frame 'ops'",
    ):
        validator.validate_configuration_against_descriptor(
            configuration,
            descriptor,
        )


def test_frame_acl_validator_rejects_wrong_operation_family() -> None:
    """
    Verify validator rejects operations stored in the wrong ruleset family.

    Returns:
        None.
    """
    validator = FrameACLValidator("ops")
    configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        FrameACLConfiguration.create_default("ops"),
        reason="draft",
    )
    bad_ruleset = FrameACLRuleSet(
        "frame_override",
        rules=[
            FrameACLRule(
                rule_name="bad_invoke",
                operation="invoke_method",
                effect="allow",
            )
        ],
    )
    configuration.set_view_configuration(
        FrameACLViewConfiguration(
            profile_name="custom",
            profile_version="0.0.1",
            minimum_spell_payload_type="detailed",
            frame_override_ruleset=bad_ruleset,
        )
    )
    configuration.finalize()

    with pytest.raises(ValueError, match="Unsupported operation 'invoke_method' in view.frame ruleset"):
        validator.validate_configuration(configuration)


def test_frame_acl_validator_rejects_member_rule_without_pattern_or_name() -> None:
    """
    Verify validator rejects malformed member rules missing selector shape.

    Returns:
        None.
    """
    validator = FrameACLValidator("ops")
    configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        FrameACLConfiguration.create_default("ops"),
        reason="draft",
    )
    bad_member_ruleset = FrameACLRuleSet(
        "member_override",
        rules=[
            FrameACLRule(
                rule_name="bad_member_rule",
                operation="show_member",
                effect="deny",
            )
        ],
    )
    configuration.set_view_configuration(
        FrameACLViewConfiguration(
            profile_name="custom",
            profile_version="0.0.1",
            minimum_spell_payload_type="detailed",
            member_override_ruleset=bad_member_ruleset,
        )
    )
    configuration.finalize()

    with pytest.raises(ValueError, match="Member rules in view.member must declare 'pattern' or 'member_name'"):
        validator.validate_configuration(configuration)


def test_frame_acl_validator_flags_unsafe_safe_profile_widening() -> None:
    """
    Verify validator flags safe-profile overrides that widen forbidden actions.

    Returns:
        None.
    """
    validator = FrameACLValidator("ops")
    configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        FrameACLConfiguration.create_default("ops"),
        reason="draft",
    )
    unsafe_spell_ruleset = FrameACLRuleSet(
        "spell_override",
        rules=[
            FrameACLRule(
                rule_name="unsafe_dynamic_access",
                operation="show_dynamic_access",
                effect="allow",
            )
        ],
    )
    configuration.set_view_configuration(
        FrameACLViewConfiguration.from_profile(
            FrameACLViewProfile.create_safe(),
            spell_override_ruleset=unsafe_spell_ruleset,
        )
    )
    configuration.finalize()

    with pytest.raises(ValueError, match="Safe profile cannot allow 'show_dynamic_access' in safe view spell ruleset"):
        validator.validate_configuration(configuration)


def test_frame_acl_validator_flags_safe_view_dunder_member_widening() -> None:
    """
    Verify validator rejects safe-view member overrides that expose dunder access.

    Returns:
        None.
    """
    validator = FrameACLValidator("ops")
    configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        FrameACLConfiguration.create_default("ops"),
        reason="draft",
    )
    unsafe_member_ruleset = FrameACLRuleSet(
        "member_override",
        rules=[
            FrameACLRule(
                rule_name="unsafe_dunder",
                operation="show_member",
                effect="allow",
                conditions={"pattern": "__*"},
            )
        ],
    )
    configuration.set_view_configuration(
        FrameACLViewConfiguration.from_profile(
            FrameACLViewProfile.create_safe(),
            member_override_ruleset=unsafe_member_ruleset,
        )
    )
    configuration.finalize()

    with pytest.raises(ValueError, match="Safe profile cannot allow dunder member access"):
        validator.validate_configuration(configuration)


def test_frame_acl_validator_flags_unsafe_safe_codegen_widening() -> None:
    """
    Verify validator flags safe codegen overrides that widen forbidden actions.

    Returns:
        None.
    """
    validator = FrameACLValidator("ops")
    configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        FrameACLConfiguration.create_default("ops"),
        reason="draft",
    )
    unsafe_capability_ruleset = FrameACLRuleSet(
        "capability_override",
        rules=[
            FrameACLRule(
                rule_name="unsafe_dynamic_access",
                operation="dynamic_access",
                effect="allow",
            )
        ],
    )
    configuration.set_codegen_configuration(
        configuration.codegen_configuration.from_profile(
            FrameACLCodegenProfile.create_safe(),
            capability_override_ruleset=unsafe_capability_ruleset,
        )
    )
    configuration.finalize()

    with pytest.raises(ValueError, match="Safe profile cannot allow 'dynamic_access' in safe codegen capability ruleset"):
        validator.validate_configuration(configuration)


def test_frame_acl_validator_rejects_invalid_codegen_configuration_type() -> None:
    """
    Verify the codegen validator rejects non-codegen configuration objects.

    Returns:
        None.
    """
    validator = FrameACLValidator("ops")

    with pytest.raises(TypeError, match="codegen_configuration must satisfy IFrameACLCodegenConfiguration"):
        validator._validate_codegen_configuration(None)


def test_frame_acl_validator_rejects_invalid_command_configuration_type() -> None:
    """
    Verify the command validator rejects non-command configuration objects.

    Returns:
        None.
    """
    validator = FrameACLValidator("ops")

    with pytest.raises(TypeError, match="command_configuration must satisfy IFrameACLCommandConfiguration"):
        validator._validate_command_configuration(None)


def test_frame_acl_validator_rejects_wrong_command_operation_family() -> None:
    """
    Verify validator rejects operations stored in the wrong command ruleset family.

    Returns:
        None.
    """
    validator = FrameACLValidator("ops")
    configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        FrameACLConfiguration.create_default("ops"),
        reason="draft",
    )
    configuration.set_command_configuration(
        FrameACLCommandConfiguration(
            profile_name="strict_command",
            profile_version="0.0.1",
            frame_override_ruleset=FrameACLRuleSet(
                "frame_override",
                rules=[
                    FrameACLRule(
                        rule_name="bad_method_call",
                        operation="invoke_method",
                        effect="allow",
                    )
                ],
            ),
        )
    )
    configuration.finalize()

    with pytest.raises(ValueError, match="Unsupported operation 'invoke_method' in command.frame ruleset"):
        validator.validate_configuration(configuration)


def test_frame_acl_validator_rejects_command_member_rule_without_pattern_or_name() -> None:
    """
    Verify validator rejects malformed command member rules missing selector shape.

    Returns:
        None.
    """
    validator = FrameACLValidator("ops")
    configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        FrameACLConfiguration.create_default("ops"),
        reason="draft",
    )
    configuration.set_command_configuration(
        FrameACLCommandConfiguration(
            profile_name="strict_command",
            profile_version="0.0.1",
            member_override_ruleset=FrameACLRuleSet(
                "member_override",
                rules=[
                    FrameACLRule(
                        rule_name="bad_member_command_rule",
                        operation="invoke_method",
                        effect="allow",
                    )
                ],
            ),
        )
    )
    configuration.finalize()

    with pytest.raises(ValueError, match="Member rules in command.member must declare 'pattern' or 'member_name'"):
        validator.validate_configuration(configuration)


def test_frame_acl_validator_rejects_invalid_ruleset_family_input() -> None:
    """
    Verify ruleset-family validation rejects non-ruleset inputs.

    Returns:
        None.
    """
    with pytest.raises(TypeError, match="view.frame ruleset must satisfy IFrameACLRuleSet"):
        FrameACLValidator("ops")._validate_ruleset_family(
            None,
            {"visible"},
            "view.frame",
        )


def test_frame_acl_validator_rejects_unsupported_descriptor_spell_payload_type() -> None:
    """
    Verify descriptor-aware validation rejects unknown payload families.

    Returns:
        None.
    """
    validator = FrameACLValidator("ops")
    configuration = FrameACLConfiguration.create_default("ops")
    descriptor = _build_descriptor(spell_payload_type="mystery")

    with pytest.raises(ValueError, match="Unsupported descriptor spell payload type 'mystery'"):
        validator.validate_configuration_against_descriptor(
            configuration,
            descriptor,
        )


def test_frame_acl_validator_rejects_ambiguous_spell_selector() -> None:
    """
    Verify descriptor-aware validation rejects ambiguous spell selectors.

    Returns:
        None.
    """
    validator = FrameACLValidator("ops")
    configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        FrameACLConfiguration.create_default("ops"),
        reason="ambiguous_selector",
    )
    configuration.set_view_configuration(
        FrameACLViewConfiguration.from_profile(
            FrameACLViewProfile.create_safe(),
            precision_profile=FrameACLViewProfile.create_precision(),
            spell_override_ruleset=FrameACLRuleSet(
                "spell_override",
                rules=[
                    FrameACLRule(
                        rule_name="select_duplicate_signature",
                        operation="visible",
                        effect="allow",
                        conditions={
                            "spellframe": "ILogic",
                            "binding_name": "primary",
                        },
                    )
                ],
            ),
        )
    )
    configuration.finalize()
    descriptor = _build_descriptor()
    descriptor.upsert_spell_record(
        SpellRecord(
            nexus_version="0.0.1",
            origin_spellbook_id="other-spellbook",
            frame_name="ops",
            owner_conduit_id="ops-conduit",
            spell_id="ops-spell-2",
            spell_index_id="ops-lineage-2",
            spell_name="OtherSpell",
            spellframe="ILogic",
            binding_name="primary",
            permissions=Permissions.create,
            existence=Existence.unique,
            payload=SpellDescriptorPayload(
                payload_type="detailed",
                payload_version="0.0.1",
                binding_payload={"kind": "class"},
                resolution_payload={"requirements": []},
                class_profile=None,
                callable_profile=None,
                metadata={},
                instance_members={},
                dynamic_access={},
            ),
        )
    )
    descriptor.upsert_spell_record(
        SpellRecord(
            nexus_version="0.0.1",
            origin_spellbook_id="third-spellbook",
            frame_name="ops",
            owner_conduit_id="ops-conduit",
            spell_id="ops-spell-3",
            spell_index_id="ops-lineage-3",
            spell_name="ThirdSpell",
            spellframe="ILogic",
            binding_name="primary",
            permissions=Permissions.create,
            existence=Existence.unique,
            payload=SpellDescriptorPayload(
                payload_type="detailed",
                payload_version="0.0.1",
                binding_payload={"kind": "class"},
                resolution_payload={"requirements": []},
                class_profile=None,
                callable_profile=None,
                metadata={},
                instance_members={},
                dynamic_access={},
            ),
        )
    )

    with pytest.raises(ValueError, match="is ambiguous"):
        validator.validate_configuration_against_descriptor(
            configuration,
            descriptor,
        )
