"""Compare warm Melder creation and overrides with one timing harness.

Run correctness checks normally with pytest. Enable timings explicitly:
    MELDER_OVERRIDE_PERF=1 python -m pytest -q -s <this file>

Controls: MELDER_OVERRIDE_GRAPHS (solo,scalar,shallow,wide,diamond,deep),
MELDER_OVERRIDE_MODES (automatic,dynamic), MELDER_OVERRIDE_REPEATS (7),
MELDER_OVERRIDE_SAMPLE_MS (30), MELDER_OVERRIDE_ITERS (0 = calibrate),
MELDER_OVERRIDE_WARMUP (128), MELDER_OVERRIDE_GC (disabled or enabled),
and MELDER_OVERRIDE_OUTPUT (optional directory for JSON and Markdown).

The graph classes come from the two supplied benchmark suites' common models;
only Melder is constructed. No competitor builder is called. All graph bindings
are transient: the legacy override suite's existing-singleton solo case is not
mixed into creation ratios. Supplying a dependency changes requested graph work;
the scalar case keeps constructor work equal. The Python control constructs only
the root from supplied inputs and is not an implemented init={} API.

Samples exclude setup, warmup, correctness assertions and explicit GC collection.
They include the same Python loop/call wrapper and normal object release. GC is
restored after every sample. Timing numbers are observations, never pass criteria.
"""

import gc
import hashlib
import json
import os
import platform
import statistics
import sys
import sysconfig
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Optional

import pytest

from benchmarks.testing_other_di import test_overrides_all as graph_models
from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
from tests._frame_posture_test_support import (
    configure_frame_posture_for_spellbook_configuration,
)

Case = tuple[Callable[[], object], dict[str, object], str]


class ScalarRoot:
    """One plain Python constructor argument with no dependency graph.

    The default and explicit input perform exactly one scalar assignment.
    Instances own no external resources; fresh identity is observable in tests.
    """

    __slots__ = ("value",)

    def __init__(self, value: int = 13) -> None:
        """Store the supplied value, defaulting to the benchmark's normal value."""
        self.value = value


@dataclass(frozen=True)
class TimingSettings:
    """Value-only settings for repeated single-thread measurements.

    Zero iterations requests calibration to sample_ms, bounded to 64..100,000
    calls. Explicit positive iterations bypass calibration. No timing threshold
    controls success; invalid settings raise before runtime construction.
    """

    repeats: int
    sample_ms: float
    iterations: int
    warmup: int
    gc_mode: str

    @classmethod
    def from_environment(cls) -> TimingSettings:
        """Parse strict environment controls and reject invalid sample settings."""
        settings = cls(
            repeats=int(os.environ.get("MELDER_OVERRIDE_REPEATS", "7")),
            sample_ms=float(os.environ.get("MELDER_OVERRIDE_SAMPLE_MS", "30")),
            iterations=int(os.environ.get("MELDER_OVERRIDE_ITERS", "0")),
            warmup=int(os.environ.get("MELDER_OVERRIDE_WARMUP", "128")),
            gc_mode=os.environ.get("MELDER_OVERRIDE_GC", "disabled"),
        )
        if settings.repeats < 1 or settings.sample_ms <= 0:
            raise ValueError("Repeats and sample duration must be positive.")
        if settings.iterations < 0 or settings.warmup < 1:
            raise ValueError("Iterations must be nonnegative and warmup positive.")
        if settings.gc_mode not in ("disabled", "enabled"):
            raise ValueError("MELDER_OVERRIDE_GC must be disabled or enabled.")
        return settings


@dataclass(frozen=True)
class TimingResult:
    """Value-only raw samples and derived statistics for one measured call shape."""

    graph: str
    mode: str
    case: str
    iterations_per_sample: int
    samples_ns: list[float]
    median_ns: float
    min_ns: float
    max_ns: float
    median_absolute_deviation_ns: float
    operations_per_second: float
    throughput_percent_of_normal: float
    latency_ratio_to_normal: float
    note: str


def _selection(
    variable: str, choices: tuple[str, ...], default: Optional[tuple[str, ...]] = None,
) -> list[str]:
    """Read a nonempty comma-separated subset without silently accepting typos."""
    selected = os.environ.get(variable, ",".join(choices if default is None else default)).split(",")
    selected = [value.strip() for value in selected if value.strip()]
    if not selected or len(selected) != len(set(selected)) or any(v not in choices for v in selected):
        raise ValueError(f"{variable} must select distinct values from {choices}.")
    return selected


def _root_inputs(root: object) -> dict[str, object]:
    """Read the known graph's direct constructor fields for supplied-input cases."""
    if isinstance(root, ScalarRoot):
        return {"value": root.value}
    if isinstance(root, graph_models.ShallowRootAB):
        return {"a": root.a, "b": root.b}
    if isinstance(root, graph_models.Wide8Root):
        return {f"l{index}": leaf for index, leaf in enumerate(root.leaves)}
    if isinstance(root, (graph_models.DiamondRoot, graph_models.Depth9Root)):
        return {"left": root.left, "right": root.right}
    if isinstance(root, graph_models.SoloRootA):
        return {}
    raise TypeError(f"Unsupported benchmark root: {type(root).__name__}")


def _path_value(root: object, path: str) -> object:
    """Follow a test-declared attribute path; names are genuinely dynamic here."""
    if isinstance(root, graph_models.Wide8Root) and path.startswith("l") and path[1:].isdigit():
        return root.leaves[int(path[1:])]
    value = root
    for part in path.split(">"):
        value = getattr(value, part)
    return value


class MelderExperiment:
    """Own one Book/root and borrowed test values for one graph and frame mode.

    Setup is explicit so its caller can clean partially constructed test state.
    Runtime caching on disk is disabled; in-memory compilation and warm doors
    remain normal. Cases use the public Conduit.meld API, without patching it.
    """

    def __init__(self) -> None:
        """Initialize optional owners before any runtime setup can fail."""
        self.book: Optional[Spellbook] = None
        self.conduit: Optional[Conduit] = None
        self.graph = ""
        self.root_type: type = ScalarRoot
        self.root_id = ""
        self.cases: dict[str, Case] = {}
        self.rejected_cases: dict[str, str] = {}

    def cleanup(self) -> None:
        """Release case closures, then the conduit/Book and isolated Aether world."""
        self.cases.clear()
        self.rejected_cases.clear()
        try:
            if self.conduit is not None:
                self.conduit.permanent_cleanup()
        finally:
            try:
                if self.book is not None:
                    self.book.cleanup()
            finally:
                self.conduit = None
                self.book = None
                Aether._reset_singleton_for_tests()
                Spellbook._aether = Aether()
                Conduit._aether = Spellbook._aether

    def setup(self, graph: str, mode: str) -> None:
        """Build transient bindings and case closures outside every timed sample."""
        self.graph = graph
        Aether._reset_singleton_for_tests()
        Spellbook._aether = Aether()
        Conduit._aether = Spellbook._aether
        if graph == "scalar":
            self.root_type, classes = ScalarRoot, (ScalarRoot,)
        else:
            spec = next(spec for spec in graph_models._override_graphs() if spec.name == graph)
            self.root_type, classes = spec.root_type, spec.classes
        configuration = SpellbookConfiguration(f"override-perf-{graph}-{mode}").with_defaults()
        configuration.with_phase_scheduler_workers(1)
        frame = configure_frame_posture_for_spellbook_configuration(
            configuration, dynamic=mode == "dynamic",
        )
        frame.with_system_caching_enabled(False)
        self.book = Spellbook(aetheric_frame=configuration._aether_frame, configuration=configuration)
        ids = {
            model: self.book.bind(spell=model, existence=Existence.many, permissions="create")
            for model in classes
        }
        self.root_id = ids[self.root_type]
        self.conduit = self.book.conjure(name="benchmark", dynamic=mode == "dynamic")
        self.cases = self._build_cases()

    def _build_cases(self) -> dict[str, Case]:
        """Build public-call cases with explicit expected fields and workload notes."""
        meld = self.conduit.meld
        root_id = self.root_id
        root_type = self.root_type
        inputs = _root_inputs(meld(spell_id=root_id))
        cases: dict[str, Case] = {
            "normal": (lambda: meld(spell_id=root_id), {}, "Full transient graph; no overrides."),
            "empty_dict": (lambda: meld(spell_id=root_id, override={}), {}, "Same graph; fresh empty dict."),
            "empty_tuple": (lambda: meld(spell_id=root_id, override=()), {}, "Same graph; empty positional input."),
        }
        if inputs:
            first_key = next(iter(inputs))
            first_value = inputs[first_key]
            one = {first_key: first_value}
            args = tuple(inputs.values())
            cases["root_one_reused"] = (
                lambda: meld(spell_id=root_id, override=one), one,
                "One supplied root argument; payload and value reused.",
            )
            cases["root_one_fresh"] = (
                lambda: meld(spell_id=root_id, override={first_key: first_value}), one,
                "Same root argument; one fresh dict per call, matching the original benchmark.",
            )
            if len(inputs) > 1:
                cases["root_all_reused"] = (
                    lambda: meld(spell_id=root_id, override=inputs), inputs,
                    "All direct root arguments supplied; retained graph values reused.",
                )
            cases["root_args_tuple"] = (
                lambda: meld(spell_id=root_id, override=args), inputs,
                "All root arguments supplied positionally; public normalization remains timed.",
            )
        cases["python_root_only"] = (
            lambda: root_type(**inputs), inputs,
            "Lower bound: Python root constructor only, supplied dependencies; no Melder semantics.",
        )
        self._add_targeted_cases(cases, meld, root_id)
        return cases

    def _add_targeted_cases(
        self, cases: dict[str, Case], meld: Callable[..., object], root_id: str,
    ) -> None:
        """Add the supplied benchmark's exact/broadcast dependency targeting cases."""
        if self.graph in ("solo", "scalar"):
            return
        spec = next(spec for spec in graph_models._override_graphs() if spec.name == self.graph)
        supplied = spec.override_target()
        key = spec.melder_override_key
        assert key is not None, "A dependency-override fixture must declare its target key."
        original = {key: supplied}
        expected = (
            {"left>leaf": supplied, "right>leaf": supplied}
            if self.graph == "diamond" else {key: supplied}
        )
        cases["original_override"] = (
            lambda: meld(spell_id=root_id, override={key: supplied}), expected,
            f"Original override workload: {key}; fresh mapping and precreated replacement.",
        )
        if self.graph in ("diamond", "deep"):
            cases["nested_reused"] = (
                lambda: meld(spell_id=root_id, override=original), expected,
                f"Same nested selector {key}; payload reused.",
            )
        if self.graph == "diamond":
            exact = {"left>leaf": supplied}
            cases["nested_exact"] = (
                lambda: meld(spell_id=root_id, override=exact), exact,
                "One exact nested leaf; the right branch remains normally constructed.",
            )

    def verify(self) -> None:
        """Check outcomes and expose known positional/DI rejection without timing failed calls.

        Only the observed positional duplicate-argument error is classified as
        rejected. Every other exception propagates. If runtime later supports
        this input shape, it automatically rejoins the measured cases.
        """
        for label, (call, expected, _note) in self.cases.items():
            try:
                first, second = call(), call()
            except MeldExecutionError as error:
                if (
                    label != "root_args_tuple" or not isinstance(error.__cause__, TypeError)
                    or "multiple values for argument" not in str(error.__cause__)
                ):
                    raise
                self.rejected_cases[label] = str(error.__cause__)
                continue
            assert isinstance(first, self.root_type), label
            assert isinstance(second, self.root_type), label
            assert first is not second, f"{label}: transient root was reused"
            for path, supplied in expected.items():
                assert _path_value(first, path) is supplied, f"{label}: override missed {path}"
                assert _path_value(second, path) is supplied, f"{label}: repeated override missed {path}"
                normal = self.conduit.meld(spell_id=self.root_id)
                if not isinstance(supplied, int):
                    assert _path_value(normal, path) is not supplied, f"{label}: leaked into normal creation"
        for label in self.rejected_cases:
            del self.cases[label]
        if self.graph == "scalar":
            changed = self.conduit.meld(spell_id=self.root_id, override={"value": 97})
            assert isinstance(changed, ScalarRoot) and changed.value == 97
            normal = self.conduit.meld(spell_id=self.root_id)
            assert isinstance(normal, ScalarRoot) and normal.value == 13


def _average_ns(call: Callable[[], object], iterations: int, gc_mode: str) -> float:
    """Time only repeated calls; restore the process GC posture even on failure."""
    gc.collect()
    was_enabled = gc.isenabled()
    if gc_mode == "disabled":
        gc.disable()
    else:
        gc.enable()
    try:
        started = time.perf_counter_ns()
        for _ in range(iterations):
            call()
        return (time.perf_counter_ns() - started) / iterations
    finally:
        if was_enabled:
            gc.enable()
        else:
            gc.disable()


def _measure(world: MelderExperiment, settings: TimingSettings, mode: str) -> list[TimingResult]:
    """Warm/calibrate each case, rotate sample order and return raw plus summary timings."""
    labels = list(world.cases)
    counts: dict[str, int] = {}
    samples: dict[str, list[float]] = {label: [] for label in labels}
    for label, (call, _expected, _note) in world.cases.items():
        for _ in range(settings.warmup):
            call()
        probe_ns = _average_ns(call, 64, settings.gc_mode)
        counts[label] = settings.iterations or max(64, min(100_000, int(settings.sample_ms * 1e6 / probe_ns)))
    for repeat in range(settings.repeats):
        order = labels[repeat % len(labels):] + labels[:repeat % len(labels)]
        for label in order:
            samples[label].append(_average_ns(world.cases[label][0], counts[label], settings.gc_mode))
    baseline_ns = statistics.median(samples["normal"])
    return [
        TimingResult(
            graph=world.graph, mode=mode, case=label,
            iterations_per_sample=counts[label], samples_ns=values,
            median_ns=statistics.median(values), min_ns=min(values), max_ns=max(values),
            median_absolute_deviation_ns=statistics.median(abs(v - statistics.median(values)) for v in values),
            operations_per_second=1e9 / statistics.median(values),
            throughput_percent_of_normal=100 * baseline_ns / statistics.median(values),
            latency_ratio_to_normal=statistics.median(values) / baseline_ns,
            note=world.cases[label][2],
        )
        for label, values in samples.items()
    ]


def _source_fingerprints(repo: Path) -> dict[str, str]:
    """Hash runtime and input fixtures to detect concurrent edits during measurement."""
    paths = [
        path for path in (repo / "src/melder").rglob("*.py")
        if "_build_assets" not in path.parts and "__melder_cache__" not in path.parts
    ]
    paths.extend([
        Path(__file__), repo / "benchmarks/testing_other_di/test_shallow_all.py",
        repo / "benchmarks/testing_other_di/test_overrides_all.py", repo / "tests/mocks/spellbook/deep_layers.py",
    ])
    return {path.relative_to(repo).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(paths)}


def _render_report(
    rows: list[TimingResult], metadata: dict[str, object], rejected: list[dict[str, str]],
) -> str:
    """Render comparable case statistics and the limits of the measured workload."""
    lines = [
        "# Melder creation and override experiment", "",
        f"Python: {metadata['python']}", f"GIL enabled: {metadata['gil_enabled']}",
        f"GC during samples: {metadata['gc_mode']}; repeats: {metadata['repeats']}", "",
        "Warm single-thread calls; disk cache disabled. Setup, assertions and explicit GC are outside timing.",
        "Supplied dependencies may change graph work. Python root-only rows exclude all Melder behavior.",
        "No init={} API or runtime optimization is implemented by this experiment.", "",
        "| Mode | Graph | Case | Median us | Min-max us | Ops/s | % normal speed |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            f"| {row.mode} | {row.graph} | {row.case} | {row.median_ns / 1000:.3f} | "
            f"{row.min_ns / 1000:.3f}-{row.max_ns / 1000:.3f} | "
            f"{row.operations_per_second:,.0f} | {row.throughput_percent_of_normal:.1f} |"
        )
    if rejected:
        lines.extend(["", "Cases rejected by current runtime (not timed):"])
        lines.extend(
            f"- {item['mode']}/{item['graph']}/{item['case']}: {item['reason']}"
            for item in rejected
        )
    lines.extend(["", "Case semantics:"])
    lines.extend(f"- {row.graph}/{row.case}: {row.note}" for row in rows if row.mode == rows[0].mode)
    return "\n".join(lines) + "\n"


@pytest.mark.parametrize("graph", ["solo", "scalar", "shallow", "wide", "diamond", "deep"])
def test_melder_override_matrix_contracts(graph: str) -> None:
    """Verify the experimental workloads without any performance threshold or timing run."""
    world = MelderExperiment()
    try:
        world.setup(graph, "automatic")
        world.verify()
    finally:
        world.cleanup()


@pytest.mark.skipif(os.environ.get("MELDER_OVERRIDE_PERF") != "1", reason="Opt-in performance experiment")
def test_melder_creation_overrides_performance() -> None:
    """Run the unified Melder-only matrix and optionally preserve JSON/Markdown results.

    Source hashes before/after must match; concurrent edits make the run fail
    rather than silently mix code versions. Performance numbers never fail CI.
    """
    settings = TimingSettings.from_environment()
    graphs = _selection("MELDER_OVERRIDE_GRAPHS", ("solo", "scalar", "shallow", "wide", "diamond", "deep"))
    modes = _selection("MELDER_OVERRIDE_MODES", ("automatic", "dynamic"), default=("automatic",))
    repo = Path(__file__).resolve().parents[2]
    before = _source_fingerprints(repo)
    rows: list[TimingResult] = []
    rejected: list[dict[str, str]] = []
    for mode in modes:
        for graph in graphs:
            world = MelderExperiment()
            try:
                world.setup(graph, mode)
                world.verify()
                rejected.extend(
                    {"graph": graph, "mode": mode, "case": label, "reason": reason}
                    for label, reason in world.rejected_cases.items()
                )
                rows.extend(_measure(world, settings, mode))
            finally:
                world.cleanup()
    after = _source_fingerprints(repo)
    changed = sorted(path for path in before.keys() | after.keys() if before.get(path) != after.get(path))
    metadata: dict[str, object] = {
        "timestamp_utc": datetime.now(UTC).isoformat(), "python": sys.version,
        "executable": sys.executable, "platform": platform.platform(), "processor": platform.processor(),
        "logical_cpus": os.cpu_count(), "gil_enabled": sys._is_gil_enabled(),
        "free_threaded_build": sysconfig.get_config_var("Py_GIL_DISABLED"),
        "gc_mode": settings.gc_mode, "repeats": settings.repeats, "warmup": settings.warmup,
        "sample_ms": settings.sample_ms, "requested_iterations": settings.iterations,
        "source_changed_during_run": changed, "source_sha256": before,
    }
    report = _render_report(rows, metadata, rejected)
    output = os.environ.get("MELDER_OVERRIDE_OUTPUT")
    if output:
        directory = Path(output)
        directory.mkdir(parents=True, exist_ok=True)
        payload = {"metadata": metadata, "results": [asdict(row) for row in rows], "rejected_cases": rejected}
        (directory / "results.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
        (directory / "results.md").write_text(report, encoding="utf-8")
    print(report)
    assert not changed, f"Runtime changed during measurement; rerun a stable checkout: {changed}"
