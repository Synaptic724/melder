from contextlib import contextmanager
from types import MappingProxyType, ModuleType
from typing import Optional, List, Any, Mapping, Callable, Sequence, Dict, Set, Iterable, Tuple
import threading
# Melder Imports
from melder.aether.aether import Aether
from melder.aether.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeControlTransactionRequest,
    ChangeTransactionType,
)
from melder.spellbook.bind.spell_index import SpellIndex
from melder.spellbook.bind.scan import Scan
from melder.spellbook.configuration.system_state import SystemState
from melder.spellbook.spell_crafter.validation.validation_system import SpellValidationSystem
from melder.spellbook.spellbinder import SpellBinder
from melder.utilities.custom_exceptions.spellbook_validation_error import SpellbookValidationError
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.interfaces.interfaces import ISpell, IConfiguration, ISpellIndex, ISpellSystemStates, ISpellbook
from melder.spellbook.configuration.configuration import Configuration
from melder.aether.conduit.conduit import Conduit
from melder.spellbook.bind.bind import Bind
from melder.spellbook.existence.existence import Existence
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.utilities.helpers.general_helpers import EnumHelpers
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.utilities.helpers.init_helpers import InitHelpers
from melder.utilities.helpers.general_helpers import SpellInputUtils
from melder.utilities.synchronization.phase_scheduler import PhaseScheduler
from melder.utilities.synchronization.cancellation_event_signal import CancellationEventSignal
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg


#region Spellbook
class Spellbook(Cleanable, ISpellbook):
    """
    Public API

    🧙 The **Spellbook** is the central authority for all spell definitions, bindings, and conduit conjurations.

    It acts as a high-level composition container and registry. All spells added to a Spellbook must be
    uniquely identifiable and comply with the Aetheric access rules and configuration state.

     -------------------------------------------------------------------------------
     ⚠️  WARNING: DO NOT USE `aetheric_frame` UNLESS YOU UNDERSTAND THE IMPLICATIONS!
     ⚠️  IMPORTANT: AETHER FRAMES

     The `aetheric_frame` parameter allows multiple Spellbooks to share the same
     configuration and spell visibility. This feature supports system-wide coordination,
     contract binding, and cross-agent sharing of spells.

     🧠 **Do not use `aetheric_frame` unless you have read the documentation** and
     understand the implications of shared scope, mutation locking, and distributed
     spell ownership.

     By default, using (aetheric_frame="default") uses the shared default frame.
     Passing a new frame name creates an isolated frame for that name.
     -------------------------------------------------------------------------------

    **Responsibilities:**
    * Holds and registers all known spells (via `bind()`).
    * Ensures configuration is frozen and synchronized via the Aether.
    * Provides conduit conjuring (`conjure()`) based on validated spells.
    * Supports optional shared configuration state through the `aetheric_frame` system.

    Args:
        aetheric_frame (str, optional):
            A shared frame name used to join multiple Spellbooks under the same Aetheric
            configuration and spell contract scope. Defaults to "default".
            If the named frame does not exist, Spellbook will create it.
        configuration (Optional[Configuration]):
            An optional pre-configured `Configuration` instance to use, typically provided
            when creating a Spellbook for an existing Aether frame.

    Notes:
        * You may only conjure one conduit per spellbook instance.
        * Configuration is locked automatically upon conjuring.
        * If configuration is already shared via an Aether frame, it will be reused.
    """
    __melder_internal__ = _mrg.sentinel
    _aether = Aether()
    def __init__(self, aetheric_frame: str = "default", configuration: Optional[IConfiguration] = None,
                 logger: Any | None = None):
        super().__init__()

        # Internal state
        self._lock: threading.RLock = threading.RLock()
        self._id: str = IDBuilder.create_id()
        self._conjured = False
        self._binding_transaction_active: bool = True
        self._active_change_request: Optional[ChangeControlTransactionRequest] = None
        self._pending_binding_frame_keys: Set[str] = set()
        self._pending_structural_spells: List[ISpell] = []
        self._conduit: Optional[Conduit] = None
        self._aetheric_frame: str = aetheric_frame
        if not isinstance(self._aetheric_frame, str):
            raise TypeError(f"aetheric_frame must be a string, got {type(self._aetheric_frame).__name__}")
        Spellbook._aether._ensure_frame(self._aetheric_frame)

        # Configuration state
        self._configuration_locked: bool = False
        self._configuration: IConfiguration = configuration
        # Temporary logger for configuration init; will be replaced in _initialize_logging.
        self._logger: Optional[Any] = InitHelpers.resolve_safe_logger(None)
        self._initialize_configuration()

        # Logger setup
        self._initialize_logging(logger)

        # Core spell storage (SpellIndex Maps)
        self._spells: Dict[SpellIndex, ISpell] = {}
        self._spell_versions: Set[str] = set()
        self._lookup_spells: Dict[tuple, SpellIndex]  = {}

        # Networked/remote spell support
        # This stores spells borrowed from other conduits (keyed by peer Conduit id)
        self._contracted_spells: Dict[str, Dict[SpellIndex, ISpell]] = {}
        self._contracted_versions: Dict[str, Set[str]] = {}
        self._lookup_contracted_spells: Dict[str, Dict[tuple, SpellIndex]]  = {}

        # Spell validator
        self._spell_validator: SpellValidationSystem = SpellValidationSystem()
        # Spell States System
        self._spell_system_states: ISpellSystemStates = Spellbook._aether._get_spell_system_states(aetheric_frame)

        # Binding system
        self._bind: Bind = Bind(self)

    #region Disposal

    def cleanup(self) -> None:
        if self._logger is not None:
            pass

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
        # 1) Clean ONLY local spells (not contracted)
        self._cleanup_spells()

        if self._spells is not None:
            try:
                self._spells.clear()
            except Exception as e:
                self._logger.error(f"Error clearing _spells: {e}", "_cleanup_components", exc_info=True)
            self._spells = None

        # 2) Clean lookup/contracted maps and local maps
        if self._lookup_spells is not None:
            try:
                self._lookup_spells.clear()
            except Exception as e:
                self._logger.error(f"Error cleaning _lookup_spells: {e}", "_cleanup_components", exc_info=True)
            self._lookup_spells = None

        if self._contracted_spells is not None:
            try:
                self._contracted_spells.clear()
            except Exception as e:
                self._logger.error(f"Error cleaning _contracted_spells: {e}", "_cleanup_components", exc_info=True)
            self._contracted_spells = None

        if self._lookup_contracted_spells is not None:
            try:
                self._lookup_contracted_spells.clear()
            except Exception as e:
                self._logger.error(f"Error cleaning _lookup_contracted_spells: {e}", "_cleanup_components", exc_info=True)
            self._lookup_contracted_spells = None

        if self._spells is not None:
            try:
                self._spells.clear()
            except Exception as e:
                self._logger.error(f"Error cleaning _spells: {e}", "_cleanup_components", exc_info=True)
            self._spells = None

        # 3) cleanup configuration
        if self._configuration is not None:
            try:
                self._configuration.cleanup()
            except Exception as e:
                self._logger.error(f"Error cleaning configuration: {e}", "_cleanup_components", exc_info=True)
            self._configuration = None

        if self._spell_versions is not None:
            try:
                self._spell_versions.clear()
            except Exception as e:
                self._logger.error(f"Error cleaning _spell_versions: {e}", "_cleanup_components", exc_info=True)
            self._spell_versions = None

        if self._contracted_versions is not None:
            try:
                self._contracted_versions.clear()
            except Exception as e:
                self._logger.error(f"Error cleaning _contracted_versions: {e}", "_cleanup_components", exc_info=True)
            self._contracted_versions = None

        if self._spell_validator is not None:
            try:
                self._spell_validator.cleanup()
            except Exception as e:
                self._logger.error(f"Error cleaning spell validator: {e}", "_cleanup_components", exc_info=True)
            self._spell_validator = None


    def _cleanup_spells(self) -> None:
        if self._spells is None:
            return

        items = list(self._spells.items())
        for spell_index, spell in items:
            try:
                spell.cleanup()
            except Exception as e:
                self._logger.error(f"Error cleaning spell '{spell_index}': {e}", "_cleanup_spells", exc_info=True)
            try:
                spell_index.cleanup()
            except Exception as e:
                self._logger.error(f"Error cleaning spell index '{spell_index}': {e}", "_cleanup_spells", exc_info=True)


    # -------------------------
    # Phase 2: Core teardown (after lock)
    # -------------------------

    def _cleanup_core(self) -> None:

        # Nullify high-level refs (no try/catch for simple None assignments)
        self._bind = None
        self._aetheric_frame = None
        self._id = None
        self._conduit = None
        self._conjured = None
        self._binding_transaction_active = None
        self._active_change_request = None
        self._pending_binding_frame_keys = None
        self._pending_structural_spells = None
        self._spell_system_states = None
        self._configuration_locked = None

        # Lock: just null it (no getattr/hasattr)
        self._lock = None

        # Destroy logger LAST
        if self._logger is not None:
            try:
                pass
            except Exception:
                pass  # if logger is already busted, skip the debug
            try:
                if hasattr(self._logger, "cleanup"):
                    self._logger.cleanup()
            except Exception as e:
                try:
                    self._logger.error(f"Error during logger cleanup: {e}", "_cleanup_core", exc_info=True)
                except Exception:
                    pass
            self._logger = None


    #endregion Disposal
    #region Context Manager
    def __enter__(self):
        """
        Enters the context manager for Aether.
        """
        self._lock.acquire()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exits the context manager for Aether.
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
              version IDs (SHA256) for that conduit’s spells.
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

    #region Logging

    def _initialize_logging(self, logger: Any | None) -> None:
        """
        Internal

        Establish the Spellbook logger, then ensure Aether has a real logger if a
        configuration-backed factory exists.

        Priority:
            1) Explicit logger arg
            2) Configuration's logger factory
            3) Silent no-op logger

        Side-effect:
            If Aether is still on a null logger and a factory exists, upgrade Aether
            to a real logger exactly once.
        """
        cfg = self._configuration
        try:
            if logger is not None:
                self._logger = InitHelpers.resolve_safe_logger(logger)
            elif cfg is not None and cfg.has_logger_factory():
                self._logger = InitHelpers.resolve_safe_logger(cfg.get_logger_for(self))
            else:
                self._logger = InitHelpers.resolve_safe_logger(None)
            self._upgrade_aether_logger_if_possible()
        except Exception as e:
            # fallback to silent logger if anything blows up
            self._logger = InitHelpers.resolve_safe_logger(None)
            self._logger.error(f"Failed to initialize logger: {e}", "_initialize_logging", exc_info=True)

    def _upgrade_aether_logger_if_possible(self) -> None:
        """
        Internal

        If a Configuration-backed logger factory exists, and the Aether singleton
        is still using a null/no-op SafeLogger, upgrade Aether to a real logger.

        This runs at Spellbook construction time when a Configuration finally exists.
        """
        cfg = self._configuration
        if cfg is None or not cfg.has_logger_factory():
            return
        aether = Spellbook._aether
        try:
            if aether._logger is not None and getattr(aether._logger, "_logger", None) is None:
                aether_logger = cfg.get_logger_for(aether)
                aether._logger = InitHelpers.resolve_safe_logger(aether_logger)
        except Exception as e:
            self._logger.error(f"Failed to upgrade Aether logger: {e}", "_upgrade_aether_logger_if_possible", exc_info=True)

    #endregion Logging
    #region Properties

    @property
    def id(self) -> str:
        """
        Public API

        Returns the unique ID of this Spellbook instance.

        Returns:
            str: The Spellbook's unique identifier.
        """
        return self._id

    @property
    def spells(self) -> Mapping[SpellIndex, ISpell]:
        """
        Public API

        Returns a read-only view of the local spells registered in this spellbook.
        This provides safe introspection without allowing mutation.

        Returns:
            Mapping[str, ISpell]: An immutable map of spell ID to spell object.
        """
        return MappingProxyType(self._spells)

    @property
    def contracted_spells(self) -> Mapping[str, Mapping[SpellIndex, ISpell]]:
        """
        Public API

        Returns a per-conduit read-only view of all **borrowed** spells.
        Each conduit ID maps to its own immutable SpellIndex→Spell map.

        Returns:
            Mapping[str, Mapping[SpellIndex, ISpell]]:
                Immutable map of peer Conduit ID to immutable map of borrowed spells.
        """
        return MappingProxyType({
            conduit_id: MappingProxyType(dict(spells))
            for conduit_id, spells in self._contracted_spells.items()
        })

    #endregion Properties

    #region Core Methods
    #region General Methods
    def get_spell_permissions(self, spell_index: ISpellIndex) -> Optional[str]:
        """
        Public API

        Retrieves the access permissions for a **locally** registered spell.

        Args:
            spell_index:
                The SpellIndex (lineage) of the spell.

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
                The spell object if found, else ``None``.
        """
        spell = self._spells.get(spell_index)
        return spell

    def _find_contracted_spell(self, spell_index: SpellIndex) -> Optional[ISpell]:
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
        for contracted_spells in self._contracted_spells.values():
            if spell_index in contracted_spells:
                return contracted_spells[spell_index]
        self._logger.error(f"Contracted spell with ID {spell_index} not found.", "_find_contracted_spell", exc_info=True)
        raise RuntimeError(f"Contracted spell with ID {spell_index} not found in the spellbook.")

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

        Finds a spell's SpellIndex (lineage identifier) using its logical identifiers.

        The search checks local spells first, then contracted spells.

        Args:
            spellframe (str): The logical namespace or grouping label.
            spell_name (str): The name of the spell class or function.
            binding_name (str): The secondary key to distinguish the spell.

        Returns:
            Optional[SpellIndex]: The SpellIndex representing this spell's lineage.

        Raises:
            RuntimeError: If the spell is not found in the spellbook (local or contracted).
        """
        key = self._make_spell_key(spellframe, spell_name, binding_name)
        if key in self._lookup_spells:
            return self._lookup_spells[key]
        for contracted_spells in self._lookup_contracted_spells.values():
            if key in contracted_spells:
                return contracted_spells[key]
        self._logger.error("Spell not found in the spellbook.", "find_spell_id", exc_info=True)
        raise RuntimeError("Spell not found in the spellbook.")

    def _make_spell_key(self, spellframe: str, spell_name: str, binding_name: str) -> tuple:
        """
        Internal

        Creates a normalized key for spell lookups.

        Args:
            spellframe (str): The logical frame (can be None).
            spell_name (str): The primary name.
            binding_name (str): The binding name (can be None).

        Returns:
            tuple: (frame_or_name, binding_name_or_default)
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
            spell_index: SpellIndex associated with the incoming spell.
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


    def _check_all_spells(self) -> None:
        """
        Internal

        Performs a system check to verify that no locally bound spell ID is already
        registered in the global Aether registry for this frame.

        Raises:
            RuntimeError: If a spell ID is found to be duplicated in the Aether.
        """
        with self._lock:
            for spell_index in self._spells.keys():
                for spell_version_id in spell_index._versions:
                    if Spellbook._aether._check_for_spell(spell_version_id, self._aetheric_frame):
                        self._logger.error(f"Spell with ID {spell_version_id} already exists in the registry.", "_check_all_spells", exc_info=True)
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

        # Pull the map of SpellIndex → ISpell for this conduit
        spell_map = self._contracted_spells.get(conduit_id)
        if spell_map is None:
            return None

        # Search for a SpellIndex whose version list contains this SHA
        for spell_index, spell in spell_map.items():
            if spell_index.has_version(spell_id):
                return spell

        return None



    def _create_link_contract(self, conduit_id: str):
        """
        Internal

        Initializes the internal storage maps for a new contract link with a peer conduit.

        This method ensures `_contracted_spells` (value map), `_lookup_contracted_spells`
        (key map), and `_contracted_versions` (version cache) are initialized
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

        if not (a_exists == b_exists == c_exists):
            self._logger.error("Inconsistent link contract state", "_create_link_contract", exc_info=True)
            raise RuntimeError(
                f"Inconsistent link contract state for conduit ID {conduit_id}: "
                f"_contracted_spells={a_exists}, "
                f"_lookup_contracted_spells={b_exists}, "
                f"_contracted_versions={c_exists}"
            )

        if not a_exists and not b_exists and not c_exists:
            with self._lock:
                self._contracted_spells[conduit_id] = {}
                self._lookup_contracted_spells[conduit_id] = {}
                self._contracted_versions[conduit_id] = set()


    def _remove_link_contract(self, conduit_id: str):
        """
        Internal

        Removes the internal storage maps for a dissolved contract link with a peer conduit.

        This ensures all three maps are removed atomically and consistently.

        Args:
            conduit_id (str): The ID of the peer conduit whose contract structure should be removed.

        Raises:
            RuntimeError: If the contract structure is found in some maps but not all
                          (inconsistent cleanup).
        """

        a_exists = conduit_id in self._contracted_spells
        b_exists = conduit_id in self._lookup_contracted_spells
        c_exists = conduit_id in self._contracted_versions

        if not (a_exists == b_exists == c_exists):
            self._logger.error("Inconsistent link contract state", "_remove_link_contract", exc_info=True)
            raise RuntimeError(
                f"Inconsistent link contract state for conduit ID {conduit_id}: "
                f"_contracted_spells={a_exists}, "
                f"_lookup_contracted_spells={b_exists}, "
                f"_contracted_versions={c_exists}"
            )

        if a_exists:
            with self._lock:
                self._contracted_spells.pop(conduit_id, None)
                self._lookup_contracted_spells.pop(conduit_id, None)
                self._contracted_versions.pop(conduit_id, None)


    def _add_contracted_spell(self, spell: ISpell, conduit_id: str) -> None:
        """
        Internal

        Adds a specific spell (borrowed from a peer) to the contracted spells
        and updates the key and version caches for the given conduit.

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

            # Main maps: SpellIndex → ISpell and key → SpellIndex
            spell_map[spell.spell_index] = spell
            lookup_map[spell_key] = spell.spell_index

            # Track all known versions for this SpellIndex in the per-conduit version set
            versions = spell.spell_index._versions
            if versions:
                for version_id in versions:
                    versions_set.add(version_id)

            frame_key = spell.key[0]
            should_mark = bool(self._conjured)

        if should_mark and frame_key:
            self._mark_collection_dependents_dirty({frame_key})
        self._try_update_staged_contract_keys(conduit_id)


    def _remove_contracted_spell(self, spell_id: str, conduit_id: str) -> None:
        """
        Internal

        Removes a specific contracted spell from the internal registry.

        When a link transaction is active, this also refreshes staged contract
        keys for the peer conduit so change-control commit hooks can observe
        the updated contract scope.

        Args:
            spell_id (str): The version SHA of the spell to remove.
            conduit_id (str): The ID of the peer conduit the spell was contracted from.
        """

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
        self._try_update_staged_contract_keys(conduit_id)


    def _clear_contracted_spells_for_conduit(self, conduit_id: str) -> None:
        """
        Internal

        Clears all spells associated with a contracted conduit, retaining
        the contract structure and zeroing the version cache.

        When a link transaction is active, this also refreshes staged contract
        keys for the peer conduit so change-control commit hooks can observe
        the updated contract scope.

        Args:
            conduit_id (str): The ID of the peer conduit whose contracted spells are to be cleared
        """

        with self._lock:
            if (
                    conduit_id not in self._contracted_spells
                    or conduit_id not in self._lookup_contracted_spells
                    or conduit_id not in self._contracted_versions
            ):
                self._logger.error(
                    f"No contracted spell maps for conduit {conduit_id}",
                    "_clear_contracted_spells_for_conduit",
                    exc_info=True,
                )
                raise RuntimeError(f"No contracted spell maps found for conduit ID {conduit_id}.")

            self._contracted_spells[conduit_id].clear()
            self._lookup_contracted_spells[conduit_id].clear()
            self._contracted_versions[conduit_id].clear()
        self._try_update_staged_contract_keys(conduit_id)


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



    #endregion Contract API
    #region Binding API

    def create_binder(
            self,
            *,
            default_existence: Existence = Existence.unique,
            default_permissions: str = "create",
    ) -> SpellBinder:
        """
        Public API

        Creates a `SpellBinder` instance that provides an Autofac-style
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
            SpellBinder:
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

        change_control = self._aether._get_change_control_manager(self._aetheric_frame)
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
    ) -> "Spellbook":
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
        Returns:
            Spellbook: The current Spellbook instance.
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
    def binding_transaction(self) -> "Spellbook":
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

        Returns:
            Spellbook: The current Spellbook instance.
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

        change_control = self._aether._get_change_control_manager(self._aetheric_frame)
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
            existence: str | Existence,
            permissions: str = "create",
            spellframe: Any = None,
            binding_name: str = None,
            **kwargs,
    ) -> str:
        """
        Binds a spell into the Spellbook for future instantiation and dependency injection.

        The `bind()` method registers a class, function, or object into Melder’s system,
        associating it with a lifecycle (`Existence`), a permission policy, and optional metadata.
        Once bound, the spell becomes available for resolution and casting within its conduit
        or across systems (depending on permissions).

        Binding requires an active binding transaction. Use
        ``begin_transaction("bind")`` (or ``begin_binding_transaction()``)
        before binding and ``end_binding_transaction()`` once registration
        is complete.

        When a change-control bind transaction is active, binding updates the
        staged request metadata with the normalized binding keys for the spells
        registered in that transaction.

        ──────────────────────────────────────────────
        🧠 Binding Overview:
            - Profiles the spell via reflection.
            - Computes a unique SHA256 `spell_id`.
            - Stores the spell into the internal spell registry.
            - Assigns its lookup key via `(spellframe, binding_name)`.
            - Applies lifecycle and permission policies.
            - Optionally attaches lifecycle hooks.

        ──────────────────────────────────────────────
        🛡️ Permissions (access control to other conduits):
            - `"read"`:
                Allows other conduits to *use* the spell but not create new instances.
                Useful for shared utilities or resources.

            - `"create"` (default):
                Allows other conduits to both use *and* create instances from this spell.

            - `"block"`:
                Completely blocks access to the spell from other conduits.
                Only the owning conduit can use or instantiate it.

        🔄 Existence (spell lifecycle):
            Determines how the spell instance is managed (singleton, transient, etc.).
            Use `Existence.unique`, `Existence.many`, etc., for fine-grained control.

        📦 Spellframe (optional):
            Logical namespace or grouping label.
            Often corresponds to a shared interface, protocol, or feature group.

        🔑 Binding Name (optional):
            Secondary key used to distinguish different versions or roles of the same type.
            Useful when multiple spells are bound under the same interface.

        ──────────────────────────────────────────────
        🪝 Lifecycle Hooks (optional `**kwargs`):

            - `pre_hooks`: List[Callable]
                Executed *before* the spell is constructed or cast.
                Can be used for validation, preparation, or logging.

            - `activation_hooks`: List[Callable]
                Executed *during* spell construction. Useful for modifying dependencies
                or adapting runtime context.

            - `post_hooks`: List[Callable]
                Executed *after* the spell has been cast. Often used for initialization,
                analytics, or final injection steps.

            ⚠️ All hooks must be callables.

        ──────────────────────────────────────────────
        Args:
            spell (Any): The class, function, or object to bind into the spellbook.
            existence (Existence): The lifecycle scope for this spell.
            permissions (str): Permission level exposed to other conduits ("read", "create", "block").
            spellframe (Optional[Any]): Logical interface or category for grouping.
            binding_name (Optional[str]): Name key to distinguish this spell among others in its frame.
            **kwargs:
                - pre_hooks (Optional[List[Callable]]): Hooks executed before casting.
                - activation_hooks (Optional[List[Callable]]): Hooks executed during casting/construction.
                - post_hooks (Optional[List[Callable]]): Hooks executed after casting/construction.

        Returns:
            str: The unique SHA256 `spell_id` associated with the bound spell.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            RuntimeError: If no binding transaction is active for this Spellbook.
            RuntimeError: If the Conduit is not a 'normal' conduit (only normal conduits can bind spells).
            RuntimeError: If the spell is already bound in the registry.
            RuntimeError: If the normalized binding key is already in use locally.
            TypeError: If invalid hook types are provided.
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
            self._lookup_spells[new_spell._key] = new_spell.spell_index
            self._spells[new_spell.spell_index] = new_spell

            # keep local version cache warm
            if self._spell_versions is not None:
                versions = new_spell.spell_index._versions
                if versions:
                    for vid in versions:
                        self._spell_versions.add(vid)
                else:
                    self._spell_versions.add(new_spell.spell_id)

            # If a Conduit already exists, stamp ownership metadata for the new spell.
            # Existing-object spells are also eagerly registered into Creations.
            if self._conjured and self._conduit is not None:
                new_spell._add_owned_conduit(
                    self._conduit._id,
                    self._conduit._name,
                    self._conduit._creations,
                )
                if new_spell.user_created_object is not None:
                    try:
                        self._conduit._register_to_creations(
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

            self._spell_system_states.register_lineage(
                spell_index=new_spell.spell_index,
                spell=new_spell,
            )
            if self._pending_binding_frame_keys is not None:
                self._pending_binding_frame_keys.add(new_spell.key[0])
            if self._pending_structural_spells is not None:
                self._pending_structural_spells.append(new_spell)
            self._try_update_staged_binding_keys()
            if self._conjured and self._conduit is not None:
                Spellbook._aether._register_single_spell_index(
                    self._conduit._id,
                    new_spell.spell_index,
                    self._aetheric_frame,
                )
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
        with self._lock:
            if "pre_hooks" in kwargs:
                for hook in kwargs["pre_hooks"]:
                    if not callable(hook):
                        self._logger.error("pre_hooks must be a list of callables.", "_add_hooks_to_spell", exc_info=True)
                        raise TypeError("pre_hooks must be a list of callables.")
                spell.pre_hooks = kwargs["pre_hooks"]
            if "activation_hooks" in kwargs:
                for hook in kwargs["activation_hooks"]:
                    if not callable(hook):
                        self._logger.error("activation_hooks must be a list of callables.", "_add_hooks_to_spell", exc_info=True)
                        raise TypeError("activation_hooks must be a list of callables.")
                spell.activation_hooks = kwargs["activation_hooks"]
            if "post_hooks" in kwargs:
                for hook in kwargs["post_hooks"]:
                    if not callable(hook):
                        self._logger.error("post_hooks must be a list of callables.", "_add_hooks_to_spell", exc_info=True)
                        raise TypeError("post_hooks must be a list of callables.")
                spell.post_hooks = kwargs["post_hooks"]

    #endregion Binding API
    #region Configuration API
    def _initialize_configuration(self) -> None:
        """
        Internal

        Initialize configuration with the following rules:
          - If Aether already has a config for this frame:
              * If a config was passed in and it's not the same object, throw.
              * Otherwise, adopt the Aether config and mark as locked.
          - If Aether has no config:
              * If a config was passed in, verify its frame matches and keep it (unlocked).
              * Otherwise create a fresh Configuration for this frame (unlocked).
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
                        "Configuration name does not match the aetheric frame",
                        "_initialize_configuration",
                        exc_info=True,
                    )
                    raise RuntimeError("Configuration name does not match the aetheric frame.")

                self._configuration_locked = False
                return

            # No config in Aether and none provided: create a fresh one and load defaults.
            self._configuration = Configuration(self._aetheric_frame)
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

        Retrieves the current configuration from the Aether's global registry.

        Returns:
            IConfiguration | None: The configuration instance for this Aether frame, or None if not registered.
        """
        try:
            return Spellbook._aether._get_configuration(self._aetheric_frame)
        except Exception as e:
            self._logger.error(
                f"Error retrieving configuration from Aether: {e}",
                "_get_configuration_from_aether",
                exc_info=True,
            )
            raise


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
        worker counts, etc.) have already been applied via the Configuration's
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
                    "Configuration validation failed.",
                    "_validate_and_freeze_configuration",
                    exc_info=True,
                )
                raise ValueError("Configuration validation failed.")

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

        Binds the now-frozen configuration to the Aether for this Spellbook's frame.
        """
        try:
            Spellbook._aether._bind_configuration(self._configuration, self._aetheric_frame)
        except Exception as e:
            self._logger.error(
                f"Failed to bind configuration to Aether: {e}",
                "_bind_configuration_to_aether",
                exc_info=True,
            )
            raise



    def get_configuration(self) -> 'Configuration':
        """
        Public API

        Returns the active configuration object for this Spellbook.

        Returns:
            Configuration: The configuration instance.
        """
        return self._configuration

    #endregion Configuration API
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


    def conjure(self, policy: Optional[str] = "default", automatic: bool = True, name: str = None, conduit_logger: Any | None = None) -> Conduit:
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
        If the active Configuration has Conduit lifecycle hooks registered under this
        Spellbook's ID, they are fetched via ``_get_conjure_hook_map()`` and invoked
        in the following order:

            1. "on_conduit_pre_created()"
                   Fired **before** the Conduit is constructed. No Conduit instance
                   is passed, because it does not exist yet.

            2. "on_conduit_activated(conduit)"
                   Fired immediately after the Conduit has been constructed
                   (its ``__init__`` has run), but before it is wired into spells.

            3. "on_conduit_post_created(conduit)"
                   Fired after the Conduit has been integrated into all local
                   spells via ``_define_conduit_into_spells``.

        For conjured (root) conduits, these hooks receive:

            - pre  : no arguments
            - act  : (conduit,)
            - post : (conduit,)
        """

        with self._lock:
            if self._conjured:
                conduit_id = None
                conduit_name = None
                if self._conduit is not None:
                    conduit_id = self._conduit._id
                    conduit_name = self._conduit._name
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

            # Ensure configuration is validated, frozen, and bound to Aether
            if not self.is_configuration_locked():
                self._validate_and_freeze_configuration()
                self._bind_configuration_to_aether()

            # Run structural phases (1-4) before resolution phases.
            self._run_structural_phases()

            # Create a unique ID for this Conduit for per-conduit resolution phases.
            conduit_id = IDBuilder.create_id()

            # Run conduit-scoped resolution phases (5-7) after structural validation.
            self._run_resolution_phases_for_conduit(conduit_id)

            # Validate policy vs system_state and local spell registry
            self._check_system_state(policy, automatic)
            policy_enum = EnumHelpers.convert_enum_and_check(policy, Policies)
            self._check_all_spells()

            # Pull the hook map once for this conjuration.
            hook_map = self._get_conjure_hook_map()

            # 1) PRE: before Conduit exists — NO conduit instance passed here.
            self._fire_conjure_hooks(
                hook_map,
                "on_conduit_pre_created",
            )

            # 2) Construct the Conduit.
            conduit = Conduit(
                spellbook=self,
                name=name,
                conduit_state=ConduitState.normal,
                configuration=self._configuration,
                aetheric_frame=self._aetheric_frame,
                policy=policy_enum,
                automatic=automatic,
                logger=conduit_logger,
                conduit_id=conduit_id,
            )

            # Mark this Spellbook as having conjured its single conduit
            self._conjured = True
            self._conduit = conduit
            self._binding_transaction_active = False
            if self._pending_binding_frame_keys is not None:
                self._pending_binding_frame_keys.clear()

            # 3) ACTIVATED: conduit exists but is not yet wired into spells.
            self._fire_conjure_hooks(
                hook_map,
                "on_conduit_activated",
                conduit,
            )

            # Wire conduit ownership metadata into all local spells.
            self._define_conduit_into_spells(conduit)

            # 4) POST: final notification after Spellbook-side init is complete.
            self._fire_conjure_hooks(
                hook_map,
                "on_conduit_post_created",
                conduit,
            )

            return conduit




    def _check_system_state(self, policy: str, automatic: bool) -> None:
        """
        Internal

        Checks if the requested policy is compatible with the current `system_state` configuration.

        Purpose:
            Enforce the contract between conduit policies and the configured
            system state before conjure proceeds.
        Contract:
            - Automatic mode only allows the default policy.
            - Dynamic policies require a dynamic system_state.
            - Raises with policy, automatic, and system_state context for diagnosis.
        Args:
            policy (str): The policy requested for the new Conduit.
            automatic (bool): Whether to operate in automatic (non-dynamic) mode.

        Raises:
            RuntimeError: If a dynamic-only policy is requested while `automatic` is True or `system_state` is automatic.
        """
        policy_enum = EnumHelpers.convert_enum_and_check(policy, Policies)
        system_state = self._configuration.get_property("system_state")

        # Automatic mode: only default policy is allowed
        if automatic:
            if policy_enum != Policies.default:
                self._logger.error(
                    "Dynamic-only policy requested while automatic=True "
                    f"(policy={policy_enum}, system_state={system_state}).",
                    "_check_system_state",
                    exc_info=True,
                )
                raise RuntimeError(
                    "Dynamic-only policies are not allowed when automatic mode is requested. "
                    f"(policy={policy_enum}, automatic={automatic}, "
                    f"system_state={system_state}, allowed=default)"
                )
            return

        # Dynamic requested: ensure system_state supports it
        if system_state == SystemState.automatic:
            self._logger.error(
                "Dynamic policy requested while system_state is automatic "
                f"(policy={policy_enum}, automatic={automatic}, "
                f"system_state={system_state}).",
                "_check_system_state",
                exc_info=True,
            )
            raise RuntimeError(
                "Cannot use dynamic policies in automatic system_state. "
                f"(policy={policy_enum}, automatic={automatic}, system_state={system_state}). "
                "Set system_state to 'dynamic' in the configuration or set automatic=True."
            )

    def _define_conduit_into_spells(self, conduit: Conduit) -> None:
        """
        Internal

        Defines the newly created Conduit's ownership metadata into all locally
        bound spells and eagerly registers any **existing-object** spells into
        the Conduit's Creations manager as unique instances.

        Behavior
        --------
        For every local spell:

          1. Stamp ownership metadata:
               - spell._owner_conduit_id
               - spell._owner_conduit_name
               - spell._owner_creations  (points at conduit._creations)

          2. If the spell represents an existing object
             (``spell.user_created_object is not None``):

               - Treat it as an already-constructed singleton instance.
               - Register it immediately into the Conduit's Creations via
                 ``conduit._register_to_creations(spell, spell.user_created_object)``.

        This means that by the time the Conduit starts resolving spells,
        all existing-object spells are already present in the Creations store
        under their normal singleton semantics.
        """

        with self._lock:
            for spell in self._spells.values():
                try:
                    # 1) Stamp conduit ownership metadata on every spell
                    spell._add_owned_conduit(conduit._id, conduit._name, conduit._creations)

                    # 2) If this spell wraps an existing object, eagerly register it.
                    if spell.user_created_object is not None:
                        try:
                            conduit._register_to_creations(spell, spell.user_created_object)
                        except Exception as reg_err:
                            self._logger.error(
                                f"Failed to register existing creation for spell_id={spell.spell_id}: {reg_err}",
                                "_define_conduit_into_spells",
                                exc_info=True,
                            )

                except Exception as e:
                    self._logger.error(
                        f"Failed to define conduit into spell: {e}",
                        "_define_conduit_into_spells",
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

#endregion Conduit API

#region Hook Management
    def _get_conjure_hook_map(self) -> Optional[Mapping[str, List[Callable]]]:
        """
        Internal

        Fetch the Conduit lifecycle hook map for this Spellbook from the
        active Configuration, if the Configuration supports hook
        registration.

        Hooks are registered under this Spellbook's ID, and the map is
        shaped as:

            {
                "on_conduit_pre_created":   [callable, ...],
                "on_conduit_activated":     [callable, ...],
                "on_conduit_post_created":  [callable, ...],
                ...
            }

        Returns:
            Optional[Mapping[str, List[Callable]]]:
                The hook map if available and non-empty, otherwise None.
        """
        if self._configuration is None:
            return None

        try:
            hook_map = self._configuration.get_hooks(self._id)
        except AttributeError:
            return None
        except Exception as e:
            self._logger.error(
                f"_get_conjure_hook_map failed: {e}",
                "_get_conjure_hook_map",
                exc_info=True,
            )
            return None

        if not hook_map:
            return None

        return hook_map

    def _fire_conjure_hooks(
            self,
            hook_map: Optional[Mapping[str, List[Callable]]],
            hook_name: str,
            *args: Any,
    ) -> None:
        """
        Internal

        Execute all hooks registered under ``hook_name`` from the provided
        hook map. This is the Spellbook-side counterpart to Conduit's
        ``_fire_conduit_hooks``, but it is used only for the conjure
        lifecycle.

        Contract:

            - If ``hook_map`` is None or empty, this no-ops.
            - If ``hook_name`` is not present, this no-ops.
            - Each hook is invoked as: ``hook(*args)``.
            - Exceptions are logged and suppressed so hooks cannot break
              core conjuration behavior.

        For root conjuration, we follow this calling convention:

            - Pre  : _fire_conjure_hooks(hooks, "on_conduit_pre_created")
                     (no Conduit instance yet; hooks must not assume one)

            - Act  : _fire_conjure_hooks(hooks, "on_conduit_activated", conduit)

            - Post : _fire_conjure_hooks(hooks, "on_conduit_post_created", conduit)
        """
        if not hook_map:
            return

        hooks = hook_map.get(hook_name)
        if not hooks:
            return

        for hook in list(hooks):
            try:
                hook(*args)
            except Exception as e:
                self._logger.error(
                    f"Error while executing conjure hook '{hook_name}': {e}",
                    "_fire_conjure_hooks",
                    exc_info=True,
                )

#endregion Hook Management
#region Resolution Phases
    def _run_resolution_phases(self, conduit_id: str) -> Dict[str, Sequence['UnitOfWork']]:
        """
        Internal

        Convenience wrapper that runs structural phases (1-4) followed by
        conduit-scoped resolution phases (5-7).

        This is primarily a compatibility shim for callers that still expect
        a single orchestration method.

        Args:
            conduit_id:
                Conduit identifier used to scope resolution artifacts.
        Returns:
            Dict[str, Sequence[UnitOfWork]]:
                Mapping of phase name -> sequence of `UnitOfWork` instances.
        Raises:
            ValueError:
                If conduit_id is empty.
            SpellbookValidationError:
                If structural validation finds broken spells.
        """
        self.check_cleaned()
        if not conduit_id:
            raise ValueError("conduit_id must not be empty.")
        results: Dict[str, Sequence['UnitOfWork']] = {}
        results.update(self._run_structural_phases())
        results.update(self._run_resolution_phases_for_conduit(conduit_id))
        return results

    def _run_structural_phases(self) -> Dict[str, Sequence['UnitOfWork']]:
        """
        Internal

        Orchestrate Phases 1-4 (requirements, symbolic graph, local frame, validation).

        This method performs a hard validation barrier after Phase 4 and raises
        :class:`SpellbookValidationError` if any spell is broken.
        """
        self.check_cleaned()

        scheduler = PhaseScheduler(
            spellbook=self,
            configuration=self._configuration,
        )

        try:
            scheduler.register_phase(
                "requirements",
                lambda: self._phase_requirements_factory(scheduler),
            )
            scheduler.register_phase(
                "symbolic_graph",
                lambda: self._phase_symbolic_graph_factory(scheduler),
            )
            scheduler.register_phase(
                "local_frame",
                lambda: self._phase_local_frame_factory(scheduler),
            )
            scheduler.register_phase(
                "validation",
                lambda: self._phase_validation_factory(scheduler),
            )

            results = scheduler.run_all_phases()

            broken_spells: list[ISpell] = []
            for spell in self._spells.values():
                try:
                    if spell.is_broken:
                        broken_spells.append(spell)
                except Exception:
                    broken_spells.append(spell)

            if broken_spells:
                broken_spell_ids = [spell.spell_id for spell in broken_spells]
                broken_spell_names = [spell.spell_name for spell in broken_spells]
                self._logger.error(
                    "Spellbook structural pipeline completed with broken spells; "
                    f"raising SpellbookValidationError. "
                    f"broken_spell_ids={broken_spell_ids}, "
                    f"broken_spell_names={broken_spell_names}",
                    "_run_structural_phases",
                )
                raise SpellbookValidationError(broken_spells)

            return results
        finally:
            try:
                scheduler.cleanup()
            except Exception:
                self._logger.error(
                    "PhaseScheduler.cleanup() raised during _run_structural_phases",
                    "_run_structural_phases",
                    exc_info=True,
                )

    def _run_post_conjure_structural_phases(self, spells: Sequence[ISpell]) -> None:
        """
        Internal

        Run Phases 1-4 for newly bound spells after conjure.

        Args:
            spells: Newly bound spells that require structural phases.
        Returns:
            None.
        Raises:
            SpellbookValidationError: If any of the new spells validate as broken.
            Exception: Propagates structural phase errors.
        """
        self.check_cleaned()
        if not spells:
            return

        cancel_signal = CancellationEventSignal()
        cancel_event = cancel_signal.event
        try:
            for spell in spells:
                spell.run_structural_phases(cancel_event=cancel_event)

            broken_spells: list[ISpell] = []
            for spell in spells:
                try:
                    if spell.is_broken:
                        broken_spells.append(spell)
                except Exception:
                    broken_spells.append(spell)

            if broken_spells:
                broken_spell_ids = [spell.spell_id for spell in broken_spells]
                broken_spell_names = [spell.spell_name for spell in broken_spells]
                self._logger.error(
                    "Post-conjure structural pipeline completed with broken spells; "
                    f"raising SpellbookValidationError. "
                    f"broken_spell_ids={broken_spell_ids}, "
                    f"broken_spell_names={broken_spell_names}",
                    "_run_post_conjure_structural_phases",
                )
                raise SpellbookValidationError(broken_spells)
        except Exception as exc:
            try:
                cancel_signal.cancel()
            except Exception:
                pass
            self._logger.error(
                f"Post-conjure structural phase execution failed: {exc}",
                "_run_post_conjure_structural_phases",
                exc_info=True,
            )
            raise
        finally:
            try:
                cancel_signal.cleanup()
            except Exception:
                self._logger.error(
                    "CancellationEventSignal.cleanup() raised during post-conjure structural phases",
                    "_run_post_conjure_structural_phases",
                    exc_info=True,
                )

    def _run_resolution_phases_for_conduit(
            self,
            conduit_id: str,
    ) -> Dict[str, Sequence['UnitOfWork']]:
        """
        Internal

        Orchestrate conduit-scoped Phases 5-7 (root blueprints, system validation,
        change control). This must run after structural phases complete.

        Args:
            conduit_id:
                Conduit identifier used to scope resolution artifacts.
        Returns:
            Dict[str, Sequence[UnitOfWork]]:
                Mapping of phase name -> sequence of `UnitOfWork` instances.
        Raises:
            ValueError:
                If conduit_id is empty.
        Notes:
            After Phase 7 completes, per-spell phase artifacts are cleaned.
        """
        self.check_cleaned()
        if not conduit_id:
            raise ValueError("conduit_id must not be empty.")

        scheduler = PhaseScheduler(
            spellbook=self,
            configuration=self._configuration,
        )

        try:
            scheduler.register_phase(
                "root_blueprints",
                lambda: self._phase_root_blueprints_factory(scheduler, conduit_id),
            )
            scheduler.register_phase(
                "system_validation",
                lambda: self._phase_system_validation_factory(scheduler, conduit_id),
            )
            scheduler.register_phase(
                "change_control",
                lambda: self._phase_change_control_factory(scheduler, conduit_id),
            )

            results = scheduler.run_all_phases()
            self._cleanup_phase_artifacts_after_resolution()
            return results
        finally:
            try:
                scheduler.cleanup()
            except Exception:
                self._logger.error(
                    "PhaseScheduler.cleanup() raised during _run_resolution_phases_for_conduit",
                    "_run_resolution_phases_for_conduit",
                    exc_info=True,
                )
    #endregion

    def _cleanup_phase_artifacts_after_resolution(self) -> None:
        """
        Internal

        Clean per-spell phase artifacts after conduit-scoped phases complete.
        """
        self.check_cleaned()
        for spell in self._spells.values():
            crafter = getattr(spell, "_crafter", None)
            if crafter is None:
                continue
            try:
                crafter.cleanup_phase_artifacts()
            except Exception:
                # Cleanup should not disrupt conjure/resolve flows.
                pass

    def _phase_requirements_factory(self, scheduler: PhaseScheduler) -> Sequence['UnitOfWork']:
        """
        Internal

        Build :class:`UnitOfWork` instances for the **requirements** phase.

        Each local spell gets one unit of work that is responsible for:
            * Performing static requirement checks.
            * Registering dependency edges.
            * Emitting any metadata needed by later phases.

        The underlying spell method is expected to be:

            ``spell.run_phase_requirements(cancel_event: CancellationEvent) -> Any``

        where the spell cooperatively honours the shared CancellationEvent
        attached via the scheduler.
        """
        self.check_cleaned()
        units: List['UnitOfWork'] = []

        for spell in self._spells.values():
            units.append(
                scheduler.create_unit_of_work(
                    func=spell.run_phase_requirements,
                    args=(scheduler.cancel_event,),
                    label=f"requirements:{spell.spell_id}",
                    metadata={
                        "phase": "requirements",
                        "spell_id": spell.spell_id,
                    },
                )
            )

        return units

    def _phase_symbolic_graph_factory(self, scheduler: PhaseScheduler) -> Sequence['UnitOfWork']:
        """
        Internal

        Build :class:`UnitOfWork` instances for the **symbolic_graph** phase.

        Each spell contributes its own symbolic graph representation – a
        spell-local structural view that captures parameters, dependencies,
        and internal resolution semantics without yet forming a global DAG.

        Expected spell surface:

            ``spell.run_phase_symbolic_graph(cancel_event: CancellationEvent) -> Any``
        """
        self.check_cleaned()
        units: List['UnitOfWork'] = []

        for spell in self._spells.values():
            units.append(
                scheduler.create_unit_of_work(
                    func=spell.run_phase_symbolic_graph,
                    args=(scheduler.cancel_event,),
                    label=f"symbolic_graph:{spell.spell_id}",
                    metadata={
                        "phase": "symbolic_graph",
                        "spell_id": spell.spell_id,
                    },
                )
            )

        return units

    def _phase_local_frame_factory(self, scheduler: PhaseScheduler) -> Sequence['UnitOfWork']:
        """
        Internal

        Build :class:`UnitOfWork` instances for the **local_frame** phase.

        This phase is responsible for constructing per-spell execution frames
        (resolution frames, local DAG fragments, etc.) that can later be
        combined into deeper, cross-spell structures.

        Expected spell surface:

            ``spell.run_phase_local_frame(cancel_event: CancellationEvent) -> Any``
        """
        self.check_cleaned()
        units: List['UnitOfWork'] = []

        for spell in self._spells.values():
            units.append(
                scheduler.create_unit_of_work(
                    func=spell.run_phase_local_frame,
                    args=(scheduler.cancel_event,),
                    label=f"local_frame:{spell.spell_id}",
                    metadata={
                        "phase": "local_frame",
                        "spell_id": spell.spell_id,
                    },
                )
            )

        return units

    def _phase_validation_factory(self, scheduler: PhaseScheduler) -> Sequence['UnitOfWork']:
        """
        Internal

        Build :class:`UnitOfWork` instances for the **validation** phase.

        This is the final Spell-level validation pass that runs after
        requirements, symbolic graphs, and local frames have been built.

        Typical responsibilities:
            * Cross-check that required dependencies were satisfied.
            * Ensure frames/graphs are internally consistent.
            * Surface any final Spell-level errors before conjuration.

        Expected spell surface:

            ``spell.run_phase_validation(cancel_event: CancellationEvent) -> Any``
        """
        self.check_cleaned()
        units: List['UnitOfWork'] = []

        for spell in self._spells.values():
            units.append(
                scheduler.create_unit_of_work(
                    func=spell.run_phase_validation,
                    args=(scheduler.cancel_event,),
                    label=f"validation:{spell.spell_id}",
                    metadata={
                        "phase": "validation",
                        "spell_id": spell.spell_id,
                    },
                )
            )

        return units

    def _phase_root_blueprints_factory(
            self,
            scheduler: PhaseScheduler,
            conduit_id: str,
    ) -> Sequence['UnitOfWork']:
        """
        Internal

        Build :class:`UnitOfWork` instances for the **root_blueprints** phase.

        This phase is frame-level and must run after Phase 4. We schedule
        a unit of work for each local spell so that each spell's crafter
        receives the frame-level artifacts.

        Expected spell surface:

            ``spell.run_phase_root_blueprints(conduit_id, cancel_event: CancellationEvent) -> Any``
        """
        self.check_cleaned()
        if not self._spells:
            return []

        units: List['UnitOfWork'] = []
        for spell in self._spells.values():
            units.append(
                scheduler.create_unit_of_work(
                    func=spell.run_phase_root_blueprints,
                    args=(conduit_id, scheduler.cancel_event,),
                    label=f"root_blueprints:{spell.spell_id}",
                    metadata={
                        "phase": "root_blueprints",
                        "spell_id": spell.spell_id,
                    },
                )
            )
        return units

    def _phase_system_validation_factory(
            self,
            scheduler: PhaseScheduler,
            conduit_id: str,
    ) -> Sequence['UnitOfWork']:
        """
        Internal

        Build :class:`UnitOfWork` instances for the **system_validation** phase.

        This phase validates the system-level DAG for the frame and runs
        after Phase 5 artifacts have been constructed. We schedule work
        for every local spell to keep per-spell validation state aligned.

        Expected spell surface:

            ``spell.run_phase_system_validation(conduit_id, cancel_event: CancellationEvent) -> Any``
        """
        self.check_cleaned()
        if not self._spells:
            return []

        units: List['UnitOfWork'] = []
        for spell in self._spells.values():
            units.append(
                scheduler.create_unit_of_work(
                    func=spell.run_phase_system_validation,
                    args=(conduit_id, scheduler.cancel_event,),
                    label=f"system_validation:{spell.spell_id}",
                    metadata={
                        "phase": "system_validation",
                        "spell_id": spell.spell_id,
                    },
                )
            )
        return units

    def _phase_change_control_factory(
            self,
            scheduler: PhaseScheduler,
            conduit_id: str,
    ) -> Sequence['UnitOfWork']:
        """
        Internal

        Build :class:`UnitOfWork` instances for the **change_control** phase.

        This phase wires change-control hooks and component-of indices for
        the frame once Phase 5 artifacts exist. We schedule work for every
        local spell to keep per-spell wiring consistent.

        Expected spell surface:

            ``spell.run_phase_change_control(conduit_id, cancel_event: CancellationEvent) -> Any``
        """
        self.check_cleaned()
        if not self._spells:
            return []

        units: List['UnitOfWork'] = []
        for spell in self._spells.values():
            units.append(
                scheduler.create_unit_of_work(
                    func=spell.run_phase_change_control,
                    args=(conduit_id, scheduler.cancel_event,),
                    label=f"change_control:{spell.spell_id}",
                    metadata={
                        "phase": "change_control",
                        "spell_id": spell.spell_id,
                    },
                )
            )
        return units
#endregion

#endregion Resolution Phases
#endregion
