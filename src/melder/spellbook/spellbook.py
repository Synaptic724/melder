from types import MappingProxyType
from typing import Optional, List, Any, Mapping, Callable
import threading

# Melder Imports
from melder.aether.aether import Aether
from melder.spellbook.bind.spell_index import SpellIndex
from melder.spellbook.configuration.system_state import SystemState
from melder.spellbook.spellbinder import SpellBinder
from melder.utilities.data_structures.concurrent_set import ConcurrentSet
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.interfaces.interfaces import ISpellbook, ISpell, IConfiguration, ISpellIndex
from melder.utilities.data_structures.concurrent_dict import ConcurrentDict
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

     By default, setting (aetheric_frame=None) will generate a unique, isolated frame.
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
        configuration (Optional[Configuration]):
            An optional pre-configured `Configuration` instance to use, typically provided
            when creating a Spellbook for an existing Aether frame.

    Notes:
        * You may only conjure one conduit per spellbook instance.
        * Configuration is locked automatically upon conjuring.
        * If configuration is already shared via an Aether frame, it will be reused.
    """
    _aether = Aether()
    def __init__(self, aetheric_frame: str = "default", configuration: Optional[IConfiguration] = None,
                 logger: Any | None = None):
        super().__init__()

        # Internal state
        self._lock: threading.RLock = threading.RLock()
        self._id: str = IDBuilder.create_id()
        self._conjured = False
        self._conduit: Optional[Conduit] = None
        self._aetheric_frame = aetheric_frame
        if not isinstance(self._aetheric_frame, str):
            raise TypeError(f"aetheric_frame must be a string, got {type(self._aetheric_frame).__name__}")

        # Configuration state
        self._configuration_locked: bool = False
        self._configuration: IConfiguration = configuration
        self._initialize_configuration()

        # Logger setup
        self._initialize_logging(logger)

        # Core spell storage (SpellIndex Maps)
        self._spells: ConcurrentDict[SpellIndex, ISpell] = ConcurrentDict()
        self._spell_versions: ConcurrentSet[str] = ConcurrentSet()
        self._lookup_spells: ConcurrentDict[tuple, SpellIndex]  = ConcurrentDict()

        # Networked/remote spell support
        # This stores spells borrowed from other conduits (keyed by peer Conduit id)
        self._contracted_spells: ConcurrentDict[str, ConcurrentDict[SpellIndex, ISpell]] = ConcurrentDict()
        self._contracted_versions: ConcurrentDict[str, ConcurrentSet[str]] = ConcurrentDict()
        self._lookup_contracted_spells: ConcurrentDict[str, ConcurrentDict[tuple, SpellIndex]]  = ConcurrentDict()

        # Binding system
        self._bind: Bind = Bind()


    #region Disposal

    def cleanup(self) -> None:
        self._logger.debug("Cleaning Spellbook", "cleanup")

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

        # 2) Clean lookup/contracted maps and local maps
        if self._lookup_spells is not None:
            try:
                self._lookup_spells.cleanup()
            except Exception as e:
                self._logger.error(f"Error cleaning _lookup_spells: {e}", "_cleanup_components", exc_info=True)
            self._lookup_spells = None

        if self._contracted_spells is not None:
            try:
                self._contracted_spells.cleanup()
            except Exception as e:
                self._logger.error(f"Error cleaning _contracted_spells: {e}", "_cleanup_components", exc_info=True)
            self._contracted_spells = None

        if self._lookup_contracted_spells is not None:
            try:
                self._lookup_contracted_spells.cleanup()
            except Exception as e:
                self._logger.error(f"Error cleaning _lookup_contracted_spells: {e}", "_cleanup_components", exc_info=True)
            self._lookup_contracted_spells = None

        if self._spells is not None:
            try:
                self._spells.cleanup()
            except Exception as e:
                self._logger.error(f"Error cleaning _spells: {e}", "_cleanup_components", exc_info=True)
            self._spells = None

        # 3) cleanup configuration
        if self._configuration is not None:
            self._logger.debug("Cleaning configuration", "_cleanup_components")
            try:
                self._configuration.cleanup()
            except Exception as e:
                self._logger.error(f"Error cleaning configuration: {e}", "_cleanup_components", exc_info=True)
            self._configuration = None

        if self._spell_versions is not None:
            try:
                self._spell_versions.cleanup()
            except Exception as e:
                self._logger.error(f"Error cleaning _spell_versions: {e}", "_cleanup_components", exc_info=True)
            self._spell_versions = None

        if self._contracted_versions is not None:
            try:
                self._contracted_versions.cleanup()
            except Exception as e:
                self._logger.error(f"Error cleaning _contracted_versions: {e}", "_cleanup_components", exc_info=True)
            self._contracted_versions = None

        self._logger.debug("Spellbook component cleanup complete", "_cleanup_components")

    def _cleanup_spells(self) -> None:
        if self._spells is None:
            return

        items = list(self._spells.items())
        for spell_id, spell in items:
            self._logger.debug(f"Cleaning local spell '{spell_id}'", "_cleanup_spells")
            try:
                spell.cleanup()
            except Exception as e:
                self._logger.error(f"Error cleaning spell '{spell_id}': {e}", "_cleanup_spells", exc_info=True)


    # -------------------------
    # Phase 2: Core teardown (after lock)
    # -------------------------

    def _cleanup_core(self) -> None:
        self._logger.debug("Final teardown: nullifying references and disposing logger", "_cleanup_core")

        # Nullify high-level refs (no try/catch for simple None assignments)
        self._bind = None
        self._aetheric_frame = None
        self._id = None
        self._conduit = None
        self._conjured = None
        self._configuration_locked = None

        # Lock: just null it (no getattr/hasattr)
        self._lock = None

        # Destroy logger LAST
        if self._logger is not None:
            try:
                self._logger.debug("Cleaning logger", "_cleanup_core")
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
        self._logger.debug("Refreshing local spell version cache", "_refresh_local_spell_versions")

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
        self._logger.debug("Refreshing contracted spell version caches", "_refresh_contracted_sp_versions")

        with self._lock:
            if self._contracted_spells is None or self._contracted_versions is None:
                return

            # Blow away old caches and rebuild them from scratch
            self._contracted_versions.clear()

            for conduit_id, spell_map in self._contracted_spells.items():
                version_set = ConcurrentSet[str]()
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
        self._logger.debug("Refreshing all spell version caches", "_refresh_all_spell_versions")
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
            self._logger.debug(f"Spellbook[{self._id}] logger initialized", "_initialize_logging")
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
            if getattr(aether, "_logger", None) is not None and getattr(aether._logger, "_logger", None) is None:
                aether_logger = cfg.get_logger_for(aether)
                aether._logger = InitHelpers.resolve_safe_logger(aether_logger)
                self._logger.debug("Upgraded Aether logger from null to real", "_upgrade_aether_logger_if_possible")
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
        self._logger.debug(
            f"get_spell_permissions(spell_index={spell_index})",
            "get_spell_permissions",
        )
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
        self._logger.debug(f"_find_spell({spell_index}) -> {spell is not None}", "_find_spell")
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
        self._logger.debug(f"_find_contracted_spell({spell_index})", "_find_contracted_spell")
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
        self._logger.debug(f"_find_spell_count -> {count}", "_find_spell_count")
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
        self._logger.debug(f"_find_contracted_spell_count -> {count}", "_find_contracted_spell_count")
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
        self._logger.debug(
            f"find_spell_id(frame={spellframe}, name={spell_name}, bind={binding_name})",
            "find_spell_id",
        )
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
        self._logger.debug(f"_make_spell_key -> {(frame_key, bind_key)}", "_make_spell_key")
        return frame_key, bind_key

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
        self._logger.debug(f"find_spell_key(frame={spellframe}, name={spell_name}, bind={binding_name})", "find_spell_key")
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
        self._logger.debug("inspect_spell()", "inspect_spell")
        with self._lock:
            try:
                spell_id = self._bind.spell_id_inspector(spell)
                found = Spellbook._aether._check_for_spell(spell_id, aetheric_frame)
                self._logger.debug(f"inspect_spell -> id={spell_id}, registered={found}", "inspect_spell")
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
        self._logger.debug("Verifying local spells are not already in Aether", "_check_all_spells")
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
        self._logger.debug(
            f"_find_contracted_spell_by_id(spell_id={spell_id}, conduit_id={conduit_id})",
            "_find_contracted_spell_by_id",
        )

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
        self._logger.debug(f"_create_link_contract(conduit_id={conduit_id})", "_create_link_contract")

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
                self._contracted_spells[conduit_id] = ConcurrentDict()
                self._lookup_contracted_spells[conduit_id] = ConcurrentDict()
                self._contracted_versions[conduit_id] = ConcurrentSet()


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
        self._logger.debug(f"_remove_link_contract(conduit_id={conduit_id})", "_remove_link_contract")

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

        Args:
            spell (ISpell): The spell object to add.
            conduit_id (str): The ID of the peer conduit the spell was contracted from.
        """
        self._logger.debug(
            f"_add_contracted_spell(spell_id={spell.spell_id}, conduit_id={conduit_id})",
            "_add_contracted_spell",
        )

        with self._lock:
            if conduit_id not in self._contracted_spells:
                self._create_link_contract(conduit_id)

            spell_key = self._make_spell_key(spell.spellframe, spell.spell_name, spell.binding_name)

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


    def _remove_contracted_spell(self, spell_id: str, conduit_id: str) -> None:
        """
        Internal

        Removes a specific contracted spell from the internal registry.

        Args:
            spell_id (str): The version SHA of the spell to remove.
            conduit_id (str): The ID of the peer conduit the spell was contracted from.
        """
        self._logger.debug(
            f"_remove_contracted_spell(spell_id={spell_id}, conduit_id={conduit_id})",
            "_remove_contracted_spell",
        )

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


    def _clear_contracted_spells_for_conduit(self, conduit_id: str) -> None:
        """
        Internal

        Clears all spells associated with a contracted conduit, retaining
        the contract structure and zeroing the version cache.

        Args:
            conduit_id (str): The ID of the peer conduit whose contracted spells are to be cleared
        """
        self._logger.debug(
            f"_clear_contracted_spells_for_conduit(conduit_id={conduit_id})",
            "_clear_contracted_spells_for_conduit",
        )

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


    def _sever_link_contract(self, conduit_id: str) -> None:
        """
        Internal

        Sever the link contract for a given conduit ID by removing all
        contracted spells and the contract structure itself.

        Args:
            conduit_id (str): The ID of the peer conduit whose contract is to be severed
        """
        self._logger.debug(
            f"_sever_link_contract(conduit_id={conduit_id})",
            "_sever_link_contract",
        )

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

    def bind(
            self,
            *,
            spell,
            existence: str,
            permissions: str = "create",
            spellframe=None,
            binding_name=None,
            **kwargs,
    ) -> str:
        """
        Binds a spell into the Spellbook for future instantiation and dependency injection.

        The `bind()` method registers a class, function, or object into Melder’s system,
        associating it with a lifecycle (`Existence`), a permission policy, and optional metadata.
        Once bound, the spell becomes available for resolution and casting within its conduit
        or across systems (depending on permissions).

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
            RuntimeError: If the Conduit is not a 'normal' conduit (only normal conduits can bind spells).
            RuntimeError: If the spell is already bound in the registry.
            TypeError: If invalid hook types are provided.
        """
        self._logger.debug("bind()", "bind")
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
                self._logger.error(f"Spell with ID {new_spell.spell_id} already exists in the registry.", "bind", exc_info=True)
                raise RuntimeError(f"Spell with ID {new_spell.spell_id} already exists in the registry.")
            self._add_hooks_to_spell(new_spell, **kwargs)
            self._lookup_spells[new_spell._key] = new_spell.spell_index
            self._spells[new_spell.spell_index] = new_spell

            # keep local version cache warm
            if self._spell_versions is not None:
                # At minimum track the primary id; if SpellIndex already has a versions list, use that.
                versions = new_spell.spell_index._versions
                if versions:
                    for vid in versions:
                        self._spell_versions.add(vid)
                else:
                    self._spell_versions.add(new_spell.spell_id)

            if self._conjured:
                self._conduit._register_to_creations(new_spell, new_spell.user_created_object)

            self._logger.debug(f"Binding spell => id={new_spell.spell_id}, key={new_spell._key}", "bind")
            return new_spell.spell_id
        except Exception as e:
            self._logger.error(f"Error while binding spell: {e}", "bind", exc_info=True)
            raise

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
        self._logger.debug(f"_add_hooks_to_spell(id={getattr(spell, 'spell_id', 'N/A')})", "_add_hooks_to_spell")
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
        self._logger.debug("Hooks attached", "_add_hooks_to_spell")

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
                    self._logger.error("Aether configuration does not match provided configuration", "_initialize_configuration", exc_info=True)
                    raise RuntimeError("Aether configuration does not match the provided configuration.")
                self._configuration = aether_config
                self._configuration_locked = True
                self._logger.debug("Adopted configuration from Aether (locked=True)", "_initialize_configuration")
                return

            if self._configuration is not None:
                if self._configuration._aether_frame != self._aetheric_frame:
                    self._logger.error("Configuration name does not match the aetheric frame", "_initialize_configuration", exc_info=True)
                    raise RuntimeError("Configuration name does not match the aetheric frame.")
                self._configuration_locked = False
                self._logger.debug("Using provided configuration (locked=False)", "_initialize_configuration")
                return

            self._configuration = Configuration(self._aetheric_frame)
            self._configuration_locked = False
            self._logger.debug("Created new Configuration (locked=False)", "_initialize_configuration")
        except Exception as e:
            self._logger.error(f"Failed to initialize configuration: {e}", "_initialize_configuration", exc_info=True)
            raise


    def _get_configuration_from_aether(self) -> IConfiguration | None:
        """
        Internal

        Retrieves the current configuration from the Aether's global registry.

        Returns:
            IConfiguration | None: The configuration instance for this Aether frame, or None if not registered.
        """
        try:
            cfg = Spellbook._aether._get_configuration(self._aetheric_frame)
            self._logger.debug(f"Retrieved configuration for frame '{self._aetheric_frame}'", "_get_configuration_from_aether")
            return cfg
        except Exception as e:
            self._logger.error(f"Error retrieving configuration from Aether: {e}", "_get_configuration_from_aether", exc_info=True)
            raise

    def is_configuration_locked(self) -> bool:
        """
        Public API

        Checks whether the spellbook's configuration is currently locked (frozen) or not.

        Returns:
            bool: True if the configuration is locked, False otherwise.
        """
        self._logger.debug(f"is_configuration_locked -> {self._configuration_locked}", "is_configuration_locked")
        return self._configuration_locked


    def configure_aether_frame(
            self,
            *,
            system_state: Optional[str],
            debugging: Optional[bool],
            disposal: Optional[bool],
            disposal_method_names: Optional[List[str]],
            logger_factory: Optional[Callable[[object], Any]] = None,
            use_default_std_logger: bool = False,
    ) -> None:
        """
        Public API

        Consolidated setup for this Spellbook's **Aether frame**:

          1. (Optional) Install a logger factory on the configuration.
          2. Apply provided configuration properties.
          3. Validate + freeze configuration.
          4. Bind the configuration to the Aether.
          5. Optionally upgrade the Aether logger.

        Once frozen during this call, the configuration becomes
        immutable.

        Args:
            system_state:
                System mode (e.g. ``"automatic"`` or ``"dynamic"``).
            debugging:
                Enables or disables internal debugging features such as
                id tagging.
            disposal:
                Enables automatic resource disposal when conduits are
                cleaned.
            disposal_method_names:
                Method names to invoke on created objects during
                disposal.
            logger_factory:
                Optional logger factory to install before freezing.
            use_default_std_logger:
                If True and `logger_factory` is not provided, installs
                the default StdLoggerFactory via `set_logger_factory()`.

        Raises:
            RuntimeError:
                If configuration is already locked/cleaned.
            KeyError:
                If an unknown configuration key is provided.
            ValueError:
                If configuration fails validation.
            TypeError:
                If the provided logger factory is invalid.
        """
        if self._configuration_locked:
            self._logger.error("Configuration is locked. Cannot modify conduit state.", "configure_aether_frame", exc_info=True)
            raise RuntimeError("Configuration is locked. Cannot modify conduit state.")
        self._logger.debug("Configuring Aether frame (pre-freeze)", "configure_aether_frame")
        try:
            self._maybe_install_logger_factory(logger_factory, use_default_std_logger)
            self._apply_configuration_properties(
                system_state=system_state,
                debugging=debugging,
                disposal=disposal,
                disposal_method_names=disposal_method_names,
            )
            self._validate_and_freeze_configuration()
            self._bind_configuration_to_aether()
            self._upgrade_aether_logger_if_possible()
            self._logger.debug(f"Configuration bound and frozen for frame '{self._aetheric_frame}'", "configure_aether_frame")
        except (KeyError, ValueError) as e:
            try:
                self._configuration.clear_properties()
                self._logger.debug("Reverted configuration properties after failure", "configure_aether_frame")
            except Exception as ce:
                self._logger.error(f"Failed to revert configuration after error: {ce}", "configure_aether_frame", exc_info=True)
            self._logger.error(f"Configuration error: {e}", "configure_aether_frame", exc_info=True)
            raise
        except Exception as e:
            self._logger.error(f"Unexpected error configuring Aether frame: {e}", "configure_aether_frame", exc_info=True)
            raise


    def _maybe_install_logger_factory(
            self,
            logger_factory: Optional[Callable[[object], Any]],
            use_default_std_logger: bool,
    ) -> None:
        """
        Internal

        Installs a logger factory onto the configuration (pre-freeze) if requested.

        Priority:
          - If `logger_factory` provided, use it.
          - Else, if `use_default_std_logger` is True, call `set_logger_factory()`
            which uses the StdLoggerFactory() default from the Configuration API.
          - Else, do nothing (silent logging).
        """
        cfg = self._configuration
        try:
            if logger_factory is not None:
                self._logger.debug("Installing explicit logger factory on configuration", "_maybe_install_logger_factory")
                cfg.set_logger_factory(logger_factory)
            elif use_default_std_logger:
                self._logger.debug("Installing default StdLoggerFactory on configuration", "_maybe_install_logger_factory")
                cfg.set_logger_factory()
        except Exception as e:
            self._logger.error(f"Failed to install logger factory: {e}", "_maybe_install_logger_factory", exc_info=True)
            raise


    def _apply_configuration_properties(
            self,
            *,
            system_state: Optional[str],
            debugging: Optional[bool],
            disposal: Optional[bool],
            disposal_method_names: Optional[List[str]],
    ) -> None:
        """
        Internal

        Applies only the provided properties to the configuration (pre-freeze).
        Enforces allowed keys using the configuration's `available_properties`.
        """
        cfg = self._configuration
        kwargs = {
            k: v for k, v in {
                "system_state": system_state,
                "debugging": debugging,
                "disposal": disposal,
                "disposal_method_names": disposal_method_names,
            }.items() if v is not None
        }
        self._logger.debug(f"Applying configuration properties: {list(kwargs.keys())}", "_apply_configuration_properties")
        for key, value in kwargs.items():
            if key not in cfg.available_properties:
                self._logger.error(f"Unknown configuration key '{key}'", "_apply_configuration_properties", exc_info=True)
                raise KeyError(
                    f"Unknown configuration key '{key}'. Allowed keys are: {list(cfg.available_properties.keys())}"
                )
            cfg.set_property(key, value)

    def _validate_and_freeze_configuration(self) -> None:
        """
        Internal

        Validates configuration, then freezes it (no further mutation allowed).
        Sets `_configuration_locked` upon success.

        Raises:
            ValueError: If validation fails.
        """
        cfg = self._configuration
        try:
            self._logger.debug("Validating configuration", "_validate_and_freeze_configuration")
            if not cfg.validate():
                self._logger.error("Configuration validation failed", "_validate_and_freeze_configuration", exc_info=True)
                raise ValueError("Invalid configuration. Please check your settings.")
            cfg.freeze()
            self._configuration_locked = True
            self._logger.debug("Configuration frozen (locked=True)", "_validate_and_freeze_configuration")
        except Exception:
            # Roll back property changes to avoid leaving a broken state around
            try:
                cfg.clear_properties()
            except Exception:
                # best-effort; if this fails, let original error surface
                pass
            raise


    def _bind_configuration_to_aether(self) -> None:
        """
        Internal

        Binds the now-frozen configuration to the Aether for this Spellbook's frame.
        """
        try:
            Spellbook._aether._bind_configuration(self._configuration, self._aetheric_frame)
            self._logger.debug(f"Bound configuration to Aether frame '{self._aetheric_frame}'", "_bind_configuration_to_aether")
        except Exception as e:
            self._logger.error(f"Failed to bind configuration to Aether: {e}", "_bind_configuration_to_aether", exc_info=True)
            raise


    def get_configuration(self) -> IConfiguration:
        """
        Public API

        Returns the active configuration object for this Spellbook.

        Returns:
            Configuration: The configuration instance.
        """
        self._logger.debug("get_configuration()", "get_configuration")
        return self._configuration

    #endregion Configuration API
    #region Conduit API

    def create_new_preset_spellbook(self) -> ISpellbook:
        """
        Internal

        Creates a new `Spellbook` instance that shares the configuration and Aether frame of the current Spellbook.

        This is used internally when upgrading a lesser conduit's spellbook to a normal conduit spellbook.

        Returns:
            Spellbook: A new Spellbook instance ready for use by a normal conduit.
        """
        return Spellbook(self._aetheric_frame, self._configuration)


    def conjure(self, policy: Optional[str] = "automatic", name: str = None, conduit_logger: Any | None = None) -> Conduit:
        """
        Public API

        Creates a new **Conduit** (execution channel) from this Spellbook.

        This method finalizes the configuration, validates all local spells, and instantiates the `Conduit`.

        Args:
            policy (str, optional):
                Determines the spell access control behavior for this conduit. Must match a `Policies` enum member.
                Defaults to "automatic".
            name (str, optional):
                An optional name for the conduit.
            conduit_logger (Any, optional):
                An optional logger instance to attach to the conduit for logging purposes.

        Returns:
            Conduit: The newly created Conduit instance.

        Raises:
            RuntimeError: If this Spellbook has already conjured a Conduit (only one is allowed).
            RuntimeError: If dynamic policies are used when `system_state` is "automatic".
            ValueError: If the configuration fails validation or the policy string is invalid.

        Policies:
            - **Automatic Mode** (default policy is `automatic`):
                * `"automatic"`: Delegates access checks, disables linking.
            - **Dynamic Mode** (requires `system_state: "dynamic"`):
                * `"dynamic"`: Enables custom linking and access resolution.
                * `"whitelist_all"`: Grants access to all local spells.
                * `"block_all"`: Denies access to all spells unless explicitly whitelisted.

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
        self._logger.debug(f"Conjuring Conduit(name={name}, policy={policy})", "conjure")

        with self._lock:
            if self._conjured:
                self._logger.error("This Spellbook has already conjured a Conduit.", "conjure", exc_info=True)
                raise RuntimeError("This Spellbook has already conjured a Conduit. Only one is allowed per Spellbook.")

            # Ensure configuration is frozen and bound to Aether
            if not self.is_configuration_locked():
                self._configuration.load_default_dictionary()
                self._configuration.freeze()
                self._configuration_locked = True
                Spellbook._aether._bind_configuration(self._configuration, self._aetheric_frame)
                self._logger.debug("Configuration locked (defaults applied)", "conjure")

            # Validate policy vs system_state and local spell registry
            self._check_system_state(policy)
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
                logger=conduit_logger,
            )

            # Mark this Spellbook as having conjured its single conduit
            self._conjured = True
            self._conduit = conduit
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

            self._logger.debug(f"Conduit created => id={conduit._id}, name={conduit._name}", "conjure")
            return conduit


    def _check_system_state(self, policy: str) -> None:
        """
        Internal

        Checks if the requested policy is compatible with the current `system_state` configuration.

        Args:
            policy (str): The policy requested for the new Conduit.

        Raises:
            RuntimeError: If a dynamic policy is requested while `system_state` is set to "automatic".
        """
        self._logger.debug("Checking system_state vs policy", "_check_system_state")
        if (self._configuration.get_property("system_state") == SystemState.automatic and
                EnumHelpers.convert_enum_and_check(policy, Policies) != Policies.automatic):
            self._logger.error("Cannot use dynamic policies in automatic mode.", "_check_system_state", exc_info=True)
            raise RuntimeError(
                "Cannot use dynamic policies in automatic mode. "
                "Please set system_state to 'dynamic' in the configuration."
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
        self._logger.debug(
            "Linking conduit metadata into local spells (and priming existing creations)",
            "_define_conduit_into_spells",
        )

        with self._lock:
            for spell in self._spells.values():
                try:
                    # 1) Stamp conduit ownership metadata on every spell
                    spell._add_owned_conduit(conduit._id, conduit._name, conduit._creations)

                    # 2) If this spell wraps an existing object, eagerly register it.
                    if spell.user_created_object is not None:
                        try:
                            conduit._register_to_creations(spell, spell.user_created_object)
                            self._logger.debug(
                                f"Primed existing creation for spell_id={spell.spell_id}",
                                "_define_conduit_into_spells",
                            )
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
            self._logger.debug(
                "_get_conjure_hook_map: no configuration; skipping conjure hooks",
                "_get_conjure_hook_map",
            )
            return None

        # Configuration may not yet support hooks.
        if self._configuration.get_hooks(self._id):
            self._logger.debug(
                "_get_conjure_hook_map: configuration has no get_hooks(spellbook_id); "
                "skipping conjure hooks",
                "_get_conjure_hook_map",
            )
            return None

        try:
            hook_map = self._configuration.get_hooks(self._id)
        except Exception as e:
            self._logger.error(
                f"_get_conjure_hook_map failed: {e}",
                "_get_conjure_hook_map",
                exc_info=True,
            )
            return None

        if not hook_map:
            self._logger.debug(
                f"_get_conjure_hook_map: no hooks registered for spellbook_id={self._id}; "
                "nothing to attach for conjure.",
                "_get_conjure_hook_map",
            )
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
#endregion