"""Generate demanded-site selection without constructing or comparing input values.

The selector callback owns native admission and claim retention. This adapter
only orders callback requests using the compact program's prepared guards and
returns the found values needed by its constructor program. No lock, store,
retry loop or application input value belongs to this compiler artifact.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    from context_compass.artifacts.override_occurrence_discovery_20260924.compact_alias_plan import (
        CompactPlan,
    )


class CompactClaimPrelude:
    """Own generated selection code; retain no graph, store or application values.

    The cold constructor consumes a prepared compact plan. At runtime,
    prepare(select) calls select(site_index) once for each demanded shared site,
    consumer first, and returns a fresh Spell-ID -> found-object mapping.
    The callback must retain its decision until the caller finishes construction
    or releases the attempt. A contention exception propagates unchanged.
    """

    def __init__(self, plan: CompactPlan) -> None:
        """Compile a value-only selection schedule without invoking the callback."""
        self.source = self.render(plan)
        self.namespace: dict[str, object] = {}
        exec(compile(self.source, "<compact-claim-prelude>", "exec"), self.namespace)
        self.function = self.namespace["prepare"]

    def cleanup(self) -> None:
        """Release the generated namespace; never release claims owned by the caller."""
        self.namespace.clear()
        self.function = None

    def prepare(self, select: Callable[[int], tuple[bool, object]]) -> dict[str, object]:
        """Select only demanded shared sites and return this attempt's found values.

        Args:
            select: Native adapter returning (found, object) for one site while
                retaining the matching claim. Falsey objects are valid hits;
                only the explicit found boolean controls presence.

        Returns:
            A fresh mapping containing hits only. No graph or prepared guard
            metadata is mutated and no result is cached by this object.

        Raises:
            Any callback exception, unchanged. Earlier claims remain the
            callback owner's responsibility to release. No retries happen here.

        Contract:
            No application constructor or input-value comparison runs. A reused
            parent disables callbacks needed only by its constructor descendants.
            Every consumer is processed before a shared provider's selection.
        """
        return self.function(select)

    @staticmethod
    def _schedule(plan: CompactPlan) -> tuple[dict[str, int], tuple[int, ...]]:
        """Find necessary guard instructions and attach each reuse probe to its site.

        Reuse instructions have implicit dependency on their site's demand guard.
        That dependency is added here before taking the instruction closure.
        Prepared construction order guarantees demand precedes the corresponding
        reuse result, so generated code remains a straight-line ordered program.
        """
        sites = {spell_id: index for index, (spell_id, shared, _sockets) in enumerate(plan.graph.rows) if shared}
        assert len(sites) == sum(shared for _spell, shared, _sockets in plan.graph.rows)
        pending = []
        for operation, (kind, _arguments, key) in enumerate(plan.guards.rows):
            if kind == "reuse" and plan.demand[sites[key]] != 0:
                assert plan.demand[sites[key]] < operation
                pending.append(operation)
        live: set[int] = set()
        while pending:
            operation = pending.pop()
            if operation in live:
                continue
            live.add(operation)
            kind, arguments, key = plan.guards.rows[operation]
            pending.extend(arguments)
            if kind == "reuse":
                pending.append(plan.demand[sites[key]])
        return sites, tuple(sorted(live))

    @staticmethod
    def render(plan: CompactPlan) -> str:
        """Emit the callback protocol with no runtime graph walk or value binding."""
        sites, operations = CompactClaimPrelude._schedule(plan)
        lines = ["def prepare(select):",
                 '    """Return settled shared hits; callback owns all native claims."""',
                 "    reused = {}"]
        for operation in operations:
            kind, arguments, key = plan.guards.rows[operation]
            if kind == "reuse":
                site = sites[key]
                lines.extend((
                    f"    if g{plan.demand[site]}:",
                    f"        found{operation}, value{operation} = select({site})",
                    f"        g{operation} = found{operation}",
                    f"        if found{operation}:",
                    f"            reused[{key!r}] = value{operation}",
                    "    else:",
                    f"        g{operation} = False",
                ))
                continue
            if kind in ("true", "false"):
                expression = "True" if kind == "true" else "False"
            elif kind == "not":
                expression = f"not g{arguments[0]}"
            else:
                assert kind in ("and", "or")
                expression = f" {kind} ".join(f"g{argument}" for argument in arguments)
            lines.append(f"    g{operation} = {expression}")
        lines.append("    return reused")
        return "\n".join(lines) + "\n"
