"""Lower the compact experimental plan to direct Python calls and boolean guards.

This is code-generation viability evidence, not native store/lifecycle integration.
The emitted function receives fixed reuse outcomes and fresh input values. It
performs no logical-path traversal or physical graph walk during execution.
"""

from typing import TYPE_CHECKING, Optional

from context_compass.artifacts.override_occurrence_discovery_20260924.alias_demand_probe import (
    AliasInputConflict,
    PreparedShapeMismatch,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from context_compass.artifacts.override_occurrence_discovery_20260924.compact_alias_plan import (
        CompactPlan,
    )


class CompactEmitter:
    """Own a generated function and its namespace; borrow application constructors."""

    def __init__(self, plan: CompactPlan, constructors: dict[str, Callable[..., object]]) -> None:
        """Lower a prepared shape once; no application objects are created here."""
        self.namespace = {
            "_keys": plan.keys, "_Mismatch": PreparedShapeMismatch, "_Conflict": AliasInputConflict,
            "_constructors": tuple(constructors[row[0]] for row in plan.graph.rows),
        }
        self.source = self.render(plan)
        exec(compile(self.source, "<compact-alias-experiment>", "exec"), self.namespace)
        self.function = self.namespace["execute"]

    def cleanup(self) -> None:
        """Drop namespace references without disposing borrowed application constructors."""
        self.namespace.clear()
        self.function = None

    def evaluate(self, raw: dict[str, object], reused: Optional[dict[str, object]] = None) -> object:
        """Run the generated program with fresh values and fixed simulated reuse."""
        return self.function(raw, {} if reused is None else reused)

    @staticmethod
    def render(plan: CompactPlan) -> str:
        """Emit scalar guards, input binding and dependency-ordered direct calls."""
        lines = ["def execute(raw, reused):",
                 '    """Execute one prepared experimental shape under fixed reuse outcomes."""',
                 "    if tuple(sorted(raw)) != _keys:",
                 "        raise _Mismatch('Selector shape changed.')"]
        for index, key in enumerate(plan.keys):
            lines.append(f"    v{index} = raw[{key!r}]")
        for index in CompactEmitter._live_guards(plan):
            kind, arguments, key = plan.guards.rows[index]
            if kind in ("true", "false"):
                expression = "True" if kind == "true" else "False"
            elif kind == "reuse":
                expression = f"{key!r} in reused"
            elif kind == "not":
                expression = f"not g{arguments[0]}"
            else:
                assert kind in ("and", "or")
                expression = f" {kind} ".join(f"g{argument}" for argument in arguments)
            lines.append(f"    g{index} = {expression}")
        for index in plan.graph.order:
            CompactEmitter._inputs(plan, index, lines)
        for index in reversed(plan.graph.order):
            CompactEmitter._constructor(plan, index, lines)
        lines.append(f"    return n{plan.graph.root}")
        return "\n".join(lines) + "\n"

    @staticmethod
    def _live_guards(plan: CompactPlan) -> tuple[int, ...]:
        """Keep only guard instructions needed by potentially demanded constructors."""
        pending = []
        for index in plan.graph.order:
            if plan.demand[index] == 0:
                continue
            pending.extend((plan.demand[index], plan.construct[index]))
            if plan.construct[index] != 0:
                pending.extend(guard for candidates in plan.inputs[index].values()
                               for _rule, _rank, guard in candidates if guard != 0)
        live: set[int] = set()
        while pending:
            index = pending.pop()
            if index not in live:
                live.add(index)
                pending.extend(plan.guards.rows[index][1])
        return tuple(sorted(live))

    @staticmethod
    def _binding_mode(candidates: list[tuple[int, int, int]]) -> str:
        """Distinguish no supply, statically fixed supply, and conditional supply."""
        active = [candidate for candidate in candidates if candidate[2] != 0]
        if not active:
            return "absent"
        return "fixed" if all(candidate[2] == 1 for candidate in active) else "conditional"

    @staticmethod
    def _inputs(plan: CompactPlan, index: int, lines: list[str]) -> None:
        """Emit value selection for each socket; retain runtime equal-rank comparisons."""
        if plan.construct[index] == 0:
            return
        for position, (_parameter, candidates) in enumerate(plan.inputs[index].items()):
            mode = CompactEmitter._binding_mode(candidates)
            if mode == "absent":
                continue
            stem = f"p{index}_{position}"
            if mode == "fixed":
                highest = max(rank for _rule, rank, guard in candidates if guard == 1)
                winners = [rule for rule, rank, guard in candidates if rank == highest and guard == 1]
                lines.append(f"    {stem} = v{winners[0]}")
                for rule in winners[1:]:
                    lines.extend((f"    if {stem} != v{rule}:",
                                  f"        raise _Conflict('Active aliases conflict at compact site {index}.')"))
                continue
            lines.extend((f"    {stem}_bound = False", f"    {stem}_rank = 0", f"    {stem} = None"))
            for rule, rank, guard in candidates:
                if guard == 0:
                    continue
                lines.extend((
                    f"    if g{guard}:",
                    f"        if not {stem}_bound or {rank} > {stem}_rank:",
                    f"            {stem}, {stem}_rank, {stem}_bound = v{rule}, {rank}, True",
                    f"        elif {rank} == {stem}_rank and {stem} != v{rule}:",
                    f"            raise _Conflict('Active aliases conflict at compact site {index}.')",
                ))

    @staticmethod
    def _constructor(plan: CompactPlan, index: int, lines: list[str]) -> None:
        """Emit one guarded constructor with direct dependency operands.

        Optional plain parameters whose supply changes with reuse use a small
        conditional kwargs mapping. Required/default-provider inputs use direct
        keyword expressions. No plan or socket table is visited by emitted code.
        """
        if plan.demand[index] == 0:
            return
        spell_id, _shared, sockets = plan.graph.rows[index]
        indent = "    "
        if plan.demand[index] != 1:
            lines.append(f"{indent}if g{plan.demand[index]}:")
            indent += "    "
        branching = plan.construct[index] != 1 and plan.construct[index] != plan.demand[index]
        if branching:
            lines.append(f"{indent}if g{plan.construct[index]}:")
            indent += "    "
        arguments = []
        optional = []
        positions = {name: position for position, name in enumerate(plan.inputs[index])}
        for parameter, collection, children in sockets:
            assert parameter.isidentifier()
            candidates = plan.inputs[index][parameter]
            mode = CompactEmitter._binding_mode(candidates)
            stem = f"p{index}_{positions[parameter]}"
            if mode == "fixed":
                arguments.append(f"{parameter}={stem}")
                continue
            if collection:
                default = "[" + ", ".join(f"n{child}" for child in children) + "]"
            elif children:
                assert len(children) == 1
                default = f"n{children[0]}"
            else:
                if mode == "conditional":
                    optional.append((parameter, stem))
                continue
            operand = f"({stem} if {stem}_bound else {default})" if mode == "conditional" else default
            arguments.append(f"{parameter}={operand}")
        if optional:
            lines.append(f"{indent}extra{index} = {{}}")
            for parameter, stem in optional:
                lines.extend((f"{indent}if {stem}_bound:", f"{indent}    extra{index}[{parameter!r}] = {stem}"))
            arguments.append(f"**extra{index}")
        lines.append(f"{indent}n{index} = _constructors[{index}]({', '.join(arguments)})")
        if branching:
            lines.extend((f"{indent[:-4]}else:", f"{indent}n{index} = reused[{spell_id!r}]"))
