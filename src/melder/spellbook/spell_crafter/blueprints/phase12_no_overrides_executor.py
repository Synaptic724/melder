from typing import Any, Callable, Dict, Optional, Tuple

from melder.spellbook.spell_crafter.blueprints.execution_plan import (
    ExecutionPlan,
    ExecutionPlanCallMode,
)
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError


def compile_phase12_no_overrides_executor(
        *,
        execution_plan: ExecutionPlan,
) -> Optional[Callable[[], Any]]:
    """
    Compile a spell-scoped Phase 12 no-overrides executor.

    Purpose:
        Move fast transient codegen ownership from `MeldRuntime` to spell
        compilation so runtime dispatch can execute a spell-local artifact.

    Contract:
        - Returns a callable only when `execution_plan.fast_transient_plan`
          exists and all call modes are supported.
        - Returns `None` when no transient plan exists or when the plan shape
          cannot be code-generated.
        - Compiled executor raises `MeldExecutionError` with step context when
          a call target raises during execution.

    Args:
        execution_plan:
            Phase 11 no-overrides execution plan for one spell.

    Returns:
        Optional[Callable[[], Any]]:
            The compiled zero-argument executor for the spell, or `None`
            when compilation is not possible for this plan.

    Raises:
        ValueError:
            If `execution_plan` is `None`.
    """
    if execution_plan is None:
        raise ValueError("execution_plan must not be None.")

    transient_plan = execution_plan.fast_transient_plan
    if transient_plan is None:
        return None

    source = _build_phase12_executor_source(transient_plan=transient_plan)
    if source is None:
        return None

    namespace = _build_executor_namespace(
        execution_plan=execution_plan,
        transient_plan=transient_plan,
    )
    local_namespace: Dict[str, Any] = {}
    try:
        exec(
            compile(source, "<melder_phase12_no_overrides_executor>", "exec"),
            namespace,
            local_namespace,
        )
    except Exception:
        return None

    executor = local_namespace.get("_phase12_executor")
    if not callable(executor):
        return None
    return executor


def _build_phase12_executor_source(
        *,
        transient_plan: Tuple[Any, ...],
) -> Optional[str]:
    """
    Build Python source for a phase12 no-overrides unrolled executor.

    Contract:
        - Generates one direct call statement per transient step.
        - Returns `None` when any step uses `CALLN` or an unsupported mode.

    Args:
        transient_plan:
            Tuple payload produced by `ExecutionPlan.fast_transient_plan`.

    Returns:
        Optional[str]:
            Source code for `_phase12_executor`, or `None` when plan shape
            is not supported.
    """
    transient_step_count = transient_plan[0]
    transient_root_index = transient_plan[1]
    transient_call_modes = transient_plan[3]
    transient_dep1 = transient_plan[4]
    transient_dep2a = transient_plan[5]
    transient_dep2b = transient_plan[6]
    transient_dep3a = transient_plan[7]
    transient_dep3b = transient_plan[8]
    transient_dep3c = transient_plan[9]
    transient_dep4a = transient_plan[10]
    transient_dep4b = transient_plan[11]
    transient_dep4c = transient_plan[12]
    transient_dep4d = transient_plan[13]
    transient_dep5a = transient_plan[14]
    transient_dep5b = transient_plan[15]
    transient_dep5c = transient_plan[16]
    transient_dep5d = transient_plan[17]
    transient_dep5e = transient_plan[18]
    transient_dep6a = transient_plan[19]
    transient_dep6b = transient_plan[20]
    transient_dep6c = transient_plan[21]
    transient_dep6d = transient_plan[22]
    transient_dep6e = transient_plan[23]
    transient_dep6f = transient_plan[24]
    transient_dep7a = transient_plan[25]
    transient_dep7b = transient_plan[26]
    transient_dep7c = transient_plan[27]
    transient_dep7d = transient_plan[28]
    transient_dep7e = transient_plan[29]
    transient_dep7f = transient_plan[30]
    transient_dep7g = transient_plan[31]
    transient_dep8a = transient_plan[32]
    transient_dep8b = transient_plan[33]
    transient_dep8c = transient_plan[34]
    transient_dep8d = transient_plan[35]
    transient_dep8e = transient_plan[36]
    transient_dep8f = transient_plan[37]
    transient_dep8g = transient_plan[38]
    transient_dep8h = transient_plan[39]

    lines = [
        "def _phase12_executor(",
        "        *,",
        "        transient_root_index=transient_root_index,",
        "        transient_targets=transient_targets,",
        "        transient_dep1=transient_dep1,",
        "        transient_dep2a=transient_dep2a,",
        "        transient_dep2b=transient_dep2b,",
        "        transient_dep3a=transient_dep3a,",
        "        transient_dep3b=transient_dep3b,",
        "        transient_dep3c=transient_dep3c,",
        "        transient_dep4a=transient_dep4a,",
        "        transient_dep4b=transient_dep4b,",
        "        transient_dep4c=transient_dep4c,",
        "        transient_dep4d=transient_dep4d,",
        "        transient_dep5a=transient_dep5a,",
        "        transient_dep5b=transient_dep5b,",
        "        transient_dep5c=transient_dep5c,",
        "        transient_dep5d=transient_dep5d,",
        "        transient_dep5e=transient_dep5e,",
        "        transient_dep6a=transient_dep6a,",
        "        transient_dep6b=transient_dep6b,",
        "        transient_dep6c=transient_dep6c,",
        "        transient_dep6d=transient_dep6d,",
        "        transient_dep6e=transient_dep6e,",
        "        transient_dep6f=transient_dep6f,",
        "        transient_dep7a=transient_dep7a,",
        "        transient_dep7b=transient_dep7b,",
        "        transient_dep7c=transient_dep7c,",
        "        transient_dep7d=transient_dep7d,",
        "        transient_dep7e=transient_dep7e,",
        "        transient_dep7f=transient_dep7f,",
        "        transient_dep7g=transient_dep7g,",
        "        transient_dep8a=transient_dep8a,",
        "        transient_dep8b=transient_dep8b,",
        "        transient_dep8c=transient_dep8c,",
        "        transient_dep8d=transient_dep8d,",
        "        transient_dep8e=transient_dep8e,",
        "        transient_dep8f=transient_dep8f,",
        "        transient_dep8g=transient_dep8g,",
        "        transient_dep8h=transient_dep8h,",
        "        steps=steps,",
        "    ):",
    ]

    for step_index in range(transient_step_count):
        lines.append(f"    t{step_index} = transient_targets[{step_index}]")

    lines.append("    __step_index = 0")
    lines.append("    try:")

    for step_index in range(transient_step_count):
        call_mode = transient_call_modes[step_index]
        call_expression = _build_unrolled_call_expression(
            step_index=step_index,
            call_mode=call_mode,
            transient_dep1=transient_dep1,
            transient_dep2a=transient_dep2a,
            transient_dep2b=transient_dep2b,
            transient_dep3a=transient_dep3a,
            transient_dep3b=transient_dep3b,
            transient_dep3c=transient_dep3c,
            transient_dep4a=transient_dep4a,
            transient_dep4b=transient_dep4b,
            transient_dep4c=transient_dep4c,
            transient_dep4d=transient_dep4d,
            transient_dep5a=transient_dep5a,
            transient_dep5b=transient_dep5b,
            transient_dep5c=transient_dep5c,
            transient_dep5d=transient_dep5d,
            transient_dep5e=transient_dep5e,
            transient_dep6a=transient_dep6a,
            transient_dep6b=transient_dep6b,
            transient_dep6c=transient_dep6c,
            transient_dep6d=transient_dep6d,
            transient_dep6e=transient_dep6e,
            transient_dep6f=transient_dep6f,
            transient_dep7a=transient_dep7a,
            transient_dep7b=transient_dep7b,
            transient_dep7c=transient_dep7c,
            transient_dep7d=transient_dep7d,
            transient_dep7e=transient_dep7e,
            transient_dep7f=transient_dep7f,
            transient_dep7g=transient_dep7g,
            transient_dep8a=transient_dep8a,
            transient_dep8b=transient_dep8b,
            transient_dep8c=transient_dep8c,
            transient_dep8d=transient_dep8d,
            transient_dep8e=transient_dep8e,
            transient_dep8f=transient_dep8f,
            transient_dep8g=transient_dep8g,
            transient_dep8h=transient_dep8h,
        )
        if call_expression is None:
            return None

        lines.append(f"        __step_index = {step_index}")
        lines.append(f"        v{step_index} = {call_expression}")

    lines.extend([
        "    except Exception as exc:",
        "        step_spell = steps[__step_index].spell",
        "        raise MeldExecutionError(",
        "            spell_id=step_spell.spell_index.current,",
        "            spell_name=step_spell.spell_name,",
        "            message=f\"Error invoking spell '{step_spell.spell_name}'.\",",
        "            inner=exc,",
        "        ) from exc",
        f"    return v{transient_root_index}",
    ])
    return "\n".join(lines)


def _build_unrolled_call_expression(
        *,
        step_index: int,
        call_mode: int,
        transient_dep1: list[int],
        transient_dep2a: list[int],
        transient_dep2b: list[int],
        transient_dep3a: list[int],
        transient_dep3b: list[int],
        transient_dep3c: list[int],
        transient_dep4a: list[int],
        transient_dep4b: list[int],
        transient_dep4c: list[int],
        transient_dep4d: list[int],
        transient_dep5a: list[int],
        transient_dep5b: list[int],
        transient_dep5c: list[int],
        transient_dep5d: list[int],
        transient_dep5e: list[int],
        transient_dep6a: list[int],
        transient_dep6b: list[int],
        transient_dep6c: list[int],
        transient_dep6d: list[int],
        transient_dep6e: list[int],
        transient_dep6f: list[int],
        transient_dep7a: list[int],
        transient_dep7b: list[int],
        transient_dep7c: list[int],
        transient_dep7d: list[int],
        transient_dep7e: list[int],
        transient_dep7f: list[int],
        transient_dep7g: list[int],
        transient_dep8a: list[int],
        transient_dep8b: list[int],
        transient_dep8c: list[int],
        transient_dep8d: list[int],
        transient_dep8e: list[int],
        transient_dep8f: list[int],
        transient_dep8g: list[int],
        transient_dep8h: list[int],
) -> Optional[str]:
    """
    Build the direct call expression for one transient step.

    Contract:
        - Returns `None` for unsupported `call_mode` values.
        - Produces expressions that reference prior `v{index}` values.

    Args:
        step_index:
            Index of the step being emitted.
        call_mode:
            Execution plan call mode for this step.
        transient_dep*:
            Precomputed dependency index arrays from the transient plan.

    Returns:
        Optional[str]:
            Unrolled call expression, or `None` when the mode is unsupported.
    """
    if call_mode == ExecutionPlanCallMode.CALL0:
        return f"t{step_index}()"
    if call_mode == ExecutionPlanCallMode.CALL1:
        return f"t{step_index}(v{transient_dep1[step_index]})"
    if call_mode == ExecutionPlanCallMode.CALL2:
        return (
            f"t{step_index}(v{transient_dep2a[step_index]}, "
            f"v{transient_dep2b[step_index]})"
        )
    if call_mode == ExecutionPlanCallMode.CALL3:
        return (
            f"t{step_index}(v{transient_dep3a[step_index]}, "
            f"v{transient_dep3b[step_index]}, "
            f"v{transient_dep3c[step_index]})"
        )
    if call_mode == ExecutionPlanCallMode.CALL4:
        return (
            f"t{step_index}(v{transient_dep4a[step_index]}, "
            f"v{transient_dep4b[step_index]}, "
            f"v{transient_dep4c[step_index]}, "
            f"v{transient_dep4d[step_index]})"
        )
    if call_mode == ExecutionPlanCallMode.CALL5:
        return (
            f"t{step_index}(v{transient_dep5a[step_index]}, "
            f"v{transient_dep5b[step_index]}, "
            f"v{transient_dep5c[step_index]}, "
            f"v{transient_dep5d[step_index]}, "
            f"v{transient_dep5e[step_index]})"
        )
    if call_mode == ExecutionPlanCallMode.CALL6:
        return (
            f"t{step_index}(v{transient_dep6a[step_index]}, "
            f"v{transient_dep6b[step_index]}, "
            f"v{transient_dep6c[step_index]}, "
            f"v{transient_dep6d[step_index]}, "
            f"v{transient_dep6e[step_index]}, "
            f"v{transient_dep6f[step_index]})"
        )
    if call_mode == ExecutionPlanCallMode.CALL7:
        return (
            f"t{step_index}(v{transient_dep7a[step_index]}, "
            f"v{transient_dep7b[step_index]}, "
            f"v{transient_dep7c[step_index]}, "
            f"v{transient_dep7d[step_index]}, "
            f"v{transient_dep7e[step_index]}, "
            f"v{transient_dep7f[step_index]}, "
            f"v{transient_dep7g[step_index]})"
        )
    if call_mode == ExecutionPlanCallMode.CALL8:
        return (
            f"t{step_index}(v{transient_dep8a[step_index]}, "
            f"v{transient_dep8b[step_index]}, "
            f"v{transient_dep8c[step_index]}, "
            f"v{transient_dep8d[step_index]}, "
            f"v{transient_dep8e[step_index]}, "
            f"v{transient_dep8f[step_index]}, "
            f"v{transient_dep8g[step_index]}, "
            f"v{transient_dep8h[step_index]})"
        )
    return None


def _build_executor_namespace(
        *,
        execution_plan: ExecutionPlan,
        transient_plan: Tuple[Any, ...],
) -> Dict[str, Any]:
    """
    Build the globals namespace used for phase12 executor compilation.

    Contract:
        - Exposes all transient arrays and the `steps` list as compile-time
          defaults for `_phase12_executor`.

    Args:
        execution_plan:
            Source plan that provides step metadata for error wrapping.
        transient_plan:
            Tuple payload from `ExecutionPlan.fast_transient_plan`.

    Returns:
        Dict[str, Any]:
            Namespace dictionary passed to `exec`.
    """
    return {
        "MeldExecutionError": MeldExecutionError,
        "transient_root_index": transient_plan[1],
        "transient_targets": transient_plan[2],
        "transient_dep1": transient_plan[4],
        "transient_dep2a": transient_plan[5],
        "transient_dep2b": transient_plan[6],
        "transient_dep3a": transient_plan[7],
        "transient_dep3b": transient_plan[8],
        "transient_dep3c": transient_plan[9],
        "transient_dep4a": transient_plan[10],
        "transient_dep4b": transient_plan[11],
        "transient_dep4c": transient_plan[12],
        "transient_dep4d": transient_plan[13],
        "transient_dep5a": transient_plan[14],
        "transient_dep5b": transient_plan[15],
        "transient_dep5c": transient_plan[16],
        "transient_dep5d": transient_plan[17],
        "transient_dep5e": transient_plan[18],
        "transient_dep6a": transient_plan[19],
        "transient_dep6b": transient_plan[20],
        "transient_dep6c": transient_plan[21],
        "transient_dep6d": transient_plan[22],
        "transient_dep6e": transient_plan[23],
        "transient_dep6f": transient_plan[24],
        "transient_dep7a": transient_plan[25],
        "transient_dep7b": transient_plan[26],
        "transient_dep7c": transient_plan[27],
        "transient_dep7d": transient_plan[28],
        "transient_dep7e": transient_plan[29],
        "transient_dep7f": transient_plan[30],
        "transient_dep7g": transient_plan[31],
        "transient_dep8a": transient_plan[32],
        "transient_dep8b": transient_plan[33],
        "transient_dep8c": transient_plan[34],
        "transient_dep8d": transient_plan[35],
        "transient_dep8e": transient_plan[36],
        "transient_dep8f": transient_plan[37],
        "transient_dep8g": transient_plan[38],
        "transient_dep8h": transient_plan[39],
        "steps": execution_plan.steps,
    }
