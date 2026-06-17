from threading import RLock
from typing import TYPE_CHECKING, Any, Dict, List, Optional, ClassVar

if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spellbook import Spellbook
    from melder.aether.spellbook.spell_compiler.profiles.resolution_profile import (
        SpellResolutionFrame,
    )
    from melder.aether.spellbook.spell_compiler.spell_requirements_finder.spell_requirements import (
        SpellRequirements,
    )
    from melder.aether.spellbook.spell_compiler.symbolic_graph.spell_symbolic_graph import (
        SpellSymbolicGraph,
    )
    from melder.aether.spellbook.spell_compiler.validation.strategies.spell_validation_strategy import (
        SpellValidationStrategy,
    )
    from melder.utilities.synchronization.cancellation_event_signal import (
        CancellationEvent,
    )



# Melder imports
from melder.aether.spellbook.spell_compiler.validation.spell_validation_context import SpellValidationContext
from melder.aether.spellbook.spell_compiler.validation.spell_validation_issue import SpellValidationIssue
from melder.aether.spellbook.spell_compiler.validation.spell_validation_result import SpellValidationResult
# Strategies
from melder.aether.spellbook.spell_compiler.validation.strategies.circular_dependency_strategy import CircularDependencyStrategy
from melder.aether.spellbook.spell_compiler.validation.strategies.dangling_dependency_strategy import \
    DanglingDependenciesStrategy
from melder.aether.spellbook.spell_compiler.validation.strategies.required_holes_strategy import RequiredHolesStrategy
from melder.aether.spellbook.spell_compiler.validation.strategies.resolution_frame_presence_strategy import \
    ResolutionFramePresenceStrategy
from melder.aether.spellbook.spell_compiler.validation.strategies.self_validation_strategy import SelfDependencyStrategy
from melder.aether.spellbook.spell_compiler.validation.strategies.duplicate_spell_name_strategy import DuplicateSpellNameStrategy
from melder.aether.spellbook.spell_compiler.validation.strategies.annotation_shape_guard_strategy import (
    AnnotationShapeGuardStrategy,
)
from melder.aether.spellbook.spell_compiler.validation.strategies.spellmap_shape_validation_strategy import (
    SpellMapShapeValidationStrategy,
)
from melder.aether.spellbook.spell_compiler.validation.strategies.parameter_policy_strategy import (
    ParameterPolicyStrategy,
)
from melder.aether.spellbook.spell_compiler.validation.strategies.callable_profile_hygiene_strategy import (
    CallableProfileHygieneStrategy,
)
from melder.aether.spellbook.spell_compiler.validation.strategies.existing_creation_compatibility_strategy import (
    ExistingCreationCompatibilityStrategy,
)
from melder.aether.spellbook.spell_compiler.validation.strategies.contract_provider_presence_strategy import (
    ContractProviderPresenceStrategy,
)
from melder.aether.spellbook.spell_compiler.validation.strategies.binding_resolution_cycle_strategy import (
    BindingResolutionCycleStrategy,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg


class SpellValidationSystem(Cleanable):
    """
    Central registry + runner for spell validation strategies.

    Typical usage
    -------------
    * Phase 4 of the SpellCrafter creates a "SpellValidationSystem".
    * Built-in strategies are auto-registered in the constructor.
    *: meth:`validate_spell` is invoked with a fully built spell context.
    * The returned: class:`SpellValidationResult` is stored on the crafter
      and surfaced via: attr:`Spell.validated` /: attr:`Spell.is_broken`.

    The system itself is **ephemeral** – it is created per validation run
    and cleaned up afterwards. Strategies are owned by the system and are
    also cleaned when the system is cleaned.
    """
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_strategies",
    ]

    def __init__(self) -> None:
        """
        Initialize one ephemeral spell validation system.

        Contract:
            - Starts with an empty strategy registry.
            - Immediately registers the built-in validation strategies in the
              intended default order.
            - Owns every registered strategy for later cleanup.
        """
        super().__init__()
        self._lock: RLock = RLock()
        self._strategies: Dict[str, SpellValidationStrategy] = {}
        self._register_builtin_strategies()

    # ------------------------------------------------------------------ #
    # Cleanup
    # ------------------------------------------------------------------ #

    def cleanup(self) -> None:
        """
        Deterministically tear down this validation system and all strategies.

        This:
        - Cleans up each registered strategy.
        - Clears the strategy registry.
        - Marks the system as cleaned and drops the lock.
        """
        if self._cleaned:
            return

        with self._lock:
            if self._cleaned:
                return

            for strategy in list(self._strategies.values()):
                try:
                    strategy.cleanup()
                except Exception:
                    # Never let strategy cleanup failures bubble up.
                    pass

            self._strategies.clear()
            self._cleaned = True

        del self._lock

    # ------------------------------------------------------------------ #
    # Strategy registration
    # ------------------------------------------------------------------ #

    def _register_builtin_strategies(self) -> None:
        """
        Register the default set of validation strategies.

        These are intentionally conservative and focused on structural
        correctness:

        * ResolutionFramePresenceStrategy
        * DanglingDependenciesStrategy
        * SelfDependencyStrategy
        * CircularDependencyStrategy
        * RequiredHolesStrategy
        * DuplicateSpellNameStrategy
        * AnnotationShapeGuardStrategy
        * SpellMapShapeValidationStrategy
        * ContractProviderPresenceStrategy
        * BindingResolutionCycleStrategy
        * ParameterPolicyStrategy
        * CallableProfileHygieneStrategy
        * ExistingCreationCompatibilityStrategy
        """
        self.register_strategy(ResolutionFramePresenceStrategy())
        self.register_strategy(DanglingDependenciesStrategy())
        self.register_strategy(SelfDependencyStrategy())
        self.register_strategy(CircularDependencyStrategy())
        self.register_strategy(RequiredHolesStrategy())
        self.register_strategy(DuplicateSpellNameStrategy())
        self.register_strategy(AnnotationShapeGuardStrategy())
        self.register_strategy(SpellMapShapeValidationStrategy())
        self.register_strategy(ContractProviderPresenceStrategy())
        self.register_strategy(BindingResolutionCycleStrategy())
        self.register_strategy(ParameterPolicyStrategy())
        self.register_strategy(CallableProfileHygieneStrategy())
        self.register_strategy(ExistingCreationCompatibilityStrategy())

    def register_strategy(self, strategy: SpellValidationStrategy) -> None:
        """
        Register (or replace) a validation strategy.

        Args:
            strategy:
                The strategy instance to register. Its "name" property is
                used as the key.

        Raises:
            ValueError:
                If "strategy" is None or has an empty name.

        Contract:
            - Replaces any existing strategy with the same name.
            - Ownership of the registered strategy transfers to the validation
              system for later cleanup.
        """
        self.check_cleaned()
        if strategy is None:
            raise ValueError("strategy cannot be None.")

        name = strategy.name
        if not name:
            raise ValueError("strategy.name cannot be empty.")

        with self._lock:
            self._strategies[name] = strategy

    def unregister_strategy(self, name: str) -> None:
        """
        Unregister a strategy by name.

        Silently does nothing if the name is not currently registered.

        Contract:
            Best-effort cleans the removed strategy after it is detached from
            the registry.
        """
        self.check_cleaned()
        if not name:
            raise ValueError("name cannot be empty.")

        with self._lock:
            strategy = self._strategies.pop(name, None)

        if strategy is not None:
            try:
                if hasattr(strategy, 'cleanup'):
                    strategy.cleanup()
            except Exception:
                # Validation cleanup should never explode callers.
                pass

    def iter_strategies(self) -> List[SpellValidationStrategy]:
        """
        Return a snapshot list of all registered strategies.

        The returned list is a copy; mutating it does not affect the registry.

        Contract:
            Returns the current registry order as a detached list.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._strategies.values())

    # ------------------------------------------------------------------ #
    # Validation entrypoints
    # ------------------------------------------------------------------ #

    def validate_spell(
            self,
            *,
            spell: Spell,
            requirements: Optional[SpellRequirements],
            symbolic_graph: Optional[SpellSymbolicGraph],
            resolution_frame: Optional[SpellResolutionFrame],
            cancel_event: Optional[CancellationEvent] = None,
            validation_pass_cache: Optional[Dict[str, Any]] = None,
    ) -> SpellValidationResult:
        """
        Validate a single spell using all registered strategies.

        Purpose:
            Execute spell-level validation strategies and return a unified: class:`SpellValidationResult` containing all issues.
        Contract:
            - Executes each strategy in registry order against the same context.
            - Appends all reported issues into the result in the order produced.
            - Automatically tags issues with the emitting strategy when missing.
            - Always cleans the validation context (references) on exit.
        Args:
            spell: Spell instance to validate.
            requirements: Phase 1 requirements artifact, if available.
            symbolic_graph: Phase 2 symbolic graph, if available.
            resolution_frame: Phase 3 resolution frame, if available.
            cancel_event: Optional cancellation token.
            validation_pass_cache: Optional pass-scoped memo dict shared across
                all spells validated in one scheduler pass; strategies use it
                to reuse pass-invariant artifacts. None on single-spell paths.
        Returns:
            SpellValidationResult: Aggregated issues for the spell.
        Raises:
            ValueError: If "spell" is None.
            Exception: Propagates any strategy exceptions or cancellation errors.
        """
        self.check_cleaned()
        if spell is None:
            raise ValueError("spell cannot be None.")

        if cancel_event is not None and cancel_event.is_set:
            cancel_event.throw_if_set()

        spellbook: Optional[Spellbook] = spell._spellbook

        issues: List['SpellValidationIssue'] = []

        context = SpellValidationContext(
            spell=spell,
            spellbook=spellbook,
            requirements=requirements,
            symbolic_graph=symbolic_graph,
            resolution_frame=resolution_frame,
            cancel_event=cancel_event,
            issues=issues,
            cleanup_artifacts=False,
            validation_pass_cache=validation_pass_cache,
        )

        # Snapshot strategies under the lock, then run them.
        with self._lock:
            strategies = list(self._strategies.values())

        try:
            for strategy in strategies:
                if cancel_event is not None and cancel_event.is_set:
                    cancel_event.throw_if_set()
                before_count = len(issues)
                strategy.validate(context)
                if len(issues) > before_count:
                    source = type(strategy).__name__
                    for issue in issues[before_count:]:
                        if isinstance(issue, SpellValidationIssue) and issue.source is None:
                            issue.source = source
        finally:
            # Always tear down the context (references, etc.)
            try:
                context.cleanup()
            except Exception:
                pass

        result = SpellValidationResult(
            spell_id=spell.spell_index.selected_spell_id,
            spell_name=spell.spell_name,
            issues=issues,
        )

        return result
