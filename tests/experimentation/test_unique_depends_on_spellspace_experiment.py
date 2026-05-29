"""
Empirically probe a broad-lived spell depending on a spellspace-scoped spell.

Purpose:
    Capture current runtime behavior for a `unique` root spell that depends on
    a `unique_per_spell_space` dependency, using the existing runtime/compiler
    pattern instead of reasoning from intent.

This file is an experimentation surface, not production runtime code.
"""

from typing import Generator

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.utilities.custom_exceptions.spellbook_validation_error import (
    SpellbookValidationError,
)
from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)


class _SpellspaceDependency:
    """
    Minimal spellspace-scoped dependency for the experiment.

    Contract:
        - Zero-arg constructor isolates scope behavior from deeper DI shape.
    """

    def __init__(self) -> None:
        """Construct one dependency instance."""
        return None


class _UniqueRoot:
    """
    Broad-lived root that depends on the spellspace-scoped dependency.

    Contract:
        - Constructor shape is intentionally minimal: one required dependency.
    """

    def __init__(self, dep: _SpellspaceDependency) -> None:
        """Store the injected dependency."""
        self.dep = dep


def _reset_runtime_singletons() -> None:
    """
    Reset singleton runtime surfaces used by the experiment.

    Contract:
        - Replaces the process-wide Aether singleton.
        - Rebinds Spellbook and Conduit class-level Aether handles.
    """

    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


@pytest.fixture(autouse=True)
def _fresh_runtime() -> Generator[None, None, None]:
    """
    Reset runtime singletons before and after each experiment.
    """

    _reset_runtime_singletons()
    yield
    _reset_runtime_singletons()


def _build_runtime() -> tuple[Spellbook, Conduit]:
    """
    Build one dynamic runtime for the experiment.

    Returns:
        tuple[Spellbook, Conduit]:
            Owning spellbook and rooted conduit.
    """

    configuration = SpellbookConfiguration("unique-depends-on-spellspace-experiment")
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook = Spellbook(
        aetheric_frame="unique-depends-on-spellspace-experiment",
        configuration=configuration,
    )
    spellbook.bind(
        spell=_SpellspaceDependency,
        existence=Existence.unique_per_spell_space,
        permissions="create",
    )
    spellbook.bind(
        spell=_UniqueRoot,
        existence=Existence.unique,
        permissions="create",
    )
    conduit = spellbook.conjure(automatic=False, name="root")
    return spellbook, conduit


def test_unique_root_depends_on_spellspace_without_active_scope() -> None:
    """
    Measure current behavior with no active spellspace.

    Contract:
        - `conjure()` succeeds.
        - The first `meld(_UniqueRoot)` fails with SpellbookValidationError.
        - The current behavior is not a direct SpellSpaceScopeError here.
    """

    _spellbook, conduit = _build_runtime()
    try:
        with pytest.raises(SpellbookValidationError, match="UniqueRoot"):
            conduit.meld(spell=_UniqueRoot)
    finally:
        conduit.cleanup()


def test_unique_root_depends_on_spellspace_even_with_active_scope() -> None:
    """
    Measure current behavior with an active spellspace on the caller conduit.

    Contract:
        - Entering a spellspace does not make the broad-lived root meldable.
        - The first `meld(_UniqueRoot)` still fails with SpellbookValidationError.
    """

    _spellbook, conduit = _build_runtime()
    try:
        with conduit.enter_spellspace():
            with pytest.raises(SpellbookValidationError, match="UniqueRoot"):
                conduit.meld(spell=_UniqueRoot)
    finally:
        conduit.cleanup()
