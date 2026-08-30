"""tests/integration/melder/conduit/test_conduit_integration_scope_ordering_spellspace.py

Validation: Not run (authored on a Python 3.10 sandbox where melder does not
import; this suite targets the 3.14t free-threaded build).

Invariant under test -- captive-dependency / scope ordering for spellspace:
    A longer-lived spell must NOT be allowed to depend on a request-local
    ``unique_per_spell_space`` spell. If a ``unique`` (frame singleton),
    ``unique_per_conduit``, ``unique_per_conduit_lineage``, or
    ``unique_per_conduit_cluster`` instance captures a spellspace-scoped
    dependency, that captured instance is cleared when the spellspace closes,
    leaving the longer-lived holder with a dangling reference. That is a captive
    dependency and must be rejected at build (conjure) time.

    ``ScopeOrderingStrategy`` (Phase 6) ranks scopes ``unique=0 .. spellspace=4``
    and is written to emit a ``scope_ordering_violation`` ERROR for exactly these
    broad->narrow edges. These tests assert that violation is enforced as a hard
    conjure failure (``SpellbookValidationError``).

    NOTE ON CURRENT BEHAVIOR: the existing experiment
    (tests/experimentation/test_unique_depends_on_spellspace_experiment.py)
    shows ``unique``->spellspace currently lets conjure SUCCEED and only trips a
    meld-time "must be built from a spellspace" ``RuntimeError`` -- i.e. the
    Phase-6 violation is not enforced at conjure. The four rejection tests below
    are therefore expected to FAIL on the current runtime until the guard is
    promoted to a hard conjure failure; that is the intended signal.

    The allowed direction (a spellspace spell depending on a broader spell) is
    covered as a positive control and is expected to pass.
"""
from __future__ import annotations

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.nexus import Nexus
from melder.utilities.custom_exceptions.spellbook_validation_error import (
    SpellbookValidationError,
)
from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)

_SPELLSPACE = Existence.unique_per_spell_space
_UNIQUE = Existence.unique
_UPC = Existence.unique_per_conduit
_LINEAGE = Existence.unique_per_conduit_lineage
_CLUSTER = Existence.unique_per_conduit_cluster


@pytest.fixture(autouse=True)
def reset_singletons_for_scope_ordering() -> None:
    """Reset Nexus + Aether around each test for singleton isolation."""

    def _reset() -> None:
        Nexus._reset_singleton_for_tests()
        Aether._reset_singleton_for_tests()
        aether = Aether()
        Spellbook._aether = aether
        Conduit._aether = aether

    _reset()
    yield
    _reset()


class _SpellspaceLeaf:
    """Request-local dependency bound as ``unique_per_spell_space``."""

    def __init__(self) -> None:
        """Construct one request-local leaf."""
        pass


class _BroadParent:
    """Longer-lived parent that (illegally) depends on a spellspace leaf."""

    def __init__(self, dep: _SpellspaceLeaf) -> None:
        """Store the injected request-local dependency."""
        self.dep = dep


class _UniqueLeaf:
    """Frame-singleton dependency for the allowed (positive-control) direction."""

    def __init__(self) -> None:
        """Construct one frame-singleton leaf."""
        pass


class _SpellspaceParent:
    """Request-local parent that legally depends on a broader ``unique`` leaf."""

    def __init__(self, dep: _UniqueLeaf) -> None:
        """Store the injected broader dependency."""
        self.dep = dep


def _book(tag: str) -> Spellbook:
    """Build one dynamic spellbook on its own frame for scope-ordering tests."""
    frame = f"scope-spellspace-{tag}"
    # The configuration's frame name MUST match the Spellbook's aetheric_frame;
    # SpellbookConfiguration.__init__(aether_frame="default") otherwise trips the
    # "name does not match the aetheric frame" guard before conjure runs.
    configuration = SpellbookConfiguration(frame)
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return Spellbook(
        aetheric_frame=frame,
        configuration=configuration,
    )


def _assert_broad_parent_rejected(tag: str, parent_existence: Existence) -> None:
    """
    Bind a spellspace leaf + a broad parent depending on it; conjure must reject.

    The broad->spellspace dependency edge is a captive dependency and must fail
    at build time with ``SpellbookValidationError``.
    """
    book = _book(tag)
    book.bind(spell=_SpellspaceLeaf, existence=_SPELLSPACE, permissions="create")
    book.bind(spell=_BroadParent, existence=parent_existence, permissions="create")
    try:
        with pytest.raises(SpellbookValidationError):
            book.conjure(dynamic=True, name="root")
    finally:
        book.cleanup()


def test_unique_cannot_depend_on_spellspace() -> None:
    """A ``unique`` frame singleton capturing a spellspace instance is rejected."""
    _assert_broad_parent_rejected("unique", _UNIQUE)


def test_unique_per_conduit_cannot_depend_on_spellspace() -> None:
    """A ``unique_per_conduit`` capturing a spellspace instance is rejected."""
    _assert_broad_parent_rejected("upc", _UPC)


def test_lineage_cannot_depend_on_spellspace() -> None:
    """A ``unique_per_conduit_lineage`` capturing a spellspace instance is rejected."""
    _assert_broad_parent_rejected("lineage", _LINEAGE)


def test_cluster_cannot_depend_on_spellspace() -> None:
    """A ``unique_per_conduit_cluster`` capturing a spellspace instance is rejected."""
    _assert_broad_parent_rejected("cluster", _CLUSTER)


def test_spellspace_may_depend_on_unique_positive_control() -> None:
    """
    Allowed direction (positive control): a ``unique_per_spell_space`` parent may
    depend on a broader ``unique`` leaf, and resolves the shared singleton.
    """
    book = _book("posctl")
    leaf_id = book.bind(spell=_UniqueLeaf, existence=_UNIQUE, permissions="create")
    parent_id = book.bind(
        spell=_SpellspaceParent,
        existence=_SPELLSPACE,
        permissions="create",
    )
    root = book.conjure(dynamic=True, name="root")
    try:
        root_leaf = root.meld(spell_id=leaf_id)
        with root.enter_spellspace() as space:
            parent = space.meld(spell_id=parent_id)
            assert isinstance(parent, _SpellspaceParent)
            assert parent.dep is root_leaf, (
                "spellspace parent must resolve the shared unique singleton"
            )
    finally:
        root.permanent_cleanup()
        book.cleanup()
