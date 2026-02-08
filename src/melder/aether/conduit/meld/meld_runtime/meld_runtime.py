import hashlib
import json
import os
import time
from collections import deque
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.conduit.meld.meld_context.meld_context import MeldContext
from melder.aether.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.spellbook.spell_crafter.blueprints.patch_maps import (
    apply_phase10_override_payload,
)
from melder.spellbook.spell_crafter.blueprints.phase12_overrides_executor import (
    compile_phase12_overrides_executor,
    compile_phase12_overrides_executor_from_source,
    emit_phase12_overrides_executor_source,
)
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.interfaces import ISpell


class MeldRuntime(Cleanable):
    """
    Execute meld calls through compiled Phase 12 codegen artifacts.

    Purpose:
        Provide the execution boundary between `Meld` and spell-scoped Phase 12
        executors compiled by SpellCrafter, without invoking legacy engine paths.

    Contract:
        - Executes no-overrides calls through `phase12_no_overrides_executor`.
        - Executes override calls through specialization executors compiled from
          the Phase 11 override execution IR rows.
        - Keeps override specialization caches bounded per spell.
        - Mutation-bearing spells route through override specialization executors.
        - Enforces spell validity/change-control invariants before execution.
        - Raises deterministic `MeldExecutionError` when runtime prerequisites
          are not satisfied.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = (
        "_override_specialization_cache",
        "_override_specialization_order",
        "_max_override_specializations_per_spell",
        "_override_specialization_source_cache",
        "_override_specialization_l2_cache_dir",
        "_max_override_specializations_l2_per_spell",
    )
    _OVERRIDE_L2_SCHEMA_VERSION = "phase12_override_source_l2_v1"
    _OVERRIDE_L2_RUNTIME_VERSION = "meld_runtime_override_codegen_2026_02_08"

    def __init__(self) -> None:
        """
        Initialize a codegen-only meld runtime.

        Contract:
            - Runtime holds no engine or frame pools.
            - Runtime owns a bounded per-spell override specialization cache.
            - All per-call state is supplied through MeldContext.
        """
        super().__init__()
        self._override_specialization_cache: Dict[str, Dict[Tuple[Any, ...], Callable[..., Any]]] = {}
        self._override_specialization_order: Dict[str, deque[Tuple[Any, ...]]] = {}
        self._max_override_specializations_per_spell: int = 64
        self._override_specialization_source_cache: Dict[int, str] = {}
        self._override_specialization_l2_cache_dir: Optional[str] = None
        self._max_override_specializations_l2_per_spell: int = 256

    def execute_fast_transient(
            self,
            *,
            spell: ISpell,
            conduit_id: Optional[str],
    ) -> Any:
        """
        Execute a transient no-overrides spell through Phase 12 executor.

        Contract:
            - Enforces spell invariants before execution.
            - Requires a compiled Phase 12 executor.
            - Does not accept overrides or mutations.
        """
        self._enforce_spell_invariants(spell, conduit_id)
        if spell.has_mutation_override:
            raise MeldExecutionError(
                spell_id=spell.spell_index.current,
                spell_name=spell.spell_name,
                message=(
                    "Mutation overrides are not supported on the Phase 12 "
                    "no-overrides runtime path."
                ),
            )
        executor = self._require_phase12_executor(spell)
        try:
            return executor(None)
        except MeldExecutionError:
            raise
        except Exception as exc:
            raise MeldExecutionError(
                spell_id=spell.spell_index.current,
                spell_name=spell.spell_name,
                message="Phase 12 transient executor failed.",
                inner=exc,
            ) from exc

    def codegen_fast_transient(
            self,
            *,
            spell: ISpell,
            conduit_id: Optional[str],
    ) -> Any:
        """
        Execute fast transient through the same Phase 12 runtime path.

        Contract:
            - Delegates directly to `execute_fast_transient`.
        """
        return self.execute_fast_transient(
            spell=spell,
            conduit_id=conduit_id,
        )

    def execute(self, context: MeldContext) -> Any:
        """
        Execute one meld call through the appropriate Phase 12 executor route.

        Contract:
            - `context` must contain a non-None root spell.
            - No-overrides calls use the precompiled no-overrides executor.
            - Override calls use spell-scoped specialization executors.
            - Mutation-bearing spells use override specialization routing even
              when no per-call override payload is present.
            - Raises MeldExecutionError when required Phase 11/12 artifacts are
              missing.
            - Returns the constructed root instance.
        """
        if context is None:
            raise ValueError("context must not be None.")
        spell = context.root_spell
        if spell is None:
            raise ValueError("context.root_spell must not be None.")

        self._enforce_spell_invariants(spell, context.conduit_id)

        overrides = context.overrides
        has_mutation_override = spell.has_mutation_override
        if overrides or has_mutation_override:
            return self._execute_with_overrides(
                context=context,
                spell=spell,
            )
        return self._execute_no_overrides(
            context=context,
            spell=spell,
        )

    def cleanup(self) -> None:
        """
        Deterministically tear down runtime-owned caches.

        Contract:
            - Idempotent.
            - Clears all spell-scoped override specialization entries.
        """
        if self._cleaned:
            return
        for cache in self._override_specialization_cache.values():
            cache.clear()
        for order in self._override_specialization_order.values():
            order.clear()
        self._override_specialization_cache.clear()
        self._override_specialization_order.clear()
        self._override_specialization_source_cache.clear()
        self._override_specialization_cache = None
        self._override_specialization_order = None
        self._max_override_specializations_per_spell = None
        self._override_specialization_source_cache = None
        self._override_specialization_l2_cache_dir = None
        self._max_override_specializations_l2_per_spell = None
        self._cleaned = True

    @staticmethod
    def collect_codegen_benchmark_samples_ns(
            *,
            cold_compile_fn: Callable[[], Any],
            warm_execute_fn: Callable[[], Any],
            mixed_execute_fn: Callable[[], Any],
            sample_count: int = 9,
            warmup_count: int = 1,
    ) -> Dict[str, Tuple[int, ...]]:
        """
        Collect benchmark timing samples for cold compile and warm/mixed execution.

        Contract:
            - Executes warmup iterations before timed samples.
            - Uses `time.perf_counter_ns` for all timing measurements.
            - Returns immutable sample tuples grouped by benchmark path.
            - Does not swallow callable exceptions.

        Args:
            cold_compile_fn:
                Callable that performs one cold compile path iteration.
            warm_execute_fn:
                Callable that performs one warm execution iteration.
            mixed_execute_fn:
                Callable that performs one mixed workload iteration.
            sample_count:
                Number of timed samples collected for each path.
            warmup_count:
                Number of untimed warmup iterations per path.

        Returns:
            Dict[str, Tuple[int, ...]]:
                Mapping containing `cold_compile_ns`, `warm_execute_ns`,
                and `mixed_execute_ns` sample tuples.

        Raises:
            ValueError:
                If callables are missing or counts are invalid.
        """
        if cold_compile_fn is None:
            raise ValueError("cold_compile_fn must not be None.")
        if warm_execute_fn is None:
            raise ValueError("warm_execute_fn must not be None.")
        if mixed_execute_fn is None:
            raise ValueError("mixed_execute_fn must not be None.")
        if sample_count < 1:
            raise ValueError("sample_count must be >= 1.")
        if warmup_count < 0:
            raise ValueError("warmup_count must be >= 0.")

        return {
            "cold_compile_ns": MeldRuntime._sample_callable_ns(
                fn=cold_compile_fn,
                sample_count=sample_count,
                warmup_count=warmup_count,
            ),
            "warm_execute_ns": MeldRuntime._sample_callable_ns(
                fn=warm_execute_fn,
                sample_count=sample_count,
                warmup_count=warmup_count,
            ),
            "mixed_execute_ns": MeldRuntime._sample_callable_ns(
                fn=mixed_execute_fn,
                sample_count=sample_count,
                warmup_count=warmup_count,
            ),
        }

    @staticmethod
    def evaluate_codegen_benchmark_gates(
            *,
            cold_compile_ns: Sequence[int],
            warm_execute_ns: Sequence[int],
            mixed_execute_ns: Sequence[int],
            warm_to_cold_max_ratio: float = 0.35,
            mixed_to_cold_max_ratio: float = 0.60,
    ) -> Dict[str, Any]:
        """
        Evaluate benchmark samples against cold/warm regression thresholds.

        Contract:
            - Uses median sample values for gate comparisons.
            - Reports warm-to-cold and mixed-to-cold ratios.
            - Declares pass only when all ratios are <= configured thresholds.

        Args:
            cold_compile_ns:
                Cold compile duration samples in nanoseconds.
            warm_execute_ns:
                Warm execution duration samples in nanoseconds.
            mixed_execute_ns:
                Mixed workload duration samples in nanoseconds.
            warm_to_cold_max_ratio:
                Maximum allowed warm median / cold median ratio.
            mixed_to_cold_max_ratio:
                Maximum allowed mixed median / cold median ratio.

        Returns:
            Dict[str, Any]:
                Threshold report containing medians, ratios, failures, and pass flag.

        Raises:
            ValueError:
                If sample payloads are invalid or thresholds are non-positive.
        """
        if warm_to_cold_max_ratio <= 0:
            raise ValueError("warm_to_cold_max_ratio must be > 0.")
        if mixed_to_cold_max_ratio <= 0:
            raise ValueError("mixed_to_cold_max_ratio must be > 0.")

        cold_samples = MeldRuntime._normalize_benchmark_samples(
            name="cold_compile_ns",
            samples=cold_compile_ns,
        )
        warm_samples = MeldRuntime._normalize_benchmark_samples(
            name="warm_execute_ns",
            samples=warm_execute_ns,
        )
        mixed_samples = MeldRuntime._normalize_benchmark_samples(
            name="mixed_execute_ns",
            samples=mixed_execute_ns,
        )

        cold_median = MeldRuntime._median_ns(cold_samples)
        warm_median = MeldRuntime._median_ns(warm_samples)
        mixed_median = MeldRuntime._median_ns(mixed_samples)
        if cold_median < 1:
            raise ValueError("cold_compile_ns median must be >= 1.")

        warm_ratio = warm_median / cold_median
        mixed_ratio = mixed_median / cold_median
        failures: List[str] = []
        if warm_ratio > warm_to_cold_max_ratio:
            failures.append(
                "warm_to_cold_ratio {0:.4f} exceeded {1:.4f}".format(
                    warm_ratio,
                    warm_to_cold_max_ratio,
                )
            )
        if mixed_ratio > mixed_to_cold_max_ratio:
            failures.append(
                "mixed_to_cold_ratio {0:.4f} exceeded {1:.4f}".format(
                    mixed_ratio,
                    mixed_to_cold_max_ratio,
                )
            )

        return {
            "cold_compile_median_ns": cold_median,
            "warm_execute_median_ns": warm_median,
            "mixed_execute_median_ns": mixed_median,
            "warm_to_cold_ratio": warm_ratio,
            "mixed_to_cold_ratio": mixed_ratio,
            "thresholds": {
                "warm_to_cold_max_ratio": warm_to_cold_max_ratio,
                "mixed_to_cold_max_ratio": mixed_to_cold_max_ratio,
            },
            "failures": tuple(failures),
            "passed": len(failures) == 0,
        }

    @staticmethod
    def evaluate_codegen_benchmark_baseline_deltas(
            *,
            current_gate_report: Dict[str, Any],
            baseline_gate_report: Dict[str, Any],
            cold_compile_max_regression_ratio: float = 1.20,
            warm_execute_max_regression_ratio: float = 1.20,
            mixed_execute_max_regression_ratio: float = 1.20,
    ) -> Dict[str, Any]:
        """
        Compare current benchmark medians against a baseline report.

        Purpose:
            Provide deterministic milestone delta reporting for codegen benchmark
            medians so runtime regressions can be evaluated from saved reports.

        Contract:
            - Expects gate reports shaped like `evaluate_codegen_benchmark_gates`.
            - Compares median nanosecond values for cold, warm, and mixed paths.
            - Uses ratio thresholds to classify regressions path-by-path.
            - Declares pass only when all ratios are <= configured thresholds.

        Args:
            current_gate_report:
                Current benchmark gate report containing median fields.
            baseline_gate_report:
                Baseline benchmark gate report containing median fields.
            cold_compile_max_regression_ratio:
                Maximum allowed `current_cold / baseline_cold` ratio.
            warm_execute_max_regression_ratio:
                Maximum allowed `current_warm / baseline_warm` ratio.
            mixed_execute_max_regression_ratio:
                Maximum allowed `current_mixed / baseline_mixed` ratio.

        Returns:
            Dict[str, Any]:
                Report containing medians, deltas, ratios, thresholds, failures,
                and overall pass state.

        Raises:
            ValueError:
                If reports are missing, malformed, or thresholds are invalid.
        """
        if current_gate_report is None:
            raise ValueError("current_gate_report must not be None.")
        if baseline_gate_report is None:
            raise ValueError("baseline_gate_report must not be None.")
        if cold_compile_max_regression_ratio <= 0:
            raise ValueError("cold_compile_max_regression_ratio must be > 0.")
        if warm_execute_max_regression_ratio <= 0:
            raise ValueError("warm_execute_max_regression_ratio must be > 0.")
        if mixed_execute_max_regression_ratio <= 0:
            raise ValueError("mixed_execute_max_regression_ratio must be > 0.")

        current_cold = MeldRuntime._require_benchmark_report_median(
            report=current_gate_report,
            key="cold_compile_median_ns",
            report_name="current_gate_report",
        )
        current_warm = MeldRuntime._require_benchmark_report_median(
            report=current_gate_report,
            key="warm_execute_median_ns",
            report_name="current_gate_report",
        )
        current_mixed = MeldRuntime._require_benchmark_report_median(
            report=current_gate_report,
            key="mixed_execute_median_ns",
            report_name="current_gate_report",
        )

        baseline_cold = MeldRuntime._require_benchmark_report_median(
            report=baseline_gate_report,
            key="cold_compile_median_ns",
            report_name="baseline_gate_report",
        )
        baseline_warm = MeldRuntime._require_benchmark_report_median(
            report=baseline_gate_report,
            key="warm_execute_median_ns",
            report_name="baseline_gate_report",
        )
        baseline_mixed = MeldRuntime._require_benchmark_report_median(
            report=baseline_gate_report,
            key="mixed_execute_median_ns",
            report_name="baseline_gate_report",
        )

        cold_ratio = current_cold / baseline_cold
        warm_ratio = current_warm / baseline_warm
        mixed_ratio = current_mixed / baseline_mixed

        failures: List[str] = []
        if cold_ratio > cold_compile_max_regression_ratio:
            failures.append(
                "cold_compile_ratio {0:.4f} exceeded {1:.4f}".format(
                    cold_ratio,
                    cold_compile_max_regression_ratio,
                )
            )
        if warm_ratio > warm_execute_max_regression_ratio:
            failures.append(
                "warm_execute_ratio {0:.4f} exceeded {1:.4f}".format(
                    warm_ratio,
                    warm_execute_max_regression_ratio,
                )
            )
        if mixed_ratio > mixed_execute_max_regression_ratio:
            failures.append(
                "mixed_execute_ratio {0:.4f} exceeded {1:.4f}".format(
                    mixed_ratio,
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
            "deltas_ns": {
                "cold_compile_delta_ns": current_cold - baseline_cold,
                "warm_execute_delta_ns": current_warm - baseline_warm,
                "mixed_execute_delta_ns": current_mixed - baseline_mixed,
            },
            "ratios": {
                "cold_compile_ratio": cold_ratio,
                "warm_execute_ratio": warm_ratio,
                "mixed_execute_ratio": mixed_ratio,
            },
            "thresholds": {
                "cold_compile_max_regression_ratio": cold_compile_max_regression_ratio,
                "warm_execute_max_regression_ratio": warm_execute_max_regression_ratio,
                "mixed_execute_max_regression_ratio": mixed_execute_max_regression_ratio,
            },
            "failures": tuple(failures),
            "passed": len(failures) == 0,
        }

    @staticmethod
    def _require_benchmark_report_median(
            *,
            report: Dict[str, Any],
            key: str,
            report_name: str,
    ) -> int:
        """
        Validate and read one median field from a benchmark gate report.

        Contract:
            - Requires `report` to be a dict.
            - Requires `key` to exist with an int value >= 1.
            - Returns the validated median value.
        """
        if not isinstance(report, dict):
            raise ValueError("{0} must be a dict.".format(report_name))
        value = report.get(key)
        if not isinstance(value, int):
            raise ValueError("{0}.{1} must be an int.".format(report_name, key))
        if value < 1:
            raise ValueError("{0}.{1} must be >= 1.".format(report_name, key))
        return value

    @staticmethod
    def _sample_callable_ns(
            *,
            fn: Callable[[], Any],
            sample_count: int,
            warmup_count: int,
    ) -> Tuple[int, ...]:
        """
        Time one callable repeatedly and return per-iteration durations.

        Contract:
            - Performs `warmup_count` untimed calls before sampling.
            - Collects exactly `sample_count` timed durations.
        """
        for _ in range(warmup_count):
            fn()
        durations: List[int] = []
        for _ in range(sample_count):
            start_ns = time.perf_counter_ns()
            fn()
            end_ns = time.perf_counter_ns()
            durations.append(end_ns - start_ns)
        return tuple(durations)

    @staticmethod
    def _normalize_benchmark_samples(
            *,
            name: str,
            samples: Sequence[int],
    ) -> Tuple[int, ...]:
        """
        Validate benchmark sample payloads and return immutable tuples.

        Contract:
            - Requires a non-empty sequence.
            - Requires all sample values to be ints >= 0.
        """
        if samples is None:
            raise ValueError("{0} must not be None.".format(name))
        normalized = tuple(samples)
        if len(normalized) == 0:
            raise ValueError("{0} must not be empty.".format(name))
        for sample in normalized:
            if not isinstance(sample, int):
                raise ValueError("{0} samples must be ints.".format(name))
            if sample < 0:
                raise ValueError("{0} samples must be >= 0.".format(name))
        return normalized

    @staticmethod
    def _median_ns(samples: Sequence[int]) -> int:
        """
        Compute median duration from integer nanosecond samples.

        Contract:
            - Uses sorted median with midpoint average for even sample counts.
            - Returns an integer nanosecond median.
        """
        ordered = sorted(samples)
        size = len(ordered)
        mid_index = size // 2
        if size % 2 == 1:
            return ordered[mid_index]
        return (ordered[mid_index - 1] + ordered[mid_index]) // 2

    @staticmethod
    def _require_phase12_executor(spell: ISpell) -> Callable[[Any], Any]:
        """
        Require and return the compiled Phase 12 no-overrides executor.

        Contract:
            - Raises MeldExecutionError when SpellCrafter artifacts are absent.
            - Raises MeldExecutionError when no Phase 12 executor is compiled.
        """
        crafter = spell._crafter
        if crafter is None:
            raise MeldExecutionError(
                spell_id=spell.spell_index.current,
                spell_name=spell.spell_name,
                message="Missing SpellCrafter artifacts for Phase 12 execution.",
            )
        executor = crafter.phase12_no_overrides_executor
        if executor is None:
            raise MeldExecutionError(
                spell_id=spell.spell_index.current,
                spell_name=spell.spell_name,
                message=(
                    "Missing Phase 12 no-overrides executor for this spell. "
                    "Run conjure resolution phases before melding."
                ),
            )
        return executor

    def _execute_no_overrides(
            self,
            *,
            context: MeldContext,
            spell: ISpell,
    ) -> Any:
        """
        Execute a no-overrides meld call through the compiled Phase 12 executor.

        Contract:
            - Requires `phase12_no_overrides_executor`.
            - Wraps unexpected executor exceptions in MeldExecutionError.
        """
        executor = self._require_phase12_executor(spell)
        try:
            result = executor(context)
        except MeldExecutionError:
            raise
        except Exception as exc:
            raise MeldExecutionError(
                spell_id=spell.spell_index.current,
                spell_name=spell.spell_name,
                message="Phase 12 no-overrides executor failed.",
                inner=exc,
            ) from exc
        self._raise_on_missing_factory_result(
            spell=spell,
            result=result,
            message=(
                "Phase 12 no-overrides executor returned None for a "
                "factory-style spell."
            ),
        )
        return result

    def _execute_with_overrides(
            self,
            *,
            context: MeldContext,
            spell: ISpell,
    ) -> Any:
        """
        Execute an override-bearing meld call through specialization routing.

        Contract:
            - Applies Phase 10 override patch maps to normalize TargetSpec keys.
            - Requires Phase11 override execution IR rows for specialization
              compile and shape-key signature construction.
            - Selects/compiles a spell-scoped specialization by override shape.
            - Uses mutation-aware plan artifacts when the root spell carries
              mutation overrides.
            - Never falls back to engine execution.
        """
        crafter = spell._crafter
        if crafter is None:
            raise MeldExecutionError(
                spell_id=spell.spell_index.current,
                spell_name=spell.spell_name,
                message="Missing SpellCrafter artifacts for Phase 12 override execution.",
            )

        is_mutation_route = spell.has_mutation_override
        execution_ir_key = "overrides_with_mutations" if is_mutation_route else "overrides"
        override_execution_ir_payload = self._resolve_override_execution_ir_payload(
            crafter=crafter,
            execution_ir_key=execution_ir_key,
        )
        if not override_execution_ir_payload:
            message = (
                "Phase 11 override execution IR payload is required for override "
                "specialization execution."
            )
            if is_mutation_route:
                message = (
                    "Phase 11 override+mutation execution IR payload is required "
                    "for override specialization execution."
                )
            raise MeldExecutionError(
                spell_id=spell.spell_index.current,
                spell_name=spell.spell_name,
                message=message,
            )
        plan_rows = override_execution_ir_payload.get("steps_rows")
        if not plan_rows:
            raise MeldExecutionError(
                spell_id=spell.spell_index.current,
                spell_name=spell.spell_name,
                message=(
                    "Phase 11 override execution IR payload must provide non-empty "
                    "'steps_rows'."
                ),
            )
        root_spell_id = override_execution_ir_payload.get("root_spell_id")
        if not root_spell_id:
            raise MeldExecutionError(
                spell_id=spell.spell_index.current,
                spell_name=spell.spell_name,
                message=(
                    "Phase 11 override execution IR payload must provide "
                    "'root_spell_id'."
                ),
            )

        override_payload = context.overrides
        root_positional_override: Optional[Sequence[Any]] = None
        override_map: Dict[Any, Any] = {}
        if override_payload:
            target_payload, root_positional_override = self._split_override_payload(
                spell=spell,
                override_payload=override_payload,
            )
            if target_payload:
                override_patch_map = crafter.override_patch_map_phase10
                if override_patch_map is None:
                    raise MeldExecutionError(
                        spell_id=spell.spell_index.current,
                        spell_name=spell.spell_name,
                        message=(
                            "Phase 10 override patch map is required for override "
                            "specialization execution."
                        ),
                    )
                try:
                    override_map = apply_phase10_override_payload(
                        override_patch_map=override_patch_map,
                        override_payload=target_payload,
                    )
                except MeldExecutionError:
                    raise
                except Exception as exc:
                    raise MeldExecutionError(
                        spell_id=spell.spell_index.current,
                        spell_name=spell.spell_name,
                        message=(
                            "Failed to apply overrides through the Phase 10 "
                            "override patch map."
                        ),
                        inner=exc,
                    ) from exc

        (
            override_targets_by_spell_id,
            socket_shape,
        ) = self._collect_override_targets_and_socket_shape(
            override_map=override_map,
        )
        try:
            plan_signature = self._build_override_plan_signature_from_ir_payload(
                override_execution_ir_payload=override_execution_ir_payload,
            )
            shape_key = self._build_override_shape_key(
                plan_signature=plan_signature,
                override_targets_by_spell_id=override_targets_by_spell_id,
                root_positional_override=root_positional_override,
                socket_shape=socket_shape,
            )
        except MeldExecutionError:
            raise
        except Exception as exc:
            raise MeldExecutionError(
                spell_id=spell.spell_index.current,
                spell_name=spell.spell_name,
                message=(
                    "Failed to build override specialization shape key from the "
                    "Phase 11 execution plan."
                ),
                inner=exc,
            ) from exc
        root_blueprint = crafter.root_blueprint_phase5
        path_registry = root_blueprint.path_registry if root_blueprint is not None else None
        any_overrides_present = bool(override_payload)
        spell_lookup = spell._spellbook._spell_id_pool
        executor = self._get_or_compile_override_executor(
            spell=spell,
            shape_key=shape_key,
            execution_plan=None,
            override_targets_by_spell_id=override_targets_by_spell_id,
            any_overrides_present=any_overrides_present,
            path_registry=path_registry,
            plan_rows=plan_rows,
            root_spell_id=root_spell_id,
            spell_lookup=spell_lookup,
        )

        try:
            result = executor(
                context,
                override_map,
                root_positional_override,
            )
        except MeldExecutionError:
            raise
        except Exception as exc:
            raise MeldExecutionError(
                spell_id=spell.spell_index.current,
                spell_name=spell.spell_name,
                message="Phase 12 override specialization executor failed.",
                inner=exc,
            ) from exc

        self._raise_on_missing_factory_result(
            spell=spell,
            result=result,
            message=(
                "Phase 12 override specialization executor returned None for a "
                "factory-style spell."
            ),
        )
        return result

    @staticmethod
    def _split_override_payload(
            *,
            spell: ISpell,
            override_payload: Dict[str, Any],
    ) -> Tuple[Dict[str, Any], Optional[Sequence[Any]]]:
        """
        Split root positional overrides from TargetSpec override payloads.

        Contract:
            - Removes `__args__` from the payload passed into patch-map apply.
            - Validates that `__args__` is list/tuple when provided.
        """
        raw_args = override_payload.get("__args__")
        if raw_args is None:
            return override_payload, None
        if not isinstance(raw_args, (list, tuple)):
            raise MeldExecutionError(
                spell_id=spell.spell_index.current,
                spell_name=spell.spell_name,
                message="__args__ override must be a list or tuple.",
            )
        if len(override_payload) == 1:
            return {}, tuple(raw_args)
        normalized_payload = dict(override_payload)
        normalized_payload.pop("__args__", None)
        return normalized_payload, tuple(raw_args)

    @staticmethod
    def _collect_override_targets(
            *,
            override_map: Dict[Any, Any],
    ) -> Dict[str, Tuple[Any, ...]]:
        """
        Group override socket refs by spell id with deterministic ordering.

        Contract:
            - Output ordering is deterministic for stable shape keying.
            - Socket refs are grouped by `socket_ref.node_id`.
        """
        by_spell_id, _ = MeldRuntime._collect_override_targets_and_socket_shape(
            override_map=override_map,
        )
        return by_spell_id

    @staticmethod
    def _collect_override_targets_and_socket_shape(
            *,
            override_map: Dict[Any, Any],
    ) -> Tuple[Dict[str, Tuple[Any, ...]], Tuple[Tuple[Any, ...], ...]]:
        """
        Collect grouped override targets and socket-shape tuples in one pass.

        Contract:
            - Performs a single deterministic sort over socket refs.
            - Uses dedicated no-sort fast paths for one- and two-socket payloads.
            - Groups refs by `socket_ref.node_id`.
            - Emits socket-shape tuples in stable sorted order.
        """
        if not override_map:
            return {}, ()
        if len(override_map) == 1:
            socket_ref = next(iter(override_map))
            return (
                {
                    socket_ref.node_id: (socket_ref,),
                },
                (
                    (
                        socket_ref.node_id,
                        socket_ref.param_path_id,
                        socket_ref.param_name,
                        socket_ref.socket_kind.value,
                    ),
                ),
            )
        if len(override_map) == 2:
            refs_iter = iter(override_map)
            first_ref = next(refs_iter)
            second_ref = next(refs_iter)
            first_shape_row = (
                first_ref.node_id,
                first_ref.param_path_id,
                first_ref.param_name,
                first_ref.socket_kind.value,
            )
            second_shape_row = (
                second_ref.node_id,
                second_ref.param_path_id,
                second_ref.param_name,
                second_ref.socket_kind.value,
            )
            if second_shape_row < first_shape_row:
                first_ref, second_ref = second_ref, first_ref
                first_shape_row, second_shape_row = second_shape_row, first_shape_row
            if first_ref.node_id == second_ref.node_id:
                by_spell_id = {
                    first_ref.node_id: (
                        first_ref,
                        second_ref,
                    ),
                }
            else:
                by_spell_id = {
                    first_ref.node_id: (first_ref,),
                    second_ref.node_id: (second_ref,),
                }
            return (
                by_spell_id,
                (
                    first_shape_row,
                    second_shape_row,
                ),
            )

        by_spell_id: Dict[str, list[Any]] = {}
        socket_shape: list[Tuple[Any, ...]] = []
        ordered_refs = sorted(
            override_map.keys(),
            key=lambda ref: (
                ref.node_id,
                ref.param_path_id,
                ref.param_name,
                ref.socket_kind.value,
            ),
        )
        current_spell_id: Optional[str] = None
        current_bucket: Optional[list[Any]] = None
        for socket_ref in ordered_refs:
            spell_id = socket_ref.node_id
            if spell_id != current_spell_id:
                current_spell_id = spell_id
                current_bucket = [socket_ref]
                by_spell_id[spell_id] = current_bucket
            else:
                if current_bucket is None:
                    current_bucket = [socket_ref]
                    by_spell_id[spell_id] = current_bucket
                else:
                    current_bucket.append(socket_ref)
            socket_shape.append(
                (
                    socket_ref.node_id,
                    socket_ref.param_path_id,
                    socket_ref.param_name,
                    socket_ref.socket_kind.value,
                )
            )

        return (
            {
                spell_id: tuple(refs)
                for spell_id, refs in by_spell_id.items()
            },
            tuple(socket_shape),
        )

    @staticmethod
    def _build_override_shape_key(
            *,
            plan_signature: Any,
            override_targets_by_spell_id: Dict[str, Tuple[Any, ...]],
            root_positional_override: Optional[Sequence[Any]],
            socket_shape: Optional[Tuple[Tuple[Any, ...], ...]] = None,
    ) -> Tuple[Any, ...]:
        """
        Build a stable override-shape key for specialization cache lookup.

        Contract:
            - Includes deterministic execution-plan signature to avoid stale-plan
              collisions without relying on object identity.
            - Includes deterministic socket-target tuples.
            - Includes root positional-argument arity when present.
        """
        if plan_signature is None:
            raise ValueError("plan_signature must not be None.")

        resolved_socket_shape = socket_shape
        if resolved_socket_shape is None:
            socket_shape_rows: list[Tuple[Any, ...]] = []
            for spell_id in sorted(override_targets_by_spell_id.keys()):
                for socket_ref in override_targets_by_spell_id[spell_id]:
                    socket_shape_rows.append(
                        (
                            socket_ref.node_id,
                            socket_ref.param_path_id,
                            socket_ref.param_name,
                            socket_ref.socket_kind.value,
                        )
                    )
            resolved_socket_shape = tuple(socket_shape_rows)
        positional_arity = -1
        if root_positional_override is not None:
            positional_arity = len(root_positional_override)
        return (
            plan_signature,
            resolved_socket_shape,
            positional_arity,
        )

    @staticmethod
    def _resolve_override_plan_signature(
            *,
            crafter: Any,
            execution_ir_key: str = "overrides",
    ) -> Tuple[Any, ...]:
        """
        Resolve the override plan-signature source for shape-key construction.

        Contract:
            - Requires schema-side Phase11 IR override signatures.
            - Selects the execution variant payload by `execution_ir_key`.
            - Raises when required signature data is missing.
        """
        overrides_payload = MeldRuntime._resolve_override_execution_ir_payload(
            crafter=crafter,
            execution_ir_key=execution_ir_key,
        )
        return MeldRuntime._build_override_plan_signature_from_ir_payload(
            override_execution_ir_payload=overrides_payload,
        )

    @staticmethod
    def _build_override_plan_signature_from_ir_payload(
            *,
            override_execution_ir_payload: Optional[Dict[str, Any]],
    ) -> Tuple[Any, ...]:
        """
        Build deterministic override plan signature from execution IR payload.

        Contract:
            - Requires a non-empty override execution IR payload mapping.
            - Requires payload field ``signature``.
            - Includes optional ``steps_rows_signature`` when present.
        """
        overrides_payload = override_execution_ir_payload
        if not overrides_payload:
            raise ValueError(
                "Phase 11 override execution IR payload is missing for shape-key signature."
            )
        variant_signature = overrides_payload.get("signature")
        if variant_signature is None:
            raise ValueError(
                "Phase 11 override execution IR payload is missing required field 'signature'."
            )
        return (
            "phase11_overrides_ir",
            variant_signature,
            overrides_payload.get("steps_rows_signature"),
        )

    @staticmethod
    def _resolve_override_execution_ir_payload(
            *,
            crafter: Any,
            execution_ir_key: str = "overrides",
    ) -> Optional[Dict[str, Any]]:
        """
        Resolve Phase11 override execution IR payload when available.

        Contract:
            - Returns None when codegen IR or override execution payload is absent.
            - Selects the execution variant payload by `execution_ir_key`.
            - Returns the override execution payload mapping by reference.
        """
        codegen_ir = crafter.codegen_ir
        if codegen_ir is None:
            return None
        phase8_11_payload = codegen_ir.get("phase8_11")
        if not phase8_11_payload:
            return None
        execution_payload = phase8_11_payload.get("execution")
        if not execution_payload:
            return None
        return execution_payload.get(execution_ir_key)

    @staticmethod
    def _build_override_plan_signature(
            *,
            execution_plan: Any,
    ) -> Tuple[Any, ...]:
        """
        Build a hashable deterministic signature for override execution plans.

        Contract:
            - Includes per-step semantics consumed by override execution routes.
            - Excludes runtime object identity.
            - Returns only hashable values suitable for cache keys.
        """
        if execution_plan is None:
            raise ValueError("execution_plan must not be None.")

        try:
            plan_variant = execution_plan.plan_variant
            root_spell_id = execution_plan.root_spell_id
            steps = execution_plan.steps
        except AttributeError as exc:
            raise ValueError(
                "execution_plan must expose plan_variant, root_spell_id, and steps."
            ) from exc

        step_signatures: list[Tuple[Any, ...]] = []
        for index, step in enumerate(steps):
            try:
                dependency_order = tuple(
                    (
                        param_name,
                        tuple(dependency_keys),
                    )
                    for param_name, dependency_keys in step.dependency_resolution_order
                )
                contract_payload_items: Tuple[Any, ...] = ()
                if step.contract_payload:
                    contract_payload_items = tuple(
                        sorted(
                            (
                                param_name,
                                MeldRuntime._freeze_override_signature_value(value),
                            )
                            for param_name, value in step.contract_payload.items()
                        )
                    )
                step_signatures.append(
                    (
                        step.instance_key,
                        step.spell.spell_index.current,
                        step.existence.name,
                        step.creations_target_kind,
                        step.shared_instance,
                        dependency_order,
                        step.override_match_prefix,
                        step.override_match_prefix_len,
                        tuple(step.override_keys),
                        step.use_spell_lock_hint,
                        step.must_register,
                        step.uses_positional_override,
                        MeldRuntime._freeze_override_signature_value(step.contract_positional_override),
                        step.has_contract_payload,
                        contract_payload_items,
                    )
                )
            except AttributeError as exc:
                raise ValueError(
                    f"execution_plan step at index {index} is missing required signature fields."
                ) from exc

        return (
            plan_variant,
            root_spell_id,
            tuple(step_signatures),
        )

    @staticmethod
    def _freeze_override_signature_value(value: Any) -> Any:
        """
        Normalize arbitrary values into hashable deterministic cache-key form.

        Contract:
            - Dicts become sorted key/value tuples.
            - Lists/tuples become tuples.
            - Sets become repr-sorted tuples.
            - Other values are returned as-is.
        """
        if isinstance(value, dict):
            return tuple(
                sorted(
                    (
                        key,
                        MeldRuntime._freeze_override_signature_value(item),
                    )
                    for key, item in value.items()
                )
            )
        if isinstance(value, (list, tuple)):
            return tuple(
                MeldRuntime._freeze_override_signature_value(item)
                for item in value
            )
        if isinstance(value, set):
            return tuple(
                sorted(
                    (
                        MeldRuntime._freeze_override_signature_value(item)
                        for item in value
                    ),
                    key=repr,
                )
            )
        return value

    def _get_or_compile_override_executor(
            self,
            *,
            spell: ISpell,
            shape_key: Tuple[Any, ...],
            execution_plan: Any,
            override_targets_by_spell_id: Dict[str, Tuple[Any, ...]],
            any_overrides_present: bool,
            path_registry: Optional[Any],
            plan_rows: Optional[Sequence[Dict[str, Any]]],
            root_spell_id: Optional[str],
            spell_lookup: Optional[Dict[str, Any]],
    ) -> Callable[[Any, Dict[Any, Any], Optional[Sequence[Any]]], Any]:
        """
        Resolve a cached override specialization executor or compile on miss.

        Contract:
            - Cache entries are bounded by `_max_override_specializations_per_spell`.
            - Eviction order is deterministic FIFO per spell id.
            - Uses persisted L2 source artifacts before cold compile misses.
        """
        spell_id = spell.spell_id
        cache = self._override_specialization_cache.get(spell_id)
        order = self._override_specialization_order.get(spell_id)
        if cache is None:
            cache = {}
            order = deque()
            self._override_specialization_cache[spell_id] = cache
            self._override_specialization_order[spell_id] = order

        cached = cache.get(shape_key)
        if cached is not None:
            return cached

        l2_enabled = self._override_specialization_l2_cache_dir is not None
        l2_key: Optional[str] = None
        shape_signature: Optional[str] = None
        restored = None
        if l2_enabled:
            l2_key, shape_signature = self._build_override_l2_key(
                spell_id=spell_id,
                shape_key=shape_key,
            )
            restored = self._load_override_executor_from_l2(
                spell=spell,
                l2_key=l2_key,
                shape_signature=shape_signature,
                execution_plan=execution_plan,
                override_targets_by_spell_id=override_targets_by_spell_id,
                any_overrides_present=any_overrides_present,
                path_registry=path_registry,
                plan_rows=plan_rows,
                root_spell_id=root_spell_id,
                spell_lookup=spell_lookup,
            )
        if restored is not None:
            compiled = restored
        else:
            try:
                compiled = compile_phase12_overrides_executor(
                    execution_plan=execution_plan,
                    override_targets_by_spell_id=override_targets_by_spell_id,
                    any_overrides_present=any_overrides_present,
                    path_registry=path_registry,
                    plan_rows=plan_rows,
                    root_spell_id=root_spell_id,
                    spell_lookup=spell_lookup,
                )
            except MeldExecutionError:
                raise
            except Exception as exc:
                raise MeldExecutionError(
                    spell_id=spell.spell_index.current,
                    spell_name=spell.spell_name,
                    message="Phase 12 override specialization compilation failed.",
                    inner=exc,
                ) from exc
            source = self._resolve_override_specialization_source(
                execution_plan=execution_plan,
                plan_rows=plan_rows,
            )
            if source is not None and l2_enabled:
                self._persist_override_executor_source_to_l2(
                    spell_id=spell_id,
                    l2_key=l2_key,
                    shape_signature=shape_signature,
                    source=source,
                )

        if shape_key not in cache:
            if len(order) >= self._max_override_specializations_per_spell:
                evicted = order.popleft()
                cache.pop(evicted, None)
            cache[shape_key] = compiled
            order.append(shape_key)
        return compiled

    def _resolve_override_specialization_source(
            self,
            *,
            execution_plan: Any,
            plan_rows: Optional[Sequence[Dict[str, Any]]],
    ) -> Optional[str]:
        """
        Resolve deterministic generated specialization source for persistence.

        Contract:
            - Uses plan row count when rows are present.
            - Falls back to execution-plan step count when available.
            - Reuses runtime-owned source cache entries by step_count.
            - Returns None when step count cannot be derived.
        """
        step_count: Optional[int] = None
        if plan_rows is not None:
            step_count = len(plan_rows)
        elif execution_plan is not None:
            step_count = len(execution_plan.steps)
        if step_count is None:
            return None
        cached_source = self._override_specialization_source_cache.get(step_count)
        if cached_source is not None:
            return cached_source
        source = emit_phase12_overrides_executor_source(
            step_count=step_count,
        )
        self._override_specialization_source_cache[step_count] = source
        return source

    @staticmethod
    def _build_override_l2_key(
            *,
            spell_id: str,
            shape_key: Tuple[Any, ...],
    ) -> Tuple[str, str]:
        """
        Build deterministic persisted-cache key metadata for one specialization.

        Contract:
            - Includes spell id, shape signature, schema version, and runtime version.
            - Returns `(l2_key, shape_signature)`.
        """
        shape_signature = hashlib.sha256(repr(shape_key).encode("utf-8")).hexdigest()
        raw = (
            f"{MeldRuntime._OVERRIDE_L2_SCHEMA_VERSION}|"
            f"{MeldRuntime._OVERRIDE_L2_RUNTIME_VERSION}|"
            f"{spell_id}|"
            f"{shape_signature}"
        )
        l2_key = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        return l2_key, shape_signature

    def _get_override_l2_artifact_path(
            self,
            *,
            spell_id: str,
            l2_key: str,
    ) -> str:
        """
        Resolve file path for one persisted override specialization artifact.

        Contract:
            - Uses spell-id hash directories to avoid invalid path characters.
            - Returns a `.json` artifact path.
        """
        cache_root = self._override_specialization_l2_cache_dir
        spell_hash = hashlib.sha256(spell_id.encode("utf-8")).hexdigest()
        spell_cache_dir = os.path.join(cache_root, spell_hash)
        return os.path.join(spell_cache_dir, f"{l2_key}.json")

    def _load_override_executor_from_l2(
            self,
            *,
            spell: ISpell,
            l2_key: str,
            shape_signature: str,
            execution_plan: Any,
            override_targets_by_spell_id: Dict[str, Tuple[Any, ...]],
            any_overrides_present: bool,
            path_registry: Optional[Any],
            plan_rows: Optional[Sequence[Dict[str, Any]]],
            root_spell_id: Optional[str],
            spell_lookup: Optional[Dict[str, Any]],
    ) -> Optional[Callable[[Any, Dict[Any, Any], Optional[Sequence[Any]]], Any]]:
        """
        Attempt to restore a specialization executor from persisted L2 source.

        Contract:
            - Validates schema/runtime versions and key metadata before compile.
            - Corrupt or stale artifacts are discarded and treated as cache misses.
        """
        if not self._override_specialization_l2_cache_dir:
            return None
        artifact_path = self._get_override_l2_artifact_path(
            spell_id=spell.spell_id,
            l2_key=l2_key,
        )
        if not os.path.exists(artifact_path):
            return None

        try:
            with open(artifact_path, "r", encoding="utf-8") as artifact_file:
                artifact = json.load(artifact_file)
        except Exception:
            self._discard_override_l2_artifact(artifact_path)
            return None

        if not isinstance(artifact, dict):
            self._discard_override_l2_artifact(artifact_path)
            return None
        metadata = artifact.get("metadata")
        source = artifact.get("source")
        if not isinstance(metadata, dict) or not isinstance(source, str) or not source:
            self._discard_override_l2_artifact(artifact_path)
            return None

        if metadata.get("schema_version") != self._OVERRIDE_L2_SCHEMA_VERSION:
            self._discard_override_l2_artifact(artifact_path)
            return None
        if metadata.get("runtime_version") != self._OVERRIDE_L2_RUNTIME_VERSION:
            self._discard_override_l2_artifact(artifact_path)
            return None
        if metadata.get("spell_id") != spell.spell_id:
            self._discard_override_l2_artifact(artifact_path)
            return None
        if metadata.get("l2_key") != l2_key:
            self._discard_override_l2_artifact(artifact_path)
            return None
        if metadata.get("shape_signature") != shape_signature:
            self._discard_override_l2_artifact(artifact_path)
            return None

        source_sha256 = hashlib.sha256(source.encode("utf-8")).hexdigest()
        if metadata.get("source_sha256") != source_sha256:
            self._discard_override_l2_artifact(artifact_path)
            return None

        try:
            return compile_phase12_overrides_executor_from_source(
                source=source,
                execution_plan=execution_plan,
                override_targets_by_spell_id=override_targets_by_spell_id,
                any_overrides_present=any_overrides_present,
                path_registry=path_registry,
                plan_rows=plan_rows,
                root_spell_id=root_spell_id,
                spell_lookup=spell_lookup,
            )
        except Exception:
            self._discard_override_l2_artifact(artifact_path)
            return None

    def _persist_override_executor_source_to_l2(
            self,
            *,
            spell_id: str,
            l2_key: str,
            shape_signature: str,
            source: str,
    ) -> None:
        """
        Persist specialization source to L2 cache with metadata validation fields.

        Contract:
            - Writes atomically via temp file + replace when possible.
            - Best-effort only; write failures never break runtime execution.
            - Applies per-spell L2 eviction after successful writes.
        """
        if not self._override_specialization_l2_cache_dir:
            return
        artifact_path = self._get_override_l2_artifact_path(
            spell_id=spell_id,
            l2_key=l2_key,
        )
        artifact_dir = os.path.dirname(artifact_path)
        metadata = {
            "schema_version": self._OVERRIDE_L2_SCHEMA_VERSION,
            "runtime_version": self._OVERRIDE_L2_RUNTIME_VERSION,
            "spell_id": spell_id,
            "l2_key": l2_key,
            "shape_signature": shape_signature,
            "created_at_unix": time.time(),
            "source_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
        }
        payload = {
            "metadata": metadata,
            "source": source,
        }
        temp_path = f"{artifact_path}.tmp"
        try:
            os.makedirs(artifact_dir, exist_ok=True)
            with open(temp_path, "w", encoding="utf-8") as temp_file:
                json.dump(
                    payload,
                    temp_file,
                    sort_keys=True,
                    separators=(",", ":"),
                )
            os.replace(temp_path, artifact_path)
            self._evict_override_l2_artifacts(spell_id=spell_id)
        except Exception:
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            except Exception:
                pass

    def _evict_override_l2_artifacts(
            self,
            *,
            spell_id: str,
    ) -> None:
        """
        Enforce bounded per-spell L2 artifact retention.

        Contract:
            - Keeps at most `_max_override_specializations_l2_per_spell` entries.
            - Evicts oldest files first by modification time.
        """
        if not self._override_specialization_l2_cache_dir:
            return
        max_entries = self._max_override_specializations_l2_per_spell
        if max_entries is None or max_entries < 1:
            return
        spell_hash = hashlib.sha256(spell_id.encode("utf-8")).hexdigest()
        spell_cache_dir = os.path.join(self._override_specialization_l2_cache_dir, spell_hash)
        if not os.path.isdir(spell_cache_dir):
            return

        entries = []
        try:
            for name in os.listdir(spell_cache_dir):
                if not name.endswith(".json"):
                    continue
                path = os.path.join(spell_cache_dir, name)
                if not os.path.isfile(path):
                    continue
                try:
                    mtime = os.path.getmtime(path)
                except Exception:
                    continue
                entries.append((mtime, path))
        except Exception:
            return

        if len(entries) <= max_entries:
            return
        entries.sort(key=lambda item: (item[0], item[1]))
        excess = len(entries) - max_entries
        for _, path in entries[:excess]:
            self._discard_override_l2_artifact(path)

    @staticmethod
    def _discard_override_l2_artifact(path: str) -> None:
        """
        Best-effort deletion for corrupt or stale L2 cache artifacts.
        """
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception:
            pass

    @staticmethod
    def _raise_on_missing_factory_result(
            *,
            spell: ISpell,
            result: Any,
            message: str,
    ) -> None:
        """
        Raise when factory-style spells produce no runtime result.

        Contract:
            - Applies only to class/method/lambda spells.
            - Returns silently for non-factory spell types.
        """
        if (
                result is None
                and (spell.is_class_spell or spell.is_method_spell or spell.is_lambda_spell)
        ):
            raise MeldExecutionError(
                spell_id=spell.spell_index.current,
                spell_name=spell.spell_name,
                message=message,
            )

    @staticmethod
    def _enforce_spell_invariants(
            spell: ISpell,
            conduit_id: Optional[str],
    ) -> None:
        """
        Validate spell validity and change-control gating before execution.

        Contract:
            - Blocks invalid/gated/disabled lineages.
            - Blocks dirty roots under ChangeControlManager.
            - Blocks broken or unvalidated spells.
        """
        if not spell._spellbook._spellbook_validation_required:
            return

        state = spell.system_state
        if state is not None:
            validity = state.validity
            if validity in (
                    SpellValidity.invalid,
                    SpellValidity.gated,
                    SpellValidity.disabled,
            ):
                raise MeldExecutionError(
                    spell_id=spell.spell_index.current,
                    spell_name=spell.spell_name,
                    message=(
                        "Cannot execute meld runtime for a spell whose lineage is "
                        f"{validity.name}."
                    ),
                )

        try:
            spellbook = spell._spellbook
            aether = spellbook._aether
            manager = aether._get_change_control_manager(spell.aetheric_frame)
            if manager is not None and conduit_id and manager.is_root_dirty(
                    conduit_id,
                    spell.spell_index.current,
            ):
                raise MeldExecutionError(
                    spell_id=spell.spell_index.current,
                    spell_name=spell.spell_name,
                    message=(
                        "Cannot execute meld runtime while the root is marked dirty. "
                        "Revalidation is required."
                    ),
                )
        except MeldExecutionError:
            raise
        except Exception:
            pass

        if spell.is_broken:
            raise MeldExecutionError(
                spell_id=spell.spell_index.current,
                spell_name=spell.spell_name,
                message="Cannot execute meld runtime for a broken spell.",
            )

        if not spell.validated:
            raise MeldExecutionError(
                spell_id=spell.spell_index.current,
                spell_name=spell.spell_name,
                message=(
                    "Spell has not been validated. Run the SpellCrafter phases "
                    "before attempting to meld this spell."
                ),
            )
