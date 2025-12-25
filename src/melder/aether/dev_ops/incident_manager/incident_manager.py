import threading
from typing import Dict, List, Optional, Any, Iterable
# Melder imports
from melder.aether.dev_ops.incident_manager.incident import Incident
from melder.aether.dev_ops.incident_manager.incident_severity import IncidentSeverity
from melder.aether.dev_ops.incident_manager.incident_status import IncidentStatus
from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class IncidentManager(Cleanable):
    """
    DevOps incident registry.

    Responsibilities:
    - Create and own all Incident objects for a frame.
    - Maintain an in-memory registry (id -> Incident) with simple lookup/filtering.
    - Provide deterministic, idempotent cleanup of incidents and the registry.

    Scope:
    - Purely descriptive; no policy or workflow enforcement is done here.
    - Optimized for diagnostic and tooling use (AI/operators), not for hot-path traffic.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_incidents_by_id",
        "_next_numeric_id",
    ]

    def __init__(self) -> None:
        super().__init__()
        self._lock: threading.RLock = threading.RLock()
        # incident_id -> Incident
        self._incidents_by_id: Dict[str, Incident] = {}
        self._next_numeric_id: int = 1

    def cleanup(self) -> None:
        """
        Idempotent cleanup.

        Cleans all tracked Incident objects, clears the registry, and nulls
        references for GC friendliness. Safe to call multiple times.
        """
        if self._cleaned:
            return

        with self._lock:
            if self._cleaned:
                return

            self._cleaned = True

            if self._incidents_by_id is not None:
                # Clean child incidents first.
                for incident in list(self._incidents_by_id.values()):
                    if incident is not None:
                        incident.cleanup()
                # Then clean the registry itself.
                self._incidents_by_id.clear()
                self._incidents_by_id = None

            self._next_numeric_id = 0

        self._lock = None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _allocate_id(self) -> str:
        """
        Allocate a new incident id.

        Caller must hold self._lock.
        """
        incident_id = f"inc-{self._next_numeric_id}"
        self._next_numeric_id += 1
        return incident_id

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def create_incident(
            self,
            *,
            kind: str,
            severity: IncidentSeverity,
            summary: str,
            spell_index_id: Optional[str] = None,
            root_ids: Optional[Iterable[str]] = None,
            details: Optional[Dict[str, Any]] = None,
    ) -> Incident:
        """
        Create and register a new Incident in this manager.

        Args:
            kind: Free-form incident kind code (e.g., "validation_failed").
            severity: IncidentSeverity enum value.
            summary: Short description of the incident.
            spell_index_id: Optional lineage id this incident is tied to.
            root_ids: Optional iterable of root spell ids impacted.
            details: Optional structured metadata (copied into the Incident).

        Returns:
            Incident: The newly created incident object (registry-owned).

        Raises:
            RuntimeError: If the manager has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            incident_id = self._allocate_id()
            incident = Incident(
                incident_id=incident_id,
                kind=kind,
                severity=severity,
                summary=summary,
                spell_index_id=spell_index_id,
                root_ids=root_ids,
                details=details,
            )
            self._incidents_by_id[incident_id] = incident
            return incident

    def get_incident(self, incident_id: str) -> Optional[Incident]:
        """
        Look up a single incident by id.

        Args:
            incident_id: Identifier previously returned by create_incident.

        Returns:
            Incident | None: The matching incident, or None if not found.

        Raises:
            RuntimeError: If the manager has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            return self._incidents_by_id.get(incident_id)

    def list_incidents(
            self,
            *,
            status: Optional[IncidentStatus] = None,
            spell_index_id: Optional[str] = None,
            kind: Optional[str] = None,
    ) -> List[Incident]:
        """
        Return a snapshot list of incidents matching optional filters.

        Args:
            status: Optional IncidentStatus filter.
            spell_index_id: Optional lineage id filter.
            kind: Optional kind string filter.

        Returns:
            List[Incident]: Snapshot of matching incidents.

        Raises:
            RuntimeError: If the manager has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            result: List[Incident] = []
            for inc in self._incidents_by_id.values():
                if status is not None and inc.status is not status:
                    continue
                if spell_index_id is not None and inc.spell_index_id != spell_index_id:
                    continue
                if kind is not None and inc.kind != kind:
                    continue
                result.append(inc)

            return result
