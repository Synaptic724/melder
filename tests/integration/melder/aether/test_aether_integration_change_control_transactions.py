from __future__ import annotations

import hashlib
import threading
import time
import warnings
from typing import Optional

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeTransactionType,
)
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicService


from tests._frame_posture_test_support import (
    apply_automatic_defaults_for_spellbook_configuration,
    apply_dynamic_defaults_for_spellbook_configuration,
)
@pytest.fixture(autouse=True)
def reset_aether_singleton_for_integration() -> None:
    """
    Purpose:
        Ensure integration tests start with a clean Aether singleton.
    Contract:
        - Resets the Aether singleton before the test runs.
        - Rebinds Spellbook._aether and Conduit._aether to the new instance.
        - Resets the singleton again after the test for isolation.
    Returns:
        None.
    """
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _make_configuration(
    *,
    aether_frame: str,
    dynamic: bool,
    workers: int = 1,
) -> SpellbookConfiguration:
    """
    Purpose:
        Build a configuration for change-control integration tests.
    Contract:
        - system_state is set to automatic or dynamic defaults.
        - phase_scheduler_workers_per_spellbook is configured.
    Args:
        aether_frame: Target frame name.
        dynamic: Whether to enable dynamic defaults.
        workers: Scheduler worker count per spellbook.
    Returns:
        SpellbookConfiguration: Configured instance.
    """
    configuration = SpellbookConfiguration(aether_frame=aether_frame)
    if dynamic:
        apply_dynamic_defaults_for_spellbook_configuration(configuration)
    else:
        apply_automatic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", workers)
    return configuration


def _get_local_spell_by_version_id(
        spellbook: Spellbook,
        spell_id: str,
) -> Optional[object]:
    """
    Purpose:
        Resolve one locally owned spell by its current version id.
    Contract:
        - Returns the first local spell whose SpellIndex.current matches the
          supplied version id.
        - Returns None when no local spell matches.
    Args:
        spellbook: Spellbook whose local spell map should be searched.
        spell_id: Current version id to resolve.
    Returns:
        Optional[object]: Matching local spell object, or None when absent.
    """
    for spell_index, spell in spellbook.spells.items():
        if spell_index.current == spell_id:
            return spell
    return None


def test_change_control_bind_transaction_opens_and_closes_embargoes() -> None:
    """
    Purpose:
        Validate bind transactions open implicit embargo scopes and close on end.
    Contract:
        - Embargo scopes include spellbook and binding keys.
        - In-flight request is cleared after end_transaction.
    Returns:
        None.
    Raises:
        AssertionError: If embargo or in-flight state is incorrect.
    """
    frame_name = "frame-cc-bind"
    configuration = _make_configuration(aether_frame=frame_name, dynamic=True)
    spellbook = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    conduit = spellbook.conjure(automatic=False, name="root")
    change_control = Aether()._get_change_control_manager(frame_name)
    embargo_manager = change_control.embargo_manager()
    transaction_manager = change_control.transaction_manager()
    binding_key = ("frame", "__default__")

    spellbook.begin_transaction(
        "bind",
        binding_keys=[binding_key],
        scope_keys=["scope:custom"],
    )
    try:
        in_flight = transaction_manager.list_in_flight()
        assert len(in_flight) == 1
        assert in_flight[0].request_type is ChangeTransactionType.BIND
        embargoed = embargo_manager.describe()["embargoed_scopes"]
        assert f"scope:spellbook:{spellbook._id}" in embargoed
        assert f"binding:{binding_key[0]}:{binding_key[1]}" in embargoed
        assert "scope:custom" in embargoed
    finally:
        spellbook.end_transaction("bind")

    assert transaction_manager.list_in_flight() == []
    assert embargo_manager.describe()["embargo_count"] == 0
    conduit.cleanup()
    spellbook.cleanup()


def test_change_control_update_staged_request_extends_embargo_scopes() -> None:
    """
    Purpose:
        Validate staged updates extend embargo scopes for admitted requests.
    Contract:
        - Initial embargoes omit binding scopes when none are supplied.
        - update_staged_request adds binding scope embargoes.
    Returns:
        None.
    Raises:
        AssertionError: If staged updates do not extend embargo scopes.
    """
    frame_name = "frame-cc-staged"
    configuration = _make_configuration(aether_frame=frame_name, dynamic=True)
    spellbook = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    conduit = spellbook.conjure(automatic=False, name="root")
    change_control = Aether()._get_change_control_manager(frame_name)
    embargo_manager = change_control.embargo_manager()
    transaction_manager = change_control.transaction_manager()
    binding_key = ("svc", "primary")

    spellbook.begin_transaction("bind")
    try:
        request = transaction_manager.list_in_flight()[0]
        embargoed_before = embargo_manager.describe()["embargoed_scopes"]
        assert not any(scope.startswith("binding:") for scope in embargoed_before)

        assert change_control.update_staged_request(
            request.request_id,
            binding_keys=[binding_key],
        )
        embargoed_after = embargo_manager.describe()["embargoed_scopes"]
        assert f"binding:{binding_key[0]}:{binding_key[1]}" in embargoed_after
    finally:
        spellbook.end_transaction("bind")

    conduit.cleanup()
    spellbook.cleanup()


def test_change_control_disable_allows_overlapping_requests() -> None:
    """
    Purpose:
        Validate disabled change-control stops conflict rejection.
    Contract:
        - Overlapping scope keys do not cause admission failure when
          change-control is disabled.
        - Strategy-owned same-thread bind starts still join the active root
          session instead of creating a second independent root request.
    Returns:
        None.
    Raises:
        AssertionError: If overlapping requests are rejected when disabled.
    """
    frame_name = "frame-cc-disabled"
    configuration = _make_configuration(aether_frame=frame_name, dynamic=True)
    spellbook_a = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    spellbook_b = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    conduit_a = spellbook_a.conjure(automatic=False, name="root-a")
    conduit_b = spellbook_b.conjure(automatic=False, name="root-b")
    change_control = Aether()._get_change_control_manager(frame_name)
    change_control.disable_change_control()

    spellbook_a.begin_transaction("bind", scope_keys=["scope-shared"])
    spellbook_b.begin_transaction("bind", scope_keys=["scope-shared"])
    transaction_manager = change_control.transaction_manager()
    assert len(transaction_manager.list_in_flight()) == 2
    spellbook_a.end_transaction("bind")
    spellbook_b.end_transaction("bind")
    assert transaction_manager.list_in_flight() == []

    conduit_a.cleanup()
    conduit_b.cleanup()
    spellbook_a.cleanup()
    spellbook_b.cleanup()


def test_change_control_scope_hash_conflict_rejects_overlap() -> None:
    """
    Purpose:
        Validate same-thread bind starts join before conflict admission.
    Contract:
        - A second same-thread bind start does not open a second root request.
        - The active bind root remains the single in-flight request.
    Returns:
        None.
    Raises:
        AssertionError: If the second bind opens another root request.
    """
    frame_name = "frame-cc-hash"
    configuration = _make_configuration(aether_frame=frame_name, dynamic=True)
    spellbook_a = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    spellbook_b = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    conduit_a = spellbook_a.conjure(automatic=False, name="root-a")
    conduit_b = spellbook_b.conjure(automatic=False, name="root-b")
    scope_hash = hashlib.sha256("shared-scope".encode("utf-8")).hexdigest()

    spellbook_a.begin_transaction("bind", scope_hashes=[scope_hash])
    try:
        with pytest.raises(RuntimeError, match="Change-control admission denied"):
            spellbook_b.begin_transaction("bind", scope_hashes=[scope_hash])
        assert len(
            Aether()._get_change_control_manager(frame_name).transaction_manager().list_in_flight()
        ) == 1
    finally:
        spellbook_a.end_transaction("bind")

    conduit_a.cleanup()
    conduit_b.cleanup()
    spellbook_a.cleanup()
    spellbook_b.cleanup()


def test_change_control_disable_allows_overlapping_requests_for_three_roots() -> None:
    """
    Purpose:
        Validate disabled change-control allows three rooted bind requests to overlap.
    Contract:
        - Three rooted spellbooks may hold overlapping bind transactions at once
          when change-control is disabled.
        - All three requests appear in the in-flight registry together.
        - Ending all three clears in-flight state.
    Returns:
        None.
    Raises:
        AssertionError: If disabled mode still rejects overlapping three-root binds.
    """
    frame_name = "frame-cc-disabled-three-roots"
    configuration = _make_configuration(aether_frame=frame_name, dynamic=True)
    spellbook_a = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    spellbook_b = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    spellbook_c = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    conduit_a = spellbook_a.conjure(automatic=False, name="root-a")
    conduit_b = spellbook_b.conjure(automatic=False, name="root-b")
    conduit_c = spellbook_c.conjure(automatic=False, name="root-c")
    change_control = Aether()._get_change_control_manager(frame_name)
    change_control.disable_change_control()

    spellbook_a.begin_transaction("bind", scope_keys=["scope-shared"])
    spellbook_b.begin_transaction("bind", scope_keys=["scope-shared"])
    spellbook_c.begin_transaction("bind", scope_keys=["scope-shared"])
    transaction_manager = change_control.transaction_manager()
    assert len(transaction_manager.list_in_flight()) == 3

    spellbook_a.end_transaction("bind")
    spellbook_b.end_transaction("bind")
    spellbook_c.end_transaction("bind")
    assert transaction_manager.list_in_flight() == []

    conduit_a.cleanup()
    conduit_b.cleanup()
    conduit_c.cleanup()
    spellbook_a.cleanup()
    spellbook_b.cleanup()
    spellbook_c.cleanup()


def test_change_control_mediator_disabled_allows_three_threaded_root_binds_to_enter_without_queueing() -> None:
    """
    Purpose:
        Validate mediator disabled mode stops cross-thread root-session gating.
    Contract:
        - Three rooted spellbooks on three threads can all enter bind
          transactions with distinct scopes without queueing behind one
          another.
        - The proof is cross-thread, not same-thread recursion.
    Returns:
        None.
    Raises:
        AssertionError: If disabled mode still blocks competing root threads.
    """
    frame_name = "frame-cc-disabled-three-threaded-roots"
    configuration = _make_configuration(aether_frame=frame_name, dynamic=True)
    spellbook_a = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    spellbook_b = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    spellbook_c = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    conduit_a = spellbook_a.conjure(automatic=False, name="root-a")
    conduit_b = spellbook_b.conjure(automatic=False, name="root-b")
    conduit_c = spellbook_c.conjure(automatic=False, name="root-c")
    change_control = Aether()._get_change_control_manager(frame_name)
    mediator = change_control.transaction_mediator()
    mediator.configure(
        change_control_mode="disabled",
        allow_multiple_root_transactions=False,
        queue_competing_root_transactions=False,
        max_transaction_wait_time_in_seconds=1.0,
    )

    start_barrier = threading.Barrier(4)
    release_event = threading.Event()
    started_labels: list[str] = []
    failures: list[BaseException] = []

    def _run_bind(
            label: str,
            spellbook: Spellbook,
            scope_key: str,
    ) -> None:
        try:
            start_barrier.wait()
            spellbook.begin_transaction("bind", scope_keys=[scope_key])
            started_labels.append(label)
            release_event.wait(timeout=1.0)
            spellbook.end_transaction("bind")
        except BaseException as exc:
            failures.append(exc)

    thread_a = threading.Thread(
        target=_run_bind,
        args=("a", spellbook_a, "scope-a"),
        name="bind-root-a",
    )
    thread_b = threading.Thread(
        target=_run_bind,
        args=("b", spellbook_b, "scope-b"),
        name="bind-root-b",
    )
    thread_c = threading.Thread(
        target=_run_bind,
        args=("c", spellbook_c, "scope-c"),
        name="bind-root-c",
    )
    thread_a.start()
    thread_b.start()
    thread_c.start()

    start_barrier.wait()

    deadline = time.monotonic() + 1.0
    while len(started_labels) < 3 and time.monotonic() < deadline:
        time.sleep(0.01)

    assert len(started_labels) == 3
    assert failures == []
    assert len(change_control.transaction_manager().list_in_flight()) == 3

    release_event.set()
    thread_a.join(timeout=5)
    thread_b.join(timeout=5)
    thread_c.join(timeout=5)
    assert thread_a.is_alive() is False
    assert thread_b.is_alive() is False
    assert thread_c.is_alive() is False
    assert failures == []
    assert change_control.transaction_manager().list_in_flight() == []

    conduit_a.cleanup()
    conduit_b.cleanup()
    conduit_c.cleanup()
    spellbook_a.cleanup()
    spellbook_b.cleanup()
    spellbook_c.cleanup()


def test_change_control_scope_hash_conflict_rejects_overlap_for_three_roots() -> None:
    """
    Purpose:
        Validate strict-mode admission rejects overlapping three-root bind requests.
    Contract:
        - The first root bind is admitted.
        - The second and third overlapping root binds are rejected.
        - The active bind root remains the single in-flight request.
    Returns:
        None.
    Raises:
        AssertionError: If strict mode admits overlapping three-root binds.
    """
    frame_name = "frame-cc-strict-three-roots"
    configuration = _make_configuration(aether_frame=frame_name, dynamic=True)
    spellbook_a = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    spellbook_b = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    spellbook_c = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    conduit_a = spellbook_a.conjure(automatic=False, name="root-a")
    conduit_b = spellbook_b.conjure(automatic=False, name="root-b")
    conduit_c = spellbook_c.conjure(automatic=False, name="root-c")
    change_control = Aether()._get_change_control_manager(frame_name)
    change_control.transaction_mediator().configure(
        change_control_mode="strict",
        allow_multiple_root_transactions=False,
        queue_competing_root_transactions=False,
        max_transaction_wait_time_in_seconds=1.0,
    )
    scope_hash = hashlib.sha256("shared-scope".encode("utf-8")).hexdigest()

    spellbook_a.begin_transaction("bind", scope_hashes=[scope_hash])
    try:
        with pytest.raises(RuntimeError, match="Change-control admission denied"):
            spellbook_b.begin_transaction("bind", scope_hashes=[scope_hash])
        with pytest.raises(RuntimeError, match="Change-control admission denied"):
            spellbook_c.begin_transaction("bind", scope_hashes=[scope_hash])
        assert len(change_control.transaction_manager().list_in_flight()) == 1
    finally:
        spellbook_a.end_transaction("bind")

    conduit_a.cleanup()
    conduit_b.cleanup()
    conduit_c.cleanup()
    spellbook_a.cleanup()
    spellbook_b.cleanup()
    spellbook_c.cleanup()


def test_change_control_queue_allows_three_roots_one_by_one_in_fifo_order() -> None:
    """
    Purpose:
        Validate queued root-session policy serializes three rooted bind transactions.
    Contract:
        - Root A starts immediately.
        - Root B and root C wait while A is active.
        - After A ends, B starts first.
        - After B ends, C starts next.
    Returns:
        None.
    Raises:
        AssertionError: If queued three-root bind order is not FIFO.
    """
    frame_name = "frame-cc-queue-three-roots"
    configuration = _make_configuration(aether_frame=frame_name, dynamic=True)
    spellbook_a = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    spellbook_b = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    spellbook_c = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    conduit_a = spellbook_a.conjure(automatic=False, name="root-a")
    conduit_b = spellbook_b.conjure(automatic=False, name="root-b")
    conduit_c = spellbook_c.conjure(automatic=False, name="root-c")
    change_control = Aether()._get_change_control_manager(frame_name)
    change_control.transaction_mediator().configure(
        change_control_mode="strict",
        allow_multiple_root_transactions=False,
        queue_competing_root_transactions=True,
        max_transaction_wait_time_in_seconds=1.0,
    )

    spellbook_a.begin_transaction("bind", scope_keys=["scope-a"])
    admitted_order: list[str] = []
    failures: list[BaseException] = []
    b_started = threading.Event()
    c_started = threading.Event()
    b_release = threading.Event()
    c_release = threading.Event()

    def _run_bind(
            label: str,
            spellbook: Spellbook,
            scope_key: str,
            started: threading.Event,
            release: threading.Event,
    ) -> None:
        try:
            spellbook.begin_transaction("bind", scope_keys=[scope_key])
            admitted_order.append(label)
            started.set()
            release.wait(timeout=1.0)
            spellbook.end_transaction("bind")
        except BaseException as exc:
            failures.append(exc)
            started.set()

    thread_b = threading.Thread(
        target=_run_bind,
        args=("b", spellbook_b, "scope-b", b_started, b_release),
        name="bind-root-b",
    )
    thread_c = threading.Thread(
        target=_run_bind,
        args=("c", spellbook_c, "scope-c", c_started, c_release),
        name="bind-root-c",
    )
    thread_b.start()
    thread_c.start()

    assert b_started.wait(timeout=0.05) is False
    assert c_started.wait(timeout=0.05) is False

    spellbook_a.end_transaction("bind")

    assert b_started.wait(timeout=1.0) is True
    assert admitted_order == ["b"]
    assert c_started.wait(timeout=0.05) is False

    b_release.set()
    assert c_started.wait(timeout=1.0) is True
    assert admitted_order == ["b", "c"]

    c_release.set()
    thread_b.join(timeout=5)
    thread_c.join(timeout=5)
    assert thread_b.is_alive() is False
    assert thread_c.is_alive() is False
    assert failures == []
    assert change_control.transaction_manager().list_in_flight() == []

    conduit_a.cleanup()
    conduit_b.cleanup()
    conduit_c.cleanup()
    spellbook_a.cleanup()
    spellbook_b.cleanup()
    spellbook_c.cleanup()


def test_change_control_warn_allows_three_threaded_root_binds_without_queueing() -> None:
    """
    Purpose:
        Validate non-disabled warn mode allows concurrent three-root bind entry.
    Contract:
        - Three rooted spellbooks on three threads can all enter bind
          transactions without queueing when mediator mode is `warn`.
        - At least one RuntimeWarning is emitted for competing roots.
    Returns:
        None.
    Raises:
        AssertionError: If warn mode still serializes or rejects competing roots.
    """
    frame_name = "frame-cc-warn-three-threaded-roots"
    configuration = _make_configuration(aether_frame=frame_name, dynamic=True)
    spellbook_a = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    spellbook_b = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    spellbook_c = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    conduit_a = spellbook_a.conjure(automatic=False, name="root-a")
    conduit_b = spellbook_b.conjure(automatic=False, name="root-b")
    conduit_c = spellbook_c.conjure(automatic=False, name="root-c")
    change_control = Aether()._get_change_control_manager(frame_name)
    mediator = change_control.transaction_mediator()
    mediator.configure(
        change_control_mode="warn",
        allow_multiple_root_transactions=False,
        queue_competing_root_transactions=False,
        max_transaction_wait_time_in_seconds=1.0,
    )

    start_barrier = threading.Barrier(4)
    release_event = threading.Event()
    started_labels: list[str] = []
    failures: list[BaseException] = []
    captured_warnings: list[warnings.WarningMessage] = []

    def _run_bind(
            label: str,
            spellbook: Spellbook,
            scope_key: str,
    ) -> None:
        try:
            start_barrier.wait()
            with warnings.catch_warnings(record=True) as seen:
                warnings.simplefilter("always")
                spellbook.begin_transaction("bind", scope_keys=[scope_key])
                captured_warnings.extend(seen)
            started_labels.append(label)
            release_event.wait(timeout=1.0)
            spellbook.end_transaction("bind")
        except BaseException as exc:
            failures.append(exc)

    thread_a = threading.Thread(
        target=_run_bind,
        args=("a", spellbook_a, "scope-a"),
        name="warn-bind-root-a",
    )
    thread_b = threading.Thread(
        target=_run_bind,
        args=("b", spellbook_b, "scope-b"),
        name="warn-bind-root-b",
    )
    thread_c = threading.Thread(
        target=_run_bind,
        args=("c", spellbook_c, "scope-c"),
        name="warn-bind-root-c",
    )
    thread_a.start()
    thread_b.start()
    thread_c.start()

    start_barrier.wait()

    deadline = time.monotonic() + 1.0
    while len(started_labels) < 3 and time.monotonic() < deadline:
        time.sleep(0.01)

    assert len(started_labels) == 3
    assert failures == []
    assert len(change_control.transaction_manager().list_in_flight()) == 3
    assert captured_warnings

    release_event.set()
    thread_a.join(timeout=5)
    thread_b.join(timeout=5)
    thread_c.join(timeout=5)
    assert thread_a.is_alive() is False
    assert thread_b.is_alive() is False
    assert thread_c.is_alive() is False
    assert failures == []
    assert change_control.transaction_manager().list_in_flight() == []

    conduit_a.cleanup()
    conduit_b.cleanup()
    conduit_c.cleanup()
    spellbook_a.cleanup()
    spellbook_b.cleanup()
    spellbook_c.cleanup()


def test_change_control_queue_blocks_other_transaction_families_too() -> None:
    """
    Purpose:
        Validate queued root-session policy is global, not bind-only.
    Contract:
        - A bind root on one thread blocks a link root on another thread when
          queueing is enabled.
        - The link root is admitted only after the bind root exits.
    Returns:
        None.
    Raises:
        AssertionError: If queueing applies only to bind-family work.
    """
    frame_name = "frame-cc-queue-cross-family"
    configuration = _make_configuration(aether_frame=frame_name, dynamic=True)
    spellbook_a = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    spellbook_b = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    spellbook_c = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    conduit_a = spellbook_a.conjure(automatic=False, name="root-a")
    conduit_b = spellbook_b.conjure(automatic=False, name="root-b")
    conduit_c = spellbook_c.conjure(automatic=False, name="root-c")
    change_control = Aether()._get_change_control_manager(frame_name)
    change_control.transaction_mediator().configure(
        change_control_mode="strict",
        allow_multiple_root_transactions=False,
        queue_competing_root_transactions=True,
        max_transaction_wait_time_in_seconds=1.0,
    )

    link_started = threading.Event()
    link_release = threading.Event()
    failures: list[BaseException] = []

    spellbook_a.begin_transaction("bind", scope_keys=["scope-a"])

    def _run_link() -> None:
        try:
            conduit_b.begin_transaction("link", conduits=[conduit_b, conduit_c])
            link_started.set()
            link_release.wait(timeout=1.0)
            conduit_b.end_transaction("link")
        except BaseException as exc:
            failures.append(exc)
            link_started.set()

    link_thread = threading.Thread(target=_run_link, name="queued-link-root")
    link_thread.start()

    assert link_started.wait(timeout=0.05) is False
    spellbook_a.end_transaction("bind")
    assert link_started.wait(timeout=1.0) is True
    assert failures == []
    assert len(change_control.transaction_manager().list_in_flight()) == 1

    link_release.set()
    link_thread.join(timeout=5)
    assert link_thread.is_alive() is False
    assert failures == []
    assert change_control.transaction_manager().list_in_flight() == []

    conduit_a.cleanup()
    conduit_b.cleanup()
    conduit_c.cleanup()
    spellbook_a.cleanup()
    spellbook_b.cleanup()
    spellbook_c.cleanup()


def test_change_control_link_transaction_embargoes_conduit_scopes() -> None:
    """
    Purpose:
        Validate link transactions embargo both borrower and peer conduits.
    Contract:
        - Embargo scopes include borrower and peer conduit ids.
        - Embargoes and in-flight requests clear on end_transaction.
    Returns:
        None.
    Raises:
        AssertionError: If conduit scope embargoes are missing.
    """
    frame_name = "frame-cc-link"
    configuration = _make_configuration(aether_frame=frame_name, dynamic=True)
    owner_book = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    borrower_book = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    change_control = Aether()._get_change_control_manager(frame_name)
    embargo_manager = change_control.embargo_manager()
    transaction_manager = change_control.transaction_manager()

    borrower.begin_transaction("link", conduits=[borrower, owner])
    try:
        embargoed = embargo_manager.describe()["embargoed_scopes"]
        assert f"scope:conduit:{borrower.id}" in embargoed
        assert f"scope:conduit:{owner.id}" in embargoed
        assert len(transaction_manager.list_in_flight()) == 1
    finally:
        borrower.end_transaction("link")

    assert transaction_manager.list_in_flight() == []
    assert embargo_manager.describe()["embargo_count"] == 0
    owner.cleanup()
    borrower.cleanup()


def test_change_control_link_contract_registers_link_mirror() -> None:
    """
    Purpose:
        Validate link contracts register borrower/provider link mirrors.
    Contract:
        - Contracting a spell registers borrower ids in the link mirror.
    Returns:
        None.
    Raises:
        AssertionError: If link mirror registration is missing.
    """
    frame_name = "frame-cc-link-mirror"
    configuration = _make_configuration(aether_frame=frame_name, dynamic=True)
    owner_book = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    borrower_book = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    spell_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    change_control = Aether()._get_change_control_manager(frame_name)
    transaction_manager = change_control.transaction_manager()
    try:
        assert owner.link(borrower) is True
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract(
                spell_id=spell_id,
                conduit=owner,
                permissions="create",
                aetheric_frame=frame_name,
            )
        registry = change_control.devops_information_registry()
        assert registry is not None
        assert borrower.id in registry.list_borrowers_for_provider(owner.id)
    finally:
        owner.cleanup()
        borrower.cleanup()


def test_change_control_sever_link_clears_link_registry_mirror() -> None:
    """
    Purpose:
        Validate sever_link removes live borrower/provider registry mirrors after a real contract existed.
    Contract:
        - A linked contracted spell registers borrower/provider mirror state.
        - sever_link removes those mirror edges and contracted spell visibility.
    Returns:
        None.
    Raises:
        AssertionError: If link teardown leaves registry mirror residue behind.
    """
    frame_name = "frame-cc-link-mirror-sever"
    configuration = _make_configuration(aether_frame=frame_name, dynamic=True)
    owner_book = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    borrower_book = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    spell_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    change_control = Aether()._get_change_control_manager(frame_name)
    registry = change_control.devops_information_registry()
    assert registry is not None
    try:
        assert owner.link(borrower) is True
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract(
                spell_id=spell_id,
                conduit=owner,
                permissions="create",
                aetheric_frame=frame_name,
            )

        assert borrower.id in registry.list_borrowers_for_provider(owner.id)
        assert owner.id in registry.list_providers_for_borrower(borrower.id)
        assert borrower.find_contracted_spell(spell_id) is not None

        assert borrower.sever_link(owner) is True

        assert registry.list_borrowers_for_provider(owner.id) == ()
        assert registry.list_providers_for_borrower(borrower.id) == ()
        assert borrower.find_contracted_spell(spell_id) is None
    finally:
        owner.cleanup()
        borrower.cleanup()


def test_change_control_bind_transaction_registers_live_registry_session() -> None:
    """
    Purpose:
        Validate bind transactions are mirrored through the live dev-ops registry.
    Contract:
        - The active bind session is discoverable by spellbook identity and type.
        - Ending the transaction clears the registry mirror.
    Returns:
        None.
    Raises:
        AssertionError: If the live registry mirror is incorrect.
    """
    frame_name = "frame-cc-bind-registry"
    configuration = _make_configuration(aether_frame=frame_name, dynamic=True)
    spellbook = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    conduit = spellbook.conjure(automatic=False, name="root")
    change_control = Aether()._get_change_control_manager(frame_name)
    registry = change_control.devops_information_registry()
    assert registry is not None

    spellbook.begin_transaction("bind")
    try:
        sessions = registry.list_live_transactions_for_identity(
            owner_kind="spellbook",
            owner_id=spellbook._id,
        )
        assert len(sessions) == 1
        assert sessions[0].request.request_type is ChangeTransactionType.BIND
        assert registry.list_live_transactions_for_type("bind") == sessions
    finally:
        spellbook.end_transaction("bind")

    assert registry.list_live_transactions_for_identity(
        owner_kind="spellbook",
        owner_id=spellbook._id,
    ) == ()
    conduit.cleanup()
    spellbook.cleanup()


def test_change_control_post_conjure_bind_updates_staged_binding_keys() -> None:
    """
    Purpose:
        Validate post-conjure bind updates staged binding metadata on the live session.
    Contract:
        - Binding during an active bind transaction updates the staged binding keys.
    Returns:
        None.
    Raises:
        AssertionError: If staged binding metadata does not update.
    """
    frame_name = "frame-cc-bind-staged-keys"
    configuration = _make_configuration(aether_frame=frame_name, dynamic=True)
    spellbook = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    conduit = spellbook.conjure(automatic=False, name="root")
    change_control = Aether()._get_change_control_manager(frame_name)
    registry = change_control.devops_information_registry()
    assert registry is not None

    spellbook.begin_transaction("bind")
    try:
        spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )
        sessions = registry.list_live_transactions_for_identity(
            owner_kind="spellbook",
            owner_id=spellbook._id,
        )
        assert len(sessions) == 1
        assert sessions[0].staged.binding_keys == (("basicservice", "__default__"),)
    finally:
        spellbook.end_transaction("bind")

    conduit.cleanup()
    spellbook.cleanup()


def test_change_control_link_transaction_registers_live_registry_session() -> None:
    """
    Purpose:
        Validate link transactions are mirrored through the live dev-ops registry.
    Contract:
        - The active link session is discoverable by conduit identity and type.
        - Ending the transaction clears the registry mirror.
    Returns:
        None.
    Raises:
        AssertionError: If the live link-session mirror is incorrect.
    """
    frame_name = "frame-cc-link-registry"
    configuration = _make_configuration(aether_frame=frame_name, dynamic=True)
    owner_book = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    borrower_book = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    change_control = Aether()._get_change_control_manager(frame_name)
    registry = change_control.devops_information_registry()
    assert registry is not None

    borrower.begin_transaction("link", conduits=[borrower, owner])
    try:
        sessions = registry.list_live_transactions_for_identity(
            owner_kind="conduit",
            owner_id=borrower.id,
        )
        assert len(sessions) == 1
        assert sessions[0].request.request_type is ChangeTransactionType.LINK
        assert registry.list_live_transactions_for_type("link") == sessions
    finally:
        borrower.end_transaction("link")

    assert registry.list_live_transactions_for_identity(
        owner_kind="conduit",
        owner_id=borrower.id,
    ) == ()
    owner.cleanup()
    borrower.cleanup()


def test_change_control_link_transaction_session_stays_live_during_contract_add() -> None:
    """
    Purpose:
        Validate the active link session stays live while contract mutation runs.
    Contract:
        - add_spell_to_contract does not terminate or replace the active link session.
        - The active link request continues to advertise the borrower and peer conduits.
    Returns:
        None.
    Raises:
        AssertionError: If contract mutation disrupts the active link session.
    """
    frame_name = "frame-cc-link-staged-contracts"
    configuration = _make_configuration(aether_frame=frame_name, dynamic=True)
    owner_book = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    borrower_book = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    spell_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    change_control = Aether()._get_change_control_manager(frame_name)
    registry = change_control.devops_information_registry()
    assert registry is not None

    assert owner.link(borrower) is True
    borrower.begin_transaction("link", conduits=[borrower, owner])
    try:
        assert borrower.add_spell_to_contract(
            spell_id=spell_id,
            conduit=owner,
            permissions="create",
            aetheric_frame=frame_name,
        )
        sessions = registry.list_live_transactions_for_identity(
            owner_kind="conduit",
            owner_id=borrower.id,
        )
        assert len(sessions) == 1
        assert sessions[0].request.request_type is ChangeTransactionType.LINK
        assert set(sessions[0].request.conduit_ids) == {borrower.id, owner.id}
    finally:
        borrower.end_transaction("link")

    owner.cleanup()
    borrower.cleanup()


def test_change_control_bind_transaction_abort_clears_registry_session() -> None:
    """
    Purpose:
        Validate aborted bind transactions clear the live registry mirror.
    Contract:
        - A raised exception inside the bind transaction aborts the root session.
        - The registry mirror is empty after abort.
    Returns:
        None.
    Raises:
        AssertionError: If abort leaves a live mirrored session behind.
    """
    frame_name = "frame-cc-bind-abort-registry"
    configuration = _make_configuration(aether_frame=frame_name, dynamic=True)
    spellbook = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    conduit = spellbook.conjure(automatic=False, name="root")
    change_control = Aether()._get_change_control_manager(frame_name)
    registry = change_control.devops_information_registry()
    assert registry is not None

    with pytest.raises(RuntimeError, match="boom"):
        with spellbook.transaction("bind"):
            raise RuntimeError("boom")

    assert registry.list_live_transactions_for_identity(
        owner_kind="spellbook",
        owner_id=spellbook._id,
    ) == ()
    conduit.cleanup()
    spellbook.cleanup()


def test_change_control_link_transaction_abort_clears_registry_session() -> None:
    """
    Purpose:
        Validate aborted link transactions clear the live registry mirror.
    Contract:
        - A raised exception inside the link transaction aborts the root session.
        - The registry mirror is empty after abort.
    Returns:
        None.
    Raises:
        AssertionError: If abort leaves a live mirrored link session behind.
    """
    frame_name = "frame-cc-link-abort-registry"
    configuration = _make_configuration(aether_frame=frame_name, dynamic=True)
    owner_book = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    borrower_book = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    registry = Aether()._get_change_control_manager(frame_name).devops_information_registry()
    assert registry is not None

    with pytest.raises(RuntimeError, match="boom"):
        with borrower.transaction("link", conduits=[borrower, owner]):
            raise RuntimeError("boom")

    assert registry.list_live_transactions_for_identity(
        owner_kind="conduit",
        owner_id=borrower.id,
    ) == ()
    owner.cleanup()
    borrower.cleanup()


@pytest.mark.parametrize(
    "flag_name",
    (
        "disable_linking",
        "disable_all_transactions_after_conjure",
    ),
)
def test_change_control_link_transaction_respects_frame_disable_flags(
        flag_name: str,
) -> None:
    """
    Purpose:
        Validate live link transaction entry respects frame posture disable flags.
    Contract:
        - The public link transaction entry raises when the matching frame gate
          is disabled.
        - No live link session is mirrored into the registry on failure.
    Args:
        flag_name: Frame configuration flag that should block link entry.
    Returns:
        None.
    Raises:
        AssertionError: If link entry bypasses the frame posture gate.
    """
    frame_name = f"frame-cc-link-gate-{flag_name}"
    configuration = _make_configuration(aether_frame=frame_name, dynamic=True)
    owner_book = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    borrower_book = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    getattr(borrower_book._aetheric_frame_configuration, f"with_{flag_name}")(True)
    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    registry = Aether()._get_change_control_manager(frame_name).devops_information_registry()
    assert registry is not None

    with pytest.raises(RuntimeError, match="disabled"):
        borrower.begin_transaction("link", conduits=[borrower, owner])

    assert registry.list_live_transactions_for_type("link") == ()
    owner.cleanup()
    borrower.cleanup()


@pytest.mark.parametrize(
    "flag_name",
    (
        "disable_bind",
        "disable_all_transactions_after_conjure",
    ),
)
def test_change_control_conduit_bind_respects_frame_disable_flags(
        flag_name: str,
) -> None:
    """
    Purpose:
        Validate live conduit.bind respects frame posture disable flags.
    Contract:
        - Public conduit.bind raises when the matching frame gate is disabled.
        - No live bind session is mirrored into the registry on failure.
    Args:
        flag_name: Frame configuration flag that should block bind entry.
    Returns:
        None.
    Raises:
        AssertionError: If conduit.bind bypasses the frame posture gate.
    """
    frame_name = f"frame-cc-bind-gate-{flag_name}"
    configuration = _make_configuration(aether_frame=frame_name, dynamic=True)
    spellbook = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    getattr(spellbook._aetheric_frame_configuration, f"with_{flag_name}")(True)
    conduit = spellbook.conjure(automatic=False, name="root")
    registry = Aether()._get_change_control_manager(frame_name).devops_information_registry()
    assert registry is not None

    with pytest.raises(RuntimeError, match="disabled"):
        conduit.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )

    assert registry.list_live_transactions_for_type("bind") == ()
    conduit.cleanup()


def test_change_control_transfer_transaction_registers_live_registry_session() -> None:
    """
    Purpose:
        Validate transfer transactions are mirrored through the live dev-ops registry.
    Contract:
        - A conduit-side transfer transaction creates one live session visible
          by conduit identity and type.
        - The staged metadata retains the target conduit and stable spell lineage.
    Returns:
        None.
    Raises:
        AssertionError: If the live transfer-session mirror is incorrect.
    """
    frame_name = "frame-cc-transfer-registry"
    configuration = _make_configuration(aether_frame=frame_name, dynamic=True)
    owner_book = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    target_book = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    spell_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    owner = owner_book.conjure(automatic=False, name="owner")
    target = target_book.conjure(automatic=False, name="target")
    change_control = Aether()._get_change_control_manager(frame_name)
    registry = change_control.devops_information_registry()
    assert registry is not None
    spell = _get_local_spell_by_version_id(owner_book, spell_id)
    assert spell is not None

    owner.begin_transaction(
        "transfer_ownership",
        metadata={
            "target_conduit_id": target.id,
            "spell_id": spell_id,
            "spell_index_id": spell.spell_index.id,
        },
    )
    try:
        sessions = registry.list_live_transactions_for_identity(
            owner_kind="conduit",
            owner_id=owner.id,
        )
        assert len(sessions) == 1
        session = sessions[0]
        assert str(session.request.request_type) == "transfer_ownership"
        assert set(session.request.conduit_ids) == {owner.id, target.id}
        assert session.staged.binding_keys == (spell.key,)
        assert session.staged.metadata["target_conduit_id"] == target.id
        assert session.staged.metadata["spell_index_id"] == spell.spell_index.id
    finally:
        owner.end_transaction("transfer_ownership")

    assert registry.list_live_transactions_for_identity(
        owner_kind="conduit",
        owner_id=owner.id,
    ) == ()
    owner.cleanup()
    target.cleanup()


def test_change_control_transfer_spell_ownership_moves_lineage_and_clears_registry() -> None:
    """
    Purpose:
        Validate the public transfer surface moves the lineage and clears live registry state.
    Contract:
        - transfer_spell_ownership moves the SpellIndex lineage to the target spellbook.
        - The moved spell reports the target conduit as owner.
        - No live transfer session remains after success.
    Returns:
        None.
    Raises:
        AssertionError: If stewardship or registry cleanup is wrong.
    """
    frame_name = "frame-cc-transfer-runtime"
    configuration = _make_configuration(aether_frame=frame_name, dynamic=True)
    owner_book = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    target_book = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    spell_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    owner = owner_book.conjure(automatic=False, name="owner")
    target = target_book.conjure(automatic=False, name="target")
    change_control = Aether()._get_change_control_manager(frame_name)
    registry = change_control.devops_information_registry()
    assert registry is not None
    spell = _get_local_spell_by_version_id(owner_book, spell_id)
    assert spell is not None
    spell_index_id = spell.spell_index.id

    summary = owner.transfer_spell_ownership(
        spell=spell_id,
        target_conduit=target,
    )

    assert summary["spell_id"] == spell_id
    assert summary["source"] == owner.id
    assert summary["target"] == target.id
    assert owner_book.get_spell_by_index_id(spell_index_id) is None
    transferred_spell = target_book.get_spell_by_index_id(spell_index_id)
    assert transferred_spell is not None
    assert transferred_spell._owner_conduit_id == target.id
    assert registry.list_live_transactions_for_type("transfer_ownership") == ()
    owner.cleanup()
    target.cleanup()


def test_change_control_transfer_transaction_abort_clears_registry_and_preserves_lineage() -> None:
    """
    Purpose:
        Validate aborted transfer transactions clear live registry state.
    Contract:
        - A raised exception inside the transfer transaction aborts the root session.
        - The source lineage remains on the source spellbook.
        - No live transfer session remains mirrored after abort.
    Returns:
        None.
    Raises:
        AssertionError: If abort cleanup or lineage preservation is wrong.
    """
    frame_name = "frame-cc-transfer-abort"
    configuration = _make_configuration(aether_frame=frame_name, dynamic=True)
    owner_book = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    target_book = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    spell_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    owner = owner_book.conjure(automatic=False, name="owner")
    target = target_book.conjure(automatic=False, name="target")
    registry = Aether()._get_change_control_manager(frame_name).devops_information_registry()
    assert registry is not None
    spell = _get_local_spell_by_version_id(owner_book, spell_id)
    assert spell is not None
    spell_index_id = spell.spell_index.id

    with pytest.raises(RuntimeError, match="boom"):
        with owner.transaction(
                "transfer_ownership",
                metadata={
                    "target_conduit_id": target.id,
                    "spell_id": spell_id,
                    "spell_index_id": spell.spell_index.id,
                },
        ):
            raise RuntimeError("boom")

    assert registry.list_live_transactions_for_type("transfer_ownership") == ()
    assert owner_book.get_spell_by_index_id(spell_index_id) is not None
    assert target_book.get_spell_by_index_id(spell_index_id) is None
    owner.cleanup()
    target.cleanup()


def test_change_control_cluster_link_transaction_registers_live_registry_session() -> None:
    """
    Purpose:
        Validate cluster-link transactions are mirrored through the live registry.
    Contract:
        - A conduit-side cluster-link transaction creates one live session visible
          by conduit identity.
        - Ending the transaction clears the registry mirror.
    Returns:
        None.
    Raises:
        AssertionError: If the live cluster-link session mirror is incorrect.
    """
    frame_name = "frame-cc-cluster-link-registry"
    configuration = _make_configuration(aether_frame=frame_name, dynamic=True)
    owner_book = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    borrower_book = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    change_control = Aether()._get_change_control_manager(frame_name)
    registry = change_control.devops_information_registry()
    assert registry is not None

    borrower.begin_transaction(
        "cluster_link",
        conduit_ids=[owner.id],
        metadata={
            "cluster_id": "cluster-a",
            "conduit_ids": (borrower.id, owner.id),
        },
    )
    try:
        sessions = registry.list_live_transactions_for_identity(
            owner_kind="conduit",
            owner_id=borrower.id,
        )
        assert len(sessions) == 1
        assert str(sessions[0].request.request_type) == "cluster_link"
        assert set(sessions[0].request.conduit_ids) == {borrower.id, owner.id}
    finally:
        borrower.end_transaction("cluster_link")

    assert registry.list_live_transactions_for_identity(
        owner_kind="conduit",
        owner_id=borrower.id,
    ) == ()
    owner.cleanup()
    borrower.cleanup()


def test_change_control_cluster_link_transaction_abort_clears_registry_session() -> None:
    """
    Purpose:
        Validate aborted cluster-link transactions clear live registry state.
    Contract:
        - A raised exception inside the cluster-link transaction aborts the root session.
        - No live cluster-link session remains mirrored after abort.
    Returns:
        None.
    Raises:
        AssertionError: If abort leaves a live cluster-link session behind.
    """
    frame_name = "frame-cc-cluster-link-abort"
    configuration = _make_configuration(aether_frame=frame_name, dynamic=True)
    owner_book = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    borrower_book = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    registry = Aether()._get_change_control_manager(frame_name).devops_information_registry()
    assert registry is not None

    with pytest.raises(RuntimeError, match="boom"):
        with borrower.transaction(
                "cluster_link",
                conduit_ids=[owner.id],
                metadata={
                    "cluster_id": "cluster-a",
                    "conduit_ids": (borrower.id, owner.id),
                },
        ):
            raise RuntimeError("boom")

    assert registry.list_live_transactions_for_type("cluster_link") == ()
    owner.cleanup()
    borrower.cleanup()


def test_change_control_cluster_join_shares_spell_and_tracks_registry_membership() -> None:
    """
    Purpose:
        Validate cluster join shares a cluster-scoped spell and mirrors membership.
    Contract:
        - Joining the borrower into the cluster shares the owner's
          unique_per_conduit_cluster spell.
        - The dev-ops registry mirrors cluster membership by conduit id.
        - No live cluster-link session remains after the join work completes.
    Returns:
        None.
    Raises:
        AssertionError: If share or membership mirroring is wrong.
    """
    frame_name = "frame-cc-cluster-join"
    configuration = _make_configuration(aether_frame=frame_name, dynamic=True)
    owner_book = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    borrower_book = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    owner_spell_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique_per_conduit_cluster,
        permissions="create",
    )
    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    change_control = Aether()._get_change_control_manager(frame_name)
    registry = change_control.devops_information_registry()
    assert registry is not None
    cloud = owner.get_conduit_cloud()
    assert owner.link(borrower) is True

    cloud.create_cluster("cluster-a")
    cluster = cloud.get_cluster("cluster-a")
    cloud.add_conduit_to_cluster(owner, "cluster-a")
    cloud.add_conduit_to_cluster(borrower, "cluster-a")

    assert borrower.find_contracted_spell(owner_spell_id) is not None
    assert registry.get_clusters_for_conduit(owner.id) == (cluster.id,)
    assert registry.get_clusters_for_conduit(borrower.id) == (cluster.id,)
    assert registry.list_live_transactions_for_type("cluster_link") == ()
    owner.cleanup()
    borrower.cleanup()


def test_change_control_refresh_cluster_shares_propagates_new_cluster_spell() -> None:
    """
    Purpose:
        Validate refresh_cluster_shares_for_conduit propagates a late cluster spell.
    Contract:
        - A post-join unique_per_conduit_cluster bind is not visible to the peer
          until refresh_cluster_shares_for_conduit runs.
        - The refresh leaves no live cluster-link session behind.
    Returns:
        None.
    Raises:
        AssertionError: If late cluster shares do not propagate cleanly.
    """
    frame_name = "frame-cc-cluster-refresh"
    configuration = _make_configuration(aether_frame=frame_name, dynamic=True)
    owner_book = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    borrower_book = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    change_control = Aether()._get_change_control_manager(frame_name)
    registry = change_control.devops_information_registry()
    assert registry is not None
    cloud = owner.get_conduit_cloud()
    assert owner.link(borrower) is True

    cloud.create_cluster("cluster-a")
    cloud.add_conduit_to_cluster(owner, "cluster-a")
    cloud.add_conduit_to_cluster(borrower, "cluster-a")

    with owner.transaction("bind"):
        late_spell_id = owner.bind(
            spell=BasicService,
            existence=Existence.unique_per_conduit_cluster,
            permissions="create",
            binding_name="late-cluster",
        )

    assert borrower.find_contracted_spell(late_spell_id) is None

    cloud.refresh_cluster_shares_for_conduit(owner)

    assert borrower.find_contracted_spell(late_spell_id) is not None
    assert registry.list_live_transactions_for_type("cluster_link") == ()
    owner.cleanup()
    borrower.cleanup()


def test_change_control_remove_conduit_from_cluster_strips_contracts_and_membership() -> None:
    """
    Purpose:
        Validate cluster removal strips borrower contracts and membership state.
    Contract:
        - Removing the borrower from the cluster removes the borrowed
          cluster-scoped spell.
        - The dev-ops registry no longer reports cluster membership for the
          removed borrower.
        - No live cluster-link session remains after removal.
    Returns:
        None.
    Raises:
        AssertionError: If cluster teardown leaves runtime residue behind.
    """
    frame_name = "frame-cc-cluster-remove"
    configuration = _make_configuration(aether_frame=frame_name, dynamic=True)
    owner_book = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    borrower_book = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    owner_spell_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique_per_conduit_cluster,
        permissions="create",
    )
    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    change_control = Aether()._get_change_control_manager(frame_name)
    registry = change_control.devops_information_registry()
    assert registry is not None
    cloud = owner.get_conduit_cloud()
    assert owner.link(borrower) is True

    cloud.create_cluster("cluster-a")
    cloud.add_conduit_to_cluster(owner, "cluster-a")
    cloud.add_conduit_to_cluster(borrower, "cluster-a")
    cluster = cloud.get_cluster("cluster-a")
    assert borrower.find_contracted_spell(owner_spell_id) is not None

    cloud.remove_conduit_from_cluster(borrower, "cluster-a")

    assert borrower.find_contracted_spell(owner_spell_id) is None
    assert registry.get_clusters_for_conduit(borrower.id) == ()
    assert registry.get_clusters_for_conduit(owner.id) == (cluster.id,)
    assert registry.list_live_transactions_for_type("cluster_link") == ()
    owner.cleanup()
    borrower.cleanup()


@pytest.mark.parametrize(
    "flag_name",
    (
        "disable_transfer_of_ownership",
        "disable_all_transactions_after_conjure",
    ),
)
def test_change_control_transfer_transaction_respects_frame_disable_flags(
        flag_name: str,
) -> None:
    """
    Purpose:
        Validate live transfer transaction entry respects frame posture disable flags.
    Contract:
        - The public transfer transaction entry raises when the matching frame
          gate is disabled.
        - No live transfer session is mirrored into the registry on failure.
    Args:
        flag_name: Frame configuration flag that should block transfer entry.
    Returns:
        None.
    Raises:
        AssertionError: If transfer entry bypasses the frame posture gate.
    """
    frame_name = f"frame-cc-transfer-gate-{flag_name}"
    configuration = _make_configuration(aether_frame=frame_name, dynamic=True)
    owner_book = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    target_book = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    spell_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    getattr(owner_book._aetheric_frame_configuration, f"with_{flag_name}")(True)
    owner = owner_book.conjure(automatic=False, name="owner")
    target = target_book.conjure(automatic=False, name="target")
    registry = Aether()._get_change_control_manager(frame_name).devops_information_registry()
    assert registry is not None
    spell = _get_local_spell_by_version_id(owner_book, spell_id)
    assert spell is not None

    with pytest.raises(RuntimeError, match="disabled"):
        owner.begin_transaction(
            "transfer_ownership",
            metadata={
                "target_conduit_id": target.id,
                "spell_id": spell_id,
                "spell_index_id": spell.spell_index.id,
            },
        )

    assert registry.list_live_transactions_for_type("transfer_ownership") == ()
    owner.cleanup()
    target.cleanup()


@pytest.mark.parametrize(
    "flag_name",
    (
        "disable_conduit_cluster",
        "disable_all_transactions_after_conjure",
    ),
)
def test_change_control_cluster_link_transaction_respects_frame_disable_flags(
        flag_name: str,
) -> None:
    """
    Purpose:
        Validate live cluster-link transaction entry respects frame posture disable flags.
    Contract:
        - The public cluster-link transaction entry raises when the matching
          frame gate is disabled.
        - No live cluster-link session is mirrored into the registry on failure.
    Args:
        flag_name: Frame configuration flag that should block cluster-link entry.
    Returns:
        None.
    Raises:
        AssertionError: If cluster-link entry bypasses the frame posture gate.
    """
    frame_name = f"frame-cc-cluster-link-gate-{flag_name}"
    configuration = _make_configuration(aether_frame=frame_name, dynamic=True)
    owner_book = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    borrower_book = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    getattr(borrower_book._aetheric_frame_configuration, f"with_{flag_name}")(True)
    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    registry = Aether()._get_change_control_manager(frame_name).devops_information_registry()
    assert registry is not None

    with pytest.raises(RuntimeError, match="disabled"):
        borrower.begin_transaction(
            "cluster_link",
            conduit_ids=[owner.id],
            metadata={
                "cluster_id": "cluster-a",
                "conduit_ids": (borrower.id, owner.id),
            },
        )

    assert registry.list_live_transactions_for_type("cluster_link") == ()
    owner.cleanup()
    borrower.cleanup()


@pytest.mark.parametrize(
    "flag_name",
    (
        "disable_conduit_cluster",
        "disable_all_transactions_after_conjure",
    ),
)
def test_change_control_create_cluster_respects_frame_disable_flags(
        flag_name: str,
) -> None:
    """
    Purpose:
        Validate live cloud cluster creation respects frame posture disable flags.
    Contract:
        - create_cluster raises when the matching frame gate is disabled.
    Args:
        flag_name: Frame configuration flag that should block cluster creation.
    Returns:
        None.
    Raises:
        AssertionError: If create_cluster bypasses the frame posture gate.
    """
    frame_name = f"frame-cc-cloud-create-gate-{flag_name}"
    configuration = _make_configuration(aether_frame=frame_name, dynamic=True)
    spellbook = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    getattr(spellbook._aetheric_frame_configuration, f"with_{flag_name}")(True)
    conduit = spellbook.conjure(automatic=False, name="root")
    cloud = conduit.get_conduit_cloud()

    with pytest.raises(RuntimeError, match="disabled"):
        cloud.create_cluster("cluster-a")

    conduit.cleanup()
    spellbook.cleanup()


@pytest.mark.parametrize(
    "flag_name",
    (
        "disable_conduit_cluster",
        "disable_all_transactions_after_conjure",
    ),
)
def test_change_control_refresh_cluster_shares_respects_frame_disable_flags(
        flag_name: str,
) -> None:
    """
    Purpose:
        Validate live cloud share refresh respects frame posture disable flags.
    Contract:
        - refresh_cluster_shares_for_conduit raises when the matching frame
          gate is disabled, even after the cluster has already been created.
    Args:
        flag_name: Frame configuration flag that should block share refresh.
    Returns:
        None.
    Raises:
        AssertionError: If refresh_cluster_shares_for_conduit bypasses the frame gate.
    """
    frame_name = f"frame-cc-cloud-refresh-gate-{flag_name}"
    configuration = _make_configuration(aether_frame=frame_name, dynamic=True)
    spellbook = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    getattr(spellbook._aetheric_frame_configuration, f"with_{flag_name}")(True)
    conduit = spellbook.conjure(automatic=False, name="root")
    cloud = conduit.get_conduit_cloud()

    with pytest.raises(RuntimeError, match="disabled"):
        cloud.refresh_cluster_shares_for_conduit(conduit)

    conduit.cleanup()
    spellbook.cleanup()


@pytest.mark.parametrize(
    "flag_name",
    (
        "disable_conduit_cluster",
        "disable_all_transactions_after_conjure",
    ),
)
def test_change_control_add_conduit_to_cluster_respects_frame_disable_flags(
        flag_name: str,
) -> None:
    """
    Purpose:
        Validate live cloud member-add respects frame posture disable flags.
    Contract:
        - add_conduit_to_cluster raises when the matching frame gate is disabled.
    Args:
        flag_name: Frame configuration flag that should block membership add.
    Returns:
        None.
    Raises:
        AssertionError: If add_conduit_to_cluster bypasses the frame gate.
    """
    frame_name = f"frame-cc-cloud-add-gate-{flag_name}"
    configuration = _make_configuration(aether_frame=frame_name, dynamic=True)
    spellbook = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    getattr(spellbook._aetheric_frame_configuration, f"with_{flag_name}")(True)
    conduit = spellbook.conjure(automatic=False, name="root")
    cloud = conduit.get_conduit_cloud()

    with pytest.raises(RuntimeError, match="disabled"):
        cloud.add_conduit_to_cluster(conduit, "cluster-a")

    conduit.cleanup()
    spellbook.cleanup()


@pytest.mark.parametrize(
    "flag_name",
    (
        "disable_conduit_cluster",
        "disable_all_transactions_after_conjure",
    ),
)
def test_change_control_remove_conduit_from_cluster_respects_frame_disable_flags(
        flag_name: str,
) -> None:
    """
    Purpose:
        Validate live cloud member-remove respects frame posture disable flags.
    Contract:
        - remove_conduit_from_cluster raises when the matching frame gate is disabled.
    Args:
        flag_name: Frame configuration flag that should block membership removal.
    Returns:
        None.
    Raises:
        AssertionError: If remove_conduit_from_cluster bypasses the frame gate.
    """
    frame_name = f"frame-cc-cloud-remove-gate-{flag_name}"
    configuration = _make_configuration(aether_frame=frame_name, dynamic=True)
    spellbook = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    getattr(spellbook._aetheric_frame_configuration, f"with_{flag_name}")(True)
    conduit = spellbook.conjure(automatic=False, name="root")
    cloud = conduit.get_conduit_cloud()

    with pytest.raises(RuntimeError, match="disabled"):
        cloud.remove_conduit_from_cluster(conduit, "cluster-a")

    conduit.cleanup()
    spellbook.cleanup()


@pytest.mark.parametrize(
    "flag_name",
    (
        "disable_conduit_cluster",
        "disable_all_transactions_after_conjure",
    ),
)
def test_change_control_delete_cluster_respects_frame_disable_flags(
        flag_name: str,
) -> None:
    """
    Purpose:
        Validate live cloud cluster delete respects frame posture disable flags.
    Contract:
        - delete_cluster raises when the matching frame gate is disabled.
    Args:
        flag_name: Frame configuration flag that should block cluster deletion.
    Returns:
        None.
    Raises:
        AssertionError: If delete_cluster bypasses the frame gate.
    """
    frame_name = f"frame-cc-cloud-delete-gate-{flag_name}"
    configuration = _make_configuration(aether_frame=frame_name, dynamic=True)
    spellbook = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    getattr(spellbook._aetheric_frame_configuration, f"with_{flag_name}")(True)
    conduit = spellbook.conjure(automatic=False, name="root")
    cloud = conduit.get_conduit_cloud()

    with pytest.raises(RuntimeError, match="disabled"):
        cloud.delete_cluster("cluster-a")

    conduit.cleanup()
    spellbook.cleanup()


@pytest.mark.parametrize(
    "metadata",
    (
        {"spell_id": "spell-only"},
        {"target_conduit_id": "target-only"},
    ),
)
def test_change_control_transfer_transaction_requires_complete_metadata(
        metadata: dict[str, object],
) -> None:
    """
    Purpose:
        Validate live transfer entry rejects incomplete planning metadata.
    Contract:
        - Missing target metadata or missing spell metadata causes transfer
          planning to raise before a live session is mirrored into the registry.
    Args:
        metadata: Incomplete transfer metadata payload under test.
    Returns:
        None.
    Raises:
        AssertionError: If incomplete transfer metadata is accepted.
    """
    frame_name = "frame-cc-transfer-metadata"
    configuration = _make_configuration(aether_frame=frame_name, dynamic=True)
    owner_book = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    target_book = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    owner = owner_book.conjure(automatic=False, name="owner")
    target = target_book.conjure(automatic=False, name="target")
    registry = Aether()._get_change_control_manager(frame_name).devops_information_registry()
    assert registry is not None
    normalized_metadata = dict(metadata)
    if normalized_metadata.get("target_conduit_id") == "target-only":
        normalized_metadata["target_conduit_id"] = target.id

    with pytest.raises(RuntimeError):
        owner.begin_transaction(
            "transfer_ownership",
            metadata=normalized_metadata,
        )

    assert registry.list_live_transactions_for_type("transfer_ownership") == ()
    owner.cleanup()
    target.cleanup()
