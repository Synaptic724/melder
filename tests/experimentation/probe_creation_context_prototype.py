"""
Probe creation-context prototype: what does it cost to instrument the real emitted plan?

WHY THIS EXISTS
    The owner's direction for the PGO lane: a switch that turns optimization on, a probing creation context that
    times and maps the node structure a conduit builds, a report in a core area (the DevOps station), and codegen
    styles selected by the measured data. Before designing the probe we need its price. This file captures the
    REAL normal plan `SitePlanLowering.emit` produces for a shape, instruments that source two ways and times the
    plan directly against the plain one:

    count-only   per-site miss counters plus one call counter (list-item increments, no clock)
    timed        the same plus `perf_counter_ns` around every top-level site (the per-site timing the report
                 would show: constructor time, subtree time)

    The reference column is today's `conduit.meld("Name")` through the front door, so the plan's share of a meld
    is visible too. The solo family has no site plan (its body is the constructor call), so it is listed only as
    a reference.

RUN (on the 3.14t target; caching is off so nothing is written)
    python -X gil=0 tests/experimentation/probe_creation_context_prototype.py
"""
import os
import re
import statistics
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.site_plan_lowering import SitePlanLowering
captured = {}
_orig_emit = SitePlanLowering.emit.__func__
def _capturing_emit(cls, **kwargs):
    result = _orig_emit(cls, **kwargs)
    if kwargs.get("normal_mode"):
        captured[kwargs["root_spell_id"]] = (result[0], result[1])
    return result
SitePlanLowering.emit = classmethod(_capturing_emit)
from pgo_codegen_composition_experiment import CompositionBuilder, MelderWorld

GROUP_START = re.compile(r"^    (try:|c(\d+) = )")
SITE_LINE = re.compile(r"^    v(\d+) = ")
MISS_IF = re.compile(r"^    if v(\d+) is None:$")

def instrument(source: str, timed: bool) -> str:
    lines = source.split("\n")
    out, in_plan, site_of_group, n_sites = [], False, None, 0
    for line in lines:
        if line.startswith("def _site_plan_executor("):
            in_plan = True
            out.append(line)
            if timed:
                out.append("    _t = _pc()")
            continue
        if not in_plan:
            out.append(line); continue
        if line.startswith("    return "):
            out.append("    _calls[0] += 1")
            out.append(line); in_plan = False; continue
        m = MISS_IF.match(line)
        if m:
            out.append(line); out.append(f"        _mis[{m.group(1)}] += 1"); continue
        s = re.match(r"^\s+v(\d+) = ", line)
        if s:
            site_of_group = int(s.group(1)); n_sites = max(n_sites, site_of_group + 1)
        out.append(line)
        # a group ends when the next line starts a new group or the return; timed line inserted lazily below
        if timed and site_of_group is not None and line.startswith("    ") and not line.startswith("     "):
            pass
    src = "\n".join(out)
    if timed:
        # insert timing after each completed top-level site: after 'v{i} = _miss{i}(...)' line or after the except block of a direct construct
        fixed = []
        plan_lines = src.split("\n")
        i = 0
        while i < len(plan_lines):
            line = plan_lines[i]
            fixed.append(line)
            m_miss_call = re.match(r"^        v(\d+) = _miss(\d+)\(", line)
            m_except = re.match(r"^        _raise_meld_construction_error\(spells\[(\d+)\]", line)
            if m_miss_call:
                k = m_miss_call.group(1)
                fixed.append(f"    _n = _pc(); _ns[{k}] += _n - _t; _t = _n")
            elif m_except and plan_lines[i - 3].startswith("    try:") and plan_lines[i - 2].startswith("        v"):
                k = m_except.group(1)
                fixed.append(f"    _n = _pc(); _ns[{k}] += _n - _t; _t = _n")
            i += 1
        src = "\n".join(fixed)
    return src, n_sites

def timeit(fn, n=60000, reps=3, warm=10000):
    for _ in range(warm): fn()
    s = []
    for _ in range(reps):
        t0 = time.perf_counter_ns()
        for _ in range(n): fn()
        s.append((time.perf_counter_ns() - t0) / n)
    return statistics.median(s)

def main():
    shapes = CompositionBuilder.compositions()
    print("| shape | plain plan direct | count-only probe | timed probe | meld by name (ref) | sites |")
    print("| --- | ---: | ---: | ---: | ---: | ---: |")
    for name in ["solo", "w1_singleton", "w2_mixed", "w4_mixed", "wide8_singleton", "chain8_transient"]:
        root = shapes[name]
        CompositionBuilder.materialize(root, f"pr_{name}")
        world = MelderWorld(root, f"pr-{name}")
        try:
            world.singleton_instances()
            conduit = world.conduit
            conduit.meld(root.cls.__name__)
            if world.root_id not in captured:
                print(f"| {name} | (solo family: no site plan) | | | {timeit(lambda: conduit.meld(root.cls.__name__)):.0f} | 0 |")
                continue
            source, namespace = captured[world.root_id]
            plain = namespace["_site_plan_executor"]
            meld = conduit._meld
            arms = {"plain": plain}
            for label, timed in (("count", False), ("timed", True)):
                src, n_sites = instrument(source, timed)
                ns = dict(namespace)
                ns.update({"_pc": time.perf_counter_ns, "_ns": [0] * max(n_sites, 1), "_mis": [0] * max(n_sites, 1), "_calls": [0]})
                exec(compile(src, f"<probe-{label}>", "exec"), ns)
                arms[label] = ns["_site_plan_executor"]
            for fn in arms.values():
                assert type(fn(meld)) is root.cls
            r = {k: timeit(lambda f=f: f(meld)) for k, f in arms.items()}
            ref = timeit(lambda: conduit.meld(root.cls.__name__))
            print(f"| {name} | {r['plain']:.0f} | {r['count']:.0f} (+{r['count']-r['plain']:.0f}) | {r['timed']:.0f} (+{r['timed']-r['plain']:.0f}) | {ref:.0f} | {n_sites} |")
        finally:
            world.cleanup()
    pc = time.perf_counter_ns
    print(f"\nperf_counter_ns alone: {timeit(pc):.0f} ns per call (VM)")

if __name__ == "__main__":
    main()
