from threading import RLock
from typing import Any, Dict, Optional
# Melder imports
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class ResolutionFrame(Cleanable):
    """
    Internal

    Per-meld resolution state shared across all nodes in a resolution DAG.

    Responsibilities:
      - Hold caller overrides (direct values passed to `meld(...)`).
      - Hold constructed results for each node (node_id -> object).
      - Optionally track per-node errors for debugging / diagnostics.

    This object is:
      - Created once per meld/resolution run.
      - Passed (or attached) to the DAG resolver.
      - Cleaned up after resolution is complete.

    It does NOT know about graph structure or spell details; it only stores values
    keyed by ids/names decided by SpellCrafter/DAG builder.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_errors",
        "_id",
        "_overrides",
        "_results",
    ]
    def __init__(self, overrides: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize a new per-meld resolution frame.

        Contract:
            - Allocates a fresh frame id for this resolution run.
            - Copies caller overrides into frame-owned storage.
            - Starts with empty result and error maps.
        """
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self._overrides: Dict[str, Any] = dict(overrides) if overrides else {}
        self._results: Dict[str, Any] = {}
        self._errors: Dict[str, BaseException] = {}

    # ------------------------------------------------------------------ #
    # Cleanup
    # ------------------------------------------------------------------ #
    def cleanup(self) -> None:
        """
        Cleans up the frame, dropping references to overrides, results, and errors.

        Idempotent.
        """
        if self._cleaned:
            return

        self._overrides.clear()
        self._results.clear()
        self._errors.clear()

        self._overrides = None
        self._results = None
        self._errors = None

        # We keep _lock and _id intact; only logical state is wiped.
        self._cleaned = True

    def reset(self, overrides: Optional[Dict[str, Any]] = None) -> None:
        """
        Reset the frame for reuse in another meld execution.

        Contract:
            - Clears overrides, results, and errors.
            - Reinitializes internal mappings if they were cleaned.
            - Generates a fresh id for the new execution run.
        """
        self._cleaned = False
        self._id = IDBuilder.create_id()

        if self._overrides is None:
            self._overrides = {}
        else:
            self._overrides.clear()

        if overrides:
            self._overrides.update(overrides)

        if self._results is None:
            self._results = {}
        else:
            self._results.clear()

        if self._errors is None:
            self._errors = {}
        else:
            self._errors.clear()


    # ------------------------------------------------------------------ #
    # Properties
    # ------------------------------------------------------------------ #
    @property
    def id(self) -> str:
        """
        Returns the unique identifier for this ResolutionFrame instance.
        """
        return self._id

    @property
    def overrides(self) -> Dict[str, Any]:
        """
        Returns a shallow copy of the caller overrides.

        Keys are parameter names or other resolution keys chosen by SpellCrafter.
        """
        return dict(self._overrides)

    @property
    def results(self) -> Dict[str, Any]:
        """
        Returns a shallow copy of all resolved node results.

        Keys are node ids (as used in the resolution DAG).
        """
        return dict(self._results)

    @property
    def errors(self) -> Dict[str, BaseException]:
        """
        Returns a shallow copy of all recorded node errors.

        Keys are node ids; values are the associated exceptions.
        """
        return dict(self._errors)

    # ------------------------------------------------------------------ #
    # Overrides
    # ------------------------------------------------------------------ #
    def has_override(self, key: str) -> bool:
        """
        Returns True if a caller override exists for the given key.
        """
        return key in self._overrides

    def get_override(self, key: str) -> Any:
        """
        Retrieves a caller override by key.

        Raises:
            KeyError: If the key is not present in overrides.
        """
        return self._overrides[key]

    # ------------------------------------------------------------------ #
    # Results
    # ------------------------------------------------------------------ #
    def set_result(self, node_id: str, value: Any) -> None:
        """
        Registers the resolved value for a given node id.
        """
        if not node_id:
            raise ValueError("node_id cannot be empty.")

        self._results[node_id] = value

    def has_result(self, node_id: str) -> bool:
        """
        Returns True if a result exists for the given node id.
        """
        return node_id in self._results

    def get_result(self, node_id: str) -> Any:
        """
        Retrieves the resolved value for a given node id.

        Raises:
            KeyError: If no result is registered for the node id.
        """
        return self._results[node_id]

    # ------------------------------------------------------------------ #
    # Errors
    # ------------------------------------------------------------------ #
    def register_error(self, node_id: str, error: BaseException) -> None:
        """
        Records an error for a node id.

        The resolver can use this for debugging or to build richer error reports.
        """
        if not node_id:
            raise ValueError("node_id cannot be empty.")
        if error is None:
            raise ValueError("error cannot be None.")

        self._errors[node_id] = error

    def get_error(self, node_id: str) -> Optional[BaseException]:
        """
        Retrieves the error associated with a node id, if any.

        Returns:
            The recorded exception instance, or None if no error is recorded.
        """
        return self._errors.get(node_id)

    def __repr__(self) -> str:
        """Return a compact debug summary of stored overrides, results, and errors."""
        return (
            f"ResolutionFrame(id={self._id!r}, "
            f"overrides={len(self._overrides)}, "
            f"results={len(self._results)}, "
            f"errors={len(self._errors)})"
        )
