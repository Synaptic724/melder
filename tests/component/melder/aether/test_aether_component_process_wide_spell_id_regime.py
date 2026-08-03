"""
Component tests for the process-wide spell_id regime.

`spell_id` is a SHA256 over the bind-time fingerprint and does NOT include the
aetheric frame, so the same target bound with the same parameters mints the SAME
id in every frame. Owner ruling 2026-08-02: one spell_id means one spell,
process-wide. `AetherConfiguration.process_wide_unique_spell_ids` defaults True;
setting it False restores per-frame scoping (the multi-tenant shape).

The cross-frame sweep in `Aether._check_for_spell` is GATED ON FRAME COUNT, so a
single-frame process does no cross-frame work at all. These tests cover both
regimes, the single-frame short-circuit, and concurrency.

The configuration is installed by assigning `aether._configuration` directly
rather than through `configure()`/`activate()`. That is deliberate: it exercises
the exact read path `_process_wide_unique_spell_ids()` uses without coupling
these tests to the configure/activate signature, which is a separate surface.
"""

import threading
from typing import Any, List, Optional

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_configuration import AetherConfiguration
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.spellbook import Spellbook


class RegimeTenantCache:
    """Bound identically in several frames to force identical spell_ids."""
    pass


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_regime() -> None:
    """
    Purpose:
        Give each test a clean Aether singleton and frame registry.
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


def _book(frame_name: str) -> Spellbook:
    """
    Purpose:
        Build a Spellbook on a named frame.
    Args:
        frame_name: Frame to bind into.
    Returns:
        Spellbook: A configured Spellbook.
    """
    spellbook = Spellbook(aetheric_frame=frame_name)
    spellbook.get_configuration().set_property(
        "phase_scheduler_workers_per_spellbook", 1
    )
    return spellbook


def _install_regime(enabled: bool) -> None:
    """
    Purpose:
        Install an AetherConfiguration carrying the requested regime.
    Contract:
        - Assigns `Aether._configuration` BEFORE any frame exists. The regime
          itself lives as a plain bool on Aether; the collapse at first frame
          birth reads this configuration and seals that bool. Installing after a
          frame exists would be ignored by design - which is the point of the
          seal, and why every caller here installs first and builds after.
    Args:
        enabled: True for process-wide uniqueness, False for per-frame.
    Returns:
        None.
    """
    configuration = AetherConfiguration().with_defaults()
    configuration.set_process_wide_unique_spell_ids(enabled)
    Spellbook._aether._configuration = configuration


def test_component_regime_default_is_process_wide_without_configuration() -> None:
    """
    Purpose:
        Prove an UNCONFIGURED Aether defaults to process-wide uniqueness.
    Contract:
        - Frames are lazy, so a frame can be born before any configuration is
          installed; the default must still be the documented one.
        - Two frames binding the same class must therefore collide.
    Returns:
        None.
    Raises:
        AssertionError: If the second conjure is permitted.
    """
    aether = Spellbook._aether
    assert aether._configuration is None, (
        "precondition: nothing configured and - because frames are lazy - no "
        "frame born yet, so the collapse has not run"
    )
    assert aether._process_wide_unique_spell_ids is True, (
        "the bool must already carry the documented default from __init__, "
        "before any configuration or frame exists"
    )

    book_a = _book("regime-default-a")
    book_b = _book("regime-default-b")
    book_a.bind(spell=RegimeTenantCache, existence="unique")
    book_b.bind(spell=RegimeTenantCache, existence="unique")

    book_a.conjure(name="regime-default-conduit-a")
    with pytest.raises(RuntimeError, match="Conjure refused"):
        book_b.conjure(name="regime-default-conduit-b")


def test_component_regime_on_refuses_same_class_across_frames() -> None:
    """
    Purpose:
        Prove the ON regime enforces uniqueness ACROSS frames, not just within.
    Returns:
        None.
    Raises:
        AssertionError: If two frames may hold the same spell_id.
    """
    _install_regime(True)

    book_a = _book("regime-on-a")
    book_b = _book("regime-on-b")
    book_a.bind(spell=RegimeTenantCache, existence="unique")
    book_b.bind(spell=RegimeTenantCache, existence="unique")

    book_a.conjure(name="regime-on-conduit-a")
    with pytest.raises(RuntimeError, match="Conjure refused"):
        book_b.conjure(name="regime-on-conduit-b")


def test_component_regime_off_restores_per_frame_isolation() -> None:
    """
    Purpose:
        Prove the OFF regime restores the multi-tenant shape: identical
        fingerprints in two frames, two independent singletons.
    Contract:
        - This is the negative control for the whole feature. If it fails, the
          off-switch does not work and multi-tenancy has been removed outright
          rather than made opt-out.
    Returns:
        None.
    Raises:
        AssertionError: If either conjure is refused or the instances are shared.
    """
    _install_regime(False)

    book_a = _book("regime-off-a")
    book_b = _book("regime-off-b")
    book_a.bind(spell=RegimeTenantCache, existence="unique")
    book_b.bind(spell=RegimeTenantCache, existence="unique")

    conduit_a = book_a.conjure(name="regime-off-conduit-a")
    conduit_b = book_b.conjure(name="regime-off-conduit-b")

    cache_a: Any = conduit_a.meld(spell=RegimeTenantCache)
    cache_b: Any = conduit_b.meld(spell=RegimeTenantCache)
    assert cache_a is not cache_b, "per-frame isolation must survive the off switch"


def test_component_single_frame_is_unaffected_by_the_regime() -> None:
    """
    Purpose:
        Prove the frame-count gate: with ONE frame there is no cross-frame work
        and ordinary binding is untouched.
    Contract:
        - The sweep engages only when `len(_aetheric_frames) > 1`, so a
          single-frame process pays nothing.
    Returns:
        None.
    Raises:
        AssertionError: If a single-frame world cannot conjure and meld.
    """
    _install_regime(True)

    book = _book("regime-single")
    book.bind(spell=RegimeTenantCache, existence="unique")
    conduit = book.conjure(name="regime-single-conduit")

    assert conduit.meld(spell=RegimeTenantCache) is not None
    assert len(Spellbook._aether._aetheric_frames) == 1, (
        "this test is only meaningful while exactly one frame exists"
    )


@pytest.mark.xfail(
    strict=True,
    reason=(
        "OPEN: the conjure sweep is a PREFLIGHT, not a mutual exclusion. It reads "
        "the frame set under the Spellbook lock while the write lands later under "
        "the FRAME lock inside Conduit.__init__, so every thread can pass before "
        "any thread registers. Closing it needs the atomic check-and-set in "
        "AethericFrame.register_conduit_spells - "
        "STORY-2026-08-02-aether-unified-spell-id-set. STRICT ON PURPOSE: when "
        "that story lands this test starts passing, xfail(strict) turns that into "
        "a FAILURE, and whoever fixed it is told to delete this marker. Do NOT "
        "loosen the assertion below to make this green."
    ),
)
def test_component_concurrent_conjures_across_frames_admit_at_most_one() -> None:
    """
    Purpose:
        Probe the regime under concurrency: several threads, each with its own
        Spellbook on its own frame, all binding the SAME class, all conjuring at
        once. Exactly one should be admitted.

    Contract:
        - A RED HERE IS A KNOWN, DOCUMENTED RACE, NOT A REGRESSION. The conjure
          sweep is a PREFLIGHT: it holds the Spellbook lock while the frame write
          happens later under the FRAME lock inside `Conduit.__init__`, so two
          threads can both pass the check before either registers. The
          authoritative check-and-set belongs in
          `AethericFrame.register_conduit_spells`, under the lock that guards the
          registry - see STORY-2026-08-02-aether-unified-spell-id-set.
        - Treat a failure as the proof that story is needed, and record the
          observed admit count rather than loosening the assertion.
    Returns:
        None.
    Raises:
        AssertionError: If more than one conjure is admitted.
    """
    _install_regime(True)

    thread_count = 8
    books: List[Spellbook] = []
    for index in range(thread_count):
        book = _book(f"regime-race-{index}")
        book.bind(spell=RegimeTenantCache, existence="unique")
        books.append(book)

    admitted: List[int] = []
    refused: List[int] = []
    unexpected: List[str] = []
    lock = threading.Lock()
    start = threading.Barrier(thread_count)

    def _attempt(index: int) -> None:
        """Conjure one book, recording the outcome."""
        start.wait()
        try:
            books[index].conjure(name=f"regime-race-conduit-{index}")
        except RuntimeError as exc:
            if "Conjure refused" in str(exc):
                with lock:
                    refused.append(index)
            else:
                with lock:
                    unexpected.append(f"{index}: {exc}")
            return
        except Exception as exc:
            # Broad catch is deliberate and NOT swallowing: anything that is not
            # the integrity refusal is recorded and asserted on below, so an
            # unrelated failure surfaces as a named test failure rather than
            # being miscounted as a refusal.
            with lock:
                unexpected.append(f"{index}: {type(exc).__name__}: {exc}")
            return
        with lock:
            admitted.append(index)

    threads = [
        threading.Thread(target=_attempt, args=(i,), name=f"regime-race-{i}")
        for i in range(thread_count)
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=30)

    print(
        f"\nadmitted={len(admitted)}  refused={len(refused)}  "
        f"unexpected={len(unexpected)}"
    )
    for line in unexpected:
        print(f"  UNEXPECTED {line}")

    assert not unexpected, (
        f"conjure raised something other than the integrity refusal: {unexpected}"
    )
    assert len(admitted) == 1, (
        f"{len(admitted)} conjures were admitted; exactly one may hold a given "
        "spell_id process-wide. This is the PREFLIGHT RACE documented in "
        "STORY-2026-08-02-aether-unified-spell-id-set: the check holds the "
        "Spellbook lock while the write happens later under the frame lock. Do "
        "NOT loosen this assertion - it is the evidence that the atomic "
        "check-and-set in register_conduit_spells is required."
    )
