from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Callable, ClassVar, Mapping, Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.conduit.meld.creation_context.creation_context_codegen import (
    compile_creation_context_hooks_no_overrides_executor,
    compile_creation_context_hooks_overrides_only_executor,
    compile_creation_context_instance_no_overrides_executor,
    compile_creation_context_instance_overrides_only_executor,
)
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
from melder.utilities.custom_exceptions.spell_space_scope_error import (
    SpellSpaceScopeError,
)
from melder.utilities.general_base.cleanable import Cleanable

if TYPE_CHECKING:
    from melder.aether.conduit.creations.creations import Creations
    from melder.aether.spellbook.spell import Spell
    from melder.utilities.synchronization.creation_gate import CreationGate


class CreationContext(Cleanable):
    """
    Spell-bound runtime executor context.

    Purpose:
        Hold the spell-static execution inputs emitted by phase 11 and compile
        them into the direct hooks/no-hooks runtime doors that meld uses on the
        hot path.

    Contract:
        - `CreationContext` keeps dynamic gate handling because that is runtime
          policy, not compiler planning.
        - The heavy override specialization work is supplied through the
          phase-11-provided `overrides_executor` callable.
        - Hook/no-hook dispatch is restored to direct compiled doors so the
          hot path matches the previous runtime shape instead of routing
          through wrapper probes.
        - `execute(...)` returns `(instance, created)`.
        - `execute_no_hooks(...)` returns only the instance.
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
        "_execute_with_overrides",
        "_cached_codegen",
    ]

    def __init__(
            self,
            *,
            spell: "Spell",
            dynamic_environment: bool = False,
            creation_gate: Optional["CreationGate"] = None,
            creation_gate_index_id: Optional[str] = None,
            resolve_route_key: str,
            fast_transient_no_overrides_enabled: bool = False,
            no_overrides_executor: Optional[Callable[..., Any]] = None,
            overrides_executor: Optional[Callable[..., Any]] = None,
            cached_codegen: Optional[Mapping[str, Any]] = None,
    ) -> None:
        """
        Build one spell-bound runtime context.

        Args:
            spell:
                Spell this context is bound to.
            dynamic_environment:
                True when the owning conduit runs in dynamic mode.
            creation_gate:
                Shared spell-index gate for dynamic-mode admission.
            creation_gate_index_id:
                Stable spell-index id used in gate diagnostics.
            resolve_route_key:
                Preselected existence route key for this spell.
            fast_transient_no_overrides_enabled:
                True when the transient-many no-overrides fast lane is valid.
            no_overrides_executor:
                Phase-11-provided base no-overrides executor.
            overrides_executor:
                Phase-11-provided override execution callable.
            cached_codegen:
                Exact cache bundle for these phase-11 outputs when already
                available. When omitted, the context captures the constructor
                inputs as its cache bundle directly.

        Raises:
            ValueError:
                If `dynamic_environment` is true and `creation_gate` is not
                supplied.
        """
        super().__init__()
        self._spell = spell
        self._spell_id = spell.spell_id
        self._dynamic_environment = bool(dynamic_environment)
        if self._dynamic_environment and creation_gate is None:
            raise ValueError(
                "creation_gate cannot be None when dynamic_environment is True."
            )
        self._creation_gate = creation_gate
        self._creation_gate_index_id = creation_gate_index_id
        self._owner_creations = spell._owner_creations
        self._no_overrides_executor = no_overrides_executor
        self._execute_with_overrides = overrides_executor
        if cached_codegen is None:
            self._cached_codegen = {
                "resolve_route_key": resolve_route_key,
                "fast_transient_no_overrides_enabled": (
                    fast_transient_no_overrides_enabled
                ),
                "no_overrides_executor": no_overrides_executor,
                "overrides_executor": overrides_executor,
            }
        else:
            self._cached_codegen = dict(cached_codegen)

        self._execute_hooks_overrides_compiled = (
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
        self._execute_no_hooks_overrides_compiled = (
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
        Deterministically release runtime references.
        """
        if self._cleaned:
            return
        self._cleaned = True

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
        del self._execute_with_overrides
        del self._cached_codegen

    @classmethod
    def load_cached(
            cls,
            *,
            spell: "Spell",
            dynamic_environment: bool = False,
            creation_gate: Optional["CreationGate"] = None,
            creation_gate_index_id: Optional[str] = None,
            resolve_route_key: str,
            fast_transient_no_overrides_enabled: bool = False,
            no_overrides_executor: Optional[Callable[..., Any]],
            overrides_executor: Optional[Callable[..., Any]],
            cached_codegen: Optional[Mapping[str, Any]] = None,
            publish: bool = False,
    ) -> "CreationContext":
        """
        Build one generic CreationContext from already-rehydrated cache outputs.

        Purpose:
            Keep cache rehydration out of the constructor call sites while still
            letting experiments or future cache loaders publish a spell-bound
            context from prebuilt executors.
        """
        loaded_creation_context = cls(
            spell=spell,
            dynamic_environment=dynamic_environment,
            creation_gate=creation_gate,
            creation_gate_index_id=creation_gate_index_id,
            resolve_route_key=resolve_route_key,
            fast_transient_no_overrides_enabled=fast_transient_no_overrides_enabled,
            no_overrides_executor=no_overrides_executor,
            overrides_executor=overrides_executor,
            cached_codegen=cached_codegen,
        )
        if publish:
            previous_creation_context = spell._creation_context
            spell._creation_context = loaded_creation_context
            current_state = spell._creation_context_switch.state
            if current_state < 2:
                spell._creation_context_switch.advance(2 - current_state)
            elif current_state > 2:
                spell._creation_context_switch.advance(-(current_state - 2))
            if (
                    previous_creation_context is not None
                    and previous_creation_context is not loaded_creation_context
            ):
                try:
                    previous_creation_context.cleanup()
                except Exception:
                    pass
        return loaded_creation_context

    @classmethod
    def load_cached_bundle(
            cls,
            *,
            spell: "Spell",
            cached_codegen: Mapping[str, Any],
            dynamic_environment: bool = False,
            creation_gate: Optional["CreationGate"] = None,
            creation_gate_index_id: Optional[str] = None,
            publish: bool = False,
    ) -> "CreationContext":
        """
        Build one generic CreationContext from a cache bundle.

        Purpose:
            Provide the cache-bundle load seam directly on `CreationContext` so
            cache hydration does not need a separate builder layer.
        """
        resolve_route_key = cached_codegen["resolve_route_key"]
        fast_transient_no_overrides_enabled = bool(
            cached_codegen.get("fast_transient_no_overrides_enabled")
        )
        no_overrides_executor = cached_codegen["no_overrides_executor"]
        overrides_executor = cached_codegen["overrides_executor"]
        return cls.load_cached(
            spell=spell,
            dynamic_environment=dynamic_environment,
            creation_gate=creation_gate,
            creation_gate_index_id=creation_gate_index_id,
            resolve_route_key=resolve_route_key,
            fast_transient_no_overrides_enabled=(
                fast_transient_no_overrides_enabled
            ),
            no_overrides_executor=no_overrides_executor,
            overrides_executor=overrides_executor,
            cached_codegen=cached_codegen,
            publish=publish,
        )

    def output_cache(self) -> Mapping[str, Any]:
        """
        Return the exact cached codegen bundle held by this CreationContext.

        Returns:
            Mapping[str, Any]:
                Read-only cache bundle for the current phase-11 outputs.
        """
        return MappingProxyType(self._cached_codegen)

    def execute(
            self,
            caller_creations: "Creations",
            overrides: Optional[dict[str, Any]] = None,
    ) -> tuple[Any, bool]:
        """
        Execute one meld resolution through the hooks-aware runtime doors.
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
            caller_creations: "Creations",
            overrides: Optional[dict[str, Any]] = None,
    ) -> Any:
        """
        Execute one meld resolution through the direct no-hooks runtime doors.
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
