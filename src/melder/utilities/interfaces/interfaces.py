import threading
from threading import RLock
from types import ModuleType
from typing import runtime_checkable, Type, Protocol, Optional, List, Union, Dict, Any, Iterable, Iterator, Callable, \
    Tuple, Mapping, Set, Sequence, Self

from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.dev_ops.spell_system_states.spell_state_change_reason import SpellStateChangeReason
from melder.spellbook.existence.existence import Existence
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent


@runtime_checkable
class ICleanable(Protocol):
    """
    Protocol definition for Cleanable.

    This protocol mirrors the public API of the Cleanable
    abstract base class.
    """

    _cleaned: bool

    @property
    def cleaned(self) -> bool:
        """Returns True if the object has already been cleaned."""
        ...

    @property
    def is_cleaned(self) -> bool:
        """Alias for `cleaned`."""
        ...

    def check_cleaned(self) -> None:
        """
        Check if the object has been cleaned.

        Raises:
            RuntimeError: If the object has already been cleaned.
        """
        ...

    def  cleanup(self) -> None:
        """
        Dispose must be implemented by subclasses.

        Must:
        -----
        - Release all resources.
        - Deregister or finalize any allocations.
        - Be idempotent (safe to call multiple times).
        """
        ...

    async def async_cleanup(self) -> None:
        """
        Dispose must be implemented by subclasses.

        Must:
        -----
        - Release all resources.
        - Deregister or finalize any allocations.
        - Be idempotent (safe to call multiple times).
        """
        ...



@runtime_checkable
class ICreations(ICleanable, Protocol):
    """
    Manages all instantiated objects within a Conduit (Normal Scope).

    This manager is responsible for tracking object instances based on their lifecycle
    (`unique`, `unique_per_scope`, `many`, etc.) and enforcing resource disposal upon cleaning.

    **Key Responsibilities:**
      * Storage and lifecycle management of created objects.
      * Controlled resource disposal via `ICleanable` or configured cleanup methods.
    """

    # -----------------
    # Attributes
    # -----------------
    _lock: RLock
    _unique: 'Dict[str, object]'
    _unique_per_scope: 'Dict[str, object]'
    _many: 'Dict[str, List[object]]'
    _unique_per_lineage: 'Dict[str, object]'
    _unique_per_cluster: 'Dict[str, object]'
    _disposal_enabled: bool
    _disposal_method_names: List[str]
    _id: str

    # -----------------
    # Methods
    # -----------------
    def _cleanup_unique(self) -> List[Exception]:
        """
        Internal

        Disposes of all objects registered under the `unique` existence scope.

        Returns:
            List[Exception]: List of any cleanup errors encountered.
        """
        ...

    def _cleanup_unique_per_lineage(self) -> List[Exception]:
        """
        Internal

        Disposes of all objects registered under the `unique_per_lineage` existence scope.

        Returns:
            List[Exception]: List of any cleanup errors encountered.
        """
        ...

    def _cleanup_unique_per_cluster(self) -> List[Exception]:
        """
        Internal

        Disposes of all objects registered under the `unique_per_cluster` existence scope.

        Returns:
            List[Exception]: List of any cleanup errors encountered.
        """
        ...

    def _cleanup_unique_per_scope(self) -> List[Exception]:
        """
        Internal

        Disposes of all objects registered under the `unique_per_scope` existence scope.

        Returns:
            List[Exception]: List of any cleanup errors encountered.
        """
        ...

    def _cleanup_many(self) -> List[Exception]:
        """
        Internal

        Disposes of all multi-instance objects registered under the `many` existence scope.

        Returns:
            List[Exception]: List of any cleanup errors encountered.
        """
        ...

    def _attempt_cleanup(self, item: object) -> Optional[Exception]:
        """
        Internal

        Attempt to clean up an object strictly via a prioritized list of method names.

        Behavior:
          - Returns None if `item` is None or disposal is disabled.
          - Iterates `self._disposal_method_names` in order (e.g., ["cleanup", "close", "dispose"]).
          - For the first attribute found on `item` that is callable, calls it.
          - If the call succeeds, returns None.
          - If the call raises, returns a RuntimeError wrapping the original exception.
          - If no listed methods exist on the object, returns None (treated as no-op).

        Notes:
          - No Protocol/type checks are performed.
          - Cleanup semantics are entirely defined by the configured method list.

        Args:
            item: The object instance to dispose.

        Returns:
            Optional[Exception]: RuntimeError if a chosen cleanup method raised; otherwise None.
        """
        ...

    def _upgrade_from_lesser_conduit(self, **kwargs: Any) -> None:
        """
        Internal

        Transfers creations data from a `LesserCreations` instance during a conduit upgrade.

        Args:
            **kwargs: Dictionary containing creation scopes (e.g., `unique_per_scope`, `many`).

        Raises:
            RuntimeError: If the `Creations` manager already contains objects before transfer.
        """
        ...

    def add_unique(self, key: str, item: object) -> None:
        """
        Adds a singleton object instance to the `unique` scope.

        Args:
            key (str): Unique identifier (Spell ID).
            item (object): Object instance to manage.

        Raises:
            RuntimeError: If the Creations manager is cleaned.
            ValueError: If the key already exists in the `unique` scope.
        """
        ...

    def add_unique_per_lineage(self, key: str, item: object) -> None:
        """
        Adds a singleton object instance to the `unique_per_lineage` scope.

        Args:
            key (str): Unique identifier (Spell ID).
            item (object): Object instance to manage.

        Raises:
            RuntimeError: If the Creations manager is cleaned.
            ValueError: If the key already exists in the `unique_per_lineage` scope.
        """
        ...

    def add_unique_per_cluster(self, key: str, item: object) -> None:
        """
        Adds a singleton object instance to the `unique_per_cluster` scope.

        Args:
            key (str): Unique identifier (Spell ID).
            item (object): Object instance to manage.

        Raises:
            RuntimeError: If the Creations manager is cleaned.
            ValueError: If the key already exists in the `unique_per_cluster` scope.
        """
        ...

    def add_unique_per_scope(self, key: str, item: object) -> None:
        """
        Adds a singleton object instance to the `unique_per_scope` scope.

        Args:
            key (str): Unique identifier (Spell ID).
            item (object): Object instance to manage.

        Raises:
            RuntimeError: If the Creations manager is cleaned.
            ValueError: If the key already exists in the `unique_per_scope` scope.
        """
        ...

    def add_many(self, key: str, item: object) -> None:
        """
        Adds an object instance to a multi-instance collection under the `many` scope.

        If the collection for the given key does not exist, it is created.

        Args:
            key (str): Collection identifier (Spell ID).
            item (object): Object instance to add.

        Raises:
            RuntimeError: If the Creations manager is cleaned.
        """
        ...


@runtime_checkable
class ILesserCreations(ICleanable, Protocol):
    """
    Manages instantiated objects within a **Lesser Conduit** (Child Scope).

    Lesser Creations is a reduced scope manager, only tracking objects with
    `unique_per_scope` and `many` lifecycles, as other scopes (`unique`, etc.)
    are delegated to the parent Conduit.

    **Key Responsibilities:**
      * Storage and disposal of local-scope objects.
      * Providing a snapshot of local objects for transfer during an upgrade.
    """

    # -----------------
    # Attributes
    # -----------------
    _unique_per_scope: Dict[str, object]
    _many: Dict[str, List[object]]
    _disposal_enabled: bool
    _disposal_method_names: List[str]
    _lock: RLock
    _id: str

    # -----------------
    # Methods
    # -----------------
    def _cleanup_unique_per_scope(self) -> List[Exception]:
        """
        Internal

        Disposes of all objects registered under the `unique_per_scope` existence scope.

        Returns:
            List[Exception]: List of any cleanup errors encountered.
        """
        ...

    def _cleanup_many(self) -> List[Exception]:
        """
        Internal

        Disposes of all multi-instance objects registered under the `many` existence scope.

        Returns:
            List[Exception]: List of any cleanup errors encountered.
        """
        ...

    def _attempt_cleanup(self, item: object) -> Optional[Exception]:
        """
        Internal

        Attempt to clean up an object strictly via a prioritized list of method names.

        Behavior:
          - Returns None if `item` is None or disposal is disabled.
          - Iterates `self._disposal_method_names` in order (e.g., ["cleanup", "close", "dispose"]).
          - For the first attribute found on `item` that is callable, calls it.
          - If the call succeeds, returns None.
          - If the call raises, returns a RuntimeError wrapping the original exception.
          - If no listed methods exist on the object, returns None (treated as no-op).

        Args:
            item: The object instance to dispose.

        Returns:
            Optional[Exception]: RuntimeError if a chosen cleanup method raised; otherwise None.
        """
        ...

    def transfer_data_and_clear(self) -> Dict[str, Any]:
        """
        Creates a lightweight snapshot of the current creations, clears the internal state, and cleans the manager.

        This is used when a Lesser Conduit is upgraded to a Normal Conduit, transferring ownership of local creations.

        Returns:
            dict: A dictionary containing copies of the internal state (`unique_per_scope` and `many`).
        """
        ...

    def add_unique_per_scope(self, key: str, item: object) -> None:
        """
        Adds a singleton object instance to the `unique_per_scope` scope.

        Args:
            key (str): Unique identifier (Spell ID).
            item (object): Object instance to manage.

        Raises:
            RuntimeError: If the Creations manager is cleaned.
            ValueError: If the key already exists in the `unique_per_scope` scope.
        """
        ...

    def add_many(self, key: str, item: object) -> None:
        """
        Adds an object instance to a multi-instance collection under the `many` scope.

        If the collection for the given key does not exist, it is created.

        Args:
            key (str): Collection identifier (Spell ID).
            item (object): Object instance to add.

        Raises:
            RuntimeError: If the Creations manager is cleaned.
        """
        ...
@runtime_checkable
class ISpell(ICleanable, Protocol):
    """
    Internal Protocol

    Represents a **registered spell** inside the Melder system.

    A spell is the concrete, runtime blueprint that the `Spellbook` binds and a
    `Conduit` later casts. It wraps:
      - The underlying callable / type (`spell`)
      - Its lineage handle (`spell_index`)
      - Identity and metadata (`spell_id`, `spellframe`, `binding_name`, `spell_name`)
      - Lifecycle policy (`existence`)
      - Structural profile (`ClassProfile` / `MethodProfile` / `SpellBindingProfile`)
      - Access control (`permissions`)
      - Dependency information (`dependency_graph`, `dependencies`)
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
    spell_index: 'SpellIndex'
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

    # Dependency graph + requirements
    dependency_graph: Any
    dependencies: List[str]

    # Spellbook
    _spellbook: Optional['ISpellbook']

    # Per-spell resolution phase artifacts
    # Note: These are populated by the resolution pipeline via SpellCrafter
    resolution_profile: Optional['SpellResolutionProfile']
    _crafter: Optional[Any] # 'SpellCrafter'

    # Ownership (filled after Conduit creation)
    _owner_conduit_id: Optional[str]
    _owner_conduit_name: Optional[str]
    owned_spell: Optional[bool]
    _owner_creations: Any

    # Lifecycle hooks (private)
    _pre_hooks: Optional[List[Callable[..., Any]]]
    _activation_hooks: Optional[List[Callable[..., Any]]]
    _post_hooks: Optional[List[Callable[..., Any]]]

    _spell_system_states: 'ISpellSystemStates'
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
        Return the SpellSystemState instance associated with this Spell's lineage.

        This is a *view* into the change-control / validation state tracked
        by SpellSystemStates. It is intentionally read-mostly at the Spell layer:

        - Mutation and contract operations can ask for the current state.
        - Higher-level dev-ops / validation pipelines can use this hook to
          inspect or assert state when orchestrating Phase 1–7 revalidation.

        Returns:
            SpellSystemState | None:
                The state object if SpellSystemStates is available and this
                spell has a registered lineage; otherwise None.
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

    def apply_mutation_override(self, override: Optional[dict]) -> None:
        """
        Apply or update the DAG-level mutation override for this Spell.

        Instead, it:

        - Updates the local overlay payload; and
        - Marks the Spell's lineage as structurally changed via
          SpellSystemStates (if available), using a mutation_contract_*
          change reason.

        The actual rebuild / revalidation of the system graph is expected to
        be driven by the Phase 5-7 pipelines and the mutation hub.

        Args:
            override:
                New overlay payload. `None` or `{}` clears the overlay and
                leaves this Spell in a "no active mutation overlay" state.
        """
        ...

    def clear_mutation_override(self) -> None:
        """
        Clear any active mutation overlay for this Spell.

        This resets the local overlay payload back to the default empty dict,
        and, if SpellSystemStates is available, marks the lineage as having
        rolled back a mutation.

        The actual effect on the compiled/system DAG is owned by the higher-
        level mutation / validation pipelines.
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
        Returns True if this spell currently holds a user-provided existing object.

        This is only meaningful for EXISTING_CREATION* SpellTypes; for other types
        it will always be False.
        """
        ...

    @property
    def owner_conduit_info(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Returns `(owner_conduit_id, owner_conduit_name)` if this spell has
        been attached to a specific Conduit, otherwise `(None, None)`.
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
    ) -> None:
        """
        Internal

        Records ownership information about the Conduit that "owns" this spell.

        This is used to:
        - Attach the spell to a specific Conduit identity (for logging, diagnostics, and scoping).
        - Provide a handle to the Conduit's creation scope (e.g., for singletons tied to that conduit).

        Args:
            conduit_id:
                The unique ID of the conduit that owns this spell.
            conduit_name:
                Human-readable name of the owning conduit, if available.
            creations:
                Conduit-level creations container used for managing shared instances.
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
        Phase 1 artifact for this spell, if it has been computed.

        This is populated by :meth:`run_phase_requirements` via :class:`SpellCrafter`.
        """
        ...

    @property
    def symbolic_graph(self) -> Optional["SpellSymbolicGraph"]:
        """
        Phase 2 symbolic graph for this spell, if it has been computed.

        This is populated by :meth:`run_phase_symbolic_graph` via :class:`SpellCrafter`.
        """
        ...

    @property
    def resolution_frame(self) -> Any:
        """
        Phase 3 local resolution frame / DAG for this spell, if it has been computed.

        This is populated by :meth:`run_phase_local_frame` via :class:`SpellCrafter`.
        Concrete type is intentionally opaque here; callers should treat it as
        an internal resolution artifact.
        """
        ...

    @property
    def validation_result_phase4(self) -> Any:
        """
        Phase 4 validation result for this spell, if it has been computed.

        This is populated by :meth:`run_phase_validation` via :class:`SpellCrafter`.
        """
        ...

    @property
    def validation_result_phase6(self) -> Any:
        """
        Phase 6 validation result for this spell, if it has been computed.

        This is populated by :meth:`run_phase_validation` via :class:`SpellCrafter`.
        """
        ...

    @property
    def validated(self) -> bool:
        """
        True if the validation phase has run and marked this spell as validated.
        """
        ...

    @property
    def is_broken(self) -> bool:
        """
        True if the validation phase classified this spell as broken / unsafe.
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
        Phase 1 – Requirements Extraction (facade).

        Delegates to :class:`SpellCrafter` to:

            - Inspect the spell’s constructor/signature and metadata.
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
        Phase 2 – Symbolic Graph Construction (facade).

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
        Phase 3 – Local Resolution Frame / DAG (facade).

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
        Phase 4 – Validation (facade).

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

    def run_phase_system_validation(
            self,
            conduit_id: str,
            cancel_event: Optional['CancellationEvent'] = None,
    ) -> None:
        """
        Phase 6 - System-level validation (facade).

        Delegates to the SpellCrafter to validate system-level DAG integrity
        and update lineage validity states.

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

            1. Requirements extraction.
            2. Symbolic graph construction.
            3. Local resolution frame / DAG construction.
            4. Validation.
            5. Root blueprint construction.
            6. System validation.
            7. Change-control wiring.

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



@runtime_checkable
class ISpellIndex(ICleanable, Protocol):
    """
    Interface for a **SpellIndex**: a stable, hashable dictionary key that
    points to a mutable version ID (e.g., a SHA256 commit or spell version).

    Design:
        * Hashing and equality are based **only** on an immutable ULID.
        * The "current" version pointer is mutable and thread-safe.
        * The object is safe to use as a dictionary key even while the
          version pointer changes over time.
        * Tracks the full lineage of versions via an internal version set.

    Typical usage:
        * As a key into spell registries:
              Dict[SpellIndex, ISpell]
        * As a stable lineage handle for spell mutation/versioning.
        * As a synchronization primitive when multiple threads need to
          reason about "which version is active" without breaking key
          identity in maps.
    """

    # ------------------------------------------------------------------
    # Core backing fields (shape only; concrete type lives in impl)
    # ------------------------------------------------------------------
    _id: str
    _current_id: Optional[str]
    _lock: Any
    _cleaned: bool
    _versions: Optional[Set[str]]

    # ------------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------------
    @property
    def current(self) -> Optional[str]:
        """
        Gets the currently active version ID (e.g., SHA256) this index points to.

        Returns:
            Optional[str]:
                The current version ID, or ``None`` if the index has
                been cleaned.
        """
        ...

    def update(self, new_id: str) -> None:
        """
        Atomically updates the pointer to a new version ID.

        This operation is thread-safe and does **not** affect the
        object's hash or its location in any dictionary.

        Args:
            new_id:
                The new version ID (e.g., SHA256 commit ID) to point to.
        """
        ...

    def get_all_versions(self) -> Set[str]:
        """
        Retrieves all version IDs that this index has ever pointed to.

        Returns:
            Set[str]:
                A copy of the internal set of all version IDs seen for
                this lineage.
        """
        ...

    def has_version(self, version_id: str) -> bool:
        """
        Checks whether this index has ever pointed to the specified
        version ID.

        Args:
            version_id:
                The version ID to check for.

        Returns:
            bool:
                ``True`` if the version ID is present in the lineage
                set, ``False`` otherwise.
        """
        ...

    @property
    def id(self) -> str:
        """
        Returns the immutable, unique ULID that serves as the stable
        identity for this index.

        This is the only value used for hashing and equality.
        """
        ...

    # ------------------------------------------------------------------
    # Dict-safety / identity semantics
    # ------------------------------------------------------------------
    def __hash__(self) -> int:
        """
        Produces a hash based **only** on the immutable ULID.

        This guarantees a stable hash even when the current version
        pointer changes, making the object safe as a dictionary key.
        """
        ...

    def __eq__(self, other: object) -> bool:
        """
        Compares two SpellIndex instances based solely on their
        immutable ULIDs.

        Args:
            other:
                Another object to compare to.

        Returns:
            bool:
                ``True`` if ``other`` is a SpellIndex/ISpellIndex with
                the same ULID; otherwise ``False``.
        """
        ...

    def __repr__(self) -> str:
        """
        Returns a developer-friendly representation of the index state,
        typically including the ULID and current version ID.
        """
        ...

    # ------------------------------------------------------------------
    # Context manager support
    # ------------------------------------------------------------------
    def __enter__(self) -> "ISpellIndex":
        """
        Context manager entry.

        Typical behavior in the concrete implementation:
            * Performs a cleaned check.
            * Acquires the internal lock.
            * Returns ``self``.
        """
        ...

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """
        Context manager exit.

        Typical behavior in the concrete implementation:
            * Releases the internal lock regardless of outcome.
        """
        ...



@runtime_checkable
class ISpellbook(ICleanable, Protocol):
    """
    Interface for a **Spellbook**: the central authority for spell definitions,
    bindings, configuration, and contract-based sharing.

    This interface reflects the *SpellIndex-native* implementation:

    * Local and contracted spells are keyed by `SpellIndex` (lineage).
    * Version SHAs are tracked via `SpellIndex._versions` plus:
        - `_spell_versions`  (local)
        - `_contracted_versions` (per-conduit)
    * Current spell_id maps are maintained for owned and contracted spells.

    The Spellbook participates in:
      * Local binding + lifecycle (`bind`, `Existence`)
      * Cross-conduit contracts (via ConduitWard/Contract)
      * Aether frame configuration and global registry
      * Conduit conjuration (execution scope)
    """

    # ------------------------------------------------------------------
    # Core backing fields (shape only; concrete types live in impl)
    # ------------------------------------------------------------------
    _lookup_contracted_spells: Optional[Any]
    _lookup_spells: Optional[Any]
    _contracted_spells: Optional[Any]
    _contracted_versions: Optional[Any]
    _contracted_spells_by_id: Optional[Any]
    _spells: Optional[Any]
    _spell_versions: Optional[Any]
    _spells_by_id: Optional[Any]
    _bind: Optional[Any]
    _id: str
    _aetheric_frame: Optional[str]
    _configuration: Optional['IConfiguration']

    # Spell Validator
    _spell_validator: 'SpellValidationSystem'
    _spell_system_states: 'ISpellSystemStates'

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------
    @property
    def spells(self) -> Mapping[ISpellIndex, ISpell]:
        """
        Public API

        Returns a read-only view of the **local spells** registered
        in this Spellbook.

        This provides safe introspection of the local registry without
        allowing external mutation.

        Returns:
            Mapping[SpellIndex, ISpell]:
                An immutable map of `SpellIndex` → spell object.
        """
        ...

    @property
    def contracted_spells(self) -> Mapping[str, Mapping[ISpellIndex, ISpell]]:
        """
        Public API

        Returns a per-conduit read-only view of all **borrowed** spells.

        Each peer conduit ID maps to its own immutable
        `SpellIndex → ISpell` map.

        Returns:
            Mapping[str, Mapping[SpellIndex, ISpell]]:
                Immutable map of peer Conduit ID → immutable map of
                borrowed spells.
        """
        ...

    def snapshot_state(self) -> Dict[str, Any]:
        """
        Public API

        Build a read-only snapshot of Spellbook state.

        Purpose:
            Provide a stable view of local and contracted spell registries while
            transactions may be in-flight.
        Contract:
            - Returns detached copies of internal maps; mutating the snapshot
              does not affect the Spellbook registries.
            - Includes a snapshot id for observability.
        Returns:
            Dict[str, Any]: Snapshot payload containing local/contracted maps
            and lookup caches.
        """
        ...

    # ------------------------------------------------------------------
    # Binding / inspection / lookup API
    # ------------------------------------------------------------------
    def bind(
            self,
            spell: Any,
            existence: str | Existence,
            *,
            permissions: str = "create",
            spellframe: Any = None,
            binding_name: Any = None,
            **kwargs: Any,
    ) -> str:
        """
        Public API

        Binds a spell into the Spellbook for future instantiation and
        dependency injection.

        This method profiles the spell, computes a unique SHA256 ID,
        stores it locally, and assigns lifecycle + permission policies.

        Binding requires an active binding transaction. Use
        ``begin_transaction("bind")`` (or ``begin_binding_transaction()``)
        before binding and ``end_binding_transaction()`` once registration
        is complete.

        Permissions (access control to other conduits):
            - ``"read"``:
                Other conduits may *use* the spell but not create
                new instances.
            - ``"create"`` (default):
                Other conduits may both use *and* create instances.
            - ``"block"``:
                Completely blocks access from other conduits; only
                the owning conduit may use it.

        Existence (spell lifecycle):
            Controls how instances are managed (e.g., `Existence.unique`,
            `Existence.many`, etc.).

        Lifecycle hooks (optional ``**kwargs``):
            - ``pre_hooks``:
                List[Callable] executed *before* the spell is constructed.
            - ``activation_hooks``:
                List[Callable] executed *during* spell construction.
            - ``post_hooks``:
                List[Callable] executed *after* the spell has been cast.

        Args:
            spell:
                The class, function, or object to bind.
            existence:
                The lifecycle scope for this spell.
            permissions:
                Permission level exposed to other conduits:
                ``"read"``, ``"create"``, or ``"block"``.
            spellframe:
                Logical interface/namespace or grouping label.
            binding_name:
                Secondary key to distinguish this spell within its frame.
            **kwargs:
                Optional lifecycle hooks: ``pre_hooks``,
                ``activation_hooks``, ``post_hooks``.

        Returns:
            str: The primary SHA256 ``spell_id`` for the head version.

        Raises:
            RuntimeError:
                If a spell with the same ID already exists in the Aether registry.
            RuntimeError:
                If no binding transaction is active for this Spellbook.
            TypeError:
                If any provided hook is not callable.
            ValueError:
                If the ``permissions`` string cannot be converted into a
                valid `Permissions` enum.
        """
        ...


    def scan(self, module: ModuleType) -> list[str]:
        """
        Public API

        Scan a module for `scan_bind`-decorated objects and bind them.

        This is a module-only scan: it does not traverse packages or import
        submodules. Any object marked with `scan_bind` must originate from the
        scanned module, otherwise the scan fails.

        Scanning requires an active binding transaction. Use
        ``begin_transaction("bind")`` (or ``begin_binding_transaction()``)
        before scanning and ``end_binding_transaction()`` once registration
        is complete.

        Args:
            module (ModuleType): The module to scan for decorated spell targets.
        Returns:
            list[str]: Spell IDs bound during the scan, in module dict order.
        Raises:
            TypeError: If `module` is not a module or metadata is invalid.
            ValueError: If a decorated object is not owned by the module.
            RuntimeError: If no binding transaction is active for this Spellbook.
            RuntimeError: Propagated from Spellbook.bind on binding errors.
        """
        ...

    def begin_binding_transaction(self) -> None:
        """
        Public API

        Begin a binding transaction for this Spellbook.

        Purpose:
            Enable binding operations (bind/scan) in a controlled transaction window.
        Contract:
            - Only one binding transaction may be active at a time.
            - While active, `bind(...)` and `scan(...)` are allowed.
            - When inactive, `bind(...)` and `scan(...)` raise.
        Returns:
            None.
        Raises:
            RuntimeError: If a binding transaction is already active.
        """
        ...

    def begin_transaction(
            self,
            transaction_type: "ChangeTransactionType | str",
            *,
            conduit_id: Optional[str] = None,
            conduit_ids: Optional[Iterable[str]] = None,
            scope_keys: Optional[Iterable[str]] = None,
            scope_hashes: Optional[Iterable[str]] = None,
            binding_keys: Optional[Iterable[Tuple[str, str]]] = None,
            contract_keys: Optional[Iterable[Tuple[str, str, str]]] = None,
            metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Public API

        Begin a change-control transaction for this Spellbook.

        Purpose:
            Admit a mutation request through the ChangeControlManager and,
            for bind transactions, open the binding transaction window.
        Contract:
            - Only one change-control transaction may be active per Spellbook.
            - Admission is serialized by the ChangeControlOrchestrator.
            - Bind transactions open the binding transaction window.
            - Scan is not a transaction type; it must run inside a bind transaction.
        Args:
            transaction_type:
                Transaction type enum or string value (e.g. "bind", "link").
            conduit_id:
                Optional initiator conduit id for logging.
            conduit_ids:
                Optional list of conduits participating in the request.
            scope_keys:
                Optional normalized scope keys for conflict checks.
            scope_hashes:
                Optional normalized scope hashes for conflict checks.
            binding_keys:
                Optional binding keys affected by the request.
            contract_keys:
                Optional contract keys affected by the request.
            metadata:
                Optional structured metadata for diagnostics.
        Returns:
            None.
        Raises:
            RuntimeError: If a change transaction is already active.
            RuntimeError: If binding transaction is already active for bind requests.
            RuntimeError: If change-control admission is denied.
            ValueError: If transaction_type is invalid.
            TypeError: If transaction_type has an invalid type.
        """
        ...

    def end_transaction(
            self,
            transaction_type: "ChangeTransactionType | str | None" = None,
    ) -> None:
        """
        Public API

        End the active change-control transaction for this Spellbook.

        Purpose:
            Finalize an admitted change-control request and release any
            implicit embargo state tracked by the ChangeControlManager.
        Contract:
            - Ends the active request tracked by this Spellbook.
            - Bind transactions close the binding transaction window.
            - Raises if no change transaction is active.
        Args:
            transaction_type:
                Optional transaction type assertion for safety checks.
        Returns:
            None.
        Raises:
            RuntimeError: If no change transaction is active.
            RuntimeError: If transaction_type does not match the active request.
            ValueError: If transaction_type is invalid.
            TypeError: If transaction_type has an invalid type.
        """
        ...

    def end_binding_transaction(self) -> None:
        """
        Public API

        End the active binding transaction for this Spellbook.

        Purpose:
            Disable binding operations until a new transaction is started.
        Contract:
            - Binding transactions must be explicitly closed.
            - When inactive, `bind(...)` and `scan(...)` raise.
        Returns:
            None.
        Raises:
            RuntimeError: If no binding transaction is active.
        """
        ...

    def binding_transaction(self) -> "ISpellbook":
        """
        Public API

        Context-managed binding transaction for this Spellbook.

        Contract:
            - Starts a binding transaction on entry.
            - Ends the transaction on exit, even if an exception is raised.
            - Nested usage raises on begin (transaction already active).
        Returns:
            ISpellbook: The current Spellbook instance.
        Raises:
            RuntimeError: If a binding transaction is already active.
        """
        ...

    def create_binder(
            self,
            *,
            default_existence: Existence = Existence.unique,
            default_permissions: str = "create",
    ) -> 'SpellBinder':
        """
        Public API

        Creates a `SpellBinder` instance that provides an Autofac-style
        fluent syntax on top of `Spellbook.bind(...)`.

        This does *not* introduce a new registration path; it simply
        forwards everything into the existing binding pipeline so all
        reflection, `SpellIndex` construction, `SpellType` classification,
        and validation flows remain exactly the same. :contentReference[oaicite:1]{index=1}

        Example:
            binder = spellbook.create_binder()

            binder.bind(MyService) \\
                  .as_unique() \\
                  .under_spellframe(IMyServiceProtocol) \\
                  .named("primary") \\
                  .with_permissions("create") \\
                  .finalize()

            # Reuse the same binder for another spell:
            binder.bind(OtherService, existence=Existence.many).finalize()

        Args:
            default_existence (Existence):
                Default lifecycle scope for fluent registrations started via
                this binder.

            default_permissions (str):
                Default permissions for fluent registrations (e.g. "create").

        Returns:
            SpellBinder:
                A reusable fluent registration helper bound to this Spellbook.
        """
        ...

    def inspect_spell(self, spell: Any, aetheric_frame: str = "default") -> Optional[str]:
        """
        Public API

        Inspects an object instance to determine its unique SHA256 ID,
        then checks if that ID is registered anywhere in the Aether
        Registry for the given frame.

        Args:
            spell:
                The object to inspect (class, function, or instance).
            aetheric_frame:
                The Aether frame to check against.

        Returns:
            Optional[str]:
                The spell_id if the spell is registered in the Aether,
                otherwise ``None``.
        """
        ...

    def find_spell_index(
            self,
            spellframe: str,
            spell_name: str,
            binding_name: str,
    ) -> Optional[ISpellIndex]:
        """
        Public API

        Finds a spell's **SpellIndex** (lineage identifier) using its
        logical identifiers.

        Lookup order:
            1. Local spells
            2. Contracted (borrowed) spells

        Args:
            spellframe:
                Logical namespace or grouping label.
            spell_name:
                Name of the spell class or function.
            binding_name:
                Secondary key used to distinguish this spell.

        Returns:
            Optional[SpellIndex]:
                The SpellIndex representing this spell's lineage.

        Raises:
            RuntimeError:
                If the spell is not found locally or in any contracted
                spellbook.
        """
        ...

    def find_spell_key(
            self,
            spellframe: str,
            spell_name: str,
            binding_name: str,
    ) -> Optional[Tuple[str, str]]:
        """
        Public API

        Finds a spell's **primary lookup key** using its logical
        identifiers.

        The search checks local spells first, then contracted spells.

        Args:
            spellframe:
                Logical namespace or grouping label.
            spell_name:
                Name of the spell class or function.
            binding_name:
                Secondary key to distinguish this spell.

        Returns:
            Optional[tuple[str, str]]:
                The normalized lookup key
                ``(frame_or_name, binding_name_or_default)`` if found.

        Raises:
            RuntimeError:
                If the key cannot be found (local or contracted).
        """
        ...

    def get_spell_permissions(self, spell_index: ISpellIndex) -> Optional[str]:
        """
        Public API

        Retrieves the access permissions for a **locally** registered spell.

        Args:
            spell_index:
                The SpellIndex (lineage) of the spell.

        Returns:
            Optional[str]:
                The permissions name (``"read"``, ``"create"``, or
                ``"block"``) for this spell.

        Raises:
            RuntimeError:
                If the spell with the given index is not found in the
                local spellbook.
        """
        ...

    # ------------------------------------------------------------------
    # Internal local/contracted lookup + version cache API
    # ------------------------------------------------------------------
    def _find_spell(self, spell_index: ISpellIndex) -> Optional[ISpell]:
        """
        Internal

        Locates a **local** spell by its `SpellIndex`.

        Args:
            spell_index:
                The SpellIndex of the spell to find.

        Returns:
            Optional[ISpell]:
                The spell object if found, else ``None``.
        """
        ...

    def _find_contracted_spell(self, spell_index: ISpellIndex) -> Optional[ISpell]:
        """
        Internal

        Locates a **contracted** spell by its `SpellIndex` by searching
        across all peer conduit maps.

        Args:
            spell_index:
                The SpellIndex of the contracted spell.

        Returns:
            Optional[ISpell]:
                The spell object if found.

        Raises:
            RuntimeError:
                If the contracted spell cannot be found in any peer
                contract map.
        """
        ...

    def _find_spell_count(self) -> int:
        """
        Internal

        Returns the total number of **locally registered** spells.

        Returns:
            int: Count of local spells.
        """
        ...

    def _find_contracted_spell_count(self) -> int:
        """
        Internal

        Returns the number of **peer conduits** this spellbook currently
        has contracts with (i.e., how many contracted spell maps exist).

        Returns:
            int: Number of active contract links (peer conduits).
        """
        ...

    def _check_all_spells(self) -> None:
        """
        Internal

        Performs a system check to verify that no locally bound spell
        version ID is already registered in the global Aether registry
        for this frame.

        Raises:
            RuntimeError:
                If any spell version is already present in Aether for
                this frame.
        """
        ...

    def _refresh_local_spell_versions(self) -> None:
        """
        Internal

        Rebuilds the local version cache (`_spell_versions`) from the
        current set of `SpellIndex` keys in `_spells`.

        Useful after bulk mutation or research operations that may have
        changed the version lists on `SpellIndex` instances.
        """
        ...

    def _refresh_contracted_spell_versions(self) -> None:
        """
        Internal

        Rebuilds the per-conduit contracted version caches
        (`_contracted_versions`) from the current `_contracted_spells`
        structure.

        After this runs:
            * Each `conduit_id` in `_contracted_spells` will have a
              corresponding `Set[str]` in `_contracted_versions`
              containing **all version IDs** (SHA256) for that
              conduit’s spells.
        """
        ...

    def _refresh_all_spell_versions(self) -> None:
        """
        Internal

        Convenience method to refresh **both** local and contracted spell
        version caches in a single call.

        Calls:
            * ``_refresh_local_spell_versions()``
            * ``_refresh_contracted_spell_versions()``
        """
        ...

    # ------------------------------------------------------------------
    # spell_id map helpers (internal)
    # ------------------------------------------------------------------
    def _register_owned_spell_id(self, spell_id: str, spell: ISpell) -> None:
        """
        Internal

        Register the current spell_id mapping for an owned spell.

        Args:
            spell_id:
                Current version id for the spell.
            spell:
                Owned spell instance.

        Raises:
            RuntimeError:
                If the spell_id map is missing or the id collides.
        """
        ...

    def _update_owned_spell_id(self, old_id: str, new_id: str, spell: ISpell) -> None:
        """
        Internal

        Update the owned spell_id mapping after a SpellIndex version change.

        Args:
            old_id:
                Previous version id for the lineage.
            new_id:
                New version id for the lineage.
            spell:
                Owned spell instance.

        Raises:
            RuntimeError:
                If the old id is missing or the new id collides.
        """
        ...

    def _register_contracted_spell_id(
            self,
            conduit_id: str,
            spell_id: str,
            spell: ISpell,
    ) -> None:
        """
        Internal

        Register the current spell_id mapping for a contracted spell.

        Args:
            conduit_id:
                Peer conduit id for the contract.
            spell_id:
                Current version id for the spell.
            spell:
                Contracted spell instance.

        Raises:
            RuntimeError:
                If the contracted map is missing or the id collides.
        """
        ...

    def _update_contracted_spell_id(
            self,
            conduit_id: str,
            old_id: str,
            new_id: str,
            spell: ISpell,
    ) -> None:
        """
        Internal

        Update the contracted spell_id mapping after a SpellIndex version change.

        Args:
            conduit_id:
                Peer conduit id for the contract.
            old_id:
                Previous version id for the lineage.
            new_id:
                New version id for the lineage.
            spell:
                Contracted spell instance.

        Raises:
            RuntimeError:
                If the old id is missing or the new id collides.
        """
        ...

    def _unregister_contracted_spell_id(
            self,
            conduit_id: str,
            spell_id: str,
            spell: ISpell,
    ) -> None:
        """
        Internal

        Remove a contracted spell_id mapping for the given conduit.

        Args:
            conduit_id:
                Peer conduit id for the contract.
            spell_id:
                Current version id for the spell.
            spell:
                Contracted spell instance.

        Raises:
            RuntimeError:
                If the id is missing from the contracted map.
        """
        ...

    # ------------------------------------------------------------------
    # Contract / link API (used by ConduitWard / Contract)
    # ------------------------------------------------------------------
    def _find_contracted_spell_by_id(
            self,
            spell_id: str,
            conduit_id: str,
    ) -> Optional[ISpell]:
        """
        Internal

        Resolves a contracted spell by its **version SHA** using the
        Spellbook’s local copies of contracted spells.

        Each contracted spell’s `SpellIndex` contains all known versions,
        so this can be resolved purely from local SpellIndex data.

        Args:
            spell_id:
                The version SHA of the spell.
            conduit_id:
                The contracting peer conduit ID.

        Returns:
            Optional[ISpell]:
                The resolved spell if found, otherwise ``None``.
        """
        ...

    def _create_link_contract(self, conduit_id: str) -> None:
        """
        Internal

        Initializes the internal storage maps for a **new contract link**
        with a peer conduit.

        Ensures that:
            * `_contracted_spells[conduit_id]`
            * `_lookup_contracted_spells[conduit_id]`
            * `_contracted_versions[conduit_id]`
            * `_contracted_spells_by_id[conduit_id]`

        are created **atomically** and remain in a consistent state.

        Args:
            conduit_id:
                The ID of the peer conduit to create the contract
                structure for.

        Raises:
            RuntimeError:
                If the contract structure is present in some maps but not
                all (inconsistent state).
        """
        ...

    def _remove_link_contract(self, conduit_id: str) -> None:
        """
        Internal

        Removes the internal storage maps for a **dissolved** contract
        link with a peer conduit.

        This removes all three maps in lockstep:

            * `_contracted_spells[conduit_id]`
            * `_lookup_contracted_spells[conduit_id]`
            * `_contracted_versions[conduit_id]`
            * `_contracted_spells_by_id[conduit_id]`

        Args:
            conduit_id:
                The ID of the peer conduit whose contract structure
                should be removed.

        Raises:
            RuntimeError:
                If the contract structure is present in some maps but not
                all (inconsistent cleanup).
        """
        ...

    def _add_contracted_spell(self, spell: ISpell, conduit_id: str) -> None:
        """
        Internal

        Adds a specific spell (borrowed from a peer) into the
        **contracted spells** registry and updates the key + version
        caches for the given conduit, plus the spell_id map.

        Args:
            spell:
                The spell object to add.
            conduit_id:
                The ID of the peer conduit this spell was contracted
                from.
        """
        ...

    def _remove_contracted_spell(self, spell_id: str, conduit_id: str) -> None:
        """
        Internal

        Removes a specific contracted spell from the internal registry,
        identified by its **version SHA** and peer conduit.

        Steps:
            * Locate `SpellIndex` whose versions contain `spell_id`.
            * Remove from `_contracted_spells[conduit_id]`.
            * Remove from `_lookup_contracted_spells[conduit_id]`.
            * Remove all versions for this SpellIndex from
              `_contracted_versions[conduit_id]`.
            * Remove from `_contracted_spells_by_id[conduit_id]`.

        Args:
            spell_id:
                The version SHA of the spell to remove.
            conduit_id:
                The ID of the peer conduit the spell was contracted from.

        Raises:
            RuntimeError:
                If the conduit maps do not exist or the target version
                cannot be found.
        """
        ...

    def _clear_contracted_spells_for_conduit(self, conduit_id: str) -> None:
        """
        Internal

        Clears **all spells** associated with a contracted conduit, while
        retaining the contract structure, clearing its id map, and
        zeroing its version cache.

        Args:
            conduit_id:
                The ID of the peer conduit whose contracted spells are
                to be cleared.

        Raises:
            RuntimeError:
                If no contracted spell maps exist for the given conduit.
        """
        ...

    def _sever_link_contract(self, conduit_id: str) -> None:
        """
        Internal

        Fully severs the link contract for a given conduit ID:

            1. Calls ``_clear_contracted_spells_for_conduit(conduit_id)``
               to zero out spells.
            2. Calls ``_remove_link_contract(conduit_id)`` to remove the
               underlying contract structure.

        Args:
            conduit_id:
                The ID of the peer conduit whose contract is to be
                severed.
        """
        ...

    # ------------------------------------------------------------------
    # Configuration / Aether frame API
    # ------------------------------------------------------------------
    def is_configuration_locked(self) -> bool:
        """
        Public API

        Indicates whether this Spellbook's configuration has been
        **frozen** (locked) for its Aether frame.

        Returns:
            bool: ``True`` if locked, ``False`` otherwise.
        """
        ...

    def configure_aether_frame(
            self,
            *,
            system_state: Optional[str],
            debugging: Optional[bool],
            disposal: Optional[bool],
            disposal_method_names: Optional[List[str]],
            logger_factory: Optional[Callable[[object], Any]] = None,
            use_default_std_logger: bool = False,
    ) -> None:
        """
        Public API

        Consolidated setup for this Spellbook's **Aether frame**:

          1. (Optional) Install a logger factory on the configuration.
          2. Apply provided configuration properties.
          3. Validate + freeze configuration.
          4. Bind the configuration to the Aether.
          5. Optionally upgrade the Aether logger.

        Once frozen during this call, the configuration becomes
        immutable.

        Args:
            system_state:
                System mode (e.g. ``"automatic"`` or ``"dynamic"``).
            debugging:
                Enables or disables internal debugging features such as
                id tagging.
            disposal:
                Enables automatic resource disposal when conduits are
                cleaned.
            disposal_method_names:
                Method names to invoke on created objects during
                disposal.
            logger_factory:
                Optional logger factory to install before freezing.
            use_default_std_logger:
                If True and `logger_factory` is not provided, installs
                the default StdLoggerFactory via `set_logger_factory()`.

        Raises:
            RuntimeError:
                If configuration is already locked/cleaned.
            KeyError:
                If an unknown configuration key is provided.
            ValueError:
                If configuration fails validation.
            TypeError:
                If the provided logger factory is invalid.
        """
        ...

    def get_configuration(self) -> 'IConfiguration':
        """
        Public API

        Returns the active configuration object for this Spellbook.

        Returns:
            IConfiguration: The configuration instance used by this
            Spellbook's Aether frame.
        """
        ...

    # ------------------------------------------------------------------
    # Conduit / cloning API
    # ------------------------------------------------------------------
    def create_new_preset_spellbook(self) -> "ISpellbook":
        """
        Internal

        Creates a new `Spellbook` instance that shares the same
        **Aether frame** and **Configuration** as the current
        Spellbook.

        Used internally when upgrading a lesser conduit into a normal
        conduit with a fresh Spellbook that reuses the existing frame +
        configuration.

        Returns:
            ISpellbook:
                A new Spellbook instance ready for use by a normal
                conduit.
        """
        ...

    def conjure(
            self,
            policy: Optional[str] = "automatic",
            name: Optional[str] = None,
            conduit_logger: Any | None = None,
    ) -> Any:
        """
        Public API

        Creates a new **Conduit** (execution channel) from this Spellbook.

        This method finalizes configuration (if needed), validates all
        local spells, and instantiates the Conduit.

        Args:
            policy:
                Spell access control behavior for this conduit.
                Must map to a `Policies` enum member (e.g. "automatic",
                "dynamic", "whitelist_all", "block_all").
            name:
                Optional name for the conduit.
            conduit_logger:
                Optional logger instance to attach to the Conduit.

        Returns:
            Any:
                The newly created Conduit instance.

        Raises:
            RuntimeError:
                If this Spellbook has already conjured a Conduit (only
                one allowed per Spellbook).
            RuntimeError:
                If dynamic policies are used while `system_state` is
                ``"automatic"``.
            ValueError:
                If configuration fails validation or the policy string is
                invalid.
        """
        ...


@runtime_checkable
class IUnitOfWork(ICleanable, Protocol):
    """
    Future-based encapsulation of a single unit of work, with integrated
    cancellation support via :class:`CancellationEvent` and explicit cleanup.

    This class extends both:

        * :class:`Cleanable` – deterministic, idempotent cleanup semantics.
        * :class:`concurrent.futures.Future` – result(), exception(), callbacks, etc.

    It **does not** own threads or an executor:

        * You construct a UnitOfWork with a callable + args + optional cancel event.
        * You then either:
            - Call :meth:`run_synchronously` on whatever thread should do the work, or
            - Treat the instance itself as a callable (``threading.Thread(target=uow)``),
              or
            - Use it inside your own worker loop / pipeline.

        * The UnitOfWork:
            - Performs an up-front check of its associated :class:`CancellationEvent`
              (if provided).
            - Executes the callable.
            - Records `set_result` or `set_exception` on the underlying Future.

    Thread-safety & coordination
    ----------------------------

    * A per-instance :class:`threading.RLock` (_lock) protects access to internal
      state that can be cleaned or mutated.
    * Most public operations call :meth:`check_cleaned` to enforce lifecycle rules.
    * ``with UnitOfWork(...) as uow:`` acquires the internal lock for the caller,
      allowing you to safely read/update metadata or coordinate multi-step actions.

    Cleanup semantics
    -----------------

    * :meth:`cleanup` is idempotent.
    * Once cleaned:
        - All internal references (func, args, kwargs, cancel_event, metadata) are
          nulled out.
        - The internal lock is set to None.
        - Subsequent guarded operations will fail via :meth:`check_cleaned` or by
          detecting that the lock is None.
    """

    _label: Optional[str]
    _metadata: Any
    _cancel_event: Optional[CancellationEvent]

    def cleanup(self) -> None:
        """
        Deterministically tear down this UnitOfWork, clearing references and
        disabling further use.

        Behavior:
            * Idempotent – safe to call multiple times.
            * Clears:
                - The wrapped callable and its bound args/kwargs.
                - The associated CancellationEvent.
                - Any label/metadata.
            * Marks the object as cleaned and drops the internal lock.

        After cleanup:
            * :meth:`check_cleaned` will cause most operations to raise
              ``RuntimeError("UnitOfWork has been cleaned.")``.
            * The underlying Future's internal state (result/exception) is left
              as-is so any awaiting code can still observe the final outcome.
        """
        ...

    def __enter__(self) -> Self:
        """
        Enter a critical section protected by this UnitOfWork's internal lock.

        This lets callers coordinate multiple operations under a single
        lock acquisition, for example:

            with uow:
                # inspect / tweak metadata atomically
                info = uow.metadata
                ...

        Note:
            This lock is **only** for UnitOfWork's own fields
            (func/args/kwargs/metadata/cancel_event), not the internal
            lock used by :class:`Future`.
        """
        ...

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Exit the critical section entered via :meth:`__enter__`.

        The internal lock is always released.
        """
        ...

    @property
    def cancel_event(self) -> Optional[CancellationEvent]:
        """
        The :class:`CancellationEvent` associated with this unit of work, if
        any.

        Worker code or the underlying callable may use this to perform
        additional cooperative cancellation checks beyond the up-front check
        done in :meth:`run_synchronously`.
        """
        ...

    @property
    def label(self) -> Optional[str]:
        """
        Optional human-readable label for this UnitOfWork.

        This is useful for logging, debugging, or exposing information to AI
        agents (e.g. tagging a unit with spell IDs and stage names).
        """
        ...

    @property
    def metadata(self) -> Any:
        """
        Arbitrary metadata attached to this unit of work.

        This can be used to attach spell identifiers, ResolutionContext
        instances, stage markers, or any other information a supervising
        pipeline wants to keep track of.
        """
        ...

    def run_synchronously(self) -> Any:
        """
        Execute the unit of work on the **current** thread.

        This is the core execution path that:

            * Ensures the UnitOfWork has not been cleaned.
            * Performs an up-front cancellation check using the associated
              :class:`CancellationEvent`, if any.
            * Invokes the underlying callable with its bound args/kwargs.
            * Records the result or exception on the underlying Future.

        It can be used directly:

            result = uow.run_synchronously()

        Or indirectly by passing the UnitOfWork instance itself as a callable:

            thread = threading.Thread(target=uow)
            thread.start()

        Returns:
            Any: The result of the underlying callable.

        Raises:
            OperationCancelledError:
                If cancellation was requested via the associated
                :class:`CancellationEvent` prior to execution.
            Exception:
                Any exception raised by the underlying callable. It will also
                be recorded on the underlying Future and re-raised here.
        """
        ...

    def __call__(self) -> Any:
        """
        Convenience alias that executes this unit of work synchronously on
        the caller's thread.

        This is equivalent to :meth:`run_synchronously`. It is mainly
        provided so that UnitOfWork instances can be passed to APIs that
        expect a plain callable (e.g. ad-hoc thread targets or custom
        worker loops).
        """
        ...

    def result(self, timeout: Optional[float] = None) -> Any:
        ...

    def exception(self, timeout: Optional[float] = None) -> BaseException | None:
        ...

    def add_done_callback(self, fn: Callable[[Any], Any]) -> None:
        ...

    def done(self) -> bool:
        ...

    def cancelled(self) -> bool:
        ...


@runtime_checkable
class IBind(ICleanable, Protocol):
    """
    An Interface for a binding mechanism, responsible for profiling and
    registering a spell blueprint.
    """
    _id: str
    def bind(
            self,
            permissions: Permissions,
            existence : Existence,
            *,
            aetheric_frame: str,
            spell=None,
            spellframe=None,
            binding_name=None,
    ) -> Union[ISpell, Any]:
        """
        Binds a spell, creating its blueprint and returning it.

        Args:
            permissions (Permissions): The access policy for the spell.
            aetheric_frame (str): The Aetheric Frame this bind is part of.
            spell (Any, optional): The class, function, or object to bind.
            spellframe (Any, optional): The logical interface or group.
            binding_name (str, optional): A unique binding name.
            existence (str, optional): The lifecycle policy.

        Returns:
            Union[ISpell, Any]: The newly created ISpell blueprint.
        """
        ...

@runtime_checkable
class IMeld(ICleanable, Protocol):
    """
    An Interface for the object resolution (melding) process.

    This is responsible for taking a spell request, resolving its dependencies,
    and "casting" it into a live object instance.
    """
    _id: str
    def meld(
            self,
            spell_name: str | None = None,
            *,
            spell: str | object | None = None,
            spellframe: str | object | None = None,
            binding_name: str | None = None,
            spell_override: Optional[dict | list | tuple] = None,
    ) -> Optional[Any]:
        """
        Resolves and creates an instance of a spell.

        Args:
            spell_name (str, optional): Logical spell name key (string).
            spell (str | object, optional): Spell id (string) or spell object.
            spellframe (str | object, optional): Spellframe / protocol / frame key.
            binding_name (str, optional): Binding name used for lookup.
            spell_override (dict | list | tuple, optional): Per-call override payload.
        """
        ...

@runtime_checkable
class IConduitWard(ICleanable, Protocol):
    """
    ConduitWard manages the dynamic linking, lineage, and permission policy
    for a single conduit within the Melder framework.

    Key Responsibilities:
    * **Contract Management:** Maintains thread-safe contracts defining shared spells with other conduits.
    * **Lineage Tracking:** Handles the tree structure via parent and lesser conduit tracking.
    * **Policy Enforcement:** Enforces conduit access policies (e.g., whitelist, block, dynamic).

    Contract Directionality:
    * `_initiated_index`: Tracks links this conduit has initiated (outbound).
    * `_received_index`: Tracks links where this conduit has been the provider target (inbound).
    """

    # Core fields (structural)
    _conduit: 'IConduit'
    _logger: 'ISafeLogger'
    _dynamic: bool
    _conduit_type: 'ConduitState'
    _id: str
    _display_name: str
    _log_groups: List[str]
    _log_sysgroups: List[str]
    _policy_set: bool
    _policy: Optional['Policies']
    _initiated_index: Dict[str, str]
    _received_index: Dict[str, str]
    _contracts: 'Dict[str, Contract]'
    _parent_conduit: Optional['IConduit']
    _root_conduit: Optional['IConduit']
    _lesser_conduits: 'Dict[str, IConduit]'
    _lock: Any

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------
    def cleanup(self) -> None:
        """
        Public API

        Cleanups the conduit ward, preventing any further modifications or operations.
        """
        ...

    def _clean_up_lesser_conduits_links(self) -> None:
        """
        Internal

        Recursively cleans up and removes all linked lesser conduits (children).
        """
        ...

    def _clean_up_links(self) -> None:
        """
        Internal

        cleans and disposes of all active external contracts and links.
        """
        ...

    def cleanup_all_lesser_conduits(self) -> None:
        """
        Public API

        Cleans up all lesser conduits (children) linked to this conduit.

        This is typically used when the parent conduit is undergoing a state change,
        like an upgrade to a normal state, or as part of a controlled shutdown.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        ...

    # ------------------------------------------------------------------
    # Context Manager
    # ------------------------------------------------------------------
    def __enter__(self) -> 'IConduitWard':
        """
        Enters the context manager for Aether.
        """
        ...

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """
        Exits the context manager for Aether.
        """
        ...

    # ------------------------------------------------------------------
    # Change Control
    # ------------------------------------------------------------------
    def begin_transaction(
            self,
            transaction_type: "ChangeTransactionType | str",
            *,
            conduit_ids: Optional[Iterable[str]] = None,
            conduits: Optional[Iterable["IConduit"]] = None,
            scope_keys: Optional[Iterable[str]] = None,
            scope_hashes: Optional[Iterable[str]] = None,
            binding_keys: Optional[Iterable[Tuple[str, str]]] = None,
            contract_keys: Optional[Iterable[Tuple[str, str, str]]] = None,
            metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Public API

        Begin a change-control transaction through the owning Conduit.

        Args:
            transaction_type:
                Transaction type enum or string value (e.g. "link", "bind").
            conduit_ids:
                Optional list of conduits participating in non-link requests.
            conduits:
                Optional list of conduit objects participating in the request.
            scope_keys:
                Optional normalized scope keys for conflict checks.
            scope_hashes:
                Optional normalized scope hashes for conflict checks.
            binding_keys:
                Optional binding keys affected by the request.
            contract_keys:
                Optional contract keys affected by the request.
            metadata:
                Optional structured metadata for diagnostics.
        Returns:
            None.
        Raises:
            RuntimeError: If the ConduitWard is cleaned.
            RuntimeError: If the owning Conduit is not normal.
            RuntimeError: If change-control admission is denied.
            ValueError: If transaction_type is invalid.
            TypeError: If transaction_type has an invalid type.
        """
        ...

    def end_transaction(
            self,
            transaction_type: "ChangeTransactionType | str | None" = None,
    ) -> None:
        """
        Public API

        End the active change-control transaction through the owning Conduit.

        Args:
            transaction_type:
                Optional transaction type assertion for safety checks.
        Returns:
            None.
        Raises:
            RuntimeError: If the ConduitWard is cleaned.
            RuntimeError: If the owning Conduit is not normal.
            RuntimeError: If no change transaction is active.
            RuntimeError: If transaction_type does not match the active request.
            ValueError: If transaction_type is invalid.
            TypeError: If transaction_type has an invalid type.
        """
        ...

    # ------------------------------------------------------------------
    # Conduit Ward Configuration
    # ------------------------------------------------------------------
    @property
    def root_conduit(self) -> Optional['IConduit']:
        """
        Return the root (normal) conduit for this lineage.

        Raises:
            RuntimeError: If the root conduit is missing or not normal.
        """
        ...

    def _convert_to_normal_conduit(self) -> None:
        """
        Internal

        Converts this Conduit from a `lesser` state to a `normal` state.

        This method is called internally during the conduit upgrade process.
        It detaches the parent link and updates the policy state.

        Raises:
            RuntimeError: If the Conduit is not a lesser conduit.
            RuntimeError: If dynamic environment is not enabled.
            RuntimeError: If no parent conduit link is found (unknown error state).
        """
        ...

    def _set_initial_policy(self, policy: 'Policies') -> Optional['Policies']:
        """
        Internal

        Sets the default policy for this Conduit during initialization.

        Args:
            policy (Policies): The desired initial policy.

        Returns:
            Optional[Policies]: The set policy.

        Raises:
            TypeError: If `policy` is not an instance of the `Policies` enum.
            RuntimeError: If the policy has already been set.
        """
        ...

    def _set_new_policy(self, policy: 'str | Policies') -> None:
        """
        Internal

        Sets a new operational policy for this Conduit.

        This is restricted to `normal` conduits in dynamic mode.

        Args:
            policy (str | Policies): The new policy to set.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            RuntimeError: If dynamic environment is not enabled.
            RuntimeError: If the Conduit is a lesser Conduit.
            RuntimeError: If attempting to set to `automatic` in dynamic mode.
            RuntimeError: If attempting to set to `lesser_conduit` on a non-lesser Conduit.
            RuntimeError: If attempting to set to `block_all` or `whitelist_all` while contracts exist.
        """
        ...

    # ------------------------------------------------------------------
    # Link Management
    # ------------------------------------------------------------------
    def _link(self, target_conduit: 'IConduit') -> bool:
        """
        Internal

        Attempts to establish a link (contract) with another normal Conduit.

        Args:
            target_conduit (IConduit): The target Conduit to link to.

        Returns:
            bool: True if the contract was established or already exists.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            RuntimeError: If attempting to link to a lesser conduit.
            RuntimeError: If attempting to link a conduit to itself.
            RuntimeError: If dynamic environment is not enabled.
        """
        ...

    def _create_new_contract(self, target_conduit: 'IConduit') -> bool:
        """
        Internal

        Creates a new bidirectional contract (link) with the specified target conduit.

        This method handles simultaneous locking of both wards to prevent deadlocks.

        Args:
            target_conduit (IConduit): The conduit to link with.

        Returns:
            bool: True if the contract was created successfully.
        """
        ...

    def _find_contract_id(self, target_conduit: 'IConduit') -> Optional[str]:
        """
        Internal

        Finds a contract ID associated with the specified target conduit.

        Args:
            target_conduit (IConduit): The target conduit to find the contract for.

        Returns:
            Optional[str]: The ID of the found contract or None if not found.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            TypeError: If `target_conduit` is not an `IConduit` instance.
        """
        ...

    def _find_contract(self, target_conduit: 'IConduit') -> Optional['Contract']:
        """
        Internal

        Finds the contract object linked to the given target conduit.

        Args:
            target_conduit (IConduit): The target conduit to find the contract for.

        Returns:
            Optional[Contract]: The contract object if it exists, otherwise None.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            TypeError: If `target_conduit` is not an `IConduit` instance.
        """
        ...

    def _find_contract_by_id(self, conduit_id: str) -> Optional['Contract']:
        """
        Internal

        Finds a contract by the peer's Conduit ID.

        Args:
            conduit_id (str): The ID of the peer conduit in the contract.

        Returns:
            Optional[Contract]: The found contract object or None if not found.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        ...

    def _sever_link(self, target_conduit: 'IConduit') -> bool:
        """
        Internal

        Sever the link (contract) between this Conduit and its target Conduit.

        Args:
            target_conduit (IConduit): The target Conduit to sever the link with.

        Returns:
            bool: True if the link was successfully severed.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            RuntimeError: If no contract is found to sever.
        """
        ...

    def _remove_contract(self, target_conduit: 'IConduit') -> bool:
        """
        Internal

        Removes the contract and cleans up internal indices and spellbook links.

        Args:
            target_conduit (IConduit): The conduit whose contract should be removed.

        Returns:
            bool: True if the contract was removed successfully.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        ...

    def _link_lesser_conduit(self, lesser_conduit: 'IConduit') -> None:
        """
        Internal

        Links a lesser conduit (child) to this conduit (parent).

        This establishes the parent-child lineage relationship.

        Args:
            lesser_conduit (IConduit): The lesser conduit to link.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        ...

    def _get_lesser_conduit(self, conduit_id: str) -> Optional['IConduit']:
        """
        Internal

        Recursively searches for a lesser conduit with the given ID within this conduit's hierarchy.

        Args:
            conduit_id (str): The ID of the conduit to retrieve.

        Returns:
            Optional[IConduit]: The matched conduit if found, else None.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        ...

    def _get_links(self) -> List['IConduit']:
        """
        Internal

        Returns a combined list of all peer conduits this conduit has contracts with (both initiated and provider).

        Returns:
            List[IConduit]: A list of all linked peer conduits.
        """
        ...

    def _get_initiated_conduits(self) -> List['IConduit']:
        """
        Internal

        Retrieves all conduits that this conduit has initiated contracts toward (outbound links).

        Returns:
            List[IConduit]: A list of conduits that this conduit has initiated contracts with.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        ...

    def _get_provider_conduits(self) -> List['IConduit']:
        """
        Internal

        Retrieves all conduits that have initiated contracts to this conduit (inbound links).

        Returns:
            List[IConduit]: A list of conduits that have linked to this conduit as a provider.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        ...

    def _get_initiated_conduit(self, conduit_id: str) -> Optional['IConduit']:
        """
        Internal

        Retrieves the conduit that this conduit has initiated a contract *toward*.

        Args:
            conduit_id (str): The ID of the target conduit this conduit linked to.

        Returns:
            Optional[IConduit]: The target conduit if the link exists, otherwise None.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        ...

    def _get_provider_conduit(self, conduit_id: str) -> Optional['IConduit']:
        """
        Internal

        Retrieves the conduit that initiated a contract *to this* conduit.

        Args:
            conduit_id (str): The ID of the source conduit that linked to this one.

        Returns:
            Optional[IConduit]: The source conduit if the link exists, otherwise None.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        ...

    def _sever_all_linked_conduits(self) -> None:
        """
        Internal

        Severs all active peer links (contracts) to conduits. Excludes lesser conduits.
        """
        ...

    # ------------------------------------------------------------------
    # Spellbinding API
    # ------------------------------------------------------------------
    def _check_spell_id_and_spell(
            self,
            spell: 'ISpell' = None,
            spell_id: str = None,
            aetheric_frame: str = "default",
    ) -> Tuple[str, 'ISpell']:
        """
        Internal

        Validation and resolution helper: ensures both a spell ID and its corresponding spell object are available.

        Args:
            spell (ISpell, optional): The spell object.
            spell_id (str, optional): The unique ID of the spell.
            aetheric_frame (str): The Aetheric Frame to search within.

        Returns:
            Tuple[str, ISpell]: The resolved (spell_id, spell) pair.

        Raises:
            ValueError: If neither `spell` nor `spell_id` is provided.
            TypeError: If types are incorrect.
            RuntimeError: If the spell cannot be resolved or if the provided ID and resolved ID mismatch.
        """
        ...

    def _check_conduit_id_and_conduit(
            self,
            conduit: 'IConduit' = None,
            conduit_id: str = None,
            aetheric_frame: str = "default",
    ) -> Tuple[str, 'IConduit']:
        """
        Internal

        Validation and resolution helper: ensures both a conduit ID and its corresponding conduit object are available.

        Args:
            conduit (IConduit, optional): The target conduit object.
            conduit_id (str, optional): The unique ID of the target conduit.
            aetheric_frame (str): The Aetheric Frame to search within.

        Returns:
            Tuple[str, IConduit]: The resolved (conduit_id, conduit) pair.

        Raises:
            ValueError: If neither `conduit` nor `conduit_id` is provided.
            TypeError: If types are incorrect.
            RuntimeError: If the conduit cannot be resolved or if IDs mismatch.
        """
        ...

    def _create_detail(
            self,
            spell: 'ISpell',
            permissions: 'Permissions',
            contract_type: 'ContractTypes',
    ) -> 'Detail':
        """
        Internal

        Factory for a lineage-aware Detail entry.

        Args:
            spell (ISpell): The spell being granted/received.
            permissions (Permissions): The permissions applied to this lineage.
            contract_type (ContractTypes): Role of this Detail from the
                perspective of the ward that will own it.

        Returns:
            Detail: A new Detail instance.
        """
        ...

    def _check_spell_if_eligible(
            self,
            spell: 'ISpell',
            conduit: 'IConduit',
            permissions: 'Permissions',
    ) -> None:
        """
        Internal

        Checks if the provided spell is eligible for contracting based on policy and spell permissions.

        Args:
            spell (ISpell): The spell to check.
            conduit (IConduit): The conduit proposing the contract.
            permissions (Permissions): The permissions requested for the contract.

        Raises:
            RuntimeError: If the conduit policy prevents contracting (`block_all`).
            RuntimeError: If the spell doesn't have the required permissions (`create`, `read`).
            RuntimeError: If the spell is blocked (`Permissions.block`) and policy isn't `whitelist_all`.
            RuntimeError: If the spell is not owned by the proposing conduit.
        """
        ...

    def _add_spell_to_contract(
            self,
            *,
            spell: 'ISpell' = None,
            spell_id: str = None,
            conduit: 'IConduit' = None,
            conduit_id: str = None,
            permissions: str = "create",
            aetheric_frame: str = "default",
            reason: Any = None,
            root_spell_id: str | None = None,
            link_dependencies: bool = False,
    ) -> bool | None:
        """
        Internal

        Adds a single spell to an existing contract with a peer conduit.

        This now contracts the **SpellIndex lineage** and uses the spell's
        current version ID only as the initial reference. On mutation, the
        lineage will advance, and lookups will resolve to the new version.

        Args:
            spell (ISpell, optional): The spell object to contract.
            spell_id (str, optional): The unique version ID of the spell.
            conduit (IConduit, optional): The target peer conduit.
            conduit_id (str, optional): The id of the target peer conduit.
            permissions (str): The permission level granted for this spell.
            aetheric_frame (str): The Aetheric Frame to resolve entities in.

        Returns:
            bool | None: True if the contract was updated, None on internal error.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            RuntimeError: If no contract exists with the target conduit (link required first).
            RuntimeError: If the spell is already contracted with the same permissions.
            ValueError/TypeError/RuntimeError: From internal helper checks.
        """
        ...

    def _add_spells_to_contract(
            self,
            *,
            spell_ids: list[str] = None,
            conduit: 'IConduit' = None,
            conduit_id: str = None,
            permissions: str = "create",
            aetheric_frame: str = "default",
            reason: Any = None,
            link_dependencies: bool = False,
    ) -> dict[str, list[str] | dict[str, str]]:
        """
        Internal

        Attempts to add multiple spells to an existing contract in a bulk operation.

        Args:
            spell_ids (list[str], optional): List of spell IDs to contract.
            conduit (IConduit, optional): The target peer conduit.
            conduit_id (str, optional): The id of the target peer conduit.
            permissions (str): The permission level to apply to all spells (default is "create").
            aetheric_frame (str): The Aetheric Frame to resolve entities in.

        Returns:
            dict: A dictionary containing a list of "success" spell IDs and a dictionary of "failed" spell IDs mapped to error messages.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        ...

    def _remove_spell_from_contract(
            self,
            *,
            spell: 'ISpell' = None,
            spell_id: str = None,
            conduit: 'IConduit' = None,
            conduit_id: str = None,
            aetheric_frame: str = "default",
    ) -> bool | None:
        """
        Internal

        Removes a specific spell from an existing contract.

        Args:
            spell (ISpell, optional): The spell object to remove.
            spell_id (str, optional): The unique ID of the spell to remove.
            conduit (IConduit, optional): The target peer conduit.
            conduit_id (str, optional): The id of the target peer conduit.
            aetheric_frame (str): The Aetheric Frame to resolve entities in.

        Returns:
            bool: True if the spell was successfully removed.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            RuntimeError: If no contract is found.
            RuntimeError: If the spell ID is not found in the contract.
            ValueError/TypeError/RuntimeError: From internal helper checks.
        """
        ...

    def _remove_spells_from_contract(
            self,
            *,
            spell_ids: list[str] = None,
            conduit: 'IConduit' = None,
            conduit_id: str = None,
            aetheric_frame: str = "default",
    ) -> dict[str, list[str] | dict[str, str]]:
        """
        Internal

        Attempts to remove multiple spells from an existing contract in a bulk operation.

        Args:
            spell_ids (list[str], optional): List of spell IDs to remove.
            conduit (IConduit, optional): The target peer conduit.
            conduit_id (str, optional): The id of the target peer conduit.
            aetheric_frame (str): The Aetheric Frame to resolve entities in.

        Returns:
            dict: A dictionary containing a list of "success" spell IDs and a dictionary of "failed" spell IDs mapped to error messages.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        ...

    def _remove_all_spells_from_contract(
            self,
            *,
            conduit: 'IConduit' = None,
            conduit_id: str = None,
            aetheric_frame: str = "default",
    ) -> bool | None:
        """
        Internal

        Removes ALL spells from the contract associated with the specified peer conduit.

        Args:
            conduit (IConduit, optional): The target peer conduit.
            conduit_id (str, optional): The id of the target peer conduit.
            aetheric_frame (str): The Aetheric Frame to resolve entities in.

        Returns:
            bool: True if all spells were successfully removed and cleanup performed.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            RuntimeError: If no contract is found.
            ValueError/TypeError/RuntimeError: From internal helper checks.
        """
        ...

    def _get_all_spells_in_contracts(
            self,
            validate: bool = True,
    ) -> Optional[dict[str, list[Tuple[str, 'ISpell']]]]:
        """
        Internal

        Retrieves all spells that **this conduit can use** via active contracts.

        For each peer conduit, this returns a list of:
            (current_spell_version_id, ISpell)

        Semantics:
            * Contracts are anchored on SpellIndex (via Detail.spell_index).
            * Resolution uses Spellbook._find_contracted_spell(spell_index),
              so if the lineage has mutated, we get the **current** spell object.
            * The version ID returned in the tuple is spell.spell_id (head).
        """
        ...

    def _get_spell_in_contracts(self, spell_id: str) -> Optional[tuple[str, 'ISpell']]:
        """
        Internal

        Attempts to retrieve a specific spell that is being granted *to* this
        conduit by any peer via active contracts.

        This now behaves in a lineage-aware way:

            * spell_id may be ANY version SHA belonging to the lineage.
            * We search each Detail's SpellIndex using Detail.has_version(spell_id).
            * If matched, we resolve via Spellbook._find_contracted_spell(spell_index)
              and return the **current** spell object (not the historical version).

        Args:
            spell_id (str): The version ID (SHA) to search for.

        Returns:
            Optional[tuple[str, ISpell]]: (peer_conduit_id, ISpell) if found, else None.
        """
        ...

    def _get_spells_in_contract_by_conduit(
            self,
            conduit_id: str,
    ) -> dict[str, list[tuple[str, 'ISpell']]] | None:
        """
        Internal

        Retrieves all spells exchanged with a specific conduit by its unique ID.

        - "inbound": spells the peer has granted to this conduit.
        - "outbound": spells this conduit has granted to the peer.

        Args:
            conduit_id (str): The id of the target conduit.

        Returns:
            dict[str, list[tuple[str, ISpell]]] | None: A dictionary mapping roles
            ("inbound", "outbound") to lists of (spell_id, ISpell) tuples, or None
            if no such conduit is linked. When a contract exists but contains no
            spells, the inbound/outbound lists are empty.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        ...

    def _get_spells_in_contract_by_conduit_name(
            self,
            conduit_name: str,
    ) -> dict[str, list[tuple[str, 'ISpell']]] | None:
        """
        Internal

        Retrieves all spells exchanged with a specific conduit by its declared name.

        Mirrors `_get_spells_in_contract_by_conduit` but performs lookup by name.

        Args:
            conduit_name (str): The name identifier of the target conduit.

        Returns:
            dict[str, list[tuple[str, ISpell]]] | None: A dictionary of spells exchanged (inbound/outbound), or None if not found.
            When a contract exists but contains no spells, inbound/outbound lists are empty.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            ValueError: If `conduit_name` is empty or not a string.
        """
        ...

    def _get_contracted_conduits(self) -> list[Tuple[str, 'IConduit']] | None:
        """
        Internal

        Returns all conduits that currently have active spell contracts with this conduit.

        Args:
            None

        Returns:
            list[Tuple[str, IConduit]] | None: A list of (`conduit_id`, `IConduit`) tuples. Returns None if no links exist.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        ...

    def _describe_contract(self, conduit_id: str) -> dict:
        """
        Internal

        Returns a detailed diagnostic summary of a contract established with a specific peer conduit ID.

        Args:
            conduit_id (str): id of the peer conduit whose contract you wish to examine.

        Returns:
            dict: Dictionary containing contract metadata, including spell list and permissions.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            RuntimeError: If no contract is found with the given conduit ID.
        """
        ...

    def _validate_contracts_and_define(self) -> dict[str, bool]:
        """
        Internal

        Validates all active contracts attached to this conduit for symmetry and integrity.

        This ensures both sides list the same spells, permissions are consistent, and all
        referenced contracted spells exist in the peer's spellbook.

        Args:
            None

        Returns:
            dict[str, bool]: Dictionary mapping contract id to validation results (True/False).

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        ...

    def _validate_received_contracts(self) -> bool:
        """
        Internal

        Performs a high-level validation check across all contracts involving this conduit.

        This aggregates the results of `_validate_contracts_and_define` to provide a simple pass/fail status.

        Args:
            None

        Returns:
            bool: True if all active contracts pass validation, False otherwise.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        ...


@runtime_checkable
class ISpellSpace(ICleanable, Protocol):
    """
    Scope handle for spellspace-scoped lifecycles.

    Purpose:
        Define the public contract for a SpellSpace-like object that
        manages a spellspace scope owned by a Conduit.
    Contract:
        - Provides a stable id and monotonic version counter.
        - Enforces active-scope checks for meld calls.
        - Supports reset and cleanup semantics consistent with SpellSpace.
    Threading:
        - No internal locking is required by the contract; callers should
          synchronize via the owning Conduit if used concurrently.
    Lifecycle:
        - cleanup() is idempotent and releases owner references.
    """

    _id: str
    _owner_conduit: Optional["IConduit"]
    _version: int

    @property
    def id(self) -> str:
        """
        Stable identifier for this spellspace scope.

        Returns:
            str: Unique ID assigned at construction time.
        """
        ...

    @property
    def owner_conduit(self) -> Optional["IConduit"]:
        """
        Owning Conduit for this spellspace.

        Returns:
            Optional[IConduit]: The owner conduit, or None after cleanup.
        """
        ...

    @property
    def version(self) -> int:
        """
        Monotonic version counter for this spellspace.

        Contract:
            - Increments on reset().

        Returns:
            int: Current version value.
        """
        ...

    def meld(
            self,
            spell_name: str | None = None,
            *,
            spell: str | object | None = None,
            spellframe: str | object | None = None,
            binding_name: str | None = None,
            spell_override: Optional[dict | list | tuple] = None,
    ) -> Any:
        """
        Delegate meld to the owner Conduit while enforcing active scope.

        Contract:
            - Raises SpellSpaceScopeError if this spellspace is not active.
            - Propagates errors from the owning Conduit meld pipeline.

        Args:
            spell_name: Optional human-readable spell name.
            spell: Unique spell identifier (typically version id).
            spellframe: Optional spellframe metadata.
            binding_name: Optional binding name metadata.
            spell_override: Optional override payload for meld metadata.

        Returns:
            Any: The resolved instance from the owner Conduit.
        """
        ...

    def reset(self) -> None:
        """
        Clear spellspace-bound instances and increment version.

        Contract:
            - Clears spellspace-specific creations in the owner.
            - Increments the version counter on success.

        Raises:
            SpellSpaceScopeError: If the owner does not expose spellspace storage.
            RuntimeError: If this SpellSpace has been cleaned.
        """
        ...


@runtime_checkable
class IConduit(ICleanable, Protocol):
    """
    A Conduit is a modular graph node that behaves like a scope and a factory.

    It can spawn lesser Conduits, link to other Conduits if dynamic mode is enabled,
    and manage the lifecycle of services registered inside itself.
    """

    # Class-level
    _aether: 'Aether'

    # Instance-level core attributes (1:1 with Conduit)
    _lock: threading.RLock
    _id: str
    _name: Optional[str]
    __debugger_mode__: bool
    __dynamic_environment__: bool
    _aetheric_frame: str

    _configuration: 'IConfiguration'
    _logger: 'ISafeLogger'

    _conduit_state: 'ConduitState'
    _creations: 'Creations | LesserCreations'
    _spellbook: 'ISpellbook'
    _meld: 'Meld'

    _conduit_ward: 'ConduitWard'

    # ------------------------------------------------------------------
    # Logger configuration
    # ------------------------------------------------------------------
    def _configure_logger(self, logger: Any, configuration: 'IConfiguration') -> Any:
        """
        Internal

        Configures the logger for this Conduit.

        Args:
            logger (Any): The logger instance or configuration.
        Returns:
            SafeLogger: The configured SafeLogger instance.
        """
        ...

    def _configure_conduit_state(self) -> None:
        """
        Internal

        Configures the conduit state based on the provided configuration.

        Raises:
            RuntimeError: If normal conduit registration fails.
        """
        ...

    # ------------------------------------------------------------------
    # Cleanup and Disposal
    # ------------------------------------------------------------------
    def cleanup(self) -> None:
        """
        Public API

        Cleans up this Conduit and all its lesser Conduits.

        Prevents further operation, releases internal references,
        and unregisters from the Aether.
        """
        ...

    # ------------------------------------------------------------------
    # Context Management
    # ------------------------------------------------------------------
    def __enter__(self) -> 'IConduit':
        """
        Public API

        Enters the context of this Conduit.

        Returns:
            Conduit: The current Conduit instance.
        """
        ...

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """
        Public API

        Exits the context of this Conduit.

        Args:
            exc_type: The exception type, if any.
            exc_value: The exception value, if any.
            traceback: The traceback object, if any.
        """
        ...

    # ------------------------------------------------------------------
    # Logger resolution
    # ------------------------------------------------------------------
    def _resolve_logger_from_config(self, configuration: 'IConfiguration') -> 'ISafeLogger':
        """
        This internal method resolves the logger for this Conduit based on the provided configuration.

        Args:
            configuration (IConfiguration): The locked system configuration.

        Returns:
            SafeLogger: The resolved SafeLogger instance.
        """
        ...

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------
    def __repr__(self) -> str:
        """
        Public API

        Returns a string representation of the Conduit instance.
        :return:
        """
        ...

    def snapshot_state(self) -> Dict[str, Any]:
        """
        Public API

        Build a read-only snapshot of Conduit state.

        Purpose:
            Provide a stable view of conduit metadata and Spellbook registries
            while transactions may be in-flight.
        Contract:
            - Returns detached copies of metadata and Spellbook snapshot data.
            - Includes a snapshot id for observability.
        Returns:
            Dict[str, Any]: Snapshot payload with conduit metadata and a
            Spellbook snapshot.
        """
        ...

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------
    @property
    def id(self) -> str:
        """
        Public API

        Returns the unique identifier of this Conduit.
        """
        ...

    @property
    def name(self) -> Optional[str]:
        """
        Public API

        Returns the name of this Conduit. Name must be created during conduit creation.
        """
        ...

    @name.setter
    def name(self, name: str) -> None:
        """
        Public API

        Allows user to name conduit if available

        Raises:
            RuntimeError: If the Conduit name is already set.
        """
        ...

    # ------------------------------------------------------------------
    # Conduit Configuration
    # ------------------------------------------------------------------
    def register_conduit_cloud(self, conduit: 'IConduit') -> None:
        """
        Public API

        Registers a conduit in the dynamic mode registry. You can use this method if you forgot to name your conduit in order
        to name it afterward and register it. You can only register it once.

        Args:
            conduit (IConduit): The conduit instance to register.

        Raises:
            RuntimeError: If dynamic environment is not enabled.
            RuntimeError: If the conduit is a lesser conduit.
            RuntimeError: If the Conduit name is not set.
        """
        ...

    def _apply_configuration_flags(self) -> None:
        """
        Internal

        Sets the environment mode and debugging mode for this Conduit
        based on the configuration instance passed.
        """
        ...

    def _add_conduit_to_aether(self) -> None:
        """
        Internal

        Adds the newly created Conduit into the shared Aether world.

        Raises:
            RuntimeError: If Aether is not initialized.
        """
        ...

    def _creations_configuration(self, configuration: 'IConfiguration') -> 'Creations | LesserCreations':
        """
        Internal

        Returns the current creations configuration for this Conduit.

        Args:
            configuration (IConfiguration): The locked system configuration.

        Returns:
            Creations | LesserCreations: The appropriate creation manager based on conduit state.

        Raises:
            RuntimeError: If the Conduit state is unknown.
        """
        ...

    # ------------------------------------------------------------------
    # Conduit Management
    # ------------------------------------------------------------------
    def upgrade_to_normal(self, name: Optional[str] = None) -> None:
        """
        Public API

        Upgrades this Conduit from a lesser to a **normal** state.

        This process allows the conduit to create its own links through the Aether system.
        It effectively forks this conduit into a new tree, retaining its children and
        creation data, and establishes new links with the parent. Only a normal conduit
        can access the Spellbook to bind new spells.

        Please name the conduit if your intention is to add it to the Conduit Cloud.

        Args:
            name (str, optional): An optional name to assign to the upgraded conduit.

        Raises:
            RuntimeError: If the dynamic environment is not enabled.
            RuntimeError: If the current conduit state is not 'lesser'.
        """
        ...

    def set_new_policy(self, policy: str) -> None:
        """
        Public API

        Sets a new policy for this Conduit. This is only allowed in dynamic mode.

        Args:
            policy (str): The new policy to set, governing linking behavior.

        Raises:
            RuntimeError: If dynamic environment is not enabled.
        """
        ...

    def create_lesser_conduit(self, logger: Any | None = None) -> 'IConduit':
        """
        Public API

        Creates a **lesser Conduit** (child node) attached to this Conduit.

        The lesser conduit inherits the parent's Spellbook and Configuration but is restricted
        in its ability to establish external links or register new spells.

        Returns:
            IConduit: The newly created lesser Conduit instance.

        Raises:
            RuntimeError: If the parent Conduit is cleaned.
        """
        ...

    # ------------------------------------------------------------------
    # Spellbook Management API
    # ------------------------------------------------------------------
    def _add_spells_to_aether(self) -> None:
        """
        Internal

        Adds this Conduit's local spell lineages (SpellIndex keys) into the shared
        Aether world's registry.

        Aether is responsible for mapping individual version IDs inside each
        SpellIndex to the owning conduit.

        Raises:
            RuntimeError: If Aether is not initialized.
        """
        ...

    def get_conduit_by_spell_id(
            self,
            spell_id: str,
            aetheric_frame_name: str = "default",
    ) -> Optional['IConduit']:
        """
        Public API

        Retrieves the conduit that has registered a spell with the given spell_id.

        This method queries the Aether to find the original source conduit for a specific spell ID.

        Args:
            spell_id (str): The unique identifier of the spell.
            aetheric_frame_name (str): The aetheric frame to check against. Defaults to "default".

        Returns:
            Optional[IConduit]: The conduit that registered the spell, or None if not found.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        ...

    def check_spell_id(self, spell_id: str, aetheric_frame_name: str = "default") -> bool:
        """
        Public API

        Checks if a spell with the given spell_id exists within the global Aether registry.

        Args:
            spell_id (str): The unique identifier of the spell to check (version SHA).
            aetheric_frame_name (str): The Aetheric Frame to search within. Defaults to "default".

        Returns:
            bool: True if the spell exists in the Aether, False otherwise.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        ...

    def get_spell_by_id(self, spell_id: str, aetheric_frame_name: str = "default") -> Optional[Any]:
        """
        Public API

        Retrieves a spell object by its unique version identifier (spell_id) from the
        spellbook of its owner.

        The method:
          1) Uses Aether to locate the owning conduit.
          2) Searches that conduit's spellbook for a SpellIndex whose lineage contains
             this version ID.
          3) Returns the corresponding ISpell instance if found.

        Args:
            spell_id (str): The unique version identifier of the spell (SHA256).
            aetheric_frame_name (str): The aetheric frame to check against. Defaults to "default".

        Returns:
            Optional[Any]: The spell object if found, otherwise None.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        ...

    def find_contracted_spell(self, spell_id: str) -> Optional['ISpell']:
        """
        Internal

        Locate a contracted spell by its version spell_id across all peer
        conduits in this Spellbook.

        Args:
            spell_id (str): The unique version ID (SHA) of the spell to find.

        Returns:
            Optional[ISpell]: The contracted spell instance, or None if not found.
        """
        ...

    def find_spell_id(self, spellframe: str, spell_name: str, binding_name: str) -> Optional[str]:
        """
        Public API

        Finds a spell's current version ID (SHA256 spell_id) using its logical identifiers.

        This now uses:
          1) Spellbook.find_spell_index(...) to locate the SpellIndex lineage.
          2) Spellbook._find_spell(SpellIndex) to retrieve the ISpell.
          3) Returns spell.spell_id (the current head version for that lineage).

        Args:
            spellframe (str): The logical namespace or grouping label.
            spell_name (str): The name of the spell class or function.
            binding_name (str): The secondary key to distinguish the spell.

        Returns:
            Optional[str]: The current SHA256 identifier of the spell.

        Raises:
            ValueError: If the spell is not found in the spellbook.
        """
        ...

    def find_spell_key(self, spellframe: str, spell_name: str, binding_name: str) -> Optional[tuple]:
        """
        Public API

        Finds a spell's primary lookup key using its logical identifiers.

        The key is typically a tuple used for internal retrieval within the spellbook.

        Args:
            spellframe (str): The logical namespace or grouping label.
            spell_name (str): The name of the spell class or function.
            binding_name (str): The secondary key to distinguish the spell.

        Returns:
            Optional[tuple]: The spell's key (frame, name, binding_name) tuple.

        Raises:
            ValueError: If the spell is not found in the spellbook.
        """
        ...

    def inspect_spell(self, spell: Any, aetheric_frame: str = "default") -> Optional[str]:
        """
        Public API

        Inspects any object to determine if it is a valid, registered spell in the Aether Registry.

        This method uses the Spellbook's internal reflection to identify the spell.

        Args:
            spell (Any): The class, function, or object instance to inspect.
            aetheric_frame (str): The Aetheric Frame to search within. Defaults to "default".

        Returns:
            Optional[str]: The SHA256 unique ID of the spell if found, otherwise None.
        """
        ...

    def bind(
            self,
            *,
            spell,
            existence: str | Existence,
            permissions: str = "create",
            spellframe=None,
            binding_name=None,
            **kwargs,
    ) -> str:
        """
        Binds a spell into the Spellbook for future instantiation and dependency injection.

        The `bind()` method registers a class, function, or object into Melder’s system,
        associating it with a lifecycle (`Existence`), a permission policy, and optional metadata.
        Once bound, the spell becomes available for resolution and casting within its conduit
        or across systems (depending on permissions).

        ──────────────────────────────────────────────
        🧠 Binding Overview:
            - Profiles the spell via reflection.
            - Computes a unique SHA256 `spell_id`.
            - Stores the spell into the internal spell registry.
            - Assigns its lookup key via `(spellframe, binding_name)`.
            - Applies lifecycle and permission policies.
            - Optionally attaches lifecycle hooks.

        ──────────────────────────────────────────────
        🛡️ Permissions (access control to other conduits):
            - `"read"`:
                Allows other conduits to *use* the spell but not create new instances.
                Useful for shared utilities or resources.

            - `"create"` (default):
                Allows other conduits to both use *and* create instances from this spell.

            - `"block"`:
                Completely blocks access to the spell from other conduits.
                Only the owning conduit can use or instantiate it.

        🔄 Existence (spell lifecycle):
            Determines how the spell instance is managed (singleton, transient, etc.).
            Use `Existence.unique`, `Existence.many`, etc., for fine-grained control.

        📦 Spellframe (optional):
            Logical namespace or grouping label.
            Often corresponds to a shared interface, protocol, or feature group.

        🔑 Binding Name (optional):
            Secondary key used to distinguish different versions or roles of the same type.
            Useful when multiple spells are bound under the same interface.

        ──────────────────────────────────────────────
        🪝 Lifecycle Hooks (optional `**kwargs`):

            - `pre_hooks`: List[Callable]
                Executed *before* the spell is constructed or cast.
                Can be used for validation, preparation, or logging.

            - `activation_hooks`: List[Callable]
                Executed *during* spell construction. Useful for modifying dependencies
                or adapting runtime context.

            - `post_hooks`: List[Callable]
                Executed *after* the spell has been cast. Often used for initialization,
                analytics, or final injection steps.

            ⚠️ All hooks must be callables.

        ──────────────────────────────────────────────
        Args:
            spell (Any): The class, function, or object to bind into the spellbook.
            existence (Existence): The lifecycle scope for this spell.
            permissions (str): Permission level exposed to other conduits ("read", "create", "block").
            spellframe (Optional[Any]): Logical interface or category for grouping.
            binding_name (Optional[str]): Name key to distinguish this spell among others in its frame.
            **kwargs:
                - pre_hooks (Optional[List[Callable]]): Hooks executed before casting.
                - activation_hooks (Optional[List[Callable]]): Hooks executed during casting/construction.
                - post_hooks (Optional[List[Callable]]): Hooks executed after casting/construction.

        Returns:
            str: The unique SHA256 `spell_id` associated with the bound spell.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            RuntimeError: If the Conduit is not a 'normal' conduit (only normal conduits can bind spells).
            RuntimeError: If no binding transaction is active for this Spellbook.
            RuntimeError: If the spell is already bound in the registry.
            TypeError: If invalid hook types are provided.
        """
        ...

    def scan(self, module: ModuleType) -> list[str]:
        """
        Public API

        Scan a module for `scan_bind`-decorated objects and bind them into this
        Conduit's Spellbook.

        This is a module-only scan: it does not traverse packages or import
        submodules. Any object marked with `scan_bind` must originate from the
        scanned module, otherwise the scan fails.

        Args:
            module (ModuleType): The module to scan for decorated spell targets.
        Returns:
            list[str]: Spell IDs bound during the scan, in module dict order.
        Raises:
            RuntimeError: If the Conduit is cleaned or not normal.
            RuntimeError: If no binding transaction is active for this Spellbook.
            TypeError: If `module` is not a module or metadata is invalid.
            ValueError: If a decorated object is not owned by the module.
            RuntimeError: Propagated from Spellbook.bind on binding errors.
        """
        ...

    def begin_transaction(
            self,
            transaction_type: "ChangeTransactionType | str",
            *,
            conduit_ids: Optional[Iterable[str]] = None,
            conduits: Optional[Iterable["IConduit"]] = None,
            scope_keys: Optional[Iterable[str]] = None,
            scope_hashes: Optional[Iterable[str]] = None,
            binding_keys: Optional[Iterable[Tuple[str, str]]] = None,
            contract_keys: Optional[Iterable[Tuple[str, str, str]]] = None,
            metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Public API

        Begin a change-control transaction for this Conduit.

        Purpose:
            Admit a mutation request through the ChangeControlManager and,
            for bind transactions, open the binding transaction window.
        Contract:
            - Only normal conduits may begin change-control transactions.
            - Admission is serialized by the ChangeControlOrchestrator.
            - Bind transactions open the binding transaction window.
            - Link transactions must explicitly include the local conduit and peers.
            - Link, transfer, mutation, and cluster link require dynamic mode.
        Args:
            transaction_type:
                Transaction type enum or string value (e.g. "bind", "link").
            conduit_ids:
                Optional list of conduits participating in non-link requests.
                Link transactions require explicit conduit objects.
            conduits:
                Optional list of conduit objects participating in the request.
                For link transactions, include the local conduit and peers.
            scope_keys:
                Optional normalized scope keys for conflict checks.
            scope_hashes:
                Optional normalized scope hashes for conflict checks.
            binding_keys:
                Optional binding keys affected by the request.
            contract_keys:
                Optional contract keys affected by the request.
            metadata:
                Optional structured metadata for diagnostics.
        Returns:
            None.
        Raises:
            RuntimeError: If the Conduit is cleaned or not normal.
            RuntimeError: If change-control admission is denied.
            ValueError: If transaction_type is invalid.
            TypeError: If transaction_type has an invalid type.
        """
        ...

    def end_transaction(
            self,
            transaction_type: "ChangeTransactionType | str | None" = None,
    ) -> None:
        """
        Public API

        End the active change-control transaction for this Conduit.

        Purpose:
            Finalize an admitted change-control request and release any
            implicit embargo state tracked by the ChangeControlManager.
        Contract:
            - Only normal conduits may end change-control transactions.
            - Raises if no change transaction is active.
        Args:
            transaction_type:
                Optional transaction type assertion for safety checks.
        Returns:
            None.
        Raises:
            RuntimeError: If the Conduit is cleaned or not normal.
            RuntimeError: If no change transaction is active.
            RuntimeError: If transaction_type does not match the active request.
            ValueError: If transaction_type is invalid.
            TypeError: If transaction_type has an invalid type.
        """
        ...

    def begin_binding_transaction(self) -> None:
        """
        Public API

        Begin a binding transaction for this Conduit.

        Purpose:
            Enable binding operations (bind/scan) through this Conduit.
        Contract:
            - Only normal conduits may begin a binding transaction.
            - Binding transactions must be explicitly ended.
        Returns:
            None.
        Raises:
            RuntimeError: If the Conduit is cleaned or not normal.
            RuntimeError: If a binding transaction is already active.
        """
        ...

    def end_binding_transaction(self) -> None:
        """
        Public API

        End the active binding transaction for this Conduit.

        Purpose:
            Disable binding operations until a new transaction is started.
        Contract:
            - Only normal conduits may end a binding transaction.
            - The transaction must be active when ending.
        Returns:
            None.
        Raises:
            RuntimeError: If the Conduit is cleaned or not normal.
            RuntimeError: If no binding transaction is active.
        """
        ...

    def binding_transaction(self) -> "IConduit":
        """
        Public API

        Context-managed binding transaction for this Conduit.

        Contract:
            - Starts a binding transaction on entry.
            - Ends the transaction on exit, even if an exception is raised.
            - Only normal conduits may enter this context.
        Returns:
            IConduit: The current Conduit instance.
        Raises:
            RuntimeError: If the Conduit is cleaned or not normal.
            RuntimeError: If a binding transaction is already active.
        """
        ...

    def get_spell_permissions(self, spell_id: str) -> Optional[str]:
        """
        Public API

        Get the permissions for a spell by its version spell_id, **within this
        conduit’s own spellbook**.

        This returns the access level ("read", "create", "block") defined when the
        spell was bound.

        Args:
            spell_id (str): Version SHA256 identifier of the spell.

        Returns:
            Optional[str]: The permissions associated with the spell's binding.

        Raises:
            RuntimeError: If the spell with the given ID is not found in the spellbook.
        """
        ...

    def meld(
            self,
            spell_name: str | None = None,
            *,
            spell: str | object | None = None,
            spellframe: str | object | None = None,
            binding_name: str | None = None,
            spell_override: Optional[dict | list | tuple] = None,
    ) -> Optional[Any]:
        """
        Public API

        Direct spell activation facade for this Conduit.

        At the Conduit boundary, `meld` supports multiple root entry modes.
        Callers may resolve by:

        - `spell` as a **string** (treated as the canonical spell_id), or
        - `spell` as a **spell object** (class/function), or
        - `spellframe` as a **frame/protocol** (or string frame key), or
        - `spell_name` as a **logical name key** (string).

        These inputs are normalized and delegated to the underlying `Meld`
        instance, which resolves a concrete spell_id via SpellInputUtils.

        Resolution, reuse, and lifecycle behavior are delegated to
        the underlying ``Meld`` instance.

        Args:
            spell_name:
                Logical spell name (string). When provided without an explicit
                `spell` or `spellframe`, this is treated as the name-based key
                for resolution (via SpellInputUtils normalization).
            spell:
                Primary spell identifier. If a string, this is treated as the
                unique spell_id (typically the SHA256 version ID). If an
                object (class/function), it participates in key normalization.
            spellframe:
                Optional spellframe / protocol / string frame key used for
                resolution. If provided, it becomes the primary frame key.
            binding_name:
                Optional binding name (string) associated with the
                spell. Used as the binding key during resolution.
            spell_override:
                Optional per-call override payload (dict / list / tuple)
                passed through to ``Meld.meld`` for constructor/factory
                argument overrides.

        Returns:
            Any:
                The resolved component instance (reused or newly
                created) as returned by ``Meld.meld``.

        Raises:
            RuntimeError:
                - If the Conduit has been cleaned.
                - If the underlying ``Meld`` instance is missing.
            ValueError:
                - If none of `spell_name`, `spell`, or `spellframe` are provided.
            TypeError:
                - If `spell_name` is not a string when provided.
                - If `binding_name` is not a string when provided.
            KeyError:
                Propagated from ``Meld.meld`` when a spell_id cannot be
                resolved.
            NotImplementedError:
                Propagated from ``Meld.meld`` for spell types or
                existence modes not yet implemented.
            HookExecutionError:
                Propagated from ``Meld.meld`` if hook execution fails.
        """
        ...

    # ------------------------------------------------------------------
    # Conduit Cloud
    # ------------------------------------------------------------------
    def get_conduit_cloud(self) -> 'IConduitCloud':
        """
        Public API

        Returns the global Conduit Cloud, a registry of all normal conduits in the current Aetheric Frame.

        This object is designed to be used in dynamic mode only and serves as an Abstract Factory/Service Locator.

        Returns:
            IConduitCloud: The conduit cloud instance.

        Raises:
            RuntimeError: If the Conduit is a lesser conduit.
            RuntimeError: If dynamic environment is not enabled.
        """
        ...

    # ------------------------------------------------------------------
    # Aether API
    # ------------------------------------------------------------------
    def get_conduit_by_id(self, conduit_id: str, aetheric_frame: str = "default") -> Optional['IConduit']:
        """
        Public API

        Retrieves a conduit by its unique ID from the Aether.

        Args:
            conduit_id (str): The unique identifier of the conduit.
            aetheric_frame (str): The aetheric frame to check against. Defaults to this conduit's frame.

        Returns:
            Optional[IConduit]: The conduit instance if found, otherwise None.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            TypeError: If the `aetheric_frame` is not a string.
        """
        ...

    def get_conduit_by_name(self, name: str, aetheric_frame: str = "default") -> Optional['IConduit']:
        """
        Public API

        Retrieves a conduit by its name from the Aether.

        Args:
            name (str): The name of the conduit.
            aetheric_frame (str): The aetheric frame to check against. Defaults to this conduit's frame.

        Returns:
            Optional[IConduit]: The conduit instance if found, otherwise None.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            TypeError: If the `aetheric_frame` is not a string.
        """
        ...

    # ------------------------------------------------------------------
    # Conduit Ward API
    # ------------------------------------------------------------------
    def link(self, target_conduit: 'IConduit') -> bool:
        """
        Public API

        Attempts to establish a link between this Conduit and a `target_conduit`.

        Linking is only allowed if the world is in dynamic mode. This process initiates a contract
        relationship between the two conduits based on the current policy.

        Args:
            target_conduit (IConduit): The target Conduit to link to.

        Returns:
            bool: True if the linking process succeeds.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            RuntimeError: If dynamic environment is not enabled.
            TypeError: If `target_conduit` is not an `IConduit` instance.
            RuntimeError: If the target conduit does not have a valid creation context.
        """
        ...

    def sever_link(self, target_conduit: 'IConduit') -> bool:
        """
        Public API

        Sever the link and the corresponding spell contracts between this Conduit and its target Conduit.

        This method validates the link's existence, ensures it can be severed according to policy,
        and removes the link and all contracted spells. This is intended for public use to dissolve a relationship.

        Args:
            target_conduit (IConduit): The target Conduit whose link to sever.

        Returns:
            bool: True if the link was successfully severed.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            RuntimeError: If dynamic environment is not enabled.
        """
        ...

    def get_links(self):
        """
        Public API

        Returns a list of all active peer links associated with this conduit.

        This list excludes links to lesser (child) conduits.

        Returns:
            list: A list of the linked conduit instances.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            RuntimeError: If dynamic environment is not enabled.
        """
        ...

    def get_lesser_conduit(self, conduit_id: str) -> Optional['IConduit']:
        """
        Internal

        Returns a specific lesser conduit (child) linked to this conduit by its ID.

        Args:
            conduit_id (str): The ID of the lesser conduit to retrieve.

        Returns:
            Optional[IConduit]: The linked lesser conduit if found, otherwise None.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        ...

    def get_initiated_conduit(self, conduit_id: str) -> Optional['IConduit']:
        """
        Public API

        Retrieves the conduit that this conduit has initiated a contract *toward*.

        This method uses the internal index to resolve an outbound connection,
        where this conduit was the **initiator** of the contract.

        Args:
            conduit_id (str): The ID of the target conduit this conduit linked to.

        Returns:
            Optional[IConduit]: The target conduit if the link exists, otherwise None.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        ...

    def get_provider_conduit(self, conduit_id: str) -> Optional['IConduit']:
        """
        Public API

        Retrieves the conduit that initiated a contract *to this* conduit.

        This method uses the internal index to resolve an inbound connection,
        where another conduit linked to this one as the **provider**.

        Args:
            conduit_id (str): The ID of the source conduit that linked to this one.

        Returns:
            Optional[IConduit]: The source conduit if the link exists, otherwise None.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        ...

    def get_initiated_conduits(self) -> list['IConduit']:
        """
        Public API

        Returns a list of all conduits that this conduit has initiated contracts toward (outbound links).

        This is useful for understanding the dependencies and relationships initiated by this conduit.

        Returns:
            list[IConduit]: A list of conduits this conduit linked to.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        ...

    def get_provider_conduits(self) -> list['IConduit']:
        """
        Public API

        Returns a list of all conduits that have initiated contracts to this conduit (inbound links).

        These are the conduits that depend on this one for contracted spells.

        Returns:
            list[IConduit]: A list of conduits that have linked to this conduit as the provider.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        ...

    def cleanup_lesser_conduits(self) -> None:
        """
        Public API

        Cleans up all lesser conduits (children) linked to this conduit.

        This prevents further operations on lesser conduits and is typically used when the parent
        is cleaning or undergoing a major state change (e.g., upgrade).

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        ...

    # ------------------------------------------------------------------
    # Conduit Resolution Validation API
    # ------------------------------------------------------------------
    def get_resolution_state(self) -> Optional['IConduitResolutionState']:
        """
        Public API

        Return the per-conduit resolution state for this conduit.

        Purpose:
            Expose conduit-scoped Phase 5-7 validity and diagnostics without
            running validation.
        Contract:
            - Does not mutate or revalidate; returns existing state only.
            - Lesser conduits resolve state via their root conduit id.
            - Returns None when no resolution state has been recorded.
        Returns:
            Optional[IConduitResolutionState]:
                Resolution state for this conduit (or its root), if present.
        Raises:
            RuntimeError: If the conduit is cleaned or the root conduit is unavailable.
            RuntimeError: If the Spellbook is not available on this conduit.
        Threading:
            Implementations should resolve identity under conduit locks and
            rely on SpellSystemStates for state-level synchronization.
        """
        ...

    def validate_resolution(self, *, refresh_structural: bool = True) -> Optional['IConduitResolutionState']:
        """
        Public API

        Run structural and conduit-scoped resolution validation, then return the state.

        Purpose:
            Provide an explicit preflight validation hook after linking or
            contracting spells so callers can confirm readiness.
        Contract:
            - When refresh_structural is True, runs structural phases (1-4) first.
            - Always runs resolution phases (5-7) for this conduit scope.
            - Returns the conduit-scoped resolution state after validation.
        Args:
            refresh_structural:
                Whether to run structural validation before conduit validation.
        Returns:
            Optional[IConduitResolutionState]:
                Resolution state for this conduit (or its root), if present.
        Raises:
            RuntimeError: If the conduit is cleaned or the root conduit is unavailable.
            RuntimeError: If the Spellbook or SpellSystemStates are unavailable.
            SpellbookValidationError:
                Propagated if structural or resolution validation fails.
        Threading:
            Implementations should avoid holding conduit locks while executing
            phase pipelines to prevent long-held lock contention.
        """
        ...

    # ------------------------------------------------------------------
    # Spell Contracting API
    # ------------------------------------------------------------------
    def _qualify_contracts(self) -> None:
        """
        Internal

        Performs checks to ensure the conduit is in a state capable of managing spell contracts.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            RuntimeError: If the Conduit is not a 'normal' conduit.
            RuntimeError: If dynamic environment is not enabled.
        """
        ...

    def add_spell_to_contract(
            self,
            *,
            spell: 'ISpell' = None,
            spell_id: str = None,
            conduit: 'IConduit' = None,
            conduit_id: str = None,
            permissions: str = "create",
            aetheric_frame="default",
            reason: Any = None,
            root_spell_id: str | None = None,
            link_dependencies: bool = False,
    ) -> bool | None:
        """
        Public API

        Establishes a single spell contract between this conduit and another target conduit.

        This allows one conduit to borrow or grant a specific spell, identified either by object or ID,
        to/from a peer conduit. The contract defines the permissions under which the spell can be used.

        You must provide either a `spell` object or a `spell_id`. The target conduit must be specified
        either directly or resolved via its ID and aetheric frame. Contract mutations require an
        active link transaction that includes both conduits.

        Args:
            spell (ISpell, optional): The spell object to contract.
            spell_id (str, optional): The unique ID of the spell to contract.
            conduit (IConduit, optional): The target conduit to contract with.
            conduit_id (str, optional): The str of the target conduit (used if `conduit` is not provided).
            permissions (str): The permission level granted for this spell (default is "create").
            aetheric_frame (str): Optional frame override used to locate the target conduit.

        Returns:
            bool | None: True if the contract was created, False otherwise. None if an internal error occurs.

        Raises:
            RuntimeError: If the Conduit fails contract qualification checks (cleaned, not normal, not dynamic).
            RuntimeError: If no active link transaction is present for this contract mutation.
        """
        ...

    def add_spells_to_contract(
            self,
            spell_ids: list[str],
            conduit: 'IConduit' = None,
            conduit_id: str = None,
            permissions: str = "create",
            aetheric_frame="default",
            reason: Any = None,
            link_dependencies: bool = False,
    ) -> dict:
        """
        Public API

        Establishes multiple spell contracts with another conduit in a single operation.

        Allows you to bulk-grant or bulk-borrow spells by specifying a list of spell IDs. Each spell
        will be contracted using the same permission level.

        Args:
            spell_ids (list[str]): List of spell IDs to contract.
            conduit (IConduit, optional): The target conduit to contract with.
            conduit_id (str, optional): The id of the target conduit (used if `conduit` is not provided).
            permissions (str): The permission level granted for all spells (default is "create").
            aetheric_frame (str): Optional frame override used to locate the target conduit.

        Returns:
            dict: Dictionary of `spell_id` -> success boolean for each attempted contract.

        Raises:
            RuntimeError: If the Conduit fails contract qualification checks (cleaned, not normal, not dynamic).
            RuntimeError: If no active link transaction is present for this contract mutation.
        """
        ...

    def remove_spell_from_contract(
            self,
            *,
            spell: 'ISpell' = None,
            spell_id: str = None,
            conduit: 'IConduit' = None,
            conduit_id: str = None,
            root_spell_id: str | None = None,
            aetheric_frame="default",
    ) -> bool | None:
        """
        Public API

        Removes a single spell contract between this conduit and another.

        Either the `spell` or `spell_id` can be provided to specify the contract to dissolve.
        Once removed, the spell is no longer accessible across the link.

        Args:
            spell (ISpell, optional): The spell object to remove.
            spell_id (str, optional): The unique ID of the spell to remove.
            conduit (IConduit, optional): The target conduit involved in the contract.
            conduit_id (str, optional): id of the target conduit (used if `conduit` not provided).
            root_spell_id (str, optional): If provided, only removes the source reference for this root.
            aetheric_frame (str): Optional frame override to resolve the target conduit.

        Returns:
            bool | None: True if the spell was successfully removed from the contract, False otherwise. None if an internal error occurs.

        Raises:
            RuntimeError: If the Conduit fails contract qualification checks (cleaned, not normal, not dynamic).
            RuntimeError: If no active link transaction is present for this contract mutation.
        """
        ...

    def remove_spells_from_contract(
            self,
            *,
            spell_ids: list[str] = None,
            conduit: 'IConduit' = None,
            conduit_id: str = None,
            root_spell_id: str | None = None,
            aetheric_frame="default",
    ) -> dict:
        """
        Public API

        Removes multiple spells from an existing contract with a target conduit.

        Useful for bulk cleanup or revocation when retiring behaviors or permissions.

        Args:
            spell_ids (list[str], optional): List of spell IDs to remove.
            conduit (IConduit, optional): Target conduit object.
            conduit_id (str, optional): str of target conduit (used if `conduit` is not provided).
            root_spell_id (str, optional): If provided, only removes the source reference for this root.
            aetheric_frame (str): Optional frame override.

        Returns:
            dict: Dictionary of `spell_id` -> success boolean for each removal attempt.

        Raises:
            RuntimeError: If the Conduit fails contract qualification checks (cleaned, not normal, not dynamic).
            RuntimeError: If no active link transaction is present for this contract mutation.
        """
        ...

    def remove_root_from_contracts(self, *, root_spell_id: str, conduit: 'IConduit' = None,
                                   conduit_id: str = None, aetheric_frame: str = "default") -> dict:
        """
        Public API

        Removes a root spell_id (and any dependency Details attributed to it) from one
        contract or all contracts. Orphaned Details trigger contracted spell removal;
        empty contracts are severed.

        Contract mutations require an active link transaction that includes the
        borrower and the peer conduits involved in the contract cleanup.
        """
        ...

    def add_spell_to_contract_with_dependencies(
            self,
            *,
            spell: 'ISpell' = None,
            spell_id: str = None,
            conduit: 'IConduit' = None,
            conduit_id: str = None,
            permissions: str = "create",
            aetheric_frame: str = "default",
    ) -> bool | None:
        """
        Public API helper

        Adds a spell to a contract and automatically links its dependencies
        (recursively) using the same permission level (downgraded to read when needed).
        """
        ...

    def _remove_all_spells_from_contract(
            self,
            *,
            conduit: 'IConduit' = None,
            conduit_id: str = None,
            aetheric_frame="default",
    ) -> bool | None:
        """
        Public API

        Dissolves **all** spell contracts between this conduit and the specified target.

        All borrowed and granted spells in the active contract will be severed, effectively
        resetting the spell relationship between the two conduits.

        Args:
            conduit (IConduit, optional): Target conduit object.
            conduit_id (str, optional): str of target conduit (used if `conduit` is not provided).
            aetheric_frame (str): Optional frame override.

        Returns:
            bool | None: True if all spells were successfully removed, False otherwise. None if an internal error occurs.

        Raises:
            RuntimeError: If the Conduit fails contract qualification checks (cleaned, not normal, not dynamic).
            RuntimeError: If no active link transaction is present for this contract mutation.
        """
        ...

    def get_all_spells_in_contracts(
            self,
            validate: bool = True,
    ) -> Optional[dict[str, list[Tuple[str, 'ISpell']]]]:
        """
        Public API

        Retrieves all active spells that this conduit has access to through its contracts (i.e., borrowed spells).

        Walks all current spell contracts and collects the spell IDs and objects that are currently
        borrowed from other conduits. Optionally validates contracts before collecting data.

        Args:
            validate (bool): If True, performs contract consistency validation before returning data.

        Returns:
            Optional[dict[str, list[Tuple[str, ISpell]]]]: Dictionary mapping peer conduit ids to lists of (spell_id, ISpell) tuples,
            or None if no contracts exist.

        Raises:
            RuntimeError: If the Conduit fails contract qualification checks (cleaned, not normal, not dynamic).
            TypeError: If `validate` is not a boolean.
        """
        ...

    def get_spell_in_contracts(self, spell_id: str) -> Optional[tuple[str, 'ISpell']]:
        """
        Public API

        Searches all known contracts to find the origin of a specific contracted spell.

        Looks for a specific spell by ID and returns the str of the conduit it's contracted from
        along with the spell object, if found.

        Args:
            spell_id (str): The unique ID of the spell.

        Returns:
            Optional[tuple[str, ISpell]]: Tuple of (`conduit_id`, `spell`) if found, otherwise None.

        Raises:
            RuntimeError: If the Conduit fails contract qualification checks (cleaned, not normal, not dynamic).
            TypeError: If `spell_id` is not a string.
        """
        ...

    def get_spells_in_contract_by_conduit(
            self,
            conduit_id: str,
    ) -> dict[str, list[tuple[str, 'ISpell']]] | None:
        """
        Public API

        Retrieves all spell contracts associated with a specific peer conduit, identified by id.

        Returns a detailed list of all spells that this conduit currently accesses or has granted
        through its relationship with the specified peer.

        Args:
            conduit_id (str): id of the target peer conduit.

        Returns:
            dict[str, list[tuple[str, ISpell]]] | None: Dictionary of `spell_id` -> (`spell_id`, `ISpell`) tuples or None
            if not found. When a contract exists but contains no spells, inbound/outbound lists are empty.

        Raises:
            RuntimeError: If the Conduit fails contract qualification checks (cleaned, not normal, not dynamic).
            TypeError: If `conduit_id` is not a str.
        """
        ...

    def get_spells_in_contract_by_conduit_name(
            self,
            conduit_name: str,
    ) -> dict[str, list[tuple[str, 'ISpell']]] | None:
        """
        Public API

        Retrieves all spell contracts associated with a peer conduit identified by name.

        Performs resolution using a human-readable name instead of str.

        Args:
            conduit_name (str): Name of the peer conduit.

        Returns:
            dict[str, list[tuple[str, ISpell]]] | None: Dictionary of `spell_id` -> (`spell_id`, `ISpell`) tuples or None if not found.

        Raises:
            RuntimeError: If the Conduit fails contract qualification checks (cleaned, not normal, not dynamic).
            TypeError: If `conduit_name` is not a string.
        """
        ...

    def get_contracted_conduits(self) -> list[Tuple[str, 'IConduit']] | None:
        """
        Public API

        Lists all conduits that have an active spell contract with this conduit.

        Each returned conduit represents a peer in the current dynamic spell network.

        Returns:
            list[Tuple[str, IConduit]] | None: List of (`conduit_id`, `IConduit`) tuples, or None if no contracts exist.

        Raises:
            RuntimeError: If the Conduit fails contract qualification checks (cleaned, not normal, not dynamic).
        """
        ...

    def _describe_contract(self, conduit_id: str) -> dict:
        """
        Public API

        Produces a detailed diagnostic summary of a contract established with a specific conduit.

        This method inspects the contract associated with the provided `conduit_id` and returns metadata
        including the peer conduit’s name, the number of active spells involved, and permission levels.
        Primarily used for debugging, introspection, and UI inspection tools.

        Args:
            conduit_id (str): str of the peer conduit whose contract you wish to examine.

        Returns:
            dict: Dictionary containing contract metadata, including a list of spells and their permissions.

        Raises:
            RuntimeError: If the Conduit fails contract qualification checks (cleaned, not normal, not dynamic).
        """
        ...

    def validate_contracts_and_define(self) -> dict[str, bool]:
        """
        Public API

        Validates all known contracts attached to this conduit and confirms mutual agreement and consistency.

        This performs a deep validation pass, ensuring both sides list the same spells, permissions are symmetrical,
        and all referenced spells are valid.

        Returns:
            dict[str, bool]: Dictionary mapping contract ids to validation results:
                 - True: Contract is valid and consistent
                 - False: Contract is malformed or inconsistent

        Raises:
            RuntimeError: If the Conduit fails contract qualification checks (cleaned, not normal, not dynamic).
        """
        ...

    def validate_received_contracts(self) -> bool:
        """
        Public API

        Performs a high-level validation check across all contracts involving this conduit.

        Aggregates the results of `_validate_contracts_and_define` to determine whether every connected
        contract is structurally valid and symmetrical.

        Returns:
            bool: True if all active contracts pass validation, False otherwise.

        Raises:
            RuntimeError: If the Conduit fails contract qualification checks (cleaned, not normal, not dynamic).
        """
        ...

    # ------------------------------------------------------------------
    # Mutation Research
    # ------------------------------------------------------------------
    def get_mutation_research(self):
        """
        Public API

        Returns the MutationResearch manager for this Conduit's Aetheric Frame.

        Mutation Research is a specialized system that allows AI agents to study and mutate spells and creations.
        If you are a human using this API directly, be aware that Mutation Research is primarily designed for AI-driven
        experimentation and may not be suitable for manual use.

        This method is only available when:
          - The Conduit is a NORMAL conduit.
          - The system is in DYNAMIC mode.

        Returns:
            MutationResearch: The mutation research manager for this Conduit's frame.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            RuntimeError: If the Conduit is a lesser conduit.
            RuntimeError: If dynamic environment is not enabled.
        """
        ...



class IDetail(ICleanable, Protocol):
    """
    An Interface for a 'Detail', a single permission or rule within a Contract.
    """
    _id: str
    @property
    def type(self) -> 'ContractTypes':
        """
        The type of contract detail (e.g., 'grant', 'borrow').
        """
        ...

    def affects_permissions(self) -> bool:
        """
        Checks if this detail modifies spell permissions.

        Returns:
            bool: True if this detail grants or revokes spell access.
        """
        ...


class IConduitCloud(ICleanable, Protocol):
    """
    An Interface for an abstract factory for named conduits.

    The ConduitCloud provides a central location to retrieve conduits by a
    human-readable name, intended for top-level access in
    highly dynamic systems.
    """
    _id: str

    def get_conduit(self, name: str) -> IConduit:
        """
        Retrieves a conduit by its registered name.

        Args:
            name (str): The unique name of the conduit.

        Returns:
            IConduit: The conduit instance.

        Raises:
            RuntimeError: If the ConduitCloud is cleaned.
            ValueError: If a conduit with that name is not found.
        """
        ...

    def _register_conduit(self, conduit: IConduit):
        """
        Registers a named conduit into the cloud. (Internal use)

        Args:
            conduit (IConduit): The conduit instance to register.

        Raises:
            ValueError: If the conduit's name is None or already exists
                in the registry.
        """
        ...


class IAethericFrame(ICleanable, Protocol):
    """
    An Interface for an isolated "universe" or "frame" within the Aether.

    An AethericFrame holds all top-level conduits, spell registries, and
    configurations for a specific, isolated domain.

    Attributes:
        name (str): The unique name of this frame.
        _configuration (Optional[Any]): The frozen configuration for this frame.
        _conduit_cloud (IConduitCloud): The abstract factory for named conduits.
        _conduits (Dict[str, IConduit]): Stores all root conduits.
        _spell_registry (Dict[str, Set[str]]): Maps
            conduit ids to their owned spell IDs.
        _conduit_clusters (Dict[str, List[str]]): Organizes
            conduits into named groups.
    """
    name: str
    _id: str
    _configuration: Optional[Any]  # Use 'Configuration' if it's a known type
    _conduit_cloud: IConduitCloud
    _conduits: 'Dict[str, IConduit]'
    _spell_registry: 'Dict[str, Set[str]]'
    _conduit_clusters: 'Dict[str, List[str]]'

@runtime_checkable
class IAether(ICleanable, Protocol):
    """
    An Interface for the global singleton that holds and manages all AethericFrames.

    Aether is the top-level "universe" of the melder system and acts as the
    central service provider for other internal components of the library.
    """

    def _bind_configuration(self, configuration: Any, aetheric_frame_name: str = "default") -> None:
        """
        Binds a configuration object to a specific Aetheric Frame.

        Args:
            configuration: The configuration object to bind.
            aetheric_frame_name: The name of the frame.

        Raises:
            ValueError: If the specified frame does not exist.
        """
        ...

    def _get_configuration(self, aetheric_frame_name: str = "default") -> Optional[Any]:
        """
        Retrieves the configuration object from a specific Aetheric Frame.

        Args:
            aetheric_frame_name: The name of the frame.

        Returns:
            The configuration object, or None if not set.

        Raises:
            ValueError: If the specified frame does not exist.
        """
        ...

    def _ensure_frame(self, aetheric_frame_name: str = "default") -> "IAethericFrame":
        """
        Ensure an AethericFrame exists for the given name, creating it if missing.

        Purpose:
            Provide a single, thread-safe creation path for named frames so
            Spellbooks can initialize against a new frame without raising.

        Contract:
            - Returns the existing frame when it already exists.
            - Creates and registers a new frame when absent.
            - Does not mutate the default frame pointer unless the name is "default".

        Args:
            aetheric_frame_name: The frame name to ensure exists.

        Returns:
            IAethericFrame: The existing or newly created frame.

        Raises:
            RuntimeError: If the Aether is cleaned or its frame registry is unavailable.
            ValueError: If the frame name is invalid for frame construction.

        Threading:
            Implementations must synchronize frame creation to prevent duplicates.

        Lifecycle:
            Frames created via this method are owned by Aether and cleaned by it.
        """
        ...

    def _register_conduit_cloud(self, conduit: IConduit, aetheric_frame_name: str = "default"):
        """
        Registers a conduit with the ConduitCloud of a specific frame.

        Args:
            conduit: The conduit to register.
            aetheric_frame_name: The name of the frame.

        Raises:
            ValueError: If the specified frame does not exist.
        """
        ...

    def _get_conduit_cloud(self, aetheric_frame_name: str = "default") -> IConduitCloud:
        """
        Retrieves the ConduitCloud instance from a specific frame.

        Args:
            aetheric_frame_name: The name of the frame.

        Returns:
            IConduitCloud: The ConduitCloud for that frame.

        Raises:
            ValueError: If the specified frame does not exist.
        """
        ...

    def _get_conduit_by_name(self, name: str, aetheric_frame_name: str = "default") -> IConduit:
        """
        Finds a root conduit within a frame by its name.

        Args:
            name (str): The name of the conduit.
            aetheric_frame_name (str): The name of the frame to search in.

        Returns:
            IConduit: The found conduit.

        Raises:
            ValueError: If the frame does not exist or the conduit is not found.
        """
        ...

    def _get_conduit_by_id(self, signature: str, aetheric_frame_name: str = "default") -> IConduit:
        """
        Finds a root conduit within a frame by its id.

        Args:
            signature (str): The id of the conduit.
            aetheric_frame_name (str): The name of the frame to search in.

        Returns:
            IConduit: The found conduit.

        Raises:
            ValueError: If the frame does not exist or the conduit is not found.
        """
        ...

    def _add_conduit(self, conduit: IConduit, aetheric_frame_name: str = "default"):
        """
        Adds a new root conduit to a frame. (Internal use)

        Args:
            conduit (IConduit): The conduit to add.
            aetheric_frame_name (str): The name of the frame.

        Raises:
            ValueError: If the frame does not exist or the conduit ID already exists.
        """
        ...

    def _remove_conduit(self, conduit: IConduit, aetheric_frame_name: str = "default"):
        """
        Removes a root conduit from a frame. (Internal use)

        Args:
            conduit (IConduit): The conduit to remove.
            aetheric_frame_name (str): The name of the frame.

        Raises:
            ValueError: If the frame does not exist or the conduit is not found.
        """
        ...

    def _create_cluster(self, cluster_name: str, aetheric_frame_name: str = "default"):
        """
        Creates a new conduit cluster within a frame. (Internal use)

        Args:
            cluster_name (str): The name for the new cluster.
            aetheric_frame_name (str): The name of the frame.

        Raises:
            ValueError: If the frame does not exist or the cluster name is taken.
        """
        ...

    def _add_conduit_to_cluster(self, conduit: IConduit, cluster_name: str, aetheric_frame_name: str = "default"):
        """
        Adds a conduit's str to a cluster. (Internal use)

        Args:
            conduit (IConduit): The conduit to add.
            cluster_name (str): The name of the cluster.
            aetheric_frame_name (str): The name of the frame.

        Raises:
            ValueError: If the frame or cluster does not exist.
        """
        ...

    def _remove_conduit_from_cluster(self, conduit: IConduit, cluster_name: str, aetheric_frame_name: str = "default"):
        """
        Removes a conduit's str from a cluster. (Internal use)

        Args:
            conduit (IConduit): The conduit to remove.
            cluster_name (str): The name of the cluster.
            aetheric_frame_name (str): The name of the frame.

        Raises:
            ValueError: If the frame or cluster does not exist.
        """
        ...

    def _get_conduits_in_cluster(self, cluster_name: str, aetheric_frame_name: str = "default") -> 'List[str]':
        """
        Gets a list of all conduit id in a specific cluster.

        Args:
            cluster_name (str): The name of the cluster.
            aetheric_frame_name (str): The name of the frame.

        Returns:
            List[str]: A list of conduit ids.

        Raises:
            ValueError: If the frame or cluster does not exist.
        """
        ...

    def _get_conduit_by_spell_id(self, spell_id: str, aetheric_frame_name: str = "default") -> IConduit:
        """
        Finds the conduit that owns a specific spell ID within a frame.

        Args:
            spell_id (str): The spell ID (SHA256 hash) to search for.
            aetheric_frame_name (str): The name of the frame.

        Returns:
            IConduit: The conduit that owns the spell.

        Raises:
            ValueError: If the frame does not exist or the spell ID is not found.
        """
        ...

    def _check_for_spell(self, spell_id: str, aetheric_frame_name: str = "default") -> bool:
        """
        Checks if a spell ID is registered in any conduit within a frame.

        Args:
            spell_id (str): The spell ID to check.
            aetheric_frame_name (str): The name of the frame.

        Returns:
            bool: True if the spell exists, False otherwise.

        Raises:
            ValueError: If the frame does not exist.
        """
        ...

    def _add_spells_to_aether(self, conduit_id: str, spell_set: 'Set[str]', aetheric_frame_name: str = "default"):
        """
        Registers a set of spell IDs as being owned by a specific conduit.

        Args:
            conduit_id (str): The id of the owning conduit.
            spell_set (Set[str]): A set of spell IDs to register.
            aetheric_frame_name (str): The name of the frame.

        Raises:
            ValueError: If the frame does not exist or the conduit ID is
                already registered.
        """
        ...

    def cleanup_aetheric_frames(self):
        """
        Cleans all aetheric frames and their contents.
        """
        ...

@runtime_checkable
class IChannelLogger(ICleanable, Protocol):
    """
    ChannelLogger
    -------------
    Concurrency-safe facade over one or more Python `logging.Logger` instances,
    registered to IRIS channels. Emits a single `LogRecord` per call, forwards it
    to all configured loggers, then notifies IRIS subscribers.

    This version adds **local state controls** so each ChannelLogger can be
    independently enabled/disabled and filtered by a minimum level, with
    optional **overrides** that can be imposed by a higher-level controller.

    Additions:
    - **groups** (membership): `Set[str]` of tokens (e.g., "SYSTEM", "PIPELINE_A").
      Snapshot is attached to each record as `record.groups` (List[str]).
    - **properties** (key/value): `Dict[str, Any]` of flat scalars you want
      stamped on every record (e.g., small IDs/flags). Snapshot is attached to each
      record as `record.properties` (Dict[str, Any]).
      (Thread/agent fields from `ContextFilter` are still injected separately.)
    - **state**:
        * `enabled` (bool): default, local on/off switch.
        * `min_level` (int): default local minimum level (e.g., `logging.INFO`).
        * `override_enabled` (Optional[bool]): if set, takes precedence over `enabled`.
        * `override_min_level` (Optional[int]): if set, takes precedence over `min_level`.

    Snapshot semantics:
    - On emit, the logger captures *current* groups/properties under lock and
      attaches those snapshots to the `LogRecord`. Mutations after that do not
      affect the already-created record.
    """
    _id: str
    @property
    def id(self) -> str:
        """
        Get the unique ID of this ChannelLogger.

        Returns:
            str: The ID assigned at construction.
        """
        ...

    @property
    def last_log_time(self) -> float:
        """
        Get the UNIX timestamp of the last emitted (accepted) log call for this ChannelLogger.

        Returns:
            float: Seconds since the epoch for the last accepted record emit attempt.
        """
        ...

    @property
    def name(self) -> str:
        """
        Get the name of this ChannelLogger.

        Returns:
            str: The name assigned at construction.
        """
        ...

    # ===== Channels =====
    def add_channel(self, channel_name: str) -> None:
        """
        Route this ChannelLogger to an additional IRIS channel.

        Creates/attaches the child logger under the channel's parent logger name
        (e.g., "Iris.<console>.<{registrant}>") and records the routing in
        self._channels / self._loggers.
        """
        ...

    def remove_channel(self, channel_name: str) -> bool:
        """
        Stop routing this ChannelLogger to a specific IRIS channel.

        We detect the child logger(s) to drop by inspecting their *parent* logger’s
        monkey-patched attribute `_command_ops_name`, which IrisChannel sets when
        constructing the parent (e.g., "console").
        """
        ...

    # ===== State (enabled/min level/overrides) =====
    def set_enabled(self, value: bool) -> None:
        """
        Set the local enabled flag.

        Args:
            value: True to enable locally, False to disable locally.

        Notes:
            - If `override_enabled` is set (not None), it *overrides* this local flag.
            - Use `get_effective_enabled()` to read the computed effective state.
        """
        ...

    def get_enabled(self) -> bool:
        """
        Get the current local enabled flag (ignoring overrides).

        Returns:
            bool: The local `enabled` setting.
        """
        ...

    def set_override_enabled(self, value: Optional[bool]) -> None:
        """
        Set or clear the override for the enabled flag.

        Args:
            value: True/False to force enabled/disabled; None to remove the override.

        Notes:
            - When not None, `override_enabled` takes precedence over the local `enabled`.
        """
        ...

    def clear_override_enabled(self) -> None:
        """
        Clear the enabled override, reverting to the local `enabled` flag.
        """
        ...

    def get_override_enabled(self) -> Optional[bool]:
        """
        Get the current override for the enabled flag.

        Returns:
            Optional[bool]: The `override_enabled` value (True/False), or None if unset.
        """
        ...

    def get_effective_enabled(self) -> bool:
        """
        Compute the effective enabled state for this ChannelLogger.

        Returns:
            bool: `override_enabled` if set; otherwise the local `enabled` flag.
        """
        ...

    def set_min_level(self, level: str) -> None:
        """
        Set the local minimum logging level.

        Level Reference (standard `logging` levels):
            - NOTSET   (0):    Special value; if used as a threshold it effectively lets everything through.
            - DEBUG    (10):   Detailed diagnostic information useful for development and deep troubleshooting.
            - INFO     (20):   High-level operational events (what the system is doing).
            - WARNING  (30):   Something unexpected or suboptimal happened, but the system can continue.
            - ERROR    (40):   A failure occurred for the current operation; the system may still be running.
            - CRITICAL (50):   The system is in a bad state and may require immediate attention / shutdown.

        Args:
            level: A standard logging level name (e.g., "INFO").

        Notes:
            - Records with a level *below* the effective min level are dropped.
            - If `override_min_level` is set, it takes precedence.
        """
        ...

    def get_min_level(self) -> int:
        """
        Get the current local minimum logging level (ignoring overrides).

        Returns:
            int: The local `min_level` integer.
        """
        ...

    def set_override_min_level(self, level: Optional[str]) -> None:
        """
        Set or clear the override for the minimum logging level.

        Level Reference (standard `logging` levels):
            - NOTSET   (0):    Special value; if used as a threshold it effectively lets everything through.
            - DEBUG    (10):   Detailed diagnostic information useful for development and deep troubleshooting.
            - INFO     (20):   High-level operational events (what the system is doing).
            - WARNING  (30):   Something unexpected or suboptimal happened, but the system can continue.
            - ERROR    (40):   A failure occurred for the current operation; the system may still be running.
            - CRITICAL (50):   The system is in a bad state and may require immediate attention / shutdown.

        Args:
            level: A standard logging level integer (e.g., `INFO`), or None to clear the override.

        Notes:
            - When not None, `override_min_level` takes precedence over local `min_level`.
        """
        ...

    def clear_override_min_level(self) -> None:
        """
        Clear the min-level override, reverting to the local `min_level`.
        """
        ...

    def get_override_min_level(self) -> Optional[int]:
        """
        Get the current override for the minimum logging level.

        Returns:
            Optional[int]: The `override_min_level` value, or None if unset.
        """
        ...

    def _effective_min_level(self) -> int:
        """
        Compute the effective minimum logging level for this ChannelLogger.

        Returns:
            int: `override_min_level` if set; otherwise the local `min_level`.
        """
        ...

    def _should_emit(self, record_level: int) -> bool:
        """
        Decide whether a record at `record_level` should be emitted given current state.

        Args:
            record_level: The logging level of the prospective record (e.g., `logging.DEBUG`).

        Returns:
            bool: True if the ChannelLogger is effectively enabled *and*
                  `record_level >= effective_min_level`; otherwise False.

        Notes:
            - This method performs no side effects and does not construct a `LogRecord`.
            - Called early in `_log()` to avoid unnecessary work when filtered out.
        """
        ...

    # ===== Groups =====
    def add_group(self, name: str) -> None:
        """
        Add a group token.

        Args:
            name: Non-empty string token. No normalization is applied.

        Behavior:
            - No-op if `name` is falsy.
            - Safe under concurrent calls.
        """
        ...

    def remove_group(self, name: str) -> None:
        """
        Remove a group token if present.

        Args:
            name: Group token to remove.

        Behavior:
            - No error if not present (discard semantics).
        """
        ...

    def clear_groups(self) -> None:
        """
        Remove all group tokens from this ChannelLogger.
        """
        ...

    def get_groups_snapshot(self) -> List[str]:
        """
        Get a stable, sorted snapshot of current group tokens.

        Returns:
            List[str]: Unique tokens sorted case-insensitively.
        """
        ...

    # ===== Properties =====
    def set_property(self, key: str, value: Any) -> None:
        """
        Set or update a property to stamp on subsequent records.

        Args:
            key: Non-empty string key (conventional guidance: <= 64 chars, token-like).
            value: Scalar value (str/int/float/bool) recommended. Small payloads only.

        Notes:
            - No serialization is performed here; downstream formatters/archivers decide.
            - Oversized or complex values may increase log overhead.
        """
        ...

    def set_properties(self, data: Dict[str, Any]) -> None:
        """
        Bulk update of properties.

        Args:
            data: Mapping of keys to values. Falsy/empty keys are skipped.

        Notes:
            - Each entry is applied atomically under the internal lock.
        """
        ...

    def remove_property(self, key: str) -> None:
        """
        Remove a property if present.

        Args:
            key: Property key to remove.

        Behavior:
            - Silent no-op when the key is absent.
        """
        ...

    def clear_properties(self) -> None:
        """
        Remove all properties from this ChannelLogger.
        """
        ...

    def get_properties_snapshot(self) -> Dict[str, Any]:
        """
        Get a shallow copy snapshot of all properties.

        Returns:
            Dict[str, Any]: Copy of current properties suitable for attaching to a record.
        """
        ...

    # ===== Emit / Logging =====
    def mask_log(
            self,
            level: int,
            message: str,
            *,
            owner: object,
            groups: Optional[Iterable[str]] = None,
            system_groups: Optional[Iterable[str]] = None,
            properties: Optional[Dict[str, Any]] = None,
            exc_info: Union[None, bool, BaseException] = None,
            **kwargs: Any
    ) -> None:
        """
        Log once with masking enabled, using the owner's display identity
        ('<ULID>.<ClassName>'), and optionally overriding groups/system_groups/properties.
        """
        ...

    def _should_fast_exit(self, level: int) -> bool:
        """
        Fast-path filter to avoid work when logger is cleaned/disabled or level is below gates.
        """
        ...

    def _resolve_caller(self, tmpl_logger, *, stacklevel: int, manual_stack: bool, kwargs: dict):
        """
        Compute caller metadata for LogRecord creation.
        Returns: (fn, lno, func, sinfo)
        """
        ...

    def _normalize_exc_info(self, exc_info):
        """
        Normalize exc_info to either a (type, value, tb) tuple or None.

        - True           -> sys.exc_info(), unless outside an except block (then None)
        - tuple          -> passthrough
        - other truthy   -> None (conservative)
        - falsy/None     -> None
        """
        ...

    def _build_record(
            self,
            tmpl_logger,
            *,
            level: int,
            msg: str,
            args: tuple,
            exc_info,
            fn: str,
            lno: int,
            func: str,
            sinfo,
    ):
        """
        Build a LogRecord with real caller metadata so formatter can render method/module/line.
        """
        ...

    def _apply_identity_and_tags(self, record, *, mask: bool, kwargs: dict):
        """
        Apply identity (id/name) and group/property tags to the LogRecord.
        """
        ...

    def _emit_record(self, record):
        """
        Fan-out to all backing loggers and notify per-channel subscribers.
        """
        ...

    def _log(self, level: int, msg: str, *args, mask: bool = False, **kwargs):
        """
        Internal logging method that creates and dispatches a LogRecord to all
        configured loggers if enabled and above the min level.

        Args:
            level: Logging level (e.g., `logging.INFO`).
            msg: Message string or format string.
            *args: Positional args used with `msg` if it's a format string.
            mask: If True, use masked identity and optional overrides from kwargs.
            **kwargs: Additional keyword arguments (e.g., `exc_info`).
                     Internal keys consumed here (and removed):
                       - _stack_info: bool -> if True, compute caller info (default False)
                       - stacklevel: int -> passed to findCaller (default 3)
                       - _mask_display_name/_mask_display_id/_groups_override/
                         _system_groups_override/_properties_override (masking branch)
        """
        ...

    def info(self, msg: str, *args, **kwargs) -> None:
        """
        Log a message with `INFO` level.

        Args:
            msg: Message string or format string.
            *args: Positional args used with `msg` if it's a format string.
            **kwargs: Additional keyword arguments (e.g., `exc_info`).

        Notes:
            - Subject to effective enablement and min-level filtering.
        """
        ...

    def warning(self, msg: str, *args, **kwargs) -> None:
        """
        Log a message with `WARNING` level.

        Args:
            msg: Message string or format string.
            *args: Positional args used with `msg` if it's a format string.
            **kwargs: Additional keyword arguments (e.g., `exc_info`).

        Notes:
            - Subject to effective enablement and min-level filtering.
        """
        ...

    warn = warning  # alias

    def error(self, msg: str, *args, **kwargs) -> None:
        """
        Log a message with `ERROR` level.

        Args:
            msg: Message string or format string.
            *args: Positional args used with `msg` if it's a format string.
            **kwargs: Additional keyword arguments (e.g., `exc_info`).

        Notes:
            - Subject to effective enablement and min-level filtering.
        """
        ...

    def debug(self, msg: str, *args, **kwargs) -> None:
        """
        Log a message with `DEBUG` level.

        Args:
            msg: Message string or format string.
            *args: Positional args used with `msg` if it's a format string.
            **kwargs: Additional keyword arguments (e.g., `exc_info`).

        Notes:
            - Subject to effective enablement and min-level filtering.
        """
        ...

    def exception(self, msg: str, *args, **kwargs) -> None:
        """
        Convenience helper to log an exception with `ERROR` level, including traceback.

        Args:
            msg: Message string or format string.
            *args: Positional args used with `msg` if it's a format string.
            **kwargs: Additional keyword arguments. `exc_info` is forced to True.

        Notes:
            - Equivalent to `error(..., exc_info=True)`.
            - Subject to effective enablement and min-level filtering.
        """
        ...

    def critical(self, msg: str, *args, **kwargs) -> None:
        """
        Log a message with CRITICAL level.s
        """
        ...

    fatal = critical

    # ===== System Groups =====
    def _add_system_group(self, name: str) -> None:
        """
        Internal: add a single system group token.

        Args:
            name: Non-empty string token. No normalization is applied.

        Behavior:
            - No-op if `name` is falsy.
            - Safe under concurrent calls.
        """
        ...

    def _add_system_groups(self, names: Optional[Iterable[str]]) -> None:
        """
        Internal: add multiple system group tokens.

        Args:
            names: Iterable of tokens. Falsy/empty tokens are skipped. If None, no-op.

        Behavior:
            - Safe under concurrent calls.
        """
        ...

    def _remove_system_group(self, name: str) -> None:
        """
        Internal: remove a system group token if present.

        Args:
            name: Token to remove.

        Behavior:
            - Silent no-op if not present (discard semantics).
        """
        ...

    def _remove_system_groups(self, names: Optional[Iterable[str]]) -> None:
        """
        Internal: remove multiple system group tokens.

        Args:
            names: Iterable of tokens to remove. If None, no-op.

        Behavior:
            - Silent no-op on missing tokens.
        """
        ...

    def _clear_system_groups(self) -> None:
        """
        Internal: remove all system group tokens.
        """
        ...

    def _has_system_group(self, name: str) -> bool:
        """
        Internal: check membership of a system group token.

        Args:
            name: Token to check.

        Returns:
            bool: True if present, else False.
        """
        ...

    def _get_system_groups_snapshot(self) -> List[str]:
        """
        Internal: get a stable, sorted snapshot of current system group tokens.

        Returns:
            List[str]: Unique tokens sorted case-insensitively.
        """
        ...

    # ===== Metadata convenience =====
    def add_metadata(
            self,
            *,
            groups: Optional[Iterable[str]] = None,
            properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Add group tokens and/or set properties in one call.

        Args:
            groups: Iterable of group tokens to add (ignored if None).
            properties: Mapping of properties to set/overwrite (ignored if None).
        """
        ...

    def remove_metadata(
            self,
            *,
            groups: Optional[Iterable[str]] = None,
            properties: Optional[Iterable[str]] = None,
    ) -> None:
        """
        Remove group tokens and/or delete properties in one call.

        Args:
            groups: Iterable of group tokens to remove (ignored if None).
            properties: Iterable of property keys to delete (ignored if None).
        """
        ...

    def refresh_properties(self, **kwargs: Any) -> None:
        """
        Refresh (set/overwrite) per-record properties in-place.

        Usage:
            ch.refresh_properties(open=self._open, queued=queue.size)
        """
        ...

    refresh_props = refresh_properties




@runtime_checkable
class IConfiguration(ICleanable, Protocol):
    """
    Configuration governs the behavior of the entire system.

    It acts as the configuration core for:
    * **Conduit Management:** How Conduits handle service lifecycles.
    * **Dynamic Behavior:** Flags controlling dynamic linking, expansion, and policies.
    * **System Flags:** Global settings like debugging mode and resource disposal.

    This object should only be configured once and then frozen to prevent any further changes,
    enforcing idempotent laws across the system. Thread-safe operations are ensured with RLock.
    """

    # --- Attributes (surface expectations only) ---
    _frozen: bool
    available_properties: 'Dict[str, Type]'
    _logger_factory: 'Pack[[object], Any] | None'
    _aether_frame: str
    _id: str

    # --- Lifecycle ---

    def cleanup(self) -> None:
        """
        Cleans the configuration, preventing any further modifications and cleaning up resources.

        This method sets both the `cleaned` and `frozen` flags.
        """
        ...

    # --- Core property API ---

    def set_logger_factory(self, factory: Callable[[object], Any] = None) -> None:
        """
        Set the logger factory used to produce per-object loggers.

        Contract:
            factory(obj: object) -> Any   # e.g., Iris ChannelLogger, SafeLogger, stdlib Logger, or None

        Usage:
            - Call with no arguments to install the implementation's default factory
              (the concrete Configuration uses StdLoggerFactory()).
            - Or pass a specific factory to override the default.

        Rules:
            - Must be set BEFORE freeze().
        """
        ...

    def get_logger_for(self, obj: object) -> Any | None:
        """
        Resolve a logger-like for 'obj' using the current logger factory.

        Returns:
            Any | None: Whatever the factory returns, or None if no factory is set.
        """
        ...

    def has_logger_factory(self) -> bool:
        """
        Returns:
            bool: True if a logger factory has been set; False otherwise.
        """
        ...

    def set_property(self, key: str, value: Any) -> None:
        """
        Defines or overwrites a property in the configuration.

        - **Idempotent properties** (e.g., 'system_state') can only be set *once* before the configuration is cleaned.
        - **Non-idempotent properties** can be freely modified before the configuration is frozen.

        Args:
            key (str): The name of the property to set.
            value (Any): The value for the property.

        Raises:
            RuntimeError: If the configuration is cleaned or frozen.
            RuntimeError: If attempting to modify an idempotent property that is already set.
            TypeError: If `key` is not a string.
            ValueError: If an enum conversion fails.
        """
        ...

    def clear_properties(self) -> None:
        """
        Clears all properties in the configuration.

        This method is useful for resetting the configuration to its initial state before it is frozen.

        Raises:
            RuntimeError: If the configuration is cleaned or frozen.
        """
        ...

    def freeze(self) -> None:
        """
        Freezes the configuration property system.

        Once frozen, no properties, including non-idempotent ones, can be modified.
        Validation is performed automatically upon freezing.

        Raises:
            RuntimeError: If the configuration is cleaned.
            ValueError: If configuration validation fails prior to freezing (e.g., missing required properties).
        """
        ...

    def validate(self) -> bool:
        """
        Validates that all required configuration properties exist and match expected types.

        Performs both presence/type checks and enum-specific validation.

        Returns:
            bool: True if all validation checks pass.

        Raises:
            RuntimeError: If the configuration is cleaned.
            ValueError: If any property is missing or has the wrong type/value.
        """
        ...

    def validate_enums(self) -> bool:
        """
        Internal

        Validates that all properties intended to be Enums (like `SystemState`) are indeed set to a valid Enum instance.

        Returns:
            bool: True if all enum values are valid.

        Raises:
            RuntimeError: If the configuration is cleaned.
            ValueError: If a known enum property is set to an invalid type.
        """
        ...

    def get_property(self, key: str) -> Any:
        """
        Retrieves the value of a configuration property.

        Args:
            key (str): The name of the property.

        Returns:
            Any: The stored value (str, int, bool, Enum, etc.).

        Raises:
            RuntimeError: If the configuration is cleaned.
            KeyError: If the property does not exist in the configuration.
        """
        ...

    def has_property(self, key: str) -> bool:
        """
        Checks if a configuration property is defined.

        Args:
            key (str): The property name to check.

        Returns:
            bool: True if the property exists, False otherwise.

        Raises:
            RuntimeError: If the configuration is cleaned.
        """
        ...

    def __iter__(self) -> Iterator[str]:
        """
        Allows iteration over the configuration properties (keys).

        Returns:
            Iterator: Property names (keys) in the configuration.
        """
        ...

    def load_default_dictionary(self) -> None:
        """
        Loads and applies a default set of properties atomically.

        This method sets sensible defaults for core properties like `system_state`, `debugging`, and `disposal`.

        Raises:
            RuntimeError: If the configuration is cleaned.
        """
        ...

    def get_hooks(self, spellbook_id: str) -> Dict[str, list[Callable[..., Any]]]:
        """
        Retrieve the live hook map for a specific Spellbook.

        This returns the internal hook map for ``spellbook_id`` so callers
        (e.g., Conduit / Meld wiring) can share a single hook registry.

        Shape:

            { hook_name: [callables...] }

        Args:
            spellbook_id (str):
                The ID of the Spellbook whose hooks should be retrieved.

        Returns:
            Dict[str, list[Callable[..., Any]]]:
                Mapping of hook name -> list of callables currently registered
                for that Spellbook. Returns an empty dict if no hooks exist yet.

        Raises:
            RuntimeError: If the configuration is cleaned.
        """
        ...
    def add_hooks(self, spellbook_id: str, **hooks: Any) -> None:
        """
        Register multiple system hooks for a specific Spellbook in one call.

        Each keyword argument maps a hook name to either:
            * A single callable, or
            * An iterable of callables.

        The internal registry shape is:

            _hooks[spellbook_id][hook_name] -> list[callables]

        Example:
            cfg.add_hooks(
                "spellbook-123",
                on_meld_pre_resolve=trace_meld_enter,
                on_conduit_cleanup_complete=[cleanup_fn_1, cleanup_fn_2],
                on_contract_created=contract_observer,
            )

        Args:
            spellbook_id (str):
                The ID of the Spellbook these hooks belong to.
            **hooks:
                Mapping of hook name -> callable or iterable[callable].

        Raises:
            RuntimeError: If the configuration is cleaned or frozen.
            ValueError: If any hook name is unknown.
            TypeError: If any value is not a callable or an iterable of callables.
        """
        ...

    # ---------------------------
    # Fluent / Builder-style API
    # ---------------------------
    def with_hook(self, spellbook_id: str, hook_name: str, hook: Callable[..., Any]) -> 'IConfiguration':
        """
        Fluent

        Register a single system hook for a specific Spellbook and return ``self``.

        This is a fluent wrapper over :meth:`add_hook`, supporting all valid
        hook names defined in :attr:`_ALLOWED_HOOKS`.

        Example:
            (Configuration()
                .with_defaults()
                .with_hook("spellbook-123", "on_meld_pre_resolve", trace_meld_enter)
                .with_hook("spellbook-123", "on_conduit_cleanup_complete", cleanup_fn)
                .finalize())
        """
        ...

    def with_hooks(self, spellbook_id: str, **hooks: Any) -> 'IConfiguration':
        """
        Fluent

        Register multiple system hooks for a specific Spellbook in one call
        and return ``self``.

        Each keyword argument maps a hook name to either:
            * A single callable, or
            * An iterable of callables.

        Example:
            (Configuration()
                .with_defaults()
                .with_hooks(
                    "spellbook-123",
                    on_meld_pre_resolve=trace_meld_enter,
                    on_conduit_pre_created=log_conduit_construction,
                    on_contract_created=[observer_1, observer_2],
                )
                .finalize())
        """
        ...
    def clear_logger_factory(self) -> 'IConfiguration':
        """
        Clear the logger factory (pre-freeze only) and return `self`.
        """
        ...

    def with_logger_factory(self, factory: Callable[[object], Any]) -> 'IConfiguration':
        """
        Fluent

        Set the logger factory (factory(obj) -> Any) and return `self`.
        Must be called before freeze().
        """
        ...

    def with_defaults(self) -> 'IConfiguration':
        """
        Fluent

        Load Melder’s standard defaults into this configuration and return `self`
        so you can keep chaining.

        Behavior:
        - Sets: system_state="automatic", debugging=False, disposal=False,
          disposal_method_names=[].
        - Respects idempotency and immutability rules (raises if frozen or cleaned).

        Returns:
            IConfiguration: This same configuration instance (for chaining).
        """
        ...

    def with_system_state(self, state: 'SystemState | str') -> 'IConfiguration':
        """
        Fluent

        Set the system state ("automatic" or "dynamic") and return `self`.

        Notes:
        - Accepts either SystemState or a case-insensitive string.
        - Idempotent: can be set only once before freeze; attempting to overwrite raises.

        Args:
            state: Desired system state (SystemState or "automatic"|"dynamic").

        Returns:
            IConfiguration: This same configuration instance (for chaining).
        """
        ...

    def with_debugging(self, enabled: bool = True) -> 'IConfiguration':
        """
        Fluent

        Enable or disable debugging and return `self`.

        Args:
            enabled: True to enable debugging; False to disable.

        Returns:
            IConfiguration: This same configuration instance (for chaining).
        """
        ...

    def with_disposal(self, enabled: bool = True) -> 'IConfiguration':
        """
        Fluent

        Enable or disable disposal features and return `self`.

        Args:
            enabled: True to enable disposal semantics; False to disable.

        Returns:
            IConfiguration: This same configuration instance (for chaining).
        """
        ...

    def with_disposal_method_names(self, names: list[str]) -> 'IConfiguration':
        """
        Fluent

        Replace the entire list of disposal method names and return `self`.

        Example:
            cfg.with_disposal_method_names(["close", "cleanup"])

        Args:
            names: Full replacement list of method names (strings).

        Returns:
            IConfiguration: This same configuration instance (for chaining).
        """
        ...

    def add_disposal_methods(self, *names: str) -> 'IConfiguration':
        """
        Fluent

        Append one or more disposal method names (deduplicated, order-preserving)
        and return `self`.

        Behavior:
        - Initializes the list to [] if unset.
        - Preserves existing order; adds new names at the end if not already present.

        Args:
            *names: One or more method names to add.

        Returns:
            IConfiguration: This same configuration instance (for chaining).
        """
        ...

    def finalize(self) -> 'IConfiguration':
        """
        Fluent

        Validate and freeze, returning `self`.

        Returns:
            IConfiguration: This same configuration instance (for chaining).
        """
        ...

    def build(self) -> 'IConfiguration':
        """
        Fluent alias for finalize().
        """
        ...

    def dynamic_defaults(self) -> 'IConfiguration':
        """
        Fluent

        Load defaults and set dynamic state, returning `self`.
        """
        ...

    def automatic_defaults(self) -> 'IConfiguration':
        """
        Fluent

        Load defaults and set automatic state, returning `self`.
        """
        ...




@runtime_checkable
class ISafeLogger(ICleanable, Protocol):
    """
    Structural contract for SafeLogger-like objects.

    Masking (optional; default False):
      - When `mask=True` and the underlying logger is a ChannelLogger, the call routes
        to ChannelLogger.mask_log(...) using the provided identity & tags.
      - When wrapping a standard logging.Logger, masking params are ignored (no-op).

    Notes:
      - Signatures mirror SafeLogger's public API (including mask options).
      - `exception()` is an explicit helper (equivalent to error(..., exc_info=True)).
      - `cleanup()` aligns with Cleanable semantics.
    """

    # Optional: some implementations surface an identifier
    _id: str  # runtime presence not enforced by Protocol, but allowed for duck-typing

    # ---- Core API --------------------------------------------------------------

    def debug(
            self,
            msg: str,
            method_name: str,
            *,
            mask: bool = False,
            owner: object = None,
            owner_id: Optional[str] = None,
            owner_display: Optional[str] = None,
            groups: Optional[Iterable[str]] = None,
            system_groups: Optional[Iterable[str]] = None,
            properties: Optional[Dict[str, Any]] = None,
    ) -> None: ...

    def info(
            self,
            msg: str,
            method_name: str,
            *,
            mask: bool = False,
            owner: object = None,
            owner_id: Optional[str] = None,
            owner_display: Optional[str] = None,
            groups: Optional[Iterable[str]] = None,
            system_groups: Optional[Iterable[str]] = None,
            properties: Optional[Dict[str, Any]] = None,
    ) -> None: ...

    def warning(
            self,
            msg: str,
            method_name: str,
            *,
            mask: bool = False,
            owner: object = None,
            owner_id: Optional[str] = None,
            owner_display: Optional[str] = None,
            groups: Optional[Iterable[str]] = None,
            system_groups: Optional[Iterable[str]] = None,
            properties: Optional[Dict[str, Any]] = None,
    ) -> None: ...

    def error(
            self,
            msg: str,
            method_name: str,
            *,
            exc_info: Union[None, bool, BaseException] = True,
            mask: bool = False,
            owner: object = None,
            owner_id: Optional[str] = None,
            owner_display: Optional[str] = None,
            groups: Optional[Iterable[str]] = None,
            system_groups: Optional[Iterable[str]] = None,
            properties: Optional[Dict[str, Any]] = None,
    ) -> None: ...

    def exception(
            self,
            msg: str,
            method_name: str,
            *,
            mask: bool = False,
            owner: object = None,
            owner_id: Optional[str] = None,
            owner_display: Optional[str] = None,
            groups: Optional[Iterable[str]] = None,
            system_groups: Optional[Iterable[str]] = None,
            properties: Optional[Dict[str, Any]] = None,
    ) -> None: ...

    def critical(
            self,
            msg: str,
            method_name: str,
            *,
            mask: bool = False,
            owner: object = None,
            owner_id: Optional[str] = None,
            owner_display: Optional[str] = None,
            groups: Optional[Iterable[str]] = None,
            system_groups: Optional[Iterable[str]] = None,
            properties: Optional[Dict[str, Any]] = None,
    ) -> None: ...


@runtime_checkable
class IContract(ICleanable, Protocol):
    """
    A symmetric contract between two conduit wards.

    Each contract maintains permission details for both sides independently.
    There is no directional bias (no initiator or provider); both parties
    may define what spells they allow the other to use.

    Fields:
    - _ward_a / _ward_b: The two conduit ward participants in this contract.
    - _details_a / _details_b: Spell permission maps for each ward's view.
    - _id: Unique identifier for this contract instance.
    """

    _id: str
    _ward_a: IConduitWard
    _ward_b: IConduitWard
    _details_a: 'Dict[str, IDetail]'
    _details_b: 'Dict[str, IDetail]'

    def _clean_up(self) -> None:
        """
        Internal

        Cleanup and clear all spell details from both sides.
        """
        ...

    def _get_peer(self, ward: IConduitWard) -> IConduitWard:
        """
        Internal

        Return the opposite conduit in this contract.
        """
        ...

    def _get_opposite_conduit(self, contract: 'IContract', known_id: str) -> Optional[IConduit]:
        """
        Internal

        Helper to find the opposite conduit in a contract based on a known conduit ID.
        :param contract:
        :param known_id:
        :return:
        """
        ...

    def _get_detail_map(self, ward: IConduitWard) -> 'Dict[str, IDetail]':
        """
        Internal

        Helper to return the permission map associated with a given ward.
        """
        ...

    def _add(self, ward: IConduitWard, contract_detail: IDetail) -> None:
        """
        Internal

        Add a spell-level permission detail to the contract on behalf of the given ward.
        """
        ...

    def _remove(self, ward: IConduitWard, spell_id: str) -> None:
        """
        Internal

        Remove a spell-level permission detail from the given ward's view.
        """
        ...

    def _clear_contract(self) -> None:
        """
        Internal

        Clear all spell details from both sides of the contract.
        This is typically called when cleaning the contract.
        """
        ...

    def _check_if_exists_and_permissions(self, ward: IConduitWard, spell_id: str, permission: 'Permissions') -> bool:
        """
        Internal

        Check if the given ward has permission for the specified spell.
        """
        ...

    def _check_if_exists(self, ward: IConduitWard, spell_id: str) -> bool:
        """
        Internal

        Check if a spell exists in the given ward's permission map.
        """
        ...

    def _find_spell_in_ward(self, spell_id: str) -> IConduitWard | None:
        """
        Internal

        Check if a spell exists in the given ward's permission map.
        """
        ...

    def _grant(self, ward: IConduitWard, spell_ids: list[str], permission: 'Permissions') -> None:
        """
        Internal

        Grant a list of spells with a single permission type for the specified ward.

        Args:
            ward (IConduitWard): The ward granting access.
            spell_ids (list[str]): List of spell IDs to grant.
            permission (Permissions): The permission level to assign.
        """
        ...

@runtime_checkable
class IConduitResolutionState(ICleanable, Protocol):
    """
    Per-conduit resolution validity container.

    This protocol mirrors the ConduitResolutionState API used to track
    Phases 5-7 validity and diagnostics for a specific conduit.
    """

    _conduit_id: str

    def get_spell_validity(self, spell_id: str) -> Optional['SpellValidity']:
        """
        Return the stored resolution validity for a spell id.
        """
        ...

    def set_spell_validity(
            self,
            spell_id: str,
            validity: 'SpellValidity',
            *,
            change_reason: Optional['SpellStateChangeReason'] = None,
    ) -> None:
        """
        Set resolution validity for a single spell id.
        """
        ...

    def bulk_set_spell_validity(
            self,
            validity_map: Mapping[str, 'SpellValidity'],
            *,
            change_reason: Optional['SpellStateChangeReason'] = None,
    ) -> None:
        """
        Bulk update resolution validity for spell ids.
        """
        ...

    def get_root_validity(self, root_id: str) -> Optional['SpellValidity']:
        """
        Return the stored resolution validity for a root id.
        """
        ...

    def set_root_validity(
            self,
            root_id: str,
            validity: 'SpellValidity',
            *,
            change_reason: Optional['SpellStateChangeReason'] = None,
    ) -> None:
        """
        Set resolution validity for a single root id.
        """
        ...

    def bulk_set_root_validity(
            self,
            validity_map: Mapping[str, 'SpellValidity'],
            *,
            change_reason: Optional['SpellStateChangeReason'] = None,
    ) -> None:
        """
        Bulk update resolution validity for root ids.
        """
        ...

    def record_diagnostics(self, diagnostics: Sequence['SystemDiagnostic']) -> None:
        """
        Record per-conduit system diagnostics, replacing on signature change.
        """
        ...

    def clear_diagnostics(self) -> None:
        """
        Clear stored diagnostics.
        """
        ...

    def list_diagnostics(self) -> List['SystemDiagnostic']:
        """
        Return a snapshot list of stored diagnostics.
        """
        ...

    def has_errors(self) -> bool:
        """
        Return True if any diagnostic has ERROR severity.
        """
        ...

    def has_warnings(self) -> bool:
        """
        Return True if any diagnostic has WARNING severity.
        """
        ...

    def mark_dirty(self, change_reason: Optional['SpellStateChangeReason'] = None) -> None:
        """
        Mark this resolution state as dirty.
        """
        ...

    def clear_dirty(self, validated_at: float) -> None:
        """
        Mark this resolution state as clean after validation.
        """
        ...

    def last_validated_at(self) -> Optional[float]:
        """
        Return the last successful validation timestamp.
        """
        ...

    def cleanup(self) -> None:
        """
        Cleanup the resolution state and release references.
        """
        ...

@runtime_checkable
class ISpellSystemStates(ICleanable, Protocol):
    """
    Per-frame registry for all SpellSystemState instances.

    This is the "control tower" object:

    - Owns the index: lineage id -> SpellSystemState.
    - Keeps an auxiliary index: current_spell_id -> SpellSystemState
      (for convenience when you only know the version id).
    - Tracks which lineages are currently dirty so higher-level
      DevOps/validation flows can decide what to re-run.
    - Tracks collection dependency indices per Spellbook for targeted
      list[Frame] revalidation.

    Intended lifecycle:

    - One instance per AethericFrame (owned by the frame and initialized
      alongside Spellbook / DevOpsManager).
    - Spellbook / SpellCrafter call:
        * `register_lineage(...)` when a new SpellIndex+Spell appears
        * `update_dependencies(...)` after Phase 3/4 attaches dependency ids
        * `mark_structural_change(...)` when a lineage is rebound/mutated
    - DevOps / validation flows call:
        * `consume_dirty_lineages(...)` to get a worklist
        * `compute_impact_closure(...)` to fan out impacted lineages
    """
    _lock: threading.RLock
    _frame: Optional["AethericFrame"]
    _states_by_index_id: Optional[Dict[str, 'SpellSystemState']]
    _states_by_spell_id: Optional[Dict[str, 'SpellSystemState']]
    _dirty_lineages: Optional['Set[str]']
    _resolution_by_conduit_id: Optional[Dict[str, 'IConduitResolutionState']]
    _lineage_owner_spellbook_id: Optional[Dict[str, str]]
    _collection_frames_by_lineage: Optional[Dict[str, 'Set[str]']]
    _collection_dependents_by_spellbook: Optional[Dict[str, Dict[str, 'Set[str]']]]

    # ------------------------------------------------------------------
    # Registration / lookup
    # ------------------------------------------------------------------
    def register_lineage(self, spell_index: ISpellIndex, spell: ISpell) -> 'SpellSystemState':
        """
        Ensure a SpellSystemState exists for the given lineage and return it.

        Behaviour:
        - If this is the first time we see `spell_index.id`, create a new
          SpellSystemState with `spell_index.current` as the current_spell_id.
        - If it already exists, update its current_spell_id to match
          `spell_index.current`.
        - Update the spell-id index so `get_by_spell_id(...)` can resolve
          by current version id.
        - Mark the lineage as structurally gated with reason
          SpellStateChangeReason.register_or_rebind and add it to the dirty set.

        This is intended to be called from Spellbook.bind(...) or equivalent.
        """
        ...

    def get_by_index_id(self, index_id: str) -> Optional['SpellSystemState']:
        """
        Lookup a SpellSystemState by lineage id.

        Returns:
            - The SpellSystemState instance for this lineage, or
            - None if no state has been registered for the id.
        """
        ...

    def get_by_spell_id(self, spell_id: str) -> Optional['SpellSystemState']:
        """
        Lookup a SpellSystemState by current spell version id.

        This is a convenience when the caller only knows the version id
        (e.g., SpellIndex.current) and wants to find the associated lineage state.

        Returns:
            - The SpellSystemState instance, or
            - None if no state is currently indexed for that spell id.
        """
        ...

    # ------------------------------------------------------------------
    # Dependency wiring (Phase 3/4 integration)
    # ------------------------------------------------------------------
    def update_dependencies(self, spell_index: ISpellIndex, dependency_ids: Iterable[str]) -> None:
        """
        Attach direct dependency ids for this lineage and update reverse edges.

        `dependency_ids` are generic "spell ids" (version or lineage ids) – the
        SpellCrafter / Spellbook decides the semantics. This manager only
        cares about connectivity, not the type system.

        Behaviour:
        - Ensure there is a SpellSystemState for this lineage (create if missing).
        - Compute the delta between previous and new dependency sets.
        - Remove reverse edges from dependencies we no longer reference.
        - Add reverse edges for new dependencies.
        - Mark this lineage as gated due to dependency change and add to
          `_dirty_lineages`.
        """
        ...

    # ------------------------------------------------------------------
    # Dirty / impact queries (used by DevOps / validation governor)
    # ------------------------------------------------------------------
    def mark_structural_change(
            self,
            spell_index: ISpellIndex,
            reason: 'SpellStateChangeReason' = SpellStateChangeReason.structure_changed,
    ) -> None:
        """
        Mark a lineage as structurally changed.

        Typical triggers:
        - New version promoted.
        - Class/method profile changed.
        - Binding semantics changed in a way that affects structure.

        Behaviour:
        - Ensure a SpellSystemState exists for the lineage.
        - Mark it structurally gated with the provided reason.
        - Add the lineage id to `_dirty_lineages`.
        """
        ...

    def mark_collection_dependents_dirty(
            self,
            *,
            spellbook_id: str,
            frame_keys: Iterable[str],
            change_reason: Optional['SpellStateChangeReason'] = None,
    ) -> Set[str]:
        """
        Mark list[Frame] consumers dirty for a specific Spellbook scope.

        Args:
            spellbook_id:
                Owning Spellbook id used to scope the collection index.
            frame_keys:
                Frame keys whose collection memberships changed.
            change_reason:
                Optional reason override; defaults to dependencies_changed.
        Returns:
            Set[str]: Lineage ids marked dirty by this call.
        """
        ...

    def register_local_topology(
            self,
            spell_index: "SpellIndex",
            topology: "SpellLocalTopology",
    ) -> None:
        """
        Register or replace the local constructor topology for the given spell.

        This is invoked from SpellCrafter Phase 3 whenever a spell is (re)built.
        """
        ...

    def get_local_topology(
            self,
            spell_index: "SpellIndex",
    ) -> Optional["SpellLocalTopology"]:
        """
        Retrieve the local constructor topology for the given spell, if any.
        """
        ...

    def get_local_topology_by_id(
            self,
            spell_id: str,
    ) -> Optional["SpellLocalTopology"]:
        """
        Retrieve the local constructor topology using a version-id key.
        """
        ...

    def compute_impact_closure(self, root_index_ids: Iterable[str]) -> Set[str]:
        """
        Compute the transitive closure of impacted lineages downstream.

        Args:
            root_index_ids:
                Lineage ids that changed *directly* (e.g., newly promoted or
                structurally altered).

        Behaviour:
        - Walk reverse edges (`direct_dependents`) starting from each root.
        - Build a set of all lineages that depend (directly or indirectly)
          on any of the roots.
        - For each impacted lineage:
            * Roots: left in their existing structural state (already gated).
            * Non-roots: marked as transitively dirty (impacted_by_dependency).
        - All impacted lineages are added to `_dirty_lineages`.

        Returns:
            A set of all impacted lineage ids, including the roots.
        """
        ...

    def consume_dirty_lineages(self) -> List[str]:
        """
        Pop and return the current set of dirty lineage ids.

        This is the handoff to whatever runs the revalidation / mutation
        governor (your "Phase 5–7" or equivalent).

        Behaviour:
        - Snapshot all ids currently in `_dirty_lineages`.
        - Clear `_dirty_lineages`.
        - Return the snapshot list. Order is unspecified.
        """
        ...

    # ------------------------------------------------------------------
    # Introspection helpers
    # ------------------------------------------------------------------
    def iter_states(self) -> List['SpellSystemState']:
        """
        Snapshot of all SpellSystemState instances currently registered.

        Returns:
            A list of SpellSystemState objects. The list is detached from the
            underlying Dict so callers cannot accidentally keep a
            live iterator into internal state.
        """
        ...

    # ------------------------------------------------------------------
    # Per-conduit resolution state (Phases 5-7)
    # ------------------------------------------------------------------
    def get_conduit_resolution_state(self, conduit_id: str) -> Optional['IConduitResolutionState']:
        """
        Retrieve the per-conduit resolution state for a conduit id.
        """
        ...

    def get_or_create_conduit_resolution_state(self, conduit_id: str) -> 'IConduitResolutionState':
        """
        Retrieve or create the per-conduit resolution state for a conduit id.
        """
        ...

    def drop_conduit_resolution_state(self, conduit_id: str) -> None:
        """
        Remove and cleanup the per-conduit resolution state for a conduit id.
        """
        ...

    def iter_conduit_resolution_states(self) -> Iterator['IConduitResolutionState']:
        """
        Iterate over registered per-conduit resolution states.
        """
        ...

    def set_conduit_spell_validity(
            self,
            conduit_id: str,
            spell_id: str,
            validity: 'SpellValidity',
            *,
            change_reason: Optional['SpellStateChangeReason'] = None,
    ) -> None:
        """
        Set per-conduit resolution validity for a spell id.
        """
        ...

    def bulk_set_conduit_spell_validity(
            self,
            conduit_id: str,
            validity_map: Mapping[str, 'SpellValidity'],
            *,
            change_reason: Optional['SpellStateChangeReason'] = None,
    ) -> None:
        """
        Bulk update per-conduit resolution validity for spell ids.
        """
        ...

    def set_conduit_root_validity(
            self,
            conduit_id: str,
            root_id: str,
            validity: 'SpellValidity',
            *,
            change_reason: Optional['SpellStateChangeReason'] = None,
    ) -> None:
        """
        Set per-conduit resolution validity for a root id.
        """
        ...

    def bulk_set_conduit_root_validity(
            self,
            conduit_id: str,
            validity_map: Mapping[str, 'SpellValidity'],
            *,
            change_reason: Optional['SpellStateChangeReason'] = None,
    ) -> None:
        """
        Bulk update per-conduit resolution validity for root ids.
        """
        ...

    def record_conduit_diagnostics(
            self,
            conduit_id: str,
            diagnostics: Sequence['SystemDiagnostic'],
    ) -> None:
        """
        Record per-conduit system diagnostics, replacing on signature change.
        """
        ...

    def clear_conduit_diagnostics(self, conduit_id: str) -> None:
        """
        Clear per-conduit diagnostics for a conduit id.
        """
        ...

    def mark_conduit_dirty(
            self,
            conduit_id: str,
            change_reason: Optional['SpellStateChangeReason'] = None,
    ) -> None:
        """
        Mark a per-conduit resolution state as dirty.
        """
        ...

    def clear_conduit_dirty(self, conduit_id: str, validated_at: float) -> None:
        """
        Mark a per-conduit resolution state as clean after validation.
        """
        ...


@runtime_checkable
class IDevOpsManager(ICleanable, Protocol):
    """
    Aetheric Frame DevOps hub protocol.

    This interface defines the contract for the hub that owns:
      - IncidentManager        (descriptive: what went wrong, where)
      - ChangeControlManager   (process-level view of pending changes / releases)
      - SpellSystemStates      (graph + dirty/impact state)

    This is the place higher-level tools / AI consult when they want to
    understand or manipulate the health and changes of a frame.
    """
    _lock: threading.RLock
    _spell_system_states: ISpellSystemStates
    _incident_manager: 'IncidentManager'
    _change_control_manager: 'ChangeControlManager'
    # ------------------------------------------------------------------
    # Public API Properties
    # ------------------------------------------------------------------
    @property
    def incident_manager(self) -> Optional['IncidentManager']:
        """
        Read-only exposure of the IncidentManager (descriptive: what went wrong, where).
        """
        ...

    @property
    def change_control_manager(self) -> Optional['ChangeControlManager']:
        """
        Read-only exposure of the ChangeControlManager (process-level view of pending changes / releases).
        """
        ...

    @property
    def spell_system_states(self) -> Optional['ISpellSystemStates']:
        """
        Expose the underlying SpellSystemStates for callers that want
        direct graph/dirty-state access through the DevOpsManager.
        """
        ...


@runtime_checkable
class IIncidentManager(ICleanable, Protocol):
    """
    Protocol for the DevOps incident registry.

    - Creates and stores Incident objects.
    - Provides simple lookup/filtering.
    - Does not enforce any policies; it is purely descriptive.
    """
    _lock: threading.RLock
    _incidents_by_id: 'Dict[str, Incident]'
    _next_numeric_id: int
    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def create_incident(
            self,
            *,
            kind: str,
            severity: 'IncidentSeverity',
            summary: str,
            spell_index_id: Optional[str] = None,
            root_ids: Optional[Iterable[str]] = None,
            details: Optional[Dict[str, Any]] = None,
    ) -> 'Incident':
        """
        Create and register a new Incident. Returns the instance so callers
        can attach it to logs/tests or stash the id.
        """
        ...

    def get_incident(self, incident_id: str) -> Optional['Incident']:
        """
        Look up a single incident by id. Returns None if not found.
        """
        ...

    def list_incidents(
            self,
            *,
            status: Optional['IncidentStatus'] = None,
            spell_index_id: Optional[str] = None,
            kind: Optional[str] = None,
    ) -> List['Incident']:
        """
        Basic filtering; returns a snapshot list of matching incidents.

        Filters:
        - status: only incidents with this IncidentStatus.
        - spell_index_id: only incidents tied to this SpellIndex.id.
        - kind: only incidents with this kind string.
        """
        ...

@runtime_checkable
class IChangeControlManager(ICleanable, Protocol):
    """
    Protocol for the High-level change/release tracker for an Aetheric Frame.

    This is *not* the hot-path resolution guard. It is the DevOps-facing layer
    that knows about:
      - which spell lineages (SpellIndex.id) have pending changes or promotions,
      - lightweight, structured metadata about those changes.

    It does not apply changes or run policies itself; it's a registry that
    higher-level tools (AI agents, DevOps flows, IncidentManager) can inspect
    and update.
    """
    _lock: RLock
    _spell_system_states: "SpellSystemStates"

    # spell_index_id -> Dict[str, Any]
    _pending_changes: 'Dict[str, Dict[str, Any]]'
    _change_control_enabled: bool

    # ----------------------------------------------------------------------
    # Change-control admission controls
    # ----------------------------------------------------------------------
    def enable_change_control(self) -> None:
        """
        Public API

        Enable change-control admission for this frame.

        Purpose:
            Allow the orchestrator admission gate to evaluate requests.
        Contract:
            - When enabled, admission checks apply conflict/embargo rules.
        Returns:
            None.
        Raises:
            RuntimeError: If the manager has been cleaned.
        """
        ...

    def disable_change_control(self) -> None:
        """
        Public API

        Disable change-control admission for this frame.

        Purpose:
            Allow transactions to proceed without conflict/embargo gating.
        Contract:
            - When disabled, admission returns accepted without conflict checks.
        Returns:
            None.
        Raises:
            RuntimeError: If the manager has been cleaned.
        """
        ...

    def is_change_control_enabled(self) -> bool:
        """
        Public API

        Return whether change-control admission is enabled.

        Returns:
            bool: True if admission gating is enabled.
        Raises:
            RuntimeError: If the manager has been cleaned.
        """
        ...

    def set_audit_logger(
            self,
            fn: Optional[Callable[['ChangeControlTransactionRequest'], None]],
    ) -> None:
        """
        Public API

        Register an audit logger for admitted change-control requests.

        Args:
            fn:
                Callable that receives the admitted request, or None.
        Returns:
            None.
        Raises:
            RuntimeError: If the manager has been cleaned.
        """
        ...

    def set_commit_validator(
            self,
            fn: Optional[Callable[['ChangeControlStagedMutation'], None]],
    ) -> None:
        """
        Public API

        Register a commit validator hook for admitted requests.

        Args:
            fn:
                Callable that validates a staged mutation, or None.
        Returns:
            None.
        Raises:
            RuntimeError: If the manager has been cleaned.
        """
        ...

    def set_structural_validator(
            self,
            fn: Optional[Callable[['ChangeControlStagedMutation'], None]],
    ) -> None:
        """
        Public API

        Register a structural validation hook for admitted requests.

        Purpose:
            Provide a hook for running structural phase validation before commit.
        Contract:
            - Passing None disables the hook.
            - Hook is invoked before the commit validator.
        Args:
            fn:
                Callable that validates a staged mutation, or None.
        Returns:
            None.
        Raises:
            RuntimeError: If the manager has been cleaned.
        """
        ...

    def set_commit_hook(
            self,
            fn: Optional[Callable[['ChangeControlStagedMutation'], None]],
    ) -> None:
        """
        Public API

        Register a commit hook for admitted requests.

        Args:
            fn:
                Callable invoked with a staged mutation, or None.
        Returns:
            None.
        Raises:
            RuntimeError: If the manager has been cleaned.
        """
        ...

    def set_dirty_marker(
            self,
            fn: Optional[Callable[['ChangeControlStagedMutation'], None]],
    ) -> None:
        """
        Public API

        Register a commit-time dirty-marker hook.

        Purpose:
            Provide a hook for marking dependency state dirty after commit.
        Contract:
            - Passing None disables dirty marking.
            - Hook is invoked before the commit hook.
        Args:
            fn:
                Callable invoked with a staged mutation, or None.
        Returns:
            None.
        Raises:
            RuntimeError: If the manager has been cleaned.
        """
        ...

    def set_abort_hook(
            self,
            fn: Optional[Callable[['ChangeControlStagedMutation'], None]],
    ) -> None:
        """
        Public API

        Register an abort hook for admitted requests.

        Args:
            fn:
                Callable invoked with a staged mutation, or None.
        Returns:
            None.
        Raises:
            RuntimeError: If the manager has been cleaned.
        """
        ...

    def admit_request(
            self,
            request: 'ChangeControlTransactionRequest',
    ) -> 'ChangeControlAdmissionResult':
        """
        Public API

        Admit a transaction request through the change-control gate.

        Args:
            request:
                Transaction request to admit.
        Returns:
            ChangeControlAdmissionResult:
                Admission decision with evidence for rejection.
        Raises:
            RuntimeError: If the manager has been cleaned.
        """
        ...

    def update_staged_request(
            self,
            request_id: str,
            *,
            scope_keys: Optional[Iterable[str]] = None,
            binding_keys: Optional[Iterable[Tuple[str, str]]] = None,
            contract_keys: Optional[Iterable[Tuple[str, str, str]]] = None,
            metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Public API

        Update staged mutation metadata for an admitted request.

        Purpose:
            Allow callers to refresh staged metadata discovered after admission.
        Contract:
            - Returns False if the request is not staged.
            - Updates only supplied fields; None keeps existing values.
            - Metadata merges into the staged record when provided.
        Args:
            request_id:
                Request identifier to update.
            scope_keys:
                Optional updated scope keys for the staged mutation.
            binding_keys:
                Optional updated binding keys for the staged mutation.
            contract_keys:
                Optional updated contract keys for the staged mutation.
            metadata:
                Optional metadata to merge into the staged record.
        Returns:
            bool: True if the staged record was updated.
        Raises:
            RuntimeError: If the manager has been cleaned.
        """
        ...

    def commit_request(self, request_id: str) -> None:
        """
        Public API

        Commit an in-flight request and release implicit embargoes.

        Args:
            request_id:
                Request id to finalize.
        Returns:
            None.
        Raises:
            RuntimeError: If the manager has been cleaned.
        """
        ...

    def abort_request(self, request_id: str) -> None:
        """
        Public API

        Abort an in-flight request and release implicit embargoes.

        Args:
            request_id:
                Request id to abort.
        Returns:
            None.
        Raises:
            RuntimeError: If the manager has been cleaned.
        """
        ...
    # ----------------------------------------------------------------------
    # Registration / updates
    # ----------------------------------------------------------------------
    def register_pending_change(
            self,
            spell_index: 'ISpellIndex',
            reason: str,
            metadata: Optional[
                Union[Dict[str, Any], 'Dict[str, Any]']
            ] = None,
    ) -> None:
        """
        Record that a given lineage has a pending change (mutation candidate,
        promotion proposal, config swap, etc.).

        This is *bookkeeping only* – it does not apply the change, it just
        surfaces it for DevOps / AI tooling.

        Args:
            spell_index:
                The SpellIndex for the lineage we're tracking.
            reason:
                Short, machine-/human-readable reason code
                (e.g. "mutation_candidate", "rebinding", "config_change").
            metadata:
                Optional free-form metadata.
        """
        ...

    # ----------------------------------------------------------------------
    # Introspection
    # ----------------------------------------------------------------------
    def get_pending_change(
            self,
            spell_index_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Get a *snapshot* of the pending-change metadata for a specific lineage.

        Returns:
            A plain dict copy of the inner Dict metadata if present,
            or None if no pending change exists for that lineage.
        """
        ...

    def list_pending_changes(self) -> Dict[str, Dict[str, Any]]:
        """
        Return a snapshot of all pending changes:

            {
              spell_index_id: { ...metadata... },
              ...
            }

        This is intended for DevOps / AI tooling – not for hot-path use.
        """
        ...

    # ----------------------------------------------------------------------
    # Clearing
    # ----------------------------------------------------------------------
    def clear_pending_change(self, spell_index_id: str) -> None:
        """
        Remove the pending-change entry for the given lineage, if any.

        This is typically called after a release is either:
          - successfully applied, or
          - explicitly cancelled/abandoned.
        """
        ...
