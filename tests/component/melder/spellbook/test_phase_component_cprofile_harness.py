import cProfile
import io
import pstats
import time
from typing import Any, Callable, Dict, List, Tuple

import pytest
import tests.component.melder.spellbook.compiler_test_helpers as compiler_test_helpers

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.deep_layers import Depth9Root
from tests.mocks.spellbook.deep_layers import get_depth_9_classes


PROFILE_ENABLE_CPROFILE = True
PROFILE_SORT = "cumtime"
PROFILE_TOP = 30


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_phase_component_profile_harness() -> None:
    """
    Purpose:
        Ensure phase harness component tests run with a clean Aether singleton.
    Contract:
        - Rebinds Spellbook and Conduit to a new Aether instance before each test.
        - Restores a clean singleton after each test.
    Returns:
        None.
    """
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _ms(seconds: float) -> float:
    """
    Purpose:
        Convert seconds to milliseconds.
    Args:
        seconds: Duration in seconds.
    Returns:
        float: Duration in milliseconds.
    """
    return seconds * 1000.0


def _print_profile(label: str, profiler: cProfile.Profile) -> None:
    """
    Purpose:
        Print cProfile stats using the standardized profile header format.
    Contract:
        - Emits `[PROFILE] <label> (sort=<sort>, top=<top>)`.
        - Emits `pstats` output trimmed to `PROFILE_TOP` rows.
    Args:
        label: Display label for the profile block.
        profiler: Completed cProfile profiler instance.
    Returns:
        None.
    """
    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream).strip_dirs().sort_stats(PROFILE_SORT)
    stats.print_stats(PROFILE_TOP)
    print(f"[PROFILE] {label} (sort={PROFILE_SORT}, top={PROFILE_TOP})")
    print(stream.getvalue())


def _profile_call(label: str, fn: Callable[[], None]) -> None:
    """
    Purpose:
        Execute a callable under cProfile and print standardized stats.
    Args:
        label: Display label for output.
        fn: Callable to profile.
    Returns:
        None.
    """
    profiler = cProfile.Profile()
    profiler.runcall(fn)
    _print_profile(label, profiler)


def _make_spellbook(frame_name: str) -> Tuple[Spellbook, str]:
    """
    Purpose:
        Create a deterministic depth-9 spellbook fixture for phase harness runs.
    Contract:
        - Binds all depth-9 classes with `Existence.unique`.
        - Sets `phase_scheduler_workers_per_spellbook` to 1 for deterministic setup.
        - Returns the version id of `Depth9Root` as the default local target spell.
    Args:
        frame_name: Aetheric frame name for this fixture.
    Returns:
        Tuple[Spellbook, str]: `(spellbook, depth9_root_spell_id)`.
    """
    spellbook = Spellbook(aetheric_frame=frame_name)
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    root_spell_id = ""
    for cls in get_depth_9_classes():
        spell_id = spellbook.bind(
            spell=cls,
            existence=Existence.unique,
            permissions="create",
        )
        if cls is Depth9Root:
            root_spell_id = spell_id

    if not root_spell_id:
        raise RuntimeError("Depth9Root spell id was not created.")
    return spellbook, root_spell_id


def _get_local_spells(spellbook: Spellbook) -> List[Any]:
    """
    Purpose:
        Return local spells in deterministic insertion order.
    Args:
        spellbook: Spellbook containing local spell registry.
    Returns:
        List[Any]: Ordered list of local spell objects.
    """
    return list(spellbook._spells.values())


def _get_spell_by_id(spellbook: Spellbook, spell_id: str) -> Any:
    """
    Purpose:
        Resolve a spell object by versioned spell id from the spell_id pool.
    Args:
        spellbook: Spellbook containing `spell_id -> spell` mapping.
        spell_id: Versioned spell id to resolve.
    Returns:
        Any: Resolved spell object.
    Raises:
        KeyError: If `spell_id` is not present.
    """
    return spellbook._spell_id_pool[spell_id]


def _get_crafter(spell: Any) -> Any:
    """
    Purpose:
        Return the spell's current crafter instance, creating one when needed.
    Args:
        spell: Spell instance whose phase artifacts are managed.
    Returns:
        Any: Active SpellCrafter instance.
    """
    return spell._compiler_artifact


def _get_conduit_resolution_has_errors(spellbook: Spellbook, conduit_id: str) -> bool:
    """
    Purpose:
        Read conduit resolution error state for report fields.
    Args:
        spellbook: Spellbook whose SpellSystemStates are inspected.
        conduit_id: Conduit scope id.
    Returns:
        bool: True when the conduit resolution state has errors.
    """
    state = spellbook._spell_system_states.get_conduit_resolution_state(conduit_id)
    return state is not None and state.has_errors()


def _print_metrics(label: str, metrics: Dict[str, Any]) -> None:
    """
    Purpose:
        Print one normalized metrics line for ticket evidence extraction.
    Contract:
        - Uses `[PHASE_PROFILE]` prefix.
        - Emits `key=value` pairs in sorted key order.
    Args:
        label: Logical label for the metrics line.
        metrics: Measured fields for this run.
    Returns:
        None.
    """
    parts = [f"{key}={metrics[key]}" for key in sorted(metrics.keys())]
    print(f"[PHASE_PROFILE] label={label} {' '.join(parts)}")


def _run_group_1_4(spellbook: Spellbook, variant: str) -> Dict[str, Any]:
    """
    Purpose:
        Execute structural phases 1-4 directly for local spells and record timing.
    Contract:
        - `cold_reset` clears phase artifacts before the run.
        - `warm_reuse` reruns without explicit artifact reset.
    Args:
        spellbook: Spellbook fixture to execute against.
        variant: `cold_reset` or `warm_reuse`.
    Returns:
        Dict[str, Any]: Timing/result fields for this group execution.
    """
    local_spells = _get_local_spells(spellbook)
    if variant == "cold_reset":
        for spell in local_spells:
            _get_crafter(spell).cleanup_phase_artifacts()

    phase_requirements_start = time.perf_counter()
    for spell in local_spells:
        compiler_test_helpers.run_phase_requirements(spell)
    phase_requirements_ms = _ms(time.perf_counter() - phase_requirements_start)

    phase_symbolic_graph_start = time.perf_counter()
    for spell in local_spells:
        compiler_test_helpers.run_phase_symbolic_graph(spell)
    phase_symbolic_graph_ms = _ms(time.perf_counter() - phase_symbolic_graph_start)

    phase_local_frame_start = time.perf_counter()
    for spell in local_spells:
        compiler_test_helpers.run_phase_local_frame(spell)
    phase_local_frame_ms = _ms(time.perf_counter() - phase_local_frame_start)

    phase_validation_start = time.perf_counter()
    for spell in local_spells:
        compiler_test_helpers.run_phase_validation(spell)
    phase_validation_ms = _ms(time.perf_counter() - phase_validation_start)

    group_total_ms = (
        phase_requirements_ms
        + phase_symbolic_graph_ms
        + phase_local_frame_ms
        + phase_validation_ms
    )
    broken_count = 0
    for spell in local_spells:
        if spell.is_broken:
            broken_count += 1

    return {
        "variant": variant,
        "spell_count": len(local_spells),
        "phase_requirements_ms": round(phase_requirements_ms, 3),
        "phase_symbolic_graph_ms": round(phase_symbolic_graph_ms, 3),
        "phase_local_frame_ms": round(phase_local_frame_ms, 3),
        "phase_validation_ms": round(phase_validation_ms, 3),
        "group_1_4_total_ms": round(group_total_ms, 3),
        "broken_spell_count": broken_count,
    }


def _run_group_5_7_conduit(
    spellbook: Spellbook,
    conduit_id: str,
    variant: str,
) -> Dict[str, Any]:
    """
    Purpose:
        Execute conduit-wide foundational phases 5-7 through lead-spell direct calls.
    Contract:
        - `cold_phase5_reset` clears phase-5 artifacts before run.
        - `warm_phase5_reuse` reruns without phase-5 reset.
    Args:
        spellbook: Spellbook fixture to execute against.
        conduit_id: Conduit scope id.
        variant: `cold_phase5_reset` or `warm_phase5_reuse`.
    Returns:
        Dict[str, Any]: Timing/result fields for this group execution.
    """
    local_spells = _get_local_spells(spellbook)
    if not local_spells:
        raise RuntimeError("Local spell registry is empty.")

    if variant == "cold_phase5_reset":
        for spell in local_spells:
            _get_crafter(spell).clear_phase5_artifacts()

    lead_spell = local_spells[0]

    phase_root_blueprints_start = time.perf_counter()
    compiler_test_helpers.run_phase_root_blueprints(lead_spell, conduit_id, cancel_event=None)
    phase_root_blueprints_ms = _ms(time.perf_counter() - phase_root_blueprints_start)

    phase_system_validation_start = time.perf_counter()
    compiler_test_helpers.run_phase_system_validation(lead_spell, conduit_id, cancel_event=None)
    phase_system_validation_ms = _ms(time.perf_counter() - phase_system_validation_start)

    phase_change_control_start = time.perf_counter()
    compiler_test_helpers.run_phase_change_control(lead_spell, conduit_id, cancel_event=None)
    phase_change_control_ms = _ms(time.perf_counter() - phase_change_control_start)

    group_total_ms = (
        phase_root_blueprints_ms
        + phase_system_validation_ms
        + phase_change_control_ms
    )
    return {
        "variant": variant,
        "lead_spell_id": lead_spell.spell_id,
        "spell_count": len(local_spells),
        "phase_root_blueprints_ms": round(phase_root_blueprints_ms, 3),
        "phase_system_validation_ms": round(phase_system_validation_ms, 3),
        "phase_change_control_ms": round(phase_change_control_ms, 3),
        "group_5_7_total_ms": round(group_total_ms, 3),
        "resolution_has_errors": _get_conduit_resolution_has_errors(spellbook, conduit_id),
    }


def _run_group_5_7_local(
    spellbook: Spellbook,
    conduit_id: str,
    target_spell_id: str,
) -> Dict[str, Any]:
    """
    Purpose:
        Execute target-local foundational phases 5-7 directly for one target spell.
    Args:
        spellbook: Spellbook fixture to execute against.
        conduit_id: Conduit scope id.
        target_spell_id: Versioned spell id selected as target.
    Returns:
        Dict[str, Any]: Timing/result fields for this local chain.
    """
    target_spell = _get_spell_by_id(spellbook, target_spell_id)

    phase_root_blueprints_local_start = time.perf_counter()
    compiler_test_helpers.run_phase_root_blueprints_local(target_spell, conduit_id, cancel_event=None)
    phase_root_blueprints_local_ms = _ms(
        time.perf_counter() - phase_root_blueprints_local_start
    )

    phase_system_validation_local_start = time.perf_counter()
    compiler_test_helpers.run_phase_system_validation_local(target_spell, conduit_id, cancel_event=None)
    phase_system_validation_local_ms = _ms(
        time.perf_counter() - phase_system_validation_local_start
    )

    phase_change_control_local_start = time.perf_counter()
    compiler_test_helpers.run_phase_change_control_local(target_spell, conduit_id, cancel_event=None)
    phase_change_control_local_ms = _ms(
        time.perf_counter() - phase_change_control_local_start
    )

    group_total_ms = (
        phase_root_blueprints_local_ms
        + phase_system_validation_local_ms
        + phase_change_control_local_ms
    )

    target_artifact = _get_crafter(target_spell)
    scoped_spell_count = 0
    scoped_root_count = 0
    if target_artifact._spell_system_index_phase5 is not None:
        scoped_spell_count = len(target_artifact._spell_system_index_phase5.nodes)
    if target_artifact._entire_dag_blueprint_phase5 is not None:
        scoped_root_count = len(target_artifact._entire_dag_blueprint_phase5)

    return {
        "target_spell_id": target_spell_id,
        "scoped_spell_count": scoped_spell_count,
        "scoped_root_count": scoped_root_count,
        "phase_root_blueprints_local_ms": round(phase_root_blueprints_local_ms, 3),
        "phase_system_validation_local_ms": round(phase_system_validation_local_ms, 3),
        "phase_change_control_local_ms": round(phase_change_control_local_ms, 3),
        "group_5_7_local_total_ms": round(group_total_ms, 3),
        "resolution_has_errors": _get_conduit_resolution_has_errors(spellbook, conduit_id),
    }


def _run_group_8_11(
    spellbook: Spellbook,
    conduit_id: str,
    variant: str,
    metric_spell_id: str,
) -> Dict[str, Any]:
    """
    Purpose:
        Execute conduit plan phases 8-11 via per-spell direct calls and measure totals.
    Contract:
        - `cold_plan_reset` resets phase-5/8-11 artifacts before running.
        - `warm_plan_reuse` reruns without artifact reset.
    Args:
        spellbook: Spellbook fixture to execute against.
        conduit_id: Conduit scope id.
        variant: `cold_plan_reset` or `warm_plan_reuse`.
        metric_spell_id: Spell id used to extract execution-plan metric fields.
    Returns:
        Dict[str, Any]: Timing/result fields for this group execution.
    """
    local_spells = _get_local_spells(spellbook)
    if not local_spells:
        raise RuntimeError("Local spell registry is empty.")

    if variant == "cold_plan_reset":
        for spell in local_spells:
            _get_crafter(spell).clear_phase5_artifacts()
        lead_spell = local_spells[0]
        compiler_test_helpers.run_phase_root_blueprints(lead_spell, conduit_id, cancel_event=None)

    phase_occurrence_plan_start = time.perf_counter()
    for spell in local_spells:
        compiler_test_helpers.run_phase_occurrence_plan(spell)
    phase_occurrence_plan_ms = _ms(time.perf_counter() - phase_occurrence_plan_start)

    phase_injection_plan_start = time.perf_counter()
    for spell in local_spells:
        compiler_test_helpers.run_phase_injection_plan(spell)
    phase_injection_plan_ms = _ms(time.perf_counter() - phase_injection_plan_start)

    phase_patch_maps_start = time.perf_counter()
    for spell in local_spells:
        compiler_test_helpers.run_phase_patch_maps(spell)
    phase_patch_maps_ms = _ms(time.perf_counter() - phase_patch_maps_start)

    phase_execution_plan_start = time.perf_counter()
    for spell in local_spells:
        compiler_test_helpers.run_phase_execution_plan(spell)
    phase_execution_plan_ms = _ms(time.perf_counter() - phase_execution_plan_start)

    metric_spell = _get_spell_by_id(spellbook, metric_spell_id)
    group_total_ms = (
        phase_occurrence_plan_ms
        + phase_injection_plan_ms
        + phase_patch_maps_ms
        + phase_execution_plan_ms
    )
    return {
        "variant": variant,
        "spell_count": len(local_spells),
        "phase_occurrence_plan_ms": round(phase_occurrence_plan_ms, 3),
        "phase_injection_plan_ms": round(phase_injection_plan_ms, 3),
        "phase_patch_maps_ms": round(phase_patch_maps_ms, 3),
        "phase_execution_plan_ms": round(phase_execution_plan_ms, 3),
        "group_8_11_total_ms": round(group_total_ms, 3),
        "resolution_has_errors": _get_conduit_resolution_has_errors(spellbook, conduit_id),
        "execution_plan_step_count": metric_spell.execution_plan_step_count,
        "execution_plan_unique_spell_count": metric_spell.execution_plan_unique_spell_count,
        "execution_plan_max_occurrence_depth": metric_spell.execution_plan_max_occurrence_depth,
        "execution_plan_max_dependency_count": metric_spell.execution_plan_max_dependency_count,
        "execution_plan_dispatch_route": metric_spell.execution_plan_dispatch_route,
    }


def test_component_phase_component_cprofile_harness_baselines() -> None:
    """
    Purpose:
        Produce deterministic phase-group timing/profile outputs for baseline tickets.
    Contract:
        - Uses direct spell-facade phase calls only (no scheduler orchestration calls).
        - Emits standardized `[PHASE_PROFILE]` lines for each phase group/variant.
        - Optionally emits one `[PROFILE]` cProfile block for warm 8-11 execution.
    Returns:
        None.
    Raises:
        AssertionError: If baseline runs do not produce positive group totals.
    """
    spellbook, root_spell_id = _make_spellbook("component-phase-cprofile-harness")
    conduit_id = "component-phase-cprofile-conduit"
    try:
        metrics_1_4_cold = _run_group_1_4(spellbook, "cold_reset")
        metrics_1_4_warm = _run_group_1_4(spellbook, "warm_reuse")
        _print_metrics("group_1_4_cold", metrics_1_4_cold)
        _print_metrics("group_1_4_warm", metrics_1_4_warm)

        metrics_5_7_conduit_cold = _run_group_5_7_conduit(
            spellbook,
            conduit_id,
            "cold_phase5_reset",
        )
        metrics_5_7_conduit_warm = _run_group_5_7_conduit(
            spellbook,
            conduit_id,
            "warm_phase5_reuse",
        )
        _print_metrics("group_5_7_conduit_cold", metrics_5_7_conduit_cold)
        _print_metrics("group_5_7_conduit_warm", metrics_5_7_conduit_warm)

        metrics_5_7_local = _run_group_5_7_local(spellbook, conduit_id, root_spell_id)
        _print_metrics("group_5_7_local", metrics_5_7_local)

        metrics_8_11_cold = _run_group_8_11(
            spellbook,
            conduit_id,
            "cold_plan_reset",
            root_spell_id,
        )
        metrics_8_11_warm = _run_group_8_11(
            spellbook,
            conduit_id,
            "warm_plan_reuse",
            root_spell_id,
        )
        _print_metrics("group_8_11_cold", metrics_8_11_cold)
        _print_metrics("group_8_11_warm", metrics_8_11_warm)

        if PROFILE_ENABLE_CPROFILE:
            _profile_call(
                "group_8_11_warm",
                lambda: _run_group_8_11(
                    spellbook,
                    conduit_id,
                    "warm_plan_reuse",
                    root_spell_id,
                ),
            )

        assert metrics_1_4_cold["group_1_4_total_ms"] > 0
        assert metrics_5_7_conduit_cold["group_5_7_total_ms"] > 0
        assert metrics_5_7_local["group_5_7_local_total_ms"] > 0
        assert metrics_8_11_cold["group_8_11_total_ms"] > 0
    finally:
        spellbook.cleanup()

