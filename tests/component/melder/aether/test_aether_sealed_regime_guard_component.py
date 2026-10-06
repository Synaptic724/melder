"""
Component tests for the sealed spell-id regime guard on Aether (0.2.8209).

WHY THIS EXISTS. The regime (`process_wide_unique_spell_ids`) is sealed when the
first frame is born, and spell ids registered afterwards were allocated under
it. `Aether.configure` used to install ANY later configuration, so a host (or a
second Melder user such as MelderOps) could install a per-frame policy that
`Aether.configuration` then reported while the process kept the process-wide
rule - the same class bound into a second frame still collided. Configure and
activate now refuse that configuration while frames exist.

Contract under test:
    1. after the first frame, a different regime is refused and nothing changes;
    2. after the first frame, the sealed regime is accepted;
    3. before any frame, either regime is accepted and the first frame seals it;
    4. activate refuses an installed configuration changed to another regime;
    5. activate(configuration) refuses a different regime through configure.
"""

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_configuration import AetherConfiguration
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.spellbook import Spellbook


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_regime_guard() -> None:
    """Give each test an Aether with no frames and no configuration."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _birth_a_frame(frame_name: str) -> Spellbook:
    """Bring one frame into existence; constructing a Spellbook on it births it."""
    return Spellbook(aetheric_frame=frame_name)


def _policy(process_wide: bool) -> AetherConfiguration:
    """Return a mutable default Aether configuration with the given regime."""
    configuration = AetherConfiguration().with_defaults()
    configuration.set_process_wide_unique_spell_ids(process_wide)
    return configuration


def test_different_regime_after_the_first_frame_is_refused_and_nothing_changes() -> None:
    """A per-frame policy after the host's first frame is refused; the sealed default stays."""
    aether = Aether()
    _birth_a_frame("host")
    sealed = aether.configuration
    assert sealed is not None and sealed.process_wide_unique_spell_ids is True

    with pytest.raises(RuntimeError, match="spell-id regime is sealed while frames exist"):
        aether.configure(_policy(False))

    assert aether.configuration is sealed
    assert aether.configured is False
    assert aether.configuration.process_wide_unique_spell_ids is True


def test_sealed_regime_after_the_first_frame_is_accepted() -> None:
    """Replacing the policy is still allowed when it keeps the sealed regime."""
    aether = Aether()
    _birth_a_frame("host")
    replacement = _policy(True).with_channel_logger_activation_enabled(False)
    aether.configure(replacement)
    assert aether.configuration is replacement
    assert aether.configured is True


def test_before_any_frame_either_regime_installs_and_the_first_frame_seals_it() -> None:
    """With no frame the guard reads nothing; the first frame seals the caller's choice."""
    aether = Aether()
    per_frame = _policy(False)
    aether.configure(per_frame)
    assert aether.configuration is per_frame
    _birth_a_frame("tenant_a")
    assert per_frame.frozen is True
    assert aether.configuration.process_wide_unique_spell_ids is False
    with pytest.raises(RuntimeError, match="process_wide_unique_spell_ids is False"):
        aether.configure(_policy(True))


def test_activate_refuses_an_installed_configuration_changed_to_another_regime() -> None:
    """A mutable installed configuration edited after configure is caught at activate."""
    aether = Aether()
    _birth_a_frame("host")
    installed = _policy(True)
    aether.configure(installed)
    installed.set_process_wide_unique_spell_ids(False)
    installed.activate()
    with pytest.raises(RuntimeError, match="spell-id regime is sealed while frames exist"):
        aether.activate()
    assert aether.activated is False


def test_activate_with_a_configuration_refuses_a_different_regime() -> None:
    """activate(configuration) installs through configure, so the same refusal applies."""
    aether = Aether()
    _birth_a_frame("host")
    per_frame = _policy(False).activate()
    with pytest.raises(RuntimeError, match="spell-id regime is sealed while frames exist"):
        aether.activate(per_frame)
    assert aether.activated is False
    assert aether.configuration.process_wide_unique_spell_ids is True


def test_matching_activation_after_the_first_frame_still_applies() -> None:
    """The guard is silent for the sealed regime: activation proceeds as before."""
    aether = Aether()
    _birth_a_frame("host")
    aether.activate(_policy(True).activate())
    assert aether.activated is True
