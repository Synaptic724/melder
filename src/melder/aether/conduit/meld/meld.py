import inspect
from threading import RLock
from typing import Optional, Dict, Any, Callable, List, Tuple, Sequence

from melder.aether.conduit.meld.creation_context.creation_context_factory import (
    CreationContextFactory,
)
from melder.utilities.general_base.cleanable import Cleanable
# Melder Imports
from melder.utilities.helpers.general_helpers import SpellInputUtils
from melder.utilities.interfaces.interfaces import (
    ISpellbook,
    ISpell,
    IMeld,
    ICreations, ISpellIndex,
)
from melder.utilities.custom_exceptions.hook_execution_error import HookExecutionError
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
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
            creations: ICreations,
            spellbook: ISpellbook,
            conduit_id: Optional[str] = None,
            resolution_conduit_id: Optional[str] = None,
            meld_hooks: Optional[Dict[str, list[Callable[..., Any]]]] = None,
    ) -> None:
        """
        Initialize the Meld component with references to the component store,
        spellbook lookup maps, spell_id maps, and meld runtime caches.

        Args:
            creations:
                The conduit-local component instance manager (`Creations`).
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
            meld_hooks:
                Optional hook map passed by Conduit. When provided, Meld stores
                this map by reference so shared hook mutations are immediately
                visible without re-copying.
        """
        super().__init__()

        self._lock = RLock()
        self._cleaned: bool = False
        self._conduit_id: Optional[str] = conduit_id
        self._resolution_conduit_id: Optional[str] = (
            resolution_conduit_id if resolution_conduit_id is not None else conduit_id
        )
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


        # Conduit-local instantiation manager.
        self._creations = creations

        # Front-door resolution caches.
        self._input_resolution_cache: Dict[tuple[Any, Any, Any, Any], ISpell] = {}
        self._spell_id_resolution_cache: Dict[str, ISpell] = {}
        self._max_resolution_cache_size: int = 2048

        # Builder-backed factory used for spell-owned CreationContext builds.
        self._creation_context_factory: CreationContextFactory = (
            CreationContextFactory()
        )

        # Optional hook map pulled from Configuration (via Conduit).
        # This is stored by reference when provided.
        self._meld_hooks: Optional[Dict[str, list[Callable[..., Any]]]] = (
            meld_hooks if meld_hooks is not None else {}
        )


    def cleanup(self) -> None:
        """
        Cleanup the Meld instance to prevent further use and release references
        to spell configurations, creations manager, and runtime caches.

        This should be called when the owning `Conduit` is being shut down.

        Contract:
            - Idempotent: repeated calls are safe.
            - Thread-safe: guarded by the internal lock.
            - Runtime caches are cleared deterministically.
            - After cleanup, references are cleared and this instance must not be used.

        Behaviour:
            - Marks the instance as cleaned.
            - Clears references to spellbook maps, spell_id maps, and creations.
            - Clears override specialization cache state.

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
            self._resolution_conduit_id = None
            creation_context_factory = self._creation_context_factory
            if creation_context_factory is not None:
                try:
                    creation_context_factory.cleanup()
                except Exception:
                    pass
            self._creation_context_factory = None
            self._meld_hooks = None
            self._input_resolution_cache = None
            self._spell_id_resolution_cache = None
            self._max_resolution_cache_size = None


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
                to be consumed by the runtime codegen layer for this specific
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
        if spell_override is None:
            override_map = None
        else:
            override_map = self._normalize_spell_override(spell_override)

        # 2) Resolve the spell object from the Spellbook / SpellIndex.
        target_spell: Optional[ISpell] = None
        if isinstance(spell, str):
            spell_id_resolution_cache = self._spell_id_resolution_cache
            target_spell = spell_id_resolution_cache.get(spell)
            if target_spell is None:
                target_spell = self._resolve_spell_by_id(spell)
                if len(spell_id_resolution_cache) >= self._max_resolution_cache_size:
                    spell_id_resolution_cache.pop(
                        next(iter(spell_id_resolution_cache)),
                        None,
                    )
                spell_id_resolution_cache[spell] = target_spell
        else:
            input_resolution_cache = self._input_resolution_cache
            cache_key = (spell_name, spell, spellframe, binding_name)
            try:
                hash(cache_key)
            except TypeError:
                cache_key = (
                    spell_name,
                    id(spell),
                    id(spellframe),
                    binding_name,
                )
            target_spell = input_resolution_cache.get(cache_key)
            if target_spell is None:
                target_spell = self._resolve_spell(
                    spell=spell,
                    spell_name=spell_name,
                    spellframe=spellframe,
                    binding_name=binding_name,
                )
                if len(input_resolution_cache) >= self._max_resolution_cache_size:
                    input_resolution_cache.pop(
                        next(iter(input_resolution_cache)),
                        None,
                    )
                input_resolution_cache[cache_key] = target_spell

        # 3) SpellSystemState / SpellValidity gate + lazy revalidation.
        if self._spellbook._spellbook_validation_required:
            self._ensure_lineage_resolvable(target_spell)

        if not (self._meld_hooks or target_spell._hooks_enabled):
            creation_context = target_spell._creation_context
            if creation_context is None or creation_context._cleaned:
                creation_context_factory = self._creation_context_factory
                creation_context = creation_context_factory.get_or_build_for_spell(
                    target_spell
                )
            execute_no_hooks_compiled = creation_context._execute_no_hooks_compiled
            instance = execute_no_hooks_compiled(
                self._creations,
                override_map,
            )

            # 7) Return the resolved instance.
            return instance
        else:
            # 1) Execute pre-cast hooks (no instance context yet).
            self._execute_hooks(target_spell._pre_hooks, "pre_cast")
            self._fire_meld_hooks("on_meld_pre_resolve", target_spell)

            creation_context = target_spell._creation_context
            if creation_context is None or creation_context._cleaned:
                creation_context_factory = self._creation_context_factory
                creation_context = creation_context_factory.get_or_build_for_spell(
                    target_spell
                )
            execute_compiled = creation_context._execute_compiled
            if override_map is None:
                instance, created = execute_compiled(self._creations)
            else:
                instance, created = execute_compiled(self._creations, override_map)

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
               `spell._spellbook._run_resolution_phases_for_target_spell(conduit_id, spell)`.
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
        - SpellValidity.invalid / disabled / cleaned -> raise SpellbookValidationError.
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
            conduit_id = self._resolution_conduit_id
            if ccm is not None and conduit_id and ccm.is_root_dirty(conduit_id, spell.spell_index.current):
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

        # invalid / disabled / cleaned → hard block, no attempt to resolve
        if (
                validity is SpellValidity.invalid
                or validity is SpellValidity.disabled
                or validity is SpellValidity.cleaned
        ):
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
        if resolution validity is UNKNOWN or GATED. Invalid, disabled, or
        cleaned validity states are hard blocks.
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
            with spell._lock:
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
                spellbook._run_resolution_phases_for_target_spell(conduit_id, spell)

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
        conduit_id = self._resolution_conduit_id
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
        """
        if not create_local_hooks:
            self._meld_hooks = hooks
            return

        local_hooks: Dict[str, list[Callable[..., Any]]] = {}

        if not overwrite and self._meld_hooks:
            for name, hook_list in self._meld_hooks.items():
                if hook_list is None:
                    continue
                local_hooks[name] = list(hook_list)

        if hooks:
            for name, hook_list in hooks.items():
                if hook_list is None:
                    continue
                if overwrite:
                    local_hooks[name] = list(hook_list)
                else:
                    local_hooks.setdefault(name, []).extend(hook_list)
        self._meld_hooks = local_hooks

    def _fire_meld_hooks(self, hook_name: str, *args: Any) -> None:
        """
        Invoke meld-level hooks by name. Exceptions are wrapped in HookExecutionError.
        """
        hook_list = self._meld_hooks.get(hook_name)
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
        Normalize the ``spell_override`` input into a consistent dictionary format.

        The **override payload** is intended to represent *per-call* constructor
        / factory overrides for a given meld operation. This helper converts the
        user-facing shapes into a uniform internal representation that can be
        consumed by the Meld runtime codegen layer.

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
              runtime can distinguish them from keyword overrides:
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

    # Resolution helpers
    # ----------------------------------------------------------------------
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
            ValueError:
                If resolution key normalization receives no spell identity source.
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
        resolved = self._resolve_spell_by_lookup_key(lookup_key)
        resolved.check_cleaned()
        return resolved

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

