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


def _build_spellbook() -> Spellbook:
    """
    Build one dynamic spellbook with both binds, stopping before conjure.

    Returns:
        Spellbook: Owning spellbook with both spells bound, not yet conjured.
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
    return spellbook


def test_unique_root_depends_on_spellspace_is_rejected_at_conjure() -> None:
    """
    Measure current behavior for a broad-to-narrow scope dependency.

    Contract:
        - A `unique` root depending on a `unique_per_spell_space` spell is a
          scope-ordering violation (a broad lifetime depending on a narrower
          spellspace scope).
        - The violation is caught at compile time: `conjure()` raises
          `SpellbookValidationError` naming `_UniqueRoot`, rather than
          deferring the failure to the first `meld` at the conduit-facing
          spellspace request gate.
    """

    spellbook = _build_spellbook()
    with pytest.raises(SpellbookValidationError, match="_UniqueRoot"):
        spellbook.conjure(dynamic=True, name="root")
