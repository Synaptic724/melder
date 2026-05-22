from threading import RLock
from typing import Dict, List, Optional, Any, Iterable, TYPE_CHECKING, ClassVar
from mypy_extensions import mypyc_attr
# Melder imports
from melder.aether.aetheric_frame.dev_ops.incident_manager.incident_status import IncidentStatus
from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import (
    __melder_registration_guard__ as _mrg,
)

if TYPE_CHECKING:
    from melder.aether.aetheric_frame.dev_ops.incident_manager.incident_severity import (
        IncidentSeverity,
    )

@mypyc_attr(native_class=True)
class Incident(Cleanable):
    """
    Mutable incident record with controlled status transitions.

    `Incident` is the concrete object stored by `IncidentManager`. It carries
    the descriptive payload for one operational problem or noteworthy runtime
    condition, plus a small mutable status field so tooling and operators can
    mark the incident as acknowledged, resolved, or suppressed over time.

    Identity and scope:
    - `id`: stable incident identifier allocated by the manager
    - `kind`: free-form incident kind code such as `"validation_failed"`
    - `severity`: structured severity level
    - `spell_index_id`: optional lineage id primarily associated with the
      incident
    - `root_ids`: optional impacted root spell ids

    Content:
    - `summary`: short human/AI-readable description
    - `details`: structured diagnostic payload for tooling

    Contract:
    - Read-only properties expose snapshots or scalar values under the lock.
    - Status transitions are explicit methods rather than direct field writes.
    - Cleanup releases internal references and invalidates the record for
      future use.
    """

    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_id",
        "_kind",
        "_severity",
        "_status",
        "_spell_index_id",
        "_root_ids",
        "_summary",
        "_details",
    ]

    def __init__(
        self,
        incident_id: str,
        kind: str,
        severity: IncidentSeverity,
        summary: str,
        *,
        spell_index_id: Optional[str] = None,
        root_ids: Optional[Iterable[str]] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Create one incident record.

        Purpose:
            Capture the descriptive payload and initial lifecycle state for one
            manager-owned operational incident.

        Contract:
            - New incidents always start in `IncidentStatus.open`.
            - `root_ids` and `details` are copied into incident-owned
              containers so later callers cannot mutate construction inputs out
              from under the record.

        Args:
            incident_id: Stable incident identifier allocated by the manager.
            kind: Free-form incident kind code.
            severity: Severity classification for the incident.
            summary: Short human/AI-readable description.
            spell_index_id: Optional lineage id primarily associated with the
                incident.
            root_ids: Optional impacted root spell ids.
            details: Optional structured diagnostic payload.

        Raises:
            ValueError: If `incident_id`, `kind`, or `summary` is empty.
        """
        if not incident_id:
            raise ValueError("incident_id cannot be empty")
        if not kind:
            raise ValueError("kind cannot be empty")
        if not summary:
            raise ValueError("summary cannot be empty")

        super().__init__()

        self._lock: RLock = RLock()

        self._id: str = incident_id
        self._kind: str = kind
        self._severity: IncidentSeverity = severity
        self._status: IncidentStatus = IncidentStatus.open
        self._spell_index_id: Optional[str] = spell_index_id
        self._summary: str = summary
        self._root_ids: List[str] = list(root_ids or [])
        self._details: Dict[str, Any] = details or {}

    def cleanup(self) -> None:
        """
        Finalize the incident record and release its payload.

        Contract:
        - Idempotent and lock-guarded.
        - Clears root-id and details containers before dropping scalar fields.
        - After cleanup, public properties and state-transition methods fail
          through `check_cleaned()`.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return

            self._cleaned = True

            if self._root_ids is not None:
                self._root_ids.clear()
            if self._details is not None:
                self._details.clear()

            del self._root_ids
            del self._details
            del self._spell_index_id
            del self._summary
            del self._kind
            del self._severity
            del self._status
            del self._id
        del self._lock

    @property
    def id(self) -> str:
        """
        Return the stable manager-assigned incident identifier.
        """
        self.check_cleaned()
        with self._lock:
            return self._id

    @property
    def kind(self) -> str:
        """
        Return the free-form incident kind code used for grouping/filtering.
        """
        self.check_cleaned()
        with self._lock:
            return self._kind

    @property
    def severity(self) -> IncidentSeverity:
        """
        Return the current severity classification for the incident.
        """
        self.check_cleaned()
        with self._lock:
            return self._severity

    @property
    def status(self) -> IncidentStatus:
        """
        Return the current operational lifecycle status of the incident.
        """
        self.check_cleaned()
        with self._lock:
            return self._status

    @property
    def spell_index_id(self) -> Optional[str]:
        """
        Return the lineage id primarily associated with the incident, if any.

        This is the incident's main lineage anchor, not a derived search over
        every impacted root.
        """
        self.check_cleaned()
        with self._lock:
            return self._spell_index_id

    @property
    def root_ids(self) -> List[str]:
        """
        Return a snapshot of impacted root spell ids.

        Contract:
        - Returns a new list so callers cannot mutate incident-owned state.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._root_ids)

    @property
    def summary(self) -> str:
        """
        Return the short human/AI-readable summary for the incident.
        """
        self.check_cleaned()
        with self._lock:
            return self._summary

    @property
    def details(self) -> Dict[str, Any]:
        """
        Return a snapshot of the structured diagnostic payload.

        Contract:
        - Returns a new dict so callers cannot mutate incident-owned state.
        """
        self.check_cleaned()
        with self._lock:
            return dict(self._details)

    def acknowledge(self) -> None:
        """
        Mark the incident as acknowledged.

        Contract:
        - Transitions the record to `IncidentStatus.acknowledged`.
        - Records triage/visibility only; it does not imply the underlying
          condition has been resolved or suppressed.
        """
        self.check_cleaned()
        with self._lock:
            self._status = IncidentStatus.acknowledged

    def resolve(self) -> None:
        """
        Mark the incident as resolved.

        Contract:
        - Transitions the record to `IncidentStatus.resolved`.
        - Higher-level tooling remains responsible for deciding what
          "resolved" means operationally; this method only updates the status
          field.
        """
        self.check_cleaned()
        with self._lock:
            self._status = IncidentStatus.resolved

    def suppress(self) -> None:
        """
        Mark the incident as suppressed.

        Contract:
        - Transitions the record to `IncidentStatus.suppressed`.
        - Uses the "accepted / intentionally muted" lifecycle state rather than
          claiming the underlying condition disappeared.
        """
        self.check_cleaned()
        with self._lock:
            self._status = IncidentStatus.suppressed
