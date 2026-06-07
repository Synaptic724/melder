import threading
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
from melder.aether.spellbook.spell_compiler.spell_examiner.profiles.binding_profile import (
    ClassBindingProfile,
)
from melder.aether.spellbook.spell_compiler.system.system_diagnostic import (
    SystemDiagnostic,
    SystemDiagnosticSeverity,
)
from melder.utilities.custom_exceptions.phase_execution_error import PhaseExecutionError
from melder.utilities.custom_exceptions.spellbook_validation_error import SpellbookValidationError
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.general_helpers import EnumHelpers
from melder.utilities.helpers.id_builder import IDBuilder
from melder.aether.spellbook.spell_compiler.spell_examiner.profiles.detailed_profile import (
    SpellDetailedProfile,
)
from melder.aether.spellbook.spell_compiler.spell_examiner.profiles.general_profile import (
    SpellGeneralProfile,
)
from melder.utilities.synchronization.cancellation_event_signal import CancellationEventSignal
from melder.utilities.synchronization.phase_scheduler import PhaseScheduler
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state_change_reason import SpellStateChangeReason
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

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
        - Owns conjure-only orchestration helpers (hook flow, policy gate,
          disposal metadata pass, and conduit ownership stamping).
        - Cleanup is deterministic and idempotent; once cleaned, this instance
          cannot be reused.

    Threading:
        Spellbook is expected to hold its own lock while invoking this system.
        This class uses an internal lock only to make "cleanup()" idempotent
        under concurrent teardown calls.
    """

    __melder_internal__: ClassVar[object] = _mrg.sentinel
    _DEFAULT_ROOT_CONDUIT_NAME: ClassVar[str] = "default"
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
            - Executes structural phases and disposal metadata wiring.
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
        SpellbookCreationSystem.define_disposal_metadata_on_spells(spellbook)

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
            - Reads dynamic/automatic posture from the caller and AOT/JIT
              posture from configuration.
            - Builds exact-match, mixed, and miss sets from live spell ids and
              cached spell ids.
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
        full_ahead_of_time_compilation = (
            SpellbookCreationSystem._read_full_ahead_of_time_compilation(
                spellbook=spellbook,
                context_name="_build_conjure_cache_state",
            )
        )
        caching_enabled = spellbook._system_caching_enabled_in_aether()
        live_spell_ids = set(spellbook._spell_id_pool.keys())
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
        is_full_hit = bool(live_spell_ids) and live_spell_ids == cached_spell_ids
        is_mixed = bool(matched_spell_ids) and bool(missing_spell_ids)
        is_full_miss = not is_full_hit and not is_mixed
        return {
            "caching_enabled": caching_enabled,
            "caching_system": caching_system,
            "dynamic_mode": bool(dynamic),
            "automatic_mode": not bool(dynamic),
            "full_ahead_of_time_compilation": full_ahead_of_time_compilation,
            "jit_mode": not full_ahead_of_time_compilation,
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
            creation_context_factory = spell._creation_context_factory
            if creation_context_factory is None:
                raise RuntimeError("Spell has no CreationContextFactory.")
            creation_gate, creation_gate_index_id = (
                creation_context_factory._resolve_runtime_gate_for_spell(spell)
            )
            CreationContext.load_cached_bundle(
                spell=spell,
                cached_codegen=spell_payload,
                dynamic_environment=spell._dynamic_environment,
                creation_gate=creation_gate,
                creation_gate_index_id=creation_gate_index_id,
                publish=True,
            )
            spell.resolution_complete = True
            spell.resolution_required = False
            loaded_spell_ids.add(spell_id)
        return loaded_spell_ids

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
            aetheric_frame_name=spellbook._aetheric_frame,
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
            spellbook._aetheric_frame
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
        return spellbook._aether._get_existing_frame(spellbook._aetheric_frame)

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
        from melder.aether.conduit.meld.creation_context.creation_context_cache_codec import (
            load_creation_context,
        )
        for spell_id in tuple(cache_state.get("live_spell_ids", ())):
            spell = spellbook._spell_id_pool.get(spell_id)
            if spell is None:
                continue
            package = caching_system.get_spell_payload(spell_id)
            if package is None:
                spell.resolution_required = True
                continue
            try:
                load_creation_context(spell, package, publish=True)
                spell.resolution_complete = True
                spell.resolution_required = False
            except Exception as exc:
                if spellbook._logger is not None:
                    spellbook._logger.error(
                        f"Cache reload failed for spell_id={spell_id}; "
                        f"falling back to JIT resolution: {exc}",
                        "_load_cached_creation_contexts_for_conjure",
                        exc_info=True,
                    )
                spell.resolution_required = True

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
            - Emits the current in-memory cache (which may be empty) to disk.
            - Never propagates cache failures into the conjure path.

        Args:
            spellbook: Owning Spellbook whose conduit cache should be emitted.

        Returns:
            None.
        """
        if not spellbook._system_caching_enabled_in_aether():
            return
        try:
            spellbook._get_or_create_caching_system().emit()
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

        if system_state == SystemState.automatic:
            spellbook._logger.error(
                "Dynamic policy requested while system_state is automatic "
                f"(policy={policy_enum}, dynamic={dynamic}, "
                f"system_state={system_state}).",
                "_check_system_state",
                exc_info=True,
            )
            raise RuntimeError(
                "Cannot enable dynamic conduit mode in automatic system_state. "
                f"(policy={policy_enum}, dynamic={dynamic}, system_state={system_state}). "
                "Set system_state to 'dynamic' in the configuration or call conjure(dynamic=False)."
            )

    @staticmethod
    def define_disposal_metadata_on_spells(spellbook: Spellbook) -> None:
        """
        Purpose:
            Precompute spell disposal metadata from configured method names.
        Contract:
            - Class-bound spells receive matched disposal methods.
            - Non-class spells or missing profiles receive empty metadata.
            - Updates "disposal_method_names" and "has_disposal_methods".
        Args:
            spellbook: Owning Spellbook instance.
        Returns:
            None.
        Raises:
            Exception: Propagates configuration property access failures.
        """
        if spellbook._configuration is None:
            raise RuntimeError(
                "Cannot define disposal metadata without a configuration. "
                f"(spellbook={spellbook})"
            )
        target_methods = list(spellbook._configuration.get_property("disposal_method_names"))
        if len(target_methods) == 0:
            return

        for spell in spellbook._spells.values():
            matched: List[str] = []
            profile = spell.profile
            binding_profile = profile
            if isinstance(profile, (SpellGeneralProfile, SpellDetailedProfile)):
                binding_profile = profile.binding_profile
            if isinstance(binding_profile, ClassBindingProfile):
                method_names = set(binding_profile.method_names)
                for method_name in target_methods:
                    if method_name in method_names:
                        matched.append(method_name)
            spell.disposal_method_names = matched
            spell.has_disposal_methods = bool(matched)

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
        full_ahead_of_time_compilation = (
            SpellbookCreationSystem._read_full_ahead_of_time_compilation(
                spellbook=spellbook,
                context_name="_define_conduit_into_spells",
            )
        )
        caching_enabled = spellbook._resolve_system_caching_enabled()
        resolution_required: bool = not full_ahead_of_time_compilation
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
                    spell.spell_index._set_owner_conduit_id(conduit._id)
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
    def _read_full_ahead_of_time_compilation(
            *,
            spellbook: Spellbook,
            context_name: str,
    ) -> bool:
        """
        Purpose:
            Read `full_ahead_of_time_compilation` from the configuration.
        Contract:
            - Defaults to `True` when configuration does not expose a value.
            - Accepts only boolean configuration values.
            - Logs retrieval failures and falls back to `True`.
        Args:
            spellbook: Owning Spellbook instance.
            context_name: Logging context for fallback diagnostics.
        Returns:
            bool: True for AOT mode; False for JIT/deferred mode.
        Raises:
            None.
        """
        full_ahead_of_time_compilation: bool = True
        configuration = spellbook._configuration
        if configuration is None:
            return full_ahead_of_time_compilation
        try:
            configured_value = configuration.get_property(
                "full_ahead_of_time_compilation"
            )
            if configured_value is None:
                return full_ahead_of_time_compilation
            if not isinstance(configured_value, bool):
                raise TypeError(
                    "full_ahead_of_time_compilation must be a bool. "
                    f"Got {type(configured_value).__name__}."
                )
            return configured_value
        except KeyError:
            return full_ahead_of_time_compilation
        except Exception as exc:
            spellbook._logger.error(
                f"Failed to read full_ahead_of_time_compilation; defaulting to True: {exc}",
                context_name,
                exc_info=True,
            )
            return full_ahead_of_time_compilation

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
                f"_get_conjure_hook_map failed: {exc}",
                "_get_conjure_hook_map",
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
            - Runs plan phases only when foundational phases have no errors and
              `full_ahead_of_time_compilation` is enabled.
            - Cleans per-spell phase artifacts before returning.
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

        if force_skip_plan_phases is None:
            full_ahead_of_time_compilation = (
                SpellbookCreationSystem._read_full_ahead_of_time_compilation(
                    spellbook=spellbook,
                    context_name="_run_resolution_phases_for_conduit",
                )
            )
            resolved_skip_plan_phases = not full_ahead_of_time_compilation
        else:
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
            return results

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

        scheduler.register_phase(
            "occurrence_plan",
            lambda: [] if _should_skip_plan_phases() else SpellbookCreationSystem.phase_occurrence_plan_factory(
                spellbook, scheduler, compiler_system, conduit_id
            ),
        )
        scheduler.register_phase(
            "injection_plan",
            lambda: [] if _should_skip_plan_phases() else SpellbookCreationSystem.phase_injection_plan_factory(
                spellbook, scheduler, compiler_system, conduit_id
            ),
        )
        scheduler.register_phase(
            "patch_maps",
            lambda: [] if _should_skip_plan_phases() else SpellbookCreationSystem.phase_patch_maps_factory(
                spellbook, scheduler, compiler_system, conduit_id
            ),
        )
        scheduler.register_phase(
            "execution_plan",
            lambda: [] if _should_skip_plan_phases() else SpellbookCreationSystem.phase_execution_plan_factory(
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
            Construct a phase scheduler bound to the supplied Spellbook/configuration.
        Contract:
            - Creates one scheduler instance for a single orchestration run.
        Args:
            spellbook: Owning Spellbook instance.
            phase_scheduler_cls: Scheduler class to instantiate.
        Returns:
            PhaseScheduler: New scheduler instance.
        Raises:
            Exception: Propagates constructor failures from `phase_scheduler_cls`.
        """
        return phase_scheduler_cls(
            spellbook=spellbook,
            configuration=spellbook._configuration,
        )

    @staticmethod
    def _cleanup_phase_scheduler(
            spellbook: Spellbook,
            scheduler: PhaseScheduler,
            context_name: str,
    ) -> None:
        """
        Purpose:
            Execute scheduler cleanup with standardized error logging.
        Contract:
            - Never raises cleanup failures.
            - Emits context-aware error logs on cleanup exceptions.
        Args:
            spellbook: Owning Spellbook instance.
            scheduler: Scheduler to clean up.
            context_name: Logging context label.
        Returns:
            None.
        Raises:
            None.
        """
        try:
            scheduler.cleanup()
        except Exception:
            spellbook._logger.error(
                f"PhaseScheduler.cleanup() raised during {context_name}",
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
        scheduler.register_phase(
            "requirements",
            lambda: SpellbookCreationSystem.phase_requirements_factory(
                spellbook, scheduler, compiler_system
            ),
        )
        scheduler.register_phase(
            "symbolic_graph",
            lambda: SpellbookCreationSystem.phase_symbolic_graph_factory(
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
            Build one unit-of-work per local spell for repeated per-spell phases.
        Contract:
            - Returns an empty list when no local spells exist.
            - Preserves existing label and metadata shape:
              `label="<phase_name>:<spell_id>"`,
              `metadata={"phase": <phase_name>, "spell_id": <spell_id>}`.
            - Uses the supplied compiler-system front method for all units.
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
        create_unit_of_work = scheduler.create_unit_of_work
        units: List[UnitOfWork] = []
        phase_func = getattr(compiler_system, phase_callable_attr)
        for spell in spells.values():
            spell_id = spell.spell_id
            units.append(
                create_unit_of_work(
                    func=phase_func,
                    args=args_factory(spell, cancel_event),
                    label=f"{phase_name}:{spell_id}",
                    metadata={
                        "phase": phase_name,
                        "spell_id": spell_id,
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
        Args:
            spellbook: Owning Spellbook instance.
            scheduler: Scheduler creating units of work.
            compiler_system: Compiler-system instance used for this run.
        Returns:
            Sequence[UnitOfWork]: Validation phase units.
        Raises:
            RuntimeError: If the spellbook has already been cleaned.
        """
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
        units: List[UnitOfWork] = []
        for spell in eligible_spells:
            spell_id = spell.spell_id
            units.append(
                create_unit_of_work(
                    func=phase_func,
                    args=(spellbook, spell),
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




