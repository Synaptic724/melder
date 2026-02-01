import inspect
from threading import RLock
from typing import Optional, Dict, Any, Callable, List, Tuple

from melder.aether.conduit.meld.meld_context.meld_context import MeldContext
from melder.aether.conduit.meld.meld_runtime.meld_runtime import MeldRuntime
from melder.utilities.general_base.cleanable import Cleanable
# Melder Imports
from melder.utilities.helpers.general_helpers import SpellInputUtils
from melder.utilities.interfaces.interfaces import (
    ISpellbook,
    ISpell,
    IMeld,
    ILesserCreations,
    ICreations, ISpellIndex,
)
from melder.utilities.custom_exceptions.hook_execution_error import HookExecutionError
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
from melder.spellbook.existence.existence import Existence
from melder.utilities.custom_exceptions.spell_space_scope_error import SpellSpaceScopeError
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
# Creations types
from melder.aether.conduit.creations.creations import Creations
from melder.aether.conduit.creations.lesser_creations import LesserCreations
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.utilities.custom_exceptions.spellbook_validation_error import SpellbookValidationError
from melder.aether.dev_ops.spell_system_states.spell_state import SpellState
from melder.aether.dev_ops.spell_system_states.spell_state_change_reason import (
    SpellStateChangeReason,
)
from melder.aether.conduit.meld.contracts.spell_contract import SpellContract


class Meld(Cleanable, IMeld):
    """
    ## 🪄 Meld: Spell Activation and Dependency Resolution

    Meld is the **conduit-level entry point** for *activating* spells (components/dependencies)
    within a specific `Conduit`. It handles the full lifecycle of spell resolution,
    creation reuse, hook execution, and registration.

    It implements the core dependency injection logic, mediating between the
    `Spellbook` (which defines the components) and the `Creations` manager (which
    holds the instantiated objects/components).

    The primary method is `meld()`.

    ### High-Level Activation Flow

    The `meld()` process follows these steps:

    1.  **Resolve Spell:** Identifies the target `ISpell` object using its ID or a
        `(spellframe, binding_name)` lookup key.
    2.  **Apply Overrides:** Attaches any per-call `spell_override` metadata to the Spell.
    3.  **Execute Pre-Cast Hooks:** Runs hooks that execute *before* instance resolution.
    4.  **Attempt Reuse:** Checks the `Creations` manager for an existing instance
        based on the Spell's `Existence` (e.g., `unique`, `unique_per_conduit`).
    5.  **Instantiate/Register (if needed):**
        * If no instance is found, dispatches to a spell-type specific path (e.g.,
            for `EXISTING_CREATION` spells) to obtain a new instance.
        * Registers the new instance with the `Creations` manager based on its
            `Existence` mode.
    6.  **Execute Activation Hooks:** Runs hooks that operate on the newly resolved/reused
        instance, passing the instance as a context argument.
    7.  **Execute Post-Cast Hooks:** Runs hooks that execute *after* activation.
    8.  **Return Instance:** Returns the final, resolved instance.
    """
    __melder_internal__ = _mrg.sentinel
    def __init__(
            self,
            creations: ILesserCreations | ICreations,
            spellbook: ISpellbook,
            conduit_id: Optional[str] = None,
    ) -> None:
        """
        Initialize the Meld component with references to the component store,
        spellbook lookup maps, spell_id maps, and the DAG-based meld runtime.

        Args:
            creations:
                The local component instance manager (either `Creations` for a
                full Conduit or `LesserCreations` for a LesserConduit).
            spellbook:
                The registry of all known spell configurations. Meld keeps
                direct references to internal spell, lookup, and spell_id
                maps to perform fast, consistent lookups.
            conduit_id:
                Optional identifier for the owning conduit. When supplied,
                this is used as the default resolution scope for per-conduit
                validity checks.
        """
        super().__init__()

        self._lock = RLock()
        self._cleaned: bool = False
        self._conduit_id: Optional[str] = conduit_id
        self._spellbook: ISpellbook = spellbook

        # Spellbook references (used for resolution)
        self._owned_spells: Dict[ISpellIndex, ISpell] = spellbook._spells
        self._contracted_spells: Dict[str, Dict[ISpellIndex, ISpell]] = (
            spellbook._contracted_spells
        )
        self._spells_by_id: Dict[str, ISpell] = spellbook._spells_by_id
        self._contracted_spells_by_id: Dict[str, Dict[str, ISpell]] = spellbook._contracted_spells_by_id
        self._spell_id_pool: Dict[str, ISpell] = spellbook._spell_id_pool

        self._lookup_owned_spells: Dict[tuple, ISpellIndex] = spellbook._lookup_spells
        self._lookup_contracted_spells: Dict[str, Dict[tuple, ISpellIndex]] = (
            spellbook._lookup_contracted_spells
        )


        # Conduit-local instantiation manager (Creations or LesserCreations)
        self._creations = creations

        # DAG-based runtime that will actually execute the DI graph for
        # factory-style spells (class / method / lambda).
        self._runtime: MeldRuntime = MeldRuntime()

        # Optional hook map pulled from Configuration (via Conduit).
        self._meld_hooks: Optional[Dict[str, list[Callable[..., Any]]]] = {}


    def cleanup(self) -> None:
        """
        Cleanup the Meld instance to prevent further use and release references
        to spell configurations, creations manager, and the meld runtime.

        This should be called when the owning `Conduit` is being shut down.

        Contract:
            - Idempotent: repeated calls are safe.
            - Thread-safe: guarded by the internal lock.
            - Runtime reference is dropped (no runtime cleanup is performed).
            - After cleanup, references are cleared and this instance must not be used.

        Behaviour:
            - Marks the instance as cleaned.
            - Clears references to spellbook maps, spell_id maps, and creations.
            - Drops the internal `MeldRuntime` reference.

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
            self._owned_spells = None
            self._contracted_spells = None
            self._spells_by_id = None
            self._contracted_spells_by_id = None
            self._spell_id_pool = None
            self._lookup_owned_spells = None
            self._lookup_contracted_spells = None
            self._spellbook = None

            # Clear creations reference
            self._creations = None
            self._conduit_id = None
            self._runtime = None
            self._meld_hooks = None


    # region Context Manager
    def __enter__(self):
        """
        Acquire the internal lock for thread-safe operations within a context.

        Returns:
            Meld: The instance itself.
        """
        self._lock.acquire()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Release the internal lock upon context manager exit.

        Args:
            exc_type: Exception type if an exception occurred.
            exc_value: Exception value.
            traceback: Exception traceback.

        Returns:
            None.
        """
        self._lock.release()
    # endregion Context Manager
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
        Entry point for resolving and activating a spell (component) within this Conduit.

        This method orchestrates the full lifecycle: resolution, reuse, instantiation,
        hook execution, and registration.

        Args:
            spell_name (str):
                spell_name of the spell to meld

                When provided without an explicit ``spell`` or ``spellframe``, this is
                treated as the **logical name key** used by the resolution pipeline.
                In other words, ``meld(spell_name=\"MyService\")`` becomes equivalent
                to a name-based lookup driven by the Spellbook / SpellIndex mappings.
            spell (str | object | None):
                The primary spell identifier.
                - If a **string**, treated as the unique `spell_id` (typically the
                  SHA256 structural fingerprint for the SpellIndex).
                - If an **object** (e.g., a class or function), used together with
                  `spellframe` and `binding_name` to form the DI identity key via the
                  `SpellInputUtils` normalization helpers.
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

                Semantics:
                - `dict`  → treated as keyword-style overrides (param_name → value).
                - `list` / `tuple` → treated as positional overrides, stored under
                  a special internal key (e.g. `"__args__"`).

                This data is **not** written onto the Spell itself; it is intended
                to be consumed by the runtime / engine layer for this specific
                meld invocation.

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
                ID resolution, unsupported Creations manager, or attempting to
                meld a broken spell).
        """
        # 1) Normalize per-call overrides into a stable dict shape.
        override_map = self._normalize_spell_override(spell_override)

        # 2) Resolve the spell object from the Spellbook / SpellIndex.
        target_spell = self._resolve_spell(
            spell=spell,
            spell_name=spell_name,
            spellframe=spellframe,
            binding_name=binding_name,
        )

        # 3) SpellSystemState / SpellValidity gate + lazy revalidation.
        if self._spellbook._spellbook_validation_required:
            self._ensure_lineage_resolvable(target_spell)

        if self._meld_hooks or target_spell._hooks_enabled:
            return self._comprehensive_meld_with_hooks(
                target_spell=target_spell,
                override_map=override_map,
            )
        else:
            return self._meld_without_hooks(
                target_spell=target_spell,
                override_map=override_map,
            )

    def _meld_without_hooks(
            self,
            target_spell: ISpell,
            override_map: Optional[dict[str, Any]] = None,
    ) -> Optional[Any]:
        """
        Internal
        
        Resolve a spell instance through the minimal meld pipeline (no hook execution).
        
        Notes:
            - Accepts the same identity inputs as meld().
            - Normalizes overrides and resolves the spell instance.
        
        Returns:
            Optional[Any]: The resolved instance.
        
        Raises:
            ValueError: If no identity inputs are provided.
            KeyError: If the spell cannot be resolved.
            RuntimeError: For unexpected internal state issues.
        """
        instance, created = self._resolve_instance_with_locks(
            target_spell,
            override_map,
        )

        # 7) Return the resolved instance.
        return instance

    def _comprehensive_meld_with_hooks(
            self,
            target_spell: ISpell,
            override_map: Optional[dict[str, Any]] = None,
    ) -> Optional[Any]:
        """
        Internal
        
        Resolve a spell instance with full validation and hook execution.
        
        Notes:
            - Accepts the same identity inputs as meld().
            - Runs lineage validation and spell hooks.
        
        Returns:
            Optional[Any]: The resolved instance.
        
        Raises:
            ValueError: If no identity inputs are provided.
            KeyError: If the spell cannot be resolved.
            HookExecutionError: If a hook raises during execution.
            RuntimeError: If the spell is broken or state is invalid.
        """
        # 1) Execute pre-cast hooks (no instance context yet).
        self._execute_hooks(target_spell._pre_hooks, "pre_cast")
        self._fire_meld_hooks("on_meld_pre_resolve", target_spell)

        instance, created = self._resolve_instance_with_locks(
            target_spell,
            override_map,
        )
        if created:
            # Activation hooks fire only when the instance is newly created.
            self._execute_activation_hooks(target_spell._activation_hooks, instance)
            self._fire_meld_hooks("on_meld_activation", target_spell, instance)

        # 2) Execute post-cast hooks (still no arguments for now).
        self._execute_hooks(target_spell._post_hooks, "post_cast")
        self._fire_meld_hooks("on_meld_post_resolve", target_spell)

        # 3) Return the resolved instance.
        return instance

    def _ensure_lineage_resolvable(self, spell: ISpell) -> None:
        """
        Internal

        Enforce structural SpellSystemState gating and per-conduit resolution
        gating for this spell.

        Behaviour:

        - If there is no SpellSystemState:
            -> no-op here; we rely on `spell.is_broken` later in `meld(...)`.

        - If structural validity is UNKNOWN or GATED:
            -> run the per-spell structural phases (1-4) via
               `spell.run_structural_phases()`.
              Then:
                * if `spell.is_broken` -> mark INVALID and raise
                  SpellbookValidationError.
                * else -> if the lineage did not move to VALID, raise
                  SpellbookValidationError.

          After this call, the lineage should no longer be UNKNOWN/GATED. If it
          is, that is treated as a validation failure.

        - If structural validity is INVALID or DISABLED:
            -> raise SpellbookValidationError immediately.
        - If per-conduit resolution validity is UNKNOWN or GATED:
            -> run conduit-scoped phases (5-7) via
               `spell._spellbook._run_resolution_phases_for_conduit(conduit_id)`.
              Then:
                * if resolution validity is INVALID/DISABLED -> raise
                  SpellbookValidationError.
                * else if still UNKNOWN/GATED -> raise SpellbookValidationError.
        Threading:
            - Uses the per-spell lock (`spell._lock`) to serialize revalidation
              when validity is UNKNOWN or GATED, preventing concurrent phase runs.
        """
        state = spell.system_state
        # Structural gating
        if self._gated_validation_required(spell):
            with spell._lock:
                if self._gated_validation_required(spell):
                    spell.run_structural_phases()

                    # If the crafter thinks it's broken, we hard-pin to invalid and bail.
                    if spell.is_broken:
                        state.set_validity(SpellValidity.invalid)
                        raise SpellbookValidationError([spell])

                    refreshed_state = spell.system_state
                    if refreshed_state is None or refreshed_state.validity is not SpellValidity.valid:
                        raise SpellbookValidationError([spell])

        self._check_contracts_and_force_revalidation(spell)

        # Resolution gating (per-conduit)
        self._ensure_resolution_resolvable(spell)

    def _gated_validation_required(self, spell: ISpell) -> bool:
        """
        Internal

        Decide whether this spell's lineage needs a **lazy structural revalidation**
        pass before we attempt to meld it.

        Semantics:

        - If no SpellSystemState is attached -> False
          (DevOps / change-control not wired; Meld falls back to Spell flags).

        - SpellValidity.valid   -> False  (safe to resolve as-is).
        - SpellValidity.unknown -> True   (first-pass revalidation needed).
        - SpellValidity.gated   -> True   (structural / contract / mutation gate).
        - SpellValidity.invalid / disabled -> raise SpellbookValidationError.
        - Dirty root under change-control -> raise MeldExecutionError.

        This method does **not** run validation; it only answers:
        "Should we try to revalidate this lineage now?"
        """
        state = spell.system_state
        # Defensive: block dirty roots under change-control regardless of validity.
        try:
            spellbook = spell._spellbook
            frame_name = spellbook._aetheric_frame
            ccm = spellbook._aether._get_change_control_manager(frame_name)
            if ccm is not None and ccm.is_root_dirty(spell.spell_index.current):
                raise MeldExecutionError(spell_id=spell.spell_index.current, spell_name=spell.spell_name, message=f"Root '{spell.spell_index.current}' is dirty under change-control; revalidation required.")
        except MeldExecutionError:
            raise
        except Exception:
            # If change-control is unavailable, proceed with existing validity gate.
            pass

        validity = state.validity

        if validity is SpellValidity.valid:
            return False

        if validity is SpellValidity.unknown or validity is SpellValidity.gated:
            return True

        # invalid / disabled → hard block, no attempt to resolve
        if validity is SpellValidity.invalid or validity is SpellValidity.disabled:
            if state is not None and SpellState.transfer_in_progress in state.flags:
                raise SpellbookValidationError([spell])
            raise SpellbookValidationError([spell])

        # Extremely defensive: any future enum value → treat as not resolvable.
        raise SpellbookValidationError([spell])



    def _ensure_resolution_resolvable(self, spell: ISpell) -> None:
        """
        Internal

        Enforce per-conduit resolution validity for Phases 5-11.

        This method checks the ConduitResolutionState for the active conduit
        (or root conduit for lesser conduits) and runs conduit-scoped phases
        if resolution validity is UNKNOWN or GATED.
        """
        spell_system_states = spell._spell_system_states
        if spell_system_states is None:
            return

        conduit_id = self._get_resolution_conduit_id()
        if not conduit_id:
            return

        resolution_state = spell_system_states.get_conduit_resolution_state(conduit_id)
        resolution_validity = self._get_resolution_validity(spell, resolution_state)

        if resolution_validity is SpellValidity.valid:
            return

        if resolution_validity is SpellValidity.invalid or resolution_validity is SpellValidity.disabled:
            raise SpellbookValidationError([spell])

        if resolution_validity is SpellValidity.unknown or resolution_validity is SpellValidity.gated:
            with spell._lock:
                resolution_state = spell_system_states.get_conduit_resolution_state(conduit_id)
                resolution_validity = self._get_resolution_validity(spell, resolution_state)
                if resolution_validity is SpellValidity.valid:
                    return
                if resolution_validity is SpellValidity.invalid or resolution_validity is SpellValidity.disabled:
                    raise SpellbookValidationError([spell])

                spellbook = spell._spellbook
                if spellbook is None:
                    raise SpellbookValidationError([spell])
                spellbook._run_resolution_phases_for_conduit(conduit_id)

                resolution_state = spell_system_states.get_conduit_resolution_state(conduit_id)
                resolution_validity = self._get_resolution_validity(spell, resolution_state)
                if resolution_validity is SpellValidity.valid:
                    return

            raise SpellbookValidationError([spell])

        raise SpellbookValidationError([spell])

    def _check_contracts_and_force_revalidation(self, spell: ISpell) -> None:
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

        spell_id = spell.spell_index.current
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
            spell: ISpell,
    ) -> List[Tuple[str, SpellContract]]:
        """
        Return SpellContract defaults discovered in the spell's call signature.

        Contract:
            - Returns an empty list when the signature cannot be inspected.
            - Skips self/cls and var-arg parameters.
            - Only parameters with SpellContract defaults are returned.

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
            signature = inspect.signature(call_target)
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

    def _force_resolution_revalidation(self, spell: ISpell) -> None:
        """
        Force resolution validity to gated so revalidation runs in this conduit.

        Contract:
            - No-op if resolution state is unavailable.
            - Uses root validity when the spell is the root blueprint.
            - Uses spell validity for non-root spells.

        Args:
            spell: Spell to mark for resolution revalidation.
        """
        spell_system_states = spell._spell_system_states
        conduit_id = self._get_resolution_conduit_id()
        if not conduit_id:
            return

        resolution_state = spell_system_states.get_conduit_resolution_state(conduit_id)
        if resolution_state is None:
            return

        spell_id = spell.spell_index.current
        use_root = False
        crafter = spell._crafter
        if crafter is not None:
            blueprint = crafter.root_blueprint_phase5
            if blueprint is not None and blueprint.root_spell_id == spell_id:
                use_root = True

        if use_root:
            resolution_state.set_root_validity(
                spell_id,
                SpellValidity.gated,
                change_reason=SpellStateChangeReason.contract_unvalidated,
            )
        else:
            resolution_state.set_spell_validity(
                spell_id,
                SpellValidity.gated,
                change_reason=SpellStateChangeReason.contract_unvalidated,
            )

    def _get_resolution_conduit_id(self) -> Optional[str]:
        """
        Resolve the conduit id used for per-conduit resolution validity.

        For normal conduits, this is the conduit's own id. For lesser conduits,
        this uses the root conduit id when available.
        """
        if self._creations is None:
            return self._conduit_id

        conduit = self._creations._conduit
        if conduit is None:
            return self._conduit_id

        if conduit._conduit_state is ConduitState.lesser:
            ward = conduit._conduit_ward
            if ward is not None:
                root = ward.root_conduit
                if root is not None:
                    return root._id

        return conduit._id

    def _get_resolution_validity(
            self,
            spell: ISpell,
            resolution_state: Optional[Any],
    ) -> Optional[SpellValidity]:
        """
        Resolve per-conduit validity for a spell, using root validity when applicable.
        """
        if resolution_state is None:
            return SpellValidity.unknown

        spell_id = spell.spell_index.current
        crafter = spell._crafter
        if crafter is not None:
            blueprint = crafter.root_blueprint_phase5
            if blueprint is not None and blueprint.root_spell_id == spell_id:
                return resolution_state.get_root_validity(spell_id)

        return resolution_state.get_spell_validity(spell_id)


    def set_meld_hooks(
            self,
            hooks: Dict[str, list[Callable[..., Any]]] | None,
            *,
            create_local_hooks: bool = False,
    ) -> None:
        """
        Install a hook map used by Meld-level hook firing.

        Expected shape: { hook_name: [callables] }.
        When create_local_hooks is False, the supplied map is stored by
        reference (no copy). When True, a local copy is created so changes
        do not propagate to other conduits.
        """
        if not create_local_hooks:
            self._meld_hooks = hooks
            return

        local_hooks: Dict[str, list[Callable[..., Any]]] = {}
        if hooks:
            for name, hook_list in hooks.items():
                if hook_list is None:
                    continue
                local_hooks[name] = list(hook_list)
        self._meld_hooks = local_hooks

    def _fire_meld_hooks(self, hook_name: str, *args: Any) -> None:
        """
        Invoke meld-level hooks by name. Exceptions are wrapped in HookExecutionError.
        """
        hook_list = self._meld_hooks.get(hook_name)
        if not hook_list:
            return
        for hook in list(hook_list):
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
        Normalize the ``spell_override`` input into a consistent dictionary format.

        The **override payload** is intended to represent *per-call* constructor
        / factory overrides for a given meld operation. This helper converts the
        user-facing shapes into a uniform internal representation that can be
        consumed by the Meld runtime / engine layer.

        Supported input shapes
        ----------------------

        * ``None``:
            - No overrides are supplied; returns ``None``.

        * ``dict``:
            - Treated as keyword-style overrides:
              ``{"param_name": value, "other_param": other_value}``.
            - A shallow copy is created to avoid accidental mutation of the
              caller's dictionary.

        * ``list`` / ``tuple``:
            - Treated as **positional argument** overrides.
            - These are stored under the special key ``"__args__"`` so that the
              engine can distinguish them from keyword overrides:
              ``{"__args__": [arg0, arg1, ...]}``.

        Any more sophisticated interpretation (e.g. mixing positional and keyword
        semantics, or nested override structures) can be layered on later, but the
        MVP is deliberately simple and explicit.

        Args:
            spell_override:
                The raw override payload supplied by the caller. Must be one of:
                ``None``, ``dict``, ``list``, or ``tuple``.

        Returns:
            Optional[dict[str, Any]]:
                A normalized dictionary representation of the overrides, or
                ``None`` if no overrides were supplied.

        Raises:
            TypeError:
                If ``spell_override`` is not one of the supported shapes.
        """
        if spell_override is None:
            return None

        if isinstance(spell_override, dict):
            # Shallow copy to avoid side-effects if the caller mutates
            # their dictionary after passing it into meld(...).
            return dict(spell_override)

        if isinstance(spell_override, (list, tuple)):
            # MVP positional override support: caller is explicitly saying
            # "treat these as *args for the constructor/factory".
            return {"__args__": list(spell_override)}

        raise TypeError(
            "[MELD] spell_override must be a dict, list, or tuple."
        )



    # ----------------------------------------------------------------------
    # Resolution helpers
    # ----------------------------------------------------------------------

    def _create_meld_context(
            self,
            spell: ISpell,
            overrides: Optional[dict[str, Any]],
            caller_creations_lock_held: bool = False,
    ) -> MeldContext:
        """
        Internal

        Create a per-call :class:`MeldContext` for a single meld operation.

        The context binds together:
            - The root spell to be constructed.
            - The caller Conduit's creations manager.
            - The owner Conduit's creations manager (from the spell).
            - Any normalized per-call overrides (constructor/factory args).

        This object is passed into the `MeldRuntime` / `MeldEngine` stack and
        is cleaned up immediately after the engine finishes.

        Args:
            spell:
                The root `ISpell` being melded.
            overrides:
                Normalized per-call overrides produced by
                :meth:`_normalize_spell_override`, or ``None`` if no overrides
                were supplied.
            caller_creations_lock_held:
                True if the caller creations lock is already held by the
                invoking thread during runtime execution.

        Returns:
            MeldContext:
                A freshly constructed context for this meld invocation.
        """
        # Positional construction keeps us insulated from minor signature changes
        # in MeldContext as long as (root_spell, creations, overrides) stay first.
        return MeldContext(
            root_spell=spell,
            overrides=overrides,
            caller_creations=self._creations,
            caller_creations_lock_held=caller_creations_lock_held,
        )


    def _resolve_spell(
            self,
            *,
            spell: Any | None,
            spell_name: str | None,
            spellframe: Any | None,
            binding_name: str | None,
    ) -> ISpell:
        """
        Internal

        Resolve an ``ISpell`` using either:

        1. A direct ``spell_id`` string (SHA256 fingerprint), or
        2. A logical identity tuple derived from
           ``(spellframe | spell, binding_name)``.

        This is the main entry point used by ``meld()``; it delegates to
        more specific helpers for each resolution strategy.

        Args:
            spell:
                If a string, treated as the canonical ``spell_id``.
                Otherwise treated as a class/function/instance used when
                deriving the logical spell key.
            spell_name:
                Optional explicit spell name to use when deriving the
                logical identity key. When provided without an explicit
                ``spell`` or ``spellframe``, this name is treated as the
                logical frame key for resolution.
            spellframe:
                Optional spellframe / Protocol / interface used as part of
                the DI identity. If ``None``, the spell’s own type/name is
                used by the normalization helper.
            binding_name:
                Optional binding name to discriminate multiple spells
                registered under the same spellframe.

        Returns:
            ISpell:
                The resolved spell configuration object.

        Raises:
            KeyError:
                If no spell can be resolved for the provided inputs.
            RuntimeError:
                If the Spellbook maps are internally inconsistent (e.g.
                a lookup key resolves to a SpellIndex that has no
                corresponding spell object).
        """
        # 1) string spell → treated as spell_id (SHA)
        if isinstance(spell, str):
            return self._resolve_spell_by_id(spell)

        # 2) Everything else → (frame_key, binding_key) path

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
        return self._resolve_spell_by_lookup_key(lookup_key)

    def _resolve_spell_by_id(self, spell_id: str) -> ISpell:
        """
        Internal

        Resolve an ``ISpell`` by its canonical current ``spell_id`` (SHA256).

        This uses the Spellbook spell_id_pool first (owned + contracted),
        then falls back to the owned map and per-conduit contracted maps.
        It is intended for cases where the caller has an exact fingerprint
        and does not care about logical identity keys.

        Args:
            spell_id:
                The SHA256 fingerprint associated with the spell.

        Returns:
            ISpell:
                The resolved spell configuration object.

        Raises:
            KeyError:
                If no spell with the given ``spell_id`` exists in either
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
    ) -> ISpell:
        """
        Internal

        Resolve an ``ISpell`` by its logical identity key:

            (frame_key, binding_name)

        The lookup proceeds in two phases:

        1. Check the local Spellbook lookup map.
        2. Check each contracted-conduit lookup map.

        This method orchestrates both lookups and is responsible for
        raising a ``KeyError`` when no spell can be found.

        Args:
            lookup_key:
                A tuple ``(frame_key, binding_name)`` produced by
                ``SpellInputUtils.normalize_spell_key`` or
                ``SpellInputUtils.make_spell_key_from_parts``.

        Returns:
            ISpell:
                The resolved spell configuration object.

        Raises:
            KeyError:
                If no spell can be resolved for the given key in either
                the local or contracted spell maps.
            RuntimeError:
                If a ``SpellIndex`` is found for the key, but the
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
    ) -> Optional[ISpell]:
        """
        Internal

        Attempt to resolve an ``ISpell`` from the **local** Spellbook maps
        using a logical identity key.

        Args:
            lookup_key:
                The logical identity key ``(frame_key, binding_name)``.

        Returns:
            Optional[ISpell]:
                The resolved spell object if found locally, otherwise
                ``None``.

        Raises:
            RuntimeError:
                If a ``SpellIndex`` is found in the local lookup map but
                the owned spell map is unavailable or does not contain
                the corresponding spell object.
        """
        spell_index = self._lookup_owned_spells.get(lookup_key)
        if spell_index is None:
            return None

        if self._owned_spells is None:
            raise RuntimeError(
                "[MELD] Local lookup map resolved a SpellIndex, but the "
                "owned spell map is not available."
            )

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
    ) -> Optional[ISpell]:
        """
        Internal

        Attempt to resolve an ``ISpell`` from **contracted** Spellbook maps
        using a logical identity key.

        This iterates over all peer conduits known to this Meld instance
        and consults their per-conduit lookup maps.

        Args:
            lookup_key:
                The logical identity key ``(frame_key, binding_name)``.

        Returns:
            Optional[ISpell]:
                The resolved spell object if found among contracted
                spells, otherwise ``None``.

        Raises:
            RuntimeError:
                If a contracted lookup map resolves a ``SpellIndex`` but:
                  * the global contracted spell map is unavailable, or
                  * there is no spell map for that conduit ID, or
                  * the spell map does not contain a spell object for
                    the resolved ``SpellIndex``.
        """
        # If contracted lookup maps exist, we expect contracted spell maps
        # to exist as well. We only enforce this when we actually find a hit.
        for conduit_id, lookup_map in self._lookup_contracted_spells.items():
            spell_index = lookup_map.get(lookup_key)
            if spell_index is None:
                continue

            spell_map = self._contracted_spells.get(conduit_id)
            if spell_map is None:
                raise RuntimeError(
                    f"[MELD] Contracted lookup map exists for conduit "
                    f"'{conduit_id}' but no contracted spell map is present."
                )

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
    def _execute_hooks(hooks: List[Callable], phase: str) -> None:
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
        for hook in hooks:
            try:
                hook()
            except Exception as e:
                hook_name = getattr(hook, "__name__", repr(hook))
                raise HookExecutionError(phase, hook_name, e) from e

    @staticmethod
    def _execute_activation_hooks(hooks: List[Callable], instance: Any) -> None:
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
        for hook in hooks:
            try:
                hook(instance)
            except Exception as e:
                hook_name = getattr(hook, "__name__", repr(hook))
                raise HookExecutionError("activation", hook_name, e) from e

    # ----------------------------------------------------------------------
    # Existing creation reuse
    # ----------------------------------------------------------------------
    def _select_creations_for_spell(self, spell: ISpell) -> Any:
        """
        Internal

        Select the appropriate creations container for reuse/registration.

        Contract:
            - Per-conduit lifetimes use the caller creations container.
            - Shared lifetimes use the owner creations container.
            - If the preferred container is None, fall back to the other.

        Args:
            spell: The spell whose Existence determines selection.

        Returns:
            The selected creations container, or None if neither is available.
        """
        existence: Existence = spell.existence
        owner_creations = spell._owner_creations

        if existence in (
                Existence.unique_per_conduit,
                Existence.many,
                Existence.unique_per_spell_space,
        ):
            if self._creations is not None:
                return self._creations
            return owner_creations

        if owner_creations is not None:
            return owner_creations
        return self._creations

    def _raise_override_on_existing_instance(
            self,
            *,
            spell: ISpell,
            overrides: Optional[dict[str, Any]],
    ) -> None:
        """
        Internal

        Reject per-call overrides when a shared instance already exists.

        Contract:
            - If no overrides are supplied, this is a no-op.
            - If overrides are present, reuse is blocked and a MeldExecutionError is raised.
            - The error message must clearly signal that the instance already exists.

        Args:
            spell:
                The spell whose cached instance would be reused.
            overrides:
                Normalized per-call overrides from :meth:`_normalize_spell_override`.

        Returns:
            None.

        Raises:
            MeldExecutionError:
                If overrides are supplied for an already-instantiated shared spell.
        """
        if not overrides:
            return

        raise MeldExecutionError(
            spell_id=spell.spell_index.current,
            spell_name=spell.spell_name,
            message=(
                "Overrides were supplied for a spell instance that already exists. "
                "Shared instances cannot be overridden after creation."
            ),
        )

    def _resolve_instance_with_locks(
            self,
            spell: ISpell,
            overrides: Optional[dict[str, Any]],
    ) -> tuple[Any, bool]:
        """
        Internal

        Resolve a spell instance while enforcing per-existence locking rules.

        Contract:
            - Per-conduit existences hold the caller creations lock across
              check -> construct -> register.
            - Shared existences hold the spell lock across the same flow and
              use the creations lock only for map access.
            - Existence.many always constructs and registers without reuse.
            - Overrides targeting existing instances raise MeldExecutionError.

        Args:
            spell:
                The resolved spell configuration object.
            overrides:
                Normalized per-call overrides, or None.

        Returns:
            tuple[Any, bool]:
                (instance, created) where created is True only when this call
                constructs and registers a new instance.
        Raises:
            MeldExecutionError:
                If overrides are supplied for a spell instance that already
                exists under a shared Existence mode.
        """
        creations = self._select_creations_for_spell(spell)
        existence: Existence = spell.existence
        is_existing_creation = spell.is_existing_creation
        has_disposal_methods = spell.has_disposal_methods
        spellspace = None
        if creations is None and existence in (
                Existence.unique_per_conduit,
                Existence.unique_per_spell_space,
                Existence.many,
        ):
            raise RuntimeError(
                "[MELD] Caller creations are required for per-conduit existences."
            )
        instance: Any = None
        created = False

        if existence is Existence.many:
            instance = self._meld_by_spell_type(
                spell,
                overrides,
                caller_creations_lock_held=False,
            )
            if not has_disposal_methods:
                return instance, True
            if is_existing_creation and creations is not None:
                with creations._lock:
                    self._register_spell(
                        spell,
                        instance,
                        creations,
                        spellspace=spellspace,
                    )
            return instance, True

        if existence is Existence.unique_per_spell_space and creations is not None:
            spellspace = self._get_active_spellspace_for_creations(creations)

        if existence in (
                Existence.unique_per_conduit,
                Existence.unique_per_spell_space,
        ):
            with creations._lock:
                instance = self._get_existing_creation_from_creations(
                    spell=spell,
                    creations=creations,
                    spellspace=spellspace,
                )
                if instance is None:
                    instance = self._meld_by_spell_type(
                        spell,
                        overrides,
                        caller_creations_lock_held=True,
                    )
                    if is_existing_creation:
                        self._register_spell(
                            spell,
                            instance,
                            creations,
                            spellspace=spellspace,
                        )
                    created = True
                else:
                    self._raise_override_on_existing_instance(
                        spell=spell,
                        overrides=overrides,
                    )
            return instance, created

        with spell._lock:
            if creations is not None:
                with creations._lock:
                    instance = self._get_existing_creation(
                        spell,
                        creations,
                    )
            else:
                instance = self._get_existing_creation(spell, None)

            if instance is None:
                instance = self._meld_by_spell_type(
                    spell,
                    overrides,
                    caller_creations_lock_held=False,
                )
                if is_existing_creation and creations is not None:
                    with creations._lock:
                        self._register_spell(
                            spell,
                            instance,
                            creations,
                            spellspace=spellspace,
                        )
                created = True
            else:
                self._raise_override_on_existing_instance(
                    spell=spell,
                    overrides=overrides,
                )

        return instance, created

    def _get_existing_creation(
            self,
            spell: ISpell,
            creations: Any | None = None,
    ) -> Optional[Any]:
        """
        Attempts to retrieve a cached instance from the `Creations` manager
        based on the spell's `Existence` lifecycle mode.

        Args:
            spell (ISpell): The resolved Spell configuration object.
            creations (Any | None): Optional creations container override.
                If None, the selection follows `_select_creations_for_spell`.

        Returns:
            Optional[Any]: The existing component instance if found and reuse is
                           permitted by the Existence mode, otherwise **None**.
        """
        existence: Existence = spell.existence
        # Existence.many means always fresh, never reuse
        if existence is Existence.many:
            return None

        if creations is None:
            creations = self._select_creations_for_spell(spell)

        if creations is None:
            return None

        spellspace = None
        if existence is Existence.unique_per_spell_space:
            spellspace = self._get_active_spellspace_for_creations(creations)

        return self._get_existing_creation_from_creations(
            spell=spell,
            creations=creations,
            spellspace=spellspace,
        )

    def _get_existing_creation_from_creations(
            self,
            *,
            spell: ISpell,
            creations: Any,
            spellspace: Optional[Any],
    ) -> Optional[Any]:
        """
        Internal

        Resolve a cached instance from a known creations container.

        Contract:
            - `creations` must already be selected for this spell.
            - `spellspace` is prevalidated when existence is unique_per_spell_space.
            - Returns None when no reuse is possible or no instance exists.
        """
        existence: Existence = spell.existence
        spell_id: str = spell.spell_id

        if isinstance(creations, Creations):
            creation_map = None
            if existence is Existence.unique:
                creation_map = creations._unique
            elif existence is Existence.unique_per_conduit:
                creation_map = creations._unique_per_scope
            elif existence is Existence.unique_per_conduit_cluster:
                creation_map = creations._unique_per_cluster
            elif existence is Existence.unique_per_conduit_lineage:
                creation_map = creations._unique_per_lineage
            if creation_map is not None:
                creation = creation_map.get(spell_id)
                return creation.value if creation is not None else None
            if existence is Existence.unique_per_spell_space and spellspace is not None:
                creation = creations.get_spellspace_creation(spellspace.id, spell_id)
                return creation.value if creation is not None else None
            return None

        if isinstance(creations, LesserCreations):
            if existence is Existence.unique_per_conduit:
                creation = creations._unique_per_scope.get(spell_id)
                return creation.value if creation is not None else None
            # Delegate frame-level singletons to root creations when available.
            parent_creations = creations._parent_creations
            if isinstance(parent_creations, Creations):
                creation_map = None
                if existence is Existence.unique:
                    creation_map = parent_creations._unique
                elif existence is Existence.unique_per_conduit_cluster:
                    creation_map = parent_creations._unique_per_cluster
                elif existence is Existence.unique_per_conduit_lineage:
                    creation_map = parent_creations._unique_per_lineage
                if creation_map is not None:
                    found = creation_map.get(spell_id)
                    return found.value if found is not None else None
                if existence is Existence.unique_per_spell_space and spellspace is not None:
                    found = creations.get_spellspace_creation(spellspace.id, spell_id)
                    return found.value if found is not None else None
            # Existence.many is handled by the caller; other modes are delegated.
            return None

        return None

    def _get_active_spellspace_for_creations(
            self,
            creations: Any,
    ) -> Any:
        """
        Resolve and validate the active SpellSpace for a creations container.

        Contract:
            - Raises SpellSpaceScopeError when no active spellspace is present.
            - Raises SpellSpaceScopeError when the active spellspace belongs to
              a different conduit.
        """
        spellspace = creations._conduit.get_active_spellspace()
        if spellspace is None:
            raise SpellSpaceScopeError(
                "Existence.unique_per_spell_space requires an active SpellSpace. "
                "Use 'with conduit.enter_spellspace()' when melding."
            )
        if spellspace.owner_conduit is not creations._conduit:
            raise SpellSpaceScopeError(
                "Active SpellSpace belongs to a different conduit."
            )
        return spellspace

    def _get_active_spellspace_for_creations(
            self,
            creations: Any,
    ) -> Any:
        """
        Resolve and validate the active SpellSpace for a creations container.

        Contract:
            - Raises SpellSpaceScopeError when no active spellspace is present.
            - Raises SpellSpaceScopeError when the active spellspace belongs to
              a different conduit.
        """
        spellspace = creations._conduit.get_active_spellspace()
        if spellspace is None:
            raise SpellSpaceScopeError(
                "Existence.unique_per_spell_space requires an active SpellSpace. "
                "Use 'with conduit.enter_spellspace()' when melding."
            )
        if spellspace.owner_conduit is not creations._conduit:
            raise SpellSpaceScopeError(
                "Active SpellSpace belongs to a different conduit."
            )
        return spellspace

    # ----------------------------------------------------------------------
    # Spell-type–aware dispatch and registration
    # ----------------------------------------------------------------------
    def _meld_by_spell_type(
            self,
            spell: ISpell,
            overrides: Optional[dict[str, Any]],
            *,
            caller_creations_lock_held: bool = False,
    ) -> Any:
        """
        Obtain a new component instance based on the Spell's canonical `SpellType`.

        Behaviour:

            * EXISTING_CREATION*:
                  Returns the pre-created object stored on the spell and relies
                  on `_register_spell` to cache it into the creations manager.

            * Class / method / lambda spells:
                  Delegate to the DAG-based `MeldRuntime` / `MeldEngine` stack
                  using a per-call `MeldContext` seeded with `overrides`.

            * Anything else:
                  Raises a `RuntimeError` indicating an unsupported SpellType.

        Args:
            spell:
                The resolved Spell configuration object.
            overrides:
                Normalized per-call overrides (or ``None``), as produced by
                :meth:`_normalize_spell_override`.
            caller_creations_lock_held:
                True if the caller creations lock is already held by the
                invoking thread during runtime execution.

        Returns:
            Any:
                The newly resolved component instance.

        Raises:
            RuntimeError:
                - If the spell is an existing-creation spell with no backing
                  `user_created_object`.
                - If the meld runtime is not configured.
                - If the SpellType is unsupported.
            MeldExecutionError:
                Propagated from `MeldRuntime.execute` if DI or construction fails.
        """
        # 1) Existing Creation: the instance already exists on the spell and
        #    must never be constructed via the runtime.
        if spell.is_existing_creation:
            instance = spell.user_created_object
            if instance is None:
                raise RuntimeError(
                    "[MELD] EXISTING_CREATION spell has no `user_created_object` "
                    f"(spell_id={spell.spell_id})."
                )
            return instance

        if spell.is_class_spell or spell.is_method_spell or spell.is_lambda_spell:
            context = self._create_meld_context(
                spell,
                overrides,
                caller_creations_lock_held=caller_creations_lock_held,
            )
            try:
                return self._runtime.execute(context)
            finally:
                # Make sure we always tear down the context, even if the runtime
                # raises a MeldExecutionError or another exception.
                try:
                    context.cleanup()
                except Exception:
                    pass

        # 2) Anything else is currently unsupported.
        raise RuntimeError(f"[MELD] Unsupported SpellType encountered: {spell.spell_type}")


# ----------------------------------------------------------------------
# Registration Helpers (New Structure)
# ----------------------------------------------------------------------
    def _register_spell(
            self,
            spell: ISpell,
            instance: Any,
            creations: Any | None = None,
            *,
            spellspace: Optional[Any] = None,
    ) -> None:
        """
        Registers a newly obtained component instance with the Creations system,
        adhering to the spell's `Existence` mode.

        This method acts as a dispatcher, calling the correct helper based on the
        type of the Conduit's creations manager (`Creations` vs `LesserCreations`).

        Args:
            spell (ISpell): The resolved Spell configuration object.
            instance (Any): The newly created component instance.
            creations (Any | None): Optional creations container override.
                If None, the selection follows `_select_creations_for_spell`.
            spellspace (Optional[Any]): Prevalidated SpellSpace for
                Existence.unique_per_spell_space when available.

        Returns:
            None.

        Raises:
            RuntimeError: Propagated from helpers, or raised if the creations manager
                type itself is unsupported.
        """
        if creations is None:
            creations = self._select_creations_for_spell(spell)

        # --- Dispatch based on Creations Manager Type ---

        # Normal conduit: full Creations manager
        if isinstance(creations, Creations):
            self._register_to_creations(
                spell=spell,
                instance=instance,
                creations=creations,
                spellspace=spellspace,
            )
            return

        # LesserConduit: LesserCreations manager
        if isinstance(creations, LesserCreations):
            self._register_to_lesser_creations(
                spell=spell,
                instance=instance,
                creations=creations,
                spellspace=spellspace,
            )
            return

        # Unknown creations manager type
        raise RuntimeError(
            f"[MELD] Unsupported creations manager type: {type(creations).__name__}"
        )

    def _register_to_creations(
            self,
            spell: ISpell,
            instance: Any,
            creations: ICreations,
            *,
            spellspace: Optional[Any],
    ) -> None:
        """
        Handles registration for the full Creations manager (used by a normal Conduit).

        It registers the new instance based on all supported Existence modes,
        including unique, unique_per_conduit, many, cluster, and lineage.

        Args:
            spell (ISpell): The resolved Spell configuration object.
            instance (Any): The newly created component instance.
            creations (ICreations): Target creations container for registration.
            spellspace (Optional[Any]): Prevalidated SpellSpace for
                Existence.unique_per_spell_space when available.

        Returns:
            None.

        Raises:
            RuntimeError: If an unsupported Existence mode is encountered for
                the Creations manager.
        """
        existence: Existence = spell.existence
        spell_id: str = spell.spell_id
        has_disposal_methods: bool = spell.has_disposal_methods
        disposal_methods: list[str] = spell.disposal_method_names

        if existence is Existence.unique:
            creations.add_unique(
                spell_id,
                instance,
                has_disposal_methods=has_disposal_methods,
                disposal_methods=disposal_methods,
            )
            return

        if existence is Existence.unique_per_conduit:
            creations.add_unique_per_scope(
                spell_id,
                instance,
                has_disposal_methods=has_disposal_methods,
                disposal_methods=disposal_methods,
            )
            return

        if existence is Existence.many:
            if not has_disposal_methods:
                return
            creations.add_many(
                spell_id,
                instance,
                has_disposal_methods=has_disposal_methods,
                disposal_methods=disposal_methods,
            )
            return

        if existence is Existence.unique_per_conduit_cluster:
            creations.add_unique_per_cluster(
                spell_id,
                instance,
                has_disposal_methods=has_disposal_methods,
                disposal_methods=disposal_methods,
            )
            return

        if existence is Existence.unique_per_conduit_lineage:
            creations.add_unique_per_lineage(
                spell_id,
                instance,
                has_disposal_methods=has_disposal_methods,
                disposal_methods=disposal_methods,
            )
            return

        if existence is Existence.unique_per_spell_space:
            if spellspace is None:
                spellspace = self._get_active_spellspace_for_creations(creations)
            creations.register_spellspace_creation(
                spellspace.id,
                spell_id,
                instance,
                has_disposal_methods=has_disposal_methods,
                disposal_methods=disposal_methods,
            )
            return

        # Fallback for any unsupported mode in Creations
        raise RuntimeError(
            f"[MELD] Unsupported Existence '{existence}' for spell_id={spell_id} "
            f"in Creations."
        )


    def _register_to_lesser_creations(
            self,
            spell: ISpell,
            instance: Any,
            creations: ILesserCreations,
            *,
            spellspace: Optional[Any],
    ) -> None:
        """
        Handles registration for the LesserCreations manager (used by a LesserConduit).

        This manager only supports a limited set of existence modes:
        `unique_per_conduit` and `many`.

        Args:
            spell (ISpell): The resolved Spell configuration object.
            instance (Any): The newly created component instance.
            creations (ILesserCreations): Target creations container for registration.
            spellspace (Optional[Any]): Prevalidated SpellSpace for
                Existence.unique_per_spell_space when available.

        Returns:
            None.

        Raises:
            RuntimeError: If an Existence mode other than `unique_per_conduit` or
                          `many` is attempted in a LesserConduit context.
        """
        existence: Existence = spell.existence
        spell_id: str = spell.spell_id
        has_disposal_methods: bool = spell.has_disposal_methods
        disposal_methods: list[str] = spell.disposal_method_names

        if existence is Existence.unique_per_conduit:
            creations.add_unique_per_scope(
                spell_id,
                instance,
                has_disposal_methods=has_disposal_methods,
                disposal_methods=disposal_methods,
            )
            return

        if existence is Existence.many:
            if not has_disposal_methods:
                return
            creations.add_many(
                spell_id,
                instance,
                has_disposal_methods=has_disposal_methods,
                disposal_methods=disposal_methods,
            )
            return

        # Delegate frame-level lifetimes to the parent creations when available.
        parent_creations = creations._parent_creations
        if isinstance(parent_creations, Creations):
            if existence is Existence.unique:
                parent_creations.add_unique(
                    spell_id,
                    instance,
                    has_disposal_methods=has_disposal_methods,
                    disposal_methods=disposal_methods,
                )
                return
            if existence is Existence.unique_per_conduit_cluster:
                parent_creations.add_unique_per_cluster(
                    spell_id,
                    instance,
                    has_disposal_methods=has_disposal_methods,
                    disposal_methods=disposal_methods,
                )
                return
            if existence is Existence.unique_per_conduit_lineage:
                parent_creations.add_unique_per_lineage(
                    spell_id,
                    instance,
                    has_disposal_methods=has_disposal_methods,
                    disposal_methods=disposal_methods,
                )
                return
            if existence is Existence.unique_per_spell_space:
                if spellspace is None:
                    spellspace = self._get_active_spellspace_for_creations(creations)
                creations.register_spellspace_creation(
                    spellspace.id,
                    spell_id,
                    instance,
                    has_disposal_methods=has_disposal_methods,
                    disposal_methods=disposal_methods,
                )
                return

        # LesserConduits only support a subset of existence modes locally
        raise RuntimeError(
            f"[MELD] Existence '{existence}' is not supported for registration "
            f"in LesserConduits (spell_id={spell_id})."
        )
