import argparse
import json
import os
import time
from typing import Any, Dict, Optional, Sequence, Tuple

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.meld.meld_runtime.meld_runtime import MeldRuntime
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
        Own one benchmark Spellbook/Conduit pair and expose warm/mixed callables.

    Contract:
        - Manages setup and cleanup of runtime objects deterministically.
        - Provides repeatable warm and mixed execute operations.
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
            with self._conduit.enter_spellspace() as spellspace:
                scoped = spellspace.meld(spell=self._spellspace_root_id)
                if not isinstance(scoped, BenchmarkSpellspaceRoot):
                    raise AssertionError(
                        "Expected BenchmarkSpellspaceRoot from spellspace meld."
                    )
        self._mixed_index += 1

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
    parser.add_argument("--baseline-path", type=str, default="")
    parser.add_argument("--cold-max-regression-ratio", type=float, default=1.20)
    parser.add_argument("--warm-max-regression-ratio", type=float, default=1.20)
    parser.add_argument("--mixed-max-regression-ratio", type=float, default=1.20)
    parser.add_argument(
        "--output-path",
        type=str,
        default="benchmarks/testing_other_di/results/codegen_benchmark_report.json",
    )
    parser.add_argument("--allow-gate-failure", action="store_true")
    parser.add_argument("--allow-baseline-regression", action="store_true")
    parser.add_argument("--print-json", action="store_true")
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
    _reset_aether_singleton_for_benchmark()
    warm_session = CodegenBenchmarkSession(
        frame_name=_build_unique_session_name("codegen-warm"),
        prewarm_root=True,
    )
    try:
        samples = MeldRuntime.collect_codegen_benchmark_samples_ns(
            cold_compile_fn=_run_cold_compile_iteration,
            warm_execute_fn=warm_session.resolve_root_once,
            mixed_execute_fn=warm_session.resolve_mixed_once,
            sample_count=arguments.sample_count,
            warmup_count=arguments.warmup_count,
        )
        gate_report = MeldRuntime.evaluate_codegen_benchmark_gates(
            cold_compile_ns=samples["cold_compile_ns"],
            warm_execute_ns=samples["warm_execute_ns"],
            mixed_execute_ns=samples["mixed_execute_ns"],
            warm_to_cold_max_ratio=arguments.warm_to_cold_max_ratio,
            mixed_to_cold_max_ratio=arguments.mixed_to_cold_max_ratio,
        )
    finally:
        try:
            warm_session.cleanup()
        finally:
            _reset_aether_singleton_for_benchmark()

    report: Dict[str, Any] = {
        "schema_version": "codegen_benchmark_report_v1",
        "generated_at_unix": time.time(),
        "sample_count": arguments.sample_count,
        "warmup_count": arguments.warmup_count,
        "samples_ns": samples,
        "gate_report": gate_report,
    }

    baseline_path = arguments.baseline_path.strip()
    if baseline_path:
        baseline_payload = _load_json_report(baseline_path)
        baseline_gate_report = _extract_gate_report(baseline_payload)
        baseline_delta_report = MeldRuntime.evaluate_codegen_benchmark_baseline_deltas(
            current_gate_report=gate_report,
            baseline_gate_report=baseline_gate_report,
            cold_compile_max_regression_ratio=arguments.cold_max_regression_ratio,
            warm_execute_max_regression_ratio=arguments.warm_max_regression_ratio,
            mixed_execute_max_regression_ratio=arguments.mixed_max_regression_ratio,
        )
        report["baseline_path"] = baseline_path
        report["baseline_delta_report"] = baseline_delta_report

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

    baseline_delta_report = report.get("baseline_delta_report")
    if (
            baseline_delta_report is not None
            and (not allow_baseline_regression)
            and (not baseline_delta_report["passed"])
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
