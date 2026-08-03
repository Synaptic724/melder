"""tests/component/melder/aether/test_nexus_configuration_ladder_component.py

Validation: Not run.

Component tests for the Nexus configuration ladder brought into line with
Crystallizer and MutationResearch (owner ruling 2026-08-03).

Why this file exists
--------------------
Nexus was the one hosted root of three that spoke a different configuration
language. It had `create_system_configuration` / `enable` / `disable` /
`is_enabled`, no builder class at all, and - the part that actually mattered -
its configuration object carried NO ACTIVATION RUNG. Crystallizer and
MutationResearch configurations have always had `activate()` and `activated`,
so their roots can be handed an already-settled policy object. Nexus could
not: `enable()` sealed the configuration on the caller's behalf, which is why
it was the only subsystem where a caller could not settle policy before
installing it.

Three things closed that gap, and these rows pin all three:
  * `NexusConfiguration.activate()` / `.activated` - the missing rung.
  * `NexusConfigurationBuilder` - the missing one-shot ownership helper.
  * `create_configuration` / `configure` / `activate` / `deactivate` /
    `activated` / `is_activated` / `configured` on the root.

THE OLD VERBS ARE GONE, not aliased (owner ruling: a rename, so nobody has
two names for one thing to choose between). All 298 call sites across src,
tests, examples and benchmarks were migrated in the same change.
"""

from __future__ import annotations

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.spellbook import Spellbook
from melder.crystallizer.crystallizer import Crystallizer
from melder.mutation_research.mutation_research import MutationResearch
from melder.nexus.configuration.nexus_configuration import NexusConfiguration
from melder.nexus.configuration.nexus_configuration_builder import (
    NexusConfigurationBuilder,
)
from melder.nexus.nexus import Nexus


@pytest.fixture(autouse=True)
def reset_world() -> None:
    """Reset every hosted root around each row."""

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
# The missing rung on the configuration object
# --------------------------------------------------------------------------

def test_a_fresh_configuration_is_neither_frozen_nor_activated() -> None:
    """Both bits start False. Authoring has not begun."""
    configuration = NexusConfiguration()

    assert configuration.frozen is False
    assert configuration.activated is False


def test_finalize_freezes_without_activating() -> None:
    """
    THE RUNG THAT DID NOT EXIST. `finalize()` settles the values; it does not
    declare them ready. A frozen-but-unactivated configuration is the normal
    state between authoring and installation, and Nexus had no way to express
    it before - which is why `enable()` had to seal on the caller's behalf.
    """
    configuration = NexusConfiguration().with_defaults()
    configuration.finalize()

    assert configuration.frozen is True
    assert configuration.activated is False


def test_activate_freezes_and_marks_ready() -> None:
    """`activate()` is finalize plus the readiness flag, never one or other."""
    configuration = NexusConfiguration().with_defaults()

    assert configuration.activate() is configuration

    assert configuration.frozen is True
    assert configuration.activated is True


def test_activating_a_configuration_is_idempotent() -> None:
    """Freeze is idempotent and the flag is a plain set with no side effect."""
    configuration = NexusConfiguration().with_defaults().activate()
    configuration.activate()

    assert configuration.activated is True


def test_activating_the_configuration_does_not_enable_the_nexus() -> None:
    """
    TWO OBJECTS, TWO BITS. Marking the policy ready says nothing about the
    root. This is the distinction the whole alignment exists to make legible.
    """
    aether = Aether()
    configuration = aether.nexus.create_configuration().with_defaults().activate()

    assert configuration.activated is True
    assert aether.nexus.is_activated is False
    assert aether.nexus.activated is False


# --------------------------------------------------------------------------
# The missing builder
# --------------------------------------------------------------------------

def test_the_root_hands_over_a_builder() -> None:
    """Nexus is no longer the root that makes you construct policy yourself."""
    builder = Aether().nexus.create_configuration_builder()

    assert isinstance(builder, NexusConfigurationBuilder)


def test_the_builder_exits_are_three_distinct_rungs() -> None:
    """
    `build()` mutable, `finalize()` frozen, `activate()` ready - the same
    three-rung contract the crystallizer builder has always had.
    """
    mutable = NexusConfigurationBuilder().with_defaults().build()
    assert mutable.frozen is False
    assert mutable.activated is False

    frozen = NexusConfigurationBuilder().with_defaults().finalize()
    assert frozen.frozen is True
    assert frozen.activated is False

    ready = NexusConfigurationBuilder().with_defaults().activate()
    assert ready.frozen is True
    assert ready.activated is True


def test_the_builder_is_one_shot() -> None:
    """
    Handoff consumes the builder. A second exit must refuse rather than hand
    the same configuration to two owners.
    """
    builder = NexusConfigurationBuilder().with_defaults()
    builder.build()

    with pytest.raises(RuntimeError):
        builder.build()


def test_the_builder_chains_the_common_knob() -> None:
    """`with_rift_creation_enabled` is the knob nearly every caller sets."""
    configuration = (
        NexusConfigurationBuilder()
        .with_defaults()
        .with_rift_creation_enabled(True)
        .activate()
    )

    assert configuration.get_property("allow_rift_creation") is True


# --------------------------------------------------------------------------
# The root verbs
# --------------------------------------------------------------------------

def test_configure_installs_without_settling() -> None:
    """
    INSTALL AND SETTLE ARE SEPARATE NOW. `configure()` accepts a still-mutable
    configuration and does not freeze it - the separation `enable()` never
    offered, because it always sealed on the way in.
    """
    nexus = Aether().nexus
    configuration = nexus.create_configuration().with_defaults()

    nexus.configure(configuration)

    assert nexus.is_configured is True
    assert configuration.frozen is False
    assert nexus.is_activated is False


def test_configure_type_checks_its_argument() -> None:
    """A non-configuration raises rather than being stored and failing later."""
    nexus = Aether().nexus

    with pytest.raises(TypeError):
        nexus.configure("not a configuration")


def test_activate_brings_the_root_live() -> None:
    """
    `activate()` is the real verb now - not a delegate. Both spellings of the
    liveness bit report it, matching Crystallizer and MutationResearch which
    each carry `activated` and `is_activated`.
    """
    nexus = Aether().nexus
    nexus.activate(nexus.create_configuration().with_defaults())

    assert nexus.activated is True
    assert nexus.is_activated is True
    assert nexus.configured is True
    assert nexus.is_configured is True


def test_deactivate_drops_liveness_and_keeps_configuration() -> None:
    """
    The two-bit law on the root: `deactivate()` turns it off and leaves the
    installed policy in place. Liveness drops, existence does not.
    """
    nexus = Aether().nexus
    nexus.activate(nexus.create_configuration().with_defaults())

    nexus.deactivate()

    assert nexus.activated is False
    assert nexus.is_configured is True


def test_the_old_verbs_are_gone() -> None:
    """
    RENAME, NOT ALIAS. `enable` / `disable` / `is_enabled` /
    `create_system_configuration` were removed outright so there is exactly
    one name per concept. This row goes red if any of them creep back as a
    compatibility shim.
    """
    nexus = Aether().nexus

    for retired in ("enable", "disable", "is_enabled", "create_system_configuration"):
        assert not hasattr(nexus, retired), (
            f"{retired} came back - the rename was supposed to be total"
        )
