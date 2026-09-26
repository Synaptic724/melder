"""
Component contracts: a fresh process over an unchanged world replays the structural tier instead of running phases 1-4.

The conjure classifies every owned spell against the structural payloads captured by the previous conjure. When all
of them hit (same key, same world stamp, replayable), the phase 3-4 durable state is rebuilt from the rows and the
structural scheduler run is skipped; the registry then holds the same dependencies, dependents, topology and verdicts
as after a cold conjure, and the first meld behaves the same. Anything else runs today's structural phases.
"""

import inspect
import shutil
from pathlib import Path
from typing import Any, Dict, Iterator, List, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.aetheric_frame.aetheric_frame_configuration import AethericFrameConfiguration
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.spell_compiler.structural_snapshot.structural_snapshot import (
    StructuralSnapshot,
)
from melder.aether.spellbook.spellbook import Spellbook
from melder.aether.spellbook.spellbook_creation_system import SpellbookCreationSystem
from melder.nexus.nexus import Nexus
from melder.utilities.logger.safe_logger import SafeLogger


def _reset_world() -> None:
    """Replace the process singletons with a fresh Aether and Nexus."""
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


@pytest.fixture(autouse=True)
def isolated_worlds() -> Iterator[None]:
    """
    Purpose: Give each case fresh worlds and leave a fresh one behind.
    Yields: None while the case runs.
    """
    _reset_world()
    yield
    _reset_world()


def _package_root() -> Path:
    """Return the melder package root the runtime anchors relative cache fragments against."""
    return Path(inspect.getfile(AethericFrameConfiguration)).resolve().parents[2]


def _fresh_cache_fragment(name: str) -> Path:
    """Empty one repo-local cache root and return it as a package-relative fragment."""
    root = _package_root() / "tests/component/melder/spellbook" / name
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)
    return root.resolve().relative_to(_package_root())


def _new_world_book(frame: str, cache_fragment: Path, caching: bool = True) -> Spellbook:
    """Start a fresh world under the fragment and return a Book on `frame`."""
    _reset_world()
    configuration = Aether()._ensure_frame(frame).frame_configuration
    configuration.with_system_caching_enabled(caching)
    configuration.with_system_cache_root_path(cache_fragment)
    book = Spellbook(aetheric_frame=frame)
    book.get_configuration().set_property("phase_scheduler_workers_per_spellbook", 1)
    return book


class Engine:
    """Provider without dependencies."""


class Wheel:
    """Second provider, collected by Car."""


class Car:
    """Consumer with one single socket and one collection socket."""

    def __init__(self, engine: Engine, wheels: list[Wheel]) -> None:
        self.engine = engine
        self.wheels = wheels


class _StructuralRunSpy:
    """Counts structural scheduler runs and records the structural classification of each conjure."""

    def __init__(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self.runs = 0
        self.paths: List[str] = []
        original_run = SpellbookCreationSystem.run_structural_phases
        original_state = SpellbookCreationSystem._build_structural_cache_state

        def counting_run(*args: Any, **kwargs: Any) -> Any:
            self.runs += 1
            return original_run(*args, **kwargs)

        def recording_state(**kwargs: Any) -> Any:
            state = original_state(**kwargs)
            self.paths.append(state["structural_path"])
            return state

        monkeypatch.setattr(SpellbookCreationSystem, "run_structural_phases", staticmethod(counting_run))
        monkeypatch.setattr(SpellbookCreationSystem, "_build_structural_cache_state", staticmethod(recording_state))


def _bind_world(book: Spellbook) -> Tuple[str, str, str]:
    """Bind Engine (unique), two Wheels (many) and Car (many); return the ids of Engine, Wheel and Car."""
    engine_id = book.bind(spell=Engine, existence="unique", permissions="create")
    wheel_id = book.bind(spell=Wheel, existence="many", permissions="create")
    car_id = book.bind(spell=Car, existence="many", permissions="create")
    return engine_id, wheel_id, car_id


def _registry_snapshot(book: Spellbook, spell_ids: Tuple[str, ...]) -> Dict[str, Any]:
    """Value view of the registry state phases 3-4 leave behind, per spell id."""
    registry = book._spell_system_states
    snapshot: Dict[str, Any] = {}
    for spell in book._spells.values():
        if spell.spell_id not in spell_ids:
            continue
        state = registry.get_by_index_id(spell.spell_index.id)
        topology = registry.get_local_topology(spell.spell_index)
        snapshot[spell.spell_id] = {
            "dependencies": tuple(spell.dependencies),
            "direct_dependencies": tuple(sorted(state.direct_dependencies)),
            "direct_dependents": tuple(sorted(
                registry.get_by_index_id(index_id).current_spell_id for index_id in state.direct_dependents
            )),
            "validity": state.validity.name,
            "flags": tuple(sorted(flag.name for flag in state.flags)),
            "sockets": tuple(
                (s.param_name, s.position, s.socket_kind.name, s.is_collection, s.is_optional, s.target_spell_ids,
                 s.dependency_key, s.contract_key, s.referenced_spell_ids, s.parameter_kind)
                for s in topology.sockets
            ),
        }
    return snapshot


def test_fresh_world_over_an_unchanged_book_replays_the_structural_tier(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Purpose: The second process skips phases 1-4 and ends in the same registry state as the cold conjure.
    Contract: The cold conjure runs the structural phases (path miss); the next world classifies full_hit, runs
        no structural scheduler pass, matches the cold registry snapshot field by field, and melds a Car.
    """
    spy = _StructuralRunSpy(monkeypatch)
    fragment = _fresh_cache_fragment("_cache_structural_hydrate_full_hit")

    cold = _new_world_book("structural-hydrate", fragment)
    ids = _bind_world(cold)
    cold.conjure(name="root")
    cold_snapshot = _registry_snapshot(cold, ids)
    assert spy.paths == ["miss"] and spy.runs == 1

    warm = _new_world_book("structural-hydrate", fragment)
    assert _bind_world(warm) == ids
    conduit = warm.conjure(name="root")

    assert spy.paths == ["miss", "full_hit"]
    assert spy.runs == 1
    assert _registry_snapshot(warm, ids) == cold_snapshot
    engine_id, wheel_id, car_id = ids
    assert cold_snapshot[car_id]["dependencies"] == (engine_id, wheel_id)
    assert cold_snapshot[engine_id]["direct_dependents"] != ()
    car = conduit.meld(spell=Car)
    assert isinstance(car.engine, Engine) and len(car.wheels) == 1 and isinstance(car.wheels[0], Wheel)


def test_changed_spell_misses_and_runs_the_structural_phases(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Purpose: A different world never replays stale rows.
    Contract: A new provider bound in the next world changes the pool, so the classification is not a full hit,
        the structural phases run, and the consumer melds against the current world.
    """
    spy = _StructuralRunSpy(monkeypatch)
    fragment = _fresh_cache_fragment("_cache_structural_hydrate_changed")

    cold = _new_world_book("structural-hydrate-changed", fragment)
    _bind_world(cold)
    cold.conjure(name="root")

    class Radio:
        """Provider added in the second world."""

    warm = _new_world_book("structural-hydrate-changed", fragment)
    _bind_world(warm)
    warm.bind(spell=Radio, existence="unique", permissions="create")
    conduit = warm.conjure(name="root")

    assert spy.paths[-1] != "full_hit"
    assert spy.runs == 2
    assert isinstance(conduit.meld(spell=Car).engine, Engine)


def test_validation_warning_report_forces_the_live_structural_run(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Purpose: The opt-in warning report needs live phase-4 results, so it never hydrates.
    Contract: With payloads on disk, `validation_warnings=True` classifies disabled and runs the phases.
    """
    spy = _StructuralRunSpy(monkeypatch)
    fragment = _fresh_cache_fragment("_cache_structural_hydrate_warnings")

    cold = _new_world_book("structural-hydrate-warnings", fragment)
    _bind_world(cold)
    cold.conjure(name="root")

    warm = _new_world_book("structural-hydrate-warnings", fragment)
    _bind_world(warm)
    warm.conjure(name="root", validation_warnings=True)

    assert spy.paths == ["miss", "disabled"]
    assert spy.runs == 2


def test_caching_disabled_never_touches_the_structural_tier(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Purpose: Without system caching there is no bundle to classify against.
    Contract: The classification is disabled, the phases run, and no cache utility is created.
    """
    spy = _StructuralRunSpy(monkeypatch)
    fragment = _fresh_cache_fragment("_cache_structural_hydrate_disabled")

    book = _new_world_book("structural-hydrate-disabled", fragment, caching=False)
    _bind_world(book)
    book.conjure(name="root")

    assert spy.paths == ["disabled"] and spy.runs == 1
    assert book._caching_system is None


def test_replay_failure_falls_back_to_the_live_structural_run(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Purpose: A failure mid-replay must not break conjure.
    Contract: When the replay raises, the error is logged, the structural phases run live, and the registry
        state equals the cold conjure's.
    """
    spy = _StructuralRunSpy(monkeypatch)
    fragment = _fresh_cache_fragment("_cache_structural_hydrate_fallback")

    cold = _new_world_book("structural-hydrate-fallback", fragment)
    ids = _bind_world(cold)
    cold.conjure(name="root")
    cold_snapshot = _registry_snapshot(cold, ids)

    def failing_hydrate(spellbook: Spellbook, hits: Dict[str, Any]) -> None:
        raise RuntimeError("replay exploded")

    monkeypatch.setattr(StructuralSnapshot, "hydrate_full_hit", staticmethod(failing_hydrate))
    errors: List[str] = []

    original_error = SafeLogger.error

    def recording_error(self: SafeLogger, message: str, *args: Any, **kwargs: Any) -> None:
        errors.append(message)
        original_error(self, message, *args, **kwargs)

    monkeypatch.setattr(SafeLogger, "error", recording_error)
    warm = _new_world_book("structural-hydrate-fallback", fragment)
    _bind_world(warm)
    conduit = warm.conjure(name="root")

    assert spy.paths == ["miss", "full_hit"]
    assert spy.runs == 2
    assert any("replay exploded" in message for message in errors)
    assert _registry_snapshot(warm, ids) == cold_snapshot
    assert isinstance(conduit.meld(spell=Car).engine, Engine)
