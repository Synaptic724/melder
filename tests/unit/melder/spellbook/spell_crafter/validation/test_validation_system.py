from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Optional

import pytest

import melder.aether.spellbook.spell_crafter.validation.validation_system as validation_system_module
from melder.aether.spellbook.spell_crafter.validation.spell_validation_issue import (
    SpellValidationIssue,
)
from melder.aether.spellbook.spell_crafter.validation.strategies.spell_validation_strategy import (
    SpellValidationStrategy,
)
from melder.aether.spellbook.spell_crafter.validation.validation_system import (
    SpellValidationSystem,
)


@dataclass
class _SpellIndexStub:
    """
    Purpose:
        Provide a minimal SpellIndex stub with a current id.
    Contract:
        Stores the current spell id and lineage id without validation.
    Attributes:
        current: Current spell id string.
        id: Lineage id string.
    """
    current: str
    id: str = "index-id"


class _SpellStub:
    """
    Purpose:
        Provide a minimal spell stub for validation system tests.
    Contract:
        Exposes spell_index, spell_name, and optional _spellbook.
    """

    def __init__(
        self,
        *,
        spell_id: str = "spell-id",
        spell_name: str = "spell-name",
        spellbook: Optional[object] = None,
        include_spellbook: bool = True,
    ) -> None:
        """
        Purpose:
            Initialize a spell stub with optional spellbook attachment.
        Contract:
            Creates spell_index with the provided spell_id.
        Args:
            spell_id: Spell id assigned to spell_index.current.
            spell_name: Spell name string.
            spellbook: Spellbook object or None.
            include_spellbook: Whether to set the _spellbook attribute.
        Returns:
            None.
        """
        self.spell_index = _SpellIndexStub(spell_id)
        self.spell_name = spell_name
        if include_spellbook:
            self._spellbook = spellbook


class _SharedViewSpellStub:
    """
    Purpose:
        Provide a spell stub with the attributes required by shared views.
    Contract:
        Exposes dependency metadata and binding identifiers used by Phase 4.
    """

    def __init__(
        self,
        *,
        spell_id: str,
        spell_name: str,
        spellframe: object,
        binding_name: object,
        dependencies: Optional[List[str]] = None,
        crafter: object = None,
    ) -> None:
        """
        Purpose:
            Initialize a shared-view spell stub with dependency metadata.
        Contract:
            Stores attributes verbatim and normalizes dependencies to a list.
        Args:
            spell_id: Spell id assigned to spell_index.current.
            spell_name: Spell name string.
            spellframe: Frame identifier for the spell.
            binding_name: Binding name identifier.
            dependencies: Optional dependency list.
            crafter: Optional crafter reference (defaults to None).
        Returns:
            None.
        """
        self.spell_index = _SpellIndexStub(spell_id)
        self.spell_name = spell_name
        self.spellframe = spellframe
        self.binding_name = binding_name
        self.dependencies = list(dependencies or [])
        self._crafter = crafter


class _SpellbookStub:
    """
    Purpose:
        Provide a minimal spellbook stub for shared view construction.
    Contract:
        Exposes a spell id pool mapping for validation system use.
    """

    def __init__(self, *, spell_lookup: dict[str, object]) -> None:
        """
        Purpose:
            Initialize the stub with a spell lookup map.
        Contract:
            Stores the provided mapping without mutation.
        Args:
            spell_lookup: Spell id -> spell mapping.
        Returns:
            None.
        """
        self._spell_id_pool = spell_lookup
        self._spell_system_states = None


class _CancelStub:
    """
    Purpose:
        Provide a minimal cancellation event stub for tests.
    Contract:
        Raises the configured exception when is_set is True.
    """

    def __init__(self, *, is_set: bool = True, exc: Optional[Exception] = None) -> None:
        """
        Purpose:
            Initialize the stub with a fixed cancellation state.
        Contract:
            Stores the provided state and exception for later use.
        Args:
            is_set: Whether cancellation is active.
            exc: Optional exception to raise; defaults to RuntimeError.
        Returns:
            None.
        """
        self._is_set = is_set
        self._exc = exc or RuntimeError("cancelled")

    @property
    def is_set(self) -> bool:
        """
        Purpose:
            Report whether cancellation is currently active.
        Contract:
            Returns the value provided at initialization.
        Returns:
            bool: True when cancellation is active.
        """
        return self._is_set

    def throw_if_set(self) -> None:
        """
        Purpose:
            Raise the configured exception when cancellation is active.
        Contract:
            Raises only when is_set is True.
        Raises:
            Exception: The configured cancellation exception.
        """
        if self.is_set:
            raise self._exc


class _ToggleCancel:
    """
    Purpose:
        Toggle cancellation state on the third is_set check.
    Contract:
        Raises once the third check is performed.
    """

    def __init__(self) -> None:
        """
        Purpose:
            Initialize the toggle state.
        Contract:
            Starts with cancellation disabled for the first two checks.
        Returns:
            None.
        """
        self._checks = 0

    @property
    def is_set(self) -> bool:
        """
        Purpose:
            Toggle to cancelled on the third check.
        Contract:
            Returns False on first two checks, True thereafter.
        Returns:
            bool: True once cancellation should be honored.
        """
        self._checks += 1
        return self._checks > 2

    def throw_if_set(self) -> None:
        """
        Purpose:
            Raise once cancellation has been toggled on.
        Contract:
            Raises RuntimeError when cancellation is active.
        Raises:
            RuntimeError: When cancellation has been toggled on.
        """
        if self._checks > 2:
            raise RuntimeError("cancelled")


class _ContextStub:
    """
    Purpose:
        Provide a minimal context stub to verify cleanup behavior.
    Contract:
        Records cleanup calls and exposes provided attributes.
    """

    last_instance: Optional["_ContextStub"] = None

    def __init__(
        self,
        *,
        spell: object,
        spellbook: Optional[object],
        requirements: Optional[object],
        symbolic_graph: Optional[object],
        resolution_frame: Optional[object],
        cancel_event: Optional[object],
        issues: list,
        cleanup_artifacts: bool = True,
    ) -> None:
        """
        Purpose:
            Store the provided context attributes for later inspection.
        Contract:
            Records the most recent instance for test assertions.
        Args:
            spell: Spell object under validation.
            spellbook: Owning spellbook, if any.
            requirements: Phase 1 requirements artifact.
            symbolic_graph: Phase 2 symbolic graph.
            resolution_frame: Phase 3 resolution frame.
            cancel_event: Cancellation event or None.
            issues: Shared issues list.
            cleanup_artifacts: Whether to clean artifacts during context cleanup.
        Returns:
            None.
        """
        self.spell = spell
        self.spellbook = spellbook
        self.requirements = requirements
        self.symbolic_graph = symbolic_graph
        self.resolution_frame = resolution_frame
        self.cancel_event = cancel_event
        self.issues = issues
        self.cleanup_artifacts = cleanup_artifacts
        self.cleanup_calls = 0
        self.cleaned = False
        _ContextStub.last_instance = self

    def cleanup(self) -> None:
        """
        Purpose:
            Record cleanup calls and mark the context as cleaned.
        Contract:
            Increments cleanup_calls and sets cleaned to True.
        Returns:
            None.
        """
        self.cleanup_calls += 1
        self.cleaned = True



class _EmptyNameStrategy:
    """
    Purpose:
        Provide a strategy stub with an empty name for validation tests.
    Contract:
        Exposes name as an empty string.
    """

    name = ""

    def validate(self, context: object) -> None:
        """
        Purpose:
            No-op validate method to satisfy the expected interface.
        Contract:
            Does not mutate context or raise.
        Args:
            context: SpellValidationContext instance.
        Returns:
            None.
        """
        return None


class _NoCleanupStrategy:
    """
    Purpose:
        Provide a strategy stub without a cleanup method.
    Contract:
        Exposes a name attribute and validate method only.
    """

    def __init__(self, name: str = "no-cleanup") -> None:
        """
        Purpose:
            Initialize the strategy with a stable name.
        Contract:
            Stores the name and resets call counters.
        Args:
            name: Strategy name string.
        Returns:
            None.
        """
        self.name = name
        self.validate_calls = 0

    def validate(self, context: object) -> None:
        """
        Purpose:
            Record that validation was invoked.
        Contract:
            Increments validate_calls.
        Args:
            context: SpellValidationContext instance.
        Returns:
            None.
        """
        self.validate_calls += 1


class _RecordingStrategy(SpellValidationStrategy):
    """
    Purpose:
        Record validation calls and optionally append issues or raise.
    Contract:
        Captures context snapshots and preserves issue list references.
    """

    def __init__(
        self,
        *,
        name: str = "recording",
        issue: Optional[SpellValidationIssue] = None,
        raise_on_validate: bool = False,
        on_validate: Optional[Callable[[], None]] = None,
    ) -> None:
        """
        Purpose:
            Initialize the recording strategy.
        Contract:
            Stores options for issue appending and exception raising.
        Args:
            name: Strategy name string.
            issue: Optional issue to append during validate.
            raise_on_validate: Whether validate should raise.
            on_validate: Optional callback invoked during validate.
        Returns:
            None.
        """
        super().__init__(name=name)
        self.calls: int = 0
        self.context_snapshots: list[dict[str, object]] = []
        self.issues_ref: Optional[list] = None
        self._issue = issue
        self._raise_on_validate = raise_on_validate
        self._on_validate = on_validate

    def validate(self, context: object) -> None:
        """
        Purpose:
            Record the context and apply configured behaviors.
        Contract:
            - Captures context fields.
            - Appends issue when configured.
            - Raises when configured.
        Args:
            context: SpellValidationContext instance.
        Returns:
            None.
        Raises:
            RuntimeError: When raise_on_validate is True.
        """
        self.calls += 1
        snapshot = {
            "spell": context.spell,
            "spellbook": context.spellbook,
            "requirements": context.requirements,
            "symbolic_graph": context.symbolic_graph,
            "resolution_frame": context.resolution_frame,
            "cancel_event": context.cancel_event,
            "issues": context.issues,
        }
        self.context_snapshots.append(snapshot)
        if self.issues_ref is None:
            self.issues_ref = context.issues
        if self._on_validate is not None:
            self._on_validate()
        if self._issue is not None:
            context.issues.append(self._issue)
        if self._raise_on_validate:
            raise RuntimeError("strategy boom")


class _CleanupStrategy(SpellValidationStrategy):
    """
    Purpose:
        Track cleanup calls for unregister_strategy tests.
    Contract:
        Increments cleanup_calls and honors base cleanup behavior.
    """

    def __init__(self, name: str = "cleanup") -> None:
        """
        Purpose:
            Initialize the cleanup-tracking strategy.
        Contract:
            Resets cleanup_calls to zero.
        Args:
            name: Strategy name string.
        Returns:
            None.
        """
        super().__init__(name=name)
        self.cleanup_calls = 0

    def validate(self, context: object) -> None:
        """
        Purpose:
            No-op validate method for cleanup testing.
        Contract:
            Does not mutate context or raise.
        Args:
            context: SpellValidationContext instance.
        Returns:
            None.
        """
        return None

    def cleanup(self) -> None:
        """
        Purpose:
            Record cleanup calls and delegate to base cleanup.
        Contract:
            Increments cleanup_calls and marks cleaned.
        Returns:
            None.
        """
        self.cleanup_calls += 1
        super().cleanup()


class _RaisingCleanupStrategy(SpellValidationStrategy):
    """
    Purpose:
        Provide a strategy that raises during cleanup.
    Contract:
        cleanup raises RuntimeError when invoked.
    """

    def __init__(self, name: str = "raising-cleanup") -> None:
        """
        Purpose:
            Initialize the raising cleanup strategy.
        Contract:
            Stores the provided name via base constructor.
        Args:
            name: Strategy name string.
        Returns:
            None.
        """
        super().__init__(name=name)

    def validate(self, context: object) -> None:
        """
        Purpose:
            No-op validate method for cleanup testing.
        Contract:
            Does not mutate context or raise.
        Args:
            context: SpellValidationContext instance.
        Returns:
            None.
        """
        return None

    def cleanup(self) -> None:
        """
        Purpose:
            Raise to simulate cleanup failure.
        Contract:
            Always raises RuntimeError.
        Raises:
            RuntimeError: Unconditional cleanup error.
        """
        raise RuntimeError("cleanup boom")


class _TestValidationSystem(SpellValidationSystem):
    """
    Purpose:
        SpellValidationSystem variant with builtin registration disabled.
    Contract:
        Does not auto-register any strategies on initialization.
    """

    def _register_builtin_strategies(self) -> None:
        """
        Purpose:
            Override builtin registration for test control.
        Contract:
            Leaves the strategy registry empty.
        Returns:
            None.
        """
        return None


def _make_spell(
    *,
    spell_id: str = "spell-id",
    spell_name: str = "spell-name",
    spellbook: Optional[object] = None,
    include_spellbook: bool = True,
) -> _SpellStub:
    """
    Purpose:
        Build a spell stub with configurable identifiers and spellbook link.
    Contract:
        Returns a _SpellStub with the provided attributes.
    Args:
        spell_id: Spell id assigned to spell_index.current.
        spell_name: Spell name string.
        spellbook: Spellbook object or None.
        include_spellbook: Whether to set the _spellbook attribute.
    Returns:
        _SpellStub: The configured spell stub.
    """
    return _SpellStub(
        spell_id=spell_id,
        spell_name=spell_name,
        spellbook=spellbook,
        include_spellbook=include_spellbook,
    )


def test_init_registers_builtin_strategies() -> None:
    """
    Purpose:
        Ensure the default system registers built-in strategies.
    Contract:
        Built-in strategy names are present in the registry.
    Returns:
        None.
    Raises:
        AssertionError: If any built-in strategy is missing.
    """
    system = SpellValidationSystem()
    names = {strategy.name for strategy in system.iter_strategies()}
    expected = {
        "resolution_frame_presence",
        "dangling_dependencies",
        "self_dependency",
        "circular_dependency",
        "required_holes",
        "duplicate_spell_name",
        "annotation_shape_guard",
        "spellmap_shape_validation",
        "parameter_policy",
        "callable_profile_hygiene",
        "existing_creation_compatibility",
        "contract_provider_presence",
        "binding_resolution_cycle",
    }
    assert expected.issubset(names)
    assert len(names) >= len(expected)


def test_register_strategy_rejects_none() -> None:
    """
    Purpose:
        Ensure registering a None strategy raises ValueError.
    Contract:
        register_strategy rejects None inputs.
    Returns:
        None.
    Raises:
        AssertionError: If ValueError is not raised.
    """
    system = _TestValidationSystem()
    with pytest.raises(ValueError, match="strategy"):
        system.register_strategy(None)


def test_register_strategy_rejects_empty_name() -> None:
    """
    Purpose:
        Ensure strategies with empty names are rejected.
    Contract:
        register_strategy raises ValueError for empty names.
    Returns:
        None.
    Raises:
        AssertionError: If ValueError is not raised.
    """
    system = _TestValidationSystem()
    with pytest.raises(ValueError, match="strategy.name"):
        system.register_strategy(_EmptyNameStrategy())


def test_register_strategy_replaces_existing() -> None:
    """
    Purpose:
        Verify registering a strategy with the same name replaces the prior one.
    Contract:
        Only the latest strategy is retained under the shared name.
    Returns:
        None.
    Raises:
        AssertionError: If the replacement does not occur.
    """
    system = _TestValidationSystem()
    first = _RecordingStrategy(name="dup")
    second = _RecordingStrategy(name="dup")
    system.register_strategy(first)
    system.register_strategy(second)
    strategies = system.iter_strategies()
    assert len(strategies) == 1
    assert strategies[0] is second


def test_unregister_strategy_rejects_empty_name() -> None:
    """
    Purpose:
        Ensure unregister rejects empty names.
    Contract:
        unregister_strategy raises ValueError for empty name inputs.
    Returns:
        None.
    Raises:
        AssertionError: If ValueError is not raised.
    """
    system = _TestValidationSystem()
    with pytest.raises(ValueError, match="name"):
        system.unregister_strategy("")


def test_unregister_strategy_removes_strategy() -> None:
    """
    Purpose:
        Verify unregister removes a registered strategy.
    Contract:
        Strategy list becomes empty after removal.
    Returns:
        None.
    Raises:
        AssertionError: If the strategy remains registered.
    """
    system = _TestValidationSystem()
    strategy = _RecordingStrategy(name="to-remove")
    system.register_strategy(strategy)
    system.unregister_strategy("to-remove")
    assert system.iter_strategies() == []


def test_unregister_strategy_calls_cleanup() -> None:
    """
    Purpose:
        Ensure unregister invokes strategy cleanup when present.
    Contract:
        cleanup is called exactly once on unregister.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup is not called.
    """
    system = _TestValidationSystem()
    strategy = _CleanupStrategy(name="cleanup")
    system.register_strategy(strategy)
    system.unregister_strategy("cleanup")
    assert strategy.cleanup_calls == 1


def test_unregister_strategy_swallows_cleanup_errors() -> None:
    """
    Purpose:
        Confirm unregister suppresses cleanup exceptions.
    Contract:
        unregister completes even if cleanup raises.
    Returns:
        None.
    Raises:
        AssertionError: If unregister raises or strategy remains.
    """
    system = _TestValidationSystem()
    strategy = _RaisingCleanupStrategy(name="boom")
    system.register_strategy(strategy)
    system.unregister_strategy("boom")
    assert system.iter_strategies() == []


def test_unregister_strategy_without_cleanup_method() -> None:
    """
    Purpose:
        Verify unregister works for strategies without cleanup methods.
    Contract:
        Strategy is removed without error.
    Returns:
        None.
    Raises:
        AssertionError: If unregister raises or strategy remains.
    """
    system = _TestValidationSystem()
    strategy = _NoCleanupStrategy(name="no-cleanup")
    system.register_strategy(strategy)
    system.unregister_strategy("no-cleanup")
    assert system.iter_strategies() == []


def test_iter_strategies_returns_snapshot() -> None:
    """
    Purpose:
        Ensure iter_strategies returns a copy of the registry.
    Contract:
        Mutating the returned list does not affect the registry.
    Returns:
        None.
    Raises:
        AssertionError: If registry is mutated by list changes.
    """
    system = _TestValidationSystem()
    strategy = _RecordingStrategy(name="snap")
    system.register_strategy(strategy)
    snapshot = system.iter_strategies()
    snapshot.clear()
    assert system.iter_strategies() == [strategy]


def test_validate_spell_requires_spell() -> None:
    """
    Purpose:
        Ensure validate_spell rejects a None spell.
    Contract:
        Raises ValueError when spell is None.
    Returns:
        None.
    Raises:
        AssertionError: If ValueError is not raised.
    """
    system = _TestValidationSystem()
    with pytest.raises(ValueError, match="spell"):
        system.validate_spell(
            spell=None,
            requirements=None,
            symbolic_graph=None,
            resolution_frame=None,
        )


def test_validate_spell_returns_result_with_spell_id_and_name() -> None:
    """
    Purpose:
        Verify validate_spell returns a result with spell id and name.
    Contract:
        Result fields match the spell's current id and name.
    Returns:
        None.
    Raises:
        AssertionError: If result fields do not match.
    """
    system = _TestValidationSystem()
    spell = _make_spell(spell_id="sid", spell_name="sname", spellbook=None)
    result = system.validate_spell(
        spell=spell,
        requirements=None,
        symbolic_graph=None,
        resolution_frame=None,
    )
    assert result.spell_id == "sid"
    assert result.spell_name == "sname"
    assert result.issues == []


def test_validate_spell_runs_all_strategies() -> None:
    """
    Purpose:
        Ensure all registered strategies are invoked.
    Contract:
        Each strategy validate runs once.
    Returns:
        None.
    Raises:
        AssertionError: If any strategy is not called.
    """
    system = _TestValidationSystem()
    first = _RecordingStrategy(name="first")
    second = _RecordingStrategy(name="second")
    system.register_strategy(first)
    system.register_strategy(second)
    system.validate_spell(
        spell=_make_spell(),
        requirements=None,
        symbolic_graph=None,
        resolution_frame=None,
    )
    assert first.calls == 1
    assert second.calls == 1


def test_validate_spell_passes_context_fields_to_strategy() -> None:
    """
    Purpose:
        Verify context fields are populated as expected for strategies.
    Contract:
        Context fields match the supplied spell and artifacts.
    Returns:
        None.
    Raises:
        AssertionError: If any context field is incorrect.
    """
    system = _TestValidationSystem()
    issue = SpellValidationIssue("warning", "W", "warn")
    strategy = _RecordingStrategy(name="rec", issue=issue)
    system.register_strategy(strategy)
    spellbook = object()
    requirements = object()
    symbolic_graph = object()
    resolution_frame = object()
    cancel_event = _CancelStub(is_set=False)
    spell = _make_spell(
        spellbook=spellbook,
        include_spellbook=True,
    )

    system.validate_spell(
        spell=spell,
        requirements=requirements,
        symbolic_graph=symbolic_graph,
        resolution_frame=resolution_frame,
        cancel_event=cancel_event,
    )

    snapshot = strategy.context_snapshots[0]
    assert snapshot["spell"] is spell
    assert snapshot["spellbook"] is spellbook
    assert snapshot["requirements"] is requirements
    assert snapshot["symbolic_graph"] is symbolic_graph
    assert snapshot["resolution_frame"] is resolution_frame
    assert snapshot["cancel_event"] is cancel_event
    assert snapshot["issues"] is strategy.issues_ref


def test_validate_spell_appends_issues_to_result() -> None:
    """
    Purpose:
        Ensure issues appended by strategies appear in the result.
    Contract:
        Result issues list contains the appended issue and matches the shared list.
    Returns:
        None.
    Raises:
        AssertionError: If issues are missing or list references differ.
    """
    system = _TestValidationSystem()
    issue = SpellValidationIssue("error", "E", "err")
    strategy = _RecordingStrategy(name="rec", issue=issue)
    system.register_strategy(strategy)
    result = system.validate_spell(
        spell=_make_spell(),
        requirements=None,
        symbolic_graph=None,
        resolution_frame=None,
    )
    assert issue in result.issues
    assert result.issues is strategy.issues_ref
    assert issue.source == "_RecordingStrategy"


def test_validate_spell_preserves_issue_source() -> None:
    """
    Purpose:
        Ensure validation does not overwrite existing issue source metadata.
    Contract:
        An issue with a pre-set source retains that value.
    Returns:
        None.
    Raises:
        AssertionError: If the source is replaced.
    """
    system = _TestValidationSystem()
    issue = SpellValidationIssue(
        "error",
        "E",
        "err",
        source="ExplicitSource",
    )
    strategy = _RecordingStrategy(name="rec", issue=issue)
    system.register_strategy(strategy)
    result = system.validate_spell(
        spell=_make_spell(),
        requirements=None,
        symbolic_graph=None,
        resolution_frame=None,
    )
    assert issue in result.issues
    assert issue.source == "ExplicitSource"


def test_validate_spell_cancellation_preempts_strategies() -> None:
    """
    Purpose:
        Ensure cancellation is honored before strategy execution.
    Contract:
        Raises cancellation exception and no strategy runs.
    Returns:
        None.
    Raises:
        RuntimeError: When cancellation is signaled.
    """
    system = _TestValidationSystem()
    strategy = _RecordingStrategy(name="rec")
    system.register_strategy(strategy)
    with pytest.raises(RuntimeError, match="cancelled"):
        system.validate_spell(
            spell=_make_spell(),
            requirements=None,
            symbolic_graph=None,
            resolution_frame=None,
            cancel_event=_CancelStub(is_set=True),
        )
    assert strategy.calls == 0


def test_validate_spell_cancellation_between_strategies() -> None:
    """
    Purpose:
        Verify cancellation stops processing between strategies.
    Contract:
        First strategy runs, second is blocked by cancellation.
    Returns:
        None.
    Raises:
        RuntimeError: When cancellation is toggled on.
    """
    system = _TestValidationSystem()
    first = _RecordingStrategy(name="first")
    second = _RecordingStrategy(name="second")
    system.register_strategy(first)
    system.register_strategy(second)
    with pytest.raises(RuntimeError, match="cancelled"):
        system.validate_spell(
            spell=_make_spell(),
            requirements=None,
            symbolic_graph=None,
            resolution_frame=None,
            cancel_event=_ToggleCancel(),
        )
    assert first.calls == 1
    assert second.calls == 0


def test_validate_spell_propagates_strategy_exception() -> None:
    """
    Purpose:
        Ensure strategy exceptions propagate out of validate_spell.
    Contract:
        RuntimeError from strategy is not swallowed.
    Returns:
        None.
    Raises:
        RuntimeError: When the strategy raises.
    """
    system = _TestValidationSystem()
    strategy = _RecordingStrategy(name="boom", raise_on_validate=True)
    system.register_strategy(strategy)
    with pytest.raises(RuntimeError, match="strategy boom"):
        system.validate_spell(
            spell=_make_spell(),
            requirements=None,
            symbolic_graph=None,
            resolution_frame=None,
        )


def test_validate_spell_cleanup_context_on_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Purpose:
        Ensure context cleanup runs even when a strategy raises.
    Contract:
        Context cleanup is invoked once before exception propagates.
    Args:
        monkeypatch: Pytest fixture for patching SpellValidationContext.
    Returns:
        None.
    Raises:
        RuntimeError: When the strategy raises.
    """
    monkeypatch.setattr(validation_system_module, "SpellValidationContext", _ContextStub)
    system = _TestValidationSystem()
    strategy = _RecordingStrategy(name="boom", raise_on_validate=True)
    system.register_strategy(strategy)
    with pytest.raises(RuntimeError, match="strategy boom"):
        system.validate_spell(
            spell=_make_spell(),
            requirements=None,
            symbolic_graph=None,
            resolution_frame=None,
        )
    assert _ContextStub.last_instance is not None
    assert _ContextStub.last_instance.cleaned is True
    assert _ContextStub.last_instance.cleanup_calls == 1


def test_cleanup_clears_strategies_and_marks_cleaned() -> None:
    """
    Purpose:
        Verify cleanup clears strategies and marks the system as cleaned.
    Contract:
        _strategies is empty and _lock is None after cleanup.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup does not clear state.
    """
    system = _TestValidationSystem()
    system.register_strategy(_RecordingStrategy(name="rec"))
    system.cleanup()
    assert system.cleaned is True
    assert system._strategies == {}
    assert not hasattr(system, '_lock')


def test_cleanup_is_idempotent() -> None:
    """
    Purpose:
        Ensure cleanup can be called multiple times safely.
    Contract:
        Second cleanup call does not raise and state remains cleaned.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup is not idempotent.
    """
    system = _TestValidationSystem()
    system.cleanup()
    system.cleanup()
    assert system.cleaned is True
    assert not hasattr(system, '_lock')


def test_cleanup_returns_early_when_cleaned_inside_lock() -> None:
    """
    Purpose:
        Cover the inner cleanup recheck after lock acquisition.
    Contract:
        cleanup returns without touching strategies when another actor marked
        the system cleaned before the body runs.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup continues past the inner recheck.
    """

    class _FlipCleanedLock:
        def __init__(self, system: _TestValidationSystem) -> None:
            self._system = system

        def __enter__(self):
            self._system._cleaned = True  # noqa: SLF001
            return self

        def __exit__(self, exc_type, exc, tb):
            return None

    system = _TestValidationSystem()
    strategy = _CleanupStrategy(name="rec")
    system.register_strategy(strategy)
    system._lock = _FlipCleanedLock(system)  # noqa: SLF001

    system.cleanup()

    assert strategy.cleanup_calls == 0
    assert system.cleaned is True
    assert isinstance(system._lock, _FlipCleanedLock)  # noqa: SLF001


def test_cleanup_swallows_strategy_cleanup_errors() -> None:
    """
    Purpose:
        Ensure system cleanup suppresses strategy cleanup failures.
    Contract:
        cleanup completes, clears the registry, and marks the system cleaned.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup propagates or leaves stale registry state.
    """
    system = _TestValidationSystem()
    system.register_strategy(_RaisingCleanupStrategy(name="boom"))

    system.cleanup()

    assert system.cleaned is True
    assert system._strategies == {}
    assert not hasattr(system, '_lock')


def test_validate_spell_after_cleanup_raises() -> None:
    """
    Purpose:
        Ensure validate_spell rejects calls after cleanup.
    Contract:
        Raises RuntimeError when system is cleaned.
    Returns:
        None.
    Raises:
        AssertionError: If RuntimeError is not raised.
    """
    system = _TestValidationSystem()
    system.cleanup()
    with pytest.raises(RuntimeError, match="cleaned"):
        system.validate_spell(
            spell=_make_spell(),
            requirements=None,
            symbolic_graph=None,
            resolution_frame=None,
        )


def test_register_strategy_after_cleanup_raises() -> None:
    """
    Purpose:
        Ensure register_strategy rejects calls after cleanup.
    Contract:
        Raises RuntimeError when system is cleaned.
    Returns:
        None.
    Raises:
        AssertionError: If RuntimeError is not raised.
    """
    system = _TestValidationSystem()
    system.cleanup()
    with pytest.raises(RuntimeError, match="cleaned"):
        system.register_strategy(_RecordingStrategy(name="rec"))


def test_iter_strategies_after_cleanup_raises() -> None:
    """
    Purpose:
        Ensure iter_strategies rejects calls after cleanup.
    Contract:
        Raises RuntimeError when system is cleaned.
    Returns:
        None.
    Raises:
        AssertionError: If RuntimeError is not raised.
    """
    system = _TestValidationSystem()
    system.cleanup()
    with pytest.raises(RuntimeError, match="cleaned"):
        system.iter_strategies()


def test_unregister_strategy_after_cleanup_raises() -> None:
    """
    Purpose:
        Ensure unregister_strategy rejects calls after cleanup.
    Contract:
        Raises RuntimeError when system is cleaned.
    Returns:
        None.
    Raises:
        AssertionError: If RuntimeError is not raised.
    """
    system = _TestValidationSystem()
    system.cleanup()
    with pytest.raises(RuntimeError, match="cleaned"):
        system.unregister_strategy("any")


def test_validate_spell_uses_strategy_snapshot() -> None:
    """
    Purpose:
        Confirm strategies registered during validation do not run in the same call.
    Contract:
        Newly registered strategy runs only on the next validation call.
    Returns:
        None.
    Raises:
        AssertionError: If strategy runs in the same call.
    """
    system = _TestValidationSystem()
    second = _RecordingStrategy(name="second")

    def register_second() -> None:
        """
        Purpose:
            Register the second strategy during validation.
        Contract:
            Adds the second strategy to the system.
        Returns:
            None.
        """
        system.register_strategy(second)

    first = _RecordingStrategy(name="first", on_validate=register_second)
    system.register_strategy(first)

    system.validate_spell(
        spell=_make_spell(),
        requirements=None,
        symbolic_graph=None,
        resolution_frame=None,
    )
    assert first.calls == 1
    assert second.calls == 0

    system.validate_spell(
        spell=_make_spell(),
        requirements=None,
        symbolic_graph=None,
        resolution_frame=None,
    )
    assert second.calls == 1


def test_validate_spell_cleanup_context_on_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Purpose:
        Ensure context cleanup runs on successful validation.
    Contract:
        Context cleanup is invoked once after validation.
    Args:
        monkeypatch: Pytest fixture for patching SpellValidationContext.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup is not called.
    """
    monkeypatch.setattr(validation_system_module, "SpellValidationContext", _ContextStub)
    system = _TestValidationSystem()
    system.register_strategy(_RecordingStrategy(name="rec"))
    system.validate_spell(
        spell=_make_spell(),
        requirements=None,
        symbolic_graph=None,
        resolution_frame=None,
    )
    assert _ContextStub.last_instance is not None
    assert _ContextStub.last_instance.cleaned is True
    assert _ContextStub.last_instance.cleanup_calls == 1


def test_validate_spell_swallows_context_cleanup_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Purpose:
        Ensure context cleanup failures are suppressed after validation.
    Contract:
        validate_spell still returns a result when context.cleanup raises.
    Args:
        monkeypatch: Pytest fixture for patching SpellValidationContext.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup failure prevents result construction.
    """

    class _RaisingContextStub(_ContextStub):
        def cleanup(self) -> None:
            self.cleanup_calls += 1
            raise RuntimeError("context cleanup boom")

    monkeypatch.setattr(
        validation_system_module,
        "SpellValidationContext",
        _RaisingContextStub,
    )
    system = _TestValidationSystem()
    system.register_strategy(_RecordingStrategy(name="rec"))

    result = system.validate_spell(
        spell=_make_spell(),
        requirements=None,
        symbolic_graph=None,
        resolution_frame=None,
    )

    assert result.spell_id == "spell-id"
    assert _RaisingContextStub.last_instance is not None
    assert _RaisingContextStub.last_instance.cleanup_calls == 1
