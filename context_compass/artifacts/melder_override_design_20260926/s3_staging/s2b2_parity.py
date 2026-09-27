"""S2b-2 parity probe: today's inner no-overrides executor vs the lowering's normal-mode plan (S2b-1 placement).

Run from a tree root: PYTHONPATH=src:. python <this file>. No production change. Per graph: warm direct calls of
the family's hydrated inner executor and of the emitted plan (median of 7 samples), results compared by type, and the
one-shot cost of building each (inner: family hydration; plan: steps, site graph, emission, compile, exec).
Generalized graphs carry shared sites; the many_only graphs come from the override experiment.
"""
import statistics
import sys
import time
from typing import Any, Callable, Dict, List, Tuple

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.manifest_creation_cache import (
    MANIFEST_METADATA_KEY,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.site_plan_lowering import (
    SitePlanLowering,
    SitePlanStep,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.site_plan_override_runtime import (
    SitePlanOverrideRuntime,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_manifest_no_overrides_compiler import (
    hydrate_no_overrides_executor,
    resolve_root_instance_key_from_rows,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_no_overrides_codegen_creation_compiler import (
    _hydrate_steps_from_rows as generalized_rows,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.hydration.generalized_binding_resolver import (
    SpellbookBindingResolver,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.hydration.generalized_hydrator import (
    _resolve_spell_lookup as generalized_lookup,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.compilers.many_only_no_overrides_codegen_creation_compiler import (
    _hydrate_steps_from_rows as many_only_rows,
    _resolve_root_instance_key,
    compile_no_overrides_codegen_creation_executor,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.hydration.many_only_hydrator import (
    _resolve_spell_lookup as many_only_lookup,
)
from tests.experimentation.test_melder_creation_overrides_performance import MelderExperiment


class GX:
    def __init__(self) -> None:
        pass


class GS:
    def __init__(self, x: GX) -> None:
        self.x = x


class GA:
    def __init__(self) -> None:
        pass


class GRoot:
    def __init__(self, a: GA, s: GS) -> None:
        self.a = a
        self.s = s


class ULeaf:
    def __init__(self) -> None:
        pass


class USvc:
    def __init__(self, leaf: ULeaf) -> None:
        self.leaf = leaf


class URoot:
    def __init__(self, svc: USvc, other: ULeaf) -> None:
        self.svc = svc
        self.other = other


class MY:
    def __init__(self) -> None:
        pass


class MZ:
    def __init__(self) -> None:
        pass


class MS:
    def __init__(self) -> None:
        pass


class MP:
    def __init__(self, s: MS) -> None:
        self.s = s


class MQ:
    def __init__(self, s: MS) -> None:
        self.s = s


class MC:
    def __init__(self, y: MY, z: MZ) -> None:
        self.y = y
        self.z = z


class MRoot:
    def __init__(self, p: MP, q: MQ, c: MC) -> None:
        self.p = p
        self.q = q
        self.c = c


class DL:
    def __init__(self) -> None:
        pass


class D1a:
    def __init__(self, l: DL) -> None:
        self.l = l


class D1b:
    def __init__(self, l: DL) -> None:
        self.l = l


class D2a:
    def __init__(self, a: D1a, b: D1b) -> None:
        self.a = a
        self.b = b


class D2b:
    def __init__(self, a: D1a, b: D1b) -> None:
        self.a = a
        self.b = b


class DRoot:
    def __init__(self, x: D2a, y: D2b) -> None:
        self.x = x
        self.y = y


MANY = Existence.many
UPC = Existence.unique_per_conduit
GENERALIZED: Tuple[Tuple[str, Any, int], ...] = (("G1", GRoot, 20000), ("unique", URoot, 20000),
                                                 ("mixed", MRoot, 20000), ("tree", DRoot, 20000))
BINDINGS: Tuple[Tuple[Any, Existence], ...] = (
    (GX, MANY), (GS, UPC), (GA, MANY), (GRoot, MANY),
    (ULeaf, MANY), (USvc, Existence.unique), (URoot, MANY),
    (MY, MANY), (MZ, MANY), (MS, UPC), (MP, MANY), (MQ, MANY), (MC, UPC), (MRoot, MANY),
    (DL, UPC), (D1a, MANY), (D1b, MANY), (D2a, MANY), (D2b, MANY), (DRoot, MANY),
)


def interleaved_ns(first: Callable[[], Any], second: Callable[[], Any], n: int) -> Tuple[float, float, float]:
    """Alternate the two callables for 11 rounds; return their median ns/call and the median per-round ratio."""
    a_samples: List[float] = []
    b_samples: List[float] = []
    ratios: List[float] = []
    for _ in range(11):
        start = time.perf_counter_ns()
        for _ in range(n):
            first()
        a = (time.perf_counter_ns() - start) / n
        start = time.perf_counter_ns()
        for _ in range(n):
            second()
        b = (time.perf_counter_ns() - start) / n
        a_samples.append(a)
        b_samples.append(b)
        ratios.append(a / b)
    return statistics.median(a_samples), statistics.median(b_samples), statistics.median(ratios)


def fresh_aether() -> None:
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


BREAKDOWN: Dict[str, float] = {}


def build_plan(spell: Any, steps: Tuple[SitePlanStep, ...], root_key: Any, inner: Any) -> Tuple[Any, Any, int]:
    runtime = SitePlanOverrideRuntime(steps=steps, root_spell=spell, root_instance_key=root_key,
                                      inner_no_overrides_executor=inner)
    start = time.perf_counter_ns()
    site_graph = runtime._site_graph_or_build()
    BREAKDOWN["graph"] = time.perf_counter_ns() - start
    start = time.perf_counter_ns()
    resolution = runtime._resolve((), 0)
    source, namespace, _ = SitePlanLowering.emit(
        steps=runtime._steps, site_graph=site_graph, resolution=resolution,
        root_instance_key=root_key, root_spell_id=spell.spell_id, root_spell_name=spell.spell_name, arity=0,
    )
    BREAKDOWN["emit"] = time.perf_counter_ns() - start
    # Normal-mode preview: with no winning key `ov` is only a pass-through parameter, so drop it from every
    # signature and call, which is what a normal-mode emission would produce.
    assert "ov[" not in source
    source = source.replace("meld, ov", "meld")
    start = time.perf_counter_ns()
    exec(compile(source, "<s2b2_parity>", "exec"), namespace)
    BREAKDOWN["compile"] = time.perf_counter_ns() - start
    return namespace[SitePlanLowering.PLAN_FUNCTION_NAME], runtime, source.count("\n")


def report(graph: str, inner: Any, plan: Any, meld: Any, n: int, t_inner_build: float, t_plan_build: float,
           lines: int) -> None:
    assert type(inner(meld)) is type(plan(meld)), graph
    t_inner, t_plan, ratio = interleaved_ns(lambda: inner(meld), lambda: plan(meld), n)
    parts = ", ".join(f"{name} {value / 1e3:.0f}" for name, value in BREAKDOWN.items())
    print(f"{graph:8} inner {t_inner:9.1f} ns | plan {t_plan:9.1f} ns ({100 * ratio:5.1f}% speed) | "
          f"build inner {t_inner_build / 1e3:7.1f} us, plan {t_plan_build / 1e3:7.1f} us ({parts}) | lines {lines}")


def generalized_graphs() -> None:
    fresh_aether()
    book = Spellbook(aetheric_frame="s2b2-parity")
    book.get_configuration().set_property("phase_scheduler_workers_per_spellbook", 1)
    book._aetheric_frame_configuration.with_system_caching_enabled(False)
    ids = {cls: book.bind(spell=cls, existence=existence, permissions="create") for cls, existence in BINDINGS}
    conduit = book.conjure()
    meld = conduit._meld
    for graph, root, n in GENERALIZED:
        conduit.meld(spell_id=ids[root])
        spell = book.find_spell_by_id(ids[root])
        manifest = spell._compiler_artifact._spell_codegen_creation.metadata[MANIFEST_METADATA_KEY]
        payload = manifest["no_overrides"]
        start = time.perf_counter_ns()
        resolver = SpellbookBindingResolver(spell=spell)
        lookup = generalized_lookup(resolver=resolver, step_spell_ids=payload["step_spell_ids"])
        inner = hydrate_no_overrides_executor(
            rows=payload["steps_rows"], transient_schema=payload["transient_schema"],
            root_instance_key=payload["root_instance_key"], root_spell_id=payload["root_spell_id"],
            spell_lookup=lookup,
        )
        t_inner_build = time.perf_counter_ns() - start
        start = time.perf_counter_ns()
        rows = generalized_rows(steps_rows=payload["steps_rows"], spell_lookup=lookup)
        root_key = resolve_root_instance_key_from_rows(
            rows=payload["steps_rows"], explicit_root_instance_key=payload["root_instance_key"],
            root_spell_id=payload["root_spell_id"],
        )
        steps = tuple(SitePlanStep.from_generalized_row(row) for row in rows)
        plan, runtime, lines = build_plan(spell, steps, root_key, inner)
        t_plan_build = time.perf_counter_ns() - start
        report(graph, inner, plan, meld, n, t_inner_build, t_plan_build, lines)
        runtime.cleanup()
        resolver.cleanup()
    book.cleanup()


def many_only_graphs() -> None:
    for graph, n in (("solo", 20000), ("shallow", 20000), ("wide", 20000), ("diamond", 20000), ("deep", 400)):
        experiment = MelderExperiment()
        experiment.setup(graph, "automatic")
        conduit = experiment.conduit
        conduit.meld(spell_id=experiment.root_id)
        spell = experiment.book.find_spell_by_id(experiment.root_id)
        payload = spell._compiler_artifact._spell_codegen_creation.metadata[MANIFEST_METADATA_KEY]["no_overrides"]
        start = time.perf_counter_ns()
        lookup = many_only_lookup(spell=spell, step_spell_ids=payload["step_spell_ids"])
        inner = compile_no_overrides_codegen_creation_executor(
            codegen_ir={"steps_rows": payload["steps_rows"], "root_spell_id": payload["root_spell_id"],
                        "transient_schema": payload["transient_schema"]},
            spell_lookup=lookup,
        )
        t_inner_build = time.perf_counter_ns() - start
        start = time.perf_counter_ns()
        rows = many_only_rows(steps_rows=payload["steps_rows"], spell_lookup=lookup)
        root_key = _resolve_root_instance_key(steps=rows, root_spell_id=payload["root_spell_id"])
        steps = tuple(SitePlanStep.from_many_only_row(row) for row in rows)
        plan, runtime, lines = build_plan(spell, steps, root_key, inner)
        t_plan_build = time.perf_counter_ns() - start
        report(graph, inner, plan, conduit._meld, n, t_inner_build, t_plan_build, lines)
        runtime.cleanup()
        experiment.cleanup()


if __name__ == "__main__":
    print(f"python {sys.version.split()[0]} gil={sys._is_gil_enabled()}")
    generalized_graphs()
    many_only_graphs()
