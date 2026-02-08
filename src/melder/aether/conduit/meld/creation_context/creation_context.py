from operator import itemgetter
from typing import Optional, Dict, Any, Callable, Tuple, Sequence

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.conduit.meld.creation_context.creation_context_codegen import (
    compile_creation_context_executor,
)
from melder.spellbook.spell_crafter.blueprints.patch_maps import (
    apply_phase10_override_payload,
)
from melder.spellbook.spell_crafter.blueprints.phase12_overrides_executor import (
    compile_phase12_overrides_executor,
)
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
from melder.utilities.custom_exceptions.spell_space_scope_error import SpellSpaceScopeError
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.interfaces import ICreations, ISpell


class OverrideRouteConfig(Cleanable):
    """
    Immutable spell-static override lane configuration.

    Purpose:
        Hold pre-resolved Phase 11/12 wiring so override execution can avoid
        repeating IR and blueprint lookups on each runtime call.

    Contract:
        - All fields are spell-static for the lifetime of one CreationContext.
        - This object carries no per-call override payload data.
    """

    __slots__ = Cleanable.__slots__ + [
        "plan_signature",
        "path_registry",
        "plan_rows",
        "root_spell_id",
        "spell_lookup",
        "empty_shape_key",
        "baseline_executor",
    ]

    def __init__(
            self,
            *,
            plan_signature: Tuple[Any, ...],
            path_registry: Optional[Any],
            plan_rows: Optional[Sequence[Dict[str, Any]]],
            root_spell_id: Optional[str],
            spell_lookup: Optional[Dict[str, Any]],
            empty_shape_key: Optional[Tuple[Any, ...]] = None,
            baseline_executor: Optional[Callable[..., Any]] = None,
    ) -> None:
        """
        Build one static override route configuration payload.

        Args:
            plan_signature:
                Deterministic Phase 11 signature tuple for this override variant.
            path_registry:
                Root blueprint path registry used by specialization prefiltering.
            plan_rows:
                Schema rows for Phase 12 override executor compilation.
            root_spell_id:
                Root spell id for this execution variant.
            spell_lookup:
                Spell lookup map keyed by spell_id for schema hydration.
            empty_shape_key:
                Deterministic empty-shape specialization key for no-payload
                override calls.
            baseline_executor:
                Optional precompiled override executor for empty override payload.
        """
        super().__init__()
        self.plan_signature: Tuple[Any, ...] = plan_signature
        self.path_registry: Optional[Any] = path_registry
        self.plan_rows: Optional[Sequence[Dict[str, Any]]] = plan_rows
        self.root_spell_id: Optional[str] = root_spell_id
        self.spell_lookup: Optional[Dict[str, Any]] = spell_lookup
        self.empty_shape_key: Optional[Tuple[Any, ...]] = empty_shape_key
        self.baseline_executor: Optional[Callable[..., Any]] = baseline_executor

    def cleanup(self) -> None:
        """
        Deterministically release references held by this route config.

        Contract:
            - Idempotent cleanup.
            - Safe for best-effort cleanup flows on detached contexts.
            - Drops all spell-static references to avoid stale retention.
        """
        if self._cleaned:
            return
        self._cleaned = True

        self.plan_signature = None
        self.path_registry = None
        self.plan_rows = None
        self.root_spell_id = None
        self.spell_lookup = None
        self.empty_shape_key = None
        self.baseline_executor = None


class CreationContext(Cleanable):
    """
    Spell-bound runtime executor context used by Meld hot paths.

    Purpose:
        Hold spell-static execution state so repeated meld calls can skip
        rebuild overhead and dispatch directly into the spell's specialized
        runtime lanes.

    Ownership:
        - Lives on `Spell` as `spell._creation_context`.
        - Built by `CreationContextBuilder` / `CreationContextFactory`.
        - Cleared when spell ownership or structural state changes.

    Contract:
        - No per-call transient state is stored on this object.
        - Per-call transients (`caller_creations`, `overrides`) are supplied
          to `execute(...)`.
        - Existence routing is selected once at build time and reused.
        - Owns override specialization executors scoped to this spell.
    """

    __melder_internal__ = _mrg.sentinel
    ROUTE_EXISTING_CREATION = "existing_creation"
    ROUTE_SPELLSPACE = "spellspace"
    ROUTE_UNIQUE_PER_CONDUIT = "unique_per_conduit"
    ROUTE_MANY = "many"
    ROUTE_SHARED = "shared"
    FLAG_FAST_TRANSIENT_NO_OVERRIDES = 1
    FLAG_OVERRIDE_ROUTE_NO_MUTATION = 2
    FLAG_OVERRIDE_ROUTE_MUTATION = 4

    __slots__ = Cleanable.__slots__ + [
        "_spell",
        "_spell_id",
        "_owner_creations",
        "_resolve_route_key",
        "_execute_compiled",
        "_runtime_flags",
        "_mutation_override_enabled",
        "_fast_transient_no_overrides_enabled",
        "_no_overrides_executor",
        "_override_patch_map_phase10",
        "_override_route_config_no_mutation",
        "_override_route_config_mutation",
        "_override_route_config_active",
        "_override_specialization_cache",
    ]

    def __init__(
            self,
            *,
            spell: ISpell,
            resolve_route_key: str,
            runtime_flags: int = 0,
            fast_transient_no_overrides_enabled: bool = False,
            no_overrides_executor: Optional[Callable[..., Any]] = None,
            override_patch_map_phase10: Optional[Any] = None,
            override_route_config_no_mutation: Optional[OverrideRouteConfig] = None,
            override_route_config_mutation: Optional[OverrideRouteConfig] = None,
    ) -> None:
        """
        Build one spell-shaped runtime context.

        Args:
            spell:
                Spell this context is bound to. All execution logic and caches
                are scoped to this spell only.
            resolve_route_key:
                Preselected existence route key from `CreationContextBuilder`.
            runtime_flags:
                Spell-static bit flags configuring hot-path lane behavior.
                See FLAG_* class constants.
            fast_transient_no_overrides_enabled:
                True when this spell can run no-overrides calls on the direct
                transient executor lane.
            no_overrides_executor:
                Prebound no-overrides phase 12 executor for this spell.
            override_patch_map_phase10:
                Prebound Phase 10 override patch map artifact.
            override_route_config_no_mutation:
                Prebound override route config for non-mutation calls.
            override_route_config_mutation:
                Prebound override route config for mutation calls.
        """
        super().__init__()
        self._spell: ISpell = spell
        self._spell_id: str = spell.spell_id
        self._owner_creations: Any = spell._owner_creations
        self._resolve_route_key: str = resolve_route_key
        resolved_runtime_flags = runtime_flags
        if fast_transient_no_overrides_enabled:
            resolved_runtime_flags |= self.FLAG_FAST_TRANSIENT_NO_OVERRIDES
        if override_route_config_no_mutation is not None:
            resolved_runtime_flags |= self.FLAG_OVERRIDE_ROUTE_NO_MUTATION
        if override_route_config_mutation is not None:
            resolved_runtime_flags |= self.FLAG_OVERRIDE_ROUTE_MUTATION
        self._runtime_flags: int = resolved_runtime_flags
        self._mutation_override_enabled: bool = bool(
            resolved_runtime_flags & self.FLAG_OVERRIDE_ROUTE_MUTATION
        )
        self._fast_transient_no_overrides_enabled: bool = (
            fast_transient_no_overrides_enabled
        )
        self._no_overrides_executor: Optional[Callable[..., Any]] = (
            no_overrides_executor
        )
        self._override_patch_map_phase10: Optional[Any] = (
            override_patch_map_phase10
        )
        self._override_route_config_no_mutation: Optional[OverrideRouteConfig] = (
            override_route_config_no_mutation
        )
        self._override_route_config_mutation: Optional[OverrideRouteConfig] = (
            override_route_config_mutation
        )
        if self._mutation_override_enabled:
            self._override_route_config_active: Optional[OverrideRouteConfig] = (
                self._override_route_config_mutation
            )
        else:
            self._override_route_config_active = self._override_route_config_no_mutation
        self._override_specialization_cache: Dict[
            Tuple[Any, ...],
            Callable[..., Any],
        ] = {}
        self._seed_baseline_override_executor(override_route_config_no_mutation)
        self._seed_baseline_override_executor(override_route_config_mutation)
        self._execute_compiled: Callable[..., tuple[Any, bool]] = (
            compile_creation_context_executor(
                resolve_route_key=resolve_route_key,
                mutation_override_enabled=self._mutation_override_enabled,
                fast_transient_no_overrides_enabled=(
                    resolve_route_key == self.ROUTE_MANY
                    and fast_transient_no_overrides_enabled
                    and not self._mutation_override_enabled
                ),
                spell=spell,
                spell_id=self._spell_id,
                owner_creations=self._owner_creations,
                no_overrides_executor=self._no_overrides_executor,
                execute_with_overrides=self._execute_with_overrides,
                meld_execution_error_type=MeldExecutionError,
                spell_space_scope_error_type=SpellSpaceScopeError,
            )
        )

    def cleanup(self) -> None:
        """
        Deterministically release runtime caches and references.

        Contract:
            - Idempotent cleanup.
            - Clears override specialization cache for this spell.
            - Drops references so stale contexts cannot execute.
        """
        if self._cleaned:
            return
        self._cleaned = True

        override_specialization_cache = self._override_specialization_cache
        override_specialization_cache.clear()

        override_route_config_no_mutation = self._override_route_config_no_mutation
        if override_route_config_no_mutation is not None:
            try:
                override_route_config_no_mutation.cleanup()
            except Exception:
                pass

        override_route_config_mutation = self._override_route_config_mutation
        if override_route_config_mutation is not None:
            try:
                override_route_config_mutation.cleanup()
            except Exception:
                pass

        self._spell = None
        self._spell_id = None
        self._owner_creations = None
        self._resolve_route_key = None
        self._execute_compiled = None
        self._runtime_flags = None
        self._mutation_override_enabled = None
        self._fast_transient_no_overrides_enabled = None
        self._no_overrides_executor = None
        self._override_patch_map_phase10 = None
        self._override_route_config_no_mutation = None
        self._override_route_config_mutation = None
        self._override_route_config_active = None
        self._override_specialization_cache = None

    def execute(
            self,
            caller_creations: ICreations,
            overrides: Optional[dict[str, Any]] = None,
    ) -> tuple[Any, bool]:
        """
        Execute one meld resolution against this spell-shaped context.

        Args:
            caller_creations:
                Creations container for the calling conduit.
            overrides:
                Optional per-call override payload already normalized by Meld.

        Returns:
            tuple[Any, bool]:
                `(instance, created)` where `created=True` means this call
                instantiated the spell object.
        """
        execute_compiled = self._execute_compiled
        return execute_compiled(caller_creations, overrides)

    def _seed_baseline_override_executor(
            self,
            override_route_config: Optional[OverrideRouteConfig],
    ) -> None:
        """
        Seed the override specialization cache with one baseline executor.

        Contract:
            - No-op when route config has no baseline executor payload.
            - Stores one empty-shape executor keyed by route-specific signature.
            - Safe to call repeatedly; later values replace earlier cache values.
        """
        if override_route_config is None:
            return
        shape_key = override_route_config.empty_shape_key
        baseline_executor = override_route_config.baseline_executor
        if shape_key is None or baseline_executor is None:
            return
        self._override_specialization_cache[shape_key] = baseline_executor

    # ----------------------------------------------------------------------
    # Existence-specialized resolve routes
    # ----------------------------------------------------------------------
    def _resolve_existing_creation_instance_no_overrides(
            self,
            caller_creations: ICreations,
    ) -> tuple[Any, bool]:
        """
        Resolve EXISTING_CREATION spells with no override payload.
        """
        spell = self._spell
        instance = spell.user_created_object
        if instance is None:
            raise RuntimeError(
                "[MELD] EXISTING_CREATION spell has no `user_created_object` "
                f"(spell_id={self._spell_id})."
            )
        return instance, False

    def _resolve_existing_creation_instance_with_overrides(
            self,
            caller_creations: ICreations,
            overrides: Optional[dict[str, Any]],
    ) -> tuple[Any, bool]:
        """
        Resolve EXISTING_CREATION spells when override or mutation lanes are active.
        """
        spell = self._spell
        self._raise_override_on_existing_instance(overrides)
        instance = spell.user_created_object
        if instance is None:
            raise RuntimeError(
                "[MELD] EXISTING_CREATION spell has no `user_created_object` "
                f"(spell_id={self._spell_id})."
            )
        return instance, False

    def _resolve_many_instance_no_overrides(
            self,
            caller_creations: ICreations,
    ) -> tuple[Any, bool]:
        """
        Resolve many-existence spells on the no-overrides lane.
        """
        instance = self._execute_no_overrides(
            caller_creations=caller_creations,
            caller_creations_lock_held=False,
        )
        return instance, True

    def _resolve_many_instance_no_overrides_fast_transient(
            self,
            caller_creations: ICreations,
    ) -> tuple[Any, bool]:
        """
        Resolve many-existence no-overrides calls through transient fast lane.
        """
        spell = self._spell
        executor = self._no_overrides_executor
        try:
            return executor(None), True
        except MeldExecutionError:
            raise
        except Exception as exc:
            raise MeldExecutionError(
                spell_id=spell.spell_index.current,
                spell_name=spell.spell_name,
                message="Phase 12 transient executor failed.",
                inner=exc,
            ) from exc

    def _resolve_many_instance_with_overrides(
            self,
            caller_creations: ICreations,
            overrides: Optional[dict[str, Any]],
    ) -> tuple[Any, bool]:
        """
        Resolve many-existence spells on the overrides or mutation lane.
        """
        instance = self._execute_with_overrides(
            caller_creations,
            overrides,
            False,
        )
        return instance, True

    def _resolve_unique_per_conduit_instance_no_overrides(
            self,
            caller_creations: ICreations,
    ) -> tuple[Any, bool]:
        """
        Resolve unique-per-conduit spells on the no-overrides lane.
        """
        spell_id = self._spell_id
        creation = caller_creations._creations.get(spell_id)
        if creation is not None:
            return creation.value, False

        with caller_creations._lock:
            creation = caller_creations._creations.get(spell_id)
            if creation is None:
                instance = self._execute_no_overrides(caller_creations, True)
                return instance, True
            return creation.value, False

    def _resolve_unique_per_conduit_instance_with_overrides(
            self,
            caller_creations: ICreations,
            overrides: Optional[dict[str, Any]],
    ) -> tuple[Any, bool]:
        """
        Resolve unique-per-conduit spells on overrides or mutation lane.
        """
        spell = self._spell
        spell_id = self._spell_id
        creation = caller_creations._creations.get(spell_id)
        if creation is not None:
            if overrides is not None:
                raise MeldExecutionError(
                    spell_id=spell.spell_index.current,
                    spell_name=spell.spell_name,
                    message=(
                        "Overrides were supplied for a spell instance that already exists. "
                        "Shared instances cannot be overridden after creation."
                    ),
                )
            return creation.value, False

        with caller_creations._lock:
            creation = caller_creations._creations.get(spell_id)
            if creation is None:
                instance = self._execute_with_overrides(
                    caller_creations,
                    overrides,
                    True,
                )
                return instance, True

            if overrides is not None:
                raise MeldExecutionError(
                    spell_id=spell.spell_index.current,
                    spell_name=spell.spell_name,
                    message=(
                        "Overrides were supplied for a spell instance that already exists. "
                        "Shared instances cannot be overridden after creation."
                    ),
                )
            return creation.value, False

    def _resolve_spellspace_instance_no_overrides(
            self,
            caller_creations: ICreations,
    ) -> tuple[Any, bool]:
        """
        Resolve spellspace-scoped spells on the no-overrides lane.
        """
        spellspace = self._get_active_spellspace_for_creations(caller_creations)
        spell_id = self._spell_id
        creation = caller_creations.get_spellspace_creation(spellspace.id, spell_id)
        if creation is not None:
            return creation.value, False

        with caller_creations._lock:
            creation = caller_creations.get_spellspace_creation(spellspace.id, spell_id)
            if creation is None:
                instance = self._execute_no_overrides(caller_creations, True)
                return instance, True
            return creation.value, False

    def _resolve_spellspace_instance_with_overrides(
            self,
            caller_creations: ICreations,
            overrides: Optional[dict[str, Any]],
    ) -> tuple[Any, bool]:
        """
        Resolve spellspace-scoped spells on overrides or mutation lane.
        """
        spell = self._spell
        spellspace = self._get_active_spellspace_for_creations(caller_creations)
        spell_id = self._spell_id
        creation = caller_creations.get_spellspace_creation(spellspace.id, spell_id)
        if creation is not None:
            if overrides is not None:
                raise MeldExecutionError(
                    spell_id=spell.spell_index.current,
                    spell_name=spell.spell_name,
                    message=(
                        "Overrides were supplied for a spell instance that already exists. "
                        "Shared instances cannot be overridden after creation."
                    ),
                )
            return creation.value, False

        with caller_creations._lock:
            creation = caller_creations.get_spellspace_creation(spellspace.id, spell_id)
            if creation is None:
                instance = self._execute_with_overrides(
                    caller_creations,
                    overrides,
                    True,
                )
                return instance, True

            if overrides is not None:
                raise MeldExecutionError(
                    spell_id=spell.spell_index.current,
                    spell_name=spell.spell_name,
                    message=(
                        "Overrides were supplied for a spell instance that already exists. "
                        "Shared instances cannot be overridden after creation."
                    ),
                )
            return creation.value, False

    def _resolve_shared_instance_no_overrides(
            self,
            caller_creations: ICreations,
    ) -> tuple[Any, bool]:
        """
        Resolve shared unique routes on the no-overrides lane.
        """
        spell = self._spell
        spell_id = self._spell_id
        owner_creations = self._owner_creations

        creation = owner_creations._creations.get(spell_id)
        if creation is not None:
            return creation.value, False

        with spell._lock:
            with owner_creations._lock:
                creation = owner_creations._creations.get(spell_id)

            if creation is None:
                instance = self._execute_no_overrides(caller_creations, False)
                return instance, True
            return creation.value, False

    def _resolve_shared_instance_with_overrides(
            self,
            caller_creations: ICreations,
            overrides: Optional[dict[str, Any]],
    ) -> tuple[Any, bool]:
        """
        Resolve shared unique routes on overrides or mutation lane.
        """
        spell = self._spell
        spell_id = self._spell_id
        owner_creations = self._owner_creations

        creation = owner_creations._creations.get(spell_id)
        if creation is not None:
            if overrides is not None:
                raise MeldExecutionError(
                    spell_id=spell.spell_index.current,
                    spell_name=spell.spell_name,
                    message=(
                        "Overrides were supplied for a spell instance that already exists. "
                        "Shared instances cannot be overridden after creation."
                    ),
                )
            return creation.value, False

        with spell._lock:
            with owner_creations._lock:
                creation = owner_creations._creations.get(spell_id)

            if creation is None:
                instance = self._execute_with_overrides(
                    caller_creations,
                    overrides,
                    False,
                )
                return instance, True

            if overrides is not None:
                raise MeldExecutionError(
                    spell_id=spell.spell_index.current,
                    spell_name=spell.spell_name,
                    message=(
                        "Overrides were supplied for a spell instance that already exists. "
                        "Shared instances cannot be overridden after creation."
                    ),
                )
            return creation.value, False

    def _get_owner_creations(self) -> Any:
        """
        Resolve owner creations for shared existence routes.
        """
        owner_creations = self._owner_creations
        if owner_creations is None:
            raise RuntimeError(
                "[MELD] Spell owner creations is not attached for a shared "
                f"existence route (spell_id={self._spell_id})."
            )
        return owner_creations

    def _raise_override_on_existing_instance(
            self,
            overrides: Optional[dict[str, Any]],
    ) -> None:
        """
        Reject per-call overrides when reuse returns an existing instance.
        """
        if overrides is None:
            return

        spell = self._spell
        raise MeldExecutionError(
            spell_id=spell.spell_index.current,
            spell_name=spell.spell_name,
            message=(
                "Overrides were supplied for a spell instance that already exists. "
                "Shared instances cannot be overridden after creation."
            ),
        )

    @staticmethod
    def _get_existing_creation_from_creations(
            *,
            spell_id: str,
            creations: Any,
    ) -> Optional[Any]:
        """
        Resolve one non-spellspace creation from the selected creations map.
        """
        creation = creations._creations.get(spell_id)
        if creation is None:
            return None
        return creation.value

    @staticmethod
    def _get_spellspace_existing_creation_from_creations(
            *,
            spell_id: str,
            creations: Any,
            spellspace: Any,
    ) -> Optional[Any]:
        """
        Resolve one spellspace-scoped instance from a creations container.
        """
        creation = creations.get_spellspace_creation(spellspace.id, spell_id)
        return creation.value if creation is not None else None

    @staticmethod
    def _get_active_spellspace_for_creations(creations: Any) -> Any:
        """
        Resolve the active spellspace for a caller creations container.
        """
        spellspace = creations._conduit.get_active_spellspace()
        if spellspace is None:
            raise SpellSpaceScopeError(
                "Existence.unique_per_spell_space requires an active SpellSpace. "
                "Use 'with conduit.enter_spellspace()' when melding."
            )
        return spellspace

    # ----------------------------------------------------------------------
    # Runtime dispatch and registration
    # ----------------------------------------------------------------------
    def execute_no_overrides_fast_transient(self) -> Any:
        """
        Execute one transient no-overrides spell through the phase 12 executor.
        """
        spell = self._spell
        executor = self._no_overrides_executor
        try:
            return executor(None)
        except MeldExecutionError:
            raise
        except Exception as exc:
            raise MeldExecutionError(
                spell_id=spell.spell_index.current,
                spell_name=spell.spell_name,
                message="Phase 12 transient executor failed.",
                inner=exc,
            ) from exc

    def _execute_no_overrides(
            self,
            caller_creations: ICreations,
            caller_creations_lock_held: bool,
    ) -> Any:
        """
        Execute one no-overrides call through compiled phase 12 executor.
        """
        spell = self._spell
        executor = self._no_overrides_executor
        try:
            result = executor(
                caller_creations,
                owner_creations=self._owner_creations,
                caller_creations_lock_held=caller_creations_lock_held,
            )
        except MeldExecutionError:
            raise
        except Exception as exc:
            raise MeldExecutionError(
                spell_id=spell.spell_index.current,
                spell_name=spell.spell_name,
                message="Phase 12 no-overrides executor failed.",
                inner=exc,
            ) from exc
        return result

    def _execute_with_overrides(
            self,
            caller_creations: ICreations,
            overrides: Optional[dict[str, Any]],
            caller_creations_lock_held: bool,
    ) -> Any:
        """
        Execute one override-bearing call through phase 10/11/12 specialization.
        """
        spell = self._spell
        override_route_config = self._override_route_config_active

        override_payload = overrides
        root_positional_override: Optional[Sequence[Any]] = None
        override_map: Dict[Any, Any] = {}
        if not override_payload:
            baseline_executor = override_route_config.baseline_executor
            if baseline_executor is not None:
                result = baseline_executor(
                    caller_creations,
                    override_map,
                    root_positional_override,
                    owner_creations=self._owner_creations,
                    caller_creations_lock_held=caller_creations_lock_held,
                )
                return result
        if override_payload:
            target_payload, root_positional_override = self._split_override_payload(
                spell=spell,
                override_payload=override_payload,
            )
            if target_payload:
                override_patch_map_phase10 = self._override_patch_map_phase10
                try:
                    override_map = apply_phase10_override_payload(
                        override_patch_map=override_patch_map_phase10,
                        override_payload=target_payload,
                    )
                except MeldExecutionError:
                    raise
                except Exception as exc:
                    raise MeldExecutionError(
                        spell_id=spell.spell_index.current,
                        spell_name=spell.spell_name,
                        message=(
                            "Failed to apply overrides through the Phase 10 "
                            "override patch map."
                        ),
                        inner=exc,
                    ) from exc

        if override_map:
            (
                override_targets_by_spell_id,
                socket_shape,
            ) = self._collect_override_targets_and_socket_shape(
                override_map=override_map,
            )
        else:
            override_targets_by_spell_id = {}
            socket_shape = ()
        try:
            plan_signature = override_route_config.plan_signature
            shape_key = self._build_override_shape_key(
                plan_signature=plan_signature,
                socket_shape=socket_shape,
                root_positional_override=root_positional_override,
            )
        except MeldExecutionError:
            raise
        except Exception as exc:
            raise MeldExecutionError(
                spell_id=spell.spell_index.current,
                spell_name=spell.spell_name,
                message=(
                    "Failed to build override specialization shape key from the "
                    "Phase 11 execution plan."
                ),
                inner=exc,
            ) from exc
        any_overrides_present = overrides is not None
        executor = self._get_or_compile_override_executor(
            shape_key=shape_key,
            override_targets_by_spell_id=override_targets_by_spell_id,
            any_overrides_present=any_overrides_present,
            path_registry=override_route_config.path_registry,
            plan_rows=override_route_config.plan_rows,
            root_spell_id=override_route_config.root_spell_id,
            spell_lookup=override_route_config.spell_lookup,
        )

        result = executor(
            caller_creations,
            override_map,
            root_positional_override,
            owner_creations=self._owner_creations,
            caller_creations_lock_held=caller_creations_lock_held,
        )
        return result

    @staticmethod
    def _split_override_payload(
            *,
            spell: ISpell,
            override_payload: Dict[str, Any],
    ) -> Tuple[Dict[str, Any], Optional[Sequence[Any]]]:
        """
        Split root positional overrides from keyed TargetSpec override payload.
        """
        raw_args = override_payload.get("__args__")
        if raw_args is None:
            return override_payload, None
        if isinstance(raw_args, tuple):
            normalized_root_args = raw_args
        elif isinstance(raw_args, list):
            normalized_root_args = tuple(raw_args)
        else:
            raise MeldExecutionError(
                spell_id=spell.spell_index.current,
                spell_name=spell.spell_name,
                message="__args__ override must be a list or tuple.",
            )
        override_payload_size = len(override_payload)
        if override_payload_size == 1:
            return {}, normalized_root_args
        if override_payload_size == 2:
            for param_name, value in override_payload.items():
                if param_name != "__args__":
                    return {
                        param_name: value,
                    }, normalized_root_args

        normalized_payload: Dict[str, Any] = {}
        for param_name, value in override_payload.items():
            if param_name == "__args__":
                continue
            normalized_payload[param_name] = value
        return normalized_payload, normalized_root_args

    @staticmethod
    def _collect_override_targets_and_socket_shape(
            *,
            override_map: Dict[Any, Any],
    ) -> Tuple[Dict[str, Tuple[Any, ...]], Tuple[Tuple[Any, ...], ...]]:
        """
        Group override sockets by spell id and build deterministic shape tuples.
        """
        if not override_map:
            return {}, ()
        if len(override_map) == 1:
            socket_ref = next(iter(override_map))
            node_id = socket_ref.node_id
            param_path_id = socket_ref.param_path_id
            param_name = socket_ref.param_name
            socket_kind_value = socket_ref.socket_kind.value
            return (
                {
                    node_id: (socket_ref,),
                },
                (
                    (
                        node_id,
                        param_path_id,
                        param_name,
                        socket_kind_value,
                    ),
                ),
            )
        if len(override_map) == 2:
            refs_iter = iter(override_map)
            first_ref = next(refs_iter)
            second_ref = next(refs_iter)
            first_ref_node_id = first_ref.node_id
            first_ref_param_path_id = first_ref.param_path_id
            first_ref_param_name = first_ref.param_name
            first_ref_socket_kind_value = first_ref.socket_kind.value
            first_shape_row = (
                first_ref_node_id,
                first_ref_param_path_id,
                first_ref_param_name,
                first_ref_socket_kind_value,
            )
            second_ref_node_id = second_ref.node_id
            second_ref_param_path_id = second_ref.param_path_id
            second_ref_param_name = second_ref.param_name
            second_ref_socket_kind_value = second_ref.socket_kind.value
            second_shape_row = (
                second_ref_node_id,
                second_ref_param_path_id,
                second_ref_param_name,
                second_ref_socket_kind_value,
            )
            if second_shape_row < first_shape_row:
                first_ref, second_ref = second_ref, first_ref
                first_shape_row, second_shape_row = second_shape_row, first_shape_row
                first_ref_node_id, second_ref_node_id = (
                    second_ref_node_id,
                    first_ref_node_id,
                )
            if first_ref_node_id == second_ref_node_id:
                by_spell_id = {
                    first_ref_node_id: (
                        first_ref,
                        second_ref,
                    ),
                }
            else:
                by_spell_id = {
                    first_ref_node_id: (first_ref,),
                    second_ref_node_id: (second_ref,),
                }
            return (
                by_spell_id,
                (
                    first_shape_row,
                    second_shape_row,
                ),
            )

        by_spell_id: Dict[str, list[Any]] = {}
        socket_shape: list[Tuple[Any, ...]] = []
        ordered_rows: list[Tuple[Tuple[Any, ...], Any]] = []
        for socket_ref in override_map:
            node_id = socket_ref.node_id
            param_path_id = socket_ref.param_path_id
            param_name = socket_ref.param_name
            socket_kind_value = socket_ref.socket_kind.value
            ordered_rows.append(
                (
                    (
                        node_id,
                        param_path_id,
                        param_name,
                        socket_kind_value,
                    ),
                    socket_ref,
                )
            )
        ordered_rows.sort(key=itemgetter(0))
        current_spell_id: Optional[str] = None
        current_bucket: Optional[list[Any]] = None
        for shape_row, socket_ref in ordered_rows:
            node_id, _, _, _ = shape_row
            if node_id != current_spell_id:
                current_spell_id = node_id
                current_bucket = [socket_ref]
                by_spell_id[node_id] = current_bucket
            else:
                current_bucket.append(socket_ref)
            socket_shape.append(shape_row)

        return (
            {
                spell_id: tuple(refs)
                for spell_id, refs in by_spell_id.items()
            },
            tuple(socket_shape),
        )

    @staticmethod
    def _build_override_shape_key(
            *,
            plan_signature: Any,
            socket_shape: Tuple[Tuple[Any, ...], ...],
            root_positional_override: Optional[Sequence[Any]],
    ) -> Tuple[Any, ...]:
        """
        Build a deterministic specialization key for override executor cache.
        """
        positional_arity = -1
        if root_positional_override is not None:
            positional_arity = len(root_positional_override)
        return (
            plan_signature,
            socket_shape,
            positional_arity,
        )

    def _get_or_compile_override_executor(
            self,
            *,
            shape_key: Tuple[Any, ...],
            override_targets_by_spell_id: Dict[str, Tuple[Any, ...]],
            any_overrides_present: bool,
            path_registry: Optional[Any],
            plan_rows: Optional[Sequence[Dict[str, Any]]],
            root_spell_id: Optional[str],
            spell_lookup: Optional[Dict[str, Any]],
    ) -> Callable[..., Any]:
        """
        Resolve one cached override specialization executor or compile on miss.
        """
        override_specialization_cache = self._override_specialization_cache
        cached = override_specialization_cache.get(shape_key)
        if cached is not None:
            return cached

        compiled = compile_phase12_overrides_executor(
            execution_plan=None,
            override_targets_by_spell_id=override_targets_by_spell_id,
            any_overrides_present=any_overrides_present,
            path_registry=path_registry,
            plan_rows=plan_rows,
            root_spell_id=root_spell_id,
            spell_lookup=spell_lookup,
        )

        override_specialization_cache[shape_key] = compiled
        return compiled
