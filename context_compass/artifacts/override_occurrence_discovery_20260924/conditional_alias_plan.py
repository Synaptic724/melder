"""Model conditional alias demand without editing the production compiler.

The prepared plan retains value-free guards and every potentially active input
source. Reuse outcomes are injected and stable for one evaluation. This proves
selection semantics only: native store admission, locks, hooks and disposal are
deliberately absent. Constructor execution is an untimed interpreter.
"""

from typing import TYPE_CHECKING, Optional

from context_compass.artifacts.override_occurrence_discovery_20260924.alias_demand_probe import (
    AliasInputConflict,
    AliasPlan,
    PreparedShapeMismatch,
)

if TYPE_CHECKING:
    from context_compass.artifacts.override_occurrence_discovery_20260924.graph_slice_probe import (
        SliceProbe,
    )
    from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.artifacts.spell_override_targeting_codegen_creation import (
        SpellOverrideTargetSocketRef,
    )


class GuardProgram:
    """Own an interned, value-only boolean instruction schedule.

    Instructions reference earlier instructions or a shared Spell's simulated
    reuse outcome. Caller values and objects never enter this representation.
    Constants and duplicate terms fold during preparation, without enumerating
    combinations of store states. No production complexity bound is claimed.
    """

    FALSE = 0
    TRUE = 1

    def __init__(self) -> None:
        """Initialize false/true instructions and an empty interning index."""
        self.rows: list[tuple[str, tuple[int, ...], str]] = [
            ("false", (), ""), ("true", (), ""),
        ]
        self.index: dict[tuple[str, tuple[int, ...], str], int] = {}

    def cleanup(self) -> None:
        """Release owned value-only metadata; repeated cleanup is harmless."""
        self.rows.clear()
        self.index.clear()

    def emit(self, kind: str, arguments: tuple[int, ...] = (), key: str = "") -> int:
        """Intern one instruction whose argument indices already exist."""
        row = (kind, arguments, key)
        if row not in self.index:
            self.index[row] = len(self.rows)
            self.rows.append(row)
        return self.index[row]

    def invert(self, value: int) -> int:
        """Negate an instruction, folding constants and repeated negation."""
        if value in (self.FALSE, self.TRUE):
            return 1 - value
        if self.rows[value][0] == "not":
            return self.rows[value][1][0]
        return self.emit("not", (value,))

    def combine(self, kind: str, *values: int) -> int:
        """Combine guard terms with AND/OR and prepare constant-free operands."""
        assert kind in ("and", "or")
        absorbing, identity = (self.FALSE, self.TRUE) if kind == "and" else (self.TRUE, self.FALSE)
        if absorbing in values:
            return absorbing
        terms = tuple(sorted(set(values) - {identity}))
        if not terms:
            return identity
        if len(terms) == 1:
            return terms[0]
        return self.emit(kind, terms)

    def evaluate(self, reused: dict[str, object]) -> tuple[bool, ...]:
        """Execute the cached schedule against fixed simulated reuse outcomes.

        Presence determines reuse, including a falsey object. This is not a
        native store probe or a claim about atomic lookup/reservation semantics.
        """
        values: list[bool] = []
        for kind, arguments, key in self.rows:
            if kind == "false":
                value = False
            elif kind == "true":
                value = True
            elif kind == "reuse":
                value = key in reused
            elif kind == "not":
                value = not values[arguments[0]]
            elif kind == "and":
                value = all(values[index] for index in arguments)
            else:
                assert kind == "or"
                value = any(values[index] for index in arguments)
            values.append(value)
        return tuple(values)


class ConditionalSite:
    """Own one physical constructor and the conditions on its logical aliases."""

    def __init__(self, index: int, spell_id: str) -> None:
        """Initialize detached metadata; application references are never retained."""
        self.index, self.spell_id = index, spell_id
        self.aliases: dict[tuple[str, int], int] = {}
        self.inputs: dict[str, list[tuple[SpellOverrideTargetSocketRef, int, int]]] = {}
        self.children: dict[str, list[int]] = {}
        self.collections: set[str] = set()
        self.demand = GuardProgram.FALSE
        self.construct = GuardProgram.FALSE

    def cleanup(self) -> None:
        """Release owned metadata without touching the borrowed application world."""
        self.aliases.clear()
        self.inputs.clear()
        self.children.clear()
        self.collections.clear()


class ConditionalAliasPlan:
    """Prepare potential constructor demand once and bind active operands per call.

    Rules beneath supplied or reused ancestors become inactive under the policy
    being tested. Shared sockets keep all guarded candidates until evaluation;
    a missing active candidate restores its ordinary dependency edge. Physical
    many identity follows the parent site/socket/member, as in the earlier proof.
    """

    def __init__(self, probe: SliceProbe) -> None:
        """Borrow real declarations and own a selector adapter, guards and sites."""
        self.probe = probe
        self.selector = AliasPlan(probe)
        self.guards = GuardProgram()
        self.sites: list[ConditionalSite] = []
        self.identities: dict[tuple, ConditionalSite] = {}
        self.by_spell: dict[str, list[ConditionalSite]] = {}
        self.socket_shape: tuple[tuple[object, ...], ...] = ()
        self.rank_shape: tuple[tuple[object, ...], ...] = ()

    def cleanup(self) -> None:
        """Release owned metadata and selector; the caller cleans the SliceProbe."""
        for site in self.sites:
            site.cleanup()
        self.sites.clear()
        self.identities.clear()
        self.by_spell.clear()
        self.guards.cleanup()
        self.selector.cleanup()
        del self.probe

    def site(self, spell_id: str, parent: int, param: str, member: int) -> ConditionalSite:
        """Keep shared identity singular and many identity relative to its parent."""
        identity = (("shared", spell_id)
                    if spell_id in self.probe.model.instance_shape.shared_spell_ids
                    else ("many", parent, param, member, spell_id))
        found = self.identities.get(identity)
        if found is None:
            found = ConditionalSite(len(self.sites), spell_id)
            self.identities[identity] = found
            self.by_spell.setdefault(spell_id, []).append(found)
            self.sites.append(found)
        return found

    def build(self, raw: dict[str, object]) -> None:
        """Prepare all potential aliases and guarded sources, without retaining values.

        Native dependency order gathers every consumer before its provider,
        including unequal-depth fan-in. Building twice is a diagnostic misuse.
        """
        assert not self.sites
        selected, self.socket_shape, levels, self.rank_shape = self.selector.selection(raw)
        by_owner = {}
        for ref in selected:
            owner = (ref.node_id, self.probe.registry.parent_id(ref.param_path_id))
            by_owner.setdefault(owner, []).append((ref, levels[ref]))
        root = self.site(self.probe.world.root_id, -1, "<root>", 0)
        root.aliases[(root.spell_id, self.probe.registry.root_path_id)] = GuardProgram.TRUE
        processed: set[str] = set()
        for spell_id in reversed(self.probe.model.order_shape.execution_order):
            for site in self.by_spell.get(spell_id, ()):
                self.prepare_site(site, by_owner, processed)
            processed.add(spell_id)
        assert all(site.spell_id in processed for site in self.sites)

    def prepare_site(
        self, site: ConditionalSite,
        by_owner: dict[tuple[str, int], list[tuple[SpellOverrideTargetSocketRef, int]]],
        processed: set[str],
    ) -> None:
        """Gather guarded socket sources before extending a constructor's children."""
        guards = self.guards
        site.demand = guards.combine("or", *site.aliases.values())
        site.construct = site.demand
        if site.spell_id in self.probe.model.instance_shape.shared_spell_ids:
            site.construct = guards.combine("and", site.demand, guards.invert(guards.emit("reuse", key=site.spell_id)))
        for alias, condition in sorted(site.aliases.items()):
            for ref, rank in by_owner.get(alias, ()):
                active = guards.combine("and", condition, site.construct)
                site.inputs.setdefault(ref.param_name, []).append((ref, rank, active))
        topology = self.probe.root._spell_system_states.get_local_topology_by_id(site.spell_id)
        site.collections.update(socket.param_name for socket in topology.sockets if socket.is_collection)
        template = self.probe.logical_graph[min(site.aliases)]
        for param, providers in template.items():
            supplied = guards.combine("or", *(guard for _ref, _rank, guard in site.inputs.get(param, ())))
            edge = guards.combine("and", site.construct, guards.invert(supplied))
            if edge == GuardProgram.FALSE:
                continue
            children = []
            for member, provider in enumerate(providers):
                assert provider[0] not in processed, "Provider processed before all consumers"
                child = self.site(provider[0], site.index, param, member)
                for alias, condition in site.aliases.items():
                    alias_providers = self.probe.logical_graph[alias][param]
                    assert len(alias_providers) == len(providers)
                    assert alias_providers[member][0] == provider[0]
                    alias_key = alias_providers[member]
                    added = guards.combine("and", condition, edge)
                    child.aliases[alias_key] = guards.combine("or", child.aliases.get(alias_key, 0), added)
                children.append(child.index)
            site.children[param] = children

    def bind_values(
        self, raw: dict[str, object], flags: tuple[bool, ...],
    ) -> dict[int, dict[str, object]]:
        """Choose highest-rank active operands and compare only active equal-rank values.

        Equality matches the earlier scalar diagnostic and is not a selected
        production contract for arbitrary objects or user-defined comparisons.
        Conflicts are checked before application constructors in this model.
        """
        selected, shape, _levels, ranked = self.selector.selection(raw)
        if shape != self.socket_shape or ranked != self.rank_shape:
            raise PreparedShapeMismatch("Rebuild for the changed selector/socket specificity layout.")
        values = {}
        for site in self.sites:
            if not flags[site.construct]:
                continue
            bound = {}
            for name, candidates in site.inputs.items():
                active = [(ref, rank) for ref, rank, guard in candidates if flags[guard]]
                if not active:
                    continue
                highest = max(rank for _ref, rank in active)
                winners = [ref for ref, rank in active if rank == highest]
                first = selected[winners[0]]
                if any(selected[ref] != first for ref in winners[1:]):
                    raise AliasInputConflict(f"Active aliases supply conflicting values for parameter {name!r}.")
                bound[name] = first
            values[site.index] = bound
        return values

    def evaluate(self, raw: dict[str, object], reused: Optional[dict[str, object]] = None) -> object:
        """Interpret prepared conditional demand using fixed simulated reuse outcomes.

        Guards, alias maps and possible edges stay unchanged. All value binding
        and constructed objects are local to the call. This does not model a
        native lookup/construction race or reserve any shared store entries.
        """
        reused_values = {} if reused is None else reused
        flags = self.guards.evaluate(reused_values)
        bound = self.bind_values(raw, flags)
        results: dict[int, object] = {}

        def resolve(index: int) -> object:
            """Construct one demanded site, selecting supplied operands before descent."""
            if index in results:
                return results[index]
            site = self.sites[index]
            assert flags[site.demand]
            if not flags[site.construct]:
                results[index] = reused_values[site.spell_id]
                return results[index]
            spell = self.probe.lookup[site.spell_id]
            assert spell.is_class_spell and not spell.has_disposal_methods
            kwargs = dict(bound[index])
            for name, children in site.children.items():
                if name in kwargs:
                    continue
                values = [resolve(child) for child in children]
                if name in site.collections:
                    kwargs[name] = values
                elif values:
                    assert len(values) == 1
                    kwargs[name] = values[0]
            results[index] = spell.spell(**kwargs)
            return results[index]

        return resolve(0)
