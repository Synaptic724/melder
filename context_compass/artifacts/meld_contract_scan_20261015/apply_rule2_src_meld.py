"""Rule 2 / D2 source change: the meld gate drops its per-meld contract scan and refreshes stale dependencies (melder_1).

contract_recheck_on_notch_2026_10_16, component_patch_meld_gate. usage: python <this script> <tree root> [--check]
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from apply_lib import apply

ROOT = pathlib.Path(sys.argv[1])
CHECK = "--check" in sys.argv[2:]
REL = "src/melder/aether/conduit/meld/meld.py"

IMPORTS = [
    ("one",
     '''from abc import ABC, abstractmethod
from annotationlib import Format
from contextlib import AbstractContextManager, nullcontext
''',
     '''from abc import ABC, abstractmethod
from contextlib import AbstractContextManager, nullcontext
''', ""),
    ("one",
     '''from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.conduit.meld.creation_context.creation_context_rebuild import (
    CreationContextRebuild,
)
from melder.aether.spellbook.existence.existence import Existence
if TYPE_CHECKING:
''',
     '''from melder.aether.conduit.meld.creation_context.creation_context_rebuild import (
    CreationContextRebuild,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind
if TYPE_CHECKING:
''', ""),
    ("one",
     '''    from melder.aether.aetheric_frame.dev_ops.spell_system_states.conduit_resolution_state import ConduitResolutionState
''',
     '''    from melder.aether.aetheric_frame.dev_ops.spell_system_states.conduit_resolution_state import ConduitResolutionState
    from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_states import SpellSystemStates
''', ""),
]

CLASS_DOC = [
    ("one",
     '''    - enforce structural validity, contract validity, and per-conduit
      resolution validity before instance access
''',
     '''    - enforce structural validity and per-conduit resolution validity before
      instance access; contract validity rides on structural validity (a
      provider change marks its SpellContract consumers, and their structural
      rerun rechecks the contract - no per-meld contract scan, 2026-10-16)
    - before a plan compiles, refresh the structure of every stale dependency
      the plan expands (`_refresh_stale_dependencies`, 2026-10-16)
''', ""),
    ("one",
     '''    3. Enforce validity/change-control gates and rerun lazy phases when needed.
''',
     '''    3. Enforce validity/change-control gates, refresh the stale dependencies a
       compile will expand, and rerun lazy phases when needed.
''', ""),
    ("one",
     '''        Meld is also the gate, not just the resolver: it enforces structural
        validity, contract validity, per-conduit resolution validity, and
        change-control dirty-root state BEFORE any instance is handed back, and
        re-runs the lazy phases when a lineage's validity is UNKNOWN or GATED.
''',
     '''        Meld is also the gate, not just the resolver: it enforces structural
        validity, per-conduit resolution validity, and change-control
        dirty-root state BEFORE any instance is handed back, and re-runs the
        lazy phases when a lineage's validity is UNKNOWN or GATED. Contract
        validity is part of structural validity: a change of the provider a
        SpellContract consumer resolves marks the consumer, and its structural
        rerun (Phase 4) rechecks the contract; a satisfied contract costs no
        per-meld scan (rule 2, 2026-10-16). Before a plan compiles, the gate
        refreshes the structure of every stale dependency the plan expands, so
        no plan is compiled over a dependency's stale topology (D2).
''', ""),
]

GATE_START = "    def _ensure_lineage_resolvable(self, spell: Spell) -> None:\n"
GATE_END = "    @abstractmethod\n    def _describe_spell_live_creation_status("
GATE_NEW = '''    def _ensure_lineage_resolvable(self, spell: Spell) -> None:
        """
        Ensure the spell is structurally valid enough to continue toward
        resolution.

        This is the main pre-resolution validity gate. It combines four
        responsibilities:

        - when the spell will compile at this meld (`_may_compile`), first
          refresh the structure of every stale dependency its plan expands
          (`_refresh_stale_dependencies`, D2 of 2026-10-16); a valid spell with
          a valid verdict reads no topology
        - rerun structural phases when the lineage is unknown or gated; for a
          SpellContract consumer that rerun is the contract recheck: a change
          of its provider marked it `gated`, Phase 4 checks the provider is
          present, and a consumer whose provider is gone stays `gated`, so the
          gate raises the first meld's SpellbookValidationError
        - gate the prior conduit-local resolution verdict after a structural
          rerun so changed dependency selection cannot retain an old executor
        - hand off to per-conduit resolution gating when structural validity is
          no longer the blocking issue; a `resolution_required` spell is left to
          the deferred lane, which every door runs right after this gate

        A satisfied SpellContract is not rechecked on every meld (rule 2,
        2026-10-16): the per-meld contract scan and its forced 5-11 rebuild are
        retired. The borrower Book's contracted-map mutators and the registry's
        downstream walk mark a consumer `gated` when the provider it resolves
        changes, and that state brings the consumer here.

        Threading:
            The catch-up runs first and holds no lock while it walks; it takes
            one stale dependency's rebuild window, then that dependency's lock,
            only while refreshing it. Structural reruns are serialized under
            `spell._lock` so concurrent meld calls do not race duplicate
            validation work. Under dynamic ownership the rerun first enters the
            spell's rebuild window (see `_rebuild_window`): the index gate is
            frozen and drained before the spell lock is taken, because Phase 3
            resets the shared context.

        Args:
            spell: The spell being melded.

        Raises:
            SpellbookValidationError: If structural or conduit-local validity
                cannot be promoted into a runnable state, or if a stale
                dependency comes out of its refresh broken or still not valid
                (the error then lists that dependency).
            MeldExecutionError: If change-control reports the root as dirty for
                the active resolution conduit.
        """
        if self._may_compile(spell):
            self._refresh_stale_dependencies(spell)

        # Structural gating
        if self._gated_validation_required(spell):
            with self._rebuild_window(spell), spell._lock:
                if self._gated_validation_required(spell):
                    self._get_spell_compiler_system().run_structural_phases(
                        self._spellbook,
                        spell,
                    )
                    # If structural validation produced errors, hard-pin to invalid and bail.
                    if spell.is_broken:
                        state = spell.system_state
                        if state is not None:
                            state.set_validity(SpellValidity.invalid)
                        raise SpellbookValidationError([spell])

                    refreshed_state = spell.system_state
                    if refreshed_state is None or refreshed_state.validity is not SpellValidity.valid:
                        raise SpellbookValidationError([spell])
                    self._force_resolution_revalidation(
                        spell, change_reason=SpellStateChangeReason.structure_changed,
                    )

        # Resolution gating (per-conduit)
        if not spell.resolution_required:
            self._ensure_resolution_resolvable(spell)

'''

DEFERRED = [
    ("one",
     '''        Contract:
            - Fast-path no-op when `resolution_required` is False.
            - When required, runs exactly one target-local pass under the
''',
     '''        Contract:
            - Fast-path no-op when `resolution_required` is False.
            - When required, first refreshes the structure of the stale
              dependencies its pass will expand (`_refresh_stale_dependencies`),
              before its own window and lock; the gate leaves that catch-up to
              this lane for a flagged spell (2026-10-16).
            - Then runs exactly one target-local pass under the
''', ""),
    ("one",
     '''            SpellbookValidationError: If a full target pass leaves the spell
                unresolved for the conduit.
            Exception: Re-raises deferred resolution failures.
        """
        # Rebuild window first (dynamic only), then the spell lock: see
        # `_rebuild_window`. Phase 11 resets the shared context.
        with self._rebuild_window(spell), spell._lock:
''',
     '''            SpellbookValidationError: If a full target pass leaves the spell
                unresolved for the conduit, or a stale dependency comes out of
                its refresh broken or not valid (the error lists it).
            Exception: Re-raises deferred resolution failures.
        """
        if spell.resolution_required:
            # The catch-up (D2) runs before this spell's window and lock; it takes
            # each stale dependency's own window and lock, one at a time.
            self._refresh_stale_dependencies(spell)
        # Rebuild window first (dynamic only), then the spell lock: see
        # `_rebuild_window`. Phase 11 resets the shared context.
        with self._rebuild_window(spell), spell._lock:
''', ""),
]

FORCE_DOC = [
    ("one",
     '''            change_reason: Why the compiled resolution must be rebuilt. Existing
                contract callers retain contract_unvalidated by default.
''',
     '''            change_reason: Why the compiled resolution must be rebuilt. The
                gate's structural branch passes `structure_changed`; the default
                `contract_unvalidated` stays for a caller that gates a verdict for
                a contract change (Meld has none since its per-meld contract scan
                was retired, 2026-10-16).
''', ""),
]

SCAN_START = "    def _check_contracts_and_force_revalidation(self, spell: Spell) -> None:\n"
SCAN_END = "    def _force_resolution_revalidation(\n"
HELPERS = '''    def _may_compile(self, spell: Spell) -> bool:
        """
        Decide whether the spell will compile at this meld, so the gate must
        refresh its stale dependencies first.

        Contract:
            - False for a spell flagged `resolution_required`: the deferred
              lane, which every door runs right after the gate, compiles it and
              runs its own catch-up first (`_ensure_runtime_resolution_ready`),
              so the gate does not walk for it twice.
            - True when the lineage has no registered state, or is `unknown` or
              `gated`: the structural branch reruns it and gates its verdict,
              so a 5-11 pass follows.
            - For a `valid` lineage, True exactly when its effective verdict for
              the resolution conduit (`_get_resolution_validity`) is `unknown`
              or `gated`, the verdicts `_ensure_resolution_resolvable` rebuilds.
            - False otherwise: an `invalid`, `disabled` or `cleaned` lineage or
              verdict fails without compiling, and a valid spell with a valid
              verdict compiles nothing, so the gate stays two state reads.
            - Reads state only and mutates nothing.

        Args:
            spell: The spell being melded.

        Returns:
            bool: True when a compile follows at this meld.
        """
        if spell.resolution_required:
            return False
        state = spell.system_state
        if state is None:
            return True
        validity = state.validity
        if validity is SpellValidity.unknown or validity is SpellValidity.gated:
            return True
        if validity is not SpellValidity.valid:
            return False
        conduit_id = self._resolution_conduit_id
        if not conduit_id:
            return False
        resolution_state = spell._spell_system_states.get_conduit_resolution_state(conduit_id)
        verdict = self._get_resolution_validity(spell, resolution_state)
        return verdict is SpellValidity.unknown or verdict is SpellValidity.gated

    @staticmethod
    def _is_stale(spell: Spell) -> bool:
        """
        Report whether a dependency's structure is stale: its lineage is
        registered and `gated` or `unknown`.

        Contract:
            - A registered lineage that is `gated` or `unknown` needs phases 1-4
              before a plan that expands it compiles: a notch, a provider change
              or the registry's downstream walk left it so.
            - A spell with no registered state is not stale: Phase 5 drops an id
              without a registered state from a plan's scope.
            - `invalid`, `disabled` and `cleaned` are not stale either; the
              compiling pass reports them as it always has.
            - Reads state only.

        Args:
            spell: A dependency the plan expands.

        Returns:
            bool: True when the dependency must be refreshed before the plan
                compiles.
        """
        state = spell.system_state
        if state is None:
            return False
        validity = state.validity
        return validity is SpellValidity.gated or validity is SpellValidity.unknown

    def _refresh_stale_dependencies(self, spell: Spell) -> None:
        """
        Refresh the structure of every stale lineage the spell's plan expands,
        before the plan compiles (D2, 2026-10-16).

        Purpose:
            A resolution pass never reruns a dependency's structural phases:
            Phase 8 expands each dependency through the topology that
            dependency's own last Phase 3 recorded, and Phase 5 drops a version
            id a notch took out of the pool. A plan compiled over the stale
            topology of a dependency two hops from a notch misses the parked
            version and records a visibility failure that keeps the spell
            refused. The catch-up reruns phases 1-4 of each stale lineage first
            and resets that lineage's own plan, so it rebuilds at its own next
            meld too.

        Contract:
            - Walks depth first from the spell's recorded topology
              (`_iter_planned_dependencies`) and visits each dependency once;
              the spell itself is never revisited, so a cycle ends the walk.
            - Refreshes a dependency (`_refresh_dependency_structure`) only when
              `_is_stale` says so, and reads its topology after the refresh, so
              the walk follows what the rerun Phase 3 recorded. A valid
              dependency is walked through, not refreshed: a stale lineage
              further down is still reached, once.
            - Resolves through the spell's Book (`spell._spellbook`, the Book
              its resolution pass compiles in) and the spell's registry at every
              depth.

        Threading:
            Holds no lock while walking; each refresh takes one dependency's
            rebuild window and lock and releases both before the walk goes on.
            A topology read takes the registry lock for the read only. The
            caller holds neither this spell's lock nor an index ticket.

        Args:
            spell: The spell about to compile.

        Raises:
            SpellbookValidationError: When a dependency comes out of its refresh
                broken or still not valid (the error lists that dependency).
            RuntimeError: When a dependency must be expanded or refreshed but its
                Book is unavailable.
        """
        spellbook = spell._spellbook
        spell_system_states = spell._spell_system_states
        visited = {spell.spell_id}
        pending = [spell]
        while pending:
            current = pending.pop()
            for dependency in self._iter_planned_dependencies(current, spellbook, spell_system_states):
                if dependency.spell_id in visited:
                    continue
                visited.add(dependency.spell_id)
                if self._is_stale(dependency):
                    self._refresh_dependency_structure(dependency)
                pending.append(dependency)

    def _iter_planned_dependencies(
            self,
            spell: Spell,
            spellbook: Optional[Spellbook],
            spell_system_states: SpellSystemStates,
    ) -> List[Spell]:
        """
        Return the dependencies a plan of `spell` expands, at the versions their
        lineages select now, as Phase 8 expands them.

        Contract:
            - Reads the topology Phase 3 last recorded for the spell's version
              (`get_local_topology_by_id`) before anything else; a spell with no
              recorded topology contributes no dependency and needs no Book.
            - Every socket's `target_spell_ids` is a dependency, as Phase 8's
              topology expansion takes it whatever the socket kind; a
              SPELL_CONTRACT socket with a `contract_key` adds the provider the
              Book's active contracted maps hold for that key (lookup map, then
              index, then copy - the path Phase 8 resolves a contract through).
            - Each dependency is taken to the version its lineage selects now
              (`_current_in_pool`): a recorded id a notch superseded leads to
              the incoming version, and an id the Book's pool does not hold is
              skipped, as Phase 5 drops it.
            - May return one lineage twice (two sockets naming it); the caller's
              visited set keeps one.
            - Walks the outer contracted lookup map through a one-call snapshot;
              every other read is one dict get.

        Args:
            spell: The spell whose recorded topology is expanded.
            spellbook: The compiling Book (the melded spell's), whose pool and
                contracted maps the plan resolves through.
            spell_system_states: The frame's lineage registry.

        Returns:
            List[Spell]: The planned dependencies, current versions only.

        Raises:
            RuntimeError: When the spell has a recorded topology but no Book is
                available to resolve it through.
        """
        topology = spell_system_states.get_local_topology_by_id(spell.spell_id)
        if topology is None:
            return []
        if spellbook is None:
            raise RuntimeError("Spell has no owning Spellbook surface.")
        spell_id_pool = spellbook._spell_id_pool
        dependencies: List[Spell] = []
        for socket in topology.sockets:
            for target_spell_id in socket.target_spell_ids:
                target = self._current_in_pool(spell_system_states, spell_id_pool, target_spell_id)
                if target is not None:
                    dependencies.append(target)
            contract_key = socket.contract_key
            if socket.socket_kind is not SocketKind.SPELL_CONTRACT or contract_key is None:
                continue
            for conduit_id, lookup_map in list(spellbook._lookup_contracted_spells.items()):
                spell_index = lookup_map.get(contract_key)
                if spell_index is None:
                    continue
                contracted_map = spellbook._contracted_spells.get(conduit_id)
                if contracted_map is None:
                    continue
                provider = contracted_map.get(spell_index)
                if provider is None:
                    continue
                target = self._current_in_pool(spell_system_states, spell_id_pool, provider.spell_id)
                if target is not None:
                    dependencies.append(target)
        return dependencies

    @staticmethod
    def _current_in_pool(
            spell_system_states: SpellSystemStates,
            spell_id_pool: Dict[str, Spell],
            spell_id: str,
    ) -> Optional[Spell]:
        """
        Return the active Spell of the lineage a version id belongs to, from the
        compiling Book's pool, or None.

        Contract:
            - The registry maps every version id an index has selected to its
              lineage (`get_by_spell_id`; a notch adds the incoming id and keeps
              the old one), so a superseded id leads to the lineage's current
              version id; an id the registry does not know is looked up as is.
            - Returns the pool's Spell for that id, or None when the Book's pool
              does not hold it (Phase 5 drops such an id from a scope).
            - Reads only.

        Args:
            spell_system_states: The frame's lineage registry.
            spell_id_pool: The compiling Book's active pool (`_spell_id_pool`).
            spell_id: A version id a topology or a contracted map recorded.

        Returns:
            Optional[Spell]: The lineage's active Spell in the Book, or None.
        """
        state = spell_system_states.get_by_spell_id(spell_id)
        current_spell_id = state.current_spell_id if state is not None else spell_id
        return spell_id_pool.get(current_spell_id)

    def _refresh_dependency_structure(self, dependency: Spell) -> None:
        """
        Rerun phases 1-4 of one stale dependency with its owner Book and reset
        its own plan, so neither the compile that found it nor its own next meld
        uses a plan built before its lineage went stale.

        Contract:
            - Enters the dependency's rebuild window, then its lock - the order
              every producer takes - and re-checks staleness under them: a
              dependency another meld refreshed meanwhile is left alone.
            - Runs the structural phases with the dependency's own Book
              (`dependency._spellbook`): a borrowed provider is refreshed by its
              lender's Book, which owns its compiler state.
            - Broken after the rerun: pins the lineage `invalid`, as the gate
              pins a broken melded spell, and raises SpellbookValidationError
              listing the dependency. Still not `valid`, or unregistered: raises
              the same error. Nothing is reset in either case.
            - Valid: an existing creation or a non-resolvable definition is
              left as it is (neither ever plans). Any other dependency is left
              owing its own resolution (`resolution_complete=False`,
              `resolution_required=True`, the flags every meld door reads); its
              CreationContext is cleaned, which moves its door epoch so no
              fast-door entry survives, and its Phase 5+ compiler state is
              cleared, so its next own meld in any conduit runs its full target
              pass (5-11) instead of serving a plan built over its old
              structure. The Phase-5-derived `requires_spellspace_request` is
              kept: the conduit door refuses a spellspace-scoped spell by that
              flag before any pass runs, and the dependency's own next pass
              recomputes it.
            - Writes no verdict: the compiling pass publishes the new ones.

        Threading:
            Holds the dependency's window and lock for the rerun and the reset
            only; the caller holds no other spell lock and no index ticket.

        Args:
            dependency: A stale lineage's active Spell, found by the walk.

        Raises:
            SpellbookValidationError: When the dependency is broken or not valid
                after its rerun.
            RuntimeError: When the dependency has no owning Book.
        """
        spell_compiler_system = self._get_spell_compiler_system()
        with self._rebuild_window(dependency), dependency._lock:
            if not self._is_stale(dependency):
                return
            dependency_book = dependency._spellbook
            if dependency_book is None:
                raise RuntimeError("Spell has no owning Spellbook surface.")
            spell_compiler_system.run_structural_phases(dependency_book, dependency)
            state = dependency.system_state
            if dependency.is_broken:
                if state is not None:
                    state.set_validity(SpellValidity.invalid)
                raise SpellbookValidationError([dependency])
            if state is None or state.validity is not SpellValidity.valid:
                raise SpellbookValidationError([dependency])
            if dependency.is_existing_creation or not dependency._resolvable:
                return
            dependency.resolution_complete = False
            dependency.resolution_required = True
            requires_spellspace_request = dependency.requires_spellspace_request
            dependency._cleanup_creation_context()
            spell_compiler_system.clear_phase5_artifacts(dependency)
            dependency.requires_spellspace_request = requires_spellspace_request

'''

STEPS = IMPORTS + CLASS_DOC + [
    ("between", GATE_START, GATE_END, GATE_NEW),
] + DEFERRED + [
    ("between", SCAN_START, SCAN_END, HELPERS),
] + FORCE_DOC

apply(ROOT, REL, STEPS, CHECK)
