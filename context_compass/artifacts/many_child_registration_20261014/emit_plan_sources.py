"""
Print the site-plan source emitted for representative shapes, so the fix's emission can be diffed before and after.
(TASK-2026-10-14-fix_many_child_follows_holder, invariant 4: every line outside the misses is unchanged.)

Shapes (D is a disposal-bearing `many`, P a plain `many`):
    many_root_over_many        Root(many) -> D                    top-level child (innermost scope, unchanged)
    many_root_over_per_conduit Root(many) -> S(per-conduit) -> D   child inside S's miss
    unique_root_over_many      Root(unique) -> D                   the root's own miss (door route "unique")
    per_conduit_root           Root(per-conduit) -> D              door-held root miss (route "unique_per_conduit")
    nested                     Root(many) -> S(per-conduit) -> U(unique) -> D, and S -> P -> D2
    lineage_and_cluster        Root(many) -> L(lineage) -> D, Root -> C(cluster) -> D2
Each shape is emitted in normal mode (with its door route key) and in override mode with no keys.

Run: PYTHONPATH=<src> python emit_plan_sources.py > out.txt
"""
import sys
import threading
from types import SimpleNamespace
from typing import Any, Dict, List, Optional, Tuple

from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.override_key_resolver import (
    OverrideKeyResolver,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.site_plan_lowering import (
    SitePlanLowering,
    SitePlanStep,
)
from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind
from melder.aether.spellbook.spell_compiler.topology.spell_local_topology import (
    SpellLocalTopology,
    SpellSocketDescriptor,
)


def spell(spell_id: str, existence: Existence, disposal: Tuple[str, ...] = ()) -> SimpleNamespace:
    """A fake spell carrying the attributes the lowering reads."""
    return SimpleNamespace(
        spell=lambda *a, **k: None, spell_id=spell_id, spell_index=SimpleNamespace(selected_spell_id=spell_id),
        spell_name=spell_id, is_class_spell=True, is_method_spell=False, is_lambda_spell=False,
        is_existing_creation=False, has_disposal_methods=bool(disposal), disposal_method_names=list(disposal),
        existence=existence, _lock=threading.RLock(), _owner_creations=None, _dynamic_environment=False,
    )


def step(key: Tuple[str, Optional[int]], sp: SimpleNamespace, *deps: Tuple[str, Tuple[Any, ...]]) -> SitePlanStep:
    """One step view."""
    return SitePlanStep(
        instance_key=key, spell=sp, existence=sp.existence, dependency_resolution_order=tuple(deps),
        collection_param_names=frozenset(), uses_positional_override=False, contract_positional_override=None,
        has_contract_payload=False, contract_payload=None, use_spell_lock_hint=False,
    )


def topology(spell_id: str, *params: str) -> SpellLocalTopology:
    """One local topology with positional sockets named `params`."""
    return SpellLocalTopology(spell_id, tuple(
        SpellSocketDescriptor(
            spell_id=spell_id, param_name=name, position=position, socket_kind=SocketKind.NORMAL,
            is_collection=False, is_optional=False, target_spell_ids=(), parameter_kind="POSITIONAL_OR_KEYWORD",
        )
        for position, name in enumerate(params)
    ))


def shapes() -> List[Tuple[str, Tuple[SitePlanStep, ...], Dict[str, Any], Tuple[str, Optional[int]], Optional[str]]]:
    """Return (name, steps, topologies, root key, door route key) per shape."""
    d = spell("d", Existence.many, ("close",))
    d2 = spell("d2", Existence.many, ("close",))
    p = spell("p", Existence.many)
    many_root = spell("root", Existence.many)
    out = []
    out.append(("many_root_over_many", (
        step(("d", 1), d), step(("root", None), many_root, ("d", (("d", 1),))),
    ), {"root": topology("root", "d"), "d": topology("d")}, ("root", None), "many"))
    s = spell("s", Existence.unique_per_conduit)
    out.append(("many_root_over_per_conduit", (
        step(("d", 2), d), step(("s", None), s, ("d", (("d", 2),))),
        step(("root", None), many_root, ("s", (("s", None),))),
    ), {"root": topology("root", "s"), "s": topology("s", "d"), "d": topology("d")}, ("root", None), "many"))
    unique_root = spell("root", Existence.unique)
    out.append(("unique_root_over_many", (
        step(("d", 1), d), step(("root", None), unique_root, ("d", (("d", 1),))),
    ), {"root": topology("root", "d"), "d": topology("d")}, ("root", None), "unique"))
    pc_root = spell("root", Existence.unique_per_conduit)
    out.append(("per_conduit_root", (
        step(("d", 1), d), step(("root", None), pc_root, ("d", (("d", 1),))),
    ), {"root": topology("root", "d"), "d": topology("d")}, ("root", None), "unique_per_conduit"))
    u = spell("u", Existence.unique)
    out.append(("nested", (
        step(("d", 3), d), step(("u", None), u, ("d", (("d", 3),))),
        step(("d2", 5), d2), step(("p", 4), p, ("d2", (("d2", 5),))),
        step(("s", None), s, ("u", (("u", None),)), ("p", (("p", 4),))),
        step(("root", None), many_root, ("s", (("s", None),))),
    ), {
        "root": topology("root", "s"), "s": topology("s", "u", "p"), "u": topology("u", "d"),
        "p": topology("p", "d2"), "d": topology("d"), "d2": topology("d2"),
    }, ("root", None), "many"))
    lin = spell("l", Existence.unique_per_conduit_lineage)
    clu = spell("c", Existence.unique_per_conduit_cluster)
    out.append(("lineage_and_cluster", (
        step(("d", 2), d), step(("l", None), lin, ("d", (("d", 2),))),
        step(("d2", 4), d2), step(("c", None), clu, ("d2", (("d2", 4),))),
        step(("root", None), many_root, ("l", (("l", None),)), ("c", (("c", None),))),
    ), {
        "root": topology("root", "l", "c"), "l": topology("l", "d"), "c": topology("c", "d2"),
        "d": topology("d"), "d2": topology("d2"),
    }, ("root", None), "many"))
    return out


def main() -> int:
    """Emit every shape in normal and override mode and print the sources."""
    for name, steps, topologies, root_key, route in shapes():
        for normal in (True, False):
            graph = SitePlanLowering.build_site_graph(
                root_spell_id=root_key[0], root_instance_key=root_key, steps=steps, topology_for=topologies.get,
            )
            resolution = OverrideKeyResolver.resolve(graph, ())
            source, _namespace, _masked = SitePlanLowering.emit(
                steps=steps, site_graph=graph, resolution=resolution, root_instance_key=root_key,
                root_spell_id=root_key[0], root_spell_name=root_key[0], arity=0, normal_mode=normal,
                door_route_key=route if normal else None,
            )
            graph.cleanup()
            sys.stdout.write(f"===== {name} ({'normal, route ' + str(route) if normal else 'override, no keys'})\n")
            sys.stdout.write(source)
    return 0


if __name__ == "__main__":
    sys.exit(main())
