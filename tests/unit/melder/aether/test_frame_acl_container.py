import threading

import pytest

from melder.aether.nexus.acl.frame_acl_builder import FrameACLBuilder
from melder.aether.nexus.acl.frame_acl_configuration import FrameACLConfiguration
from melder.aether.nexus.acl.frame_acl_configuration_chain import FrameACLConfigurationChain
from melder.aether.nexus.acl.frame_acl_container import FrameACLContainer
from melder.aether.nexus.acl.profiles.frame_acl_rule import FrameACLRule
from melder.aether.nexus.acl.profiles.frame_acl_ruleset import FrameACLRuleSet
from melder.aether.nexus.acl.frame_acl_view_configuration import (
    FrameACLViewConfiguration,
)
from melder.aether.nexus.acl.frame_acl_validator import FrameACLValidator


def test_frame_acl_container_builds_defaults() -> None:
    """
    Verify the container creates default config, validator, and builder.

    Returns:
        None.
    """
    container = FrameACLContainer("ops")

    assert container.frame_name == "ops"
    assert isinstance(container.frame_acl_builder, FrameACLBuilder)
    assert isinstance(container.frame_acl_configuration, FrameACLConfiguration)
    assert isinstance(container.frame_acl_configuration_chain, FrameACLConfigurationChain)
    assert isinstance(container.frame_acl_validator, FrameACLValidator)
    assert container.frame_acl_history == []
    assert container.list_named_configuration_names() == ["default"]
    assert (
        container.get_named_configuration("default")
        is container.frame_acl_configuration
    )


def test_frame_acl_container_rejects_invalid_init_inputs() -> None:
    """
    Verify container requires a frame name and valid history limit.

    Returns:
        None.
    """
    with pytest.raises(ValueError, match="frame_name cannot be empty"):
        FrameACLContainer("")

    with pytest.raises(ValueError, match="history_limit must be an integer >= 1"):
        FrameACLContainer("ops", history_limit=0)


def test_frame_acl_container_install_configuration_appends_history() -> None:
    """
    Verify installing a new configuration retains the previous one in history.

    Returns:
        None.
    """
    container = FrameACLContainer("ops")
    previous_configuration = container.frame_acl_configuration
    next_configuration = FrameACLConfiguration.from_json_configuration_string(
        frame_name="ops",
        json_configuration_string='{"frame_name":"ops","view_configuration":{"profile_name":"hybrid","profile_version":"0.0.1","minimum_spell_payload_type":"detailed","frame_override_ruleset":{"name":"frame_override","rules":[]},"conduit_override_ruleset":{"name":"conduit_override","rules":[]},"spell_override_ruleset":{"name":"spell_override","rules":[]},"member_override_ruleset":{"name":"member_override","rules":[]}},"codegen_configuration":{"profile_name":"safe","profile_version":"0.0.1","frame_override_ruleset":{"name":"frame_override","rules":[]},"conduit_override_ruleset":{"name":"conduit_override","rules":[]},"spell_override_ruleset":{"name":"spell_override","rules":[]},"capability_override_ruleset":{"name":"capability_override","rules":[]}}}',
        source_configuration_id=None,
        previous_configuration_id=previous_configuration.configuration_id,
        reason="install",
        locked=True,
    )

    container.install_configuration(next_configuration)

    assert container.frame_acl_configuration is next_configuration
    assert next_configuration.previous_configuration_id == previous_configuration.configuration_id
    assert container.frame_acl_history == [previous_configuration]
    assert container.frame_acl_validator.last_validated_configuration_id == next_configuration.configuration_id
    assert container.get_named_configuration("default") is next_configuration


def test_frame_acl_container_can_register_additional_named_configuration() -> None:
    """
    Verify the container can register one additional named ACL configuration.

    Returns:
        None.
    """
    container = FrameACLContainer("ops")
    named_configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        container.frame_acl_configuration,
        reason="named",
    )
    named_configuration.finalize()

    registered = container.register_named_configuration(
        named_configuration,
        contract_name="ops_contract",
    )

    assert registered is named_configuration
    assert container.get_named_configuration("ops_contract") is named_configuration
    assert container.list_named_configuration_names() == ["default", "ops_contract"]


def test_frame_acl_container_rejects_duplicate_named_configuration() -> None:
    """
    Verify the container rejects duplicate contract names for one frame.

    Returns:
        None.
    """
    container = FrameACLContainer("ops")
    first_named_configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        container.frame_acl_configuration,
        reason="named-1",
    )
    first_named_configuration.finalize()
    second_named_configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        container.frame_acl_configuration,
        reason="named-2",
    )
    second_named_configuration.finalize()

    container.register_named_configuration(
        first_named_configuration,
        contract_name="ops_contract",
    )

    with pytest.raises(ValueError, match="already exists"):
        container.register_named_configuration(
            second_named_configuration,
            contract_name="ops_contract",
        )


def test_frame_acl_container_history_is_capped_and_drops_oldest() -> None:
    """
    Verify history trimming drops and cleans the oldest configuration.

    Returns:
        None.
    """
    container = FrameACLContainer("ops", history_limit=2)
    first_configuration = container.frame_acl_configuration

    second_configuration = FrameACLConfiguration.from_json_configuration_string(
        frame_name="ops",
        json_configuration_string='{"frame_name":"ops","view_configuration":{"profile_name":"hybrid","profile_version":"0.0.1","minimum_spell_payload_type":"detailed","frame_override_ruleset":{"name":"frame_override","rules":[]},"conduit_override_ruleset":{"name":"conduit_override","rules":[]},"spell_override_ruleset":{"name":"spell_override","rules":[]},"member_override_ruleset":{"name":"member_override","rules":[]}},"codegen_configuration":{"profile_name":"safe","profile_version":"0.0.1","frame_override_ruleset":{"name":"frame_override","rules":[]},"conduit_override_ruleset":{"name":"conduit_override","rules":[]},"spell_override_ruleset":{"name":"spell_override","rules":[]},"capability_override_ruleset":{"name":"capability_override","rules":[]}}}',
        source_configuration_id=None,
        previous_configuration_id=first_configuration.configuration_id,
        reason="second",
        locked=True,
    )
    third_configuration = FrameACLConfiguration.from_json_configuration_string(
        frame_name="ops",
        json_configuration_string='{"frame_name":"ops","view_configuration":{"profile_name":"permissive","profile_version":"0.0.1","minimum_spell_payload_type":"detailed","frame_override_ruleset":{"name":"frame_override","rules":[]},"conduit_override_ruleset":{"name":"conduit_override","rules":[]},"spell_override_ruleset":{"name":"spell_override","rules":[]},"member_override_ruleset":{"name":"member_override","rules":[]}},"codegen_configuration":{"profile_name":"hybrid","profile_version":"0.0.1","frame_override_ruleset":{"name":"frame_override","rules":[]},"conduit_override_ruleset":{"name":"conduit_override","rules":[]},"spell_override_ruleset":{"name":"spell_override","rules":[]},"capability_override_ruleset":{"name":"capability_override","rules":[]}}}',
        source_configuration_id=None,
        previous_configuration_id=second_configuration.configuration_id,
        reason="third",
        locked=True,
    )
    fourth_configuration = FrameACLConfiguration.from_json_configuration_string(
        frame_name="ops",
        json_configuration_string='{"frame_name":"ops","view_configuration":{"profile_name":"safe","profile_version":"0.0.1","minimum_spell_payload_type":"detailed","frame_override_ruleset":{"name":"frame_override","rules":[]},"conduit_override_ruleset":{"name":"conduit_override","rules":[]},"spell_override_ruleset":{"name":"spell_override","rules":[]},"member_override_ruleset":{"name":"member_override","rules":[]}},"codegen_configuration":{"profile_name":"permissive","profile_version":"0.0.1","frame_override_ruleset":{"name":"frame_override","rules":[]},"conduit_override_ruleset":{"name":"conduit_override","rules":[]},"spell_override_ruleset":{"name":"spell_override","rules":[]},"capability_override_ruleset":{"name":"capability_override","rules":[]}}}',
        source_configuration_id=None,
        previous_configuration_id=third_configuration.configuration_id,
        reason="fourth",
        locked=True,
    )

    container.install_configuration(second_configuration)
    container.install_configuration(third_configuration)
    container.install_configuration(fourth_configuration)

    assert first_configuration.cleaned is True
    assert len(container.frame_acl_history) == 1
    assert container.frame_acl_history == [third_configuration]


def test_frame_acl_container_install_rejects_wrong_frame_configuration() -> None:
    """
    Verify container install fails when configuration targets another frame.

    Returns:
        None.
    """
    container = FrameACLContainer("ops")
    wrong_configuration = FrameACLConfiguration.create_default("finance")

    with pytest.raises(ValueError, match="targets frame 'finance', expected 'ops'"):
        container.install_configuration(wrong_configuration)


def test_frame_acl_container_install_rejects_rule_invalid_configuration() -> None:
    """
    Verify container install fails when validator rejects the typed rules.

    Returns:
        None.
    """
    container = FrameACLContainer("ops")
    invalid_configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        container.frame_acl_configuration,
        reason="invalid",
    )
    invalid_configuration.set_view_configuration(
        FrameACLViewConfiguration(
            profile_name="custom",
            profile_version="0.0.1",
            minimum_spell_payload_type="detailed",
            frame_override_ruleset=FrameACLRuleSet(
                "frame_override",
                rules=[
                    FrameACLRule(
                        rule_name="bad_invoke",
                        operation="invoke_method",
                        effect="allow",
                    )
                ],
            ),
        )
    )
    invalid_configuration.finalize()

    with pytest.raises(ValueError, match="Unsupported operation 'invoke_method' in view.frame ruleset"):
        container.install_configuration(invalid_configuration)


def test_frame_acl_container_select_and_rollback_delegate_to_chain() -> None:
    """
    Verify container selection helpers delegate to the underlying chain.

    Returns:
        None.
    """
    container = FrameACLContainer("ops")
    original = container.frame_acl_configuration
    next_configuration = FrameACLConfiguration.from_json_configuration_string(
        frame_name="ops",
        json_configuration_string='{"frame_name":"ops","view_configuration":{"profile_name":"hybrid","profile_version":"0.0.1","minimum_spell_payload_type":"detailed","frame_override_ruleset":{"name":"frame_override","rules":[]},"conduit_override_ruleset":{"name":"conduit_override","rules":[]},"spell_override_ruleset":{"name":"spell_override","rules":[]},"member_override_ruleset":{"name":"member_override","rules":[]}},"codegen_configuration":{"profile_name":"safe","profile_version":"0.0.1","frame_override_ruleset":{"name":"frame_override","rules":[]},"conduit_override_ruleset":{"name":"conduit_override","rules":[]},"spell_override_ruleset":{"name":"spell_override","rules":[]},"capability_override_ruleset":{"name":"capability_override","rules":[]}}}',
        source_configuration_id=None,
        previous_configuration_id=original.configuration_id,
        reason="next",
        locked=True,
    )
    container.install_configuration(next_configuration)

    selected = container.select_current_configuration(original.configuration_id)
    rolled_back = container.rollback_to_configuration(next_configuration.configuration_id)

    assert selected is original
    assert rolled_back is next_configuration


def test_frame_acl_container_cleanup_cleans_all_owned_acl_objects() -> None:
    """
    Verify cleanup cascades through builder, validator, current config, and
    history.

    Returns:
        None.
    """
    container = FrameACLContainer("ops")
    previous_configuration = container.frame_acl_configuration
    next_configuration = FrameACLConfiguration.from_json_configuration_string(
        frame_name="ops",
        json_configuration_string='{"frame_name":"ops","view_configuration":{"profile_name":"hybrid","profile_version":"0.0.1","minimum_spell_payload_type":"detailed","frame_override_ruleset":{"name":"frame_override","rules":[]},"conduit_override_ruleset":{"name":"conduit_override","rules":[]},"spell_override_ruleset":{"name":"spell_override","rules":[]},"member_override_ruleset":{"name":"member_override","rules":[]}},"codegen_configuration":{"profile_name":"safe","profile_version":"0.0.1","frame_override_ruleset":{"name":"frame_override","rules":[]},"conduit_override_ruleset":{"name":"conduit_override","rules":[]},"spell_override_ruleset":{"name":"spell_override","rules":[]},"capability_override_ruleset":{"name":"capability_override","rules":[]}}}',
        source_configuration_id=None,
        previous_configuration_id=previous_configuration.configuration_id,
        reason="cleanup",
        locked=True,
    )
    container.install_configuration(next_configuration)
    builder = container.frame_acl_builder
    validator = container.frame_acl_validator
    chain = container.frame_acl_configuration_chain

    container.cleanup()

    assert builder.cleaned is True
    assert validator.cleaned is True
    assert previous_configuration.cleaned is True
    assert next_configuration.cleaned is True
    assert chain.cleaned is True
    assert container._lock is None
    assert container._frame_acl_builder is None
    assert container._frame_acl_validator is None


def test_frame_acl_container_cleanup_is_idempotent() -> None:
    """
    Verify cleanup can be called repeatedly.

    Returns:
        None.
    """
    container = FrameACLContainer("ops")

    container.cleanup()
    container.cleanup()

    assert container.cleaned is True


def test_frame_acl_container_cleanup_rechecks_cleaned_inside_lock() -> None:
    """
    Verify cleanup returns early when another thread already cleaned the container.

    Returns:
        None.
    """

    class _CoordinatedLock:
        def __init__(self) -> None:
            self._entered_first = threading.Event()
            self._second_attempted = threading.Event()
            self._lock = threading.RLock()

        def __enter__(self):
            if self._entered_first.is_set():
                self._second_attempted.set()
            self._lock.acquire()
            if not self._entered_first.is_set():
                self._entered_first.set()
                assert self._second_attempted.wait(timeout=1.0)
            return self

        def __exit__(self, exc_type, exc, tb):
            self._lock.release()

    container = FrameACLContainer("ops")
    coordinated_lock = _CoordinatedLock()
    container._lock = coordinated_lock

    thread_results = []

    def _run_cleanup() -> None:
        container.cleanup()
        thread_results.append(True)

    first = threading.Thread(target=_run_cleanup)
    second = threading.Thread(target=_run_cleanup)
    first.start()
    coordinated_lock._entered_first.wait(timeout=1.0)
    second.start()
    first.join(timeout=1.0)
    second.join(timeout=1.0)

    assert thread_results == [True, True]
    assert container.cleaned is True
    assert container._lock is None

