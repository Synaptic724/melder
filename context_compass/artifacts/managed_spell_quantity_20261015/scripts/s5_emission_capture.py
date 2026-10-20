"""
S5 emission capture (EPIC-2026-10-14-managed_spell_quantity, B7 gate): emit a broad set of NON-managed site-plan
shapes, the door template bodies and the certification harness worlds' normal plans, and write them to one JSON
file. Run it on the tree before S5 and after; equal files prove every non-managed emission byte-identical.

Run from the tree root: PYTHONPATH=src:. python <this file> <out.json>
"""
import json
import sys
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple

from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets import (
    creation_runtime_door_compiler as door_compiler,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.override_key_resolver import (
    OverrideKeyResolver,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.site_plan_lowering import (
    SitePlanLowering,
    SitePlanStep,
)
from melder.aether.spellbook.spell_compiler.topology.spell_local_topology import SpellLocalTopology
from tests.unit.melder.spellbook.spell_compiler.shared_assets.test_site_plan_lowering import (
    _socket,
    _spell,
    _step,
    _unresolved,
)

MANY = Existence.many
UNIQUE = Existence.unique
UPC = Existence.unique_per_conduit
SPACE = Existence.unique_per_spell_space
LINEAGE = Existence.unique_per_conduit_lineage
CLUSTER = Existence.unique_per_conduit_cluster
SHARED = (UNIQUE, UPC, SPACE, LINEAGE, CLUSTER)
ROUTE = {MANY: "many", UNIQUE: "unique", UPC: "unique_per_conduit", SPACE: "spellspace", LINEAGE: "lineage",
         CLUSTER: "cluster"}


def _key(name: str, existence: Existence, path: int) -> Tuple[str, Optional[int]]:
    return (name, None) if existence is not MANY else (name, path)


def _emit(steps: Tuple[SitePlanStep, ...], topologies: Dict[str, Any], root_key: Tuple[str, Any],
          keys: Tuple[str, ...], door: Optional[str], arity: int = 0) -> Dict[str, Any]:
    normal = not keys and arity == 0
    graph = SitePlanLowering.build_site_graph(
        root_spell_id=root_key[0], root_instance_key=root_key, steps=steps, topology_for=topologies.get,
    )
    try:
        resolution = OverrideKeyResolver.resolve(graph, keys, arity)
        source, namespace, _masked = SitePlanLowering.emit(
            steps=steps, site_graph=graph, resolution=resolution, root_instance_key=root_key,
            root_spell_id=root_key[0], root_spell_name=root_key[0], arity=arity,
            normal_mode=normal, door_route_key=door if normal else None,
        )
        return {"source": source, "names": sorted(namespace)}
    except Exception as exc:
        return {"error": f"{type(exc).__name__}: {exc}"}
    finally:
        graph.cleanup()


def _mark(spells: List[Any], dynamic: bool, owned: bool) -> None:
    for spell in spells:
        spell._dynamic_environment = dynamic
        if not owned:
            spell._owner_creations = None


def t1_shapes(out: Dict[str, Any]) -> None:
    """root(a: A(x: X), b: B, limit=?) over every existence mix."""
    for root_e in (MANY,) + SHARED:
        for a_e in (MANY, UNIQUE, UPC):
            for b_e in (MANY, UNIQUE):
                for x_e in (MANY, UNIQUE):
                    for x_disposal in (False, True):
                        for dynamic, owned, lock in ((False, True, False), (True, True, False),
                                                     (False, False, False), (False, True, True)):
                            built: Counter = Counter()
                            x = _spell("x", built, x_e, ("close",) if x_disposal else ())
                            a, b, root = _spell("a", built, a_e), _spell("b", built, b_e), _spell("root", built, root_e)
                            _mark([x, a, b, root], dynamic, owned)
                            kx, ka, kb, kr = _key("x", x_e, 3), _key("a", a_e, 1), _key("b", b_e, 2), _key("root", root_e, 0)
                            steps = (
                                _step(kx, x, lock_hint=lock and x_e is UNIQUE),
                                _step(ka, a, ("x", (kx,)), lock_hint=lock and a_e is UNIQUE),
                                _step(kb, b, lock_hint=lock and b_e is UNIQUE),
                                _step(kr, root, ("a", (ka,)), ("b", (kb,)), lock_hint=lock and root_e is UNIQUE),
                            )
                            topologies = {
                                "root": SpellLocalTopology("root", (
                                    _socket("root", "a", 0), _socket("root", "b", 1),
                                    _socket("root", "limit", 2, optional=True),
                                )),
                                "a": SpellLocalTopology("a", (_socket("a", "x", 0),)),
                                "b": SpellLocalTopology("b", ()),
                                "x": SpellLocalTopology("x", ()),
                            }
                            tag = f"t1|{root_e.name}|{a_e.name}|{b_e.name}|{x_e.name}|disp={x_disposal}|" \
                                  f"dyn={dynamic}|owned={owned}|lock={lock}"
                            for keys in ((), ("b",), ("a>x",), ("limit",), ("a",)):
                                doors = (None, ROUTE[root_e]) if not keys else (None,)
                                for door in doors:
                                    out[f"{tag}|keys={keys}|door={door}"] = _emit(steps, topologies, kr, keys, door)


def t2_shapes(out: Dict[str, Any]) -> None:
    """root(t: T(s: S(d: D)), d2: D2): nested holders."""
    for root_e in (MANY, UPC, SPACE):
        for t_e in SHARED:
            for s_e in SHARED:
                for d_disposal in (False, True):
                    built: Counter = Counter()
                    d = _spell("d", built, MANY, ("close",) if d_disposal else ())
                    s, t = _spell("s", built, s_e), _spell("t", built, t_e)
                    d2, root = _spell("d2", built, MANY, ("close",)), _spell("root", built, root_e)
                    kd, ks, kt, kd2, kr = ("d", 1), _key("s", s_e, 4), _key("t", t_e, 5), ("d2", 2), _key("root", root_e, 0)
                    steps = (
                        _step(kd, d), _step(ks, s, ("d", (kd,))), _step(kt, t, ("s", (ks,))), _step(kd2, d2),
                        _step(kr, root, ("t", (kt,)), ("d2", (kd2,))),
                    )
                    topologies = {
                        "root": SpellLocalTopology("root", (_socket("root", "t", 0), _socket("root", "d2", 1))),
                        "t": SpellLocalTopology("t", (_socket("t", "s", 0),)),
                        "s": SpellLocalTopology("s", (_socket("s", "d", 0),)),
                    }
                    tag = f"t2|{root_e.name}|{t_e.name}|{s_e.name}|disp={d_disposal}"
                    for keys in ((), ("d2",), ("t>s",), ("t",)):
                        doors = (None, ROUTE[root_e]) if not keys else (None,)
                        for door in doors:
                            out[f"{tag}|keys={keys}|door={door}"] = _emit(steps, topologies, kr, keys, door)


def t3_shapes(out: Dict[str, Any]) -> None:
    """root(a: A(s: S), b: B(s: S)): one shared site under two consumers."""
    for s_e in SHARED:
        for a_e in (MANY, UPC, UNIQUE):
            for b_e in (MANY, UPC):
                built: Counter = Counter()
                s, a, b, root = (_spell("s", built, s_e, ("close",)), _spell("a", built, a_e),
                                 _spell("b", built, b_e), _spell("root", built, MANY))
                ks, ka, kb, kr = _key("s", s_e, 3), _key("a", a_e, 1), _key("b", b_e, 2), ("root", 0)
                steps = (_step(ks, s), _step(ka, a, ("s", (ks,))), _step(kb, b, ("s", (ks,))),
                         _step(kr, root, ("a", (ka,)), ("b", (kb,))))
                topologies = {
                    "root": SpellLocalTopology("root", (_socket("root", "a", 0), _socket("root", "b", 1))),
                    "a": SpellLocalTopology("a", (_socket("a", "s", 0),)),
                    "b": SpellLocalTopology("b", (_socket("b", "s", 0),)),
                }
                tag = f"t3|{s_e.name}|{a_e.name}|{b_e.name}"
                for keys in ((), ("a",), ("*s",), ("**s",)):
                    out[f"{tag}|keys={keys}"] = _emit(steps, topologies, kr, keys, None)


def t4_shapes(out: Dict[str, Any]) -> None:
    """root(items: list[I]) with 1-3 members, many or shared root, plus positional payloads."""
    for root_e in (MANY, UPC):
        for count in (1, 2, 3):
            for i_disposal in (False, True):
                built: Counter = Counter()
                members = [_spell(f"i{n}", built, MANY, ("close",) if i_disposal else ()) for n in range(count)]
                keys_ = [(f"i{n}", n + 1) for n in range(count)]
                root = _spell("root", built, root_e)
                kr = _key("root", root_e, 0)
                steps = tuple(_step(k, m) for k, m in zip(keys_, members)) + (
                    _step(kr, root, ("items", tuple(keys_)), collections=("items",)),
                )
                topologies = {"root": SpellLocalTopology("root", (
                    _socket("root", "items", 0, collection=True), _socket("root", "extra", 1, optional=True),
                ))}
                tag = f"t4|{root_e.name}|n={count}|disp={i_disposal}"
                for keys in ((), ("items",), ("extra",)):
                    out[f"{tag}|keys={keys}"] = _emit(steps, topologies, kr, keys, None)
                for arity in (1, 2, 3):
                    out[f"{tag}|args={arity}"] = _emit(steps, topologies, kr, ("__args__",), None, arity)


def t5_shapes(out: Dict[str, Any]) -> None:
    """A generic (contract payload) step inside a shared miss, and unresolved inputs."""
    for s_e in (UPC, UNIQUE):
        built: Counter = Counter()
        y, z, x = _spell("y", built), _spell("z", built, UPC), _spell("x", built)
        s, root = _spell("s", built, s_e), _spell("root", built)
        generic = SitePlanStep(
            instance_key=("x", 3), spell=x, existence=MANY,
            dependency_resolution_order=(("y", (("y", 4),)), ("z", (("z", None),))),
            collection_param_names=frozenset(), uses_positional_override=False, contract_positional_override=None,
            has_contract_payload=True, contract_payload={"c": "contract"}, use_spell_lock_hint=False,
        )
        ks = _key("s", s_e, 5)
        steps = (_step(("y", 4), y), _step(("z", None), z), generic, _step(ks, s, ("x", (("x", 3),))),
                 _step(("root", 0), root, ("s", (ks,)), ("z", (("z", None),))))
        topologies = {
            "root": SpellLocalTopology("root", (_socket("root", "s", 0), _socket("root", "z", 1))),
            "s": SpellLocalTopology("s", (_socket("s", "x", 0),)),
            "x": SpellLocalTopology("x", (_socket("x", "y", 0), _socket("x", "z", 1))),
        }
        for keys in ((), ("z",), ("s>x>y",), ("**y",)):
            out[f"t5|generic|{s_e.name}|keys={keys}"] = _emit(steps, topologies, ("root", 0), keys, None)
    for holder_e in (MANY, UPC):
        built = Counter()
        a, root = _spell("a", built, holder_e), _spell("root", built)
        ka = _key("a", holder_e, 1)
        steps = (_step(ka, a), _step(("root", 0), root, ("a", (ka,))))
        topologies = {
            "root": SpellLocalTopology("root", (_socket("root", "a", 0), _unresolved("root", "u", 1))),
            "a": SpellLocalTopology("a", (_unresolved("a", "w", 0),)),
        }
        for keys in ((), ("u",), ("a>w",), ("u", "a>w")):
            out[f"t5|unresolved|{holder_e.name}|keys={keys}"] = _emit(steps, topologies, ("root", 0), keys, None)


def door_templates(out: Dict[str, Any]) -> None:
    """The emitted door bodies of every existing route."""
    for route in ("existing_creation", "many", "unique_per_conduit", "spellspace", "unique", "lineage", "cluster"):
        for return_created in (False, True):
            for fast in (False, True):
                lines = door_compiler._build_no_overrides_lines(
                    resolve_route_key=route, fast_transient_no_overrides_enabled=fast, return_created=return_created,
                )
                out[f"door|no_overrides|{route}|fast={fast}|created={return_created}"] = "\n".join(lines)
            lines = door_compiler._build_with_overrides_lines(resolve_route_key=route, return_created=return_created)
            out[f"door|with_overrides|{route}|created={return_created}"] = "\n".join(lines)


def harness_worlds(out: Dict[str, Any]) -> None:
    """The certification harness's five real worlds: the normal plan each root hydrates."""
    sys.argv = [sys.argv[0]]
    from tests.experimentation import codegen_strategy_certification as harness

    for shape in harness.shapes():
        harness.captured.clear()
        book, conduit = harness.build_world(shape, "s5")
        conduit.meld(spell=shape.root)
        for spell_id, (source, namespace) in sorted(harness.captured.items()):
            spell = book.find_spell_by_id(spell_id)
            name = spell.spell_name if spell is not None else spell_id
            out[f"harness|{shape.name}|{name}"] = {"source": source, "names": sorted(namespace)}
        conduit.cleanup()


def main(target: str) -> int:
    out: Dict[str, Any] = {}
    t1_shapes(out)
    t2_shapes(out)
    t3_shapes(out)
    t4_shapes(out)
    t5_shapes(out)
    door_templates(out)
    harness_worlds(out)
    errors = sum(1 for value in out.values() if isinstance(value, dict) and "error" in value)
    with open(target, "w", encoding="utf-8") as handle:
        json.dump(out, handle, indent=1, sort_keys=True)
    print(f"captured {len(out)} entries ({errors} emission errors recorded as data)")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: s5_emission_capture.py <out.json>")
    raise SystemExit(main(sys.argv[1]))
