from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Protocol,
    Sequence,
    Set,
    Tuple,
    runtime_checkable,
)

from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.symbolic_graph.spell_symbolic_graph import (
    SpellSymbolicGraph,
)
from melder.aether.spellbook.spell_compiler.system.spell_system_validation_state import (
    SpellSystemValidationState,
)
from melder.aether.spellbook.spell_compiler.validation.spell_validation_result import (
    SpellValidationResult,
)
from melder.aether.spellbook.spell_types.spell_types import SpellType
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.utilities.interfaces.icleanable import ICleanable
from melder.utilities.interfaces.icreations import ICreations
from melder.utilities.interfaces.ispellindex import ISpellIndex
from melder.utilities.interfaces.ispellrequirements import ISpellRequirements
from melder.utilities.interfaces.ispellsystemstates import ISpellSystemStates
from melder.utilities.synchronization.counter_switch import CounterSwitch
from melder.utilities.synchronization.creation_gate_controller import (
    CreationGateController,
)
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state_change_reason import (
    SpellStateChangeReason,
)
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_state import (
    SpellSystemState,
)

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
    _compiler_artifact: "SpellCompilerArtifact"
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
    _spellbook: "ISpellbook"

    # Per-spell resolution phase artifacts
    # Note: These are populated by the resolution pipeline.
    _creation_context: Any
    _creation_context_factory: Optional["ICreationContextFactory"]
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

    _spell_system_states: ISpellSystemStates
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

    def _get_or_build_creation_context(self) -> Any:
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

        This is typically invoked by the structural DAG builder after it has
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
    def requirements(self) -> Optional['ISpellRequirements']:
        """
        Return the Phase 1 requirements artifact for this spell, if present.

        This is populated by structural phase execution.
        """
        ...

    @property
    def symbolic_graph(self) -> Optional["SpellSymbolicGraph"]:
        """
        Return the Phase 2 symbolic graph for this spell, if present.

        This is populated by structural phase execution.
        """
        ...

    @property
    def resolution_frame(self) -> Any:
        """
        Return the Phase 3 local resolution frame / DAG for this spell, if present.

        This is populated by structural phase execution. Concrete type is
        intentionally opaque here;
        callers should treat it as an internal resolution artifact.
        """
        ...

    @property
    def validation_result_phase4(self) -> Optional[SpellValidationResult]:
        """
        Return the Phase 4 validation result for this spell, if present.

        This is populated by structural phase execution.
        """
        ...

    @property
    def validation_result_phase6(self) -> Optional[SpellSystemValidationState]:
        """
        Return the Phase 6 validation result for this spell, if present.

        This is populated by conduit-scoped validation.
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

