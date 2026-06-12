from contextlib import contextmanager
from types import MappingProxyType, ModuleType, TracebackType
from typing import TYPE_CHECKING, Optional, List, Any, Mapping, Sequence, Dict, Set, Iterable, Tuple, Generator, Union, \
    ClassVar
import threading
import time


# Melder Imports
from melder.aether.aether import Aether
from melder.aether.aetheric_frame.dev_ops.devops_identity import (
    DevopsIdentity,
)
from melder.aether.spellbook.bind.scan import Scan
from melder.aether.spellbook.spellbook_creation_system import SpellbookCreationSystem
from melder.aether.spellbook.configuration.system_state import SystemState
from melder.utilities.caching_system.caching_system import CachingSystem
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.bind.bind import Bind
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.utilities.helpers.general_helpers import EnumHelpers
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.spellbook.spell import Spell
from melder.utilities.helpers.init_helpers import InitHelpers
from melder.utilities.helpers.general_helpers import SpellInputUtils
from melder.utilities.synchronization.phase_scheduler import PhaseScheduler
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.nexus.nexus import Nexus

if TYPE_CHECKING:
    from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_states import (
        SpellSystemStates,
    )
    from melder.aether.conduit.conduit import Conduit
    from melder.aether.spellbook.bind.spell_index import SpellIndex
    from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.transaction_mediator import (
        TransactionMediator,
    )
    from melder.utilities.synchronization.unit_of_work import UnitOfWork
    from melder.aether.aetheric_frame.aetheric_frame_configuration import AethericFrameConfiguration
    from melder.utilities.logger.safe_logger import SafeLogger

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
    """
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    _aether: ClassVar[Aether] = Aether()
    __slots__ = Cleanable.__slots__ + [
        "__dict__",
        "__weakref__",
        "_aetheric_frame",
        "_aetheric_frame_configuration",
        "_bind",
        "_block_all_spells",
        "_conduit",
        "_configuration",
        "_configuration_locked",
        "_conjured",
        "_cache_emit_required",
        "_caching_enabled",
        "_caching_system",
        "_contracted_spells",
        "_contracted_spells_by_id",
        "_contracted_versions",
        "_id",
        "_lock",
        "_logger",
        "_lookup_contracted_spells",
        "_nexus",
        "_nexus_publish_enabled",
        "_lookup_spells",
        "_pending_binding_frame_keys",
        "_pending_structural_spells",
        "_configured_disposal_method_names",
        "_spell_id_pool",
        "_spell_system_states",
        "_spell_versions",
        "_spellbook_validation_required",
        "_spells",
        "_spells_by_id",
        "_transaction_identity",
        "_whitelist_all_spells",
    ]

    def __init__(self, aetheric_frame: str = "default", configuration: Optional[SpellbookConfiguration] = None,
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
        """
        super().__init__()

        # Internal state
        self._lock: threading.RLock = threading.RLock()
        self._id: str = IDBuilder.create_id()
        self._nexus: Nexus = Nexus()
        self._conjured = False
        self._cache_emit_required: bool = False
        self._caching_enabled: bool = False
        self._caching_system: Optional[CachingSystem] = None
        self._pending_binding_frame_keys: Set[str] = set()
        self._pending_structural_spells: List[Spell] = []
        self._configured_disposal_method_names: Optional[frozenset[str]] = None
        self._conduit: Optional[Conduit] = None
        self._nexus_publish_enabled: bool = False
        self._aetheric_frame: str = aetheric_frame
        if not isinstance(self._aetheric_frame, str):
            raise TypeError(f"aetheric_frame must be a string, got {type(self._aetheric_frame).__name__}")
        Spellbook._aether._ensure_frame(self._aetheric_frame)
        self._transaction_identity: DevopsIdentity = DevopsIdentity(
            owner_kind="spellbook",
            owner_id=self._id,
            aetheric_frame_name=self._aetheric_frame,
            metadata={
                "conjured": False,
                "conduit_id": None,
            },
            available_transactions=(
                "bind",
                "scan",
            ),
        )
        self._transaction_identity.attach_registry(
            Spellbook._aether._get_existing_frame(
                self._aetheric_frame,
            ).devops_information_registry,
            object_ref=self,
        )
        self._refresh_devops_identity_state()

        # SpellbookConfiguration state
        self._configuration_locked: bool = False
        self._configuration: Optional[SpellbookConfiguration] = configuration
        self._aetheric_frame_configuration: Optional[AethericFrameConfiguration] = None
        # Temporary logger for configuration init; will be replaced in _initialize_logging.
        self._logger: SafeLogger = InitHelpers.resolve_safe_logger(None)
        self._initialize_aetheric_frame_configuration()
        self._initialize_configuration()
        self._caching_enabled = self._resolve_system_caching_enabled()

        # Logger setup
        self._initialize_logging(logger)

        # Core spell storage (SpellIndex Maps)
        self._spells: Dict[SpellIndex, Spell] = {} # Active Spells not all spell indexed spells
        self._spell_versions: Set[str] = set()
        self._lookup_spells: Dict[tuple, SpellIndex]  = {}
        self._spells_by_id: Dict[str, Spell] = {}
        self._spell_id_pool: Dict[str, Spell] = {}

        # Networked/remote spell support
        # This stores spells borrowed from other conduits (keyed by peer Conduit id)
        self._contracted_spells: Dict[str, Dict[SpellIndex, Spell]] = {}  # Active Contracted Spells not all spell indexed spells
        self._contracted_versions: Dict[str, Set[str]] = {}
        self._lookup_contracted_spells: Dict[str, Dict[tuple, SpellIndex]]  = {}
        self._contracted_spells_by_id: Dict[str, Dict[str, Spell]] = {}

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
        self._remove_spells_from_nexus()
        # 1) Clean ONLY local spells (not contracted)
        self._cleanup_spells()

        try:
            self._spells.clear()
        except Exception as e:
            self._logger.error(f"Error clearing _spells: {e}", "_cleanup_components", exc_info=True)
        del self._spells

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
        try:
            self._lookup_spells.clear()
        except Exception as e:
            self._logger.error(f"Error cleaning _lookup_spells: {e}", "_cleanup_components", exc_info=True)
        del self._lookup_spells

        try:
            self._contracted_spells.clear()
        except Exception as e:
            self._logger.error(f"Error cleaning _contracted_spells: {e}", "_cleanup_components", exc_info=True)
        del self._contracted_spells

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

        self._aetheric_frame_configuration = None

        try:
            self._spell_versions.clear()
        except Exception as e:
            self._logger.error(f"Error cleaning _spell_versions: {e}", "_cleanup_components", exc_info=True)
        del self._spell_versions

        try:
            self._contracted_versions.clear()
        except Exception as e:
            self._logger.error(f"Error cleaning _contracted_versions: {e}", "_cleanup_components", exc_info=True)
        del self._contracted_versions

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
        target_spell: Optional[Spell]
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

            self._spells.pop(target_spell_index, None)
            existing_lookup = self._lookup_spells.get(target_lookup_key)
            if existing_lookup is target_spell_index:
                self._lookup_spells.pop(target_lookup_key, None)

        if self._conjured and owner_conduit_id:
            self._unregister_spell_with_risk_manager(owner_conduit_id, target_spell)
            self._aether._remove_spells_from_aether(
                owner_conduit_id,
                {target_spell_index},
                self._aetheric_frame,
            )

        self._unregister_owned_spell_id(target_spell_id, target_spell)

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
        del self._spellbook_validation_required
        del self._nexus_publish_enabled
        del self._nexus

        try:
            if hasattr(self._logger, "cleanup"):
                self._logger.cleanup()
        except Exception as e:
            self._logger.error(f"Error during logger cleanup: {e}", "_cleanup_core", exc_info=True)
        del self._logger


    #endregion Disposal
    #region Context Manager
    def __enter__(self) -> "Spellbook":
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
            exc_type: Optional[type[BaseException]],
            exc_value: Optional[BaseException],
            traceback: Optional[TracebackType],
    ) -> None:
        """
        Exit the Spellbook lock context.

        Returns:
            None.
        """
        self._lock.release()

    #endregion Context Manager

    def _refresh_local_spell_versions(self) -> None:
        """
        Internal

        Rebuilds the local version cache (`_spell_versions`) from the current
        set of SpellIndex keys in `_spells`.

        This is useful after bulk mutation or research operations that may
        have changed the version lists on SpellIndex instances.
        """
        with self._lock:
            if self._spell_versions is None or self._spells is None:
                return

            self._spell_versions.clear()

            for spell_index in self._spells.keys():
                versions = spell_index._versions
                if not versions:
                    continue
                for version_id in versions:
                    self._spell_versions.add(version_id)

    def _refresh_contracted_spell_versions(self) -> None:
        """
        Internal

        Rebuilds the per-conduit contracted version caches (`_contracted_versions`)
        from the current `_contracted_spells` structure.

        After this runs:
            - Each conduit_id in `_contracted_spells` will have a corresponding
              ConcurrentSet[str] in `_contracted_versions` containing all
              version IDs (SHA256) for that conduitÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â‚¬Å¾Ã‚Â¢s spells.
        """
        with self._lock:
            if self._contracted_spells is None or self._contracted_versions is None:
                return

            # Blow away old caches and rebuild them from scratch
            self._contracted_versions.clear()

            for conduit_id, spell_map in self._contracted_spells.items():
                version_set = set[str]()
                for spell_index in spell_map.keys():
                    versions = spell_index._versions
                    if not versions:
                        continue
                    for version_id in versions:
                        version_set.add(version_id)
                self._contracted_versions[conduit_id] = version_set


    def _refresh_all_spell_versions(self) -> None:
        """
        Internal

        Convenience method to refresh both local and contracted
        spell version caches in one call.
        """
        self._refresh_local_spell_versions()
        self._refresh_contracted_spell_versions()

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
            conduit_name: Optional[str] = None,
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
                frame_name=self._aetheric_frame,
                conduit_name=conduit_name,
                cache_root_path=self._aetheric_frame_configuration.resolve_system_cache_root_path(),
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
            from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized_cache.manifest.generalized_cache_manifest import (
                MANIFEST_METADATA_KEY,
            )
            if (
                    artifact._spell_codegen_creation.metadata.get(
                        MANIFEST_METADATA_KEY
                    )
                    is not None
            ):
                # generalized_cache family output: the manifest already IS the
                # cache payload, so export is a metadata read instead of a
                # full both-lane recompile.
                from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized_cache.generalized_cache_creation_cache import (
                    build_package as build_generalized_cache_package,
                )
                spell_payload = build_generalized_cache_package(spell)
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
            if self._spell_versions is not None:
                self._spell_versions.add(new_id)
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
            self._spell_versions.discard(spell_id)
        if self._nexus_publish_enabled:
            self._nexus._remove_spell_record(
                self._id,
                spell_id,
                self._aetheric_frame,
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
            if self._contracted_versions is not None:
                versions_set = self._contracted_versions.get(conduit_id)
                if versions_set is None:
                    self._logger.error(
                        f"Contracted version cache missing for conduit_id={conduit_id}",
                        "_update_contracted_spell_id",
                        exc_info=True,
                    )
                    raise RuntimeError(f"Contracted version cache missing for conduit_id={conduit_id}")
                versions_set.add(new_id)

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
                    props={"aether_frame": self._aetheric_frame},
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

        Return the unique identifier of this Spellbook instance.

        Returns:
            str:
                This Spellbook's unique identifier.
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
        contracted_views: Dict[str, Mapping[SpellIndex, Spell]] = {
            conduit_id: MappingProxyType(dict(spells))
            for conduit_id, spells in self._contracted_spells.items()
        }
        contracted_spells_view: Mapping[str, Mapping[SpellIndex, Spell]] = (
            MappingProxyType(contracted_views)
        )
        return contracted_spells_view

    def snapshot_state(self) -> Dict[str, Any]:
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
            spell_versions = set(self._spell_versions) if self._spell_versions is not None else set()

            contracted_spells: Dict[str, Dict[SpellIndex, Spell]] = {}
            if self._contracted_spells is not None:
                for conduit_id, spells in self._contracted_spells.items():
                    contracted_spells[conduit_id] = dict(spells)

            lookup_contracted_spells: Dict[str, Dict[Tuple[str, str], SpellIndex]] = {}
            if self._lookup_contracted_spells is not None:
                for conduit_id, lookup_map in self._lookup_contracted_spells.items():
                    lookup_contracted_spells[conduit_id] = dict(lookup_map)

            contracted_versions: Dict[str, Set[str]] = {}
            if self._contracted_versions is not None:
                for conduit_id, versions in self._contracted_versions.items():
                    contracted_versions[conduit_id] = set(versions)

        return {
            "snapshot_id": snapshot_id,
            "captured_at_ms": captured_at_ms,
            "spellbook_id": self._id,
            "aetheric_frame": self._aetheric_frame,
            "local_spells": local_spells,
            "lookup_spells": lookup_spells,
            "spell_versions": spell_versions,
            "contracted_spells": contracted_spells,
            "lookup_contracted_spells": lookup_contracted_spells,
            "contracted_versions": contracted_versions,
        }

    #endregion Properties

    #region Core Methods
    #region General Methods
    def find_spell_by_id(self, spell_id: str) -> Optional[Spell]:
        """
        Finds a spell by its unique identifier within the spellbook.

        Args:
            spell_id: The identifier of the spell to find.

        Returns:
            Optional[Spell]: The spell if found, otherwise None.
        """
        self.check_cleaned()
        for spell_index, spell in self._spells.items():
            # SpellIndex is responsible for telling us whether it owns this version
            if spell_index.has_version(spell_id):
                return spell

        return None

    def get_spell_permissions(self, spell_index: SpellIndex) -> Optional[str]:
        """
        Public API

        Retrieves the access permissions for a **locally** registered spell.

        Args:
            spell_index:
                The SpellIndex of the spell.

        Returns:
            Optional[str]:
                The permissions name (``"read"``, ""create"", or
                ""block"") for this spell.

        Raises:
            RuntimeError:
                If the spell with the given index is not found in the
                local spellbook.
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

    def _find_spell(self, spell_index: SpellIndex) -> Optional[Spell]:
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

    def _find_contracted_spell(self, spell_index: SpellIndex) -> Optional[Spell]:
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
    ) -> Optional[SpellIndex]:
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
    ) -> Optional[SpellIndex]:
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
    ) -> Optional[Spell]:
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


    def find_spell_index(self, spellframe: str, spell_name: str, binding_name: str) -> Optional[SpellIndex]:
        """
        Public API

        Finds a spell's SpellIndex using its logical identifiers.

        The search checks local spells first, then contracted spells.

        Args:
            spellframe (str): The logical namespace or grouping label.
            spell_name (str): The name of the spell class or function.
            binding_name (str): The secondary key to distinguish the spell.

        Returns:
            Optional[SpellIndex]: The SpellIndex associated with this spell.

        Raises:
            RuntimeError: If the spell is not found in the spellbook (local or contracted).
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
            binding_name: Optional[str],
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

    def find_spell_key(self, spellframe: str, spell_name: str, binding_name: str) -> Optional[tuple]:
        """
        Public API

        Finds a spell's primary lookup key using its logical identifiers.

        The search checks local spells first, then contracted spells.

        Args:
            spellframe (str): The logical namespace or grouping label.
            spell_name (str): The name of the spell class or function.
            binding_name (str): The secondary key to distinguish the spell.

        Returns:
            Optional[tuple]: The spell's lookup key (`(frame_or_name, binding_name_or_default)`).

        Raises:
            RuntimeError: If the spell key is not found (local or contracted).
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
    ) -> Optional[str]:
        """
        Public API

        Inspects an object instance to determine its unique SHA256 ID, then checks if that ID
        is registered anywhere in the Aether Registry (globally).

        Args:
            spell (Any): The object to inspect (class, function, or instance).
            aetheric_frame (str): The Aetheric Frame to check the global registry against.

        Returns:
            Optional[str]: The unique SHA256 ID of the spell if it is registered in the Aether, else None.
        """
        with self._lock:
            try:
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
            self._aetheric_frame,
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
                self._aetheric_frame,
            )

    def _get_conduit_by_spell_id(
            self,
            spell_id: str,
            aetheric_frame_name: str = "default",
    ) -> Optional[Conduit]:
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
            aetheric_frame_name = self._aetheric_frame
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
            aetheric_frame_name = self._aetheric_frame
        return bool(self._aether._check_for_spell(spell_id, aetheric_frame_name))

    def _get_spell_by_id_via_aether(
            self,
            spell_id: str,
            aetheric_frame_name: str = "default",
    ) -> Optional[Spell]:
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
            aetheric_frame = self._aetheric_frame
            version_ids = self._spell_versions

            if version_ids:
                for spell_version_id in version_ids:
                    if check_for_spell(spell_version_id, aetheric_frame):
                        self._logger.error(
                            f"Spell with ID {spell_version_id} already exists in the registry.",
                            "_check_all_spells",
                            exc_info=True,
                        )
                        raise RuntimeError(f"Spell with ID {spell_version_id} already exists in the registry.")
                return

            for spell_index in self._spells.keys():
                versions = spell_index._versions
                if not versions:
                    continue
                for spell_version_id in versions:
                    if check_for_spell(spell_version_id, aetheric_frame):
                        self._logger.error(
                            f"Spell with ID {spell_version_id} already exists in the registry.",
                            "_check_all_spells",
                            exc_info=True,
                        )
                        raise RuntimeError(f"Spell with ID {spell_version_id} already exists in the registry.")


    #endregion General Methods
    #region Contract API
    def _find_contracted_spell_by_id(self, spell_id: str, conduit_id: str) -> Optional[Spell]:
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
            if spell_index.has_version(spell_id):
                return spell

        return None



    def _create_link_contract(self, conduit_id: str) -> None:
        """
        Internal

        Initializes the internal storage maps for a new contract link with a peer conduit.

        This method ensures `_contracted_spells` (value map), `_lookup_contracted_spells`
        (key map), `_contracted_versions` (version cache), and
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
        c_exists = conduit_id in self._contracted_versions
        d_exists = conduit_id in self._contracted_spells_by_id

        if not (a_exists == b_exists == c_exists == d_exists):
            self._logger.error("Inconsistent link contract state", "_create_link_contract", exc_info=True)
            raise RuntimeError(
                f"Inconsistent link contract state for conduit ID {conduit_id}: "
                f"_contracted_spells={a_exists}, "
                f"_lookup_contracted_spells={b_exists}, "
                f"_contracted_versions={c_exists}, "
                f"_contracted_spells_by_id={d_exists}"
            )

        if not a_exists and not b_exists and not c_exists and not d_exists:
            with self._lock:
                self._contracted_spells[conduit_id] = {}
                self._lookup_contracted_spells[conduit_id] = {}
                self._contracted_versions[conduit_id] = set()
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
        c_exists = conduit_id in self._contracted_versions
        d_exists = conduit_id in self._contracted_spells_by_id

        if not (a_exists == b_exists == c_exists == d_exists):
            self._logger.error("Inconsistent link contract state", "_remove_link_contract", exc_info=True)
            raise RuntimeError(
                f"Inconsistent link contract state for conduit ID {conduit_id}: "
                f"_contracted_spells={a_exists}, "
                f"_lookup_contracted_spells={b_exists}, "
                f"_contracted_versions={c_exists}, "
                f"_contracted_spells_by_id={d_exists}"
            )

        if a_exists:
            with self._lock:
                self._contracted_spells.pop(conduit_id, None)
                self._lookup_contracted_spells.pop(conduit_id, None)
                self._contracted_versions.pop(conduit_id, None)
                self._contracted_spells_by_id.pop(conduit_id, None)


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
            versions_set = self._contracted_versions[conduit_id]

            spell_index = spell.spell_index
            spell_index._attach_contracted(self, conduit_id, spell)

            # Main maps: SpellIndex? Spell and key? SpellIndex
            spell_map[spell_index] = spell
            lookup_map[spell_key] = spell_index

            # Track all known versions for this SpellIndex in the per-conduit version set
            versions = spell_index._versions
            if versions:
                for version_id in versions:
                    versions_set.add(version_id)

            frame_key = spell.key[0]
            should_mark = bool(self._conjured)

        if should_mark and frame_key:
            self._mark_collection_dependents_dirty({frame_key})
        self._try_update_staged_contract_keys(conduit_id)
        if self._conjured and self._conduit is not None:
            self._register_spell_with_risk_manager(self._conduit._id, spell)


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
            versions_set = self._contracted_versions.get(conduit_id)

            if spell_map is None or lookup_map is None or versions_set is None:
                self._logger.error(
                    f"No contracted spell maps for conduit {conduit_id}",
                    "_remove_contracted_spell",
                    exc_info=True,
                )
                raise RuntimeError(f"No contracted spell maps found for conduit ID {conduit_id}.")

            # Find the SpellIndex whose version list contains this version SHA
            spell_index = None
            spell = None
            for idx, s in spell_map.items():
                versions = idx._versions
                if versions and spell_id in versions:
                    spell_index = idx
                    spell = s
                    break

            if spell_index is None or spell is None:
                self._logger.error(
                    f"Spell version {spell_id} not found for conduit {conduit_id}",
                    "_remove_contracted_spell",
                    exc_info=True,
                )
                raise RuntimeError(f"Spell version {spell_id} not found for conduit ID {conduit_id}.")

            spell_index._detach_contracted(self, conduit_id)

            # Remove from main map
            spell_map.pop(spell_index, None)

            # Remove from lookup map
            key = self._make_spell_key(spell.spellframe, spell.spell_name, spell.binding_name)
            lookup_map.pop(key, None)

            # Remove *all* versions for this SpellIndex from the version cache
            versions = spell_index._versions
            if versions:
                for version_id in versions:
                    versions_set.discard(version_id)
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

        removed_spells: List[Spell] = []
        with self._lock:
            if (
                conduit_id not in self._contracted_spells
                or conduit_id not in self._lookup_contracted_spells
                or conduit_id not in self._contracted_versions
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
                spell.spell_index._detach_contracted(self, conduit_id)

            self._contracted_spells[conduit_id].clear()
            self._lookup_contracted_spells[conduit_id].clear()
            self._contracted_versions[conduit_id].clear()
            self._contracted_spells_by_id[conduit_id].clear()
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

    def _get_required_transaction_mediator(self) -> "TransactionMediator":
        """
        Internal

        Return the frame-owned live transaction mediator.

        Returns:
            TransactionMediator:
                Transaction mediator instance owned by the frame control plane.
        """
        change_control = self._aether._get_change_control_manager(
            self._aetheric_frame,
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
            transaction_type="bind",
        )
        if session is None and self._conduit is not None:
            session = self._get_required_transaction_mediator().get_session_for_identity(
                identity=self._conduit._transaction_identity,
                transaction_type="bind",
            )
        if session is None:
            return False
        return session.supports_capabilities(("bind",))

    #endregion Contract API
    #region Binding API

    def _normalize_change_transaction_type(
            self,
            value: str,
    ) -> str:
        """
        Internal

        Normalize a transaction type input to its lowercase string form.

        Purpose:
            Keep the public Spellbook transaction boundary string-based while
            still validating supported transaction names early.
        Contract:
            - Accepts plain strings and StrEnum-backed string values.
            - Comparison is case-insensitive for string inputs.
        Args:
            value:
                Transaction type as a string-like value.
        Returns:
            str:
                Lowercase normalized transaction type.
        Raises:
            ValueError: If the value is empty or not a valid transaction type.
            TypeError: If the value is not a string-like value.
        """
        if isinstance(value, str):
            candidate = value.strip().lower()
            if not candidate:
                raise ValueError("transaction_type cannot be empty.")
            if candidate not in (
                    "bind",
                    "link",
                    "transfer_ownership",
                    "mutation",
                    "cluster_link",
            ):
                raise ValueError(
                    "Invalid transaction_type "
                    f"'{value}'. Expected one of: "
                    "['bind', 'link', 'transfer_ownership', 'mutation', 'cluster_link']."
                )
            return candidate
        raise TypeError(
            "transaction_type must be a string-like value."
        )

    def begin_transaction(
            self,
            transaction_type: str,
            *,
            conduit_id: Optional[str] = None,
            conduit_ids: Optional[Iterable[str]] = None,
            scope_keys: Optional[Iterable[str]] = None,
            scope_hashes: Optional[Iterable[str]] = None,
            binding_keys: Optional[Iterable[Tuple[str, str]]] = None,
            contract_keys: Optional[Iterable[Tuple[str, str, str]]] = None,
            metadata: Optional[Dict[str, Any]] = None,
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
                Optional normalized scope keys for conflict checks.
            scope_hashes:
                Optional normalized scope hashes for conflict checks.
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
        request_type = self._normalize_change_transaction_type(transaction_type)
        mediator = self._get_required_transaction_mediator()
        if request_type == "bind":
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
            mediator.start_transaction(
                identity=self._transaction_identity,
                transaction_type="bind",
                metadata=bind_metadata,
            )
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
            self._aetheric_frame,
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
            transaction_type: Optional[str] = None,
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
            transaction_type="bind",
        )
        if transaction_type is not None:
            expected_type = self._normalize_change_transaction_type(
                transaction_type,
            )
            if bind_session is not None and expected_type != "bind":
                raise RuntimeError(
                    "[SPELLBOOK] Active change transaction does not match the requested type."
                )
            if expected_type == "bind" and bind_session is not None:
                mediator.end_transaction_for_identity(
                    identity=self._transaction_identity,
                    transaction_type="bind",
                )
                return
        request = mediator.get_active_request()
        if request is None:
            raise RuntimeError("[SPELLBOOK] No active change transaction to end.")
        session = mediator.get_session_by_request_id(request.request_id)
        if session is None:
            raise RuntimeError("[SPELLBOOK] Active transaction session could not be resolved.")

        if transaction_type is not None:
            expected_type = self._normalize_change_transaction_type(transaction_type)
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
            transaction_type: str,
            *,
            conduit_id: Optional[str] = None,
            conduit_ids: Optional[Iterable[str]] = None,
            scope_keys: Optional[Iterable[str]] = None,
            scope_hashes: Optional[Iterable[str]] = None,
            binding_keys: Optional[Iterable[Tuple[str, str]]] = None,
            contract_keys: Optional[Iterable[Tuple[str, str, str]]] = None,
            metadata: Optional[Dict[str, Any]] = None,
    ) -> Generator["Spellbook", None, None]:
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
                Optional normalized scope keys for conflict checks.
            scope_hashes:
                Optional normalized scope hashes for conflict checks.
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
            conduit_id: Optional[str],
            scope_keys: Optional[Iterable[str]],
            scope_hashes: Optional[Iterable[str]],
            binding_keys: Optional[Iterable[Tuple[str, str]]],
    ) -> Dict[str, object]:
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
            _staged: Optional[Any] = None,
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

    def _ensure_binding_transaction_active(self, *, action: str) -> None:
        """
        Internal

        Raise if a binding transaction is not active for the given action.

        Args:
            action: Operation name for diagnostics (e.g., "bind" or "scan").
        Returns:
            None.
        Raises:
            RuntimeError: If no binding transaction is active.
        """
        if not self._binding_transaction_is_active():
            self._logger.error(
                f"{action} requires an active binding transaction",
                action,
            )
            raise RuntimeError(
                f"[SPELLBOOK] {action} requires an active binding transaction. "
                "Call begin_transaction('bind') or "
                "transaction('bind') "
                "before binding or scanning."
            )

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
        pending_spells: List[Spell] = []
        with self._lock:
            if self._pending_structural_spells is not None:
                pending_spells = list(self._pending_structural_spells)
        session = self._get_required_transaction_mediator().get_session_for_identity(
            identity=self._transaction_identity,
            transaction_type="bind",
        )
        if session is None:
            return
        if not pending_spells:
            return
        binding_keys: List[Tuple[str, str]] = []
        seen_keys: Set[Tuple[str, str]] = set()
        for spell in pending_spells:
            key = spell.key
            if key in seen_keys:
                continue
            seen_keys.add(key)
            binding_keys.append(key)
        self._get_required_transaction_mediator().update_transaction_for_identity(
            identity=self._transaction_identity,
            transaction_type="bind",
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
        lookup_keys: List[Tuple[str, str]] = []
        with self._lock:
            if self._lookup_contracted_spells is not None:
                lookup_map = self._lookup_contracted_spells.get(conduit_id)
                if lookup_map:
                    lookup_keys = list(lookup_map.keys())
        session = self._get_required_transaction_mediator().get_session_for_identity(
            identity=self._transaction_identity,
            transaction_type="link",
        )
        if session is None:
            return
        existing_keys = session.staged.contract_keys
        filtered_keys = [key for key in existing_keys if key[2] != conduit_id]
        for frame_key, binding_key in lookup_keys:
            filtered_keys.append((frame_key, binding_key, conduit_id))

        self._get_required_transaction_mediator().update_transaction_for_identity(
            identity=self._transaction_identity,
            transaction_type="link",
            contract_keys=filtered_keys,
        )

    def _mark_collection_dependents_dirty(self, frame_keys: Set[str]) -> None:
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

    def _bind_under_active_transaction(
            self,
            *,
            spell: Any,
            existence: Union[str, Existence],
            permissions: str | Permissions = "create",
            spellframe: Any = None,
            binding_name: Optional[str] = None,
            disposal_method_names: Optional[Sequence[str]] = None,
            profile: str = "general",
            **kwargs: Any,
    ) -> str:
        """
        Internal

        Execute the bind pipeline assuming a bind-family transaction is active.

        Purpose:
            Keep the actual spell registration logic in one place while the
            public `bind()` method decides whether it needs to open the
            bind-family transaction window first.

        Contract:
            - Requires an active binding transaction.
            - Profiles the spell, computes its structural `spell_id`, and
              inserts the resulting `Spell` into local lookup and version caches.
            - Enforces local lookup-key uniqueness before registration.
            - Applies lifecycle hooks only after validating that the supplied
              hooks are callable.
            - When the Spellbook already has a conjured conduit, stamps conduit
              ownership/runtime metadata onto the new spell and publishes it
              into the relevant runtime mirrors.

        Returns:
            str:
                The unique SHA256 `spell_id` associated with the bound spell.
        """
        self._ensure_binding_transaction_active(action="bind")
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
                aetheric_frame=self._aetheric_frame,
                configured_disposal_method_names=self._configured_disposal_method_names,
            )

            if Spellbook._aether._check_for_spell(new_spell.spell_id, self._aetheric_frame):
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

            self._assert_lookup_key_available(
                lookup_key=new_spell._key,
                spell_index=new_spell.spell_index,
                context="bind",
                check_local=True,
                check_contracted=False,
            )

            self._add_hooks_to_spell(new_spell, **kwargs)

            # Register into local spell maps
            spell_index = new_spell.spell_index
            self._lookup_spells[new_spell._key] = spell_index
            self._spells[spell_index] = new_spell
            spell_index._attach_owner(self, new_spell)

            # keep local version cache warm
            if self._spell_versions is not None:
                versions = spell_index._versions
                if versions:
                    for vid in versions:
                        self._spell_versions.add(vid)
                else:
                    self._spell_versions.add(new_spell.spell_id)

            # If a Conduit already exists, stamp ownership metadata and runtime
            # resolution defaults for the new spell. Existing-object spells are
            # also eagerly registered into Creations.
            if self._conjured and self._conduit is not None:
                full_ahead_of_time_compilation = self._get_required_configuration().get_property(
                    "full_ahead_of_time_compilation"
                )

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
                spell_index._set_owner_conduit_id(conduit._id)
                new_spell.resolution_required = not full_ahead_of_time_compilation
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
            )
            if self._conjured and self._conduit is not None:
                self._register_spell_with_risk_manager(
                    self._get_required_conduit_surface()._id,
                    new_spell,
                )
            if self._pending_binding_frame_keys is not None:
                self._pending_binding_frame_keys.add(new_spell.key[0])
            if self._pending_structural_spells is not None:
                self._pending_structural_spells.append(new_spell)
            self._try_update_staged_binding_keys()
            if self._conjured and self._conduit is not None:
                Spellbook._aether._register_single_spell_index(
                    self._get_required_conduit_surface()._id,
                    spell_index,
                    self._aetheric_frame,
                )
                self._publish_spell_record_to_nexus(new_spell)
            return new_spell.spell_id
        except Exception as e:
            self._logger.error(f"Error while binding spell: {e}", "bind", exc_info=True)
            raise

    def bind(
            self,
            *,
            spell: Any,
            existence: Union[str, Existence],
            permissions: str | Permissions = "create",
            spellframe: Any = None,
            binding_name: Optional[str] = None,
            disposal_method_names: Optional[Sequence[str]] = None,
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
            **kwargs:
                Optional lifecycle hooks:
                - pre_hooks
                - activation_hooks
                - post_hooks

        Returns:
            str:
                The unique SHA256 `spell_id` associated with the bound spell.
        """
        self.check_cleaned()
        if self._bind_family_disabled_for_current_posture():
            self._logger.error(
                "bind denied by current frame posture",
                "bind",
            )
            raise RuntimeError(
                "[SPELLBOOK] Bind is disabled after conjure for the current frame posture."
            )
        if self._binding_transaction_is_active():
            return self._bind_under_active_transaction(
                spell=spell,
                existence=existence,
                permissions=permissions,
                spellframe=spellframe,
                binding_name=binding_name,
                disposal_method_names=disposal_method_names,
                profile=profile,
                **kwargs,
            )
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
            return self._bind_under_active_transaction(
                spell=spell,
                existence=existence,
                permissions=permissions,
                spellframe=spellframe,
                binding_name=binding_name,
                disposal_method_names=disposal_method_names,
                profile=profile,
                **kwargs,
            )

    def scan(self, module: ModuleType) -> list[str]:
        """
        Public API

        Scan a module for `scan_bind`-decorated objects and bind them.

        This is a module-only scan: it does not traverse packages or import
        submodules. Any object marked with `scan_bind` must originate from the
        scanned module, otherwise the scan fails.

        Direct spellbook-level `scan()` opens a bind-family transaction
        automatically when none is active. If a bind-family transaction is
        already active, scan reuses that window.

        Args:
            module (ModuleType): The module to scan for decorated spell targets.
        Returns:
            list[str]: Spell IDs bound during the scan, in module dict order.
        Raises:
            TypeError: If `module` is not a module or metadata is invalid.
            ValueError: If the module does not own a decorated object.
            RuntimeError: Propagated from Spellbook.bind on binding errors.
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
            aether_config: Optional[SpellbookConfiguration] = self._get_configuration_from_aether()
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
                if self._configuration._aether_frame != self._aetheric_frame:
                    self._logger.error(
                        "SpellbookConfiguration name does not match the aetheric frame",
                        "_initialize_configuration",
                        exc_info=True,
                    )
                    raise RuntimeError("SpellbookConfiguration name does not match the aetheric frame.")

                self._configuration_locked = False
                return

            # No config in Aether and none provided: create a fresh one and load defaults.
            self._configuration = SpellbookConfiguration(self._aetheric_frame)
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
            return Spellbook._aether._get_configuration(self._aetheric_frame)
        except Exception as e:
            self._logger.error(
                f"Error retrieving configuration from Aether: {e}",
                "_get_configuration_from_aether",
                exc_info=True,
            )
            raise

    def _is_frame_owned_shared_configuration(
            self,
            configuration: Optional[SpellbookConfiguration] = None,
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
                self._aetheric_frame
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
                self._aetheric_frame
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
            devops = Spellbook._aether._get_devops_manager(self._aetheric_frame)
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

        Checks whether the spellbook's configuration is currently locked (frozen) or not.

        Returns:
            bool: True if the configuration is locked, False otherwise.
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

        # If configuration is already frozen, just mark locked and return.
        if self._configuration._frozen:
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

            self._configuration.freeze()
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
                self._aetheric_frame
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
            Spellbook._aether._bind_configuration(self._configuration, self._aetheric_frame)
            shared_configuration = Spellbook._aether._get_configuration(
                self._aetheric_frame
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
            frame = Spellbook._aether._ensure_frame(self._aetheric_frame)
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
            self._aetheric_frame,
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
                self._aetheric_frame,
            )



    def get_configuration(self) -> SpellbookConfiguration:
        """
        Public API

        Returns the active configuration object for this Spellbook.

        Returns:
            SpellbookConfiguration: The active configuration instance.
        """
        return self._get_required_configuration()

    def configure_aether_frame(
            self,
            *,
            system_state: Optional[str],
            disposal: Optional[bool],
            disposal_method_names: Optional[List[str]],
            system_caching_enabled: Optional[bool] = None,
    ) -> None:
        """
        Public API

        Apply frame/runtime posture inputs, freeze configuration, and bind the
        result into Aether for this spellbook's frame.

        Contract:
            - Uses the existing spellbook configuration and frame-configuration
              objects rather than creating a parallel setup path.
            - Applies only provided values; omitted values leave the current state
              unchanged.
            - Freezes the rich spellbook configuration and then binds it to the
              owning Aether frame.

        Args:
            system_state:
                Optional frame system-state name.
            disposal:
                Optional disposal toggle for the rich spellbook configuration.
            disposal_method_names:
                Optional replacement disposal-method list.
            system_caching_enabled:
                Optional replacement system-caching-enabled toggle.
        """
        self.check_cleaned()
        frame_configuration = self._aetheric_frame_configuration
        if frame_configuration is None:
            raise RuntimeError("AethericFrameConfiguration is unavailable.")
        if system_state is not None:
            frame_configuration.with_system_state(system_state)
        if system_caching_enabled is not None:
            frame_configuration.with_system_caching_enabled(system_caching_enabled)

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

    def create_new_preset_spellbook(self) -> 'Spellbook':
        """
        Internal

        Creates a new `Spellbook` instance that shares the configuration and Aether frame of the current Spellbook.

        This is used internally when upgrading a lesser conduit's spellbook to a normal conduit spellbook.

        Returns:
            Spellbook: A new Spellbook instance ready for use by a normal conduit.
        """
        return Spellbook(self._aetheric_frame, self._configuration)


    def conjure(
            self,
            policy: Optional[str] = "default",
            dynamic: bool = False,
            name: Optional[str] = None,
            conduit_logger: Optional[Any] = None,
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
        with self._lock:
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

    def _run_structural_phases(self) -> Dict[str, Sequence[UnitOfWork]]:
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
    ) -> Dict[str, Sequence[UnitOfWork]]:
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
    ) -> Dict[str, Sequence[UnitOfWork]]:
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
    ) -> Dict[str, Sequence[UnitOfWork]]:
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







