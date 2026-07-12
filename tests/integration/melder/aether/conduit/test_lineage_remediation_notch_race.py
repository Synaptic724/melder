"""
Lineage remediation vs notch race probe (mediator epic, owner-directed
2026-07-12: "make some tests for that and go find out if that happens").

The question under test: meld-time lazy remediation
(Meld._ensure_lineage_resolvable) writes lineage validity WITHOUT a
mediator claim (the readers-never-enter law), while notch_spell seals
book+conduit+binding exclusively. Can a remediation window straddling a
concurrent notch poison post-settle truth - a stale verdict for the OLD
member masking the NEW member, a wedged meld gate, or a deadlock?

Method: a barrier injected at the EXACT remediation seam (the compiler
system's run_structural_phases call inside the spell-lock window) holds
one meld's remediation open while a notch runs on the same lineage from
another thread. Every join carries a timeout so a deadlock FAILS LOUDLY
as its own finding instead of hanging the suite. Post-settle assertions
check the things that must survive any legal interleaving.
"""
import contextlib
import threading
from typing import Any, Iterator

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.meld.meld import Meld
from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook

from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)


class _RaceAlpha:
    def __init__(self) -> None:
        self.tag = "A"


class _RaceBeta:
    def __init__(self) -> None:
        self.tag = "B"


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_race_probe() -> None:
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


@contextlib.contextmanager
def _two_member_index() -> Iterator[tuple]:
    """
    Dynamic conduit whose index has ACTIVE member A and parked member B.
    Yields (book, conduit, id_a, id_b, index, spell_b).
    """
    config = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(config)
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    book = Spellbook(configuration=config)
    id_a = book.bind(
        spell=_RaceAlpha, existence=Existence.unique,
        permissions="create", binding_name="a",
    )
    conduit = book.conjure(dynamic=True, name="race-root")
    index = book.find_spell_by_id(id_a).spell_index
    id_b = conduit.bind_inactive(
        spell=_RaceBeta, spell_index=index, existence=Existence.unique,
        permissions="create", binding_name="b",
    )
    spell_b = book._get_owned_spell(id_b)
    try:
        yield (book, conduit, id_a, id_b, index, spell_b)
    finally:
        conduit.cleanup()


class _BarrieredCompilerSystem:
    """
    Delegating wrapper that parks run_structural_phases on an Event.

    Purpose:
        Deterministic interleaving control at the exact seam under
        test: the remediation window opens (in_window set), then waits
        for release before the REAL phases run. Everything else
        delegates untouched - this is a barrier, not a fake.
    """

    def __init__(self, real: Any, in_window: threading.Event,
                 release: threading.Event) -> None:
        self._real = real
        self._in_window = in_window
        self._release = release

    def run_structural_phases(self, spellbook: Any, spell: Any) -> Any:
        self._in_window.set()
        # A bounded wait: if the releasing thread never comes back the
        # window self-opens so the suite cannot hang here.
        self._release.wait(timeout=15)
        return self._real.run_structural_phases(spellbook, spell)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._real, name)


def test_notch_during_open_remediation_window_cannot_poison_post_settle_truth(
        monkeypatch,
):
    """
    REGRESSION MONITOR (owner-directed): the lineage remediation race.

    History:
        2026-07-12 this probe CONFIRMED the race on the unpatched
        runtime - a validation window straddling a notch wrote a stale
        terminal verdict onto the freshly promoted member (validity
        writes key by live `selected_spell_id` at write time), and
        `invalid` is terminal, so the notched-in member was permanently
        poisoned. An earlier fix (mediating the validator as its own
        transaction) was owner-reverted (commit 7abb39e62). The LANDED
        fix (owner ruling, patch notch_conduit_gate_freeze_2026_07_12):
        the NOTCH strategy's on_start freezes the sealed conduits'
        CreationGates through the DevOps ConduitLineageGateOps facade -
        new melds park, in-flight melds (this probe's barriered
        validator included, since a meld holds its conduit gate ticket
        across its whole executor) drain to zero BEFORE the repoint -
        and on_end reopens on every exit path via root finalize. This
        test stays green as the proof and MUST NOT regress.

    Contract (post-fix expectations):
        The notch either PARKS behind the held validation window (gate
        drain waits for the in-flight meld ticket) and completes after
        release, or completes before the window opens - never
        interleaves inside it. Post-settle: the index selects B, a
        fresh meld yields B, no deadlocks (timeout-guarded joins fail
        loudly), and the in-window meld returns either an A-instance
        or a legal refusal. The probe's 15s self-opening barrier stays
        inside the freeze's 30s drain bound.
    """
    with _two_member_index() as (book, conduit, id_a, id_b, index, spell_b):
        in_window = threading.Event()
        release = threading.Event()
        meld_component = conduit._meld
        real_system = meld_component._get_spell_compiler_system()
        barriered = _BarrieredCompilerSystem(real_system, in_window, release)
        # Class-level patch: Meld types are slotted, so instance
        # setattr would raise; the autouse world-reset fixture scopes
        # the patch's blast radius to this test.
        monkeypatch.setattr(
            type(meld_component),
            "_get_spell_compiler_system",
            lambda self: barriered,
        )
        # Force the gate to demand remediation for A's first meld so the
        # window opens deterministically (the double-checked gate reads
        # this twice before entering the locked rerun). gate_calls
        # instruments whether the meld path consults the gate AT ALL -
        # zero calls on a completed meld would itself be a finding (a
        # fast lane skipping _ensure_lineage_resolvable).
        real_required = Meld._gated_validation_required
        forced = {"remaining": 2, "gate_calls": 0}

        def force_gated_once(self: Any, spell: Any) -> bool:
            forced["gate_calls"] += 1
            if spell.spell_id == id_a and forced["remaining"] > 0:
                forced["remaining"] -= 1
                return True
            return real_required(self, spell)

        monkeypatch.setattr(
            Meld, "_gated_validation_required", force_gated_once
        )

        # The remediation path is DOUBLY gated: conduit_meld.py:306 only
        # calls _ensure_lineage_resolvable when the book's
        # _spellbook_validation_required flag is up (the RiskManager
        # toggle; the runtime raises it when a not-yet-validated member
        # appears, spellbook.py:3183). Raise it through the real setter
        # so the probe recreates the exact runtime posture of a gated
        # lineage instead of silently melding down the clean fast lane
        # (the first probe run died here: window never opened because
        # the gate was never consulted).
        book._set_spellbook_validation_required(True)

        meld_outcome: dict = {}

        def melder() -> None:
            try:
                meld_outcome["value"] = conduit.meld(spell=id_a)
            except Exception as error:  # legal refusal is a finding, not a fail
                meld_outcome["error"] = error

        notch_outcome: dict = {}

        def notcher() -> None:
            try:
                conduit.notch_spell(spell_index=index, spell=spell_b)
                notch_outcome["completed"] = True
            except Exception as error:
                notch_outcome["error"] = error

        meld_thread = threading.Thread(target=melder, name="race-melder")
        meld_thread.start()
        if not in_window.wait(timeout=10):
            # Surface the ACTUAL story instead of a mute harness fault:
            # did the meld die early, finish without gating, or hang?
            meld_thread.join(timeout=5)
            pytest.fail(
                "remediation window never opened. Diagnostics: "
                "gate_calls={0}, force_remaining={1}, meld_thread_alive={2}, "
                "meld_outcome={3}".format(
                    forced["gate_calls"],
                    forced["remaining"],
                    meld_thread.is_alive(),
                    (
                        "error: {0!r}".format(meld_outcome["error"])
                        if "error" in meld_outcome
                        else "value: {0}".format(
                            type(meld_outcome.get("value")).__name__
                        )
                    ),
                )
            )

        notch_thread = threading.Thread(target=notcher, name="race-notcher")
        notch_thread.start()
        # Give the notch a moment to either complete or park on whatever
        # the runtime serializes it with, then release the window.
        notch_thread.join(timeout=5)
        notch_parked_on_window = notch_thread.is_alive()
        release.set()

        meld_thread.join(timeout=15)
        notch_thread.join(timeout=15)
        assert not meld_thread.is_alive(), (
            "DEADLOCK FINDING: the in-window meld never completed after "
            "release - remediation vs notch wedged"
        )
        assert not notch_thread.is_alive(), (
            "DEADLOCK FINDING: the notch never completed - it is "
            "serialized behind something the remediation window holds "
            "and the release did not unblock it"
        )
        assert notch_outcome.get("completed") is True, (
            "notch failed outright during the window: "
            f"{notch_outcome.get('error')!r}"
        )

        # The verdict phase runs on the FULLY UNPATCHED runtime: undo
        # removes the gate force AND the barrier, so a post-settle
        # refusal can only come from state the race actually wrote -
        # never from probe leakage.
        monkeypatch.undo()

        # --- The post-settle truth this probe exists for ---------------
        assert index.selected_spell_id == id_b
        in_window_story = (
            "in-window meld -> "
            + ("error: {0!r}".format(meld_outcome.get("error"))
               if "error" in meld_outcome
               else "instance: {0}".format(
                   type(meld_outcome.get("value")).__name__))
            + "; notch "
            + ("PARKED behind the window" if notch_parked_on_window
               else "completed DURING the window")
        )
        try:
            fresh = conduit.meld(spell=id_b)
        except Exception as poison:
            pytest.fail(
                "POISONING VERDICT: post-settle meld of the notched-in "
                "member REFUSED on the unpatched runtime - the stale "
                "remediation window wrote a verdict that outlived the "
                "notch. Refusal: {0!r}. Interleaving: {1}. Sequential "
                "control proves this never happens without the window - "
                "the lineage race is REAL; route the epic to D1-D5 "
                "drafting.".format(poison, in_window_story)
            )
        assert isinstance(fresh, _RaceBeta), (
            "POISONED (wrong member): post-settle meld yielded "
            f"{type(fresh)!r} instead of B. Interleaving: {in_window_story}"
        )
        # Record the interleaving shape observed (both are legal; the
        # print rides pytest -s for the owner's read of what happened).
        print(
            "race shape: notch "
            + ("PARKED behind the open window" if notch_parked_on_window
               else "completed DURING the window")
            + "; in-window meld -> "
            + ("error: {0!r}".format(meld_outcome.get("error"))
               if "error" in meld_outcome
               else "instance: {0}".format(
                   type(meld_outcome.get("value")).__name__))
        )


def test_sequential_notch_control_lane():
    """
    Contract (control):
        The same harness WITHOUT any window: notch then meld yields B.
        If this fails, the probe's post-settle assertions are testing
        the wrong invariant and the race test's verdict is void.
    """
    with _two_member_index() as (book, conduit, id_a, id_b, index, spell_b):
        conduit.notch_spell(spell_index=index, spell=spell_b)
        assert index.selected_spell_id == id_b
        assert isinstance(conduit.meld(spell=id_b), _RaceBeta)
