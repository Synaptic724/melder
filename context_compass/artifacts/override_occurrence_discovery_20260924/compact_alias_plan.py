"""Experimental physical graph and selector-state compiler.

Unlike the earlier oracle this representation never expands all logical paths.
It accepts the existing TargetSpec grammar, preserves declared-path uniqueness,
and prepares conditional sources on a compact construction DAG. The native
adapter is deliberately restricted to class fixtures without contracts,
positional-only inputs, multi-provider sockets or disposal. This is not a
production replacement, and supplied reuse outcomes are stable test conditions.
"""

import marshal
from typing import TYPE_CHECKING, Optional

from context_compass.artifacts.override_occurrence_discovery_20260924.alias_demand_probe import (
    AliasInputConflict,
    PreparedShapeMismatch,
)
from context_compass.artifacts.override_occurrence_discovery_20260924.conditional_alias_plan import (
    GuardProgram,
)
from melder.aether.spellbook.spell_compiler.dag.target_spec import (
    TargetSpec,
    TargetSpecKind,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from context_compass.artifacts.override_occurrence_discovery_20260924.graph_slice_probe import (
        World,
    )

SocketRow = tuple[str, bool, tuple[int, ...]]
SiteRow = tuple[str, bool, tuple[SocketRow, ...]]
RuleRow = tuple[str, int, tuple[str, ...], str]
InputRow = tuple[int, int, int]


class CompactGraph:
    """Own value-only physical sites and parameter edges, with no path registry.

    Site identities are opaque indices. Shared aliases are represented by
    multiple incoming edges to one site, not duplicated descendant trees.
    Constructor callables are supplied separately at execution and never stored.
    """

    def __init__(self, root: int, rows: tuple[SiteRow, ...]) -> None:
        """Validate the rooted DAG and compute order and declared path multiplicity."""
        self.root, self.rows = root, rows
        self.order = self._order()
        self.path_counts = [0] * len(rows)
        self.path_counts[root] = 1
        for index in self.order:
            for _name, _collection, children in rows[index][2]:
                for child in children:
                    self.path_counts[child] += self.path_counts[index]

    def cleanup(self) -> None:
        """Release owned value metadata; application objects are never owned here."""
        self.rows = ()
        self.order = ()
        self.path_counts.clear()

    def _order(self) -> tuple[int, ...]:
        """Return consumer-before-provider order and refuse cycles explicitly."""
        pending: set[int] = set()
        done: set[int] = set()
        output: list[int] = []

        def visit(index: int) -> None:
            """Read one physical site once while checking the active recursion stack."""
            if index in done:
                return
            if index in pending:
                raise ValueError("The experimental construction graph must be acyclic.")
            pending.add(index)
            for _name, _collection, children in self.rows[index][2]:
                for child in children:
                    visit(child)
            pending.remove(index)
            done.add(index)
            output.append(index)

        visit(self.root)
        return tuple(reversed(output))

    @classmethod
    def from_world(cls, world: World) -> CompactGraph:
        """Adapt current physical injection rows; do not clone/expand occurrence paths.

        Plain parameter names come from the retained topology, rather than
        inferred dependencies. Unsupported fixture semantics fail explicitly;
        they are not silently treated as already qualified by this experiment.
        """
        root = world.book._spell_id_pool[world.root_id]
        model = root._compiler_artifact._spell_codegen_model
        specs = model.injection_shape.instance_specs_by_instance_key
        keys = tuple(specs)
        indexes = {key: index for index, key in enumerate(keys)}
        rows = []
        for key in keys:
            spell = world.book._spell_id_pool[key[0]]
            spec = specs[key]
            assert spell.is_class_spell and not spell.has_disposal_methods
            assert not spec.contract_payload and not spec.uses_positional_override
            topology = root._spell_system_states.get_local_topology_by_id(key[0])
            sockets = []
            for socket in topology.sockets:
                assert socket.socket_kind.name != "SPELL_CONTRACT"
                assert socket.parameter_kind not in ("POSITIONAL_ONLY", "VAR_POSITIONAL", "VAR_KEYWORD")
                source = spec.param_sources.get(socket.param_name)
                children = () if source is None else tuple(indexes[child] for child in source.dependency_keys or ())
                assert len(children) <= 1, "Collection member addressing is outside this bounded adapter."
                sockets.append((socket.param_name, socket.is_collection, children))
            rows.append((key[0], key[0] in model.instance_shape.shared_spell_ids, tuple(sockets)))
        return cls(indexes[model.instance_shape.root_instance_key], tuple(rows))

    def declared_matches(self, rule: RuleRow) -> int:
        """Count declared logical socket matches without enumerating shared paths.

        Uniqueness precedes cuts/reuse. Multiple aliases of the same physical
        socket therefore still make a UNIQUE selector ambiguous, as native
        targeting requires. Integers carry multiplicity without path strings.
        """
        _raw, rank, path, name = rule
        if rank < 3:
            return sum(self.path_counts[index] for index in self.order
                       for parameter, _collection, _children in self.rows[index][2] if parameter == name)
        owners = {self.root: 1}
        for position, segment in enumerate(path):
            next_owners: dict[int, int] = {}
            matches = 0
            for index, count in owners.items():
                for parameter, _collection, children in self.rows[index][2]:
                    if parameter != segment:
                        continue
                    matches += count
                    for child in children:
                        next_owners[child] = next_owners.get(child, 0) + count
            if position == len(path) - 1:
                return matches
            owners = next_owners
        return 0


class CompactPlan:
    """Compile raw selector shapes into a value-only conditional construction program.

    Exact paths propagate (rule, prefix-position) states across physical edges.
    A state merges incoming guards with OR, so repeated shared paths need not be
    enumerated. Broadcast/unique rules use site demand after declaration checks.
    Native lifetime locks and admission are deliberately outside this model.
    """

    VERSION = 1

    def __init__(self, graph: CompactGraph, keys: tuple[str, ...], *, prepared: Optional[tuple] = None) -> None:
        """Borrow graph, retain sorted raw key slots, and build or hydrate value rows."""
        self.graph = graph
        self.keys = tuple(sorted(keys))
        self.guards = GuardProgram()
        self.rules = tuple(self._rule(key) for key in self.keys)
        self.demand = [0] * len(graph.rows)
        self.construct = [0] * len(graph.rows)
        self.inputs: list[dict[str, list[InputRow]]] = [{} for _row in graph.rows]
        self.state_count = 0
        if prepared is None:
            self._build()
        else:
            rows, demand, construct, inputs, state_count = prepared
            self.guards.rows[:] = rows
            self.demand[:] = demand
            self.construct[:] = construct
            self.inputs[:] = inputs
            self.state_count = state_count

    def cleanup(self) -> None:
        """Release prepared metadata without cleaning the borrowed graph."""
        self.guards.cleanup()
        self.demand.clear()
        self.construct.clear()
        self.inputs.clear()
        self.rules = ()
        self.keys = ()

    @staticmethod
    def _rule(raw: str) -> RuleRow:
        """Use Melder's parser and retain only its value fields plus raw operand slot."""
        spec = TargetSpec.parse(raw)
        rank = 3 if spec.kind is TargetSpecKind.PATH else 2 if spec.kind is TargetSpecKind.UNIQUE else 1
        return raw, rank, spec.path or (), spec.param_name or ""

    def _build(self) -> None:
        """Prepare path-state guards and conditional default edges in dependency order."""
        for rule in self.rules:
            count = self.graph.declared_matches(rule)
            if count == 0 or (rule[1] == 2 and count != 1):
                raise ValueError(f"Selector {rule[0]!r} matched {count} declared sockets.")
        states: list[dict[tuple[int, int], int]] = [{} for _row in self.graph.rows]
        self.demand[self.graph.root] = GuardProgram.TRUE
        for rule_index, rule in enumerate(self.rules):
            if rule[1] == 3:
                states[self.graph.root][rule_index, 0] = GuardProgram.TRUE
        for index in self.graph.order:
            self._site(index, states)
        self.state_count = sum(len(state) for state in states)

    def _site(self, index: int, states: list[dict[tuple[int, int], int]]) -> None:
        """Merge all consumer contributions before lowering one site's socket sources."""
        guards = self.guards
        spell_id, shared, sockets = self.graph.rows[index]
        constructing = self.demand[index]
        if shared:
            constructing = guards.combine("and", constructing, guards.invert(guards.emit("reuse", key=spell_id)))
        self.construct[index] = constructing
        for parameter, _collection, children in sockets:
            candidates = []
            for rule_index, (_raw, rank, _path, name) in enumerate(self.rules):
                if rank < 3 and parameter == name:
                    candidates.append((rule_index, rank, constructing))
            for (rule_index, position), guard in states[index].items():
                path = self.rules[rule_index][2]
                if position == len(path) - 1 and path[position] == parameter:
                    candidates.append((rule_index, 3, guards.combine("and", guard, constructing)))
            self.inputs[index][parameter] = candidates
            supplied = guards.combine("or", *(candidate[2] for candidate in candidates))
            edge = guards.combine("and", constructing, guards.invert(supplied))
            for child in children:
                self.demand[child] = guards.combine("or", self.demand[child], edge)
                for (rule_index, position), guard in states[index].items():
                    path = self.rules[rule_index][2]
                    if position < len(path) - 1 and path[position] == parameter:
                        key = (rule_index, position + 1)
                        advance = guards.combine("and", guard, edge)
                        states[child][key] = guards.combine("or", states[child].get(key, 0), advance)

    def bind(self, raw: dict[str, object], flags: tuple[bool, ...]) -> list[dict[str, object]]:
        """Bind new values by cached raw-key slots and resolve active priorities only."""
        if tuple(sorted(raw)) != self.keys:
            raise PreparedShapeMismatch("This compact program requires its original raw selector shape.")
        values = [raw[key] for key in self.keys]
        bound: list[dict[str, object]] = [{} for _row in self.graph.rows]
        for index in self.graph.order:
            if not flags[self.construct[index]]:
                continue
            for parameter, candidates in self.inputs[index].items():
                active = [(rule, rank) for rule, rank, guard in candidates if flags[guard]]
                if not active:
                    continue
                rank = max(level for _rule, level in active)
                winners = [rule for rule, level in active if level == rank]
                value = values[winners[0]]
                if any(values[rule] != value for rule in winners[1:]):
                    raise AliasInputConflict(f"Active aliases conflict at compact site {index}, parameter {parameter!r}.")
                bound[index][parameter] = value
        return bound

    def evaluate(
        self, raw: dict[str, object], constructors: dict[str, Callable[..., object]],
        reused: Optional[dict[str, object]] = None,
    ) -> object:
        """Interpret the physical program under fixed supplied reuse outcomes.

        All input and application references remain call-local. The runtime does
        not rebuild selector states or logical aliases. This interpreter is not
        the proposed generated hot path and makes no native performance claim.
        """
        reuse = {} if reused is None else reused
        flags = self.guards.evaluate(reuse)
        bound = self.bind(raw, flags)
        results: dict[int, object] = {}

        def resolve(index: int) -> object:
            """Resolve a demanded physical site once, respecting supplied arguments."""
            if index in results:
                return results[index]
            spell_id, _shared, sockets = self.graph.rows[index]
            assert flags[self.demand[index]]
            if not flags[self.construct[index]]:
                results[index] = reuse[spell_id]
                return results[index]
            kwargs = dict(bound[index])
            for parameter, collection, children in sockets:
                if parameter in kwargs:
                    continue
                if collection:
                    kwargs[parameter] = [resolve(child) for child in children]
                elif children:
                    assert len(children) == 1
                    kwargs[parameter] = resolve(children[0])
            results[index] = constructors[spell_id](**kwargs)
            return results[index]

        return resolve(self.graph.root)

    def dump(self) -> bytes:
        """Serialize only graph, selector and prepared value metadata, never values/code."""
        prepared = (self.guards.rows, self.demand, self.construct, self.inputs, self.state_count)
        return marshal.dumps((self.VERSION, self.graph.root, self.graph.rows, self.keys, prepared))

    @classmethod
    def load(cls, data: bytes) -> CompactPlan:
        """Hydrate a trusted experimental payload; caller must clean its new graph too.

        This models a family-owned payload boundary, not a public untrusted
        deserializer or a change to Melder's existing cache admission rules.
        """
        version, root, rows, keys, prepared = marshal.loads(data)
        if version != cls.VERSION:
            raise ValueError("Unsupported compact diagnostic schema.")
        return cls(CompactGraph(root, rows), keys, prepared=prepared)
