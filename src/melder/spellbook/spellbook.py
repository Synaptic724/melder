from contextlib import contextmanager
from types import MappingProxyType, ModuleType
from typing import Optional, List, Any, Mapping, Callable, Sequence, Dict, Set, Iterable, Tuple, Collection, Generator, Union, cast, Protocol
import threading
import time
# Melder Imports
from melder.aether.aether import Aether
from melder.aether.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeControlTransactionRequest,
    ChangeTransactionType,
)
from melder.spellbook.bind.spell_index import SpellIndex
from melder.spellbook.bind.scan import Scan
from melder.spellbook.spellbook_creation_system import SpellbookCreationSystem
from melder.spellbook.configuration.system_state import SystemState
from melder.spellbook.spell_crafter.validation.validation_system import SpellValidationSystem
from melder.spellbook.spellbinder import SpellBinder
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.interfaces import (
    IConduit,
    ISpell,
    IConfiguration,
    ISpellIndex,
    ISpellBinder,
    ISpellSystemStates,
    ISpellValidationSystem,
    ISpellbook,
    IUnitOfWork,
    ISafeLogger,
    IChangeControlManager,
)
from melder.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.spellbook.bind.bind import Bind
from melder.spellbook.existence.existence import Existence
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.utilities.helpers.general_helpers import EnumHelpers
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.utilities.helpers.init_helpers import InitHelpers
from melder.utilities.helpers.general_helpers import SpellInputUtils
from melder.utilities.synchronization.phase_scheduler import PhaseScheduler
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.nexus.nexus import Nexus

class _SpellbookSpellIndexSurface(ISpellIndex, Protocol):
    """
    Narrow concrete SpellIndex surface used by Spellbook internals.
    """

    _versions: Optional[Set[str]]

    def _attach_owner(self, spellbook: Any, spell: ISpell) -> None:
        ...

    def _attach_contracted(
            self,
            spellbook: Any,
            conduit_id: str,
            spell: ISpell,
    ) -> None:
        ...

    def _detach_contracted(self, spellbook: Any, conduit_id: str) -> None:
        ...

    def _set_owner_conduit_id(self, conduit_id: str) -> None:
        ...


class _SpellbookConduitSurface(IConduit, Protocol):
    """
    Narrow conduit surface used by Spellbook runtime wiring.
    """

    _id: str
    _name: Optional[str]
    _creations: Any
    _creation_gate_controller: Any
    _nexus_publish_enabled: bool
    __dynamic_environment__: bool

    def _register_to_creations(self, spell: ISpell, instance: Any) -> None:
        ...


class _SpellbookChangeControlSurface(IChangeControlManager, Protocol):
    """
    Narrow change-control surface used by Spellbook transactions.
    """

    def transaction_manager(self) -> Any:
        ...

    def orchestrator(self) -> Any:
        ...

#region Spellbook
class Spellbook(Cleanable, ISpellbook):
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
    - Use the default frame only when shared scope is intentional.

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
        - Local registries, contracted registries, validators, configuration,
          and logging are owned by this object.
        - Cleanup is staged so component teardown happens under the lock first
          and high-level references are dropped afterward.

    Notes:
        - SpellbookConfiguration is locked automatically once the spellbook crosses into
          the conjured runtime path.
        - Frame-wide rich Spellbook configuration reuse is explicit and only
          occurs when the frame posture permits it and a shared rich config
          object already exists on the frame.
    """
    __melder_internal__ = _mrg.sentinel
    _cleaned: bool
    __slots__ = Cleanable.__slots__ + [
        "_active_change_request",
        "_aetheric_frame",
        "_aetheric_frame_configuration",
        "_bind",
        "_binding_transaction_active",
        "_block_all_spells",
        "_conduit",
        "_configuration",
        "_configuration_locked",
        "_conjured",
        "_contracted_spells",
        "_contracted_spells_by_id",
        "_contracted_versions",
        "_id",
        "_lock",
        "_logger",
        "_lookup_contracted_spells",
        "_nexus_publish_enabled",
        "_lookup_spells",
        "_pending_binding_frame_keys",
        "_pending_structural_spells",
        "_spell_id_pool",
        "_spell_system_states",
        "_spell_validator",
        "_spell_versions",
        "_spellbook_validation_required",
        "_spells",
        "_spells_by_id",
        "_whitelist_all_spells",
    ]
    _aether = Aether()
    def __init__(self, aetheric_frame: str = "default", configuration: Optional[IConfiguration] = None,
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
            configuration (Optional[IConfiguration]):
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
        self._binding_transaction_active: bool = True
        self._active_change_request: Optional[ChangeControlTransactionRequest] = None
        self._pending_binding_frame_keys: Set[str] = set()
        self._pending_structural_spells: List[ISpell] = []
        self._conduit: Optional[_SpellbookConduitSurface] = None
        self._nexus_publish_enabled: bool = False
        self._aetheric_frame: str = aetheric_frame
        if not isinstance(self._aetheric_frame, str):
            raise TypeError(f"aetheric_frame must be a string, got {type(self._aetheric_frame).__name__}")
        Spellbook._aether._ensure_frame(self._aetheric_frame)

        # SpellbookConfiguration state
        self._configuration_locked: bool = False
        self._configuration: Optional[IConfiguration] = configuration
        self._aetheric_frame_configuration: Optional[Any] = None
        # Temporary logger for configuration init; will be replaced in _initialize_logging.
        self._logger: ISafeLogger = InitHelpers.resolve_safe_logger(None)
        self._initialize_aetheric_frame_configuration()
        self._initialize_configuration()

        # Logger setup
        self._initialize_logging(logger)

        # Core spell storage (SpellIndex Maps)
        self._spells: Dict[ISpellIndex, ISpell] = {}
        self._spell_versions: Set[str] = set()
        self._lookup_spells: Dict[tuple, ISpellIndex]  = {}
        self._spells_by_id: Dict[str, ISpell] = {}
        self._spell_id_pool: Dict[str, ISpell] = {}

        # Networked/remote spell support
        # This stores spells borrowed from other conduits (keyed by peer Conduit id)
        self._contracted_spells: Dict[str, Dict[ISpellIndex, ISpell]] = {}
        self._contracted_versions: Dict[str, Set[str]] = {}
        self._lookup_contracted_spells: Dict[str, Dict[tuple, ISpellIndex]]  = {}
        self._contracted_spells_by_id: Dict[str, Dict[str, ISpell]] = {}

        # Spell validator
        self._spell_validator: ISpellValidationSystem = SpellValidationSystem()
        # Spell States System
        self._spell_system_states: ISpellSystemStates = Spellbook._aether._get_spell_system_states(aetheric_frame)
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

        Cleanup owned registries and component references under the Spellbook lock.

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

        try:
            self._spell_validator.cleanup()
        except Exception as e:
            self._logger.error(f"Error cleaning spell validator: {e}", "_cleanup_components", exc_info=True)
        del self._spell_validator


    def _cleanup_spells(self) -> None:
        """
        Internal

        Cleanup local spell objects and unregister their spell indexes.

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
        del self._binding_transaction_active
        del self._active_change_request
        del self._pending_binding_frame_keys
        del self._pending_structural_spells
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
    def __enter__(self):
        """
        Enter the Spellbook lock context and return `self`.

        Purpose:
            Allow internal multi-step operations to hold the Spellbook lock
            across a controlled block without exposing `_lock` directly.

        Returns:
            Spellbook:
                This Spellbook instance while the lock is held.
        """
        self.check_cleaned()
        self._lock.acquire()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
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
              version IDs (SHA256) for that conduitâ€™s spells.
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

    @staticmethod
    def _get_required_spell_index_surface(
            spell_index: ISpellIndex,
    ) -> _SpellbookSpellIndexSurface:
        """
        Return the concrete internal SpellIndex surface used by Spellbook.
        """
        return cast(_SpellbookSpellIndexSurface, spell_index)

    def _get_required_conduit_surface(self) -> _SpellbookConduitSurface:
        """
        Return the live conjured conduit surface or raise.
        """
        conduit = self._conduit
        if conduit is None:
            raise RuntimeError("Spellbook requires a live conjured conduit.")
        return conduit

    def _get_required_change_control_manager(
            self,
    ) -> _SpellbookChangeControlSurface:
        """
        Return the frame-local change-control manager surface used internally.
        """
        manager = self._aether._get_change_control_manager(self._aetheric_frame)
        return cast(_SpellbookChangeControlSurface, manager)

    def _get_required_configuration(self) -> IConfiguration:
        """
        Return the live spellbook configuration or raise.
        """
        configuration = self._configuration
        if configuration is None:
            raise RuntimeError("Spellbook configuration is unavailable.")
        return configuration

    def _register_owned_spell_id(self, spell_id: str, spell: ISpell) -> None:
        """
        Internal

        Register the current spell_id mapping for an owned spell.

        Purpose:
            Provide O(1) lookup by current version id for owned spells.

        Contract:
            - Only the current version id is stored in the map.
            - Raises if the id is mapped to a different spell.

        Args:
            spell_id (str): Current version id for the spell.
            spell (ISpell): Owned spell instance.

        Raises:
            RuntimeError: If the Spellbook is cleaned or the map is missing.
            RuntimeError: If the id already maps to a different spell.

        Threading:
            - Acquires the Spellbook lock.
        """
        self.check_cleaned()
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

    def _update_owned_spell_id(self, old_id: str, new_id: str, spell: ISpell) -> None:
        """
        Internal

        Update the owned spell_id map entry after a SpellIndex version change.

        Contract:
            - Removes the old id mapping and registers the new id mapping.
            - Adds the new id to the local version cache.

        Args:
            old_id (str): Previous version id for the spell index.
            new_id (str): New version id for the spell index.
            spell (ISpell): Owned spell instance.

        Raises:
            RuntimeError: If the map is missing or does not contain the old id.
            RuntimeError: If the new id collides with another spell.

        Threading:
            - Acquires the Spellbook lock.
        """
        self.check_cleaned()
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

    def _unregister_owned_spell_id(self, spell_id: str, spell: ISpell) -> None:
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
            spell (ISpell): Owned spell instance being removed.
        Raises:
            RuntimeError: If the owned id map is missing.
            RuntimeError: If the spell_id maps to a different spell.
        Threading:
            - Acquires the Spellbook lock.
        """
        self.check_cleaned()
        with self._lock:
            if self._spells_by_id is None:
                self._logger.error(
                    "Owned spell_id map is not available.",
                    "_unregister_owned_spell_id",
                )
                raise RuntimeError("Owned spell_id map is not available.")
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
        if self._nexus_publish_enabled:
            self._nexus._remove_spell_record(
                self._id,
                spell_id,
                self._aetheric_frame,
            )

    def _register_contracted_spell_id(self, conduit_id: str, spell_id: str, spell: ISpell) -> None:
        """
        Internal

        Register the current spell_id mapping for a contracted spell.

        Purpose:
            Provide O(1) lookup by current version id for contracted spells.

        Contract:
            - Mapping is stored under the given conduit_id.
            - Raises if the id is mapped to a different spell.

        Args:
            conduit_id (str): Peer conduit id that owns the contract.
            spell_id (str): Current version id for the spell.
            spell (ISpell): Contracted spell instance.

        Raises:
            RuntimeError: If the contracted map is missing.
            RuntimeError: If the id already maps to a different spell.

        Threading:
            - Acquires the Spellbook lock.
        """
        self.check_cleaned()
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
            spell: ISpell,
    ) -> None:
        """
        Internal

        Update the contracted spell_id map entry after a SpellIndex version change.

        Contract:
            - Removes the old id mapping and registers the new id mapping.
            - Adds the new id to the per-conduit version cache.

        Args:
            conduit_id (str): Peer conduit id that owns the contract.
            old_id (str): Previous version id for the spell index.
            new_id (str): New version id for the spell index.
            spell (ISpell): Contracted spell instance.

        Raises:
            RuntimeError: If the map is missing or does not contain the old id.
            RuntimeError: If the new id collides with another spell.

        Threading:
            - Acquires the Spellbook lock.
        """
        self.check_cleaned()
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

    def _unregister_contracted_spell_id(self, conduit_id: str, spell_id: str, spell: ISpell) -> None:
        """
        Internal

        Remove a contracted spell_id mapping for the given conduit.

        Args:
            conduit_id (str): Peer conduit id that owns the contract.
            spell_id (str): Current version id for the spell.
            spell (ISpell): Contracted spell instance.

        Raises:
            RuntimeError: If the map is missing or does not contain the id.

        Threading:
            - Acquires the Spellbook lock.
        """
        self.check_cleaned()
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
    def spells(self) -> Mapping[ISpellIndex, ISpell]:
        """
        Public API

        Return a read-only view of the local spells registered in this
        Spellbook.

        Contract:
            - Exposes a `MappingProxyType` wrapper over the local spell map.
            - Supports safe introspection without allowing direct registry
              mutation.

        Returns:
            Mapping[ISpellIndex, ISpell]:
                Immutable map of local `SpellIndex` keys to spell
                objects.
        """
        self.check_cleaned()
        return cast(Mapping[ISpellIndex, ISpell], MappingProxyType(self._spells))

    @property
    def contracted_spells(self) -> Mapping[str, Mapping[ISpellIndex, ISpell]]:
        """
        Public API

        Return a per-conduit read-only view of all borrowed spells.

        Contract:
            - Outer keys are peer conduit identifiers.
            - Each value is an immutable spell map for that peer conduit.

        Returns:
            Mapping[str, Mapping[ISpellIndex, ISpell]]:
                Immutable map of peer conduit id to immutable borrowed-spell
                map.
        """
        self.check_cleaned()
        return cast(
            Mapping[str, Mapping[ISpellIndex, ISpell]],
            MappingProxyType({
                conduit_id: MappingProxyType(dict(spells))
                for conduit_id, spells in self._contracted_spells.items()
            }),
        )

    def snapshot_state(self) -> Dict[str, Any]:
        """
        Public API

        Build a read-only snapshot of Spellbook state.

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

            contracted_spells: Dict[str, Dict[ISpellIndex, ISpell]] = {}
            if self._contracted_spells is not None:
                for conduit_id, spells in self._contracted_spells.items():
                    contracted_spells[conduit_id] = dict(spells)

            lookup_contracted_spells: Dict[str, Dict[Tuple[str, str], ISpellIndex]] = {}
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
    def find_spell_by_id(self, spell_id: str) -> Optional[ISpell]:
        """
        Finds a spell by its unique identifier within the spellbook.

        Args:
            spell_id: The identifier of the spell to find.

        Returns:
            Optional[ISpell]: The spell if found, otherwise None.
        """
        self.check_cleaned()
        for spell_index, spell in self._spells.items():
            # SpellIndex is responsible for telling us whether it owns this version
            if spell_index.has_version(spell_id):
                return spell

        return None

    def get_spell_permissions(self, spell_index: ISpellIndex) -> Optional[str]:
        """
        Public API

        Retrieves the access permissions for a **locally** registered spell.

        Args:
            spell_index:
                The SpellIndex of the spell.

        Returns:
            Optional[str]:
                The permissions name (``"read"``, ``"create"``, or
                ``"block"``) for this spell.

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

    def _find_spell(self, spell_index: ISpellIndex) -> Optional[ISpell]:
        """
        Internal

        Locates a **local** spell by its `SpellIndex`.

        Args:
            spell_index:
                The SpellIndex of the spell to find.

        Returns:
            Optional[ISpell]:
                The spell object if found, else `None`.
        """
        with self._lock:
            spell = self._spells.get(spell_index, None)
        return spell

    def _find_contracted_spell(self, spell_index: ISpellIndex) -> Optional[ISpell]:
        """
        Internal

        Locates a contracted spell by its unique ID by searching across all peer contracts.

        Args:
            spell_index (SpellIndex): The ID of the contracted spell to find.

        Returns:
            Optional[ISpell]: The spell object if found.

        Raises:
            RuntimeError: If the contracted spell with the given ID is not found.
        """
        self.check_cleaned()
        with self._lock:
            for contracted_spells in self._contracted_spells.values():
                if spell_index in contracted_spells:
                    return contracted_spells[spell_index]
            self._logger.error(f"Contracted spell with ID {spell_index} not found.", "_find_contracted_spell", exc_info=True)
        raise RuntimeError(f"Contracted spell with ID {spell_index} not found in the spellbook.")

    def _find_spell_index_by_index_id(
            self,
            spell_index_id: str,
    ) -> Optional[ISpellIndex]:
        """
        Internal

        Locate a **local** SpellIndex by its stable index id.

        Args:
            spell_index_id:
                Stable SpellIndex id (ULID) to resolve.

        Returns:
            Optional[ISpellIndex]:
                Matching local SpellIndex when found, else ``None``.
        """
        self.check_cleaned()
        with self._lock:
            for spell_index in self._spells.keys():
                if spell_index.id == spell_index_id:
                    return spell_index
        return None

    def _find_contracted_spell_index_by_index_id(
            self,
            spell_index_id: str,
    ) -> Optional[ISpellIndex]:
        """
        Internal

        Locate a contracted SpellIndex by its stable index id.

        Args:
            spell_index_id:
                Stable SpellIndex id (ULID) to resolve.

        Returns:
            Optional[ISpellIndex]:
                Matching contracted SpellIndex when found, else ``None``.
        """
        self.check_cleaned()
        with self._lock:
            for contracted_spells in self._contracted_spells.values():
                for spell_index in contracted_spells.keys():
                    if spell_index.id == spell_index_id:
                        return spell_index
        return None

    def get_spell_by_index_id(
            self,
            spell_index_id: str,
    ) -> Optional[ISpell]:
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
            - Returns ``None`` when no matching SpellIndex exists.

        Args:
            spell_index_id:
                Stable SpellIndex id (ULID) to resolve.

        Returns:
            Optional[ISpell]:
                Matching local or contracted spell when found, else ``None``.
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


    def find_spell_index(self, spellframe: str, spell_name: str, binding_name: str) -> Optional[ISpellIndex]:
        """
        Public API

        Finds a spell's SpellIndex using its logical identifiers.

        The search checks local spells first, then contracted spells.

        Args:
            spellframe (str): The logical namespace or grouping label.
            spell_name (str): The name of the spell class or function.
            binding_name (str): The secondary key to distinguish the spell.

        Returns:
            Optional[ISpellIndex]: The SpellIndex associated with this spell.

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
            spell_index: ISpellIndex,
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
        self.check_cleaned()

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


    def inspect_spell(self, spell: Any, aetheric_frame= "default") -> Optional[str]:
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
            - Raises on the first duplicate detected in the Aether registry.

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
    def _find_contracted_spell_by_id(self, spell_id: str, conduit_id: str) -> Optional[ISpell]:
        """
        Internal

        Resolves a contracted spell by its SHA256 version id using the Spellbook's
        local copies of contracted spells. Each contracted spell's SpellIndex
        contains all known versions, so we can resolve purely from Spellbook data.

        Args:
            spell_id (str): The version SHA of the spell.
            conduit_id (str): The contracting peer conduit ID.

        Returns:
            Optional[ISpell]: The resolved spell, or None if not found.
        """

        # Pull the map of SpellIndex ? ISpell for this conduit
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
        atomically to maintain consistent state.

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
        self._register_link_mirror(conduit_id)


    def _remove_link_contract(self, conduit_id: str):
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


    def _add_contracted_spell(self, spell: ISpell, conduit_id: str) -> None:
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
            spell (ISpell): The spell object to add.
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

            spell_index = self._get_required_spell_index_surface(
                spell.spell_index
            )
            spell_index._attach_contracted(self, conduit_id, spell)

            # Main maps: SpellIndex ? ISpell and key ? SpellIndex
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

        The SpellIndex attachment is removed so this Spellbook no longer
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

            spell_index_surface = self._get_required_spell_index_surface(
                spell_index
            )
            spell_index_surface._detach_contracted(self, conduit_id)

            # Remove from main map
            spell_map.pop(spell_index, None)

            # Remove from lookup map
            key = self._make_spell_key(spell.spellframe, spell.spell_name, spell.binding_name)
            lookup_map.pop(key, None)

            # Remove *all* versions for this SpellIndex from the version cache
            versions = spell_index_surface._versions
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

        SpellIndex attachments are removed so this Spellbook no longer
        receives spell_id updates for the contracted spell index.

        When a link transaction is active, this also refreshes staged contract
        keys for the peer conduit so change-control commit hooks can observe
        the updated contract scope.

        Args:
            conduit_id (str): The ID of the peer conduit whose contracted spells are to be cleared
        """

        removed_spells: List[ISpell] = []
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
                spell_index_surface = self._get_required_spell_index_surface(
                    spell.spell_index
                )
                spell_index_surface._detach_contracted(self, conduit_id)

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
        self._unregister_link_mirror(conduit_id)

    def _register_link_mirror(self, conduit_id: str) -> None:
        """
        Internal

        Register a link-mirror entry for this Spellbook's conduit.

        Purpose:
            Record a borrower->provider relationship for change-control checks.
        Contract:
            - No-op when the Spellbook has no conjured conduit.
            - Delegates to the ChangeControlTransactionManager registry.
        Args:
            conduit_id:
                Provider conduit id associated with the link.
        Returns:
            None.
        Raises:
            RuntimeError: If the Spellbook has been cleaned.
        """
        self.check_cleaned()
        if not conduit_id:
            return
        change_control = self._get_required_change_control_manager()
        transaction_manager = change_control.transaction_manager()
        transaction_manager.register_link(
            borrower_conduit_id=self._get_required_conduit_surface()._id,
            provider_conduit_id=conduit_id,
        )

    def _unregister_link_mirror(self, conduit_id: str) -> None:
        """
        Internal

        Remove a link-mirror entry for this Spellbook's conduit.

        Purpose:
            Remove borrower->provider tracking when a link is severed.
        Contract:
            - No-op when the Spellbook has no conjured conduit.
            - Delegates to the ChangeControlTransactionManager registry.
        Args:
            conduit_id:
                Provider conduit id associated with the link.
        Returns:
            None.
        Raises:
            RuntimeError: If the Spellbook has been cleaned.
        """
        self.check_cleaned()
        if not conduit_id:
            return
        change_control = self._get_required_change_control_manager()
        transaction_manager = change_control.transaction_manager()
        transaction_manager.unregister_link(
            borrower_conduit_id=self._get_required_conduit_surface()._id,
            provider_conduit_id=conduit_id,
        )



    #endregion Contract API
    #region Binding API

    def create_binder(
            self,
            *,
            default_existence: Existence = Existence.unique,
            default_permissions: str = "create",
    ) -> ISpellBinder:
        """
        Public API

        Creates an `ISpellBinder` surface backed by `SpellBinder` and providing
        an Autofac-style
        fluent syntax on top of `Spellbook.bind(...)`.

        This does *not* introduce a new registration path; it simply
        forwards everything into the existing binding pipeline so all
        reflection, `SpellIndex` construction, `SpellType` classification,
        and validation flows remain exactly the same. :contentReference[oaicite:1]{index=1}

        Example:
            binder = spellbook.create_binder()

            binder.bind(MyService) \\
                  .as_unique() \\
                  .under_spellframe(IMyServiceProtocol) \\
                  .named("primary") \\
                  .with_permissions("create") \\
                  .finalize()

            # Reuse the same binder for another spell:
            binder.bind(OtherService, existence=Existence.many).finalize()

        Args:
            default_existence (Existence):
                Default lifecycle scope for fluent registrations started via
                this binder.

            default_permissions (str):
                Default permissions for fluent registrations (e.g. "create").

        Returns:
            ISpellBinder:
                A reusable fluent registration helper bound to this Spellbook.
        """
        self.check_cleaned()
        return SpellBinder(
            spellbook=self,
            default_existence=default_existence,
            default_permissions=default_permissions,
        )

    def _normalize_change_transaction_type(
            self,
            value: ChangeTransactionType | str,
    ) -> ChangeTransactionType:
        """
        Internal

        Normalize a transaction type input to ChangeTransactionType.

        Purpose:
            Convert string inputs into the canonical ChangeTransactionType enum.
        Contract:
            - Accepts ChangeTransactionType values or their string values.
            - Comparison is case-insensitive for string inputs.
        Args:
            value:
                Transaction type as an enum or string.
        Returns:
            ChangeTransactionType:
                Normalized transaction type.
        Raises:
            ValueError: If the value is empty or not a valid transaction type.
            TypeError: If the value is not a string or ChangeTransactionType.
        """
        if isinstance(value, ChangeTransactionType):
            return value
        if isinstance(value, str):
            candidate = value.strip().lower()
            if not candidate:
                raise ValueError("transaction_type cannot be empty.")
            try:
                return ChangeTransactionType(candidate)
            except ValueError as exc:
                valid = [item.value for item in ChangeTransactionType]
                raise ValueError(
                    f"Invalid transaction_type '{value}'. Expected one of: {valid}."
                ) from exc
        raise TypeError(
            "transaction_type must be a ChangeTransactionType or string."
        )

    def begin_transaction(
            self,
            transaction_type: ChangeTransactionType | str,
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
            Admit a mutation request through the ChangeControlManager and,
            for bind transactions, open the binding transaction window.
        Contract:
            - Only one change-control transaction may be active per Spellbook.
            - Admission is serialized by the ChangeControlOrchestrator.
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
                Optional binding keys affected by the request.
            contract_keys:
                Optional contract keys affected by the request.
            metadata:
                Optional structured metadata for diagnostics.
        Returns:
            None.
        Raises:
            RuntimeError: If a change transaction is already active.
            RuntimeError: If binding transaction is already active for bind requests.
            RuntimeError: If change-control admission is denied.
            ValueError: If transaction_type is invalid.
            TypeError: If transaction_type has an invalid type.
        Threading:
            Admission uses the orchestrator lock; local state uses the Spellbook lock.
        """
        self.check_cleaned()
        request_type = self._normalize_change_transaction_type(transaction_type)
        dynamic_only = {
            ChangeTransactionType.LINK,
            ChangeTransactionType.TRANSFER_OWNERSHIP,
            ChangeTransactionType.MUTATION,
            ChangeTransactionType.CLUSTER_LINK,
        }
        if request_type in dynamic_only:
            system_state = None
            if self._aetheric_frame_configuration is not None:
                system_state = self._aetheric_frame_configuration.system_state
            if system_state is None:
                self._logger.error(
                    "Change transaction requires dynamic mode with missing system_state",
                    "begin_transaction",
                )
                raise RuntimeError(
                    "[SPELLBOOK] Change transactions require dynamic mode, but system_state is unavailable."
                )
            state_enum = EnumHelpers.convert_enum_and_check(system_state, SystemState)
            if state_enum is not SystemState.dynamic:
                self._logger.error(
                    "Change transaction denied in automatic mode",
                    "begin_transaction",
                )
                raise RuntimeError(
                    "[SPELLBOOK] Change transactions require dynamic mode. "
                    f"transaction_type='{request_type.value}'."
                )

        with self._lock:
            if self._active_change_request is not None:
                self._logger.error(
                    "Change transaction already active",
                    "begin_transaction",
                )
                raise RuntimeError(
                    "[SPELLBOOK] Change transaction already active. "
                    "End the current transaction before starting another."
                )
            if request_type is ChangeTransactionType.BIND and self._binding_transaction_active:
                self._logger.error(
                    "Binding transaction already active",
                    "begin_transaction",
                )
                raise RuntimeError(
                    "[SPELLBOOK] Binding transaction already active. "
                    "End the current transaction before starting another."
                )

        initiator = conduit_id
        if not initiator and self._conduit is not None:
            initiator = self._conduit._id
        if not initiator:
            initiator = f"spellbook:{self._id}"

        change_control = self._get_required_change_control_manager()
        transaction_manager = change_control.transaction_manager()

        scope_values = list(scope_keys) if scope_keys else []
        base_scope = transaction_manager.make_scope_key_spellbook(self._id)
        if base_scope not in scope_values:
            scope_values.append(base_scope)

        conduit_values = list(conduit_ids) if conduit_ids else []
        if initiator and initiator not in conduit_values and not initiator.startswith("spellbook:"):
            conduit_values.append(initiator)

        request = transaction_manager.build_request(
            request_type=request_type,
            initiator_conduit_id=initiator,
            spellbook_id=self._id,
            conduit_ids=conduit_values,
            scope_keys=scope_values,
            scope_hashes=scope_hashes,
            binding_keys=binding_keys,
            contract_keys=contract_keys,
            metadata=metadata,
        )
        admission = change_control.admit_request(request)

        if not admission.admitted:
            details = []
            if admission.conflicts:
                details.append(f"conflicts={admission.conflicts}")
            if admission.embargoes:
                details.append(f"embargoes={admission.embargoes}")
            detail_msg = "; ".join(details) if details else "no conflict metadata available"
            raise RuntimeError(
                "[SPELLBOOK] Change-control admission denied "
                f"(reasons={admission.reasons}). {detail_msg}"
            )

        try:
            with self._lock:
                if self._active_change_request is not None:
                    raise RuntimeError(
                        "[SPELLBOOK] Change transaction already active. "
                        "End the current transaction before starting another."
                    )
                if request_type is ChangeTransactionType.BIND and self._binding_transaction_active:
                    raise RuntimeError(
                        "[SPELLBOOK] Binding transaction already active. "
                        "End the current transaction before starting another."
                    )
                if request_type is ChangeTransactionType.BIND:
                    self._begin_binding_transaction(owner_label="Spellbook")
                self._active_change_request = request
        except Exception:
            change_control.abort_request(request.request_id)
            raise

    def end_transaction(
            self,
            transaction_type: ChangeTransactionType | str | None = None,
    ) -> None:
        """
        Public API

        End the active change-control transaction for this Spellbook.

        Purpose:
            Finalize an admitted change-control request and release any
            implicit embargo state tracked by the ChangeControlManager.
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
            Uses the Spellbook lock for local state; orchestrator handles admission state.
        """
        self.check_cleaned()
        request: Optional[ChangeControlTransactionRequest] = None
        expected_type: Optional[ChangeTransactionType] = None
        with self._lock:
            request = self._active_change_request
        if request is None:
            raise RuntimeError("[SPELLBOOK] No active change transaction to end.")

        if transaction_type is not None:
            expected_type = self._normalize_change_transaction_type(transaction_type)
            if request.request_type is not expected_type:
                raise RuntimeError(
                    "[SPELLBOOK] Active change transaction does not match the requested type."
                )

        change_control = self._aether._get_change_control_manager(self._aetheric_frame)
        try:
            if request.request_type is ChangeTransactionType.BIND:
                self._end_binding_transaction(owner_label="Spellbook")
        except Exception:
            change_control.abort_request(request.request_id)
            with self._lock:
                self._active_change_request = None
            raise

        change_control.commit_request(request.request_id)
        with self._lock:
            self._active_change_request = None

    @contextmanager
    def transaction(
            self,
            transaction_type: ChangeTransactionType | str,
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
                Optional binding keys affected by the request.
            contract_keys:
                Optional contract keys affected by the request.
            metadata:
                Optional structured metadata for diagnostics.
        Yields:
            Spellbook: The current Spellbook instance for the duration of the transaction context.
        Raises:
            RuntimeError: If a change transaction is already active.
            RuntimeError: If binding transaction is already active for bind requests.
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
        finally:
            self.end_transaction(transaction_type)

    def begin_binding_transaction(self) -> None:
        """
        Public API

        Begin a binding transaction for this Spellbook.

        Purpose:
            Enable binding operations (bind/scan) in a controlled transaction window.
        Contract:
            - Only one binding transaction may be active at a time.
            - While active, `bind(...)` and `scan(...)` are allowed.
            - When inactive, `bind(...)` and `scan(...)` raise.
        Returns:
            None.
        Raises:
            RuntimeError: If a binding transaction is already active.
        """
        self.begin_transaction(ChangeTransactionType.BIND)

    def end_binding_transaction(self) -> None:
        """
        Public API

        End the active binding transaction for this Spellbook.

        Purpose:
            Disable binding operations until a new transaction is started.
        Contract:
            - Binding transactions must be explicitly closed.
            - When inactive, `bind(...)` and `scan(...)` raise.
            - If the Spellbook has conjured a Conduit, ending a transaction
              gates list[Frame] consumers and runs structural phases for new spells.
        Returns:
            None.
        Raises:
            RuntimeError: If no binding transaction is active.
        """
        self.check_cleaned()
        with self._lock:
            active_request = self._active_change_request
        if active_request is not None:
            if active_request.request_type is not ChangeTransactionType.BIND:
                raise RuntimeError(
                    "[SPELLBOOK] Active change transaction is not a bind transaction."
                )
            self.end_transaction(ChangeTransactionType.BIND)
            return
        self._end_binding_transaction(owner_label="Spellbook")

    @contextmanager
    def binding_transaction(self) -> Generator["Spellbook", None, None]:
        """
        Public API

        Context-managed binding transaction for this Spellbook.

        Usage:
            with spellbook.binding_transaction():
                spellbook.bind(...)
                spellbook.scan(...)

        Contract:
            - Starts a binding transaction on entry.
            - Ends the transaction on exit, even if an exception is raised.
            - Nested usage raises on begin (transaction already active).
            - If the Spellbook has conjured a Conduit, exit gates list[Frame]
              consumers and runs structural phases for new spells.

        Yields:
            Spellbook: The current Spellbook instance for the duration of the binding context.
        Raises:
            RuntimeError: If a binding transaction is already active.
        """
        self.begin_binding_transaction()
        try:
            yield self
        finally:
            self.end_binding_transaction()

    def _begin_binding_transaction(self, *, owner_label: str) -> None:
        """
        Internal

        Begin a binding transaction with a caller-specific error message.

        Args:
            owner_label: Label used to tailor error messages (Spellbook or Conduit).
        Returns:
            None.
        Raises:
            RuntimeError: If a binding transaction is already active.
        """
        with self._lock:
            if self._binding_transaction_active:
                if self._logger is not None:
                    self._logger.error(
                        f"{owner_label} binding transaction already active",
                        "begin_binding_transaction",
                    )
                raise RuntimeError(
                    f"[{owner_label.upper()}] Binding transaction already active. "
                    "End the current transaction before starting another."
                )
            self._binding_transaction_active = True
            if self._pending_binding_frame_keys is None:
                self._pending_binding_frame_keys = set()
            else:
                self._pending_binding_frame_keys.clear()
            if self._pending_structural_spells is None:
                self._pending_structural_spells = []
            else:
                self._pending_structural_spells.clear()

    def _end_binding_transaction(self, *, owner_label: str) -> None:
        """
        Internal

        End a binding transaction with a caller-specific error message.

        When the Spellbook has already conjured a Conduit, this method also
        gates list[Frame] consumers for targeted revalidation.

        Args:
            owner_label: Label used to tailor error messages (Spellbook or Conduit).
        Returns:
            None.
        Raises:
            RuntimeError: If no binding transaction is active.
        """
        pending_frame_keys: Set[str] = set()
        pending_spells: List[ISpell] = []
        conjured = False
        with self._lock:
            if not self._binding_transaction_active:
                self._logger.error(
                    f"{owner_label} binding transaction is not active",
                    "end_binding_transaction",
                )
                raise RuntimeError(
                    f"[{owner_label.upper()}] Binding transaction is not active. "
                    "Start a transaction before ending it."
                )
            self._binding_transaction_active = False
            if self._pending_binding_frame_keys is not None:
                pending_frame_keys = set(self._pending_binding_frame_keys)
                self._pending_binding_frame_keys.clear()
            if self._pending_structural_spells is not None:
                pending_spells = list(self._pending_structural_spells)
                self._pending_structural_spells.clear()
            conjured = bool(self._conjured)

        if conjured and pending_frame_keys:
            self._mark_collection_dependents_dirty(pending_frame_keys)
        if conjured and pending_spells:
            self._run_post_conjure_structural_phases(pending_spells)

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
        with self._lock:
            if not self._binding_transaction_active:
                self._logger.error(
                    f"{action} requires an active binding transaction",
                    action,
                )
                raise RuntimeError(
                    f"[SPELLBOOK] {action} requires an active binding transaction. "
                    "Call begin_transaction('bind') or begin_binding_transaction() "
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
            - No-op if no change transaction is active or it is not a bind request.
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
        self.check_cleaned()
        request: Optional[ChangeControlTransactionRequest] = None
        pending_spells: List[ISpell] = []
        with self._lock:
            request = self._active_change_request
            if self._pending_structural_spells is not None:
                pending_spells = list(self._pending_structural_spells)
        if request is None:
            return
        if request.request_type is not ChangeTransactionType.BIND:
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
        change_control = self._aether._get_change_control_manager(self._aetheric_frame)
        change_control.update_staged_request(
            request.request_id,
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
            - No-op if no change transaction is active or it is not a link request.
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
            Captures current contracted lookup keys under the Spellbook lock;
            change-control updates run without holding the Spellbook lock.
        """
        self.check_cleaned()
        if not conduit_id:
            return
        request: Optional[ChangeControlTransactionRequest] = None
        lookup_keys: List[Tuple[str, str]] = []
        with self._lock:
            request = self._active_change_request
            if self._lookup_contracted_spells is not None:
                lookup_map = self._lookup_contracted_spells.get(conduit_id)
                if lookup_map:
                    lookup_keys = list(lookup_map.keys())
        if request is None:
            return
        if request.request_type is not ChangeTransactionType.LINK:
            return

        change_control = self._get_required_change_control_manager()
        staged = change_control.orchestrator().get_staged(request.request_id)
        existing_keys = staged.contract_keys if staged is not None else request.contract_keys
        filtered_keys = [key for key in existing_keys if key[2] != conduit_id]
        for frame_key, binding_key in lookup_keys:
            filtered_keys.append((frame_key, binding_key, conduit_id))

        change_control.update_staged_request(
            request.request_id,
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

    def bind(
            self,
            *,
            spell,
            existence: Union[str, Existence],
            permissions: str = "create",
            spellframe: Any = None,
            binding_name: Optional[str] = None,
            profile: str = "general",
            **kwargs,
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
            - Requires an active binding transaction.
            - Profiles the spell, computes its structural `spell_id`, and
              inserts the resulting `Spell` into local lookup and version caches.
            - Enforces local lookup-key uniqueness before registration.
            - Applies lifecycle hooks only after validating that the supplied
              hooks are callable.
            - When the Spellbook already has a conjured conduit, stamps conduit
              ownership/runtime metadata onto the new spell and publishes it
              into the relevant runtime mirrors.

        Binding requires an active binding transaction. Use
        ``begin_transaction("bind")`` (or ``begin_binding_transaction()``)
        before binding and ``end_binding_transaction()`` once registration
        is complete.

        When a change-control bind transaction is active, binding updates the
        staged request metadata with the normalized binding keys for the spells
        registered in that transaction.

        Permissions:
            - `"read"` allows other conduits to consume the spell but not create
              new instances from it.
            - `"create"` allows other conduits to consume and instantiate the
              spell.
            - `"block"` restricts access to the owning conduit.

        Lookup semantics:
            - `spellframe` provides the primary namespace or grouping key.
            - `binding_name` provides the secondary disambiguation key inside
              that frame.
            - The normalized lookup tuple is derived through
              `SpellInputUtils.make_spell_key_from_parts(...)`.

        Optional lifecycle hooks (`**kwargs`):
            - `pre_hooks`
            - `activation_hooks`
            - `post_hooks`

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

        Raises:
            RuntimeError:
                If the Spellbook is cleaned, no binding transaction is active,
                the normalized binding key is already in use, or the spell
                collides with an existing registry entry.
            TypeError:
                If invalid hook types are provided.
        """
        self.check_cleaned()
        self._ensure_binding_transaction_active(action="bind")
        try:
            permissions_enum = EnumHelpers.convert_enum_and_check(permissions, Permissions)
            existence_enum = EnumHelpers.convert_enum_and_check(existence, Existence)

            new_spell = self._bind.bind(
                permissions=permissions_enum,
                spell=spell,
                spellframe=spellframe,
                binding_name=binding_name,
                profile=profile,
                existence=existence_enum,
                aetheric_frame=self._aetheric_frame,
            )

            if Spellbook._aether._check_for_spell(new_spell.spell_id, self._aetheric_frame):
                self._logger.error(
                    f"Spell with ID {new_spell.spell_id} already exists in the registry.",
                    "bind",
                    exc_info=True,
                )
                raise RuntimeError(
                    "Spell ID collision detected. spell_id is computed from the spell's structural \n"
                    "fingerprint (e.g., module, qualname, signature, defaults). The existing spell \n"
                    "with this id is already registered in the Aether for this frame. If you intended \n"
                    "to register a distinct spell, ensure its structure (or binding/frame/name) differs \n"
                    "so it produces a unique spell_id."
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
            spell_index = self._get_required_spell_index_surface(
                new_spell.spell_index
            )
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
                new_spell._add_owned_conduit(
                    conduit._id,
                    conduit._name,
                    conduit._creations,
                    dynamic_environment=conduit.__dynamic_environment__,
                    creation_gate_controller=conduit._creation_gate_controller,
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
                spell=new_spell,
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
                    cast(SpellIndex, spell_index),
                    self._aetheric_frame,
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

        Scanning requires an active binding transaction. Use
        ``begin_transaction("bind")`` (or ``begin_binding_transaction()``)
        before scanning and ``end_binding_transaction()`` once registration
        is complete.

        Args:
            module (ModuleType): The module to scan for decorated spell targets.
        Returns:
            list[str]: Spell IDs bound during the scan, in module dict order.
        Raises:
            TypeError: If `module` is not a module or metadata is invalid.
            ValueError: If a decorated object is not owned by the module.
            RuntimeError: If no binding transaction is active for this Spellbook.
            RuntimeError: Propagated from Spellbook.bind on binding errors.
        """
        self.check_cleaned()
        self._ensure_binding_transaction_active(action="scan")
        scanner = Scan(self)
        return scanner.scan_module(module)

    def _add_hooks_to_spell(self, spell: ISpell, **kwargs) -> None:
        """
        Internal

        Attaches validation and lifecycle hooks to the newly bound spell object.

        Args:
            spell (ISpell): The newly created spell object.
            **kwargs: Contains optional keys for `pre_hooks`, `activation_hooks`, and `post_hooks`.

        Raises:
            TypeError: If any provided hook is not callable.
        """
        if not isinstance(spell, ISpell):
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
            rich-config sharing and the frame already has such a config:
              * If a config was passed in and it's not the same object, throw.
              * Otherwise, adopt the frame-owned config directly.
          - Otherwise:
              * If a config was passed in, verify its frame matches and keep it (unlocked).
              * Otherwise create a fresh SpellbookConfiguration for this frame (unlocked).
        """
        try:
            aether_config: Optional[IConfiguration] = self._get_configuration_from_aether()
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

    def _get_configuration_from_aether(self) -> IConfiguration | None:
        """
        Internal

        Retrieve the current frame-owned shared rich configuration from Aether,
        when the canonical frame posture explicitly permits shared rich config.

        Returns:
            IConfiguration | None: The frame-owned shared rich configuration for
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
            configuration: Optional[IConfiguration] = None,
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

    def _register_conduit_with_risk_manager(self, conduit: IConduit) -> None:
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

    def _register_spell_with_risk_manager(self, conduit_id: str, spell: ISpell) -> None:
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

    def _unregister_spell_with_risk_manager(self, conduit_id: str, spell: ISpell) -> None:
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
              first successful bind or accepts Nexus-provided posture that was
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

    def _publish_nexus_state_for_conjure(self, conduit: IConduit) -> None:
        """
        Internal

        Publish the frame/root-conduit spell state into Nexus after successful
        conjure wiring.

        Args:
            conduit:
                Root conduit created during conjure.

        Returns:
            None.
        """
        if not self._refresh_nexus_publish_enabled():
            conduit_surface = cast(_SpellbookConduitSurface, conduit)
            conduit_surface._nexus_publish_enabled = False
            return

        conduit_surface = cast(_SpellbookConduitSurface, conduit)
        conduit_surface._nexus_publish_enabled = True
        self._nexus._publish_frame_record(self)
        self._nexus._publish_conduit_record(conduit)
        for spell in self._spells.values():
            self._nexus._publish_spell_record(self, spell, conduit._id)

    def _publish_spell_record_to_nexus(self, spell: ISpell) -> None:
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
            spell: ISpell,
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



    def get_configuration(self) -> 'SpellbookConfiguration':
        """
        Public API

        Returns the active configuration object for this Spellbook.

        Returns:
            SpellbookConfiguration: The configuration instance.
        """
        return cast(SpellbookConfiguration, self._configuration)

    def configure_aether_frame(
            self,
            *,
            system_state: Optional[str],
            disposal: Optional[bool],
            disposal_method_names: Optional[List[str]],
    ) -> None:
        """
        Public API

        Apply frame/runtime posture inputs, freeze configuration, and bind the
        result into Aether for this spellbook's frame.

        Contract:
            - Uses the existing spellbook configuration and frame-configuration
              objects rather than creating a parallel setup path.
            - Applies only provided values; omitted values leave current state
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
        """
        self.check_cleaned()
        frame_configuration = self._aetheric_frame_configuration
        if frame_configuration is None:
            raise RuntimeError("AethericFrameConfiguration is unavailable.")
        if system_state is not None:
            frame_configuration.with_system_state(system_state)

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


    def conjure(self, policy: Optional[str] = "default", automatic: bool = True, name: Optional[str] = None, conduit_logger: Optional[Any] = None) -> IConduit:
        """
        Public API

        Creates a new **Conduit** (execution channel) from this Spellbook.

        This method finalizes the configuration, validates all local spells, and instantiates the `Conduit`.
        Conjuring disables the default binding transaction; post-conjure bind/scan
        requires an explicit `begin_binding_transaction()` call.

        Args:
            policy (str, optional):
                Access control policy for this conduit (dynamic-only modes). Must match a `Policies` enum member.
                Defaults to "default".
            automatic (bool, optional):
                If True, operate in automatic (non-dynamic) mode. If False, require `system_state` to be dynamic.
            name (str, optional):
                An optional name for the conduit.
            conduit_logger (Any, optional):
                An optional logger instance to attach to the conduit for logging purposes.

        Returns:
            Conduit: The newly created Conduit instance.

        Raises:
            RuntimeError: If this Spellbook has already conjured a Conduit (only one is allowed).
            RuntimeError: If dynamic-only policies are used when `system_state` is "automatic" or when `automatic` is True.
            ValueError: If the configuration fails validation or the policy string is invalid.

        Policies:
            - **Automatic mode (automatic=True)**: only `"default"` is allowed (linking disabled).
            - **Dynamic mode (automatic=False and `system_state` is dynamic)**:
                * `"default"`: normal per-spell rules.
                * `"whitelist_all"` / `"block_all"`: override per-spell whitelist behavior.
                * `"inbound_only"` / `"outbound_only"`: directional link restrictions.

        Hook integration
        ----------------
        If the active SpellbookConfiguration has Conduit lifecycle hooks registered under this
        Spellbook's ID, they are fetched via
        ``SpellbookCreationSystem.get_conjure_hook_map()`` and invoked
        in the following order:

            1. "on_conduit_pre_created()"
                   Fired **before** the Conduit is constructed. No Conduit instance
                   is passed, because it does not exist yet.

            2. "on_conduit_activated(conduit)"
                   Fired immediately after the Conduit has been constructed
                   (its ``__init__`` has run), but before it is wired into spells.

            3. "on_conduit_post_created(conduit)"
                   Fired after the Conduit has been integrated into all local
                   spells via
                   ``SpellbookCreationSystem.define_conduit_into_spells``.

        For conjured (root) conduits, these hooks receive:

            - pre  : no arguments
            - act  : (conduit,)
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

            spellbook_creation_system = SpellbookCreationSystem(
                spellbook=self,
                policy=policy,
                automatic=automatic,
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

    def _run_structural_phases(self) -> Dict[str, Sequence[IUnitOfWork]]:
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
            Dict[str, Sequence[IUnitOfWork]]: Phase execution result mapping.
        Raises:
            SpellbookValidationError: If structural validation marks any spell broken.
            Exception: Propagates scheduler/phase execution failures.
        """
        return SpellbookCreationSystem.run_structural_phases(
            spellbook=self,
            phase_scheduler_cls=PhaseScheduler,
        )

    def _run_post_conjure_structural_phases(self, spells: Sequence[ISpell]) -> None:
        """
        Internal

        Purpose:
            Execute structural phases for spells bound after conduit conjure.
        Contract:
            - Delegates execution to `SpellbookCreationSystem`.
            - Applies only to the provided spell sequence.
            - Leaves already-conjured conduit state intact.
        Threading:
            Caller must hold the Spellbook lock while mutating bound spell state.
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
    ) -> Dict[str, Sequence[IUnitOfWork]]:
        """
        Internal

        Purpose:
            Execute conduit-scoped resolution phases (5-11) for one conduit id.
        Contract:
            - Delegates orchestration to `SpellbookCreationSystem`.
            - Uses Spellbook's `PhaseScheduler` symbol to preserve patch points.
            - Cleans temporary phase artifacts before returning.
        Threading:
            Caller must hold the Spellbook lock for consistent conduit scope state.
        Args:
            conduit_id: Conduit id for resolution scope.
        Returns:
            Dict[str, Sequence[IUnitOfWork]]: Phase execution result mapping.
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
            target_spell: ISpell,
    ) -> Dict[str, Sequence[IUnitOfWork]]:
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
            Dict[str, Sequence[IUnitOfWork]]: Phase execution result mapping.
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
            target_spell: ISpell,
    ) -> Dict[str, Sequence[IUnitOfWork]]:
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
            Dict[str, Sequence[IUnitOfWork]]: Phase execution result mapping.
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




