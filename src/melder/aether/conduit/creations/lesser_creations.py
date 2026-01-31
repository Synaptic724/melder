from threading import RLock
from typing import List, Optional, Dict
from collections import deque

# Melder imports
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.interfaces import IConduit, ILesserCreations
from melder.aether.conduit.creations.creation import Creation
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class LesserCreations(Cleanable, ILesserCreations):
    """
    Manages instantiated objects within a **Lesser Conduit** (Child Scope).

    Lesser Creations is a reduced scope manager, only tracking objects with
    `unique_per_scope` and `many` lifecycles, as other scopes (`unique`, etc.)
    are delegated to the parent Conduit.

    **Key Responsibilities:**
      * Storage and disposal of local-scope objects.
      * Providing a snapshot of local objects for transfer during an upgrade.
    """
    __melder_internal__ = _mrg.sentinel
    def __init__(self, conduit: IConduit, parent_creations=None):
        """
        Initialize a new LesserCreations manager.

        Args:
        The internal dictionaries hold references to the locally created objects,
        indexed by the spell's unique ID (str).
        """
        super().__init__()
        self._conduit: IConduit = conduit
        # Optional link back to the parent conduit creations for delegating
        # frame-wide singletons.
        self._parent_creations = parent_creations
        self._id: str = conduit._id
        self._logger = conduit._logger

        if conduit._conduit_state is None:
            raise RuntimeError("LesserCreations initialized with a Conduit that has no state.")
        elif conduit._conduit_state.__str__() != "lesser":
            raise RuntimeError("LesserCreations can only be initialized for Lesser Conduits.")
        self._conduit_state = conduit._conduit_state

        self._display_name: str = self.__class__.__name__
        self._log_groups = ["creation_management", "creations"]
        self._log_sysgroups = ["conduit"]
        self._lock = RLock()
        self._disposal_stack: deque = deque()

        # Internal storage for managed objects
        self._unique_per_scope: Dict[str, Creation] = {}
        self._many: Dict[str, List[Creation]] = {}
        self._spellspace_instances: Dict[str, Dict[str, Creation]] = {}
        self._spellspace_disposal_stacks: Dict[str, deque] = {}


    #region Destructor

    def cleanup(self) -> None:
        """
        Cleanup the creations manager, disposing of all managed objects.

        Once cleaned, no further modifications are allowed. If any disposal method fails,
        an `ExceptionGroup` containing all errors is raised.

        Disposal ordering:
            - Uses a LIFO disposal stack populated at creation time.
            - Per-scope buckets are cleared after the stack is drained.

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
            # Single try/except for the whole sequence
            try:
                errors.extend(self._drain_disposal_stack())
            except Exception as e:
                self._logger.error(
                    f"cleanup: fatal error during sequence: {e}",
                    method_name="cleanup", mask=True, exc_info=True,
                    owner_id=self._id, owner_display=self._display_name,
                    groups=self._log_groups, system_groups=self._log_sysgroups,
                )
                errors.append(e)

            # Null internals last
            self._unique_per_scope.clear()
            self._many.clear()
            self._spellspace_instances.clear()
            self._spellspace_disposal_stacks.clear()
            self._disposal_stack.clear()
            self._unique_per_scope = None
            self._many = None
            self._spellspace_instances = None
            self._spellspace_disposal_stacks = None
            self._conduit = None
            self._parent_creations = None
            self._disposal_stack = None

            if errors:
                self._logger.error(
                    f"cleanup: completed with {len(errors)} error(s); raising ExceptionGroup",
                    method_name="cleanup", mask=True,
                    owner_id=self._id, owner_display=self._display_name,
                    groups=self._log_groups, system_groups=self._log_sysgroups,
                )
                raise ExceptionGroup("Errors occurred during cleanup", errors)


            if self._logger is not None:
                self._display_name: str = ""
                self._log_groups.clear()
                self._log_groups = None
                self._log_sysgroups.clear()
                self._log_sysgroups = None
                self._logger = None

    def _cleanup_spellspace_instances(self) -> List[Exception]:
        """
        Internal

        Disposes of all objects registered under the spellspace scope buckets.

        Returns:
            List[Exception]: List of any cleanup errors encountered.
        """
        errors: List[Exception] = []
        for spellspace_id, bucket in self._spellspace_instances.items():
            errors.extend(self._drain_spellspace_disposal_stack(spellspace_id))
            for item in bucket.values():
                if item is not None:
                    item.cleanup()
            bucket.clear()
        self._spellspace_instances.clear()
        self._spellspace_disposal_stacks.clear()
        return errors

    def _attempt_cleanup(self, creation: Creation) -> Optional[Exception]:
        """
        Internal

        Attempt to clean up an object strictly via a prioritized list of method names.

        Behavior:
          - Returns None if `item` is None or disposal is disabled.
          - Iterates the Creation's `disposal_method_names` in order
            (e.g., ["cleanup", "close", "dispose"]).
          - For the first attribute found on `item` that is callable, calls it.
          - If the call succeeds, returns None.
          - If the call raises, returns a RuntimeError wrapping the original exception.
          - If no listed methods exist on the object, returns None (treated as no-op).

        Args:
            creation: The Creation wrapper to dispose.

        Returns:
            Optional[Exception]: RuntimeError if a chosen cleanup method raised; otherwise None.
        """
        if creation is None:
            return None
        item = creation.value
        if item is None:
            return None
        method_names = creation.disposal_method_names or []
        if not method_names:
            return None

        for method_name in method_names:
            try:
                method = item.__getattribute__(method_name)
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

        return None

    def _push_disposal_creation(self, creation: Creation) -> None:
        """
        Internal

        Push a Creation onto the disposal stack when it declares disposal methods.
        """
        if creation is None:
            return
        if creation.has_disposal_methods:
            self._disposal_stack.appendleft(creation)

    def _push_spellspace_disposal_creation(self, spellspace_id: str, creation: Creation) -> None:
        """
        Internal

        Push a Creation onto a spellspace-local disposal stack when it declares disposal methods.
        """
        if creation is None:
            return
        if creation.has_disposal_methods:
            stack = self._spellspace_disposal_stacks.setdefault(spellspace_id, deque())
            stack.appendleft(creation)

    def _remove_disposal_creation(self, creation: Creation) -> None:
        """
        Internal

        Remove a Creation from the disposal stack if present.
        """
        if creation is None:
            return
        if not creation.has_disposal_methods:
            return
        if not self._disposal_stack:
            return
        self._disposal_stack = deque(
            item for item in self._disposal_stack
            if item is not creation
        )

    def _remove_spellspace_disposal_creation(self, spellspace_id: str, creation: Creation) -> None:
        """
        Internal

        Remove a Creation from a spellspace-local disposal stack if present.
        """
        if creation is None:
            return
        if not creation.has_disposal_methods:
            return
        stack = self._spellspace_disposal_stacks.get(spellspace_id)
        if not stack:
            return
        self._spellspace_disposal_stacks[spellspace_id] = deque(
            item for item in stack
            if item is not creation
        )

    def _drain_disposal_stack(self) -> List[Exception]:
        """
        Internal

        Drain the disposal stack in LIFO order and dispose each Creation.
        """
        errors: List[Exception] = []
        while self._disposal_stack:
            creation = self._disposal_stack.popleft()
            if creation is None:
                continue
            maybe_error = self._attempt_cleanup(creation)
            if maybe_error:
                errors.append(maybe_error)
            creation.cleanup()
        return errors

    def _drain_spellspace_disposal_stack(self, spellspace_id: str) -> List[Exception]:
        """
        Internal

        Drain a spellspace-local disposal stack in LIFO order and dispose each Creation.
        """
        errors: List[Exception] = []
        stack = self._spellspace_disposal_stacks.get(spellspace_id)
        if not stack:
            return errors
        while stack:
            creation = stack.popleft()
            if creation is None:
                continue
            maybe_error = self._attempt_cleanup(creation)
            if maybe_error:
                errors.append(maybe_error)
            creation.cleanup()
        return errors


    #endregion Destructor


    def transfer_data_and_clear(self) -> dict:
        """
        Creates a lightweight snapshot of the current creations, clears the internal state, and cleans the manager.

        This is used when a Lesser Conduit is upgraded to a Normal Conduit, transferring ownership of local creations.

        Returns:
            dict: A dictionary containing copies of the internal state
                (`unique_per_scope`, `many`, and `disposal_stack`).
        """
        self.check_cleaned()
        try:
            data = {
                "unique_per_scope": self._unique_per_scope.copy(),
                "many": self._many.copy(),
                "disposal_stack": deque(self._disposal_stack),
            }
        finally:
            self._unique_per_scope.clear()
            self._many.clear()
            self._disposal_stack.clear()
            # Use cleanup() to finalize & null refs
            self.cleanup()
        return data


    def add_unique_per_scope(
            self,
            key: str,
            item: object,
            *,
            has_disposal_methods: bool = False,
            disposal_methods: list[str] | None = None,
    ) -> None:
        """
        Adds a singleton object instance to the `unique_per_scope` scope.

        Args:
            key (str): Unique identifier (Spell ID).
            item (object): Object instance to manage.
            has_disposal_methods: True when the spell declares disposal methods.
            disposal_methods: Ordered list of disposal method names for this creation.

        Raises:
            RuntimeError: If the Creations manager is cleaned.
            ValueError: If the key already exists in the `unique_per_scope` scope.
        """
        self.check_cleaned()
        if key in self._unique_per_scope:
            self._logger.error(
                f"add_unique_per_scope: duplicate key={key}",
                method_name="add_unique_per_scope", mask=True,
                owner_id=self._id, owner_display=self._display_name,
                groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            raise ValueError(f"Key {key} already exists in unique-per-scope objects.")
        creation = Creation(
            item,
            has_disposal_methods=has_disposal_methods,
            disposal_methods=disposal_methods,
        )
        self._unique_per_scope[key] = creation
        if has_disposal_methods:
            self._push_disposal_creation(creation)
    def add_many(
            self,
            key: str,
            item: object,
            *,
            has_disposal_methods: bool = False,
            disposal_methods: list[str] | None = None,
    ) -> None:
        """
        Adds an object instance to a multi-instance collection under the `many` scope.

        If the collection for the given key does not exist, it is created.

        Args:
            key (str): Collection identifier (Spell ID).
            item (object): Object instance to add.
            has_disposal_methods: True when the spell declares disposal methods.
            disposal_methods: Ordered list of disposal method names for this creation.

        Raises:
            RuntimeError: If the Creations manager is cleaned.
        """
        self.check_cleaned()
        if key not in self._many:
            self._many[key] = []
        creation = Creation(
            item,
            has_disposal_methods=has_disposal_methods,
            disposal_methods=disposal_methods,
        )
        self._many[key].append(creation)
        if has_disposal_methods:
            self._push_disposal_creation(creation)

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

    def register_spellspace_creation(
            self,
            spellspace_id: str,
            spell_id: str,
            item: object,
            *,
            has_disposal_methods: bool = False,
            disposal_methods: list[str] | None = None,
    ) -> None:
        """
        Register a creation under a specific spellspace bucket.

        Args:
            spellspace_id: SpellSpace bucket identifier.
            spell_id: Spell id used as the bucket key.
            item: Object instance to register.
            has_disposal_methods: True when the spell declares disposal methods.
            disposal_methods: Ordered list of disposal method names for this creation.
        """
        self.check_cleaned()
        if spellspace_id not in self._spellspace_instances:
            self._spellspace_instances[spellspace_id] = {}
        bucket = self._spellspace_instances[spellspace_id]
        if spell_id in bucket:
            raise ValueError(f"Key {spell_id} already exists in spellspace '{spellspace_id}'.")
        creation = Creation(
            item,
            has_disposal_methods=has_disposal_methods,
            disposal_methods=disposal_methods,
        )
        bucket[spell_id] = creation
        self._push_spellspace_disposal_creation(spellspace_id, creation)

    def clear_spellspace_instances(self, spellspace_id: str) -> None:
        """
        Dispose and clear all creations for a specific spellspace.
        """
        self.check_cleaned()
        bucket = self._spellspace_instances.get(spellspace_id)
        if bucket is None:
            return
        errors: List[Exception] = []
        errors.extend(self._drain_spellspace_disposal_stack(spellspace_id))
        for item in bucket.values():
            if item is not None:
                item.cleanup()
        bucket.clear()
        del self._spellspace_instances[spellspace_id]
        self._spellspace_disposal_stacks.pop(spellspace_id, None)
        if errors:
            raise ExceptionGroup("Errors occurred during spellspace cleanup", errors)
