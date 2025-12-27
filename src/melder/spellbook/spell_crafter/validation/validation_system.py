from threading import RLock
from typing import Any, Dict, List, Optional
# Melder imports
from melder.spellbook.spell_crafter.validation.spell_validation_context import SpellValidationContext
from melder.spellbook.spell_crafter.validation.spell_validation_result import SpellValidationResult
# Strategies
from melder.spellbook.spell_crafter.validation.strategies.circular_dependency_strategy import CircularDependencyStrategy
from melder.spellbook.spell_crafter.validation.strategies.dangling_dependency_strategy import \
    DanglingDependenciesStrategy
from melder.spellbook.spell_crafter.validation.strategies.required_holes_strategy import RequiredHolesStrategy
from melder.spellbook.spell_crafter.validation.strategies.resolution_frame_presence_strategy import \
    ResolutionFramePresenceStrategy
from melder.spellbook.spell_crafter.validation.strategies.self_validation_strategy import SelfDependencyStrategy
from melder.spellbook.spell_crafter.validation.strategies.duplicate_spell_name_strategy import DuplicateSpellNameStrategy
from melder.spellbook.spell_crafter.validation.strategies.annotation_shape_guard_strategy import (
    AnnotationShapeGuardStrategy,
)
from melder.spellbook.spell_crafter.validation.strategies.spellmap_shape_validation_strategy import (
    SpellMapShapeValidationStrategy,
)
from melder.spellbook.spell_crafter.validation.strategies.parameter_policy_strategy import (
    ParameterPolicyStrategy,
)
from melder.spellbook.spell_crafter.validation.strategies.callable_profile_hygiene_strategy import (
    CallableProfileHygieneStrategy,
)
from melder.spellbook.spell_crafter.validation.strategies.existing_creation_compatibility_strategy import (
    ExistingCreationCompatibilityStrategy,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.interfaces import ISpell, ISpellbook
from melder.spellbook.spell_crafter.symbolic_graph.spell_symbolic_graph import (
    SpellSymbolicGraph,
)
from melder.spellbook.spell_crafter.spell_examiner.spell_requirements_finder.spell_requirements import (
    SpellRequirements,
)
from melder.spellbook.spell_crafter.spell_examiner.profiles.resolution_profile import (
    SpellResolutionFrame,
)
from melder.spellbook.spell_crafter.spellbook_scanner import SpellbookScanner
from melder.utilities.synchronization.cancellation_event_signal import (
    CancellationEvent,
)
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg


class SpellValidationSystem(Cleanable):
    """
    Central registry + runner for spell validation strategies.

    Typical usage
    -------------
    * Phase 4 of the SpellCrafter creates a ``SpellValidationSystem``.
    * Built-in strategies are auto-registered in the constructor.
    * :meth:`validate_spell` is invoked with a fully-built spell context.
    * The returned :class:`SpellValidationResult` is stored on the crafter
      and surfaced via :attr:`Spell.validated` / :attr:`Spell.is_broken`.

    The system itself is **ephemeral** – it is created per validation run
    and cleaned up afterwards. Strategies are owned by the system and are
    also cleaned when the system is cleaned.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_strategies",
    ]

    def __init__(self) -> None:
        super().__init__()
        self._lock: RLock = RLock()
        self._strategies: Dict[str, 'SpellValidationStrategy'] = {}
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

        self._lock = None

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
        self.register_strategy(ParameterPolicyStrategy())
        self.register_strategy(CallableProfileHygieneStrategy())
        self.register_strategy(ExistingCreationCompatibilityStrategy())

    def register_strategy(self, strategy: 'SpellValidationStrategy') -> None:
        """
        Register (or replace) a validation strategy.

        Args:
            strategy:
                The strategy instance to register. Its ``name`` property is
                used as the key.

        Raises:
            ValueError:
                If ``strategy`` is None or has an empty name.
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

    def iter_strategies(self) -> List['SpellValidationStrategy']:
        """
        Return a snapshot list of all registered strategies.

        The returned list is a copy; mutating it does not affect the registry.
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
            spell: ISpell,
            requirements: Optional[SpellRequirements],
            symbolic_graph: Optional[SpellSymbolicGraph],
            resolution_frame: Optional[SpellResolutionFrame],
            cancel_event: Optional[CancellationEvent] = None,
    ) -> 'SpellValidationResult':
        """
        Validate a single spell using all registered strategies.
        """
        self.check_cleaned()
        if spell is None:
            raise ValueError("spell cannot be None.")

        if cancel_event is not None and cancel_event.is_set:
            cancel_event.throw_if_set()

        # Try to obtain the owning Spellbook without resorting to getattr.
        spellbook: Optional[ISpellbook]
        try:
            spellbook = spell._spellbook
        except AttributeError:
            spellbook = None

        scanner: Optional[SpellbookScanner] = None
        if spellbook is not None:
            scanner = SpellbookScanner(spellbook)

        issues: List['SpellValidationIssue'] = []

        context = SpellValidationContext(
            spell=spell,
            spellbook=spellbook,
            requirements=requirements,
            symbolic_graph=symbolic_graph,
            resolution_frame=resolution_frame,
            scanner=scanner,
            cancel_event=cancel_event,
            issues=issues,
        )

        # Snapshot strategies under the lock, then run them.
        with self._lock:
            strategies = list(self._strategies.values())

        try:
            for strategy in strategies:
                if cancel_event is not None and cancel_event.is_set:
                    cancel_event.throw_if_set()
                strategy.validate(context)
        finally:
            # Always tear down the context (scanner, references, etc.)
            try:
                context.cleanup()
            except Exception:
                pass

        result = SpellValidationResult(
            spell_id=spell.spell_index.current,
            spell_name=spell.spell_name,
            issues=issues,
        )

        return result
