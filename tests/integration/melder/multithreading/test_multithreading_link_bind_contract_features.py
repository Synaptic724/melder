from __future__ import annotations

from threading import Event, Lock, Thread
from typing import Any

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
from melder.utilities.custom_exceptions.phase_execution_error import PhaseExecutionError
from melder.utilities.custom_exceptions.spellbook_validation_error import SpellbookValidationError
from tests.mocks.spellbook.contract_classes import (
    ContractConsumerPrimary,
    ContractConsumerSecondary,
    ContractServicePrimary,
    ContractServiceSecondary,
)
from tests.mocks.spellbook.protocols import IService


from tests._frame_posture_test_support import (
    apply_automatic_defaults_for_spellbook_configuration,
    apply_dynamic_defaults_for_spellbook_configuration,
    build_aetheric_frame_configuration_for_spellbook_configuration,
    set_frame_ai_native_for_spellbook_configuration,
    set_frame_rift_enabled_for_spellbook_configuration,
    set_frame_system_state_for_spellbook_configuration,
    set_shared_framewide_spellbook_configuration_for_spellbook_configuration,
)
class _LeaderDrivenWorker:
    """
    Purpose:
        Execute meld calls only when the orchestrator (main thread) releases a named step.
    Contract:
        - Worker blocks on per-step release events.
        - Each step performs one meld attempt.
        - Result/exception is captured per step for deterministic assertions.
    """

    def __init__(
        self,
        *,
        name: str,
        conduit: Conduit,
        spell_id: str,
        steps: list[str],
    ) -> None:
        """
        Purpose:
            Initialize worker state and backing thread.
        Contract:
            - Creates release/done events for each step.
            - Thread target is `_run`.
        Args:
            name: Worker thread name.
            conduit: Conduit to call `meld` on.
            spell_id: Spell id resolved by `meld`.
            steps: Ordered list of orchestrated step names.
        Returns:
            None.
        """
        self._name = name
        self._conduit = conduit
        self._spell_id = spell_id
        self._steps = list(steps)
        self._release_events: dict[str, Event] = {step: Event() for step in self._steps}
        self._done_events: dict[str, Event] = {step: Event() for step in self._steps}
        self._results: dict[str, Any] = {}
        self._errors: dict[str, BaseException] = {}
        self._lock = Lock()
        self._thread = Thread(target=self._run, name=name, daemon=True)

    def has_step(self, step: str) -> bool:
        """
        Purpose:
            Determine whether this worker participates in a step.
        Contract:
            - Returns True only when step is present in worker script.
        Args:
            step: Step name.
        Returns:
            bool: Participation indicator.
        """
        return step in self._release_events

    def start(self) -> None:
        """
        Purpose:
            Start the worker thread.
        Contract:
            - Must be called once before step releases.
        Returns:
            None.
        """
        self._thread.start()

    def release(self, step: str) -> None:
        """
        Purpose:
            Release one orchestrated step.
        Contract:
            - No-op when worker does not participate in step.
        Args:
            step: Step name.
        Returns:
            None.
        """
        event = self._release_events.get(step)
        if event is not None:
            event.set()

    def wait_done(self, step: str, *, timeout_seconds: float = 10.0) -> None:
        """
        Purpose:
            Wait for worker completion of a step.
        Contract:
            - Asserts completion within timeout for participating steps.
        Args:
            step: Step name.
            timeout_seconds: Maximum wait time.
        Returns:
            None.
        Raises:
            AssertionError: If step does not complete in time.
        """
        done_event = self._done_events.get(step)
        if done_event is None:
            return
        assert done_event.wait(timeout=timeout_seconds), (
            f"Worker '{self._name}' timed out waiting for step '{step}'."
        )

    def join(self, *, timeout_seconds: float = 10.0) -> None:
        """
        Purpose:
            Join worker thread at test end.
        Contract:
            - Asserts thread terminated.
        Args:
            timeout_seconds: Maximum join timeout.
        Returns:
            None.
        Raises:
            AssertionError: If worker remains alive.
        """
        self._thread.join(timeout=timeout_seconds)
        assert not self._thread.is_alive(), f"Worker '{self._name}' did not terminate."

    def result(self, step: str) -> Any | None:
        """
        Purpose:
            Return recorded step result.
        Contract:
            - Returns None when step produced no result.
        Args:
            step: Step name.
        Returns:
            Any | None: Captured step result.
        """
        with self._lock:
            return self._results.get(step)

    def error(self, step: str) -> BaseException | None:
        """
        Purpose:
            Return recorded step error.
        Contract:
            - Returns None when step completed without exception.
        Args:
            step: Step name.
        Returns:
            BaseException | None: Captured exception.
        """
        with self._lock:
            return self._errors.get(step)

    def _run(self) -> None:
        """
        Purpose:
            Execute meld attempts in scripted step order.
        Contract:
            - Waits for release signal per step.
            - Captures either result or error per step.
            - Always marks step done.
        Returns:
            None.
        """
        for step in self._steps:
            released = self._release_events[step].wait(timeout=20.0)
            if not released:
                with self._lock:
                    self._errors[step] = TimeoutError(
                        f"Step '{step}' was not released."
                    )
                self._done_events[step].set()
                return
            try:
                result = self._conduit.meld(spell=self._spell_id)
                with self._lock:
                    self._results[step] = result
            except Exception as exc:
                with self._lock:
                    self._errors[step] = exc
            finally:
                self._done_events[step].set()


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_multithreading_link_features() -> None:
    """
    Purpose:
        Ensure each test has isolated Aether singleton state.
    Contract:
        - Resets Aether before and after test.
        - Rebinds Spellbook/Conduit class-level Aether handles.
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


def _make_dynamic_configuration(*, workers: int = 4) -> SpellbookConfiguration:
    """
    Purpose:
        Create dynamic configuration for integration tests.
    Contract:
        - Enables dynamic defaults.
        - Sets scheduler worker count.
    Args:
        workers: Workers per spellbook for phase scheduler.
    Returns:
        SpellbookConfiguration: Configured dynamic object.
    """
    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", workers)
    return configuration


def _release_and_wait(workers: list[_LeaderDrivenWorker], step: str) -> None:
    """
    Purpose:
        Release one step for all workers and wait for step completion.
    Contract:
        - Releases only workers that participate in the step.
        - Waits for completion for participating workers.
    Args:
        workers: Worker lanes.
        step: Step name.
    Returns:
        None.
    """
    for worker in workers:
        if worker.has_step(step):
            worker.release(step)
    for worker in workers:
        if worker.has_step(step):
            worker.wait_done(step)


def _assert_success(worker: _LeaderDrivenWorker, step: str) -> Any:
    """
    Purpose:
        Assert worker step succeeded and return result.
    Contract:
        - Step error must be None.
        - Step result must not be None.
    Args:
        worker: Worker lane.
        step: Step name.
    Returns:
        Any: Step result object.
    Raises:
        AssertionError: If step failed or produced no result.
    """
    error = worker.error(step)
    assert error is None, f"Unexpected worker error for step '{step}': {error!r}"
    result = worker.result(step)
    assert result is not None, f"Missing worker result for step '{step}'."
    return result


def _inbound_spell_ids(
    spells_by_conduit: dict[str, list[tuple[str, Any]]] | None,
) -> list[str]:
    """
    Purpose:
        Extract inbound spell ids from contract snapshot.
    Contract:
        - Returns empty list when no snapshot/entries exist.
        - Returns only inbound spell ids.
    Args:
        spells_by_conduit: Snapshot from `get_spells_in_contract_by_conduit`.
    Returns:
        list[str]: Inbound spell ids.
    """
    if not spells_by_conduit:
        return []
    return [spell_id for spell_id, _spell in spells_by_conduit.get("inbound", [])]


def _assert_allowed_live_mutation_error(error: BaseException) -> None:
    """
    Purpose:
        Validate meld errors observed during live link/contract mutation windows.
    Contract:
        - Rejects PhaseExecutionError as internal phase failure.
        - Accepts runtime/meld/validation errors expected during churn.
    Args:
        error: Captured exception from a worker step.
    Returns:
        None.
    Raises:
        AssertionError: If error type is unexpected.
    """
    assert not isinstance(error, PhaseExecutionError), (
        "Unexpected internal phase failure during live mutation: "
        f"{error!r}"
    )
    assert isinstance(
        error,
        (RuntimeError, MeldExecutionError, SpellbookValidationError),
    ), f"Unexpected live mutation error type: {type(error).__name__}: {error!r}"


def _assert_step_state(
    *,
    worker: _LeaderDrivenWorker,
    step: str,
    expectation: str,
) -> Any | None:
    """
    Purpose:
        Assert one worker outcome for an orchestrated step.
    Contract:
        - `expectation='success'`: requires result and no error.
        - `expectation='error'`: requires error and validates allowed type.
        - `expectation='either'`: accepts either result or allowed error.
    Args:
        worker: Worker lane.
        step: Step name.
        expectation: One of {'success', 'error', 'either'}.
    Returns:
        Any | None: Step result when available.
    Raises:
        AssertionError: If outcome does not match expectation.
    """
    error = worker.error(step)
    result = worker.result(step)
    if expectation == "success":
        assert error is None, f"Expected success at step '{step}', got error: {error!r}"
        assert result is not None, f"Expected result at step '{step}', got None."
        return result
    if expectation == "error":
        assert error is not None, f"Expected error at step '{step}', got success."
        _assert_allowed_live_mutation_error(error)
        return None
    assert expectation == "either", f"Unsupported expectation '{expectation}'."
    if error is not None:
        _assert_allowed_live_mutation_error(error)
        return None
    return result


def _is_resolved_contract_value(value: Any) -> bool:
    """
    Purpose:
        Determine whether a consumer result carries a resolved service instance.
    Contract:
        - Returns True when value has `.service` of ContractServicePrimary.
    Args:
        value: Consumer result object.
    Returns:
        bool: Resolution status.
    """
    return hasattr(value, "service") and isinstance(value.service, ContractServicePrimary)


def _is_placeholder_contract_value(value: Any) -> bool:
    """
    Purpose:
        Determine whether a consumer result still carries SpellContract placeholder payload.
    Contract:
        - Returns True when value has `.service` of type SpellContract.
    Args:
        value: Consumer result object.
    Returns:
        bool: Placeholder status.
    """
    return hasattr(value, "service") and isinstance(value.service, SpellContract)


def test_multithreading_bind_transaction_then_contract_uncontract_recontract() -> None:
    """
    Purpose:
        Validate bind transactions after conjure with contract add/remove/re-add lifecycle.
    Contract:
        - Existing primary consumer remains stable across all steps.
        - New secondary provider/consumer can be bound post-conjure in bind transactions.
        - Secondary contract can be removed and re-added in link transactions.
        - Secondary consumer resolves after re-contract on post step.
    Returns:
        None.
    Raises:
        AssertionError: If bind/contract lifecycle is inconsistent.
    """
    owner_book = Spellbook(configuration=_make_dynamic_configuration(workers=4))
    borrower_book = Spellbook(configuration=_make_dynamic_configuration(workers=4))

    primary_service_id = owner_book.bind(
        spell=ContractServicePrimary,
        existence=Existence.unique,
        permissions="create",
        spellframe=IService,
        binding_name="primary",
    )
    primary_consumer_id = borrower_book.bind(
        spell=ContractConsumerPrimary,
        existence=Existence.many,
        permissions="create",
    )

    owner = owner_book.conjure(automatic=False, name="owner-bind-contract")
    borrower = borrower_book.conjure(automatic=False, name="borrower-bind-contract")

    try:
        assert owner.link(borrower) is True
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract_with_dependencies(
                spell_id=primary_service_id,
                conduit=owner,
                permissions="create",
            )

        owner_worker = _LeaderDrivenWorker(
            name="owner-worker-bind",
            conduit=owner,
            spell_id=primary_service_id,
            steps=["pre", "during", "post"],
        )
        primary_worker = _LeaderDrivenWorker(
            name="primary-worker-bind",
            conduit=borrower,
            spell_id=primary_consumer_id,
            steps=["pre", "during", "post"],
        )
        workers = [owner_worker, primary_worker]
        for worker in workers:
            worker.start()

        _release_and_wait(workers, "pre")
        assert isinstance(_assert_success(owner_worker, "pre"), ContractServicePrimary)
        primary_pre = _assert_success(primary_worker, "pre")
        assert isinstance(primary_pre, ContractConsumerPrimary)
        assert isinstance(primary_pre.service, ContractServicePrimary)

        with owner.binding_transaction():
            secondary_service_id = owner.bind(
                spell=ContractServiceSecondary,
                existence=Existence.unique,
                permissions="create",
                spellframe=IService,
                binding_name="secondary",
            )
        with borrower.binding_transaction():
            secondary_consumer_id = borrower.bind(
                spell=ContractConsumerSecondary,
                existence=Existence.many,
                permissions="create",
            )
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract_with_dependencies(
                spell_id=secondary_service_id,
                conduit=owner,
                permissions="create",
            )
        with borrower.transaction("link", conduits=[borrower, owner]):
            report = borrower.remove_root_from_contracts(
                root_spell_id=secondary_service_id,
                conduit=owner,
            )
        assert report["failed"] == {}
        inbound_ids_after_remove = _inbound_spell_ids(
            borrower.get_spells_in_contract_by_conduit(owner.id),
        )
        assert secondary_service_id not in inbound_ids_after_remove
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract_with_dependencies(
                spell_id=secondary_service_id,
                conduit=owner,
                permissions="create",
            )

        _release_and_wait(workers, "during")
        assert isinstance(_assert_success(owner_worker, "during"), ContractServicePrimary)
        primary_during = _assert_success(primary_worker, "during")
        assert isinstance(primary_during, ContractConsumerPrimary)
        assert isinstance(primary_during.service, ContractServicePrimary)

        secondary_worker = _LeaderDrivenWorker(
            name="secondary-worker-bind",
            conduit=borrower,
            spell_id=secondary_consumer_id,
            steps=["post"],
        )
        secondary_worker.start()
        workers.append(secondary_worker)

        _release_and_wait(workers, "post")
        assert isinstance(_assert_success(owner_worker, "post"), ContractServicePrimary)
        primary_post = _assert_success(primary_worker, "post")
        assert isinstance(primary_post, ContractConsumerPrimary)
        assert isinstance(primary_post.service, ContractServicePrimary)
        secondary_post = _assert_success(secondary_worker, "post")
        assert isinstance(secondary_post, ContractConsumerSecondary)
        assert isinstance(secondary_post.service, ContractServiceSecondary)

        for worker in workers:
            worker.join()
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_multithreading_sever_link_blocks_contract_mutation_until_relink() -> None:
    """
    Purpose:
        Validate severed links block contract mutation transactions until relink.
    Contract:
        - Initial contract mutation succeeds while linked.
        - Contract add attempt after sever_link raises RuntimeError.
        - Relink restores ability to add contract and borrower meld stays valid.
    Returns:
        None.
    Raises:
        AssertionError: If link lifecycle guardrails are violated.
    """
    owner_book = Spellbook(configuration=_make_dynamic_configuration(workers=4))
    borrower_book = Spellbook(configuration=_make_dynamic_configuration(workers=4))

    service_id = owner_book.bind(
        spell=ContractServicePrimary,
        existence=Existence.unique,
        permissions="create",
        spellframe=IService,
        binding_name="primary",
    )
    consumer_id = borrower_book.bind(
        spell=ContractConsumerPrimary,
        existence=Existence.many,
        permissions="create",
    )

    owner = owner_book.conjure(automatic=False, name="owner-link-guard")
    borrower = borrower_book.conjure(automatic=False, name="borrower-link-guard")

    try:
        assert owner.link(borrower) is True
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract_with_dependencies(
                spell_id=service_id,
                conduit=owner,
                permissions="create",
            )

        borrower_worker = _LeaderDrivenWorker(
            name="borrower-worker-link-guard",
            conduit=borrower,
            spell_id=consumer_id,
            steps=["pre", "post"],
        )
        borrower_worker.start()

        _release_and_wait([borrower_worker], "pre")
        pre_value = _assert_success(borrower_worker, "pre")
        assert isinstance(pre_value, ContractConsumerPrimary)
        assert isinstance(pre_value.service, ContractServicePrimary)

        assert owner.sever_link(borrower) is True
        with pytest.raises(RuntimeError, match="No contract found"):
            with borrower.transaction("link", conduits=[borrower, owner]):
                borrower.add_spell_to_contract_with_dependencies(
                    spell_id=service_id,
                    conduit=owner,
                    permissions="create",
                )

        assert owner.link(borrower) is True
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract_with_dependencies(
                spell_id=service_id,
                conduit=owner,
                permissions="create",
            )

        _release_and_wait([borrower_worker], "post")
        post_value = _assert_success(borrower_worker, "post")
        assert isinstance(post_value, ContractConsumerPrimary)
        assert isinstance(post_value.service, ContractServicePrimary)
        borrower_worker.join()
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_multithreading_uncontract_isolated_to_one_borrower_then_restore() -> None:
    """
    Purpose:
        Validate uncontracting one borrower does not remove another borrower's contract.
    Contract:
        - Both borrowers resolve contracted service at pre step.
        - Removing root contract for borrower A leaves borrower B inbound contract intact.
        - Removing the only root may sever borrower-A contract object.
        - Re-link + re-contract borrower A restores both borrowers for post step.
    Returns:
        None.
    Raises:
        AssertionError: If uncontract scope leaks across borrowers.
    """
    class _BorrowerAConsumer:
        """
        Purpose:
            Provide a borrower-A specific consumer class for id isolation.
        Contract:
            - Requests IService(primary) via SpellContract.
            - Stores resolved service on instance.
        """

        def __init__(
            self,
            service: IService = SpellContract(spellframe=IService, binding_name="primary"),
        ) -> None:
            """
            Purpose:
                Capture contracted service dependency.
            Contract:
                - Stores resolved service on `self.service`.
            Args:
                service: Contract-resolved IService instance.
            Returns:
                None.
            """
            self.service = service

    class _BorrowerBConsumer:
        """
        Purpose:
            Provide a borrower-B specific consumer class for id isolation.
        Contract:
            - Requests IService(primary) via SpellContract.
            - Stores resolved service on instance.
        """

        def __init__(
            self,
            service: IService = SpellContract(spellframe=IService, binding_name="primary"),
        ) -> None:
            """
            Purpose:
                Capture contracted service dependency.
            Contract:
                - Stores resolved service on `self.service`.
            Args:
                service: Contract-resolved IService instance.
            Returns:
                None.
            """
            self.service = service

    owner_book = Spellbook(configuration=_make_dynamic_configuration(workers=4))
    borrower_a_book = Spellbook(configuration=_make_dynamic_configuration(workers=4))
    borrower_b_book = Spellbook(configuration=_make_dynamic_configuration(workers=4))

    service_id = owner_book.bind(
        spell=ContractServicePrimary,
        existence=Existence.unique,
        permissions="create",
        spellframe=IService,
        binding_name="primary",
    )
    consumer_a_id = borrower_a_book.bind(
        spell=_BorrowerAConsumer,
        existence=Existence.many,
        permissions="create",
    )
    consumer_b_id = borrower_b_book.bind(
        spell=_BorrowerBConsumer,
        existence=Existence.many,
        permissions="create",
    )

    owner = owner_book.conjure(automatic=False, name="owner-uncontract-isolation")
    borrower_a = borrower_a_book.conjure(automatic=False, name="borrower-a-uncontract")
    borrower_b = borrower_b_book.conjure(automatic=False, name="borrower-b-uncontract")

    try:
        assert owner.link(borrower_a) is True
        assert owner.link(borrower_b) is True
        with borrower_a.transaction("link", conduits=[borrower_a, owner]):
            assert borrower_a.add_spell_to_contract_with_dependencies(
                spell_id=service_id,
                conduit=owner,
                permissions="create",
            )
        with borrower_b.transaction("link", conduits=[borrower_b, owner]):
            assert borrower_b.add_spell_to_contract_with_dependencies(
                spell_id=service_id,
                conduit=owner,
                permissions="create",
            )

        worker_a = _LeaderDrivenWorker(
            name="worker-a-uncontract",
            conduit=borrower_a,
            spell_id=consumer_a_id,
            steps=["pre", "during", "post"],
        )
        worker_b = _LeaderDrivenWorker(
            name="worker-b-uncontract",
            conduit=borrower_b,
            spell_id=consumer_b_id,
            steps=["pre", "during", "post"],
        )
        workers = [worker_a, worker_b]
        for worker in workers:
            worker.start()

        _release_and_wait(workers, "pre")
        a_pre = _assert_success(worker_a, "pre")
        b_pre = _assert_success(worker_b, "pre")
        assert isinstance(a_pre, _BorrowerAConsumer)
        assert isinstance(b_pre, _BorrowerBConsumer)
        assert isinstance(a_pre.service, ContractServicePrimary)
        assert isinstance(b_pre.service, ContractServicePrimary)

        with borrower_a.transaction("link", conduits=[borrower_a, owner]):
            report = borrower_a.remove_root_from_contracts(
                root_spell_id=service_id,
                conduit=owner,
            )
        assert report["failed"] == {}

        inbound_a = _inbound_spell_ids(borrower_a.get_spells_in_contract_by_conduit(owner.id))
        inbound_b = _inbound_spell_ids(borrower_b.get_spells_in_contract_by_conduit(owner.id))
        assert service_id not in inbound_a
        assert service_id in inbound_b

        with pytest.raises(RuntimeError, match="No contract found"):
            with borrower_a.transaction("link", conduits=[borrower_a, owner]):
                borrower_a.add_spell_to_contract_with_dependencies(
                    spell_id=service_id,
                    conduit=owner,
                    permissions="create",
                )
        assert owner.link(borrower_a) is True
        with borrower_a.transaction("link", conduits=[borrower_a, owner]):
            assert borrower_a.add_spell_to_contract_with_dependencies(
                spell_id=service_id,
                conduit=owner,
                permissions="create",
            )

        _release_and_wait(workers, "during")
        a_during = _assert_success(worker_a, "during")
        b_during = _assert_success(worker_b, "during")
        assert isinstance(a_during, _BorrowerAConsumer)
        assert isinstance(b_during, _BorrowerBConsumer)
        assert isinstance(a_during.service, ContractServicePrimary)
        assert isinstance(b_during.service, ContractServicePrimary)

        _release_and_wait(workers, "post")
        a_post = _assert_success(worker_a, "post")
        b_post = _assert_success(worker_b, "post")
        assert isinstance(a_post, _BorrowerAConsumer)
        assert isinstance(b_post, _BorrowerBConsumer)
        assert isinstance(a_post.service, ContractServicePrimary)
        assert isinstance(b_post.service, ContractServicePrimary)

        for worker in workers:
            worker.join()
    finally:
        borrower_b.cleanup()
        borrower_a.cleanup()
        owner.cleanup()


def test_multithreading_live_link_unlink_and_contract_churn_cycles() -> None:
    """
    Purpose:
        Stress live churn with orchestrator-controlled mutation and concurrent meld workers.
    Contract:
        - Main thread drives mutation phases and worker release order.
        - Owner lane remains healthy across all phases.
        - Borrower lanes are exercised through unlink/relink and uncontract/recontract.
        - During active mutation windows, borrower lanes may succeed or raise allowed errors.
        - After each mutation settles, expectations become deterministic.
    Returns:
        None.
    Raises:
        AssertionError: If outcomes violate expected settled-state behavior.
    """
    class _CycleConsumerA:
        """
        Purpose:
            Consumer class for borrower-A cycle lane.
        Contract:
            - Resolves IService(primary) via SpellContract each meld.
        """

        def __init__(
            self,
            service: IService = SpellContract(spellframe=IService, binding_name="primary"),
        ) -> None:
            """
            Purpose:
                Store resolved service dependency.
            Contract:
                - Persists resolved service on `self.service`.
            Args:
                service: Resolved IService instance.
            Returns:
                None.
            """
            self.service = service

    class _CycleConsumerB:
        """
        Purpose:
            Consumer class for borrower-B cycle lane.
        Contract:
            - Resolves IService(primary) via SpellContract each meld.
        """

        def __init__(
            self,
            service: IService = SpellContract(spellframe=IService, binding_name="primary"),
        ) -> None:
            """
            Purpose:
                Store resolved service dependency.
            Contract:
                - Persists resolved service on `self.service`.
            Args:
                service: Resolved IService instance.
            Returns:
                None.
            """
            self.service = service

    owner_book = Spellbook(configuration=_make_dynamic_configuration(workers=4))
    borrower_a_book = Spellbook(configuration=_make_dynamic_configuration(workers=4))
    borrower_b_book = Spellbook(configuration=_make_dynamic_configuration(workers=4))

    service_id = owner_book.bind(
        spell=ContractServicePrimary,
        existence=Existence.many,
        permissions="create",
        spellframe=IService,
        binding_name="primary",
    )
    consumer_a_id = borrower_a_book.bind(
        spell=_CycleConsumerA,
        existence=Existence.many,
        permissions="create",
    )
    consumer_b_id = borrower_b_book.bind(
        spell=_CycleConsumerB,
        existence=Existence.many,
        permissions="create",
    )

    owner = owner_book.conjure(automatic=False, name="owner-live-cycle")
    borrower_a = borrower_a_book.conjure(automatic=False, name="borrower-a-live-cycle")
    borrower_b = borrower_b_book.conjure(automatic=False, name="borrower-b-live-cycle")

    steps = [
        "stable_0",
        "during_unlink_a",
        "after_unlink_a",
        "during_relink_a",
        "after_relink_a",
        "during_uncontract_b",
        "after_uncontract_b",
        "during_recontract_b",
        "after_recontract_b",
        "stable_1",
    ]

    mutation_lock = Lock()
    mutation_signal = Event()
    mutation_done = Event()
    mutation_stop = Event()
    mutation_errors: list[BaseException] = []
    mutation_command: dict[str, str | None] = {"action": None}

    def mutation_worker() -> None:
        """
        Purpose:
            Apply one mutation action at a time when released by the orchestrator.
        Contract:
            - Waits for mutation command signal.
            - Executes exactly one action and marks completion.
            - Captures exceptions for assertion.
        Returns:
            None.
        """
        while True:
            if not mutation_signal.wait(timeout=20.0):
                if mutation_stop.is_set():
                    return
                continue
            mutation_signal.clear()
            if mutation_stop.is_set():
                return
            action = mutation_command["action"]
            try:
                if action == "unlink_a":
                    owner.sever_link(borrower_a)
                elif action == "relink_a":
                    owner.link(borrower_a)
                    with borrower_a.transaction("link", conduits=[borrower_a, owner]):
                        borrower_a.add_spell_to_contract_with_dependencies(
                            spell_id=service_id,
                            conduit=owner,
                            permissions="create",
                        )
                    borrower_a.validate_contracts_and_define()
                elif action == "uncontract_b":
                    with borrower_b.transaction("link", conduits=[borrower_b, owner]):
                        borrower_b.remove_root_from_contracts(
                            root_spell_id=service_id,
                            conduit=owner,
                        )
                elif action == "recontract_b":
                    owner.link(borrower_b)
                    with borrower_b.transaction("link", conduits=[borrower_b, owner]):
                        borrower_b.add_spell_to_contract_with_dependencies(
                            spell_id=service_id,
                            conduit=owner,
                            permissions="create",
                        )
                    borrower_b.validate_contracts_and_define()
            except Exception as exc:
                with mutation_lock:
                    mutation_errors.append(exc)
            finally:
                mutation_done.set()

    try:
        assert owner.link(borrower_a) is True
        assert owner.link(borrower_b) is True
        with borrower_a.transaction("link", conduits=[borrower_a, owner]):
            assert borrower_a.add_spell_to_contract_with_dependencies(
                spell_id=service_id,
                conduit=owner,
                permissions="create",
            )
        with borrower_b.transaction("link", conduits=[borrower_b, owner]):
            assert borrower_b.add_spell_to_contract_with_dependencies(
                spell_id=service_id,
                conduit=owner,
                permissions="create",
            )
        borrower_a.validate_contracts_and_define()
        borrower_b.validate_contracts_and_define()

        owner_worker = _LeaderDrivenWorker(
            name="owner-cycle-worker",
            conduit=owner,
            spell_id=service_id,
            steps=steps,
        )
        borrower_a_worker = _LeaderDrivenWorker(
            name="borrower-a-cycle-worker",
            conduit=borrower_a,
            spell_id=consumer_a_id,
            steps=steps,
        )
        borrower_b_worker = _LeaderDrivenWorker(
            name="borrower-b-cycle-worker",
            conduit=borrower_b,
            spell_id=consumer_b_id,
            steps=steps,
        )
        workers = [owner_worker, borrower_a_worker, borrower_b_worker]
        for worker in workers:
            worker.start()
        mutator = Thread(target=mutation_worker, name="mutation-cycle-worker", daemon=True)
        mutator.start()

        schedule = [
            ("stable_0", None, "success", "success"),
            ("during_unlink_a", "unlink_a", "either", "success"),
            ("after_unlink_a", None, "either", "success"),
            ("during_relink_a", "relink_a", "either", "success"),
            ("after_relink_a", None, "success", "success"),
            ("during_uncontract_b", "uncontract_b", "success", "either"),
            ("after_uncontract_b", None, "success", "either"),
            ("during_recontract_b", "recontract_b", "success", "either"),
            ("after_recontract_b", None, "success", "success"),
            ("stable_1", None, "success", "success"),
        ]

        for step_name, action, expected_a, expected_b in schedule:
            if action is not None:
                mutation_command["action"] = action
                mutation_done.clear()
                mutation_signal.set()

            _release_and_wait(workers, step_name)

            owner_result = _assert_step_state(
                worker=owner_worker,
                step=step_name,
                expectation="success",
            )
            assert isinstance(owner_result, ContractServicePrimary)

            a_value = _assert_step_state(
                worker=borrower_a_worker,
                step=step_name,
                expectation=expected_a,
            )
            b_value = _assert_step_state(
                worker=borrower_b_worker,
                step=step_name,
                expectation=expected_b,
            )

            if expected_a == "success":
                assert a_value is not None and _is_resolved_contract_value(a_value)

            if expected_b == "success":
                assert b_value is not None and _is_resolved_contract_value(b_value)

            print(
                f"[multithreading-cycle] step={step_name} "
                f"action={action} "
                f"owner={'ok' if owner_worker.error(step_name) is None else 'err'} "
                f"borrower_a={'ok' if borrower_a_worker.error(step_name) is None else 'err'} "
                f"borrower_b={'ok' if borrower_b_worker.error(step_name) is None else 'err'}"
            )

            if action is not None:
                assert mutation_done.wait(timeout=10.0), (
                    f"Mutation action '{action}' did not complete in time."
                )

        for worker in workers:
            worker.join()

        mutation_stop.set()
        mutation_signal.set()
        mutator.join(timeout=10.0)
        assert not mutator.is_alive(), "Mutation worker did not terminate."
        assert mutation_errors == []
    finally:
        mutation_stop.set()
        mutation_signal.set()
        borrower_b.cleanup()
        borrower_a.cleanup()
        owner.cleanup()
