import threading
from typing import Dict, List, Optional, Any, Iterable
# Melder imports
from melder.aether.dev_ops.incident_manager.incident import Incident
from melder.aether.dev_ops.incident_manager.incident_severity import (
    IncidentSeverity,
)
from melder.aether.dev_ops.incident_manager.incident_status import IncidentStatus
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces import IIncidentManager
from melder.__melder_registration_guard__ import (
    __melder_registration_guard__ as _mrg,
)


class IncidentManager(Cleanable, IIncidentManager):
    """
    Frame-local registry of `Incident` records.

    `IncidentManager` is the descriptive side of the DevOps surface. It owns
    the incident objects for one frame, allocates their ids, and provides the
    lookup/filtering entrypoints that tooling, operators, or higher-level
    automation can use to inspect that frame's incident history.

    Contract:
    - The manager owns every `Incident` it creates.
    - Incident ids are allocated sequentially for the lifetime of the manager.
    - Query methods return current registry state only; no policy decisions are
      made here.
    - Cleanup is idempotent and tears down child incidents before clearing the
      registry itself.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_incidents_by_id",
        "_next_numeric_id",
    ]

    def __init__(self) -> None:
        """
        Initialize the incident registry.

        Contract:
        - Starts with an empty `incident_id -> Incident` map.
        - Numeric incident ids begin at `inc-1` for a fresh manager lifetime.
        """
        super().__init__()
        self._lock: threading.RLock = threading.RLock()
        # incident_id -> Incident
        self._incidents_by_id: Dict[str, Incident] = {}
        self._next_numeric_id: int = 1

    def cleanup(self) -> None:
        """
        Finalize the incident registry and its owned incidents.

        Contract:
        - Idempotent cleanup.
        - Cleans child `Incident` objects before clearing the registry.
        - Drops registry references and zeroes the numeric id counter.
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
                self._incidents_by_id.clear()
                del self._incidents_by_id
            self._next_numeric_id = 0

        del self._lock

    def _allocate_id(self) -> str:
        """
        Allocate the next incident id.

        Caller contract:
        - `self._lock` must already be held before this helper is called.
        """
        incident_id = f"inc-{self._next_numeric_id}"
        self._next_numeric_id += 1
        return incident_id

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
        Create and register one new `Incident`.

        This is the manager-owned construction path. The new incident is built
        under the registry lock, assigned a fresh id, inserted into the
        registry, and then returned as the registry-owned object.

        Args:
            kind: Free-form incident kind code, for example
                `"validation_failed"`.
            severity: `IncidentSeverity` value for the new incident.
            summary: Short description of the incident.
            spell_index_id: Optional lineage id the incident is tied to.
            root_ids: Optional iterable of impacted root spell ids.
            details: Optional structured metadata copied into the incident.

        Returns:
            Incident: Newly created, registry-owned incident object.

        Raises:
            RuntimeError: If the manager has already been cleaned.
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
        Return one incident by id, if present.

        Args:
            incident_id: Identifier previously returned by `create_incident()`.

        Returns:
            Optional[Incident]: Matching incident, or `None` if not found.

        Raises:
            RuntimeError: If the manager has already been cleaned.
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
        Return a filtered snapshot of the incident registry.

        Filtering is additive: every supplied filter must match for the
        incident to be included in the returned snapshot.

        Args:
            status: Optional `IncidentStatus` filter.
            spell_index_id: Optional lineage-id filter.
            kind: Optional incident-kind filter.

        Returns:
            List[Incident]: Snapshot of matching incidents.

        Raises:
            RuntimeError: If the manager has already been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            result: List[Incident] = []
            for inc in self._incidents_by_id.values():
                if status is not None and inc.status is not status:
                    continue
                if (
                    spell_index_id is not None
                    and inc.spell_index_id != spell_index_id
                ):
                    continue
                if kind is not None and inc.kind != kind:
                    continue
                result.append(inc)

            return result
