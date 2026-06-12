import types
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence

import pytest

from melder.aether.conduit.meld.creation_context.creation_context import (
    CreationContext,
)
from melder.utilities.custom_exceptions.phase_execution_error import PhaseExecutionError
from melder.utilities.custom_exceptions.spellbook_validation_error import (
    SpellbookValidationError,
)
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.aether.spellbook.spell_compiler.spell_compiler_system import (
    SpellCompilerSystem,
)
from melder.aether.spellbook.spellbook_creation_system import SpellbookCreationSystem


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
            - Exposes minimal configuration/logging surfaces required by the
              tested orchestration paths.
        Returns:
            None.
        """
        self.check_cleaned_calls = 0
        self._configuration = _StubConfiguration()
        self._logger = _StubLogger()
        self._spells: Dict[Any, Any] = {}

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


class _StubConfiguration:
    """
    Purpose:
        Provide minimal configuration property access for orchestration tests.
    Contract:
        - Raises KeyError for every property name (tested paths must not
          depend on configuration reads).
    Lifecycle:
        - Test-only helper with no state.
    """

    def get_property(self, name: str) -> Any:
        """
        Purpose:
            Reject configuration property reads in tested orchestration paths.
        Contract:
            - Raises KeyError for every key.
        Args:
            name: Requested property key.
        Raises:
            KeyError: Always.
        """
        raise KeyError(name)


class _StubLogger:
    """
    Purpose:
        Provide minimal logger surface for fallback-path compatibility.
    Contract:
        - Accepts `.error(...)` calls from tested code paths.
        - Stores error invocations for optional assertions.
    Lifecycle:
        - Test-only helper with append-only call log.
    """

    def __init__(self) -> None:
        """
        Purpose:
            Initialize logger call capture storage.
        Contract:
            - Starts with an empty error call list.
        Returns:
            None.
        """
        self.error_calls: List[tuple[Any, ...]] = []

    def error(self, *args: Any, **kwargs: Any) -> None:
        """
        Purpose:
            Capture logger error calls issued by the tested code.
        Contract:
            - Appends call payload for later inspection.
        Args:
            *args: Positional logger arguments.
            **kwargs: Keyword logger arguments.
        Returns:
            None.
        """
        self.error_calls.append(args + (kwargs,))


class _StubCachingSystem:
    """
    Purpose:
        Provide the minimum cache-utility surface for cache-path helper tests.
    Contract:
        - Exposes `cached_spell_ids` as a live key view.
        - Resolves cached spell payloads by spell id.
    Lifecycle:
        - Test-only helper with in-memory payload storage only.
    """

    def __init__(self, payloads_by_spell_id: Optional[Dict[str, Any]] = None) -> None:
        """
        Purpose:
            Initialize the in-memory spell-payload map.
        Contract:
            - Starts with the provided payload mapping or an empty mapping.
        Args:
            payloads_by_spell_id:
                Optional spell-id keyed cache payload mapping.
        Returns:
            None.
        """
        self._payloads_by_spell_id = payloads_by_spell_id or {}

    @property
    def cached_spell_ids(self):
        """
        Return the live spell-id key view.
        """
        return self._payloads_by_spell_id.keys()

    def get_spell_payload(self, spell_id: str) -> Optional[Any]:
        """
        Return one cached spell payload by spell id.
        """
        return self._payloads_by_spell_id.get(spell_id)


class _HookConfiguration:
    """
    Minimal hook/configuration double for hook-map helper tests.
    """

    def __init__(
            self,
            *,
            hook_map: Optional[Mapping[str, List[Callable]]] = None,
            hooks_error: Optional[Exception] = None,
    ) -> None:
        self._hook_map = hook_map
        self._hooks_error = hooks_error

    def get_conduit_hooks(self, owner_id: str) -> Optional[Mapping[str, List[Callable]]]:
        if self._hooks_error is not None:
            raise self._hooks_error
        return self._hook_map


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

        def _factory(
                _spellbook: Any,
                _scheduler: Any,
                _compiler_system: Any,
                _conduit_id: str,
        ) -> Sequence[Any]:
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
    # The fused plan_group factory replaced the four separate plan-phase
    # registrations (8-11 now run fused per spell). The historical per-phase
    # factories still exist as public surfaces but are no longer registered.
    _install("phase_plan_group_factory", "plan_group")


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
        "plan_group",
    ]
    assert results["root_blueprints"] == ["root_blueprints"]
    assert results["system_validation"] == ["system_validation"]
    assert results["change_control"] == ["change_control"]
    assert results["plan_group"] == ["plan_group"]
    assert phase_calls == {
        "root_blueprints": 1,
        "system_validation": 1,
        "change_control": 1,
        "plan_group": 1,
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
        "plan_group": 0,
    }


def test_run_resolution_phases_for_conduit_skips_plan_group_when_force_skip_is_set(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Verify the cache full-hit path skips conduit plan phases.
    Contract:
        - Foundational factories still execute once.
        - Plan factories do not execute when `force_skip_plan_phases=True`
          (phases 8-11 hydrate from the cache bundle instead).
        - Returned results include only foundational phase outputs.
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

    def _fake_cleanup_phase_artifacts_after_resolution(
        *,
        spellbook: Any,
        spell_ids: Optional[Sequence[str]] = None,
    ) -> None:
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
        conduit_id="cid-cache-full-hit",
        force_skip_plan_phases=True,
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
        "plan_group": 0,
    }


def test_creation_system_cleanup_is_idempotent_and_clears_fields() -> None:
    system = SpellbookCreationSystem(
        spellbook=object(),
        policy="default",
        dynamic=False,
        name="root",
        conduit_logger=object(),
        phase_scheduler_cls=object,
    )

    system.cleanup()
    system.cleanup()

    assert system.cleaned is True
    assert not hasattr(system, "_spellbook")
    assert not hasattr(system, "_policy")
    assert not hasattr(system, "_dynamic")
    assert system._lock is not None


def test_creation_system_cleanup_rechecks_cleaned_state_under_lock() -> None:
    class _FlipCleanedOnEnter:
        def __init__(self, owner) -> None:
            self._owner = owner

        def __enter__(self):
            self._owner._cleaned = True
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    system = SpellbookCreationSystem(
        spellbook=object(),
        policy="default",
        dynamic=False,
        name="root",
        conduit_logger=object(),
        phase_scheduler_cls=object,
    )
    original_lock = system._lock
    system._lock = _FlipCleanedOnEnter(system)
    try:
        system.cleanup()
    finally:
        system._lock = original_lock

    assert system.cleaned is True


def test_get_conjure_hook_map_and_fire_conjure_hooks_cover_fallbacks() -> None:
    spellbook = _StubSpellbook()
    spellbook._id = "spellbook-id"

    assert SpellbookCreationSystem.get_conjure_hook_map(spellbook) is None

    spellbook._configuration = _HookConfiguration(hooks_error=RuntimeError("boom"))
    assert SpellbookCreationSystem.get_conjure_hook_map(spellbook) is None
    assert len(spellbook._logger.error_calls) >= 1

    hook_calls: List[tuple[str, tuple[Any, ...]]] = []

    def _ok_hook(*args: Any) -> None:
        hook_calls.append(("ok", args))

    def _bad_hook(*args: Any) -> None:
        hook_calls.append(("bad", args))
        raise RuntimeError("hook boom")

    hook_map = {"on_conduit_pre_created": [_ok_hook, _bad_hook]}
    spellbook._configuration = _HookConfiguration(hook_map=hook_map)

    resolved = SpellbookCreationSystem.get_conjure_hook_map(spellbook)
    assert resolved is hook_map

    SpellbookCreationSystem.fire_conjure_hooks(
        spellbook,
        resolved,
        "on_conduit_pre_created",
        "arg1",
    )
    SpellbookCreationSystem.fire_conjure_hooks(spellbook, None, "missing")
    SpellbookCreationSystem.fire_conjure_hooks(spellbook, resolved, "missing")

    assert hook_calls == [
        ("ok", ("arg1",)),
        ("bad", ("arg1",)),
    ]
    assert len(spellbook._logger.error_calls) >= 2


def test_extract_missing_dependency_ids_filters_non_keyerrors() -> None:
    phase_error = PhaseExecutionError(
        "phase failed",
        errors=[KeyError("a"), RuntimeError("boom"), KeyError("b"), KeyError()],
    )

    assert SpellbookCreationSystem._extract_missing_dependency_ids(phase_error) == [
        "a",
        "b",
    ]


def test_cleanup_phase_artifacts_after_resolution_cleans_all_and_scoped_spells(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    spellbook = _StubSpellbook()

    class _Spell:
        def __init__(self, fail: bool = False) -> None:
            self.cleanup_calls = 0
            self._fail = fail

    def _fake_cleanup_phase_artifacts(self, spell) -> None:
        spell.cleanup_calls += 1
        if spell._fail:
            raise RuntimeError("cleanup boom")

    monkeypatch.setattr(
        SpellCompilerSystem,
        "cleanup_phase_artifacts",
        _fake_cleanup_phase_artifacts,
    )

    all_spell = _Spell()
    failing_spell = _Spell(fail=True)
    scoped_spell = _Spell()
    scoped_failing_spell = _Spell(fail=True)
    spellbook._spells = {"a": all_spell, "b": failing_spell}
    spellbook._spell_id_pool = {"c": scoped_spell, "d": scoped_failing_spell}

    SpellbookCreationSystem.cleanup_phase_artifacts_after_resolution(spellbook)
    SpellbookCreationSystem.cleanup_phase_artifacts_after_resolution(
        spellbook,
        spell_ids=["c", "d", "missing"],
    )

    assert spellbook.check_cleaned_calls == 2
    assert all_spell.cleanup_calls == 1
    assert failing_spell.cleanup_calls == 1
    assert scoped_spell.cleanup_calls == 1
    assert scoped_failing_spell.cleanup_calls == 1


def test_prepare_spellbook_for_conjure_runs_structural_phases_without_disposal_rewrite(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    spellbook = types.SimpleNamespace(
        is_configuration_locked=lambda: True,
        _spells={
            "a": types.SimpleNamespace(
                disposal_method_names=frozenset({"cleanup"}),
                has_disposal_methods=True,
            )
        },
    )
    calls: List[tuple[Any, Any]] = []

    monkeypatch.setattr(
        SpellbookCreationSystem,
        "run_structural_phases",
        staticmethod(
            lambda *, spellbook, phase_scheduler_cls: calls.append(
                (spellbook, phase_scheduler_cls)
            )
        ),
    )

    SpellbookCreationSystem._prepare_spellbook_for_conjure(
        spellbook=spellbook,
        phase_scheduler_cls=_SchedulerProbe,
    )

    assert calls == [(spellbook, _SchedulerProbe)]
    assert spellbook._spells["a"].disposal_method_names == frozenset({"cleanup"})
    assert spellbook._spells["a"].has_disposal_methods is True


def test_run_resolution_phases_rejects_empty_conduit_id() -> None:
    spellbook = _StubSpellbook()

    with pytest.raises(ValueError, match="conduit_id must not be empty."):
        SpellbookCreationSystem.run_resolution_phases(spellbook, conduit_id="")

    with pytest.raises(ValueError, match="conduit_id must not be empty."):
        SpellbookCreationSystem.run_resolution_phases_for_conduit(
            spellbook=spellbook,
            conduit_id="",
        )


def test_run_post_conjure_structural_phases_handles_empty_and_failure_cleanup(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    spellbook = _StubSpellbook()
    cleanup_calls = {"count": 0}
    cancel_calls = {"count": 0}

    class _Signal:
        def __init__(self):
            self.event = object()

        def cancel(self):
            cancel_calls["count"] += 1

        def cleanup(self):
            cleanup_calls["count"] += 1

    monkeypatch.setattr(
        "melder.aether.spellbook.spellbook_creation_system.CancellationEventSignal",
        _Signal,
    )
    monkeypatch.setattr(
        SpellCompilerSystem,
        "run_structural_phases",
        lambda self, spellbook, spell, cancel_event=None: spell.run_structural_phases(
            cancel_event=cancel_event
        ),
    )

    SpellbookCreationSystem.run_post_conjure_structural_phases(spellbook, [])
    assert spellbook.check_cleaned_calls == 1

    failing_spell = types.SimpleNamespace(
        run_structural_phases=lambda cancel_event=None: (_ for _ in ()).throw(
            RuntimeError("boom")
        ),
    )

    with pytest.raises(RuntimeError, match="boom"):
        SpellbookCreationSystem.run_post_conjure_structural_phases(
            spellbook,
            [failing_spell],
        )

    assert cancel_calls["count"] == 1
    assert cleanup_calls["count"] == 1
    assert len(spellbook._logger.error_calls) >= 1


def test_run_post_conjure_structural_phases_logs_broken_spell_cleanup_fallbacks(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    spellbook = _StubSpellbook()
    cancel_calls = {"count": 0}
    cleanup_calls = {"count": 0}

    class _Signal:
        def __init__(self):
            self.event = object()

        def cancel(self):
            cancel_calls["count"] += 1
            raise RuntimeError("cancel boom")

        def cleanup(self):
            cleanup_calls["count"] += 1
            raise RuntimeError("cleanup boom")

    monkeypatch.setattr(
        "melder.aether.spellbook.spellbook_creation_system.CancellationEventSignal",
        _Signal,
    )
    monkeypatch.setattr(
        SpellCompilerSystem,
        "run_structural_phases",
        lambda self, spellbook, spell, cancel_event=None: spell.run_structural_phases(
            cancel_event=cancel_event
        ),
    )
    monkeypatch.setattr(
        SpellbookCreationSystem,
        "_collect_broken_spells",
        staticmethod(lambda spells: [object()]),
    )
    monkeypatch.setattr(
        SpellbookCreationSystem,
        "_raise_structural_validation_error",
        staticmethod(
            lambda **kwargs: (_ for _ in ()).throw(RuntimeError("validation boom"))
        ),
    )

    healthy_spell = types.SimpleNamespace(
        run_structural_phases=lambda cancel_event=None: None,
    )

    with pytest.raises(RuntimeError, match="validation boom"):
        SpellbookCreationSystem.run_post_conjure_structural_phases(
            spellbook,
            [healthy_spell],
        )

    assert cancel_calls["count"] == 1
    assert cleanup_calls["count"] == 1
    assert len(spellbook._logger.error_calls) >= 2


def test_collect_target_resolution_scope_uses_index_and_root_blueprint_fallbacks() -> None:
    target_spell = types.SimpleNamespace(
        _compiler_artifact=types.SimpleNamespace(
            _spell_system_index_phase5=types.SimpleNamespace(
                nodes={
                    "spell-1": object(),
                    "extra": object(),
                },
            ),
            _entire_dag_blueprint_phase5=None,
        ),
    )

    scoped_spell_ids, scoped_root_ids = (
        SpellbookCreationSystem._collect_target_resolution_scope(
            target_spell=target_spell,
            target_spell_id="spell-1",
        )
    )

    assert scoped_spell_ids == {"spell-1", "extra"}
    assert scoped_root_ids == ("spell-1",)


def test_collect_target_resolution_scope_uses_root_blueprint_keys_when_present() -> None:
    target_spell = types.SimpleNamespace(
        _compiler_artifact=types.SimpleNamespace(
            _spell_system_index_phase5=types.SimpleNamespace(
                nodes={"spell-1": object()},
            ),
            _entire_dag_blueprint_phase5={
                "root-a": object(),
                "root-b": object(),
            },
        ),
    )

    scoped_spell_ids, scoped_root_ids = (
        SpellbookCreationSystem._collect_target_resolution_scope(
            target_spell=target_spell,
            target_spell_id="spell-1",
        )
    )

    assert scoped_spell_ids == {"spell-1"}
    assert tuple(scoped_root_ids) == ("root-a", "root-b")


def test_register_target_single_phase_builds_local_scope_unit() -> None:
    created_units = []

    class _Scheduler:
        cancel_event = "cancel"

        def __init__(self):
            self.factories = {}

        def create_unit_of_work(self, **kwargs):
            created_units.append(kwargs)
            return kwargs

        def register_phase(self, name, factory):
            self.factories[name] = factory

    scheduler = _Scheduler()
    phase_calls = []

    def _phase(conduit_id, cancel_event):
        phase_calls.append((conduit_id, cancel_event))

    SpellbookCreationSystem._register_target_single_phase(
        scheduler=scheduler,
        phase_name="local_phase",
        target_spell_id="spell-1",
        phase_func=_phase,
        args=("cid", "cancel"),
    )

    units = scheduler.factories["local_phase"]()

    assert len(units) == 1
    assert created_units[0]["func"] is _phase
    assert created_units[0]["args"] == ("cid", "cancel")
    assert created_units[0]["label"] == "local_phase:spell-1"
    assert created_units[0]["metadata"] == {
        "phase": "local_phase",
        "spell_id": "spell-1",
        "scope": "local",
    }
    assert phase_calls == []


def test_run_resolution_phases_for_target_spell_foundational_error_raises_validation_error(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Gated foundational resolution must surface as SpellbookValidationError.

    Regression contract: the old silent return left callers marking the spell
    resolution-complete with no phase-11 creation built, so meld failed deep
    in the context builder with an opaque RuntimeError. The gate now raises
    the same validation contract as the conduit-wide path, after cleaning the
    scoped phase artifacts.
    """
    spellbook = _StubSpellbook()
    cleanup_calls = []

    monkeypatch.setattr(
        SpellbookCreationSystem,
        "_run_target_foundational_resolution_phases",
        staticmethod(lambda **kwargs: {"root_blueprints_local": ["rb"]}),
    )
    monkeypatch.setattr(
        SpellbookCreationSystem,
        "_conduit_resolution_has_errors",
        staticmethod(lambda **kwargs: True),
    )
    monkeypatch.setattr(
        SpellbookCreationSystem,
        "cleanup_phase_artifacts_after_resolution",
        staticmethod(lambda *, spellbook, spell_ids=None: cleanup_calls.append(set(spell_ids))),
    )

    with pytest.raises(SpellbookValidationError):
        SpellbookCreationSystem.run_resolution_phases_for_target_spell(
            spellbook=spellbook,
            conduit_id="cid",
            target_spell=types.SimpleNamespace(spell_id="spell-1"),
        )

    assert cleanup_calls == [{"spell-1"}]


def test_run_resolution_phases_for_target_spell_records_visibility_failures(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    spellbook = _StubSpellbook()
    recorded = []
    cleanup_calls = []

    monkeypatch.setattr(
        SpellbookCreationSystem,
        "_run_target_foundational_resolution_phases",
        staticmethod(lambda **kwargs: {"root_blueprints_local": ["rb"]}),
    )
    monkeypatch.setattr(
        SpellbookCreationSystem,
        "_conduit_resolution_has_errors",
        staticmethod(lambda **kwargs: False),
    )
    monkeypatch.setattr(
        SpellbookCreationSystem,
        "_collect_target_resolution_scope",
        staticmethod(lambda **kwargs: ({"spell-1", "dep-spell"}, ("root-1",))),
    )
    monkeypatch.setattr(
        SpellbookCreationSystem,
        "_run_target_plan_resolution_phases",
        staticmethod(
            lambda **kwargs: (_ for _ in ()).throw(
                PhaseExecutionError("phase failed", errors=[KeyError("missing-dep")])
            )
        ),
    )
    monkeypatch.setattr(
        SpellbookCreationSystem,
        "record_local_resolution_visibility_failure",
        staticmethod(lambda **kwargs: recorded.append(kwargs)),
    )
    monkeypatch.setattr(
        SpellbookCreationSystem,
        "cleanup_phase_artifacts_after_resolution",
        staticmethod(lambda *, spellbook, spell_ids=None: cleanup_calls.append(set(spell_ids))),
    )

    result = SpellbookCreationSystem.run_resolution_phases_for_target_spell(
        spellbook=spellbook,
        conduit_id="cid",
        target_spell=types.SimpleNamespace(spell_id="spell-1"),
    )

    assert result == {"root_blueprints_local": ["rb"]}
    assert recorded[0]["missing_dependency_ids"] == ["missing-dep"]
    assert recorded[0]["scoped_spell_ids"] == {"spell-1", "dep-spell"}
    assert cleanup_calls == [{"spell-1", "dep-spell"}]


def test_run_deferred_resolution_phases_for_target_spell_handles_missing_dependency_visibility(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    spellbook = _StubSpellbook()
    recorded = []
    cleanup_calls = []

    monkeypatch.setattr(
        SpellbookCreationSystem,
        "_collect_target_resolution_scope",
        staticmethod(lambda **kwargs: ({"spell-1"}, ("root-1",))),
    )
    monkeypatch.setattr(
        SpellbookCreationSystem,
        "_run_target_plan_resolution_phases",
        staticmethod(
            lambda **kwargs: (_ for _ in ()).throw(
                PhaseExecutionError("phase failed", errors=[KeyError("missing-dep")])
            )
        ),
    )
    monkeypatch.setattr(
        SpellbookCreationSystem,
        "record_local_resolution_visibility_failure",
        staticmethod(lambda **kwargs: recorded.append(kwargs)),
    )
    monkeypatch.setattr(
        SpellbookCreationSystem,
        "cleanup_phase_artifacts_after_resolution",
        staticmethod(lambda *, spellbook, spell_ids=None: cleanup_calls.append(set(spell_ids))),
    )

    result = SpellbookCreationSystem.run_deferred_resolution_phases_for_target_spell(
        spellbook=spellbook,
        conduit_id="cid",
        target_spell=types.SimpleNamespace(spell_id="spell-1"),
    )

    assert result == {}
    assert recorded[0]["missing_dependency_ids"] == ["missing-dep"]
    assert cleanup_calls == [{"spell-1"}]


def test_record_local_resolution_visibility_failure_deduplicates_and_marks_invalid() -> None:
    bulk_spell_calls = []
    bulk_root_calls = []
    diagnostic_calls = []
    spellbook = _StubSpellbook()
    spellbook._spell_system_states = types.SimpleNamespace(
        bulk_set_conduit_spell_validity=lambda conduit_id, payload, change_reason=None: bulk_spell_calls.append(
            (conduit_id, payload, change_reason)
        ),
        bulk_set_conduit_root_validity=lambda conduit_id, payload, change_reason=None: bulk_root_calls.append(
            (conduit_id, payload, change_reason)
        ),
        record_conduit_diagnostics=lambda conduit_id, diagnostics: diagnostic_calls.append(
            (conduit_id, diagnostics)
        ),
    )

    SpellbookCreationSystem.record_local_resolution_visibility_failure(
        spellbook,
        "cid",
        {"spell-1", "spell-2"},
        ("root-1",),
        ["dep-a", "dep-a", "dep-b"],
    )

    assert bulk_spell_calls[0][0] == "cid"
    assert set(bulk_spell_calls[0][1].keys()) == {"spell-1", "spell-2"}
    assert bulk_root_calls[0][1] == {"root-1": SpellValidity.invalid}
    diagnostics = diagnostic_calls[0][1]
    assert len(diagnostics) == 2
    assert {diagnostic.spell_id for diagnostic in diagnostics} == {"dep-a", "dep-b"}


def test_run_resolution_target_paths_reject_empty_conduit_and_none_target() -> None:
    spellbook = _StubSpellbook()

    with pytest.raises(ValueError, match="conduit_id must not be empty."):
        SpellbookCreationSystem.run_resolution_phases_for_target_spell(
            spellbook=spellbook,
            conduit_id="",
            target_spell=object(),
        )
    with pytest.raises(ValueError, match="target_spell must not be None."):
        SpellbookCreationSystem.run_resolution_phases_for_target_spell(
            spellbook=spellbook,
            conduit_id="cid",
            target_spell=None,
        )
    with pytest.raises(ValueError, match="conduit_id must not be empty."):
        SpellbookCreationSystem.run_deferred_resolution_phases_for_target_spell(
            spellbook=spellbook,
            conduit_id="",
            target_spell=object(),
        )
    with pytest.raises(ValueError, match="target_spell must not be None."):
        SpellbookCreationSystem.run_deferred_resolution_phases_for_target_spell(
            spellbook=spellbook,
            conduit_id="cid",
            target_spell=None,
        )


def test_run_target_foundational_and_plan_resolution_phase_wrappers_register_expected_phases(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    recorded_scheduler_runs = []

    def _fake_run_scheduler_with_phases(
            *,
            spellbook: Any,
            phase_scheduler_cls: Any,
            context_name: str,
            register_phases: Callable[[Any], None],
    ) -> Dict[str, Sequence[Any]]:
        scheduler = _SchedulerProbe()
        scheduler.cancel_event = "cancel"
        scheduler.create_unit_of_work = lambda **kwargs: kwargs
        register_phases(scheduler)
        recorded_scheduler_runs.append((context_name, list(scheduler._phase_factories)))
        return scheduler.execute_registered_phases()

    monkeypatch.setattr(
        SpellbookCreationSystem,
        "_run_scheduler_with_phases",
        staticmethod(_fake_run_scheduler_with_phases),
    )

    target_spell = types.SimpleNamespace(
        is_existing_creation=False,
        _compiler_artifact=types.SimpleNamespace(_root_blueprint_phase5=object()),
        run_phase_root_blueprints_local=lambda conduit_id, cancel_event: None,
        run_phase_system_validation_local=lambda conduit_id, cancel_event: None,
        run_phase_change_control_local=lambda conduit_id, cancel_event: None,
        run_phase_occurrence_plan=lambda conduit_id, cancel_event: None,
        run_phase_injection_plan=lambda conduit_id, cancel_event: None,
        run_phase_patch_maps=lambda conduit_id, cancel_event: None,
        run_phase_execution_plan=lambda conduit_id, cancel_event: None,
    )

    foundational = SpellbookCreationSystem._run_target_foundational_resolution_phases(
        spellbook=_StubSpellbook(),
        conduit_id="cid",
        target_spell=target_spell,
        target_spell_id="spell-1",
        phase_scheduler_cls=object,
    )
    plan = SpellbookCreationSystem._run_target_plan_resolution_phases(
        spellbook=_StubSpellbook(),
        conduit_id="cid",
        target_spell=target_spell,
        target_spell_id="spell-1",
        phase_scheduler_cls=object,
    )

    assert list(foundational.keys()) == [
        "root_blueprints_local",
        "system_validation_local",
        "change_control_local",
    ]
    assert list(plan.keys()) == [
        "occurrence_plan_local",
        "injection_plan_local",
        "patch_maps_local",
        "execution_plan_local",
    ]
    assert recorded_scheduler_runs[0][0] == "_run_resolution_phases_for_target_spell"
    assert recorded_scheduler_runs[1][0] == "_run_resolution_phases_for_target_spell"


def test_run_conduit_foundational_and_plan_resolution_phase_wrappers_register_expected_phases(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    recorded_scheduler_runs = []

    def _fake_run_scheduler_with_phases(
            *,
            spellbook: Any,
            phase_scheduler_cls: Any,
            context_name: str,
            register_phases: Callable[[Any], None],
    ) -> Dict[str, Sequence[Any]]:
        scheduler = _SchedulerProbe()
        register_phases(scheduler)
        recorded_scheduler_runs.append((context_name, list(scheduler._phase_factories)))
        return scheduler.execute_registered_phases()

    monkeypatch.setattr(
        SpellbookCreationSystem,
        "_run_scheduler_with_phases",
        staticmethod(_fake_run_scheduler_with_phases),
    )
    monkeypatch.setattr(
        SpellbookCreationSystem,
        "phase_root_blueprints_factory",
        staticmethod(lambda spellbook, scheduler, compiler_system, conduit_id: ["root_blueprints"]),
    )
    monkeypatch.setattr(
        SpellbookCreationSystem,
        "phase_system_validation_factory",
        staticmethod(lambda spellbook, scheduler, compiler_system, conduit_id: ["system_validation"]),
    )
    monkeypatch.setattr(
        SpellbookCreationSystem,
        "phase_change_control_factory",
        staticmethod(lambda spellbook, scheduler, compiler_system, conduit_id: ["change_control"]),
    )
    # The fused plan_group factory replaced the four separate plan-phase
    # registrations (phases 8-11 run fused per spell).
    monkeypatch.setattr(
        SpellbookCreationSystem,
        "phase_plan_group_factory",
        staticmethod(lambda spellbook, scheduler, compiler_system, conduit_id: ["plan_group"]),
    )
    foundational = SpellbookCreationSystem._run_conduit_foundational_resolution_phases(
        spellbook=_StubSpellbook(),
        conduit_id="cid",
        phase_scheduler_cls=object,
    )
    plan = SpellbookCreationSystem._run_conduit_plan_resolution_phases(
        spellbook=_StubSpellbook(),
        conduit_id="cid",
        phase_scheduler_cls=object,
    )

    assert set(foundational.keys()) >= {
        "root_blueprints",
        "system_validation",
        "change_control",
    }
    assert set(plan.keys()) >= {"plan_group"}
    assert recorded_scheduler_runs[0][0] == "_run_resolution_phases_for_conduit"
    assert recorded_scheduler_runs[1][0] == "_run_resolution_phases_for_conduit"


def test_run_conduit_foundational_and_plan_resolution_phase_wrappers_register_expected_phases(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    recorded_scheduler_runs = []

    def _fake_run_scheduler_with_phases(
            *,
            spellbook: Any,
            phase_scheduler_cls: Any,
            context_name: str,
            register_phases: Callable[[Any], None],
    ) -> Dict[str, Sequence[Any]]:
        scheduler = _SchedulerProbe()
        register_phases(scheduler)
        recorded_scheduler_runs.append((context_name, list(scheduler._phase_factories)))
        return scheduler.execute_registered_phases()

    monkeypatch.setattr(
        SpellbookCreationSystem,
        "_run_scheduler_with_phases",
        staticmethod(_fake_run_scheduler_with_phases),
    )
    monkeypatch.setattr(
        SpellbookCreationSystem,
        "phase_root_blueprints_factory",
        staticmethod(lambda spellbook, scheduler, compiler_system, conduit_id: ["root_blueprints"]),
    )
    monkeypatch.setattr(
        SpellbookCreationSystem,
        "phase_system_validation_factory",
        staticmethod(lambda spellbook, scheduler, compiler_system, conduit_id: ["system_validation"]),
    )
    monkeypatch.setattr(
        SpellbookCreationSystem,
        "phase_change_control_factory",
        staticmethod(lambda spellbook, scheduler, compiler_system, conduit_id: ["change_control"]),
    )
    # The fused plan_group factory replaced the four separate plan-phase
    # registrations (phases 8-11 run fused per spell).
    monkeypatch.setattr(
        SpellbookCreationSystem,
        "phase_plan_group_factory",
        staticmethod(lambda spellbook, scheduler, compiler_system, conduit_id: ["plan_group"]),
    )

    foundational = SpellbookCreationSystem._run_conduit_foundational_resolution_phases(
        spellbook=_StubSpellbook(),
        conduit_id="cid",
        phase_scheduler_cls=object,
    )
    plan = SpellbookCreationSystem._run_conduit_plan_resolution_phases(
        spellbook=_StubSpellbook(),
        conduit_id="cid",
        phase_scheduler_cls=object,
    )

    assert set(foundational.keys()) >= {
        "root_blueprints",
        "system_validation",
        "change_control",
    }
    assert set(plan.keys()) >= {"plan_group"}
    assert recorded_scheduler_runs[0][0] == "_run_resolution_phases_for_conduit"
    assert recorded_scheduler_runs[1][0] == "_run_resolution_phases_for_conduit"


def test_run_resolution_phases_for_target_spell_success_and_non_visibility_reraise(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    spellbook = _StubSpellbook()
    cleanup_calls = []

    monkeypatch.setattr(
        SpellbookCreationSystem,
        "_run_target_foundational_resolution_phases",
        staticmethod(lambda **kwargs: {"root_blueprints_local": ["rb"]}),
    )
    monkeypatch.setattr(
        SpellbookCreationSystem,
        "_conduit_resolution_has_errors",
        staticmethod(lambda **kwargs: False),
    )
    monkeypatch.setattr(
        SpellbookCreationSystem,
        "_collect_target_resolution_scope",
        staticmethod(lambda **kwargs: ({"spell-1", "dep-spell"}, ("root-1",))),
    )
    monkeypatch.setattr(
        SpellbookCreationSystem,
        "_run_target_plan_resolution_phases",
        staticmethod(lambda **kwargs: {"occurrence_plan_local": ["op"]}),
    )
    monkeypatch.setattr(
        SpellbookCreationSystem,
        "cleanup_phase_artifacts_after_resolution",
        staticmethod(lambda *, spellbook, spell_ids=None: cleanup_calls.append(set(spell_ids))),
    )

    result = SpellbookCreationSystem.run_resolution_phases_for_target_spell(
        spellbook=spellbook,
        conduit_id="cid",
        target_spell=types.SimpleNamespace(spell_id="spell-1"),
    )

    assert result == {
        "root_blueprints_local": ["rb"],
        "occurrence_plan_local": ["op"],
    }
    assert cleanup_calls == [{"spell-1", "dep-spell"}]

    monkeypatch.setattr(
        SpellbookCreationSystem,
        "_run_target_plan_resolution_phases",
        staticmethod(
            lambda **kwargs: (_ for _ in ()).throw(
                PhaseExecutionError("phase failed", errors=[RuntimeError("boom")])
            )
        ),
    )

    with pytest.raises(PhaseExecutionError, match="phase failed"):
        SpellbookCreationSystem.run_resolution_phases_for_target_spell(
            spellbook=spellbook,
            conduit_id="cid",
            target_spell=types.SimpleNamespace(spell_id="spell-1"),
        )


def test_run_deferred_resolution_phases_for_target_spell_success_and_non_visibility_reraise(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    spellbook = _StubSpellbook()
    cleanup_calls = []

    monkeypatch.setattr(
        SpellbookCreationSystem,
        "_collect_target_resolution_scope",
        staticmethod(lambda **kwargs: ({"spell-1"}, ("root-1",))),
    )
    monkeypatch.setattr(
        SpellbookCreationSystem,
        "_run_target_plan_resolution_phases",
        staticmethod(lambda **kwargs: {"occurrence_plan_local": ["op"]}),
    )
    monkeypatch.setattr(
        SpellbookCreationSystem,
        "cleanup_phase_artifacts_after_resolution",
        staticmethod(lambda *, spellbook, spell_ids=None: cleanup_calls.append(set(spell_ids))),
    )

    result = SpellbookCreationSystem.run_deferred_resolution_phases_for_target_spell(
        spellbook=spellbook,
        conduit_id="cid",
        target_spell=types.SimpleNamespace(spell_id="spell-1"),
    )

    assert result == {"occurrence_plan_local": ["op"]}
    assert cleanup_calls == [{"spell-1"}]

    monkeypatch.setattr(
        SpellbookCreationSystem,
        "_run_target_plan_resolution_phases",
        staticmethod(
            lambda **kwargs: (_ for _ in ()).throw(
                PhaseExecutionError("phase failed", errors=[RuntimeError("boom")])
            )
        ),
    )

    with pytest.raises(PhaseExecutionError, match="phase failed"):
        SpellbookCreationSystem.run_deferred_resolution_phases_for_target_spell(
            spellbook=spellbook,
            conduit_id="cid",
            target_spell=types.SimpleNamespace(spell_id="spell-1"),
        )


def test_build_conjure_cache_state_reports_disabled_path() -> None:
    """
    Verify disabled Spellbook cache posture returns the disabled cache path.

    Returns:
        None.
    """
    spellbook = types.SimpleNamespace(
        _spell_id_pool={"spell-a": types.SimpleNamespace(is_existing_creation=False)},
        _system_caching_enabled_in_aether=lambda: False,
    )

    cache_state = SpellbookCreationSystem._build_conjure_cache_state(
        spellbook=spellbook,
        dynamic=True,
    )

    assert cache_state["caching_enabled"] is False
    assert cache_state["dynamic_mode"] is True
    assert cache_state["automatic_mode"] is False
    assert cache_state["cache_path"] == "disabled"
    assert cache_state["caching_system"] is None
    assert cache_state["live_spell_ids"] == {"spell-a"}
    assert cache_state["cached_spell_ids"] == set()


def test_build_conjure_cache_state_reports_full_hit_path() -> None:
    """
    Verify live spell-id subset coverage is classified as a full cache hit.

    Returns:
        None.
    """
    caching_system = _StubCachingSystem(
        {
            "spell-a": {"spell_id": "spell-a"},
            "spell-b": {"spell_id": "spell-b"},
        }
    )
    spellbook = types.SimpleNamespace(
        _spell_id_pool={
            "spell-a": types.SimpleNamespace(is_existing_creation=False),
            "spell-b": types.SimpleNamespace(is_existing_creation=False),
        },
        _system_caching_enabled_in_aether=lambda: True,
        _get_or_create_caching_system=lambda conduit_name=None: caching_system,
    )

    cache_state = SpellbookCreationSystem._build_conjure_cache_state(
        spellbook=spellbook,
        dynamic=False,
    )

    assert cache_state["caching_enabled"] is True
    assert cache_state["dynamic_mode"] is False
    assert cache_state["automatic_mode"] is True
    assert cache_state["cache_path"] == "full_hit"
    assert cache_state["is_full_hit"] is True
    assert cache_state["is_mixed"] is False
    assert cache_state["is_full_miss"] is False
    assert cache_state["matched_spell_ids"] == {"spell-a", "spell-b"}
    assert cache_state["missing_spell_ids"] == set()
    assert cache_state["stale_cached_spell_ids"] == set()


def test_build_conjure_cache_state_reports_mixed_path() -> None:
    """
    Verify partial coverage is classified as a mixed cache run.

    Returns:
        None.
    """
    caching_system = _StubCachingSystem(
        {
            "spell-a": {"spell_id": "spell-a"},
            "stale-spell": {"spell_id": "stale-spell"},
        }
    )
    spellbook = types.SimpleNamespace(
        _spell_id_pool={
            "spell-a": types.SimpleNamespace(is_existing_creation=False),
            "spell-b": types.SimpleNamespace(is_existing_creation=False),
        },
        _system_caching_enabled_in_aether=lambda: True,
        _get_or_create_caching_system=lambda conduit_name=None: caching_system,
    )

    cache_state = SpellbookCreationSystem._build_conjure_cache_state(
        spellbook=spellbook,
        dynamic=True,
    )

    assert cache_state["cache_path"] == "mixed"
    assert cache_state["is_full_hit"] is False
    assert cache_state["is_mixed"] is True
    assert cache_state["is_full_miss"] is False
    assert cache_state["matched_spell_ids"] == {"spell-a"}
    assert cache_state["missing_spell_ids"] == {"spell-b"}
    assert cache_state["stale_cached_spell_ids"] == {"stale-spell"}


def test_build_conjure_cache_state_treats_stale_surplus_cache_as_full_hit() -> None:
    """
    Verify stale extra cached spell ids do not force recompilation.

    Returns:
        None.
    """
    caching_system = _StubCachingSystem(
        {
            "spell-a": {"spell_id": "spell-a"},
            "spell-b": {"spell_id": "spell-b"},
            "stale-spell": {"spell_id": "stale-spell"},
        }
    )
    spellbook = types.SimpleNamespace(
        _spell_id_pool={
            "spell-a": types.SimpleNamespace(is_existing_creation=False),
            "spell-b": types.SimpleNamespace(is_existing_creation=False),
        },
        _system_caching_enabled_in_aether=lambda: True,
        _get_or_create_caching_system=lambda conduit_name=None: caching_system,
    )

    cache_state = SpellbookCreationSystem._build_conjure_cache_state(
        spellbook=spellbook,
        dynamic=False,
    )

    assert cache_state["cache_path"] == "full_hit"
    assert cache_state["is_full_hit"] is True
    assert cache_state["is_mixed"] is False
    assert cache_state["is_full_miss"] is False
    assert cache_state["matched_spell_ids"] == {"spell-a", "spell-b"}
    assert cache_state["missing_spell_ids"] == set()
    assert cache_state["stale_cached_spell_ids"] == {"stale-spell"}


def test_load_cached_spell_payloads_for_conjure_loads_and_clears_resolution_flags(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify the conjure cache-load helper publishes cached payloads onto spells.

    Returns:
        None.
    """
    loaded_calls: List[tuple[str, Dict[str, Any], bool]] = []

    def _fake_load_creation_context(
            spell: Any,
            cached_package: Dict[str, Any],
            publish: bool = True,
    ) -> object:
        loaded_calls.append((spell.spell_id, cached_package, publish))
        return object()
    monkeypatch.setattr(
        "melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation.spell_codegen_creation_cache.load_creation_context",
        _fake_load_creation_context,
    )
    creation_context_factory = types.SimpleNamespace(
        _resolve_runtime_gate_for_spell=lambda spell: (None, None),
    )
    spell_a = types.SimpleNamespace(
        spell_id="spell-a",
        resolution_complete=False,
        resolution_required=True,
        _creation_context_factory=creation_context_factory,
        _dynamic_environment=False,
    )
    spell_b = types.SimpleNamespace(
        spell_id="spell-b",
        resolution_complete=False,
        resolution_required=True,
        _creation_context_factory=creation_context_factory,
        _dynamic_environment=False,
    )
    spellbook = types.SimpleNamespace(
        _spell_id_pool={
            "spell-a": spell_a,
            "spell-b": spell_b,
        }
    )
    caching_system = _StubCachingSystem(
        {
            "spell-a": {"spell_id": "spell-a"},
            "missing": {"spell_id": "missing"},
        }
    )
    loaded_spell_ids = SpellbookCreationSystem._load_cached_spell_payloads_for_conjure(
        spellbook=spellbook,
        caching_system=caching_system,
        spell_ids=("spell-a", "missing", "spell-z"),
    )

    assert loaded_spell_ids == {"spell-a"}
    assert loaded_calls == [("spell-a", {"spell_id": "spell-a"}, True)]
    assert spell_a.resolution_complete is True
    assert spell_a.resolution_required is False
    assert spell_b.resolution_complete is False
    assert spell_b.resolution_required is True


def test_emit_spell_payloads_for_conjure_returns_only_successful_spell_ids() -> None:
    """
    Verify the conjure cache-save helper reports only successful emits.

    Returns:
        None.
    """
    emit_calls: List[str] = []

    def _emit_true() -> bool:
        emit_calls.append("spell-a")
        return True

    def _emit_false() -> bool:
        emit_calls.append("spell-b")
        return False

    spellbook = types.SimpleNamespace(
        _spell_id_pool={
            "spell-a": types.SimpleNamespace(emit_cache=_emit_true),
            "spell-b": types.SimpleNamespace(emit_cache=_emit_false),
        }
    )

    emitted_spell_ids = SpellbookCreationSystem._emit_spell_payloads_for_conjure(
        spellbook=spellbook,
        spell_ids=("spell-a", "spell-b", "spell-z"),
    )

    assert emitted_spell_ids == {"spell-a"}
    assert sorted(emit_calls) == ["spell-a", "spell-b"]
