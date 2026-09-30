"""
Component tests for the Nexus active-reconfiguration guard (0.2.8210).

WHY THIS EXISTS. A live Nexus reads its installed policy at every Rift
validation, so replacing the policy of an ACTIVE Nexus changes the rules under
Rifts that already passed them - and `configure` installs the replacement
unfrozen, so it could keep changing afterwards. Crystallizer and
MutationResearch have always refused reconfiguration while active; Nexus
accepted it, which let a second Melder user in the same process (MelderOps)
swap a host's live AR policy without the host knowing. `configure`, and
`activate` handed another configuration, now refuse while Nexus is active.

Contract under test:
    1. configure on an active Nexus raises and the installed policy stays in force;
    2. the refused replacement is left untouched, so it can be installed later;
    3. after deactivate, configure installs the replacement and activate brings it live;
    4. activate with another configuration while active raises and changes nothing;
    5. the guard compares identity: an equal-valued second object is still refused;
    6. activate with the installed configuration, or with none, re-enables as before;
    7. a configured but inactive Nexus still accepts a replacement through either verb.
"""

from typing import Iterator

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.spellbook import Spellbook
from melder.crystallizer.crystallizer import Crystallizer
from melder.mutation_research.mutation_research import MutationResearch
from melder.nexus.configuration.nexus_configuration import NexusConfiguration
from melder.nexus.nexus import Nexus


@pytest.fixture(autouse=True)
def reset_world_for_nexus_guard() -> Iterator[None]:
    """Give each test fresh hosted roots, so every Nexus starts unconfigured and inactive."""

    def _reset() -> None:
        """Reset the hosted roots and rebind the static Aether references."""
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


def _policy(allowed_frame: str) -> NexusConfiguration:
    """Return a mutable default Nexus policy whose Rift targets are limited to one named frame."""
    return NexusConfiguration().with_defaults().with_allowed_target_frame_names((allowed_frame,))


def _live_nexus() -> Nexus:
    """Return the hosted Nexus, activated with a default policy that targets frame 'default'."""
    nexus = Aether().nexus
    nexus.activate(_policy("default"))
    return nexus


def test_configure_on_an_active_nexus_is_refused_and_the_live_policy_stays() -> None:
    """A host's live AR policy cannot be swapped underneath it; the refusal names the fix."""
    nexus = _live_nexus()
    installed = nexus.configuration

    with pytest.raises(RuntimeError, match="Cannot reconfigure Nexus while it is active. Deactivate it first."):
        nexus.configure(_policy("melderops"))

    assert nexus.configuration is installed
    assert nexus.activated is True
    assert nexus.configuration.get_property("allowed_target_frame_names") == ("default",)


def test_a_refused_replacement_is_left_untouched() -> None:
    """The refusal happens before install: the caller's object is neither frozen nor consumed."""
    nexus = _live_nexus()
    replacement = _policy("melderops")

    with pytest.raises(RuntimeError, match="Cannot reconfigure Nexus while it is active"):
        nexus.configure(replacement)

    assert replacement.frozen is False
    assert replacement.activated is False
    assert replacement.get_property("allowed_target_frame_names") == ("melderops",)


def test_after_deactivate_configure_installs_and_activate_brings_it_live() -> None:
    """Deactivating first is the documented remedy; the replacement then goes live as usual."""
    nexus = _live_nexus()
    replacement = _policy("melderops")

    nexus.deactivate()
    nexus.configure(replacement)
    assert nexus.configuration is replacement
    assert replacement.frozen is False

    nexus.activate()
    assert nexus.activated is True
    assert replacement.frozen is True
    assert nexus.configuration.get_property("allowed_target_frame_names") == ("melderops",)


def test_activate_with_another_configuration_while_active_is_refused() -> None:
    """activate(configuration) installs, so it follows the same rule as configure."""
    nexus = _live_nexus()
    installed = nexus.configuration
    replacement = _policy("melderops")

    with pytest.raises(RuntimeError, match="Cannot reconfigure Nexus while it is active. Deactivate it first."):
        nexus.activate(replacement)

    assert nexus.configuration is installed
    assert nexus.activated is True
    assert replacement.frozen is False


def test_an_equal_valued_second_object_is_still_refused_while_active() -> None:
    """The guard compares identity, not values: another object is a replacement even when equal."""
    nexus = _live_nexus()
    twin = _policy("default")
    assert twin.get_configuration_dictionary() == nexus.configuration.get_configuration_dictionary()

    with pytest.raises(RuntimeError, match="Cannot reconfigure Nexus while it is active"):
        nexus.configure(twin)
    with pytest.raises(RuntimeError, match="Cannot reconfigure Nexus while it is active"):
        nexus.activate(twin)


def test_activate_with_the_installed_configuration_or_none_re_enables() -> None:
    """Re-enabling a live Nexus with its own policy stays legal and keeps that policy."""
    nexus = _live_nexus()
    installed = nexus.configuration

    nexus.activate(installed)
    nexus.activate()

    assert nexus.configuration is installed
    assert nexus.activated is True


def test_a_configured_but_inactive_nexus_still_accepts_a_replacement() -> None:
    """The guard is about liveness: an installed policy that is not in force can be replaced."""
    nexus = Aether().nexus
    nexus.configure(_policy("default"))
    replacement = _policy("melderops")

    nexus.configure(replacement)
    assert nexus.configuration is replacement

    final = _policy("tenant")
    nexus.activate(final)
    assert nexus.configuration is final
    assert nexus.activated is True
    assert nexus.configuration.get_property("allowed_target_frame_names") == ("tenant",)
