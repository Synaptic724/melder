"""Frame and Spellbook configurations report their freeze state and target frame through public reads.

Hosts compare a supplied configuration against the frame it will be used in and check whether a posture or a
rich configuration has already been settled. Until 0.2.8208 those facts were readable only as `_frozen` and
`_aether_frame`; `AethericFrameConfiguration.frozen`, `SpellbookConfiguration.frozen` and
`SpellbookConfiguration.aether_frame` now answer them without changing either configuration.
"""

import pytest

from melder.aether.aetheric_frame.aetheric_frame_configuration import AethericFrameConfiguration
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.configuration.system_state import SystemState


def _posture() -> AethericFrameConfiguration:
    """Build one automatic, unfrozen frame posture with no origin."""
    return AethericFrameConfiguration(
        origin_spellbook_id=None,
        system_state=SystemState.automatic,
        ai_native_enabled=False,
        rift_enabled=False,
    )


def test_spellbook_configuration_reports_the_frame_it_was_built_for() -> None:
    """The target frame is the constructor's `aether_frame`, "default" when omitted."""
    assert SpellbookConfiguration().aether_frame == "default"
    assert SpellbookConfiguration(aether_frame="ops").aether_frame == "ops"


def test_spellbook_configuration_frozen_is_false_until_frozen() -> None:
    """`frozen` reads False while mutable and True once `freeze()` succeeds."""
    configuration = SpellbookConfiguration().with_defaults()
    assert configuration.frozen is False
    configuration.freeze()
    assert configuration.frozen is True


def test_spellbook_configuration_finalize_reports_frozen() -> None:
    """`finalize()` freezes, and the read reflects it."""
    configuration = SpellbookConfiguration().with_defaults().finalize()
    assert configuration.frozen is True


def test_spellbook_configuration_reads_change_nothing() -> None:
    """Reading the accessors leaves the configuration mutable."""
    configuration = SpellbookConfiguration(aether_frame="ops").with_defaults()
    assert configuration.frozen is False
    assert configuration.aether_frame == "ops"
    configuration.with_phase_scheduler_workers(2)
    assert configuration.frozen is False


def test_spellbook_configuration_accessors_raise_once_cleaned() -> None:
    """A cleaned configuration refuses both reads."""
    configuration = SpellbookConfiguration(aether_frame="ops")
    configuration.cleanup()
    with pytest.raises(RuntimeError):
        _ = configuration.frozen
    with pytest.raises(RuntimeError):
        _ = configuration.aether_frame


def test_frame_posture_frozen_is_false_until_frozen() -> None:
    """A posture reads unfrozen until `freeze()`, then frozen; its builders refuse from then on."""
    posture = _posture()
    assert posture.frozen is False
    posture.freeze()
    assert posture.frozen is True
    with pytest.raises(RuntimeError):
        posture.with_rift_enabled(True)


def test_frame_posture_frozen_raises_once_cleaned() -> None:
    """A cleaned posture refuses the read."""
    posture = _posture()
    posture.cleanup()
    with pytest.raises(RuntimeError):
        _ = posture.frozen
