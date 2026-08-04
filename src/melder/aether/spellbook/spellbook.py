import threading
import time
from collections.abc import Generator, Iterable, Mapping, Sequence
from contextlib import contextmanager
from pathlib import Path
from types import MappingProxyType, ModuleType, TracebackType
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
)

from melder.aether.aether import Aether
from melder.aether.aetheric_frame.aetheric_frame_configuration import (
    AethericFrameConfiguration,
)

# Melder Imports
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeTransactionType,
)
from melder.aether.aetheric_frame.dev_ops.devops_identity import (
    DevopsIdentity,
)
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state_change_reason import (
    SpellStateChangeReason,
)
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_validity import (
    SpellValidity,
)
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.aether.spellbook.bind.bind import Bind
from melder.aether.spellbook.bind.scan import Scan
from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)
from melder.aether.spellbook.configuration.system_state import SystemState
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell import Spell
from melder.aether.spellbook.spellbook_creation_system import SpellbookCreationSystem
from melder.nexus.nexus import Nexus
from melder.utilities.caching_system.caching_system import CachingSystem
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.general_helpers import EnumHelpers, SpellInputUtils
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.helpers.init_helpers import InitHelpers
from melder.utilities.synchronization.phase_scheduler import PhaseScheduler

if TYPE_CHECKING:
    from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.transaction_mediator import (
        TransactionMediator,
    )
    from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_states import (
        SpellSystemStates,
    )
    from melder.aether.conduit.conduit import Conduit
    from melder.crystallizer.crystallizer import Crystallizer
    from melder.mutation_research.mutation_research import MutationResearch
    from melder.utilities.logger.safe_logger import SafeLogger
    from melder.utilities.synchronization.unit_of_work import UnitOfWork

#region Spellbook

class Spellbook(Cleanable):
    """
    Public API

    The `Spellbook` is the primary local authority for spell binding, spell
    lookup, configuration ownership, and conduit conjuration inside one
    aetheric frame. It is the object users interact with when they register
    spells, freeze configuration, begin binding transactions, and conjure the
    conduit that will execute against those registrations.

    Contract:
    - Owns the local spell registries, lookup maps, contracted-spell mirrors,
      version caches, validation system, and frame-local configuration state
      for one spellbook instance.
    - Coordinates with the shared `Aether` for frame creation, frame-level
      configuration sharing, and system-state services.
    - Admits binding and contract changes through explicit transaction windows
      rather than allowing uncontrolled registry mutation.
    - Supports exactly one conjured conduit per spellbook instance.
    - Becomes unusable after cleanup completes.

    Warning about `aetheric_frame`:
    - `aetheric_frame` is not a cosmetic namespace. Using it joins this
      Spellbook to shared frame-level configuration and visibility state inside
      Aether.
    - Reusing a frame means sharing spell visibility, configuration posture,
      and change-control surfaces with other participants in that frame.
    - Use the default frame only when the shared scope is intentional.

    Responsibilities:
    - Hold and register local spells through `bind()` and `scan()`.
    - Maintain local and contracted spell lookup surfaces.
    - Freeze and bind configuration into Aether at the correct lifecycle point.
    - Conjure and own the runtime `Conduit` for this spellbook.
    - Coordinate change-control, staged binding metadata, and contracted link state.

    Args:
        aetheric_frame (str, optional):
            Shared frame name used to bind this Spellbook to one Aether frame.
            Defaults to `"default"`. If the frame does not exist yet, Spellbook
            creates it.
        configuration (Optional[SpellbookConfiguration]):
            Optional pre-configured configuration instance to reuse for this
            frame.

    Threading / Concurrency:
        - Creates an internal `RLock` and uses it to guard registry mutation,
          cleanup staging, and transaction-sensitive local state.
        - Relies on Aether and downstream managers for cross-object coordination.

    Lifecycle / Cleanup:
        - This object owns local registries, contracted registries, validators, configuration,
and logging.
        - Cleanup is staged so component teardown happens under the lock first
          and high-level references are dropped afterward.

    Notes:
        - SpellbookConfiguration is locked automatically once the spellbook crosses into
          the conjured runtime path.
        - Frame-wide rich Spellbook configuration reuse is explicit and only
          occurs when the frame posture permits it and a shared rich config
          object already exists on the frame.

    Registration:
        MELDER KERNEL - guarded. The user DRIVES a Spellbook through its public API
        (bind/scan/conjure plus the transaction-backed SpellIndex verbs) but can never
        `bind()` the Spellbook itself. `access = "public"` reflects that hands-on
        driving.

    Subsystem Context:
        The primary front door of the `aether/spellbook` binding surface. It
        owns the local spell registries and O(1) spell-id maps, runs the
        SpellCompiler phase pipeline through `PhaseScheduler`, and conjures
        exactly ONE `Conduit` per instance. `bind()` reflects a user object into
        a `SpellIndex` (stable ULID identity + active selected spell) plus a
        `Spell` (the bind-time metadata record), and it delegates the
        conjure-only orchestration - hook flow, the `check_system_state`
        policy/posture gate, conduit-ownership stamping - to
        `SpellbookCreationSystem`. `Existence` / `SpellType` /
        `SpellbookConfiguration` are the value and policy surfaces it binds
        against.

    System Context:
        The Spellbook layer of the canonical boot order
        `Aether|AetherUtilitySystem -> Crystallizer -> MutationResearch ->
        Nexus -> AethericFrame -> Spellbook -> Conduit|Ward`. It runs AFTER a
        frame exists and BEFORE/DURING conjure, which is why joining a frame is a
        real coupling rather than a cosmetic namespace (see the aetheric_frame
        warning above): reusing a frame shares spell visibility, configuration
        posture, and change-control surfaces with every other participant. The
        `Spell` it produces is the unit of currency every downstream layer keys
        on - the SpellCompiler phases, SpellSystemStates validity, ChangeControl
        dirty-roots, and Meld resolution all resolve through it.

    AGENT_ACCESS: public

    AGENT_PURPOSE:
        access: public. The binding authority. Call bind(...)/scan(...) to register, then
        conjure(...) exactly once to build the root Conduit. Owns the APPLIED SEAMS of the
        transaction-backed SpellIndex verbs - _apply_notch, _apply_add_to_index,
        _apply_remove_from_index - which run inside the held change-control window. The
        PUBLIC verbs are on Conduit (notch_spell, add_to_spell_index,
        remove_from_spell_index): the Conduit admits the transaction because it owns the
        lineage, and Spellbook applies the membership change because it owns the index
        maps. Neither half is callable on its own.
    """
    _aether: ClassVar[Aether] = Aether()
    __slots__ = Cleanable.__slots__ + [
        "__dict__",
        "__weakref__",
        "_aetheric_frame_name",
        "_aetheric_frame",
        "_aetheric_frame_configuration",
        "_bind",
        "_block_all_spells",
        "_conduit",
        "_configuration",
        "_configuration_locked",
        "_binds_before_configuration_count",
        "_conjure_dynamic_hint",
        "_conjured",
        "_cache_emit_required",
        "_caching_enabled",
        "_caching_system",
        "_contracted_spells",
        "_contracted_spells_by_id",
        "_contracted_spell_ids",
        "_contracted_indexes",
        "_id",
        "_lock",
        "_logger",
        "_lookup_contracted_spells",
        "_nexus",
        "_nexus_publish_enabled",
        "_lookup_spells",
        "_pending_binding_frame_keys",
        "_pending_structural_spells",
        "_phase_scheduler",
        "_phase_run_lock",
        "_configured_disposal_method_names",
        "_spell_id_pool",
        "_spell_system_states",
        "_spell_ids",
        "_spellbook_validation_required",
        "_spells",
        "_spells_by_id",
        "_transaction_identity",
        "_whitelist_all_spells",
        "_crystallizer",
        "_mutation_research",
    ]

    def __init__(self, aetheric_frame: str = "default", configuration: SpellbookConfiguration | None = None,
                 logger: Any | None = None):
        """
        Public API

        Initialize a Spellbook with configuration, logging, and spell registries.

        Purpose:
            Provide the primary binding and conjure surface for a single aetheric
            frame and initialize all internal registries needed for spell binding
            and contract management.

        Contract:
            - Initializes local and contracted spell registries and lookup maps.
            - Initializes spell_id maps for O(1) resolution by current version id.
            - Attaches to an Aether frame and configures logging.

        Args:
            aetheric_frame (str):
                Frame name to bind this Spellbook to.
            configuration (Optional[SpellbookConfiguration]):
                Optional configuration to reuse for the frame.
            logger (Optional[Any]):
                Optional logger instance or factory output.

        Raises:
            TypeError: If aetheric_frame is not a string.

        Threading:
            - Creates an internal RLock for subsequent synchronized operations.

        Lifecycle:
            - Owned registries are cleared and nulled during cleanup.

        Returns:
            None.
        """
        super().__init__()

        # Internal state
        self._lock: threading.RLock = threading.RLock()
        self._id: str = IDBuilder.create_id()
        self._nexus: Nexus = Nexus()
        self._conjured = False
        self._cache_emit_required: bool = False
        self._caching_enabled: bool = False
        self._caching_system: CachingSystem | None = None
        self._pending_binding_frame_keys: set[str] = set()
        self._pending_structural_spells: list[Spell] = []
        # Spellbook-owned persistent phase scheduler (lazy): one worker pool
        # reused across every conjure phase group and lazy revalidation run.
        # Created on first phase run; cleaned (sentinels + joins) exactly
        # once in Spellbook cleanup.
        self._phase_scheduler: PhaseScheduler | None = None
        # Serializes phase RUNS on the shared persistent scheduler: the
        # per-run phase registry is scheduler state, so concurrent meld-time
        # revalidations (which do not hold the Spellbook lock) must not
        # interleave register/run/clear cycles. RLock so a thread that
        # already owns a run can re-enter (conjure runs structural then
        # resolution back-to-back). Runs must never be initiated from inside
        # a phase unit (worker thread) - that would deadlock against the
        # owning control thread.
        self._phase_run_lock: threading.RLock = threading.RLock()
        self._configured_disposal_method_names: frozenset[str] | None = None
        self._conduit: Conduit | None = None
        self._nexus_publish_enabled: bool = False
        self._aetheric_frame_name: str = aetheric_frame
        if not isinstance(self._aetheric_frame_name, str):
            raise TypeError(f"aetheric_frame must be a string, got {type(self._aetheric_frame_name).__name__}")
        self._aetheric_frame = Spellbook._aether._ensure_frame(self._aetheric_frame_name)
        self._crystallizer: Crystallizer = self._aetheric_frame._crystallizer
        # Borrowed world-root reference (owner ruling 2026-07-12): bound at
        # init exactly like `_crystallizer` above. `Aether.mutation_research`
        # lazily builds the (inactive) root on first touch and RAISES for a
        # cleaned root - a cleaned MR root under a live Aether therefore
        # fail-fasts Spellbook construction by design.
        self._mutation_research: MutationResearch = Spellbook._aether.mutation_research
        self._transaction_identity: DevopsIdentity = DevopsIdentity(
            owner_kind="spellbook",
            owner_id=self._id,
            aetheric_frame_name=self._aetheric_frame_name,
            metadata={
                "conjured": False,
                "conduit_id": None,
            },
            available_transactions=(
                "bind",
                "scan",
                "conjure",
            ),
        )
        self._transaction_identity.attach_registry(
            Spellbook._aether._get_existing_frame(
                self._aetheric_frame_name,
            ).devops_information_registry,
            object_ref=self,
        )
        self._refresh_devops_identity_state()

        # SpellbookConfiguration state
        self._configuration_locked: bool = False
        self._binds_before_configuration_count: int = 0
        self._conjure_dynamic_hint: bool | None = None
        self._configuration: SpellbookConfiguration | None = configuration
        self._aetheric_frame_configuration: AethericFrameConfiguration | None = None
        # Temporary logger for configuration init; will be replaced in _initialize_logging.
        self._logger: SafeLogger = InitHelpers.resolve_safe_logger(None)
        self._initialize_aetheric_frame_configuration()
        self._initialize_configuration()
        self._caching_enabled = self._resolve_system_caching_enabled()

        # Logger setup
        self._initialize_logging(logger)

        # ACTIVE resolution surface — a spell is PULLED from all of these on inactivate
        self._spells: dict[SpellIndex, Spell] = {}          # ACTIVE: index -> active spell (cold meld resolves here)
        self._lookup_spells: dict[tuple, SpellIndex] = {}   # ACTIVE: spell._key (frame_key,bind_key) -> index (binding lookup)
        self._spells_by_id: dict[str, Spell] = {}           # ACTIVE: spell_id -> active spell (meld-by-id)
        self._spell_id_pool: dict[str, Spell] = {}          # ACTIVE: spell_id -> active spell (warm pool)

        # EXISTENCE — all owned ids (active ∪ inactive); KEPT on inactivate, dropped only on full unregister
        self._spell_ids: set[str] = set()                   # ALL owned ids (Nexus snapshot reads this; the frame will reference it)
        self._inactive_spells: dict[str, Spell] = {}  # INACTIVE owned: spell_id -> parked spell (off resolution; repopulates the 7 active maps on notch-back)

        # Contracted (borrowed, keyed by peer conduit id) — same split
        self._contracted_spells: dict[str, dict[SpellIndex, Spell]] = {}        # ACTIVE: conduit -> {index -> active borrowed spell}
        self._lookup_contracted_spells: dict[str, dict[tuple, SpellIndex]] = {} # ACTIVE: conduit -> {signature -> index}
        self._contracted_spells_by_id: dict[str, dict[str, Spell]] = {}         # ACTIVE: conduit -> {spell_id -> active borrowed spell}
        self._contracted_spell_ids: dict[str, set[str]] = {}                    # ALL borrowed ids per conduit (existence; contracted twin of _spell_ids)
        self._inactive_contracted_spells: dict[str, dict[str, Spell]] = {}  # INACTIVE borrowed: conduit_id -> {spell_id -> parked borrowed spell}
        self._contracted_indexes: dict[str, SpellIndex] = {}  # CONTRACTED INDEXES: index_id -> the contracted SpellIndex (concrete target; ward owns the per-peer relationship)

        # Spell States System
        self._spell_system_states: SpellSystemStates = Spellbook._aether._get_spell_system_states(aetheric_frame)
        # Validation gate used by Meld to skip safety checks when risk is zero.
        self._spellbook_validation_required: bool = True

        # Binding system
        self._bind: Bind = Bind(self)

    #region Disposal

    def cleanup(self) -> None:
        """
        Public API

        Release the Spellbook's owned runtime state and permanently retire it.

        Contract:
            - Idempotent: repeated calls are safe after `_cleaned` flips.
            - Performs component cleanup under the Spellbook lock first, then
              clears high-level references outside the lock.
            - Best-effort child cleanup: downstream cleanup failures are logged
              and teardown continues where possible.
            - After cleanup completes, local registries, configuration,
              validators, conduit references, and logger references are no
              longer usable.

        Returns:
            None.
        """
        if self._cleaned:
            return

        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._cleanup_components()

        self._cleanup_core()


    # -------------------------
    # Phase 1: Components (under lock)
    # -------------------------

    def _cleanup_components(self) -> None:
        """
        Internal

        Clean up owned registries and component references under the Spellbook lock.

        Contract:
            - Cleans local spells and SpellIndex instances.
            - Clears and nulls owned and contracted registries, lookup maps,
              version caches, and spell_id maps.
            - Cleans local rich configuration only when it is not the
              frame-owned shared configuration object.
            - Cleans validation subsystems.
        """
        if self._conduit is not None:
            self._unregister_conduit_from_risk_manager(self._conduit._id)
        # 0) Stop the persistent phase-worker pool before registries die so
        # no in-flight phase unit can observe a half-torn Spellbook. This is
        # the single place pool threads are sentinelled and joined.
        if self._phase_scheduler is not None:
            try:
                self._phase_scheduler.cleanup()
            except Exception as e:
                self._logger.error(
                    f"Error cleaning phase scheduler: {e}",
                    "_cleanup_components",
                    exc_info=True,
                )
        del self._phase_scheduler
        del self._phase_run_lock
        # True book death: this spellbook's ENTIRE record subtree (book
        # twin + conduit twin(s) + all spell custody) leaves the record so
        # restore never rebuilds a dead book's world. Root-conduit teardown
        # and direct cleanup both arrive here; lesser conduits never do.
        if self._crystallizer.activated:
            self._crystallizer.emit_spellbook_removed(self._id)
        self._remove_spells_from_nexus()
        # 1) Clean ONLY local spells (not contracted)
        self._cleanup_spells()

        try:
            self._spells.clear()
            self._inactive_spells.clear()
        except Exception as e:
            self._logger.error(f"Error clearing _spells: {e}", "_cleanup_components", exc_info=True)
        del self._spells
        del self._inactive_spells

        try:
            self._spells_by_id.clear()
        except Exception as e:
            self._logger.error(f"Error clearing _spells_by_id: {e}", "_cleanup_components", exc_info=True)
        del self._spells_by_id

        try:
            self._spell_id_pool.clear()
        except Exception as e:
            self._logger.error(f"Error clearing _spell_id_pool: {e}", "_cleanup_components", exc_info=True)
        del self._spell_id_pool

        # 2) Clean lookup/contracted maps and local maps
        # Release this spellbook's framewide signature claims before dropping the
        # local lookup (best-effort; the frame may already be tearing down).
        try:
            for lookup_key in self._lookup_spells:
                self._aetheric_frame.release_lookup(lookup_key)
        except Exception as e:
            self._logger.error(f"Error releasing framewide lookups: {e}", "_cleanup_components", exc_info=True)
        try:
            self._lookup_spells.clear()
        except Exception as e:
            self._logger.error(f"Error cleaning _lookup_spells: {e}", "_cleanup_components", exc_info=True)
        del self._lookup_spells

        try:
            self._contracted_spells.clear()
            self._inactive_contracted_spells.clear()
        except Exception as e:
            self._logger.error(f"Error cleaning _contracted_spells: {e}", "_cleanup_components", exc_info=True)
        del self._contracted_spells
        del self._inactive_contracted_spells

        try:
            self._contracted_spells_by_id.clear()
        except Exception as e:
            self._logger.error(
                f"Error cleaning _contracted_spells_by_id: {e}",
                "_cleanup_components",
                exc_info=True,
            )
        del self._contracted_spells_by_id

        try:
            self._lookup_contracted_spells.clear()
        except Exception as e:
            self._logger.error(f"Error cleaning _lookup_contracted_spells: {e}", "_cleanup_components", exc_info=True)
        del self._lookup_contracted_spells

        # 3) cleanup configuration
        try:
            configuration = self._configuration
            if (
                    configuration is not None
                    and not self._is_frame_owned_shared_configuration(configuration)
            ):
                configuration.cleanup()
        except Exception as e:
            self._logger.error(f"Error cleaning configuration: {e}", "_cleanup_components", exc_info=True)
        del self._configuration
        if self._caching_system is not None:
            try:
                self._caching_system.cleanup()
            except Exception as e:
                self._logger.error(
                    f"Error cleaning caching system: {e}",
                    "_cleanup_components",
                    exc_info=True,
                )
        del self._caching_system
        del self._cache_emit_required
        del self._caching_enabled
        del self._crystallizer
        del self._mutation_research
        self._aetheric_frame_configuration = None

        try:
            self._spell_ids.clear()
        except Exception as e:
            self._logger.error(f"Error cleaning _spell_ids: {e}", "_cleanup_components", exc_info=True)
        del self._spell_ids

        try:
            self._contracted_spell_ids.clear()
        except Exception as e:
            self._logger.error(f"Error cleaning _contracted_spell_ids: {e}", "_cleanup_components", exc_info=True)
        del self._contracted_spell_ids

        try:
            self._contracted_indexes.clear()
        except Exception as e:
            self._logger.error(f"Error cleaning _contracted_indexes: {e}", "_cleanup_components", exc_info=True)
        del self._contracted_indexes

    def _cleanup_spells(self) -> None:
        """
        Internal

        Clean up local spell objects and unregister their spell indexes.

        Contract:
            - Unregisters each local SpellIndex entry from SpellSystemStates.
            - Cleans Spell and SpellIndex instances (best-effort).
            - Logs cleanup errors and continues.

        Returns:
            None.
        """
        for spell_index, spell in self._spells.items():
            try:
                spell_index_label = spell_index.id
            except Exception:
                spell_index_label = f"<spell-index:{id(spell_index)}>"
            try:
                self._spell_system_states.unregister_index(spell_index)
            except Exception as e:
                self._logger.error(
                    f"Error unregistering spell index '{spell_index_label}': {e}",
                    "_cleanup_spells",
                    exc_info=True,
                )
            try:
                spell._spellbook_cleanup = True
                spell.cleanup()
            except Exception as e:
                self._logger.error(
                    f"Error cleaning spell '{spell_index_label}': {e}",
                    "_cleanup_spells",
                    exc_info=True,
                )
            try:
                spell_index.cleanup()
            except Exception as e:
                self._logger.error(
                    f"Error cleaning spell index '{spell_index_label}': {e}",
                    "_cleanup_spells",
                    exc_info=True,
                )

    def cleanup_and_remove_spell(self, spell: Spell | str) -> None:
        """
        Public API

        Remove one locally owned spell from this Spellbook and clean it.

        Purpose:
            Provide a single authoritative local-spell removal path that
            unregisters system state, removes Spellbook/Aether/Nexus/risk
            references, and only then performs local spell teardown.

        Contract:
            - Accepts either a live `Spell` or its current `spell_id`.
            - Supports only locally owned spells in this Spellbook.
            - Unregisters the spell index from `SpellSystemStates` before local
              spell cleanup.
            - Removes Spellbook id maps and lookup maps before local spell
              cleanup so no cleaned spell stays reachable from the pools.
            - Best-effort unregisters the spell from RiskManager when a
              conjured conduit currently owns it.
            - Removes local spell indexes from Aether for the current conduit
              when conjured.
            - Cleans the local `Spell` and `SpellIndex` as the final step.

        Args:
            spell:
                Live local spell instance or current versioned `spell_id`.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the spell is not found locally or is not owned by this
                Spellbook.
        """
        self.check_cleaned()
        target_spell: Spell | None
        target_spell_id: str
        with self._lock:
            if isinstance(spell, str):
                target_spell_id = spell
                target_spell = self._spells_by_id.get(target_spell_id)
            else:
                target_spell_id = spell.spell_id
                target_spell = self._spells_by_id.get(target_spell_id)

            if target_spell is None:
                raise RuntimeError("Spellbook could not resolve the requested local spell.")
            if not isinstance(spell, str) and target_spell is not spell:
                raise RuntimeError("Spellbook can only remove the exact local spell instance.")
            if target_spell._cleaned:
                return

            target_spell_index = target_spell.spell_index
            target_lookup_key = target_spell.key
            owner_conduit_id = target_spell._owner_conduit_id

            self._spell_system_states.unregister_index(target_spell_index)
            # True removal: custody leaves the record entirely (both
            # locations) so restore never rebuilds a shed spell.
            if self._crystallizer.activated:
                self._crystallizer.emit_spell_removed(target_spell_id)
                # The index is torn down at this verb's tail; its
                # membership twin leaves the record with it.
                self._crystallizer.emit_spell_index_removed(
                    target_spell_index.id
                )

            self._spells.pop(target_spell_index, None)
            existing_lookup = self._lookup_spells.get(target_lookup_key)
            if existing_lookup is target_spell_index:
                self._lookup_spells.pop(target_lookup_key, None)

        if self._conjured and owner_conduit_id:
            self._unregister_spell_with_risk_manager(owner_conduit_id, target_spell)
            self._aether._remove_spells_from_aether(
                owner_conduit_id,
                {target_spell_index},
                self._aetheric_frame_name,
            )

        self._unregister_owned_spell_id(target_spell_id, target_spell)

        # Release the FRAMEWIDE binding-signature claim. Popping
        # `self._lookup_spells` above only clears this Spellbook's LOCAL map; the
        # frame's LookupContainer still maps this signature to the id being
        # destroyed, so a later bind of a different spell under the same
        # signature would be refused by `claim` naming a spell that no longer
        # exists. `lookup_container.py:18-20` requires the release: "a spellbook
        # cleaning up must release its keys".
        # BY SPELL_ID, NOT BY KEY, and the difference matters: `release_lookup`
        # pops whoever holds the key, while `release_lookup_by_spell_id` is a
        # no-op when this spell holds no signature. That keeps the call correct
        # if this verb is ever widened to parked spells, which claim no
        # signature and whose sibling holds the key.
        try:
            self._aetheric_frame.release_lookup_by_spell_id(target_spell_id)
        except Exception as e:
            self._logger.error(
                f"Error releasing framewide lookup for '{target_spell_id}': {e}",
                "cleanup_and_remove_spell",
                exc_info=True,
            )

        target_spell._spellbook_cleanup = True
        target_spell.cleanup()

        try:
            target_spell_index.cleanup()
        except Exception as e:
            self._logger.error(
                f"Error cleaning spell index '{target_spell_id}': {e}",
                "cleanup_and_remove_spell",
                exc_info=True,
            )
            raise


    # -------------------------
    # Phase 2: Core teardown (after lock)
    # -------------------------

    def _cleanup_core(self) -> None:

        # Nullify high-level refs (no try/catch for simple None assignments)
        del self._bind
        del self._aetheric_frame_name
        del self._aetheric_frame
        del self._id
        del self._conduit
        del self._conjured
        self._transaction_identity.cleanup()
        del self._transaction_identity
        del self._pending_binding_frame_keys
        del self._pending_structural_spells
        del self._configured_disposal_method_names
        del self._spell_system_states
        del self._configuration_locked
        del self._binds_before_configuration_count
        del self._conjure_dynamic_hint
        del self._spellbook_validation_required
        del self._nexus_publish_enabled
        del self._nexus
        self._crystallizer = None
        self._mutation_research = None

        try:
            if hasattr(self._logger, "cleanup"):
                self._logger.cleanup()
        except Exception as e:
            self._logger.error(f"Error during logger cleanup: {e}", "_cleanup_core", exc_info=True)
        del self._logger


    #endregion Disposal
    #region Context Manager
    def __enter__(self) -> Spellbook:
        """
        Enter the Spellbook lock context and return `self`.

        Purpose:
            Allow internal multistep operations to hold the Spellbook lock
            across a controlled block without exposing `_lock` directly.

        Returns:
            Spellbook:
                This Spellbook instance while the lock is held.
        """
        self.check_cleaned()
        self._lock.acquire()
        return self

    def __exit__(
            self,
            exc_type: type[BaseException] | None,
            exc_value: BaseException | None,
            traceback: TracebackType | None,
    ) -> None:
        """
        Exit the Spellbook lock context.

        Contract:
            - Releases unconditionally, including when the block raised. Exception
              arguments are accepted and IGNORED, so no exception is suppressed here.
            - Exactly one release per `__enter__`; the lock is reentrant, so nested
              `with` blocks are legal and each level must exit.

        Threading:
            Releases the spellbook lock acquired by `__enter__`.

        Lifecycle / Cleanup:
            Performs no cleaned-state check - it is purely the unlock half.

        Raises:
            RuntimeError: If called without a matching `__enter__` on this thread.

        Returns:
            None.
        """
        self._lock.release()

    #endregion Context Manager

    def _refresh_local_spell_ids(self) -> None:
        """
        Internal

        Rebuilds the owned-id cache (`_spell_ids`) as the union of the active
        id-pool keys (`_spells_by_id`) and the inactive parking-lot keys
        (`_inactive_spells`) -- every owned spell id, active or inactive.

        O(1)-amortized delta-sync against those live keyviews (no nested rebuild
        over index members); the sole consumer is the Nexus snapshot.
        """
        with self._lock:
            if self._spell_ids is None or self._spells_by_id is None or self._inactive_spells is None:
                return

            # O(1)-amortized: owned id set == active id-pool keys + inactive parking-lot keys.
            # Delta-sync against those live keyviews instead of a nested rebuild over index members.
            target = self._spells_by_id.keys() | self._inactive_spells.keys()
            self._spell_ids |= target - self._spell_ids   # add what is missing
            self._spell_ids -= self._spell_ids - target   # drop what is stale

    def _refresh_contracted_spell_ids(self) -> None:
        """
        Internal

        Rebuilds the per-conduit contracted version caches (`_contracted_spell_ids`)
        from the current `_contracted_spells` structure.

        After this runs:
            - Each conduit_id in `_contracted_spells` will have a corresponding
              ConcurrentSet[str] in `_contracted_spell_ids` containing all
              version IDs (SHA256) for that conduit’s spells.
        """
        with self._lock:
            if self._contracted_spells is None or self._contracted_spell_ids is None:
                return

            # Blow away old caches and rebuild them from scratch
            self._contracted_spell_ids.clear()

            for conduit_id, spell_map in self._contracted_spells.items():
                conduit_spell_ids = set[str]()
                for spell_index in spell_map.keys():
                    member_ids = spell_index._spells_in_index
                    if not member_ids:
                        continue
                    for member_id in member_ids:
                        conduit_spell_ids.add(member_id)
                self._contracted_spell_ids[conduit_id] = conduit_spell_ids


    def _refresh_all_spell_ids(self) -> None:
        """
        Internal

        Convenience method to refresh both local and contracted
        spell version caches in one call.
        """
        self._refresh_local_spell_ids()
        self._refresh_contracted_spell_ids()

    def _get_required_conduit_surface(self) -> Conduit:
        """
        Return the live-conjured conduit surface or raise.
        """
        conduit = self._conduit
        if conduit is None:
            raise RuntimeError("Spellbook requires a live conjured conduit.")
        return conduit

    def _get_required_configuration(self) -> SpellbookConfiguration:
        """
        Return the live spellbook configuration or raise.
        """
        configuration = self._configuration
        if configuration is None:
            raise RuntimeError("Spellbook configuration is unavailable.")
        return configuration

    def _resolve_system_caching_enabled(self) -> bool:
        """
        Internal

        Return the authoritative caching posture for this Spellbook's frame.

        Contract:
            - Caching is owned entirely by the frame: both the toggle
              (`system_caching_enabled`) and the cache root path live on the
              `AethericFrameConfiguration`.

        Returns:
            bool: True when caching is enabled for this Spellbook's frame.
        """
        frame_configuration = self._aetheric_frame_configuration
        return (
            frame_configuration is not None
            and frame_configuration.system_caching_enabled
        )

    def _system_caching_enabled_in_aether(self) -> bool:
        """
        Internal

        Return whether this Spellbook currently treats system caching as enabled
        and mirror that onto the spell-level cache posture flag.

        Returns:
            bool:
                True when caching is enabled for this Spellbook's frame.
        """
        self._caching_enabled = self._resolve_system_caching_enabled()
        return self._caching_enabled

    def _get_or_create_caching_system(
            self,
            conduit_name: str | None = None,
    ) -> CachingSystem:
        """
        Internal

        Lazily resolve the Spellbook-owned conduit cache utility.

        Purpose:
            Build the cache utility only when:
            - the Aether root config explicitly enables caching, and
            - this Spellbook already owns a root conduit.

        Contract:
            - Reuses the same utility instance after first creation.
            - Uses the Aether root cache path resolver as the authoritative
              filesystem root.
            - Assumes the caller already proved:
              - root caching is enabled, and
              - the Spellbook owns a root conduit.

        Returns:
            CachingSystem:
                The Spellbook-owned cache utility.
        """
        with self._lock:
            caching_system = self._caching_system
            if caching_system is not None:
                return caching_system
            if conduit_name is None:
                conduit_name = self._conduit._name
            caching_system = CachingSystem(
                frame_name=self._aetheric_frame_name,
                conduit_name=conduit_name,
                cache_root_path=self._aetheric_frame_configuration.resolve_conjure_cache_root_path(),
                logger=self._logger,
            )
            self._caching_system = caching_system
            return caching_system

    def _emit_spell_cache(
            self,
            spell: Spell,
    ) -> bool:
        """
        Internal

        Emit one spell's current cache payload into the Spellbook-owned cache.

        Purpose:
            Keep cache-file ownership on Spellbook while allowing public
            spell-facing callers to delegate the actual write here.

        Contract:
            - Returns early when the spell cache policy bit is disabled.
            - Requires the spell to belong to this Spellbook.
            - Stages the current phase-11 artifact cache payload.
            - Hands the payload to the Spellbook-owned `CachingSystem`.

        Args:
            spell:
                Spell whose current runtime payload should be emitted.

        Returns:
            bool:
                True when a payload was emitted, otherwise False.
        """
        if not spell._caching_enabled:
            return False
        if spell._spellbook is not self:
            raise RuntimeError(
                "Spell cache emission requires the spell to belong to this Spellbook."
            )
        caching_system = self._get_or_create_caching_system()
        if caching_system.has_spell_payload(spell.spell_id):
            return False
        try:
            artifact = spell._compiler_artifact
            if (
                    artifact is None
                    or artifact._spell_codegen_creation is None
            ):
                return False
            from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.manifest_creation_cache import (
                MANIFEST_METADATA_KEY,
            )
            from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.manifest_creation_cache import (
                build_package as build_manifest_package,
            )
            if (
                    artifact._spell_codegen_creation.metadata.get(
                        MANIFEST_METADATA_KEY
                    )
                    is not None
            ):
                # Manifest-first family output (generalized, solo, ...): the
                # manifest already IS the cache payload, so export is a
                # metadata read instead of a full both-lane recompile.
                spell_payload = build_manifest_package(spell)
            else:
                from melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation.spell_codegen_creation_cache import (
                    build_package,
                )
                spell_payload = build_package(spell)
        except Exception as exc:
            if self._logger is not None:
                self._logger.error(
                    f"Failed to stage cache payload for spell_id={spell.spell_id}: {exc}",
                    "_emit_spell_cache",
                    exc_info=True,
                )
            return False
        caching_system.upsert_spell_payload(spell.spell_id, spell_payload)
        self._cache_emit_required = True
        return True

    def _emit_cache_file_if_required(self) -> bool:
        """
        Internal

        Emit the Spellbook-owned cache file only when this operation staged new
        cache into the in-memory bundle.

        Purpose:
            Keep cache persistence on top-level operation boundaries instead of
            forcing synchronous file writes from the publish hot path.

        Contract:
            - Returns early when no new cache was staged since the last emit.
            - Emits at most once per staged operation window.
            - Restores the emit-required flag when file emission fails so a
              later caller can retry.

        Returns:
            bool:
                True when a cache file emit occurred, otherwise False.
        """
        # Lock-free fast path: this runs on every meld, and the flag is False
        # for all but the one meld that follows fresh cache staging. A stale
        # read here only delays the emit to the next meld boundary; the locked
        # re-check below keeps the actual emit single-shot.
        if not self._cache_emit_required:
            return False
        with self._lock:
            if not self._cache_emit_required:
                return False
            self._cache_emit_required = False
        try:
            self._get_or_create_caching_system().emit()
            return True
        except Exception:
            with self._lock:
                self._cache_emit_required = True
            raise

    def _emit_cache_file(self, spell: Spell) -> bool:
        """
        Internal

        Emit the Spellbook-owned cache file for the current in-memory cache state.

        Purpose:
            Keep cache-file ownership on Spellbook while allowing spell-facing
            callers to force a file emit through a Spellbook-controlled seam.

        Contract:
            - Returns early when the spell cache policy bit is disabled.
            - Requires the spell to belong to this Spellbook.
            - Emits the current `CachingSystem` in-memory state to disk.

        Args:
            spell:
                Spell requesting the Spellbook-owned cache file emit.

        Returns:
            bool:
                True when the cache file was emitted, otherwise False.
        """
        if not spell._caching_enabled:
            return False
        if spell._spellbook is not self:
            raise RuntimeError(
                "Spell cache-file emission requires the spell to belong to this Spellbook."
            )
        return self._emit_cache_file_if_required()

    def _register_owned_spell_id(self, spell_id: str, spell: Spell) -> None:
        """
        Internal

        Register the current spell_id mapping for an owned spell.

        Purpose:
            Provide O(1) lookup by the current version id for owned spells.

        Contract:
            - Only the current version id is stored in the map.
            - Raises if the id is mapped to a different spell.

        Args:
            spell_id (str): Current version id for the spell.
            spell (Spell): Owned spell instance.

        Raises:
            RuntimeError: If the Spellbook is cleaned or the map is missing.
            RuntimeError: If the id already maps to a different spell.

        Threading:
            - Acquires the Spellbook lock.
        """
        with self._lock:
            existing = self._spells_by_id.get(spell_id)
            if existing is not None and existing is not spell:
                self._logger.error(
                    f"spell_id collision for owned spell_id={spell_id}",
                    "_register_owned_spell_id",
                    exc_info=True,
                )
                raise RuntimeError(f"spell_id collision for owned spell_id={spell_id}")
            self._spells_by_id[spell_id] = spell
            existing_pool = self._spell_id_pool.get(spell_id)
            if existing_pool is not None and existing_pool is not spell:
                self._logger.error(
                    f"spell_id collision for spell_id_pool spell_id={spell_id}",
                    "_register_owned_spell_id",
                    exc_info=True,
                )
                raise RuntimeError(f"spell_id collision for spell_id_pool spell_id={spell_id}")
            self._spell_id_pool[spell_id] = spell

    def _update_owned_spell_id(self, old_id: str, new_id: str, spell: Spell) -> None:
        """
        Internal

        Update the owned spell_id map entry after a SpellIndex version change.

        Contract:
            - Removes the old id mapping and registers the new id mapping.
            - Adds the new id to the local version cache.

        Args:
            old_id (str): Previous version id for the spell index.
            new_id (str): New version id for the spell index.
            spell (Spell): Owned spell instance.

        Raises:
            RuntimeError: If the map is missing or does not contain the old id.
            RuntimeError: If the new id collides with another spell.

        Threading:
            - Acquires the Spellbook lock.
        """
        if old_id == new_id:
            return
        with self._lock:
            if self._spells_by_id is None:
                self._logger.error("Owned spell_id map is not available.", "_update_owned_spell_id")
                raise RuntimeError("Owned spell_id map is not available.")
            existing_old = self._spells_by_id.get(old_id)
            if existing_old is None:
                self._logger.error(
                    f"Owned spell_id not found for update (old_id={old_id}).",
                    "_update_owned_spell_id",
                    exc_info=True,
                )
                raise RuntimeError(f"Owned spell_id not found for update (old_id={old_id}).")
            if existing_old is not spell:
                self._logger.error(
                    f"Owned spell_id mapped to a different spell (old_id={old_id}).",
                    "_update_owned_spell_id",
                    exc_info=True,
                )
                raise RuntimeError(f"Owned spell_id mapped to a different spell (old_id={old_id}).")
            existing_new = self._spells_by_id.get(new_id)
            if existing_new is not None and existing_new is not spell:
                self._logger.error(
                    f"Owned spell_id collision for new_id={new_id}",
                    "_update_owned_spell_id",
                    exc_info=True,
                )
                raise RuntimeError(f"Owned spell_id collision for new_id={new_id}")

            self._spells_by_id.pop(old_id, None)
            self._spells_by_id[new_id] = spell
            self._spell_id_pool.pop(old_id, None)
            existing_pool = self._spell_id_pool.get(new_id)
            if existing_pool is not None and existing_pool is not spell:
                self._logger.error(
                    f"spell_id collision for spell_id_pool new_id={new_id}",
                    "_update_owned_spell_id",
                    exc_info=True,
                )
                raise RuntimeError(f"spell_id collision for spell_id_pool new_id={new_id}")
            self._spell_id_pool[new_id] = spell
            if self._spell_ids is not None:
                self._spell_ids.add(new_id)
        self._replace_spell_record_in_nexus(old_id, spell)

    def _unregister_owned_spell_id(self, spell_id: str, spell: Spell) -> None:
        """
        Internal

        Remove an owned spell_id mapping for the given spell.

        Purpose:
            Keep owned spell_id lookups and the spell_id_pool consistent when
            a locally owned spell is removed or transferred.
        Contract:
            - Removes the spell_id from `_spells_by_id` when present.
            - Removes the spell_id from `_spell_id_pool` when present.
            - Raises if the spell_id maps to a different spell in either map.
        Args:
            spell_id (str): Current version id for the spell.
            spell (Spell): Owned spell instance being removed.
        Raises:
            RuntimeError: If the owned id map is missing.
            RuntimeError: If the spell_id maps to a different spell.
        Threading:
            - Acquires the Spellbook lock.
        """
        with self._lock:
            existing = self._spells_by_id.get(spell_id)
            if existing is not None and existing is not spell:
                self._logger.error(
                    f"Owned spell_id mapped to a different spell (spell_id={spell_id}).",
                    "_unregister_owned_spell_id",
                    exc_info=True,
                )
                raise RuntimeError(
                    f"Owned spell_id mapped to a different spell (spell_id={spell_id})."
                )
            self._spells_by_id.pop(spell_id, None)

            existing_pool = self._spell_id_pool.get(spell_id)
            if existing_pool is not None and existing_pool is not spell:
                self._logger.error(
                    f"spell_id_pool mapped to a different spell (spell_id={spell_id}).",
                    "_unregister_owned_spell_id",
                    exc_info=True,
                )
                raise RuntimeError(
                    f"spell_id_pool mapped to a different spell (spell_id={spell_id})."
                )
            self._spell_id_pool.pop(spell_id, None)
            self._spell_ids.discard(spell_id)
        if self._nexus_publish_enabled:
            self._nexus._remove_spell_record(
                self._id,
                spell_id,
                self._aetheric_frame_name,
            )

    def _register_contracted_spell_id(self, conduit_id: str, spell_id: str, spell: Spell) -> None:
        """
        Internal

        Register the current spell_id mapping for a contracted spell.

        Purpose:
            Provide O(1) lookup by the current version id for contracted spells.

        Contract:
            - Mapping is stored under the given conduit_id.
            - Raises if the id is mapped to a different spell.

        Args:
            conduit_id (str): Peer conduit id that owns the contract.
            spell_id (str): Current version id for the spell.
            spell (Spell): Contracted spell instance.

        Raises:
            RuntimeError: If the contracted map is missing.
            RuntimeError: If the id already maps to a different spell.

        Threading:
            - Acquires the Spellbook lock.
        """
        with self._lock:
            if self._contracted_spells_by_id is None:
                self._logger.error("Contracted spell_id map is not available.", "_register_contracted_spell_id")
                raise RuntimeError("Contracted spell_id map is not available.")
            spell_map = self._contracted_spells_by_id.get(conduit_id)
            if spell_map is None:
                self._logger.error(
                    f"Contracted spell_id map missing for conduit_id={conduit_id}",
                    "_register_contracted_spell_id",
                    exc_info=True,
                )
                raise RuntimeError(f"Contracted spell_id map missing for conduit_id={conduit_id}")
            existing = spell_map.get(spell_id)
            if existing is not None and existing is not spell:
                self._logger.error(
                    f"Contracted spell_id collision for conduit_id={conduit_id}, spell_id={spell_id}",
                    "_register_contracted_spell_id",
                    exc_info=True,
                )
                raise RuntimeError(
                    f"Contracted spell_id collision for conduit_id={conduit_id}, spell_id={spell_id}"
                )
            spell_map[spell_id] = spell
            existing_pool = self._spell_id_pool.get(spell_id)
            if existing_pool is not None and existing_pool is not spell:
                self._logger.error(
                    f"Contracted spell_id collision for spell_id_pool spell_id={spell_id}",
                    "_register_contracted_spell_id",
                    exc_info=True,
                )
                raise RuntimeError(f"Contracted spell_id collision for spell_id_pool spell_id={spell_id}")
            self._spell_id_pool[spell_id] = spell

    def _update_contracted_spell_id(
            self,
            conduit_id: str,
            old_id: str,
            new_id: str,
            spell: Spell,
    ) -> None:
        """
        Internal

        Update the contracted spell_id map entry after a SpellIndex version change.

        Contract:
            - Removes the old id mapping and registers the new id mapping.
            - Adds the new id to the per-conduit version cache.

        Args:
            conduit_id (str): Peer conduit id that owns the contract.
            old_id (str): The previous version id for the spell index.
            new_id (str): New version id for the spell index.
            spell (Spell): Contracted spell instance.

        Raises:
            RuntimeError: If the map is missing or does not contain the old id.
            RuntimeError: If the new id collides with another spell.

        Threading:
            - Acquires the Spellbook lock.
        """
        if old_id == new_id:
            return
        with self._lock:
            if self._contracted_spells_by_id is None:
                self._logger.error("Contracted spell_id map is not available.", "_update_contracted_spell_id")
                raise RuntimeError("Contracted spell_id map is not available.")
            spell_map = self._contracted_spells_by_id.get(conduit_id)
            if spell_map is None:
                self._logger.error(
                    f"Contracted spell_id map missing for conduit_id={conduit_id}",
                    "_update_contracted_spell_id",
                    exc_info=True,
                )
                raise RuntimeError(f"Contracted spell_id map missing for conduit_id={conduit_id}")
            existing_old = spell_map.get(old_id)
            if existing_old is None:
                self._logger.error(
                    f"Contracted spell_id not found for update (old_id={old_id}).",
                    "_update_contracted_spell_id",
                    exc_info=True,
                )
                raise RuntimeError(f"Contracted spell_id not found for update (old_id={old_id}).")
            if existing_old is not spell:
                self._logger.error(
                    f"Contracted spell_id mapped to a different spell (old_id={old_id}).",
                    "_update_contracted_spell_id",
                    exc_info=True,
                )
                raise RuntimeError(f"Contracted spell_id mapped to a different spell (old_id={old_id}).")
            existing_new = spell_map.get(new_id)
            if existing_new is not None and existing_new is not spell:
                self._logger.error(
                    f"Contracted spell_id collision for new_id={new_id}",
                    "_update_contracted_spell_id",
                    exc_info=True,
                )
                raise RuntimeError(f"Contracted spell_id collision for new_id={new_id}")

            spell_map.pop(old_id, None)
            spell_map[new_id] = spell
            self._spell_id_pool.pop(old_id, None)
            existing_pool = self._spell_id_pool.get(new_id)
            if existing_pool is not None and existing_pool is not spell:
                self._logger.error(
                    f"Contracted spell_id collision for spell_id_pool new_id={new_id}",
                    "_update_contracted_spell_id",
                    exc_info=True,
                )
                raise RuntimeError(f"Contracted spell_id collision for spell_id_pool new_id={new_id}")
            self._spell_id_pool[new_id] = spell
            if self._contracted_spell_ids is not None:
                conduit_spell_ids = self._contracted_spell_ids.get(conduit_id)
                if conduit_spell_ids is None:
                    self._logger.error(
                        f"Contracted version cache missing for conduit_id={conduit_id}",
                        "_update_contracted_spell_id",
                        exc_info=True,
                    )
                    raise RuntimeError(f"Contracted version cache missing for conduit_id={conduit_id}")
                conduit_spell_ids.add(new_id)

    def _unregister_contracted_spell_id(self, conduit_id: str, spell_id: str, spell: Spell) -> None:
        """
        Internal

        Remove a contracted spell_id mapping for the given conduit.

        Args:
            conduit_id (str): Peer conduit id that owns the contract.
            spell_id (str): Current version id for the spell.
            spell (Spell): Contracted spell instance.

        Raises:
            RuntimeError: If the map is missing or does not contain the id.

        Threading:
            - Acquires the Spellbook lock.
        """
        with self._lock:
            if self._contracted_spells_by_id is None:
                self._logger.error("Contracted spell_id map is not available.", "_unregister_contracted_spell_id")
                raise RuntimeError("Contracted spell_id map is not available.")
            spell_map = self._contracted_spells_by_id.get(conduit_id)
            if spell_map is None:
                self._logger.error(
                    f"Contracted spell_id map missing for conduit_id={conduit_id}",
                    "_unregister_contracted_spell_id",
                    exc_info=True,
                )
                raise RuntimeError(f"Contracted spell_id map missing for conduit_id={conduit_id}")
            existing = spell_map.get(spell_id)
            if existing is None:
                self._logger.error(
                    f"Contracted spell_id not found for removal (spell_id={spell_id}).",
                    "_unregister_contracted_spell_id",
                    exc_info=True,
                )
                raise RuntimeError(f"Contracted spell_id not found for removal (spell_id={spell_id}).")
            if existing is not spell:
                self._logger.error(
                    f"Contracted spell_id mapped to a different spell (spell_id={spell_id}).",
                    "_unregister_contracted_spell_id",
                    exc_info=True,
                )
                raise RuntimeError(f"Contracted spell_id mapped to a different spell (spell_id={spell_id}).")
            spell_map.pop(spell_id, None)
            self._spell_id_pool.pop(spell_id, None)

    def _deactivate_owned_spell(self, spell: Spell) -> None:
        """
        Internal

        Park an active owned spell, pulling it off the active resolution surface.

        Contract:
            - The spell must be the active owned spell for its id (present in
              `_spells_by_id`); otherwise raises.
            - Pulls the spell from the four active owned maps (`_spells`,
              `_lookup_spells`, `_spells_by_id`, `_spell_id_pool`) and parks it
              in `_inactive_spells`.
            - Leaves `_spell_ids` untouched: existence is kept across the
              inactive window; only a full unregister drops the id.
            - Does not touch the SpellIndex or the framewide lookup; the caller
              (mediator-admitted notch/structural transaction) wires those.

        Args:
            spell (Spell): The active owned spell to park.

        Returns:
            None.

        Raises:
            RuntimeError: If the spell is not the active owned spell for its id.

        Threading:
            - Acquires the Spellbook lock; the admitting transaction serializes
              the wider operation.
        """
        spell_id = spell.spell_id
        spell_index = spell.spell_index
        binding_key = spell._key
        with self._lock:
            existing = self._spells_by_id.get(spell_id)
            if existing is None:
                self._logger.error(
                    f"Owned spell_id not active for deactivation (spell_id={spell_id}).",
                    "_deactivate_owned_spell",
                    exc_info=True,
                )
                raise RuntimeError(f"Owned spell_id not active for deactivation (spell_id={spell_id}).")
            if existing is not spell:
                self._logger.error(
                    f"Owned spell_id mapped to a different spell (spell_id={spell_id}).",
                    "_deactivate_owned_spell",
                    exc_info=True,
                )
                raise RuntimeError(f"Owned spell_id mapped to a different spell (spell_id={spell_id}).")
            self._spells.pop(spell_index, None)
            self._lookup_spells.pop(binding_key, None)
            self._spells_by_id.pop(spell_id, None)
            self._spell_id_pool.pop(spell_id, None)
            self._inactive_spells[spell_id] = spell
            spell._active = False
        # Mirror the park into the record (and, knob-gated, the module
        # world): the crystal moves to the inactive location exactly as
        # this spell just moved to _inactive_spells.
        if self._crystallizer.activated:
            self._crystallizer.emit_spell_activity(spell_id, active=False)

    def _reactivate_owned_spell(self, spell: Spell) -> None:
        """
        Internal

        Restore a parked owned spell to the active resolution surface.

        Contract:
            - The spell must be parked for its id (present in
              `_inactive_spells`); otherwise raises.
            - Removes the spell from `_inactive_spells` and repopulates the four
              active owned maps (`_spells`, `_lookup_spells`, `_spells_by_id`,
              `_spell_id_pool`).
            - `_spell_ids` already carries the id (existence was kept on park).
            - Does not touch the SpellIndex or the framewide lookup.

        Args:
            spell (Spell): The parked owned spell to reactivate.

        Returns:
            None.

        Raises:
            RuntimeError: If the spell is not the parked owned spell for its id.

        Threading:
            - Acquires the Spellbook lock; the admitting transaction serializes
              the wider operation.
        """
        spell_id = spell.spell_id
        spell_index = spell.spell_index
        binding_key = spell._key
        with self._lock:
            parked = self._inactive_spells.get(spell_id)
            if parked is None:
                self._logger.error(
                    f"Owned spell_id not parked for reactivation (spell_id={spell_id}).",
                    "_reactivate_owned_spell",
                    exc_info=True,
                )
                raise RuntimeError(f"Owned spell_id not parked for reactivation (spell_id={spell_id}).")
            if parked is not spell:
                self._logger.error(
                    f"Parked owned spell_id mapped to a different spell (spell_id={spell_id}).",
                    "_reactivate_owned_spell",
                    exc_info=True,
                )
                raise RuntimeError(f"Parked owned spell_id mapped to a different spell (spell_id={spell_id}).")
            self._inactive_spells.pop(spell_id, None)
            self._spells[spell_index] = spell
            self._lookup_spells[binding_key] = spell_index
            self._spells_by_id[spell_id] = spell
            self._spell_id_pool[spell_id] = spell
            spell._active = True
        # Mirror the promotion into the record (re-publishing the spell's
        # synthetic root module if it was unpublished while parked).
        if self._crystallizer.activated:
            self._crystallizer.emit_spell_activity(spell_id, active=True)

    def _deactivate_contracted_spell(self, conduit_id: str, spell: Spell) -> None:
        """
        Internal

        Park an active contracted (borrowed) spell for one peer conduit.

        Contract:
            - The spell must be the active contracted spell for its id under
              `conduit_id` (present in `_contracted_spells_by_id[conduit_id]`);
              otherwise raises.
            - Pulls the spell from the three active contracted maps for the
              conduit (`_contracted_spells`, `_lookup_contracted_spells`,
              `_contracted_spells_by_id`) and from the shared `_spell_id_pool`,
              and parks it in `_inactive_contracted_spells`.
            - Leaves `_contracted_spell_ids[conduit_id]` untouched: borrowed
              existence is kept across the inactive window.
            - Does not touch the SpellIndex or the framewide lookup.

        Args:
            conduit_id (str): Peer conduit id that owns the contract.
            spell (Spell): The active borrowed spell to park.

        Returns:
            None.

        Raises:
            RuntimeError: If the spell is not the active contracted spell for
                its id under `conduit_id`.

        Threading:
            - Acquires the Spellbook lock; the admitting transaction serializes
              the wider operation.
        """
        spell_id = spell.spell_id
        spell_index = spell.spell_index
        binding_key = spell._key
        with self._lock:
            active_by_id = self._contracted_spells_by_id.get(conduit_id)
            existing = active_by_id.get(spell_id) if active_by_id is not None else None
            if existing is None:
                self._logger.error(
                    f"Contracted spell_id not active for deactivation (conduit_id={conduit_id}, spell_id={spell_id}).",
                    "_deactivate_contracted_spell",
                    exc_info=True,
                )
                raise RuntimeError(
                    f"Contracted spell_id not active for deactivation (conduit_id={conduit_id}, spell_id={spell_id})."
                )
            if existing is not spell:
                self._logger.error(
                    f"Contracted spell_id mapped to a different spell (conduit_id={conduit_id}, spell_id={spell_id}).",
                    "_deactivate_contracted_spell",
                    exc_info=True,
                )
                raise RuntimeError(
                    f"Contracted spell_id mapped to a different spell (conduit_id={conduit_id}, spell_id={spell_id})."
                )
            self._contracted_spells[conduit_id].pop(spell_index, None)
            self._lookup_contracted_spells[conduit_id].pop(binding_key, None)
            active_by_id.pop(spell_id, None)
            self._spell_id_pool.pop(spell_id, None)
            parked = self._inactive_contracted_spells.get(conduit_id)
            if parked is None:
                parked = {}
                self._inactive_contracted_spells[conduit_id] = parked
            parked[spell_id] = spell

    def _reactivate_contracted_spell(self, conduit_id: str, spell: Spell) -> None:
        """
        Internal

        Restore a parked contracted (borrowed) spell for one peer conduit.

        Contract:
            - The spell must be parked for its id under `conduit_id` (present in
              `_inactive_contracted_spells[conduit_id]`); otherwise raises.
            - Removes the spell from `_inactive_contracted_spells` and
              repopulates the three active contracted maps for the conduit plus
              the shared `_spell_id_pool`.
            - `_contracted_spell_ids[conduit_id]` already carries the id
              (existence was kept on park).
            - Assumes the conduit's contract maps are live (park never drops the
              conduit sub-dicts); does not touch the SpellIndex or framewide
              lookup.

        Args:
            conduit_id (str): Peer conduit id that owns the contract.
            spell (Spell): The parked borrowed spell to reactivate.

        Returns:
            None.

        Raises:
            RuntimeError: If the spell is not the parked contracted spell for
                its id under `conduit_id`.

        Threading:
            - Acquires the Spellbook lock; the admitting transaction serializes
              the wider operation.
        """
        spell_id = spell.spell_id
        spell_index = spell.spell_index
        binding_key = spell._key
        with self._lock:
            parked_map = self._inactive_contracted_spells.get(conduit_id)
            existing = parked_map.get(spell_id) if parked_map is not None else None
            if existing is None:
                self._logger.error(
                    f"Contracted spell_id not parked for reactivation (conduit_id={conduit_id}, spell_id={spell_id}).",
                    "_reactivate_contracted_spell",
                    exc_info=True,
                )
                raise RuntimeError(
                    f"Contracted spell_id not parked for reactivation (conduit_id={conduit_id}, spell_id={spell_id})."
                )
            if existing is not spell:
                self._logger.error(
                    f"Parked contracted spell_id mapped to a different spell (conduit_id={conduit_id}, spell_id={spell_id}).",
                    "_reactivate_contracted_spell",
                    exc_info=True,
                )
                raise RuntimeError(
                    f"Parked contracted spell_id mapped to a different spell (conduit_id={conduit_id}, spell_id={spell_id})."
                )
            parked_map.pop(spell_id, None)
            self._contracted_spells[conduit_id][spell_index] = spell
            self._lookup_contracted_spells[conduit_id][binding_key] = spell_index
            self._contracted_spells_by_id[conduit_id][spell_id] = spell
            self._spell_id_pool[spell_id] = spell

    def _inactivate_contract_spell(self, conduit_id: str, spell_id: str) -> None:
        """
        Internal

        Park THIS spellbook's active borrowed copy of `spell_id` for one peer
        conduit, if it is currently active. Idempotent: a no-op when the spell is
        not an active contracted spell for `conduit_id` (already inactive, or never
        borrowed). Resolves the local contracted copy by id and delegates the map
        work to `_deactivate_contracted_spell`.

        This method manages only this spellbook's own contracted maps; it has no
        knowledge of links or conduits beyond the `conduit_id` key. The owning
        Conduit walks the links and calls this on each borrower's spellbook.

        Args:
            conduit_id (str): Peer (owner) conduit id keying the contracted bucket.
            spell_id (str): Version id of the borrowed spell to deactivate.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            active_by_id = self._contracted_spells_by_id.get(conduit_id)
            spell = active_by_id.get(spell_id) if active_by_id is not None else None
        if spell is None:
            return
        self._deactivate_contracted_spell(conduit_id, spell)

    def _activate_contract_spell(self, conduit_id: str, spell_id: str) -> None:
        """
        Internal

        Restore THIS spellbook's parked borrowed copy of `spell_id` for one peer
        conduit, if it is currently parked. Idempotent: a no-op when the spell is
        not parked for `conduit_id`. Resolves the local parked copy by id and
        delegates the map work to `_reactivate_contracted_spell`.

        This method manages only this spellbook's own contracted maps; it has no
        knowledge of links or conduits beyond the `conduit_id` key.

        Args:
            conduit_id (str): Peer (owner) conduit id keying the contracted bucket.
            spell_id (str): Version id of the borrowed spell to reactivate.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            parked = self._inactive_contracted_spells.get(conduit_id)
            spell = parked.get(spell_id) if parked is not None else None
        if spell is None:
            return
        self._reactivate_contracted_spell(conduit_id, spell)

    def _ensure_contracted_active(self, spell: Spell, conduit_id: str) -> None:
        """
        Internal

        Ensure `spell` is the ACTIVE contracted (borrowed) spell for `conduit_id`,
        contracting it eagerly if this spellbook does not hold it yet. This is the
        eager "follow" used when an owner notches an index-linked lineage to a
        version this borrower has not seen:
            - already active for this conduit -> no-op.
            - parked inactive for this conduit -> reactivate it.
            - not held at all -> add it as a fresh active contracted copy.

        Idempotent and link-agnostic (takes only a Spell + conduit_id).

        Args:
            spell (Spell): The owner's spell object (the new active member) to make
                this spellbook's active borrowed copy.
            conduit_id (str): Peer (owner) conduit id keying the contracted bucket.

        Returns:
            None.
        """
        self.check_cleaned()
        spell_id = spell.spell_id
        with self._lock:
            active_by_id = self._contracted_spells_by_id.get(conduit_id)
            if active_by_id is not None and spell_id in active_by_id:
                return
            parked = self._inactive_contracted_spells.get(conduit_id)
            is_parked = parked is not None and spell_id in parked
        if is_parked:
            self._reactivate_contracted_spell(conduit_id, spell)
        else:
            self._add_contracted_spell(spell, conduit_id)

    #region Logging

    def _initialize_logging(self, logger: Any | None) -> None:
        """
        Internal

        Establish the Spellbook logger through the hosted utility system.

        Priority:
            1) Explicit logger arg
            2) AetherUtilitySystem channel logger
            3) Silent no-op logger
        """
        try:
            if logger is not None:
                self._logger = InitHelpers.resolve_safe_logger(logger)
            else:
                self._logger = InitHelpers.resolve_channel_logger(
                    self,
                    groups=["spellbook", "lifecycle"],
                    system_groups=["spellbook", "aether"],
                    props={"aether_frame": self._aetheric_frame_name},
                    channels="system",
                )
        except Exception as e:
            # fallback to silent logger if anything blows up
            self._logger = InitHelpers.resolve_safe_logger(None)
            self._logger.error(f"Failed to initialize logger: {e}", "_initialize_logging", exc_info=True)

    #endregion Logging
    #region Properties

    @property
    def id(self) -> str:
        """
        Public API

        Return this spellbook's generated ownership id.

        Purpose:
            The id is the stamp the rest of the system uses to say "this
            spellbook owns that thing". Spell indexes record it as their
            `owner_spellbook_id`, transaction scope keys and the
            `spellbook:<id>` initiator string are derived from it, and
            crystallizer removal events carry it.

        Contract:
            - Generated once by `IDBuilder` during `__init__` and never
              reassigned; stable for the object's whole life.
            - Not derived from the frame name. Two spellbooks on the same
              aetheric frame have different ids, and a book produced by
              `create_new_preset_spellbook()` does NOT inherit its source's id.
            - Identifies the BOOK, not its contents. It does not change when
              spells are bound, removed, or grafted.

        Threading:
            Unsynchronized read of a write-once slot; safe from any thread
            while the spellbook is live.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`, so this raises after cleanup rather
            than returning a stale id - the slot itself is deleted during core
            teardown.

        Returns:
            str:
                This Spellbook's unique identifier.

        Raises:
            RuntimeError: If the spellbook has already been cleaned.
        """
        self.check_cleaned()
        return self._id

    @property
    def spells(self) -> Mapping[SpellIndex, Spell]:
        """
        Public API

        Return a read-only view of the local spells registered in this
        Spellbook.

        Contract:
            - Exposes a `MappingProxyType` wrapper over the local spell map.
            - Supports safe introspection without allowing direct registry
              mutation.

        Returns:
            Mapping[SpellIndex, Spell]:
                Immutable map of local `SpellIndex` keys to spell
                objects.
        """
        self.check_cleaned()
        spells_view: Mapping[SpellIndex, Spell] = MappingProxyType(self._spells)
        return spells_view

    @property
    def contracted_spells(self) -> Mapping[str, Mapping[SpellIndex, Spell]]:
        """
        Public API

        Return a per-conduit read-only view of all borrowed spells.

        Contract:
            - Outer keys are peer conduit identifiers.
            - Each value is an immutable spell map for that peer conduit.

        Returns:
            Mapping[str, Mapping[SpellIndex, Spell]]:
                Immutable map of peer conduit id to immutable borrowed-spell
                map.
        """
        self.check_cleaned()
        contracted_views: dict[str, Mapping[SpellIndex, Spell]] = {
            conduit_id: MappingProxyType(dict(spells))
            for conduit_id, spells in self._contracted_spells.items()
        }
        contracted_spells_view: Mapping[str, Mapping[SpellIndex, Spell]] = (
            MappingProxyType(contracted_views)
        )
        return contracted_spells_view

    def snapshot_state(self) -> dict[str, Any]:
        """
        Public API

        Build a read-only snapshot of the Spellbook state.

        Purpose:
            Provide a stable view of local and contracted spell registries while
            transactions may be in-flight.
        Contract:
            - Returns detached copies of internal maps; mutating the snapshot
              does not affect the Spellbook registries.
            - Includes a snapshot id for observability.
        Returns:
            Dict[str, Any]:
                Snapshot payload with local and contracted spell maps, lookup maps,
                and version caches.
        Raises:
            RuntimeError: If the Spellbook has been cleaned.
        Threading:
            Acquires the Spellbook lock while copying state.
        """
        self.check_cleaned()
        snapshot_id = IDBuilder.create_id()
        captured_at_ms = int(time.time() * 1000.0)

        with self._lock:
            local_spells = dict(self._spells) if self._spells is not None else {}
            lookup_spells = dict(self._lookup_spells) if self._lookup_spells is not None else {}
            spell_ids = set(self._spell_ids) if self._spell_ids is not None else set()

            contracted_spells: dict[str, dict[SpellIndex, Spell]] = {}
            if self._contracted_spells is not None:
                for conduit_id, spells in self._contracted_spells.items():
                    contracted_spells[conduit_id] = dict(spells)

            lookup_contracted_spells: dict[str, dict[tuple[str, str], SpellIndex]] = {}
            if self._lookup_contracted_spells is not None:
                for conduit_id, lookup_map in self._lookup_contracted_spells.items():
                    lookup_contracted_spells[conduit_id] = dict(lookup_map)

            contracted_spell_ids: dict[str, set[str]] = {}
            if self._contracted_spell_ids is not None:
                for conduit_id, conduit_spell_ids in self._contracted_spell_ids.items():
                    contracted_spell_ids[conduit_id] = set(conduit_spell_ids)

        return {
            "snapshot_id": snapshot_id,
            "captured_at_ms": captured_at_ms,
            "spellbook_id": self._id,
            "aetheric_frame": self._aetheric_frame_name,
            "local_spells": local_spells,
            "lookup_spells": lookup_spells,
            "spell_ids": spell_ids,
            "contracted_spells": contracted_spells,
            "lookup_contracted_spells": lookup_contracted_spells,
            "contracted_spell_ids": contracted_spell_ids,
        }

    #endregion Properties

    #region Core Methods
    #region General Methods
    def find_spell_by_id(self, spell_id: str) -> Spell | None:
        """
        Public API

        Return the local spell whose index owns `spell_id`, or None.

        Purpose:
            Resolve any id in a spell's version lineage back to the live
            `Spell` object that currently represents it.

        Contract:
            - Searches THIS spellbook's registry only. Spells reachable through
              contracted conduits or through other books in the frame are not
              consulted; `inspect_spell` is the frame-wide search.
            - Ownership is decided by `SpellIndex.has_spell`, which tests
              MEMBERSHIP of the index's version lineage rather than equality
              with the currently selected id. A superseded or parked version id
              therefore still resolves - and it resolves to the spell as it
              exists NOW, not to the state that version described.
            - Returns None on a miss. This is deliberately unlike the
              `find_spell_index` / `find_spell_key` siblings, which raise on a
              miss; a None here means "no local index claims this id", not
              "lookup failed".
            - Pure lookup: creates, registers, and mutates nothing.

        Threading:
            Does not acquire `self._lock`. The returned object is a live
            reference, so a concurrent removal or graft can invalidate it after
            this returns. Callers that need the result to stay valid must hold
            the lock across their own use of it.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Args:
            spell_id:
                Any id belonging to the target spell's version lineage.

        Returns:
            Optional[Spell]:
                The owning spell, or None when no local index claims the id.

        Raises:
            RuntimeError: If the spellbook has already been cleaned.
        """
        self.check_cleaned()
        for spell_index, spell in self._spells.items():
            # SpellIndex is responsible for telling us whether it owns this version
            if spell_index.has_spell(spell_id):
                return spell

        return None

    def get_spell_permissions(self, spell_index: SpellIndex) -> str | None:
        """
        Public API

        Read the capability ceiling recorded for one LOCAL spell lineage.

        Purpose:
            Report what this Spellbook is willing to expose for a lineage it OWNS, which is
            the upper bound any contract can grant a peer.

        Contract:
            - LOCAL ONLY. Contracted (borrowed) lineages are not searched, so a lineage
              this book borrows raises rather than reporting the lender's permission. That
              is deliberate: the ceiling belongs to the owner, not the borrower.
            - Returns the enum's NAME as a string, not the `Permissions` member. Compare
              against `Permissions.create.name`, or convert with
              `EnumHelpers.convert_enum_and_check(...)`, rather than comparing to the enum
              directly.
            - NEVER RETURNS None. Despite the `Optional[str]` annotation, the outcomes are
              a name or a raised `RuntimeError`.
            - This is the SPELL-side ceiling. A contract may grant less, never more - see
              `Permissions` for how the ward applies it.

        Args:
            spell_index:
                Lineage handle whose owning spell should be read.

        Returns:
            str:
                One of `"read"`, `"create"`, or `"block"`.

        Raises:
            RuntimeError:
                If no LOCAL spell is registered for the given index.

        Threading:
            Takes no lock of its own; it delegates to the internal spell lookup.
        """
        spell = self._find_spell(spell_index)
        if spell:
            return spell.permissions.name
        self._logger.error(
            f"Spell with index {spell_index} not found in the spellbook.",
            "get_spell_permissions",
            exc_info=True,
        )
        raise RuntimeError(f"Spell with index {spell_index} not found in the spellbook.")

    def _find_spell(self, spell_index: SpellIndex) -> Spell | None:
        """
        Internal

        Locates a **local** spell by its `SpellIndex`.

        Args:
            spell_index:
                The SpellIndex of the spell to find.

        Returns:
            Optional[Spell]:
                The spell object if found, else `None`.
        """
        with self._lock:
            spell = self._spells.get(spell_index, None)
        return spell

    def _find_contracted_spell(self, spell_index: SpellIndex) -> Spell | None:
        """
        Internal

        Locates a contracted spell by its unique ID by searching across all peer contracts.

        Args:
            spell_index (SpellIndex): The ID of the contracted spell to find.

        Returns:
            Optional[Spell]: The spell object if found.

        Raises:
            RuntimeError: If the contracted spell with the given ID is not found.
        """
        with self._lock:
            for contracted_spells in self._contracted_spells.values():
                if spell_index in contracted_spells:
                    return contracted_spells[spell_index]
            self._logger.error(f"Contracted spell with ID {spell_index} not found.", "_find_contracted_spell", exc_info=True)
        raise RuntimeError(f"Contracted spell with ID {spell_index} not found in the spellbook.")

    def _find_spell_index_by_index_id(
            self,
            spell_index_id: str,
    ) -> SpellIndex | None:
        """
        Internal

        Locate a **local** SpellIndex by its stable index id.

        Args:
            spell_index_id:
                Stable SpellIndex id (ULID) to resolve.

        Returns:
            Optional[SpellIndex]:
                Matching local SpellIndex when found, else "None".
        """
        with self._lock:
            for spell_index in self._spells.keys():
                if spell_index.id == spell_index_id:
                    return spell_index
        return None

    def _find_contracted_spell_index_by_index_id(
            self,
            spell_index_id: str,
    ) -> SpellIndex | None:
        """
        Internal

        Locate a contracted SpellIndex by its stable index id.

        Args:
            spell_index_id:
                Stable SpellIndex id (ULID) to resolve.

        Returns:
            Optional[SpellIndex]:
                Matching contracted SpellIndex when found, else "None".
        """
        with self._lock:
            for contracted_spells in self._contracted_spells.values():
                for spell_index in contracted_spells.keys():
                    if spell_index.id == spell_index_id:
                        return spell_index
        return None

    def get_spell_by_index_id(
            self,
            spell_index_id: str,
    ) -> Spell | None:
        """
        Public API

        Resolve a spell by its stable SpellIndex id.

        Purpose:
            Provide a runtime lookup path keyed by the stable SpellIndex identity
            (`spell_index_id`) rather than the current version id (`spell_id`).

        Contract:
            - Searches local SpellIndex attachments first, then contracted ones.
            - Once the matching `SpellIndex` object is found, resolves the
              spell directly through the existing index-based helpers instead of
              bouncing back through a second spell-id lookup.
            - Returns "None" when no matching SpellIndex exists.

        Args:
            spell_index_id:
                Stable SpellIndex id (ULID) to resolve.

        Returns:
            Optional[Spell]:
                Matching local or contracted spell when found, else "None".
        """
        self.check_cleaned()
        local_spell_index = self._find_spell_index_by_index_id(spell_index_id)
        if local_spell_index is not None:
            return self._find_spell(local_spell_index)
        contracted_spell_index = self._find_contracted_spell_index_by_index_id(
            spell_index_id
        )
        if contracted_spell_index is not None:
            return self._find_contracted_spell(contracted_spell_index)
        return None

    def _find_spell_count(self) -> int:
        """
        Internal

        Returns the total number of locally registered spells.

        Returns:
            int: The count of local spells.
        """
        with self._lock:
            count = len(self._spells) if self._spells else 0
        return count

    def _find_contracted_spell_count(self) -> int:
        """
        Internal

        Returns the number of peer conduits this spellbook currently has contracts with.

        Returns:
            int: The number of active contract links.
        """
        with self._lock:
            count = len(self._contracted_spells) if self._contracted_spells else 0
        return count


    def find_spell_index(self, spellframe: str, spell_name: str, binding_name: str) -> SpellIndex | None:
        """
        Public API

        Resolve the lineage (`SpellIndex`) behind one logical spell address.

        Purpose:
            Turn the human-facing `(spellframe, spell_name, binding_name)` address into the
            durable lineage handle, so callers can follow the lineage rather than pinning
            whichever version happens to be selected right now.

        Contract:
            - Searches LOCAL spells first, then every contracted (borrowed) spellbook map.
              A borrowed lineage is therefore resolvable through the borrower's own book.
            - The three inputs are normalized into one lookup key before matching, so
              casing differences in the binding name do not change the result.
            - NEVER RETURNS None. Despite the `Optional[SpellIndex]` annotation, the only
              outcomes are a `SpellIndex` or a raised `RuntimeError`. Do not write a
              `is None` branch against this method - it is unreachable.

        Args:
            spellframe:
                Logical namespace or grouping label the spell was bound under.
            spell_name:
                Name of the bound class or function.
            binding_name:
                Secondary key distinguishing several providers of the same frame.

        Returns:
            SpellIndex:
                The lineage handle for the addressed spell. The returned index is the
                stable identity - its `selected_spell_id` may move underneath you when the
                owner notches, which is the intended way to follow a lineage.

        Raises:
            RuntimeError: If the address matches neither a local nor a contracted spell.

        Threading:
            Takes the Spellbook lock for the lookup and RELEASES it before raising, so the
            failure path does not hold the lock while unwinding.
        """
        self.check_cleaned()
        with self._lock:
            key = self._make_spell_key(spellframe, spell_name, binding_name)
            if key in self._lookup_spells:
                return self._lookup_spells[key]
            for contracted_spells in self._lookup_contracted_spells.values():
                if key in contracted_spells:
                    return contracted_spells[key]
            self._logger.error("Spell not found in the spellbook.", "find_spell_id", exc_info=True)
        raise RuntimeError("Spell not found in the spellbook.")

    def _make_spell_key(
            self,
            spellframe: Any,
            spell_name: str,
            binding_name: str | None,
    ) -> tuple[str, str]:
        """
        Internal

        Creates a normalized key for spell lookups.

        Args:
            spellframe (Any): The logical frame / spellframe value.
            spell_name (str): The primary name.
            binding_name (Optional[str]): Optional binding name.

        Returns:
            tuple[str, str]: (frame_or_name, binding_name_or_default)
        """
        frame_key, bind_key = SpellInputUtils.make_spell_key_from_parts(
            spellframe=spellframe,
            spell_name=spell_name,
            binding_name=binding_name,
        )
        return frame_key, bind_key

    def _assert_lookup_key_available(
            self,
            *,
            lookup_key: tuple[str, str],
            spell_index: SpellIndex,
            context: str,
            check_local: bool = True,
            check_contracted: bool = True,
    ) -> None:
        """
        Internal

        Purpose:
            Guard against duplicate binding keys across selected local/contracted maps.
        Contract:
            - Raises RuntimeError if the lookup key is already mapped to a different
              SpellIndex in local or contracted lookup maps when those checks are enabled.
            - Allows the lookup key when it maps to the same SpellIndex (idempotent).
        Args:
            lookup_key: Normalized (frame_key, binding_key) tuple for the spell.
            spell_index: SpellIndex surface associated with the incoming spell.
            context: Method name used for logging/error context.
            check_local: If True, enforce uniqueness against local bindings.
            check_contracted: If True, enforce uniqueness against contracted bindings.
        Returns:
            None.
        Raises:
            RuntimeError: If the lookup key is already bound to another spell.
        """
        if check_local:
            existing_local = self._lookup_spells.get(lookup_key)
            if existing_local is not None and existing_local is not spell_index:
                frame_key, bind_key = lookup_key
                message = (
                    "Spell binding key collision detected in local registry. "
                    f"frame_key='{frame_key}', binding_name='{bind_key}'. "
                    "Use a distinct spellframe or binding_name to disambiguate."
                )
                self._logger.error(message, context, exc_info=True)
                raise RuntimeError(message)

        if check_contracted:
            for conduit_id, lookup_map in self._lookup_contracted_spells.items():
                existing_contracted = lookup_map.get(lookup_key)
                if existing_contracted is None or existing_contracted is spell_index:
                    continue
                frame_key, bind_key = lookup_key
                message = (
                    "Spell binding key collision detected in contracted registry. "
                    f"frame_key='{frame_key}', binding_name='{bind_key}', "
                    f"conduit_id='{conduit_id}'. Use a distinct spellframe or binding_name "
                    "to disambiguate."
                )
                self._logger.error(message, context, exc_info=True)
                raise RuntimeError(message)

    def find_spell_key(self, spellframe: str, spell_name: str, binding_name: str) -> tuple | None:
        """
        Public API

        Confirm that one logical spell address is resolvable, returning its lookup key.

        Purpose:
            An EXISTENCE PROBE, not a derivation. The key is built from the three inputs
            before any lookup, so the returned value is fully determined by the arguments -
            what the call actually tells you is that a spell is registered under it.

        Contract:
            - Searches LOCAL spells first, then every contracted (borrowed) map.
            - The returned key is the SAME key constructed from the arguments; nothing is
              read out of the registry into it. Call this to answer "is this address
              bound?", not to discover an address you did not already have.
            - NEVER RETURNS None. Despite the `Optional[tuple]` annotation, the outcomes
              are a key or a raised `RuntimeError`.
            - Use `find_spell_index(...)` instead when you want the lineage itself; that is
              the call that returns information you did not already hold.

        Args:
            spellframe:
                Logical namespace or grouping label the spell was bound under.
            spell_name:
                Name of the bound class or function.
            binding_name:
                Secondary key distinguishing several providers of the same frame.

        Returns:
            tuple:
                The normalized lookup key, shaped `(frame_or_name, binding_name_or_default)`.

        Raises:
            RuntimeError: If the address matches neither a local nor a contracted spell.

        Threading:
            Takes the Spellbook lock for the lookup and, unlike `find_spell_index`, raises
            while still HOLDING it.
        """
        self.check_cleaned()
        with self._lock:
            key = self._make_spell_key(spellframe, spell_name, binding_name)
            if key in self._lookup_spells:
                return key
            for contracted_spells in self._lookup_contracted_spells.values():
                if key in contracted_spells:
                    return key
            self._logger.error("Spell key not found in the spellbook.", "find_spell_key", exc_info=True)
            raise RuntimeError("Spell key not found in the spellbook.")


    def inspect_spell(
            self,
            spell: Any,
            aetheric_frame: str = "default",
    ) -> str | None:
        """
        Public API

        Resolve a live object back to its registered spell id, if the Aether knows it.

        Purpose:
            Answer "is this object bound, and under what id?" starting from the object
            itself rather than from an id or a lookup key.

        Contract:
            - Resolution is a THREE-STAGE search, in this order:
              1. IDENTITY against this Spellbook's own spells - each candidate is compared
                 with `is` on both `spell` and `user_created_object`, so an
                 existing-creation binding is findable by the very instance the caller
                 handed to `bind(...)`.
              2. IDENTITY frame-wide - every other conduit's Spellbook in the named frame
                 is walked, which is what keeps foreign spells (cluster shares, dynamic-link
                 providers) inspectable by object.
              3. FINGERPRINT fallback - only if identity found nothing, the id is
                 re-derived from the object alone.
            - Stage 3 is a LEGACY path and rarely matches a registered binding. The spell
              fingerprint composes BIND-TIME facts (existence, disposal methods, binding
              name, spell name) that a bare class, function, or instance cannot supply, so
              an id re-derived from the object generally cannot equal the id recorded at
              bind. Identity matching exists precisely because of that.
            - Every stage confirms the candidate id against the Aether registry before
              returning it; a spell known locally but absent from the registry returns None.
            - THIS METHOD NEVER RAISES. Every exception is caught, logged, and converted to
              None - including a `KeyError` for an unknown `aetheric_frame` name. A None
              result is therefore ambiguous: not registered, OR inspection failed. Check the
              log when the distinction matters.

        Args:
            spell:
                The object to resolve - a class, function, or live instance.
            aetheric_frame:
                Frame whose registry is consulted and whose conduits are walked in stage 2.
                Defaults to the lazily created "default" frame.

        Returns:
            Optional[str]:
                The registered spell id (SHA256) when the object resolves AND the Aether
                confirms it, otherwise None. See the contract above - None does not prove
                the object is unbound.

        Threading:
            Holds the Spellbook lock for the entire search, including the frame-wide walk
            across other conduits' spellbooks.
        """
        with self._lock:
            try:
                # The spell fingerprint composes bind-time facts (existence,
                # disposal methods, binding name, spell name) that a bare
                # class/function/instance cannot supply, so re-deriving the
                # id from the object alone can never match a registered
                # binding. Resolve by object identity against this
                # Spellbook's registered spells first; fall back to the
                # legacy default-fact fingerprint for foreign objects so
                # cross-book inspection semantics stay unchanged.
                for candidate_spell in self._spells.values():
                    if (
                            candidate_spell.spell is spell
                            or candidate_spell.user_created_object is spell
                    ):
                        candidate_spell_id = candidate_spell.spell_index.selected_spell_id
                        found = Spellbook._aether._check_for_spell(
                            candidate_spell_id,
                            aetheric_frame,
                        )
                        return candidate_spell_id if found else None
                # Frame-wide object inspection: walk the frame's registered
                # conduits' spellbooks so foreign spells (cluster shares,
                # dynamic-link providers) remain inspectable by object, which
                # the legacy fingerprint path provided before bind-time facts
                # joined the id composition.
                if aetheric_frame != "default":
                    frame = Spellbook._aether._aetheric_frames[aetheric_frame]
                else:
                    frame = Spellbook._aether._ensure_default_frame()
                for frame_conduit in frame._conduits.values():
                    conduit_spellbook = frame_conduit._spellbook
                    if conduit_spellbook is None or conduit_spellbook is self:
                        continue
                    for candidate_spell in conduit_spellbook._spells.values():
                        if (
                                candidate_spell.spell is spell
                                or candidate_spell.user_created_object is spell
                        ):
                            candidate_spell_id = (
                                candidate_spell.spell_index.selected_spell_id
                            )
                            found = Spellbook._aether._check_for_spell(
                                candidate_spell_id,
                                aetheric_frame,
                            )
                            return candidate_spell_id if found else None
                spell_id = self._bind.spell_id_inspector(spell)
                found = Spellbook._aether._check_for_spell(spell_id, aetheric_frame)
                return spell_id if found else None
            except Exception as e:
                self._logger.error(f"Failed to inspect spell: {e}", "inspect_spell", exc_info=True)
                return None

    def _register_conduit_spells_in_aether(self, conduit_id: str) -> None:
        """
        Internal

        Register this Spellbook's local spell indices in Aether for one conduit.

        Args:
            conduit_id:
                Conduit id that should own these local spell indices in the
                shared Aether registry.

        Returns:
            None.
        """
        with self._lock:
            spell_set = set(self._spells.keys())
        self._aether._add_spells_to_aether(
            conduit_id,
            spell_set,
            self._aetheric_frame_name,
            spell_ids=self._spell_ids,
        )

    def _unregister_conduit_spells_from_aether(self, conduit_id: str) -> None:
        """
        Internal

        Remove this Spellbook's local spell indices from Aether for one conduit.

        Args:
            conduit_id:
                Conduit id whose local spell indices should be removed from the
                shared Aether registry.

        Returns:
            None.
        """
        with self._lock:
            spell_set = set(self._spells.keys())
        if spell_set:
            self._aether._remove_spells_from_aether(
                conduit_id,
                spell_set,
                self._aetheric_frame_name,
            )

    def _get_conduit_by_spell_id(
            self,
            spell_id: str,
            aetheric_frame_name: str = "default",
    ) -> Conduit | None:
        """
        Internal

        Resolve the conduit that owns the supplied spell id through Aether.

        Args:
            spell_id:
                Version id / spell id to resolve.
            aetheric_frame_name:
                Frame name to search. `"default"` is normalized to this
                Spellbook's current frame.

        Returns:
            Optional[Conduit]:
                Owning conduit when found, otherwise "None".
        """
        if aetheric_frame_name == "default":
            aetheric_frame_name = self._aetheric_frame_name
        return self._aether._get_conduit_by_spell_id(
            spell_id,
            aetheric_frame_name,
        )

    def _check_spell_id_in_aether(
            self,
            spell_id: str,
            aetheric_frame_name: str = "default",
    ) -> bool:
        """
        Internal

        Return whether the supplied spell id exists in Aether.

        Args:
            spell_id:
                Version id / spell id to check.
            aetheric_frame_name:
                Frame name to search. `"default"` is normalized to this
                Spellbook's current frame.

        Returns:
            bool:
                "True" when Aether resolves the spell id, else "False".
        """
        if aetheric_frame_name == "default":
            aetheric_frame_name = self._aetheric_frame_name
        return bool(self._aether._check_for_spell(spell_id, aetheric_frame_name))

    def _spell_id_integrity_checker(self) -> None:
        """
        Internal

        Refuse conjure when any spell_id this Spellbook owns is already
        registered in the aetheric frame.

        Purpose:
            Close the pre-conjure blind spot in the frame existence aggregate.
            `bind` already checks one id at a time against the frame, but a
            Spellbook's owned-id set is only handed to the frame when its
            Conduit is constructed (`Conduit._configure_conduit_state` ->
            `_add_spells_to_aether` -> `_register_conduit_spells_in_aether`).
            Two Spellbooks that bind before either conjures therefore both pass
            every bind-time check, because neither is visible to the other yet.
            This sweeps the whole owned set against the frame in one pass, at
            the last moment before the Conduit is built.

        Contract:
            - Compares by SET INTERSECTION, not per-id lookup: one frame read
              instead of one per owned spell.
            - Reads `_spell_ids`, which is the EXISTENCE set (active AND parked
              owned ids), so a spell staged by `bind_inactive` still reserves
              its id. A dormant candidate's spell_id is allocated.
            - No-op for a Spellbook that owns nothing.
            - PREFLIGHT, NOT A GUARANTEE. It runs under the Spellbook lock while
              the frame write happens later under the FRAME lock, so two
              concurrent conjures can both pass it. Its job is to fail fast with
              a good message before phases 1-11 and Conduit construction are
              paid for. The authoritative check-and-set belongs in
              `AethericFrame.register_conduit_spells`, under the lock that
              guards the registry itself.
            - SELF-MATCH WARNING. This is safe today ONLY because a Spellbook
              has no entry in the frame registry until its Conduit is
              constructed, so its own ids cannot be in the aggregate yet. If the
              owned-id set is ever registered earlier - for example at Spellbook
              construction, to close the bind-time hole - this method will match
              its own ids on every conjure and MUST then exclude its own entry.
              The frame stores the live `_spell_ids` reference, so identity
              (`other_ids is self._spell_ids`) is the cheapest way to do that.

        Returns:
            None.

        Raises:
            RuntimeError: If any owned spell_id is already registered in the
                frame by another Spellbook.

        Threading:
            - Acquires the Spellbook lock to snapshot the owned set before
              reading the frame. The lock is reentrant and the conjure preflight
              already holds it.
        """
        with self._lock:
            owned_spell_ids = set(self._spell_ids)

        if not owned_spell_ids:
            return

        frame_spell_ids = self._aether._get_all_spell_ids(self._aetheric_frame_name)
        collisions = owned_spell_ids & frame_spell_ids
        if not collisions:
            return

        described = self._describe_colliding_spells(collisions)
        self._logger.error(
            f"Conjure refused: {len(collisions)} owned spell(s) already registered "
            f"in frame '{self._aetheric_frame_name}': {described}",
            "_spell_id_integrity_checker",
            exc_info=True,
        )
        raise RuntimeError(
            f"[SPELLBOOK] Conjure refused: {len(collisions)} spell(s) owned by this \n"
            f"Spellbook are already registered in aetheric frame "
            f"'{self._aetheric_frame_name}' by \n"
            "another Spellbook:\n"
            f"{described}\n"
            "A spell_id is a SHA256 over the bind-time fingerprint (structural profile, \n"
            "lookup signature, existence, and resolved disposal metadata) and does NOT \n"
            "include the frame, so two Spellbooks binding the same target with the same \n"
            "bind parameters mint the same id. That includes spells staged inactive \n"
            "by bind_inactive - a parked spell still holds its id. \n"
            "SCOPE: a spell_id is unique per PROCESS while "
            "`process_wide_unique_spell_ids` \n"
            "is on (the default), and per FRAME only when it is off. \n"
            "Fix: differentiate the binding with a distinct spellframe or "
            "binding_name. \n"
            "Moving to another aetheric frame is NOT a fix under the process-wide \n"
            "regime - the id follows the fingerprint, and the fingerprint has no frame \n"
            "in it."
        )

    def _describe_colliding_spells(self, spell_ids: set[str]) -> str:
        """
        Internal

        Render colliding spell ids as human-readable lines for a refusal message.

        Purpose:
            A bare SHA256 tells a caller nothing about WHICH binding collided.
            This resolves each id back to the owned `Spell` and reports its name
            and binding signature alongside a short id prefix.

        Contract:
            - FAILURE PATH ONLY. Called solely when a collision has already been
              detected, so the per-id map lookups never run on a healthy conjure.
            - Looks in the active map first, then the parked map, because a
              collision can be caused by a spell staged with `bind_inactive`.
            - Degrades rather than raises: an id that resolves to no owned spell
              is reported as `<unresolved>` instead of masking the original
              refusal with a lookup error.
            - Caps output at 10 entries so a large collision set stays readable.

        Args:
            spell_ids (Set[str]): The colliding spell ids.

        Returns:
            str: One `  - name  [signature]  id=prefix...` line per spell.
        """
        lines: list[str] = []
        for spell_id in sorted(spell_ids)[:10]:
            spell = self._spells_by_id.get(spell_id)
            if spell is None:
                spell = self._inactive_spells.get(spell_id)

            if spell is None:
                lines.append(f"  - <unresolved>  id={spell_id[:16]}...")
                continue

            name = getattr(spell, "spell_name", None) or "<unnamed>"
            binding_key = getattr(spell, "_key", None)
            state = "parked" if spell_id in self._inactive_spells else "active"
            lines.append(
                f"  - {name}  [{binding_key}]  {state}  id={spell_id[:16]}..."
            )

        remaining = len(spell_ids) - len(lines)
        if remaining > 0:
            lines.append(f"  - ... and {remaining} more")
        return "\n".join(lines)

    def _get_spell_by_id_via_aether(
            self,
            spell_id: str,
            aetheric_frame_name: str = "default",
    ) -> Spell | None:
        """
        Internal

        Resolve a spell by id through Aether ownership lookup.

        Args:
            spell_id:
                Version id / spell id to resolve.
            aetheric_frame_name:
                Frame name to search. `"default"` is normalized to this
                Spellbook's current frame.

        Returns:
            Optional[Spell]:
                Matching spell when found, otherwise "None".
        """
        owner = self._get_conduit_by_spell_id(spell_id, aetheric_frame_name)
        if owner is None:
            return None
        owner_spellbook = owner._spellbook
        if owner_spellbook is None:
            raise RuntimeError("Owner conduit has no spellbook.")
        return owner_spellbook.find_spell_by_id(spell_id)

    def describe_spells_in_spellbook(self) -> list[dict[str, Any]]:
        """
        Public API

        Return a stable authoring dump of spell targeting details currently
        visible through this Spellbook.

        Purpose:
            Provide an ACL-authoring/introspection surface that lets callers
            inspect the exact `spell_id` values available in this Spellbook
            alongside the logical targeting fields users may prefer when they
            do not want to author by SHA256 alone.

        Contract:
            - Uses the Spellbook-owned spell-id pool as the visible spell set.
            - Returns one detached dictionary per spell.
            - Does not mutate local or contracted registries.
            - Includes only the user-facing selector and ownership fields:
              `spell_id`, `spell_name`, `binding_name`, `spellframe`,
              `existence`, and `owner_conduit_id`.
            - Sorts results deterministically by spell name, effective binding
              name, and spell id.

        Returns:
            list[dict[str, Any]]:
                Detached spell-target description payloads for all visible
                spells in this Spellbook.
        """
        self.check_cleaned()
        with self._lock:
            spell_descriptions: list[dict[str, Any]] = []
            for spell in self._spell_id_pool.values():
                owner_conduit_id, _ = spell.owner_conduit_info
                spellframe_value = spell.spellframe
                spellframe_display = (
                    getattr(spellframe_value, "__name__", str(spellframe_value))
                    if spellframe_value is not None
                    else None
                )
                spell_descriptions.append(
                    {
                        "spell_id": spell.spell_id,
                        "spell_name": spell.spell_name,
                        "binding_name": spell.binding_name or "__default__",
                        "spellframe": spellframe_display,
                        "existence": spell.existence.name,
                        "owner_conduit_id": owner_conduit_id,
                    }
                )
            return sorted(
                spell_descriptions,
                key=lambda description: (
                    description["spell_name"],
                    description["binding_name"],
                    description["spell_id"],
                ),
            )


    def _check_all_spells(self) -> None:
        """
        Internal

        Performs a system check to verify that no locally bound spell ID is already
        registered in the global Aether registry for this frame.

        Contract:
            - Uses the warmed local version cache when available.
            - Falls back to SpellIndex version scans when the cache is empty.
            - Rises on the first duplicate detected in the Aether registry.

        Raises:
            RuntimeError: If a spell ID is found to be duplicated in the Aether.
        """
        with self._lock:
            check_for_spell = Spellbook._aether._check_for_spell
            aetheric_frame = self._aetheric_frame_name
            spell_ids = self._spell_ids

            if spell_ids:
                for spell_id in spell_ids:
                    if check_for_spell(spell_id, aetheric_frame):
                        self._logger.error(
                            f"Spell with ID {spell_id} already exists in the registry.",
                            "_check_all_spells",
                            exc_info=True,
                        )
                        raise RuntimeError(f"Spell with ID {spell_id} already exists in the registry.")
                return

            for spell_index in self._spells.keys():
                member_ids = spell_index._spells_in_index
                if not member_ids:
                    continue
                for member_id in member_ids:
                    if check_for_spell(member_id, aetheric_frame):
                        self._logger.error(
                            f"Spell with ID {member_id} already exists in the registry.",
                            "_check_all_spells",
                            exc_info=True,
                        )
                        raise RuntimeError(f"Spell with ID {member_id} already exists in the registry.")


    #endregion General Methods
    #region Contract API
    def _find_contracted_spell_by_id(self, spell_id: str, conduit_id: str) -> Spell | None:
        """
        Internal

        Resolves a contracted spell by its SHA256 version id using the Spellbook's
        local copies of contracted spells. Each contracted spell's SpellIndex
        contains all known versions, so we can resolve purely from Spellbook data.

        Args:
            spell_id (str): The version SHA of the spell.
            conduit_id (str): The contracting peer conduit ID.

        Returns:
            Optional[Spell]: The resolved spell, or None if not found.
        """

        # Pull the map of SpellIndex? Spell for this conduit
        spell_map = self._contracted_spells.get(conduit_id)
        if spell_map is None:
            return None

        # Search for a SpellIndex whose version list contains this SHA
        for spell_index, spell in spell_map.items():
            if spell_index.has_spell(spell_id):
                return spell

        return None



    def _create_link_contract(self, conduit_id: str) -> None:
        """
        Internal

        Initializes the internal storage maps for a new contract link with a peer conduit.

        This method ensures `_contracted_spells` (value map), `_lookup_contracted_spells`
        (key map), `_contracted_spell_ids` (version cache), and
        `_contracted_spells_by_id` (id map) are initialized
        atomically to maintain a consistent state.

        Args:
            conduit_id (str): The ID of the peer conduit to create the contract structure for.

        Raises:
            RuntimeError: If the contract structure is found in one map but not the others
                          (inconsistent state).
        """

        a_exists = conduit_id in self._contracted_spells
        b_exists = conduit_id in self._lookup_contracted_spells
        c_exists = conduit_id in self._contracted_spell_ids
        d_exists = conduit_id in self._contracted_spells_by_id

        if not (a_exists == b_exists == c_exists == d_exists):
            self._logger.error("Inconsistent link contract state", "_create_link_contract", exc_info=True)
            raise RuntimeError(
                f"Inconsistent link contract state for conduit ID {conduit_id}: "
                f"_contracted_spells={a_exists}, "
                f"_lookup_contracted_spells={b_exists}, "
                f"_contracted_spell_ids={c_exists}, "
                f"_contracted_spells_by_id={d_exists}"
            )

        if not a_exists and not b_exists and not c_exists and not d_exists:
            with self._lock:
                self._contracted_spells[conduit_id] = {}
                self._lookup_contracted_spells[conduit_id] = {}
                self._contracted_spell_ids[conduit_id] = set()
                self._contracted_spells_by_id[conduit_id] = {}


    def _remove_link_contract(self, conduit_id: str) -> None:
        """
        Internal

        Removes the internal storage maps for a dissolved contract link with a peer conduit.

        This ensures all four maps are removed atomically and consistently.

        Args:
            conduit_id (str): The ID of the peer conduit whose contract structure should be removed.

        Raises:
            RuntimeError: If the contract structure is found in some maps but not all
                          (inconsistent cleanup).
        """

        a_exists = conduit_id in self._contracted_spells
        b_exists = conduit_id in self._lookup_contracted_spells
        c_exists = conduit_id in self._contracted_spell_ids
        d_exists = conduit_id in self._contracted_spells_by_id

        if not (a_exists == b_exists == c_exists == d_exists):
            self._logger.error("Inconsistent link contract state", "_remove_link_contract", exc_info=True)
            raise RuntimeError(
                f"Inconsistent link contract state for conduit ID {conduit_id}: "
                f"_contracted_spells={a_exists}, "
                f"_lookup_contracted_spells={b_exists}, "
                f"_contracted_spell_ids={c_exists}, "
                f"_contracted_spells_by_id={d_exists}"
            )

        if a_exists:
            with self._lock:
                self._contracted_spells.pop(conduit_id, None)
                self._lookup_contracted_spells.pop(conduit_id, None)
                self._contracted_spell_ids.pop(conduit_id, None)
                self._contracted_spells_by_id.pop(conduit_id, None)
                # The parked (inactive) borrowed map is created lazily on the add
                # side (`_add_inactive_contracted_spell`), so it is not part of the
                # four-map lockstep check above. Drop its bucket too so a dissolved
                # contract leaves no orphaned inactive-copy map behind.
                self._inactive_contracted_spells.pop(conduit_id, None)


    def _add_contracted_spell(self, spell: Spell, conduit_id: str) -> None:
        """
        Internal

        Adds a specific spell (borrowed from a peer) to the contracted spells
        and updates the key and version caches for the given conduit.

        The SpellIndex is also attached to this Spellbook so future version
        updates can refresh spell_id lookup maps.

        When a link transaction is active, this also refreshes staged contract
        keys for the peer conduit so change-control commit hooks can observe
        the updated contract scope.

        Args:
            spell (Spell): The spell object to add.
            conduit_id (str): The ID of the peer conduit the spell was contracted from.
        Raises:
            RuntimeError: If the contracted spell's binding key collides with existing bindings.
        """
        frame_key = None
        should_mark = False
        with self._lock:
            if conduit_id not in self._contracted_spells:
                self._create_link_contract(conduit_id)

            spell_key = self._make_spell_key(spell.spellframe, spell.spell_name, spell.binding_name)
            self._assert_lookup_key_available(
                lookup_key=spell_key,
                spell_index=spell.spell_index,
                context="_add_contracted_spell",
                check_local=False,
                check_contracted=True,
            )

            spell_map = self._contracted_spells[conduit_id]
            lookup_map = self._lookup_contracted_spells[conduit_id]
            conduit_spell_ids = self._contracted_spell_ids[conduit_id]

            spell_index = spell.spell_index
            self._register_contracted_spell_id(conduit_id, spell_index.selected_spell_id, spell)

            # Main maps: SpellIndex? Spell and key? SpellIndex
            spell_map[spell_index] = spell
            lookup_map[spell_key] = spell_index

            # Track all known versions for this SpellIndex in the per-conduit version set
            member_ids = spell_index._spells_in_index
            if member_ids:
                for member_id in member_ids:
                    conduit_spell_ids.add(member_id)

            frame_key = spell.key[0]
            should_mark = bool(self._conjured)

        if should_mark and frame_key:
            self._mark_collection_dependents_dirty({frame_key})
        self._try_update_staged_contract_keys(conduit_id)
        if self._conjured and self._conduit is not None:
            self._register_spell_with_risk_manager(self._conduit._id, spell)

    def _add_inactive_contracted_spell(self, spell: Spell, conduit_id: str) -> None:
        """
        Internal

        Add an INACTIVE spell (borrowed from a peer) to the contracted-spell state,
        parked exactly like a deactivated contracted spell. Only the inactive map
        and the per-conduit existence set are populated -- NOT the active
        `_contracted_spells` / `_lookup_contracted_spells` / `_contracted_spells_by_id`
        maps and NOT the shared `_spell_id_pool`. The borrowed copy therefore stays
        off resolution (unmeldable) until the owner notches the lineage and the
        owning Conduit drives `_activate_contract_spell` on this spellbook.

        This is the inactive counterpart of `_add_contracted_spell`. The linking
        framework chooses between them based on the owner spell's active state, so a
        parked owner spell produces a parked borrowed copy -- not a resolvable one
        keyed under the wrong (selected) version id.

        Args:
            spell (Spell): The inactive spell object to park as a borrowed copy.
            conduit_id (str): The id of the peer conduit the spell was contracted from.
        """
        self.check_cleaned()
        with self._lock:
            if conduit_id not in self._contracted_spells:
                self._create_link_contract(conduit_id)
            spell_id = spell.spell_id
            spell_index = spell.spell_index
            # Park the borrowed copy (mirror of _deactivate_contracted_spell's resting
            # state): inactive map only, create the per-conduit bucket on demand since
            # _create_link_contract does not make the inactive one.
            parked = self._inactive_contracted_spells.get(conduit_id)
            if parked is None:
                parked = {}
                self._inactive_contracted_spells[conduit_id] = parked
            parked[spell_id] = spell
            # Existence: track every member id of the lineage, matching the active
            # path, so the borrower knows all versions exist.
            conduit_spell_ids = self._contracted_spell_ids[conduit_id]
            member_ids = spell_index._spells_in_index
            if member_ids:
                for member_id in member_ids:
                    conduit_spell_ids.add(member_id)
        self._try_update_staged_contract_keys(conduit_id)

    def _add_contracted_index(self, index: SpellIndex) -> None:
        """
        Internal

        Track a contracted SpellIndex by its stable id. This spellbook owns the
        concrete index object the borrower follows (`index_id -> SpellIndex`); the
        ConduitWard owns the per-peer contract relationship and the version deltas.
        Idempotent -- re-adding the same index just refreshes the mapping.

        Args:
            index (SpellIndex): The contracted index to track.
        """
        self.check_cleaned()
        with self._lock:
            self._contracted_indexes[index.id] = index

    def _remove_contracted_index(self, index_id: str) -> None:
        """
        Internal

        Stop tracking a contracted SpellIndex by id. Idempotent -- a no-op when the
        id is not tracked.

        Args:
            index_id (str): Stable id of the contracted index to drop.
        """
        self.check_cleaned()
        with self._lock:
            self._contracted_indexes.pop(index_id, None)

    def _get_owned_spell(self, spell_id: str) -> Spell | None:
        """
        Internal

        Return this spellbook's owned spell for `spell_id` -- active (in the id pool)
        or inactive (parked) -- or None if it owns no such spell. Used to resolve the
        members of an owned index for per-member contracting.

        Args:
            spell_id (str): Version id of the owned spell to resolve.

        Returns:
            Optional[Spell]: The owned (active or inactive) spell, or None.
        """
        self.check_cleaned()
        with self._lock:
            spell = self._spells_by_id.get(spell_id)
            if spell is not None:
                return spell
            return self._inactive_spells.get(spell_id)

    def _remove_contracted_spell(self, spell_id: str, conduit_id: str) -> None:
        """
        Internal

        Removes a specific contracted spell from the internal registry.

        The SpellIndex attachment is removed, so this Spellbook no longer
        receives spell_id updates for the contracted spell index.

        When a link transaction is active, this also refreshes staged contract
        keys for the peer conduit so change-control commit hooks can observe
        the updated contract scope.

        Args:
            spell_id (str): The version SHA of the spell to remove.
            conduit_id (str): The ID of the peer conduit the spell was contracted from.
        """

        removed_spell = None
        with self._lock:
            spell_map = self._contracted_spells.get(conduit_id)
            lookup_map = self._lookup_contracted_spells.get(conduit_id)
            conduit_spell_ids = self._contracted_spell_ids.get(conduit_id)

            if spell_map is None or lookup_map is None or conduit_spell_ids is None:
                self._logger.error(
                    f"No contracted spell maps for conduit {conduit_id}",
                    "_remove_contracted_spell",
                    exc_info=True,
                )
                raise RuntimeError(f"No contracted spell maps found for conduit ID {conduit_id}.")

            # Find the contracted SpellIndex holding this member id. A destroyed
            # (cleaned) contracted index can no longer report its member set, so
            # fall back to matching the contracted spell's own id -- the removed
            # member's live copy -- so its stale entry is still dropped.
            spell_index = None
            spell = None
            for idx, s in spell_map.items():
                if idx._cleaned:
                    if s.spell_id == spell_id:
                        spell_index = idx
                        spell = s
                        break
                    continue
                member_ids = idx._spells_in_index
                if member_ids and spell_id in member_ids:
                    spell_index = idx
                    spell = s
                    break

            if spell_index is None or spell is None:
                # Not in the ACTIVE contracted maps. A borrowed member can be
                # parked (inactive) instead of active: `_add_inactive_contracted_spell`
                # populates ONLY `_inactive_contracted_spells` plus the per-conduit
                # existence set -- never the active maps, the lookup, or the risk
                # manager. Removal must mirror that so it is symmetric with add for
                # parked members. This is the common case, not an edge one:
                # `remove_from_spell_index` only ever removes INACTIVE members
                # (`_apply_remove_from_index` forces an active head to be notched
                # away first), so the member handed to teardown is virtually always
                # the parked borrowed copy.
                parked = self._inactive_contracted_spells.get(conduit_id)
                parked_spell = parked.get(spell_id) if parked is not None else None
                if parked_spell is None:
                    self._logger.error(
                        f"Spell version {spell_id} not found for conduit {conduit_id}",
                        "_remove_contracted_spell",
                        exc_info=True,
                    )
                    raise RuntimeError(f"Spell version {spell_id} not found for conduit ID {conduit_id}.")
                # Drop the parked copy and its existence entry. No active-map,
                # lookup-map, or risk-manager teardown: a parked copy never
                # populated any of those (leave `removed_spell` None so the
                # risk-manager unregister below is skipped).
                parked.pop(spell_id, None)
                conduit_spell_ids.discard(spell_id)
            else:
                # Use the contracted spell's own id (the active member copy) rather than
                # the index selected id, which is unavailable once the index is cleaned.
                self._unregister_contracted_spell_id(conduit_id, spell.spell_id, spell)

                # Remove from main map
                spell_map.pop(spell_index, None)

                # Remove from lookup map
                key = self._make_spell_key(spell.spellframe, spell.spell_name, spell.binding_name)
                lookup_map.pop(key, None)

                # Drop the removed member from the version cache. While the index is
                # live, drop every member id it carries; once destroyed, only the
                # removed id remains to clear.
                if not spell_index._cleaned:
                    member_ids = spell_index._spells_in_index
                    if member_ids:
                        for member_id in member_ids:
                            conduit_spell_ids.discard(member_id)
                else:
                    conduit_spell_ids.discard(spell_id)
                removed_spell = spell
        self._try_update_staged_contract_keys(conduit_id)
        if removed_spell is not None and self._conjured and self._conduit is not None:
            self._unregister_spell_with_risk_manager(self._conduit._id, removed_spell)


    def _clear_contracted_spells_for_conduit(self, conduit_id: str) -> None:
        """
        Internal

        Clears all spells associated with a contracted conduit, retaining
        the contract structure and zeroing the version cache.

        SpellIndex attachments are removed, so this Spellbook no longer
        receives spell_id updates for the contracted spell index.

        When a link transaction is active, this also refreshes staged contract
        keys for the peer conduit so change-control commit hooks can observe
        the updated contract scope.

        Args:
            conduit_id (str): The ID of the peer conduit whose contracted spells are to be cleared
        """

        removed_spells: list[Spell] = []
        with self._lock:
            if (
                conduit_id not in self._contracted_spells
                or conduit_id not in self._lookup_contracted_spells
                or conduit_id not in self._contracted_spell_ids
                or conduit_id not in self._contracted_spells_by_id
            ):
                self._logger.error(
                    f"No contracted spell maps for conduit {conduit_id}",
                    "_clear_contracted_spells_for_conduit",
                    exc_info=True,
                )
                raise RuntimeError(f"No contracted spell maps found for conduit ID {conduit_id}.")

            spell_map = self._contracted_spells[conduit_id]
            removed_spells = list(spell_map.values())
            for spell in spell_map.values():
                self._unregister_contracted_spell_id(conduit_id, spell.spell_index.selected_spell_id, spell)

            self._contracted_spells[conduit_id].clear()
            self._lookup_contracted_spells[conduit_id].clear()
            self._contracted_spell_ids[conduit_id].clear()
            self._contracted_spells_by_id[conduit_id].clear()
            # Parked (inactive) borrowed copies live in a separate map the active
            # clears above never touch. Clear them too so a full contract teardown
            # is symmetric with the add side (which parks inactive members via
            # `_add_inactive_contracted_spell`). No risk-manager teardown: parked
            # copies were never registered with it.
            parked = self._inactive_contracted_spells.get(conduit_id)
            if parked is not None:
                parked.clear()
        self._try_update_staged_contract_keys(conduit_id)
        if removed_spells and self._conjured and self._conduit is not None:
            for spell in removed_spells:
                self._unregister_spell_with_risk_manager(self._conduit._id, spell)


    def _sever_link_contract(self, conduit_id: str) -> None:
        """
        Internal

        Sever the link contract for a given conduit ID by removing all
        contracted spells and the contract structure itself.

        Args:
            conduit_id (str): The ID of the peer conduit whose contract is to be severed
        """

        # 1) Clear all contracted spells but keep the structure (verifies existence)
        self._clear_contracted_spells_for_conduit(conduit_id)

        # 2) Remove the contract structure itself (three maps in lockstep)
        self._remove_link_contract(conduit_id)

    def _detach_link_contract(
            self,
            conduit_id: str,
    ) -> tuple[dict[SpellIndex, Spell], dict[tuple, SpellIndex], set[str], dict[str, Spell], dict[str, Spell] | None] | None:
        """
        Internal

        Reversibly pop one peer's whole bucket surface (BUG-005 seam).

        Purpose:
            Phase 1 of the two-phase link sever: pull the peer's five bucket
            maps off the live surface WITHOUT destroying any content, so a
            failure severing the other side can restore this side exactly
            via `_reattach_link_contract`. Destruction is deferred to
            `_destroy_detached_link_contract` after the sever commits.

        Contract:
            - Non-destructive and reversible: no id-pool removal, no
              risk-manager teardown, no staged-key refresh happens here.
            - Residue-tolerant: returns `None` when the peer has no bucket
              (already-detached residue must not fail a sever retry).
            - Lockstep guard: raises when the four active maps disagree
              about the peer's presence (mirrors `_remove_link_contract`).

        Args:
            conduit_id (str): The peer conduit id whose buckets to detach.

        Returns:
            Optional[Tuple[...]]: `(active_map, lookup_map, spell_id_set,
            by_id_map, inactive_map_or_None)` when a bucket existed,
            otherwise `None`.

        Raises:
            RuntimeError: If the bucket maps are in inconsistent lockstep
                state for this peer.

        Threading:
            - Acquires the Spellbook lock for the pop group.
        """
        a_exists = conduit_id in self._contracted_spells
        b_exists = conduit_id in self._lookup_contracted_spells
        c_exists = conduit_id in self._contracted_spell_ids
        d_exists = conduit_id in self._contracted_spells_by_id

        if not (a_exists == b_exists == c_exists == d_exists):
            self._logger.error("Inconsistent link contract state", "_detach_link_contract", exc_info=True)
            raise RuntimeError(
                f"Inconsistent link contract state for conduit ID {conduit_id}: "
                f"_contracted_spells={a_exists}, "
                f"_lookup_contracted_spells={b_exists}, "
                f"_contracted_spell_ids={c_exists}, "
                f"_contracted_spells_by_id={d_exists}"
            )
        if not a_exists:
            return None
        with self._lock:
            return (
                self._contracted_spells.pop(conduit_id),
                self._lookup_contracted_spells.pop(conduit_id),
                self._contracted_spell_ids.pop(conduit_id),
                self._contracted_spells_by_id.pop(conduit_id),
                # The parked (inactive) map is created lazily on the add
                # side, so it is outside the four-map lockstep guard and
                # may legitimately be absent.
                self._inactive_contracted_spells.pop(conduit_id, None),
            )

    def _reattach_link_contract(
            self,
            conduit_id: str,
            payload: tuple[
                dict[SpellIndex, Spell],
                dict[tuple, SpellIndex],
                set[str],
                dict[str, Spell],
                dict[str, Spell] | None,
            ],
    ) -> None:
        """
        Internal

        Restore one detached bucket payload exactly (BUG-005 seam).

        Purpose:
            The rollback half of the two-phase sever: when the second
            side's detach fails, the first side's payload is reattached so
            a raised sever leaves ZERO asymmetric state - bucket content
            included.

        Contract:
            - Restores the exact detached objects; nothing is copied or
              rebuilt, so borrowed-spell content survives verbatim.
            - Refuses to overwrite: raises when any bucket already exists
              for the peer (a reattach must never merge two surfaces).

        Args:
            conduit_id (str): The peer conduit id being restored.
            payload: The exact tuple returned by `_detach_link_contract`.

        Raises:
            RuntimeError: If a bucket surface already exists for this peer.

        Threading:
            - Acquires the Spellbook lock for the restore group.
        """
        with self._lock:
            if (
                conduit_id in self._contracted_spells
                or conduit_id in self._lookup_contracted_spells
                or conduit_id in self._contracted_spell_ids
                or conduit_id in self._contracted_spells_by_id
                or conduit_id in self._inactive_contracted_spells
            ):
                self._logger.error(
                    f"Reattach refused: bucket already present for {conduit_id}",
                    "_reattach_link_contract",
                )
                raise RuntimeError(
                    f"Cannot reattach link contract for {conduit_id}: a bucket surface already exists."
                )
            active_map, lookup_map, spell_id_set, by_id_map, inactive_map = payload
            self._contracted_spells[conduit_id] = active_map
            self._lookup_contracted_spells[conduit_id] = lookup_map
            self._contracted_spell_ids[conduit_id] = spell_id_set
            self._contracted_spells_by_id[conduit_id] = by_id_map
            if inactive_map is not None:
                self._inactive_contracted_spells[conduit_id] = inactive_map

    def _destroy_detached_link_contract(
            self,
            conduit_id: str,
            payload: tuple[
                dict[SpellIndex, Spell],
                dict[tuple, SpellIndex],
                set[str],
                dict[str, Spell],
                dict[str, Spell] | None,
            ],
    ) -> None:
        """
        Internal

        Destructively tear down one detached bucket payload (BUG-005 seam).

        Purpose:
            Phase 3 of the two-phase sever, after the removal committed:
            run the destructive per-spell teardown the old one-shot sever
            performed inline - warm-pool release, staged-contract-key
            refresh, and risk-manager unregistration - against the
            DETACHED payload, where a failure can no longer split the
            contract topology (the caller treats this phase as loud
            best-effort).

        Contract:
            - Mirrors `_clear_contracted_spells_for_conduit` semantics over
              a detached payload: each active borrowed spell's selected id
              leaves `_spell_id_pool`; parked copies die with the payload.
            - Refreshes staged contract keys so an active link transaction
              observes the shrunken contract scope.
            - Risk-manager unregistration runs only when this book is
              conjured (parked copies never registered there).

        Args:
            conduit_id (str): The peer conduit id the payload belonged to.
            payload: The exact tuple returned by `_detach_link_contract`.

        Threading:
            - Acquires the Spellbook lock for the pool-release group; the
              staged-key and risk-manager calls run outside it, mirroring
              the clear path.
        """
        active_map = payload[0]
        removed_spells = list(active_map.values())
        with self._lock:
            for spell in removed_spells:
                self._spell_id_pool.pop(spell.spell_index.selected_spell_id, None)
        self._try_update_staged_contract_keys(conduit_id)
        if removed_spells and self._conjured and self._conduit is not None:
            for spell in removed_spells:
                self._unregister_spell_with_risk_manager(self._conduit._id, spell)

    def _refresh_devops_identity_state(self) -> None:
        """
        Internal

        Refresh this Spellbook's dev-ops identity metadata.

        Purpose:
            Keep the Spellbook identity in sync with the local bind-resolution
            facts the mediator needs, without pushing transaction orchestration
            back into the Spellbook.
        """
        conduit_id = None
        if self._conduit is not None:
            conduit_id = self._conduit._id
        self._transaction_identity.update_metadata(
            spellbook_id=self._id,
            conjured=self._conjured,
            conduit_id=conduit_id,
        )

    def _bind_family_disabled_for_current_posture(self) -> bool:
        """
        Internal

        Return whether bind-family entry should be rejected for current posture.

        Contract:
            - Pre-conjure bind/scan remains allowed unless `disable_bind` is
              explicitly set.
            - Post-conjure bind/scan is rejected when bind is disabled, when
              post-conjure transactions are disabled, or when the frame is not
              dynamic.
        """
        frame_configuration = self._aetheric_frame_configuration
        if frame_configuration is None:
            return False
        if frame_configuration.disable_bind:
            return True
        if not self._conjured:
            return False
        if frame_configuration.disable_all_transactions_after_conjure:
            return True
        return frame_configuration.system_state is not SystemState.dynamic

    def _is_dynamic_posture(self) -> bool:
        """
        Internal

        Return whether this Spellbook's frame runs in dynamic mode.

        Dynamic posture is a Spellbook/frame property (owned by the
        AethericFrameConfiguration), not a per-conduit one, so it is available
        before conjure. Pre-conjure dynamic-only paths such as `bind_inactive`
        read it here rather than depending on a conduit that may not exist yet.
        """
        frame_configuration = self._aetheric_frame_configuration
        return (
            frame_configuration is not None
            and frame_configuration.system_state is SystemState.dynamic
        )

    def _get_required_transaction_mediator(self) -> TransactionMediator:
        """
        Internal

        Return the frame-owned live transaction mediator.

        Returns:
            TransactionMediator:
                Transaction mediator instance owned by the frame control plane.
        """
        change_control = self._aether._get_change_control_manager(
            self._aetheric_frame_name,
        )
        return change_control.transaction_mediator()

    def _binding_transaction_is_active(self) -> bool:
        """
        Internal

        Return whether bind/scan operations are currently allowed.

        Contract:
            - Pre-conjure spellbooks allow local bind/scan without an explicit
              transaction window.
            - Post-conjure spellbooks require an active bind-capable session.
        """
        if not self._conjured:
            return True
        session = self._get_required_transaction_mediator().get_session_for_identity(
            identity=self._transaction_identity,
            transaction_type=ChangeTransactionType.BIND,
        )
        if session is None and self._conduit is not None:
            session = self._get_required_transaction_mediator().get_session_for_identity(
                identity=self._conduit._transaction_identity,
                transaction_type=ChangeTransactionType.BIND,
            )
        if session is None:
            return False
        return session.supports_capabilities(("bind",))

    #endregion Contract API
    #region Binding API

    def _notch_spell(
            self,
            *,
            spell_index: SpellIndex,
            spell: Spell,
            change_reason: SpellStateChangeReason = SpellStateChangeReason.selected_different_spell,
    ) -> Spell:
        """
        Internal -- called by the owning Conduit (Conduit.notch_spell is the public surface).

        Notch a SpellIndex so `spell` becomes its selected (resolvable) spell,
        admitted as a `notch` change-control transaction through the mediator.

        `change_reason` records WHY the active member was repointed; it defaults
        to `selected_different_spell` (a general selection, not a mutation) and is
        threaded into the spell-owned invalidation so the lineage -- and its
        dependents -- are flagged with that reason.

        Contract:
            - Admits a `notch` transaction (claims the owning spellbook INTENT
              and the spell binding key EXCLUSIVE), performs the selected-spell
              switch inside the held window, then commits.
            - The actual switch (a SpellIndex repoint via `SpellIndex.update`) is
              the SpellIndex-model seam `_apply_notch`.

        Args:
            spell_index: The SpellIndex whose selected spell is switched.
            spell: The already-bound spell to make selected.

        Returns:
            Spell: The now-selected `spell`.

        Raises:
            RuntimeError: If the Spellbook is cleaned.
        """
        self.check_cleaned()
        # The owning Conduit admits the `notch` transaction (it owns the
        # change-control envelope and the conduit-link surface); this seam performs
        # the local selected-spell switch inside that held window.
        notched_spell = self._apply_notch(
            spell_index=spell_index, spell=spell, change_reason=change_reason
        )
        # The promoted member's phases 1-4 now run at the NOTCH transaction
        # commit through the generalized staged-binding-key structural validator
        # (the same commit path bind uses), which delegates back to this
        # spellbook's own phase runner. Phase-4/phase-6 results are transient
        # (nulled at conjure end), so they must never be used as a compile
        # signal here; the duplicate rerun previously keyed on them fired on
        # every notch, including no-op notches.
        return notched_spell

    def _apply_notch(
            self,
            *,
            spell_index: SpellIndex,
            spell: Spell,
            change_reason: SpellStateChangeReason = SpellStateChangeReason.selected_different_spell,
    ) -> Spell:
        """
        Internal SEAM -- notch the SpellIndex's ACTIVE member to `spell`.

        Runs inside the held `notch` transaction window (owning spellbook INTENT
        + binding key EXCLUSIVE). A SpellIndex holds a SET of member spell ids;
        `selected_spell_id` is the one currently active. Notch swaps which member
        is active using the active/inactive park machinery.

        Steps (owner side):
            1. Park the outgoing active spell off the four active owned maps via
               `_deactivate_owned_spell` (existence kept in `_spell_ids`), then
               tear down its creation context to bump the door epoch so the warm
               fast-door cannot serve the stale spell.
            2. Promote `spell` from `_inactive_spells` into the four active maps
               via `_reactivate_owned_spell` (precondition: `spell` is parked --
               staged by `bind_inactive` or a prior notch).
            3. Repoint the index pointer + record the member (`SpellIndex.update`).
            4. Repoint the framewide binding signature old -> new active id.
            5. Re-register the index so it is structurally gated + dirty; meld-time
               revalidation recompiles lazily on next resolve.

        Contracted borrowers are NOT yet fanned out here (owner-side only); a notch
        on a shared index does not yet update borrowers' contracted maps -- that is
        the next slice (cross-conduit fan-out under the same seal).

        Args:
            spell_index: The SpellIndex whose active member is switched.
            spell: The already-staged (inactive) spell to make active.

        Returns:
            Spell: `spell`, now the active member.

        Raises:
            RuntimeError: If `spell` is not parked in `_inactive_spells`, or the
                outgoing spell is not the active owned spell for its id.
        """
        self.check_cleaned()
        new_id = spell.spell_id
        with self._lock:
            outgoing = self._spells.get(spell_index)
            if outgoing is spell:
                # Already the active member for this index; notch is idempotent.
                return spell
            if outgoing is not None:
                # Park the outgoing active spell (off the four active maps; keeps
                # _spell_ids existence), then kill its fast-door so meld(old_id)
                # cannot serve the stale spell.
                self._deactivate_owned_spell(outgoing)
                outgoing._cleanup_creation_context()
            # Promote the incoming spell from _inactive_spells into the active maps.
            self._reactivate_owned_spell(spell)
            # Index pointer: select the new id and record it as a member.
            spell_index.update(new_id)
            # Framewide binding signature: repoint old -> new active id.
            self._aetheric_frame.update_lookup(spell._key, new_id)
            # Membership snapshot AFTER the repoint: the park/promote tails
            # above fire while the index still points at the OLD member, so
            # the one truthful selection snapshot for a notch lives here.
            if self._crystallizer.activated:
                self._crystallizer.emit(
                    self._crystallizer.create_spell_index_crystal(
                        spell_index, self._id
                    )
                )
        # Research record: the selection moved - journal the promotion
        # (forward-only; None on a first selection; the root declares an
        # unknown incoming id before journaling).
        self._record_research_promotion(
            outgoing.spell_id if outgoing is not None else None,
            new_id,
        )
        # Structural gate: re-register marks the index gated + dirty so meld-time
        # revalidation recompiles on next resolve (lazy).
        self._spell_system_states.register_index(
            spell_index=spell_index,
            owner_spellbook_id=self._id,
        )
        # Refresh the spellbook validation-required flag for the promoted member:
        # register_spell recomputes its structural/resolution validity and, for a
        # not-yet-validated member, flips `_spellbook_validation_required` True --
        # which is exactly what makes meld run the gated revalidation (the compile)
        # instead of trying to build a CreationContext for an uncompiled spell.
        if self._conjured and self._conduit is not None:
            self._register_spell_with_risk_manager(
                self._get_required_conduit_surface()._id,
                spell,
            )
        # Nexus visibility: the active member changed, so remove the parked
        # outgoing member's now-stale record and publish the newly-active one
        # (a plain publish when there is no outgoing member). Not phase-6-gated:
        # the active-member swap must be reflected regardless of any recompile.
        if self._conjured and self._conduit is not None:
            if outgoing is not None:
                self._replace_spell_record_in_nexus(outgoing.spell_id, spell)
            else:
                self._publish_spell_record_to_nexus(spell)
        # Mark the lineage structurally changed so dependents revalidate, and clear
        # the promoted member's stale CreationContext. invalidate_spell also sets
        # resolution_required=True as a side effect; bind-parity routing below sets
        # it back to False so meld's validation-required lane (the one that runs
        # the full 5-7/8-11 target pass) owns the recompile, exactly as it does for
        # a freshly bound spell. resolution_required=True would instead route the
        # deferred 8-11 lane, which cannot compile a member with no phase-5
        # blueprint.
        spell.invalidate_spell(change_reason=change_reason)
        spell.resolution_required = False
        # Phases 1-4 for the promoted member now run at the NOTCH transaction
        # commit: the strategy stages this binding key and the generalized
        # structural commit validator delegates back to this spellbook's own
        # phase runner, exactly like a bind commit. No hand-rolled structural
        # run here -- the seam owns the swap, the commit owns the checks.
        #
        # Bind gets its meld revalidation for free because a freshly bound id has
        # never been validated in this conduit (UNKNOWN verdict). A notched member
        # can carry a stale conjure-era `valid` verdict for this conduit, so knock
        # the promoted id's spell- and root-level verdicts back to gated -- the
        # explicit flag that makes meld's validation lane recompile it.
        if self._conjured and self._conduit is not None:
            resolution_state = self._spell_system_states.get_or_create_conduit_resolution_state(
                self._get_required_conduit_surface()._id,
            )
            resolution_state.set_spell_validity(
                new_id,
                SpellValidity.gated,
                change_reason=change_reason,
            )
            resolution_state.set_root_validity(
                new_id,
                SpellValidity.gated,
                change_reason=change_reason,
            )
        return spell

    def _add_to_spell_index(self, *, spell: Spell, target_index: SpellIndex) -> Spell:
        """
        Internal -- called by the owning Conduit (Conduit.add_to_spell_index is the public surface).

        Move an owned spell onto `target_index`, admitted as an `add_to_index`
        change-control transaction through the mediator.

        Contract:
            - Only a spell owned by THIS Spellbook may be added (enforced in the
              seam via `spell._spellbook is self`).
            - The `target_index` must be an index this Spellbook owns (enforced via
              `target_index.selected_spell_id in self._spell_ids`); you cannot add
              onto a foreign index.
            - The spell must be inactive; notch away from an active spell first.
            - The spell leaves its current index and joins `target_index` as an
              inactive member. If its old index empties, that index is destroyed.

        Args:
            spell: The owned, inactive spell to move.
            target_index: The index to move it onto.

        Returns:
            Spell: The moved `spell`.

        Raises:
            RuntimeError: If the Spellbook is cleaned, the spell is not owned
                here, or the spell is active.
        """
        self.check_cleaned()
        # The owning Conduit admits the `add_to_index` transaction; this seam
        # performs the move-onto-target inside that held window.
        return self._apply_add_to_index(spell=spell, target_index=target_index)

    def _apply_add_to_index(self, *, spell: Spell, target_index: SpellIndex) -> Spell:
        """
        Internal SEAM -- move an owned inactive spell onto `target_index`.

        Runs inside the held `add_to_index` transaction window (the mediator
        seals the source and target surfaces EXCLUSIVE, so this choreography is
        race-safe). The move is membership-only: the spell stays owned and
        inactive, so its id-keyed state (`_inactive_spells`, `_spell_ids`, id
        pools, Nexus record, fast-door, Creations) travels with it untouched.

        Steps:
            1. Enforce ownership: `spell._spellbook is self`, and `target_index` is
               owned here -- its selected spell id is in `self._spell_ids`
               (`target_index.selected_spell_id in self._spell_ids`, O(1)). You can
               only add onto an index you own.
            2. Enforce the spell is inactive (active members must be notched away
               first; moving an active member would orphan its active maps).
            3. Remove the spell id from its source index member set, add it to the
               target index, and repoint `spell.spell_index`.
            4. If the source index is now empty, destroy it.

        Args:
            spell: The owned, inactive spell to move.
            target_index: The index to move it onto.

        Returns:
            Spell: The moved `spell`.

        Raises:
            RuntimeError: If `spell` is not owned by this Spellbook, is active, or
                `target_index` is not an index this Spellbook owns.
        """
        self.check_cleaned()
        if spell._spellbook is not self:
            self._logger.error(
                f"add_to_spell_index: spell {spell.spell_id} is not owned by this spellbook.",
                "_apply_add_to_index",
                exc_info=True,
            )
            raise RuntimeError(
                f"add_to_spell_index: spell {spell.spell_id} is not owned by this spellbook."
            )
        spell_id = spell.spell_id
        if spell_id not in self._inactive_spells:
            self._logger.error(
                f"add_to_spell_index: spell {spell_id} is active; notch away before moving it.",
                "_apply_add_to_index",
                exc_info=True,
            )
            raise RuntimeError(
                f"add_to_spell_index: spell {spell_id} is active in its index; "
                f"notch away from it before moving it."
            )
        source_index = spell.spell_index
        if source_index is target_index:
            return spell
        if target_index.selected_spell_id not in self._spell_ids:
            self._logger.error(
                f"add_to_spell_index: target index {target_index.id} is not owned by this spellbook.",
                "_apply_add_to_index",
                exc_info=True,
            )
            raise RuntimeError(
                f"add_to_spell_index: target index {target_index.id} is not owned by this "
                f"spellbook; you can only add onto an index you own."
            )
        binding_key = spell._key
        owner_conduit_id = spell._owner_conduit_id
        with self._lock:
            source_index.remove_member(spell_id)
            target_index.add_member(spell_id)
            spell.spell_index = target_index
            source_emptied = source_index.is_empty()
        if source_emptied:
            self._destroy_spell_index(
                source_index,
                binding_key=binding_key,
                owner_conduit_id=owner_conduit_id,
            )
        if self._crystallizer.activated:
            # Membership moved between indexes: re-emit the target snapshot
            # always, and the source when it survived (the emptied case is
            # evicted by the destroy seam above).
            self._crystallizer.emit(
                self._crystallizer.create_spell_index_crystal(
                    target_index, self._id
                )
            )
            if not source_emptied:
                self._crystallizer.emit(
                    self._crystallizer.create_spell_index_crystal(
                        source_index, self._id
                    )
                )
        return spell

    def _destroy_spell_index(
            self,
            spell_index: SpellIndex,
            *,
            binding_key: tuple[str, str],
            owner_conduit_id: str | None,
    ) -> None:
        """
        Internal -- idempotently destroy an emptied, LOCAL SpellIndex.

        Tears down every system that can hold a reference to the index. Each step
        is a no-op when the index was never registered there (an inactive-only
        index touches almost none of these), so the routine is safe regardless of
        the index's history.

        NOTE: contracted/borrower fan-out for a SHARED index is intentionally NOT
        handled here -- this covers the local (un-shared) case only.

        Steps:
            1. Spellbook: drop the active-map entry + the binding-key lookup.
            2. Frame: release the binding signature + unregister from the spell
               registry.
            3. SpellSystemStates: `unregister_index` (states, closure, risk).
            4. The index object: `cleanup()`.

        Args:
            spell_index: The emptied index to destroy.
            binding_key: The `(frame_key, bind_key)` signature the index held.
            owner_conduit_id: The owning conduit id, or None when unconjured.
        """
        with self._lock:
            self._spells.pop(spell_index, None)
            self._lookup_spells.pop(binding_key, None)
        self._aetheric_frame.release_lookup(binding_key)
        if owner_conduit_id is not None:
            Spellbook._aether._remove_single_spell_index(
                owner_conduit_id,
                spell_index,
                self._aetheric_frame_name,
            )
        self._spell_system_states.unregister_index(spell_index)
        # Membership twin leaves with the destroyed index (tolerant when
        # the index never recorded).
        if self._crystallizer.activated:
            self._crystallizer.emit_spell_index_removed(spell_index.id)
        spell_index.cleanup()

    def _remove_from_spell_index(self, *, spell: Spell, source_index: SpellIndex) -> Spell:
        """
        Internal -- called by the owning Conduit (Conduit.remove_from_spell_index is the public surface).

        Separate an owned inactive spell out of `source_index` into its own fresh
        index, admitted as a `remove_from_index` change-control transaction.

        Contract:
            - Only a spell owned by THIS Spellbook may be moved (seam-enforced).
            - The spell must be inactive (notch away from an active spell first).
            - If the spell is the sole member of `source_index` this raises;
              use `cleanup_spell` to dispose it instead.
            - Otherwise the spell leaves `source_index` (which keeps its remaining
              members) and becomes the sole member of a fresh inactive index. No
              index is destroyed.

        Args:
            spell: The owned, inactive spell to separate.
            source_index: The index the spell currently belongs to.

        Returns:
            Spell: The separated `spell`.

        Raises:
            RuntimeError: If the Spellbook is cleaned, the spell is not owned
                here, the spell is active, or it is not a member of `source_index`.
        """
        self.check_cleaned()
        # The owning Conduit admits the `remove_from_index` transaction; this seam
        # performs the split-into-fresh-index inside that held window.
        return self._apply_remove_from_index(spell=spell, source_index=source_index)

    def _apply_remove_from_index(self, *, spell: Spell, source_index: SpellIndex) -> Spell:
        """
        Internal SEAM -- separate an owned inactive spell into its own fresh index.

        Runs inside the held `remove_from_index` transaction window. Membership-
        only: the spell stays owned and inactive, so its id-keyed state
        (`_inactive_spells`, `_spell_ids`, id pools, Nexus, fast-door, Creations)
        is untouched. No index is destroyed -- the source keeps its remaining
        members; the separated spell gets a fresh inactive index.

        Steps:
            1. Enforce ownership (`spell._spellbook is self`) + inactive + that the
               spell actually belongs to `source_index`.
            2. If the spell is the sole member of `source_index`, raise (use
               `cleanup_spell` to dispose it instead).
            3. Otherwise mint a fresh `SpellIndex` seeded with this spell id, remove
               the spell from `source_index`, and repoint `spell.spell_index`.

        Args:
            spell: The owned, inactive spell to separate.
            source_index: The index the spell currently belongs to.

        Returns:
            Spell: The separated `spell`.

        Raises:
            RuntimeError: If `spell` is not owned here, is active, or is not a
                member of `source_index`.
        """
        self.check_cleaned()
        if spell._spellbook is not self:
            self._logger.error(
                f"remove_from_spell_index: spell {spell.spell_id} is not owned by this spellbook.",
                "_apply_remove_from_index",
                exc_info=True,
            )
            raise RuntimeError(
                f"remove_from_spell_index: spell {spell.spell_id} is not owned by this spellbook."
            )
        spell_id = spell.spell_id
        if spell_id not in self._inactive_spells:
            self._logger.error(
                f"remove_from_spell_index: spell {spell_id} is active; notch away before moving it.",
                "_apply_remove_from_index",
                exc_info=True,
            )
            raise RuntimeError(
                f"remove_from_spell_index: spell {spell_id} is active in its index; "
                f"notch away from it before moving it."
            )
        if spell.spell_index is not source_index:
            self._logger.error(
                f"remove_from_spell_index: spell {spell_id} is not a member of the given source index.",
                "_apply_remove_from_index",
                exc_info=True,
            )
            raise RuntimeError(
                f"remove_from_spell_index: spell {spell_id} is not a member of the given source index."
            )
        if source_index.is_sole_member(spell_id):
            self._logger.error(
                f"remove_from_spell_index: spell {spell_id} is the only member of its index.",
                "_apply_remove_from_index",
                exc_info=True,
            )
            raise RuntimeError(
                f"remove_from_spell_index: spell {spell_id} is the only member of its index; "
                f"use cleanup_spell to dispose it instead."
            )
        with self._lock:
            new_index = SpellIndex(initial_id=spell_id)
            source_index.remove_member(spell_id)
            spell.spell_index = new_index
        if self._crystallizer.activated:
            # The member split onto a FRESH index: snapshot both sides.
            self._crystallizer.emit(
                self._crystallizer.create_spell_index_crystal(
                    source_index, self._id
                )
            )
            self._crystallizer.emit(
                self._crystallizer.create_spell_index_crystal(
                    new_index, self._id
                )
            )
        return spell

    def cleanup_spell(self, *, spell: Spell) -> None:
        """
        Public API

        Fully dispose an owned spell. Invalidate it FIRST so the spell and its
        lineage are flagged dirty (and dependents are rechecked) while the index
        and dependency edges still exist, then take it off every resolution
        surface, destroying its index when the spell was that index's only member.
        This is the disposal path `remove_from_spell_index` points at for a
        sole-member index.

        Contract:
            - Only a spell owned by THIS Spellbook may be disposed.
            - The ACTIVE member of a MULTI-member index cannot be disposed
              directly (it would leave the index headless); notch away from it
              first. The sole member of an index may always be disposed -- the
              index is destroyed with it.
            - Invalidation happens FIRST (`spell.invalidate_spell()`): the creation
              context is cleared and the lineage is marked structurally changed so
              dependents are rechecked, while the index and dependency edges still
              exist. Teardown only runs afterwards.
            - An ACTIVE spell is then disposed through `cleanup_and_remove_spell`,
              the authoritative path that unregisters the index from
              `SpellSystemStates` (fanning the dependent closure via
              `compute_impact_closure`), removes every id/lookup map, and cleans the
              spell and the index. An INACTIVE member is dropped from its index
              directly; the shared index survives unless this empties it.
            - Conduit Creations persist in this model and are left alone here.
            - NOTE: not yet sealed by a mediator transaction (no cleanup strategy
              exists); the map mutations run under the Spellbook lock.

        Args:
            spell: The owned spell to dispose.

        Raises:
            RuntimeError: If the spell is not owned here, or it is the active
                member of a multi-member index.

        Returns:
            None.
        """
        self.check_cleaned()
        spell_id = spell.spell_id
        if spell._spellbook is not self:
            self._logger.error(
                f"cleanup_spell: spell {spell_id} is not owned by this spellbook.",
                "cleanup_spell",
                exc_info=True,
            )
            raise RuntimeError(
                f"cleanup_spell: spell {spell_id} is not owned by this spellbook."
            )
        index = spell.spell_index
        with self._lock:
            is_active = spell_id in self._spells_by_id
            is_sole = index.is_sole_member(spell_id)
            if is_active and not is_sole:
                self._logger.error(
                    f"cleanup_spell: spell {spell_id} is the active member of a multi-member index.",
                    "cleanup_spell",
                    exc_info=True,
                )
                raise RuntimeError(
                    f"cleanup_spell: spell {spell_id} is the active member of a multi-member "
                    f"index; notch away from it before disposing it."
                )
        # CLEAN UP. Only an ACTIVE spell is invalidated first: flag it + its lineage
        # dirty (clear the creation context, force a next-meld rebuild) while the index
        # and dependency edges still exist, so dependents can be rechecked before
        # teardown. An INACTIVE member is off the resolution surface -- nothing resolves
        # through it and dependents run through the active member -- so it is dropped
        # without invalidation (invalidating a parked spell is pointless, and pre-notch
        # it is not even valid).
        if is_active:
            # Authoritative disposal: unregisters the index (its compute_impact_closure
            # fans the dependent closure), removes every id/lookup map, and cleans the
            # spell and the index. Self-guards re-entry via _spellbook_cleanup.
            spell.invalidate_spell(change_reason=SpellStateChangeReason.cleaned_up_spell)
            self.cleanup_and_remove_spell(spell)
        else:
            # Inactive member: drop just this member; the shared index and its other
            # members survive unless this empties it.
            binding_key = spell._key
            owner_conduit_id = spell._owner_conduit_id
            with self._lock:
                self._inactive_spells.pop(spell_id, None)
                self._spell_ids.discard(spell_id)
                # True removal (parked lane): custody leaves the record
                # entirely so restore never rebuilds a shed spell.
                if self._crystallizer.activated:
                    self._crystallizer.emit_spell_removed(spell_id)
                index.remove_member(spell_id)
                index_emptied = index.is_empty()
            if index_emptied:
                self._destroy_spell_index(
                    index,
                    binding_key=binding_key,
                    owner_conduit_id=owner_conduit_id,
                )
            elif self._crystallizer.activated:
                # The shared index survived minus one member: re-emit its
                # membership snapshot.
                self._crystallizer.emit(
                    self._crystallizer.create_spell_index_crystal(
                        index, self._id
                    )
                )
            # Local teardown only (already off the maps); set the guard so
            # Spell.cleanup() does not re-enter cleanup_and_remove_spell.
            spell._spellbook_cleanup = True
            spell.cleanup()

    def begin_transaction(
            self,
            transaction_type: ChangeTransactionType,
            *,
            conduit_id: str | None = None,
            conduit_ids: Iterable[str] | None = None,
            scope_keys: Iterable[str] | None = None,
            scope_hashes: Iterable[str] | None = None,
            binding_keys: Iterable[tuple[str, str]] | None = None,
            contract_keys: Iterable[tuple[str, str, str]] | None = None,
            metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Public API

        Begin a change-control transaction for this Spellbook.

        Purpose:
            Admit a mutation request through the frame-owned transaction
            mediator and, for bind transactions, open the binding transaction
            window.
        Contract:
            - Only one change-control transaction may be active per Spellbook.
            - Admission is serialized by the mediator-owned change-control
              pipeline.
            - Bind transactions open the binding transaction window.
            - Scan is not a transaction type; it must run inside a bind transaction.
        Args:
            transaction_type:
                Transaction type enum or string value (e.g. "bind", "link").
            conduit_id:
                Optional initiator conduit id for logging. Defaults to the
                conjured conduit id when available.
            conduit_ids:
                Optional list of conduits participating in the request.
            scope_keys:
                Optional normalized scope keys. These ARE the admission
                vocabulary: they become the request's scope claims, and the
                moded claim table acquires and arbitrates them.
            scope_hashes:
                Optional normalized scope hashes. ADVISORY IDENTITY ONLY - they
                carry NO claims and are NOT checked for conflicts. Their only
                reader is the retired `ChangeControlConflictManager`, which
                nothing calls. Supplying hashes declares no overlap and buys no
                isolation; use `scope_keys` to declare scope.
            binding_keys:
                Optional binding keys are affected by the request.
            contract_keys:
                Optional contract keys are affected by the request.
            metadata:
                Optional structured metadata for diagnostics.
        Returns:
            None.
        Raises:
            RuntimeError: If a change transaction is already active.
            RuntimeError: If the binding transaction is already active for bind requests.
            RuntimeError: If change-control admission is denied.
            ValueError: If transaction_type is invalid.
            TypeError: If transaction_type has an invalid type.
        Threading:
            Admission uses the orchestrator lock; the local state uses the Spellbook lock.
        """
        self.check_cleaned()
        request_type = transaction_type
        mediator = self._get_required_transaction_mediator()
        if request_type == ChangeTransactionType.BIND:
            if self._bind_family_disabled_for_current_posture():
                self._logger.error(
                    "Bind-family transaction denied by current frame posture",
                    "begin_transaction",
                )
                raise RuntimeError(
                    "[SPELLBOOK] Bind and scan are disabled for the current frame posture."
                )
            bind_metadata = dict(metadata) if metadata is not None else {}
            bind_metadata.update(
                self._build_bind_transaction_metadata(
                    origin_surface="spellbook.bind",
                    conduit_id=conduit_id,
                    scope_keys=scope_keys,
                    scope_hashes=scope_hashes,
                    binding_keys=binding_keys,
                )
            )
            existing_bind_session = mediator.get_session_for_identity(
                identity=self._transaction_identity,
                transaction_type=ChangeTransactionType.BIND,
            )
            mediator.start_transaction(
                identity=self._transaction_identity,
                transaction_type=ChangeTransactionType.BIND,
                metadata=bind_metadata,
            )
            # Spellbook owns its own local bind state. Only the outermost bind
            # window may reset the pending structural collections. Nested bind
            # calls inside an already-active scan/bind session must preserve the
            # spells staged earlier in that outer window so commit-time
            # structural validation can see the full bound set.
            if existing_bind_session is None:
                self._prepare_bind_transaction_state()
            return
        existing_session = mediator.get_session_for_identity(
            identity=self._transaction_identity,
            transaction_type=request_type,
        )

        initiator = conduit_id
        if not initiator and self._conduit is not None:
            initiator = self._conduit._id
        if not initiator:
            initiator = f"spellbook:{self._id}"

        transaction_manager = self._aether._get_change_control_manager(
            self._aetheric_frame_name,
        ).transaction_manager()

        scope_values = list(scope_keys) if scope_keys else []
        base_scope = transaction_manager.make_scope_key_spellbook(self._id)
        if base_scope not in scope_values:
            scope_values.append(base_scope)

        conduit_values = list(conduit_ids) if conduit_ids else []
        if initiator and initiator not in conduit_values and not initiator.startswith("spellbook:"):
            conduit_values.append(initiator)

        session = mediator.begin_transaction(
            identity=self._transaction_identity,
            transaction_type=request_type,
            existing_request_id=(
                existing_session.request.request_id
                if existing_session is not None
                else None
            ),
            spellbook_id=self._id,
            conduit_ids=conduit_values,
            scope_keys=scope_values,
            scope_hashes=scope_hashes,
            binding_keys=binding_keys,
            contract_keys=contract_keys,
            metadata=metadata,
        )

    def end_transaction(
            self,
            transaction_type: ChangeTransactionType | None = None,
            *,
            success: bool = True,
    ) -> None:
        """
        Public API

        End the active change-control transaction for this Spellbook.

        Purpose:
            Finalize an admitted change-control request and release any
            implicit transaction state tracked through the mediator-owned
            change-control pipeline.
        Contract:
            - Ends the active request tracked by this Spellbook.
            - Bind transactions close the binding transaction window.
            - Raises if no change transaction is active.
        Args:
            transaction_type:
                Optional transaction type assertion for safety checks.
        Returns:
            None.
        Raises:
            RuntimeError: If no change transaction is active.
            RuntimeError: If transaction_type does not match the active request.
            ValueError: If transaction_type is invalid.
            TypeError: If transaction_type has an invalid type.
        Threading:
            Uses the Spellbook lock for the local state; orchestrator handles admission state.
        """
        self.check_cleaned()
        mediator = self._get_required_transaction_mediator()
        bind_session = mediator.get_session_for_identity(
            identity=self._transaction_identity,
            transaction_type=ChangeTransactionType.BIND,
        )
        if transaction_type is not None:
            expected_type = transaction_type
            if bind_session is not None and expected_type != ChangeTransactionType.BIND:
                raise RuntimeError(
                    "[SPELLBOOK] Active change transaction does not match the requested type."
                )
            if expected_type == ChangeTransactionType.BIND and bind_session is not None:
                mediator.end_transaction_for_identity(
                    identity=self._transaction_identity,
                    transaction_type=ChangeTransactionType.BIND,
                )
                # Spellbook owns its own local bind state (see begin_transaction).
                # Nested bind windows (scan / bind_inactive joins) share the outer
                # session, so clearing after EVERY end wiped the staged structural
                # set down to the most recent bind and starved the commit-time
                # validator. Clear only when the mediator reports the bind
                # envelope fully finalized (the outermost end).
                if mediator.get_session_for_identity(
                    identity=self._transaction_identity,
                    transaction_type=ChangeTransactionType.BIND,
                ) is None:
                    self._clear_bind_transaction_state()
                return
        request = mediator.get_active_request()
        if request is None:
            raise RuntimeError("[SPELLBOOK] No active change transaction to end.")
        session = mediator.get_session_by_request_id(request.request_id)
        if session is None:
            raise RuntimeError("[SPELLBOOK] Active transaction session could not be resolved.")

        if transaction_type is not None:
            expected_type = transaction_type
            if request.request_type != expected_type:
                raise RuntimeError(
                    "[SPELLBOOK] Active change transaction does not match the requested type."
                )

        mediator.end_transaction_by_request_id(
            request.request_id,
            expected_type=transaction_type,
            success=success,
        )

    @contextmanager
    def transaction(
            self,
            transaction_type: ChangeTransactionType,
            *,
            conduit_id: str | None = None,
            conduit_ids: Iterable[str] | None = None,
            scope_keys: Iterable[str] | None = None,
            scope_hashes: Iterable[str] | None = None,
            binding_keys: Iterable[tuple[str, str]] | None = None,
            contract_keys: Iterable[tuple[str, str, str]] | None = None,
            metadata: dict[str, Any] | None = None,
    ) -> Generator[Spellbook]:
        """
        Public API

        Context-managed change-control transaction for this Spellbook.

        Purpose:
            Provide a safe begin/end wrapper for change-control transactions.
        Contract:
            - Begins a change-control transaction on entry.
            - Ends the transaction on exit, even if an exception is raised.
            - Bind transactions open/close the binding transaction window.
        Args:
            transaction_type:
                Transaction type enum or string value (e.g. "bind", "link").
            conduit_id:
                Optional initiator conduit id for logging.
            conduit_ids:
                Optional list of conduits participating in the request.
            scope_keys:
                Optional normalized scope keys. These ARE the admission
                vocabulary: they become the request's scope claims, and the
                moded claim table acquires and arbitrates them.
            scope_hashes:
                Optional normalized scope hashes. ADVISORY IDENTITY ONLY - they
                carry NO claims and are NOT checked for conflicts. Their only
                reader is the retired `ChangeControlConflictManager`, which
                nothing calls. Supplying hashes declares no overlap and buys no
                isolation; use `scope_keys` to declare scope.
            binding_keys:
                Optional binding keys are affected by the request.
            contract_keys:
                Optional contract keys are affected by the request.
            metadata:
                Optional structured metadata for diagnostics.
        Yields:
            Spellbook: The current Spellbook instance for the duration of the transaction context.
        Raises:
            RuntimeError: If a change transaction is already active.
            RuntimeError: If the binding transaction is already active for bind requests.
            RuntimeError: If change-control admission is denied.
            ValueError: If transaction_type is invalid.
            TypeError: If transaction_type has an invalid type.

        Returns:
            Generator[Spellbook, None, None]: A context manager yielding this spellbook
                inside a held change-control transaction window.
        """
        self.begin_transaction(
            transaction_type,
            conduit_id=conduit_id,
            conduit_ids=conduit_ids,
            scope_keys=scope_keys,
            scope_hashes=scope_hashes,
            binding_keys=binding_keys,
            contract_keys=contract_keys,
            metadata=metadata,
        )
        try:
            yield self
        except Exception:
            self.end_transaction(transaction_type, success=False)
            raise
        else:
            self.end_transaction(transaction_type, success=True)

    def _prepare_bind_transaction_state(self) -> None:
        """
        Internal

        Prepare local Spellbook bind state for one bind transaction.

        Purpose:
            Reset the Spellbook-local pending collections that accumulate bind
            side effects while the mediator/change-control layer owns the actual
            transaction start and end lifecycle.
        """
        with self._lock:
            if self._pending_binding_frame_keys is None:
                self._pending_binding_frame_keys = set()
            else:
                self._pending_binding_frame_keys.clear()
            if self._pending_structural_spells is None:
                self._pending_structural_spells = []
            else:
                self._pending_structural_spells.clear()

    def _build_bind_transaction_metadata(
            self,
            *,
            origin_surface: str,
            conduit_id: str | None,
            scope_keys: Iterable[str] | None,
            scope_hashes: Iterable[str] | None,
            binding_keys: Iterable[tuple[str, str]] | None,
    ) -> dict[str, object]:
        """
        Internal

        Build the bind metadata handed to the mediator strategy layer.

        Purpose:
            Keep the Spellbook bind entry surface thin. The spellbook only
            supplies the local object plus caller-provided bind metadata; the
            mediator side resolves request shape, embargo scope, and bind
            transaction policy from there.
        """
        resolved_conduit_id = conduit_id
        if resolved_conduit_id is None and self._conduit is not None:
            resolved_conduit_id = self._conduit._id
        return {
            "conduit_id": resolved_conduit_id,
            "origin_surface": origin_surface,
            "scope_keys": tuple(scope_keys) if scope_keys is not None else tuple(),
            "scope_hashes": tuple(scope_hashes) if scope_hashes is not None else tuple(),
            "binding_keys": tuple(binding_keys) if binding_keys is not None else tuple(),
        }

    def _clear_bind_transaction_state(
            self,
            _staged: Any | None = None,
    ) -> None:
        """
        Internal

        Clear local Spellbook bind state after commit or abort.

        Purpose:
            Drop the Spellbook-local pending collections once the mediator and
            change-control layers have finished the bind transaction lifecycle.
        """
        with self._lock:
            if self._pending_binding_frame_keys is not None:
                self._pending_binding_frame_keys.clear()
            if self._pending_structural_spells is not None:
                self._pending_structural_spells.clear()

    def _stage_spell_for_structural_phases(self, spell: Spell) -> None:
        """
        Internal

        Stage `spell` onto the active bind transaction so its commit runs the
        structural phases (1-4) on it: record the frame key + the spell in the
        pending bind-transaction collections and push the staged binding keys onto
        the session, which the change-control commit consumes to run the phases.

        Used by the active bind path. Notch does NOT stage -- it promotes an
        existing member under a NOTCH transaction, whose commit never fires the
        bind structural validator, so it runs the structural phases directly via
        `_run_post_conjure_structural_phases`.

        Args:
            spell (Spell): The spell to stage.
        """
        if self._pending_binding_frame_keys is not None:
            self._pending_binding_frame_keys.add(spell.key[0])
        if self._pending_structural_spells is not None:
            self._pending_structural_spells.append(spell)
        self._try_update_staged_binding_keys()

    def _try_update_staged_binding_keys(self) -> None:
        """
        Internal

        Update staged binding keys for an active bind transaction.

        Purpose:
            Refresh staged binding metadata with the normalized keys for spells
            bound during the active change-control bind transaction.
        Contract:
            - No-op if no change transaction is active, or it is not a bind request.
            - No-op if there are no pending structural spells to report.
            - Uses the pending structural spells list as the source of truth.
        Returns:
            None.
        Raises:
            RuntimeError: If the Spellbook has been cleaned.
        Threading:
            Captures staged inputs under the Spellbook lock; change-control
            update is performed without the Spellbook lock.
        """
        pending_spells: list[Spell] = []
        with self._lock:
            if self._pending_structural_spells is not None:
                pending_spells = list(self._pending_structural_spells)
        session = self._get_required_transaction_mediator().get_session_for_identity(
            identity=self._transaction_identity,
            transaction_type=ChangeTransactionType.BIND,
        )
        if session is None:
            return
        if not pending_spells:
            return
        binding_keys: list[tuple[str, str]] = []
        seen_keys: set[tuple[str, str]] = set()
        for spell in pending_spells:
            key = spell.key
            if key in seen_keys:
                continue
            seen_keys.add(key)
            binding_keys.append(key)
        self._get_required_transaction_mediator().update_transaction_for_identity(
            identity=self._transaction_identity,
            transaction_type=ChangeTransactionType.BIND,
            binding_keys=binding_keys,
        )

    def _try_update_staged_contract_keys(self, conduit_id: str) -> None:
        """
        Internal

        Update staged contract keys for an active link transaction.

        Purpose:
            Refresh staged contract metadata for a peer conduit after contract
            changes are applied to the contracted spell maps.
        Contract:
            - No-op if no change transaction is active, or it is not a link request.
            - Replaces contract keys for the supplied conduit id while preserving
              staged keys for other peers.
            - No-op if conduit_id is empty.
        Args:
            conduit_id:
                Peer conduit id whose contract keys should be refreshed.
        Returns:
            None.
        Raises:
            RuntimeError: If the Spellbook has been cleaned.
        Threading:
            Captures current contracted lookup keys under the Spellbook lock
            and uses mediator-owned session metadata as the source of truth for
            the currently staged contract keys.
        """
        if not conduit_id:
            return
        lookup_keys: list[tuple[str, str]] = []
        with self._lock:
            if self._lookup_contracted_spells is not None:
                lookup_map = self._lookup_contracted_spells.get(conduit_id)
                if lookup_map:
                    lookup_keys = list(lookup_map.keys())
        session = self._get_required_transaction_mediator().get_session_for_identity(
            identity=self._transaction_identity,
            transaction_type=ChangeTransactionType.LINK,
        )
        if session is None:
            return
        existing_keys = session.staged.contract_keys
        filtered_keys = [key for key in existing_keys if key[2] != conduit_id]
        for frame_key, binding_key in lookup_keys:
            filtered_keys.append((frame_key, binding_key, conduit_id))

        self._get_required_transaction_mediator().update_transaction_for_identity(
            identity=self._transaction_identity,
            transaction_type=ChangeTransactionType.LINK,
            contract_keys=filtered_keys,
        )

    def _mark_collection_dependents_dirty(self, frame_keys: set[str]) -> None:
        """
        Internal

        Mark list[Frame] consumers dirty for this Spellbook after binding changes.

        Args:
            frame_keys: Frame keys whose collection membership changed.
        Returns:
            None.
        Raises:
            RuntimeError: If the spell system state is unavailable.
        """
        if not frame_keys:
            return
        if self._spell_system_states is None:
            self._logger.error("SpellSystemStates unavailable for revalidation", "_mark_collection_dependents_dirty")
            raise RuntimeError("SpellSystemStates unavailable for revalidation.")
        try:
            self._spell_system_states.mark_collection_dependents_dirty(
                spellbook_id=self._id,
                frame_keys=frame_keys,
            )
        except Exception as e:
            self._logger.error(
                f"Failed to mark collection dependents dirty: {e}",
                "_mark_collection_dependents_dirty",
                exc_info=True,
            )
            raise

    def bind_inactive(
            self,
            *,
            spell: Any,
            spell_index: SpellIndex,
            existence: str | Existence,
            permissions: str | Permissions = "create",
            spellframe: Any = None,
            binding_name: str | None = None,
            disposal_method_names: Sequence[str] | None = None,
            profile: str = "general",
            **kwargs: Any,
    ) -> str:
        """
        Public API

        Bind a spell as an INACTIVE member of an existing owned `spell_index`.

        Purpose:
            Stage a spell off the resolution surface so a later `notch` can
            promote it. The spell is created (the `Bind` component mints its own
            fresh index), parked into `_inactive_spells` with existence kept in
            `_spell_ids` and `_active = False`, then folded onto the caller
            provided `spell_index` via `_apply_add_to_index` (which repoints the
            spell's index to the target and destroys the throwaway fresh index).
            The parked spell is inert and unmeldable until `notch_spell` promotes
            it.

        Contract:
            - Requires an active binding transaction and a dynamic Spellbook
              posture.
            - `spell_index` must be an index this Spellbook already owns (its
              selected member id is in `_spell_ids`), enforced by
              `_apply_add_to_index`.
            - Performs no active-map registration and claims no binding
              signature; the spell stays inactive until notched.

        Args:
            spell (Any):
                The class, function, lambda, or existing object to register.
            spell_index (SpellIndex):
                The already-owned index to attach the inactive spell to.
            existence (Union[str, Existence]):
                Lifecycle scope for the spell.
            permissions (str | Permissions):
                Permission level exposed to other conduits.
            spellframe (Any):
                Logical interface/frame grouping key.
            binding_name (Optional[str]):
                Secondary disambiguation key within the frame.
            disposal_method_names (Optional[Sequence[str]]):
                Optional disposal method names to associate with the spell.
            profile (str):
                Spell profile family to attach after bind completion.
            **kwargs:
                Optional lifecycle hooks (pre/activation/post).

        Returns:
            str:
                The SHA256 `spell_id` of the parked inactive spell.

        Raises:
            RuntimeError:
                If the spell_id collides, the Spellbook is not in a dynamic
                posture, or `spell_index` is not owned here.
        """
        # The staging transaction lives directly in this method. Conduit
        # .bind_inactive delegates here without holding a window of its own,
        # so `bind_inactive` opens the bind window and runs the inactive
        # registration inside it end to end. If a bind session is already
        # active on this thread the mediator joins it instead of opening a
        # second root.
        with self.transaction(
                "bind",
                metadata=self._build_bind_transaction_metadata(
                    origin_surface="spellbook.bind_inactive",
                    conduit_id=None,
                    scope_keys=None,
                    scope_hashes=None,
                    binding_keys=None,
                ),
        ):
            try:
                permissions_enum = EnumHelpers.convert_enum_and_check(permissions, Permissions)
                existence_enum = EnumHelpers.convert_enum_and_check(existence, Existence)
                if self._configured_disposal_method_names is None:
                    if disposal_method_names is not None:
                        self._configured_disposal_method_names = frozenset(
                            disposal_method_names
                        )
                    elif (
                            self._configuration is not None
                            and self._configuration.has_property("disposal_method_names")
                    ):
                        self._configured_disposal_method_names = frozenset(
                            self._configuration.get_property("disposal_method_names")
                        )
                    else:
                        self._configured_disposal_method_names = frozenset()

                new_spell = self._bind.bind(
                    permissions=permissions_enum,
                    spell=spell,
                    spellframe=spellframe,
                    binding_name=binding_name,
                    profile=profile,
                    existence=existence_enum,
                    aetheric_frame=self._aetheric_frame_name,
                    configured_disposal_method_names=self._configured_disposal_method_names,
                    # Owner ruling 2026-07-19: non-hook bind kwargs thread into
                    # Spell's construction (its native **kwargs metadata channel).
                    **{
                        key: value for key, value in kwargs.items()
                        if key not in ("pre_hooks", "activation_hooks", "post_hooks")
                    },
                )

                if Spellbook._aether._check_for_spell(new_spell.spell_id, self._aetheric_frame_name):
                    self._logger.error(
                        f"Spell with ID {new_spell.spell_id} already exists in the registry.",
                        "bind",
                        exc_info=True,
                    )
                    raise RuntimeError(
                        "Spell ID collision detected. spell_id is computed from the spell's bind-time \n"
                        "fingerprint (e.g., structural profile, lookup signature, existence, and resolved \n"
                        "disposal metadata). The existing spell with this id is already registered in the \n"
                        "Aether for this frame. If you intended to register a distinct spell, ensure its \n"
                        "bind-time fingerprint differs so it produces a unique spell_id."
                    )

                self._add_hooks_to_spell(new_spell, **kwargs)
                # Inactive pathing: route the registration setters to the inactive
                # surface instead of the active one. The SpellIndex records the
                # spell as a member (no active select); the Spellbook parks it in
                # _inactive_spells and keeps existence in _spell_ids. No id-pools,
                # no _lookup_spells, no _spells[index], no binding-signature claim
                # -- the spell is inert/unmeldable until notch_spell promotes it.
                if not self._is_dynamic_posture():
                    raise RuntimeError(
                        "bind_inactive requires a dynamic Spellbook posture. Build the "
                        "frame configuration with system_state=dynamic before staging an "
                        "inactive spell for later notch activation."
                    )
                inactive_index = new_spell.spell_index
                inactive_index.add_member(new_spell.spell_id)
                self._inactive_spells[new_spell.spell_id] = new_spell
                new_spell._active = False
                # Dynamic posture is a Spellbook/frame property, not a per-conduit
                # one, and no conduit exists here (pre-conjure). Stamp it from the
                # Spellbook so the parked spell is invalidation-eligible when a later
                # notch promotes it -- without attaching a conduit or invalidating it.
                new_spell._dynamic_environment = True
                # If a conduit already exists (post-conjure bind_inactive), follow the
                # same conduit wiring an active bind does so the parked spell owns a
                # CreationContextFactory. Pre-conjure inactive spells have no conduit
                # yet; they are wired at conjure like pre-conjure active spells.
                if self._conjured and self._conduit is not None:
                    conduit = self._get_required_conduit_surface()
                    caching_enabled = self._resolve_system_caching_enabled()
                    new_spell._add_owned_conduit(
                        conduit._id,
                        conduit._name,
                        conduit._creations,
                        dynamic_environment=conduit.__dynamic_environment__,
                        creation_gate_controller=conduit._creation_gate_controller,
                        caching_enabled=caching_enabled,
                    )
                if self._spell_ids is not None:
                    self._spell_ids.add(new_spell.spell_id)
                # Fold the parked spell from its own fresh index onto the caller's
                # target index (membership-only move; destroys the emptied source).
                self._apply_add_to_index(spell=new_spell, target_index=spell_index)
                # Staged binds are binds: they count toward the conjure
                # configuration-discipline evidence, and they map custody
                # the same way an active bind does (custody always; the
                # parked member seeds nothing until a notch promotes it).
                # Posture is already enforced above - this path is
                # structurally dynamic-only.
                if self._configuration is not None and not self._configuration._frozen:
                    self._binds_before_configuration_count += 1
                if self._crystallizer.activated:
                    self._crystallizer.emit_spell_crystal(
                        self._crystallizer.create_spell_crystal(
                            new_spell,
                            spellbook_id=self._id,
                        ),
                        active=False,
                    )
                    # The staged member joined an EXISTING index: re-emit
                    # its membership snapshot.
                    self._crystallizer.emit(
                        self._crystallizer.create_spell_index_crystal(
                            new_spell.spell_index, self._id
                        )
                    )
                # Research record: a staged bind is a world entry too
                # (bind_inactive is structurally dynamic-only, so no
                # posture re-check is needed here).
                self._record_research_world_entry(
                    new_spell.spell_id, staged=True,
                )
                return new_spell.spell_id
            except Exception as e:
                self._logger.error(f"Error while binding spell: {e}", "bind", exc_info=True)
                raise

    def _record_research_world_entry(
            self,
            spell_id: str,
            *,
            staged: bool,
    ) -> None:
        """
        Declare one world entry into the research record, when it is live.

        Purpose:
            The MutationResearch runtime seam: every dynamic-lane world
            entry (active bind or staged bind_inactive) is a formal
            research declaration once the MR root is active.

        Contract:
            - NO-OP unless the Aether-hosted MutationResearch root ALREADY
              EXISTS (it is never lazily constructed from the bind path)
              and is activated.
            - Rediscovery (identical content rebinding to the same SHA256)
              is a quiet no-op inside the root - research bookkeeping never
              gates a bind.

        Args:
            spell_id:
                Binding-signature SHA256 entering the world.
            staged:
                True for parked (`bind_inactive`) entries.

        Returns:
            None.
        """
        aether = Spellbook._aether
        if aether is None:
            return
        research = aether._mutation_research
        if research is None or research.cleaned or not research.activated:
            return
        research.record_world_entry(spell_id, staged=staged)

    def _record_research_promotion(
            self,
            from_spell_id: str | None,
            to_spell_id: str,
    ) -> None:
        """
        Record one notch selection change into the research record.

        Contract:
            - Same liveness gates as `_record_research_world_entry`; the
              root declares an unknown `to_spell_id` before journaling the
              promotion (world-entry catch-up).

        Args:
            from_spell_id:
                Previously selected spell id, when one existed.
            to_spell_id:
                Newly selected spell id.

        Returns:
            None.
        """
        aether = Spellbook._aether
        if aether is None:
            return
        research = aether._mutation_research
        if research is None or research.cleaned or not research.activated:
            return
        research.record_promotion(from_spell_id, to_spell_id)

    def bind(
            self,
            *,
            spell: Any,
            existence: str | Existence,
            permissions: str | Permissions = "create",
            spellframe: Any = None,
            binding_name: str | None = None,
            disposal_method_names: Sequence[str] | None = None,
            profile: str = "general",
            **kwargs: Any,
    ) -> str:
        """
        Bind a spell into the Spellbook for future instantiation and dependency
        injection.

        Purpose:
            Register one class, function, lambda, or existing object into the
            Spellbook's local registry so later conduit work can resolve it by
            spell identity, `(spellframe, binding_name)` lookup key, and
            lifecycle policy.

        Contract:
            - Direct spellbook-level `bind()` opens a bind-family transaction
              automatically when none is active.
            - If a bind-family transaction is already active, the method reuses
              that existing window.
            - The underlying registration semantics are identical whether the
              bind-family transaction window was opened explicitly or
              implicitly.

        Args:
            spell (Any):
                The class, function, lambda, or existing object to register.
            existence (Existence):
                Lifecycle scope for the spell.
            permissions (str):
                Permission level exposed to other conduits (`"read"`,
                `"create"`, or `"block"`).
            spellframe (Optional[Any]):
                Logical interface, frame, or grouping key for the spell.
            binding_name (Optional[str]):
                Secondary key used to distinguish this spell among others in
                the same frame.
            profile (str):
                Spell profile family to attach after bind completion.
            disposal_method_names (Optional[Sequence[str]]):
                Optional disposal method names to associate with the spell.
            **kwargs:
                Optional lifecycle hooks:
                - pre_hooks
                - activation_hooks
                - post_hooks

        Returns:
            str:
                The unique SHA256 `spell_id` associated with the bound spell.

        Raises:
            ValueError:
                If ``spell`` is ``None``.
            TypeError:
                If ``spell`` is a primitive value (int, float, bool, complex,
                str, bytes, bytearray); a spell must be a class, function,
                lambda, or an existing object instance.
        """
        self.check_cleaned()
        if spell is None:
            raise ValueError(
                "[SPELLBOOK] bind requires a spell target, but got None. "
                "Bind a class, function, lambda, or an existing object instance."
            )
        if isinstance(spell, (bool, int, float, complex, str, bytes, bytearray)):
            raise TypeError(
                "[SPELLBOOK] bind received a primitive "
                f"{type(spell).__name__!r}, which is not a valid spell target. "
                "Bind a class, function, lambda, or an existing object instance."
            )
        if self._bind_family_disabled_for_current_posture():
            self._logger.error(
                "bind denied by current frame posture",
                "bind",
            )
            raise RuntimeError(
                "[SPELLBOOK] Bind is disabled after conjure for the current frame posture."
            )
        # The bind transaction lives directly in this method: open a bind
        # window and run the registration inside it. If a bind session is
        # already active on this thread (a nested bind, or a bind issued
        # inside a conjure/scan window), the mediator joins the existing
        # session instead of opening a second root -- so one unconditional
        # `with` covers both the fresh and the reuse case. No separate
        # "is a bind transaction active?" pre-check is required.
        with self.transaction(
                "bind",
                metadata=self._build_bind_transaction_metadata(
                    origin_surface="spellbook.bind",
                    conduit_id=None,
                    scope_keys=None,
                    scope_hashes=None,
                    binding_keys=None,
                ),
        ):
            try:
                permissions_enum = EnumHelpers.convert_enum_and_check(permissions, Permissions)
                existence_enum = EnumHelpers.convert_enum_and_check(existence, Existence)
                if self._configured_disposal_method_names is None:
                    if disposal_method_names is not None:
                        self._configured_disposal_method_names = frozenset(
                            disposal_method_names
                        )
                    elif (
                            self._configuration is not None
                            and self._configuration.has_property("disposal_method_names")
                    ):
                        self._configured_disposal_method_names = frozenset(
                            self._configuration.get_property("disposal_method_names")
                        )
                    else:
                        self._configured_disposal_method_names = frozenset()

                new_spell = self._bind.bind(
                    permissions=permissions_enum,
                    spell=spell,
                    spellframe=spellframe,
                    binding_name=binding_name,
                    profile=profile,
                    existence=existence_enum,
                    aetheric_frame=self._aetheric_frame_name,
                    configured_disposal_method_names=self._configured_disposal_method_names,
                    # Owner ruling 2026-07-19: non-hook bind kwargs thread into
                    # Spell's construction (its native **kwargs metadata channel).
                    **{
                        key: value for key, value in kwargs.items()
                        if key not in ("pre_hooks", "activation_hooks", "post_hooks")
                    },
                )

                if Spellbook._aether._check_for_spell(new_spell.spell_id, self._aetheric_frame_name):
                    self._logger.error(
                        f"Spell with ID {new_spell.spell_id} already exists in the registry.",
                        "bind",
                        exc_info=True,
                    )
                    raise RuntimeError(
                        "Spell ID collision detected. spell_id is computed from the spell's bind-time \n"
                        "fingerprint (e.g., structural profile, lookup signature, existence, and resolved \n"
                        "disposal metadata). The existing spell with this id is already registered in the \n"
                        "Aether for this frame. If you intended to register a distinct spell, ensure its \n"
                        "bind-time fingerprint differs so it produces a unique spell_id."
                    )

                self._add_hooks_to_spell(new_spell, **kwargs)
                # Register into local spell maps
                spell_index = new_spell.spell_index
                # Framewide one-active-signature-per-frame gate (replaces the old
                # local-only lookup-key check): claim before committing local maps.
                self._aetheric_frame.claim_lookup(new_spell._key, new_spell.spell_id)
                self._lookup_spells[new_spell._key] = spell_index
                self._spells[spell_index] = new_spell
                self._register_owned_spell_id(new_spell.spell_id, new_spell)

                # Configuration-discipline evidence: count binds that ran
                # while the SpellbookConfiguration was still mutable. The
                # counter self-limits to pre-freeze binds (conjure freezes
                # the configuration), and dynamic-mode conjure refuses a
                # crystallizer-recorded world with a non-zero count.
                if self._configuration is not None and not self._configuration._frozen:
                    self._binds_before_configuration_count += 1

                # keep local version cache warm
                if self._spell_ids is not None:
                    member_ids = spell_index._spells_in_index
                    if member_ids:
                        for member_id in member_ids:
                            self._spell_ids.add(member_id)
                    else:
                        self._spell_ids.add(new_spell.spell_id)

                # If a Conduit already exists, stamp ownership metadata and runtime
                # resolution defaults for the new spell. Existing-object spells are
                # also eagerly registered into Creations.
                if self._conjured and self._conduit is not None:
                    conduit = self._get_required_conduit_surface()
                    caching_enabled = self._resolve_system_caching_enabled()
                    new_spell._add_owned_conduit(
                        conduit._id,
                        conduit._name,
                        conduit._creations,
                        dynamic_environment=conduit.__dynamic_environment__,
                        creation_gate_controller=conduit._creation_gate_controller,
                        caching_enabled=caching_enabled,
                    )
                    # Compilation is always full/eager (AOT/JIT knob removed);
                    # post-conjure spells get compiled via the gated revalidation
                    # paths, not via a deferred-resolution flag.
                    new_spell.resolution_required = False
                    if new_spell.user_created_object is not None:
                        try:
                            conduit._register_to_creations(
                                new_spell,
                                new_spell.user_created_object,
                            )
                        except Exception as reg_err:
                            self._logger.error(
                                f"Failed to register existing-object spell into Creations "
                                f"(spell_id={new_spell.spell_id}): {reg_err}",
                                "bind",
                                exc_info=True,
                            )

                self._spell_system_states.register_index(
                    spell_index=new_spell.spell_index,
                    owner_spellbook_id=self._id,
                )
                if self._conjured and self._conduit is not None:
                    self._register_spell_with_risk_manager(
                        self._get_required_conduit_surface()._id,
                        new_spell,
                    )
                self._stage_spell_for_structural_phases(new_spell)
                # Bind maps the crystal, uniformly: every bind (pre- or
                # post-conjure, active or staged) mints + emits custody
                # when the crystallizer records and the FRAME posture is
                # dynamic. The frame configuration is the posture truth
                # (owner canon: frames are configured before building;
                # Nexus-managed frames are born dynamic), and the conjure
                # guard already enforces configuration-before-bind in the
                # recorded lane - so bind-time knows everything it needs.
                if (
                        self._crystallizer.activated
                        and self._is_dynamic_posture()
                ):
                    self._crystallizer.emit_spell_crystal(
                        self._crystallizer.create_spell_crystal(
                            new_spell,
                            spellbook_id=self._id,
                        ),
                        active=True,
                    )
                    # Membership twin: every index state change re-emits
                    # the full snapshot (replace-on-emit keeps one per
                    # index); a fresh bind mints a fresh index.
                    self._crystallizer.emit(
                        self._crystallizer.create_spell_index_crystal(
                            new_spell.spell_index, self._id
                        )
                    )
                # Research record: every dynamic-lane world entry is a formal
                # declaration once MutationResearch is active (independent of
                # crystallizer recording; the root handles rediscovery).
                if self._is_dynamic_posture():
                    self._record_research_world_entry(
                        new_spell.spell_id, staged=False,
                    )
                if self._conjured and self._conduit is not None:
                    Spellbook._aether._register_single_spell_index(
                        self._get_required_conduit_surface()._id,
                        spell_index,
                        self._aetheric_frame_name,
                    )
                    self._publish_spell_record_to_nexus(new_spell)
                return new_spell.spell_id
            except Exception as e:
                self._logger.error(f"Error while binding spell: {e}", "bind", exc_info=True)
                raise

    def scan(self, module: ModuleType) -> list[str]:
        """
        Public API

        Scan a module for `scan_bind`-decorated objects and bind them.

        This is a module-only scan: it does not traverse packages or import
        submodules. Any object marked with `scan_bind` must originate from the
        scanned module, otherwise the scan fails.

        Contract:
            - Posture gate first. The scan is refused outright when the frame
              configuration sets `disable_bind`, and additionally - once this
              book has conjured - when the frame sets
              `disable_all_transactions_after_conjure` or when the frame's
              system state is anything other than `dynamic`. In practice:
              POST-CONJURE SCANNING REQUIRES A DYNAMIC FRAME. The refusal is a
              `RuntimeError` raised here, before any binding is attempted.
            - Transaction window is chosen, not always opened. When a
              bind-capable transaction is already active, scan runs inside the
              caller's window and opens nothing, so the whole scan commits or
              rolls back with that outer window. Only when no such window
              exists does scan open its own `"bind"` transaction, which makes
              the scan atomic in isolation.
            - Pre-conjure books always take the "already active" branch, so a
              pre-conjure scan never opens a transaction of its own.
            - Post-conjure, "already active" means a live BIND session on this
              spellbook's transaction identity, or - failing that - on its
              conduit's identity, and that session must advertise the `bind`
              capability.
            - Binding is delegated to `Scan.scan_module`, which walks the
              module dict in definition order.

        Threading:
            Takes no lock itself; serialization comes from the bind lane and
            from the transaction window in effect.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Args:
            module (ModuleType): The module to scan for decorated spell targets.
        Returns:
            list[str]: Spell IDs bound during the scan, in module dict order.
        Raises:
            TypeError: If `module` is not a module or metadata is invalid.
            ValueError: If the module does not own a decorated object.
            RuntimeError: If the current frame posture disables the bind family
                (see the posture gate above), or propagated from Spellbook.bind
                on binding errors.
        """
        self.check_cleaned()
        if self._bind_family_disabled_for_current_posture():
            self._logger.error(
                "scan denied by current frame posture",
                "scan",
            )
            raise RuntimeError(
                "[SPELLBOOK] Scan is disabled after conjure for the current frame posture."
            )
        scanner = Scan(self)
        if self._binding_transaction_is_active():
            return scanner.scan_module(module)
        with self.transaction(
                "bind",
                metadata=self._build_bind_transaction_metadata(
                    origin_surface="spellbook.scan",
                    conduit_id=None,
                    scope_keys=None,
                    scope_hashes=None,
                    binding_keys=None,
                ),
        ):
            return scanner.scan_module(module)

    def _add_hooks_to_spell(self, spell: Spell, **kwargs: Any) -> None:
        """
        Internal

        Attaches validation and lifecycle hooks to the newly bound spell object.

        Args:
            spell (Spell): The newly created spell object.
            **kwargs: Contains optional keys for `pre_hooks`, `activation_hooks`, and `post_hooks`.

        Raises:
            TypeError: If any provided hook is not callable.
        """
        if not isinstance(spell, Spell):
            self._logger.error("spell must be an instance of Spell.", "_add_hooks_to_spell", exc_info=True)
            raise TypeError("spell must be an instance of Spell.")
        if len(kwargs) == 0:
            return

        with self._lock:
            pre_hooks = None
            activation_hooks = None
            post_hooks = None
            if "pre_hooks" in kwargs:
                for hook in kwargs["pre_hooks"]:
                    if not callable(hook):
                        self._logger.error("pre_hooks must be a list of callables.", "_add_hooks_to_spell", exc_info=True)
                        raise TypeError("pre_hooks must be a list of callables.")
                pre_hooks = kwargs["pre_hooks"]
            if "activation_hooks" in kwargs:
                for hook in kwargs["activation_hooks"]:
                    if not callable(hook):
                        self._logger.error("activation_hooks must be a list of callables.", "_add_hooks_to_spell", exc_info=True)
                        raise TypeError("activation_hooks must be a list of callables.")
                activation_hooks = kwargs["activation_hooks"]
            if "post_hooks" in kwargs:
                for hook in kwargs["post_hooks"]:
                    if not callable(hook):
                        self._logger.error("post_hooks must be a list of callables.", "_add_hooks_to_spell", exc_info=True)
                        raise TypeError("post_hooks must be a list of callables.")
                post_hooks = kwargs["post_hooks"]

            if pre_hooks is not None or activation_hooks is not None or post_hooks is not None:
                spell._set_hooks(
                    pre_hooks=pre_hooks,
                    activation_hooks=activation_hooks,
                    post_hooks=post_hooks,
                )

    #endregion Binding API
    #region SpellbookConfiguration API
    def _initialize_configuration(self) -> None:
        """
        Internal

        Initialize configuration with the following rules:
          - If the canonical frame posture already permits explicit frame-wide
            rich-config sharing, and the frame already has such a config:
              * If a config was passed in, and it's different object, throw.
              * Otherwise, adopt the frame-owned config directly.
          - Otherwise:
              * If a config was passed in, verify its frame matches and keep it (unlocked).
              * Otherwise create a fresh SpellbookConfiguration for this frame (unlocked).
        """
        try:
            aether_config: SpellbookConfiguration | None = self._get_configuration_from_aether()
            if aether_config is not None:
                if self._configuration is not None and aether_config is not self._configuration:
                    self._logger.error(
                        "Aether configuration does not match provided configuration",
                        "_initialize_configuration",
                        exc_info=True,
                    )
                    raise RuntimeError("Aether configuration does not match the provided configuration.")

                self._configuration = aether_config
                self._configuration_locked = True
                return

            # No configuration registered in Aether yet
            if self._configuration is not None:
                # User supplied a configuration object
                if self._configuration._aether_frame != self._aetheric_frame_name:
                    self._logger.error(
                        "SpellbookConfiguration name does not match the aetheric frame",
                        "_initialize_configuration",
                        exc_info=True,
                    )
                    raise RuntimeError("SpellbookConfiguration name does not match the aetheric frame.")

                self._configuration_locked = False
                return

            # No config in Aether and none provided: create a fresh one and load defaults.
            self._configuration = SpellbookConfiguration(self._aetheric_frame_name)
            self._configuration.load_default_dictionary()
            self._configuration_locked = False
        except Exception as e:
            self._logger.error(
                f"Failed to initialize configuration: {e}",
                "_initialize_configuration",
                exc_info=True,
            )
            raise

    def _get_configuration_from_aether(self) -> SpellbookConfiguration | None:
        """
        Internal

        Retrieve the current frame-owned shared rich configuration from Aether,
        when the canonical frame posture explicitly permits shared rich config.

        Returns:
            SpellbookConfiguration | None: The frame-owned shared rich configuration for
            this Aether frame, or None when explicit shared rich-config reuse is
            not active.
        """
        try:
            frame_configuration = self._aetheric_frame_configuration
            if (
                frame_configuration is None
                or not frame_configuration.shared_framewide_spellbook_configuration
            ):
                return None
            return Spellbook._aether._get_configuration(self._aetheric_frame_name)
        except Exception as e:
            self._logger.error(
                f"Error retrieving configuration from Aether: {e}",
                "_get_configuration_from_aether",
                exc_info=True,
            )
            raise

    def _is_frame_owned_shared_configuration(
            self,
            configuration: SpellbookConfiguration | None = None,
    ) -> bool:
        """
        Internal

        Determine whether one rich Spellbook configuration is the frame-owned
        shared configuration for this Spellbook's frame.

        Args:
            configuration:
                Optional configuration object to check. When omitted, the
                Spellbook's current `_configuration` reference is used.

        Returns:
            bool: True when the given configuration is the current frame-owned
            shared rich configuration and the active frame posture explicitly
            enables that sharing mode.
        """
        target_configuration = configuration
        if target_configuration is None:
            target_configuration = self._configuration
        if target_configuration is None:
            return False
        try:
            frame_configuration = self._aetheric_frame_configuration
            if (
                frame_configuration is None
                or not frame_configuration.shared_framewide_spellbook_configuration
            ):
                return False
            shared_configuration = Spellbook._aether._get_configuration(
                self._aetheric_frame_name
            )
            return shared_configuration is target_configuration
        except Exception:
            return False

    def _initialize_aetheric_frame_configuration(self) -> None:
        """
        Internal

        Attach the frame-owned `AethericFrameConfiguration` reference for this
        Spellbook.

        Contract:
            - The owning `AethericFrame` creates the default posture object.
            - Spellbook only retrieves and retains that frame-owned object.
        """
        try:
            frame_configuration = Spellbook._aether._get_aetheric_frame_configuration(
                self._aetheric_frame_name
            )
            if frame_configuration is None:
                raise RuntimeError("AethericFrameConfiguration is unavailable.")
            self._aetheric_frame_configuration = frame_configuration
        except Exception as e:
            self._logger.error(
                f"Failed to initialize frame configuration: {e}",
                "_initialize_aetheric_frame_configuration",
                exc_info=True,
            )
            raise


    def _get_risk_manager(self) -> Any | None:
        """
        Internal

        Resolve the per-frame RiskManager, if available.
        """
        try:
            devops = Spellbook._aether._get_devops_manager(self._aetheric_frame_name)
        except Exception:
            return None
        return devops.risk_manager

    def _set_spellbook_validation_required(self, required: bool) -> None:
        """
        Internal

        Update the meld validation gate for this Spellbook.
        """
        self._spellbook_validation_required = bool(required)

    def _register_conduit_with_risk_manager(self, conduit: Conduit) -> None:
        """
        Internal

        Register this Spellbook's conduit in the RiskManager.
        """
        if conduit is None:
            return
        risk_manager = self._get_risk_manager()
        if risk_manager is None:
            return
        try:
            risk_manager.register_conduit(conduit._id, self)
        except Exception as e:
            self._logger.error(
                f"RiskManager registration failed: {e}",
                "_register_conduit_with_risk_manager",
                exc_info=True,
            )

    def _unregister_conduit_from_risk_manager(self, conduit_id: str) -> None:
        """
        Internal

        Unregister this Spellbook's conduit from the RiskManager.
        """
        if not conduit_id:
            return
        risk_manager = self._get_risk_manager()
        if risk_manager is None:
            return
        try:
            risk_manager.unregister_conduit(conduit_id)
        except Exception as e:
            self._logger.error(
                f"RiskManager unregister failed: {e}",
                "_unregister_conduit_from_risk_manager",
                exc_info=True,
            )

    def _register_spell_with_risk_manager(self, conduit_id: str, spell: Spell) -> None:
        """
        Internal

        Register a spell in the RiskManager for the owning conduit.
        """
        if not conduit_id or spell is None:
            return
        risk_manager = self._get_risk_manager()
        if risk_manager is None:
            return
        try:
            risk_manager.register_spell(conduit_id, spell)
        except Exception as e:
            self._logger.error(
                f"RiskManager spell registration failed: {e}",
                "_register_spell_with_risk_manager",
                exc_info=True,
            )

    def _unregister_spell_with_risk_manager(self, conduit_id: str, spell: Spell) -> None:
        """
        Internal

        Unregister a spell from the RiskManager for the owning conduit.
        """
        if not conduit_id or spell is None:
            return
        risk_manager = self._get_risk_manager()
        if risk_manager is None:
            return
        try:
            risk_manager.unregister_spell(conduit_id, spell)
        except Exception as e:
            self._logger.error(
                f"RiskManager spell unregister failed: {e}",
                "_unregister_spell_with_risk_manager",
                exc_info=True,
            )

    def is_configuration_locked(self) -> bool:
        """
        Public API

        Report whether this spellbook's configuration is frozen.

        Purpose:
            Answer "can configuration still change?" before attempting a
            configuration-mutating call, so callers can branch instead of
            provoking a refusal.

        Contract:
            - Starts `False` on a newly constructed book.
            - Becomes `True` on the paths that commit this book to a
              configuration - conjure, and adoption of a frame-shared
              configuration - and returns to `False` on the paths that replace
              or reset the configuration outright.
            - Reports the LOCK FLAG only. It says nothing about whether a
              configuration object is actually present; an unlocked book may
              still have no configuration at all (see `get_configuration`).

        Threading:
            Unsynchronized read of a plain bool. It is a snapshot, not a
            reservation - a concurrent conjure can flip it immediately after
            this returns, so a `False` here does not guarantee a subsequent
            configuration write will be accepted.

        Lifecycle / Cleanup:
            NOT guarded by `check_cleaned()`, and the backing slot is deleted
            during core teardown. Calling this on a cleaned spellbook therefore
            raises `AttributeError` rather than the `RuntimeError` the guarded
            methods raise. Do not use it as a liveness probe.

        Returns:
            bool: True if the configuration is locked, False otherwise.

        Raises:
            AttributeError: If the spellbook has already been cleaned.
        """
        return self._configuration_locked



    def _validate_and_freeze_configuration(self) -> None:
        """
        Internal

        Validates configuration, then freezes it (no further mutation allowed).
        Sets `_configuration_locked` upon success.

        This assumes that any desired properties (including AI-native flags,
        worker counts, etc.) have already been applied via the SpellbookConfiguration's
        own API. This method does not mutate properties; it only validates and
        finalizes.

        Raises:
            ValueError: If validation fails.
            RuntimeError: If no configuration is present.
        """
        if self._configuration is None:
            self._logger.error(
                "No configuration instance available to validate/freeze.",
                "_validate_and_freeze_configuration",
                exc_info=True,
            )
            raise RuntimeError("No configuration instance available to validate/freeze.")

        # If the configuration is already frozen (the recorded lane's law:
        # finalize BEFORE the first bind), re-enter freeze WITH origin
        # identity anyway - the freeze transition no-ops on a frozen
        # configuration, but the spellbook-twin emission (conjure is the
        # emission factor for recorded worlds) must still fire. Skipping
        # this call left every legal recorded world without its book twin
        # (restore_engine_2026_07_07 round-trip finding).
        if self._configuration._frozen:
            self._configuration.freeze(
                origin_spellbook_id=self._id,
                origin_frame_name=self._aetheric_frame_name,
                origin_dynamic=self._conjure_dynamic_hint,
            )
            self._configuration_locked = True
            return

        try:

            if not self._configuration.validate():
                self._logger.error(
                    "SpellbookConfiguration validation failed.",
                    "_validate_and_freeze_configuration",
                    exc_info=True,
                )
                raise ValueError("SpellbookConfiguration validation failed.")

            self._configuration.freeze(
                origin_spellbook_id=self._id,
                origin_frame_name=self._aetheric_frame_name,
                origin_dynamic=self._conjure_dynamic_hint,
            )
            self._configuration_locked = True

        except Exception as e:
            self._logger.error(
                f"Error validating/freezing configuration: {e}",
                "_validate_and_freeze_configuration",
                exc_info=True,
            )
            raise




    def _bind_configuration_to_aether(self) -> None:
        """
        Internal

        Bind the now-frozen rich configuration into Aether only when the
        effective frame posture permits explicit shared rich-config reuse.

        Contract:
            - The first shared rich configuration bound for the frame wins.
            - Later concurrent binders adopt the frame-owned shared
              configuration instead of overwriting it.
        """
        if self._configuration is None:
            self._logger.error(
                "No configuration instance available to bind to Aether.",
                "_bind_configuration_to_aether",
                exc_info=True,
            )
            raise RuntimeError("No configuration instance available to bind to Aether.")

        frame_configuration = self._aetheric_frame_configuration

        if frame_configuration is not None:
            if not frame_configuration.shared_framewide_spellbook_configuration:
                return

            existing_shared_configuration = Spellbook._aether._get_configuration(
                self._aetheric_frame_name
            )
            if existing_shared_configuration is not None:
                if existing_shared_configuration is not self._configuration:
                    local_configuration = self._configuration
                    self._configuration = existing_shared_configuration
                    self._configuration_locked = True
                    if local_configuration is not None:
                        local_configuration.cleanup()
                return

        else:
            return
        try:
            Spellbook._aether._bind_configuration(self._configuration, self._aetheric_frame_name)
            shared_configuration = Spellbook._aether._get_configuration(
                self._aetheric_frame_name
            )
            if (
                    shared_configuration is not None
                    and shared_configuration is not self._configuration
            ):
                local_configuration = self._configuration
                self._configuration = shared_configuration
                self._configuration_locked = True
                if local_configuration is not None:
                    local_configuration.cleanup()
        except Exception as e:
            self._logger.error(
                f"Failed to bind configuration to Aether: {e}",
                "_bind_configuration_to_aether",
                exc_info=True,
            )
            raise

    def _bind_aetheric_frame_configuration_to_aether(self) -> None:
        """
        Internal

        Bind the retained frame-owned AR posture reference into Aether.

        Contract:
            - Uses the `AethericFrame`-owned posture reference already attached
              to this Spellbook.
            - Binds it through the owning `AethericFrame`, which freezes it on
               the first successful bind or accepts Nexus-provided posture that was
              already bound earlier.

        Returns:
            None.

        Raises:
            RuntimeError: If no frame posture reference exists.
            Exception: Propagates failures from Aether
                binding.
        """
        if self._aetheric_frame_configuration is None:
            self._logger.error(
                "No frame configuration instance available to bind to Aether.",
                "_bind_aetheric_frame_configuration_to_aether",
                exc_info=True,
            )
            raise RuntimeError(
                "No frame configuration instance available to bind to Aether."
            )

        try:
            frame = Spellbook._aether._ensure_frame(self._aetheric_frame_name)
            frame.bind_frame_configuration(
                self._aetheric_frame_configuration
            )
        except Exception as e:
            self._logger.error(
                f"Failed to bind AethericFrameConfiguration to Aether: {e}",
                "_bind_aetheric_frame_configuration_to_aether",
                exc_info=True,
            )
            raise

    def _refresh_nexus_publish_enabled(self) -> bool:
        """
        Internal

        Refresh the cached passive Nexus publication flag from the retained
        frame-owned posture reference.

        Returns:
            bool: True when the current frame is publishable into Nexus.
        """
        frame_configuration = self._aetheric_frame_configuration
        self._nexus_publish_enabled = (
            frame_configuration is not None and frame_configuration.rift_enabled
        )
        return self._nexus_publish_enabled

    def _publish_nexus_state_for_conjure(self, conduit: Conduit) -> None:
        """
        Internal

        Publish the frame/root-conduit spell state into Nexus after successful
        conjure wiring.

        Args:
            conduit:
                Root conduit created during conjuring.

        Returns:
            None.
        """
        if not self._refresh_nexus_publish_enabled():
            conduit_surface = conduit
            conduit_surface._nexus_publish_enabled = False
            return

        conduit_surface = conduit
        conduit_surface._nexus_publish_enabled = True
        self._nexus._publish_frame_record(self)
        self._nexus._publish_conduit_record(conduit)
        for spell in self._spells.values():
            self._nexus._publish_spell_record(self, spell, conduit._id)

    def _publish_spell_record_to_nexus(self, spell: Spell) -> None:
        """
        Internal

        Publish one incremental spell record into Nexus after bind when the
        Spellbook already has a root conduit.

        Args:
            spell:
                Newly bound spell.

        Returns:
            None.
        """
        if not self._nexus_publish_enabled:
            return
        if not self._conjured or self._conduit is None:
            return

        owner_conduit_id = spell._owner_conduit_id or self._conduit._id
        self._nexus._publish_spell_record(self, spell, owner_conduit_id)

    def _replace_spell_record_in_nexus(
            self,
            old_spell_id: str,
            spell: Spell,
    ) -> None:
        """
        Internal

        Replace one published SpellRecord after the active version id changes.

        Args:
            old_spell_id:
                Previous current spell/version id.
            spell:
                Spell whose `spell_id` now reflects the new current version id.

        Returns:
            None.
        """
        if not self._nexus_publish_enabled:
            return

        self._nexus._remove_spell_record(
            self._id,
            old_spell_id,
            self._aetheric_frame_name,
        )
        self._nexus._publish_spell_record(self, spell, spell._owner_conduit_id)

    def _remove_spells_from_nexus(self) -> None:
        """
        Internal

        Remove all currently published local spell records for this Spellbook
        from Nexus during Spellbook cleanup.

        Returns:
            None.
        """
        if not self._nexus_publish_enabled:
            return
        if self._spells is None:
            return
        for spell in self._spells.values():
            self._nexus._remove_spell_record(
                self._id,
                spell.spell_id,
                self._aetheric_frame_name,
            )



    def get_configuration(self) -> SpellbookConfiguration:
        """
        Public API

        Return the active configuration object for this Spellbook.

        Contract:
            - Returns the LIVE configuration object, not a copy or a snapshot.
              Configuration objects are deliberately shared between spellbooks
              on the same frame, so mutating the returned object is visible to
              every book sharing it. Treat the result as read-only unless you
              intend that reach.
            - Raises rather than returning None. A spellbook constructed
              without an explicit configuration holds none until one is adopted
              or created, and calling this in that window is an error, not an
              empty result.

        Threading:
            Unsynchronized read. The reference is stable once adopted, but the
            object it points at is shared mutable state.

        Lifecycle / Cleanup:
            NOT guarded by `check_cleaned()`, and the backing slot is deleted
            during teardown, so a call on a cleaned spellbook raises
            `AttributeError` rather than the documented `RuntimeError`.

        Returns:
            SpellbookConfiguration: The active configuration instance.

        Raises:
            RuntimeError: If this spellbook has no configuration yet.
            AttributeError: If the spellbook has already been cleaned.
        """
        return self._get_required_configuration()

    def configure_aether_frame(
            self,
            *,
            system_state: str | None,
            disposal: bool | None,
            disposal_method_names: list[str] | None,
            system_caching_enabled: bool | None = None,
            ai_native: bool | None = None,
            rift_enabled: bool | None = None,
            shared_framewide_spellbook_configuration: bool | None = None,
            system_cache_root_path: str | Path | None = None,
            disable_all_transactions_after_conjure: bool | None = None,
            disable_mutations: bool | None = None,
            disable_linking: bool | None = None,
            disable_bind: bool | None = None,
            disable_conduit_cluster: bool | None = None,
            disable_transfer_of_ownership: bool | None = None,
            disable_contract_mutation: bool | None = None,
            max_transaction_wait_time_in_seconds: float | None = None,
    ) -> None:
        """
        Public API

        Apply frame/runtime posture inputs, freeze configuration, and bind the
        result into Aether for this spellbook's frame.

        Purpose:
            This is the ONE public door onto a book's frame posture. The
            `AethericFrameConfiguration` this method writes through is created
            and retained by the spellbook itself - it is never handed to the
            caller - so every knob that is not a parameter here is a knob no
            user can reach. That made two capabilities unreachable from the
            public root before this door was widened:

              - `rift_enabled` is the frame's OPT-IN TO BEING OBSERVABLE. It
                gates passive Nexus publication
                (`_refresh_nexus_publish_enabled`) and static AR attachment,
                which raises `"AR requires rift_enabled on target frame"` when
                it is False.
              - `ai_native` is the AI-native runtime posture, and it is the
                single consistency rule `AethericFrameConfiguration.validate()`
                enforces.

        Contract:
            - Uses the existing spellbook configuration and frame-configuration
              objects rather than creating a parallel setup path.
            - Applies only provided values; omitted values leave the current state
              unchanged. `None` means "do not touch", NOT "reset to default" -
              there is no way to clear a knob through this door, only to set it.
            - COVERS THE WHOLE FRAME POSTURE. Every `with_*` builder on
              `AethericFrameConfiguration` has a parameter here.
            - `system_state` IS APPLIED FIRST, DELIBERATELY. `ai_native`
              requires dynamic state and that rule is enforced at FREEZE rather
              than at assignment, so ordering the two lets a single call move a
              frame to dynamic and enable AI-native together. Passing
              `ai_native=True` without a dynamic frame (either already dynamic
              or made so by `system_state` in this same call) succeeds here and
              makes the later frame freeze raise `ValueError`.
            - PRE-SETTLEMENT ONLY. The frame posture freezes when the frame
              settles at conjure, and every `with_*` builder refuses afterwards.
              This method does not freeze the frame posture itself; it freezes
              the rich SPELLBOOK configuration and binds that to the owning
              Aether frame.
            - NOT ATOMIC. Values are applied in parameter order and a rejected
              value leaves the earlier ones already written. Re-call with a
              corrected argument rather than assuming the posture is untouched.

        Threading:
            Each `with_*` assignment takes the frame configuration's own lock
            individually; this method holds no lock spanning the group, which
            is why the sequence is not atomic.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The frame configuration is owned by
            this spellbook and is not the caller's to clean.

        Args:
            system_state:
                Optional frame system-state name, e.g. `"dynamic"` or
                `"automatic"`. Applied before every other posture value.
            disposal:
                Optional disposal toggle for the rich spellbook configuration.
            disposal_method_names:
                Optional replacement disposal-method list.
            system_caching_enabled:
                Optional replacement system-caching-enabled toggle.
            ai_native:
                Optional AI-native frame posture. Requires the frame to be
                dynamic by the time it freezes.
            rift_enabled:
                Optional Rift-visibility opt-in. Must be True for a Rift to
                attach to this frame, for static AR to target it, and for the
                frame to publish passively into Nexus.
            shared_framewide_spellbook_configuration:
                Optional toggle for sharing one spellbook configuration across
                every book on the frame.
            system_cache_root_path:
                Optional replacement cache-root fragment, as a `str` or `Path`.
                MUST BE RELATIVE - it is resolved against the melder package
                root, not the working directory, and an absolute path raises
                `ValueError`.
            disable_all_transactions_after_conjure:
                Optional toggle that closes the transaction surface once the
                frame has conjured.
            disable_mutations:
                Optional toggle that refuses spell mutation on this frame.
            disable_linking:
                Optional toggle that refuses conduit linking on this frame.
            disable_bind:
                Optional toggle that refuses further binding on this frame.
            disable_conduit_cluster:
                Optional toggle that refuses conduit clustering on this frame.
            disable_transfer_of_ownership:
                Optional toggle that refuses ownership transfer on this frame.
            disable_contract_mutation:
                Optional toggle that refuses contract mutation on this frame.
            max_transaction_wait_time_in_seconds:
                Optional transaction wait ceiling, in seconds.

        Returns:
            None.

        Raises:
            RuntimeError: If this spellbook has been cleaned, if the frame
                configuration or the spellbook configuration is unavailable, or
                if the frame posture has already frozen.
            TypeError: If a posture value is not the type its `with_*` builder
                requires.
            ValueError: If the spellbook configuration fails validation during
                the freeze that closes this call.
        """
        self.check_cleaned()
        frame_configuration = self._aetheric_frame_configuration
        if frame_configuration is None:
            raise RuntimeError("AethericFrameConfiguration is unavailable.")
        # system_state leads on purpose: ai_native's dynamic requirement is
        # checked at freeze, so applying the state first lets one call satisfy
        # both. Do not reorder these two.
        if system_state is not None:
            frame_configuration.with_system_state(system_state)
        if system_caching_enabled is not None:
            frame_configuration.with_system_caching_enabled(system_caching_enabled)
        if ai_native is not None:
            frame_configuration.with_ai_native(ai_native)
        if rift_enabled is not None:
            frame_configuration.with_rift_enabled(rift_enabled)
        if shared_framewide_spellbook_configuration is not None:
            frame_configuration.with_shared_framewide_spellbook_configuration(
                shared_framewide_spellbook_configuration,
            )
        if system_cache_root_path is not None:
            frame_configuration.with_system_cache_root_path(system_cache_root_path)
        if disable_all_transactions_after_conjure is not None:
            frame_configuration.with_disable_all_transactions_after_conjure(
                disable_all_transactions_after_conjure,
            )
        if disable_mutations is not None:
            frame_configuration.with_disable_mutations(disable_mutations)
        if disable_linking is not None:
            frame_configuration.with_disable_linking(disable_linking)
        if disable_bind is not None:
            frame_configuration.with_disable_bind(disable_bind)
        if disable_conduit_cluster is not None:
            frame_configuration.with_disable_conduit_cluster(disable_conduit_cluster)
        if disable_transfer_of_ownership is not None:
            frame_configuration.with_disable_transfer_of_ownership(
                disable_transfer_of_ownership,
            )
        if disable_contract_mutation is not None:
            frame_configuration.with_disable_contract_mutation(disable_contract_mutation)
        if max_transaction_wait_time_in_seconds is not None:
            frame_configuration.with_max_transaction_wait_time_in_seconds(
                max_transaction_wait_time_in_seconds,
            )

        configuration = self._configuration
        if configuration is None:
            raise RuntimeError("Spellbook configuration is unavailable.")
        if disposal is not None:
            configuration.set_property("disposal", disposal)
        if disposal_method_names is not None:
            configuration.set_property(
                "disposal_method_names",
                disposal_method_names,
            )

        self._validate_and_freeze_configuration()
        self._bind_configuration_to_aether()

    #endregion SpellbookConfiguration API
    #region Conduit API

    def create_new_preset_spellbook(self) -> Spellbook:
        """
        Internal

        Create a new `Spellbook` on this book's frame, sharing its configuration.

        Used when upgrading a lesser conduit's spellbook to a normal conduit
        spellbook.

        Contract:
            - Shares the configuration OBJECT by reference; it is not copied.
              The new book and this one therefore observe each other's
              configuration mutations. That sharing is the point of the call -
              the upgraded conduit must land on the same frame policy - so
              callers must not treat the new book's configuration as private.
            - Carries over the aetheric frame name, so both books resolve to
              the same frame.
            - Carries over NOTHING else. The new book gets a fresh generated
              `id`, its own logger, and an empty spell registry; bindings,
              spell indexes, and conduit attachment do not transfer. Migrating
              spells is the caller's job.
            - Constructs only. It does not register the new book with this one,
              conjure it, or attach it to any conduit.

        Threading:
            Takes no lock. The new book is unpublished and reachable only by
            the caller until the caller shares it.

        Lifecycle / Cleanup:
            The returned book is independently owned - cleaning this spellbook
            does not clean it. Because the configuration is shared, however,
            the new book keeps that object alive.

        Returns:
            Spellbook: A new Spellbook instance ready for use by a normal conduit.
        """
        return Spellbook(self._aetheric_frame_name, self._configuration)

    @property
    def conduit(self) -> Conduit | None:
        """
        Return this book's conjured root conduit, or None pre-conjure.

        Purpose:
            Public accessor (spell_index_graft 2026-07-12): borrowers -
            the crystallizer's graft runner first among them - previously
            had no public read for the conjured conduit and would have
            needed the `_conduit` slot as a documented seam.

        Contract:
            - `None` is a normal answer, not a failure. It means the book has
              not conjured, and it is how borrowers detect an unconjured host
              rather than by catching an exception.
            - Returns the ROOT conduit only. Lesser conduits and contracted
              conduits are not reachable through this accessor.
            - Returns a live reference, not a handle or proxy. Reading it does
              not keep the conduit alive or prevent its teardown.

        Threading:
            Unsynchronized read. Because the value transitions from `None` to
            the root conduit at conjure, a caller racing conjure can observe
            either; re-read rather than caching the `None`.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. Distinguish the two negative
            outcomes: `None` means "not conjured yet", while `RuntimeError`
            means "this spellbook is gone".

        Returns:
            Optional[Conduit]: The live root conduit, or None when this
            book has not conjured yet.

        Raises:
            RuntimeError: If the spellbook has been cleaned.
        """
        self.check_cleaned()
        return self._conduit

    @property
    def mutation_research(self) -> MutationResearch:
        """
        Return the Aether-hosted MutationResearch WORLD root.

        Purpose:
            Accessor door (owner ruling 2026-07-12): hand back the one
            process-wide research root without routing through `Aether`,
            mirroring how this book already carries `_crystallizer`.

        Contract:
            - The reference is BORROWED and world-scoped: it is the exact
              object `Aether().mutation_research` returns, never a book-
              or conduit-scoped view. This book never cleans it.
            - The door only returns the object. Activation, liveness, and
              recording gates are enforced by the root's own verbs; an
              inactive root refuses research work itself.
            - Bound once at `__init__`; the reference is stable for this
              book's lifetime and deleted during cleanup.

        Returns:
            MutationResearch: The hosted mutation-research singleton root.

        Raises:
            RuntimeError: If the spellbook has been cleaned.
        """
        self.check_cleaned()
        return self._mutation_research

    def _settle_or_inherit_conjure_mode(self, dynamic: bool) -> bool:
        """
        Internal

        Resolve the EFFECTIVE conjure mode under the settle-then-inherit
        law (owner ruling 2026-07-20):

        Contract:
            - UNSETTLED world (frame posture still the unfrozen birth
              default): dynamic=True SETTLES the world dynamic through the
              canonical bind_frame_configuration lifecycle (first bind
              freezes); plain conjure leaves settlement to the existing
              derive-and-bind step (automatic).
            - SETTLED world (posture frozen/explicit): every conjure
              INHERITS the world's mode; the flag never polices - dynamic-
              only operations fail later at their own gates, on purpose.
        Args:
            dynamic (bool): The caller's requested mode (settlement input
                on unsettled worlds; ignored in favor of the world's truth
                on settled worlds).
        Returns:
            bool: The effective conjure mode.
        """
        frame_configuration = self._aetheric_frame_configuration
        if frame_configuration is None:
            # check_system_state keeps its honest missing-posture refusal.
            return dynamic
        if dynamic and not frame_configuration._frozen:
            # Settlement: conjure is the settlement point for unset
            # configuration - the flag is a legitimate input here.
            # Settle the RETAINED frame-owned posture object ITSELF
            # (with_system_state + rebind of the SAME object):
            # bind_frame_configuration's unfrozen branch copies attempted
            # values over the canonical posture only for a DIFFERENT
            # object, so binding a fresh posture here would bulldoze
            # every flag staged pre-conjure (with_disable_*, ai_native,
            # rift, wait bound) back to defaults.
            if frame_configuration.system_state is not SystemState.dynamic:
                frame_configuration.with_system_state(SystemState.dynamic)
            self._aetheric_frame.bind_frame_configuration(frame_configuration)
        return frame_configuration.system_state is SystemState.dynamic

    def conjure(
            self,
            policy: str | None = "default",
            dynamic: bool = False,
            name: str | None = None,
            conduit_logger: Any | None = None,
    ) -> Conduit:
        """
        Public API

        Creates a new **Conduit** (execution channel) from this Spellbook.

        This method finalizes the configuration, validates all local spells, and instantiates the `Conduit`.
        Conjuring disables the default binding transaction; post-conjure bind/scan
        requires an explicit bind-family transaction through
        `begin_transaction("bind")` or
        `transaction("bind")`.

        Args:
            policy (str, optional):
                Access control policy for this conduit (dynamic-only modes). Must match a `Policies` enum member.
                Defaults to "default".
            dynamic (bool, optional):
                If True, operate in dynamic mode and require `system_state` to
                be dynamic. Defaults to False.
            name (str, optional):
                An optional name for the conduit.
            conduit_logger (Any, optional):
                An optional logger instance to attach to the conduit for logging purposes.

        Returns:
            Conduit: The newly created Conduit instance.

        Raises:
            RuntimeError: If this Spellbook has already conjured a Conduit (only one is allowed).
            RuntimeError: If dynamic-only policies are used when `system_state` is "automatic" or when `dynamic` is False.
            ValueError: If the configuration fails validation or the policy string is invalid.

        Policies:
            - **Non-dynamic mode (dynamic=False)**: only `"default"` is allowed (linking disabled).
            - **Dynamic mode (dynamic=True and `system_state` is dynamic)**:
                * `"default"`: normal per-spell rules.
                * `"whitelist_all"` / `"block_all"`: override per-spell whitelist behaviour.
                * `"inbound_only"` / `"outbound_only"`: directional link restrictions.

        Hook integration
        ----------------
        If the active SpellbookConfiguration has Conduit lifecycle hooks registered under this
        Spellbook's ID, they are fetched via
        "SpellbookCreationSystem.get_conjure_hook_map()" and invoked
        in the following order:

            1. "on_conduit_pre_created()"
                   Fired **before** the Conduit is constructed. No Conduit instance
                   is passed because it does not exist yet.

            2. "on_conduit_activated(conduit)"
                   Fired immediately after the Conduit has been constructed
                   (its "__init__" has run), but before it is wired into spells.

            3. "on_conduit_post_created(conduit)"
                   Fired after the Conduit has been integrated into all local
                   spells via
                   "SpellbookCreationSystem.define_conduit_into_spells".

        For conjured (root) conduits, these hooks receive:

            - pre  : no arguments
            - act : (conduit,)
            - post : (conduit,)
        """
        self.check_cleaned()
        mediator = self._get_required_transaction_mediator()
        mediator.start_transaction(
            identity=self._transaction_identity,
            transaction_type=ChangeTransactionType.CONJURE,
            metadata={
                "spellbook_id": self._id,
                "origin_surface": "spellbook.conjure",
            },
        )
        try:
            return self._conjure_within_transaction_window(
                policy=policy,
                dynamic=self._settle_or_inherit_conjure_mode(dynamic),
                name=name,
                conduit_logger=conduit_logger,
            )
        finally:
            mediator.end_transaction_for_identity(
                identity=self._transaction_identity,
                transaction_type=ChangeTransactionType.CONJURE,
            )

    def _conjure_within_transaction_window(
            self,
            *,
            policy: str | None,
            dynamic: bool,
            name: str | None,
            conduit_logger: Any | None,
    ) -> Conduit:
        """
        Internal

        Run the conjure creation pipeline inside the held CONJURE transaction
        window.

        Contract:
            - Called only by `conjure()` after the CONJURE change-control
              transaction has claimed the owning spellbook EXCLUSIVE.
            - Preserves the single-conjure invariant and the original creation
              flow unchanged.
        Threading:
            - The CONJURE embargo is acquired by `conjure()` BEFORE this method
              takes the Spellbook lock, preserving embargo-then-lock ordering so
              a concurrent bind (spellbook INTENT, then lock) cannot deadlock a
              conjure (spellbook EXCLUSIVE, then lock).
        """
        self._conjure_dynamic_hint = dynamic
        with self._lock:
            # Dynamic-mode configuration discipline (crystallizer worlds):
            # a recorded world must not be born from binds that ran while
            # the configuration was still mutable -- the profile record and
            # default bootstrap would durably persist config-incoherent
            # bind truth. Automatic mode and crystallizer-off worlds are
            # exempt so non-recorded runtimes stay byte-identical.
            if (
                    dynamic
                    and self._binds_before_configuration_count > 0
                    and self._crystallizer.activated
            ):
                early_bind_count = self._binds_before_configuration_count
                self._logger.error(
                    f"conjure refused: {early_bind_count} bind(s) preceded configuration "
                    "finalization in a dynamic crystallizer world",
                    "conjure",
                )
                raise RuntimeError(
                    "[SPELLBOOK] Dynamic-mode conjure with an active Crystallizer requires the \n"
                    f"SpellbookConfiguration to be finalized BEFORE the first bind. {early_bind_count} spell(s) \n"
                    "were bound while the configuration was still mutable, so the recorded world \n"
                    "(profiles, checkpoints, the default bootstrap) would persist binds that ran \n"
                    "against unsettled configuration. Fix: build and finalize the configuration \n"
                    "first, pass it to the Spellbook before binding, then conjure. Automatic-mode \n"
                    "worlds and worlds without an active Crystallizer are not affected."
                )
            if self._conjured:
                conduit_id = None
                conduit_name = None
                if self._conduit is not None:
                    conduit_id = self._conduit._id
                    conduit_name = self._conduit._name
                if self._logger is not None:
                    self._logger.error(
                        "Conjure denied: Spellbook already has a conduit "
                        f"(spellbook_id={self._id}, conduit_id={conduit_id}, "
                        f"conduit_name={conduit_name}).",
                        "conjure",
                        exc_info=True,
                    )
                raise RuntimeError(
                    "This Spellbook has already conjured a Conduit. "
                    "Only one is allowed per Spellbook. "
                    f"(spellbook_id={self._id}, conduit_id={conduit_id}, "
                    f"conduit_name={conduit_name})"
                )
            if self._configured_disposal_method_names is not None:
                for spell in self._spells.values():
                    if not isinstance(spell.disposal_method_names, frozenset):
                        raise RuntimeError(
                            "Spell disposal metadata must be frozen before conjure."
                        )
                    if spell.has_disposal_methods != bool(
                            spell.disposal_method_names
                    ):
                        raise RuntimeError(
                            "Spell disposal flags are inconsistent before conjure."
                        )

            # Frame-wide spell_id integrity, checked BEFORE any conduit work.
            # Registration into the frame happens inside Conduit.__init__
            # (`_configure_conduit_state` -> `_add_spells_to_aether`), so a
            # collision detected there would surface after phases 1-11 have run
            # and a Conduit object exists, leaving a half-built conduit to
            # unwind. This refuses at the cheapest possible moment instead.
            self._spell_id_integrity_checker()

            spellbook_creation_system = SpellbookCreationSystem(
                spellbook=self,
                policy=policy,
                dynamic=dynamic,
                name=name,
                conduit_logger=conduit_logger,
                phase_scheduler_cls=PhaseScheduler,
            )
            try:
                return spellbook_creation_system.conjure()
            finally:
                try:
                    spellbook_creation_system.cleanup()
                except Exception as e:
                    if self._logger is not None:
                        self._logger.error(
                            f"Failed to cleanup SpellbookCreationSystem: {e}",
                            "conjure",
                            exc_info=True,
                        )

    def _set_policy_state(self, policy: Policies) -> None:
        """
        Internal

        Placeholder method to set the policy state for the conduit.

        Args:
            policy (Policies): The policy to set.
        """
        with self._lock:
            if policy == Policies.whitelist_all:
                self._block_all_spells = False
                self._whitelist_all_spells = True
            elif policy == Policies.block_all:
                self._block_all_spells = True
                self._whitelist_all_spells = False
            else:
                # Default: clear any prior flags
                self._block_all_spells = False
                self._whitelist_all_spells = False

    def _run_structural_phases(self) -> dict[str, Sequence[UnitOfWork]]:
        """
        Internal

        Purpose:
            Execute structural phases (1-4) for this Spellbook.
        Contract:
            - Delegates structural orchestration to `SpellbookCreationSystem`.
            - Uses Spellbook's `PhaseScheduler` symbol to preserve patch points.
            - Does not mutate registry membership; updates phase artifacts only.
        Threading:
            Caller must hold the Spellbook lock for deterministic conjure ordering.
        Returns:
            Dict[str, Sequence[UnitOfWork]]: Phase execution result mapping.
        Raises:
            SpellbookValidationError: If structural validation marks any spell broken.
            Exception: Propagates scheduler/phase execution failures.
        """
        return SpellbookCreationSystem.run_structural_phases(
            spellbook=self,
            phase_scheduler_cls=PhaseScheduler,
        )

    def _get_or_create_phase_scheduler(
            self,
            phase_scheduler_cls: type[PhaseScheduler],
    ) -> PhaseScheduler:
        """
        Internal

        Return the Spellbook-owned persistent phase scheduler, creating it
        lazily on first use.

        Purpose:
            Provide the single long-lived scheduler (and its worker pool)
            that every conjure phase group and lazy revalidation run borrows,
            replacing the per-group construct/spawn/join lifecycle.

        Contract:
            - Creates the scheduler on first call with this Spellbook and its
              active configuration; later calls return the same instance.
            - Preserves the `phase_scheduler_cls` patch seam: when a caller
              supplies a different scheduler class than the live instance's
              type (test stubs), the live instance is cleaned and replaced so
              patched runs are deterministic.
            - The returned scheduler's worker pool is spawned lazily on its
              first run, not here.

        Args:
            phase_scheduler_cls:
                Scheduler class to instantiate (patch point; defaults to
                `PhaseScheduler` at every call site).

        Returns:
            PhaseScheduler: The live Spellbook-owned scheduler.

        Raises:
            RuntimeError: If the Spellbook has been cleaned.

        Threading:
            Callers hold the Spellbook lock on every phase-run path, so
            lazy creation does not race itself.
        """
        self.check_cleaned()
        scheduler = self._phase_scheduler
        if scheduler is not None and type(scheduler) is phase_scheduler_cls:
            return scheduler
        if scheduler is not None:
            # Patch-seam replacement: a different scheduler class was
            # requested than the live instance (test stubs). Retire the old
            # pool deterministically before installing the new one.
            try:
                scheduler.cleanup()
            except Exception as e:
                self._logger.error(
                    f"Error cleaning replaced phase scheduler: {e}",
                    "_get_or_create_phase_scheduler",
                    exc_info=True,
                )
        scheduler = phase_scheduler_cls(
            spellbook=self,
            configuration=self._configuration,
        )
        self._phase_scheduler = scheduler
        return scheduler

    def _run_post_conjure_structural_phases(self, spells: Sequence[Spell]) -> None:
        """
        Internal

        Purpose:
            Execute structural phases for spells bound after conduit conjure.
        Contract:
            - Delegates execution to `SpellbookCreationSystem`.
            - Applies only to the provided spell sequence.
            - Leaves already-conjured conduit state intact.
        Threading:
            Caller must hold the Spellbook lock while mutating the bound spell state.
        Args:
            spells: Newly bound spells requiring structural validation.
        Returns:
            None.
        Raises:
            SpellbookValidationError: If any provided spell validates as broken.
            Exception: Propagates phase execution failures.
        """
        SpellbookCreationSystem.run_post_conjure_structural_phases(
            spellbook=self,
            spells=spells,
        )

    def _run_resolution_phases_for_conduit(
            self,
            conduit_id: str,
    ) -> dict[str, Sequence[UnitOfWork]]:
        """
        Internal

        Purpose:
            Execute conduit-scoped resolution phases (5-11) for one conduit id.
        Contract:
            - Delegates orchestration to `SpellbookCreationSystem`.
            - Uses Spellbook's `PhaseScheduler` symbol to preserve patch points.
            - Cleans temporary phase artifacts before returning.
        Threading:
            Caller must hold the Spellbook lock for a consistent conduit scope state.
        Args:
            conduit_id: Conduit id for resolution scope.
        Returns:
            Dict[str, Sequence[UnitOfWork]]: Phase execution result mapping.
        Raises:
            ValueError: If conduit_id is empty.
            Exception: Propagates phase execution failures.
        """
        return SpellbookCreationSystem.run_resolution_phases_for_conduit(
            spellbook=self,
            conduit_id=conduit_id,
            phase_scheduler_cls=PhaseScheduler,
        )

    def _run_resolution_phases_for_target_spell(
            self,
            conduit_id: str,
            target_spell: Spell,
    ) -> dict[str, Sequence[UnitOfWork]]:
        """
        Internal

        Purpose:
            Execute local resolution phases for one target spell in a conduit scope.
        Contract:
            - Delegates orchestration to `SpellbookCreationSystem`.
            - Uses Spellbook's `PhaseScheduler` symbol to preserve patch points.
            - Restricts cleanup and diagnostics to target-local scope.
        Threading:
            Caller must hold the Spellbook lock for deterministic target revalidation.
        Args:
            conduit_id: Conduit id for resolution scope.
            target_spell: Spell being resolved locally.
        Returns:
            Dict[str, Sequence[UnitOfWork]]: Phase execution result mapping.
        Raises:
            ValueError: If conduit_id is empty or target_spell is None.
            PhaseExecutionError: On non-visibility execution failures.
        """
        return SpellbookCreationSystem.run_resolution_phases_for_target_spell(
            spellbook=self,
            conduit_id=conduit_id,
            target_spell=target_spell,
            phase_scheduler_cls=PhaseScheduler,
        )

    def _run_deferred_resolution_phases_for_target_spell(
            self,
            conduit_id: str,
            target_spell: Spell,
    ) -> dict[str, Sequence[UnitOfWork]]:
        """
        Internal

        Purpose:
            Execute local deferred plan phases (8-11) for one target spell.
        Contract:
            - Delegates orchestration to `SpellbookCreationSystem`.
            - Uses Spellbook's `PhaseScheduler` symbol to preserve patch points.
            - Restricts execution/cleanup to target-local deferred scope.
        Threading:
            Caller must hold target spell synchronization for deterministic
            deferred runtime gating.
        Args:
            conduit_id: Conduit id for deferred-resolution scope.
            target_spell: Spell being resolved in deferred mode.
        Returns:
            Dict[str, Sequence[UnitOfWork]]: Phase execution result mapping.
        Raises:
            ValueError: If conduit_id is empty or target_spell is None.
            PhaseExecutionError: On non-visibility execution failures.
        """
        return SpellbookCreationSystem.run_deferred_resolution_phases_for_target_spell(
            spellbook=self,
            conduit_id=conduit_id,
            target_spell=target_spell,
            phase_scheduler_cls=PhaseScheduler,
        )

    #endregion
#endregion
