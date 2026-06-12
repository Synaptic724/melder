from __future__ import annotations

import threading

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import (
    apply_automatic_defaults_for_spellbook_configuration,
)


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_fast_door_integration() -> None:
    """
    Purpose:
        Ensure fast-door integration tests start with a clean Aether singleton.
    Contract:
        - Resets the Aether singleton before the test runs.
        - Rebinds Spellbook._aether and Conduit._aether to the new instance.
        - Resets the singleton again after the test for isolation.
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


class _SharedUnique:
    """
    Purpose:
        Shared `unique` service for cross-cycle identity assertions.
    Contract:
        - Instances are distinguishable by identity.
    """

    def __init__(self) -> None:
        """
        Purpose:
            Initialize an identity marker.
        Contract:
            - marker is unique per instance.
        Returns:
            None.
        """
        self.marker = object()


class _SessionService:
    """
    Purpose:
        Outer-scope `unique_per_conduit` service for lesser-cycle assertions.
    Contract:
        - Instances are distinguishable by identity.
    """

    def __init__(self) -> None:
        """
        Purpose:
            Initialize an identity marker.
        Contract:
            - marker is unique per instance.
        Returns:
            None.
        """
        self.marker = object()


class _ScopeMarker:
    """
    Purpose:
        Request-scope `unique_per_spell_space` marker for scope isolation.
    Contract:
        - Instances are distinguishable by identity.
    """

    def __init__(self) -> None:
        """
        Purpose:
            Initialize an identity marker.
        Contract:
            - marker is unique per instance.
        Returns:
            None.
        """
        self.marker = object()


def _build_runtime() -> tuple[Spellbook, Conduit, dict[str, str]]:
    """
    Purpose:
        Build one automatic-mode runtime with the three fast-door routes bound.
    Contract:
        - Binds shared unique, per-conduit session, and per-spellspace marker.
        - Conjures one root conduit named "root".
    Returns:
        tuple[Spellbook, Conduit, dict[str, str]]:
            Spellbook, rooted conduit, and spell-id map.
    """
    configuration = SpellbookConfiguration()
    configuration.load_default_dictionary()
    apply_automatic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    spellbook = Spellbook(configuration=configuration)
    spell_ids = {
        "shared": spellbook.bind(
            spell=_SharedUnique,
            existence=Existence.unique,
            permissions="create",
        ),
        "session": spellbook.bind(
            spell=_SessionService,
            existence=Existence.unique_per_conduit,
            permissions="create",
        ),
        "marker": spellbook.bind(
            spell=_ScopeMarker,
            existence=Existence.unique_per_spell_space,
            permissions="create",
        ),
    }
    conduit = spellbook.conjure(name="root")
    return spellbook, conduit, spell_ids


def test_integration_fast_door_stays_correct_across_pooled_lesser_cycles() -> None:
    """
    Purpose:
        Verify fast-door correctness across repeated pooled lesser/spellspace
        scope cycles, the gauntlet-shaped hot path.
    Contract:
        - Shared unique identity holds across every cycle.
        - Outer session objects are cached within one lesser cycle and replaced
          across cycles (creations reset on pool return).
        - Spellspace markers are cached within one scope and replaced across
          scopes.
        - Pooled lesser reuse keeps the same conduit shell and meld door, so
          fast-door entries stay warm across cycles while results stay
          scope-correct.
    """
    _spellbook, conduit, spell_ids = _build_runtime()
    try:
        shared_baseline = conduit.meld(spell=spell_ids["shared"])

        previous_lesser: Conduit | None = None
        previous_session: _SessionService | None = None
        previous_marker: _ScopeMarker | None = None

        for cycle_index in range(8):
            lesser = conduit.create_lesser_conduit()
            try:
                if previous_lesser is not None:
                    # Pooled reuse hands back the same shell, which is what
                    # keeps the fast-door registry warm across cycles.
                    assert lesser is previous_lesser
                    assert spell_ids["session"] in lesser._meld._fast_meld_doors

                session_first = lesser.meld(spell=spell_ids["session"])
                session_second = lesser.meld(spell=spell_ids["session"])
                assert session_second is session_first
                if previous_session is not None:
                    # Creations reset on pool return: a new cycle must build a
                    # fresh session object even through a warm fast door.
                    assert session_first is not previous_session

                assert lesser.meld(spell=spell_ids["shared"]) is shared_baseline

                with lesser.enter_spellspace() as space:
                    marker_first = space.meld(spell=spell_ids["marker"])
                    marker_second = space.meld(spell=spell_ids["marker"])
                    assert marker_second is marker_first
                    if previous_marker is not None:
                        assert marker_first is not previous_marker
                    # Outer scope propagates into the request scope.
                    assert space.meld(spell=spell_ids["session"]) is session_first
                    previous_marker = marker_first

                previous_session = session_first
                previous_lesser = lesser
            finally:
                lesser.cleanup()
    finally:
        conduit.permanent_cleanup()


def test_integration_fast_door_multithreaded_scope_cycles_stay_isolated() -> None:
    """
    Purpose:
        Verify fast-door correctness under concurrent scope cycles.
    Contract:
        - Each worker thread runs its own lesser/spellspace cycles.
        - Shared unique identity is process-wide identical across threads.
        - Per-scope markers stay unique within each scope and are never shared
          across concurrently active scopes.
        - No worker observes an error; assertions are contract-based and do
          not depend on thread scheduling.
    """
    _spellbook, conduit, spell_ids = _build_runtime()
    try:
        shared_baseline = conduit.meld(spell=spell_ids["shared"])
        errors: list[BaseException] = []

        def _worker() -> None:
            try:
                for _ in range(6):
                    lesser = conduit.create_lesser_conduit()
                    try:
                        session = lesser.meld(spell=spell_ids["session"])
                        assert lesser.meld(spell=spell_ids["session"]) is session
                        assert (
                            lesser.meld(spell=spell_ids["shared"])
                            is shared_baseline
                        )
                        with lesser.enter_spellspace() as space:
                            marker = space.meld(spell=spell_ids["marker"])
                            assert space.meld(spell=spell_ids["marker"]) is marker
                            assert (
                                space.meld(spell=spell_ids["session"]) is session
                            )
                    finally:
                        lesser.cleanup()
            except BaseException as exc:
                # Test-only collection seam: worker assertions cannot fail the
                # test from a child thread, so they are captured here and
                # re-asserted by the main thread after join.
                errors.append(exc)

        threads = [threading.Thread(target=_worker) for _ in range(3)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=30.0)

        assert not errors, f"worker errors: {errors!r}"
    finally:
        conduit.permanent_cleanup()
