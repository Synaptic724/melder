from collections import deque
from typing import Any, Callable, Dict, Optional, Sequence, Tuple

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.conduit.meld.meld_context.meld_context import MeldContext
from melder.aether.dev_ops.spell_system_states.spell_validity import SpellValidity
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
        executors compiled by SpellCrafter, without invoking MeldEngine.

    Contract:
        - Executes no-overrides calls through `phase12_no_overrides_executor`.
        - Executes override calls through specialization executors compiled from
          the Phase 11 override plan.
        - Keeps override specialization caches bounded per spell.
        - Mutation overrides are not supported on this runtime path.
        - Enforces spell validity/change-control invariants before execution.
        - Raises deterministic `MeldExecutionError` when runtime prerequisites
          are not satisfied.
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

    def execute_fast_transient(
            self,
            *,
            spell: ISpell,
            conduit_id: Optional[str],
    ) -> Any:
        """
        Execute a transient no-overrides spell through Phase 12 executor.

        Contract:
            - Enforces spell invariants before execution.
            - Requires a compiled Phase 12 executor.
            - Does not accept overrides or mutations.
        """
        self._enforce_spell_invariants(spell, conduit_id)
        if spell.has_mutation_override:
            raise MeldExecutionError(
                spell_id=spell.spell_index.current,
                spell_name=spell.spell_name,
                message=(
                    "Mutation overrides are not supported on the Phase 12 "
                    "no-overrides runtime path."
                ),
            )
        executor = self._require_phase12_executor(spell)
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

    def codegen_fast_transient(
            self,
            *,
            spell: ISpell,
            conduit_id: Optional[str],
    ) -> Any:
        """
        Execute fast transient through the same Phase 12 runtime path.

        Contract:
            - Delegates directly to `execute_fast_transient`.
        """
        return self.execute_fast_transient(
            spell=spell,
            conduit_id=conduit_id,
        )

    def execute(self, context: MeldContext) -> Any:
        """
        Execute one meld call through the appropriate Phase 12 executor route.

        Contract:
            - `context` must contain a non-None root spell.
            - No-overrides calls use the precompiled no-overrides executor.
            - Override calls use spell-scoped specialization executors.
            - Mutation overrides are rejected.
            - Raises MeldExecutionError when required Phase 11/12 artifacts are
              missing.
            - Returns the constructed root instance.
        """
        if context is None:
            raise ValueError("context must not be None.")
        spell = context.root_spell
        if spell is None:
            raise ValueError("context.root_spell must not be None.")

        self._enforce_spell_invariants(spell, context.conduit_id)

        if spell.has_mutation_override:
            raise MeldExecutionError(
                spell_id=spell.spell_index.current,
                spell_name=spell.spell_name,
                message=(
                    "Mutation overrides are not supported on the Phase 12 "
                    "no-overrides runtime path."
                ),
            )

        if context.overrides:
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
        for cache in self._override_specialization_cache.values():
            cache.clear()
        for order in self._override_specialization_order.values():
            order.clear()
        self._override_specialization_cache.clear()
        self._override_specialization_order.clear()
        self._override_specialization_cache = None
        self._override_specialization_order = None
        self._max_override_specializations_per_spell = None
        self._cleaned = True

    @staticmethod
    def _require_phase12_executor(spell: ISpell) -> Callable[[Any], Any]:
        """
        Require and return the compiled Phase 12 no-overrides executor.

        Contract:
            - Raises MeldExecutionError when SpellCrafter artifacts are absent.
            - Raises MeldExecutionError when no Phase 12 executor is compiled.
        """
        crafter = spell._crafter
        if crafter is None:
            raise MeldExecutionError(
                spell_id=spell.spell_index.current,
                spell_name=spell.spell_name,
                message="Missing SpellCrafter artifacts for Phase 12 execution.",
            )
        executor = crafter.phase12_no_overrides_executor
        if executor is None:
            raise MeldExecutionError(
                spell_id=spell.spell_index.current,
                spell_name=spell.spell_name,
                message=(
                    "Missing Phase 12 no-overrides executor for this spell. "
                    "Run conjure resolution phases before melding."
                ),
            )
        return executor

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
        executor = self._require_phase12_executor(spell)
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
            - Selects/compiles a spell-scoped specialization by override shape.
            - Never falls back to engine execution.
        """
        crafter = spell._crafter
        if crafter is None:
            raise MeldExecutionError(
                spell_id=spell.spell_index.current,
                spell_name=spell.spell_name,
                message="Missing SpellCrafter artifacts for Phase 12 override execution.",
            )

        override_patch_map = crafter.override_patch_map_phase10
        if override_patch_map is None:
            raise MeldExecutionError(
                spell_id=spell.spell_index.current,
                spell_name=spell.spell_name,
                message=(
                    "Phase 10 override patch map is required for override "
                    "specialization execution."
                ),
            )

        execution_plan = crafter.execution_plan_phase11_overrides
        if execution_plan is None:
            raise MeldExecutionError(
                spell_id=spell.spell_index.current,
                spell_name=spell.spell_name,
                message=(
                    "Phase 11 override execution plan is required for override "
                    "specialization execution."
                ),
            )

        override_payload = context.overrides
        if override_payload is None:
            raise MeldExecutionError(
                spell_id=spell.spell_index.current,
                spell_name=spell.spell_name,
                message="Override execution route requires context overrides.",
            )

        target_payload, root_positional_override = self._split_override_payload(
            spell=spell,
            override_payload=override_payload,
        )
        try:
            override_map = apply_phase10_override_payload(
                override_patch_map=override_patch_map,
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

        override_targets_by_spell_id = self._collect_override_targets(
            override_map=override_map,
        )
        shape_key = self._build_override_shape_key(
            execution_plan=execution_plan,
            override_targets_by_spell_id=override_targets_by_spell_id,
            root_positional_override=root_positional_override,
        )
        root_blueprint = crafter.root_blueprint_phase5
        path_registry = root_blueprint.path_registry if root_blueprint is not None else None
        any_overrides_present = bool(override_payload)
        executor = self._get_or_compile_override_executor(
            spell=spell,
            shape_key=shape_key,
            execution_plan=execution_plan,
            override_targets_by_spell_id=override_targets_by_spell_id,
            any_overrides_present=any_overrides_present,
            path_registry=path_registry,
        )

        try:
            result = executor(
                context,
                override_map,
                root_positional_override,
            )
        except MeldExecutionError:
            raise
        except Exception as exc:
            raise MeldExecutionError(
                spell_id=spell.spell_index.current,
                spell_name=spell.spell_name,
                message="Phase 12 override specialization executor failed.",
                inner=exc,
            ) from exc

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
        if not isinstance(raw_args, (list, tuple)):
            raise MeldExecutionError(
                spell_id=spell.spell_index.current,
                spell_name=spell.spell_name,
                message="__args__ override must be a list or tuple.",
            )
        normalized_payload: Dict[str, Any] = {}
        for key, value in override_payload.items():
            if key == "__args__":
                continue
            normalized_payload[key] = value
        return normalized_payload, tuple(raw_args)

    @staticmethod
    def _collect_override_targets(
            *,
            override_map: Dict[Any, Any],
    ) -> Dict[str, Tuple[Any, ...]]:
        """
        Group override socket refs by spell id with deterministic ordering.

        Contract:
            - Output ordering is deterministic for stable shape keying.
            - Socket refs are grouped by `socket_ref.node_id`.
        """
        by_spell_id: Dict[str, list[Any]] = {}
        for socket_ref in override_map.keys():
            spell_id = socket_ref.node_id
            bucket = by_spell_id.get(spell_id)
            if bucket is None:
                by_spell_id[spell_id] = [socket_ref]
            else:
                bucket.append(socket_ref)

        ordered: Dict[str, Tuple[Any, ...]] = {}
        for spell_id in sorted(by_spell_id.keys()):
            refs = by_spell_id[spell_id]
            refs.sort(
                key=lambda ref: (
                    ref.node_id,
                    ref.param_path_id,
                    ref.param_name,
                    ref.socket_kind.value,
                ),
            )
            ordered[spell_id] = tuple(refs)
        return ordered

    @staticmethod
    def _build_override_shape_key(
            *,
            execution_plan: Any,
            override_targets_by_spell_id: Dict[str, Tuple[Any, ...]],
            root_positional_override: Optional[Sequence[Any]],
    ) -> Tuple[Any, ...]:
        """
        Build a stable override-shape key for specialization cache lookup.

        Contract:
            - Includes execution-plan identity to avoid stale-plan collisions.
            - Includes deterministic socket-target tuples.
            - Includes root positional-argument arity when present.
        """
        socket_shape: list[Tuple[Any, ...]] = []
        for spell_id in sorted(override_targets_by_spell_id.keys()):
            for socket_ref in override_targets_by_spell_id[spell_id]:
                socket_shape.append(
                    (
                        socket_ref.node_id,
                        socket_ref.param_path_id,
                        socket_ref.param_name,
                        socket_ref.socket_kind.value,
                    )
                )
        positional_arity = -1
        if root_positional_override is not None:
            positional_arity = len(root_positional_override)
        return (
            id(execution_plan),
            tuple(socket_shape),
            positional_arity,
        )

    def _get_or_compile_override_executor(
            self,
            *,
            spell: ISpell,
            shape_key: Tuple[Any, ...],
            execution_plan: Any,
            override_targets_by_spell_id: Dict[str, Tuple[Any, ...]],
            any_overrides_present: bool,
            path_registry: Optional[Any],
    ) -> Callable[[Any, Dict[Any, Any], Optional[Sequence[Any]]], Any]:
        """
        Resolve a cached override specialization executor or compile on miss.

        Contract:
            - Cache entries are bounded by `_max_override_specializations_per_spell`.
            - Eviction order is deterministic FIFO per spell id.
        """
        spell_id = spell.spell_id
        cache = self._override_specialization_cache.get(spell_id)
        order = self._override_specialization_order.get(spell_id)
        if cache is None:
            cache = {}
            order = deque()
            self._override_specialization_cache[spell_id] = cache
            self._override_specialization_order[spell_id] = order

        cached = cache.get(shape_key)
        if cached is not None:
            return cached

        compiled = compile_phase12_overrides_executor(
            execution_plan=execution_plan,
            override_targets_by_spell_id=override_targets_by_spell_id,
            any_overrides_present=any_overrides_present,
            path_registry=path_registry,
        )
        if shape_key not in cache:
            if len(order) >= self._max_override_specializations_per_spell:
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

    @staticmethod
    def _enforce_spell_invariants(
            spell: ISpell,
            conduit_id: Optional[str],
    ) -> None:
        """
        Validate spell validity and change-control gating before execution.

        Contract:
            - Blocks invalid/gated/disabled lineages.
            - Blocks dirty roots under ChangeControlManager.
            - Blocks broken or unvalidated spells.
        """
        if not spell._spellbook._spellbook_validation_required:
            return

        state = spell.system_state
        if state is not None:
            validity = state.validity
            if validity in (
                    SpellValidity.invalid,
                    SpellValidity.gated,
                    SpellValidity.disabled,
            ):
                raise MeldExecutionError(
                    spell_id=spell.spell_index.current,
                    spell_name=spell.spell_name,
                    message=(
                        "Cannot execute meld runtime for a spell whose lineage is "
                        f"{validity.name}."
                    ),
                )

        try:
            spellbook = spell._spellbook
            aether = spellbook._aether
            manager = aether._get_change_control_manager(spell.aetheric_frame)
            if manager is not None and conduit_id and manager.is_root_dirty(
                    conduit_id,
                    spell.spell_index.current,
            ):
                raise MeldExecutionError(
                    spell_id=spell.spell_index.current,
                    spell_name=spell.spell_name,
                    message=(
                        "Cannot execute meld runtime while the root is marked dirty. "
                        "Revalidation is required."
                    ),
                )
        except MeldExecutionError:
            raise
        except Exception:
            pass

        if spell.is_broken:
            raise MeldExecutionError(
                spell_id=spell.spell_index.current,
                spell_name=spell.spell_name,
                message="Cannot execute meld runtime for a broken spell.",
            )

        if not spell.validated:
            raise MeldExecutionError(
                spell_id=spell.spell_index.current,
                spell_name=spell.spell_name,
                message=(
                    "Spell has not been validated. Run the SpellCrafter phases "
                    "before attempting to meld this spell."
                ),
            )
