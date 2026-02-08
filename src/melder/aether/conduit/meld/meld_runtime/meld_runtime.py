from collections import deque
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.conduit.meld.meld_context.meld_context import MeldContext
from melder.spellbook.spell_crafter.blueprints.patch_maps import (
    apply_phase10_override_payload,
)
from melder.spellbook.spell_crafter.blueprints.phase12_overrides_executor import (
    compile_phase12_overrides_executor,
)
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.interfaces import ISpell


class MeldRuntime(Cleanable):
    """
    Execute meld calls through compiled Phase 12 codegen artifacts.

    Purpose:
        Provide the execution boundary between `Meld` and spell-scoped Phase 12
        executors compiled by SpellCrafter, without invoking legacy engine paths.

    Contract:
        - Executes no-overrides calls through `phase12_no_overrides_executor`.
        - Executes override calls through specialization executors compiled from
          the Phase 11 override execution IR rows.
        - Keeps override specialization caches bounded per spell.
        - Mutation-bearing spells route through override specialization executors.
        - Trusts upstream Meld/Spellbook validation and uses direct artifact
          access on execution paths.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = (
        "_override_specialization_cache",
        "_override_specialization_order",
        "_max_override_specializations_per_spell",
    )

    def __init__(self) -> None:
        """
        Initialize a codegen-only meld runtime.

        Contract:
            - Runtime holds no engine or frame pools.
            - Runtime owns a bounded per-spell override specialization cache.
            - All per-call state is supplied through MeldContext.
        """
        super().__init__()
        self._override_specialization_cache: Dict[str, Dict[Tuple[Any, ...], Callable[..., Any]]] = {}
        self._override_specialization_order: Dict[str, deque[Tuple[Any, ...]]] = {}
        self._max_override_specializations_per_spell: int = 64

    def execute_no_overrides_fast_transient(
            self,
            *,
            spell: ISpell
    ) -> Any:
        """
        Execute a transient no-overrides spell through Phase 12 executor.

        Contract:
            - Uses the precompiled Phase 12 transient executor directly.
            - Requires a compiled Phase 12 executor.
            - Caller must route only no-overrides/no-mutation spells here.
        """
        try:
            return spell._crafter.phase12_no_overrides_executor(None)
        except MeldExecutionError:
            raise
        except Exception as exc:
            raise MeldExecutionError(
                spell_id=spell.spell_index.current,
                spell_name=spell.spell_name,
                message="Phase 12 transient executor failed.",
                inner=exc,
            ) from exc

    def execute(self, context: MeldContext) -> Any:
        """
        Execute one meld call through the appropriate Phase 12 executor route.

        Contract:
            - `context` and `context.root_spell` are required call contracts.
            - No-overrides calls use the precompiled no-overrides executor.
            - Override calls use spell-scoped specialization executors.
            - Mutation-bearing spells use override specialization routing even
              when no per-call override payload is present.
            - Trusts upstream artifact preparation and uses direct contract access.
            - Returns the constructed root instance.
        """
        spell = context.root_spell
        overrides = context.overrides
        has_mutation_override = spell.has_mutation_override
        if overrides or has_mutation_override:
            return self._execute_with_overrides(
                context=context,
                spell=spell,
            )
        return self._execute_no_overrides(
            context=context,
            spell=spell,
        )

    def cleanup(self) -> None:
        """
        Deterministically tear down runtime-owned caches.

        Contract:
            - Idempotent.
            - Clears all spell-scoped override specialization entries.
        """
        if self._cleaned:
            return
        override_specialization_cache = self._override_specialization_cache
        override_specialization_order = self._override_specialization_order
        for cache in override_specialization_cache.values():
            cache.clear()
        for order in override_specialization_order.values():
            order.clear()
        override_specialization_cache.clear()
        override_specialization_order.clear()
        self._override_specialization_cache = None
        self._override_specialization_order = None
        self._max_override_specializations_per_spell = None
        self._cleaned = True

    def _execute_no_overrides(
            self,
            *,
            context: MeldContext,
            spell: ISpell,
    ) -> Any:
        """
        Execute a no-overrides meld call through the compiled Phase 12 executor.

        Contract:
            - Requires `phase12_no_overrides_executor`.
            - Wraps unexpected executor exceptions in MeldExecutionError.
        """
        executor = spell._crafter.phase12_no_overrides_executor
        try:
            result = executor(context)
        except MeldExecutionError:
            raise
        except Exception as exc:
            raise MeldExecutionError(
                spell_id=spell.spell_index.current,
                spell_name=spell.spell_name,
                message="Phase 12 no-overrides executor failed.",
                inner=exc,
            ) from exc
        self._raise_on_missing_factory_result(
            spell=spell,
            result=result,
            message=(
                "Phase 12 no-overrides executor returned None for a "
                "factory-style spell."
            ),
        )
        return result

    def _execute_with_overrides(
            self,
            *,
            context: MeldContext,
            spell: ISpell,
    ) -> Any:
        """
        Execute an override-bearing meld call through specialization routing.

        Contract:
            - Applies Phase 10 override patch maps to normalize TargetSpec keys.
            - Requires Phase11 override execution IR rows for specialization
              compile and shape-key signature construction.
            - Selects/compiles a spell-scoped specialization by override shape.
            - Uses mutation-aware plan artifacts when the root spell carries
              mutation overrides.
            - Never falls back to engine execution.
        """
        crafter = spell._crafter
        is_mutation_route = spell.has_mutation_override
        execution_ir_key = "overrides_with_mutations" if is_mutation_route else "overrides"
        override_execution_ir_payload = self._resolve_override_execution_ir_payload(
            crafter=crafter,
            execution_ir_key=execution_ir_key,
        )

        override_payload = context.overrides
        root_positional_override: Optional[Sequence[Any]] = None
        override_map: Dict[Any, Any] = {}
        if override_payload:
            target_payload, root_positional_override = self._split_override_payload(
                spell=spell,
                override_payload=override_payload,
            )
            if target_payload:
                try:
                    override_map = apply_phase10_override_payload(
                        override_patch_map=crafter.override_patch_map_phase10,
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

        (
            override_targets_by_spell_id,
            socket_shape,
        ) = self._collect_override_targets_and_socket_shape(
            override_map=override_map,
        )
        try:
            plan_signature = self._build_override_plan_signature_from_ir_payload(
                override_execution_ir_payload=override_execution_ir_payload,
            )
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
        executor = self._get_or_compile_override_executor(
            spell=spell,
            shape_key=shape_key,
            execution_plan=None,
            override_targets_by_spell_id=override_targets_by_spell_id,
            any_overrides_present=bool(override_payload),
            path_registry=crafter.root_blueprint_phase5.path_registry,
            plan_rows=override_execution_ir_payload["steps_rows"],
            root_spell_id=override_execution_ir_payload["root_spell_id"],
            spell_lookup=spell._spellbook._spell_id_pool,
        )

        result = executor(
            context,
            override_map,
            root_positional_override,
        )

        self._raise_on_missing_factory_result(
            spell=spell,
            result=result,
            message=(
                "Phase 12 override specialization executor returned None for a "
                "factory-style spell."
            ),
        )
        return result

    @staticmethod
    def _split_override_payload(
            *,
            spell: ISpell,
            override_payload: Dict[str, Any],
    ) -> Tuple[Dict[str, Any], Optional[Sequence[Any]]]:
        """
        Split root positional overrides from TargetSpec override payloads.

        Contract:
            - Removes `__args__` from the payload passed into patch-map apply.
            - Validates that `__args__` is list/tuple when provided.
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
        if len(override_payload) == 1:
            return {}, normalized_root_args
        if len(override_payload) == 2:
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
        Collect grouped override targets and socket-shape tuples in one pass.

        Contract:
            - Performs a single deterministic sort over socket refs.
            - Uses dedicated no-sort fast paths for one- and two-socket payloads.
            - Groups refs by `socket_ref.node_id`.
            - Emits socket-shape tuples in stable sorted order.
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
        ordered_refs = sorted(
            override_map.keys(),
            key=lambda ref: (
                ref.node_id,
                ref.param_path_id,
                ref.param_name,
                ref.socket_kind.value,
            ),
        )
        current_spell_id: Optional[str] = None
        current_bucket: Optional[list[Any]] = None
        for socket_ref in ordered_refs:
            node_id = socket_ref.node_id
            param_path_id = socket_ref.param_path_id
            param_name = socket_ref.param_name
            socket_kind_value = socket_ref.socket_kind.value
            if node_id != current_spell_id:
                current_spell_id = node_id
                current_bucket = [socket_ref]
                by_spell_id[node_id] = current_bucket
            else:
                current_bucket.append(socket_ref)
            socket_shape.append(
                (
                    node_id,
                    param_path_id,
                    param_name,
                    socket_kind_value,
                )
            )

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
        Build a stable override-shape key for specialization cache lookup.

        Contract:
            - Includes deterministic execution-plan signature to avoid stale-plan
              collisions without relying on object identity.
            - Includes deterministic socket-target tuples.
            - Includes root positional-argument arity when present.
        """
        positional_arity = -1
        if root_positional_override is not None:
            positional_arity = len(root_positional_override)
        return (
            plan_signature,
            socket_shape,
            positional_arity,
        )

    @staticmethod
    def _build_override_plan_signature_from_ir_payload(
            *,
            override_execution_ir_payload: Dict[str, Any],
    ) -> Tuple[Any, ...]:
        """
        Build deterministic override plan signature from execution IR payload.

        Contract:
            - Requires payload field ``signature``.
            - Includes optional ``steps_rows_signature`` when present.
        """
        variant_signature = override_execution_ir_payload["signature"]
        return (
            "phase11_overrides_ir",
            variant_signature,
            override_execution_ir_payload.get("steps_rows_signature"),
        )

    @staticmethod
    def _resolve_override_execution_ir_payload(
            *,
            crafter: Any,
            execution_ir_key: str = "overrides",
    ) -> Dict[str, Any]:
        """
        Resolve Phase11 override execution IR payload by required variant key.

        Contract:
            - Selects the execution variant payload by `execution_ir_key`.
            - Returns the override execution payload mapping by reference.
        """
        codegen_ir = crafter.codegen_ir
        phase8_11_payload = codegen_ir["phase8_11"]
        execution_payload = phase8_11_payload["execution"]
        return execution_payload[execution_ir_key]

    def _get_or_compile_override_executor(
            self,
            *,
            spell: ISpell,
            shape_key: Tuple[Any, ...],
            execution_plan: Any,
            override_targets_by_spell_id: Dict[str, Tuple[Any, ...]],
            any_overrides_present: bool,
            path_registry: Optional[Any],
            plan_rows: Optional[Sequence[Dict[str, Any]]],
            root_spell_id: Optional[str],
            spell_lookup: Optional[Dict[str, Any]],
    ) -> Callable[[Any, Dict[Any, Any], Optional[Sequence[Any]]], Any]:
        """
        Resolve a cached override specialization executor or compile on miss.

        Contract:
            - Cache entries are bounded by `_max_override_specializations_per_spell`.
            - Eviction order is deterministic FIFO per spell id.
        """
        spell_id = spell.spell_id
        override_specialization_cache = self._override_specialization_cache
        override_specialization_order = self._override_specialization_order
        max_override_specializations_per_spell = (
            self._max_override_specializations_per_spell
        )
        cache = override_specialization_cache.get(spell_id)
        order = override_specialization_order.get(spell_id)
        if cache is None:
            cache = {}
            order = deque()
            override_specialization_cache[spell_id] = cache
            override_specialization_order[spell_id] = order

        cached = cache.get(shape_key)
        if cached is not None:
            return cached

        compiled = compile_phase12_overrides_executor(
            execution_plan=execution_plan,
            override_targets_by_spell_id=override_targets_by_spell_id,
            any_overrides_present=any_overrides_present,
            path_registry=path_registry,
            plan_rows=plan_rows,
            root_spell_id=root_spell_id,
            spell_lookup=spell_lookup,
        )

        if len(order) >= max_override_specializations_per_spell:
            evicted = order.popleft()
            cache.pop(evicted, None)
        cache[shape_key] = compiled
        order.append(shape_key)
        return compiled

    @staticmethod
    def _raise_on_missing_factory_result(
            *,
            spell: ISpell,
            result: Any,
            message: str,
    ) -> None:
        """
        Raise when factory-style spells produce no runtime result.

        Contract:
            - Applies only to class/method/lambda spells.
            - Returns silently for non-factory spell types.
        """
        if (
            result is None
            and (spell.is_class_spell or spell.is_method_spell or spell.is_lambda_spell)
        ):
            raise MeldExecutionError(
                spell_id=spell.spell_index.current,
                spell_name=spell.spell_name,
                message=message,
            )

