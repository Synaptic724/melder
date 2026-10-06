"""
Codegen strategy certification: measure each concrete strategy on the REAL emitted bodies before any of it is built.

WHY THIS EXISTS
    The adaptive-creation-contexts epic lists concrete strategies (S1-S8) with predicted savings. Before a lane
    is opened to implement any of them, this file answers whether they pay on real emitted plans: it captures
    the plain normal plan `SitePlanLowering.emit` produces for five shapes, applies each strategy as a source
    transform of that captured body, executes it in the same namespace (real spells, real stores, real objects)
    and times plain vs each strategy vs all combined, with Python/C call counts.

    S1  registration trim       `many_store.add_many_creations(sid, v, has_disposal_methods=True, disposal_methods=dm)`
                                -> one append into a store that recorded the per-key methods once (stand-in store)
    S2a existing-object constants  an existing-object site's three lines -> `v = k` (no guard: automatic posture)
    S2b unique captures            a unique site's three lines -> `if s._door_epoch == e: v = k` else the read path
    S4  single-door prologue       the spellspace/conduit store selection -> the conduit store read alone
    S5  batched registration       the registration line -> `scope_list.append((sid, v))` (stand-in list)
    S6  thread-affine append       the registration line -> a `get_ident()` compare and a per-thread bucket
    S8  lazy instance_results      dict mode only inside the misses: the warm path builds no dict and stores nothing
    ALL S8 + S4 + S2a + S2b + S1 ; ALL+S5 swaps S1 for S5

    S1, S5 and S6 use stand-in stores written here: they show the floor of each registration shape in situ,
    they are not store code, and they do not settle the cleaned-store refusal for a lock-free append.

RUN (3.14t target; caching off, nothing is written)
    python -X gil=0 tests/experimentation/codegen_strategy_certification.py
"""

import gc
import os
import re
import statistics
import sys
import threading
import time
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.site_plan_lowering import SitePlanLowering

captured: Dict[str, Tuple[str, Dict[str, Any]]] = {}
_original_emit = SitePlanLowering.emit.__func__


def _capturing_emit(cls: type, **kwargs: Any) -> Any:
    """Record the normal plan's (source, namespace) per root spell id as the lowering emits it."""
    result = _original_emit(cls, **kwargs)
    if kwargs.get("normal_mode"):
        captured[kwargs["root_spell_id"]] = (result[0], result[1])
    return result


SitePlanLowering.emit = classmethod(_capturing_emit)

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.nexus import Nexus
from tests._frame_posture_test_support import configure_frame_posture_for_spellbook_configuration


# ---------------------------------------------------------------------------------------------------------------
# shapes
# ---------------------------------------------------------------------------------------------------------------

def _service(name: str, disposal: bool) -> type:
    """A dependency-free class, optionally with a `cleanup` disposal method."""
    body: Dict[str, Any] = {"__init__": lambda self: setattr(self, "state", 0)}
    if disposal:
        body["cleanup"] = lambda self: setattr(self, "state", -1)
    return type(name, (), body)


def _existing(name: str) -> type:
    """A class whose INSTANCE is bound (an existing object)."""
    return type(name, (), {"__init__": lambda self, n: setattr(self, "n", n)})


def _consumer(name: str, dependencies: Sequence[type], disposal: bool) -> type:
    """A class taking one annotated parameter per dependency, in order."""
    params = [f"d{i}" for i in range(len(dependencies))]
    src = "def __init__(self, " + ", ".join(f"{p}: {d.__name__}" for p, d in zip(params, dependencies)) + "):\n"
    src += "".join(f"    self.{p} = {p}\n" for p in params) or "    pass\n"
    ns: Dict[str, Any] = {d.__name__: d for d in dependencies}
    exec(src, ns)
    body: Dict[str, Any] = {"__init__": ns["__init__"]}
    if disposal:
        body["cleanup"] = lambda self: setattr(self, "state", -1)
    return type(name, (), body)


class Shape:
    """One measured shape: bindings plus the root class melded by name."""

    def __init__(self, name: str, root: type, uniques: Sequence[type], existing: Sequence[type], manys: Sequence[type]) -> None:
        self.name = name
        self.root = root
        self.uniques = tuple(uniques)
        self.existing = tuple(existing)
        self.manys = tuple(manys)


def shapes() -> List[Shape]:
    """The five shapes: two from commandops' cache, three DI-heavy ones the profile is meant to find."""
    manager = _service("Manager", True)
    worker = _consumer("Worker", [manager], True)
    config, builders, resources, utilities = (_existing(n) for n in ("Config", "Builders", "Resources", "Utilities"))
    spectrum = _service("Spectrum", True)
    context_root = _consumer("ContextRoot", [config, builders, resources, utilities, spectrum], True)
    svc = [_service(f"Svc{i}", False) for i in range(8)]
    wide8u = _consumer("Wide8Unique", svc, True)
    ext = [_existing(f"Ext{i}") for i in range(8)]
    wide8e = _consumer("Wide8Existing", ext, True)
    chain: List[type] = [_service("Leaf", False)]
    for i in range(7):
        chain.append(_consumer(f"Link{i}", [chain[-1]], False))
    chain_root = _consumer("Chain8", [chain[-1]], True)
    return [
        Shape("worker", worker, [manager], [], [worker]),
        Shape("context_root", context_root, [spectrum], [config, builders, resources, utilities], [context_root]),
        Shape("wide8_unique", wide8u, svc, [], [wide8u]),
        Shape("wide8_existing", wide8e, [], ext, [wide8e]),
        Shape("chain8_transient", chain_root, [chain[0]], [], chain[1:] + [chain_root]),
    ]


def build_world(shape: Shape, tag: str) -> Tuple[Spellbook, Conduit]:
    """Bind one shape into a fresh automatic world with disposal on and conjure its root conduit."""
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    configuration = SpellbookConfiguration()
    configuration.set_property("disposal", True)
    configuration.set_property("disposal_method_names", ["cleanup"])
    configuration.load_default_dictionary()
    configure_frame_posture_for_spellbook_configuration(configuration, dynamic=False)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    book = Spellbook(configuration=configuration)
    book.configure_aether_frame(system_state=None, disposal=None, disposal_method_names=None, system_caching_enabled=False)
    for cls in shape.uniques:
        book.bind(spell=cls, existence=Existence.unique, permissions="create")
    for n, cls in enumerate(shape.existing):
        book.bind(spell=cls(n), existence=Existence.unique, permissions="create")
    for cls in shape.manys:
        book.bind(spell=cls, existence=Existence.many, permissions="create")
    conduit = book.conjure(name=f"cert-{tag}-root", dynamic=False)
    return book, conduit


# ---------------------------------------------------------------------------------------------------------------
# stand-in stores for S1 / S5 / S6
# ---------------------------------------------------------------------------------------------------------------

class TrimmedStore:
    """S1 stand-in: per-key disposal methods recorded once, the store lock kept, one append per creation."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._many: Dict[str, List[object]] = {}
        self._methods: Dict[str, Tuple[str, ...]] = {}

    def record_methods(self, key: str, methods: Tuple[str, ...]) -> None:
        """Record the spell's disposal methods for `key` (hydration would do this once from the rows)."""
        self._methods[key] = methods

    def append_many(self, key: str, item: object) -> None:
        """Register one creation under the lock with one append."""
        with self._lock:
            bucket = self._many.get(key)
            if bucket is None:
                bucket = self._many[key] = []
            bucket.append(item)


# ---------------------------------------------------------------------------------------------------------------
# transforms over the captured source
# ---------------------------------------------------------------------------------------------------------------

SITE_ALIAS = re.compile(r"^    c(\d+) = spells\[(\d+)\]\._owner_creations$")
# The emitted registration line since the trim landed (2026-10-01): the positional hot verb. The S1 transform
# now measures the real `register_many` against its stand-in, which should be a wash.
REGISTER = re.compile(r"^    many_store\.register_many\(sid(\d+), v(\d+), dm(\d+)\)$", re.M)
PROLOGUE = ["    many_store = meld._spellspace_creations", "    if many_store is None:", "        many_store = meld._conduit_creations"]


def _executor_lines(source: str) -> Tuple[List[str], int]:
    """Split the source into lines and return them with the index of the executor's `def` line."""
    lines = source.split("\n")
    for i, line in enumerate(lines):
        if line.startswith("def _site_plan_executor("):
            return lines, i
    raise RuntimeError("no _site_plan_executor in the captured source")


def site_groups(source: str) -> Dict[int, Tuple[int, int]]:
    """Map a top-level shared site index to the (start, end) line span of its three-line read group."""
    lines, start = _executor_lines(source)
    groups: Dict[int, Tuple[int, int]] = {}
    i = start
    while i < len(lines):
        m = SITE_ALIAS.match(lines[i])
        if m and lines[i + 1] == f"    v{m.group(1)} = c{m.group(1)}._creations.get(sid{m.group(1)})" and lines[i + 2] == f"    if v{m.group(1)} is None:" and lines[i + 3].startswith(f"        v{m.group(1)} = _miss{m.group(1)}("):
            groups[int(m.group(1))] = (i, i + 4)
            i += 4
            continue
        i += 1
    return groups


def transform_sites(source: str, namespace: Dict[str, Any], indexes: Sequence[int], guarded: bool) -> Tuple[str, Dict[str, Any]]:
    """S2a (guarded=False) / S2b (guarded=True): replace the read groups of `indexes` by constants."""
    lines, _ = _executor_lines(source)
    groups = site_groups(source)
    extra: Dict[str, Any] = {}
    out: List[str] = []
    i = 0
    while i < len(lines):
        replaced = False
        for index, (s, e) in groups.items():
            if i == s and index in indexes:
                spell = namespace["spells"][index]
                instance = spell._owner_creations._creations.get(namespace[f"sid{index}"])
                assert instance is not None, "site must be warm before capture"
                extra[f"k{index}"] = instance
                if guarded:
                    extra[f"s{index}"] = spell
                    extra[f"e{index}"] = spell._door_epoch
                    out.append(f"    if s{index}._door_epoch == e{index}:")
                    out.append(f"        v{index} = k{index}")
                    out.append("    else:")
                    out.extend("    " + line for line in lines[s:e])
                else:
                    out.append(f"    v{index} = k{index}")
                i = e
                replaced = True
                break
        if not replaced:
            out.append(lines[i])
            i += 1
    return "\n".join(out), extra


def transform_prologue(source: str) -> str:
    """S4: the single-door prologue (conduit door)."""
    joined = "\n".join(PROLOGUE)
    assert source.count(joined) >= 1
    return source.replace(joined, "    many_store = meld._conduit_creations")


def transform_registration(source: str, namespace: Dict[str, Any], mode: str) -> Tuple[str, Dict[str, Any]]:
    """S1 (`trim`), S5 (`batched`) or S6 (`affine`) on every top-level registration line."""
    lines, start = _executor_lines(source)
    extra: Dict[str, Any] = {}
    out: List[str] = []
    for i, line in enumerate(lines):
        m = REGISTER.match(line) if i > start else None
        if not m:
            out.append(line)
            continue
        n = m.group(1)
        if mode == "trim":
            store = extra.setdefault("_trim_store", TrimmedStore())
            store.record_methods(namespace[f"sid{n}"], tuple(namespace[f"dm{n}"]))
            out.append(f"    _trim_store.append_many(sid{n}, v{n})")
        elif mode == "batched":
            extra.setdefault("_scope_list", [])
            out.append(f"    _scope_list.append((sid{n}, v{n}))")
        elif mode == "affine":
            extra["_get_ident"] = threading.get_ident
            extra["_t0"] = threading.get_ident()
            extra.setdefault("_bucket", [])
            out.append(f"    if _get_ident() == _t0:")
            out.append(f"        _bucket.append(v{n})")
            out.append("    else:")
            out.append("    " + line)
        else:
            raise ValueError(mode)
    return "\n".join(out), extra


def transform_lazy_dict(source: str) -> str:
    """S8: no `instance_results` on the warm path; a miss gets a fresh empty dict."""
    lines, start = _executor_lines(source)
    out: List[str] = []
    for i, line in enumerate(lines):
        if i > start:
            if line == "    instance_results = {}":
                continue
            if re.match(r"^    instance_results\[key\d+\] = v\d+$", line):
                continue
            line = re.sub(r"_miss(\d+)\(meld, c(\d+), instance_results\)", r"_miss\1(meld, c\2, {})", line)
        out.append(line)
    return "\n".join(out)


# ---------------------------------------------------------------------------------------------------------------
# measurement
# ---------------------------------------------------------------------------------------------------------------

def time_ns(fn: Callable[[], object], n: int = 40000, reps: int = 3, warm: int = 10000) -> float:
    """Median ns per call over `reps` batches after warm-up."""
    for _ in range(warm):
        fn()
    samples: List[float] = []
    for _ in range(reps):
        t0 = time.perf_counter_ns()
        for _ in range(n):
            fn()
        samples.append((time.perf_counter_ns() - t0) / n)
    return statistics.median(samples)


def call_counts(fn: Callable[[], object]) -> Tuple[int, int]:
    """Python and C call counts of one call, the profiler's own entry excluded."""
    counts = {"call": 0, "c_call": 0}

    def profile(frame: object, event: str, arg: object) -> None:
        if event in counts:
            counts[event] += 1

    sys.setprofile(profile)
    try:
        fn()
    finally:
        sys.setprofile(None)
    return counts["call"] - 1, counts["c_call"] - 1


def compile_variant(source: str, namespace: Dict[str, Any], extra: Dict[str, Any], label: str) -> Callable[[Any], Any]:
    """Execute a transformed body in a copy of the captured namespace and return its executor."""
    ns = dict(namespace)
    ns.update(extra)
    exec(compile(source, f"<cert-{label}>", "exec"), ns)
    return ns["_site_plan_executor"]


def measure_shape(shape: Shape, show_source: bool) -> List[str]:
    """Return the table rows for one shape."""
    captured.clear()
    book, conduit = build_world(shape, shape.name)
    rows: List[str] = []
    try:
        root_name = shape.root.__name__
        instance = conduit.meld(root_name)
        assert type(instance) is shape.root
        root_id: Optional[str] = None
        for sid, (_src, ns) in captured.items():
            if any(s.spell is shape.root and s.spell_id == ns.get("root_spell_id") for s in ns.get("spells", ())):
                root_id = sid
        if root_id is None:
            raise RuntimeError(f"no captured normal plan for {root_name}")
        source, namespace = captured[root_id]
        if show_source:
            print(f"\n```\n# {shape.name}\n{source}\n```")
        meld = conduit._meld
        plain = namespace["_site_plan_executor"]
        for _ in range(3):
            plain(meld)
        spells = namespace["spells"]
        groups = site_groups(source)
        existing_idx = [i for i in groups if spells[i].is_existing_creation]
        unique_idx = [i for i in groups if not spells[i].is_existing_creation]
        dict_mode = "    instance_results = {}" in source
        variants: List[Tuple[str, str, Dict[str, Any]]] = [("plain", source, {})]
        if REGISTER.search(source):
            s1, x1 = transform_registration(source, namespace, "trim"); variants.append(("S1 trim registration", s1, x1))
        if existing_idx:
            s2a, x2a = transform_sites(source, namespace, existing_idx, guarded=False); variants.append(("S2a existing constants", s2a, x2a))
        if unique_idx:
            s2b, x2b = transform_sites(source, namespace, unique_idx, guarded=True); variants.append(("S2b unique captures", s2b, x2b))
        if "\n".join(PROLOGUE) in source:
            variants.append(("S4 single-door prologue", transform_prologue(source), {}))
        if REGISTER.search(source):
            s5, x5 = transform_registration(source, namespace, "batched"); variants.append(("S5 batched registration", s5, x5))
            s6, x6 = transform_registration(source, namespace, "affine"); variants.append(("S6 thread-affine append", s6, x6))
        if dict_mode:
            variants.append(("S8 lazy instance_results", transform_lazy_dict(source), {}))
        # all combined: S8 + S4 + S2a + S2b + S1 ; and with S5 instead of S1
        combined = transform_lazy_dict(source) if dict_mode else source
        if "\n".join(PROLOGUE) in combined:
            combined = transform_prologue(combined)
        extra_all: Dict[str, Any] = {}
        if existing_idx:
            combined, x = transform_sites(combined, namespace, existing_idx, guarded=False); extra_all.update(x)
        if unique_idx:
            combined, x = transform_sites(combined, namespace, unique_idx, guarded=True); extra_all.update(x)
        if REGISTER.search(combined):
            all_s1, x = transform_registration(combined, namespace, "trim"); variants.append(("ALL (S8+S4+S2a+S2b+S1)", all_s1, {**extra_all, **x}))
            all_s5, x = transform_registration(combined, namespace, "batched"); variants.append(("ALL+S5 (S5 for S1)", all_s5, {**extra_all, **x}))
        else:
            variants.append(("ALL (S8+S4+S2a+S2b)", combined, extra_all))
        results: List[Tuple[str, float, int, int]] = []
        plain_ns: Optional[float] = None
        stores = [meld._conduit_creations]

        def drain() -> None:
            # keep the heap flat between variants: the many buckets and the stand-ins grow with every call
            for store in stores:
                for key, bucket in list(store._creations.items()):
                    if isinstance(bucket, list):
                        bucket.clear()
                for key, bucket in list(store._disposable_creations.items()):
                    if isinstance(bucket, list):
                        bucket.clear()

        gc.disable()
        try:
            for label, src, extra in variants:
                fn = compile_variant(src, namespace, extra, label)
                assert type(fn(meld)) is shape.root, label
                ns_per = time_ns(lambda f=fn: f(meld))
                py, c = call_counts(lambda f=fn: f(meld))
                drain()
                for value in extra.values():
                    if isinstance(value, list):
                        value.clear()
                    elif isinstance(value, TrimmedStore):
                        for bucket in value._many.values():
                            bucket.clear()
                gc.collect()
                if plain_ns is None:
                    plain_ns = ns_per
                results.append((label, ns_per, py, c))
            ref = time_ns(lambda: conduit.meld(root_name))
            drain()
        finally:
            gc.enable()
        for label, ns_per, py, c in results:
            delta = "" if label == "plain" else f"{(ns_per - plain_ns) / plain_ns * 100:+.0f}%"
            rows.append(f"| {shape.name} | {label} | {ns_per:.0f} | {delta} | {py} | {c} |")
        rows.append(f"| {shape.name} | reference: conduit.meld(\"{root_name}\") | {ref:.0f} | | | |")
    finally:
        conduit.cleanup()
        book.cleanup()
    return rows


def main(argv: Sequence[str]) -> int:
    """Print the certification table for the five shapes; `--source` also prints the captured bodies."""
    show_source = "--source" in argv
    print("| shape | variant | ns per creation (plan direct) | vs plain | py calls | C calls |")
    print("| --- | --- | ---: | ---: | ---: | ---: |")
    for shape in shapes():
        for row in measure_shape(shape, show_source):
            print(row)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
