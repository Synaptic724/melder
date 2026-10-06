"""
Component tests for `Aether.process_wide_unique_spell_ids` (0.2.8213).

WHY THIS EXISTS. The spell-id regime is sealed when the first frame is born, and until now it was readable only
through private state: `Aether.configuration` may be a policy the next first frame will seal, or one a first frame
already sealed, and nothing said which. The crystallizer records the regime in the Aether twin and keys spell custody
by it, and a restore must know whether the live regime can still change, so the root answers the question itself.

Contract under test:
    1. a fresh Aether (no configuration, no frame) answers True;
    2. before any frame, the answer follows the installed configuration;
    3. the first frame seals the answer;
    4. a frame born without a configuration seals process-wide ids;
    5. a cleaned Aether refuses the read.
"""

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_configuration import AetherConfiguration
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.spellbook import Spellbook


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_regime_property() -> None:
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


def _policy(process_wide: bool) -> AetherConfiguration:
    """Return a mutable default Aether configuration with the given regime."""
    configuration = AetherConfiguration().with_defaults()
    configuration.set_process_wide_unique_spell_ids(process_wide)
    return configuration


def test_fresh_aether_reports_process_wide_ids() -> None:
    """Nothing installed and no frame: the default regime (process-wide) is in force."""
    aether = Aether()
    assert aether.configuration is None
    assert aether.list_frame_names() == ()
    assert aether.process_wide_unique_spell_ids is True


def test_before_any_frame_the_answer_follows_the_installed_configuration() -> None:
    """The next first frame seals the installed policy, so that policy's regime is the answer, and may still change."""
    aether = Aether()
    aether.configure(_policy(False))
    assert aether.process_wide_unique_spell_ids is False
    aether.configure(_policy(True))
    assert aether.process_wide_unique_spell_ids is True


def test_the_first_frame_seals_the_answer() -> None:
    """A per-frame policy installed before the first frame stays the answer once a frame exists."""
    aether = Aether()
    aether.configure(_policy(False))
    Spellbook(aetheric_frame="tenant_a")
    assert "tenant_a" in aether.list_frame_names()
    assert aether.process_wide_unique_spell_ids is False
    with pytest.raises(RuntimeError, match="spell-id regime is sealed while frames exist"):
        aether.configure(_policy(True))
    assert aether.process_wide_unique_spell_ids is False


def test_a_frame_born_without_configuration_seals_process_wide_ids() -> None:
    """The first frame installs frozen defaults without configuring the root; the answer is True."""
    aether = Aether()
    Spellbook(aetheric_frame="host")
    assert aether.configured is False
    assert aether.process_wide_unique_spell_ids is True


def test_a_cleaned_aether_refuses_the_read() -> None:
    """A torn-down root has no regime in force; reading it raises like every other guarded root read."""
    aether = Aether()
    aether.cleanup()
    with pytest.raises(RuntimeError):
        _ = aether.process_wide_unique_spell_ids
