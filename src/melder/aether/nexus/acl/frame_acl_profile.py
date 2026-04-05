import json
import threading
from typing import Any, Dict, List, Optional, Tuple

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class ViewACLDetails(Cleanable):
    """
    Purpose:
        Hold the placeholder serialized view-ACL details for one ACL profile
        strategy entry.

    Contract:
        - Owns one normalized JSON payload string.
        - Exposes parsed and serialized views of that payload.
        - Can be reused by `FrameACLProfile` strategies without introducing
          live ACL-application logic yet.

    Threading:
        Uses one instance `threading.RLock` to serialize payload mutation and
        cleanup.

    Lifecycle:
        Cleanup is idempotent and clears id, lock, and payload references.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_normalized_json_payload_string",
    ]

    def __init__(
            self,
            json_payload_string: str = "{}",
    ) -> None:
        """
        Initialize one view ACL details object.

        Purpose:
            Create the placeholder holder for serialized view-ACL profile
            details.

        Contract:
            - Payload is normalized into sorted-key JSON on construction.
            - Empty/default construction produces the normalized empty-object
              payload.

        Args:
            json_payload_string:
                JSON payload string to normalize and store.

        Returns:
            None.

        Raises:
            TypeError:
                If `json_payload_string` is not a string.
            ValueError:
                If the payload is not valid JSON.
        """
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._normalized_json_payload_string: str = self._normalize_json_payload(
            json_payload_string
        )

    def cleanup(self) -> None:
        """
        Idempotently clear the details object.

        Purpose:
            Tear down the placeholder details holder and release its payload.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._normalized_json_payload_string = None
            self._id = None
        self._lock = None

    @property
    def id(self) -> str:
        """
        Return the stable details-object identifier.

        Returns:
            str: Stable details-object id.
        """
        self.check_cleaned()
        return self._id

    @property
    def normalized_json_payload_string(self) -> str:
        """
        Return the canonical normalized JSON payload string.

        Returns:
            str: Normalized JSON payload string.
        """
        self.check_cleaned()
        with self._lock:
            return self._normalized_json_payload_string

    def set_json_payload_string(
            self,
            json_payload_string: str,
    ) -> None:
        """
        Replace the serialized view-ACL payload.

        Args:
            json_payload_string:
                JSON payload string to normalize and store.

        Returns:
            None.

        Raises:
            TypeError:
                If `json_payload_string` is not a string.
            ValueError:
                If the payload is not valid JSON.
        """
        self.check_cleaned()
        normalized_json_payload_string = self._normalize_json_payload(
            json_payload_string
        )
        with self._lock:
            self._normalized_json_payload_string = normalized_json_payload_string

    def to_json_dict(self) -> Dict[str, Any]:
        """
        Return the stored payload as a detached JSON-compatible dictionary.

        Returns:
            Dict[str, Any]: Parsed payload dictionary.
        """
        self.check_cleaned()
        return json.loads(self.normalized_json_payload_string)

    def to_json_string(self) -> str:
        """
        Return the canonical normalized payload string.

        Returns:
            str: Normalized payload string.
        """
        self.check_cleaned()
        return self.normalized_json_payload_string

    @staticmethod
    def _normalize_json_payload(json_payload_string: str) -> str:
        """
        Normalize one JSON payload into stable sorted-key string form.

        Args:
            json_payload_string:
                JSON payload string to normalize.

        Returns:
            str: Canonical normalized JSON string.

        Raises:
            TypeError:
                If `json_payload_string` is not a string.
            ValueError:
                If the payload is not valid JSON.
        """
        if not isinstance(json_payload_string, str):
            raise TypeError("json_payload_string must be a string.")
        try:
            parsed_payload = json.loads(json_payload_string)
        except json.JSONDecodeError as exc:
            raise ValueError("json_payload_string must be valid JSON.") from exc
        return json.dumps(parsed_payload, sort_keys=True)


class CodegenACLDetails(Cleanable):
    """
    Purpose:
        Hold the placeholder serialized codegen-ACL details for one ACL profile
        strategy entry.

    Contract:
        - Owns one normalized JSON payload string.
        - Exposes parsed and serialized views of that payload.
        - Can be reused by `FrameACLProfile` strategies without introducing
          live ACL-application logic yet.

    Threading:
        Uses one instance `threading.RLock` to serialize payload mutation and
        cleanup.

    Lifecycle:
        Cleanup is idempotent and clears id, lock, and payload references.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_normalized_json_payload_string",
    ]

    def __init__(
            self,
            json_payload_string: str = "{}",
    ) -> None:
        """
        Initialize one codegen ACL details object.

        Purpose:
            Create the placeholder holder for serialized codegen-ACL profile
            details.

        Contract:
            - Payload is normalized into sorted-key JSON on construction.
            - Empty/default construction produces the normalized empty-object
              payload.

        Args:
            json_payload_string:
                JSON payload string to normalize and store.

        Returns:
            None.

        Raises:
            TypeError:
                If `json_payload_string` is not a string.
            ValueError:
                If the payload is not valid JSON.
        """
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._normalized_json_payload_string: str = self._normalize_json_payload(
            json_payload_string
        )

    def cleanup(self) -> None:
        """
        Idempotently clear the details object.

        Purpose:
            Tear down the placeholder details holder and release its payload.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._normalized_json_payload_string = None
            self._id = None
        self._lock = None

    @property
    def id(self) -> str:
        """
        Return the stable details-object identifier.

        Returns:
            str: Stable details-object id.
        """
        self.check_cleaned()
        return self._id

    @property
    def normalized_json_payload_string(self) -> str:
        """
        Return the canonical normalized JSON payload string.

        Returns:
            str: Normalized JSON payload string.
        """
        self.check_cleaned()
        with self._lock:
            return self._normalized_json_payload_string

    def set_json_payload_string(
            self,
            json_payload_string: str,
    ) -> None:
        """
        Replace the serialized codegen-ACL payload.

        Args:
            json_payload_string:
                JSON payload string to normalize and store.

        Returns:
            None.

        Raises:
            TypeError:
                If `json_payload_string` is not a string.
            ValueError:
                If the payload is not valid JSON.
        """
        self.check_cleaned()
        normalized_json_payload_string = self._normalize_json_payload(
            json_payload_string
        )
        with self._lock:
            self._normalized_json_payload_string = normalized_json_payload_string

    def to_json_dict(self) -> Dict[str, Any]:
        """
        Return the stored payload as a detached JSON-compatible dictionary.

        Returns:
            Dict[str, Any]: Parsed payload dictionary.
        """
        self.check_cleaned()
        return json.loads(self.normalized_json_payload_string)

    def to_json_string(self) -> str:
        """
        Return the canonical normalized payload string.

        Returns:
            str: Normalized payload string.
        """
        self.check_cleaned()
        return self.normalized_json_payload_string

    @staticmethod
    def _normalize_json_payload(json_payload_string: str) -> str:
        """
        Normalize one JSON payload into stable sorted-key string form.

        Args:
            json_payload_string:
                JSON payload string to normalize.

        Returns:
            str: Canonical normalized JSON string.

        Raises:
            TypeError:
                If `json_payload_string` is not a string.
            ValueError:
                If the payload is not valid JSON.
        """
        if not isinstance(json_payload_string, str):
            raise TypeError("json_payload_string must be a string.")
        try:
            parsed_payload = json.loads(json_payload_string)
        except json.JSONDecodeError as exc:
            raise ValueError("json_payload_string must be valid JSON.") from exc
        return json.dumps(parsed_payload, sort_keys=True)


class FrameACLProfile(Cleanable):
    """
    Purpose:
        Hold one reusable placeholder ACL profile and its named strategy
        entries.

    Contract:
        - Each profile owns one default strategy entry made from one
          `ViewACLDetails` object and one `CodegenACLDetails` object.
        - Additional named strategy entries may be registered later in the same
          profile.
        - The profile is storage-only in this slice; it does not apply itself
          into a live ACL configuration yet.

    Threading:
        Uses one instance `threading.RLock` to serialize strategy registry
        mutation and cleanup.

    Lifecycle:
        Cleanup is idempotent and cascades into all owned detail objects before
        the strategy registry is dropped.
    """

    __melder_internal__ = _mrg.sentinel
    _DEFAULT_STRATEGY_NAME = "default"
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_name",
        "_strategies_by_name",
    ]

    def __init__(
            self,
            name: str,
            view_acl_details: Optional[ViewACLDetails] = None,
            codegen_acl_details: Optional[CodegenACLDetails] = None,
    ) -> None:
        """
        Initialize one frame ACL profile with one default strategy entry.

        Purpose:
            Create the reusable profile object that groups placeholder view and
            codegen details under one profile name.

        Contract:
            - `name` must be non-empty.
            - The default strategy entry always exists after construction.
            - Missing detail objects are replaced with empty placeholder
              details.

        Args:
            name:
                Stable profile name used in manager-level registries.
            view_acl_details:
                Optional placeholder view details for the default strategy.
            codegen_acl_details:
                Optional placeholder codegen details for the default strategy.

        Returns:
            None.

        Raises:
            ValueError:
                If `name` is empty.
            TypeError:
                If supplied detail objects have the wrong type.
        """
        super().__init__()
        if not name:
            raise ValueError("name cannot be empty.")
        if view_acl_details is not None and not isinstance(
                view_acl_details,
                ViewACLDetails,
        ):
            raise TypeError("view_acl_details must be a ViewACLDetails.")
        if codegen_acl_details is not None and not isinstance(
                codegen_acl_details,
                CodegenACLDetails,
        ):
            raise TypeError("codegen_acl_details must be a CodegenACLDetails.")

        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._name: str = name
        self._strategies_by_name: Dict[str, Tuple[ViewACLDetails, CodegenACLDetails]] = {
            self._DEFAULT_STRATEGY_NAME: (
                view_acl_details or ViewACLDetails(),
                codegen_acl_details or CodegenACLDetails(),
            )
        }

    def cleanup(self) -> None:
        """
        Idempotently cleanup the profile and all owned strategy details.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            cleaned_ids: set[int] = set()
            for view_acl_details, codegen_acl_details in self._strategies_by_name.values():
                if id(view_acl_details) not in cleaned_ids:
                    view_acl_details.cleanup()
                    cleaned_ids.add(id(view_acl_details))
                if id(codegen_acl_details) not in cleaned_ids:
                    codegen_acl_details.cleanup()
                    cleaned_ids.add(id(codegen_acl_details))
            self._strategies_by_name.clear()
            self._strategies_by_name = None
            self._name = None
            self._id = None
        self._lock = None

    @property
    def id(self) -> str:
        """
        Return the stable profile identifier.

        Returns:
            str: Stable profile id.
        """
        self.check_cleaned()
        return self._id

    @property
    def name(self) -> str:
        """
        Return the stable profile name.

        Returns:
            str: Stable profile name.
        """
        self.check_cleaned()
        return self._name

    @property
    def view_acl_details(self) -> ViewACLDetails:
        """
        Return the view details from the default strategy entry.

        Returns:
            ViewACLDetails: Default view details object.
        """
        self.check_cleaned()
        with self._lock:
            return self._strategies_by_name[self._DEFAULT_STRATEGY_NAME][0]

    @property
    def codegen_acl_details(self) -> CodegenACLDetails:
        """
        Return the codegen details from the default strategy entry.

        Returns:
            CodegenACLDetails: Default codegen details object.
        """
        self.check_cleaned()
        with self._lock:
            return self._strategies_by_name[self._DEFAULT_STRATEGY_NAME][1]

    @property
    def strategies_by_name(self) -> Dict[str, Tuple[ViewACLDetails, CodegenACLDetails]]:
        """
        Return a snapshot of the strategy registry.

        Returns:
            Dict[str, Tuple[ViewACLDetails, CodegenACLDetails]]:
                Snapshot of named strategy entries.
        """
        self.check_cleaned()
        with self._lock:
            return dict(self._strategies_by_name)

    def has_strategy(self, strategy_name: str) -> bool:
        """
        Return whether the profile currently owns the named strategy.

        Args:
            strategy_name:
                Strategy name to inspect.

        Returns:
            bool: True when the strategy exists.
        """
        self.check_cleaned()
        with self._lock:
            return strategy_name in self._strategies_by_name

    def list_strategy_names(self) -> List[str]:
        """
        Return the current strategy names in insertion order.

        Returns:
            List[str]: Current strategy names.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._strategies_by_name.keys())

    def get_required_strategy(
            self,
            strategy_name: str,
    ) -> Tuple[ViewACLDetails, CodegenACLDetails]:
        """
        Return one existing strategy tuple or raise.

        Args:
            strategy_name:
                Strategy name to resolve.

        Returns:
            Tuple[ViewACLDetails, CodegenACLDetails]:
                Named placeholder strategy tuple.

        Raises:
            KeyError:
                If the strategy does not exist.
        """
        self.check_cleaned()
        with self._lock:
            try:
                return self._strategies_by_name[strategy_name]
            except KeyError as exc:
                raise KeyError(strategy_name) from exc

    def register_strategy(
            self,
            strategy_name: str,
            view_acl_details: ViewACLDetails,
            codegen_acl_details: CodegenACLDetails,
    ) -> None:
        """
        Register or replace one named strategy tuple on the profile.

        Args:
            strategy_name:
                Strategy name to register.
            view_acl_details:
                View-details object for the strategy.
            codegen_acl_details:
                Codegen-details object for the strategy.

        Returns:
            None.

        Raises:
            ValueError:
                If `strategy_name` is empty.
            TypeError:
                If either details object has the wrong type.
        """
        self.check_cleaned()
        if not strategy_name:
            raise ValueError("strategy_name cannot be empty.")
        if not isinstance(view_acl_details, ViewACLDetails):
            raise TypeError("view_acl_details must be a ViewACLDetails.")
        if not isinstance(codegen_acl_details, CodegenACLDetails):
            raise TypeError("codegen_acl_details must be a CodegenACLDetails.")
        with self._lock:
            existing = self._strategies_by_name.get(strategy_name)
            if existing is not None:
                existing_view_acl_details, existing_codegen_acl_details = existing
                if existing_view_acl_details is not view_acl_details:
                    existing_view_acl_details.cleanup()
                if existing_codegen_acl_details is not codegen_acl_details:
                    existing_codegen_acl_details.cleanup()
            self._strategies_by_name[strategy_name] = (
                view_acl_details,
                codegen_acl_details,
            )

