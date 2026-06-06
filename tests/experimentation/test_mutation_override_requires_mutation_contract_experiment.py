"""
Experiment the runtime boundary between MutationContract sockets and
spell-owned mutation bindings.

Purpose:
    Prove, with one focused A/B runtime experiment, that:
    - unresolved MutationContract sockets block meld
    - a spell-owned ``mutation_override`` only produces successful meld-time
      rewiring when the target parameter is actually declared as a
      ``MutationContract`` socket

Scope:
    - This test exercises the live runtime behavior directly.
    - It does not claim planner/phase-11 mutation-lane cleanup is complete.
"""

from typing import Any, Iterator

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.meld.contracts.mutation_contract import MutationContract
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.utilities.custom_exceptions.meld_execution_error import (
    MeldExecutionError,
)
from melder.utilities.custom_exceptions.phase_execution_error import (
    PhaseExecutionError,
)
from melder.utilities.custom_exceptions.spellbook_validation_error import (
    SpellbookValidationError,
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


def test_experiment_mutation_override_added_after_conjure_requires_mutation_contract() -> None:
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
    Returns:
        None.
    """
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


def test_experiment_unresolved_mutation_contract_blocks_meld() -> None:
    """
    Prove a MutationContract socket cannot baseline-meld while unresolved.

    Contract:
        - Conjure still succeeds in dynamic mode.
        - Meld fails until the mutation socket is satisfied by a mutation
          binding.

    Returns:
        None.
    """
    mutation_spellbook = _make_spellbook()
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
        with pytest.raises(SpellbookValidationError):
            mutation_conduit.meld(spell=mutation_host_spell_id)
    finally:
        mutation_conduit.cleanup()
