import json
import threading

import pytest

from melder.aether.nexus.acl.frame_acl_configuration import FrameACLConfiguration
from melder.aether.nexus.acl.frame_acl_configuration_chain import (
    FrameACLConfigurationChain,
)


def _make_locked_configuration(
        frame_name: str,
        *,
        reason: str,
        json_payload: str,
) -> FrameACLConfiguration:
    """
    Build one locked ACL configuration node for chain tests.

    Args:
        frame_name:
            Owning frame name.
        reason:
            Creation reason.
        json_payload:
            JSON payload string.

    Returns:
        FrameACLConfiguration: Locked configuration node.
    """
    configuration = FrameACLConfiguration.from_json_configuration_string(
        frame_name=frame_name,
        json_configuration_string=json_payload,
        source_configuration_id=None,
        previous_configuration_id=None,
        reason=reason,
        locked=False,
    )
    configuration.finalize()
    return configuration


def _build_typed_json_payload(
        frame_name: str,
        *,
        view_marker: str = "",
        codegen_marker: str = "",
) -> str:
    """
    Build one minimal typed ACL JSON payload for configuration-chain tests.

    Args:
        frame_name:
            Frame name stored in the JSON payload.
        view_marker:
            Optional suffix used to vary the view payload content.
        codegen_marker:
            Optional suffix used to vary the codegen payload content.

    Returns:
        str:
            JSON payload string that matches the live typed ACL contract.
    """
    frame_override_name = "frame_override"
    capability_override_name = "capability_override"
    if view_marker:
        frame_override_name = "frame_override_{0}".format(view_marker)
    if codegen_marker:
        capability_override_name = "capability_override_{0}".format(
            codegen_marker
        )
    return json.dumps(
        {
            "frame_name": frame_name,
            "view_configuration": {
                "profile_name": "safe",
                "profile_version": "0.0.1",
                "minimum_spell_payload_type": "detailed",
                "frame_override_ruleset": {
                    "name": frame_override_name,
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
                "profile_name": "safe",
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
                    "name": capability_override_name,
                    "rules": [],
                },
            },
        },
        sort_keys=True,
    )


def test_chain_starts_with_one_default_head_and_current() -> None:
    """
    Verify chain initialization creates one default head/current config.

    Returns:
        None.
    """
    chain = FrameACLConfigurationChain("ops")

    head = chain.get_head_configuration()
    current = chain.get_current_configuration()

    assert head is current
    assert chain.frame_name == "ops"
    assert chain.history_limit == 30
    assert chain.head_configuration_id == head.configuration_id
    assert chain.current_configuration_id == current.configuration_id
    assert chain.count_configurations() == 1
    assert chain.list_configuration_ids() == [head.configuration_id]


def test_chain_rejects_invalid_init_inputs() -> None:
    """
    Verify chain requires a frame name and valid history limit.

    Returns:
        None.
    """
    with pytest.raises(ValueError, match="frame_name cannot be empty"):
        FrameACLConfigurationChain("")

    with pytest.raises(ValueError, match="history_limit must be an integer >= 1"):
        FrameACLConfigurationChain("ops", history_limit=0)


def test_chain_insert_head_sets_previous_pointer_and_head() -> None:
    """
    Verify head insertion links the previous pointer and updates head/current.

    Returns:
        None.
    """
    chain = FrameACLConfigurationChain("ops")
    old_head = chain.get_head_configuration()
    next_configuration = _make_locked_configuration(
        "ops",
        reason="new-head",
        json_payload=_build_typed_json_payload("ops", view_marker="visible"),
    )

    inserted = chain.insert_head_configuration(
        next_configuration,
        select_as_current=True,
    )

    assert inserted is next_configuration
    assert inserted.previous_configuration_id == old_head.configuration_id
    assert chain.head_configuration_id == inserted.configuration_id
    assert chain.current_configuration_id == inserted.configuration_id


def test_chain_insert_head_can_leave_current_on_older_config() -> None:
    """
    Verify insertion can update head without changing current.

    Returns:
        None.
    """
    chain = FrameACLConfigurationChain("ops")
    old_current = chain.get_current_configuration()
    next_configuration = _make_locked_configuration(
        "ops",
        reason="new-head",
        json_payload=_build_typed_json_payload("ops", view_marker="visible"),
    )

    chain.insert_head_configuration(next_configuration, select_as_current=False)

    assert chain.head_configuration_id == next_configuration.configuration_id
    assert chain.current_configuration_id == old_current.configuration_id


def test_chain_insert_head_rejects_unlocked_wrong_frame_and_duplicates() -> None:
    """
    Verify insertion rejects invalid config-node inputs.

    Returns:
        None.
    """
    chain = FrameACLConfigurationChain("ops")

    unlocked = FrameACLConfiguration.create_new_from_acl_configuration(
        chain.get_current_configuration(),
        reason="draft",
    )
    with pytest.raises(ValueError, match="Configuration must be locked"):
        chain.insert_head_configuration(unlocked, select_as_current=True)

    wrong_frame = _make_locked_configuration(
        "finance",
        reason="wrong-frame",
        json_payload=_build_typed_json_payload("finance"),
    )
    with pytest.raises(ValueError, match="targets frame 'finance', expected 'ops'"):
        chain.insert_head_configuration(wrong_frame, select_as_current=True)

    existing = chain.get_head_configuration()
    with pytest.raises(ValueError, match="already exists in the chain"):
        chain.insert_head_configuration(existing, select_as_current=True)

    with pytest.raises(TypeError, match="configuration must be a FrameACLConfiguration"):
        chain.insert_head_configuration(None, select_as_current=True)


def test_chain_has_get_and_missing_config_behavior() -> None:
    """
    Verify direct config lookup and missing-id behavior.

    Returns:
        None.
    """
    chain = FrameACLConfigurationChain("ops")
    current = chain.get_current_configuration()

    assert chain.has_configuration(current.configuration_id) is True
    assert chain.get_configuration(current.configuration_id) is current

    with pytest.raises(KeyError, match="missing"):
        chain.get_configuration("missing")


def test_chain_list_configurations_returns_newest_first() -> None:
    """
    Verify listing walks the chain from head to tail.

    Returns:
        None.
    """
    chain = FrameACLConfigurationChain("ops")
    first = _make_locked_configuration(
        "ops",
        reason="one",
        json_payload=_build_typed_json_payload("ops", view_marker="v1"),
    )
    second = _make_locked_configuration(
        "ops",
        reason="two",
        json_payload=_build_typed_json_payload("ops", view_marker="v2"),
    )

    chain.insert_head_configuration(first, select_as_current=True)
    chain.insert_head_configuration(second, select_as_current=True)

    listed = chain.list_configurations()

    assert [config.configuration_id for config in listed] == [
        second.configuration_id,
        first.configuration_id,
        chain.get_configuration(first.previous_configuration_id).configuration_id,
    ]


def test_chain_select_and_rollback_move_current_pointer() -> None:
    """
    Verify current selection and rollback both move the current pointer.

    Returns:
        None.
    """
    chain = FrameACLConfigurationChain("ops")
    original = chain.get_current_configuration()
    next_configuration = _make_locked_configuration(
        "ops",
        reason="new-head",
        json_payload=_build_typed_json_payload("ops", view_marker="visible"),
    )
    chain.insert_head_configuration(next_configuration, select_as_current=True)

    selected = chain.select_current_configuration(original.configuration_id)

    assert selected is original
    assert chain.current_configuration_id == original.configuration_id

    rolled_back = chain.rollback_to_configuration(next_configuration.configuration_id)

    assert rolled_back is next_configuration
    assert chain.current_configuration_id == next_configuration.configuration_id


def test_chain_create_new_from_acl_configuration_copies_existing_payload() -> None:
    """
    Verify create-from copies payload from a historical config in the chain.

    Returns:
        None.
    """
    chain = FrameACLConfigurationChain("ops")
    current = chain.get_current_configuration()

    copied = chain.create_new_from_acl_configuration(
        current.configuration_id,
        reason="copy",
    )

    assert copied.frame_name == "ops"
    assert copied.source_configuration_id == current.configuration_id
    assert copied.previous_configuration_id is None
    assert copied.locked is False
    assert copied.to_json_string() == current.to_json_string()


def test_chain_trim_tail_drops_oldest_when_over_limit() -> None:
    """
    Verify tail trimming removes the oldest configs once over the limit.

    Returns:
        None.
    """
    chain = FrameACLConfigurationChain("ops", history_limit=3)
    first_default = chain.get_current_configuration()
    first_default_id = first_default.configuration_id
    second = _make_locked_configuration(
        "ops",
        reason="2",
        json_payload=_build_typed_json_payload("ops", view_marker="v2"),
    )
    third = _make_locked_configuration(
        "ops",
        reason="3",
        json_payload=_build_typed_json_payload("ops", view_marker="v3"),
    )
    fourth = _make_locked_configuration(
        "ops",
        reason="4",
        json_payload=_build_typed_json_payload("ops", view_marker="v4"),
    )

    chain.insert_head_configuration(second, select_as_current=True)
    chain.insert_head_configuration(third, select_as_current=True)
    chain.insert_head_configuration(fourth, select_as_current=True)

    assert first_default.cleaned is True
    assert chain.count_configurations() == 3
    assert first_default_id not in chain.list_configuration_ids()


def test_chain_trim_tail_preserves_old_current_selection() -> None:
    """
    Verify trimming stops when the oldest retained node is still the current
    selection.

    Returns:
        None.
    """
    chain = FrameACLConfigurationChain("ops", history_limit=2)
    original = chain.get_current_configuration()
    second = _make_locked_configuration(
        "ops",
        reason="2",
        json_payload=_build_typed_json_payload("ops", view_marker="v2"),
    )
    third = _make_locked_configuration(
        "ops",
        reason="3",
        json_payload=_build_typed_json_payload("ops", view_marker="v3"),
    )

    chain.insert_head_configuration(second, select_as_current=True)
    chain.select_current_configuration(original.configuration_id)
    chain.insert_head_configuration(third, select_as_current=False)

    assert chain.count_configurations() == 3
    assert original.configuration_id in chain.list_configuration_ids()
    assert original.cleaned is False


def test_chain_list_limit_and_cleanup_work() -> None:
    """
    Verify listing limit works and cleanup clears owned configs.

    Returns:
        None.
    """
    chain = FrameACLConfigurationChain("ops")
    second = _make_locked_configuration(
        "ops",
        reason="2",
        json_payload=_build_typed_json_payload("ops", view_marker="v2"),
    )
    chain.insert_head_configuration(second, select_as_current=True)

    listed = chain.list_configurations(limit=1)
    owned_ids = chain.list_configuration_ids()

    assert listed == [second]
    assert len(owned_ids) == 2

    chain.cleanup()

    assert chain.cleaned is True
    assert chain._lock is None
    assert chain._configurations_by_id is None


def test_chain_list_configurations_rejects_invalid_limit() -> None:
    """
    Verify list_configurations validates the optional limit argument.

    Returns:
        None.
    """
    chain = FrameACLConfigurationChain("ops")

    with pytest.raises(ValueError, match="limit must be an integer >= 1 when provided"):
        chain.list_configurations(limit=0)


def test_chain_cleanup_is_idempotent() -> None:
    """
    Verify cleanup can be called repeatedly.

    Returns:
        None.
    """
    chain = FrameACLConfigurationChain("ops")

    chain.cleanup()
    chain.cleanup()

    assert chain.cleaned is True


def test_chain_cleanup_rechecks_cleaned_inside_lock() -> None:
    """
    Verify cleanup returns early when another thread cleans under the lock.

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

    chain = FrameACLConfigurationChain("ops")
    coordinated_lock = _CoordinatedLock()
    chain._lock = coordinated_lock

    thread_results = []

    def _run_cleanup() -> None:
        chain.cleanup()
        thread_results.append(True)

    first = threading.Thread(target=_run_cleanup)
    second = threading.Thread(target=_run_cleanup)
    first.start()
    coordinated_lock._entered_first.wait(timeout=1.0)
    second.start()
    first.join(timeout=1.0)
    second.join(timeout=1.0)

    assert thread_results == [True, True]
    assert chain.cleaned is True
    assert chain._lock is None

