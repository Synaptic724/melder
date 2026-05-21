import inspect
from types import TracebackType
from threading import RLock
from typing import Optional, Dict, Any, Callable, List, Tuple, Sequence

from mypy_extensions import mypyc_attr

from melder.utilities.general_base.cleanable import Cleanable
# Melder Imports
from melder.utilities.helpers.general_helpers import SpellInputUtils
from melder.utilities.interfaces.ispellbook import ISpellbook
from melder.utilities.interfaces.ispell import ISpell
from melder.utilities.interfaces.ispellindex import ISpellIndex
from melder.utilities.interfaces.icreation import ICreation
from melder.utilities.interfaces.ichangecontrolmanager import IChangeControlManager
from melder.utilities.interfaces.iconduitresolutionstate import IConduitResolutionState
from melder.utilities.custom_exceptions.hook_execution_error import HookExecutionError
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.utilities.custom_exceptions.spellbook_validation_error import SpellbookValidationError
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state import SpellState
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state_change_reason import (
    SpellStateChangeReason,
)
from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.spell_compiler_system import (
    SpellCompilerSystem,
)

@mypyc_attr(native_class=True)
class Meld(Cleanable):
    """
    ## 🪄 Meld: Spell Activation and Dependency Resolution

    Meld is the **conduit-level entry point** for *activating* spells (components/dependencies)
    within a specific `Conduit`. It handles the full lifecycle of spell resolution,
    creation reuse, hook execution, and registration.

    It is the conduit-local runtime bridge between:
    - `Spellbook`, which owns spell metadata and lookup maps
    - `Creations`, which owns live instances under Existence rules
    - SpellSystemStates / change-control state, which decide whether runtime
      resolution is allowed to continue

    Primary responsibilities:
    - resolve a target spell by spell id or normalized lookup key
    - normalize per-call override payloads
    - enforce structural validity, contract validity, and per-conduit
      resolution validity before instance access
    - reuse existing creations when allowed, or dispatch into creation-context
      runtime lanes when construction is required
    - run pre-cast, activation, post-cast, and meld-level hooks when present
    - own the foundation runtime compiler system surface for later dynamic
      recompilation ownership work

    High-level activation flow:
    1. Resolve the target spell from the requested identity inputs.
    2. Normalize per-call override payloads.
    3. Enforce validity/change-control gates and rerun lazy phases when needed.
    4. Reuse an existing creation or build through `CreationContext`.
    5. Fire activation and meld-level hooks when the route requires them.
    6. Return the final resolved instance.
    """
    __melder_internal__ = _mrg.sentinel
    def __init__(
            self,
            creations: Creations,
            spellbook: ISpellbook,
            conduit_id: Optional[str] = None,
            resolution_conduit_id: Optional[str] = None,
            dynamic_environment: bool = False,
            meld_hooks: Optional[Dict[str, list[Callable[..., Any]]]] = None,
    ) -> None:
        """
        Initialize the Meld component with references to the component store,
        spellbook lookup maps, spell_id maps, and creation-context caches.

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
            dynamic_environment:
                True when the owning conduit runs in dynamic mode. This flag is
                propagated into creation-context construction so runtime context
                policy can branch by mode without re-reading conduit state.
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
        self._dynamic_environment: bool = bool(dynamic_environment)
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
        self._creations: Creations = creations

        # Front-door resolution caches.
        self._input_resolution_cache: Dict[tuple[Any, Any, Any, Any], ISpell] = {}
        self._spell_id_resolution_cache: Dict[str, ISpell] = {}
        self._max_resolution_cache_size: int = 2048
        self._change_control_manager_by_frame: Dict[str, IChangeControlManager] = {}

        # Optional hook map pulled from Configuration (via Conduit).
        # This is stored by reference when provided.
        self._meld_hooks: Optional[Dict[str, list[Callable[..., Any]]]] = (
            meld_hooks if meld_hooks is not None else {}
        )
        # Foundation runtime compiler owner surface for later spell compiler
        # ownership decomposition.
        self._spell_compiler_system: SpellCompilerSystem = (
            SpellCompilerSystem()
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
            del self._owned_spells
            del self._contracted_spells
            del self._spells_by_id
            del self._contracted_spells_by_id
            del self._spell_id_pool
            del self._lookup_owned_spells
            del self._lookup_contracted_spells
            del self._spellbook
            # Clear creations reference
            del self._creations
            del self._conduit_id
            del self._resolution_conduit_id
            del self._dynamic_environment
            del self._meld_hooks
            del self._input_resolution_cache
            del self._spell_id_resolution_cache
            del self._max_resolution_cache_size
            del self._change_control_manager_by_frame
            self._spell_compiler_system.cleanup()
            del self._spell_compiler_system


    # region Context Manager
    def __enter__(self) -> Meld:
        """
        Enter the meld lock context.

        Returns:
            Meld: The resolver instance itself, with the caller now inside the
            same lock-protected critical section used by other mutable meld
            operations.
        """
        return self

    def __exit__(
            self,
            exc_type: type[BaseException] | None,
            exc_value: BaseException | None,
            traceback: TracebackType | None,
    ) -> None:
        """
        Exit the meld lock context.

        Args:
            exc_type: Exception type if an exception occurred inside the
                context.
            exc_value: Exception instance raised inside the context.
            traceback: Traceback for the exception, if any.

        Returns:
            None. The method exists for context-manager symmetry; the surrounding
            lock usage determines the effective critical-section behavior.
        """
        pass

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

                When provided without an explicit spell or spellframe, this is
                treated as the **logical name key** used by the resolution pipeline.
                In other words, meld(spell_name=\"MyService\") becomes equivalent
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
        # 1) Resolve the spell object from the Spellbook / SpellIndex.
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
                target_spell = input_resolution_cache.get(cache_key)
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

        # 2) Normalize per-call overrides into a stable dict shape.
        if spell_override is None:
            override_map = None
        else:
            override_map = self._normalize_spell_override(spell_override)

        # 3) SpellSystemState / SpellValidity gate + lazy revalidation.
        if self._spellbook._spellbook_validation_required:
            self._ensure_lineage_resolvable(target_spell)
        if target_spell.resolution_required:
           self._ensure_runtime_resolution_ready(target_spell)

        creations = self._creations
        meld_hooks = self._meld_hooks
        spell_hooks_enabled = target_spell._hooks_enabled

        if not (meld_hooks or spell_hooks_enabled):
            if target_spell._creation_context_switch.state >= 2:
                creation_context = target_spell._creation_context
            else:
                creation_context = target_spell._get_or_build_creation_context()
            if creation_context is None:
                raise RuntimeError("Spell returned no live CreationContext.")
            if override_map is None:
                execute_no_hooks_no_overrides_compiled = (
                    creation_context._execute_no_hooks_no_overrides_compiled
                )
                instance = execute_no_hooks_no_overrides_compiled(creations)
            else:
                execute_no_hooks_overrides_compiled = (
                    creation_context._execute_no_hooks_overrides_compiled
                )
                instance = execute_no_hooks_overrides_compiled(
                    creations,
                    override_map,
                )

            # 7) Return the resolved instance.
            return instance
        else:
            # 1) Execute pre-cast hooks (no instance context yet).
            self._execute_hooks(target_spell._pre_hooks, "pre_cast")
            self._fire_meld_hooks("on_meld_pre_resolve", target_spell)

            if target_spell._creation_context_switch.state >= 2:
                creation_context = target_spell._creation_context
            else:
                creation_context = target_spell._get_or_build_creation_context()
            if creation_context is None:
                raise RuntimeError("Spell returned no live CreationContext.")
            if override_map is None:
                execute_hooks_no_overrides_compiled = (
                    creation_context._execute_hooks_no_overrides_compiled
                )
                instance, created = execute_hooks_no_overrides_compiled(
                    creations
                )
            else:
                execute_hooks_overrides_compiled = (
                    creation_context._execute_hooks_overrides_compiled
                )
                instance, created = execute_hooks_overrides_compiled(
                    creations,
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
                target_spell = input_resolution_cache.get(cache_key)
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

        if target_spell.is_existing_creation:
            if target_spell.user_created_object is None:
                raise ValueError(
                    "Spell '{0}' is not live.".format(target_spell.spell_id)
                )
            return target_spell.user_created_object

        existence = target_spell.existence
        spell_id = target_spell.spell_id
        caller_creations = self._creations

        if existence is Existence.many:
            raise RuntimeError(
                "meld_existing_spell is not supported for Existence.many."
            )

        if existence is Existence.unique_per_conduit:
            creation = caller_creations._creations.get(spell_id)
            if not isinstance(creation, ICreation):
                raise ValueError(
                    "Spell '{0}' is not live.".format(spell_id)
                )
            return creation.value

        if existence is Existence.unique_per_spell_space:
            spellspace = caller_creations.get_active_spellspace()
            if spellspace is None:
                raise ValueError(
                    "Spell '{0}' is not live.".format(spell_id)
                )
            creation = caller_creations.get_spellspace_creation(
                spellspace.id,
                spell_id,
            )
            if creation is None:
                raise ValueError(
                    "Spell '{0}' is not live.".format(spell_id)
                )
            return creation.value

        if existence in {
                Existence.unique,
                Existence.unique_per_conduit_cluster,
                Existence.unique_per_conduit_lineage,
        }:
            owner_creations = target_spell._owner_creations
            if owner_creations is None:
                raise ValueError(
                    "Spell '{0}' is not live.".format(spell_id)
                )
            creation = owner_creations._creations.get(spell_id)
            if not isinstance(creation, ICreation):
                raise ValueError(
                    "Spell '{0}' is not live.".format(spell_id)
                )
            return creation.value

        raise RuntimeError(
            "meld_existing_spell is unsupported for existence '{0}'.".format(
                existence.name
            )
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
            - Reports the query conduit context explicitly so callers know the
              result is scoped to the current conduit and, where relevant, its
              active spellspace or shared owner-creation path.

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
        self.check_cleaned()
        target_spell = self._resolve_spell_for_live_creation_probe(
            spell_name=spell_name,
            spell=spell,
            spellframe=spellframe,
            binding_name=binding_name,
        )
        return self._describe_spell_live_creation_status(target_spell)

    def _ensure_lineage_resolvable(self, spell: ISpell) -> None:
        """
        Ensure the spell is structurally valid enough to continue toward
        resolution.

        This is the main pre-resolution validity gate. It combines three
        responsibilities:

        - rerun structural phases when the lineage is unknown or gated
        - force contract-driven revalidation when `SpellContract` defaults are
          present and need to invalidate conduit-local resolution state
        - hand off to per-conduit resolution gating when structural validity is
          no longer the blocking issue

        Threading:
            Structural reruns are serialized under `spell._lock` so concurrent
            meld calls do not race duplicate validation work.

        Raises:
            SpellbookValidationError: If structural or conduit-local validity
                cannot be promoted into a runnable state.
            MeldExecutionError: If change-control reports the root as dirty for
                the active resolution conduit.
        """
        state = spell.system_state
        # Structural gating
        if self._gated_validation_required(spell):
            with spell._lock:
                if self._gated_validation_required(spell):
                    self._spell_compiler_system.run_structural_phases(
                        self._spellbook,
                        spell,
                    )

                    # If structural validation produced errors, hard-pin to invalid and bail.
                    if spell.is_broken:
                        if state is not None:
                            state.set_validity(SpellValidity.invalid)
                        raise SpellbookValidationError([spell])

                    refreshed_state = spell.system_state
                    if refreshed_state is None or refreshed_state.validity is not SpellValidity.valid:
                        raise SpellbookValidationError([spell])

        self._check_contracts_and_force_revalidation(spell)

        # Resolution gating (per-conduit)
        if not spell.resolution_required:
            self._ensure_resolution_resolvable(spell)

    def _resolve_spell_for_live_creation_probe(
            self,
            *,
            spell_name: str | None,
            spell: str | object | None,
            spellframe: str | object | None,
            binding_name: str | None,
    ) -> ISpell:
        """
        Resolve one spell for the live-creation probe using meld semantics.

        Purpose:
            Keep the probe on the same identity-resolution spine as `meld(...)`
            without changing the main meld method itself.

        Args:
            spell_name:
                Optional logical spell name for name-based resolution.
            spell:
                Optional spell id string or spell object.
            spellframe:
                Optional spellframe / protocol / frame key.
            binding_name:
                Optional binding name used for lookup-key resolution.

        Returns:
            ISpell: Resolved spell object for the probe.
        """
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
            return target_spell

        input_resolution_cache = self._input_resolution_cache
        cache_key = (spell_name, spell, spellframe, binding_name)
        try:
            target_spell = input_resolution_cache.get(cache_key)
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
        return target_spell

    def _describe_spell_live_creation_status(self, spell: ISpell) -> Dict[str, object]:
        """
        Return structured live-creation status for one resolved spell.

        Purpose:
            Interpret the resolved spell's existence semantics against the
            current runtime storage state without creating anything.

        Args:
            spell:
                Resolved spell object whose live creation state should be
                checked.

        Returns:
            Dict[str, object]: Structured status payload for the resolved
            spell.

        Raises:
            RuntimeError:
                If the spell advertises an unsupported or inconsistent
                existence/storage relationship.
        """
        query_conduit_id = self._conduit_id
        if spell.is_existing_creation:
            return {
                "is_live": spell.user_created_object is not None,
                "spell_id": spell.spell_id,
                "spell_name": spell.spell_name,
                "existence": spell.existence.name,
                "query_conduit_id": query_conduit_id,
                "storage_scope_kind": "existing_creation",
                "storage_owner_conduit_id": None,
                "active_spellspace_id": None,
                "creation_count": 1 if spell.user_created_object is not None else 0,
            }

        existence = spell.existence
        spell_id = spell.spell_id
        caller_creations = self._creations

        if existence is Existence.many:
            creation_bucket = caller_creations._creations.get(spell_id)
            creation_count = (
                len(creation_bucket)
                if isinstance(creation_bucket, list)
                else 0
            )
            return {
                "is_live": creation_count > 0,
                "spell_id": spell_id,
                "spell_name": spell.spell_name,
                "existence": existence.name,
                "query_conduit_id": query_conduit_id,
                "storage_scope_kind": "caller_conduit_many",
                "storage_owner_conduit_id": query_conduit_id,
                "active_spellspace_id": None,
                "creation_count": creation_count,
            }

        if existence is Existence.unique_per_conduit:
            creation = caller_creations._creations.get(spell_id)
            return {
                "is_live": creation is not None,
                "spell_id": spell_id,
                "spell_name": spell.spell_name,
                "existence": existence.name,
                "query_conduit_id": query_conduit_id,
                "storage_scope_kind": "caller_conduit",
                "storage_owner_conduit_id": query_conduit_id,
                "active_spellspace_id": None,
                "creation_count": 1 if creation is not None else 0,
            }

        if existence is Existence.unique_per_spell_space:
            spellspace = caller_creations.get_active_spellspace()
            if spellspace is None:
                return {
                    "is_live": False,
                    "spell_id": spell_id,
                    "spell_name": spell.spell_name,
                    "existence": existence.name,
                    "query_conduit_id": query_conduit_id,
                    "storage_scope_kind": "active_spellspace",
                    "storage_owner_conduit_id": query_conduit_id,
                    "active_spellspace_id": None,
                    "creation_count": 0,
                }
            creation = caller_creations.get_spellspace_creation(
                spellspace.id,
                spell_id,
            )
            return {
                "is_live": creation is not None,
                "spell_id": spell_id,
                "spell_name": spell.spell_name,
                "existence": existence.name,
                "query_conduit_id": query_conduit_id,
                "storage_scope_kind": "active_spellspace",
                "storage_owner_conduit_id": query_conduit_id,
                "active_spellspace_id": spellspace.id,
                "creation_count": 1 if creation is not None else 0,
            }

        if existence in {
                Existence.unique,
                Existence.unique_per_conduit_cluster,
                Existence.unique_per_conduit_lineage,
        }:
            owner_creations = spell._owner_creations
            if owner_creations is None:
                return {
                    "is_live": False,
                    "spell_id": spell_id,
                    "spell_name": spell.spell_name,
                    "existence": existence.name,
                    "query_conduit_id": query_conduit_id,
                    "storage_scope_kind": "owner_creations",
                    "storage_owner_conduit_id": spell._owner_conduit_id,
                    "active_spellspace_id": None,
                    "creation_count": 0,
                }
            creation = owner_creations._creations.get(spell_id)
            return {
                "is_live": creation is not None,
                "spell_id": spell_id,
                "spell_name": spell.spell_name,
                "existence": existence.name,
                "query_conduit_id": query_conduit_id,
                "storage_scope_kind": "owner_creations",
                "storage_owner_conduit_id": spell._owner_conduit_id,
                "active_spellspace_id": None,
                "creation_count": 1 if creation is not None else 0,
            }

        raise RuntimeError(
            "Unsupported existence '{0}' for live creation probe.".format(
                existence,
            )
        )

    def _ensure_runtime_resolution_ready(self, spell: ISpell) -> None:
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
        with spell._lock:
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
                raise

            spell.resolution_complete = True
            spell.resolution_required = False

    def _get_cached_change_control_manager(
            self,
            spellbook: Optional[ISpellbook],
    ) -> Optional[IChangeControlManager]:
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
            Optional[IChangeControlManager]:
                Change-control manager for the frame, or None.
        """
        if spellbook is None:
            return None

        frame_name = spellbook._aetheric_frame
        if frame_name is None:
            return None
        cache = self._change_control_manager_by_frame
        cached_manager = cache.get(frame_name)
        if cached_manager is not None:
            return cached_manager

        aether = spellbook._aether
        if aether is None:
            return None

        manager: Optional[IChangeControlManager] = None
        try:
            manager = aether._get_change_control_manager(frame_name)
        except Exception:
            return None

        if manager is not None:
            cache[frame_name] = manager

        return manager

    def _gated_validation_required(self, spell: ISpell) -> bool:
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
        state = spell.system_state
        conduit_id = self._resolution_conduit_id
        if conduit_id:
            spellbook = spell._spellbook
            ccm = self._get_cached_change_control_manager(spellbook)
            if ccm is not None:
                spell_id = spell.spell_index.current
                if spell_id is None:
                    raise RuntimeError("SpellIndex.current is required for meld gating.")
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

        if state is None:
            return True

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
                if spellbook is None:
                    raise RuntimeError("Spell has no owning Spellbook surface.")
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
        if spell_id is None:
            raise RuntimeError("SpellIndex.current is required for SpellContract validation.")
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
        if spell_id is None:
            raise RuntimeError("SpellIndex.current is required for resolution revalidation.")
        use_root = self._spell_compiler_system.is_current_spell_phase5_root(
            spell
        )

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
            resolution_state: Optional[IConduitResolutionState],
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

        spell_id = spell.spell_index.current
        if spell_id is None:
            return SpellValidity.unknown
        if self._spell_compiler_system.is_current_spell_phase5_root(spell):
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
            - A shallow copy is created to avoid accidental mutation of the
              caller's dictionary.

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

        Resolve an ISpell using either:

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
        return resolved

    def _resolve_spell_by_id(self, spell_id: str) -> ISpell:
        """
        Resolve a spell by its current canonical spell id.

        This is the direct-id lookup path for callers that already know the
        exact current lineage id and do not need logical frame/binding
        normalization.

        Args:
            spell_id:
                The SHA256 fingerprint associated with the spell.

        Returns:
            ISpell:
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
    ) -> ISpell:
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
            ISpell:
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
    ) -> Optional[ISpell]:
        """
        Attempt local Spellbook resolution for one logical lookup key.

        Args:
            lookup_key:
                The logical identity key (frame_key, binding_name).

        Returns:
            Optional[ISpell]:
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
    ) -> Optional[ISpell]:
        """
        Attempt contracted-conduit resolution for one logical lookup key.

        This is the borrower/provider lookup path. It iterates through the
        per-conduit contracted maps until it finds a matching SpellIndex and
        then resolves that index back to the concrete spell object.

        Args:
            lookup_key:
                The logical identity key (frame_key, binding_name).

        Returns:
            Optional[ISpell]:
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
