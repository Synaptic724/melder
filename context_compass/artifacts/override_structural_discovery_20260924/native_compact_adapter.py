"""Join compact generated construction with experimental claims over native stores.

This adapter is deliberately outside production. Definitions must already be
compiled and stable. All participating writers must share the coordinator;
ordinary legacy creation/purge paths are not transparently upgraded by it.
It models demand-driven claims, retry before construction and native publication.
"""

from collections.abc import Callable
from contextlib import contextmanager
from functools import partial
from threading import Event
from typing import TYPE_CHECKING

from context_compass.artifacts.override_occurrence_discovery_20260924.alias_demand_probe import (
    AliasInputConflict,
    PreparedShapeMismatch,
)
from context_compass.artifacts.override_occurrence_discovery_20260924.compact_alias_emitter import (
    CompactEmitter,
)
from context_compass.artifacts.override_structural_discovery_20260924.entry_claim_probe import (
    ClaimCoordinator,
)
from melder.aether.spellbook.existence.existence import Existence

if TYPE_CHECKING:
    from collections.abc import Iterator

    from context_compass.artifacts.override_occurrence_discovery_20260924.compact_alias_plan import (
        CompactPlan,
    )
    from context_compass.artifacts.override_occurrence_discovery_20260924.graph_slice_probe import (
        World,
    )
    from context_compass.artifacts.override_structural_discovery_20260924.entry_claim_probe import (
        Entry,
    )
    from melder.aether.conduit.creations.creations import Creations
    from melder.aether.conduit.meld.meld import Meld


class RetryClaim(Exception):
    """Request a pre-construction retry after releasing every claim held so far."""

    def __init__(self, entry: Entry) -> None:
        """Borrow the contested entry for waiting after the failed attempt is cleaned."""
        super().__init__(entry.spell.spell_id)
        self.entry = entry


class SelectionAttempt:
    """Own one call's writer claims and reuse observations; never cache them."""

    def __init__(self, entries: dict[int, Entry]) -> None:
        """Borrow static site-to-entry bindings and start an empty demand trace."""
        self.entries = entries
        self.held: list[Entry] = []
        self.observations: dict[Entry, tuple[bool, object]] = {}
        self.selected: list[int] = []

    def cleanup(self) -> None:
        """Release claims before dropping selected object references."""
        for entry in reversed(self.held):
            entry.lock.release()
        self.held.clear()
        self.observations.clear()

    def select(self, index: int) -> tuple[bool, object]:
        """Settle a demanded shared site or request retry without constructing anything."""
        self.selected.append(index)
        entry = self.entries[index]
        if entry in self.observations:
            return self.observations[entry]
        if not entry.lock.acquire(False):
            raise RetryClaim(entry)
        self.held.append(entry)
        with entry.store._lock:
            present = entry.spell.spell_id in entry.store._creations
            value = entry.store._creations.get(entry.spell.spell_id)
        self.observations[entry] = present, value
        return present, value

    def construct(self, entry: Entry, constructor: Callable[..., object], **kwargs: object) -> object:
        """Invoke a claimed miss factory outside the store lock, then publish natively.

        This is a class-fixture adapter. Registration uses the existing Spell
        identity and disposal metadata; no alternate live-object store is added.
        Generated calls may only reach this method after the entire prelude has
        succeeded. A later constructor error is propagated and never retried.
        """
        assert entry in self.held and not self.observations[entry][0]
        value = constructor(**kwargs)
        with entry.store._lock:
            entry.store.add_creation(
                entry.spell.spell_id, value,
                has_disposal_methods=entry.spell.has_disposal_methods,
                disposal_methods=entry.spell.disposal_method_names,
            )
        self.observations[entry] = True, value
        return value


class NativeCompactAdapter:
    """Borrow a compact prelude and run generated calls under demanded writer claims.

    The generated body is compiled once. Per-call constructor operands close over
    that call's claims, so concurrent calls do not share a mutable current-call
    field or a value cache. The prototype intentionally makes no speed claim.
    Scope lookup is here, above Creations. Only prevalidated class fixtures are
    admitted; full native validation, transfer and mutation integration remain open.
    """

    def __init__(
        self, world: World, plan: CompactPlan,
        prepare: Callable[[Callable[[int], tuple[bool, object]]], dict[str, object]],
        coordinator: ClaimCoordinator, meld: Meld, *, explicit_space: bool = False,
    ) -> None:
        """Bind current native stores and compile a body with call-local constructor operands."""
        self.world = world
        self.plan = plan
        self.prepare = prepare
        self.coordinator = coordinator
        self.meld = meld
        self.explicit_space = explicit_space
        self.retry_waiting = Event()
        self.root = world.book._spell_id_pool[world.root_id]
        self.epoch = self.root._door_epoch
        self.context = self.root._get_or_build_creation_context()
        self.spells = tuple(world.book._spell_id_pool[row[0]] for row in plan.graph.rows)
        self.entries: dict[int, Entry] = {}
        for index, (_spell_id, shared, _sockets) in enumerate(plan.graph.rows):
            if shared:
                self.entries[index] = coordinator.entry(self._store(index), self.spells[index])
        source = CompactEmitter.render(plan)
        original = "def execute(raw, reused):"
        assert source.startswith(original)
        source = source.replace(original, "def execute(raw, reused, _constructors):", 1)
        self.namespace = {"_keys": plan.keys, "_Mismatch": PreparedShapeMismatch, "_Conflict": AliasInputConflict}
        exec(compile(source, "<native-compact-adapter-experiment>", "exec"), self.namespace)
        self.function = self.namespace["execute"]

    def cleanup(self) -> None:
        """Drop borrowed bindings after callers finish; stores remain owned by their scopes."""
        self.namespace.clear()
        self.entries.clear()
        self.spells = ()
        del self.function
        del self.prepare
        del self.world
        del self.plan
        del self.coordinator
        del self.meld
        del self.root
        del self.context

    def _store(self, index: int) -> Creations:
        """Mirror native fixture store selection without adding scope policy to Creations."""
        spell = self.spells[index]
        if spell.existence is Existence.unique:
            return spell._owner_creations
        if spell.existence is Existence.unique_per_conduit:
            return self.meld._conduit_creations
        if spell.existence is Existence.unique_per_spell_space:
            assert self.explicit_space
            return self.meld._spellspace_creations
        if spell.existence is Existence.unique_per_conduit_lineage:
            return self.meld._root_creations
        if spell.existence is Existence.unique_per_conduit_cluster:
            return self.meld._cluster_creations.resolved_store()
        raise ValueError("The compact adapter requested a shared claim for a non-shared site.")

    @contextmanager
    def _admitted(self) -> Iterator[None]:
        """Preserve ticket-first native gate ordering around preparation and execution.

        A parked request can outlive its compiled context. Reject a changed
        epoch/context after admission instead of executing the captured plan.
        This is not a substitute for native baseline/provider validation.
        """
        if not self.context._dynamic_environment:
            yield
            return
        conduit_gate = self.world.conduit._creation_gate
        if not self.explicit_space:
            conduit_gate.admit_ticket()
        try:
            gate = self.context._creation_gate
            gate.admit_ticket()
            try:
                if self.root._door_epoch != self.epoch or self.root._creation_context is not self.context:
                    raise RuntimeError("The captured compact plan changed while waiting for admission.")
                yield
            finally:
                gate.unregister_ticket()
        finally:
            if not self.explicit_space:
                conduit_gate.unregister_ticket()

    def execute(self, raw: dict[str, object]) -> tuple[object, tuple[int, ...], int]:
        """Select demanded claims, then execute once; retry only a prelude contention.

        Returns the root, successful demanded-site trace and attempt count for
        diagnostics. Retry is caught only around preparation, so constructor or
        input-comparison exceptions cannot replay application side effects.
        """
        with self._admitted():
            for count in range(1, 33):
                attempt = SelectionAttempt(self.entries)
                contested = None
                try:
                    try:
                        reused = self.prepare(attempt.select)
                    except RetryClaim as retry:
                        contested = retry.entry
                    if contested is None:
                        constructors = tuple(
                            partial(attempt.construct, self.entries[index], spell.spell)
                            if index in self.entries else spell.spell
                            for index, spell in enumerate(self.spells)
                        )
                        result = self.function(raw, reused, constructors)
                        return result, tuple(attempt.selected), count
                finally:
                    attempt.cleanup()
                self.retry_waiting.set()
                if not contested.lock.acquire(timeout=5):
                    raise TimeoutError("The native diagnostic claim did not become available.")
                contested.lock.release()
        raise RuntimeError("Native compact diagnostic retry bound reached before construction.")
