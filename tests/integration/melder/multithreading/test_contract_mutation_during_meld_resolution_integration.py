"""
Regression: a meld that loses its SpellContract provider in the middle of its resolution pass.

The hosted macOS 3.14.8 run of `test_multithreading_live_link_unlink_and_contract_churn_cycles`
(2026-10-04) failed with PhaseExecutionError ("Phase 'injection_plan_local' ... RuntimeError:
Occurrence spell could not be resolved from the spell lookup."): a link sever on another thread
popped the borrowed provider from the borrower's pool after Phase 8 saw it and before a Phase 9
processor looked it up. These tests force that interleaving instead of racing for it. The
mutation runs to completion on its own thread just before one of the two Phase 9 processors
that read the live pool, and the meld must end in the SpellbookValidationError a meld starting a
moment later gets. After the contract is restored the consumer melds again.
"""

from threading import Thread
from typing import Any, Callable, Iterator, Optional

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.artifact_processor.strategies.spell_occurrence_contract_processor_strategy import (
    SpellOccurrenceContractProcessorStrategy,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.strategies.spell_runtime_processor_strategy import (
    SpellRuntimeProcessorStrategy,
)
from melder.aether.spellbook.spellbook import Spellbook
from melder.utilities.custom_exceptions.spellbook_validation_error import SpellbookValidationError
from tests._frame_posture_test_support import apply_dynamic_defaults_for_spellbook_configuration
from tests.mocks.spellbook.contract_classes import ContractServicePrimary
from tests.mocks.spellbook.protocols import IService


class _RaceConsumer:
    """
    Purpose:
        SpellContract consumer whose provider a forced mutation removes mid-resolution.
    Contract:
        - Receives IService(primary) through its SpellContract default on every meld.
    """

    def __init__(
            self,
            service: IService = SpellContract(spellframe=IService, binding_name="primary"),
    ) -> None:
        """
        Purpose:
            Keep the resolved service for the assertions.
        Args:
            service: The contracted IService provider.
        Returns:
            None.
        """
        self.service = service


class _ContractWorld:
    """
    Purpose:
        Build the churn test's lane in miniature: an owner conduit providing IService(primary)
        and a borrower conduit whose consumer resolves it through a contract.
    Contract:
        - Both books are dynamic with four scheduler workers, as in the churn test.
        - `restore_contract` re-links and re-contracts the provider the way the churn test does.
        - `cleanup` tears down the borrower before the owner.
    """

    def __init__(self) -> None:
        """
        Purpose:
            Bind, conjure, link and contract the two-conduit world.
        Returns:
            None.
        """
        owner_book = Spellbook(configuration=_dynamic_configuration())
        borrower_book = Spellbook(configuration=_dynamic_configuration())
        self.service_id: str = owner_book.bind(
            spell=ContractServicePrimary,
            existence=Existence.many,
            permissions="create",
            spellframe=IService,
            binding_name="primary",
        )
        self.consumer_id: str = borrower_book.bind(
            spell=_RaceConsumer,
            existence=Existence.many,
            permissions="create",
        )
        self.owner: Conduit = owner_book.conjure(dynamic=True, name="race-owner")
        self.borrower: Conduit = borrower_book.conjure(dynamic=True, name="race-borrower")
        self.restore_contract()

    def restore_contract(self) -> None:
        """
        Purpose:
            Link the borrower to the owner and contract the provider with its dependencies.
        Returns:
            None.
        """
        self.owner.link(self.borrower)
        with self.borrower.transaction("link", conduits=[self.borrower, self.owner]):
            assert self.borrower.add_spell_to_contract_with_dependencies(
                spell_id=self.service_id,
                conduit=self.owner,
                permissions="create",
            )
        self.borrower.validate_contracts_and_define()

    def meld_consumer(self) -> Any:
        """
        Purpose:
            Meld the borrower's consumer once.
        Returns:
            Any: The consumer instance.
        """
        return self.borrower.meld(spell_id=self.consumer_id)

    def cleanup(self) -> None:
        """
        Purpose:
            Tear down the borrower, then the owner.
        Returns:
            None.
        """
        self.borrower.cleanup()
        self.owner.cleanup()


class _MutationProbe:
    """
    Purpose:
        Run one contract mutation to completion just before a wrapped processor's first call.
    Contract:
        - The mutation runs on its own thread and is joined, so it lands after the pass's
          Phase 8 and before the wrapped Phase 9 processor reads the pool.
        - Later calls go straight to the wrapped method.
        - Failures are recorded and asserted on the test thread, because the wrapper runs on a
          phase-scheduler worker whose exceptions become phase errors.
    """

    def __init__(
            self,
            world: _ContractWorld,
            mutation: Callable[[_ContractWorld], None],
    ) -> None:
        """
        Purpose:
            Hold the world and the mutation to apply.
        Args:
            world: The two-conduit world under test.
            mutation: Callable that removes the provider from the borrower's view.
        Returns:
            None.
        """
        self._world = world
        self._mutation = mutation
        self._fired = False
        self._finished = False
        self._error: Optional[Exception] = None

    def wrap(self, original: Callable[[Any, Any, Any, Any], None]) -> Callable[[Any, Any, Any, Any], None]:
        """
        Purpose:
            Build the replacement `process` method.
        Args:
            original: The processor's own `process` function.
        Returns:
            Callable: A `process` that mutates once, then delegates.
        """

        def process(strategy: Any, spell: Any, artifact: Any, model: Any) -> None:
            if not self._fired:
                self._fired = True
                self._run_mutation()
            original(strategy, spell, artifact, model)

        return process

    def _run_mutation(self) -> None:
        """
        Purpose:
            Run the mutation on a helper thread and wait for it.
        Returns:
            None.
        """
        worker = Thread(target=self._mutate, name="race-mutation", daemon=True)
        worker.start()
        worker.join(timeout=20.0)
        self._finished = not worker.is_alive()

    def _mutate(self) -> None:
        """
        Purpose:
            Apply the mutation and keep any exception for the test thread.
        Returns:
            None.
        """
        try:
            self._mutation(self._world)
        except Exception as exc:
            self._error = exc

    def assert_completed(self) -> None:
        """
        Purpose:
            Prove the forced interleaving happened.
        Returns:
            None.
        Raises:
            AssertionError: If the processor never ran or the mutation hung or failed.
        """
        assert self._fired, "The wrapped Phase 9 processor never ran."
        assert self._finished, "The mutation did not finish within 20 s."
        assert self._error is None, f"The mutation failed: {self._error!r}"


def _dynamic_configuration() -> SpellbookConfiguration:
    """
    Purpose:
        Dynamic Spellbook configuration with four phase-scheduler workers.
    Returns:
        SpellbookConfiguration: The configuration.
    """
    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 4)
    return configuration


def _sever_link(world: _ContractWorld) -> None:
    """
    Purpose:
        Sever the owner-borrower link, as the churn test's unlink step does.
    Args:
        world: The two-conduit world.
    Returns:
        None.
    """
    world.owner.sever_link(world.borrower)


def _uncontract(world: _ContractWorld) -> None:
    """
    Purpose:
        Remove the provider root from the borrower's contracts, as the churn test's uncontract step does.
    Args:
        world: The two-conduit world.
    Returns:
        None.
    """
    with world.borrower.transaction("link", conduits=[world.borrower, world.owner]):
        world.borrower.remove_root_from_contracts(
            root_spell_id=world.service_id,
            conduit=world.owner,
        )


def _install_fresh_aether() -> None:
    """
    Purpose:
        Reset the Aether singleton and rebind the class-level handles.
    Returns:
        None.
    """
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


@pytest.fixture(autouse=True)
def fresh_aether_for_resolution_race() -> Iterator[None]:
    """
    Purpose:
        Give each test its own Aether singleton.
    Returns:
        Iterator[None]: Yields once around the test.
    """
    _install_fresh_aether()
    yield
    _install_fresh_aether()


@pytest.mark.parametrize(
    "mutation",
    [_sever_link, _uncontract],
    ids=["sever_link", "uncontract"],
)
@pytest.mark.parametrize(
    "processor_cls",
    [SpellOccurrenceContractProcessorStrategy, SpellRuntimeProcessorStrategy],
    ids=["contract_processor", "runtime_processor"],
)
def test_meld_that_loses_its_contract_provider_mid_resolution_raises_validation_error(
        monkeypatch: pytest.MonkeyPatch,
        processor_cls: type,
        mutation: Callable[[_ContractWorld], None],
) -> None:
    """
    Purpose:
        A meld whose provider leaves the borrower's pool between Phase 8 and a Phase 9 processor
        raises SpellbookValidationError, never PhaseExecutionError, and the consumer recovers.
    Contract:
        - Before 0.2.8227 both processors reported the miss as RuntimeError, which the target
          pass could not classify, so the meld raised PhaseExecutionError.
        - After the contract is restored, the next meld resolves the provider again.
    """
    world = _ContractWorld()
    try:
        assert isinstance(world.meld_consumer().service, ContractServicePrimary)

        probe = _MutationProbe(world, mutation)
        monkeypatch.setattr(processor_cls, "process", probe.wrap(processor_cls.process))
        with pytest.raises(SpellbookValidationError):
            world.meld_consumer()
        monkeypatch.undo()
        probe.assert_completed()

        world.restore_contract()
        assert isinstance(world.meld_consumer().service, ContractServicePrimary)
    finally:
        world.cleanup()
