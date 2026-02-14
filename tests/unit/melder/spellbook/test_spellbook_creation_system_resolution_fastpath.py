from typing import Any, Callable, Dict, List, Optional, Sequence

import pytest

from melder.spellbook.spellbook_creation_system import SpellbookCreationSystem


class _SchedulerProbe:
    """
    Purpose:
        Provide a minimal scheduler probe for registration/execution testing.
    Contract:
        - Stores registered phase factories in registration order.
        - Executes each registered factory once when requested.
        - Does not require worker threads, UnitOfWork, or queue orchestration.
    Lifecycle:
        - Test-only helper with no cleanup requirements.
    """

    def __init__(self) -> None:
        """
        Purpose:
            Initialize the in-memory factory registry used by this probe.
        Contract:
            - Starts with an empty ordered registration list.
        Returns:
            None.
        """
        self._phase_factories: List[tuple[str, Callable[[], Sequence[Any]]]] = []

    def register_phase(self, name: str, factory: Callable[[], Sequence[Any]]) -> None:
        """
        Purpose:
            Record one phase registration from the tested code path.
        Contract:
            - Preserves registration order.
            - Accepts the same shape as PhaseScheduler.register_phase.
        Args:
            name: Phase name.
            factory: Zero-arg phase factory to execute later.
        Returns:
            None.
        """
        self._phase_factories.append((name, factory))

    def execute_registered_phases(self) -> Dict[str, Sequence[Any]]:
        """
        Purpose:
            Execute registered phase factories in order and collect outputs.
        Contract:
            - Calls each factory exactly once.
            - Returns a name->factory-output mapping.
        Returns:
            Dict[str, Sequence[Any]]: Captured phase outputs.
        """
        results: Dict[str, Sequence[Any]] = {}
        for phase_name, factory in self._phase_factories:
            results[phase_name] = factory()
        return results


class _StubSpellbook:
    """
    Purpose:
        Provide the minimum Spellbook surface required by conduit-resolution tests.
    Contract:
        - Exposes check_cleaned() and tracks invocation count.
    Lifecycle:
        - Test-only helper with no cleanup requirements.
    """

    def __init__(self) -> None:
        """
        Purpose:
            Initialize invocation counters for Spellbook surface probes.
        Contract:
            - Starts with zero check_cleaned invocations.
        Returns:
            None.
        """
        self.check_cleaned_calls = 0

    def check_cleaned(self) -> None:
        """
        Purpose:
            Mirror Spellbook.check_cleaned for tested orchestration paths.
        Contract:
            - Increments invocation count and performs no additional logic.
        Returns:
            None.
        """
        self.check_cleaned_calls += 1


def _install_stub_phase_factories(
    monkeypatch: pytest.MonkeyPatch,
    *,
    calls: Dict[str, int],
    change_control_hook: Optional[Callable[[], None]] = None,
) -> None:
    """
    Purpose:
        Install deterministic phase factory stubs for conduit-resolution tests.
    Contract:
        - Each installed phase factory increments calls[phase_name] once.
        - Each factory returns a single-token sequence tagged by phase name.
        - Optional change_control_hook executes when the change-control factory runs.
    Args:
        monkeypatch: Pytest monkeypatch fixture.
        calls: Mutable call-counter mapping keyed by phase name.
        change_control_hook:
            Optional callback executed only by the change-control phase factory.
    Returns:
        None.
    """

    def _install(method_name: str, phase_name: str) -> None:
        calls.setdefault(phase_name, 0)

        def _factory(_spellbook: Any, _scheduler: Any, _conduit_id: str) -> Sequence[Any]:
            calls[phase_name] = calls.get(phase_name, 0) + 1
            if phase_name == "change_control" and change_control_hook is not None:
                change_control_hook()
            return [phase_name]

        monkeypatch.setattr(
            SpellbookCreationSystem,
            method_name,
            staticmethod(_factory),
        )

    _install("phase_root_blueprints_factory", "root_blueprints")
    _install("phase_system_validation_factory", "system_validation")
    _install("phase_change_control_factory", "change_control")
    _install("phase_occurrence_plan_factory", "occurrence_plan")
    _install("phase_injection_plan_factory", "injection_plan")
    _install("phase_patch_maps_factory", "patch_maps")
    _install("phase_execution_plan_factory", "execution_plan")


def test_run_resolution_phases_for_conduit_uses_one_scheduler_lifecycle(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Verify conduit resolution executes 5-11 within a single scheduler run.
    Contract:
        - run_resolution_phases_for_conduit calls _run_scheduler_with_phases once.
        - Foundational and plan phase factories each execute once when no gate is set.
        - cleanup_phase_artifacts_after_resolution executes once.
    Returns:
        None.
    """
    spellbook = _StubSpellbook()
    scheduler_run_calls = {"count": 0}
    cleanup_calls = {"count": 0}
    phase_calls: Dict[str, int] = {}

    def _fake_run_scheduler_with_phases(
        *,
        spellbook: Any,
        phase_scheduler_cls: Any,
        context_name: str,
        register_phases: Callable[[Any], None],
    ) -> Dict[str, Sequence[Any]]:
        scheduler_run_calls["count"] += 1
        scheduler = _SchedulerProbe()
        register_phases(scheduler)
        return scheduler.execute_registered_phases()

    def _fake_cleanup_phase_artifacts_after_resolution(*, spellbook: Any, spell_ids: Optional[Sequence[str]] = None) -> None:
        cleanup_calls["count"] += 1

    monkeypatch.setattr(
        SpellbookCreationSystem,
        "_run_scheduler_with_phases",
        staticmethod(_fake_run_scheduler_with_phases),
    )
    monkeypatch.setattr(
        SpellbookCreationSystem,
        "_conduit_resolution_has_errors",
        staticmethod(lambda *, spellbook, conduit_id: False),
    )
    monkeypatch.setattr(
        SpellbookCreationSystem,
        "cleanup_phase_artifacts_after_resolution",
        staticmethod(_fake_cleanup_phase_artifacts_after_resolution),
    )
    _install_stub_phase_factories(monkeypatch, calls=phase_calls)

    results = SpellbookCreationSystem.run_resolution_phases_for_conduit(
        spellbook=spellbook,
        conduit_id="cid-1",
    )

    assert spellbook.check_cleaned_calls == 1
    assert scheduler_run_calls["count"] == 1
    assert cleanup_calls["count"] == 1
    assert list(results.keys()) == [
        "root_blueprints",
        "system_validation",
        "change_control",
        "occurrence_plan",
        "injection_plan",
        "patch_maps",
        "execution_plan",
    ]
    assert results["root_blueprints"] == ["root_blueprints"]
    assert results["system_validation"] == ["system_validation"]
    assert results["change_control"] == ["change_control"]
    assert results["occurrence_plan"] == ["occurrence_plan"]
    assert results["injection_plan"] == ["injection_plan"]
    assert results["patch_maps"] == ["patch_maps"]
    assert results["execution_plan"] == ["execution_plan"]
    assert phase_calls == {
        "root_blueprints": 1,
        "system_validation": 1,
        "change_control": 1,
        "occurrence_plan": 1,
        "injection_plan": 1,
        "patch_maps": 1,
        "execution_plan": 1,
    }


def test_run_resolution_phases_for_conduit_skips_plan_group_when_foundational_errors_exist(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Verify plan phase factories are skipped when foundational phases set conduit errors.
    Contract:
        - Foundational factories still execute once.
        - Plan factories do not execute when foundational gate is tripped.
        - Returned results match prior behavior (5-7 only when plan is gated off).
    Returns:
        None.
    """
    spellbook = _StubSpellbook()
    scheduler_run_calls = {"count": 0}
    cleanup_calls = {"count": 0}
    conduit_errors = {"value": False}
    phase_calls: Dict[str, int] = {}

    def _fake_run_scheduler_with_phases(
        *,
        spellbook: Any,
        phase_scheduler_cls: Any,
        context_name: str,
        register_phases: Callable[[Any], None],
    ) -> Dict[str, Sequence[Any]]:
        scheduler_run_calls["count"] += 1
        scheduler = _SchedulerProbe()
        register_phases(scheduler)
        return scheduler.execute_registered_phases()

    def _fake_cleanup_phase_artifacts_after_resolution(*, spellbook: Any, spell_ids: Optional[Sequence[str]] = None) -> None:
        cleanup_calls["count"] += 1

    def _mark_errors() -> None:
        conduit_errors["value"] = True

    monkeypatch.setattr(
        SpellbookCreationSystem,
        "_run_scheduler_with_phases",
        staticmethod(_fake_run_scheduler_with_phases),
    )
    monkeypatch.setattr(
        SpellbookCreationSystem,
        "_conduit_resolution_has_errors",
        staticmethod(lambda *, spellbook, conduit_id: conduit_errors["value"]),
    )
    monkeypatch.setattr(
        SpellbookCreationSystem,
        "cleanup_phase_artifacts_after_resolution",
        staticmethod(_fake_cleanup_phase_artifacts_after_resolution),
    )
    _install_stub_phase_factories(
        monkeypatch,
        calls=phase_calls,
        change_control_hook=_mark_errors,
    )

    results = SpellbookCreationSystem.run_resolution_phases_for_conduit(
        spellbook=spellbook,
        conduit_id="cid-2",
    )

    assert spellbook.check_cleaned_calls == 1
    assert scheduler_run_calls["count"] == 1
    assert cleanup_calls["count"] == 1
    assert list(results.keys()) == [
        "root_blueprints",
        "system_validation",
        "change_control",
    ]
    assert results["root_blueprints"] == ["root_blueprints"]
    assert results["system_validation"] == ["system_validation"]
    assert results["change_control"] == ["change_control"]
    assert phase_calls == {
        "root_blueprints": 1,
        "system_validation": 1,
        "change_control": 1,
        "occurrence_plan": 0,
        "injection_plan": 0,
        "patch_maps": 0,
        "execution_plan": 0,
    }
