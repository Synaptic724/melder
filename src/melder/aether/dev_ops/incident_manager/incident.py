from __future__ import annotations
from threading import RLock
from typing import Dict, List, Optional, Any, Iterable
# Melder imports
from melder.aether.dev_ops.incident_manager.incident_severity import IncidentSeverity
from melder.aether.dev_ops.incident_manager.incident_status import IncidentStatus
from melder.utilities.general_base.cleanable import Cleanable


class Incident(Cleanable):
    """
    Lightweight DevOps incident.

    This is intentionally generic: it carries identifiers and metadata but
    does not prescribe how incidents are consumed. It is a tool surface
    for AI, operators, and tests.

    Identity / scope
    ----------------
    - id:
        Stable incident id (ULID or similar).
    - kind:
        Free-form incident kind code (e.g. "validation_failed",
        "graph_dirty", "mutation_stalled").
    - severity:
        Structured severity enum (info / warning / error / critical).
    - spell_index_id:
        Optional SpellIndex.id (lineage id) this incident is primarily
        associated with.
    - root_ids:
        Optional list of root spell ids impacted by this incident.

    Content
    -------
    - summary:
        Short, human/AI-readable summary.
    - details:
        Free-form structured metadata for diagnostics and tooling.
    """

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
        if not incident_id:
            raise ValueError("incident_id cannot be empty")
        if not kind:
            raise ValueError("kind cannot be empty")
        if not summary:
            raise ValueError("summary cannot be empty")

        super().__init__()

        self._lock: RLock = RLock()

        # scalar identity / status
        self._id: str = incident_id
        self._kind: str = kind
        self._severity: IncidentSeverity = severity
        self._status: IncidentStatus = IncidentStatus.open
        self._spell_index_id: Optional[str] = spell_index_id
        self._summary: str = summary
        self._root_ids: List[str] = list(root_ids or [])
        self._details: ConcurrentDict[str, Any] = details or {}

    def cleanup(self) -> None:
        """
        Idempotent cleanup.

        Marks this incident as cleaned and releases internal collections
        and references so it can be safely discarded.

        After cleanup():
        - All public methods / properties will raise via check_cleaned().
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return

            self._cleaned = True

            if self._root_ids is not None:
                self._root_ids.clear()
                self._root_ids = None

            if self._details is not None:
                self._details.clear()
                self._details = None

            self._spell_index_id = None
            self._summary = None
            self._kind = None
            self._severity = None
            self._status = None
            self._id = None

        self._lock = None

    # ---------------------------------------------------------------------
    # Read-only views (all under lock)
    # ---------------------------------------------------------------------
    @property
    def id(self) -> str:
        with self._lock:
            self.check_cleaned()
            return self._id

    @property
    def kind(self) -> str:
        with self._lock:
            self.check_cleaned()
            return self._kind

    @property
    def severity(self) -> IncidentSeverity:
        with self._lock:
            self.check_cleaned()
            return self._severity

    @property
    def status(self) -> IncidentStatus:
        with self._lock:
            self.check_cleaned()
            return self._status

    @property
    def spell_index_id(self) -> Optional[str]:
        with self._lock:
            self.check_cleaned()
            return self._spell_index_id

    @property
    def root_ids(self) -> List[str]:
        # Return a snapshot; callers can’t mutate internal list.
        with self._lock:
            self.check_cleaned()
            # If cleanup ran between check and lock acquisition, _root_ids will be None,
            # but check_cleaned() would have raised already.
            return list(self._root_ids)

    @property
    def summary(self) -> str:
        with self._lock:
            self.check_cleaned()
            return self._summary

    @property
    def details(self) -> Dict[str, Any]:
        # Return a snapshot; callers can’t mutate internal dict.
        with self._lock:
            self.check_cleaned()
            return dict(self._details)

    # ---------------------------------------------------------------------
    # State transitions (all under lock)
    # ---------------------------------------------------------------------
    def acknowledge(self) -> None:
        """
        Mark this incident as acknowledged (seen / triaged).

        Does not resolve it; it just records that someone/thing has
        looked at it.
        """
        with self._lock:
            self.check_cleaned()
            self._status = IncidentStatus.acknowledged

    def resolve(self) -> None:
        """
        Mark this incident as resolved.

        Higher-level tooling is responsible for deciding what "resolved"
        means (e.g., underlying validation fixed, graph revalidated, etc.).
        """
        with self._lock:
            self.check_cleaned()
            self._status = IncidentStatus.resolved

    def suppress(self) -> None:
        """
        Mark this incident as suppressed.

        This is typically used when the underlying condition is accepted
        (e.g., known limitation, intentionally dirty graph) and we do not
        want further noise from it.
        """
        with self._lock:
            self.check_cleaned()
            self._status = IncidentStatus.suppressed
