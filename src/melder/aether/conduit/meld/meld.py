from abc import ABC, abstractmethod
from annotationlib import Format
from contextlib import AbstractContextManager, nullcontext
import inspect
from threading import RLock
from typing import (
    TYPE_CHECKING,
    Optional,
    Dict,
    Any,
    Callable,
    List,
    Tuple,
    Sequence,
    ClassVar,
    NoReturn,
    Union,
)


from melder.utilities.general_base.cleanable import Cleanable
# Melder Imports
from melder.utilities.helpers.general_helpers import SpellInputUtils
from melder.utilities.custom_exceptions.hook_execution_error import HookExecutionError
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.utilities.custom_exceptions.spellbook_validation_error import SpellbookValidationError
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state import SpellState
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state_change_reason import (
    SpellStateChangeReason,
)
from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.conduit.meld.creation_context.creation_context_rebuild import (
    CreationContextRebuild,
)
from melder.aether.spellbook.existence.existence import Existence
if TYPE_CHECKING:
    from melder.aether.spellbook.spell_compiler.spell_compiler_system import (
        SpellCompilerSystem,
    )
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spellbook import Spellbook
    from melder.aether.spellbook.bind.spell_index import SpellIndex
    from melder.aether.aetheric_frame.dev_ops.change_control_manager.change_control_manager import ChangeControlManager
    from melder.aether.aetheric_frame.dev_ops.spell_system_states.conduit_resolution_state import ConduitResolutionState
    from melder.aether.conduit.meld.creation_context.creation_context import CreationContext
    from melder.utilities.synchronization.creation_gate import CreationGate

class Meld(Cleanable, ABC):
    """
    ## Meld: Spell Activation and Dependency Resolution

    Meld is the **shared runtime core** for spell activation and dependency
    resolution beneath concrete conduit-facing and spellspace-facing front
    doors.

    It is the runtime bridge between:
    - `Spellbook`, which owns spell metadata and lookup maps
    - SpellSystemStates / change-control state, which decide whether runtime
      resolution is allowed to continue

    Primary responsibilities:
    - resolve a target spell by spell id or normalized lookup key
    - provide the shared refusal diagnostic for non-resolvable registrations;
      concrete execution doors enforce capability while observational lookup remains available
    - normalize per-call override payloads
    - enforce structural validity, contract validity, and per-conduit
      resolution validity before instance access
    - reuse existing creations when allowed, or dispatch into creation-context
      runtime lanes when construction is required
    - run pre-cast, activation, post-cast, and meld-level hooks when present
    - own the foundation runtime compiler system surface for later dynamic
      recompilation ownership work
    - own the per-door fast meld door registry (`_fast_meld_doors`): a plain
      success-only memoization dict, keyed by spell-id string, mapping to
      `(spell, captured_context, captured_epoch, existing_object_entry)`
      tuples used by the concrete doors' guarded warm fast lane. `captured_epoch`
      is the spell's `_door_epoch` read BEFORE the building meld executed;
      every spell-level invalidation chokepoint (hook attach, resolution
      invalidation, creation-context cleanup/reset) bumps the live epoch,
      so a hit needs one int compare plus the context-identity pin instead
      of re-reading each guard flag (shared-object traffic measured at
      2.6x/4.2x pure-door inflation at threads=3/5). The executor is
      deliberately not part of the entry: it is read per hit through the
      captured context's `_no_overrides_executor` slot because phase-11
      hydration hot-swaps that slot in place (cold door -> hot door) on
      first execution. The override arm (2026-09-26) reads the same entry
      for an id-string meld with a non-empty dict payload and calls the
      live `_overrides_executor` slot instead. `existing_object_entry` is
      True when the spell holds a bound object (`user_created_object`); the
      plain arm then returns that object without the door call (2026-09-26),
      since the existing-creation door returns the same slot. The flag keeps
      the check off every other spell's warm path, and it is a bool rather
      than the object so a stale entry never keeps a removed object alive.
      Four readers apply one guard ladder and both arms and must stay
      identical: `ConduitMeld.meld`, `SpellSpaceMeld.meld`,
      `Conduit.meld` (automatic id melds) and `SpellSpace.meld` (id melds,
      2026-09-26). Cardinality is bounded by
      construction because entries are inserted only after a successful
      full-lane meld (no-override or override branch, never for a spell
      holding a mutation override), so the keyspace is the bound-spell
      registry, not caller input. The registry is deleted in `cleanup()`.

    High-level activation flow:
    1. Resolve the target spell from the requested identity inputs.
    2. Normalize per-call override payloads.
    3. Enforce validity/change-control gates and rerun lazy phases when needed.
    4. Reuse an existing creation or build through `CreationContext`.
    5. Fire activation and meld-level hooks when the route requires them.
    6. Return the final resolved instance.

    Threading:
        Concurrency-sensitive by nature: this is the hot path, and under
        free-threaded 3.14t the fast-door registry is read by many threads at
        once. The epoch design above is the concurrency answer - a warm hit
        costs one int compare plus an identity pin rather than re-reading each
        guard flag, because shared-object traffic was measured at 2.6x/4.2x
        pure-door inflation at 3 and 5 threads. Lazy revalidation takes the
        per-spell lock before re-running structural phases.

    Registration:
        MELDER KERNEL. Both subclasses (`ConduitMeld`, `SpellSpaceMeld`) are
        melder-internal and constructed only inside `Conduit.__init__`; there is no
        injection seam - no `meld=` kwarg, no factory hook.

    Subsystem Context:
        The abstract core beneath two concrete front doors. `ConduitMeld` is
        the conduit-caller door; `SpellSpaceMeld` is the spellspace door. The
        split exists purely to own DIFFERENT STORAGE - all lookup, validation,
        gating, and compiler logic lives here so the two doors cannot drift
        apart on resolution semantics. `Conduit.meld(...)` delegates here;
        `CreationContext` executes the construction lanes this class dispatches.

    System Context:
        This class is where the six `Existence` modes stop being an enum and
        become storage routing. `unique_per_conduit` and `many` land in the
        caller's own `ConduitCreations`; `unique`, `unique_per_conduit_cluster`,
        and `unique_per_conduit_lineage` resolve against broader spell-owned or
        cluster-owned stores; `unique_per_spell_space` is reachable only through
        the spellspace door. That is why `ConduitMeld` REFUSES a
        `requires_spellspace_request` spell rather than improvising a scope -
        fabricating request-local scope from the conduit door would silently
        produce an instance with the wrong lifetime, which is far worse than a
        refusal.
        Meld is also the gate, not just the resolver: it enforces structural
        validity, contract validity, per-conduit resolution validity, and
        change-control dirty-root state BEFORE any instance is handed back, and
        re-runs the lazy phases when a lineage's validity is UNKNOWN or GATED.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. ## Meld: Spell Activation and Dependency Resolution. Melder kernel
        machinery: read it to understand the runtime, do not drive it directly.
    """
    __slots__ = [
        "_lock",
        "_conduit_id",
        "_resolution_conduit_id",
        "_dynamic_environment",
        "_spellbook",
        "_owned_spells",
        "_contracted_spells",
        "_spells_by_id",
        "_contracted_spells_by_id",
        "_spell_id_pool",
        "_lookup_owned_spells",
        "_lookup_contracted_spells",
        "_input_resolution_cache",
        "_max_resolution_cache_size",
        "_change_control_manager_by_frame",
        "_meld_hooks",
        "_baseline_meld_hooks",
        "_meld_hooks_modified",
        "_spell_compiler_system",
        "_fast_meld_doors",
        # Canonical creation-store surface (both concrete doors inherit these).
        "_conduit_creations",
        "_root_creations",
        "_cluster_creations",
        "_spellspace_creations",
    ]
    def __init__(
            self,
            spellbook: Spellbook,
            conduit_id: Optional[str] = None,
            resolution_conduit_id: Optional[str] = None,
            dynamic_environment: bool = False,
            meld_hooks: Optional[Dict[str, list[Callable[..., Any]]]] = None,
            conduit_creations=None,
            root_creations=None,
            cluster_creations=None,
            spellspace_creations=None,
    ) -> None:
        """
        Initialize the shared meld runtime core.

        Purpose:
            Capture the immutable spellbook-facing lookup surfaces and the
            conduit-facing runtime metadata that every concrete meld front door
            needs in order to resolve spells, validate runtime readiness, and
            delegate into creation-context execution.

        Contract:
            - Stores direct references to the spellbook's owned and contracted
              lookup maps rather than copying them.
            - Normalizes `resolution_conduit_id` to `conduit_id` when the
              caller does not provide a different root-resolution identity.
            - Creates one per-meld input-resolution cache used by the concrete
              `meld(...)` front doors.
            - Stores the meld-hooks mapping by reference when supplied so shared
              hook updates stay visible without additional synchronization.
            - Starts on that baseline with no local divergence. Pooled runtimes
              track temporary hook references with one bool, read only at lease
              boundaries; ordinary meld dispatch remains unchanged.
            - Owns the canonical creation-store surface (`_conduit_creations`,
              `_root_creations`, `_cluster_creations` facade,
              `_spellspace_creations`); concrete subclasses pass their values in
              and may repoint/assign them post-construction.

        Args:
            spellbook:
                The registry of all known spell configurations. Meld keeps
                direct references to internal spell, lookup, and spell_id
                maps to perform fast, consistent lookups.
            conduit_id:
                Optional identifier for the owning conduit. When supplied,
                this tracks the owning conduit identity.
            resolution_conduit_id:
                Optional identifier used for per-conduit resolution/change-control
                state lookups. For lesser conduits this should be the root conduit id.
            dynamic_environment:
                True when the owning conduit runs in dynamic mode. This flag is
                propagated into creation-context construction so runtime context
                policy can branch by mode without re-reading conduit state.
            meld_hooks:
                Optional hook map passed by Conduit. When provided, Meld stores
                this map by reference so shared hook mutations are immediately
                visible without re-copying.

        Threading:
            - Creates one internal `RLock` used by cleanup and lazy compiler
              helper creation.
            - Assumes the spellbook maps themselves are already protected by the
              owning runtime's synchronization rules.

        Returns:
            None.
        """
        super().__init__()

        self._lock = RLock()
        self._conduit_id: Optional[str] = conduit_id
        self._resolution_conduit_id: Optional[str] = (
            resolution_conduit_id if resolution_conduit_id is not None else conduit_id
        )
        self._dynamic_environment: bool = bool(dynamic_environment)
        self._spellbook: Spellbook = spellbook
        # Spellbook references (used for resolution)
        self._owned_spells: Dict[SpellIndex, Spell] = spellbook._spells
        self._contracted_spells: Dict[str, Dict[SpellIndex, Spell]] = (
            spellbook._contracted_spells
        )
        self._spells_by_id: Dict[str, Spell] = spellbook._spells_by_id
        self._contracted_spells_by_id: Dict[str, Dict[str, Spell]] = spellbook._contracted_spells_by_id
        self._spell_id_pool: Dict[str, Spell] = spellbook._spell_id_pool

        self._lookup_owned_spells: Dict[tuple, SpellIndex] = spellbook._lookup_spells
        self._lookup_contracted_spells: Dict[str, Dict[tuple, SpellIndex]] = (
            spellbook._lookup_contracted_spells
        )
        # Foundation runtime compiler owner surface for later spell compiler
        # ownership decomposition.
        self._spell_compiler_system: Optional[SpellCompilerSystem] = None

        # Front-door resolution caches.
        self._input_resolution_cache: Dict[tuple[Any, Any, Any, Any], str] = {}
        self._max_resolution_cache_size: int = 2048

        # Change-control state.
        self._change_control_manager_by_frame: Dict[str, ChangeControlManager] = {}

        # Optional hook map pulled from Configuration (via Conduit).
        # This is stored by reference when provided.
        self._baseline_meld_hooks: Dict[str, list[Callable[..., Any]]] = (
            meld_hooks if meld_hooks is not None else {}
        )
        self._meld_hooks: Optional[Dict[str, list[Callable[..., Any]]]] = self._baseline_meld_hooks
        self._meld_hooks_modified: bool = False

        # Fast meld door registry: success-only memoization of warm id-string
        # melds. Entries are (spell, captured_context, captured_epoch,
        # existing_object_entry) tuples built by the concrete doors only after
        # one full normal-lane meld succeeded for that spell id, and validated
        # per hit by a live
        # guard ladder (context identity, validation/resolution flags, hook
        # state). The executor is read per hit through the captured context
        # slot because phase-11 hydration hot-swaps it in place. Plain dict on
        # purpose: per-op dict atomicity covers the access pattern, racing
        # first-builds converge last-write-wins, and cardinality is
        # registry-bounded by the success-only insertion rule.
        self._fast_meld_doors: Dict[
            str,
            Tuple[Spell, CreationContext, int, bool],
        ] = {}

        # Canonical creation-store surface. `_conduit_creations` is the owning
        # conduit's store (`unique_per_conduit` / `many`); `_root_creations` is
        # the lineage-root store (defaults to the conduit store for a root
        # conduit, repointed for lessers); `_cluster_creations` holds the
        # ClusterCreations facade (resolved at the front door via
        # `resolved_store()`, assigned post-construction by the owning conduit);
        # `_spellspace_creations` is the active spellspace scope store and is
        # None on the conduit path.
        self._conduit_creations = conduit_creations
        self._root_creations = (
            root_creations if root_creations is not None else conduit_creations
        )
        self._cluster_creations = cluster_creations
        self._spellspace_creations = spellspace_creations

    def cleanup(self) -> None:
        """
        Permanently retire the shared meld runtime core.

        Contract:
            - Idempotent: repeated calls are safe.
            - Thread-safe: guarded by the internal lock.
            - Clears spellbook map references, front-door caches (including the
              fast meld door registry), change-control manager cache, and
              optional compiler-system helper.
            - Drops the meld's references to the creation stores it holds; the
              registries themselves are owned by the conduit / spellspace surface
              and are not cleaned here.
            - After cleanup, this meld instance no longer exposes any live
              runtime lookup surface and must not be reused.

        Returns:
            None.
        """
        if self._cleaned:
            return

        with self._lock:
            if self._cleaned:
                return

            self._cleaned = True

            # Clear spellbook references
            del self._owned_spells
            del self._contracted_spells
            del self._spells_by_id
            del self._contracted_spells_by_id
            del self._spell_id_pool
            del self._lookup_owned_spells
            del self._lookup_contracted_spells
            del self._spellbook
            del self._conduit_id
            del self._resolution_conduit_id
            del self._dynamic_environment
            del self._meld_hooks
            del self._baseline_meld_hooks
            del self._meld_hooks_modified
            del self._input_resolution_cache
            del self._max_resolution_cache_size
            del self._change_control_manager_by_frame
            # Fast-door entries hold spell/context/executor/creations refs;
            # dropping the dict here is the owner-driven release point.
            del self._fast_meld_doors
            if self._spell_compiler_system is not None:
                self._spell_compiler_system.cleanup()
            del self._spell_compiler_system
            # Drop the canonical creation-store references (the registries
            # themselves are owned by the conduit / spellspace, not the meld).
            del self._conduit_creations
            del self._root_creations
            del self._cluster_creations
            del self._spellspace_creations

    @abstractmethod
    def meld(
            self,
            spell: str | object | None = None,
            *,
            spell_name: str | None = None,
            spellframe: str | object | None = None,
            binding_name: str | None = None,
            spell_override: Optional[dict | list | tuple] = None,
    ) -> Optional[Any]:
        """
        Entry point for resolving and activating a spell (component) within this Conduit.

        This method orchestrates the full lifecycle: resolution, reuse, instantiation,
        hook execution, and registration.

        Call shape:
            `spell` is the only positional parameter, so the dominant warm
            pattern is the cheapest possible call: `meld(spell_id)` passes
            one positional argument with no keyword marshaling and routes
            straight into the id-string fast lane. All other entry modes
            (`spell_name`, `spellframe`, `binding_name`, `spell_override`)
            are keyword-only.

        Args:
            spell (str | object | None):
                The primary spell identifier (first positional parameter).
                - If a **string**, treated as the unique `spell_id` (typically the
                  SHA256 structural fingerprint for the SpellIndex).
                - If an **object** (e.g., a class or function), used together with
                  `spellframe` and `binding_name` to form the DI identity key via the
                  `SpellInputUtils` normalization helpers.
            spell_name (str):
                spell_name of the spell to meld (keyword-only).

                When provided without an explicit spell or spellframe, this is
                treated as the **logical name key** used by the resolution pipeline.
                In other words, meld(spell_name=\"MyService\") becomes equivalent
                to a name-based lookup driven by the Spellbook / SpellIndex mappings.
            spellframe (str | object | None):
                Optional Spellframe / Protocol / class used as the primary DI identity.
                Often redundant if `spell` is the class/protocol itself. Spellframes
                act as grouping keys (interfaces, protocol frames, string categories)
                under which multiple spells may be bound.
            binding_name (str | None):
                Optional binding name, used alongside `spell` or `spellframe` to create
                a unique lookup key within a given frame. If omitted, the default
                binding (e.g. `"__default__"`) is used internally.
            spell_override (dict | list | tuple | None):
                Optional override payload attached to the meld call. This payload
                represents **per-call overrides** (constructor arguments, factory
                inputs, etc.) and is normalized into a dictionary by
                :meth:`_normalize_spell_override`.
                The payload is rejected when the resolved spell disables
                override-capable runtime posture.

        Returns:
            Optional[Any]:
                The resolved component instance (either reused or newly created)
                after all pre-/activation-/post-hooks have executed.

        Raises:
            ValueError:
                If none of `spell_name`, `spell`, or `spellframe` are provided.
            KeyError:
                If the spell cannot be resolved by the provided inputs.
            NotImplementedError:
                If the spell type (e.g., class-based DI) or existence mode is not
                yet supported for construction/registration.
            HookExecutionError:
                If a pre-cast, activation, or post-cast hook fails.
            RuntimeError:
                For unexpected internal state issues (e.g., missing object after
                ID resolution, unsupported Creations manager, attempting to
                meld a broken spell, or passing `spell_override` to a spell
                that has overrides disabled).
        """
        raise NotImplementedError("Concrete Meld subclasses must implement meld().")

    # Note: a dedicated `meld_id(spell_id, /)` fast entry briefly existed on
    # this surface. It was removed in favor of the single `meld(...)` API:
    # `spell` now rides the positional seat, so `meld(spell_id)` is the
    # supported minimal-arity warm call shape and no second public resolution
    # method is required.

    @abstractmethod
    def meld_existing_spell(
            self,
            spell_name: str | None = None,
            *,
            spell: str | object | None = None,
            spellframe: str | object | None = None,
            binding_name: str | None = None,
    ) -> Any:
        """
        Return an already-live object for one resolved spell or fail.

        Purpose:
            Provide a cold-path reuse-only runtime operation that resolves
            spell identity the same way `meld(...)` does but never creates.

        Contract:
            - Reuses the same spell identity inputs accepted by `meld(...)`.
            - Never enters any creation path.
            - Returns one already-live object or raises.
            - Supports only lifecycles that can resolve to one deterministic
              existing object.
            - Concrete subclasses decide which live storage surface counts as
              "existing" for the caller: conduit-owned, spellspace-owned, or
              owner-conduit/shared storage.

        Args:
            spell_name:
                Optional logical spell name for name-based resolution.
            spell:
                Optional spell id string or spell object used for resolution.
            spellframe:
                Optional spellframe / protocol / frame key used for
                resolution.
            binding_name:
                Optional binding name used for lookup-key resolution.

        Returns:
            Any: Existing live runtime object for the resolved spell.

        Raises:
            ValueError:
                If the spell is not currently live.
            RuntimeError:
                If the spell lifecycle does not support unambiguous
                existing-object retrieval.
        """
        raise NotImplementedError(
            "Concrete Meld subclasses must implement meld_existing_spell()."
        )

    @abstractmethod
    def purge(
            self,
            spell: Optional[Union[str, object]] = None,
            *,
            spell_name: Optional[str] = None,
            spellframe: Optional[Union[str, object]] = None,
            binding_name: Optional[str] = None,
            purge_all: bool = True,
    ) -> int:
        """
        Define the retirement contract implemented by each concrete Meld door.

        Purpose:
            Keep conduit and SpellSpace purge orchestration on the concrete
            door that owns the corresponding scope rules.

        Contract:
            - Concrete doors use `_resolve_purge_spell` for shared discovery.
            - Each door authorizes and selects its existing creation store.
            - Creations owns the removal locks and recorded disposal work.
            - Discovery never creates an instance or compiles a dependency graph.

        Args:
            spell: Canonical id string, class/function reference or application instance.
            spell_name: Logical name forwarded by the public facade.
            spellframe: Optional frame/type used for binding lookup.
            binding_name: Optional binding name within that frame.
            purge_all: True retires the target's retained entries. False retires
                only the supplied instance from the authorized store.

        Returns:
            int: Number of retired creations, or zero when the selected store
            contains none for the resolved target.

        Raises:
            NotImplementedError: If a subclass calls this abstract body rather
                than implementing its own scope-specific purge operation.
        """
        raise NotImplementedError(
            "Concrete Meld subclasses must implement purge()."
        )

    def _resolve_purge_spell(
            self,
            *,
            spell: Optional[Union[str, object]],
            spell_name: Optional[str],
            spellframe: Optional[Union[str, object]],
            binding_name: Optional[str],
            purge_all: bool,
    ) -> Spell:
        """
        Discover a purge target through the existing meld lookup machinery.

        Purpose:
            Share selector validation and discovery without moving either
            concrete door's scope policy into this base class.

        Contract:
            - Uses `_resolve_spell` unchanged for local/contracted lookup.
            - Returns the already-registered internal definition, never an
              application instance and never a newly constructed definition.
            - Inspects an application instance to obtain its class reference,
              then submits that reference to the existing spell lookup.
            - Explicit selectors remain available; no stored-object search or
              automatic binding/frame recovery is performed during discovery.
            - False requires an instance so retirement never guesses one.
            - Does not select a store, authorize a scope, compile, or dispose.

        Args:
            spell: Canonical id string, class/function reference or application instance.
            spell_name: Optional logical name from the public facade.
            spellframe: Optional frame/type used by ordinary meld discovery.
            binding_name: Optional named binding within that frame.
            purge_all: True selects the whole binding; False requires an instance.

        Returns:
            Spell: Existing definition visible to this Meld door.

        Raises:
            RuntimeError: If this Meld has been cleaned.
            TypeError: If purge_all is not a bool.
            ValueError: If no usable selector is supplied, or False has no instance.
            KeyError: If ordinary meld discovery cannot find the binding.

        Threading / Lifecycle:
            Uses the same lookup maps as meld. Structural changes keep their
            existing coordination contract; this helper owns no new state or lock.
        """
        self.check_cleaned()
        if not isinstance(purge_all, bool):
            raise TypeError("purge_all must be a bool.")
        if spell is not None and not (
            isinstance(spell, str) or inspect.isclass(spell) or inspect.isroutine(spell)
        ):
            # Discovery uses the class; the concrete door retains the original
            # reference separately for Creations when single removal is requested.
            spell = type(spell)
        elif not purge_all:
            raise ValueError(
                "purge_all=False requires an object instance. Pass that instance "
                "as spell, or use purge_all=True with a binding selector."
            )
        return self._resolve_spell(
            spell=spell,
            spell_name=spell_name,
            spellframe=spellframe,
            binding_name=binding_name,
        )

    def has_live_creation(
            self,
            spell_name: str | None = None,
            *,
            spell: str | object | None = None,
            spellframe: str | object | None = None,
            binding_name: str | None = None,
    ) -> bool:
        """
        Report whether a resolved spell already has a live creation.

        Purpose:
            Provide one no-create probe that mirrors the identity-resolution
            behavior of `meld(...)` while stopping before any creation path is
            entered.

        Contract:
            - Uses the same root identity inputs as `meld(...)`.
            - Reuses the same spell-resolution helpers used by the meld path.
            - Inspects current live runtime storage only.
            - Never creates, registers, or mutates runtime objects.
            - Returns `False` when the spell resolves correctly but has no live
              creation in the relevant runtime scope.

        Args:
            spell_name:
                Optional logical spell name for name-based resolution.
            spell:
                Optional spell id string or spell object used for resolution.
            spellframe:
                Optional spellframe / protocol / frame key used for
                resolution.
            binding_name:
                Optional binding name used for lookup-key resolution.

        Returns:
            bool: True when the resolved spell already has a live creation in
            the relevant runtime scope.

        Raises:
            ValueError:
                If none of `spell_name`, `spell`, or `spellframe` are
                provided.
            KeyError:
                If the spell cannot be resolved by the provided inputs.
            RuntimeError:
                If the probe encounters an unsupported or inconsistent runtime
                storage state.
        """
        status = self.describe_live_creation_status(
            spell_name=spell_name,
            spell=spell,
            spellframe=spellframe,
            binding_name=binding_name,
        )
        return bool(status["is_live"])

    @abstractmethod
    def describe_live_creation_status(
            self,
            spell_name: str | None = None,
            *,
            spell: str | object | None = None,
            spellframe: str | object | None = None,
            binding_name: str | None = None,
    ) -> Dict[str, object]:
        """
        Return structured live-creation status for one resolved spell.

        Purpose:
            Provide a richer no-create status payload over the same lookup path
            used by `has_live_creation(...)` and `meld(...)`.

        Contract:
            - Uses the same root identity inputs as `meld(...)`.
            - Reuses the same spell-resolution helpers used by the meld path.
            - Inspects current live runtime storage only.
            - Never creates, registers, or mutates runtime objects.
            - Reports enough caller-context metadata that higher-level tooling
              can tell whether the answer came from conduit-local, spellspace-
              local, existing-creation, or shared owner-created state.

        Args:
            spell_name:
                Optional logical spell name for name-based resolution.
            spell:
                Optional spell id string or spell object used for resolution.
            spellframe:
                Optional spellframe / protocol / frame key used for
                resolution.
            binding_name:
                Optional binding name used for lookup-key resolution.

        Returns:
            Dict[str, object]: Structured live-creation status payload.

        Raises:
            ValueError:
                If none of `spell_name`, `spell`, or `spellframe` are
                provided.
            KeyError:
                If the spell cannot be resolved by the provided inputs.
            RuntimeError:
                If the probe encounters an unsupported or inconsistent runtime
                storage state.
        """
        raise NotImplementedError(
            "Concrete Meld subclasses must implement describe_live_creation_status()."
        )

    @staticmethod
    def _raise_non_resolvable_registration(spell: Spell) -> NoReturn:
        """
        Refuse direct resolution of one explicitly non-resolvable registration.

        Contract:
            - Called only on the failure branch of concrete execution doors.
            - Preserves the selected version's identity without searching for another provider.
            - Performs no validation, hook dispatch, construction or creation-store access.
            - Observational lookup and status probes do not call this helper.

        Args:
            spell: Selected registration whose immutable resolution capability is False.

        Raises:
            MeldExecutionError: Always, with target identity and supported resolution guidance.
        """
        raise MeldExecutionError(
            spell_id=spell.spell_id,
            spell_name=spell.spell_name,
            message=(
                "The selected registration is non-resolvable (resolvable=False) and cannot "
                "be melded or returned by reuse-only resolution. It remains available for "
                "discovery. Supply the application value through the consuming spell's "
                "override, or select a resolvable registration."
            ),
        )

    @staticmethod
    def _rebuild_window(spell: Spell) -> AbstractContextManager[object]:
        """
        Return the rebuild window a producer enters before taking `spell._lock`.

        Contract:
            - Dynamic ownership (`spell._creation_gate` set): a
              CreationContextRebuild over this one spell. It freezes the
              spell-index gate, drains admitted melds, and on exit publishes
              the rebuilt context (when the plan is present) before reopening.
            - Automatic ownership: a no-op context; automatic melds take no
              index ticket and are unchanged.
            - Phase 5 local resolution republishes only to its target
              (2026-09-19), so the target is the whole affected set.

        Args:
            spell: Spell whose phases are about to be rerun.

        Returns:
            AbstractContextManager[object]:
                The window to enter, outermost, before `spell._lock`.
        """
        if spell._creation_gate is None:
            return nullcontext()
        return CreationContextRebuild((spell,))

    def _execute_admitted(
            self,
            spell: Spell,
            creation_gate: CreationGate,
            override_map: Optional[Dict[str, Any]],
            with_created: bool,
    ) -> Any:
        """
        Run one dynamic meld's context read and execution under one index ticket.

        Purpose:
            Dynamic spells share one CreationContext across conduits, and a
            conduit-local rebuild replaces it. Holding the spell-index ticket
            from before the context read until the executor returns means a
            rebuild window either waits for this meld to finish or has finished
            before it reads, so the meld never uses a cleaned context or builds
            from a missing plan (2026-09-26).

        Contract:
            - Admits exactly one ticket and unregisters it exactly once, on
              success or failure. The context's own `execute*` wrappers (which
              admit again) are not used; their executor slots are called here.
            - After admission, a spell that became `resolution_required` while
              this meld was parked releases the ticket, runs the existing
              deferred path, and admits again (input-generation recheck).
            - `with_created` selects the hooks-lane result `(instance, created)`;
              otherwise the instance alone is returned.

        Args:
            spell: Target spell, already validated for this conduit.
            creation_gate: The spell's `_creation_gate`.
            override_map: Normalized overrides, or None.
            with_created: True for the hooks lane.

        Returns:
            Any:
                `(instance, created)` when `with_created`, else the instance.

        Raises:
            RuntimeError:
                When the gate is terminally closed, or when no context can be
                built or published.
            Exception:
                Executor and deferred-resolution failures propagate unchanged.
        """
        creation_gate.admit_ticket()
        while spell.resolution_required:
            creation_gate.unregister_ticket()
            self._ensure_runtime_resolution_ready(spell)
            creation_gate.admit_ticket()
        try:
            # Warm read inlined (one lock-free state read and one slot read,
            # as the doors do); the cold path elects a builder via the spell.
            if spell._creation_context_switch.fast_state >= 2:
                creation_context = spell._creation_context
            else:
                creation_context = spell._get_or_build_creation_context()
            if with_created:
                if override_map is None:
                    return creation_context._no_overrides_executor(self)
                return creation_context._overrides_executor(self, override_map)
            if override_map is None:
                return creation_context._no_overrides_instance_executor(self)
            return creation_context._overrides_executor(self, override_map)[0]
        finally:
            creation_gate.unregister_ticket()

    def _ensure_lineage_resolvable(self, spell: Spell) -> None:
        """
        Ensure the spell is structurally valid enough to continue toward
        resolution.

        This is the main pre-resolution validity gate. It combines three
        responsibilities:

        - rerun structural phases when the lineage is unknown or gated
        - gate the prior conduit-local resolution verdict after a structural
          rerun so changed dependency selection cannot retain an old executor
        - force contract-driven revalidation when `SpellContract` defaults are
          present and need to invalidate conduit-local resolution state
        - hand off to per-conduit resolution gating when structural validity is
          no longer the blocking issue

        Threading:
            Structural reruns are serialized under `spell._lock` so concurrent
            meld calls do not race duplicate validation work. Under dynamic
            ownership the rerun first enters the spell's rebuild window (see
            `_rebuild_window`): the index gate is frozen and drained before the
            spell lock is taken, because Phase 3 resets the shared context.

        Raises:
            SpellbookValidationError: If structural or conduit-local validity
                cannot be promoted into a runnable state.
            MeldExecutionError: If change-control reports the root as dirty for
                the active resolution conduit.
        """
        # Structural gating
        if self._gated_validation_required(spell):
            with self._rebuild_window(spell), spell._lock:
                if self._gated_validation_required(spell):
                    self._get_spell_compiler_system().run_structural_phases(
                        self._spellbook,
                        spell,
                    )
                    # If structural validation produced errors, hard-pin to invalid and bail.
                    if spell.is_broken:
                        state = spell.system_state
                        if state is not None:
                            state.set_validity(SpellValidity.invalid)
                        raise SpellbookValidationError([spell])

                    refreshed_state = spell.system_state
                    if refreshed_state is None or refreshed_state.validity is not SpellValidity.valid:
                        raise SpellbookValidationError([spell])
                    self._force_resolution_revalidation(
                        spell, change_reason=SpellStateChangeReason.structure_changed,
                    )

        self._check_contracts_and_force_revalidation(spell)

        # Resolution gating (per-conduit)
        if not spell.resolution_required:
            self._ensure_resolution_resolvable(spell)

    @abstractmethod
    def _describe_spell_live_creation_status(self, spell: Spell) -> Dict[str, object]:
        """
        Return caller-specific live-creation status for one resolved spell.

        Contract:
            - Concrete subclasses must interpret the resolved spell against the
              caller-owned storage surfaces they front.
            - The returned payload should stay aligned with
              `describe_live_creation_status(...)` so `has_live_creation(...)`
              can trust the `is_live` field without knowing caller scope rules.
        """
        raise NotImplementedError(
            "Concrete Meld subclasses must implement _describe_spell_live_creation_status()."
        )

    def _ensure_runtime_resolution_ready(self, spell: Spell) -> None:
        """
        Ensure deferred runtime resolution is complete before context build.

        Contract:
            - Fast-path no-op when `resolution_required` is False.
            - When required, runs exactly one deferred target-local plan pass
              (`8-11`) under the spell lock.
            - On success: sets `resolution_complete=True` and
              `resolution_required=False`.
            - On failure: preserves `resolution_required=True` and
              `resolution_complete=False`, then re-raises.
            - Hard-fails when deferred resolution is required but no active
              resolution conduit id exists.

        Args:
            spell: Spell about to resolve through meld.

        Raises:
            RuntimeError: If no resolution conduit id is available.
            Exception: Re-raises deferred resolution failures.
        """
        # Rebuild window first (dynamic only), then the spell lock: see
        # `_rebuild_window`. Phase 11 resets the shared context.
        with self._rebuild_window(spell), spell._lock:
            if not spell.resolution_required:
                return
            if spell.resolution_complete:
                spell.resolution_required = False
                return

            conduit_id = self._resolution_conduit_id
            if not conduit_id:
                raise RuntimeError(
                    "Deferred runtime resolution requires a resolution conduit id."
                )

            spellbook = spell._spellbook
            if spellbook is None:
                raise RuntimeError("Spell has no owning Spellbook surface.")
            try:
                spellbook._run_deferred_resolution_phases_for_target_spell(
                    conduit_id,
                    spell,
                )
            except Exception:
                spell.resolution_complete = False
                spell.resolution_required = True
                # Invalidate fast-meld-door entries: resolution regressed.
                spell._door_epoch += 1
                raise

            spell.resolution_complete = True
            spell.resolution_required = False

    def _get_cached_change_control_manager(
            self,
            spellbook: Optional[Spellbook],
    ) -> Optional[ChangeControlManager]:
        """
        Return a cached change-control manager for the spellbook frame.

        Contract:
            - Returns None when spellbook/aether is unavailable.
            - Returns None when manager lookup fails.
            - Caches only non-None managers keyed by frame name.

        Args:
            spellbook:
                Spellbook owning the spell currently being validated.

        Returns:
            Optional[ChangeControlManager]:
                Change-control manager for the frame, or None.
        """
        if spellbook is None:
            return None

        frame_name = spellbook._aetheric_frame_name
        if frame_name is None:
            return None
        cache = self._change_control_manager_by_frame
        cached_manager = cache.get(frame_name)
        if cached_manager is not None:
            return cached_manager

        aether = spellbook._aether
        if aether is None:
            return None

        manager: Optional[ChangeControlManager] = None
        try:
            manager = aether._get_change_control_manager(frame_name)
        except Exception:
            return None

        if manager is not None:
            cache[frame_name] = manager

        return manager

    def _gated_validation_required(self, spell: Spell) -> bool:
        """
        Decide whether structural revalidation must run before meld continues.

        This helper is a decision gate only. It does not run phases itself. It
        interprets the current spell-system state plus change-control state and
        answers one question:

        "Is this lineage eligible to continue as-is, or must meld force a
        structural validation pass first?"

        Decision rules:

        - `valid` -> safe to continue without structural rerun
        - `unknown` / `gated` -> structural rerun required
        - `invalid` / `disabled` / `cleaned` -> hard validation failure
        - dirty root under change-control -> hard runtime block

        Raises:
            SpellbookValidationError: If the lineage is already in a hard-fail
                state.
            MeldExecutionError: If change-control reports the root as dirty for
                the active conduit.
        """
        conduit_id = self._resolution_conduit_id
        if conduit_id:
            spellbook = spell._spellbook
            ccm = self._get_cached_change_control_manager(spellbook)
            if ccm is not None:
                spell_id = spell.spell_index.selected_spell_id
                if spell_id is None:
                    raise RuntimeError("SpellIndex.selected_spell_id is required for meld gating.")
                try:
                    if ccm.is_root_dirty(conduit_id, spell_id):
                        raise MeldExecutionError(
                            spell_id=spell_id,
                            spell_name=spell.spell_name,
                            message=(
                                f"Root '{spell_id}' is dirty under change-control; "
                                "revalidation required."
                            ),
                        )
                except MeldExecutionError:
                    raise
                except Exception:
                    # If change-control is unavailable, proceed with existing validity gate.
                    pass
        state = spell.system_state
        if state is None:
            return True

        validity = state.validity

        if validity is SpellValidity.valid:
            return False

        if validity is SpellValidity.unknown or validity is SpellValidity.gated:
            return True

        # invalid / disabled / cleaned -> hard block, no attempt to resolve
        if (
                validity is SpellValidity.invalid
                or validity is SpellValidity.disabled
                or validity is SpellValidity.cleaned
        ):
            if state is not None and SpellState.transfer_in_progress in state.flags:
                raise SpellbookValidationError([spell])
            raise SpellbookValidationError([spell])

        # Extremely defensive: any future enum value -> treat as not resolvable.
        raise SpellbookValidationError([spell])



    def _ensure_resolution_resolvable(self, spell: Spell) -> None:
        """
        Ensure the spell is resolution-valid for the active conduit.

        Structural validity alone is not enough for meld. A spell can be
        structurally sound but still require conduit-local resolution work
        because phases 5-11 have not yet been completed for this conduit, or
        for its root conduit in lesser-lineage cases.

        This helper reads the active `ConduitResolutionState`, reruns
        conduit-scoped resolution phases when that state is unknown or gated,
        and hard-blocks invalid, disabled, or cleaned states.

        Raises:
            SpellbookValidationError: If conduit-scoped resolution cannot be
                promoted into a valid state.
        """
        spell_system_states = spell._spell_system_states
        conduit_id = self._resolution_conduit_id
        if not conduit_id:
            return
        resolution_state = spell_system_states.get_conduit_resolution_state(conduit_id)
        resolution_validity = self._get_resolution_validity(spell, resolution_state)

        if resolution_validity is SpellValidity.valid:
            return

        if (
            resolution_validity is SpellValidity.invalid
            or resolution_validity is SpellValidity.disabled
            or resolution_validity is SpellValidity.cleaned
        ):
            raise SpellbookValidationError([spell])

        if resolution_validity is SpellValidity.unknown or resolution_validity is SpellValidity.gated:
            # Rebuild window first (dynamic only), then the spell lock: Phase 5
            # clears the plan and resets the shared context that other
            # conduits' admitted melds may be using. See `_rebuild_window`.
            with self._rebuild_window(spell), spell._lock:
                resolution_state = spell_system_states.get_conduit_resolution_state(conduit_id)
                resolution_validity = self._get_resolution_validity(spell, resolution_state)
                if resolution_validity is SpellValidity.valid:
                    return
                if (
                        resolution_validity is SpellValidity.invalid
                        or resolution_validity is SpellValidity.disabled
                        or resolution_validity is SpellValidity.cleaned
                ):
                    raise SpellbookValidationError([spell])

                spellbook = spell._spellbook
                if spellbook is None:
                    raise RuntimeError("Spell has no owning Spellbook surface.")
                spellbook._run_resolution_phases_for_target_spell(conduit_id, spell)

                resolution_state = spell_system_states.get_conduit_resolution_state(conduit_id)
                resolution_validity = self._get_resolution_validity(spell, resolution_state)
                if resolution_validity is SpellValidity.valid:
                    return

            raise SpellbookValidationError([spell])
        raise SpellbookValidationError([spell])

    def _check_contracts_and_force_revalidation(self, spell: Spell) -> None:
        """
        Validate SpellContract sockets and force resolution revalidation.

        Purpose:
            Ensure that any SpellContract defaults declared on the spell can
            be resolved via the current Spellbook's contracted spell maps.
            When contracts are present and resolvable, force the resolution
            validity to gated so phases 5/8/9/10/6/7 re-run on this conduit.

        Contract:
            - If the spell declares no SpellContract defaults, this is a no-op.
            - If any SpellContract cannot be resolved to a contracted provider,
              raise MeldExecutionError with a contract-specific diagnostic.
            - If all contracts resolve, mark resolution validity as gated to
              force revalidation on this conduit.

        Args:
            spell: Spell under resolution.

        Raises:
            MeldExecutionError:
                When a SpellContract has no contracted provider or contracted
                maps are inconsistent.
        """
        contracts = self._iter_spell_contract_defaults(spell)
        if not contracts:
            return

        spell_id = spell.spell_index.selected_spell_id
        if spell_id is None:
            raise RuntimeError("SpellIndex.selected_spell_id is required for SpellContract validation.")
        for param_name, contract in contracts:
            if contract is None:
                continue
            lookup_key = contract.canonical_key
            try:
                provider = self._resolve_contracted_by_lookup_key(lookup_key)
            except Exception as exc:
                raise MeldExecutionError(
                    spell_id=spell_id,
                    spell_name=spell.spell_name,
                    node_id=spell_id,
                    param_name=param_name,
                    message=(
                        "SpellContract could not be resolved. "
                        f"Contract lookup failed for key {lookup_key} "
                        f"on param '{param_name}' for spell '{spell.spell_name}'. "
                        f"Contract={contract!r}."
                    ),
                    inner=exc,
                ) from exc
            if provider is None:
                frame_key, binding_key = lookup_key
                raise MeldExecutionError(
                    spell_id=spell_id,
                    spell_name=spell.spell_name,
                    node_id=spell_id,
                    param_name=param_name,
                    message=(
                        "SpellContract could not be resolved. "
                        "Missing contracted provider for key "
                        f"(frame_key='{frame_key}', binding_key='{binding_key}') "
                        f"on param '{param_name}' for spell '{spell.spell_name}'. "
                        f"Contract={contract!r}."
                    ),
                )

        self._force_resolution_revalidation(spell)

    @staticmethod
    def _iter_spell_contract_defaults(
            spell: Spell,
    ) -> List[Tuple[str, SpellContract]]:
        """
        Return SpellContract defaults discovered in the spell's call signature.

        Contract:
            - Returns an empty list when the signature cannot be inspected.
            - Skips self/cls and var-arg parameters.
            - Only parameters with SpellContract defaults are returned.
            - Preserves unresolved Python 3.14 annotation names as ForwardRefs;
              checking defaults must not evaluate TYPE_CHECKING-only imports.

        Args:
            spell: Spell whose callable signature is inspected.

        Returns:
            List[Tuple[str, SpellContract]]: Parameter names paired with defaults.
        """
        try:
            call_target = spell.spell
        except AttributeError:
            return []

        try:
            signature = inspect.signature(call_target, annotation_format=Format.FORWARDREF)
        except (TypeError, ValueError):
            return []

        contracts: List[Tuple[str, SpellContract]] = []
        for param_name, parameter in signature.parameters.items():
            if param_name in ("self", "cls"):
                continue
            if parameter.kind in (
                    inspect.Parameter.VAR_POSITIONAL,
                    inspect.Parameter.VAR_KEYWORD,
            ):
                continue
            if parameter.default is inspect.Parameter.empty:
                continue
            default_value = parameter.default
            if isinstance(default_value, SpellContract):
                contracts.append((param_name, default_value))

        return contracts

    def _force_resolution_revalidation(
            self,
            spell: Spell,
            *,
            change_reason: SpellStateChangeReason = SpellStateChangeReason.contract_unvalidated,
    ) -> None:
        """
        Force resolution validity to gated so revalidation runs in this conduit.

        Contract:
            - No-op if resolution state is unavailable.
            - Uses root validity when the spell is the root blueprint.
            - Uses spell validity for non-root spells.

        Args:
            spell: Spell to mark for resolution revalidation.
            change_reason: Why the compiled resolution must be rebuilt. Existing
                contract callers retain contract_unvalidated by default.
        """
        spell_system_states = spell._spell_system_states
        conduit_id = self._resolution_conduit_id
        if not conduit_id:
            return

        resolution_state = spell_system_states.get_conduit_resolution_state(conduit_id)
        if resolution_state is None:
            return

        spell_id = spell.spell_index.selected_spell_id
        if spell_id is None:
            raise RuntimeError("SpellIndex.selected_spell_id is required for resolution revalidation.")
        use_root = self._get_spell_compiler_system().is_current_spell_phase5_root(
            spell
        )

        if use_root:
            resolution_state.set_root_validity(
                spell_id,
                SpellValidity.gated,
                change_reason=change_reason,
            )
        else:
            resolution_state.set_spell_validity(
                spell_id,
                SpellValidity.gated,
                change_reason=change_reason,
            )

    def _get_resolution_validity(
            self,
            spell: Spell,
            resolution_state: Optional[ConduitResolutionState],
    ) -> Optional[SpellValidity]:
        """
        Return the effective conduit-local validity for this spell.

        Some spells should be judged against root validity rather than
        spell-local validity when they are the root blueprint for the current
        conduit-local resolution graph. This helper hides that distinction so
        callers can ask for one effective validity answer without duplicating
        root-detection logic.
        """
        if resolution_state is None:
            return SpellValidity.unknown

        spell_id = spell.spell_index.selected_spell_id
        if spell_id is None:
            return SpellValidity.unknown
        if self._get_spell_compiler_system().is_current_spell_phase5_root(spell):
            return resolution_state.get_root_validity(spell_id)

        return resolution_state.get_spell_validity(spell_id)

    def _get_spell_compiler_system(self) -> "SpellCompilerSystem":
        """
        Return the compiler-system helper, creating it on first demand.

        Purpose:
            Keep the heavy compiler/validation foundation off the hot lesser-
            conduit path until one actual validation or root-check path needs
            it. The module import itself is also deferred to this point so
            `import meld` does not pull the compiler package eagerly.

        Contract:
            - Creates exactly one SpellCompilerSystem per Meld instance.
            - Reuses the same helper for subsequent accesses.

        Returns:
            SpellCompilerSystem: Lazily created compiler-system helper.
        """
        compiler_system = self._spell_compiler_system
        if compiler_system is not None:
            return compiler_system
        with self._lock:
            compiler_system = self._spell_compiler_system
            if compiler_system is None:
                from melder.aether.spellbook.spell_compiler.spell_compiler_system import (
                    SpellCompilerSystem,
                )

                compiler_system = SpellCompilerSystem()
                self._spell_compiler_system = compiler_system
        return compiler_system


    @property
    def hooks_modified(self) -> bool:
        """
        Report whether this runtime uses temporary hooks instead of its baseline.

        Contract:
            Includes a Space borrowing its owner's local map, not just callbacks
            registered directly here. This is a diagnostic read under the existing
            Meld lock; pool paths inspect the bool under their lease ownership.

        Returns:
            bool: True when pool return must restore the baseline reference.

        Raises:
            RuntimeError: The runtime has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            self.check_cleaned()
            return self._meld_hooks_modified

    def _bind_meld_hook_baseline(self, hooks: Dict[str, list[Callable[..., Any]]]) -> None:
        """
        Attach a trusted baseline during initialization or quiesced graduation.

        Args:
            hooks: Stable dictionary owned by the current normal root.

        Contract:
            Replaces both references and clears divergence; never edits either
            dictionary. The caller owns quiescence. Callback objects are borrowed.

        Returns:
            None.
        """
        self._baseline_meld_hooks = hooks
        self._meld_hooks = hooks
        self._meld_hooks_modified = False

    def _inherit_meld_hooks(self, source: Meld) -> None:
        """
        Capture an immediate owner's current hooks for a new or acquired Space.

        Args:
            source: Live owner Meld whose baseline and effective map are borrowed.

        Contract:
            A temporary owner map marks this runtime for restoration even though
            it has not registered local callbacks itself. Compare the captured
            references, so an owner switching sources cannot leave a false clean
            flag on a captured local map. Caller exclusively owns this new lease.

        Returns:
            None. No callback containers are copied and no callback is invoked.
        """
        self._baseline_meld_hooks = source._baseline_meld_hooks
        self._meld_hooks = source._meld_hooks
        self._meld_hooks_modified = self._meld_hooks is not self._baseline_meld_hooks

    def _reset_pooled_meld_hooks(self) -> None:
        """
        Restore temporary hook state after current-lease disposal has finished.

        Contract:
            Called only when the pool's bool check reports divergence. Uses the
            existing mutation lock, restores one reference and clears one bool.
            Does not clear borrowed maps or dispose callable objects. Hook edits
            must finish before a caller hands its scope back to the pool.

        Returns:
            None.
        """
        with self._lock:
            self._meld_hooks = self._baseline_meld_hooks
            self._meld_hooks_modified = False

    def register_meld_hooks(
            self,
            hooks: Dict[str, Any],
            *,
            create_local_hooks: bool = True,
            overwrite: bool = False,
    ) -> None:
        """
        Register validated Meld callbacks locally or in a normal root's baseline.

        Args:
            hooks: Meld event names mapped to a callable or list/tuple of callables.
            create_local_hooks: True copies the effective map for this runtime.
                False publishes into a normal root's stable shared baseline and
                selects that baseline for the caller. Lesser/Space shared writes
                are refused; use their normal root for lineage-wide changes.
            overwrite: False appends in order. True replaces the selected Meld
                map; an empty replacement clears its callbacks.

        Contract:
            Validates the whole batch before publication. Local maps stay isolated;
            shared maps retain identity so existing inheritors see changes. Shared
            publication replaces event lists under the existing lock. Readers keep
            current per-event semantics; a multi-event update is not an operation-
            wide snapshot. Callbacks never execute under the mutation lock.

        Returns:
            None. Empty additive input is a no-op.

        Raises:
            RuntimeError: Cleaned runtime or shared update from a lesser/Space.
            ValueError: Unknown Meld event name.
            TypeError: Invalid mapping or non-callable entries.
        """
        self.check_cleaned()
        if not isinstance(hooks, dict):
            raise TypeError("Meld hooks must be a dictionary of event names to callbacks.")
        # Cold mutation path: local import avoids introducing a bootstrap cycle.
        from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration

        additions: Dict[str, list[Callable[..., Any]]] = {}
        for name, value in hooks.items():
            if name not in SpellbookConfiguration._MELD_HOOK_NAMES:
                raise ValueError(f"Unknown Meld hook name: {name!r}")
            if callable(value):
                additions[name] = [value]
            elif isinstance(value, (list, tuple)) and all(callable(item) for item in value):
                additions[name] = list(value)
            else:
                raise TypeError(f"Meld hook '{name}' must be a callable or list/tuple of callables.")
        if not additions and not overwrite:
            return
        if create_local_hooks:
            self.set_meld_hooks(additions, create_local_hooks=True, overwrite=overwrite)
            return
        if self._conduit_id != self._resolution_conduit_id or self._spellspace_creations is not None:
            raise RuntimeError("Shared Meld hooks must be changed through the normal root conduit.")
        with self._lock:
            self.check_cleaned()
            if overwrite:
                self._baseline_meld_hooks.clear()
            for name, callbacks in additions.items():
                if callbacks:
                    self._baseline_meld_hooks[name] = self._baseline_meld_hooks.get(name, []) + callbacks
            self._meld_hooks = self._baseline_meld_hooks
            self._meld_hooks_modified = False

    def set_meld_hooks(
            self,
            hooks: Optional[Dict[str, list[Callable[..., Any]]]],
            *,
            create_local_hooks: bool = False,
            overwrite: bool = False,
    ) -> None:
        """
        Install a hook map used by Meld-level hook firing.

        Expected shape: { hook_name: [callables] }.
        When create_local_hooks is False, the supplied map is stored by
        reference (no copy). When True, a local copy is created so changes
        do not propagate to other conduits.

        Local mode behavior:
            - overwrite=False (default): incoming hooks are merged into the
              current effective hook map.
            - overwrite=True: incoming hooks replace the local map.

        Reference mode remains an internal installation operation, not a shared
        root publication API. Both modes track divergence for pool restoration.
        Uses the existing lock only on this mutation path. To publish a root
        update to existing inheritors, use register_meld_hooks with
        create_local_hooks=False. Local copying snapshots the source mapping
        because a root writer may replace shared event entries concurrently.
        Empty event lists are omitted so clearing keeps the native no-hooks
        fast-door guard available without another dispatch flag.

        Args:
            hooks: Trusted event lists, or None to install no effective hooks.
            create_local_hooks: False borrows this exact reference; True creates
                independent callback containers for this runtime.
            overwrite: In local mode, replace the effective map when True;
                otherwise append to a copy. Ignored for reference installation.

        Returns:
            None.

        Raises:
            RuntimeError: This Meld runtime has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            self.check_cleaned()
            if not create_local_hooks:
                self._meld_hooks = hooks
                self._meld_hooks_modified = hooks is not self._baseline_meld_hooks
                return

            local_hooks: Dict[str, list[Callable[..., Any]]] = {}
            if not overwrite and self._meld_hooks:
                for name, hook_list in self._meld_hooks.copy().items():
                    if not hook_list:
                        continue
                    local_hooks[name] = list(hook_list)
            if hooks:
                for name, hook_list in hooks.items():
                    if not hook_list:
                        continue
                    if overwrite:
                        local_hooks[name] = list(hook_list)
                    else:
                        local_hooks.setdefault(name, []).extend(hook_list)
            self._meld_hooks = local_hooks
            self._meld_hooks_modified = True

    def _fire_meld_hooks(self, hook_name: str, *args: Any) -> None:
        """
        Invoke one meld-level hook list by name.

        This is the dispatcher for conduit-supplied meld hooks such as
        pre-resolve, activation, and post-resolve notifications. Hook failures
        are normalized into `HookExecutionError` so callers see one stable
        hook-failure contract instead of arbitrary raw exceptions.
        """
        meld_hooks = self._meld_hooks
        if meld_hooks is None:
            return
        hook_list = meld_hooks.get(hook_name)
        if not hook_list:
            return
        for hook in hook_list:
            try:
                hook(*args)
            except Exception as e:
                hook_name_str = getattr(hook, "__name__", repr(hook))
                raise HookExecutionError(hook_name, hook_name_str, e) from e


    def _normalize_spell_override(
            self,
            spell_override: Optional[dict | list | tuple]
    ) -> Optional[dict[str, Any]]:
        """
        Normalize the spell_override input into a consistent dictionary format.

        The **override payload** is intended to represent *per-call* constructor
        / factory overrides for a given meld operation. This helper converts the
        user-facing shapes into a uniform internal representation that can be
        consumed by the Meld runtime codegen layer.

        Supported input shapes
        ----------------------

        * None:
            - No overrides are supplied; returns None.

        * dict:
            - Treated as keyword-style overrides:
              {"param_name": value, "other_param": other_value}.
            - Empty dict payloads are normalized to None (no overrides).
            - Non-empty dict payloads are returned AS-IS (no copy): the
              payload is consumed read-only downstream, so the legacy
              defensive shallow copy was removed as a documented hot-path
              decision. Callers must not mutate a payload after passing it.

        * list / tuple:
            - Treated as **positional argument** overrides.
            - These are stored under the special key "__args__" so that the
              runtime can distinguish them from keyword overrides:
              {"__args__": [arg0, arg1, ...]}.

        Any more sophisticated interpretation (e.g. mixing positional and keyword
        semantics, or nested override structures) can be layered on later, but the
        MVP is deliberately simple and explicit.

        Args:
            spell_override:
                The raw override payload supplied by the caller. Must be one of:
                None, dict, list, or tuple.

        Returns:
            Optional[dict[str, Any]]:
                A normalized dictionary representation of the overrides, or
                None if no overrides were supplied.

        Raises:
            TypeError:
                If spell_override is not one of the supported shapes.
        """
        if spell_override is None:
            return None

        if isinstance(spell_override, dict):
            if not spell_override:
                return None
            # Hot path: the payload is consumed read-only downstream (the
            # split helper builds new dicts when it reshapes, targeting only
            # reads, executors consume the socket-keyed map), so the legacy
            # defensive shallow copy was one dict allocation per override
            # meld protecting against a mutation that never happens.
            return spell_override

        if isinstance(spell_override, (list, tuple)):
            return {"__args__": list(spell_override)}

        raise TypeError(
            "[MELD] spell_override must be a dict, list, or tuple."
        )

    # Resolution helpers
    # ----------------------------------------------------------------------
    def _resolve_spell(
            self,
            *,
            spell: Any | None,
            spell_name: str | None,
            spellframe: Any | None,
            binding_name: str | None,
    ) -> Spell:
        """
        Internal

        Resolve an Spell using either:

        1. A direct spell_id string (SHA256 fingerprint), or
        2. A logical identity tuple derived from
           (spellframe | spell, binding_name).

        This is the main entry point used by meld(); it delegates to
        more specific helpers for each resolution strategy.

        Args:
            spell:
                If a string, treated as the canonical spell_id.
                Otherwise treated as a class/function/instance used when
                deriving the logical spell key.
            spell_name:
                Optional explicit spell name to use when deriving the
                logical identity key. When provided without an explicit
                spell or spellframe, this name is treated as the
                logical frame key for resolution.
            spellframe:
                Optional spellframe / Protocol / interface used as part of
                the DI identity. If None, the spell’s own type/name is
                used by the normalization helper.
            binding_name:
                Optional binding name to discriminate multiple spells
                registered under the same spellframe.

        Returns:
            Spell:
                The resolved spell configuration object.

        Raises:
            KeyError:
                If no spell can be resolved for the provided inputs.
            ValueError:
                If resolution key normalization receives no spell identity source.
            RuntimeError:
                If the Spellbook maps are internally inconsistent (e.g.
                a lookup key resolves to a SpellIndex that has no
                corresponding spell object).
        """
        # 1) string spell treated as spell_id (SHA)
        if isinstance(spell, str):
            return self._resolve_spell_by_id(spell)

        # 2) Everything else (frame_key, binding_key) path

        # Decide what we use as "spell" for name-based resolution:
        # - if we have a concrete spell object (class/function), use that
        # - else if we have a spell_name string and no spellframe, resolve by name
        # - else spell remains None and spellframe must be non-None
        spell_for_name = spell
        if spell_for_name is None and spell_name is not None and spellframe is None:
            frame_key, bind_key = SpellInputUtils.make_spell_key_from_parts(
                spellframe=None,
                spell_name=spell_name,
                binding_name=binding_name,
            )
            lookup_key = (frame_key, bind_key)
            return self._resolve_spell_by_lookup_key(lookup_key)
        if spell_for_name is None and spell_name is not None:
            spell_for_name = spell_name

        frame_key, bind_key = SpellInputUtils.normalize_spell_key(
            spell=spell_for_name,
            spellframe=spellframe,
            binding_name=binding_name,
        )

        lookup_key = (frame_key, bind_key)
        resolved = self._resolve_spell_by_lookup_key(lookup_key)
        return resolved

    def _resolve_spell_by_id(self, spell_id: str) -> Spell:
        """
        Resolve a spell by its current canonical spell id.

        This is the direct-id lookup path for callers that already know the
        exact current lineage id and do not need logical frame/binding
        normalization.

        Args:
            spell_id:
                The SHA256 fingerprint associated with the spell.

        Returns:
            Spell:
                The resolved spell configuration object.

        Raises:
            KeyError:
                If no spell with the given spell_id exists in either
                the local or contracted spell maps.
        """
        # Local spells
        pooled_spell = self._spell_id_pool.get(spell_id)
        if pooled_spell is not None:
            return pooled_spell

        # Local spells
        if spell_id in self._spells_by_id:
            return self._spells_by_id[spell_id]

        # Contracted spells (per-conduit maps)
        for spell_map in self._contracted_spells_by_id.values():
            if spell_id in spell_map:
                return spell_map[spell_id]

        raise KeyError(f"[MELD] No spell found with spell_id: {spell_id}")

    def _resolve_spell_by_lookup_key(
            self,
            lookup_key: tuple[str, str],
    ) -> Spell:
        """
        Resolve a spell by normalized logical identity key.

        The lookup order is:

        1. local Spellbook maps
        2. contracted-conduit maps

        This method is the orchestration point for that two-layer search and is
        responsible for turning "not found anywhere" into one stable `KeyError`
        contract.

        Args:
            lookup_key:
                A tuple (frame_key, binding_name) produced by
                SpellInputUtils.normalize_spell_key or
                SpellInputUtils.make_spell_key_from_parts.

        Returns:
            Spell:
                The resolved spell configuration object.

        Raises:
            KeyError:
                If no spell can be resolved for the given key in either
                the local or contracted spell maps.
            RuntimeError:
                If a SpellIndex is found for the key, but the
                associated spell object is missing from the expected map.
        """
        frame_key, bind_key = lookup_key

        # 1) Local lookup
        local_spell = self._resolve_local_by_lookup_key(lookup_key)
        if local_spell is not None:
            return local_spell

        # 2) Contracted lookup
        contracted_spell = self._resolve_contracted_by_lookup_key(lookup_key)
        if contracted_spell is not None:
            return contracted_spell

        # 3) Not found anywhere
        raise KeyError(
            f"[MELD] No spell found for frame='{frame_key}', binding='{bind_key}'."
        )

    def _resolve_local_by_lookup_key(
            self,
            lookup_key: tuple[str, str],
    ) -> Optional[Spell]:
        """
        Attempt local Spellbook resolution for one logical lookup key.

        Args:
            lookup_key:
                The logical identity key (frame_key, binding_name).

        Returns:
            Optional[Spell]:
                The resolved spell object if found locally, otherwise
                None.

        Raises:
            RuntimeError:
                If a SpellIndex is found in the local lookup map but
                the owned spell map does not contain the corresponding
                spell object.
        """
        spell_index = self._lookup_owned_spells.get(lookup_key)
        if spell_index is None:
            return None

        result = self._owned_spells.get(spell_index)
        if result is None:
            raise RuntimeError(
                f"[MELD] Local SpellIndex {spell_index} resolved for key "
                f"{lookup_key}, but no spell object found."
            )

        return result

    def _resolve_contracted_by_lookup_key(
            self,
            lookup_key: tuple[str, str],
    ) -> Optional[Spell]:
        """
        Attempt contracted-conduit resolution for one logical lookup key.

        This is the borrower/provider lookup path. It iterates through the
        per-conduit contracted maps until it finds a matching SpellIndex and
        then resolves that index back to the concrete spell object.

        Args:
            lookup_key:
                The logical identity key (frame_key, binding_name).

        Returns:
            Optional[Spell]:
                The resolved spell object if found among contracted
                spells, otherwise None.

        Raises:
            RuntimeError:
                If a contracted lookup map resolves a SpellIndex but:
                  * the spell map does not contain a spell object for
                     the resolved SpellIndex.
        """
        # If contracted lookup maps exist, we expect contracted spell maps
        # to exist as well. We only enforce this when we actually find a hit.
        for conduit_id, lookup_map in self._lookup_contracted_spells.items():
            spell_index = lookup_map.get(lookup_key)
            if spell_index is None:
                continue

            spell_map = self._contracted_spells.get(conduit_id)
            if spell_map is None:
                continue
            result = spell_map.get(spell_index)
            if result is None:
                raise RuntimeError(
                    f"[MELD] SpellIndex {spell_index} resolved for key "
                    f"{lookup_key} in conduit '{conduit_id}', but no "
                    f"spell object found."
                )

            return result

        return None

    @staticmethod
    def _execute_hooks(
            hooks: Optional[Sequence[Callable[..., Any]]],
            phase: str,
    ) -> None:
        """
        Execute lifecycle hooks (e.g., pre-cast, post-cast) that do **not** take
        an instance context (zero-argument callables).

        Args:
            hooks (List[Callable]): The list of functions to execute.
            phase (str): The name of the lifecycle phase (for error reporting).

        Returns:
            None.

        Raises:
            HookExecutionError: Wraps any exception raised by a hook during execution.
        """
        if not hooks:
            return
        for hook in hooks:
            try:
                hook()
            except Exception as e:
                hook_name = getattr(hook, "__name__", repr(hook))
                raise HookExecutionError(phase, hook_name, e) from e

    @staticmethod
    def _execute_activation_hooks(
            hooks: Optional[Sequence[Callable[..., Any]]],
            instance: Any,
    ) -> None:
        """
        Execute activation hooks, passing the resolved component instance as context.

        Each activation hook is expected to accept at least one positional
        argument: the instance being activated.

        Args:
            hooks (List[Callable]): The list of functions to execute.
            instance (Any): The resolved component instance.

        Returns:
            None.

        Raises:
            HookExecutionError: Wraps any exception raised by a hook during execution.
        """
        if not hooks:
            return
        for hook in hooks:
            try:
                hook(instance)
            except Exception as e:
                hook_name = getattr(hook, "__name__", repr(hook))
                raise HookExecutionError("activation", hook_name, e) from e
