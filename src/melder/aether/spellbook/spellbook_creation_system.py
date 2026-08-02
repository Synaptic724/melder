import threading
from types import CodeType, FunctionType
from typing import TYPE_CHECKING, Any, Callable, Collection, Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple, Type, \
    ClassVar


from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.meld.creation_context.creation_context import (
    CreationContext,
)
from melder.aether.spellbook.spell_compiler.spell_compiler_system import (
    SpellCompilerSystem,
)
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.aether.spellbook.configuration.system_state import SystemState
from melder.aether.spellbook.spell_compiler.system.system_diagnostic import (
    SystemDiagnostic,
    SystemDiagnosticSeverity,
)
from melder.utilities.custom_exceptions.operation_cancelled_error import OperationCancelledError
from melder.utilities.custom_exceptions.phase_execution_error import PhaseExecutionError
from melder.utilities.custom_exceptions.spellbook_validation_error import SpellbookValidationError
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.general_helpers import EnumHelpers
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.synchronization.cancellation_event_signal import CancellationEventSignal
from melder.utilities.synchronization.phase_scheduler import PhaseScheduler
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state_change_reason import SpellStateChangeReason
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_validity import SpellValidity

if TYPE_CHECKING:
    from melder.aether.aetheric_frame.aetheric_frame import AethericFrame
    from melder.utilities.caching_system.caching_system import CachingSystem
    from melder.utilities.synchronization.unit_of_work import UnitOfWork
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spellbook import Spellbook
    from melder.utilities.synchronization.creation_gate_controller import (
        CreationGateController,
    )


class SpellbookCreationSystem(Cleanable):
    """
    Internal conjure orchestration system for Spellbook.

    Purpose:
        Encapsulate conjure-only orchestration concerns that previously lived
        inline in "Spellbook.conjure" while preserving Spellbook ownership of
        shared phase/revalidation methods.

    Contract:
        - Uses Spellbook methods for overlapping behaviour (configuration
          freeze/bind, structural phases, resolution phases, and spell checks).
        - Owns conjure-only orchestration helpers (hook flow, policy gate, and
          conduit ownership stamping).
        - Cleanup is deterministic and idempotent; once cleaned, this instance
          cannot be reused.

    Threading:
        Spellbook is expected to hold its own lock while invoking this system.
        This class uses an internal lock only to make "cleanup()" idempotent
        under concurrent teardown calls.

    Registration:
        MELDER KERNEL - guarded (internal manifest). Conjure-only
        orchestration that `Spellbook` constructs internally for one `conjure(...)`
        run; a user never holds or binds it. `access=internal` - kernel machinery to
        read for understanding, not to drive directly.

    Subsystem Context:
        The conjure orchestration helper of the spellbook subsystem. `Spellbook.conjure`
        constructs one per run and delegates conjure-only concerns to it: the pre/
        activation/post hook flow, the `check_system_state` policy/posture gate (a static
        method that raises when the frame's `AethericFrameConfiguration` posture is
        missing and admits only `Policies.default` when the effective mode is non-dynamic),
        and conduit-ownership stamping (`define_conduit_into_spells`) - while borrowing
        Spellbook's shared configuration-freeze, structural-phase, and resolution-phase
        methods. It sits between `SpellbookConfiguration` (freeze/bind) and the
        `PhaseScheduler` phase pipeline, and hands off to the constructed `Conduit`.

    System Context:
        Runs in the Spellbook layer of the DGR boot order
        (Aether|AetherUtilitySystem -> Crystallizer -> MutationResearch -> Nexus ->
        AethericFrame -> Spellbook -> Conduit|Ward), during `conjure` only: after config
        freeze and the settle-then-inherit effective-mode resolution, it gates whether a
        `Conduit` is born and threads the effective dynamic mode through phases 1-11 and
        cloud registration. One-run helper, cleaned after each conjure.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Internal conjure orchestration system for Spellbook. Melder kernel
        machinery: read it to understand the runtime, do not drive it directly.
    """

    _DEFAULT_ROOT_CONDUIT_NAME: ClassVar[str] = "default"
    # Chunk-granularity factor for the fused plan_group (phases 8-11) phase.
    # Measurement basis (29-class gauntlet graph, workers=5, repeats=5):
    # multiplier 1 -> barrier wall 5.22ms, worker load skew 2.46x,
    # parallel efficiency 0.64; multiplier 2 -> wall 4.42ms, skew 1.52x,
    # efficiency 0.80; multiplier 4 regressed (busy time inflated
    # 16.7 -> 22.2ms by cross-thread contention). 2 is the evidence-backed
    # production value; revisit only with new breakdown-harness numbers
    # (`benchmarks/testing_other_di/profile_phase_scheduler_breakdown.py`).
    # At workers == 1 the multiplier is gated off inside
    # `_build_chunked_phase_units` (bind/compiler-lane measurement showed
    # +1-1.6ms cold-setup tax from no-parallelism chunk splitting).
    PLAN_GROUP_CHUNK_MULTIPLIER: ClassVar[int] = 2
    __slots__ = Cleanable.__slots__ + [
        "_dynamic",
        "_conduit_logger",
        "_lock",
        "_name",
        "_phase_scheduler_cls",
        "_policy",
        "_spellbook",
    ]

    def __init__(
            self,
            *,
            spellbook: Spellbook,
            policy: Optional[str],
            dynamic: bool,
            name: Optional[str],
            conduit_logger: Optional[Any],
            phase_scheduler_cls: Type[PhaseScheduler],
    ) -> None:
        """
        Purpose:
            Initialize a one-run Spellbook creation orchestration helper.
        Contract:
            - Stores conjure inputs for a single execution run.
            - Uses injected classes so tests can monkeypatch construction flow.
            - Instance is cleaned via `cleanup()` and must not be reused after cleanup.
        Args:
            spellbook: Owning a Spellbook instance for this run.
            policy: Requested conduit policy string.
            dynamic: Dynamic-mode flag.
            name: Optional conduit name.
            conduit_logger: Optional conduit logger.
            phase_scheduler_cls:
                Scheduler class used for structural and resolution phases.
        Returns:
            None.
        Raises:
            None.
        """
        super().__init__()
        self._spellbook: Spellbook = spellbook
        self._policy: Optional[str] = policy
        self._dynamic: bool = dynamic
        self._name: Optional[str] = name
        self._conduit_logger = conduit_logger
        self._phase_scheduler_cls: Type[PhaseScheduler] = phase_scheduler_cls
        self._lock: threading.RLock = threading.RLock()

    def cleanup(self) -> None:
        """
        Purpose:
            Deterministically tear down this helper and release owned references.
        Contract:
            - Idempotent.
            - Drops all strong references to Spellbook and construction inputs.
            - Leaves the object permanently cleaned.
        Returns:
            None.
        Threading:
            Protected by an internal lock so concurrent cleanup calls resolve to
            one teardown pass.
        Lifecycle:
            Idempotent terminal operation; this instance must not be reused after
            cleanup.
        """
        if self._cleaned:
            return

        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            del self._spellbook
            del self._policy
            del self._dynamic
            del self._name
            del self._conduit_logger
            del self._phase_scheduler_cls

    def conjure(self) -> Conduit:
        """
        Purpose:
            Execute the full Spellbook creation pipeline and return a Conduit.
        Contract:
            - Preserves Spellbook conjure ordering and side effects.
            - Builds structural + resolution artifacts before conduit construction.
            - Fires lifecycle hooks in pre/activated/post order.
            - Marks Spellbook as conjured and wires ownership metadata into spells.
        Args:
            None.
        Returns:
            Conduit: Newly created conduit.
        Raises:
            Exception: Propagates exceptions from validation/phase/conduit flows.
        """
        self.check_cleaned()
        spellbook = self._spellbook

        phase_scheduler_cls = self._phase_scheduler_cls
        SpellbookCreationSystem._prepare_spellbook_for_conjure(
            spellbook=spellbook,
            phase_scheduler_cls=phase_scheduler_cls,
        )
        # Classify cache posture before plan phases so a full hit can skip the
        # phase-8-to-11 compile and load the runtime lanes from cache instead.
        resolved_conduit_name = (
            self._name or SpellbookCreationSystem._DEFAULT_ROOT_CONDUIT_NAME
        )
        cache_state = SpellbookCreationSystem._build_conjure_cache_state(
            spellbook=spellbook,
            dynamic=self._dynamic,
            conduit_name=resolved_conduit_name,
        )
        cache_full_hit = cache_state["cache_path"] == "full_hit"
        conduit_id = SpellbookCreationSystem._prepare_resolution_for_conjure(
            spellbook=spellbook,
            phase_scheduler_cls=phase_scheduler_cls,
            force_skip_plan_phases=True if cache_full_hit else None,
        )
        # Build-lane gate: enforce the resolution verdict only on a real
        # from-scratch compile. A full cache hit replays a bundle whose verdict
        # was already enforced when it was first built, so it must not
        # re-validate or re-raise here.
        if not cache_full_hit:
            SpellbookCreationSystem._enforce_conduit_resolution_valid(
                spellbook=spellbook,
                conduit_id=conduit_id,
            )
        policy_enum = SpellbookCreationSystem._resolve_conjure_policy(
            spellbook=spellbook,
            policy=self._policy,
            dynamic=self._dynamic,
        )
        hook_map = SpellbookCreationSystem.get_conjure_hook_map(spellbook)
        if hook_map:
            SpellbookCreationSystem.fire_conjure_hooks(
                spellbook,
                hook_map,
                "on_conduit_pre_created",
            )
        creation_gate_controller = (
            SpellbookCreationSystem._resolve_frame_creation_gate_controller(
            spellbook=spellbook,
        ))
        aetheric_frame = SpellbookCreationSystem._resolve_existing_frame(
            spellbook=spellbook,
        )

        conduit = SpellbookCreationSystem._build_conduit(
            spellbook=spellbook,
            name=self._name,
            conduit_logger=self._conduit_logger,
            dynamic=self._dynamic,
            policy=policy_enum,
            conduit_id=conduit_id,
            creation_gate_controller=creation_gate_controller,
            aetheric_frame=aetheric_frame,
        )
        SpellbookCreationSystem._activate_conjured_conduit(
            spellbook=spellbook,
            conduit=conduit,
            hook_map=hook_map,
            cache_state=cache_state,
        )
        return conduit

    @staticmethod
    def _prepare_spellbook_for_conjure(
            *,
            spellbook: Spellbook,
            phase_scheduler_cls: Type[PhaseScheduler],
    ) -> None:
        """
        Purpose:
            Prepare Spellbook state required before conduit construction.
        Contract:
            - Freezes and binds configuration when not already locked.
            - Executes structural phases before conduit construction.
        Args:
            spellbook: Owning Spellbook instance.
            phase_scheduler_cls: Scheduler class used for phase execution.
        Returns:
            None.
        Raises:
            Exception: Propagates freeze/bind/phase failures from delegated calls.
        """
        if not spellbook.is_configuration_locked():
            spellbook._validate_and_freeze_configuration()
            spellbook._bind_aetheric_frame_configuration_to_aether()
            spellbook._bind_configuration_to_aether()
        SpellbookCreationSystem.run_structural_phases(
            spellbook=spellbook,
            phase_scheduler_cls=phase_scheduler_cls,
        )

    @staticmethod
    def _prepare_resolution_for_conjure(
            *,
            spellbook: Spellbook,
            phase_scheduler_cls: Type[PhaseScheduler],
            force_skip_plan_phases: Optional[bool] = None,
    ) -> str:
        """
        Purpose:
            Build conduit-scoped resolution artifacts before conduit creation.
        Contract:
            - Generates a new conduit id for phase scoping.
            - Runs conduit-scoped resolution phases against that id.
        Args:
            spellbook: Owning Spellbook instance.
            phase_scheduler_cls: Scheduler class used for phase execution.
        Returns:
            str: Newly generated conduit id used for phase scoping.
        Raises:
            Exception: Propagates failures from conduit-scoped phase execution.
        """
        conduit_id = IDBuilder.create_id()
        SpellbookCreationSystem.run_resolution_phases_for_conduit(
            spellbook=spellbook,
            conduit_id=conduit_id,
            phase_scheduler_cls=phase_scheduler_cls,
            force_skip_plan_phases=force_skip_plan_phases,
        )
        return conduit_id

    @staticmethod
    def _enforce_conduit_resolution_valid(
            *,
            spellbook: Spellbook,
            conduit_id: str,
    ) -> None:
        """
        Purpose:
            Build-lane gate that fails conjure when a from-scratch conduit
            compile produced an ERROR-severity resolution verdict (e.g. a
            `scope_ordering_violation`), rather than recording it silently and
            letting it surface later at meld.
        Contract:
            - Callers invoke this ONLY on the from-scratch path; a full cache
              hit replays a bundle whose verdict was already enforced when it
              was first built, so it must not re-validate or re-raise.
            - No-op when the conduit has no recorded resolution state or no
              ERROR diagnostics.
            - Raises `SpellbookValidationError` naming the spells the ERROR
              diagnostics attribute the failure to; graph-level errors that
              carry no spell_id fall back to every scoped spell.
        Args:
            spellbook: Owning Spellbook instance.
            conduit_id: Conduit id whose resolution verdict is enforced.
        Returns:
            None.
        Raises:
            SpellbookValidationError: When the conduit resolved with errors.
        """
        spell_system_states = spellbook._spell_system_states
        if spell_system_states is None:
            return
        resolution_state = spell_system_states.get_conduit_resolution_state(
            conduit_id
        )
        if resolution_state is None or not resolution_state.has_errors():
            return

        from melder.aether.spellbook.spell_compiler.system.system_diagnostic import (
            SystemDiagnosticSeverity,
        )
        from melder.utilities.custom_exceptions.spellbook_validation_error import (
            SpellbookValidationError,
        )

        spell_id_pool = spellbook._spell_id_pool
        offender_ids = [
            diagnostic.spell_id
            for diagnostic in resolution_state.list_diagnostics()
            if diagnostic.severity is SystemDiagnosticSeverity.ERROR
            and diagnostic.spell_id is not None
        ]
        # Graph-level errors (cycles, coverage) carry no spell_id; fall back to
        # every scoped spell so the failure stays attributable.
        if not offender_ids:
            offender_ids = list(spell_id_pool.keys())
        offending = [
            spell_id_pool[spell_id]
            for spell_id in dict.fromkeys(offender_ids)
            if spell_id in spell_id_pool
        ]
        raise SpellbookValidationError(offending)

    @staticmethod
    def _build_conjure_cache_state(
            *,
            spellbook: Spellbook,
            dynamic: bool,
            conduit_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Build the cache-state summary used by conjure cache orchestration.

        Purpose:
            Provide one bounded helper that classifies the current Spellbook
            spell set against the owned conduit cache so later conjure slices
            can choose between full-hit, mixed, and full-miss cache paths.

        Contract:
            - Uses the Spellbook-owned cache-enabled bool as the first gate.
            - Reads dynamic/automatic posture from the caller.
            - Builds exact-match, mixed, and miss sets from live spell ids and
              cached spell ids.
            - Live spell ids cover payload-eligible spells only:
              existing-creation spells bypass phases 8-11 by design and never
              carry cache payloads, so they must not block the full-hit
              classification.
            - Creates the Spellbook-owned CachingSystem only when caching is
              enabled.

        Args:
            spellbook:
                Owning Spellbook instance whose local spell set should be
                compared to cache state.
            dynamic:
                True when conjure is running in dynamic mode.

        Returns:
            Dict[str, Any]:
                Cache-state summary containing the cache utility, runtime
                posture flags, spell-id sets, and the classified cache path.
        """
        caching_enabled = spellbook._system_caching_enabled_in_aether()
        live_spell_ids = {
            spell_id
            for spell_id, spell in spellbook._spell_id_pool.items()
            if not spell.is_existing_creation
        }
        caching_system: Optional[CachingSystem] = None
        cached_spell_ids: Set[str] = set()
        if caching_enabled:
            caching_system = spellbook._get_or_create_caching_system(
                conduit_name=conduit_name,
            )
            cached_spell_ids = set(caching_system.cached_spell_ids)
        matched_spell_ids = live_spell_ids.intersection(cached_spell_ids)
        missing_spell_ids = live_spell_ids.difference(cached_spell_ids)
        stale_cached_spell_ids = cached_spell_ids.difference(live_spell_ids)
        is_full_hit = bool(live_spell_ids) and not missing_spell_ids
        is_mixed = bool(matched_spell_ids) and bool(missing_spell_ids)
        is_full_miss = not is_full_hit and not is_mixed
        return {
            "caching_enabled": caching_enabled,
            "caching_system": caching_system,
            "dynamic_mode": bool(dynamic),
            "automatic_mode": not bool(dynamic),
            "live_spell_ids": live_spell_ids,
            "cached_spell_ids": cached_spell_ids,
            "matched_spell_ids": matched_spell_ids,
            "missing_spell_ids": missing_spell_ids,
            "stale_cached_spell_ids": stale_cached_spell_ids,
            "cache_path": SpellbookCreationSystem._resolve_conjure_cache_path(
                caching_enabled=caching_enabled,
                is_full_hit=is_full_hit,
                is_mixed=is_mixed,
            ),
            "is_full_hit": is_full_hit,
            "is_mixed": is_mixed,
            "is_full_miss": is_full_miss,
        }

    @staticmethod
    def _resolve_conjure_cache_path(
            *,
            caching_enabled: bool,
            is_full_hit: bool,
            is_mixed: bool,
    ) -> str:
        """
        Resolve the current conjure cache classification label.

        Args:
            caching_enabled:
                True when the Spellbook cache policy is enabled.
            is_full_hit:
                True when the live spell set matches the cached spell set.
            is_mixed:
                True when the live spell set partially overlaps the cache.

        Returns:
            str:
                One of `disabled`, `full_hit`, `mixed`, or `full_miss`.
        """
        if not caching_enabled:
            return "disabled"
        if is_full_hit:
            return "full_hit"
        if is_mixed:
            return "mixed"
        return "full_miss"

    @staticmethod
    def _load_cached_spell_payloads_for_conjure(
            *,
            spellbook: Spellbook,
            caching_system: "CachingSystem",
            spell_ids: Iterable[str],
    ) -> Set[str]:
        """
        Load cached spell payloads into live spells for the conjure path.

        Purpose:
            Provide the production cache-load surface for conjure-owned cache
            orchestration without forcing the caller to rebuild individual
            payload-loading logic.

        Contract:
            - Requires a live Spellbook-owned cache utility.
            - Loads only the current production payload shape.
            - Publishes the rebuilt CreationContext back onto each loaded spell.
            - Marks loaded spells as runtime-resolution complete.

        Args:
            spellbook:
                Owning Spellbook instance.
            caching_system:
                Spellbook-owned cache utility.
            spell_ids:
                Spell ids whose cached payloads should be loaded.

        Returns:
            Set[str]:
                Spell ids successfully loaded from cache.
        """
        loaded_spell_ids: Set[str] = set()
        requested_spell_ids = set(spell_ids)
        matched_spell_ids = requested_spell_ids.intersection(
            spellbook._spell_id_pool.keys(),
            caching_system.cached_spell_ids,
        )
        for spell_id in matched_spell_ids:
            spell = spellbook._spell_id_pool.get(spell_id)
            spell_payload = caching_system.get_spell_payload(spell_id)
            if spell_payload is None:
                continue
            try:
                SpellbookCreationSystem._publish_cached_creation_context_for_spell(
                    spell=spell,
                    spell_payload=spell_payload,
                )
            except Exception:
                continue
            spell.resolution_complete = True
            spell.resolution_required = False
            loaded_spell_ids.add(spell_id)
        return loaded_spell_ids

    @staticmethod
    def _publish_cached_creation_context_for_spell(
            *,
            spell: Any,
            spell_payload: Mapping[str, Any],
    ) -> None:
        """
        Publish one cached CreationContext payload onto a spell.

        Contract:
            - Cache selection is already spell-id keyed before this runs.
            - Manifest-first family packages publish a lazy context with
              ZERO conjure-time hydration; the first meld hydrates once and
              swaps the hot doors into the published context.
            - When the payload already carries live executors, it publishes
              directly through `CreationContext.load_cached(...)`.
            - When the payload carries a legacy phase-11 cache package, it
              delegates to the cache-load seam that rebuilds executors after
              phases 1-7.
        """
        from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.manifest_creation_cache import (
            is_manifest_package,
            load_creation_context_lazy,
        )

        if is_manifest_package(spell_payload):
            load_creation_context_lazy(
                spell,
                dict(spell_payload),
                publish=True,
            )
            return
        creation_context_factory = spell._creation_context_factory
        if creation_context_factory is None:
            raise RuntimeError("Spell has no CreationContextFactory.")
        creation_gate, creation_gate_index_id = (
            creation_context_factory._resolve_runtime_gate_for_spell(spell)
        )
        if not isinstance(spell_payload, Mapping):
            from melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation.spell_codegen_creation_cache import (
                load_creation_context,
            )

            _ = creation_gate
            _ = creation_gate_index_id
            load_creation_context(
                spell,
                spell_payload,
                publish=True,
            )
            return
        no_overrides_executor = spell_payload.get("no_overrides_executor")
        if isinstance(no_overrides_executor, CodeType):
            no_overrides_executor, overrides_executor = (
                SpellbookCreationSystem._rebuild_cached_creation_context_executors(
                    spell=spell,
                    spell_payload=spell_payload,
                )
            )
            CreationContext.load_cached(
                spell=spell,
                dynamic_environment=spell._dynamic_environment,
                creation_gate=creation_gate,
                creation_gate_index_id=creation_gate_index_id,
                no_overrides_executor=no_overrides_executor,
                overrides_executor=overrides_executor,
                publish=True,
            )
            return
        from melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation.spell_codegen_creation_cache import (
            load_creation_context,
        )

        _ = creation_gate
        _ = creation_gate_index_id
        load_creation_context(
            spell,
            dict(spell_payload),
            publish=True,
        )

    @staticmethod
    def _rebuild_cached_creation_context_executors(
            *,
            spell: Any,
            spell_payload: Mapping[str, Any],
    ) -> tuple[Callable[..., Any], Callable[..., Any]]:
        """
        Rebuild the final cached CreationContext executors from cached artifacts.
        """
        no_overrides_code_object = spell_payload["no_overrides_executor"]
        overrides_code_object = spell_payload["overrides_executor"]
        if spell_payload.get("existing_creation"):
            no_overrides_executor = SpellbookCreationSystem._build_function_from_code_object(
                code_object=no_overrides_code_object,
                freevar_values={
                    "spell": spell,
                    "_spell": spell,
                    "spell_id": spell.spell_id,
                    "_spell_id": spell.spell_id,
                },
            )
            overrides_executor = SpellbookCreationSystem._build_function_from_code_object(
                code_object=overrides_code_object,
                freevar_values={
                    "spell": spell,
                    "_spell": spell,
                    "spell_id": spell.spell_id,
                    "_spell_id": spell.spell_id,
                    "MeldExecutionError": _load_meld_execution_error_type(),
                    "_MeldExecutionError": _load_meld_execution_error_type(),
                    "existing_override_message": _EXISTING_OVERRIDE_MESSAGE,
                    "_existing_override_message": _EXISTING_OVERRIDE_MESSAGE,
                },
            )
            return no_overrides_executor, overrides_executor

        from melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation.spell_codegen_creation_cache import (
            _build_inner_no_overrides_executor,
        )

        base_no_overrides_executor = _build_inner_no_overrides_executor(
            spell,
            dict(spell_payload),
        )
        overrides_payload = spell_payload.get("overrides")
        if overrides_payload is None:
            def execute_with_overrides(
                    caller_creations: Any,
                    overrides: Optional[dict[str, Any]],
                    caller_creations_lock_held: bool = False,
            ) -> Any:
                _ = caller_creations
                _ = overrides
                _ = caller_creations_lock_held
                raise RuntimeError(
                    "Cached spell has no override lane "
                    f"(spell_id={spell.spell_id})."
                )
        else:
            # Zero override work at cache load. The override runtime is built
            # only on the first override-meld of this spell, never during load.
            _override_runtime_cell: list = [None]

            def execute_with_overrides(
                    caller_creations: Any,
                    overrides: Optional[dict[str, Any]],
                    caller_creations_lock_held: bool = False,
            ) -> Any:
                override_runtime = _override_runtime_cell[0]
                if override_runtime is None:
                    from melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation.spell_codegen_creation_cache import (
                        _build_inner_overrides_runtime,
                    )
                    override_runtime = _build_inner_overrides_runtime(
                        spell=spell,
                        overrides_payload=overrides_payload,
                        base_no_overrides_executor=base_no_overrides_executor,
                    )
                    _override_runtime_cell[0] = override_runtime
                return override_runtime(
                    caller_creations,
                    overrides,
                    caller_creations_lock_held,
                )

        no_overrides_executor = SpellbookCreationSystem._build_function_from_code_object(
            code_object=no_overrides_code_object,
            freevar_values={
                "_no_overrides_executor": base_no_overrides_executor,
                "_spell": spell,
                "_spell_id": spell.spell_id,
            },
        )
        overrides_executor = SpellbookCreationSystem._build_function_from_code_object(
            code_object=overrides_code_object,
            freevar_values={
                "_MeldExecutionError": _load_meld_execution_error_type(),
                "_execute_with_overrides": execute_with_overrides,
                "_existing_override_message": _EXISTING_OVERRIDE_MESSAGE,
                "_spell": spell,
                "_spell_id": spell.spell_id,
            },
        )
        return no_overrides_executor, overrides_executor

    @staticmethod
    def _build_function_from_code_object(
            *,
            code_object: Any,
            freevar_values: Mapping[str, Any],
    ) -> Callable[..., Any]:
        """
        Rebuild one cached executor function from its code object and closure.
        """
        if not isinstance(code_object, CodeType):
            raise RuntimeError("Cached executor artifact is not a CodeType.")
        closure = tuple(
            _make_cell(freevar_values[freevar_name])
            for freevar_name in code_object.co_freevars
        )
        return FunctionType(
            code_object,
            {"__builtins__": __builtins__},
            code_object.co_name,
            None,
            closure,
        )

    @staticmethod
    def _emit_spell_payloads_for_conjure(
            *,
            spellbook: Spellbook,
            spell_ids: Iterable[str],
    ) -> Set[str]:
        """
        Emit current spell payloads through the Spellbook-owned cache path.

        Purpose:
            Provide the save-side helper surface for later conjure cache
            branches while keeping cache ownership on Spellbook.

        Contract:
            - Delegates payload emission to `Spell.emit_cache()`.
            - Returns only the spell ids whose emit call reported success.
            - Uses the current production write behavior of the cache utility.

        Args:
            spellbook:
                Owning Spellbook instance.
            spell_ids:
                Spell ids to emit into cache.

        Returns:
            Set[str]:
                Spell ids whose payloads were emitted successfully.
        """
        matched_spell_ids = set(spell_ids).intersection(
            spellbook._spell_id_pool.keys(),
        )
        return {
            spell_id
            for spell_id in matched_spell_ids
            if spellbook._spell_id_pool[spell_id].emit_cache()
        }

    @staticmethod
    def _resolve_conjure_policy(
            *,
            spellbook: Spellbook,
            policy: Optional[str],
            dynamic: bool,
    ) -> Policies:
        """
        Purpose:
            Validate the requested conjure policy and convert it to `Policies`.
        Contract:
            - Applies system-state/dynamic-mode policy gating.
            - Ensures spell-level validation gate is satisfied before returning.
        Args:
            spellbook: Owning Spellbook instance.
            policy: Requested policy value.
            dynamic: Dynamic-mode flag.
        Returns:
            Policies: Resolved policy enum.
        Raises:
            RuntimeError: If policy/system-state rules are violated.
            ValueError: If the policy value cannot be converted to `Policies`.
        """
        resolved_policy = policy or "default"
        SpellbookCreationSystem.check_system_state(
            spellbook=spellbook,
            policy=resolved_policy,
            dynamic=dynamic,
        )
        policy_enum: Policies = EnumHelpers.convert_enum_and_check(
            resolved_policy,
            Policies,
        )
        return policy_enum

    @staticmethod
    def _build_conduit(
            *,
            spellbook: Spellbook,
            name: Optional[str],
            conduit_logger: Optional[Any],
            dynamic: bool,
            policy: Policies,
            conduit_id: str,
            creation_gate_controller: "CreationGateController",
            aetheric_frame: AethericFrame,
    ) -> Conduit:
        """
        Purpose:
            Build a conduit instance from resolved conjure inputs.
        Contract:
            - Passes through the resolved policy and generated conduit id.
            - Owns the concrete `Conduit` construction boundary directly.
        Args:
            spellbook: Owning Spellbook instance.
            name: Optional conduit name.
            conduit_logger: Optional conduit logger.
            dynamic: Dynamic-mode flag.
            policy: Resolved policy enum.
            conduit_id: Generated conduit id.
            creation_gate_controller:
                Frame-owned CreationGateController for the conduit frame.
            aetheric_frame: Live frame object for the conduit frame.
        Returns:
            Conduit: Newly constructed conduit instance.
        Raises:
            Exception: Propagates constructor failures from `Conduit`.
        """
        resolved_name = name or SpellbookCreationSystem._DEFAULT_ROOT_CONDUIT_NAME
        config = spellbook._configuration
        if config is None:
            raise ValueError("Spellbook configuration cannot be None")
        return Conduit(
            spellbook=spellbook,
            name=resolved_name,
            conduit_state=ConduitState.normal,
            configuration=config,
            aetheric_frame_name=spellbook._aetheric_frame_name,
            aetheric_frame=aetheric_frame,
            policy=policy,
            dynamic=dynamic,
            logger=conduit_logger,
            conduit_id=conduit_id,
            creation_gate_controller=creation_gate_controller,
        )

    @staticmethod
    def _resolve_frame_creation_gate_controller(
            *,
            spellbook: Spellbook,
    ) -> "CreationGateController":
        """
        Purpose:
            Resolve the frame-owned CreationGateController required for root
            conduit creation.

        Contract:
            - Delegates through the owning Spellbook's shared Aether surface.
            - Returns the live CreationGateController owned by the target frame.

        Args:
            spellbook: Owning Spellbook for this conjure run.

        Returns:
            CreationGateController:
                Frame-owned gate controller for the target frame.
        """
        manager = spellbook._aether._get_devops_manager(
            spellbook._aetheric_frame_name
        )
        return manager.creation_gate_controller

    @staticmethod
    def _resolve_existing_frame(
            *,
            spellbook: Spellbook,
    ) -> AethericFrame:
        """
        Purpose:
            Resolve the live frame object required for root conduit creation.

        Contract:
            - Delegates through the owning Spellbook's shared Aether surface.
            - Returns the live AethericFrame owned by the target frame.

        Args:
            spellbook: Owning Spellbook for this conjure run.

        Returns:
            AethericFrame: The live frame object for the target frame.
        """
        return spellbook._aether._get_existing_frame(spellbook._aetheric_frame_name)

    @staticmethod
    def _activate_conjured_conduit(
            *,
            spellbook: Spellbook,
            conduit: Conduit,
            hook_map: Optional[Mapping[str, List[Callable]]],
            cache_state: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Purpose:
            Finalize spellbook state and post-construction conduit wiring.
        Contract:
            - Marks Spellbook as conjured and disables default binding transaction.
            - Fires activation/post-hooks in order.
            - Wires conduit ownership into local spells and registers risk manager.
        Args:
            spellbook: Owning Spellbook instance.
            conduit: Created conduit.
            hook_map: Optional hook map for lifecycle callbacks.
        Returns:
            None.
        Raises:
            Exception: Propagates failures from hook execution and registration.
        """
        spellbook._conjured = True
        spellbook._conduit = conduit
        spellbook._refresh_devops_identity_state()
        spellbook._pending_binding_frame_keys.clear()

        if hook_map:
            SpellbookCreationSystem.fire_conjure_hooks(
                spellbook,
                hook_map,
                "on_conduit_activated",
                conduit,
            )
        SpellbookCreationSystem.define_conduit_into_spells(
            spellbook=spellbook,
            conduit=conduit,
        )
        if cache_state is not None and cache_state.get("cache_path") == "full_hit":
            SpellbookCreationSystem._load_cached_creation_contexts_for_conjure(
                spellbook=spellbook,
                cache_state=cache_state,
            )
        if cache_state is not None and cache_state.get("cache_path") in (
                "mixed",
                "full_miss",
        ):
            SpellbookCreationSystem._stage_spell_payloads_at_conjure_end(
                spellbook=spellbook,
                cache_state=cache_state,
            )
        SpellbookCreationSystem._emit_conduit_cache_file_at_conjure_end(
            spellbook=spellbook,
        )
        spellbook._publish_nexus_state_for_conjure(conduit)
        spellbook._register_conduit_with_risk_manager(conduit)
        if hook_map:
            SpellbookCreationSystem.fire_conjure_hooks(
                spellbook,
                hook_map,
                "on_conduit_post_created",
                conduit,
            )

    @staticmethod
    def _load_cached_creation_contexts_for_conjure(
            *,
            spellbook: Spellbook,
            cache_state: Dict[str, Any],
    ) -> None:
        """
        Load both-lane CreationContexts from cache for a full-hit conjure.

        Purpose:
            On a full cache hit, rebuild and publish each spell's runtime
            CreationContext from its cached package instead of compiling phases
            8-11. Must run after ownership wiring (so `spell._owner_creations`
            is set) and after phases 1-7 (so the phase-5 path registry is live).

        Contract:
            - Best-effort per spell. A reload failure degrades that spell to the
              JIT path (`resolution_required=True`) so meld re-runs phases 8-11
              for it rather than breaking.
        """
        caching_system = cache_state.get("caching_system")
        if caching_system is None:
            return
        loaded_spell_ids = SpellbookCreationSystem._load_cached_spell_payloads_for_conjure(
            spellbook=spellbook,
            caching_system=caching_system,
            spell_ids=tuple(cache_state.get("live_spell_ids", ())),
        )
        for spell_id in tuple(cache_state.get("live_spell_ids", ())):
            if spell_id in loaded_spell_ids:
                continue
            spell = spellbook._spell_id_pool.get(spell_id)
            if spell is None:
                continue
            spell.resolution_required = True
            # Invalidate fast-meld-door entries: this spell now requires a
            # deferred-resolution pass before any fast-lane execution.
            spell._door_epoch += 1

    @staticmethod
    def _stage_spell_payloads_at_conjure_end(
            *,
            spellbook: Spellbook,
            cache_state: Dict[str, Any],
    ) -> None:
        """
        Stage cache payloads for spells the conduit cache is missing.

        Purpose:
            Make conjure the staging boundary for every constructed spell so a
            cache full hit does not depend on each spell being melded directly
            at least once. Dependency-only spells never receive their own
            `CreationContextFactory` publish, so meld-time staging alone leaves
            them permanently missing from the bundle and locks the conduit
            cache into the mixed path, recompiling phases 8-11 on every
            conjure.

        Contract:
            - Runs only on non-full-hit conjures, after phases 8-11 have built
              the compiler artifact for every constructed spell; staging is a
              metadata read for manifest-first families.
            - Delegates to `Spellbook._emit_spell_cache`, which dedupes against
              already-staged payloads and flags the conjure-end file emit
              boundary on success.
            - Payload eligibility is enforced upstream: `missing_spell_ids`
              derives from the live set built by `_build_conjure_cache_state`,
              which already excludes existing-creation spells.
            - Best-effort per spell: a staging miss leaves that spell on the
              compile path for the next conjure without failing this one.

        Args:
            spellbook:
                Owning Spellbook whose missing spell payloads should stage.
            cache_state:
                Conjure cache-state summary built by
                `_build_conjure_cache_state`.

        Returns:
            None.
        """
        for spell_id in cache_state["missing_spell_ids"]:
            spellbook._emit_spell_cache(spellbook._spell_id_pool[spell_id])

    @staticmethod
    def _emit_conduit_cache_file_at_conjure_end(
            *,
            spellbook: Spellbook,
    ) -> None:
        """
        Form the conduit cache file once at the end of conjure.

        Purpose:
            Materialize the conduit-scoped cache bundle after ownership wiring
            so a rooted conduit always has a cache file, even when no spell
            assets were staged during conjure.

        Contract:
            - No-op when root caching is disabled for this Spellbook.
            - Emits only when this conjure operation staged new cache.
            - Never propagates cache failures into the conjure path.

        Args:
            spellbook: Owning Spellbook whose conduit cache should be emitted.

        Returns:
            None.
        """
        if not spellbook._system_caching_enabled_in_aether():
            return
        try:
            spellbook._emit_cache_file_if_required()
        except Exception as exc:
            if spellbook._logger is not None:
                spellbook._logger.error(
                    f"Failed to emit conduit cache file at conjure end: {exc}",
                    "_emit_conduit_cache_file_at_conjure_end",
                    exc_info=True,
                )

    @staticmethod
    def check_system_state(spellbook: Spellbook, policy: str, dynamic: bool) -> None:
        """
        Purpose:
            Validate requested policy compatibility with the current system state.
        Contract:
            - Non-dynamic mode only allows "Policies.default".
            - Dynamic policy usage requires "SystemState.dynamic".
            - Raises RuntimeError with diagnostic context on policy/state mismatch.
        Args:
            spellbook: Owning Spellbook instance.
            policy: Requested policy value.
            dynamic: Dynamic-mode flag.
        Returns:
            None.
        Raises:
            RuntimeError: On policy/state contract violations.
        """
        policy_enum = EnumHelpers.convert_enum_and_check(policy, Policies)
        aetheric_frame_configuration = spellbook._aetheric_frame_configuration
        if aetheric_frame_configuration is None:
            raise RuntimeError(
                "Cannot check system state without an AethericFrameConfiguration. "
                f"(policy={policy}, dynamic={dynamic})"
            )
        system_state = aetheric_frame_configuration.system_state

        if not dynamic:
            if policy_enum != Policies.default:
                spellbook._logger.error(
                    "Dynamic-only policy requested while dynamic=False "
                    f"(policy={policy_enum}, system_state={system_state}).",
                    "_check_system_state",
                    exc_info=True,
                )
                raise RuntimeError(
                    "Dynamic-only policies are not allowed when dynamic mode is disabled. "
                    f"(policy={policy_enum}, dynamic={dynamic}, "
                    f"system_state={system_state}, allowed=default)"
                )
            return

        # Settle-then-inherit law (owner ruling 2026-07-20): the dynamic
        # argument reaching this gate is the EFFECTIVE mode resolved from
        # the frame posture by Spellbook._settle_or_inherit_conjure_mode,
        # so a flag-vs-posture mismatch is structurally impossible here.
        # Conjure no longer polices mode; dynamic-only operations fail at
        # their own gates. The policy check above remains the one real
        # constraint this gate owns.

    @staticmethod
    def define_conduit_into_spells(spellbook: Spellbook, conduit: Conduit) -> None:
        """
        Purpose:
            Stamp conduit ownership metadata and existing-object registrations.
        Contract:
            - Sets owner conduit metadata and SpellIndex owner conduit id.
            - Stamps spell runtime resolution gate defaults from configuration.
            - Eagerly registers existing-object spells into conduit creations.
            - Logs and suppresses per-spell failures so one spell does not block
              ownership wiring for the rest.
        Args:
            spellbook: Owning Spellbook instance.
            conduit: Conduit to stamp into local spells.
        Returns:
            None.
        Raises:
            None.
        """
        caching_enabled = spellbook._resolve_system_caching_enabled()
        # Conjure-time compilation is always full/eager now (the AOT/JIT knob
        # was removed once caching became the default skip mechanism), so no
        # spell starts life owing deferred resolution work.
        resolution_required: bool = False
        with spellbook._lock:
            for spell in spellbook._spells.values():
                try:
                    spell._add_owned_conduit(
                        conduit._id,
                        conduit._name,
                        conduit._creations,
                        dynamic_environment=conduit.__dynamic_environment__,
                        creation_gate_controller=conduit._creation_gate_controller,
                        caching_enabled=caching_enabled,
                    )
                    spell.resolution_required = resolution_required

                    if spell.user_created_object is not None:
                        try:
                            conduit._register_to_creations(spell, spell.user_created_object)
                        except Exception as reg_err:
                            spellbook._logger.error(
                                f"Failed to register existing creation for spell_id={spell.spell_id}: {reg_err}",
                                "_define_conduit_into_spells",
                                exc_info=True,
                            )
                except Exception as exc:
                    spellbook._logger.error(
                        f"Failed to define conduit into spell: {exc}",
                        "_define_conduit_into_spells",
                        exc_info=True,
                    )

    @staticmethod
    def get_conjure_hook_map(spellbook: Spellbook) -> Optional[Mapping[str, List[Callable]]]:
        """
        Purpose:
            Fetch registered conduit lifecycle hooks for the Spellbook id.
        Contract:
            - Returns None when hooks are unavailable or empty.
            - Suppresses and logs configuration hook retrieval failures.
        Args:
            spellbook: Owning Spellbook instance.
        Returns:
            Optional[Mapping[str, List[Callable]]]:
                Hook map or None when unavailable.
        Raises:
            None.
        """
        configuration = spellbook._configuration
        if configuration is None:
            return None

        try:
            hook_map = configuration.get_conduit_hooks(spellbook._id)
        except AttributeError:
            return None
        except Exception as exc:
            spellbook._logger.error(
                f"get_conjure_hook_map failed: {exc}",
                "get_conjure_hook_map",
                exc_info=True,
            )
            return None

        if not hook_map:
            return None

        return hook_map

    @staticmethod
    def fire_conjure_hooks(
            spellbook: Spellbook,
            hook_map: Optional[Mapping[str, List[Callable]]],
            hook_name: str,
            *args: Any,
    ) -> None:
        """
        Purpose:
            Execute all hooks for a lifecycle event and suppress hook-local errors.
        Contract:
            - No-op when hook map is missing or hook name is not registered.
            - Executes hooks in registration order.
            - Logs and suppresses per-hook exceptions.
        Args:
            spellbook: Owning Spellbook instance.
            hook_map: Optional lifecycle hook map.
            hook_name: Hook event name.
            *args: Positional args forwarded to each hook.
        Returns:
            None.
        """
        if not hook_map:
            return

        hooks = hook_map.get(hook_name)
        if not hooks:
            return

        for hook in hooks:
            try:
                hook(*args)
            except Exception as exc:
                spellbook._logger.error(
                    f"Error while executing conjure hook '{hook_name}': {exc}",
                    "_fire_conjure_hooks",
                    exc_info=True,
                )

    @staticmethod
    def run_resolution_phases(
            spellbook: Spellbook,
            conduit_id: str,
            phase_scheduler_cls: Type[PhaseScheduler] = PhaseScheduler,
    ) -> Dict[str, Sequence[UnitOfWork]]:
        """
        Purpose:
            Run structural phases followed by conduit-scoped resolution phases.
        Contract:
            - Requires a non-empty conduit id.
            - Runs phases 1-4, then conduit phases 5-11.
        Args:
            spellbook: Owning Spellbook instance.
            conduit_id: Conduit id used for resolution scope.
            phase_scheduler_cls: Phase scheduler class to instantiate.
        Returns:
            Dict[str, Sequence[UnitOfWork]]: Phase result mapping.
        Raises:
            ValueError: If conduit_id is empty.
        """
        spellbook.check_cleaned()
        if not conduit_id:
            raise ValueError("conduit_id must not be empty.")
        results: Dict[str, Sequence[UnitOfWork]] = {}
        results.update(
            SpellbookCreationSystem.run_structural_phases(
                spellbook=spellbook,
                phase_scheduler_cls=phase_scheduler_cls,
            )
        )
        results.update(
            SpellbookCreationSystem.run_resolution_phases_for_conduit(
                spellbook=spellbook,
                conduit_id=conduit_id,
                phase_scheduler_cls=phase_scheduler_cls,
            )
        )
        return results

    @staticmethod
    def run_structural_phases(
            spellbook: Spellbook,
            phase_scheduler_cls: Type[PhaseScheduler] = PhaseScheduler,
    ) -> Dict[str, Sequence[UnitOfWork]]:
        """
        Purpose:
            Run structural phase pipeline (requirements/symbolic/local/validation).
        Contract:
            - Executes phases 1-4 through the configured scheduler.
            - Raises SpellbookValidationError when any spell resolves as broken.
        Args:
            spellbook: Owning Spellbook instance.
            phase_scheduler_cls: Phase scheduler class to instantiate.
        Returns:
            Dict[str, Sequence[UnitOfWork]]: Phase result mapping.
        Raises:
            SpellbookValidationError: If any spell validates as broken.
        """
        spellbook.check_cleaned()
        compiler_system = SpellCompilerSystem()
        try:
            results = SpellbookCreationSystem._run_scheduler_with_phases(
                spellbook=spellbook,
                phase_scheduler_cls=phase_scheduler_cls,
                context_name="_run_structural_phases",
                register_phases=lambda scheduler: SpellbookCreationSystem._register_structural_phases(
                    spellbook=spellbook,
                    scheduler=scheduler,
                    compiler_system=compiler_system,
                ),
            )

            broken_spells = SpellbookCreationSystem._collect_broken_spells(
                spells=spellbook._spells.values(),
            )
            if broken_spells:
                SpellbookCreationSystem._raise_structural_validation_error(
                    spellbook=spellbook,
                    broken_spells=broken_spells,
                    context_name="_run_structural_phases",
                    message_prefix="Spellbook structural pipeline completed with broken spells; ",
                )
            return results
        finally:
            compiler_system.cleanup()

    @staticmethod
    def run_post_conjure_structural_phases(spellbook: Spellbook, spells: Sequence[Spell]) -> None:
        """
        Purpose:
            Run structural phases for spells bound after a conduit is already conjured.
        Contract:
            - No-ops when `spells` are empty.
            - Uses one shared CancellationEventSignal for the run.
            - Raises SpellbookValidationError when any spell resolves as broken.
        Args:
            spellbook: Owning Spellbook instance.
            spells: Newly bound spells to structurally validate.
        Returns:
            None.
        Raises:
            SpellbookValidationError: If any spell validates as broken.
            Exception: Propagates phase execution exceptions.
        """
        spellbook.check_cleaned()
        if not spells:
            return

        cancel_signal = CancellationEventSignal()
        cancel_event = cancel_signal.event
        compiler_system = SpellCompilerSystem()
        try:
            for spell in spells:
                compiler_system.run_structural_phases(
                    spellbook,
                    spell,
                    cancel_event=cancel_event,
                )

            broken_spells = SpellbookCreationSystem._collect_broken_spells(spells)
            if broken_spells:
                SpellbookCreationSystem._raise_structural_validation_error(
                    spellbook=spellbook,
                    broken_spells=broken_spells,
                    context_name="_run_post_conjure_structural_phases",
                    message_prefix="Post-conjure structural pipeline completed with broken spells; ",
                )
        except Exception as exc:
            try:
                cancel_signal.cancel()
            except Exception:
                pass
            spellbook._logger.error(
                f"Post-conjure structural phase execution failed: {exc}",
                "_run_post_conjure_structural_phases",
                exc_info=True,
            )
            raise
        finally:
            try:
                compiler_system.cleanup()
            except Exception:
                spellbook._logger.error(
                    "SpellCompilerSystem.cleanup() raised during post-conjure structural phases",
                    "_run_post_conjure_structural_phases",
                    exc_info=True,
                )
            try:
                cancel_signal.cleanup()
            except Exception:
                spellbook._logger.error(
                    "CancellationEventSignal.cleanup() raised during post-conjure structural phases",
                    "_run_post_conjure_structural_phases",
                    exc_info=True,
                )

    @staticmethod
    def run_resolution_phases_for_conduit(
            spellbook: Spellbook,
            conduit_id: str,
            phase_scheduler_cls: Type[PhaseScheduler] = PhaseScheduler,
            *,
            force_skip_plan_phases: Optional[bool] = None,
    ) -> Dict[str, Sequence[UnitOfWork]]:
        """
        Purpose:
            Run conduit-scoped resolution phases for a single conduit id.
        Contract:
            - Requires a non-empty conduit id.
            - Runs foundational phases first.
            - Runs plan phases whenever foundational phases have no errors,
              unless the caller forces a skip (cache full-hit path).
            - Cleans per-spell phase artifacts before returning.
        Args:
            spellbook: Owning Spellbook instance.
            conduit_id: Conduit id used for resolution scope.
            phase_scheduler_cls: Phase scheduler class to instantiate.
            force_skip_plan_phases: True only on the cache full-hit path,
                where plan phases (8-11) are hydrated from the cache bundle
                instead of recompiled. None/False means run them.
        Returns:
            Dict[str, Sequence[UnitOfWork]]: Phase result mapping.
        Raises:
            ValueError: If conduit_id is empty.
        """
        spellbook.check_cleaned()
        if not conduit_id:
            raise ValueError("conduit_id must not be empty.")

        resolved_skip_plan_phases = bool(force_skip_plan_phases)
        plan_skip_state: List[Optional[bool]] = [None]
        compiler_system = SpellCompilerSystem()
        try:
            results = SpellbookCreationSystem._run_scheduler_with_phases(
                spellbook=spellbook,
                phase_scheduler_cls=phase_scheduler_cls,
                context_name="_run_resolution_phases_for_conduit",
                register_phases=lambda scheduler: SpellbookCreationSystem._register_conduit_resolution_phases(
                    spellbook=spellbook,
                    scheduler=scheduler,
                    compiler_system=compiler_system,
                    conduit_id=conduit_id,
                    plan_skip_state=plan_skip_state,
                    force_skip_plan_phases=resolved_skip_plan_phases,
                ),
            )
        finally:
            compiler_system.cleanup()
        if plan_skip_state[0]:
            # The fused plan phase replaces the historical four plan phases;
            # the old keys are popped too in case a patched scheduler class
            # still reports them.
            results.pop("plan_group", None)
            results.pop("occurrence_plan", None)
            results.pop("injection_plan", None)
            results.pop("patch_maps", None)
            results.pop("execution_plan", None)

        SpellbookCreationSystem.cleanup_phase_artifacts_after_resolution(spellbook=spellbook)
        return results

    @staticmethod
    def run_resolution_phases_for_target_spell(
            spellbook: Spellbook,
            conduit_id: str,
            target_spell: Spell,
            phase_scheduler_cls: Type[PhaseScheduler] = PhaseScheduler,
    ) -> Dict[str, Sequence[UnitOfWork]]:
        """
        Purpose:
            Run target-local resolution phases for one spell within a conduit scope.
        Contract:
            - Requires non-empty conduit id and non-null target spell.
            - Runs local foundational phases before local plan phases.
            - Converts local KeyError dependency misses into deterministic diagnostics.
            - Cleans scoped phase artifacts before returning.
        Args:
            spellbook: Owning Spellbook instance.
            conduit_id: Conduit id used for resolution scope.
            target_spell: Target spell for local resolution.
            phase_scheduler_cls: Phase scheduler class to instantiate.
        Returns:
            Dict[str, Sequence[UnitOfWork]]: Phase result mapping.
        Raises:
            ValueError: If conduit_id is empty or target_spell is None.
            PhaseExecutionError: When non-visibility phase errors occur.
        """
        spellbook.check_cleaned()
        if not conduit_id:
            raise ValueError("conduit_id must not be empty.")
        if target_spell is None:
            raise ValueError("target_spell must not be None.")

        results: Dict[str, Sequence[UnitOfWork]] = {}
        target_spell_id = target_spell.spell_id

        results.update(
            SpellbookCreationSystem._run_target_foundational_resolution_phases(
                spellbook=spellbook,
                conduit_id=conduit_id,
                target_spell=target_spell,
                target_spell_id=target_spell_id,
                phase_scheduler_cls=phase_scheduler_cls,
            )
        )
        if SpellbookCreationSystem._conduit_resolution_has_errors(
                spellbook=spellbook,
                conduit_id=conduit_id,
        ):
            SpellbookCreationSystem.cleanup_phase_artifacts_after_resolution(
                spellbook=spellbook,
                spell_ids={target_spell_id},
            )
            # Gated resolution must surface as a validation failure, exactly
            # like the conduit-wide path. Returning here was a silent success:
            # callers marked the spell resolution-complete with no phase-11
            # creation built, and meld then failed deep in the context
            # builder with an opaque RuntimeError instead of the validation
            # contract callers rely on.
            raise SpellbookValidationError([target_spell])

        scoped_spell_ids, scoped_root_ids = SpellbookCreationSystem._collect_target_resolution_scope(
            target_spell=target_spell,
            target_spell_id=target_spell_id,
        )
        try:
            results.update(
                SpellbookCreationSystem._run_target_plan_resolution_phases(
                    spellbook=spellbook,
                    conduit_id=conduit_id,
                    target_spell=target_spell,
                    target_spell_id=target_spell_id,
                    phase_scheduler_cls=phase_scheduler_cls,
                )
            )
        except PhaseExecutionError as exc:
            missing_dependency_ids = SpellbookCreationSystem._extract_missing_dependency_ids(exc)
            if not missing_dependency_ids:
                raise
            SpellbookCreationSystem.record_local_resolution_visibility_failure(
                spellbook=spellbook,
                conduit_id=conduit_id,
                scoped_spell_ids=scoped_spell_ids,
                scoped_root_ids=scoped_root_ids,
                missing_dependency_ids=missing_dependency_ids,
            )
            SpellbookCreationSystem.cleanup_phase_artifacts_after_resolution(
                spellbook=spellbook,
                spell_ids=scoped_spell_ids,
            )
            return results
        SpellbookCreationSystem.cleanup_phase_artifacts_after_resolution(
            spellbook=spellbook,
            spell_ids=scoped_spell_ids,
        )
        return results

    @staticmethod
    def run_deferred_resolution_phases_for_target_spell(
            spellbook: Spellbook,
            conduit_id: str,
            target_spell: Spell,
            phase_scheduler_cls: Type[PhaseScheduler] = PhaseScheduler,
    ) -> Dict[str, Sequence[UnitOfWork]]:
        """
        Purpose:
            Run target-local deferred plan phases (8/9/10/11) for one spell.
        Contract:
            - Requires non-empty conduit id and non-null target spell.
            - Executes only local plan phases for the target spell.
            - Converts local KeyError dependency misses into deterministic
              visibility diagnostics.
            - Cleans scoped phase artifacts before returning.
        Args:
            spellbook: Owning Spellbook instance.
            conduit_id: Conduit id used for deferred-resolution scope.
            target_spell: Target spell for local deferred resolution.
            phase_scheduler_cls: Phase scheduler class to instantiate.
        Returns:
            Dict[str, Sequence[UnitOfWork]]: Phase result mapping.
        Raises:
            ValueError: If conduit_id is empty or target_spell is None.
            PhaseExecutionError: When non-visibility phase errors occur.
        """
        spellbook.check_cleaned()
        if not conduit_id:
            raise ValueError("conduit_id must not be empty.")
        if target_spell is None:
            raise ValueError("target_spell must not be None.")

        target_spell_id = target_spell.spell_id
        scoped_spell_ids, scoped_root_ids = (
            SpellbookCreationSystem._collect_target_resolution_scope(
                target_spell=target_spell,
                target_spell_id=target_spell_id,
            )
        )
        try:
            results = SpellbookCreationSystem._run_target_plan_resolution_phases(
                spellbook=spellbook,
                conduit_id=conduit_id,
                target_spell=target_spell,
                target_spell_id=target_spell_id,
                phase_scheduler_cls=phase_scheduler_cls,
            )
        except PhaseExecutionError as exc:
            missing_dependency_ids = SpellbookCreationSystem._extract_missing_dependency_ids(exc)
            if not missing_dependency_ids:
                raise
            SpellbookCreationSystem.record_local_resolution_visibility_failure(
                spellbook=spellbook,
                conduit_id=conduit_id,
                scoped_spell_ids=scoped_spell_ids,
                scoped_root_ids=scoped_root_ids,
                missing_dependency_ids=missing_dependency_ids,
            )
            SpellbookCreationSystem.cleanup_phase_artifacts_after_resolution(
                spellbook=spellbook,
                spell_ids=scoped_spell_ids,
            )
            return {}

        SpellbookCreationSystem.cleanup_phase_artifacts_after_resolution(
            spellbook=spellbook,
            spell_ids=scoped_spell_ids,
        )
        return results

    @staticmethod
    def _register_conduit_resolution_phases(
            *,
            spellbook: Spellbook,
            scheduler: PhaseScheduler,
            compiler_system: SpellCompilerSystem,
            conduit_id: str,
            plan_skip_state: List[Optional[bool]],
            force_skip_plan_phases: bool = False,
    ) -> None:
        """
        Purpose:
            Register conduit-scoped 5-11 phases on one scheduler lifecycle.
        Contract:
            - Preserves foundational-first ordering (`5/6/7` then `8/9/10/11`).
            - Samples conduit error state exactly once at the plan boundary and
              skips all plan phases when foundational phases already produced
              conduit-resolution errors.
            - Skips all plan phases when `force_skip_plan_phases` is True
              (used by deferred/JIT conjure mode).
            - Does not suppress plan phases due to errors introduced inside the
              plan group itself, preserving previous two-pass semantics.
        Args:
            spellbook: Owning Spellbook instance.
            scheduler: Scheduler receiving phase registrations.
            conduit_id: Conduit scope id for resolution.
            plan_skip_state:
                Single-slot mutable state updated to indicate whether plan phases
                were skipped due to foundational errors.
            force_skip_plan_phases:
                Whether plan phases should be skipped unconditionally.
        Returns:
            None.
        Raises:
            None.
        """
        scheduler.register_phase(
            "root_blueprints",
            lambda: SpellbookCreationSystem.phase_root_blueprints_factory(
                spellbook, scheduler, compiler_system, conduit_id
            ),
        )
        scheduler.register_phase(
            "system_validation",
            lambda: SpellbookCreationSystem.phase_system_validation_factory(
                spellbook, scheduler, compiler_system, conduit_id
            ),
        )
        scheduler.register_phase(
            "change_control",
            lambda: SpellbookCreationSystem.phase_change_control_factory(
                spellbook, scheduler, compiler_system, conduit_id
            ),
        )

        def _should_skip_plan_phases() -> bool:
            if force_skip_plan_phases:
                plan_skip_state[0] = True
                return True
            sampled_skip = plan_skip_state[0]
            if sampled_skip is None:
                sampled_skip = SpellbookCreationSystem._conduit_resolution_has_errors(
                    spellbook=spellbook,
                    conduit_id=conduit_id,
                )
                plan_skip_state[0] = sampled_skip
            return sampled_skip

        # Phases 8-11 are fused per spell: each step consumes only the same
        # spell's previous artifact (occurrence analysis -> model -> plan ->
        # codegen creation; phase 8's spellbook parameter is an explicitly
        # unused compatibility argument), so the three inter-phase barriers
        # carried no data contract and were deleted. One chunked phase runs
        # the whole plan sequence per eligible spell.
        scheduler.register_phase(
            "plan_group",
            lambda: [] if _should_skip_plan_phases() else SpellbookCreationSystem.phase_plan_group_factory(
                spellbook, scheduler, compiler_system, conduit_id
            ),
        )

    @staticmethod
    def _new_phase_scheduler(
            spellbook: Spellbook,
            phase_scheduler_cls: Type[PhaseScheduler],
    ) -> PhaseScheduler:
        """
        Purpose:
            Return the Spellbook-owned persistent phase scheduler for one
            orchestration run.
        Contract:
            - Borrows (lazily creating) the Spellbook's long-lived scheduler
              instead of constructing a fresh one per orchestration run, so
              every conjure group and revalidation reuses one worker pool.
            - Preserves the `phase_scheduler_cls` patch seam through the
              Spellbook accessor (a stub class replaces the live instance).
            - The historical name is retained as the single creation-system
              acquisition point so callers and patches stay stable.
        Args:
            spellbook: Owning Spellbook instance.
            phase_scheduler_cls: Scheduler class to instantiate (patch point).
        Returns:
            PhaseScheduler: The Spellbook-owned scheduler.
        Raises:
            Exception: Propagates constructor failures from `phase_scheduler_cls`.
        """
        return spellbook._get_or_create_phase_scheduler(phase_scheduler_cls)

    @staticmethod
    def _cleanup_phase_scheduler(
            spellbook: Spellbook,
            scheduler: PhaseScheduler,
            context_name: str,
    ) -> None:
        """
        Purpose:
            Release a borrowed persistent scheduler after one orchestration
            run, with standardized error logging.
        Contract:
            - Does NOT clean the scheduler: the pool is Spellbook-owned and
              torn down exactly once in Spellbook cleanup. This release only
              clears per-run phase registrations so a registration failure
              before `run_all_phases(...)` can never leak stale phases into
              the next run on the same pool.
            - Never raises release failures.
            - Emits context-aware error logs on release exceptions.
        Args:
            spellbook: Owning Spellbook instance.
            scheduler: Borrowed scheduler to release.
            context_name: Logging context label.
        Returns:
            None.
        Raises:
            None.
        """
        try:
            scheduler.clear_phases()
        except Exception:
            spellbook._logger.error(
                f"PhaseScheduler.clear_phases() raised during {context_name}",
                context_name,
                exc_info=True,
            )

    @staticmethod
    def _run_scheduler_with_phases(
            *,
            spellbook: Spellbook,
            phase_scheduler_cls: Type[PhaseScheduler],
            context_name: str,
            register_phases: Callable[[PhaseScheduler], None],
    ) -> Dict[str, Sequence[UnitOfWork]]:
        """
        Purpose:
            Run a scheduler lifecycle from phase registration through execution.
        Contract:
            - Always attempts scheduler cleanup in `finally`.
            - Returns scheduler `run_all_phases()` mapping.
        Args:
            spellbook: Owning Spellbook instance.
            phase_scheduler_cls: Scheduler class to instantiate.
            context_name: Logging context label.
            register_phases: Callback that registers phases on the scheduler.
        Returns:
            Dict[str, Sequence[UnitOfWork]]: Phase execution results.
        Raises:
            Exception: Propagates scheduler registration and execution failures.
        """
        # Run serialization: the persistent scheduler's phase registry is
        # per-run state, and meld-time revalidations can hit this path from
        # multiple threads without the Spellbook lock. The Spellbook-owned
        # run lock makes register/run/release atomic per run so concurrent
        # runs queue instead of corrupting each other's registrations.
        with spellbook._phase_run_lock:
            scheduler = SpellbookCreationSystem._new_phase_scheduler(
                spellbook=spellbook,
                phase_scheduler_cls=phase_scheduler_cls,
            )
            try:
                register_phases(scheduler)
                return scheduler.run_all_phases()
            finally:
                SpellbookCreationSystem._cleanup_phase_scheduler(
                    spellbook=spellbook,
                    scheduler=scheduler,
                    context_name=context_name,
                )

    @staticmethod
    def _register_structural_phases(
            *,
            spellbook: Spellbook,
            scheduler: PhaseScheduler,
            compiler_system: SpellCompilerSystem,
    ) -> None:
        """
        Purpose:
            Register structural phases (1-4) on a scheduler.
        Contract:
            - Registers requirements, symbolic_graph, local_frame, validation.
        Args:
            spellbook: Owning Spellbook instance.
            scheduler: Scheduler receiving phase registrations.
        Returns:
            None.
        """
        # Phases 1 and 2 are fused per spell: both read only the spell's own
        # artifact state (phase 2 consumes the same spell's phase-1
        # requirements and never reads other spells), so the barrier between
        # them carried no data contract and was deleted. Phase 3 reads the
        # whole live spell pool (`_iter_all_spells`) and therefore keeps hard
        # barriers on both sides; phase 4 runs per-spell parallel against
        # bind-time-static metadata behind the phase-3 barrier.
        scheduler.register_phase(
            "requirements_symbolic",
            lambda: SpellbookCreationSystem.phase_requirements_symbolic_factory(
                spellbook, scheduler, compiler_system
            ),
        )
        scheduler.register_phase(
            "local_frame",
            lambda: SpellbookCreationSystem.phase_local_frame_factory(
                spellbook, scheduler, compiler_system
            ),
        )
        scheduler.register_phase(
            "validation",
            lambda: SpellbookCreationSystem.phase_validation_factory(
                spellbook, scheduler, compiler_system
            ),
        )

    @staticmethod
    def _collect_broken_spells(spells: Iterable[Spell]) -> List[Spell]:
        """
        Purpose:
            Collect spells that resolve as broken from a spell sequence.
        Contract:
            - Treats `is_broken` access errors as broken for safety parity.
        Args:
            spells: Iterable of spells to inspect.
        Returns:
            List[Spell]: Spells considered broken.
        """
        broken_spells: List[Spell] = []
        for spell in spells:
            try:
                if spell.is_broken:
                    broken_spells.append(spell)
            except Exception:
                broken_spells.append(spell)
        return broken_spells

    @staticmethod
    def _raise_structural_validation_error(
            *,
            spellbook: Spellbook,
            broken_spells: List[Spell],
            context_name: str,
            message_prefix: str,
    ) -> None:
        """
        Purpose:
            Log and raise SpellbookValidationError for broken structural results.
        Contract:
            - Includes broken spell ids/names in error logs.
            - Always raises `SpellbookValidationError`.
        Args:
            spellbook: Owning Spellbook instance.
            broken_spells: Broken spells to report.
            context_name: Logging context label.
            message_prefix: Prefix for the log message body.
        Returns:
            None.
        Raises:
            SpellbookValidationError: Always rose with `broken_spells`.
        """
        broken_spell_ids = [spell.spell_id for spell in broken_spells]
        broken_spell_names = [spell.spell_name for spell in broken_spells]
        spellbook._logger.error(
            f"{message_prefix}"
            f"raising SpellbookValidationError. "
            f"broken_spell_ids={broken_spell_ids}, "
            f"broken_spell_names={broken_spell_names}",
            context_name,
        )
        raise SpellbookValidationError(broken_spells)

    @staticmethod
    def _conduit_resolution_has_errors(
            *,
            spellbook: Spellbook,
            conduit_id: str,
    ) -> bool:
        """
        Purpose:
            Read the conduit resolution error state from SpellSystemStates.
        Contract:
            - Returns False when no resolution errors are present.
        Args:
            spellbook: Owning Spellbook instance.
            conduit_id: Conduit scope id.
        Returns:
            bool: True when the conduit resolution state has errors.
        Raises:
            Exception: Propagates conduit-resolution state retrieval failures.
        """
        resolution_state = spellbook._spell_system_states.get_conduit_resolution_state(conduit_id)
        return resolution_state is not None and resolution_state.has_errors()

    @staticmethod
    def _run_conduit_foundational_resolution_phases(
            *,
            spellbook: Spellbook,
            conduit_id: str,
            phase_scheduler_cls: Type[PhaseScheduler],
    ) -> Dict[str, Sequence[UnitOfWork]]:
        """
        Purpose:
            Run foundational conduit resolution phases (5/6/7).
        Contract:
            - Registers root_blueprints, system_validation, and change_control.
        Args:
            spellbook: Owning Spellbook instance.
            conduit_id: Conduit scope id.
            phase_scheduler_cls: Scheduler class to instantiate.
        Returns:
            Dict[str, Sequence[UnitOfWork]]: Phase execution results.
        Raises:
            Exception: Propagates scheduler registration and execution failures.
        """
        compiler_system = SpellCompilerSystem()
        try:
            return SpellbookCreationSystem._run_scheduler_with_phases(
                spellbook=spellbook,
                phase_scheduler_cls=phase_scheduler_cls,
                context_name="_run_resolution_phases_for_conduit",
                register_phases=lambda scheduler: SpellbookCreationSystem._register_conduit_resolution_phases(
                    spellbook=spellbook,
                    scheduler=scheduler,
                    compiler_system=compiler_system,
                    conduit_id=conduit_id,
                    plan_skip_state=[None],
                    force_skip_plan_phases=True,
                ),
            )
        finally:
            compiler_system.cleanup()

    @staticmethod
    def _run_conduit_plan_resolution_phases(
            *,
            spellbook: Spellbook,
            conduit_id: str,
            phase_scheduler_cls: Type[PhaseScheduler],
    ) -> Dict[str, Sequence[UnitOfWork]]:
        """
        Purpose:
            Run conduit plan compilation phases (8/9/10/11).
        Contract:
            - Registers occurrence, injection, patch, and execution plan phases.
        Args:
            spellbook: Owning Spellbook instance.
            conduit_id: Conduit scope id.
            phase_scheduler_cls: Scheduler class to instantiate.
        Returns:
            Dict[str, Sequence[UnitOfWork]]: Phase execution results.
        Raises:
            Exception: Propagates scheduler registration and execution failures.
        """
        compiler_system = SpellCompilerSystem()
        try:
            return SpellbookCreationSystem._run_scheduler_with_phases(
                spellbook=spellbook,
                phase_scheduler_cls=phase_scheduler_cls,
                context_name="_run_resolution_phases_for_conduit",
                register_phases=lambda scheduler: SpellbookCreationSystem._register_conduit_resolution_phases(
                    spellbook=spellbook,
                    scheduler=scheduler,
                    compiler_system=compiler_system,
                    conduit_id=conduit_id,
                    plan_skip_state=[False],
                    force_skip_plan_phases=False,
                ),
            )
        finally:
            compiler_system.cleanup()

    @staticmethod
    def _register_target_single_phase(
            *,
            scheduler: PhaseScheduler,
            phase_name: str,
            target_spell_id: str,
            phase_func: Callable[..., Any],
            args: Tuple[Any, ...],
    ) -> None:
        """
        Purpose:
            Register one local target-spell phase as a single unit of work.
        Contract:
            - Registers exactly one unit with local-scope metadata.
        Args:
            scheduler: Scheduler receiving the phase.
            phase_name: Phase name/label prefix.
            target_spell_id: Target spell id for labelling metadata.
            phase_func: Bound spell phase callable.
            args: Concrete argument tuple for the phase callable.
        Returns:
            None.
        """
        scheduler.register_phase(
            phase_name,
            lambda: [
                scheduler.create_unit_of_work(
                    func=phase_func,
                    args=args,
                    label=f"{phase_name}:{target_spell_id}",
                    metadata={
                        "phase": phase_name,
                        "spell_id": target_spell_id,
                        "scope": "local",
                    },
                )
            ],
        )

    @staticmethod
    def _run_target_foundational_resolution_phases(
            *,
            spellbook: Spellbook,
            conduit_id: str,
            target_spell: Spell,
            target_spell_id: str,
            phase_scheduler_cls: Type[PhaseScheduler],
    ) -> Dict[str, Sequence[UnitOfWork]]:
        """
        Purpose:
            Run target-local foundational phases (root/system/change-control).
        Contract:
            - Registers local foundational phases for one target spell only.
        Args:
            spellbook: Owning Spellbook instance.
            conduit_id: Conduit scope id.
            target_spell: Target spell being revalidated.
            target_spell_id: Target spell id.
            phase_scheduler_cls: Scheduler class to instantiate.
        Returns:
            Dict[str, Sequence[UnitOfWork]]: Phase execution results.
        Raises:
            Exception: Propagates scheduler registration and execution failures.
        """
        compiler_system = SpellCompilerSystem()
        try:
            def _register(scheduler: PhaseScheduler) -> None:
                SpellbookCreationSystem._register_target_single_phase(
                    scheduler=scheduler,
                    phase_name="root_blueprints_local",
                    target_spell_id=target_spell_id,
                    phase_func=compiler_system.run_phase_root_blueprints_local,
                    args=(spellbook, target_spell, conduit_id, scheduler.cancel_event,),
                )
                SpellbookCreationSystem._register_target_single_phase(
                    scheduler=scheduler,
                    phase_name="system_validation_local",
                    target_spell_id=target_spell_id,
                    phase_func=compiler_system.run_phase_system_validation_local,
                    args=(spellbook, target_spell, conduit_id, scheduler.cancel_event,),
                )
                SpellbookCreationSystem._register_target_single_phase(
                    scheduler=scheduler,
                    phase_name="change_control_local",
                    target_spell_id=target_spell_id,
                    phase_func=compiler_system.run_phase_change_control_local,
                    args=(spellbook, target_spell, conduit_id,),
                )

            return SpellbookCreationSystem._run_scheduler_with_phases(
                spellbook=spellbook,
                phase_scheduler_cls=phase_scheduler_cls,
                context_name="_run_resolution_phases_for_target_spell",
                register_phases=_register,
            )
        finally:
            compiler_system.cleanup()

    @staticmethod
    def _collect_target_resolution_scope(
            *,
            target_spell: Spell,
            target_spell_id: str,
    ) -> Tuple[Set[str], Collection[str]]:
        """
        Purpose:
            Derive local spell/root scope used for cleanup and diagnostics.
        Contract:
            - Uses target spell phase-5 artifacts when available.
            - Falls back to the target spell id as root scope.
        Args:
            target_spell: Target spell being revalidated.
            target_spell_id: Target spell id.
        Returns:
            Tuple[Set[str], Collection[str]]:
                `(scoped_spell_ids, scoped_root_ids)` for local resolution scope.
        Raises:
            Exception: Propagates crafter/index access failures from target spell.
        """
        scoped_spell_ids: Set[str] = {target_spell_id}
        system_index = target_spell._compiler_artifact._spell_system_index_phase5
        if system_index is not None:
            scoped_spell_ids.update(system_index.nodes.keys())

        root_blueprints = target_spell._compiler_artifact._entire_dag_blueprint_phase5
        if root_blueprints is None or len(root_blueprints) == 0:
            scoped_root_ids: Collection[str] = ()
        else:
            scoped_root_ids = tuple(root_blueprints.keys())
        if len(scoped_root_ids) == 0:
            scoped_root_ids = (target_spell_id,)
        return scoped_spell_ids, scoped_root_ids

    @staticmethod
    def _run_target_plan_resolution_phases(
            *,
            spellbook: Spellbook,
            conduit_id: str,
            target_spell: Spell,
            target_spell_id: str,
            phase_scheduler_cls: Type[PhaseScheduler],
    ) -> Dict[str, Sequence[UnitOfWork]]:
        """
        Purpose:
            Run target-local plan phases (occurrence/injection/patch/execution).
        Contract:
            - Registers local plan phases for one target spell only.
        Args:
            spellbook: Owning Spellbook instance.
            conduit_id: Conduit scope id.
            target_spell: Target spell being revalidated.
            target_spell_id: Target spell id.
            phase_scheduler_cls: Scheduler class to instantiate.
        Returns:
            Dict[str, Sequence[UnitOfWork]]: Phase execution results.
        Raises:
            Exception: Propagates scheduler registration and execution failures.
        """
        if not SpellbookCreationSystem._is_spell_plan_phase_eligible(target_spell):
            return {}
        compiler_system = SpellCompilerSystem()
        try:
            def _register(scheduler: PhaseScheduler) -> None:
                SpellbookCreationSystem._register_target_single_phase(
                    scheduler=scheduler,
                    phase_name="occurrence_plan_local",
                    target_spell_id=target_spell_id,
                    phase_func=compiler_system.run_phase_occurrence_plan,
                    args=(spellbook, target_spell,),
                )
                SpellbookCreationSystem._register_target_single_phase(
                    scheduler=scheduler,
                    phase_name="injection_plan_local",
                    target_spell_id=target_spell_id,
                    phase_func=compiler_system.run_phase_injection_plan,
                    args=(target_spell,),
                )
                SpellbookCreationSystem._register_target_single_phase(
                    scheduler=scheduler,
                    phase_name="patch_maps_local",
                    target_spell_id=target_spell_id,
                    phase_func=compiler_system.run_phase_patch_maps,
                    args=(target_spell,),
                )
                SpellbookCreationSystem._register_target_single_phase(
                    scheduler=scheduler,
                    phase_name="execution_plan_local",
                    target_spell_id=target_spell_id,
                    phase_func=compiler_system.run_phase_execution_plan,
                    args=(spellbook, target_spell,),
                )

            return SpellbookCreationSystem._run_scheduler_with_phases(
                spellbook=spellbook,
                phase_scheduler_cls=phase_scheduler_cls,
                context_name="_run_resolution_phases_for_target_spell",
                register_phases=_register,
            )
        finally:
            compiler_system.cleanup()

    @staticmethod
    def _extract_missing_dependency_ids(exc: PhaseExecutionError) -> List[str]:
        """
        Purpose:
            Extract missing dependency ids from PhaseExecutionError KeyError entries.
        Contract:
            - Ignores non-KeyError execution failures.
            - Preserves encounter order from the scheduler error list.
        Args:
            exc: Raised PhaseExecutionError instance.
        Returns:
            List[str]: Missing dependency ids referenced by local plan execution.
        """
        missing_dependency_ids: List[str] = []
        for error in exc.errors:
            if not isinstance(error, KeyError):
                continue
            if not error.args:
                continue
            missing_dependency_ids.append(str(error.args[0]))
        return missing_dependency_ids

    @staticmethod
    def record_local_resolution_visibility_failure(
            spellbook: Spellbook,
            conduit_id: str,
            scoped_spell_ids: Collection[str],
            scoped_root_ids: Collection[str],
            missing_dependency_ids: Collection[str],
    ) -> None:
        """
        Purpose:
            Record local visibility failures as conduit diagnostics and invalid states.
        Contract:
            - Deduplicates missing dependency ids.
            - Marks scoped spell/root validity invalid for the conduit.
            - Records ERROR diagnostics on conduit resolution state.
        Args:
            spellbook: Owning Spellbook instance.
            conduit_id: Conduit scope id.
            scoped_spell_ids: Local spell ids participating in this run.
            scoped_root_ids: Local root ids participating in this run.
            missing_dependency_ids: Missing dependency ids from phase execution.
        Returns:
            None.
        Raises:
            Exception: Propagates state/diagnostic write failures.
        """
        diagnostics: List[SystemDiagnostic] = []
        seen_missing_ids: Set[str] = set()
        for missing_dependency_id in missing_dependency_ids:
            if missing_dependency_id in seen_missing_ids:
                continue
            seen_missing_ids.add(missing_dependency_id)
            diagnostics.append(
                SystemDiagnostic(
                    code="visibility_gap_dependency_filtered",
                    message=(
                        f"Local resolution referenced dependency "
                        f"'{missing_dependency_id}', but it is not visible "
                        "to this Spellbook."
                    ),
                    severity=SystemDiagnosticSeverity.ERROR,
                    spell_id=missing_dependency_id,
                    root_id=None,
                    source="LocalResolutionPhaseGuard",
                    details={
                        "missing_dependency_id": missing_dependency_id,
                    },
                )
            )

        spellbook._spell_system_states.bulk_set_conduit_spell_validity(
            conduit_id,
            {spell_id: SpellValidity.invalid for spell_id in scoped_spell_ids},
            change_reason=SpellStateChangeReason.validation_failed,
        )
        spellbook._spell_system_states.bulk_set_conduit_root_validity(
            conduit_id,
            {root_id: SpellValidity.invalid for root_id in scoped_root_ids},
            change_reason=SpellStateChangeReason.validation_failed,
        )
        spellbook._spell_system_states.record_conduit_diagnostics(conduit_id, diagnostics)

    @staticmethod
    def cleanup_phase_artifacts_after_resolution(
            spellbook: Spellbook,
            spell_ids: Optional[Collection[str]] = None,
    ) -> None:
        """
        Purpose:
            Cleanup per-spell phase artifacts after resolution phase execution.
        Contract:
            - Cleans all local spells when `spell_ids` is None.
            - Cleans only scoped spell ids when provided.
            - Suppresses per-spell cleanup exceptions.
        Args:
            spellbook: Owning Spellbook instance.
            spell_ids: Optional scoped spell ids to clean up.
        Returns:
            None.
        """
        spellbook.check_cleaned()
        compiler_system = SpellCompilerSystem()
        try:
            if spell_ids is None:
                for spell in spellbook._spells.values():
                    try:
                        compiler_system.cleanup_phase_artifacts(spell)
                    except Exception:
                        pass
                return

            for spell_id in spell_ids:
                target_spell = spellbook._spell_id_pool.get(spell_id, None)
                if target_spell is None:
                    continue
                try:
                    compiler_system.cleanup_phase_artifacts(target_spell)
                except Exception:
                    pass
        finally:
            compiler_system.cleanup()

    @staticmethod
    def _build_per_spell_phase_units(
            *,
            spellbook: Spellbook,
            scheduler: PhaseScheduler,
            compiler_system: SpellCompilerSystem,
            phase_name: str,
            phase_callable_attr: str,
            args_factory: Callable[[Spell, Any], Tuple[Any, ...]],
    ) -> Sequence[UnitOfWork]:
        """
        Purpose:
            Build chunked units of work for repeated per-spell phases.
        Contract:
            - Returns an empty list when no local spells exist.
            - Dispatches at most `scheduler.workers` chunk units per phase
              (see `_build_chunked_phase_units` for the unit shape); the
              historical one-unit-per-spell shape was retired with the
              persistent-pool scheduler because per-spell Future/queue
              overhead dominated the tiny per-spell phase steps.
            - Uses the supplied compiler-system front method for all spells.
            - Uses the provided `args_factory` to keep phase argument shape exact.
        Args:
            spellbook: Owning Spellbook instance.
            scheduler: Scheduler creating units of work.
            compiler_system: Compiler-system instance used for this run.
            phase_name: Phase label prefix and metadata phase value.
            phase_callable_attr: Compiler-system method name to invoke for each unit.
            args_factory: Builder for unit args per spell.
        Returns:
            Sequence[UnitOfWork]: Per-spell units for the requested phase.
        Raises:
            RuntimeError: If the spellbook has already been cleaned.
            AttributeError: If compiler system does not expose `phase_callable_attr`.
        """
        spellbook.check_cleaned()
        spells = spellbook._spells
        if not spells:
            return []

        cancel_event = scheduler.cancel_event
        phase_func = getattr(compiler_system, phase_callable_attr)

        def _spell_runner(spell: Spell) -> None:
            phase_func(*args_factory(spell, cancel_event))

        return SpellbookCreationSystem._build_chunked_phase_units(
            scheduler=scheduler,
            phase_name=phase_name,
            spells=list(spells.values()),
            spell_runner=_spell_runner,
        )

    @staticmethod
    def _chunk_spells(
            spells: List[Spell],
            chunk_count: int,
    ) -> List[Tuple[Spell, ...]]:
        """
        Purpose:
            Partition a spell batch into at most `chunk_count` contiguous
            chunks for one phase dispatch.
        Contract:
            - Preserves spell order within and across chunks.
            - Never returns empty chunks; chunk sizes differ by at most one.
        Args:
            spells: Ordered spell batch for one phase.
            chunk_count: Maximum number of chunks (>= 1).
        Returns:
            List[Tuple[Spell, ...]]: Non-empty contiguous chunks.
        """
        total = len(spells)
        effective = min(chunk_count, total)
        base_size, remainder = divmod(total, effective)
        chunks: List[Tuple[Spell, ...]] = []
        start = 0
        for index in range(effective):
            size = base_size + (1 if index < remainder else 0)
            chunks.append(tuple(spells[start:start + size]))
            start += size
        return chunks

    @staticmethod
    def _run_spell_chunk(
            spell_runner: Callable[[Spell], None],
            chunk: Tuple[Spell, ...],
            cancel_event: Any,
            phase_name: str,
    ) -> None:
        """
        Purpose:
            Execute one phase step for every spell in one dispatched chunk.
        Contract:
            - Runs spells sequentially on one worker; chunks of the same
              phase run in parallel across workers.
            - Checks the run cancel event before each spell so an aborted
              run stops promptly at spell granularity.
            - Raises the FIRST failing spell's original exception unchanged
              (no wrapping), preserving exception-type contracts for
              upstream consumers (e.g. SpellbookValidationError matching);
              the failing spell remains identifiable from the exception and
              the chunk unit's metadata spell-id list.
        Args:
            spell_runner: Callable executing the phase step(s) for one spell.
            chunk: Spells assigned to this worker for this phase.
            cancel_event: Current run's cooperative cancellation view.
            phase_name: Phase label used in cancellation messages.
        Returns:
            None.
        Raises:
            OperationCancelledError: When the run is cancelled mid-chunk.
            BaseException: First failing spell's original exception.
        """
        for spell in chunk:
            if cancel_event is not None and cancel_event.is_set:
                raise OperationCancelledError(
                    f"Phase '{phase_name}' chunk aborted due to run cancellation."
                )
            spell_runner(spell)

    @staticmethod
    def _build_chunked_phase_units(
            *,
            scheduler: PhaseScheduler,
            phase_name: str,
            spells: List[Spell],
            spell_runner: Callable[[Spell], None],
            chunk_multiplier: int = 1,
    ) -> Sequence[UnitOfWork]:
        """
        Purpose:
            Build at most `scheduler.workers * chunk_multiplier` chunk units
            for one phase, instead of one unit per spell.
        Contract:
            - Static batch dispatch: phase membership is known up front, so
              spells are partitioned into contiguous chunks (one unit per
              chunk) rather than streamed as per-spell queue items. This
              cuts per-phase Future/queue/wakeup overhead by the chunk
              factor while preserving barrier semantics exactly (the phase
              completes when all chunks complete).
            - `chunk_multiplier > 1` requests finer granularity than the
              worker count so the shared queue load-balances heterogeneous
              per-spell costs (a worker that drew a cheap chunk pulls the
              next one instead of idling at the barrier). Measured on the
              29-class gauntlet graph at workers=5: multiplier 2 cut the
              plan_group barrier wall 5.22 -> 4.42ms and load skew
              2.46x -> 1.52x; multiplier 4 over-fragmented (busy time
              inflated by cross-thread contention). Keep 1 for phases whose
              per-spell work is small or homogeneous.
            - The multiplier is ignored at `workers == 1`: with no
              parallelism there is nothing to balance and the extra chunks
              are pure dispatch tax (measured by the bind/compiler lane as
              +1-1.6ms on workers=1 cold setup before this gate).
            - Unit shape: `label="<phase_name>:chunk<i>"`,
              `metadata={"phase", "chunk_index", "spell_ids"}`.
        Args:
            scheduler: Scheduler creating units of work.
            phase_name: Phase label prefix and metadata phase value.
            spells: Ordered spell batch for this phase.
            spell_runner: Callable executing the phase step(s) for one spell.
            chunk_multiplier: Chunk-granularity factor (>= 1) over workers.
        Returns:
            Sequence[UnitOfWork]: Chunk units for the requested phase.
        """
        if not spells:
            return []
        cancel_event = scheduler.cancel_event
        create_unit_of_work = scheduler.create_unit_of_work
        workers = max(1, scheduler.workers)
        effective_multiplier = max(1, chunk_multiplier) if workers > 1 else 1
        chunks = SpellbookCreationSystem._chunk_spells(
            spells,
            workers * effective_multiplier,
        )
        units: List[UnitOfWork] = []
        for index, chunk in enumerate(chunks):
            units.append(
                create_unit_of_work(
                    func=SpellbookCreationSystem._run_spell_chunk,
                    args=(spell_runner, chunk, cancel_event, phase_name),
                    label=f"{phase_name}:chunk{index}",
                    metadata={
                        "phase": phase_name,
                        "chunk_index": index,
                        "spell_ids": [spell.spell_id for spell in chunk],
                    },
                )
            )
        return units

    @staticmethod
    def _is_spell_plan_phase_eligible(
            spell: Spell,
    ) -> bool:
        """
        Purpose:
            Decide whether one spell should enter the live phase-8-to-phase-11
            plan group.

        Contract:
            - Existing-creation spells are not eligible because they do not
              build occurrence graph truth or downstream model/plan/creation
              outputs.
            - Constructed spells require a live Phase 5 root blueprint before
              entering analyzer -> processor -> planner -> codegen creation.
            - Returns only a boolean decision and does not mutate spell state.

        Args:
            spell: Spell candidate being considered for plan-phase scheduling.

        Returns:
            bool:
                True when the spell should run live phases 8-11.
        """
        try:
            is_existing_creation = spell.is_existing_creation
        except AttributeError:
            is_existing_creation = False
        if is_existing_creation:
            return False
        try:
            compiler_artifact = spell._compiler_artifact
        except AttributeError:
            return True
        try:
            return compiler_artifact._root_blueprint_phase5 is not None
        except AttributeError:
            return True

    @staticmethod
    def phase_requirements_factory(
            spellbook: Spellbook,
            scheduler: PhaseScheduler,
            compiler_system: SpellCompilerSystem,
    ) -> Sequence[UnitOfWork]:
        """
        Purpose:
            Build phase-1 requirements units for all local spells.
        Contract:
            - Produces one unit per local spell.
        Args:
            spellbook: Owning Spellbook instance.
            scheduler: Scheduler creating units of work.
            compiler_system: Compiler-system instance used for this run.
        Returns:
            Sequence[UnitOfWork]: Requirements phase units.
        Raises:
            RuntimeError: If the spellbook has already been cleaned.
        """
        return SpellbookCreationSystem._build_per_spell_phase_units(
            spellbook=spellbook,
            scheduler=scheduler,
            compiler_system=compiler_system,
            phase_name="requirements",
            phase_callable_attr="run_phase_requirements",
            args_factory=lambda spell, cancel_event: (spell, cancel_event),
        )

    @staticmethod
    def phase_symbolic_graph_factory(
            spellbook: Spellbook,
            scheduler: PhaseScheduler,
            compiler_system: SpellCompilerSystem,
    ) -> Sequence[UnitOfWork]:
        """
        Purpose:
            Build phase-2 symbolic graph units for all local spells.
        Contract:
            - Produces one unit per local spell.
        Args:
            spellbook: Owning Spellbook instance.
            scheduler: Scheduler creating units of work.
            compiler_system: Compiler-system instance used for this run.
        Returns:
            Sequence[UnitOfWork]: Symbolic graph phase units.
        Raises:
            RuntimeError: If the spellbook has already been cleaned.
        """
        return SpellbookCreationSystem._build_per_spell_phase_units(
            spellbook=spellbook,
            scheduler=scheduler,
            compiler_system=compiler_system,
            phase_name="symbolic_graph",
            phase_callable_attr="run_phase_symbolic_graph",
            args_factory=lambda spell, cancel_event: (spell, cancel_event),
        )

    @staticmethod
    def phase_requirements_symbolic_factory(
            spellbook: Spellbook,
            scheduler: PhaseScheduler,
            compiler_system: SpellCompilerSystem,
    ) -> Sequence[UnitOfWork]:
        """
        Purpose:
            Build fused phase-1+2 units: one chunked unit stream where each
            spell runs requirements and then its symbolic graph back-to-back.
        Contract:
            - Fusion legality: phase 2 consumes only the SAME spell's
              phase-1 requirements (`artifact._requirements`) and never
              reads other spells, so no cross-spell barrier is required
              between phases 1 and 2.
            - Produces at most `scheduler.workers` chunk units; per spell,
              `run_phase_requirements` then `run_phase_symbolic_graph`
              execute sequentially with the run cancel event threaded
              through both, preserving each phase's cooperative-cancellation
              checks.
            - Returns an empty list when no local spells exist.
        Args:
            spellbook: Owning Spellbook instance.
            scheduler: Scheduler creating units of work.
            compiler_system: Compiler-system instance used for this run.
        Returns:
            Sequence[UnitOfWork]: Fused requirements+symbolic chunk units.
        Raises:
            RuntimeError: If the spellbook has already been cleaned.
        """
        spellbook.check_cleaned()
        spells = spellbook._spells
        if not spells:
            return []

        cancel_event = scheduler.cancel_event
        run_requirements = compiler_system.run_phase_requirements
        run_symbolic = compiler_system.run_phase_symbolic_graph

        def _spell_runner(spell: Spell) -> None:
            run_requirements(spell, cancel_event)
            run_symbolic(spell, cancel_event)

        return SpellbookCreationSystem._build_chunked_phase_units(
            scheduler=scheduler,
            phase_name="requirements_symbolic",
            spells=list(spells.values()),
            spell_runner=_spell_runner,
        )

    @staticmethod
    def phase_local_frame_factory(
            spellbook: Spellbook,
            scheduler: PhaseScheduler,
            compiler_system: SpellCompilerSystem,
    ) -> Sequence[UnitOfWork]:
        """
        Purpose:
            Build phase-3 local frame units for all local spells.
        Contract:
            - Produces one unit per local spell.
        Args:
            spellbook: Owning Spellbook instance.
            scheduler: Scheduler creating units of work.
            compiler_system: Compiler-system instance used for this run.
        Returns:
            Sequence[UnitOfWork]: Local frame phase units.
        Raises:
            RuntimeError: If the spellbook has already been cleaned.
        """
        # Pass-scoped memo shared by every phase-3 unit in this pass: the
        # candidate index over the live spell pool is built once and reused
        # by all per-spell resolutions (same lifetime contract as the
        # phase-4 `validation_pass_cache` below: dies with the units).
        resolution_pass_cache: Dict[str, Any] = {}
        return SpellbookCreationSystem._build_per_spell_phase_units(
            spellbook=spellbook,
            scheduler=scheduler,
            compiler_system=compiler_system,
            phase_name="local_frame",
            phase_callable_attr="run_phase_local_frame",
            args_factory=lambda spell, cancel_event: (
                spellbook,
                spell,
                cancel_event,
                resolution_pass_cache,
            ),
        )

    @staticmethod
    def phase_validation_factory(
            spellbook: Spellbook,
            scheduler: PhaseScheduler,
            compiler_system: SpellCompilerSystem,
    ) -> Sequence[UnitOfWork]:
        """
        Purpose:
            Build phase-4 validation units for all local spells.
        Contract:
            - Produces one unit per local spell.
            - Creates one pass-scoped memo dict shared by every unit in this
              pass so strategies can reuse pass-invariant artifacts (for
              example the frame-wide binding graph) instead of rebuilding them
              per spell. The dict dies with the units, so its lifetime IS the
              pass and no invalidation protocol exists.
        Args:
            spellbook: Owning Spellbook instance.
            scheduler: Scheduler creating units of work.
            compiler_system: Compiler-system instance used for this run.
        Returns:
            Sequence[UnitOfWork]: Validation phase units.
        Raises:
            RuntimeError: If the spellbook has already been cleaned.
        """
        validation_pass_cache: Dict[str, Any] = {}
        return SpellbookCreationSystem._build_per_spell_phase_units(
            spellbook=spellbook,
            scheduler=scheduler,
            compiler_system=compiler_system,
            phase_name="validation",
            phase_callable_attr="run_phase_validation",
            args_factory=lambda spell, cancel_event: (
                spellbook,
                spell,
                cancel_event,
                validation_pass_cache,
            ),
        )

    @staticmethod
    def phase_root_blueprints_factory(
            spellbook: Spellbook,
            scheduler: PhaseScheduler,
            compiler_system: SpellCompilerSystem,
            conduit_id: str,
    ) -> Sequence[UnitOfWork]:
        """
        Purpose:
            Build frame-scoped phase-5 root-blueprints unit(s).
        Contract:
            - Returns empty when no local spells exist.
            - Uses lead spell for frame-scoped blueprint build.
        Args:
            spellbook: Owning Spellbook instance.
            scheduler: Scheduler creating units of work.
            compiler_system: Compiler-system instance used for this run.
            conduit_id: Conduit scope id.

        Returns:
            Sequence[UnitOfWork]: Root-blueprints phase units.
        Raises:
            RuntimeError: If the spellbook has already been cleaned.
        """
        spellbook.check_cleaned()
        if not spellbook._spells:
            return []

        lead_spell = next(iter(spellbook._spells.values()))
        return [
            scheduler.create_unit_of_work(
                func=compiler_system.run_phase_root_blueprints,
                args=(spellbook, lead_spell, conduit_id, scheduler.cancel_event,),
                label=f"root_blueprints:{lead_spell.spell_id}",
                metadata={
                    "phase": "root_blueprints",
                    "spell_id": lead_spell.spell_id,
                    "scope": "frame",
                },
            )
        ]

    @staticmethod
    def phase_occurrence_plan_factory(
            spellbook: Spellbook,
            scheduler: PhaseScheduler,
            compiler_system: SpellCompilerSystem,
            conduit_id: str,
    ) -> Sequence[UnitOfWork]:
        """
        Purpose:
            Build phase-8 occurrence-plan units for all local spells.
        Contract:
            - Returns empty when no local spells exist.
            - Produces one unit per local spell otherwise.
        Args:
            spellbook: Owning Spellbook instance.
            scheduler: Scheduler creating units of work.
            conduit_id: Conduit scope id.
        Returns:
            Sequence[UnitOfWork]: Occurrence-plan phase units.
        Raises:
            RuntimeError: If the spellbook has already been cleaned.
        """
        spellbook.check_cleaned()
        eligible_spells = [
            spell
            for spell in spellbook._spells.values()
            if SpellbookCreationSystem._is_spell_plan_phase_eligible(spell)
        ]
        if not eligible_spells:
            return []

        cancel_event = scheduler.cancel_event
        create_unit_of_work = scheduler.create_unit_of_work
        phase_func = compiler_system.run_phase_occurrence_plan
        # Pass-scoped memo shared by every phase-8 unit in this pass: the
        # full-pool spell walk and the graph-wide shape rows are built once
        # and reused by all per-spell analyses (same lifetime contract as
        # the phase-3/phase-4 pass caches: dies with the units).
        analysis_pass_cache: Dict[str, Any] = {}
        units: List[UnitOfWork] = []
        for spell in eligible_spells:
            spell_id = spell.spell_id
            units.append(
                create_unit_of_work(
                    func=phase_func,
                    args=(spellbook, spell, analysis_pass_cache),
                    label=f"occurrence_plan:{spell_id}",
                    metadata={
                        "phase": "occurrence_plan",
                        "spell_id": spell_id,
                    },
                )
            )
        return units

    @staticmethod
    def phase_injection_plan_factory(
            spellbook: Spellbook,
            scheduler: PhaseScheduler,
            compiler_system: SpellCompilerSystem,
            conduit_id: str,
    ) -> Sequence[UnitOfWork]:
        """
        Purpose:
            Build phase-9 injection-plan units for all local spells.
        Contract:
            - Returns empty when no local spells exist.
            - Produces one unit per local spell otherwise.
        Args:
            spellbook: Owning Spellbook instance.
            scheduler: Scheduler creating units of work.
            conduit_id: Conduit scope id.
            compiler_system: Compiler-system instance used for this run.
        Returns:
            Sequence[UnitOfWork]: Injection-plan phase units.
        Raises:
            RuntimeError: If the spellbook has already been cleaned.
        """
        spellbook.check_cleaned()
        eligible_spells = [
            spell
            for spell in spellbook._spells.values()
            if SpellbookCreationSystem._is_spell_plan_phase_eligible(spell)
        ]
        if not eligible_spells:
            return []

        create_unit_of_work = scheduler.create_unit_of_work
        phase_func = compiler_system.run_phase_injection_plan
        units: List[UnitOfWork] = []
        for spell in eligible_spells:
            spell_id = spell.spell_id
            units.append(
                create_unit_of_work(
                    func=phase_func,
                    args=(spell,),
                    label=f"injection_plan:{spell_id}",
                    metadata={
                        "phase": "injection_plan",
                        "spell_id": spell_id,
                    },
                )
            )
        return units

    @staticmethod
    def phase_patch_maps_factory(
            spellbook: Spellbook,
            scheduler: PhaseScheduler,
            compiler_system: SpellCompilerSystem,
            conduit_id: str,
    ) -> Sequence[UnitOfWork]:
        """
        Purpose:
            Build phase-10 patch-map units for all local spells.
        Contract:
            - Returns empty when no local spells exist.
            - Produces one unit per local spell otherwise.
        Args:
            spellbook: Owning Spellbook instance.
            scheduler: Scheduler creating units of work.
            conduit_id: Conduit scope id.
            compiler_system: Compiler-system instance used for this run.
        Returns:
            Sequence[UnitOfWork]: Patch-maps phase units.
        Raises:
            RuntimeError: If the spellbook has already been cleaned.
        """
        spellbook.check_cleaned()
        eligible_spells = [
            spell
            for spell in spellbook._spells.values()
            if SpellbookCreationSystem._is_spell_plan_phase_eligible(spell)
        ]
        if not eligible_spells:
            return []

        create_unit_of_work = scheduler.create_unit_of_work
        phase_func = compiler_system.run_phase_patch_maps
        units: List[UnitOfWork] = []
        for spell in eligible_spells:
            spell_id = spell.spell_id
            units.append(
                create_unit_of_work(
                    func=phase_func,
                    args=(spell,),
                    label=f"patch_maps:{spell_id}",
                    metadata={
                        "phase": "patch_maps",
                        "spell_id": spell_id,
                    },
                )
            )
        return units

    @staticmethod
    def phase_execution_plan_factory(
            spellbook: Spellbook,
            scheduler: PhaseScheduler,
            compiler_system: SpellCompilerSystem,
            conduit_id: str,
    ) -> Sequence[UnitOfWork]:
        """
        Purpose:
            Build phase-11 execution-plan units for all local spells.
        Contract:
            - Returns empty when no local spells exist.
            - Produces one unit per local spell otherwise.
        Args:
            spellbook: Owning Spellbook instance.
            scheduler: Scheduler creating units of work.
            conduit_id: Conduit scope id.
            compiler_system: Compiler-system instance used for this run.
        Returns:
            Sequence[UnitOfWork]: Execution-plan phase units.
        Raises:
            RuntimeError: If the spellbook has already been cleaned.
        """
        spellbook.check_cleaned()
        eligible_spells = [
            spell
            for spell in spellbook._spells.values()
            if SpellbookCreationSystem._is_spell_plan_phase_eligible(spell)
        ]
        if not eligible_spells:
            return []

        create_unit_of_work = scheduler.create_unit_of_work
        phase_func = compiler_system.run_phase_execution_plan
        units: List[UnitOfWork] = []
        for spell in eligible_spells:
            spell_id = spell.spell_id
            units.append(
                create_unit_of_work(
                    func=phase_func,
                    args=(spellbook, spell),
                    label=f"execution_plan:{spell_id}",
                    metadata={
                        "phase": "execution_plan",
                        "spell_id": spell_id,
                    },
                )
            )
        return units

    @staticmethod
    def phase_plan_group_factory(
            spellbook: Spellbook,
            scheduler: PhaseScheduler,
            compiler_system: SpellCompilerSystem,
            conduit_id: str,
    ) -> Sequence[UnitOfWork]:
        """
        Purpose:
            Build fused phase-8-to-11 units: one chunked unit stream where
            each eligible spell runs occurrence analysis, model, plan, and
            codegen creation back-to-back.
        Contract:
            - Fusion legality: every step consumes only the SAME spell's
              previous artifact; none of the four phase implementations read
              other spells (phase 8's spellbook parameter is documented as
              an unused compatibility argument). The historical inter-phase
              barriers carried no data contract.
            - Eligibility matches the historical per-phase gates exactly
              (`_is_spell_plan_phase_eligible`); existing-creation spells
              skip the whole fused sequence as before.
            - A spell failing mid-sequence raises its original exception
              unchanged; its remaining fused steps do not run, and the run's
              cancel event stops other chunks at spell granularity —
              equivalent fail-fast posture to the historical four-barrier
              layout, with slightly better isolation.
            - Produces at most `scheduler.workers` chunk units.
            - Returns an empty list when no eligible spells exist.
        Args:
            spellbook: Owning Spellbook instance.
            scheduler: Scheduler creating units of work.
            compiler_system: Compiler-system instance used for this run.
            conduit_id: Conduit scope id (carried for signature parity).
        Returns:
            Sequence[UnitOfWork]: Fused plan-group chunk units.
        Raises:
            RuntimeError: If the spellbook has already been cleaned.
        """
        spellbook.check_cleaned()
        eligible_spells = [
            spell
            for spell in spellbook._spells.values()
            if SpellbookCreationSystem._is_spell_plan_phase_eligible(spell)
        ]
        if not eligible_spells:
            return []

        run_occurrence = compiler_system.run_phase_occurrence_plan
        run_injection = compiler_system.run_phase_injection_plan
        run_patch_maps = compiler_system.run_phase_patch_maps
        run_execution = compiler_system.run_phase_execution_plan

        # Pass-scoped memo shared by every fused plan-group chunk in this
        # pass (see `phase_occurrence_plan_factory` for the contract).
        analysis_pass_cache: Dict[str, Any] = {}

        def _spell_runner(spell: Spell) -> None:
            run_occurrence(spellbook, spell, analysis_pass_cache)
            run_injection(spell)
            run_patch_maps(spell)
            run_execution(spellbook, spell)

        # Fused plan sequences have strongly heterogeneous per-spell costs
        # (deep roots cost multiples of leaves: e.g. RequestRoot ~2.3ms vs
        # ~0.1ms leaves on the gauntlet graph), so this phase requests finer
        # chunks than workers and lets the shared queue level the load. See
        # `PLAN_GROUP_CHUNK_MULTIPLIER` for the measurement basis.
        return SpellbookCreationSystem._build_chunked_phase_units(
            scheduler=scheduler,
            phase_name="plan_group",
            spells=eligible_spells,
            spell_runner=_spell_runner,
            chunk_multiplier=SpellbookCreationSystem.PLAN_GROUP_CHUNK_MULTIPLIER,
        )

    @staticmethod
    def phase_system_validation_factory(
            spellbook: Spellbook,
            scheduler: PhaseScheduler,
            compiler_system: SpellCompilerSystem,
            conduit_id: str,
    ) -> Sequence[UnitOfWork]:
        """
        Purpose:
            Build frame-scoped system-validation phase units.
        Contract:
            - Returns empty when no local spells exist.
            - Uses lead spell for frame-scoped system validation.
        Args:
            spellbook: Owning Spellbook instance.
            scheduler: Scheduler creating units of work.
            conduit_id: Conduit scope id.
            compiler_system: Compiler-system instance used for this run.
        Returns:
            Sequence[UnitOfWork]: System-validation phase units.
        Raises:
            RuntimeError: If the spellbook has already been cleaned.
        """
        spellbook.check_cleaned()
        if not spellbook._spells:
            return []

        lead_spell = next(iter(spellbook._spells.values()))
        return [
            scheduler.create_unit_of_work(
                func=compiler_system.run_phase_system_validation,
                args=(spellbook, lead_spell, conduit_id, scheduler.cancel_event,),
                label=f"system_validation:{lead_spell.spell_id}",
                metadata={
                    "phase": "system_validation",
                    "spell_id": lead_spell.spell_id,
                    "scope": "frame",
                },
            )
        ]

    @staticmethod
    def phase_change_control_factory(
            spellbook: Spellbook,
            scheduler: PhaseScheduler,
            compiler_system: SpellCompilerSystem,
            conduit_id: str,
    ) -> Sequence[UnitOfWork]:
        """
        Purpose:
            Build frame-scoped change-control phase units.
        Contract:
            - Returns empty when no local spells exist.
            - Uses lead spell for frame-scoped change-control wiring.
        Args:
            spellbook: Owning Spellbook instance.
            scheduler: Scheduler creating units of work.
            conduit_id: Conduit scope id.
            compiler_system: Compiler-system instance used for this run.
        Returns:
            Sequence[UnitOfWork]: Change-control phase units.
        Raises:
            RuntimeError: If the spellbook has already been cleaned.
        """
        spellbook.check_cleaned()
        if not spellbook._spells:
            return []

        lead_spell = next(iter(spellbook._spells.values()))
        return [
            scheduler.create_unit_of_work(
                func=compiler_system.run_phase_change_control,
                args=(spellbook, lead_spell, conduit_id,),
                label=f"change_control:{lead_spell.spell_id}",
                metadata={
                    "phase": "change_control",
                    "spell_id": lead_spell.spell_id,
                    "scope": "frame",
                },
            )
        ]


_EXISTING_OVERRIDE_MESSAGE = (
    "Overrides were supplied for a spell instance that already exists. "
    "Shared instances cannot be overridden after creation."
)


def _load_meld_execution_error_type() -> Any:
    """Return the live MeldExecutionError type without a module-level import cycle."""
    from melder.utilities.custom_exceptions.meld_execution_error import (
        MeldExecutionError,
    )
    return MeldExecutionError


def _make_cell(value: Any) -> Any:
    """Build one closure cell for cached-function reconstruction."""
    def inner() -> Any:
        return value
    return inner.__closure__[0]




