"""
Experiment comparing forced generalized versus solo across solo existence categories.

Purpose:
    Probe the real runtime creation seam by:
    - binding exactly one visible spell per scenario,
    - conjuring normally so phases 1-9 are real,
    - forcing phase-10 and phase-11 family choices locally,
    - building the real `CreationContext`,
    - and timing generalized versus solo on both no-overrides and overrides
      paths across the solo existence matrix.

This is an experimentation surface, not production runtime code.
"""

import gc
import sys
import time
from typing import Any, Dict, Optional, Sequence, Tuple

from tests.component.melder.spellbook.spell_compiler_runtime_test_support import (
    get_spell_by_version_id,
    make_spellbook,
    reset_aether_runtime,
)


def _ensure_src_on_path() -> None:
    """
    Ensure the local `src/` tree is importable for direct experiment execution.
    """
    if "src" not in sys.path:
        sys.path.insert(0, "src")
    if "." not in sys.path:
        sys.path.insert(0, ".")


_ensure_src_on_path()

from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation.spell_codegen_creation import (
    SpellCodegenCreation,
)
from melder.aether.spellbook import spellbook as spellbook_module
from melder.aether.spellbook import spellbook_creation_system as spellbook_creation_system_module
from melder.aether.spellbook.spell_compiler.codegen_creation_system.spell_codegen_strategy_builder import (
    SpellCodegenStrategyBuilder,
)
from melder.aether.conduit.meld.creation_context.creation_context_builder import (
    CreationContextBuilder,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_plan import (
    SpellCodegenPlan,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_plan_strategy_builder import (
    SpellCodegenPlanStrategyBuilder,
)
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError

if not hasattr(spellbook_creation_system_module, "Spellbook"):
    spellbook_creation_system_module.Spellbook = spellbook_module.Spellbook


class _SoloConfigurableRoot:
    """
    One visible spell used for solo existence-matrix comparisons.
    """

    __slots__ = ("value",)

    def __init__(self, value: Any = None) -> None:
        self.value = value


class _ManyOnlyConfigurableLeaf:
    """
    Extra visible all-many spell used to make the many-only family legal.
    """

    __slots__ = ()

    def __init__(self) -> None:
        return None


class _FreshCreationsProbe:
    """
    Minimal creations store used to control create-versus-reuse behavior per iteration.
    """

    __slots__ = [
        "_creations",
        "_disposable_creations",
        "_lock",
    ]

    def __init__(self) -> None:
        self._creations = {}
        self._disposable_creations = {}
        self._lock = _NullLock()

    def reset(self) -> None:
        """
        Clear all stored state before one measured iteration.
        """
        self._creations.clear()
        self._disposable_creations.clear()

    def get_creation(self, spell_id: str) -> Any:
        return self._creations.get(spell_id)

    def add_creation(
            self,
            spell_id: str,
            instance: Any,
            has_disposal_methods: bool = False,
            disposal_methods: Optional[Sequence[str]] = None,
    ) -> None:
        _ = has_disposal_methods
        _ = disposal_methods
        self._creations[spell_id] = instance

    def add_many_creations(
            self,
            spell_id: str,
            instance: Any,
            has_disposal_methods: bool = False,
            disposal_methods: Optional[Sequence[str]] = None,
    ) -> None:
        _ = has_disposal_methods
        _ = disposal_methods
        self._disposable_creations.setdefault(spell_id, []).append(instance)


class _NullLock:
    """
    Minimal no-op context-manager lock for fresh creations probes.
    """

    __slots__ = ()

    def __enter__(self) -> "_NullLock":
        return self

    def __exit__(
            self,
            exc_type: Any,
            exc: Any,
            tb: Any,
    ) -> None:
        _ = exc_type
        _ = exc
        _ = tb
        return None


def _replace_spell_codegen_plan(
        artifact: Any,
        plan: SpellCodegenPlan,
) -> None:
    """
    Publish one forced `SpellCodegenPlan` onto the artifact.
    """
    previous_plan = artifact._spell_codegen_plan
    artifact._spell_codegen_plan = plan
    if previous_plan is not None and previous_plan is not plan:
        try:
            previous_plan.cleanup()
        except Exception:
            pass


def _replace_spell_codegen_creation(
        artifact: Any,
        creation: SpellCodegenCreation,
) -> None:
    """
    Publish one forced `SpellCodegenCreation` onto the artifact.
    """
    previous_creation = artifact._spell_codegen_creation
    artifact._spell_codegen_creation = creation
    if previous_creation is not None and previous_creation is not creation:
        try:
            previous_creation.cleanup()
        except Exception:
            pass


def _build_forced_plan(
        *,
        artifact: Any,
        plan_strategy_id: str,
        plan_family_id: str,
        candidate_codegen_style_ids: Tuple[str, ...],
) -> SpellCodegenPlan:
    """
    Build one forced phase-10 plan using the real plan strategy.
    """
    spell_codegen_model = artifact._spell_codegen_model
    if spell_codegen_model is None:
        raise RuntimeError("Forced plan build requires artifact._spell_codegen_model.")

    plan = SpellCodegenPlan(
        processor_strategy_ids=spell_codegen_model.snapshot_applied_strategy_ids(),
        plan_strategy_ids=(),
        plan_family_id=plan_family_id,
        candidate_codegen_style_ids=candidate_codegen_style_ids,
        no_overrides_plan=None,
        overrides_plan=None,
        metadata={
            "selected_strategy_id": plan_strategy_id,
            "discovery_reason": "forced_experiment_plan_strategy",
            "plan_family_id": plan_family_id,
            "candidate_codegen_style_ids": candidate_codegen_style_ids,
        },
    )
    builder = SpellCodegenPlanStrategyBuilder()
    try:
        strategy = builder.get_strategy(plan_strategy_id)
        strategy.apply(spell_codegen_model, artifact, plan)
        plan.plan_strategy_ids = plan.plan_strategy_ids + (strategy.strategy_id,)
    finally:
        builder.cleanup()
    _replace_spell_codegen_plan(artifact, plan)
    return plan


def _build_forced_creation(
        *,
        artifact: Any,
        creation_strategy_ids: Tuple[str, ...],
        discovery_reason: str,
        selected_codegen_style_id: str,
) -> SpellCodegenCreation:
    """
    Build one forced phase-11 creation artifact using the real creation strategies.
    """
    spell_codegen_model = artifact._spell_codegen_model
    spell_codegen_plan = artifact._spell_codegen_plan
    if spell_codegen_model is None or spell_codegen_plan is None:
        raise RuntimeError(
            "Forced creation build requires artifact._spell_codegen_model and artifact._spell_codegen_plan."
        )

    creation = SpellCodegenCreation(
        selected_strategy_ids=creation_strategy_ids,
        discovery_reason=discovery_reason,
        no_overrides_executor=None,
        overrides_executor=None,
        metadata={
            "selected_codegen_style_id": selected_codegen_style_id,
            "selected_plan_family_id": spell_codegen_plan.plan_family_id,
            "candidate_codegen_style_ids": spell_codegen_plan.candidate_codegen_style_ids,
        },
    )
    builder = SpellCodegenStrategyBuilder()
    try:
        strategies = builder.get_strategies(creation_strategy_ids)
        for strategy in strategies:
            strategy.apply(
                spell_codegen_model,
                spell_codegen_plan,
                creation,
            )
    finally:
        builder.cleanup()
    _replace_spell_codegen_creation(artifact, creation)
    return creation


def _build_forced_creation_context(
        *,
        spell: Any,
        plan_strategy_id: str,
        plan_family_id: str,
        candidate_codegen_style_ids: Tuple[str, ...],
        creation_strategy_ids: Tuple[str, ...],
        selected_codegen_style_id: str,
        discovery_reason: str,
        owner_creations_override: Optional[Any] = None,
        restore_owner_creations: bool = True,
) -> Any:
    """
    Build one forced `CreationContext` from real phase-9 truth.
    """
    artifact = spell._compiler_artifact
    original_owner_creations = spell._owner_creations
    if owner_creations_override is not None:
        spell._owner_creations = owner_creations_override
    try:
        _build_forced_plan(
            artifact=artifact,
            plan_strategy_id=plan_strategy_id,
            plan_family_id=plan_family_id,
            candidate_codegen_style_ids=candidate_codegen_style_ids,
        )
        _build_forced_creation(
            artifact=artifact,
            creation_strategy_ids=creation_strategy_ids,
            discovery_reason=discovery_reason,
            selected_codegen_style_id=selected_codegen_style_id,
        )
        spell._cleanup_creation_context()
        return CreationContextBuilder.build(spell)
    finally:
        if restore_owner_creations:
            spell._owner_creations = original_owner_creations


def _measure_execute_no_hooks(
        *,
        action: Any,
        reset: Optional[Any],
        iterations: int,
        warmup: int,
) -> float:
    """
    Measure one prepared `CreationContext.execute_no_hooks(...)` action.
    """
    for _ in range(warmup):
        if reset is not None:
            reset()
        action()
    start_ns = time.perf_counter_ns()
    for _ in range(iterations):
        if reset is not None:
            reset()
        action()
    end_ns = time.perf_counter_ns()
    return (end_ns - start_ns) / iterations


def _measure_meld(
        *,
        action: Any,
        reset: Optional[Any],
        iterations: int,
        warmup: int,
) -> float:
    """
    Measure one prepared `meld(...)` action.
    """
    for _ in range(warmup):
        if reset is not None:
            reset()
        action()
    start_ns = time.perf_counter_ns()
    for _ in range(iterations):
        if reset is not None:
            reset()
        action()
    end_ns = time.perf_counter_ns()
    return (end_ns - start_ns) / iterations


def _measure_execute_raises(
        *,
        action: Any,
        expected_exception: type[BaseException],
        reset: Optional[Any],
) -> str:
    """
    Run one override action and return the observed expected exception type name.
    """
    if reset is not None:
        reset()
    try:
        action()
    except expected_exception as exc:
        return type(exc).__name__
    raise AssertionError(
        f"Expected {expected_exception.__name__} was not raised."
    )


def _make_spell_for_existence(
        *,
        existence: Existence,
        bind_mode: str,
        extra_many_visible_spell: bool = False,
) -> Tuple[Any, Any, Any]:
    """
    Build one fresh one-spell runtime environment for a solo existence scenario.
    """
    reset_aether_runtime()
    spellbook = make_spellbook()
    conduit = None
    try:
        if bind_mode == "existing_creation":
            root_object = _SoloConfigurableRoot()
            root_spell_id = spellbook.bind(
                spell=root_object,
                existence=Existence.unique,
                permissions="create",
            )
        else:
            root_spell_id = spellbook.bind(
                spell=_SoloConfigurableRoot,
                existence=existence,
                permissions="create",
            )
            if extra_many_visible_spell:
                spellbook.bind(
                    spell=_ManyOnlyConfigurableLeaf,
                    existence=Existence.many,
                    permissions="create",
                )
        conduit = spellbook.conjure(name="root")
        root_spell = get_spell_by_version_id(spellbook, root_spell_id)
        assert root_spell is not None
        return spellbook, conduit, root_spell
    except Exception:
        if conduit is not None:
            try:
                conduit.permanent_cleanup()
            except Exception:
                pass
        try:
            spellbook.cleanup()
        except Exception:
            pass
        reset_aether_runtime()
        gc.collect()
        raise


def _cleanup_environment(
        *,
        spellbook: Any,
        conduit: Any,
) -> None:
    """
    Clean one fresh one-spell runtime environment.
    """
    if conduit is not None:
        try:
            conduit.permanent_cleanup()
        except Exception:
            pass
    try:
        spellbook.cleanup()
    except Exception:
        pass
    reset_aether_runtime()
    gc.collect()


def _benchmark_forced_family_no_overrides(
        *,
        existence: Existence,
        bind_mode: str,
        plan_strategy_id: str,
        plan_family_id: str,
        candidate_codegen_style_ids: Tuple[str, ...],
        creation_strategy_ids: Tuple[str, ...],
        selected_codegen_style_id: str,
        discovery_reason: str,
        caller_mode: str,
        iterations: int,
        warmup: int,
        extra_many_visible_spell: bool = False,
) -> float:
    """
    Time one forced family on the solo no-overrides path for one exact existence.
    """
    spellbook, conduit, root_spell = _make_spell_for_existence(
        existence=existence,
        bind_mode=bind_mode,
        extra_many_visible_spell=extra_many_visible_spell,
    )
    try:
        caller_creations = conduit._creations
        reset = None
        owner_override = None
        if caller_mode == "fresh_caller":
            caller_creations = _FreshCreationsProbe()
            reset = caller_creations.reset
        elif caller_mode == "fresh_owner":
            owner_override = _FreshCreationsProbe()
            reset = owner_override.reset
            caller_creations = None

        creation_context = _build_forced_creation_context(
            spell=root_spell,
            plan_strategy_id=plan_strategy_id,
            plan_family_id=plan_family_id,
            candidate_codegen_style_ids=candidate_codegen_style_ids,
            creation_strategy_ids=creation_strategy_ids,
            selected_codegen_style_id=selected_codegen_style_id,
            discovery_reason=discovery_reason,
            owner_creations_override=owner_override,
            restore_owner_creations=owner_override is None,
        )

        return _measure_execute_no_hooks(
            action=lambda: creation_context.execute_no_hooks(caller_creations),
            reset=reset,
            iterations=iterations,
            warmup=warmup,
        )
    finally:
        _cleanup_environment(spellbook=spellbook, conduit=conduit)


def _benchmark_forced_family_overrides(
        *,
        existence: Existence,
        bind_mode: str,
        plan_strategy_id: str,
        plan_family_id: str,
        candidate_codegen_style_ids: Tuple[str, ...],
        creation_strategy_ids: Tuple[str, ...],
        selected_codegen_style_id: str,
        discovery_reason: str,
        caller_mode: str,
        iterations: int,
        warmup: int,
        extra_many_visible_spell: bool = False,
) -> Tuple[Optional[float], Optional[str]]:
    """
    Time or classify one forced family on the solo overrides path for one exact existence.
    """
    spellbook, conduit, root_spell = _make_spell_for_existence(
        existence=existence,
        bind_mode=bind_mode,
        extra_many_visible_spell=extra_many_visible_spell,
    )
    try:
        override_payload = {"value": object()}
        caller_creations = conduit._creations
        reset = None
        owner_override = None
        if caller_mode == "fresh_caller":
            caller_creations = _FreshCreationsProbe()
            reset = caller_creations.reset
        elif caller_mode == "fresh_owner":
            owner_override = _FreshCreationsProbe()
            reset = owner_override.reset
            caller_creations = None

        creation_context = _build_forced_creation_context(
            spell=root_spell,
            plan_strategy_id=plan_strategy_id,
            plan_family_id=plan_family_id,
            candidate_codegen_style_ids=candidate_codegen_style_ids,
            creation_strategy_ids=creation_strategy_ids,
            selected_codegen_style_id=selected_codegen_style_id,
            discovery_reason=discovery_reason,
            owner_creations_override=owner_override,
            restore_owner_creations=owner_override is None,
        )

        if bind_mode == "existing_creation":
            error_name = _measure_execute_raises(
                action=lambda: creation_context.execute_no_hooks(
                    caller_creations,
                    override_payload,
                ),
                expected_exception=MeldExecutionError,
                reset=reset,
            )
            return None, error_name

        return _measure_execute_no_hooks(
            action=lambda: creation_context.execute_no_hooks(
                caller_creations,
                override_payload,
            ),
            reset=reset,
            iterations=iterations,
            warmup=warmup,
        ), None
    finally:
        _cleanup_environment(spellbook=spellbook, conduit=conduit)


def _benchmark_forced_family_meld_no_overrides(
        *,
        existence: Existence,
        bind_mode: str,
        plan_strategy_id: str,
        plan_family_id: str,
        candidate_codegen_style_ids: Tuple[str, ...],
        creation_strategy_ids: Tuple[str, ...],
        selected_codegen_style_id: str,
        discovery_reason: str,
        route: str,
        meld_mode: str,
        iterations: int,
        warmup: int,
        extra_many_visible_spell: bool = False,
) -> Optional[float]:
    """
    Time one forced family through the real meld front door on the no-overrides path.
    """
    if bind_mode == "existing_creation":
        return None
    if meld_mode == "warm_reuse" and route == "many":
        return None

    spellbook, conduit, root_spell = _make_spell_for_existence(
        existence=existence,
        bind_mode=bind_mode,
        extra_many_visible_spell=extra_many_visible_spell,
    )
    try:
        _build_forced_creation_context(
            spell=root_spell,
            plan_strategy_id=plan_strategy_id,
            plan_family_id=plan_family_id,
            candidate_codegen_style_ids=candidate_codegen_style_ids,
            creation_strategy_ids=creation_strategy_ids,
            selected_codegen_style_id=selected_codegen_style_id,
            discovery_reason=discovery_reason,
        )
        root_spell_id = root_spell.spell_id

        if route == "spellspace":
            with conduit.enter_spellspace() as space:
                reset = None
                if meld_mode == "cold_create":
                    reset = space._creations.clear_all
                return _measure_meld(
                    action=lambda: space.meld(spell=root_spell_id),
                    reset=reset,
                    iterations=iterations,
                    warmup=warmup,
                )

        reset = None
        if meld_mode == "cold_create":
            reset = conduit._creations.clear_all
        return _measure_meld(
            action=lambda: conduit.meld(spell=root_spell_id),
            reset=reset,
            iterations=iterations,
            warmup=warmup,
        )
    finally:
        _cleanup_environment(spellbook=spellbook, conduit=conduit)


def _format_results_table(rows: Sequence[Dict[str, Any]]) -> str:
    """
    Format one compact benchmark table for terminal output.
    """
    headers = (
        "existence",
        "route",
        "bind_mode",
        "strategy_family",
        "phase10_strategy_id",
        "phase11_strategy_id",
        "no_ns",
        "meld_cold_ns",
        "meld_warm_ns",
        "ov_ns",
        "note",
    )
    string_rows = []
    for row in rows:
        if row["bind_mode"] == "existing_creation":
            string_rows.append(
                {
                    "existence": str(row["existence"]),
                    "route": str(row["route"]),
                    "bind_mode": str(row["bind_mode"]),
                    "strategy_family": "bypassed",
                    "phase10_strategy_id": "-",
                    "phase11_strategy_id": "-",
                    "no_ns": "-",
                    "meld_cold_ns": "-",
                    "meld_warm_ns": "-",
                    "ov_ns": "-",
                    "note": row["overrides_note"],
                }
            )
            continue

        string_rows.append(
            {
                "existence": str(row["existence"]),
                "route": str(row["route"]),
                "bind_mode": str(row["bind_mode"]),
                "strategy_family": "generalized",
                "phase10_strategy_id": "generalized_codegen_plan",
                "phase11_strategy_id": "generalized_codegen_creation",
                "no_ns": (
                    "-"
                    if row["no_generalized_ns_per_iter"] is None
                    else f"{row['no_generalized_ns_per_iter']:.3f}"
                ),
                "meld_cold_ns": (
                    "-"
                    if row["meld_cold_generalized_ns_per_iter"] is None
                    else f"{row['meld_cold_generalized_ns_per_iter']:.3f}"
                ),
                "meld_warm_ns": (
                    "-"
                    if row["meld_warm_generalized_ns_per_iter"] is None
                    else f"{row['meld_warm_generalized_ns_per_iter']:.3f}"
                ),
                "ov_ns": (
                    "-"
                    if row["overrides_generalized_ns_per_iter"] is None
                    else f"{row['overrides_generalized_ns_per_iter']:.3f}"
                ),
                "note": (
                    row["generalized_note"]
                    or (
                        "warm_reuse_bypassed=always_creates"
                        if row["meld_warm_generalized_ns_per_iter"] is None
                        and row["route"] == "many"
                        else ""
                    )
                ),
            }
        )
        string_rows.append(
            {
                "existence": str(row["existence"]),
                "route": str(row["route"]),
                "bind_mode": str(row["bind_mode"]),
                "strategy_family": "solo",
                "phase10_strategy_id": "generalized_solo_codegen_plan",
                "phase11_strategy_id": "solo_codegen_creation",
                "no_ns": (
                    "-"
                    if row["no_solo_ns_per_iter"] is None
                    else f"{row['no_solo_ns_per_iter']:.3f}"
                ),
                "meld_cold_ns": (
                    "-"
                    if row["meld_cold_solo_ns_per_iter"] is None
                    else f"{row['meld_cold_solo_ns_per_iter']:.3f}"
                ),
                "meld_warm_ns": (
                    "-"
                    if row["meld_warm_solo_ns_per_iter"] is None
                    else f"{row['meld_warm_solo_ns_per_iter']:.3f}"
                ),
                "ov_ns": (
                    "-"
                    if row["overrides_solo_ns_per_iter"] is None
                    else f"{row['overrides_solo_ns_per_iter']:.3f}"
                ),
                "note": (
                    row["solo_note"]
                    or (
                        "-"
                        if row["no_solo_over_generalized_ratio"] is None
                        else f"no={row['no_solo_over_generalized_ratio']:.6f}; "
                        f"cold={row['meld_cold_solo_over_generalized_ratio']:.6f}; "
                        + (
                            "warm=always_creates; "
                            if row["meld_warm_solo_over_generalized_ratio"] is None
                            else f"warm={row['meld_warm_solo_over_generalized_ratio']:.6f}; "
                        )
                        + (
                            f"ov={row['overrides_solo_over_generalized_ratio']:.6f}"
                        )
                    )
                ),
            }
        )
        if row["route"] == "many":
            string_rows.append(
                {
                    "existence": str(row["existence"]),
                    "route": str(row["route"]),
                    "bind_mode": str(row["bind_mode"]),
                    "strategy_family": "many_only",
                    "phase10_strategy_id": "many_only_codegen_plan",
                    "phase11_strategy_id": "many_only_codegen_creation",
                    "no_ns": (
                        "-"
                        if row["no_many_only_ns_per_iter"] is None
                        else f"{row['no_many_only_ns_per_iter']:.3f}"
                    ),
                    "meld_cold_ns": (
                        "-"
                        if row["meld_cold_many_only_ns_per_iter"] is None
                        else f"{row['meld_cold_many_only_ns_per_iter']:.3f}"
                    ),
                    "meld_warm_ns": (
                        "-"
                        if row["meld_warm_many_only_ns_per_iter"] is None
                        else f"{row['meld_warm_many_only_ns_per_iter']:.3f}"
                    ),
                    "ov_ns": (
                        "-"
                        if row["overrides_many_only_ns_per_iter"] is None
                        else f"{row['overrides_many_only_ns_per_iter']:.3f}"
                    ),
                    "note": (
                        row["many_only_note"]
                        or (
                            "-"
                            if row["no_many_only_over_generalized_ratio"] is None
                            else f"no={row['no_many_only_over_generalized_ratio']:.6f}; "
                            f"cold={row['meld_cold_many_only_over_generalized_ratio']:.6f}; "
                            + (
                                "warm=always_creates; "
                                if row["meld_warm_many_only_over_generalized_ratio"] is None
                                else f"warm={row['meld_warm_many_only_over_generalized_ratio']:.6f}; "
                            )
                            + (
                                "-"
                                if row["overrides_many_only_over_generalized_ratio"] is None
                                else f"ov={row['overrides_many_only_over_generalized_ratio']:.6f}"
                            )
                        )
                    ),
                }
            )
    widths = {header: len(header) for header in headers}
    for row in string_rows:
        for header in headers:
            widths[header] = max(widths[header], len(row[header]))

    def _line(values: Dict[str, str]) -> str:
        return "| " + " | ".join(
            values[header].ljust(widths[header]) for header in headers
        ) + " |"

    header_row = {header: header for header in headers}
    separator_row = {
        header: "-" * widths[header]
        for header in headers
    }
    lines = [
        _line(header_row),
        _line(separator_row),
    ]
    for row in string_rows:
        lines.append(_line(row))
    return "\n".join(lines)


def _capture_benchmark_result(
        action: Callable[[], Optional[float]],
) -> Tuple[Optional[float], Optional[str]]:
    """
    Run one benchmark action and capture an honest failure note on exception.
    """
    try:
        return action(), None
    except Exception as exc:
        return None, f"{type(exc).__name__}: {exc}"


def _capture_overrides_benchmark_result(
        action: Callable[[], Tuple[Optional[float], Optional[str]]],
) -> Tuple[Optional[float], Optional[str]]:
    """
    Run one overrides benchmark and capture an honest failure note on exception.
    """
    try:
        return action()
    except Exception as exc:
        return None, f"{type(exc).__name__}: {exc}"


def _benchmark_solo_existence_matrix() -> Sequence[Dict[str, Any]]:
    """
    Compare generalized versus solo across exact solo existence categories.
    """
    iterations = 5000
    warmup = 1000
    scenarios = (
        {
            "existence": Existence.many,
            "route": "many",
            "bind_mode": "construct",
            "caller_mode": "fresh_caller",
        },
        {
            "existence": Existence.unique_per_conduit,
            "route": "unique_per_conduit",
            "bind_mode": "construct",
            "caller_mode": "fresh_caller",
        },
        {
            "existence": Existence.unique_per_spell_space,
            "route": "spellspace",
            "bind_mode": "construct",
            "caller_mode": "fresh_caller",
        },
        {
            "existence": Existence.unique,
            "route": "shared",
            "bind_mode": "construct",
            "caller_mode": "fresh_owner",
        },
        {
            "existence": Existence.unique_per_conduit_cluster,
            "route": "shared",
            "bind_mode": "construct",
            "caller_mode": "fresh_owner",
        },
        {
            "existence": Existence.unique_per_conduit_lineage,
            "route": "shared",
            "bind_mode": "construct",
            "caller_mode": "fresh_owner",
        },
        {
            "existence": Existence.unique,
            "route": "existing_creation",
            "bind_mode": "existing_creation",
            "caller_mode": "existing",
        },
    )

    rows = []
    for scenario in scenarios:
        overrides_note = ""
        use_all_many_visible_shape = scenario["route"] == "many"
        if scenario["bind_mode"] == "existing_creation":
            no_generalized_ns = None
            no_solo_ns = None
            no_many_only_ns = None
            meld_cold_generalized_ns = None
            meld_cold_solo_ns = None
            meld_cold_many_only_ns = None
            meld_cold_ratio = None
            meld_cold_many_only_ratio = None
            meld_warm_generalized_ns = None
            meld_warm_solo_ns = None
            meld_warm_many_only_ns = None
            meld_warm_ratio = None
            meld_warm_many_only_ratio = None
            overrides_generalized_ns = None
            overrides_solo_ns = None
            overrides_many_only_ns = None
            overrides_ratio = None
            overrides_many_only_ratio = None
            overrides_note = "phase10_11_bypassed"
            no_ratio = None
            no_many_only_ratio = None
            generalized_note = None
            solo_note = None
            many_only_note = "not_applicable=requires_multi_spell_all_many"
        else:
            no_generalized_ns, generalized_note = _capture_benchmark_result(
                lambda: _benchmark_forced_family_no_overrides(
                    existence=scenario["existence"],
                    bind_mode=scenario["bind_mode"],
                    plan_strategy_id="generalized_codegen_plan",
                    plan_family_id="generalized",
                    candidate_codegen_style_ids=("generalized_default",),
                    creation_strategy_ids=("generalized_codegen_creation",),
                    selected_codegen_style_id="generalized_default",
                    discovery_reason="forced_generalized_creation_family",
                    caller_mode=scenario["caller_mode"],
                    iterations=iterations,
                    warmup=warmup,
                    extra_many_visible_spell=use_all_many_visible_shape,
                )
            )
            no_solo_ns, solo_note = _capture_benchmark_result(
                lambda: _benchmark_forced_family_no_overrides(
                    existence=scenario["existence"],
                    bind_mode=scenario["bind_mode"],
                    plan_strategy_id="generalized_solo_codegen_plan",
                    plan_family_id="solo",
                    candidate_codegen_style_ids=("generalized_solo",),
                    creation_strategy_ids=("solo_codegen_creation",),
                    selected_codegen_style_id="generalized_solo",
                    discovery_reason="forced_solo_creation_family",
                    caller_mode=scenario["caller_mode"],
                    iterations=iterations,
                    warmup=warmup,
                )
            )
            meld_cold_generalized_ns, generalized_meld_cold_note = _capture_benchmark_result(
                lambda: _benchmark_forced_family_meld_no_overrides(
                    existence=scenario["existence"],
                    bind_mode=scenario["bind_mode"],
                    plan_strategy_id="generalized_codegen_plan",
                    plan_family_id="generalized",
                    candidate_codegen_style_ids=("generalized_default",),
                    creation_strategy_ids=("generalized_codegen_creation",),
                    selected_codegen_style_id="generalized_default",
                    discovery_reason="forced_generalized_creation_family",
                    route=scenario["route"],
                    meld_mode="cold_create",
                    iterations=iterations,
                    warmup=warmup,
                    extra_many_visible_spell=use_all_many_visible_shape,
                )
            )
            meld_cold_solo_ns, solo_meld_cold_note = _capture_benchmark_result(
                lambda: _benchmark_forced_family_meld_no_overrides(
                    existence=scenario["existence"],
                    bind_mode=scenario["bind_mode"],
                    plan_strategy_id="generalized_solo_codegen_plan",
                    plan_family_id="solo",
                    candidate_codegen_style_ids=("generalized_solo",),
                    creation_strategy_ids=("solo_codegen_creation",),
                    selected_codegen_style_id="generalized_solo",
                    discovery_reason="forced_solo_creation_family",
                    route=scenario["route"],
                    meld_mode="cold_create",
                    iterations=iterations,
                    warmup=warmup,
                )
            )
            meld_warm_generalized_ns, generalized_meld_warm_note = _capture_benchmark_result(
                lambda: _benchmark_forced_family_meld_no_overrides(
                    existence=scenario["existence"],
                    bind_mode=scenario["bind_mode"],
                    plan_strategy_id="generalized_codegen_plan",
                    plan_family_id="generalized",
                    candidate_codegen_style_ids=("generalized_default",),
                    creation_strategy_ids=("generalized_codegen_creation",),
                    selected_codegen_style_id="generalized_default",
                    discovery_reason="forced_generalized_creation_family",
                    route=scenario["route"],
                    meld_mode="warm_reuse",
                    iterations=iterations,
                    warmup=warmup,
                    extra_many_visible_spell=use_all_many_visible_shape,
                )
            )
            meld_warm_solo_ns, solo_meld_warm_note = _capture_benchmark_result(
                lambda: _benchmark_forced_family_meld_no_overrides(
                    existence=scenario["existence"],
                    bind_mode=scenario["bind_mode"],
                    plan_strategy_id="generalized_solo_codegen_plan",
                    plan_family_id="solo",
                    candidate_codegen_style_ids=("generalized_solo",),
                    creation_strategy_ids=("solo_codegen_creation",),
                    selected_codegen_style_id="generalized_solo",
                    discovery_reason="forced_solo_creation_family",
                    route=scenario["route"],
                    meld_mode="warm_reuse",
                    iterations=iterations,
                    warmup=warmup,
                )
            )
            meld_cold_ratio = None
            if (
                    meld_cold_generalized_ns is not None
                    and meld_cold_solo_ns is not None
            ):
                meld_cold_ratio = meld_cold_solo_ns / meld_cold_generalized_ns
            meld_warm_ratio = None
            if (
                    meld_warm_generalized_ns is not None
                    and meld_warm_solo_ns is not None
            ):
                meld_warm_ratio = meld_warm_solo_ns / meld_warm_generalized_ns
            overrides_generalized_ns, overrides_generalized_note = (
                _capture_overrides_benchmark_result(
                    lambda: _benchmark_forced_family_overrides(
                        existence=scenario["existence"],
                        bind_mode=scenario["bind_mode"],
                        plan_strategy_id="generalized_codegen_plan",
                        plan_family_id="generalized",
                        candidate_codegen_style_ids=("generalized_default",),
                        creation_strategy_ids=("generalized_codegen_creation",),
                        selected_codegen_style_id="generalized_default",
                        discovery_reason="forced_generalized_creation_family",
                        caller_mode=scenario["caller_mode"],
                        iterations=iterations,
                        warmup=warmup,
                        extra_many_visible_spell=use_all_many_visible_shape,
                    )
                )
            )
            overrides_solo_ns, overrides_solo_note = _capture_overrides_benchmark_result(
                lambda: _benchmark_forced_family_overrides(
                    existence=scenario["existence"],
                    bind_mode=scenario["bind_mode"],
                    plan_strategy_id="generalized_solo_codegen_plan",
                    plan_family_id="solo",
                    candidate_codegen_style_ids=("generalized_solo",),
                    creation_strategy_ids=("solo_codegen_creation",),
                    selected_codegen_style_id="generalized_solo",
                    discovery_reason="forced_solo_creation_family",
                    caller_mode=scenario["caller_mode"],
                    iterations=iterations,
                    warmup=warmup,
                )
            )
            overrides_note = (
                overrides_generalized_note
                or overrides_solo_note
                or ""
            )
            overrides_ratio = None
            if (
                    overrides_generalized_ns is not None
                    and overrides_solo_ns is not None
            ):
                overrides_ratio = overrides_solo_ns / overrides_generalized_ns
            no_ratio = None
            if no_generalized_ns is not None and no_solo_ns is not None:
                no_ratio = no_solo_ns / no_generalized_ns

            no_many_only_ns = None
            meld_cold_many_only_ns = None
            meld_warm_many_only_ns = None
            overrides_many_only_ns = None
            no_many_only_ratio = None
            meld_cold_many_only_ratio = None
            meld_warm_many_only_ratio = None
            overrides_many_only_ratio = None
            many_only_note = "not_applicable=requires_multi_spell_all_many"
            if scenario["route"] == "many":
                no_many_only_ns, many_no_note = _capture_benchmark_result(
                    lambda: _benchmark_forced_family_no_overrides(
                        existence=scenario["existence"],
                        bind_mode=scenario["bind_mode"],
                        plan_strategy_id="many_only_codegen_plan",
                        plan_family_id="many_only",
                        candidate_codegen_style_ids=("many_only",),
                        creation_strategy_ids=("many_only_codegen_creation",),
                        selected_codegen_style_id="many_only",
                        discovery_reason="forced_many_only_creation_family",
                        caller_mode=scenario["caller_mode"],
                        iterations=iterations,
                        warmup=warmup,
                        extra_many_visible_spell=True,
                    )
                )
                meld_cold_many_only_ns, many_meld_cold_note = _capture_benchmark_result(
                    lambda: _benchmark_forced_family_meld_no_overrides(
                        existence=scenario["existence"],
                        bind_mode=scenario["bind_mode"],
                        plan_strategy_id="many_only_codegen_plan",
                        plan_family_id="many_only",
                        candidate_codegen_style_ids=("many_only",),
                        creation_strategy_ids=("many_only_codegen_creation",),
                        selected_codegen_style_id="many_only",
                        discovery_reason="forced_many_only_creation_family",
                        route=scenario["route"],
                        meld_mode="cold_create",
                        iterations=iterations,
                        warmup=warmup,
                        extra_many_visible_spell=True,
                    )
                )
                meld_warm_many_only_ns, many_meld_warm_note = _capture_benchmark_result(
                    lambda: _benchmark_forced_family_meld_no_overrides(
                        existence=scenario["existence"],
                        bind_mode=scenario["bind_mode"],
                        plan_strategy_id="many_only_codegen_plan",
                        plan_family_id="many_only",
                        candidate_codegen_style_ids=("many_only",),
                        creation_strategy_ids=("many_only_codegen_creation",),
                        selected_codegen_style_id="many_only",
                        discovery_reason="forced_many_only_creation_family",
                        route=scenario["route"],
                        meld_mode="warm_reuse",
                        iterations=iterations,
                        warmup=warmup,
                        extra_many_visible_spell=True,
                    )
                )
                overrides_many_only_ns, many_overrides_note = _capture_overrides_benchmark_result(
                    lambda: _benchmark_forced_family_overrides(
                        existence=scenario["existence"],
                        bind_mode=scenario["bind_mode"],
                        plan_strategy_id="many_only_codegen_plan",
                        plan_family_id="many_only",
                        candidate_codegen_style_ids=("many_only",),
                        creation_strategy_ids=("many_only_codegen_creation",),
                        selected_codegen_style_id="many_only",
                        discovery_reason="forced_many_only_creation_family",
                        caller_mode=scenario["caller_mode"],
                        iterations=iterations,
                        warmup=warmup,
                        extra_many_visible_spell=True,
                    )
                )
                many_only_note = (
                    many_no_note
                    or many_meld_cold_note
                    or many_meld_warm_note
                    or many_overrides_note
                    or ""
                )
                if (
                        no_generalized_ns is not None
                        and no_many_only_ns is not None
                ):
                    no_many_only_ratio = (
                        no_many_only_ns / no_generalized_ns
                    )
                if (
                        meld_cold_generalized_ns is not None
                        and meld_cold_many_only_ns is not None
                ):
                    meld_cold_many_only_ratio = (
                        meld_cold_many_only_ns / meld_cold_generalized_ns
                    )
                if (
                        meld_warm_generalized_ns is not None
                        and meld_warm_many_only_ns is not None
                ):
                    meld_warm_many_only_ratio = (
                        meld_warm_many_only_ns / meld_warm_generalized_ns
                    )
                if (
                        overrides_generalized_ns is not None
                        and overrides_many_only_ns is not None
                ):
                    overrides_many_only_ratio = (
                        overrides_many_only_ns / overrides_generalized_ns
                    )

            if generalized_note is None:
                generalized_note = (
                    generalized_meld_cold_note
                    or generalized_meld_warm_note
                    or overrides_generalized_note
                )
            if solo_note is None:
                solo_note = (
                    solo_meld_cold_note
                    or solo_meld_warm_note
                    or overrides_solo_note
                )

        rows.append(
            {
                "existence": scenario["existence"].name,
                "route": scenario["route"],
                "bind_mode": scenario["bind_mode"],
                "iterations": iterations,
                "warmup": warmup,
                "generalized_note": generalized_note,
                "solo_note": solo_note,
                "many_only_note": many_only_note,
                "no_generalized_ns_per_iter": no_generalized_ns,
                "no_solo_ns_per_iter": no_solo_ns,
                "no_solo_over_generalized_ratio": no_ratio,
                "no_many_only_ns_per_iter": no_many_only_ns,
                "no_many_only_over_generalized_ratio": no_many_only_ratio,
                "meld_cold_generalized_ns_per_iter": meld_cold_generalized_ns,
                "meld_cold_solo_ns_per_iter": meld_cold_solo_ns,
                "meld_cold_solo_over_generalized_ratio": meld_cold_ratio,
                "meld_cold_many_only_ns_per_iter": meld_cold_many_only_ns,
                "meld_cold_many_only_over_generalized_ratio": (
                    meld_cold_many_only_ratio
                ),
                "meld_warm_generalized_ns_per_iter": meld_warm_generalized_ns,
                "meld_warm_solo_ns_per_iter": meld_warm_solo_ns,
                "meld_warm_solo_over_generalized_ratio": meld_warm_ratio,
                "meld_warm_many_only_ns_per_iter": meld_warm_many_only_ns,
                "meld_warm_many_only_over_generalized_ratio": (
                    meld_warm_many_only_ratio
                ),
                "overrides_generalized_ns_per_iter": overrides_generalized_ns,
                "overrides_solo_ns_per_iter": overrides_solo_ns,
                "overrides_solo_over_generalized_ratio": overrides_ratio,
                "overrides_many_only_ns_per_iter": overrides_many_only_ns,
                "overrides_many_only_over_generalized_ratio": (
                    overrides_many_only_ratio
                ),
                "overrides_note": overrides_note,
            }
        )

    print("FORCED_PHASE10_PHASE11_CREATION_CONTEXT_STRATEGY_TABLE")
    print(_format_results_table(rows))
    return rows


def test_forced_phase10_phase11_creation_context_solo_existence_matrix() -> None:
    """
    Run the solo existence matrix and assert every category produced usable output.
    """
    rows = _benchmark_solo_existence_matrix()
    assert len(rows) == 7
    for row in rows:
        assert row["iterations"] >= 1000
        if row["bind_mode"] == "existing_creation":
            assert row["overrides_note"] == "phase10_11_bypassed"
        else:
            assert row["no_generalized_ns_per_iter"] is not None
            assert row["no_generalized_ns_per_iter"] > 0
            assert row["meld_cold_generalized_ns_per_iter"] is not None
            assert row["meld_cold_generalized_ns_per_iter"] > 0
            if row["route"] != "many":
                assert row["meld_warm_generalized_ns_per_iter"] is not None
                assert row["meld_warm_generalized_ns_per_iter"] > 0
            assert row["overrides_generalized_ns_per_iter"] is not None
            assert row["overrides_generalized_ns_per_iter"] > 0

            if row["no_solo_ns_per_iter"] is None:
                assert row["solo_note"]
            else:
                assert row["no_solo_ns_per_iter"] > 0
            if row["meld_cold_solo_ns_per_iter"] is None:
                assert row["solo_note"]
            else:
                assert row["meld_cold_solo_ns_per_iter"] > 0
            if row["route"] != "many":
                if row["meld_warm_solo_ns_per_iter"] is None:
                    assert row["solo_note"]
                else:
                    assert row["meld_warm_solo_ns_per_iter"] > 0
            if row["overrides_solo_ns_per_iter"] is None:
                assert row["solo_note"] or row["overrides_note"]
            else:
                assert row["overrides_solo_ns_per_iter"] > 0

            if row["route"] == "many":
                if row["no_many_only_ns_per_iter"] is None:
                    assert row["many_only_note"]
                else:
                    assert row["no_many_only_ns_per_iter"] > 0
                if row["meld_cold_many_only_ns_per_iter"] is None:
                    assert row["many_only_note"]
                else:
                    assert row["meld_cold_many_only_ns_per_iter"] > 0
                if row["overrides_many_only_ns_per_iter"] is None:
                    assert row["many_only_note"]
                else:
                    assert row["overrides_many_only_ns_per_iter"] > 0


def _run_experiment() -> None:
    """
    Execute the solo existence matrix directly.
    """
    _benchmark_solo_existence_matrix()
    print("OK_FORCED_PHASE10_PHASE11_CREATION_CONTEXT_COMPARISON_HARNESS")


if __name__ == "__main__":
    _run_experiment()
