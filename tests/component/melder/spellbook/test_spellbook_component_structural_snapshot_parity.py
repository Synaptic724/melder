"""
Parity contracts: the world after a hydrated conjure behaves like the world after a cold one.

Every invalidation event of the D5 table that a conjured book can see - a bind after conjure, a notch, a spell
removal, a contract grant, a transfer - writes through the registry, never through the phases, so it must leave
the same registry state and the same meld outcome whether phases 1-4 ran live or were replayed from rows. Two
further contracts pin the process boundary: the rows a child process captured hydrate this process (the key and
world stamp are value-only), and a crystallizer restore (fresh index ULIDs, same spell ids) still hydrates.
"""

import inspect
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, List, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.aetheric_frame.aetheric_frame_configuration import AethericFrameConfiguration
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.aether.spellbook.spellbook_creation_system import SpellbookCreationSystem
from melder.crystallizer.configuration.crystallizer_configuration import CrystallizerConfiguration
from melder.crystallizer.crystallizer import Crystallizer
from melder.nexus.nexus import Nexus
from tests._frame_posture_test_support import apply_dynamic_defaults_for_spellbook_configuration
from tests.mocks.spellbook.contract_classes import ContractConsumerPrimary, ContractServicePrimary
from tests.mocks.spellbook.protocols import IService
from tests.mocks.spellbook.structural_snapshot_classes import Car, Engine, EngineAlternative, Radio, Wheel

FRAME = "structural-parity"
_REPO_ROOT = Path(__file__).resolve().parents[4]


def _reset_world() -> None:
    """Replace the process singletons with a fresh Aether, Nexus and (inactive) Crystallizer."""
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    Crystallizer._reset_singleton_for_tests()
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


def _new_world_book(frame: str, cache_fragment: Path) -> Spellbook:
    """Start a fresh world with caching enabled under the fragment and return a Book on `frame`."""
    _reset_world()
    configuration = Aether()._ensure_frame(frame).frame_configuration
    configuration.with_system_caching_enabled(True)
    configuration.with_system_cache_root_path(cache_fragment)
    book = Spellbook(aetheric_frame=frame)
    book.get_configuration().set_property("phase_scheduler_workers_per_spellbook", 1)
    return book


class _StructuralRunSpy:
    """Counts structural scheduler runs and records the structural classification of each conjure."""

    def __init__(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self.runs = 0
        self.paths: List[str] = []
        self.root_paths: List[str] = []
        original_run = SpellbookCreationSystem.run_structural_phases
        original_state = SpellbookCreationSystem._build_structural_cache_state

        def counting_run(*args: Any, **kwargs: Any) -> Any:
            self.runs += 1
            return original_run(*args, **kwargs)

        def recording_state(**kwargs: Any) -> Any:
            state = original_state(**kwargs)
            self.paths.append(state["structural_path"])
            if kwargs.get("conduit_name") == "root":
                self.root_paths.append(state["structural_path"])
            return state

        monkeypatch.setattr(SpellbookCreationSystem, "run_structural_phases", staticmethod(counting_run))
        monkeypatch.setattr(SpellbookCreationSystem, "_build_structural_cache_state", staticmethod(recording_state))


def _bind_world(book: Spellbook) -> Dict[str, str]:
    """Bind Engine (unique), Wheel (many), Car (many) and Radio (unique); return the ids by class name."""
    return {
        "Engine": book.bind(spell=Engine, existence="unique", permissions="create"),
        "Wheel": book.bind(spell=Wheel, existence="many", permissions="create"),
        "Car": book.bind(spell=Car, existence="many", permissions="create"),
        "Radio": book.bind(spell=Radio, existence="unique", permissions="create"),
    }


def _registry_snapshot(book: Spellbook) -> Dict[str, Any]:
    """Value view of the registry state phases 3-4 leave behind, per owned spell id (no index ULIDs)."""
    registry = book._spell_system_states
    snapshot: Dict[str, Any] = {}
    for spell in book._spells.values():
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
            "sockets": None if topology is None else tuple(
                (s.param_name, s.position, s.socket_kind.name, s.is_collection, s.is_optional, s.target_spell_ids,
                 s.dependency_key, s.contract_key, s.referenced_spell_ids, s.parameter_kind)
                for s in topology.sockets
            ),
        }
    return snapshot


Event = Callable[[Spellbook, Conduit, Dict[str, str]], Any]


def _run_world(fragment: Path, event: Event) -> Tuple[Any, Dict[str, Any]]:
    """Fresh world -> bind -> dynamic conjure -> event -> (event outcome, registry snapshot)."""
    book = _new_world_book(FRAME, fragment)
    ids = _bind_world(book)
    conduit = book.conjure(name="root", dynamic=True)
    outcome = event(book, conduit, ids)
    return outcome, _registry_snapshot(book)


def _event_post_conjure_bind(book: Spellbook, conduit: Conduit, ids: Dict[str, str]) -> Any:
    """Bind a new consumer after conjure and meld it with the pre-existing providers."""

    class Dashboard:
        def __init__(self, radio: Radio, engine: Engine) -> None:
            self.radio = radio
            self.engine = engine

    Dashboard.__qualname__ = "Dashboard"
    dashboard_id = conduit.bind(spell=Dashboard, existence="many", permissions="create")
    dashboard = conduit.meld(spell_id=dashboard_id)
    car = conduit.meld(spell=Car)
    return (type(dashboard.radio).__name__, type(dashboard.engine).__name__, type(car.engine).__name__, len(car.wheels))


def _event_notch(book: Spellbook, conduit: Conduit, ids: Dict[str, str]) -> Any:
    """
    Meld Car, stage an alternative Engine into Engine's index, notch it, then meld the new member and Car again.

    The pre-notch meld matches the notch contract's supported order (a dependent melded for the first time after
    a provider notch fails with "generalized manifest references unknown spell_id" on cold and hydrated worlds
    alike - recorded for the owner, outside this lane).
    """
    before = conduit.meld(spell=Car)
    engine_index = book.find_spell_by_id(ids["Engine"]).spell_index
    staged_id = conduit.bind_inactive(spell=EngineAlternative, spell_index=engine_index, existence="unique")
    conduit.notch_spell(spell_index=engine_index, spell=book._inactive_spells[staged_id])
    member = conduit.meld(spell_id=staged_id)
    after = conduit.meld(spell=Car)
    return (
        type(before.engine).__name__, type(member).__name__, type(after.engine).__name__,
        book.find_spell_by_id(staged_id).spell_id == staged_id,
    )


def _event_remove(book: Spellbook, conduit: Conduit, ids: Dict[str, str]) -> Any:
    """Remove the consumer and meld a remaining provider."""
    book.cleanup_and_remove_spell(ids["Car"])
    return (book.find_spell_by_id(ids["Car"]) is None, type(conduit.meld(spell=Engine)).__name__)


def _event_transfer(book: Spellbook, conduit: Conduit, ids: Dict[str, str]) -> Any:
    """Transfer the standalone Radio to another conduit and meld Car in the source."""
    target_book = Spellbook(aetheric_frame=FRAME)
    target = target_book.conjure(name="target", dynamic=True)
    summary = conduit.transfer_spell_ownership(spell=ids["Radio"], target_conduit=target)
    car = conduit.meld(spell=Car)
    return (
        summary["spell_id"] == ids["Radio"],
        book.find_spell_by_id(ids["Radio"]) is None,
        target_book.find_spell_by_id(ids["Radio"]) is not None,
        type(car.engine).__name__,
    )


@pytest.mark.parametrize(
    "event",
    [
        pytest.param(_event_post_conjure_bind, id="bind-after-conjure"),
        pytest.param(_event_notch, id="notch"),
        pytest.param(_event_remove, id="remove-spell"),
        pytest.param(_event_transfer, id="transfer-ownership"),
    ],
)
def test_invalidation_event_after_a_hydrated_conjure_matches_the_cold_world(
        event: Event, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose: Every registry-writing event keeps working unchanged after a replayed conjure.
    Contract: The cold world (path miss) and the hydrated world (path full_hit, no structural run) end with the
        same event outcome and the same registry snapshot.
    """
    spy = _StructuralRunSpy(monkeypatch)
    fragment = _fresh_cache_fragment("_cache_structural_parity_" + event.__name__)

    cold = _run_world(fragment, event)
    warm = _run_world(fragment, event)

    assert spy.root_paths == ["miss", "full_hit"]
    assert spy.runs == len(spy.paths) - 1
    assert warm == cold


def _contract_world(fragment: Path) -> Tuple[Tuple[str, Tuple[str, ...]], Any]:
    """
    Fresh world with a SpellContract consumer and no provider: conjure (gated verdict), then grant the contract
    from a provider conduit and meld. Returns (consumer verdict after conjure, meld outcome).
    """
    book = _new_world_book(FRAME, fragment)
    consumer_id = book.bind(spell=ContractConsumerPrimary, existence=Existence.unique, permissions="create")
    borrower = book.conjure(name="root", dynamic=True)
    consumer = book.find_spell_by_id(consumer_id)
    state = book._spell_system_states.get_by_index_id(consumer.spell_index.id)
    verdict = (state.validity.name, tuple(sorted(flag.name for flag in state.flags)))

    owner_book = Spellbook(aetheric_frame=FRAME)
    service_id = owner_book.bind(
        spell=ContractServicePrimary, existence=Existence.unique, permissions="create",
        spellframe=IService, binding_name="primary",
    )
    owner = owner_book.conjure(name="owner", dynamic=True)
    owner.link(borrower)
    with borrower.transaction("link", conduits=[borrower, owner]):
        assert borrower.add_spell_to_contract(spell_id=service_id, conduit=owner, permissions="create")
    assert borrower.validate_contracts_and_define()
    instance = borrower.meld(spell_id=consumer_id)
    return verdict, (type(instance).__name__, type(instance.service).__name__)


def test_gated_contract_verdict_replays_verbatim_and_the_grant_still_melds(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Purpose: A gated (contract_unvalidated) verdict is replayed as recorded and the contract flow is unchanged.
    Contract: The hydrated consumer carries the same validity and flags as the cold one right after conjure, and
        granting the contract afterwards melds the same objects.
    """
    spy = _StructuralRunSpy(monkeypatch)
    fragment = _fresh_cache_fragment("_cache_structural_parity_contract")

    cold = _contract_world(fragment)
    warm = _contract_world(fragment)

    assert spy.root_paths == ["miss", "full_hit"]
    assert cold[0] == ("gated", ("contract_unvalidated",))
    assert warm == cold


_CHILD_COLD_CONJURE = '''
import sys
from pathlib import Path
sys.path[:0] = [{root!r}, {src!r}]
from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.structural_snapshot_classes import Car, Engine, Radio, Wheel
aether = Aether()
Spellbook._aether = aether
Conduit._aether = aether
configuration = aether._ensure_frame({frame!r}).frame_configuration
configuration.with_system_caching_enabled(True)
configuration.with_system_cache_root_path(Path({fragment!r}))
book = Spellbook(aetheric_frame={frame!r})
book.get_configuration().set_property("phase_scheduler_workers_per_spellbook", 1)
ids = [
    book.bind(spell=Engine, existence="unique", permissions="create"),
    book.bind(spell=Wheel, existence="many", permissions="create"),
    book.bind(spell=Car, existence="many", permissions="create"),
    book.bind(spell=Radio, existence="unique", permissions="create"),
]
book.conjure(name="root", dynamic=True)
print(",".join(ids))
'''


def test_rows_captured_by_another_process_hydrate_this_one(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Purpose: The key and world stamp are value-only, so a bundle written by one process hits in another.
    Contract: A child process conjures cold; this process binds the same classes, classifies full_hit, runs no
        structural phase, and melds Car.
    """
    spy = _StructuralRunSpy(monkeypatch)
    fragment = _fresh_cache_fragment("_cache_structural_parity_two_process")
    code = _CHILD_COLD_CONJURE.format(
        root=str(_REPO_ROOT), src=str(_REPO_ROOT / "src"), frame=FRAME, fragment=str(fragment),
    )
    child = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=120)
    assert child.returncode == 0, child.stderr
    child_ids = child.stdout.strip().split(",")

    book = _new_world_book(FRAME, fragment)
    ids = _bind_world(book)
    conduit = book.conjure(name="root", dynamic=True)

    assert [ids["Engine"], ids["Wheel"], ids["Car"], ids["Radio"]] == child_ids
    assert spy.root_paths == ["full_hit"] and spy.runs == 0
    car = conduit.meld(spell=Car)
    assert isinstance(car.engine, Engine) and len(car.wheels) == 1


def _activate_crystallizer() -> Crystallizer:
    """Activate the Aether-hosted crystallizer with default knobs."""
    configuration = CrystallizerConfiguration().with_defaults()
    configuration.activate()
    crystallizer = Crystallizer()
    crystallizer.activate(configuration)
    return crystallizer


def test_crystallizer_restore_hydrates_with_fresh_index_ulids(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose: Restore parity - a restored world (fresh index ULIDs, same spell ids and posture) still hits.
    Contract: record -> checkpoint -> flush -> fresh boot -> reload -> load_checkpoint conjures the recorded
        root with a full structural hit and no structural run, and the restored conduit melds Car.
    """
    from melder.crystallizer.asset_management import crystallizer_cache

    monkeypatch.setattr(
        crystallizer_cache.CrystallizerCache, "resolve_cache_root_path",
        staticmethod(lambda: tmp_path / "__melder_cache__" / "__crystallizer_cache__"),
    )
    spy = _StructuralRunSpy(monkeypatch)
    fragment = _fresh_cache_fragment("_cache_structural_parity_restore")

    _reset_world()
    crystallizer = _activate_crystallizer()
    frame_configuration = Aether()._ensure_frame(FRAME).frame_configuration
    frame_configuration.with_system_caching_enabled(True)
    frame_configuration.with_system_cache_root_path(fragment)
    configuration = SpellbookConfiguration(aether_frame=FRAME)
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    configuration.finalize()
    book = Spellbook(aetheric_frame=FRAME, configuration=configuration)
    ids = _bind_world(book)
    book.conjure(name="root", dynamic=True)
    checkpoint_id = crystallizer.create_checkpoint()
    crystallizer.flush_checkpoint(checkpoint_id)

    _reset_world()
    rebooted = _activate_crystallizer()
    rebooted.reload_cached_checkpoint(checkpoint_id)
    report = rebooted.load_checkpoint(checkpoint_id)

    assert report["status"] == "complete"
    assert spy.root_paths == ["miss", "full_hit"]
    assert spy.runs == 1
    restored = Aether().get_conduit_by_name("root", aetheric_frame_name=FRAME)
    car = restored.meld(spell=Car)
    assert isinstance(car.engine, Engine) and len(car.wheels) == 1
    assert rebooted.get_spell_crystal(ids["Car"]).id == ids["Car"]

