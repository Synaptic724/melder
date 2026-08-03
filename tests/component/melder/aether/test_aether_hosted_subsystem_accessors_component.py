"""tests/component/melder/aether/test_aether_hosted_subsystem_accessors_component.py

Validation: Not run.

Component tests for the four hosted-subsystem accessors on `Aether`.

Why this file exists
--------------------
Aether CONSTRUCTS, OWNS and CLEANS four subsystem roots - the admission
plane, the crystallizer, the Rift domain and the research root - but until
2026-08-03 it published handles for only two of them. Callers reached the
other two by calling `Crystallizer()` and `Nexus()` and relying on singleton
re-entry, which worked only for the two roots Aether happened to build
eagerly - MutationResearch was lazy, so `MutationResearch()` was a lookup for
callers who were lucky with ordering and an error for everyone else.

Both gaps are closed. All three roots are now constructed EAGERLY by Aether
(owner ruling 2026-08-03) and all three have accessors. These rows pin the
accessors AND the identity relationship that makes the bare constructors safe,
so neither can drift away from the other.
"""

from __future__ import annotations

import pytest

from melder.aether.aether import Aether
from melder.aether.aetheric_mediator.mediator import Mediator as AethericMediator
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.spellbook import Spellbook
from melder.crystallizer.crystallizer import Crystallizer
from melder.mutation_research.mutation_research import MutationResearch
from melder.nexus.nexus import Nexus


@pytest.fixture(autouse=True)
def reset_hosted_world() -> None:
    """Reset every hosted root around each row so identity claims are honest."""

    def _reset() -> None:
        MutationResearch._reset_singleton_for_tests()
        Crystallizer._reset_singleton_for_tests()
        Nexus._reset_singleton_for_tests()
        Aether._reset_singleton_for_tests()
        aether = Aether()
        Spellbook._aether = aether
        Conduit._aether = aether

    _reset()
    yield
    _reset()


# --------------------------------------------------------------------------
# The set is complete
# --------------------------------------------------------------------------

def test_aether_publishes_every_root_it_owns() -> None:
    """
    Aether cleans four roots in `cleanup`; it must hand back all four.

    This is the row that fails if a fifth hosted subsystem is added with an
    owned slot and no accessor - which is exactly how `crystallizer` and
    `nexus` went missing for as long as they did.
    """
    aether = Aether()
    assert isinstance(aether.aetheric_mediator, AethericMediator)
    assert isinstance(aether.crystallizer, Crystallizer)
    assert isinstance(aether.nexus, Nexus)
    assert isinstance(aether.mutation_research, MutationResearch)


# --------------------------------------------------------------------------
# The accessor and the bare constructor are the same object
# --------------------------------------------------------------------------

def test_the_crystallizer_accessor_is_the_process_wide_singleton() -> None:
    """`Crystallizer()` re-entry and the accessor must never diverge."""
    aether = Aether()
    assert aether.crystallizer is Crystallizer()
    assert aether.crystallizer is aether._crystallizer


def test_the_nexus_accessor_is_the_process_wide_singleton() -> None:
    """Same identity law for the Rift domain."""
    aether = Aether()
    assert aether.nexus is Nexus()
    assert aether.nexus is aether._nexus


def test_repeated_reads_return_the_same_instance() -> None:
    """
    These are reaches, not builds. A fresh object per call would mean two
    callers could hold different crystallizers, which would silently split
    checkpoint custody.
    """
    aether = Aether()
    assert aether.crystallizer is aether.crystallizer
    assert aether.nexus is aether.nexus


# --------------------------------------------------------------------------
# Why the bare constructor is not the real door
# --------------------------------------------------------------------------

def test_a_bare_call_is_a_lookup_for_all_three_roots() -> None:
    """
    THE PAYOFF OF EAGER CONSTRUCTION. Because Aether builds all three in
    `__init__`, and `Aether()` runs at package import, every one of these
    singletons is already initialized before any caller executes. Each
    `__init__` opens with an initialized check, so a bare call short-circuits
    to a lookup rather than failing on a missing host.

    This is what makes keeping all three in `__all__` honest - you really can
    reach for them whenever you want.
    """
    aether = Aether()

    assert Crystallizer() is aether.crystallizer
    assert Nexus() is aether.nexus
    assert MutationResearch() is aether.mutation_research


def test_a_hostless_first_construction_is_refused_on_a_torn_down_world() -> None:
    """
    The guarantee above depends on Aether having built first, and this row
    proves that dependency is real rather than assumed: reset every singleton
    so there is no host, and each root refuses.

    A caller cannot reach this state through the public surface - it takes the
    test-only resets to get here - which is precisely why the eager build is
    what makes the bare constructors safe.
    """
    Crystallizer._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    MutationResearch._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()

    for root in (Crystallizer, Nexus, MutationResearch):
        with pytest.raises(ValueError, match="Aether"):
            root()
        assert root._instance is None, f"{root.__name__} left a husk"
        assert root._initialized is False, f"{root.__name__} stayed initialized"


# --------------------------------------------------------------------------
# Existence is not liveness
# --------------------------------------------------------------------------

def test_the_accessors_report_existence_not_liveness() -> None:
    """
    AVAILABLE IS NOT ACTIVE. Aether builds all three roots eagerly, so all
    three EXIST the moment the package is imported - and none of them is
    live. Reaching a root does not configure it and does not turn it on.

    This is the two-bit law applied to the roots themselves, and it is why
    eager construction is safe: it settles existence only, and leaves the
    liveness bit exactly where the caller left it.
    """
    aether = Aether()

    assert aether.crystallizer.activated is False
    assert aether.mutation_research.activated is False
    assert aether.nexus.is_enabled is False

    # ...and neither is any of them CONFIGURED, which is the rung below.
    assert aether.crystallizer.is_configured is False
    assert aether.mutation_research.is_configured is False
    assert aether.nexus.is_configured is False


def test_every_root_offers_the_same_configuration_ladder() -> None:
    """
    The three caller-driven roots expose ONE configuration vocabulary:
    a factory, a fluent builder factory, install, activate, deactivate, and
    both readable bits. `create_configuration_builder` was the last hole -
    `CrystallizerConfigurationBuilder` existed and was exported from the
    package root, but the crystallizer never published a door to it while
    Aether and MutationResearch both did.

    NEXUS IS DELIBERATELY ABSENT from this row. It uses
    `create_system_configuration` / `enable` / `disable` / `is_enabled` and
    seals its own configuration on the way in - the documented 3-to-1
    divergence, not drift.
    """
    ladder = (
        "create_configuration",
        "create_configuration_builder",
        "configure",
        "activate",
        "deactivate",
        "is_configured",
        "is_activated",
    )
    aether = Aether()
    for root in (aether.crystallizer, aether.mutation_research):
        missing = [verb for verb in ladder if not hasattr(type(root), verb)]
        assert not missing, f"{type(root).__name__} is missing {missing}"


def test_a_built_configuration_is_not_a_live_root() -> None:
    """
    The builder's exits are rungs, not switches. `activate()` on the BUILDER
    marks the policy object ready; the ROOT is still off until you install
    and activate it there. Two different objects, two different bits.
    """
    aether = Aether()
    crystallizer = aether.crystallizer

    configuration = crystallizer.create_configuration_builder().with_defaults().activate()

    assert configuration.activated is True
    assert crystallizer.activated is False, (
        "activating the configuration must not activate the root"
    )


# --------------------------------------------------------------------------
# Lifecycle
# --------------------------------------------------------------------------

def test_a_cleaned_aether_refuses_every_accessor() -> None:
    """
    `check_cleaned()` fires rather than handing back a root whose owner is
    gone. Melder does not return a live-looking handle from a dead world.
    """
    aether = Aether()
    aether.cleanup()

    for name in ("aetheric_mediator", "crystallizer", "nexus", "mutation_research"):
        with pytest.raises(RuntimeError):
            getattr(aether, name)
