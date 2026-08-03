"""tests/component/melder/aether/test_configure_aether_frame_posture_component.py

Validation: Not run.

Component tests for `Spellbook.configure_aether_frame` as the ONE public door
onto a frame's posture.

Why this file exists
--------------------
`AethericFrameConfiguration` is created and retained by the spellbook and is
never handed to the caller, so a posture knob that is not a parameter of
`configure_aether_frame` is a knob NO PUBLIC CALLER CAN REACH. The door
previously carried two of the fourteen `with_*` builders, which left
`rift_enabled` and `ai_native_enabled` unreachable from `import melder` - and
those two are exactly what `Nexus._validate_target_frame_runtime_requirements`
demands before a Rift may engage an Aether frame.

The tests below are grouped by the guarantee they defend:
  * COVERAGE   - every builder has a parameter and the parameter lands.
  * ORDERING   - `system_state` is applied before `ai_native`, deliberately.
  * OMISSION   - `None` means "do not touch", never "reset to default".
  * REACH      - the posture written here satisfies the real AR gate.
  * LIFECYCLE  - frozen posture and cleaned book refuse.
"""

from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from melder.aether.aether import Aether
from melder.aether.aetheric_frame.aetheric_frame_configuration import (
    AethericFrameConfiguration,
)
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.system_state import SystemState
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.configuration.rift_space_type import RiftSpaceType
from melder.nexus.nexus import Nexus


@pytest.fixture(autouse=True)
def reset_singletons_for_frame_posture() -> None:
    """Reset Nexus + Aether around each test so frame postures never leak."""

    def _reset() -> None:
        Nexus._reset_singleton_for_tests()
        Aether._reset_singleton_for_tests()
        aether = Aether()
        Spellbook._aether = aether
        Conduit._aether = aether

    _reset()
    yield
    _reset()


class _Service:
    def __init__(self) -> None:
        pass


def _book(frame_name: str) -> Spellbook:
    """Build a bound spellbook on its own frame, so postures stay isolated."""
    book = Spellbook(frame_name)
    # binding_name keeps each frame's spell_id distinct - the frame itself is not
    # in the bind-time fingerprint, so it cannot separate them under process-wide
    # uniqueness.
    book.bind(spell=_Service, existence="unique", binding_name=frame_name)
    return book


def _posture(frame_name: str) -> AethericFrameConfiguration:
    """Read back the live frame-owned posture the door wrote through."""
    configuration = Aether()._get_aetheric_frame_configuration(frame_name)
    if configuration is None:
        raise AssertionError(f"frame '{frame_name}' has no posture")
    return configuration


# --------------------------------------------------------------------------
# COVERAGE
# --------------------------------------------------------------------------

def test_every_posture_builder_has_a_parameter_on_the_public_door() -> None:
    """
    The door must stay total.

    A `with_*` builder added to `AethericFrameConfiguration` without a matching
    parameter here is a silently unreachable capability - which is the exact
    defect this file was written for. Failing this test is the signal to widen
    the door, not to amend the expectation.
    """
    builders = {
        name[len("with_"):]
        for name, _ in inspect.getmembers(AethericFrameConfiguration, inspect.isfunction)
        if name.startswith("with_") and name != "with_defaults"
    }
    parameters = set(
        inspect.signature(Spellbook.configure_aether_frame).parameters
    )
    unreachable = builders - parameters
    assert not unreachable, (
        f"posture knobs with no public door: {sorted(unreachable)}"
    )


def test_every_boolean_posture_knob_lands_on_the_frame() -> None:
    """Each toggle passed through the door is readable on the live posture."""
    book = _book("cover-bools")
    book.configure_aether_frame(
        system_state="dynamic",
        disposal=None,
        disposal_method_names=None,
        ai_native=True,
        rift_enabled=True,
        shared_framewide_spellbook_configuration=True,
        system_caching_enabled=True,
        disable_all_transactions_after_conjure=True,
        disable_mutations=True,
        disable_linking=True,
        disable_bind=True,
        disable_conduit_cluster=True,
        disable_transfer_of_ownership=True,
        disable_contract_mutation=True,
    )
    posture = _posture("cover-bools")
    assert posture.system_state is SystemState.dynamic
    assert posture.ai_native_enabled is True
    assert posture.rift_enabled is True
    assert posture.shared_framewide_spellbook_configuration is True
    assert posture.system_caching_enabled is True
    assert posture.disable_all_transactions_after_conjure is True
    assert posture.disable_mutations is True
    assert posture.disable_linking is True
    assert posture.disable_bind is True
    assert posture.disable_conduit_cluster is True
    assert posture.disable_transfer_of_ownership is True
    assert posture.disable_contract_mutation is True


def test_non_boolean_posture_knobs_land_on_the_frame() -> None:
    """
    The two knobs that are not toggles carry their values through. The cache
    root is a RELATIVE fragment resolved against the melder package root, so
    the value asserted here is a fragment and not a filesystem location.
    """
    book = _book("cover-values")
    book.configure_aether_frame(
        system_state=None,
        disposal=None,
        disposal_method_names=None,
        system_cache_root_path=Path("posture_cache"),
        max_transaction_wait_time_in_seconds=12.5,
    )
    posture = _posture("cover-values")
    assert posture.system_cache_root_path == Path("posture_cache")
    assert posture.max_transaction_wait_time_in_seconds == 12.5


def test_system_cache_root_path_accepts_a_string() -> None:
    """`Union[str, Path]` is truthful: a plain string is accepted and coerced."""
    book = _book("cover-str-path")
    book.configure_aether_frame(
        system_state=None,
        disposal=None,
        disposal_method_names=None,
        system_cache_root_path="posture_cache_from_str",
    )
    assert _posture("cover-str-path").system_cache_root_path == Path(
        "posture_cache_from_str"
    )


def test_an_absolute_cache_root_is_refused_through_the_door() -> None:
    """
    The setter's "must be relative" rule is not softened by the facade. The
    door forwards the value and lets the posture object refuse it, rather than
    normalizing an absolute path into something the caller did not ask for.

    The path MUST be built from `Path.cwd()` and not written as a literal.
    `_normalize_cache_root_path` rejects on `Path.is_absolute()`, and on
    Windows a rooted-but-driveless literal like "/tmp/x" is NOT absolute -
    `WindowsPath("/tmp/x").is_absolute()` is False. An earlier version of this
    row used that literal, so it was a no-op on Windows and passed a relative
    path into a test asserting absolute paths are refused.
    """
    absolute_root = Path.cwd() / "melder-posture-probe"
    assert absolute_root.is_absolute(), "the probe path must be absolute here"
    book = _book("cover-abs-path")
    with pytest.raises(ValueError):
        book.configure_aether_frame(
            system_state=None,
            disposal=None,
            disposal_method_names=None,
            system_cache_root_path=absolute_root,
        )


def test_a_non_positive_transaction_timeout_is_refused_through_the_door() -> None:
    """Zero and negative timeouts raise rather than being clamped."""
    book = _book("cover-bad-timeout")
    with pytest.raises(ValueError):
        book.configure_aether_frame(
            system_state=None,
            disposal=None,
            disposal_method_names=None,
            max_transaction_wait_time_in_seconds=0.0,
        )


# --------------------------------------------------------------------------
# ORDERING
# --------------------------------------------------------------------------

def test_dynamic_and_ai_native_settle_in_one_call() -> None:
    """
    The ordering law.

    `ai_native` requires dynamic state and that rule is checked at FREEZE, not
    at assignment. Because the door applies `system_state` first, one call can
    move an automatic frame to dynamic AND enable AI-native without the freeze
    later rejecting the pair. If the two applications were ever reordered, the
    posture would still be written but `freeze()` would raise.
    """
    book = _book("order-pair")
    book.configure_aether_frame(
        system_state="dynamic",
        disposal=None,
        disposal_method_names=None,
        ai_native=True,
    )
    posture = _posture("order-pair")
    posture.validate()  # raises ValueError if ai_native outran the state
    posture.freeze()
    assert posture.ai_native_enabled is True
    assert posture.system_state is SystemState.dynamic


def test_ai_native_on_an_automatic_frame_defers_its_failure_to_freeze() -> None:
    """
    The documented sharp edge: the door ACCEPTS the inconsistent pair and the
    frame's own settlement rejects it. This is melder's never-substitute law -
    `validate()` raises rather than returning False - so the test asserts the
    raise, not a falsy verdict.
    """
    book = _book("order-bad")
    book.configure_aether_frame(
        system_state="automatic",
        disposal=None,
        disposal_method_names=None,
        ai_native=True,
    )
    posture = _posture("order-bad")
    assert posture.ai_native_enabled is True  # accepted here
    with pytest.raises(ValueError):
        posture.validate()  # refused there


# --------------------------------------------------------------------------
# OMISSION
# --------------------------------------------------------------------------

def test_omitted_knobs_are_left_alone_not_reset() -> None:
    """
    `None` means "do not touch". A second call that omits a knob must not
    quietly restore its default - otherwise incremental configuration would
    silently undo earlier decisions.
    """
    book = _book("omit-keeps")
    book.configure_aether_frame(
        system_state=None,
        disposal=None,
        disposal_method_names=None,
        rift_enabled=True,
        disable_linking=True,
    )
    book.configure_aether_frame(
        system_state=None,
        disposal=None,
        disposal_method_names=None,
        disable_mutations=True,
    )
    posture = _posture("omit-keeps")
    assert posture.rift_enabled is True     # survived the second call
    assert posture.disable_linking is True  # survived the second call
    assert posture.disable_mutations is True


def test_false_is_a_value_and_not_an_omission() -> None:
    """`False` must reach the frame; only `None` is the skip sentinel."""
    book = _book("omit-false")
    book.configure_aether_frame(
        system_state=None,
        disposal=None,
        disposal_method_names=None,
        rift_enabled=True,
    )
    assert _posture("omit-false").rift_enabled is True
    book.configure_aether_frame(
        system_state=None,
        disposal=None,
        disposal_method_names=None,
        rift_enabled=False,
    )
    assert _posture("omit-false").rift_enabled is False


# --------------------------------------------------------------------------
# ATOMICITY (documented as absent)
# --------------------------------------------------------------------------

def test_a_rejected_value_leaves_earlier_values_written() -> None:
    """
    The door is documented NOT atomic, and this pins that honestly so nobody
    later assumes a failed call is a no-op. `rift_enabled` is applied before
    `disable_mutations`, so a bad type on the latter leaves the former written.
    """
    book = _book("no-rollback")
    with pytest.raises(TypeError):
        book.configure_aether_frame(
            system_state=None,
            disposal=None,
            disposal_method_names=None,
            rift_enabled=True,
            disable_mutations="yes",
        )
    assert _posture("no-rollback").rift_enabled is True


# --------------------------------------------------------------------------
# REACH - the posture written here satisfies the real gate
# --------------------------------------------------------------------------

def test_rift_enabled_false_is_what_the_ar_gate_refuses() -> None:
    """A frame left at the default posture is refused by the AR gate."""
    _book("gate-closed").conjure(name="gate-closed-conduit")
    nexus = Nexus()
    system_configuration = nexus.create_system_configuration()
    system_configuration.with_rift_creation_enabled(True)
    nexus.enable(system_configuration)
    with pytest.raises(ValueError, match="rift_enabled"):
        nexus._validate_target_frame_runtime_requirements(
            "gate-closed",
            RiftSpaceType.capability,
        )


def test_rift_enabled_through_the_door_opens_the_ar_gate() -> None:
    """
    The whole point of the addition: the same gate that refused above now
    passes, and the ONLY thing that changed is a public call. Before this
    parameter existed there was no `import melder` path to this outcome.
    """
    book = _book("gate-open")
    book.configure_aether_frame(
        system_state=None,
        disposal=None,
        disposal_method_names=None,
        rift_enabled=True,
    )
    book.conjure(name="gate-open-conduit")
    nexus = Nexus()
    system_configuration = nexus.create_system_configuration()
    system_configuration.with_rift_creation_enabled(True)
    nexus.enable(system_configuration)
    nexus._validate_target_frame_runtime_requirements(
        "gate-open",
        RiftSpaceType.capability,
    )


def test_codegen_rooms_need_both_knobs_and_the_door_now_supplies_both() -> None:
    """
    A codegen room demands `rift_enabled` AND `ai_native_enabled` AND dynamic
    state on the target frame. All three are settable in one public call now;
    `rift_enabled` alone is still correctly refused.
    """
    rift_only = _book("codegen-partial")
    rift_only.configure_aether_frame(
        system_state=None,
        disposal=None,
        disposal_method_names=None,
        rift_enabled=True,
    )
    rift_only.conjure(name="codegen-partial-conduit")

    full = _book("codegen-full")
    full.configure_aether_frame(
        system_state="dynamic",
        disposal=None,
        disposal_method_names=None,
        rift_enabled=True,
        ai_native=True,
    )
    full.conjure(name="codegen-full-conduit")

    nexus = Nexus()
    system_configuration = nexus.create_system_configuration()
    system_configuration.with_rift_creation_enabled(True)
    nexus.enable(system_configuration)

    with pytest.raises(ValueError):
        nexus._validate_target_frame_runtime_requirements(
            "codegen-partial",
            RiftSpaceType.codegen,
        )
    nexus._validate_target_frame_runtime_requirements(
        "codegen-full",
        RiftSpaceType.codegen,
    )


# --------------------------------------------------------------------------
# LIFECYCLE
# --------------------------------------------------------------------------

def test_a_frozen_posture_refuses_the_door() -> None:
    """
    Frame posture settles at conjure and every builder refuses afterwards, so
    the door refuses too. It raises rather than dropping the request - the
    caller must not believe a settled world was reconfigured.
    """
    book = _book("frozen")
    _posture("frozen").freeze()
    with pytest.raises(RuntimeError):
        book.configure_aether_frame(
            system_state=None,
            disposal=None,
            disposal_method_names=None,
            rift_enabled=True,
        )


def test_a_cleaned_book_refuses_the_door() -> None:
    """`check_cleaned()` fires before any posture value is touched."""
    book = _book("cleaned")
    book.cleanup()
    with pytest.raises(RuntimeError):
        book.configure_aether_frame(
            system_state=None,
            disposal=None,
            disposal_method_names=None,
            rift_enabled=True,
        )
