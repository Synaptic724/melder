from typing import Any, Callable, Dict, List, Optional, Protocol, Sequence, Tuple, runtime_checkable
from melder.aether.dev_ops.spell_system_states.spell_state_change_reason import (
    SpellStateChangeReason,
)
from melder.aether.dev_ops.spell_system_states.spell_system_state import (
    SpellSystemState,
)
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell_crafter.spell_requirements_finder.spell_requirements import (
    SpellRequirements,
)
from melder.spellbook.spell_crafter.symbolic_graph.spell_symbolic_graph import (
    SpellSymbolicGraph,
)
from melder.spellbook.spell_types.spell_types import SpellType
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.utilities.interfaces.icleanable import ICleanable
from melder.utilities.interfaces.iconduitresolutionstate import IConduitResolutionState
from melder.utilities.interfaces.icreations import ICreations
from melder.utilities.interfaces.ispellindex import ISpellIndex
from melder.utilities.interfaces.iunitofwork import IUnitOfWork
from melder.utilities.synchronization.counter_switch import CounterSwitch
from melder.utilities.synchronization.cancellation_event_signal import (
    CancellationEvent,
)
from melder.utilities.synchronization.creation_gate_controller import (
    CreationGateController,
)

@runtime_checkable
class _SpellFrameConfigurationSurface(Protocol):
    """Minimal frame-configuration surface borrowed through a spellbook."""

    @property
    def system_state(self) -> Any:
        """Return the current frame system-state value."""
        ...


@runtime_checkable
class _SpellAetherSurface(Protocol):
    """Minimal Aether surface borrowed through a spellbook."""

    def _get_change_control_manager(
            self,
            aetheric_frame: str,
    ) -> object:
        """Return one frame-scoped change-control manager."""
        ...


@runtime_checkable
class ISpellSystemStatesSpellSurface(Protocol):
    """
    Minimal spell-facing view of the structural state registry.

    Purpose:
        Let `ISpell` describe the borrowed lineage-state operations it actually
        needs without importing the full `ISpellSystemStates` protocol back
        into this module and recreating the interface cycle.

    Contract:
        - Supports structural invalidation for one spell lineage.
        - Supports lookup of a `SpellSystemState` by SpellIndex id.
    """

    def mark_structural_change(
            self,
            spell_index: ISpellIndex,
            reason: SpellStateChangeReason = SpellStateChangeReason.structure_changed,
    ) -> None:
        """
        Mark one lineage structurally changed.
        """
        ...

    def get_by_index_id(self, index_id: str) -> Optional[SpellSystemState]:
        """
        Return the state entry for one SpellIndex id, if present.
        """
        ...

    def get_conduit_resolution_state(
            self,
            conduit_id: str,
    ) -> Optional[IConduitResolutionState]:
        """
        Return the conduit-scoped resolution state for one conduit id, if present.
        """
        ...


@runtime_checkable
class ISpellbookSpellSurface(Protocol):
    """
    Minimal spellbook-facing surface consumed by `ISpell`.

    Purpose:
        Keep the spell-owned contract narrow and cycle-safe. The concrete spell
        only borrows spell-system-state access from its owning Spellbook.
    """

    _id: str
    _aetheric_frame: Optional[str]
    _aether: _SpellAetherSurface
    _aetheric_frame_configuration: _SpellFrameConfigurationSurface
    _spellbook_validation_required: bool
    _spell_id_pool: Dict[str, "ISpell"]
    _lookup_contracted_spells: Dict[str, Dict[tuple, ISpellIndex]]
    _contracted_spells: Dict[str, Dict[ISpellIndex, "ISpell"]]
    _spell_system_states: ISpellSystemStatesSpellSurface

    def _run_resolution_phases_for_target_spell(
            self,
            conduit_id: str,
            target_spell: "ISpell",
    ) -> Dict[str, Sequence[IUnitOfWork]]:
        """
        Run target-local conduit resolution phases for one spell.
        """
        ...

    def _run_deferred_resolution_phases_for_target_spell(
            self,
            conduit_id: str,
            target_spell: "ISpell",
    ) -> Dict[str, Sequence[IUnitOfWork]]:
        """
        Run deferred target-local plan phases for one spell.
        """
        ...

    def _set_spellbook_validation_required(self, required: bool) -> None:
        """
        Set the spellbook-level validation-required gate.
        """
        ...


@runtime_checkable
class ISpellCreationContextSurface(Protocol):
    """
    Minimal creation-context execution surface consumed by `Meld`.
    """

    def _execute_no_hooks_no_overrides_compiled(
            self,
            creations: ICreations,
    ) -> Any:
        """Execute the no-hook, no-override runtime lane."""
        ...

    def _execute_no_hooks_overrides_compiled(
            self,
            creations: ICreations,
            override_map: Dict[str, Any],
    ) -> Any:
        """Execute the no-hook override runtime lane."""
        ...

    def _execute_hooks_no_overrides_compiled(
            self,
            creations: ICreations,
    ) -> Tuple[Any, bool]:
        """Execute the hook-aware, no-override runtime lane."""
        ...

    def _execute_hooks_overrides_compiled(
            self,
            creations: ICreations,
            override_map: Dict[str, Any],
    ) -> Tuple[Any, bool]:
        """Execute the hook-aware override runtime lane."""
        ...


@runtime_checkable
class ISpell(ICleanable, Protocol):
    """
    Internal Protocol

    Represents a **registered spell** inside the Melder system.

    A spell is the concrete, runtime blueprint that the `Spellbook` binds and a
    `Conduit` later casts. It wraps:
      - The underlying callable / type (`spell`)
      - Its index handle (`spell_index`)
      - Identity and metadata (`spell_id`, `spellframe`, `binding_name`, `spell_name`)
      - Lifecycle policy (`existence`)
      - Structural profile (`ClassProfile` / `MethodProfile` / `SpellBindingProfile`)
      - Access control (`permissions`)
      - Dependency information (`dependency_graph`, `dependencies`)
      - Conjure-time disposal metadata (`disposal_method_names`, `has_disposal_methods`)
      - Conduit ownership metadata
      - Hook-based lifecycle behavior (pre / activation / post)
      - Per-spell **resolution phase artifacts** (requirements, symbolic graphs,
        local frames, validation flags)

    It is **never** user-facing directly; users call into higher-level APIs
    (Spellbook / Conduit). This protocol describes the shape used internally
    across Melder for type-checking and contracts.
    """

    # ------------------------------------------------------------------
    # Core identity and locking
    # ------------------------------------------------------------------
    _id: str
    _lock: Any

    # ------------------------------------------------------------------
    # Spell metadata / structure
    # ------------------------------------------------------------------
    spell_index: 'ISpellIndex'
    _hooks_enabled: bool
    spell: Any
    spell_id: str
    spellframe: Optional[Any]
    spell_type: 'SpellType'
    user_created_object: Optional[object]
    binding_name: Optional[str]
    spell_name: str
    existence: Existence
    # Profile type broadened to Any to support Binding/Resolution/AI profiles
    profile: Optional[Any]
    aetheric_frame: str

    # Execution policy
    timeout: Optional[int]
    retries: int

    # Permissions
    permissions: Permissions

    # Arbitrary metadata
    tags: List
    metadata: Dict
    _mutation_override: dict
    disposal_method_names: List[str]
    has_disposal_methods: bool

    # Dependency graph + requirements
    dependency_graph: Any
    dependencies: List[str]

    # Spellbook
    _spellbook: Optional['ISpellbookSpellSurface']

    # Per-spell resolution phase artifacts
    # Note: These are populated by the resolution pipeline via SpellCrafter
    _crafter: Optional[Any] # 'SpellCrafter'
    _creation_context: Optional[ISpellCreationContextSurface]
    _creation_context_factory: Optional[Any]
    _creation_context_switch: CounterSwitch
    _dynamic_environment: bool
    resolution_required: bool
    resolution_complete: bool

    # Phase 11 execution-plan metrics (populated during conjure)
    execution_plan_step_count: Optional[int]
    execution_plan_unique_spell_count: Optional[int]
    execution_plan_max_occurrence_depth: Optional[int]
    execution_plan_max_dependency_count: Optional[int]
    execution_plan_has_calln: Optional[bool]
    execution_plan_has_contract_payloads: Optional[bool]
    execution_plan_has_existing_creations: Optional[bool]
    execution_plan_dispatch_route: Optional[str]

    # Ownership (filled after Conduit creation)
    _owner_conduit_id: Optional[str]
    _owner_conduit_name: Optional[str]
    owned_spell: Optional[bool]
    _owner_creations: Optional[ICreations]

    # Lifecycle hooks (private)
    _pre_hooks: Optional[List[Callable[..., Any]]]
    _activation_hooks: Optional[List[Callable[..., Any]]]
    _post_hooks: Optional[List[Callable[..., Any]]]

    _spell_system_states: 'ISpellSystemStatesSpellSurface'
    _key: Tuple[str, str]

    # ------------------------------------------------------------------
    # Key property
    # ------------------------------------------------------------------
    @property
    def key(self) -> Tuple[str, str]:
        """
        Internal

        Returns the canonical `(frame_key, binding_key)` used by the Spellbook
        for dictionary-based lookups. This is always normalized via SpellInputUtils.

        This is intentionally read-only; key semantics are controlled by binding time.
        """
        ...

    @property
    def system_state(self) -> Optional["SpellSystemState"]:
        """
        Return the SpellSystemState instance associated with this Spell's index.

        This is a *view* into the change-control / validation state tracked
        by SpellSystemStates. It is intentionally read-mostly at the Spell layer:

        - Mutation and contract operations can ask for the current state.
        - Higher-level dev-ops / validation pipelines can use this hook to
          inspect or assert state when orchestrating Phase 1-7 revalidation.

        Returns:
            SpellSystemState | None:
                The state object if SpellSystemStates is available and this
                spell has a registered index; otherwise None.
        """
        ...


    def _set_hooks(
            self,
            *,
            pre_hooks: Optional[Sequence[Callable[..., Any]]] = None,
            activation_hooks: Optional[Sequence[Callable[..., Any]]] = None,
            post_hooks: Optional[Sequence[Callable[..., Any]]] = None,
    ) -> None:
        """
        Internal

        Attach lifecycle hook lists and update the hook gate.

        Contract:
            - Replaces only the hook lists provided (None means "leave as-is").
            - Updates `_hooks_enabled` based on current hook list contents.
            - Requires a live Spell instance.

        Args:
            pre_hooks:
                Optional list/tuple of pre-cast hooks.
            activation_hooks:
                Optional list/tuple of activation hooks.
            post_hooks:
                Optional list/tuple of post-cast hooks.
        """
        ...

    def _cleanup_creation_context(self) -> None:
        """
        Internal

        Dispose and clear the spell-owned CreationContext.

        This is used when spell ownership or structural runtime artifacts
        change and the context must be rebuilt on next meld execution.
        """
        ...

    def _get_or_build_creation_context(self) -> ISpellCreationContextSurface:
        """
        Internal

        Resolve or build the spell-owned CreationContext through the spell's
        configured CreationContextFactory.
        """
        ...

    # ------------------------------------------------------------------
    # Mutation override (graph overlay) API
    # ------------------------------------------------------------------
    @property
    def mutation_override(self) -> dict:
        """
        Current mutation override payload for this Spell's DAG.

        This is a *structural overlay* that the mutation pipeline can apply
        to the spell's DI shape in Dynamic / AI-native mode. It is conceptually
        separate from normal SpellMap overrides:

        - SpellMap.spell_override -> per-call / per-site DI override.
        - Spell.mutation_override -> per-spell *graph* overlay used by the
          MutationContract / mutation hub.

        Semantics:
            - An empty dict (`{}`) is treated as "no active overlay" by
              default. The higher-level mutation system may refine this
              distinction later (e.g., between "no overlay" and "explicit
              empty override") but at the Spell level we simply expose the
              raw payload.
        """
        ...

    @property
    def has_mutation_override(self) -> bool:
        """
        Whether this Spell currently has a non-empty mutation overlay.

        This is a convenience for Dynamic / AI-native flows that want a quick
        check before doing more expensive revalidation or graph rebuilds.
        """
        ...

    def invalidate_spell(
            self,
            change_reason: Optional[SpellStateChangeReason] = None,
    ) -> None:
        """
        Invalidate this Spell for a full next-meld rebuild.

        Contract:
            - Requires the spell to be attached to a dynamic runtime
              environment.
            - Clears the spell-owned CreationContext cache.
            - Forces deferred runtime resolution to rerun on the next meld by
              setting `resolution_complete=False` and
              `resolution_required=True`.
            - Marks the lineage structurally gated in SpellSystemStates when
              available, defaulting the reason to `structure_changed`.
            - Models the normal recoverable post-change posture; it does not
              imply transfer-only hard-disable semantics.
        """
        ...

    def apply_mutation_override(self, override: Optional[dict]) -> None:
        """
        Apply or update the DAG-level mutation override for this Spell.

        Contract:
            - Requires the spell to be attached to a dynamic runtime
              environment.
            - Rejects writes when the spell is not running in dynamic mode.

        Instead, it:

        - Updates the local overlay payload; and
        - Delegates to `invalidate_spell(...)` with the appropriate
          mutation-contract change reason.

        The actual rebuild / revalidation of the system graph is expected to
        be driven by the Phase 5-7 pipelines and the mutation hub.

        Args:
            override:
                New overlay payload. `None` or `{}` clears the overlay and
                leaves this Spell in a "no active mutation overlay" state.

        Raises:
            RuntimeError:
                If dynamic mode is not enabled for the spell's current runtime
                ownership context.
        """
        ...

    def clear_mutation_override(self) -> None:
        """
        Clear any active mutation overlay for this Spell.

        Contract:
            - Requires the spell to be attached to a dynamic runtime
              environment.
            - Rejects writes when the spell is not running in dynamic mode.

        This resets the local overlay payload back to the default empty dict,
        then delegates to `invalidate_spell(...)` with the cleared mutation
        reason.

        The actual effect on the compiled/system DAG is owned by the higher-
        level mutation / validation pipelines.

        Raises:
            RuntimeError:
                If dynamic mode is not enabled for the spell's current runtime
                ownership context.
        """
        ...


    # ------------------------------------------------------------------
    # Introspection Helpers
    # ------------------------------------------------------------------
    @property
    def is_existing_creation(self) -> bool:
        """
        Returns True if this spell represents an existing, pre-created object
        (EXISTING_CREATION* SpellTypes), rather than a factory.
        """
        ...

    @property
    def is_class_spell(self) -> bool:
        """
        Returns True if this spell represents a class-based factory (SPELL* SpellTypes).
        """
        ...

    @property
    def is_method_spell(self) -> bool:
        """
        Returns True if this spell represents a non-lambda method/function spell.
        """
        ...

    @property
    def is_lambda_spell(self) -> bool:
        """
        Returns True if this spell represents a lambda-based method spell.
        """
        ...

    @property
    def has_existing_object(self) -> bool:
        """
        Return whether this spell currently holds a user-provided existing object.

        This is only meaningful for EXISTING_CREATION* spell types. Other spell
        kinds should report ``False`` here even when they later resolve to live
        creations through normal factory behavior.
        """
        ...

    @property
    def owner_conduit_info(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Return ``(owner_conduit_id, owner_conduit_name)`` for this spell.

        Returns:
            tuple[Optional[str], Optional[str]]:
                Conduit ownership tuple when conduit wiring has been attached;
                otherwise ``(None, None)``.
        """
        ...

    # ------------------------------------------------------------------
    # Ownership / configuration API
    # ------------------------------------------------------------------
    def _add_owned_conduit(
            self,
            conduit_id: str,
            conduit_name: Optional[str] = None,
            creations: Any = None,
            *,
            dynamic_environment: bool,
            creation_gate_controller: 'CreationGateController',
    ) -> None:
        """
        Internal

        Records ownership information about the Conduit that "owns" this spell.

        This is used to:
        - Attach the spell to a specific Conduit identity (for logging, diagnostics, and scoping).
        - Provide a handle to the Conduit's creation scope (e.g., for singletons tied to that conduit).
        - Reconfigure spell-owned CreationContextFactory ownership wiring.

        Args:
            conduit_id:
                The unique ID of the conduit that owns this spell.
            conduit_name:
                Human-readable name of the owning conduit, if available.
            creations:
                Conduit-level creations container used for managing shared instances.
            dynamic_environment:
                True when the owning conduit runs in dynamic mode.
            creation_gate_controller:
                Frame-owned CreationGateController used by CreationContextFactory.
        """
        ...

    def _add_build_details(
            self,
            dag: Any,
            dependencies: List[str],
    ) -> None:
        """
        Internal

        Attach static build-time dependency graph details to this spell.

        This is typically invoked by the SpellCrafter / DAG builder after it has
        analyzed the spell's parameters and constructed a dependency DAG.

        Args:
            dag:
                A static DAG representation for this spell's dependency structure.
                This object is considered immutable at runtime and may expose a
                `dispose()` method for cleanup.
            dependencies:
                A list of spell_ids (SHA256 fingerprints) that this spell depends on.

        Raises:
            ValueError:
                If `dag` is None or `dependencies` is None.
        """
        ...

    # ------------------------------------------------------------------
    # Resolution Phase Artifacts (read-only view)
    # ------------------------------------------------------------------
    @property
    def requirements(self) -> Optional['SpellRequirements']:
        """
        Return the Phase 1 requirements artifact for this spell, if present.

        This is populated by :meth:`run_phase_requirements` via
        :class:`SpellCrafter`.
        """
        ...

    @property
    def symbolic_graph(self) -> Optional["SpellSymbolicGraph"]:
        """
        Return the Phase 2 symbolic graph for this spell, if present.

        This is populated by :meth:`run_phase_symbolic_graph` via
        :class:`SpellCrafter`.
        """
        ...

    @property
    def resolution_frame(self) -> Any:
        """
        Return the Phase 3 local resolution frame / DAG for this spell, if present.

        This is populated by :meth:`run_phase_local_frame` via
        :class:`SpellCrafter`. Concrete type is intentionally opaque here;
        callers should treat it as an internal resolution artifact.
        """
        ...

    @property
    def validation_result_phase4(self) -> Any:
        """
        Return the Phase 4 validation result for this spell, if present.

        This is populated by :meth:`run_phase_validation` via
        :class:`SpellCrafter`.
        """
        ...

    @property
    def validation_result_phase6(self) -> Any:
        """
        Return the Phase 6 validation result for this spell, if present.

        This is populated by :meth:`run_phase_validation` via
        :class:`SpellCrafter`.
        """
        ...

    @property
    def validated(self) -> bool:
        """
        Return whether this spell currently reports a validated state.
        """
        ...

    @property
    def is_broken(self) -> bool:
        """
        Return whether this spell currently reports a broken / unsafe state.
        """
        ...

    # ------------------------------------------------------------------
    # Resolution / compilation phases
    # ------------------------------------------------------------------
    def run_phase_requirements(
            self,
            cancel_event: Optional['CancellationEvent'] = None,
    ) -> None:
        """
        Phase 1 - Requirements Extraction (facade).

        Delegates to :class:`SpellCrafter` to:

            - Inspect the spell's constructor/signature and metadata.
            - Determine dependencies (spellframes, binding names, types, etc.).
            - Capture existence constraints that are relevant to resolution.

        Side effects:
            - Stores a :class:`SpellRequirements` instance inside the crafter.

        The return value is intentionally ignored at the Spell level; callers
        should access :attr:`requirements` if they need the artifact.
        """
        ...

    def run_phase_symbolic_graph(
            self,
            cancel_event: Optional['CancellationEvent'] = None,
    ) -> None:
        """
        Phase 2 - Symbolic Graph Construction (facade).

        Delegates to :class:`SpellCrafter`.

        In the full implementation, this will:

            - Use Phase 1 requirements to construct a per-spell symbolic graph.
            - Represent DI relationships as nodes/edges, without binding to
              concrete creations yet.

        The Spell class does not use the return value; later phases read
        artifacts via the crafter if needed.
        """
        ...

    def run_phase_local_frame(
            self,
            cancel_event: Optional['CancellationEvent'] = None,
    ) -> None:
        """
        Phase 3 - Local Resolution Frame / DAG (facade).

        Delegates to :class:`SpellCrafter`.

        In the full implementation, this will:

            - Translate the symbolic graph into a concrete, per-spell
              resolution frame / local DAG.
            - Encode the order and actions required for resolution.
            - Eventually push the final DAG into this Spell via
              :meth:`_add_build_details`.

        The Spell class does not use the return value; later phases read
        artifacts via the crafter if needed.
        """
        ...

    def run_phase_validation(
            self,
            cancel_event: Optional['CancellationEvent'] = None,
    ) -> None:
        """
        Phase 4 - Validation (facade).

        Delegates to :class:`SpellCrafter`.

        In the full implementation, this will:

            - Validate the resolution frame and requirements.
            - Populate underlying validation results.
            - Set validated/broken flags.

        The Spell class does not use the return value; callers consult
        :attr:`validated` and :attr:`is_broken`.
        """
        ...

    def run_phase_root_blueprints(
            self,
            conduit_id: str,
            cancel_event: Optional['CancellationEvent'] = None,
    ) -> None:
        """
        Phase 5 - Root blueprint construction (facade).

        Delegates to the SpellCrafter to build system-level DAG blueprints
        and a SpellSystemIndex for the current frame.

        Contract:
            - Requires Phase 4 to have completed successfully.
            - Does not return a value; artifacts are stored on the crafter.
            - Does not execute later phases.

        Args:
            conduit_id:
                Conduit identifier used to scope resolution artifacts.
            cancel_event:
                Optional cancellation signal shared across the scheduler.

        Returns:
            None.
        """
        ...

    def run_phase_occurrence_plan(
            self,
            conduit_id: str,
            cancel_event: Optional['CancellationEvent'] = None,
    ) -> None:
        """
        Phase 8 - Occurrence plan compilation (facade).

        Delegates to :class:`SpellCrafter` to compile an OccurrencePlan for
        root spells. Non-root spells are treated as a no-op.

        Contract:
            - Requires Phase 5 artifacts to be available.
            - Does not return a value; artifacts are stored on the crafter.
            - Does not execute later phases.

        Args:
            conduit_id:
                Conduit identifier used to scope resolution artifacts.
            cancel_event:
                Optional cancellation signal shared across the scheduler.

        Returns:
            None.
        """
        ...

    def run_phase_system_validation(
            self,
            conduit_id: str,
            cancel_event: Optional['CancellationEvent'] = None,
    ) -> None:
        """
        Phase 6 - System-level validation (facade).

        Delegates to the SpellCrafter to validate system-level DAG integrity
        and update index validity states.

        Contract:
            - Requires Phase 5 to have completed successfully.
            - Does not return a value; results are stored on the crafter.
            - Does not execute later phases.

        Args:
            conduit_id:
                Conduit identifier used to scope resolution artifacts.
            cancel_event:
                Optional cancellation signal shared across the scheduler.

        Returns:
            None.
        """
        ...

    def run_phase_change_control(
            self,
            conduit_id: str,
            cancel_event: Optional['CancellationEvent'] = None,
    ) -> None:
        """
        Phase 7 - Change-control wiring (facade).

        Delegates to the SpellCrafter to ensure change-control wiring and
        component-of indexing are prepared for this frame.

        Contract:
            - Requires Phase 5 artifacts to be available.
            - Does not return a value; wiring occurs inside the crafter.

        Args:
            conduit_id:
                Conduit identifier used to scope resolution artifacts.
            cancel_event:
                Optional cancellation signal shared across the scheduler.

        Returns:
            None.
        """
        ...

    def run_structural_phases(
            self,
            cancel_event: Optional['CancellationEvent'] = None,
    ) -> None:
        """
        Convenience helper to run **structural phases only** (1-4) for this spell.

        Phases executed via the :class:`SpellCrafter`:

            1. Requirements extraction.
            2. Symbolic graph construction.
            3. Local resolution frame / DAG construction.
            4. Validation (structural only).

        Each phase honours the optional :class:`CancellationEvent`. If the
        event is set, the underlying phase methods will raise via
        ``cancel_event.throw_if_set()``.

        Raises:
            Exception: Propagates exceptions raised by the underlying phases.
        """
        ...

    def run_all_phases(
            self,
            conduit_id: str,
            cancel_event: Optional['CancellationEvent'] = None,
    ) -> None:
        """
        Convenience helper to run **all compiler / resolution phases** for this spell, in order.

        Phases executed via the :class:`SpellCrafter`:

            - Phase 1: Requirements extraction.
            - Phase 2: Symbolic graph construction.
            - Phase 3: Local resolution frame / DAG construction.
            - Phase 4: Validation.
            - Phase 5: Root blueprint construction.
            - Phase 8: Occurrence plan compilation.
            - Phase 6: System validation.
            - Phase 7: Change-control wiring.

        Each phase honours the optional :class:`CancellationEvent`. If the
        event is set, the underlying phase methods will raise via
        ``cancel_event.throw_if_set()``.

        Args:
            conduit_id:
                Conduit identifier used to scope resolution artifacts.
            cancel_event:
                Optional cancellation signal shared across the scheduler.
        """
        ...
