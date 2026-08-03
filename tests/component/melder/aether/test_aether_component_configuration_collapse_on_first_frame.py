"""
Component tests for the Aether configuration COLLAPSE at first frame birth.

WHY THIS EXISTS. Frames are LAZY - `import melder` creates zero frames (owner
ruling 2026-07-11) - so nothing forces `configure()` to happen before a frame
exists. Without a collapse, a configuration installed later would change the
regime under frames already registered under the old one, and the process would
hold spell_ids allocated by two different rules with nothing able to say which
applies.

`Aether._collapse_configuration_on_first_frame` closes that: at the birth of the
FIRST frame, inside `_ensure_frame`'s lock hold and before any frame is fetched
or created, it installs defaults if nothing was configured, seals the regime into
the plain bool `_process_wide_unique_spell_ids`, and FREEZES the configuration.

The four properties below are the whole contract, and none of them were covered
when the collapse was written:
    1. unconfigured -> defaults appear, sealed and frozen;
    2. configured first -> the CALLER'S choice is what gets sealed;
    3. it happens ONCE - a later configuration cannot re-collapse;
    4. the seal survives as a refusal, not just a value.

Validation: Not run.
"""

from typing import Any

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_configuration import AetherConfiguration
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.spellbook import Spellbook


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_collapse() -> None:
    """
    Purpose:
        Give each test an Aether with NO frames and NO configuration, which is
        the only state in which a collapse can be observed happening.
    Returns:
        None.
    """
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
    """
    Purpose:
        Bring one frame into existence. Frames are lazy, so constructing a
        Spellbook on a named frame is what births it.
    Args:
        frame_name: The aetheric frame to bring into existence.
    Returns:
        Spellbook: The Spellbook whose construction created the frame.
    """
    spellbook = Spellbook(aetheric_frame=frame_name)
    spellbook.get_configuration().set_property(
        "phase_scheduler_workers_per_spellbook", 1
    )
    return spellbook


def test_component_no_frames_means_no_collapse_has_happened_yet() -> None:
    """
    Purpose:
        PRECONDITION FOR EVERY OTHER TEST HERE. Establish that a fresh Aether has
        collapsed nothing, so the assertions below are observing the collapse and
        not a state that was already true.
    Contract:
        - `import melder` creates zero frames, therefore zero collapses.
        - The bool still carries its `__init__` default, which is the same value
          the collapse would seal - so ONLY the frozen configuration distinguishes
          "collapsed" from "not yet collapsed".
    Returns:
        None.
    Raises:
        AssertionError: If a fresh Aether arrives pre-configured.
    """
    aether = Spellbook._aether

    assert aether._configuration is None, (
        "a fresh Aether must carry no configuration - if it does, the collapse "
        "already ran and every test in this module is observing the wrong thing"
    )
    assert aether._process_wide_unique_spell_ids is True, (
        "the bool must carry the documented default from __init__, before any "
        "configuration or frame exists"
    )


def test_component_first_frame_installs_and_freezes_defaults() -> None:
    """
    Purpose:
        The unconfigured path: a frame is born with nothing configured, and the
        collapse must supply the documented defaults rather than leaving the
        world unsealed.
    Contract:
        - A configuration exists afterwards where none existed before.
        - It is FROZEN, so nothing can change the regime under a live world.
        - The bool matches what was sealed.
    Returns:
        None.
    Raises:
        AssertionError: If the frame is born without a sealed configuration.
    """
    aether = Spellbook._aether
    assert aether._configuration is None, "precondition: unconfigured"

    _birth_a_frame("collapse-default")

    assert aether._configuration is not None, (
        "the first frame was born without collapsing the configuration - the "
        "regime is now unsealed under a live frame"
    )
    assert aether._process_wide_unique_spell_ids is True

    with pytest.raises(RuntimeError):
        aether._configuration.set_process_wide_unique_spell_ids(False)


def test_component_collapse_seals_the_callers_choice_not_the_default() -> None:
    """
    Purpose:
        THE CASE THAT MATTERS MOST. An explicitly configured Aether must keep what
        the caller installed. A collapse that overwrote it would silently discard
        a deliberate opt-out.
    Contract:
        - Configuration installed BEFORE any frame exists is the one that gets
          sealed, object identity included.
        - The bool reflects the caller's value, not the default.
    Returns:
        None.
    Raises:
        AssertionError: If the caller's configuration is replaced or ignored.
    """
    aether = Spellbook._aether
    configuration = AetherConfiguration().with_defaults()
    configuration.set_process_wide_unique_spell_ids(False)
    aether._configuration = configuration

    _birth_a_frame("collapse-explicit")

    assert aether._configuration is configuration, (
        "the collapse replaced the caller's configuration object instead of "
        "sealing it"
    )
    assert aether._process_wide_unique_spell_ids is False, (
        "the caller opted OUT of process-wide uniqueness and the collapse sealed "
        "the default anyway"
    )


def test_component_a_later_configuration_cannot_re_collapse() -> None:
    """
    Purpose:
        THE SEAL. Once a frame exists the regime is fixed for the process, so a
        configuration installed afterwards must be ignored - otherwise ids
        allocated under the first rule and the second sit in one process with
        nothing able to say which applies.
    Contract:
        - Birth a frame (collapse runs, seals True).
        - Install a NEW, unfrozen configuration saying False.
        - Birth a SECOND frame - the collapse must not run again.
        - The bool still reads True, and the late configuration is left unfrozen,
          which is the evidence the collapse never touched it.
    Returns:
        None.
    Raises:
        AssertionError: If the regime changes after the world has started.
    """
    aether = Spellbook._aether
    _birth_a_frame("collapse-sealed-first")
    assert aether._process_wide_unique_spell_ids is True

    late: Any = AetherConfiguration().with_defaults()
    late.set_process_wide_unique_spell_ids(False)
    aether._configuration = late

    _birth_a_frame("collapse-sealed-second")

    assert aether._process_wide_unique_spell_ids is True, (
        "a configuration installed AFTER the first frame changed the regime - "
        "frames now disagree about whether a spell_id is unique per process"
    )
    assert late.process_wide_unique_spell_ids is False, (
        "the late configuration should be untouched - the collapse must not "
        "have read it at all"
    )
    with pytest.raises(TypeError):
        late.set_process_wide_unique_spell_ids("still mutable")


def test_component_collapse_never_blocks_a_frame_from_being_born() -> None:
    """
    Purpose:
        The collapse is a seal, not a gate. A failure to collapse must not stop a
        frame existing - the bool already carries the same default, so behaviour
        is identical either way and only the freeze is lost.
    Contract:
        - A configuration whose regime read RAISES must not prevent frame birth.
        - The bool keeps its prior value rather than being corrupted.
    Returns:
        None.
    Raises:
        AssertionError: If a bad configuration takes the whole world down.
    """
    aether = Spellbook._aether

    # A drifted value: the defensive property raises TypeError on READ, which is
    # exactly what the collapse must swallow rather than propagate.
    tampered = AetherConfiguration().with_defaults()
    tampered._properties["process_wide_unique_spell_ids"] = "true"
    aether._configuration = tampered

    spellbook = _birth_a_frame("collapse-tolerant")

    assert spellbook is not None, (
        "a configuration that cannot be read took down frame creation; the "
        "collapse is documented as never raising"
    )
    assert aether._process_wide_unique_spell_ids is True, (
        "a failed collapse must leave the bool at its __init__ default, not "
        "half-write it"
    )
