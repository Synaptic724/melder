"""
Experiment the runtime boundary between MutationContract sockets and
spell-owned mutation overrides.

Purpose:
    Prove, with one focused A/B runtime experiment, that a spell-owned
    ``mutation_override`` only produces a successful meld-time rewiring when
    the target parameter is actually declared as a ``MutationContract`` socket.

Scope:
    - This test intentionally bypasses the current Phase 4
      ``MUTATION_CONTRACT_DISABLED`` validation issue so we can observe the
      runtime behavior that sits behind that gate today.
    - It does not change production behavior.
    - It does not claim mutation contracts are fully enabled in normal runs.
"""

from __future__ import annotations

from typing import Any, Iterator

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.meld.contracts.mutation_contract import MutationContract
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.validation.strategies.contract_provider_presence_strategy import (
    ContractProviderPresenceStrategy,
)
from melder.aether.spellbook.spellbook import Spellbook
from melder.utilities.custom_exceptions.meld_execution_error import (
    MeldExecutionError,
)
from melder.utilities.custom_exceptions.phase_execution_error import (
    PhaseExecutionError,
)


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_mutation_override_experiment() -> Iterator[None]:
    """
    Reset global runtime singletons around the experiment.

    Contract:
        - Ensures each experiment case starts from a clean Aether singleton.
        - Rebinds ``Spellbook._aether`` and ``Conduit._aether`` to the fresh
          singleton before the case runs.
        - Resets the singleton again after the case completes.

    Yields:
        None.
    """
    _reset_runtime_singletons()
    yield
    _reset_runtime_singletons()


def _reset_runtime_singletons() -> None:
    """
    Reset the Aether singleton and rebind spellbook/conduit globals.

    Returns:
        None.
    """
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


@pytest.fixture
def allow_mutation_contract_runtime_path(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Suppress only the current Phase 4 mutation-contract disable issue.

    Purpose:
        Reach the runtime meld path behind the current validation gate so the
        experiment can prove whether ``MutationContract`` sockets are actually
        required for spell-owned mutation overrides to take effect.

    Contract:
        - Calls the real strategy implementation first.
        - Removes only ``MUTATION_CONTRACT_DISABLED`` issues from the mutable
          validation issue list.
        - Leaves every other validation issue untouched.

    Args:
        monkeypatch:
            Pytest monkeypatch fixture used to patch the strategy method for
            the duration of the test.

    Returns:
        None.
    """
    original_validate = ContractProviderPresenceStrategy.validate

    def _validate_without_disable_issue(
            self: ContractProviderPresenceStrategy,
            context: Any,
    ) -> None:
        """
        Run the real validation strategy, then drop only the disable issue.

        Args:
            self:
                Strategy instance under test.
            context:
                Spell validation context supplied by the runtime.

        Returns:
            None.
        """
        original_validate(self, context)
        context.issues[:] = [
            issue
            for issue in context.issues
            if issue.code != "MUTATION_CONTRACT_DISABLED"
        ]

    monkeypatch.setattr(
        ContractProviderPresenceStrategy,
        "validate",
        _validate_without_disable_issue,
    )


class DefaultMutationProvider:
    """
    Default mutation-provider spell used by the experiment.

    Contract:
        - Stores ``marker='default'`` so the resolved provider identity can be
          asserted directly.
    """

    def __init__(self) -> None:
        """
        Initialize the default provider marker.

        Returns:
            None.
        """
        self.marker = "default"


class OverrideMutationProvider:
    """
    Alternate mutation-provider spell used as the mutation target.

    Contract:
        - Stores ``marker='override'`` so the rewired meld result is easy to
          distinguish from the default provider.
    """

    def __init__(self) -> None:
        """
        Initialize the override provider marker.

        Returns:
            None.
        """
        self.marker = "override"


def _make_spellbook() -> Spellbook:
    """
    Build a dynamic Spellbook configured for single-worker reproducibility.

    Returns:
        Spellbook:
            Configured spellbook for the experiment.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    spellbook._aetheric_frame_configuration.with_system_state("dynamic")
    return spellbook


def _get_spell_by_version_id(
        spellbook: Spellbook,
        spell_id: str,
) -> object:
    """
    Resolve one locally bound spell by its current version id.

    Args:
        spellbook:
            Spellbook holding the local spell registry.
        spell_id:
            Versioned spell id returned by ``bind(...)``.

    Returns:
        object:
            Matching bound spell object.

    Raises:
        AssertionError:
            If no matching spell exists.
    """
    for spell_index, spell in spellbook.spells.items():
        if spell_index.current == spell_id:
            return spell
    raise AssertionError(
        "Expected local spell for version id '{0}'.".format(spell_id)
    )


def _make_host_with_mutation_contract() -> type:
    """
    Build a host spell class whose dependency socket is mutation-capable.

    Returns:
        type:
            Host class with a ``MutationContract`` default on ``mutant``.
    """
    contract = MutationContract(spellframe=DefaultMutationProvider)

    class MutationHost:
        """
        Host spell with a MutationContract-backed dependency socket.

        Contract:
            - The ``mutant`` parameter is a mutation-capable socket.
            - The resolved dependency is stored on the instance.
        """

        def __init__(self, mutant: object = contract) -> None:
            """
            Store the resolved mutation dependency.

            Args:
                mutant:
                    Mutation-capable dependency value.

            Returns:
                None.
            """
            self.mutant = mutant

    return MutationHost


def _make_host_without_mutation_contract() -> type:
    """
    Build a host spell class whose dependency socket is a normal DI socket.

    Returns:
        type:
            Host class with a plain dependency socket named ``mutant``.
    """
    class PlainHost:
        """
        Host spell with a normal non-mutation dependency socket.

        Contract:
            - The ``mutant`` parameter is resolved as a normal dependency.
            - The resolved dependency is stored on the instance.
        """

        def __init__(self, mutant: DefaultMutationProvider) -> None:
            """
            Store the resolved dependency.

            Args:
                mutant:
                    Plain dependency value.

            Returns:
                None.
            """
            self.mutant = mutant

    return PlainHost


def test_experiment_mutation_override_added_after_conjure_requires_mutation_contract(
        allow_mutation_contract_runtime_path: None,
) -> None:
    """
    Prove the post-conjure A/B runtime difference with and without a mutation
    socket before any instance exists.

    Contract:
        - Both spellbooks conjure successfully before any mutation override is
          applied.
        - When the host declares a ``MutationContract`` socket named
          ``mutant``, applying a spell-owned ``mutation_override`` after
          conjure rewires the later meld-time resolution to the override
          provider spell.
        - When the host does not declare a ``MutationContract`` socket, the
          same post-conjure ``mutation_override`` payload fails at meld time
          because no mutation socket exists to target.

    Args:
        allow_mutation_contract_runtime_path:
            Fixture that suppresses only the current validation disable issue
            so the runtime path can be observed.

    Returns:
        None.
    """
    _ = allow_mutation_contract_runtime_path

    mutation_spellbook = _make_spellbook()
    mutation_override_spell_id = mutation_spellbook.bind(
        spell=OverrideMutationProvider,
        existence=Existence.unique,
        permissions="create",
    )
    mutation_host_class = _make_host_with_mutation_contract()
    mutation_host_spell_id = mutation_spellbook.bind(
        spell=mutation_host_class,
        existence=Existence.unique,
        permissions="create",
    )
    mutation_conduit = mutation_spellbook.conjure(
        name="mutation-root",
        automatic=False,
    )
    try:
        mutation_host_spell = _get_spell_by_version_id(
            mutation_spellbook,
            mutation_host_spell_id,
        )
        mutation_host_spell.apply_mutation_override(
            {"mutant": mutation_override_spell_id}
        )

        mutation_instance = mutation_conduit.meld(spell=mutation_host_spell_id)

        assert isinstance(mutation_instance, mutation_host_class)
        assert isinstance(mutation_instance.mutant, OverrideMutationProvider)
        assert mutation_instance.mutant.marker == "override"
    finally:
        mutation_conduit.cleanup()

    _reset_runtime_singletons()

    plain_spellbook = _make_spellbook()
    plain_override_spell_id = plain_spellbook.bind(
        spell=OverrideMutationProvider,
        existence=Existence.unique,
        permissions="create",
    )
    plain_spellbook.bind(
        spell=DefaultMutationProvider,
        existence=Existence.unique,
        permissions="create",
    )
    plain_host_class = _make_host_without_mutation_contract()
    plain_host_spell_id = plain_spellbook.bind(
        spell=plain_host_class,
        existence=Existence.unique,
        permissions="create",
    )
    plain_conduit = plain_spellbook.conjure(
        name="plain-root",
        automatic=False,
    )
    try:
        plain_host_spell = _get_spell_by_version_id(
            plain_spellbook,
            plain_host_spell_id,
        )
        plain_host_spell.apply_mutation_override(
            {"mutant": plain_override_spell_id}
        )

        with pytest.raises(
                PhaseExecutionError,
                match="No mutation sockets found",
        ):
            plain_conduit.meld(spell=plain_host_spell_id)
    finally:
        plain_conduit.cleanup()


def test_experiment_mutation_override_after_shared_instance_exists_fails(
        allow_mutation_contract_runtime_path: None,
) -> None:
    """
    Prove the shared-instance reuse guard once a unique host has already melded.

    Contract:
        - A host with a ``MutationContract`` socket can meld once without any
          mutation override and produce the unresolved contract placeholder.
        - If a spell-owned mutation override is applied after that unique/shared
          instance already exists, the later meld fails with the override-on-
          existing-instance guard instead of silently mutating the live object.

    Returns:
        None.
    """
    _ = allow_mutation_contract_runtime_path

    mutation_spellbook = _make_spellbook()
    mutation_override_spell_id = mutation_spellbook.bind(
        spell=OverrideMutationProvider,
        existence=Existence.unique,
        permissions="create",
    )
    mutation_host_class = _make_host_with_mutation_contract()
    mutation_host_spell_id = mutation_spellbook.bind(
        spell=mutation_host_class,
        existence=Existence.unique,
        permissions="create",
    )
    mutation_conduit = mutation_spellbook.conjure(
        name="mutation-existing-root",
        automatic=False,
    )
    try:
        mutation_host_spell = _get_spell_by_version_id(
            mutation_spellbook,
            mutation_host_spell_id,
        )
        baseline_instance = mutation_conduit.meld(spell=mutation_host_spell_id)
        assert isinstance(baseline_instance, mutation_host_class)
        assert isinstance(baseline_instance.mutant, MutationContract)
        assert baseline_instance.mutant.spellframe is DefaultMutationProvider

        mutation_host_spell.apply_mutation_override(
            {"mutant": mutation_override_spell_id}
        )

        with pytest.raises(
                MeldExecutionError,
                match="Shared instances cannot be overridden after creation",
        ):
            mutation_conduit.meld(spell=mutation_host_spell_id)
    finally:
        mutation_conduit.cleanup()
