"""Remove full-catalog wrapper rebuilding from the native integration experiment.

The first adapter remains unchanged as evidence. This variant binds the real
constructors during initialization and injects call-local publication after each
emitted shared-miss constructor. It still uses the experimental claim protocol
and does not establish production throughput or complete native compatibility.
"""

import re
from typing import TYPE_CHECKING

from context_compass.artifacts.override_occurrence_discovery_20260924.compact_alias_emitter import (
    CompactEmitter,
)
from context_compass.artifacts.override_structural_discovery_20260924.native_compact_adapter import (
    NativeCompactAdapter,
    RetryClaim,
    SelectionAttempt,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from context_compass.artifacts.override_occurrence_discovery_20260924.compact_alias_plan import (
        CompactPlan,
    )
    from context_compass.artifacts.override_occurrence_discovery_20260924.graph_slice_probe import (
        World,
    )
    from context_compass.artifacts.override_structural_discovery_20260924.entry_claim_probe import (
        ClaimCoordinator,
    )
    from melder.aether.conduit.meld.meld import Meld


class DirectAttempt(SelectionAttempt):
    """Publish a generated constructor result under this call's retained entry claim."""

    def publish(self, index: int, value: object) -> None:
        """Register only a demanded shared miss, using existing native disposal metadata."""
        entry = self.entries[index]
        assert entry in self.held and not self.observations[entry][0]
        with entry.store._lock:
            entry.store.add_creation(
                entry.spell.spell_id, value,
                has_disposal_methods=entry.spell.has_disposal_methods,
                disposal_methods=entry.spell.disposal_method_names,
            )
        self.observations[entry] = True, value


class DirectNativeCompactAdapter(NativeCompactAdapter):
    """Keep constructor binding cold and publication proportional to actual shared misses.

    Initialization reuses the first prototype's scope/entry binding and then
    replaces its emitted body. That duplicates cold compilation in this bounded
    experiment; production should share the cold builder. No full base catalog
    is scanned during execute, and no mutable current-call state is shared.
    """

    def __init__(
        self, world: World, plan: CompactPlan,
        prepare: Callable[[Callable[[int], tuple[bool, object]]], dict[str, object]],
        coordinator: ClaimCoordinator, meld: Meld, *, explicit_space: bool = False,
    ) -> None:
        """Bind the tested native scope metadata, then install the direct-publication body."""
        super().__init__(world, plan, prepare, coordinator, meld, explicit_space=explicit_space)
        self._bind_direct_body()

    def _bind_direct_body(self) -> None:
        """Install direct constructor bindings once after normal prototype initialization."""
        self.namespace["_constructors"] = tuple(spell.spell for spell in self.spells)
        self.source = self.render_direct(self.plan)
        exec(compile(self.source, "<native-compact-direct-experiment>", "exec"), self.namespace)
        self.function = self.namespace["execute"]

    @staticmethod
    def render_direct(plan: CompactPlan) -> str:
        """Add publication at known generated shared-constructor statements only.

        This cold transformation accepts only the trusted CompactEmitter shape.
        It checks every matched result/constructor index and the publication
        count, so a changed emitter cannot silently omit native registration.
        """
        base = CompactEmitter.render(plan).splitlines()
        assert base[0] == "def execute(raw, reused):"
        lines = ["def execute(raw, reused, publish):"]
        published = set()
        for line in base[1:]:
            lines.append(line)
            match = re.fullmatch(r"(\s*)n(\d+) = _constructors\[(\d+)\]\(.*\)", line)
            if match is None:
                continue
            assert match[2] == match[3]
            index = int(match[2])
            if plan.graph.rows[index][1]:
                assert index not in published
                published.add(index)
                lines.append(f"{match[1]}publish({index}, n{index})")
        expected = {index for index in plan.graph.order
                    if plan.graph.rows[index][1] and plan.demand[index] != 0 and plan.construct[index] != 0}
        assert published == expected
        return "\n".join(lines) + "\n"

    def execute(self, raw: dict[str, object]) -> tuple[object, tuple[int, ...], int]:
        """Run demanded selection and direct generated calls with a call-local publisher.

        Constructor operands already live in the immutable generated namespace.
        Retries remain confined to the prelude; neither construction nor input
        comparisons can be replayed by the contention handler.
        """
        with self._admitted():
            for count in range(1, 33):
                attempt = DirectAttempt(self.entries)
                contested = None
                try:
                    try:
                        reused = self.prepare(attempt.select)
                    except RetryClaim as retry:
                        contested = retry.entry
                    if contested is None:
                        result = self.function(raw, reused, attempt.publish)
                        return result, tuple(attempt.selected), count
                finally:
                    attempt.cleanup()
                self.retry_waiting.set()
                if not contested.lock.acquire(timeout=5):
                    raise TimeoutError("The native diagnostic claim did not become available.")
                contested.lock.release()
        raise RuntimeError("Native compact diagnostic retry bound reached before construction.")
