import threading

import pytest

from melder.aether.nexus.acl.frame_acl_configuration_chain import (
    FrameACLConfigurationChain,
)
from melder.aether.nexus.acl.configurations.frame_acl_view_configuration import (
    FrameACLViewConfiguration,
)
from melder.aether.nexus.acl.configurations.profiles.view.frame_acl_view_profile import (
    FrameACLViewProfile,
)


def _make_locked_view_configuration(
        *,
        profile_name: str = "safe",
        marker: str = "default",
        reason: str = "test",
) -> FrameACLViewConfiguration:
    """
    Build one locked view configuration revision for chain tests.

    Returns:
        FrameACLViewConfiguration: Locked configuration revision.
    """
    payload = {
        "profile_name": profile_name,
        "profile_version": "0.0.1",
        "required_nexus_label": "default",
        "required_nexus_version": "0.0.1",
        "minimum_spell_payload_type": "detailed",
        "minimum_spell_payload_version": "0.0.1",
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
    }
    return FrameACLViewConfiguration.from_json_dict(
        payload,
        reason=reason,
        locked=True,
    )


def test_chain_starts_with_one_default_head_and_current() -> None:
    """
    Verify chain initialization creates one default head/current config.

    Returns:
        None.
    """
    default_configuration = FrameACLViewConfiguration.from_profile(
        FrameACLViewProfile.create_safe(),
        reason="default",
        locked=True,
    )
    chain = FrameACLConfigurationChain(
        family_name="view",
        contract_name="default",
        default_configuration=default_configuration,
    )

    head = chain.get_head_configuration()
    current = chain.get_current_configuration()

    assert head is current
    assert chain.family_name == "view"
    assert chain.contract_name == "default"
    assert chain.history_limit == 30
    assert chain.head_configuration_id == head.configuration_id
    assert chain.current_configuration_id == current.configuration_id
    assert chain.count_configurations() == 1
    assert chain.list_configuration_ids() == [head.configuration_id]


def test_chain_rejects_invalid_init_inputs() -> None:
    """
    Verify chain requires family/contract/default config and valid history limit.

    Returns:
        None.
    """
    default_configuration = _make_locked_view_configuration()

    with pytest.raises(ValueError, match="family_name cannot be empty"):
        FrameACLConfigurationChain(
            family_name="",
            contract_name="default",
            default_configuration=default_configuration,
        )

    with pytest.raises(ValueError, match="contract_name cannot be empty"):
        FrameACLConfigurationChain(
            family_name="view",
            contract_name="",
            default_configuration=default_configuration,
        )

    with pytest.raises(ValueError, match="history_limit must be an integer >= 1"):
        FrameACLConfigurationChain(
            family_name="view",
            contract_name="default",
            default_configuration=default_configuration,
            history_limit=0,
        )


def test_chain_insert_head_sets_previous_pointer_and_head() -> None:
    """
    Verify head insertion links the previous pointer and updates head/current.

    Returns:
        None.
    """
    chain = FrameACLConfigurationChain(
        family_name="view",
        contract_name="default",
        default_configuration=_make_locked_view_configuration(marker="v1"),
    )
    old_head = chain.get_head_configuration()
    next_configuration = _make_locked_view_configuration(marker="v2")

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
    chain = FrameACLConfigurationChain(
        family_name="view",
        contract_name="default",
        default_configuration=_make_locked_view_configuration(marker="v1"),
    )
    old_current = chain.get_current_configuration()
    next_configuration = _make_locked_view_configuration(marker="v2")

    chain.insert_head_configuration(next_configuration, select_as_current=False)

    assert chain.head_configuration_id == next_configuration.configuration_id
    assert chain.current_configuration_id == old_current.configuration_id


def test_chain_insert_head_rejects_unlocked_and_duplicates() -> None:
    """
    Verify insertion rejects invalid config-node inputs.

    Returns:
        None.
    """
    chain = FrameACLConfigurationChain(
        family_name="view",
        contract_name="default",
        default_configuration=_make_locked_view_configuration(marker="v1"),
    )

    unlocked = FrameACLViewConfiguration.create_new_from_configuration(
        chain.get_current_configuration(),
        reason="draft",
    )
    with pytest.raises(ValueError, match="Configuration must be locked"):
        chain.insert_head_configuration(unlocked, select_as_current=True)

    existing = chain.get_head_configuration()
    with pytest.raises(ValueError, match="already exists in the chain"):
        chain.insert_head_configuration(existing, select_as_current=True)

    with pytest.raises(TypeError, match="configuration must support"):
        chain.insert_head_configuration(None, select_as_current=True)


def test_chain_list_configurations_returns_newest_first() -> None:
    """
    Verify listing walks the chain from head to tail.

    Returns:
        None.
    """
    chain = FrameACLConfigurationChain(
        family_name="view",
        contract_name="default",
        default_configuration=_make_locked_view_configuration(marker="v1"),
    )
    first = _make_locked_view_configuration(marker="v2")
    second = _make_locked_view_configuration(marker="v3")

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
    chain = FrameACLConfigurationChain(
        family_name="view",
        contract_name="default",
        default_configuration=_make_locked_view_configuration(marker="v1"),
    )
    original = chain.get_current_configuration()
    next_configuration = _make_locked_view_configuration(marker="v2")
    chain.insert_head_configuration(next_configuration, select_as_current=True)

    selected = chain.select_current_configuration(original.configuration_id)
    rolled_back = chain.rollback_to_configuration(next_configuration.configuration_id)

    assert selected is original
    assert rolled_back is next_configuration
    assert chain.current_configuration_id == next_configuration.configuration_id


def test_chain_create_new_from_acl_configuration_copies_existing_payload() -> None:
    """
    Verify create-from copies payload from a historical config in the chain.

    Returns:
        None.
    """
    chain = FrameACLConfigurationChain(
        family_name="view",
        contract_name="default",
        default_configuration=_make_locked_view_configuration(marker="v1"),
    )
    current = chain.get_current_configuration()

    copied = chain.create_new_from_acl_configuration(
        current.configuration_id,
        reason="copy",
    )

    assert copied.source_configuration_id == current.configuration_id
    assert copied.previous_configuration_id is None
    assert copied.locked is False
    assert copied.to_json_dict() == current.to_json_dict()


def test_chain_trim_tail_drops_oldest_when_over_limit() -> None:
    """
    Verify tail trimming removes the oldest configs once over the limit.

    Returns:
        None.
    """
    original = _make_locked_view_configuration(marker="v1")
    original_configuration_id = original.configuration_id
    chain = FrameACLConfigurationChain(
        family_name="view",
        contract_name="default",
        default_configuration=original,
        history_limit=2,
    )
    second = _make_locked_view_configuration(marker="v2")
    third = _make_locked_view_configuration(marker="v3")

    chain.insert_head_configuration(second, select_as_current=True)
    chain.insert_head_configuration(third, select_as_current=True)

    assert original.cleaned is True
    assert chain.count_configurations() == 2
    assert original_configuration_id not in chain.list_configuration_ids()


def test_chain_cleanup_is_idempotent() -> None:
    """
    Verify cleanup can be called repeatedly.

    Returns:
        None.
    """
    chain = FrameACLConfigurationChain(
        family_name="view",
        contract_name="default",
        default_configuration=_make_locked_view_configuration(marker="v1"),
    )

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

    chain = FrameACLConfigurationChain(
        family_name="view",
        contract_name="default",
        default_configuration=_make_locked_view_configuration(marker="v1"),
    )
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
