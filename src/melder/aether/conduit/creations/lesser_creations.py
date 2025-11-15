from threading import RLock
from typing import List, Optional

# Melder imports
from melder.utilities.data_structures.concurrent_dictionary import ConcurrentDict
from melder.utilities.data_structures.concurrent_list import ConcurrentList
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.interfaces import IConduit
from melder.aether.conduit.creations.creation import Creation

class LesserCreations(Cleanable):
    """
    Manages instantiated objects within a **Lesser Conduit** (Child Scope).

    Lesser Creations is a reduced scope manager, only tracking objects with
    `unique_per_scope` and `many` lifecycles, as other scopes (`unique`, etc.)
    are delegated to the parent Conduit.

    **Key Responsibilities:**
      * Storage and disposal of local-scope objects.
      * Providing a snapshot of local objects for transfer during an upgrade.
    """

    def __init__(self, disposal_enabled: bool, disposal_method_names: List[str], conduit: IConduit):
        """
        Initialize a new LesserCreations manager.

        Args:
            disposal_enabled (bool): Whether disposal behavior is active.
            disposal_method_names (List[str]): List of method names to attempt during cleanup.

        The internal dictionaries hold references to the locally created objects,
        indexed by the spell's unique ID (str).
        """
        super().__init__()
        self._conduit: IConduit = conduit
        self._id: str = conduit._id
        self._logger = conduit._logger
        self._display_name: str = self.__class__.__name__
        self._log_groups = ["creation_management", "creations"]
        self._log_sysgroups = ["conduit"]
        self._lock = RLock()

        # Internal storage for managed objects
        self._unique_per_scope: ConcurrentDict[str, Creation] = ConcurrentDict()
        self._many: ConcurrentDict[str, ConcurrentList[Creation]] = ConcurrentDict()

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
        Cleanup the creations manager, disposing of all managed objects.

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
            self._logger.debug(
                "cleanup: begin",
                method_name="cleanup", mask=True,
                owner_id=self._id, owner_display=self._display_name,
                groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            errors: List[Exception] = []
            # Single try/except for the whole sequence
            try:
                self._logger.debug(
                    "_cleanup_unique_per_scope()",
                    method_name="cleanup", mask=True,
                    owner_id=self._id, owner_display=self._display_name,
                    groups=self._log_groups, system_groups=self._log_sysgroups,
                )
                errors.extend(self._cleanup_unique_per_scope())

                self._logger.debug(
                    "_cleanup_many()",
                    method_name="cleanup", mask=True,
                    owner_id=self._id, owner_display=self._display_name,
                    groups=self._log_groups, system_groups=self._log_sysgroups,
                )
                errors.extend(self._cleanup_many())
            except Exception as e:
                self._logger.error(
                    f"cleanup: fatal error during sequence: {e}",
                    method_name="cleanup", mask=True, exc_info=True,
                    owner_id=self._id, owner_display=self._display_name,
                    groups=self._log_groups, system_groups=self._log_sysgroups,
                )
                errors.append(e)

            # Null internals last
            self._unique_per_scope = None
            self._many = None
            self._conduit = None
            self._disposal_method_names = None

            if errors:
                self._logger.error(
                    f"cleanup: completed with {len(errors)} error(s); raising ExceptionGroup",
                    method_name="cleanup", mask=True,
                    owner_id=self._id, owner_display=self._display_name,
                    groups=self._log_groups, system_groups=self._log_sysgroups,
                )
                raise ExceptionGroup("Errors occurred during cleanup", errors)

            self._logger.debug(
                "cleanup: complete",
                method_name="cleanup", mask=True,
                owner_id=self._id, owner_display=self._display_name,
                groups=self._log_groups, system_groups=self._log_sysgroups,
            )

            if self._logger is not None:
                self._display_name: str = ""
                self._log_groups.clear()
                self._log_groups = None
                self._log_sysgroups.clear()
                self._log_sysgroups = None
                self._logger = None

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
        self._logger.debug(
            f"_cleanup_unique_per_scope: errors={len(errors)}",
            method_name="_cleanup_unique_per_scope", mask=True,
            owner_id=self._id, owner_display=self._display_name,
            groups=self._log_groups, system_groups=self._log_sysgroups,
        )
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
            items.cleanup()
        self._many.cleanup()
        self._logger.debug(
            f"_cleanup_many: errors={len(errors)}",
            method_name="_cleanup_many", mask=True,
            owner_id=self._id, owner_display=self._display_name,
            groups=self._log_groups, system_groups=self._log_sysgroups,
        )
        return errors

    def _attempt_cleanup(self, item: object) -> Optional[Exception]:
        """
        Internal

        Attempt to clean up an object strictly via a prioritized list of method names.

        Behavior:
          - Returns None if `item` is None or disposal is disabled.
          - Iterates `self._disposal_method_names` in order (e.g., ["cleanup", "close", "dispose"]).
          - For the first attribute found on `item` that is callable, calls it.
          - If the call succeeds, returns None.
          - If the call raises, returns a RuntimeError wrapping the original exception.
          - If no listed methods exist on the object, returns None (treated as no-op).

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
                method = getattr(item, method_name, None)
                if callable(method):
                    self._logger.debug(
                        f"_attempt_cleanup: calling '{method_name}' on {type(item).__name__}",
                        method_name="_attempt_cleanup", mask=True,
                        owner_id=self._id, owner_display=self._display_name,
                        groups=self._log_groups, system_groups=self._log_sysgroups,
                    )
                    try:
                        method()
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


    def transfer_data_and_clear(self) -> dict:
        """
        Creates a lightweight snapshot of the current creations, clears the internal state, and cleans the manager.

        This is used when a Lesser Conduit is upgraded to a Normal Conduit, transferring ownership of local creations.

        Returns:
            dict: A dictionary containing copies of the internal state (`unique_per_scope` and `many`).
        """
        self.check_cleaned()
        self._logger.debug(
            "transfer_data_and_clear: begin",
            method_name="transfer_data_and_clear", mask=True,
            owner_id=self._id, owner_display=self._display_name,
            groups=self._log_groups, system_groups=self._log_sysgroups,
        )

        try:
            data = {
                "unique_per_scope": self._unique_per_scope.copy(),
                "many": self._many.copy()
            }
        finally:
            self._logger.debug(
                "transfer_data_and_clear: clearing internal containers",
                method_name="transfer_data_and_clear", mask=True,
                owner_id=self._id, owner_display=self._display_name,
                groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            self._unique_per_scope.clear()
            self._many.clear()
            # Use cleanup() to finalize & null refs
            self.cleanup()

        self._logger.debug(
            "transfer_data_and_clear: complete",
            method_name="transfer_data_and_clear", mask=True,
            owner_id=self._id, owner_display=self._display_name,
            groups=self._log_groups, system_groups=self._log_sysgroups,
        )
        return data


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
        self._logger.debug(
            f"add_unique_per_scope: key={key}",
            method_name="add_unique_per_scope", mask=True,
            owner_id=self._id, owner_display=self._display_name,
            groups=self._log_groups, system_groups=self._log_sysgroups,
        )
        if key in self._unique_per_scope:
            self._logger.error(
                f"add_unique_per_scope: duplicate key={key}",
                method_name="add_unique_per_scope", mask=True,
                owner_id=self._id, owner_display=self._display_name,
                groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            raise ValueError(f"Key {key} already exists in unique-per-scope objects.")
        self._unique_per_scope[key] = Creation(item)

    def add_many(self, key: str, item: object) -> None:
        """
        Adds an object instance to a multi-instance collection under the `many` scope.

        If the collection for the given key does not exist, it is created.

        Args:
            key (str): Collection identifier (Spell ID).
            item (object): Object instance to add.

        Raises:
            RuntimeError: If the Creations manager is cleaned.
        """
        self.check_cleaned()
        self._logger.debug(
            f"add_many: key={key}",
            method_name="add_many", mask=True,
            owner_id=self._id, owner_display=self._display_name,
            groups=self._log_groups, system_groups=self._log_sysgroups,
        )
        if key not in self._many:
            self._many[key] = ConcurrentList()
        self._many[key].append(Creation(item))