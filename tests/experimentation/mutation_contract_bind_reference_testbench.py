"""
Experiment MutationContract reference behavior after bind.

Purpose:
    Answer one concrete runtime question:
    when a class declares a ``MutationContract`` default in ``__init__`` and we
    bind that class into a spell, what object do we recover later from the
    bound spell's requirements path?

This bench checks two things:
    1. whether the bound spell can recover the same live in-memory
       ``MutationContract`` object that was declared on the class signature
    2. whether mutating that recovered reference in memory "sticks" when we
       re-read the signature default and the spell requirements again

This is an experimentation bench, not production runtime code.
"""

import faulthandler
import inspect
import os
import sys
import threading
from typing import Optional


if "src" not in sys.path:
    sys.path.insert(0, "src")


from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.meld.contracts.mutation_contract import MutationContract
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell_crafter.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from melder.spellbook.spellbook import Spellbook


EXPERIMENT_TIMEOUT_SECONDS = 10.0


def _emit(marker: str) -> None:
    """
    Print one unbuffered progress marker.

    Args:
        marker:
            Marker text to print.

    Returns:
        None.
    """
    sys.stdout.write(marker + "\n")
    sys.stdout.flush()


def _run_with_timeout(label: str, func, timeout_seconds: float = EXPERIMENT_TIMEOUT_SECONDS) -> None:
    """
    Run one experiment on the main thread with a hard watchdog timer.

    Args:
        label:
            Label used in timeout/progress markers.
        func:
            Callable experiment body.
        timeout_seconds:
            Watchdog timeout.

    Returns:
        None.
    """

    def watchdog() -> None:
        sys.stderr.write("TIMEOUT_{0}_{1:.1f}s\n".format(label, timeout_seconds))
        faulthandler.dump_traceback(file=sys.stderr, all_threads=True)
        sys.stderr.flush()
        os._exit(124)

    _emit("START_{0}".format(label))
    timer = threading.Timer(timeout_seconds, watchdog)
    timer.daemon = True
    timer.start()
    try:
        func()
    finally:
        timer.cancel()
    _emit("DONE_{0}".format(label))


def _find_spell_by_version_id(spellbook: Spellbook, spell_id: str):
    """
    Return the bound spell for one version id.

    Args:
        spellbook:
            Spellbook holding the bound spell.
        spell_id:
            Bound spell version id returned by ``bind(...)``.

    Returns:
        ISpell:
            Matching bound spell.

    Raises:
        AssertionError:
            If the spell cannot be found.
    """
    spell = spellbook.find_spell_by_id(spell_id)
    assert spell is not None, "Expected bound spell for spell_id={0}".format(spell_id)
    return spell


def _get_mutation_requirement(spell):
    """
    Return the first MutationContract parameter requirement for a spell.

    Args:
        spell:
            Bound spell whose Phase 1 requirements should be inspected.

    Returns:
        SpellParameterRequirement:
            First requirement classified as ``MUTATION_CONTRACT``.

    Raises:
        AssertionError:
            If no mutation requirement is present.
    """
    spell.run_phase_requirements()
    requirements = spell.requirements
    assert requirements is not None, "Expected Phase 1 requirements."
    for requirement in requirements.parameters:
        if requirement.di_shape is ParameterDIShape.MUTATION_CONTRACT:
            return requirement
    raise AssertionError("Expected one MutationContract requirement.")


def _experiment_bind_reference_recovery_and_update() -> None:
    """
    Bind a class with a MutationContract default and prove reference behavior.

    Returns:
        None.
    """

    class ProviderA:
        """
        Default mutation provider shape for the first contract state.
        """

    class ProviderB:
        """
        Alternate mutation provider shape used after in-memory retarget.
        """

    contract = MutationContract(
        spellframe=ProviderA,
        binding_name="Primary",
        late_binding=False,
    )

    class Host:
        """
        Host class carrying a MutationContract default in its constructor.
        """

        def __init__(self, mutant: object = contract) -> None:
            """
            Store the provided mutant object.

            Args:
                mutant:
                    Mutation dependency placeholder or resolved object.

            Returns:
                None.
            """
            self.mutant = mutant

    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether

    spellbook = Spellbook()
    try:
        spell_id = spellbook.bind(
            spell=Host,
            existence=Existence.unique,
            permissions="create",
        )
        spell = _find_spell_by_version_id(spellbook, spell_id)

        requirement = _get_mutation_requirement(spell)
        recovered_contract = requirement.default_value
        signature_contract = inspect.signature(Host.__init__).parameters["mutant"].default

        assert recovered_contract is contract
        assert signature_contract is contract
        _emit("OK_MUTATION_CONTRACT_REFERENCE_SHARED")

        recovered_contract.update_contract(
            spell=recovered_contract.spell,
            spellframe=ProviderB,
            binding_name="Secondary",
            spell_override=recovered_contract.spell_override,
            late_binding=True,
        )

        requirement_after = _get_mutation_requirement(spell)
        recovered_after = requirement_after.default_value
        signature_after = inspect.signature(Host.__init__).parameters["mutant"].default

        assert recovered_after is contract
        assert signature_after is contract
        assert recovered_after is recovered_contract
        assert recovered_after.spellframe is ProviderB
        assert recovered_after.binding_name == "secondary"
        assert recovered_after.late_binding is True
        assert signature_after.spellframe is ProviderB
        assert signature_after.binding_name == "secondary"
        assert signature_after.late_binding is True
        _emit("OK_MUTATION_CONTRACT_UPDATE_STUCK")
    finally:
        spellbook.cleanup()
        Aether._reset_singleton_for_tests()
        aether = Aether()
        Spellbook._aether = aether
        Conduit._aether = aether


if __name__ == "__main__":
    _run_with_timeout(
        "MUTATION_CONTRACT_BIND_REFERENCE",
        _experiment_bind_reference_recovery_and_update,
    )
