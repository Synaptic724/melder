"""S5 probe: the Phase-5 path overlay's share of conjure time on layered lattice graphs.

Run from a tree root: PYTHONPATH=src python <this file>. No production change: the overlay method is wrapped
in-process to time it and count the SocketRefs it appends. Each graph is a lattice of L layers of W classes; every
class in layer i takes all W classes of layer i+1, and one root takes all of layer 0, so there are W**L logical paths
below the root while a shared existence builds only L*W + 1 objects. The binary chain of n sites (design v2 section
14) has C_i(a: C_i+1, b: C_i+1), so 2**n paths over n objects. Caching is off so every conjure compiles.
"""
import importlib.util
import pathlib
import sys
import tempfile
import time
from typing import Any, Dict, List, Tuple

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.aether.spellbook.spell_compiler.system.spell_system_root_blueprint_builder import (
    SpellSystemRootBlueprintBuilder,
)

STATS: Dict[str, float] = {"overlay_ns": 0.0, "calls": 0.0, "socket_refs": 0.0}
try:
    ORIGINAL = SpellSystemRootBlueprintBuilder._overlay_sockets_and_index
except AttributeError:
    ORIGINAL = None  # S5 tree: the overlay is gone, so only conjure time is measured


def timed_overlay(self: Any, blueprint: Any, topologies: Any) -> None:
    start = time.perf_counter_ns()
    ORIGINAL(self, blueprint=blueprint, topologies=topologies)
    STATS["overlay_ns"] += time.perf_counter_ns() - start
    STATS["calls"] += 1
    STATS["socket_refs"] += len(blueprint._socket_refs)


if ORIGINAL is not None:
    SpellSystemRootBlueprintBuilder._overlay_sockets_and_index = timed_overlay


def lattice_module(width: int, layers: int, tag: str) -> Tuple[Any, List[str]]:
    lines: List[str] = []
    names: List[str] = []
    for layer in range(layers - 1, -1, -1):
        for column in range(width):
            name = f"L{tag}_{layer}_{column}"
            names.append(name)
            if layer == layers - 1:
                lines.append(f"class {name}:\n    def __init__(self) -> None:\n        pass\n")
            else:
                params = ", ".join(f"p{c}: L{tag}_{layer + 1}_{c}" for c in range(width))
                values = ", ".join(f"p{c}" for c in range(width))
                lines.append(f"class {name}:\n    def __init__(self, {params}) -> None:\n        self.p = ({values},)\n")
    root_params = ", ".join(f"p{c}: L{tag}_0_{c}" for c in range(width))
    root_values = ", ".join(f"p{c}" for c in range(width))
    lines.append(f"class Root{tag}:\n    def __init__(self, {root_params}) -> None:\n        self.p = ({root_values},)\n")
    names.append(f"Root{tag}")
    directory = pathlib.Path(tempfile.mkdtemp(prefix="s5_overlay_"))
    path = directory / f"lattice_{tag}.py"
    path.write_text("\n".join(lines), encoding="utf-8")
    spec = importlib.util.spec_from_file_location(f"lattice_{tag}", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module, names


def run(width: int, layers: int, existence: Existence) -> None:
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    if width == 0:
        tag = f"chain{layers}{existence.name[:4]}"
        module, names = chain_module(layers, tag)
    else:
        tag = f"w{width}l{layers}{existence.name[:4]}"
        module, names = lattice_module(width, layers, tag)
    book = Spellbook(aetheric_frame=f"s5-{tag}")
    book.get_configuration().set_property("phase_scheduler_workers_per_spellbook", 1)
    book._aetheric_frame_configuration.with_system_caching_enabled(False)
    ids = {}
    for name in names:
        ids[name] = book.bind(spell=getattr(module, name), existence=existence, permissions="create")
    for key in STATS:
        STATS[key] = 0.0
    start = time.perf_counter_ns()
    conduit = book.conjure()
    conjure_ns = time.perf_counter_ns() - start
    root = conduit.meld(spell_id=ids[f"Root{tag}"])
    assert type(root).__name__ == f"Root{tag}"
    share = 100.0 * STATS["overlay_ns"] / conjure_ns
    print(f"W={width} L={layers:2d} {existence.name:19} paths {(width or 2) ** layers:7d} spells {len(names):3d} | "
          f"conjure {conjure_ns / 1e6:9.1f} ms | overlay {STATS['overlay_ns'] / 1e6:9.1f} ms ({share:5.1f}%) "
          f"calls {int(STATS['calls']):3d} socket_refs {int(STATS['socket_refs']):9d}", flush=True)
    book.cleanup()


def chain_module(sites: int, tag: str) -> Tuple[Any, List[str]]:
    lines: List[str] = []
    names: List[str] = []
    for site in range(sites - 1, -1, -1):
        name = f"C{tag}_{site}" if site else f"Root{tag}"
        names.append(name)
        if site == sites - 1:
            lines.append(f"class {name}:\n    def __init__(self) -> None:\n        pass\n")
        else:
            below = f"C{tag}_{site + 1}"
            lines.append(f"class {name}:\n    def __init__(self, a: {below}, b: {below}) -> None:\n        self.p = (a, b)\n")
    directory = pathlib.Path(tempfile.mkdtemp(prefix="s5_chain_"))
    path = directory / f"chain_{tag}.py"
    path.write_text("\n".join(lines), encoding="utf-8")
    spec = importlib.util.spec_from_file_location(f"chain_{tag}", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module, names


def main() -> None:
    if "--gate" in sys.argv:
        for sites in (13, 15, 13, 15):
            run(0, sites, Existence.unique_per_conduit)
        for width, layers in ((2, 12), (2, 12), (3, 7), (3, 7)):
            run(width, layers, Existence.unique_per_conduit)
        return
    shared = ((3, 3), (3, 5), (2, 8), (2, 10), (3, 7), (2, 12))
    many = ((2, 4), (2, 6), (2, 8))
    for width, layers in shared:
        run(width, layers, Existence.unique_per_conduit)
    for width, layers in many:
        run(width, layers, Existence.many)
    for sites in (13, 15):
        run(0, sites, Existence.unique_per_conduit)


if __name__ == "__main__":
    main()
