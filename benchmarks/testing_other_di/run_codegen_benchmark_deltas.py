import cProfile
import argparse
import json
import os
import pstats
import time
from typing import Any, Callable, Dict, Optional, Sequence, Tuple

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook


class BenchmarkLeafA:
    """
    Purpose:
        Provide a no-dependency leaf used by the benchmark root graph.

    Contract:
        - Construction is side-effect free.
        - Instances are immutable for benchmark timing purposes.
    """

    def __init__(self) -> None:
        """
        Initialize a benchmark leaf instance.
        """
        self.value = "leaf-a"


class BenchmarkLeafB:
    """
    Purpose:
        Provide a second no-dependency leaf used by the benchmark root graph.

    Contract:
        - Construction is side-effect free.
        - Instances are immutable for benchmark timing purposes.
    """

    def __init__(self) -> None:
        """
        Initialize a benchmark leaf instance.
        """
        self.value = "leaf-b"


class BenchmarkRoot:
    """
    Purpose:
        Provide a small constructor dependency graph for root meld measurements.

    Contract:
        - Depends on two leaf types with deterministic constructor wiring.
        - Stores references only; does no external I/O.
    """

    def __init__(self, left: BenchmarkLeafA, right: BenchmarkLeafB) -> None:
        """
        Initialize root with deterministic dependencies.

        Args:
            left:
                Resolved `BenchmarkLeafA` instance.
            right:
                Resolved `BenchmarkLeafB` instance.
        """
        self.left = left
        self.right = right


class BenchmarkOverrideRoot:
    """
    Purpose:
        Provide a many-scoped root used for override specialization benchmarks.

    Contract:
        - Depends on `BenchmarkLeafA` so targeted override payloads exercise
          SocketRef mapping and substitution.
        - Used with `Existence.many` to avoid shared-instance override rejects.
    """

    def __init__(self, left: BenchmarkLeafA) -> None:
        """
        Initialize override benchmark root with one dependency.

        Args:
            left:
                Resolved `BenchmarkLeafA` instance or override substitution value.
        """
        self.left = left


class BenchmarkOverrideArgsRoot:
    """
    Purpose:
        Provide a many-scoped root used for root-args override benchmarks.

    Contract:
        - Uses a plain positional constructor argument to benchmark
          `__args__` override specialization.
        - Used with `Existence.many` to avoid shared-instance override rejects.
    """

    def __init__(self, value: int) -> None:
        """
        Initialize override-args benchmark root.

        Args:
            value:
                Positional value routed through `__args__` overrides.
        """
        self.value = value


class BenchmarkSpellspaceLeaf:
    """
    Purpose:
        Provide spellspace-scoped dependency for mixed workload sampling.

    Contract:
        - Construction is side-effect free.
        - Intended for `Existence.unique_per_spell_space` resolution.
    """

    def __init__(self) -> None:
        """
        Initialize a spellspace leaf instance.
        """
        self.value = "spellspace-leaf"


class BenchmarkSpellspaceRoot:
    """
    Purpose:
        Provide spellspace-scoped root for mixed workload benchmark calls.

    Contract:
        - Depends on `BenchmarkSpellspaceLeaf`.
        - Used only inside active spellspace scopes.
    """

    def __init__(self, leaf: BenchmarkSpellspaceLeaf) -> None:
        """
        Initialize spellspace root with one scoped dependency.

        Args:
            leaf:
                Resolved spellspace leaf instance.
        """
        self.leaf = leaf


class CodegenBenchmarkSession:
    """
    Purpose:
        Own one benchmark Spellbook/Conduit pair and expose route callables.

    Contract:
        - Manages setup and cleanup of runtime objects deterministically.
        - Provides repeatable warm, spellspace, mixed, and override execute operations.
        - `cleanup` is idempotent.
    """

    def __init__(self, *, frame_name: str, prewarm_root: bool) -> None:
        """
        Build benchmark runtime state for one sampling session.

        Args:
            frame_name:
                Unique frame/conduit name to avoid cross-session collisions.
            prewarm_root:
                Whether to resolve root once during initialization.
        """
        self._cleaned = False
        self._mixed_index = 0
        self._spellbook = Spellbook(aetheric_frame=frame_name)
        configuration = self._spellbook.get_configuration()
        configuration.set_property("phase_scheduler_workers_per_spellbook", 1)

        self._root_id = self._spellbook.bind(
            spell=BenchmarkRoot,
            existence=Existence.unique,
            permissions="create",
        )
        self._spellbook.bind(
            spell=BenchmarkLeafA,
            existence=Existence.unique,
            permissions="create",
        )
        self._spellbook.bind(
            spell=BenchmarkLeafB,
            existence=Existence.unique,
            permissions="create",
        )
        self._override_root_id = self._spellbook.bind(
            spell=BenchmarkOverrideRoot,
            existence=Existence.many,
            permissions="create",
        )
        self._override_args_root_id = self._spellbook.bind(
            spell=BenchmarkOverrideArgsRoot,
            existence=Existence.many,
            permissions="create",
        )
        self._spellspace_root_id = self._spellbook.bind(
            spell=BenchmarkSpellspaceRoot,
            existence=Existence.unique_per_spell_space,
            permissions="create",
        )
        self._spellbook.bind(
            spell=BenchmarkSpellspaceLeaf,
            existence=Existence.unique_per_spell_space,
            permissions="create",
        )

        self._conduit = self._spellbook.conjure(
            name=frame_name,
            automatic=True,
        )
        if prewarm_root:
            self.resolve_root_once()

    def resolve_root_once(self) -> None:
        """
        Resolve the primary root once.

        Contract:
            - Performs one `Conduit.meld` on the root spell id.
            - Raises AssertionError if the returned type is unexpected.
        """
        root = self._conduit.meld(spell=self._root_id)
        if not isinstance(root, BenchmarkRoot):
            raise AssertionError("Expected BenchmarkRoot from root meld.")

    def resolve_mixed_once(self) -> None:
        """
        Resolve one mixed workload iteration.

        Contract:
            - Alternates between root meld and spellspace-scoped root meld.
            - Increments internal iteration index exactly once per call.
        """
        if (self._mixed_index % 2) == 0:
            self.resolve_root_once()
        else:
            self.resolve_spellspace_once()
        self._mixed_index += 1

    def resolve_spellspace_once(self) -> None:
        """
        Resolve one spellspace-scoped root instance.

        Contract:
            - Enters an active spellspace scope for the call.
            - Raises AssertionError if the returned type is unexpected.
        """
        with self._conduit.enter_spellspace() as spellspace:
            scoped = spellspace.meld(spell=self._spellspace_root_id)
            if not isinstance(scoped, BenchmarkSpellspaceRoot):
                raise AssertionError(
                    "Expected BenchmarkSpellspaceRoot from spellspace meld."
                )

    def resolve_override_root_args_once(self) -> None:
        """
        Resolve one override call using root positional payload only.

        Contract:
            - Routes through override specialization without Phase10 patch-map apply.
            - Uses many-scoped root so repeated override calls remain valid.
        """
        overridden = self._conduit.meld(
            spell=self._override_args_root_id,
            spell_override=[7],
        )
        if not isinstance(overridden, BenchmarkOverrideArgsRoot):
            raise AssertionError("Expected BenchmarkOverrideArgsRoot from __args__ override meld.")

    def resolve_override_targeted_once(self) -> None:
        """
        Resolve one override call using targeted socket override payload.

        Contract:
            - Routes through TargetSpec -> SocketRef patch-map normalization.
            - Uses many-scoped root so repeated override calls remain valid.
        """
        overridden = self._conduit.meld(
            spell=self._override_root_id,
            spell_override={"left": BenchmarkLeafA()},
        )
        if not isinstance(overridden, BenchmarkOverrideRoot):
            raise AssertionError("Expected BenchmarkOverrideRoot from targeted override meld.")

    def cleanup(self) -> None:
        """
        Release benchmark runtime resources.

        Contract:
            - Idempotent.
            - Cleans conduit and resets singleton state for the next session.
        """
        if self._cleaned:
            return
        self._cleaned = True
        try:
            self._conduit.cleanup()
        finally:
            self._spellbook.cleanup()


def _reset_aether_singleton_for_benchmark() -> None:
    """
    Reset global Aether singleton and rebind Spellbook/Conduit class handles.

    Contract:
        - Ensures benchmark runs are isolated across sessions.
        - Leaves `Spellbook._aether` and `Conduit._aether` bound to a fresh Aether.
    """
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _build_arg_parser() -> argparse.ArgumentParser:
    """
    Build CLI parser for codegen benchmark delta runner.

    Returns:
        argparse.ArgumentParser:
            Parser configured with sampling, threshold, and output arguments.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Run repeatable Melder codegen benchmark samples and optionally "
            "compare against a baseline report."
        )
    )
    parser.add_argument("--sample-count", type=int, default=9)
    parser.add_argument("--warmup-count", type=int, default=1)
    parser.add_argument("--warm-to-cold-max-ratio", type=float, default=0.35)
    parser.add_argument("--mixed-to-cold-max-ratio", type=float, default=0.60)
    parser.add_argument("--route-to-cold-max-ratio", type=float, default=0.80)
    parser.add_argument("--profile-iteration-count", type=int, default=5)
    parser.add_argument("--profile-top-functions", type=int, default=12)
    parser.add_argument("--baseline-path", type=str, default="")
    parser.add_argument("--cold-max-regression-ratio", type=float, default=1.20)
    parser.add_argument("--warm-max-regression-ratio", type=float, default=1.20)
    parser.add_argument("--mixed-max-regression-ratio", type=float, default=1.20)
    parser.add_argument("--route-max-regression-ratio", type=float, default=1.20)
    parser.add_argument("--weighted-cprofile-weight", type=float, default=0.75)
    parser.add_argument("--weighted-time-weight", type=float, default=0.25)
    parser.add_argument("--weighted-max-regression-ratio", type=float, default=1.00)
    parser.add_argument(
        "--weighted-routes",
        type=str,
        default="warm_root_ns,warm_override_root_args_ns,warm_override_targeted_ns",
    )
    parser.add_argument(
        "--output-path",
        type=str,
        default="benchmarks/testing_other_di/results/codegen_benchmark_report.json",
    )
    parser.add_argument("--allow-gate-failure", action="store_true")
    parser.add_argument("--allow-baseline-regression", action="store_true")
    parser.add_argument("--print-json", action="store_true")
    parser.add_argument(
        "--pin-p-cores",
        action="store_true",
        help=(
            "Enable optional P-core process affinity pinning "
            "(equivalent to DI_PIN_P_CORES=1)."
        ),
    )
    return parser


def _run_cold_compile_iteration() -> None:
    """
    Execute one cold compile benchmark iteration.

    Contract:
        - Creates fresh benchmark runtime state.
        - Executes one root resolve.
        - Cleans all runtime state before returning.
    """
    session = CodegenBenchmarkSession(
        frame_name=_build_unique_session_name("codegen-cold"),
        prewarm_root=False,
    )
    try:
        session.resolve_root_once()
    finally:
        session.cleanup()


def _build_unique_session_name(prefix: str) -> str:
    """
    Build a unique benchmark frame/conduit name.

    Args:
        prefix:
            Prefix describing the benchmark mode.

    Returns:
        str:
            Unique name containing nanosecond timestamp.
    """
    return "{0}-{1}".format(prefix, time.perf_counter_ns())


def _load_json_report(path: str) -> Dict[str, Any]:
    """
    Load one JSON report file and validate top-level shape.

    Args:
        path:
            Report path to load.

    Returns:
        Dict[str, Any]:
            Parsed JSON object.

    Raises:
        ValueError:
            If file is missing or payload is not a dict.
    """
    if not path:
        raise ValueError("path must not be empty.")
    if not os.path.exists(path):
        raise ValueError("Baseline report does not exist: {0}".format(path))
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("Report payload must be a dict: {0}".format(path))
    return payload


def _extract_gate_report(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract gate report section from a benchmark report payload.

    Contract:
        - Accepts either full report payloads with `gate_report` field or a raw
          gate report object.
        - Raises ValueError when no dict-shaped gate report can be found.
    """
    nested = payload.get("gate_report")
    if isinstance(nested, dict):
        return nested
    if isinstance(payload, dict):
        return payload
    raise ValueError("Unable to extract gate report payload.")


def _extract_route_matrix_report(payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Extract optional route-matrix report section from a benchmark payload.

    Contract:
        - Returns route-matrix mapping when present and dict-shaped.
        - Returns None when no route-matrix report is available.
    """
    nested = payload.get("route_matrix_report")
    if isinstance(nested, dict):
        return nested
    return None


def _extract_route_profile_report(payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Extract optional route-profile report section from a benchmark payload.

    Contract:
        - Returns route-profile mapping when present and dict-shaped.
        - Returns None when no route-profile report is available.
    """
    nested = payload.get("route_profile_report")
    if isinstance(nested, dict):
        return nested
    return None


def _parse_weighted_routes(raw_value: str) -> Tuple[str, ...]:
    """
    Parse and normalize weighted-route CSV argument values.

    Contract:
        - Trims whitespace and removes empty segments.
        - Preserves first-seen order and drops duplicates.
        - Returns non-empty immutable tuple.
    """
    parts = [part.strip() for part in raw_value.split(",")]
    normalized = []
    seen = set()
    for part in parts:
        if not part:
            continue
        if part in seen:
            continue
        seen.add(part)
        normalized.append(part)
    if not normalized:
        raise ValueError("weighted_routes must contain at least one route key.")
    return tuple(normalized)


def _sample_callable_ns(
        *,
        fn: Callable[[], Any],
        sample_count: int,
        warmup_count: int,
) -> Tuple[int, ...]:
    """
    Collect nanosecond timing samples for one callable.

    Contract:
        - Executes warmup calls before timed samples.
        - Uses `time.perf_counter_ns`.
        - Returns immutable sample tuple.
    """
    if fn is None:
        raise ValueError("fn must not be None.")
    if sample_count < 1:
        raise ValueError("sample_count must be >= 1.")
    if warmup_count < 0:
        raise ValueError("warmup_count must be >= 0.")

    for _ in range(warmup_count):
        fn()

    samples = []
    for _ in range(sample_count):
        start_ns = time.perf_counter_ns()
        fn()
        end_ns = time.perf_counter_ns()
        samples.append(end_ns - start_ns)
    return tuple(samples)


def _normalize_benchmark_samples(
        *,
        name: str,
        samples: Sequence[int],
) -> Tuple[int, ...]:
    """
    Normalize one benchmark sample sequence and enforce numeric contract rules.

    Contract:
        - Requires non-empty int-only sample values.
        - Rejects negative values.
        - Returns immutable tuple for downstream median/ratio calculations.
    """
    if samples is None:
        raise ValueError("{0} samples must not be None.".format(name))
    normalized_samples = []
    for sample in samples:
        if not isinstance(sample, int):
            raise ValueError("{0} samples must contain int values only.".format(name))
        if sample < 0:
            raise ValueError("{0} samples must be >= 0.".format(name))
        normalized_samples.append(sample)
    if not normalized_samples:
        raise ValueError("{0} samples must not be empty.".format(name))
    return tuple(normalized_samples)


def _median_ns(samples: Sequence[int]) -> int:
    """
    Compute median nanosecond value using deterministic integer arithmetic.

    Contract:
        - Input sequence must be non-empty.
        - Even-length medians are floor-divided integer midpoint values.
    """
    sorted_samples = sorted(samples)
    if not sorted_samples:
        raise ValueError("samples must not be empty.")
    middle_index = len(sorted_samples) // 2
    if (len(sorted_samples) % 2) == 1:
        return sorted_samples[middle_index]
    return (sorted_samples[middle_index - 1] + sorted_samples[middle_index]) // 2


def _collect_codegen_benchmark_samples_ns(
        *,
        cold_compile_fn: Callable[[], Any],
        warm_execute_fn: Callable[[], Any],
        mixed_execute_fn: Callable[[], Any],
        sample_count: int,
        warmup_count: int,
) -> Dict[str, Tuple[int, ...]]:
    """
    Collect cold/warm/mixed benchmark sample tuples for gate evaluation.

    Contract:
        - Applies identical sample/warmup counts to all benchmark lanes.
        - Returns a stable key schema used by report and gate evaluators.
    """
    return {
        "cold_compile_ns": _sample_callable_ns(
            fn=cold_compile_fn,
            sample_count=sample_count,
            warmup_count=warmup_count,
        ),
        "warm_execute_ns": _sample_callable_ns(
            fn=warm_execute_fn,
            sample_count=sample_count,
            warmup_count=warmup_count,
        ),
        "mixed_execute_ns": _sample_callable_ns(
            fn=mixed_execute_fn,
            sample_count=sample_count,
            warmup_count=warmup_count,
        ),
    }


def _evaluate_codegen_benchmark_gates(
        *,
        cold_compile_ns: Sequence[int],
        warm_execute_ns: Sequence[int],
        mixed_execute_ns: Sequence[int],
        warm_to_cold_max_ratio: float,
        mixed_to_cold_max_ratio: float,
) -> Dict[str, Any]:
    """
    Evaluate warm/mixed benchmark gate ratios relative to cold compile median.

    Contract:
        - Produces deterministic median and ratio fields consumed by summary output.
        - Fails gates when configured ratio thresholds are exceeded.
    """
    if warm_to_cold_max_ratio <= 0:
        raise ValueError("warm_to_cold_max_ratio must be > 0.")
    if mixed_to_cold_max_ratio <= 0:
        raise ValueError("mixed_to_cold_max_ratio must be > 0.")

    cold_samples = _normalize_benchmark_samples(
        name="cold_compile_ns",
        samples=cold_compile_ns,
    )
    warm_samples = _normalize_benchmark_samples(
        name="warm_execute_ns",
        samples=warm_execute_ns,
    )
    mixed_samples = _normalize_benchmark_samples(
        name="mixed_execute_ns",
        samples=mixed_execute_ns,
    )

    cold_compile_median_ns = _median_ns(cold_samples)
    if cold_compile_median_ns < 1:
        raise ValueError("cold compile median must be >= 1.")
    warm_execute_median_ns = _median_ns(warm_samples)
    mixed_execute_median_ns = _median_ns(mixed_samples)

    warm_to_cold_ratio = warm_execute_median_ns / cold_compile_median_ns
    mixed_to_cold_ratio = mixed_execute_median_ns / cold_compile_median_ns

    failures = []
    if warm_to_cold_ratio > warm_to_cold_max_ratio:
        failures.append(
            "warm_execute ratio {0:.4f} exceeded {1:.4f}".format(
                warm_to_cold_ratio,
                warm_to_cold_max_ratio,
            )
        )
    if mixed_to_cold_ratio > mixed_to_cold_max_ratio:
        failures.append(
            "mixed_execute ratio {0:.4f} exceeded {1:.4f}".format(
                mixed_to_cold_ratio,
                mixed_to_cold_max_ratio,
            )
        )

    return {
        "cold_compile_median_ns": cold_compile_median_ns,
        "warm_execute_median_ns": warm_execute_median_ns,
        "mixed_execute_median_ns": mixed_execute_median_ns,
        "warm_to_cold_ratio": warm_to_cold_ratio,
        "mixed_to_cold_ratio": mixed_to_cold_ratio,
        "thresholds": {
            "warm_to_cold_max_ratio": warm_to_cold_max_ratio,
            "mixed_to_cold_max_ratio": mixed_to_cold_max_ratio,
        },
        "failures": tuple(failures),
        "passed": len(failures) == 0,
    }


def _evaluate_codegen_benchmark_baseline_deltas(
        *,
        current_gate_report: Dict[str, Any],
        baseline_gate_report: Dict[str, Any],
        cold_compile_max_regression_ratio: float,
        warm_execute_max_regression_ratio: float,
        mixed_execute_max_regression_ratio: float,
) -> Dict[str, Any]:
    """
    Compare current gate medians against baseline medians with ratio thresholds.

    Contract:
        - Validates required median fields in both report payloads.
        - Emits ratio fields consumed by summary output and exit-code checks.
        - Fails when any configured regression threshold is exceeded.
    """
    if cold_compile_max_regression_ratio <= 0:
        raise ValueError("cold_compile_max_regression_ratio must be > 0.")
    if warm_execute_max_regression_ratio <= 0:
        raise ValueError("warm_execute_max_regression_ratio must be > 0.")
    if mixed_execute_max_regression_ratio <= 0:
        raise ValueError("mixed_execute_max_regression_ratio must be > 0.")

    def _require_median(report: Dict[str, Any], key: str, label: str) -> int:
        value = report.get(key)
        if not isinstance(value, int):
            raise ValueError(
                "{0}.{1} must be an int.".format(label, key)
            )
        if value < 1:
            raise ValueError(
                "{0}.{1} must be >= 1.".format(label, key)
            )
        return value

    current_cold = _require_median(
        current_gate_report,
        "cold_compile_median_ns",
        "current_gate_report",
    )
    current_warm = _require_median(
        current_gate_report,
        "warm_execute_median_ns",
        "current_gate_report",
    )
    current_mixed = _require_median(
        current_gate_report,
        "mixed_execute_median_ns",
        "current_gate_report",
    )
    baseline_cold = _require_median(
        baseline_gate_report,
        "cold_compile_median_ns",
        "baseline_gate_report",
    )
    baseline_warm = _require_median(
        baseline_gate_report,
        "warm_execute_median_ns",
        "baseline_gate_report",
    )
    baseline_mixed = _require_median(
        baseline_gate_report,
        "mixed_execute_median_ns",
        "baseline_gate_report",
    )

    ratios = {
        "cold_compile_ratio": current_cold / baseline_cold,
        "warm_execute_ratio": current_warm / baseline_warm,
        "mixed_execute_ratio": current_mixed / baseline_mixed,
    }
    failures = []
    if ratios["cold_compile_ratio"] > cold_compile_max_regression_ratio:
        failures.append(
            "cold_compile ratio {0:.4f} exceeded {1:.4f}".format(
                ratios["cold_compile_ratio"],
                cold_compile_max_regression_ratio,
            )
        )
    if ratios["warm_execute_ratio"] > warm_execute_max_regression_ratio:
        failures.append(
            "warm_execute ratio {0:.4f} exceeded {1:.4f}".format(
                ratios["warm_execute_ratio"],
                warm_execute_max_regression_ratio,
            )
        )
    if ratios["mixed_execute_ratio"] > mixed_execute_max_regression_ratio:
        failures.append(
            "mixed_execute ratio {0:.4f} exceeded {1:.4f}".format(
                ratios["mixed_execute_ratio"],
                mixed_execute_max_regression_ratio,
            )
        )

    return {
        "current_medians_ns": {
            "cold_compile_median_ns": current_cold,
            "warm_execute_median_ns": current_warm,
            "mixed_execute_median_ns": current_mixed,
        },
        "baseline_medians_ns": {
            "cold_compile_median_ns": baseline_cold,
            "warm_execute_median_ns": baseline_warm,
            "mixed_execute_median_ns": baseline_mixed,
        },
        "ratios": ratios,
        "thresholds": {
            "cold_compile_max_regression_ratio": cold_compile_max_regression_ratio,
            "warm_execute_max_regression_ratio": warm_execute_max_regression_ratio,
            "mixed_execute_max_regression_ratio": mixed_execute_max_regression_ratio,
        },
        "failures": tuple(failures),
        "passed": len(failures) == 0,
    }


def _collect_route_matrix_samples(
        *,
        session: CodegenBenchmarkSession,
        sample_count: int,
        warmup_count: int,
) -> Dict[str, Tuple[int, ...]]:
    """
    Collect per-route warm-path sample sets for optimization matrix reporting.

    Contract:
        - Includes root, spellspace, mixed, and two override routes.
        - Uses identical sample/warmup counts per route.
    """
    return {
        "warm_root_ns": _sample_callable_ns(
            fn=session.resolve_root_once,
            sample_count=sample_count,
            warmup_count=warmup_count,
        ),
        "warm_spellspace_ns": _sample_callable_ns(
            fn=session.resolve_spellspace_once,
            sample_count=sample_count,
            warmup_count=warmup_count,
        ),
        "warm_override_root_args_ns": _sample_callable_ns(
            fn=session.resolve_override_root_args_once,
            sample_count=sample_count,
            warmup_count=warmup_count,
        ),
        "warm_override_targeted_ns": _sample_callable_ns(
            fn=session.resolve_override_targeted_once,
            sample_count=sample_count,
            warmup_count=warmup_count,
        ),
        "warm_mixed_ns": _sample_callable_ns(
            fn=session.resolve_mixed_once,
            sample_count=sample_count,
            warmup_count=warmup_count,
        ),
    }


def _build_route_callable_map(session: CodegenBenchmarkSession) -> Dict[str, Callable[[], Any]]:
    """
    Build route-name to callable mapping used by timing and profiling collectors.

    Contract:
        - Route keys match route matrix report key schema.
        - Values are zero-argument execute callables.
    """
    return {
        "warm_root_ns": session.resolve_root_once,
        "warm_spellspace_ns": session.resolve_spellspace_once,
        "warm_override_root_args_ns": session.resolve_override_root_args_once,
        "warm_override_targeted_ns": session.resolve_override_targeted_once,
        "warm_mixed_ns": session.resolve_mixed_once,
    }


def _profile_callable(
        *,
        fn: Callable[[], Any],
        profile_iteration_count: int,
        warmup_count: int,
        profile_top_functions: int,
) -> Dict[str, Any]:
    """
    Capture one cProfile sample payload for a callable.

    Contract:
        - Performs warmup calls before profiled iterations.
        - Profiles exactly `profile_iteration_count` calls under one profiler.
        - Returns aggregate call/time counters and top cumulative hotspots.
    """
    if profile_iteration_count < 1:
        raise ValueError("profile_iteration_count must be >= 1.")
    if warmup_count < 0:
        raise ValueError("warmup_count must be >= 0.")
    if profile_top_functions < 1:
        raise ValueError("profile_top_functions must be >= 1.")

    for _ in range(warmup_count):
        fn()

    profile = cProfile.Profile()
    start_ns = time.perf_counter_ns()
    profile.enable()
    for _ in range(profile_iteration_count):
        fn()
    profile.disable()
    end_ns = time.perf_counter_ns()

    stats = pstats.Stats(profile)
    top_functions = []
    sorted_rows = sorted(
        stats.stats.items(),
        key=lambda item: item[1][3],
        reverse=True,
    )
    for function_key, values in sorted_rows[:profile_top_functions]:
        top_functions.append(
            {
                "function": "{0}:{1}:{2}".format(
                    function_key[0],
                    function_key[1],
                    function_key[2],
                ),
                "primitive_calls": int(values[0]),
                "total_calls": int(values[1]),
                "total_time_seconds": float(values[2]),
                "cumulative_time_seconds": float(values[3]),
            }
        )

    elapsed_ns = end_ns - start_ns
    return {
        "iteration_count": profile_iteration_count,
        "warmup_count": warmup_count,
        "wall_total_ns": elapsed_ns,
        "wall_ns_per_iteration": elapsed_ns / profile_iteration_count,
        "total_calls": int(stats.total_calls),
        "primitive_calls": int(stats.prim_calls),
        "total_calls_per_iteration": stats.total_calls / profile_iteration_count,
        "primitive_calls_per_iteration": stats.prim_calls / profile_iteration_count,
        "cpu_total_seconds": float(stats.total_tt),
        "cpu_seconds_per_iteration": float(stats.total_tt) / profile_iteration_count,
        "top_functions_by_cumulative_time": top_functions,
    }


def _collect_route_profile_report(
        *,
        session: CodegenBenchmarkSession,
        profile_iteration_count: int,
        warmup_count: int,
        profile_top_functions: int,
) -> Dict[str, Any]:
    """
    Collect cProfile snapshots for each benchmark route.

    Contract:
        - Uses one cProfile capture per route key.
        - Route keys match route matrix report route names.
    """
    route_callables = _build_route_callable_map(session)
    route_profiles: Dict[str, Dict[str, Any]] = {}
    for route_name, route_callable in route_callables.items():
        route_profiles[route_name] = _profile_callable(
            fn=route_callable,
            profile_iteration_count=profile_iteration_count,
            warmup_count=warmup_count,
            profile_top_functions=profile_top_functions,
        )
    return {
        "profile_iteration_count": profile_iteration_count,
        "warmup_count": warmup_count,
        "profile_top_functions": profile_top_functions,
        "routes": route_profiles,
    }


def _evaluate_route_matrix_report(
        *,
        route_samples_ns: Dict[str, Sequence[int]],
        cold_compile_median_ns: int,
        route_to_cold_max_ratio: float,
) -> Dict[str, Any]:
    """
    Evaluate per-route medians against a shared cold-relative threshold.

    Contract:
        - Uses median sample values per route.
        - Fails routes whose median/cold ratio exceeds configured threshold.
    """
    if cold_compile_median_ns < 1:
        raise ValueError("cold_compile_median_ns must be >= 1.")
    if route_to_cold_max_ratio <= 0:
        raise ValueError("route_to_cold_max_ratio must be > 0.")

    route_medians_ns: Dict[str, int] = {}
    route_to_cold_ratios: Dict[str, float] = {}
    failures = []
    for route_name, samples in route_samples_ns.items():
        normalized_samples = _normalize_benchmark_samples(
            name=route_name,
            samples=samples,
        )
        median_ns = _median_ns(normalized_samples)
        ratio = median_ns / cold_compile_median_ns
        route_medians_ns[route_name] = median_ns
        route_to_cold_ratios[route_name] = ratio
        if ratio > route_to_cold_max_ratio:
            failures.append(
                "{0} ratio {1:.4f} exceeded {2:.4f}".format(
                    route_name,
                    ratio,
                    route_to_cold_max_ratio,
                )
            )

    return {
        "route_medians_ns": route_medians_ns,
        "route_to_cold_ratios": route_to_cold_ratios,
        "thresholds": {
            "route_to_cold_max_ratio": route_to_cold_max_ratio,
        },
        "failures": tuple(failures),
        "passed": len(failures) == 0,
    }


def _evaluate_route_matrix_baseline_deltas(
        *,
        current_route_report: Dict[str, Any],
        baseline_route_report: Dict[str, Any],
        route_max_regression_ratio: float,
) -> Dict[str, Any]:
    """
    Compare per-route warm medians against baseline medians.

    Contract:
        - Requires identical route keys between current and baseline reports.
        - Fails each route whose current/baseline ratio exceeds threshold.
    """
    if route_max_regression_ratio <= 0:
        raise ValueError("route_max_regression_ratio must be > 0.")

    current_medians = current_route_report.get("route_medians_ns")
    baseline_medians = baseline_route_report.get("route_medians_ns")
    if not isinstance(current_medians, dict):
        raise ValueError("current_route_report.route_medians_ns must be a dict.")
    if not isinstance(baseline_medians, dict):
        raise ValueError("baseline_route_report.route_medians_ns must be a dict.")

    current_route_names = tuple(sorted(current_medians.keys()))
    baseline_route_names = tuple(sorted(baseline_medians.keys()))
    if current_route_names != baseline_route_names:
        raise ValueError("route matrix keys differ between current and baseline reports.")

    ratios: Dict[str, float] = {}
    deltas_ns: Dict[str, int] = {}
    failures = []
    for route_name in current_route_names:
        current_value = current_medians[route_name]
        baseline_value = baseline_medians[route_name]
        if not isinstance(current_value, int):
            raise ValueError(
                "current_route_report.route_medians_ns[{0}] must be an int.".format(
                    route_name
                )
            )
        if not isinstance(baseline_value, int):
            raise ValueError(
                "baseline_route_report.route_medians_ns[{0}] must be an int.".format(
                    route_name
                )
            )
        if baseline_value < 1:
            raise ValueError(
                "baseline_route_report.route_medians_ns[{0}] must be >= 1.".format(
                    route_name
                )
            )

        ratio = current_value / baseline_value
        delta = current_value - baseline_value
        ratios[route_name] = ratio
        deltas_ns["{0}_delta_ns".format(route_name)] = delta
        if ratio > route_max_regression_ratio:
            failures.append(
                "{0} ratio {1:.4f} exceeded {2:.4f}".format(
                    route_name,
                    ratio,
                    route_max_regression_ratio,
                )
            )

    return {
        "current_route_medians_ns": dict(current_medians),
        "baseline_route_medians_ns": dict(baseline_medians),
        "route_ratios": ratios,
        "route_deltas_ns": deltas_ns,
        "thresholds": {
            "route_max_regression_ratio": route_max_regression_ratio,
        },
        "failures": tuple(failures),
        "passed": len(failures) == 0,
    }


def _evaluate_weighted_route_regression(
        *,
        current_route_report: Dict[str, Any],
        baseline_route_report: Dict[str, Any],
        current_route_profile_report: Dict[str, Any],
        baseline_route_profile_report: Dict[str, Any],
        weighted_routes: Sequence[str],
        weighted_cprofile_weight: float,
        weighted_time_weight: float,
        weighted_max_regression_ratio: float,
) -> Dict[str, Any]:
    """
    Evaluate weighted route regression with cProfile/time blend.

    Contract:
        - Weighted ratio = (`cProfile_ratio` * cprofile_weight) + (`time_ratio` * time_weight).
        - Lower ratio is better; values above threshold fail.
        - Uses route medians for time ratio and total calls per iteration for profile ratio.
    """
    if weighted_cprofile_weight <= 0:
        raise ValueError("weighted_cprofile_weight must be > 0.")
    if weighted_time_weight <= 0:
        raise ValueError("weighted_time_weight must be > 0.")
    if abs((weighted_cprofile_weight + weighted_time_weight) - 1.0) > 1e-9:
        raise ValueError("weighted_cprofile_weight + weighted_time_weight must equal 1.0.")
    if weighted_max_regression_ratio <= 0:
        raise ValueError("weighted_max_regression_ratio must be > 0.")

    current_route_medians = current_route_report.get("route_medians_ns")
    baseline_route_medians = baseline_route_report.get("route_medians_ns")
    current_route_profiles = current_route_profile_report.get("routes")
    baseline_route_profiles = baseline_route_profile_report.get("routes")
    if not isinstance(current_route_medians, dict):
        raise ValueError("current_route_report.route_medians_ns must be a dict.")
    if not isinstance(baseline_route_medians, dict):
        raise ValueError("baseline_route_report.route_medians_ns must be a dict.")
    if not isinstance(current_route_profiles, dict):
        raise ValueError("current_route_profile_report.routes must be a dict.")
    if not isinstance(baseline_route_profiles, dict):
        raise ValueError("baseline_route_profile_report.routes must be a dict.")
    if not weighted_routes:
        raise ValueError("weighted_routes must not be empty.")

    route_scores: Dict[str, Dict[str, Any]] = {}
    failures = []
    weighted_ratio_sum = 0.0
    for route_name in weighted_routes:
        current_time_ns = current_route_medians.get(route_name)
        baseline_time_ns = baseline_route_medians.get(route_name)
        current_profile = current_route_profiles.get(route_name)
        baseline_profile = baseline_route_profiles.get(route_name)
        if not isinstance(current_time_ns, int):
            raise ValueError("current_route_report.route_medians_ns[{0}] must be an int.".format(route_name))
        if not isinstance(baseline_time_ns, int):
            raise ValueError("baseline_route_report.route_medians_ns[{0}] must be an int.".format(route_name))
        if baseline_time_ns < 1:
            raise ValueError("baseline_route_report.route_medians_ns[{0}] must be >= 1.".format(route_name))
        if not isinstance(current_profile, dict):
            raise ValueError("current_route_profile_report.routes[{0}] must be a dict.".format(route_name))
        if not isinstance(baseline_profile, dict):
            raise ValueError("baseline_route_profile_report.routes[{0}] must be a dict.".format(route_name))

        current_calls = current_profile.get("total_calls_per_iteration")
        baseline_calls = baseline_profile.get("total_calls_per_iteration")
        if not isinstance(current_calls, (float, int)):
            raise ValueError(
                "current_route_profile_report.routes[{0}].total_calls_per_iteration must be numeric.".format(
                    route_name
                )
            )
        if not isinstance(baseline_calls, (float, int)):
            raise ValueError(
                "baseline_route_profile_report.routes[{0}].total_calls_per_iteration must be numeric.".format(
                    route_name
                )
            )
        if baseline_calls <= 0:
            raise ValueError(
                "baseline_route_profile_report.routes[{0}].total_calls_per_iteration must be > 0.".format(
                    route_name
                )
            )

        time_ratio = current_time_ns / baseline_time_ns
        cprofile_ratio = float(current_calls) / float(baseline_calls)
        weighted_ratio = (
                (weighted_cprofile_weight * cprofile_ratio)
                + (weighted_time_weight * time_ratio)
        )
        route_passed = weighted_ratio <= weighted_max_regression_ratio
        if not route_passed:
            failures.append(
                "{0} weighted ratio {1:.4f} exceeded {2:.4f}".format(
                    route_name,
                    weighted_ratio,
                    weighted_max_regression_ratio,
                )
            )
        route_scores[route_name] = {
            "current_time_median_ns": current_time_ns,
            "baseline_time_median_ns": baseline_time_ns,
            "time_ratio": time_ratio,
            "current_profile_calls_per_iteration": float(current_calls),
            "baseline_profile_calls_per_iteration": float(baseline_calls),
            "cprofile_ratio": cprofile_ratio,
            "weighted_ratio": weighted_ratio,
            "passed": route_passed,
        }
        weighted_ratio_sum += weighted_ratio

    overall_weighted_ratio = weighted_ratio_sum / len(weighted_routes)
    if overall_weighted_ratio > weighted_max_regression_ratio:
        failures.append(
            "overall weighted ratio {0:.4f} exceeded {1:.4f}".format(
                overall_weighted_ratio,
                weighted_max_regression_ratio,
            )
        )

    return {
        "weighted_routes": tuple(weighted_routes),
        "weights": {
            "cprofile": weighted_cprofile_weight,
            "time": weighted_time_weight,
        },
        "thresholds": {
            "weighted_max_regression_ratio": weighted_max_regression_ratio,
        },
        "route_scores": route_scores,
        "overall_weighted_ratio": overall_weighted_ratio,
        "failures": tuple(failures),
        "passed": len(failures) == 0,
    }


def run_codegen_benchmark_report(arguments: argparse.Namespace) -> Dict[str, Any]:
    """
    Execute benchmark sampling and optional baseline delta evaluation.

    Args:
        arguments:
            Parsed CLI arguments.

    Returns:
        Dict[str, Any]:
            Combined benchmark report with samples, gate report, and optional
            baseline delta report.
    """
    if bool(arguments.pin_p_cores):
        os.environ["DI_PIN_P_CORES"] = "1"
    from benchmarks.p_core_affinity.p_core_affinity import (
        get_or_apply_p_core_affinity_from_env,
    )

    affinity_status = get_or_apply_p_core_affinity_from_env()
    _reset_aether_singleton_for_benchmark()
    warm_session = CodegenBenchmarkSession(
        frame_name=_build_unique_session_name("codegen-warm"),
        prewarm_root=True,
    )
    try:
        samples = _collect_codegen_benchmark_samples_ns(
            cold_compile_fn=_run_cold_compile_iteration,
            warm_execute_fn=warm_session.resolve_root_once,
            mixed_execute_fn=warm_session.resolve_mixed_once,
            sample_count=arguments.sample_count,
            warmup_count=arguments.warmup_count,
        )
        gate_report = _evaluate_codegen_benchmark_gates(
            cold_compile_ns=samples["cold_compile_ns"],
            warm_execute_ns=samples["warm_execute_ns"],
            mixed_execute_ns=samples["mixed_execute_ns"],
            warm_to_cold_max_ratio=arguments.warm_to_cold_max_ratio,
            mixed_to_cold_max_ratio=arguments.mixed_to_cold_max_ratio,
        )
        route_samples_ns = _collect_route_matrix_samples(
            session=warm_session,
            sample_count=arguments.sample_count,
            warmup_count=arguments.warmup_count,
        )
        route_matrix_report = _evaluate_route_matrix_report(
            route_samples_ns=route_samples_ns,
            cold_compile_median_ns=gate_report["cold_compile_median_ns"],
            route_to_cold_max_ratio=arguments.route_to_cold_max_ratio,
        )
        route_profile_report = _collect_route_profile_report(
            session=warm_session,
            profile_iteration_count=arguments.profile_iteration_count,
            warmup_count=arguments.warmup_count,
            profile_top_functions=arguments.profile_top_functions,
        )
    finally:
        try:
            warm_session.cleanup()
        finally:
            _reset_aether_singleton_for_benchmark()

    report: Dict[str, Any] = {
        "schema_version": "codegen_benchmark_report_v3",
        "generated_at_unix": time.time(),
        "sample_count": arguments.sample_count,
        "warmup_count": arguments.warmup_count,
        "affinity": affinity_status,
        "samples_ns": samples,
        "gate_report": gate_report,
        "route_samples_ns": route_samples_ns,
        "route_matrix_report": route_matrix_report,
        "route_profile_report": route_profile_report,
    }

    baseline_path = arguments.baseline_path.strip()
    if baseline_path:
        baseline_payload = _load_json_report(baseline_path)
        baseline_gate_report = _extract_gate_report(baseline_payload)
        baseline_delta_report = _evaluate_codegen_benchmark_baseline_deltas(
            current_gate_report=gate_report,
            baseline_gate_report=baseline_gate_report,
            cold_compile_max_regression_ratio=arguments.cold_max_regression_ratio,
            warm_execute_max_regression_ratio=arguments.warm_max_regression_ratio,
            mixed_execute_max_regression_ratio=arguments.mixed_max_regression_ratio,
        )
        report["baseline_path"] = baseline_path
        report["baseline_delta_report"] = baseline_delta_report
        baseline_route_matrix_report = _extract_route_matrix_report(baseline_payload)
        if baseline_route_matrix_report is not None:
            report["route_matrix_baseline_delta_report"] = (
                _evaluate_route_matrix_baseline_deltas(
                    current_route_report=route_matrix_report,
                    baseline_route_report=baseline_route_matrix_report,
                    route_max_regression_ratio=arguments.route_max_regression_ratio,
                )
            )
        baseline_route_profile_report = _extract_route_profile_report(baseline_payload)
        if (
                baseline_route_matrix_report is not None
                and baseline_route_profile_report is not None
        ):
            weighted_routes = _parse_weighted_routes(arguments.weighted_routes)
            report["weighted_score_report"] = _evaluate_weighted_route_regression(
                current_route_report=route_matrix_report,
                baseline_route_report=baseline_route_matrix_report,
                current_route_profile_report=route_profile_report,
                baseline_route_profile_report=baseline_route_profile_report,
                weighted_routes=weighted_routes,
                weighted_cprofile_weight=arguments.weighted_cprofile_weight,
                weighted_time_weight=arguments.weighted_time_weight,
                weighted_max_regression_ratio=arguments.weighted_max_regression_ratio,
            )

    return report


def _write_report(path: str, report: Dict[str, Any]) -> None:
    """
    Persist benchmark report JSON to disk.

    Contract:
        - Creates parent directory when missing.
        - Writes deterministic JSON with sorted keys.
    """
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, sort_keys=True)


def _compute_exit_code(
        *,
        report: Dict[str, Any],
        allow_gate_failure: bool,
        allow_baseline_regression: bool,
) -> int:
    """
    Compute process exit code from gate and baseline pass flags.

    Contract:
        - Returns `1` when gate failures are not allowed and gate report failed.
        - Returns `1` when baseline regressions are not allowed and baseline
          report exists with failed status.
        - Returns `0` otherwise.
    """
    exit_code = 0
    gate_report = report["gate_report"]
    if (not allow_gate_failure) and (not gate_report["passed"]):
        exit_code = 1

    route_matrix_report = report.get("route_matrix_report")
    if (
            route_matrix_report is not None
            and (not allow_gate_failure)
            and (not route_matrix_report["passed"])
    ):
        exit_code = 1

    baseline_delta_report = report.get("baseline_delta_report")
    if (
            baseline_delta_report is not None
            and (not allow_baseline_regression)
            and (not baseline_delta_report["passed"])
    ):
        exit_code = 1

    route_matrix_baseline_delta_report = report.get("route_matrix_baseline_delta_report")
    if (
            route_matrix_baseline_delta_report is not None
            and (not allow_baseline_regression)
            and (not route_matrix_baseline_delta_report["passed"])
    ):
        exit_code = 1
    weighted_score_report = report.get("weighted_score_report")
    if (
            weighted_score_report is not None
            and (not allow_baseline_regression)
            and (not weighted_score_report["passed"])
    ):
        exit_code = 1
    return exit_code


def _print_summary(report: Dict[str, Any]) -> None:
    """
    Print a compact human-readable summary of benchmark results.

    Contract:
        - Always prints gate medians and ratio pass state.
        - Prints baseline delta ratio pass state when present.
    """
    gate_report = report["gate_report"]
    print(
        "[codegen-benchmark] medians(ns): cold={0}, warm={1}, mixed={2}".format(
            gate_report["cold_compile_median_ns"],
            gate_report["warm_execute_median_ns"],
            gate_report["mixed_execute_median_ns"],
        )
    )
    print(
        "[codegen-benchmark] ratios: warm/cold={0:.4f}, mixed/cold={1:.4f}, passed={2}".format(
            gate_report["warm_to_cold_ratio"],
            gate_report["mixed_to_cold_ratio"],
            gate_report["passed"],
        )
    )
    baseline_delta_report = report.get("baseline_delta_report")
    if baseline_delta_report is not None:
        ratios = baseline_delta_report["ratios"]
        print(
            "[codegen-benchmark] baseline ratios: cold={0:.4f}, warm={1:.4f}, mixed={2:.4f}, passed={3}".format(
                ratios["cold_compile_ratio"],
                ratios["warm_execute_ratio"],
                ratios["mixed_execute_ratio"],
                baseline_delta_report["passed"],
            )
        )
    route_matrix_report = report.get("route_matrix_report")
    if route_matrix_report is not None:
        route_ratios = route_matrix_report["route_to_cold_ratios"]
        print(
            "[codegen-benchmark] route ratios: "
            "warm_root={0:.4f}, spellspace={1:.4f}, "
            "override_args={2:.4f}, override_targeted={3:.4f}, mixed={4:.4f}, passed={5}".format(
                route_ratios["warm_root_ns"],
                route_ratios["warm_spellspace_ns"],
                route_ratios["warm_override_root_args_ns"],
                route_ratios["warm_override_targeted_ns"],
                route_ratios["warm_mixed_ns"],
                route_matrix_report["passed"],
            )
        )
    route_matrix_baseline_delta_report = report.get("route_matrix_baseline_delta_report")
    if route_matrix_baseline_delta_report is not None:
        route_delta_ratios = route_matrix_baseline_delta_report["route_ratios"]
        print(
            "[codegen-benchmark] route baseline ratios: "
            "warm_root={0:.4f}, spellspace={1:.4f}, "
            "override_args={2:.4f}, override_targeted={3:.4f}, mixed={4:.4f}, passed={5}".format(
                route_delta_ratios["warm_root_ns"],
                route_delta_ratios["warm_spellspace_ns"],
                route_delta_ratios["warm_override_root_args_ns"],
                route_delta_ratios["warm_override_targeted_ns"],
                route_delta_ratios["warm_mixed_ns"],
                route_matrix_baseline_delta_report["passed"],
            )
        )
    weighted_score_report = report.get("weighted_score_report")
    if weighted_score_report is not None:
        print(
            "[codegen-benchmark] weighted score: overall_ratio={0:.4f}, passed={1}, weights(cprofile={2:.2f}, time={3:.2f})".format(
                weighted_score_report["overall_weighted_ratio"],
                weighted_score_report["passed"],
                weighted_score_report["weights"]["cprofile"],
                weighted_score_report["weights"]["time"],
            )
        )


def main(argv: Optional[Sequence[str]] = None) -> int:
    """
    Run codegen benchmark delta workflow.

    Args:
        argv:
            Optional argument sequence for programmatic invocation.

    Returns:
        int:
            Process-style exit code (`0` pass, `1` failure).
    """
    parser = _build_arg_parser()
    arguments = parser.parse_args(argv)

    report = run_codegen_benchmark_report(arguments)
    _write_report(arguments.output_path, report)
    _print_summary(report)
    if arguments.print_json:
        print(json.dumps(report, indent=2, sort_keys=True))
    return _compute_exit_code(
        report=report,
        allow_gate_failure=arguments.allow_gate_failure,
        allow_baseline_regression=arguments.allow_baseline_regression,
    )


if __name__ == "__main__":
    raise SystemExit(main())
