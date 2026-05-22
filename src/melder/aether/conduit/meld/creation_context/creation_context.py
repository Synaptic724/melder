from operator import itemgetter
from typing import (
    TYPE_CHECKING,
    Optional,
    Dict,
    Any,
    Callable,
    Tuple,
    Sequence,
    ClassVar,
)



from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.conduit.meld.creation_context.creation_context_codegen import (
    compile_creation_context_hooks_overrides_only_executor,
    compile_creation_context_hooks_no_overrides_executor,
    compile_creation_context_instance_overrides_only_executor,
    compile_creation_context_instance_no_overrides_executor,
)
from melder.aether.spellbook.spell_compiler.blueprints.phase12_overrides_executor import (
    compile_phase12_overrides_executor_code_object,
    compile_phase12_overrides_executor,
    _compile_phase12_overrides_executor_from_code_object_with_prefilter_cache,
    build_phase12_override_step_target_counts_from_rows,
    emit_phase12_overrides_executor_shape_source,
)
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
from melder.utilities.custom_exceptions.spell_space_scope_error import SpellSpaceScopeError
from melder.utilities.general_base.cleanable import Cleanable
if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell
    from melder.aether.conduit.creations.creations import Creations
    from melder.utilities.synchronization.creation_gate import CreationGate


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

        del self.plan_signature
        del self.path_registry
        del self.plan_rows
        del self.root_spell_id
        del self.spell_lookup
        del self.empty_shape_key
        del self.baseline_executor


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

    __melder_internal__: ClassVar[object] = _mrg.sentinel
    ROUTE_EXISTING_CREATION: ClassVar[str] = "existing_creation"
    ROUTE_SPELLSPACE: ClassVar[str] = "spellspace"
    ROUTE_UNIQUE_PER_CONDUIT: ClassVar[str] = "unique_per_conduit"
    ROUTE_MANY: ClassVar[str] = "many"
    ROUTE_SHARED: ClassVar[str] = "shared"

    __slots__ = Cleanable.__slots__ + [
        "_spell",
        "_spell_id",
        "_dynamic_environment",
        "_creation_gate",
        "_creation_gate_index_id",
        "_owner_creations",
        "_execute_hooks_overrides_compiled",
        "_execute_hooks_no_overrides_compiled",
        "_execute_no_hooks_overrides_compiled",
        "_execute_no_hooks_no_overrides_compiled",
        "_no_overrides_executor",
        "_override_patch_map_phase10",
        "_override_apply_with_socket_shape_prechecked_phase10",
        "_override_route_config_no_mutation",
        "_override_route_config_mutation",
        "_override_route_config_active",
        "_override_empty_shape_key",
        "_override_specialization_cache",
        "_override_executor_source_cache_by_plan_signature",
        "_override_executor_code_object_cache_by_plan_signature",
        "_override_prefilter_step_targets_cache",
        "_override_prefilter_path_metadata_cache",
        "_override_socket_shape_cache",
        "_override_last_socket_shape",
        "_override_last_root_positional_arity",
        "_override_last_executor",
    ]

    def __init__(
            self,
            *,
            spell: Spell,
            dynamic_environment: bool = False,
            creation_gate: Optional[CreationGate] = None,
            creation_gate_index_id: Optional[str] = None,
            resolve_route_key: str,
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
            dynamic_environment:
                True when the owning conduit runs in dynamic mode. Stored as
                context-level runtime mode metadata.
            creation_gate:
                Shared spell-index CreationGate used for dynamic-mode
                admission and ticket tracking during execute paths.
            creation_gate_index_id:
                Stable spell-index id used for gate diagnostics.
            resolve_route_key:
                Preselected existence route key from `CreationContextBuilder`.
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
        self._spell: Spell = spell
        self._spell_id: str = spell.spell_id
        self._dynamic_environment: bool = bool(dynamic_environment)
        if self._dynamic_environment and creation_gate is None:
            raise ValueError(
                "creation_gate cannot be None when dynamic_environment is True."
            )
        self._creation_gate: Optional[CreationGate] = creation_gate
        self._creation_gate_index_id: Optional[str] = creation_gate_index_id
        self._owner_creations: Any = spell._owner_creations
        self._no_overrides_executor: Optional[Callable[..., Any]] = (
            no_overrides_executor
        )
        self._override_patch_map_phase10: Optional[Any] = (
            override_patch_map_phase10
        )
        self._override_apply_with_socket_shape_prechecked_phase10: Optional[
            Callable[..., Any]
        ]
        if override_patch_map_phase10 is None:
            self._override_apply_with_socket_shape_prechecked_phase10 = None
        else:
            self._override_apply_with_socket_shape_prechecked_phase10 = (
                override_patch_map_phase10._apply_with_socket_shape_prechecked
            )
        self._override_route_config_no_mutation: Optional[OverrideRouteConfig] = (
            override_route_config_no_mutation
        )
        self._override_route_config_mutation: Optional[OverrideRouteConfig] = (
            override_route_config_mutation
        )
        mutation_override_enabled = override_route_config_mutation is not None
        if mutation_override_enabled:
            self._override_route_config_active: Optional[OverrideRouteConfig] = (
                override_route_config_mutation
            )
        else:
            self._override_route_config_active = override_route_config_no_mutation
        override_route_config_active = self._override_route_config_active
        if override_route_config_active is not None:
            self._override_empty_shape_key: Optional[Tuple[Any, ...]] = (
                override_route_config_active.plan_signature,
                (),
                -1,
            )
        else:
            self._override_empty_shape_key = None
        self._override_specialization_cache: Dict[
            Tuple[Any, ...],
            Callable[..., Any],
        ] = {}
        self._override_executor_source_cache_by_plan_signature: Dict[Tuple[Any, ...], str] = {}
        self._override_executor_code_object_cache_by_plan_signature: Dict[
            Tuple[Any, ...],
            Any,
        ] = {}
        self._override_prefilter_step_targets_cache: Dict[
            Tuple[Any, ...],
            Tuple[Tuple[Any, ...], ...],
        ] = {}
        self._override_prefilter_path_metadata_cache: Dict[Any, Tuple[Any, Any]] = {}
        self._override_socket_shape_cache: Dict[
            Tuple[Any, ...],
            Tuple[Tuple[Any, ...], ...],
        ] = {}
        self._override_last_socket_shape: Optional[Tuple[Tuple[Any, ...], ...]] = None
        self._override_last_root_positional_arity: int = -2
        self._override_last_executor: Optional[Callable[..., Any]] = None
        self._seed_baseline_override_executor(override_route_config_no_mutation)
        self._seed_baseline_override_executor(override_route_config_mutation)
        self._execute_hooks_overrides_compiled: Callable[..., tuple[Any, bool]] = (
            compile_creation_context_hooks_overrides_only_executor(
                resolve_route_key=resolve_route_key,
                spell=spell,
                spell_id=self._spell_id,
                owner_creations=self._owner_creations,
                no_overrides_executor=self._no_overrides_executor,
                execute_with_overrides=self._execute_with_overrides,
                meld_execution_error_type=MeldExecutionError,
                spell_space_scope_error_type=SpellSpaceScopeError,
            )
        )
        if mutation_override_enabled:
            self._execute_hooks_no_overrides_compiled: Callable[..., tuple[Any, bool]] = (
                self._execute_hooks_overrides_compiled
            )
        else:
            self._execute_hooks_no_overrides_compiled = (
                compile_creation_context_hooks_no_overrides_executor(
                    resolve_route_key=resolve_route_key,
                    fast_transient_no_overrides_enabled=(
                        resolve_route_key == self.ROUTE_MANY
                        and fast_transient_no_overrides_enabled
                    ),
                    spell=spell,
                    spell_id=self._spell_id,
                    owner_creations=self._owner_creations,
                    no_overrides_executor=self._no_overrides_executor,
                    spell_space_scope_error_type=SpellSpaceScopeError,
                )
            )
        self._execute_no_hooks_overrides_compiled: Callable[..., Any] = (
            compile_creation_context_instance_overrides_only_executor(
                resolve_route_key=resolve_route_key,
                spell=spell,
                spell_id=self._spell_id,
                owner_creations=self._owner_creations,
                no_overrides_executor=self._no_overrides_executor,
                execute_with_overrides=self._execute_with_overrides,
                meld_execution_error_type=MeldExecutionError,
                spell_space_scope_error_type=SpellSpaceScopeError,
            )
        )
        if mutation_override_enabled:
            self._execute_no_hooks_no_overrides_compiled: Callable[..., Any] = (
                self._execute_no_hooks_overrides_compiled
            )
        else:
            self._execute_no_hooks_no_overrides_compiled = (
                compile_creation_context_instance_no_overrides_executor(
                    resolve_route_key=resolve_route_key,
                    fast_transient_no_overrides_enabled=(
                        resolve_route_key == self.ROUTE_MANY
                        and fast_transient_no_overrides_enabled
                    ),
                    spell=spell,
                    spell_id=self._spell_id,
                    owner_creations=self._owner_creations,
                    no_overrides_executor=self._no_overrides_executor,
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
        override_executor_source_cache = (
            self._override_executor_source_cache_by_plan_signature
        )
        override_executor_source_cache.clear()
        override_executor_code_object_cache = (
            self._override_executor_code_object_cache_by_plan_signature
        )
        override_executor_code_object_cache.clear()
        override_prefilter_step_targets_cache = self._override_prefilter_step_targets_cache
        override_prefilter_step_targets_cache.clear()
        override_prefilter_path_metadata_cache = self._override_prefilter_path_metadata_cache
        override_prefilter_path_metadata_cache.clear()
        override_socket_shape_cache = self._override_socket_shape_cache
        override_socket_shape_cache.clear()
        self._override_last_root_positional_arity = -2

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

        del self._override_last_executor
        del self._override_last_socket_shape
        del self._spell
        del self._spell_id
        del self._dynamic_environment
        del self._creation_gate
        del self._creation_gate_index_id
        del self._owner_creations
        del self._execute_hooks_overrides_compiled
        del self._execute_hooks_no_overrides_compiled
        del self._execute_no_hooks_overrides_compiled
        del self._execute_no_hooks_no_overrides_compiled
        del self._no_overrides_executor
        del self._override_patch_map_phase10
        del self._override_apply_with_socket_shape_prechecked_phase10
        del self._override_route_config_no_mutation
        del self._override_route_config_mutation
        del self._override_route_config_active
        del self._override_empty_shape_key
        del self._override_specialization_cache
        del self._override_executor_source_cache_by_plan_signature
        del self._override_executor_code_object_cache_by_plan_signature
        del self._override_prefilter_step_targets_cache
        del self._override_prefilter_path_metadata_cache
        del self._override_socket_shape_cache
        del self._override_last_root_positional_arity

    def execute(
            self,
            caller_creations: Creations,
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

        Dynamic gate policy:
            - Automatic mode bypasses gate checks.
            - Dynamic mode mirrors Conduit.meld gate admission:
              fail-fast on terminal close, wait while disabled, then
              register/unregister one ticket around execution.

        Raises:
            RuntimeError:
                If dynamic-mode spell-index gate is terminally closed.
        """
        if not self._dynamic_environment:
            if overrides is None:
                execute_hooks_no_overrides_compiled = (
                    self._execute_hooks_no_overrides_compiled
                )
                return execute_hooks_no_overrides_compiled(caller_creations)
            execute_hooks_overrides_compiled = self._execute_hooks_overrides_compiled
            return execute_hooks_overrides_compiled(caller_creations, overrides)

        creation_gate = self._creation_gate
        index_id = self._creation_gate_index_id
        if creation_gate is None:
            raise RuntimeError(
                f"CreationGate is unavailable for spell index '{index_id}'."
            )
        if creation_gate.is_closed():
            raise RuntimeError(
                f"CreationGate is closed for spell index '{index_id}'."
            )
        if not creation_gate.enabled:
            creation_gate.wait()
            if creation_gate.is_closed():
                raise RuntimeError(
                    f"CreationGate is closed for spell index '{index_id}'."
                )
        try:
            creation_gate.register_ticket()
            if overrides is None:
                execute_hooks_no_overrides_compiled = (
                    self._execute_hooks_no_overrides_compiled
                )
                return execute_hooks_no_overrides_compiled(caller_creations)
            execute_hooks_overrides_compiled = self._execute_hooks_overrides_compiled
            return execute_hooks_overrides_compiled(caller_creations, overrides)
        finally:
            creation_gate.unregister_ticket()

    def execute_no_hooks(
            self,
            caller_creations: Creations,
            overrides: Optional[dict[str, Any]] = None,
    ) -> Any:
        """
        Execute no-hooks lane through dedicated no-hooks runtime doors.

        Contract:
            - `overrides is None` uses the no-overrides compiled door.
            - Override payloads route through the no-hooks compiled override door.
            - Caller must supply frontdoor-normalized overrides from Meld.

        Dynamic gate policy:
            - Automatic mode bypasses gate checks.
            - Dynamic mode mirrors Conduit.meld gate admission:
              fail-fast on terminal close, wait while disabled, then
              register/unregister one ticket around execution.

        Raises:
            RuntimeError:
                If dynamic-mode spell-index gate is terminally closed.
        """
        if not self._dynamic_environment:
            if overrides is None:
                execute_no_hooks_no_overrides_compiled = (
                    self._execute_no_hooks_no_overrides_compiled
                )
                return execute_no_hooks_no_overrides_compiled(caller_creations)
            execute_no_hooks_overrides_compiled = (
                self._execute_no_hooks_overrides_compiled
            )
            return execute_no_hooks_overrides_compiled(caller_creations, overrides)

        creation_gate = self._creation_gate
        index_id = self._creation_gate_index_id
        if creation_gate is None:
            raise RuntimeError(
                f"CreationGate is unavailable for spell index '{index_id}'."
            )
        if creation_gate.is_closed():
            raise RuntimeError(
                f"CreationGate is closed for spell index '{index_id}'."
            )
        if not creation_gate.enabled:
            creation_gate.wait()
            if creation_gate.is_closed():
                raise RuntimeError(
                    f"CreationGate is closed for spell index '{index_id}'."
                )
        try:
            creation_gate.register_ticket()
            if overrides is None:
                execute_no_hooks_no_overrides_compiled = (
                    self._execute_no_hooks_no_overrides_compiled
                )
                return execute_no_hooks_no_overrides_compiled(caller_creations)
            execute_no_hooks_overrides_compiled = (
                self._execute_no_hooks_overrides_compiled
            )
            return execute_no_hooks_overrides_compiled(caller_creations, overrides)
        finally:
            creation_gate.unregister_ticket()

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
    # Override route runtime
    # ----------------------------------------------------------------------

    def _execute_with_overrides(
            self,
            caller_creations: Creations,
            overrides: Optional[dict[str, Any]],
            caller_creations_lock_held: bool,
    ) -> Any:
        """
        Execute one override-bearing meld call through the specialization
        pipeline.

        This is the hot-path entry for override execution after Meld has already
        normalized the frontdoor payload. The method:

        - separates root positional overrides from targeted socket overrides
        - uses the Phase 10 patch map to turn targeted payloads into an
          override map plus deterministic socket shape
        - reuses the most recent executor when the socket shape and root
          positional arity are identical
        - otherwise resolves or compiles a specialized Phase 12 executor keyed
          by the current override shape

        The override payload values themselves do not participate in executor
        cache identity. Only the structural shape matters for specialization
        reuse.
        """
        spell = self._spell
        override_route_config = self._override_route_config_active
        owner_creations = self._owner_creations
        if override_route_config is None:
            raise RuntimeError(
                "Override route configuration is unavailable for this spell."
            )
        spell_id = spell.spell_index.current or spell.spell_id

        override_payload = overrides
        root_positional_override: Optional[Sequence[Any]] = None
        override_map: Dict[Any, Any] = {}
        socket_shape: Tuple[Tuple[Any, ...], ...] = ()
        if override_payload is None:
            baseline_executor = override_route_config.baseline_executor
            if baseline_executor is not None:
                return baseline_executor(
                    caller_creations,
                    override_map,
                    root_positional_override,
                    owner_creations=owner_creations,
                    caller_creations_lock_held=caller_creations_lock_held,
                )
            shape_key = self._override_empty_shape_key
            if shape_key is None:
                raise RuntimeError(
                    "Empty override shape key is unavailable for this spell."
                )
            empty_payload_executor = self._get_or_compile_override_executor(
                shape_key=shape_key,
                override_targets_by_spell_id={},
                any_overrides_present=False,
                path_registry=override_route_config.path_registry,
                plan_rows=override_route_config.plan_rows,
                root_spell_id=override_route_config.root_spell_id,
                spell_lookup=override_route_config.spell_lookup,
            )
            return empty_payload_executor(
                caller_creations,
                override_map,
                root_positional_override,
                owner_creations=owner_creations,
                caller_creations_lock_held=caller_creations_lock_held,
            )
        if override_payload:
            if "__args__" in override_payload:
                target_payload, root_positional_override = self._split_override_payload(
                    spell=spell,
                    override_payload=override_payload,
                )
            else:
                target_payload = override_payload
            if target_payload:
                override_apply_with_socket_shape_prechecked_phase10 = (
                    self._override_apply_with_socket_shape_prechecked_phase10
                )
                try:
                    if override_apply_with_socket_shape_prechecked_phase10 is None:
                        raise RuntimeError(
                            "Phase 10 override patch map is required for meld execution."
                        )
                    (
                        override_map,
                        socket_shape,
                    ) = override_apply_with_socket_shape_prechecked_phase10(
                        spell_override=target_payload,
                    )
                except MeldExecutionError:
                    raise
                except Exception as exc:
                    raise MeldExecutionError(
                        spell_id=spell_id,
                        spell_name=spell.spell_name,
                        message=(
                            "Failed to apply overrides."
                        ),
                        inner=exc,
                    ) from exc

        plan_signature = override_route_config.plan_signature
        if root_positional_override is None:
            root_positional_arity = -1
        else:
            root_positional_arity = len(root_positional_override)
        executor: Optional[Callable[..., Any]]
        if (
                socket_shape is self._override_last_socket_shape
                and root_positional_arity == self._override_last_root_positional_arity
        ):
            executor = self._override_last_executor
        else:
            executor = None
        if executor is None:
            shape_key = (
                plan_signature,
                socket_shape,
                root_positional_arity,
            )
            override_specialization_cache = self._override_specialization_cache
            executor = override_specialization_cache.get(shape_key)
            if executor is None:
                if override_map:
                    override_targets_by_spell_id = (
                        self._collect_override_targets_from_socket_shape(
                            override_map=override_map,
                            socket_shape=socket_shape,
                        )
                    )
                else:
                    override_targets_by_spell_id = {}
                any_overrides_present = overrides is not None
                prefilter_cache_key = (
                    plan_signature,
                    socket_shape,
                )
                executor = self._get_or_compile_override_executor(
                    shape_key=shape_key,
                    override_targets_by_spell_id=override_targets_by_spell_id,
                    any_overrides_present=any_overrides_present,
                    path_registry=override_route_config.path_registry,
                    plan_rows=override_route_config.plan_rows,
                    root_spell_id=override_route_config.root_spell_id,
                    spell_lookup=override_route_config.spell_lookup,
                    prefilter_cache_key=prefilter_cache_key,
                )
            self._override_last_socket_shape = socket_shape
            self._override_last_root_positional_arity = root_positional_arity
            self._override_last_executor = executor
        if executor is None:
            raise RuntimeError("Override executor resolution failed.")

        result = executor(
            caller_creations,
            override_map,
            root_positional_override,
            owner_creations=owner_creations,
            caller_creations_lock_held=caller_creations_lock_held,
        )
        return result

    @staticmethod
    def _split_override_payload(
            *,
            spell: Spell,
            override_payload: Dict[str, Any],
    ) -> Tuple[Dict[str, Any], Optional[Sequence[Any]]]:
        """
        Separate root positional overrides from targeted socket overrides.

        `__args__` is the reserved root-level positional override carrier. This
        helper removes that payload from the keyed override mapping and returns
        the two channels separately so the later specialization path can reason
        about:

        - targeted socket override shape
        - root positional arity

        without conflating the two.
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
                spell_id=spell.spell_index.current or spell.spell_id,
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

    def _collect_override_socket_shape_cached(
            self,
            *,
            override_map: Dict[Any, Any],
    ) -> Tuple[Tuple[Any, ...], ...]:
        """
        Return deterministic socket-shape rows with context-local memoization.

        Purpose:
            Reuse shape tuples for repeated override socket sets so cached
            specialization lookup avoids rebuilding shape rows on hot paths.

        Contract:
            - Output semantics match `_collect_override_socket_shape(...)`.
            - Uses per-context cache keys derived from override socket refs.
            - Returns an empty tuple for empty override maps.
        """
        if not override_map:
            return ()

        override_map_size = len(override_map)
        if override_map_size == 1:
            socket_ref = next(iter(override_map))
            cache_key: Tuple[Any, ...] = ("single", socket_ref)
        elif override_map_size == 2:
            refs_iter = iter(override_map)
            first_ref = next(refs_iter)
            second_ref = next(refs_iter)
            first_shape_row = (
                first_ref.node_id,
                first_ref.param_path_id,
                first_ref.param_name,
                first_ref.socket_kind.value,
            )
            second_shape_row = (
                second_ref.node_id,
                second_ref.param_path_id,
                second_ref.param_name,
                second_ref.socket_kind.value,
            )
            if second_shape_row < first_shape_row:
                first_ref, second_ref = second_ref, first_ref
            cache_key = (
                "double",
                first_ref,
                second_ref,
            )
        else:
            cache_key = (
                "many",
                frozenset(override_map),
            )

        override_socket_shape_cache = self._override_socket_shape_cache
        cached_socket_shape = override_socket_shape_cache.get(cache_key)
        if cached_socket_shape is not None:
            return cached_socket_shape

        socket_shape = self._collect_override_socket_shape(
            override_map=override_map,
        )
        override_socket_shape_cache[cache_key] = socket_shape
        return socket_shape

    @staticmethod
    def _collect_override_socket_shape(
            *,
            override_map: Dict[Any, Any],
    ) -> Tuple[Tuple[Any, ...], ...]:
        """
        Build deterministic socket-shape rows without per-spell grouping.

        Purpose:
            Support override specialization cache lookup with lower per-call
            preprocessing overhead on cache-hit paths.

        Contract:
            - Output ordering matches
              `_collect_override_targets_and_socket_shape(...)[1]`.
            - Does not allocate spell-id grouping buckets.
            - Uses one/two-socket fast paths to avoid sort overhead.
        """
        if not override_map:
            return ()
        if len(override_map) == 1:
            socket_ref = next(iter(override_map))
            return (
                (
                    socket_ref.node_id,
                    socket_ref.param_path_id,
                    socket_ref.param_name,
                    socket_ref.socket_kind.value,
                ),
            )
        if len(override_map) == 2:
            refs_iter = iter(override_map)
            first_ref = next(refs_iter)
            second_ref = next(refs_iter)
            first_shape_row = (
                first_ref.node_id,
                first_ref.param_path_id,
                first_ref.param_name,
                first_ref.socket_kind.value,
            )
            second_shape_row = (
                second_ref.node_id,
                second_ref.param_path_id,
                second_ref.param_name,
                second_ref.socket_kind.value,
            )
            if second_shape_row < first_shape_row:
                return (
                    second_shape_row,
                    first_shape_row,
                )
            return (
                first_shape_row,
                second_shape_row,
            )

        socket_shape: list[Tuple[Any, ...]] = []
        for socket_ref in override_map:
            socket_shape.append(
                (
                    socket_ref.node_id,
                    socket_ref.param_path_id,
                    socket_ref.param_name,
                    socket_ref.socket_kind.value,
                )
            )
        socket_shape.sort()
        return tuple(socket_shape)

    @staticmethod
    def _collect_override_targets_from_socket_shape(
            *,
            override_map: Dict[Any, Any],
            socket_shape: Tuple[Tuple[Any, ...], ...],
    ) -> Dict[str, Tuple[Any, ...]]:
        """
        Group override targets by spell id from precomputed socket-shape rows.

        Purpose:
            Reuse the existing shape-key preprocessing output on cache-miss paths
            so grouped-target construction avoids a second sort workflow.

        Contract:
            - `socket_shape` must be the deterministic output from
              `_collect_override_socket_shape(override_map=...)`.
            - Group ordering follows `socket_shape` row order.
            - Returns an empty mapping when no override sockets are present.
        """
        if not socket_shape:
            return {}

        shape_row_to_socket_ref: Dict[Tuple[Any, ...], Any] = {}
        for socket_ref in override_map:
            shape_row_to_socket_ref[
                (
                    socket_ref.node_id,
                    socket_ref.param_path_id,
                    socket_ref.param_name,
                    socket_ref.socket_kind.value,
                )
            ] = socket_ref

        by_spell_id: Dict[str, list[Any]] = {}
        current_spell_id: Optional[str] = None
        current_bucket: Optional[list[Any]] = None
        for shape_row in socket_shape:
            node_id, _, _, _ = shape_row
            socket_ref = shape_row_to_socket_ref[shape_row]
            if node_id != current_spell_id:
                current_spell_id = node_id
                current_bucket = [socket_ref]
                by_spell_id[node_id] = current_bucket
            else:
                if current_bucket is None:
                    raise RuntimeError(
                        "Override target bucket was not initialized."
                    )
                current_bucket.append(socket_ref)

        return {
            spell_id: tuple(refs)
            for spell_id, refs in by_spell_id.items()
        }

    @staticmethod
    def _collect_override_targets_and_socket_shape(
            *,
            override_map: Dict[Any, Any],
    ) -> Tuple[Dict[str, Tuple[Any, ...]], Tuple[Tuple[Any, ...], ...]]:
        """
        Build both grouped override targets and the deterministic socket-shape
        tuple in one pass.

        This is the full preprocessing path used when the caller needs both:

        - per-spell grouped override targets for executor compilation, and
        - a stable socket-shape tuple for specialization identity

        The helper keeps one- and two-socket fast paths so small override sets
        avoid the heavier generic ordering workflow.
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
                pair_by_spell_id: Dict[str, Tuple[Any, ...]] = {
                    first_ref_node_id: (
                        first_ref,
                        second_ref,
                    ),
                }
            else:
                pair_by_spell_id = {
                    first_ref_node_id: (first_ref,),
                    second_ref_node_id: (second_ref,),
                }
            return (
                pair_by_spell_id,
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
                if current_bucket is None:
                    raise RuntimeError(
                        "Override target bucket was not initialized."
                    )
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
        Build the specialization-cache key for one override call shape.

        The key intentionally captures only structural information needed to
        decide executor reuse:

        - the Phase 11 plan signature
        - the deterministic socket-shape tuple
        - the arity of root positional overrides

        It does not encode concrete override values, because those values are
        runtime data passed to the compiled executor, not part of specialization
        identity.
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
            prefilter_cache_key: Optional[Tuple[Any, ...]] = None,
    ) -> Callable[..., Any]:
        """
        Return a cached override specialization executor, compiling it on miss.

        This is the main specialization-cache lookup for override execution.
        Callers supply the already-derived structural shape and the grouped
        targets for the current override call. If a matching executor is not
        cached yet, the method compiles one using either the spell's plan rows
        or the generic Phase 12 fallback path.
        """
        override_specialization_cache = self._override_specialization_cache
        cached = override_specialization_cache.get(shape_key)
        if cached is not None:
            return cached

        if plan_rows is not None:
            compiled = self._compile_override_executor_from_plan_rows(
                shape_key=shape_key,
                override_targets_by_spell_id=override_targets_by_spell_id,
                any_overrides_present=any_overrides_present,
                path_registry=path_registry,
                plan_rows=plan_rows,
                root_spell_id=root_spell_id,
                spell_lookup=spell_lookup,
                prefilter_cache_key=prefilter_cache_key,
            )
        else:
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

    def _compile_override_executor_from_plan_rows(
            self,
            *,
            shape_key: Tuple[Any, ...],
            override_targets_by_spell_id: Dict[str, Tuple[Any, ...]],
            any_overrides_present: bool,
            path_registry: Optional[Any],
            plan_rows: Sequence[Dict[str, Any]],
            root_spell_id: Optional[str],
            spell_lookup: Optional[Dict[str, Any]],
            prefilter_cache_key: Optional[Tuple[Any, ...]],
    ) -> Callable[..., Any]:
        """
        Compile one override specialization using reusable shape artifacts.

        Contract:
            - Reuses emitted source and compiled code objects per shape key.
            - Binds per-shape namespace constants for each specialization compile.
            - Preserves runtime behavior of override executor compilation.
        """
        targeted_spell_ids = tuple(sorted(override_targets_by_spell_id.keys()))
        override_target_counts_by_spell_id = tuple(
            sorted(
                (
                    spell_id,
                    len(targets),
                )
                for spell_id, targets in override_targets_by_spell_id.items()
                if targets
            )
        )
        override_target_counts_by_step = (
            build_phase12_override_step_target_counts_from_rows(
                plan_rows=plan_rows,
                override_targets_by_spell_id=override_targets_by_spell_id,
                path_registry=path_registry,
                prefilter_step_targets_cache=self._override_prefilter_step_targets_cache,
                prefilter_cache_key=prefilter_cache_key,
                prefilter_path_metadata_cache=self._override_prefilter_path_metadata_cache,
            )
        )
        has_root_positional_override = shape_key[2] >= 0
        source = self._get_or_build_override_executor_source(
            source_cache_key=shape_key,
            plan_rows=plan_rows,
            root_spell_id=root_spell_id,
            spell_lookup=spell_lookup,
            override_targeted_spell_ids=targeted_spell_ids,
            override_target_counts_by_spell_id=override_target_counts_by_spell_id,
            override_target_counts_by_step=override_target_counts_by_step,
            has_root_positional_override=has_root_positional_override,
        )
        code_object = self._get_or_build_override_executor_code_object(
            source_cache_key=shape_key,
            source=source,
        )
        return _compile_phase12_overrides_executor_from_code_object_with_prefilter_cache(
            code_object=code_object,
            execution_plan=None,
            override_targets_by_spell_id=override_targets_by_spell_id,
            any_overrides_present=any_overrides_present,
            path_registry=path_registry,
            plan_rows=plan_rows,
            root_spell_id=root_spell_id,
            spell_lookup=spell_lookup,
            prefilter_step_targets_cache=self._override_prefilter_step_targets_cache,
            prefilter_cache_key=prefilter_cache_key,
            prefilter_path_metadata_cache=self._override_prefilter_path_metadata_cache,
        )

    def _get_or_build_override_executor_source(
            self,
            *,
            source_cache_key: Tuple[Any, ...],
            plan_rows: Sequence[Dict[str, Any]],
            root_spell_id: Optional[str],
            spell_lookup: Optional[Dict[str, Any]],
            override_targeted_spell_ids: Tuple[str, ...],
            override_target_counts_by_spell_id: Tuple[Tuple[str, int], ...],
            override_target_counts_by_step: Tuple[int, ...],
            has_root_positional_override: bool,
    ) -> str:
        """
        Return the emitted Python source for one override specialization shape.

        Source text is cached separately from compiled code objects so later
        specialization work can reuse the emitted shape-specific program text
        without regenerating it from plan rows each time.
        """
        override_executor_source_cache = (
            self._override_executor_source_cache_by_plan_signature
        )
        cached_source = override_executor_source_cache.get(source_cache_key)
        if cached_source is not None:
            return cached_source
        emitted_source = emit_phase12_overrides_executor_shape_source(
            plan_rows=plan_rows,
            root_spell_id=root_spell_id,
            spell_lookup=spell_lookup,
            override_targeted_spell_ids=override_targeted_spell_ids,
            override_target_counts_by_spell_id=override_target_counts_by_spell_id,
            override_target_counts_by_step=override_target_counts_by_step,
            has_root_positional_override=has_root_positional_override,
        )
        override_executor_source_cache[source_cache_key] = emitted_source
        return emitted_source

    def _get_or_build_override_executor_code_object(
            self,
            *,
            source_cache_key: Tuple[Any, ...],
            source: str,
    ) -> Any:
        """
        Return the compiled code object for one specialization shape.

        This is the second stage of specialization caching: emitted source is
        compiled once per shape key, then reused by later executor builds that
        need to bind fresh runtime namespaces against the same program body.
        """
        override_executor_code_object_cache = (
            self._override_executor_code_object_cache_by_plan_signature
        )
        cached_code_object = override_executor_code_object_cache.get(
            source_cache_key,
        )
        if cached_code_object is not None:
            return cached_code_object
        compiled_code_object = compile_phase12_overrides_executor_code_object(
            source=source,
        )
        override_executor_code_object_cache[source_cache_key] = (
            compiled_code_object
        )
        return compiled_code_object
