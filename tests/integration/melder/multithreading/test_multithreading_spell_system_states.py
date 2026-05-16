from __future__ import annotations

from threading import Event, Lock, Thread
from typing import Any

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
from melder.utilities.custom_exceptions.phase_execution_error import PhaseExecutionError
from melder.utilities.custom_exceptions.spellbook_validation_error import SpellbookValidationError
from tests.mocks.spellbook.contract_classes import ContractServiceRemote
from tests.mocks.spellbook.protocols import IService


class ThreadConsumerOne:
    """
    Purpose:
        Borrower consumer used by multithreading integration tests.
    Contract:
        - Requests IService via SpellContract using binding_name='primary'.
        - Stores resolved service on the instance.
    """

    def __init__(
        self,
        service: IService = SpellContract(spellframe=IService, binding_name="primary"),
    ) -> None:
        """
        Purpose:
            Capture contracted service dependency.
        Contract:
            - Stores resolved dependency on `self.service`.
        Args:
            service: Resolved IService instance from contracted provider.
        Returns:
            None.
        """
        self.service = service


class ThreadConsumerTwo:
    """
    Purpose:
        Second borrower consumer used by multithreading integration tests.
    Contract:
        - Same dependency contract as ThreadConsumerOne.
    """

    def __init__(
        self,
        service: IService = SpellContract(spellframe=IService, binding_name="primary"),
    ) -> None:
        """
        Purpose:
            Capture contracted service dependency.
        Contract:
            - Stores resolved dependency on `self.service`.
        Args:
            service: Resolved IService instance from contracted provider.
        Returns:
            None.
        """
        self.service = service


class ThreadConsumerThree:
    """
    Purpose:
        Third borrower consumer used by multithreading integration tests.
    Contract:
        - Same dependency contract as ThreadConsumerOne.
    """

    def __init__(
        self,
        service: IService = SpellContract(spellframe=IService, binding_name="primary"),
    ) -> None:
        """
        Purpose:
            Capture contracted service dependency.
        Contract:
            - Stores resolved dependency on `self.service`.
        Args:
            service: Resolved IService instance from contracted provider.
        Returns:
            None.
        """
        self.service = service


class ThreadConsumerFour:
    """
    Purpose:
        Fourth borrower consumer used by multithreading integration tests.
    Contract:
        - Same dependency contract as ThreadConsumerOne.
    """

    def __init__(
        self,
        service: IService = SpellContract(spellframe=IService, binding_name="primary"),
    ) -> None:
        """
        Purpose:
            Capture contracted service dependency.
        Contract:
            - Stores resolved dependency on `self.service`.
        Args:
            service: Resolved IService instance from contracted provider.
        Returns:
            None.
        """
        self.service = service


class _OrchestratedMeldWorker:
    """
    Purpose:
        Execute meld attempts only when the orchestrator releases named steps.
    Contract:
        - Worker thread blocks on per-step release events.
        - Each released step performs one `conduit.meld(spell=spell_id)` call.
        - Result or raised exception is captured per step.
        - The orchestrator can wait on per-step completion events.
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
            Initialize scripted worker state.
        Contract:
            - Builds release and completion events for every step.
            - Creates a daemon worker thread bound to `_run`.
        Args:
            name: Worker thread name.
            conduit: Conduit used for meld calls.
            spell_id: Spell id to resolve each step.
            steps: Ordered step names controlled by orchestrator.
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

    def start(self) -> None:
        """
        Purpose:
            Start the worker thread.
        Contract:
            - Must be called before releasing steps.
        Returns:
            None.
        """
        self._thread.start()

    def has_step(self, step: str) -> bool:
        """
        Purpose:
            Check whether this worker is scripted for a step.
        Contract:
            - Returns True only when the step exists in worker script.
        Args:
            step: Step name.
        Returns:
            bool: Step presence indicator.
        """
        return step in self._release_events

    def release(self, step: str) -> None:
        """
        Purpose:
            Release a step so the worker executes its meld attempt.
        Contract:
            - No-op if worker is not scripted for the step.
        Args:
            step: Step name to release.
        Returns:
            None.
        """
        event = self._release_events.get(step)
        if event is not None:
            event.set()

    def wait_done(self, step: str, *, timeout_seconds: float = 10.0) -> None:
        """
        Purpose:
            Wait for step completion.
        Contract:
            - Asserts completion within timeout when step exists.
        Args:
            step: Step name.
            timeout_seconds: Max wait time.
        Returns:
            None.
        Raises:
            AssertionError: If the step did not finish before timeout.
        """
        done_event = self._done_events.get(step)
        if done_event is None:
            return
        assert done_event.wait(timeout=timeout_seconds), (
            f"Worker '{self._name}' did not finish step '{step}' in time."
        )

    def join(self, *, timeout_seconds: float = 10.0) -> None:
        """
        Purpose:
            Join worker thread deterministically.
        Contract:
            - Asserts worker is not alive after timeout.
        Args:
            timeout_seconds: Max join timeout.
        Returns:
            None.
        Raises:
            AssertionError: If worker thread remains alive.
        """
        self._thread.join(timeout=timeout_seconds)
        assert not self._thread.is_alive(), f"Worker '{self._name}' did not terminate."

    def result(self, step: str) -> Any | None:
        """
        Purpose:
            Return meld result for a completed step.
        Contract:
            - Returns None when no result is stored.
        Args:
            step: Step name.
        Returns:
            Any | None: Captured result object.
        """
        with self._lock:
            return self._results.get(step)

    def error(self, step: str) -> BaseException | None:
        """
        Purpose:
            Return captured exception for a completed step.
        Contract:
            - Returns None when step completed without exception.
        Args:
            step: Step name.
        Returns:
            BaseException | None: Captured error.
        """
        with self._lock:
            return self._errors.get(step)

    def _run(self) -> None:
        """
        Purpose:
            Execute scripted meld attempts in step order.
        Contract:
            - Waits for orchestrator release per step.
            - Captures result or error for each step.
            - Always signals step completion.
        Returns:
            None.
        """
        for step in self._steps:
            released = self._release_events[step].wait(timeout=20.0)
            if not released:
                with self._lock:
                    self._errors[step] = TimeoutError(
                        f"Step '{step}' was not released by orchestrator."
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
def reset_aether_singleton_for_multithreading_integration() -> None:
    """
    Purpose:
        Ensure each test starts with a clean Aether singleton.
    Contract:
        - Resets Aether before and after each test.
        - Rebinds Spellbook._aether and Conduit._aether.
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
        Build dynamic configuration for multithreading scenarios.
    Contract:
        - Enables dynamic defaults.
        - Sets phase scheduler worker count.
    Args:
        workers: Scheduler workers per spellbook.
    Returns:
        SpellbookConfiguration: Configured dynamic configuration.
    """
    configuration = SpellbookConfiguration()
    configuration.dynamic_defaults()
    configuration.set_property("phase_scheduler_workers_per_spellbook", workers)
    return configuration


def _release_and_wait(workers: list[_OrchestratedMeldWorker], step: str) -> None:
    """
    Purpose:
        Release a step for all workers and block until completion.
    Contract:
        - Releases only workers scripted for the step.
        - Waits on completion for those workers.
    Args:
        workers: Worker lanes.
        step: Step name to execute.
    Returns:
        None.
    """
    for worker in workers:
        worker.release(step)
    for worker in workers:
        worker.wait_done(step)


def _start_workers(workers: list[_OrchestratedMeldWorker]) -> None:
    """
    Purpose:
        Start all worker lanes.
    Contract:
        - Starts each worker exactly once before orchestrated releases.
    Args:
        workers: Worker lanes.
    Returns:
        None.
    """
    for worker in workers:
        worker.start()


def _join_workers(workers: list[_OrchestratedMeldWorker]) -> None:
    """
    Purpose:
        Join all worker lanes.
    Contract:
        - Asserts no worker remains alive.
    Args:
        workers: Worker lanes.
    Returns:
        None.
    """
    for worker in workers:
        worker.join()


def _remove_root_contract(*, borrower: Conduit, owner: Conduit, root_spell_id: str) -> None:
    """
    Purpose:
        Remove a root contract deterministically in link transaction context.
    Contract:
        - Runs remove_root_from_contracts and asserts zero failures.
    Args:
        borrower: Borrower conduit.
        owner: Owner conduit.
        root_spell_id: Root spell id to remove.
    Returns:
        None.
    """
    with borrower.transaction("link", conduits=[borrower, owner]):
        report = borrower.remove_root_from_contracts(
            root_spell_id=root_spell_id,
            conduit=owner,
        )
    assert report["failed"] == {}


def _restore_root_contract(*, borrower: Conduit, owner: Conduit, root_spell_id: str) -> None:
    """
    Purpose:
        Restore a root contract and its dependency closure.
    Contract:
        - Ensures owner->borrower link exists.
        - Adds root contract with dependencies inside link transaction.
    Args:
        borrower: Borrower conduit.
        owner: Owner conduit.
        root_spell_id: Root spell id to restore.
    Returns:
        None.
    """
    owner.link(borrower)
    with borrower.transaction("link", conduits=[borrower, owner]):
        assert borrower.add_spell_to_contract_with_dependencies(
            spell_id=root_spell_id,
            conduit=owner,
            permissions="create",
        )


def _assert_expected_mutation_error(error: BaseException) -> None:
    """
    Purpose:
        Validate mutation-window errors are expected, not scheduler regressions.
    Contract:
        - Rejects PhaseExecutionError.
        - Accepts SpellbookValidationError, MeldExecutionError, and RuntimeError.
    Args:
        error: Captured step error.
    Returns:
        None.
    Raises:
        AssertionError: If error type is unexpected.
    """
    assert not isinstance(error, PhaseExecutionError), (
        "Unexpected phase scheduler failure under mutation load; "
        f"got: {error!r}"
    )
    assert isinstance(
        error,
        (SpellbookValidationError, MeldExecutionError, RuntimeError),
    ), f"Unexpected mutation error type: {type(error).__name__}: {error!r}"


def _assert_service_consumer(instance: Any) -> None:
    """
    Purpose:
        Validate consumer instance shape used in this suite.
    Contract:
        - Instance must have `.service` of type ContractServiceRemote.
    Args:
        instance: Result object from meld.
    Returns:
        None.
    Raises:
        AssertionError: If object shape is incorrect.
    """
    assert isinstance(instance.service, ContractServiceRemote)


def _assert_worker_step_success(worker: _OrchestratedMeldWorker, step: str) -> Any:
    """
    Purpose:
        Assert worker step finished without error and return result.
    Contract:
        - Step error must be None.
        - Step result must not be None.
    Args:
        worker: Worker lane.
        step: Step name.
    Returns:
        Any: Step result.
    Raises:
        AssertionError: If step failed or no result exists.
    """
    error = worker.error(step)
    assert error is None, f"Unexpected error for step '{step}': {error!r}"
    result = worker.result(step)
    assert result is not None, f"Missing result for step '{step}'."
    return result


def _assert_worker_step_expected_error(worker: _OrchestratedMeldWorker, step: str) -> BaseException:
    """
    Purpose:
        Assert worker step produced a controlled mutation-time failure.
    Contract:
        - Step error must exist.
        - Error must pass mutation error contract.
    Args:
        worker: Worker lane.
        step: Step name.
    Returns:
        BaseException: Captured step error.
    Raises:
        AssertionError: If step unexpectedly succeeded or error is unexpected.
    """
    error = worker.error(step)
    assert error is not None, f"Expected error for step '{step}' but step succeeded."
    _assert_expected_mutation_error(error)
    return error


def _assert_worker_step_cleaned_error(worker: _OrchestratedMeldWorker, step: str) -> None:
    """
    Purpose:
        Assert step failed because the conduit was cleaned.
    Contract:
        - Step error must be RuntimeError.
        - Error message must include 'cleaned'.
    Args:
        worker: Worker lane.
        step: Step name.
    Returns:
        None.
    Raises:
        AssertionError: If step error is not a cleaned-conduit RuntimeError.
    """
    error = worker.error(step)
    assert isinstance(error, RuntimeError), (
        f"Expected RuntimeError for cleaned conduit at step '{step}', got: {error!r}"
    )
    assert "cleaned" in str(error).lower(), (
        f"Expected cleaned error at step '{step}', got: {error!r}"
    )


def test_multithreading_orchestrated_two_threads_contract_toggle() -> None:
    """
    Purpose:
        Validate two worker lanes under orchestrated contract removal and restore.
    Contract:
        - Owner lane remains stable across all steps.
        - Borrower lane is cleaned mid-run and fails on the next meld step.
        - Owner lane continues to meld after borrower cleanup.
    Returns:
        None.
    Raises:
        AssertionError: If behavior diverges from expected transition model.
    """
    owner_book = Spellbook(configuration=_make_dynamic_configuration(workers=4))
    borrower_book = Spellbook(configuration=_make_dynamic_configuration(workers=4))

    service_id = owner_book.bind(
        spell=ContractServiceRemote,
        existence=Existence.unique,
        permissions="create",
        spellframe=IService,
        binding_name="primary",
    )
    consumer_id = borrower_book.bind(
        spell=ThreadConsumerOne,
        existence=Existence.many,
        permissions="create",
    )

    owner = owner_book.conjure(automatic=False, name="owner-two")
    borrower = borrower_book.conjure(automatic=False, name="borrower-two")

    try:
        assert owner.link(borrower) is True
        _restore_root_contract(borrower=borrower, owner=owner, root_spell_id=service_id)

        owner_worker = _OrchestratedMeldWorker(
            name="owner-worker-two",
            conduit=owner,
            spell_id=service_id,
            steps=["pre", "during", "post"],
        )
        borrower_worker = _OrchestratedMeldWorker(
            name="borrower-worker-two",
            conduit=borrower,
            spell_id=consumer_id,
            steps=["pre", "during"],
        )
        workers = [owner_worker, borrower_worker]
        _start_workers(workers)

        _release_and_wait(workers, "pre")
        _assert_worker_step_success(owner_worker, "pre")
        _assert_service_consumer(_assert_worker_step_success(borrower_worker, "pre"))

        borrower.cleanup()
        _release_and_wait(workers, "during")
        _assert_worker_step_success(owner_worker, "during")
        _assert_worker_step_cleaned_error(borrower_worker, "during")

        _release_and_wait(workers, "post")
        _assert_worker_step_success(owner_worker, "post")

        _join_workers(workers)
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_multithreading_orchestrated_three_threads_unlink_restore() -> None:
    """
    Purpose:
        Validate orchestrated unlink/relink with three worker lanes.
    Contract:
        - Owner and borrower-two lanes stay healthy during borrower-one cleanup.
        - Borrower-one lane fails after cleanup.
        - Borrower-two link can be severed/relinked by orchestrator without destabilizing meld.
    Returns:
        None.
    Raises:
        AssertionError: If orchestrated transition behavior is incorrect.
    """
    owner_book = Spellbook(configuration=_make_dynamic_configuration(workers=4))
    borrower_one_book = Spellbook(configuration=_make_dynamic_configuration(workers=4))
    borrower_two_book = Spellbook(configuration=_make_dynamic_configuration(workers=4))

    service_id = owner_book.bind(
        spell=ContractServiceRemote,
        existence=Existence.unique,
        permissions="create",
        spellframe=IService,
        binding_name="primary",
    )
    consumer_one_id = borrower_one_book.bind(
        spell=ThreadConsumerOne,
        existence=Existence.many,
        permissions="create",
    )
    consumer_two_id = borrower_two_book.bind(
        spell=ThreadConsumerTwo,
        existence=Existence.many,
        permissions="create",
    )

    owner = owner_book.conjure(automatic=False, name="owner-three")
    borrower_one = borrower_one_book.conjure(automatic=False, name="borrower-one-three")
    borrower_two = borrower_two_book.conjure(automatic=False, name="borrower-two-three")

    try:
        assert owner.link(borrower_one) is True
        assert owner.link(borrower_two) is True
        _restore_root_contract(borrower=borrower_one, owner=owner, root_spell_id=service_id)
        _restore_root_contract(borrower=borrower_two, owner=owner, root_spell_id=service_id)

        owner_worker = _OrchestratedMeldWorker(
            name="owner-worker-three",
            conduit=owner,
            spell_id=service_id,
            steps=["pre", "during", "post"],
        )
        borrower_one_worker = _OrchestratedMeldWorker(
            name="borrower-one-worker-three",
            conduit=borrower_one,
            spell_id=consumer_one_id,
            steps=["pre", "during"],
        )
        borrower_two_worker = _OrchestratedMeldWorker(
            name="borrower-two-worker-three",
            conduit=borrower_two,
            spell_id=consumer_two_id,
            steps=["pre", "during", "post"],
        )
        workers = [owner_worker, borrower_one_worker, borrower_two_worker]
        _start_workers(workers)

        _release_and_wait(workers, "pre")
        _assert_worker_step_success(owner_worker, "pre")
        _assert_service_consumer(_assert_worker_step_success(borrower_one_worker, "pre"))
        _assert_service_consumer(_assert_worker_step_success(borrower_two_worker, "pre"))

        borrower_one.cleanup()
        assert owner.sever_link(borrower_two) is True
        _restore_root_contract(borrower=borrower_two, owner=owner, root_spell_id=service_id)
        _release_and_wait(workers, "during")
        _assert_worker_step_success(owner_worker, "during")
        _assert_worker_step_cleaned_error(borrower_one_worker, "during")
        _assert_service_consumer(_assert_worker_step_success(borrower_two_worker, "during"))

        _release_and_wait(workers, "post")
        _assert_worker_step_success(owner_worker, "post")
        _assert_service_consumer(_assert_worker_step_success(borrower_two_worker, "post"))

        _join_workers(workers)
    finally:
        borrower_two.cleanup()
        borrower_one.cleanup()
        owner.cleanup()


def test_multithreading_orchestrated_four_threads_mixed_mutations() -> None:
    """
    Purpose:
        Validate orchestrated mixed mutations across four worker lanes.
    Contract:
        - Owner and borrower-three remain stable during mutation window.
        - Borrower-one fails after cleanup.
        - Borrower-two and borrower-three survive orchestrated unlink/relink and contract churn.
    Returns:
        None.
    Raises:
        AssertionError: If mixed mutation behavior diverges from contract.
    """
    owner_book = Spellbook(configuration=_make_dynamic_configuration(workers=4))
    borrower_one_book = Spellbook(configuration=_make_dynamic_configuration(workers=4))
    borrower_two_book = Spellbook(configuration=_make_dynamic_configuration(workers=4))
    borrower_three_book = Spellbook(configuration=_make_dynamic_configuration(workers=4))

    service_id = owner_book.bind(
        spell=ContractServiceRemote,
        existence=Existence.unique,
        permissions="create",
        spellframe=IService,
        binding_name="primary",
    )
    consumer_one_id = borrower_one_book.bind(
        spell=ThreadConsumerOne,
        existence=Existence.many,
        permissions="create",
    )
    consumer_two_id = borrower_two_book.bind(
        spell=ThreadConsumerTwo,
        existence=Existence.many,
        permissions="create",
    )
    consumer_three_id = borrower_three_book.bind(
        spell=ThreadConsumerThree,
        existence=Existence.many,
        permissions="create",
    )

    owner = owner_book.conjure(automatic=False, name="owner-four")
    borrower_one = borrower_one_book.conjure(automatic=False, name="borrower-one-four")
    borrower_two = borrower_two_book.conjure(automatic=False, name="borrower-two-four")
    borrower_three = borrower_three_book.conjure(automatic=False, name="borrower-three-four")

    try:
        assert owner.link(borrower_one) is True
        assert owner.link(borrower_two) is True
        assert owner.link(borrower_three) is True
        _restore_root_contract(borrower=borrower_one, owner=owner, root_spell_id=service_id)
        _restore_root_contract(borrower=borrower_two, owner=owner, root_spell_id=service_id)
        _restore_root_contract(borrower=borrower_three, owner=owner, root_spell_id=service_id)

        owner_worker = _OrchestratedMeldWorker(
            name="owner-worker-four",
            conduit=owner,
            spell_id=service_id,
            steps=["pre", "during", "post"],
        )
        borrower_one_worker = _OrchestratedMeldWorker(
            name="borrower-one-worker-four",
            conduit=borrower_one,
            spell_id=consumer_one_id,
            steps=["pre", "during"],
        )
        borrower_two_worker = _OrchestratedMeldWorker(
            name="borrower-two-worker-four",
            conduit=borrower_two,
            spell_id=consumer_two_id,
            steps=["pre", "during", "post"],
        )
        borrower_three_worker = _OrchestratedMeldWorker(
            name="borrower-three-worker-four",
            conduit=borrower_three,
            spell_id=consumer_three_id,
            steps=["pre", "during", "post"],
        )
        workers = [owner_worker, borrower_one_worker, borrower_two_worker, borrower_three_worker]
        _start_workers(workers)

        _release_and_wait(workers, "pre")
        _assert_worker_step_success(owner_worker, "pre")
        _assert_service_consumer(_assert_worker_step_success(borrower_one_worker, "pre"))
        _assert_service_consumer(_assert_worker_step_success(borrower_two_worker, "pre"))
        _assert_service_consumer(_assert_worker_step_success(borrower_three_worker, "pre"))

        borrower_one.cleanup()
        _remove_root_contract(borrower=borrower_two, owner=owner, root_spell_id=service_id)
        _restore_root_contract(borrower=borrower_two, owner=owner, root_spell_id=service_id)
        assert owner.sever_link(borrower_three) is True
        _restore_root_contract(borrower=borrower_three, owner=owner, root_spell_id=service_id)

        _release_and_wait(workers, "during")
        _assert_worker_step_success(owner_worker, "during")
        _assert_worker_step_cleaned_error(borrower_one_worker, "during")
        _assert_service_consumer(_assert_worker_step_success(borrower_two_worker, "during"))
        _assert_service_consumer(_assert_worker_step_success(borrower_three_worker, "during"))

        _release_and_wait(workers, "post")
        _assert_worker_step_success(owner_worker, "post")
        _assert_service_consumer(_assert_worker_step_success(borrower_two_worker, "post"))
        _assert_service_consumer(_assert_worker_step_success(borrower_three_worker, "post"))

        _join_workers(workers)
    finally:
        borrower_three.cleanup()
        borrower_two.cleanup()
        borrower_one.cleanup()
        owner.cleanup()


def test_multithreading_orchestrated_five_threads_with_mid_cleanup() -> None:
    """
    Purpose:
        Validate orchestrated five-thread scenario with contract churn, unlink, and cleanup.
    Contract:
        - Owner and borrower-three stay healthy during mutation window.
        - Borrower-one and borrower-four fail after cleanup.
        - Borrower-two and borrower-three survive orchestrated unlink/relink + contract churn.
        - Borrower-four fails after conduit cleanup.
        - Non-cleaned borrowers remain healthy after post step.
    Returns:
        None.
    Raises:
        AssertionError: If state transitions violate expected behavior.
    """
    owner_book = Spellbook(configuration=_make_dynamic_configuration(workers=4))
    borrower_one_book = Spellbook(configuration=_make_dynamic_configuration(workers=4))
    borrower_two_book = Spellbook(configuration=_make_dynamic_configuration(workers=4))
    borrower_three_book = Spellbook(configuration=_make_dynamic_configuration(workers=4))
    borrower_four_book = Spellbook(configuration=_make_dynamic_configuration(workers=4))

    service_id = owner_book.bind(
        spell=ContractServiceRemote,
        existence=Existence.unique,
        permissions="create",
        spellframe=IService,
        binding_name="primary",
    )
    consumer_one_id = borrower_one_book.bind(
        spell=ThreadConsumerOne,
        existence=Existence.many,
        permissions="create",
    )
    consumer_two_id = borrower_two_book.bind(
        spell=ThreadConsumerTwo,
        existence=Existence.many,
        permissions="create",
    )
    consumer_three_id = borrower_three_book.bind(
        spell=ThreadConsumerThree,
        existence=Existence.many,
        permissions="create",
    )
    consumer_four_id = borrower_four_book.bind(
        spell=ThreadConsumerFour,
        existence=Existence.many,
        permissions="create",
    )

    owner = owner_book.conjure(automatic=False, name="owner-five")
    borrower_one = borrower_one_book.conjure(automatic=False, name="borrower-one-five")
    borrower_two = borrower_two_book.conjure(automatic=False, name="borrower-two-five")
    borrower_three = borrower_three_book.conjure(automatic=False, name="borrower-three-five")
    borrower_four = borrower_four_book.conjure(automatic=False, name="borrower-four-five")

    try:
        assert owner.link(borrower_one) is True
        assert owner.link(borrower_two) is True
        assert owner.link(borrower_three) is True
        assert owner.link(borrower_four) is True
        _restore_root_contract(borrower=borrower_one, owner=owner, root_spell_id=service_id)
        _restore_root_contract(borrower=borrower_two, owner=owner, root_spell_id=service_id)
        _restore_root_contract(borrower=borrower_three, owner=owner, root_spell_id=service_id)
        _restore_root_contract(borrower=borrower_four, owner=owner, root_spell_id=service_id)

        owner_worker = _OrchestratedMeldWorker(
            name="owner-worker-five",
            conduit=owner,
            spell_id=service_id,
            steps=["pre", "during", "post"],
        )
        borrower_one_worker = _OrchestratedMeldWorker(
            name="borrower-one-worker-five",
            conduit=borrower_one,
            spell_id=consumer_one_id,
            steps=["pre", "during"],
        )
        borrower_two_worker = _OrchestratedMeldWorker(
            name="borrower-two-worker-five",
            conduit=borrower_two,
            spell_id=consumer_two_id,
            steps=["pre", "during", "post"],
        )
        borrower_three_worker = _OrchestratedMeldWorker(
            name="borrower-three-worker-five",
            conduit=borrower_three,
            spell_id=consumer_three_id,
            steps=["pre", "during", "post"],
        )
        borrower_four_worker = _OrchestratedMeldWorker(
            name="borrower-four-worker-five",
            conduit=borrower_four,
            spell_id=consumer_four_id,
            steps=["pre", "during"],
        )
        workers = [
            owner_worker,
            borrower_one_worker,
            borrower_two_worker,
            borrower_three_worker,
            borrower_four_worker,
        ]
        _start_workers(workers)

        _release_and_wait(workers, "pre")
        _assert_worker_step_success(owner_worker, "pre")
        _assert_service_consumer(_assert_worker_step_success(borrower_one_worker, "pre"))
        _assert_service_consumer(_assert_worker_step_success(borrower_two_worker, "pre"))
        _assert_service_consumer(_assert_worker_step_success(borrower_three_worker, "pre"))
        _assert_service_consumer(_assert_worker_step_success(borrower_four_worker, "pre"))

        borrower_one.cleanup()
        assert owner.sever_link(borrower_two) is True
        _restore_root_contract(borrower=borrower_two, owner=owner, root_spell_id=service_id)
        _remove_root_contract(borrower=borrower_three, owner=owner, root_spell_id=service_id)
        _restore_root_contract(borrower=borrower_three, owner=owner, root_spell_id=service_id)
        borrower_four.cleanup()

        _release_and_wait(workers, "during")
        _assert_worker_step_success(owner_worker, "during")
        _assert_worker_step_cleaned_error(borrower_one_worker, "during")
        _assert_service_consumer(_assert_worker_step_success(borrower_two_worker, "during"))
        _assert_service_consumer(_assert_worker_step_success(borrower_three_worker, "during"))
        _assert_worker_step_cleaned_error(borrower_four_worker, "during")

        _release_and_wait(workers, "post")
        _assert_worker_step_success(owner_worker, "post")
        _assert_service_consumer(_assert_worker_step_success(borrower_two_worker, "post"))
        _assert_service_consumer(_assert_worker_step_success(borrower_three_worker, "post"))

        _join_workers(workers)

        borrower_two_state = borrower_two_book._spell_system_states.get_conduit_resolution_state(borrower_two._id)
        borrower_three_state = borrower_three_book._spell_system_states.get_conduit_resolution_state(borrower_three._id)
        assert borrower_two_state is not None
        assert borrower_three_state is not None
        assert borrower_two_state.get_root_validity(consumer_two_id) is SpellValidity.valid
        assert borrower_three_state.get_root_validity(consumer_three_id) is SpellValidity.valid
    finally:
        borrower_four.cleanup()
        borrower_three.cleanup()
        borrower_two.cleanup()
        borrower_one.cleanup()
        owner.cleanup()
