from threading import RLock
from typing import List, Optional, Dict, Any

# Melder imports
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.interfaces import IConduit, ICreations
from melder.aether.conduit.creations.creation import Creation
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

#TODO: Create a creations object to encapsulate the objects under my control.

class Creations(Cleanable, ICreations):
    """
    Manages all instantiated objects within a Conduit (Normal Scope).

    This manager is responsible for tracking object instances based on their lifecycle
    (`unique`, `unique_per_scope`, `many`, etc.) and enforcing resource disposal upon cleaning.

    **Key Responsibilities:**
      * Storage and lifecycle management of created objects.
      * Controlled resource disposal via `ICleanable` or configured cleanup methods.
    """
    __melder_internal__ = _mrg.sentinel
    def __init__(self, disposal_enabled: bool, disposal_method_names: List[str], conduit: IConduit):
        """
        Initialize a new Creations manager.

        Args:
            disposal_enabled (bool): Whether disposal behavior is active.
            disposal_method_names (List[str]): List of method names to attempt during cleanup.

        The internal dictionaries hold references to the objects created by the conduit,
        indexed by the spell's unique ID (`str`).
        """
        super().__init__()
        self._conduit: IConduit = conduit
        self._id: str = conduit._id

        if conduit._conduit_state is None:
            raise RuntimeError("Conduit state is not initialized.")
        elif conduit._conduit_state.__str__() != "normal":
            raise RuntimeError("Creations can only be initialized for normal conduits.")
        self._conduit_state = conduit._conduit_state

        self._lock = RLock()
        self._display_name: str = self.__class__.__name__
        self._log_groups = ["creation_management", "creations"]
        self._log_sysgroups = ["conduit"]
        self._logger = conduit._logger

        # Internal storage for created objects by lifecycle scope
        self._unique: Dict[str, Creation] = {}
        self._unique_per_scope: Dict[str, Creation] = {}
        self._many: Dict[str, List[Creation]] = {}
        self._unique_per_lineage: Dict[str, Creation] = {}
        self._unique_per_cluster: Dict[str, Creation] = {}
        self._spellspace_instances: Dict[str, Dict[str, Creation]] = {}

        # Disposal configuration
        self._disposal_enabled = disposal_enabled
        self._disposal_method_names = disposal_method_names or []


    #region Destructor
    def cleanup(self) -> None:
        """
        Cleans the creations manager, disposing of all managed objects across all existence types.

        Once cleaned, no further modifications are allowed. If any disposal method fails,
        an `ExceptionGroup` containing all errors is raised.

        Raises:
            ExceptionGroup: Contains a list of all exceptions encountered during cleanup.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            errors: List[Exception] = []

            # Single try/except around the whole sequence (per request)
            try:
                errors.extend(self._cleanup_unique())

                errors.extend(self._cleanup_unique_per_scope())

                errors.extend(self._cleanup_many())

                errors.extend(self._cleanup_unique_per_lineage())

                errors.extend(self._cleanup_unique_per_cluster())

                errors.extend(self._cleanup_spellspace_instances())
            except Exception as e:
                # Fatal exception in the sequence (unexpected); record and continue teardown
                self._logger.error(f"cleanup: fatal error during sequence: {e}", method_name="cleanup",
                                   mask=True, owner_id=self._id, owner_display=self._display_name,
                                   groups=self._log_groups, system_groups=self._log_sysgroups, exc_info=True)
                errors.append(e)

            # Null internal refs last
            self._unique = None
            self._unique_per_scope = None
            self._many = None
            self._unique_per_lineage = None
            self._unique_per_cluster = None
            self._spellspace_instances = None
            self._conduit = None
            self._disposal_method_names = None

            if errors:
                self._logger.error(
                    f"cleanup: completed with {len(errors)} error(s); raising ExceptionGroup",
                    method_name="cleanup", mask=True,
                    owner_id=self._id, owner_display=self._display_name,
                    groups=self._log_groups, system_groups=self._log_sysgroups,
                )
                raise ExceptionGroup("Errors occurred during cleaning", errors)


            if self._logger is not None:
                self._display_name: str = ""
                self._log_groups.clear()
                self._log_groups = None
                self._log_sysgroups.clear()
                self._log_sysgroups = None
                self._logger = None

    def _cleanup_unique(self) -> List[Exception]:
        """
        Internal

        Disposes of all objects registered under the `unique` existence scope.

        Returns:
            List[Exception]: List of any cleanup errors encountered.
        """
        errors: List[Exception] = []
        for _, item in self._unique.items():
            if item is not None:
                maybe_error = self._attempt_cleanup(item.value)
                if maybe_error:
                    errors.append(maybe_error)
                item.cleanup()
        self._unique.clear()
        return errors

    def _cleanup_unique_per_lineage(self) -> List[Exception]:
        """
        Internal

        Disposes of all objects registered under the `unique_per_lineage` existence scope.

        Returns:
            List[Exception]: List of any cleanup errors encountered.
        """
        errors: List[Exception] = []
        for key, item in self._unique_per_lineage.items():
            if item is not None:
                maybe_error = self._attempt_cleanup(item.value)
                if maybe_error:
                    errors.append(maybe_error)
                item.cleanup()
        self._unique_per_lineage.clear()
        return errors

    def _cleanup_unique_per_cluster(self) -> List[Exception]:
        """
        Internal

        Disposes of all objects registered under the `unique_per_cluster` existence scope.

        Returns:
            List[Exception]: List of any cleanup errors encountered.
        """
        errors: List[Exception] = []
        for _, item in self._unique_per_cluster.items():
            if item is not None:
                maybe_error = self._attempt_cleanup(item.value)
                if maybe_error:
                    errors.append(maybe_error)
                item.cleanup()
        self._unique_per_cluster.clear()
        return errors

    def _cleanup_unique_per_scope(self) -> List[Exception]:
        """
        Internal

        Disposes of all objects registered under the `unique_per_scope` existence scope.

        Returns:
            List[Exception]: List of any cleanup errors encountered.
        """
        errors: List[Exception] = []
        for _, item in self._unique_per_scope.items():
            if item is not None:
                maybe_error = self._attempt_cleanup(item.value)
                if maybe_error:
                    errors.append(maybe_error)
                item.cleanup()
        self._unique_per_scope.clear()
        return errors

    def _cleanup_many(self) -> List[Exception]:
        """
        Internal

        Disposes of all multi-instance objects registered under the `many` existence scope.

        Returns:
            List[Exception]: List of any cleanup errors encountered.
        """
        errors: List[Exception] = []
        for _, items in self._many.items():
            for item in items:
                if item is not None:
                    maybe_error = self._attempt_cleanup(item.value)
                    if maybe_error:
                        errors.append(maybe_error)
                    item.cleanup()
            items.clear()
        self._many.clear()
        return errors

    def _cleanup_spellspace_instances(self) -> List[Exception]:
        """
        Internal

        Disposes of all objects registered under the spellspace scope buckets.

        Returns:
            List[Exception]: List of any cleanup errors encountered.
        """
        errors: List[Exception] = []
        for _, bucket in self._spellspace_instances.items():
            for item in bucket.values():
                if item is not None:
                    maybe_error = self._attempt_cleanup(item.value)
                    if maybe_error:
                        errors.append(maybe_error)
                    item.cleanup()
            bucket.clear()
        self._spellspace_instances.clear()
        return errors

    def _attempt_cleanup(self, item: object) -> Optional[Exception]:
        """
        Internal

        Attempt to clean up an object strictly via a prioritized list of method names.

        Behavior:
          - Returns None if `item` is None or disposal is disabled.
          - Iterates `self._disposal_method_names` in order (e.g., ["cleanup", "cleanup", "close", "dispose"]).
          - For the first attribute found on `item` that is callable, calls it.
          - If the call succeeds, returns None.
          - If the call raises, returns a RuntimeError wrapping the original exception.
          - If no listed methods exist on the object, returns None (treated as no-op).

        Notes:
          - No Protocol/type checks are performed.
          - Cleanup semantics are entirely defined by the configured method list.

        Args:
            item: The object instance to dispose.

        Returns:
            Optional[Exception]: RuntimeError if a chosen cleanup method raised; otherwise None.
        """
        if item is None:
            return None
        if not self._disposal_enabled:
            return None

        for method_name in self._disposal_method_names:
            if hasattr(item, method_name):
                meth = getattr(item, method_name, None)
                if callable(meth):
                    try:
                        meth()
                        return None
                    except Exception as ex:
                        self._logger.error(
                            f"_attempt_cleanup: '{method_name}' failed on {type(item).__name__}: {ex}",
                            method_name="_attempt_cleanup", mask=True, exc_info=True,
                            owner_id=self._id, owner_display=self._display_name,
                            groups=self._log_groups, system_groups=self._log_sysgroups,
                        )
                        return RuntimeError(f"Failed to dispose object {item} using method '{method_name}': {ex}")

        return None


    #endregion Destructor

    def _upgrade_from_lesser_conduit(self, **kwargs) -> None:
        """
        Internal

        Transfers creations data from a `LesserCreations` instance during a conduit upgrade.

        Args:
            **kwargs: Dictionary containing creation scopes (e.g., `unique_per_scope`, `many`).

        Raises:
            RuntimeError: If the `Creations` manager already contains objects before transfer.
        """
        if not len(self._unique_per_scope) == 0 and not len(self._many) == 0:
            self._logger.error(
                "_upgrade_from_lesser_conduit: target already has objects",
                method_name="_upgrade_from_lesser_conduit", mask=True,
                owner_id=self._id, owner_display=self._display_name,
                groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            raise RuntimeError("Objects already exist in conduit, cannot transfer data.")

        self._unique_per_scope = kwargs.get("unique_per_scope")
        self._many = kwargs.get("many")


    def add_unique(self, key: str, item: object) -> None:
        """
        Adds a singleton object instance to the `unique` scope.

        Args:
            key (UUID): Unique identifier (Spell ID).
            item (object): Object instance to manage.

        Raises:
            RuntimeError: If the Creations manager is cleaned.
            ValueError: If the key already exists in the `unique` scope.
        """
        self.check_cleaned()
        if key in self._unique:
            self._logger.error(f"add_unique: duplicate key={key}", method_name="add_unique", mask=True,
                               owner_id=self._id, owner_display=self._display_name,
                               groups=self._log_groups, system_groups=self._log_sysgroups)
            raise ValueError(f"Key {key} already exists in unique objects.")
        self._unique[key] = Creation(item)

    def add_unique_per_lineage(self, key: str, item: object) -> None:
        """
        Adds a singleton object instance to the `unique_per_lineage` scope.

        Args:
            key (str): Unique identifier (Spell ID).
            item (object): Object instance to manage.

        Raises:
            RuntimeError: If the Creations manager is cleaned.
            ValueError: If the key already exists in the `unique_per_lineage` scope.
        """
        self.check_cleaned()
        if key in self._unique_per_lineage:
            self._logger.error(f"add_unique_per_lineage: duplicate key={key}", method_name="add_unique_per_lineage", mask=True,
                               owner_id=self._id, owner_display=self._display_name,
                               groups=self._log_groups, system_groups=self._log_sysgroups)
            raise ValueError(f"Key {key} already exists in unique-per-lineage objects.")
        self._unique_per_lineage[key] = Creation(item)

    def add_unique_per_cluster(self, key: str, item: object) -> None:
        """
        Adds a singleton object instance to the `unique_per_cluster` scope.

        Args:
            key (UUID): Unique identifier (Spell ID).
            item (object): Object instance to manage.

        Raises:
            RuntimeError: If the Creations manager is cleaned.
            ValueError: If the key already exists in the `unique_per_cluster` scope.
        """
        self.check_cleaned()
        if key in self._unique_per_cluster:
            self._logger.error(f"add_unique_per_cluster: duplicate key={key}", method_name="add_unique_per_cluster", mask=True,
                               owner_id=self._id, owner_display=self._display_name,
                               groups=self._log_groups, system_groups=self._log_sysgroups)
            raise ValueError(f"Key {key} already exists in unique-per-cluster objects.")
        self._unique_per_cluster[key] = Creation(item)

    def add_unique_per_scope(self, key: str, item: object) -> None:
        """
        Adds a singleton object instance to the `unique_per_scope` scope.

        Args:
            key (str): Unique identifier (Spell ID).
            item (object): Object instance to manage.

        Raises:
            RuntimeError: If the Creations manager is cleaned.
            ValueError: If the key already exists in the `unique_per_scope` scope.
        """
        self.check_cleaned()
        if key in self._unique_per_scope:
            self._logger.error(f"add_unique_per_scope: duplicate key={key}", method_name="add_unique_per_scope", mask=True,
                               owner_id=self._id, owner_display=self._display_name,
                               groups=self._log_groups, system_groups=self._log_sysgroups)
            raise ValueError(f"Key {key} already exists in unique-per-scope objects.")
        self._unique_per_scope[key] = Creation(item)

    def add_many(self, key: str, item: object) -> None:
        """
        Adds an object instance to a multi-instance collection under the `many` scope.

        If the collection for the given key does not exist, it is created.

        Args:
            key (UUID): Collection identifier (Spell ID).
            item (object): Object instance to add.

        Raises:
            RuntimeError: If the Creations manager is cleaned.
        """
        self.check_cleaned()
        if key not in self._many:
            self._many[key] = []
        self._many[key].append(Creation(item))

    # ------------------------------------------------------------------
    # Extraction / restoration helpers (for transfers)
    # ------------------------------------------------------------------
    def extract_spell_creations(self, spell_id: str) -> List[Dict[str, Any]]:
        """
        Remove and return all creations associated with a spell_id across all scopes.

        Returns:
            List[Dict[str, Any]]: Entries of the form:
                {"scope": str, "creation": Creation, "spellspace_id": Optional[str]}
        """
        self.check_cleaned()
        extracted: List[Dict[str, Any]] = []
        with self._lock:
            # Singletons
            for scope_name, bucket in (
                ("unique", self._unique),
                ("unique_per_scope", self._unique_per_scope),
                ("unique_per_lineage", self._unique_per_lineage),
                ("unique_per_cluster", self._unique_per_cluster),
            ):
                if spell_id in bucket:
                    creation = bucket.pop(spell_id)
                    extracted.append({"scope": scope_name, "creation": creation})

            # Many (list)
            if spell_id in self._many:
                creations = self._many.pop(spell_id)
                for creation in creations:
                    extracted.append({"scope": "many", "creation": creation})

            # Spellspace buckets
            for spellspace_id, bucket in list(self._spellspace_instances.items()):
                if spell_id in bucket:
                    creation = bucket.pop(spell_id)
                    extracted.append({
                        "scope": "spellspace",
                        "spellspace_id": spellspace_id,
                        "creation": creation,
                    })
                    if not bucket:
                        del self._spellspace_instances[spellspace_id]

        return extracted

    def restore_spell_creations(self, spell_id: str, creations: List[Dict[str, Any]]) -> None:
        """
        Restore creations previously extracted via extract_spell_creations.
        """
        if not creations:
            return
        self.check_cleaned()
        with self._lock:
            for entry in creations:
                scope = entry.get("scope")
                creation: Creation = entry.get("creation")
                if creation is None or scope is None:
                    continue
                if scope == "unique":
                    self._unique[spell_id] = creation
                elif scope == "unique_per_scope":
                    self._unique_per_scope[spell_id] = creation
                elif scope == "unique_per_lineage":
                    self._unique_per_lineage[spell_id] = creation
                elif scope == "unique_per_cluster":
                    self._unique_per_cluster[spell_id] = creation
                elif scope == "many":
                    if spell_id not in self._many:
                        self._many[spell_id] = []
                    self._many[spell_id].append(creation)
                elif scope == "spellspace":
                    spellspace_id = entry.get("spellspace_id")
                    if spellspace_id is None:
                        continue
                    bucket = self._spellspace_instances.setdefault(spellspace_id, {})
                    bucket[spell_id] = creation

    # ------------------------------------------------------------------
    # SpellSpace helpers
    # ------------------------------------------------------------------

    def get_spellspace_creation(self, spellspace_id: str, spell_id: str) -> Optional[Creation]:
        """
        Retrieve a creation from a specific spellspace bucket.
        """
        self.check_cleaned()
        bucket = self._spellspace_instances.get(spellspace_id)
        if bucket is None:
            return None
        return bucket.get(spell_id)

    def register_spellspace_creation(self, spellspace_id: str, spell_id: str, item: object) -> None:
        """
        Register a creation under a specific spellspace bucket.
        """
        self.check_cleaned()
        if spellspace_id not in self._spellspace_instances:
            self._spellspace_instances[spellspace_id] = {}
        bucket = self._spellspace_instances[spellspace_id]
        if spell_id in bucket:
            raise ValueError(f"Key {spell_id} already exists in spellspace '{spellspace_id}'.")
        bucket[spell_id] = Creation(item)

    def clear_spellspace_instances(self, spellspace_id: str) -> None:
        """
        Dispose and clear all creations for a specific spellspace.
        """
        self.check_cleaned()
        bucket = self._spellspace_instances.get(spellspace_id)
        if bucket is None:
            return
        errors: List[Exception] = []
        for item in bucket.values():
            if item is not None:
                maybe_error = self._attempt_cleanup(item.value)
                if maybe_error:
                    errors.append(maybe_error)
                item.cleanup()
        bucket.clear()
        del self._spellspace_instances[spellspace_id]
        if errors:
            raise ExceptionGroup("Errors occurred during spellspace cleanup", errors)
