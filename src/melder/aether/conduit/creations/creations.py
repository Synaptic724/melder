from threading import RLock
from typing import List, Optional

# Melder imports
from melder.utilities.data_structures.concurrent_dict import ConcurrentDict
from melder.utilities.data_structures.concurrent_list import ConcurrentList
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.interfaces import IConduit
from melder.aether.conduit.creations.creation import Creation


#TODO: Create a creations object to encapsulate the objects under my control.

class Creations(Cleanable):
    """
    Manages all instantiated objects within a Conduit (Normal Scope).

    This manager is responsible for tracking object instances based on their lifecycle
    (`unique`, `unique_per_scope`, `many`, etc.) and enforcing resource disposal upon cleaning.

    **Key Responsibilities:**
      * Storage and lifecycle management of created objects.
      * Controlled resource disposal via `ICleanable` or configured cleanup methods.
    """

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
        self._lock = RLock()
        self._display_name: str = self.__class__.__name__
        self._log_groups = ["creation_management", "creations"]
        self._log_sysgroups = ["conduit"]
        self._logger = conduit._logger

        # Internal storage for created objects by lifecycle scope
        self._unique: ConcurrentDict[str, Creation] = ConcurrentDict()
        self._unique_per_scope: ConcurrentDict[str, Creation] = ConcurrentDict()
        self._many: ConcurrentDict[str, ConcurrentList[Creation]] = ConcurrentDict()
        self._unique_per_lineage: ConcurrentDict[str, Creation] = ConcurrentDict()
        self._unique_per_cluster: ConcurrentDict[str, Creation] = ConcurrentDict()

        # Disposal configuration
        self._disposal_enabled = disposal_enabled
        self._disposal_method_names = disposal_method_names or []

        self._logger.debug(
            f"__init__: disposal_enabled={disposal_enabled}, methods={self._disposal_method_names}",
            method_name="__init__", mask=True,
            owner_id=self._id, owner_display=self._display_name,
            groups=self._log_groups, system_groups=self._log_sysgroups,
        )

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
            self._logger.debug("cleanup: begin", method_name="cleanup", mask=True,
                               owner_id=self._id, owner_display=self._display_name,
                               groups=self._log_groups, system_groups=self._log_sysgroups)
            self._cleaned = True
            errors: List[Exception] = []

            # Single try/except around the whole sequence (per request)
            try:
                self._logger.debug("_cleanup_unique()", method_name="cleanup", mask=True,
                                   owner_id=self._id, owner_display=self._display_name,
                                   groups=self._log_groups, system_groups=self._log_sysgroups)
                errors.extend(self._cleanup_unique())

                self._logger.debug("_cleanup_unique_per_scope()", method_name="cleanup", mask=True,
                                   owner_id=self._id, owner_display=self._display_name,
                                   groups=self._log_groups, system_groups=self._log_sysgroups)
                errors.extend(self._cleanup_unique_per_scope())

                self._logger.debug("_cleanup_many()", method_name="cleanup", mask=True,
                                   owner_id=self._id, owner_display=self._display_name,
                                   groups=self._log_groups, system_groups=self._log_sysgroups)
                errors.extend(self._cleanup_many())

                self._logger.debug("_cleanup_unique_per_lineage()", method_name="cleanup", mask=True,
                                   owner_id=self._id, owner_display=self._display_name,
                                   groups=self._log_groups, system_groups=self._log_sysgroups)
                errors.extend(self._cleanup_unique_per_lineage())

                self._logger.debug("_cleanup_unique_per_cluster()", method_name="cleanup", mask=True,
                                   owner_id=self._id, owner_display=self._display_name,
                                   groups=self._log_groups, system_groups=self._log_sysgroups)
                errors.extend(self._cleanup_unique_per_cluster())
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

            self._logger.debug("cleanup: complete", method_name="cleanup", mask=True,
                               owner_id=self._id, owner_display=self._display_name,
                               groups=self._log_groups, system_groups=self._log_sysgroups)

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
        self._unique.cleanup()
        self._logger.debug(f"_cleanup_unique: errors={len(errors)}", method_name="_cleanup_unique", mask=True,
                           owner_id=self._id, owner_display=self._display_name,
                           groups=self._log_groups, system_groups=self._log_sysgroups)
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
        self._unique_per_lineage.cleanup()
        self._logger.debug(f"_cleanup_unique_per_lineage: errors={len(errors)}",
                           method_name="_cleanup_unique_per_lineage", mask=True,
                           owner_id=self._id, owner_display=self._display_name,
                           groups=self._log_groups, system_groups=self._log_sysgroups)
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
        self._unique_per_cluster.cleanup()
        self._logger.debug(f"_cleanup_unique_per_cluster: errors={len(errors)}",
                           method_name="_cleanup_unique_per_cluster", mask=True,
                           owner_id=self._id, owner_display=self._display_name,
                           groups=self._log_groups, system_groups=self._log_sysgroups)
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
        self._unique_per_scope.cleanup()
        self._logger.debug(f"_cleanup_unique_per_scope: errors={len(errors)}",
                           method_name="_cleanup_unique_per_scope", mask=True,
                           owner_id=self._id, owner_display=self._display_name,
                           groups=self._log_groups, system_groups=self._log_sysgroups)
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
                    maybe_error = self._attempt_cleanup(item)
                    if maybe_error:
                        errors.append(maybe_error)
                    item.cleanup()
            items.cleanup()
        self._many.cleanup()
        self._logger.debug(f"_cleanup_many: errors={len(errors)}",
                           method_name="_cleanup_many", mask=True,
                           owner_id=self._id, owner_display=self._display_name,
                           groups=self._log_groups, system_groups=self._log_sysgroups)
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
            self._logger.debug(
                "_attempt_cleanup: disposal disabled; skipping",
                method_name="_attempt_cleanup", mask=True,
                owner_id=self._id, owner_display=self._display_name,
                groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            return None

        for method_name in self._disposal_method_names:
            if hasattr(item, method_name):
                meth = getattr(item, method_name, None)
                if callable(meth):
                    self._logger.debug(
                        f"_attempt_cleanup: calling '{method_name}' on {type(item).__name__}",
                        method_name="_attempt_cleanup", mask=True,
                        owner_id=self._id, owner_display=self._display_name,
                        groups=self._log_groups, system_groups=self._log_sysgroups,
                    )
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

        self._logger.debug(
            "_attempt_cleanup: no disposal method matched; noop",
            method_name="_attempt_cleanup", mask=True,
            owner_id=self._id, owner_display=self._display_name,
            groups=self._log_groups, system_groups=self._log_sysgroups,
        )
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
        self._logger.debug(
            "_upgrade_from_lesser_conduit: begin",
            method_name="_upgrade_from_lesser_conduit", mask=True,
            owner_id=self._id, owner_display=self._display_name,
            groups=self._log_groups, system_groups=self._log_sysgroups,
        )

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

        self._logger.debug(
            "_upgrade_from_lesser_conduit: complete",
            method_name="_upgrade_from_lesser_conduit", mask=True,
            owner_id=self._id, owner_display=self._display_name,
            groups=self._log_groups, system_groups=self._log_sysgroups,
        )

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
        self._logger.debug(f"add_unique: key={key}", method_name="add_unique", mask=True,
                           owner_id=self._id, owner_display=self._display_name,
                           groups=self._log_groups, system_groups=self._log_sysgroups)
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
        self._logger.debug(f"add_unique_per_lineage: key={key}", method_name="add_unique_per_lineage", mask=True,
                           owner_id=self._id, owner_display=self._display_name,
                           groups=self._log_groups, system_groups=self._log_sysgroups)
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
        self._logger.debug(f"add_unique_per_cluster: key={key}", method_name="add_unique_per_cluster", mask=True,
                           owner_id=self._id, owner_display=self._display_name,
                           groups=self._log_groups, system_groups=self._log_sysgroups)
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
        self._logger.debug(f"add_unique_per_scope: key={key}", method_name="add_unique_per_scope", mask=True,
                           owner_id=self._id, owner_display=self._display_name,
                           groups=self._log_groups, system_groups=self._log_sysgroups)
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
        self._logger.debug(f"add_many: key={key}", method_name="add_many", mask=True,
                           owner_id=self._id, owner_display=self._display_name,
                           groups=self._log_groups, system_groups=self._log_sysgroups)
        if key not in self._many:
            self._many[key] = ConcurrentList()
        self._many[key].append(Creation(item))