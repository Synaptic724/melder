"""Rule 2 red tests for Meld: the scan's tests replaced, the structural catch-up covered (melder_1).

usage: python <this script> <tree root> [--check]
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from apply_lib import apply  # noqa: E402  (script-local helper import)

ROOT = pathlib.Path(sys.argv[1])
CHECK = "--check" in sys.argv[2:]

IMPORTS_OLD = """from threading import RLock
from types import SimpleNamespace
from typing import Any, Callable, Iterable, Dict, TYPE_CHECKING
from unittest.mock import MagicMock
"""
IMPORTS_NEW = """from contextlib import contextmanager
from threading import RLock
from types import SimpleNamespace
from typing import Any, Callable, Iterable, Iterator, Dict, Sequence, TYPE_CHECKING
from unittest.mock import MagicMock
"""

IMPORTS2_OLD = """from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
    SpellCompilerArtifact,
)
"""
IMPORTS2_NEW = """from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind
from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
    SpellCompilerArtifact,
)
from melder.aether.spellbook.spell_compiler.topology.spell_local_topology import (
    SpellLocalTopology,
    SpellSocketDescriptor,
)
"""

STATES_OLD = '''    def __init__(self, resolution_state: _ResolutionStateStub) -> None:
        """
        Initialize the stub with a resolution state.
        """
        self._resolution_state = resolution_state

    def get_conduit_resolution_state(self, conduit_id: str) -> _ResolutionStateStub:
        """
        Return the stored resolution state.
        """
        return self._resolution_state
'''
STATES_NEW = '''    def __init__(
            self,
            resolution_state: _ResolutionStateStub,
            *,
            topologies: Dict[str, Any] | None = None,
            states_by_spell_id: Dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize the stub with a resolution state and, for the structural catch-up, the registry's two reads.

        Args:
            resolution_state: The conduit resolution state every conduit id answers with.
            topologies: Version id -> local topology (`get_local_topology_by_id`); none recorded by default.
            states_by_spell_id: Version id -> lineage state exposing `current_spell_id` (`get_by_spell_id`).
        """
        self._resolution_state = resolution_state
        self._topologies: Dict[str, Any] = topologies if topologies is not None else {}
        self._states_by_spell_id: Dict[str, Any] = states_by_spell_id if states_by_spell_id is not None else {}
        self.topology_reads: list[str] = []
        self.topology_read_hooks: list[Callable[[str], None]] = []

    def get_conduit_resolution_state(self, conduit_id: str) -> _ResolutionStateStub:
        """
        Return the stored resolution state.
        """
        return self._resolution_state

    def get_local_topology_by_id(self, spell_id: str) -> Any:
        """
        Return the topology recorded for a version id, or None; record the read and run the read hooks.
        """
        self.topology_reads.append(spell_id)
        for hook in self.topology_read_hooks:
            hook(spell_id)
        return self._topologies.get(spell_id)

    def get_by_spell_id(self, spell_id: str) -> Any:
        """
        Return the lineage state recorded under a version id (old version ids included), or None.
        """
        return self._states_by_spell_id.get(spell_id)
'''

SPELL_INIT_OLD = """        self.run_all_phases_calls = 0
        self.run_structural_phases_calls = 0
"""
SPELL_INIT_NEW = """        self.run_all_phases_calls = 0
        self.run_structural_phases_calls = 0
        self.cleanup_creation_context_calls = 0
        self.clear_phase5_calls = 0
"""

SPELL_METHOD_OLD = '''    def check_cleaned(self) -> None:
        """
        Verify the stub spell has not been cleaned.
'''
SPELL_METHOD_NEW = '''    def _cleanup_creation_context(self) -> None:
        """
        Record a context clear and bump the door epoch first, as Spell._cleanup_creation_context does.
        """
        self.cleanup_creation_context_calls += 1
        self._door_epoch += 1
        self._creation_context = None
        self._creation_context_switch.state = 0
        self._creation_context_switch.fast_state = 0

    def check_cleaned(self) -> None:
        """
        Verify the stub spell has not been cleaned.
'''

COMPILER_OLD = """            and spell._compiler_artifact._root_blueprint_phase5.root_spell_id == spell.spell_index.selected_spell_id
        ),
        cleanup=lambda: None,
    )
    return meld
"""
COMPILER_NEW = """            and spell._compiler_artifact._root_blueprint_phase5.root_spell_id == spell.spell_index.selected_spell_id
        ),
        clear_phase5_artifacts=_record_phase5_clear,
        cleanup=lambda: None,
    )
    return meld


def _record_phase5_clear(spell: _SpellStub) -> None:
    \"\"\"
    Compiler-double `clear_phase5_artifacts`: count the call on the stub spell.
    \"\"\"
    spell.clear_phase5_calls += 1
"""

SCAN_START = "def test_ensure_lineage_resolvable_missing_contract_raises() -> None:\n"
SCAN_END = "def test_force_resolution_revalidation_uses_root_validity_for_root_blueprints() -> None:\n"
SCAN_NEW = '''class _ContractConsumer:
    """
    A consumer whose constructor declares a SpellContract default, as a contract consumer's class does.
    """

    def __init__(self, service: Any = SpellContract(spellframe="svc", binding_name="primary")) -> None:
        self.service = service


def test_ensure_lineage_resolvable_valid_contract_consumer_makes_no_contract_lookup(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify a contract consumer whose state needs no recheck melds with no contract work (rule 2).

    Contract:
        - Structurally valid with a valid conduit verdict: no contracted lookup, no verdict write, no 5-11 pass.
        - A satisfied SpellContract is rechecked only when a provider change marks its consumer.
    """
    spellbook = _SpellbookStub()
    spellbook._run_resolution_phases_for_target_spell = MagicMock()
    resolution_state = _ResolutionStateStub()
    spell = _SpellStub(
        spell_id="spell-1",
        system_state=_SystemStateStub(validity=SpellValidity.valid),
        spell_system_states=_SpellSystemStatesStub(resolution_state),
        spellbook=spellbook,
    )
    spell.spell = _ContractConsumer
    lookup = MagicMock(return_value=None)
    _patch_meld_method(monkeypatch, "_resolve_contracted_by_lookup_key", lookup)
    meld = _make_meld(spellbook=spellbook)

    meld._ensure_lineage_resolvable(spell)

    lookup.assert_not_called()
    spellbook._run_resolution_phases_for_target_spell.assert_not_called()
    assert resolution_state.spell_set_calls == []
    assert resolution_state.root_set_calls == []


def test_ensure_lineage_resolvable_contract_consumer_still_gated_raises_validation_error(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify a marked consumer whose provider is gone fails with the first meld's error.

    Contract:
        - Phase 4 leaves the lineage gated (its SPELL_CONTRACT_MISSING_PROVIDER warning gates it), so the gate
          raises SpellbookValidationError, never the retired scan's MeldExecutionError.
        - No contracted lookup is made.
    """
    spellbook = _SpellbookStub()
    spell = _SpellStub(
        spell_id="spell-1",
        system_state=_SystemStateStub(validity=SpellValidity.gated),
        validity_after_run=SpellValidity.gated,
        spellbook=spellbook,
    )
    spell.spell = _ContractConsumer
    lookup = MagicMock(return_value=None)
    _patch_meld_method(monkeypatch, "_resolve_contracted_by_lookup_key", lookup)
    meld = _make_meld(spellbook=spellbook)

    with pytest.raises(SpellbookValidationError) as raised:
        meld._ensure_lineage_resolvable(spell)

    assert raised.value.broken_spells == [spell]
    assert spell.run_structural_phases_calls == 1
    lookup.assert_not_called()


def test_ensure_lineage_resolvable_gated_contract_consumer_rebuilds_once_with_structure_changed() -> None:
    """
    Verify a marked consumer whose provider is present is rechecked and rebuilt once.

    Contract:
        - The structural rerun makes it valid, the conduit verdict is gated once with `structure_changed`, and
          one 5-11 pass rebuilds it; no second, contract-driven gate follows.
    """
    contract = SpellContract(spellframe="svc", binding_name="primary")
    provider = _SpellStub(spell_id="provider-1")
    spellbook = _SpellbookStub(
        contracted_spells={"peer-1": {provider.spell_index: provider}},
        lookup_contracted_spells={"peer-1": {contract.canonical_key: provider.spell_index}},
    )
    resolution_state = _ResolutionStateStub()
    spell = _SpellStub(
        spell_id="spell-1",
        system_state=_SystemStateStub(validity=SpellValidity.gated),
        validity_after_run=SpellValidity.valid,
        spell_system_states=_SpellSystemStatesStub(resolution_state),
        spellbook=spellbook,
    )
    spell.spell = _ContractConsumer

    def _rebuild(conduit_id: str, target_spell: _SpellStub) -> None:
        """Model a successful 5-11 pass."""
        resolution_state.set_spell_validity(target_spell.spell_id, SpellValidity.valid)

    spellbook._run_resolution_phases_for_target_spell = MagicMock(side_effect=_rebuild)
    meld = _make_meld(spellbook=spellbook)

    meld._ensure_lineage_resolvable(spell)

    gated_writes = [call for call in resolution_state.spell_set_calls if call[1] is SpellValidity.gated]
    assert gated_writes == [("spell-1", SpellValidity.gated, SpellStateChangeReason.structure_changed)]
    spellbook._run_resolution_phases_for_target_spell.assert_called_once_with("conduit-1", spell)


'''

ITER_START = "def test_iter_spell_contract_defaults_skips_non_contract_and_special_params() -> None:\n"
ITER_END = "def test_gated_validation_required_returns_false_without_state() -> None:\n"
ITER_NEW = '''def _normal_topology(version_id: str, targets: Sequence[str]) -> SpellLocalTopology:
    """A local topology with one NORMAL socket per target, as Phase 3 records resolved constructor dependencies."""
    return SpellLocalTopology(
        spell_id=version_id,
        sockets=tuple(
            SpellSocketDescriptor(
                spell_id=version_id,
                param_name=f"dep_{position}",
                position=position,
                socket_kind=SocketKind.NORMAL,
                is_collection=False,
                is_optional=False,
                target_spell_ids=(target,),
            )
            for position, target in enumerate(targets)
        ),
    )


def _contract_socket_topology(version_id: str, key: tuple[str, str]) -> SpellLocalTopology:
    """A local topology with one SPELL_CONTRACT socket and no target, as Phase 3 records a contract consumer."""
    return SpellLocalTopology(
        spell_id=version_id,
        sockets=(
            SpellSocketDescriptor(
                spell_id=version_id,
                param_name="service",
                position=0,
                socket_kind=SocketKind.SPELL_CONTRACT,
                is_collection=False,
                is_optional=False,
                target_spell_ids=(),
                contract_key=key,
            ),
        ),
    )


class _CatchUpWorld:
    """
    A consumer in a Book with stub registry reads, for the meld's structural catch-up (D2).

    Purpose:
        Each dependency is a stub spell in the consumer Book's pool, registered under its version id with its own
        lineage state; `structural_runs` records (Book, spell id) per structural rerun, `passes` each 5-11 pass,
        and `events` both in order.
    """

    def __init__(
            self,
            *,
            consumer_validity: SpellValidity = SpellValidity.gated,
            consumer_targets: Sequence[str] = (),
            resolution_required: bool = False,
    ) -> None:
        """Build the consumer (valid after its own rerun) and its Book, registry and meld."""
        self.resolution_state = _ResolutionStateStub()
        self.topologies: Dict[str, Any] = {}
        self.lineages: Dict[str, Any] = {}
        self.states = _SpellSystemStatesStub(
            self.resolution_state,
            topologies=self.topologies,
            states_by_spell_id=self.lineages,
        )
        self.book = _SpellbookStub()
        self.structural_runs: list[tuple[Any, str]] = []
        self.passes: list[str] = []
        self.events: list[str] = []
        self.after_run: Dict[str, Callable[[], None]] = {}
        self.book._run_resolution_phases_for_target_spell = self._pass
        self.meld = _make_meld(spellbook=self.book)
        self.meld._spell_compiler_system.run_structural_phases = self._run_structural
        self.consumer = self.add(
            "consumer-1",
            validity=consumer_validity,
            targets=consumer_targets,
            in_pool=False,
        )
        self.consumer.resolution_required = resolution_required
        self.consumer.resolution_complete = not resolution_required

    def add(
            self,
            spell_id: str,
            *,
            validity: SpellValidity = SpellValidity.gated,
            after: SpellValidity = SpellValidity.valid,
            targets: Sequence[str] = (),
            book: Any | None = None,
            existing: bool = False,
            broken_after: bool | None = None,
            in_pool: bool = True,
    ) -> _SpellStub:
        """Register one spell: in the pool, its lineage under its id, its topology naming `targets`."""
        spell = _SpellStub(
            spell_id=spell_id,
            system_state=_SystemStateStub(validity=validity),
            validity_after_run=after,
            broken_after_run=broken_after,
            spell_system_states=self.states,
            spellbook=book if book is not None else self.book,
            is_existing_creation=existing,
        )
        if in_pool:
            self.book._spell_id_pool[spell_id] = spell
        self.lineages[spell_id] = SimpleNamespace(current_spell_id=spell_id)
        if targets:
            self.topologies[spell_id] = _normal_topology(spell_id, targets)
        return spell

    def _run_structural(self, spellbook: Any, spell: _SpellStub, cancel_event: Any = None) -> None:
        """Compiler-double structural rerun: record the Book, rerun the stub, run its after-hook."""
        self.structural_runs.append((spellbook, spell.spell_id))
        self.events.append(f"structural:{spell.spell_id}")
        spell.run_structural_phases()
        hook = self.after_run.get(spell.spell_id)
        if hook is not None:
            hook()

    def _pass(self, conduit_id: str, target_spell: _SpellStub) -> None:
        """Stub 5-11 pass: record it and leave the target valid for the conduit."""
        self.passes.append(target_spell.spell_id)
        self.events.append(f"pass:{target_spell.spell_id}")
        self.resolution_state.set_spell_validity(target_spell.spell_id, SpellValidity.valid)

    def runs_of(self, spell_id: str) -> int:
        """How many structural reruns the spell had."""
        return sum(1 for _, run_id in self.structural_runs if run_id == spell_id)


def test_catch_up_refreshes_a_stale_dependency_with_its_owner_book_and_resets_its_plan() -> None:
    """
    Verify the catch-up reruns a stale dependency's phases 1-4 with its owner Book and resets its own plan.

    Contract:
        - A borrowed dependency (owned by another Book) is refreshed with that Book, not the consumer's.
        - Its context and Phase 5+ state are cleared, it owes its own resolution and its door epoch moves, so no
          door keeps serving the plan built for its old structure.
    """
    world = _CatchUpWorld(consumer_targets=("dep-1",))
    lender = _SpellbookStub()
    dep = world.add("dep-1", book=lender)
    epoch_before = dep._door_epoch

    world.meld._ensure_lineage_resolvable(world.consumer)

    assert [(book, run_id) for book, run_id in world.structural_runs if run_id == "dep-1"] == [(lender, "dep-1")]
    assert dep.system_state.validity is SpellValidity.valid
    assert dep.cleanup_creation_context_calls == 1
    assert dep.clear_phase5_calls == 1
    assert dep.resolution_required is True
    assert dep.resolution_complete is False
    assert dep._door_epoch > epoch_before
    assert world.passes == ["consumer-1"]


def test_catch_up_leaves_a_valid_dependency_alone() -> None:
    """Verify a dependency whose lineage is valid is neither rerun nor reset."""
    world = _CatchUpWorld(consumer_targets=("dep-1",))
    dep = world.add("dep-1", validity=SpellValidity.valid)

    world.meld._ensure_lineage_resolvable(world.consumer)

    assert world.runs_of("dep-1") == 0
    assert dep.cleanup_creation_context_calls == 0
    assert dep.resolution_required is False


def test_catch_up_raises_naming_a_broken_dependency_and_pins_it_invalid() -> None:
    """
    Verify a dependency that comes out of its rerun broken stops the meld with an error naming it.

    Contract:
        - SpellbookValidationError lists the dependency; its lineage is pinned invalid, as the gate pins a broken
          melded spell; the consumer's own phases never run.
    """
    world = _CatchUpWorld(consumer_targets=("dep-1",))
    dep = world.add("dep-1", broken_after=True)

    with pytest.raises(SpellbookValidationError) as raised:
        world.meld._ensure_lineage_resolvable(world.consumer)

    assert raised.value.broken_spells == [dep]
    assert dep.system_state.validity is SpellValidity.invalid
    assert world.runs_of("consumer-1") == 0


def test_catch_up_raises_naming_a_dependency_left_gated() -> None:
    """Verify a dependency still gated after its rerun stops the meld with an error naming it."""
    world = _CatchUpWorld(consumer_targets=("dep-1",))
    dep = world.add("dep-1", after=SpellValidity.gated)

    with pytest.raises(SpellbookValidationError) as raised:
        world.meld._ensure_lineage_resolvable(world.consumer)

    assert raised.value.broken_spells == [dep]
    assert dep.cleanup_creation_context_calls == 0


def test_catch_up_does_not_walk_for_a_spell_that_will_not_compile() -> None:
    """
    Verify a spell that is valid with a valid verdict reads no topology, even with a stale dependency.

    Contract:
        - The catch-up runs only when the melded spell compiles at this meld; the warm gate stays a state read.
    """
    world = _CatchUpWorld(consumer_validity=SpellValidity.valid, consumer_targets=("dep-1",))
    world.add("dep-1")

    world.meld._ensure_lineage_resolvable(world.consumer)

    assert world.states.topology_reads == []
    assert world.structural_runs == []


def test_catch_up_follows_a_contract_socket_through_the_books_active_copy() -> None:
    """
    Verify a SPELL_CONTRACT socket leads to the provider copy the Book's active contracted maps hold.

    Contract:
        - The provider is found as Phase 8 finds it (lookup map -> index -> copy) and refreshed with its own Book.
    """
    key = ("svc", "primary")
    world = _CatchUpWorld()
    world.topologies["consumer-1"] = _contract_socket_topology("consumer-1", key)
    lender = _SpellbookStub()
    provider = world.add("provider-1", book=lender)
    world.book._lookup_contracted_spells["peer-1"] = {key: provider.spell_index}
    world.book._contracted_spells["peer-1"] = {provider.spell_index: provider}

    world.meld._ensure_lineage_resolvable(world.consumer)

    assert [(book, run_id) for book, run_id in world.structural_runs if run_id == "provider-1"] == [
        (lender, "provider-1")
    ]


def test_catch_up_walks_the_refreshed_topology_of_a_dependency() -> None:
    """
    Verify the walk goes on through a dependency's topology as its rerun left it.

    Contract:
        - Two hops away: P's rerun now names D, so D is refreshed in the same catch-up.
    """
    world = _CatchUpWorld(consumer_targets=("p-1",))
    world.add("p-1")
    world.add("d-1")
    world.after_run["p-1"] = lambda: world.topologies.__setitem__("p-1", _normal_topology("p-1", ("d-1",)))

    world.meld._ensure_lineage_resolvable(world.consumer)

    assert world.runs_of("p-1") == 1
    assert world.runs_of("d-1") == 1


def test_catch_up_takes_a_recorded_target_to_its_lineages_current_version() -> None:
    """
    Verify a topology naming a superseded version leads to the version its lineage now selects.

    Contract:
        - The registry maps the old version id to the lineage; the pool supplies the current version, which is
          the one refreshed (a notch parked the old one out of the pool).
    """
    world = _CatchUpWorld(consumer_targets=("dep-old",))
    current = world.add("dep-new")
    world.lineages["dep-old"] = SimpleNamespace(current_spell_id="dep-new")

    world.meld._ensure_lineage_resolvable(world.consumer)

    assert world.runs_of("dep-new") == 1
    assert current.resolution_required is True


def test_catch_up_refreshes_a_shared_dependency_once() -> None:
    """Verify a dependency two plan branches share is refreshed once."""
    world = _CatchUpWorld(consumer_targets=("p-1", "p-2"))
    world.add("p-1", validity=SpellValidity.valid, targets=("d-1",))
    world.add("p-2", validity=SpellValidity.valid, targets=("d-1",))
    world.add("d-1")

    world.meld._ensure_lineage_resolvable(world.consumer)

    assert world.runs_of("d-1") == 1


def test_catch_up_holds_no_lock_while_walking_and_only_the_dependencys_while_refreshing() -> None:
    """
    Verify the lock discipline: no spell lock across the walk, the dependency's own lock across its rerun.
    """
    world = _CatchUpWorld(consumer_targets=("dep-1",))
    dep = world.add("dep-1")
    world.consumer._lock = _TrackingLock()
    dep._lock = _TrackingLock()
    held_at_reads: list[tuple[bool, bool]] = []
    world.states.topology_read_hooks.append(
        lambda spell_id: held_at_reads.append((world.consumer._lock.locked, dep._lock.locked))
    )
    held_at_run: list[tuple[bool, bool]] = []
    world.after_run["dep-1"] = lambda: held_at_run.append((world.consumer._lock.locked, dep._lock.locked))

    world.meld._ensure_lineage_resolvable(world.consumer)

    assert held_at_reads and all(held == (False, False) for held in held_at_reads)
    assert held_at_run == [(False, True)]


def test_catch_up_enters_the_dependencys_rebuild_window_before_its_lock(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Verify the refresh enters the dependency's rebuild window first, then its lock (the producer order).
    """
    world = _CatchUpWorld(consumer_targets=("dep-1",))
    dep = world.add("dep-1")
    dep._lock = _TrackingLock()
    windows: list[tuple[str, bool]] = []

    @contextmanager
    def _window(spell: Any) -> Iterator[None]:
        windows.append((spell.spell_id, spell._lock.locked if spell is dep else False))
        yield

    monkeypatch.setattr(Meld, "_rebuild_window", staticmethod(_window))

    world.meld._ensure_lineage_resolvable(world.consumer)

    assert ("dep-1", False) in windows
    assert world.runs_of("dep-1") == 1


def test_catch_up_does_not_reset_a_stale_existing_creation() -> None:
    """
    Verify an existing creation is refreshed structurally but its plan is left alone (it never plans).
    """
    world = _CatchUpWorld(consumer_targets=("dep-1",))
    dep = world.add("dep-1", existing=True)

    world.meld._ensure_lineage_resolvable(world.consumer)

    assert world.runs_of("dep-1") == 1
    assert dep.cleanup_creation_context_calls == 0
    assert dep.clear_phase5_calls == 0
    assert dep.resolution_required is False


def test_deferred_lane_runs_the_catch_up_before_its_pass() -> None:
    """
    Verify a spell owing its resolution refreshes its stale dependencies before its own pass compiles.
    """
    world = _CatchUpWorld(consumer_validity=SpellValidity.valid, consumer_targets=("dep-1",), resolution_required=True)
    world.add("dep-1")

    world.meld._ensure_runtime_resolution_ready(world.consumer)

    assert world.events == ["structural:dep-1", "pass:consumer-1"]
    assert world.consumer.resolution_required is False


def test_gate_leaves_the_catch_up_to_the_deferred_lane() -> None:
    """
    Verify the gate does not walk for a spell owing its resolution: the deferred lane, which every door runs right
    after the gate, walks once before it compiles.
    """
    world = _CatchUpWorld(consumer_validity=SpellValidity.valid, consumer_targets=("dep-1",), resolution_required=True)
    world.add("dep-1")

    world.meld._ensure_lineage_resolvable(world.consumer)

    assert world.states.topology_reads == []
    assert world.structural_runs == []


def test_catch_up_rechecks_staleness_under_the_dependencys_lock(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Verify a dependency another meld refreshed while this one waited for its window is not refreshed again.
    """
    world = _CatchUpWorld(consumer_targets=("dep-1",))
    dep = world.add("dep-1")
    windows: list[str] = []

    @contextmanager
    def _window(spell: Any) -> Iterator[None]:
        windows.append(spell.spell_id)
        if spell is dep:
            dep.system_state.validity = SpellValidity.valid
        yield

    monkeypatch.setattr(Meld, "_rebuild_window", staticmethod(_window))

    world.meld._ensure_lineage_resolvable(world.consumer)

    assert "dep-1" in windows
    assert world.runs_of("dep-1") == 0
    assert dep.cleanup_creation_context_calls == 0


'''

STEPS = [
    ("one", IMPORTS_OLD, IMPORTS_NEW, ""),
    ("one", IMPORTS2_OLD, IMPORTS2_NEW, ""),
    ("one", STATES_OLD, STATES_NEW, ""),
    ("one", SPELL_INIT_OLD, SPELL_INIT_NEW, ""),
    ("one", SPELL_METHOD_OLD, SPELL_METHOD_NEW, ""),
    ("one", COMPILER_OLD, COMPILER_NEW, ""),
    ("between", SCAN_START, SCAN_END, SCAN_NEW),
    ("between", ITER_START, ITER_END, ITER_NEW),
]

apply(ROOT, "tests/unit/melder/aether/conduit/meld/test_meld.py", STEPS, CHECK)
