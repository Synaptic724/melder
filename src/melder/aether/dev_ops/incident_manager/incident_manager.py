from __future__ import annotations
from threading import RLock
from typing import Dict, List, Optional, Any, Iterable
# Melder imports
from melder.aether.dev_ops.incident_manager.incident import Incident
from melder.aether.dev_ops.incident_manager.incident_severity import IncidentSeverity
from melder.aether.dev_ops.incident_manager.incident_status import IncidentStatus
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.data_structures.concurrent_dict import ConcurrentDict
from melder.utilities.interfaces.interfaces import IIncidentManager


class IncidentManager(IIncidentManager, Cleanable):
    """
    DevOps incident registry.

    - Creates and stores Incident objects.
    - Provides simple lookup/filtering.
    - Does not enforce any policies; it is purely descriptive.
    """

    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_incidents_by_id",
        "_next_numeric_id",
    ]

    def __init__(self) -> None:
        super().__init__()
        self._lock: RLock = RLock()
        # incident_id -> Incident
        self._incidents_by_id: ConcurrentDict[str, Incident] = ConcurrentDict({})
        self._next_numeric_id: int = 1

    def cleanup(self) -> None:
        """
        Idempotent cleanup.

        Cleans up all tracked Incident objects and the internal registry,
        then nulls references for GC friendliness.
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
                self._incidents_by_id.cleanup()
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
        Create and register a new Incident. Returns the instance so callers
        can attach it to logs/tests or stash the id.
        """
        with self._lock:
            self.check_cleaned()

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
        Look up a single incident by id. Returns None if not found.
        """
        with self._lock:
            self.check_cleaned()
            return self._incidents_by_id.get(incident_id)

    def list_incidents(
            self,
            *,
            status: Optional[IncidentStatus] = None,
            spell_index_id: Optional[str] = None,
            kind: Optional[str] = None,
    ) -> List[Incident]:
        """
        Basic filtering; returns a snapshot list of matching incidents.

        Filters:
        - status: only incidents with this IncidentStatus.
        - spell_index_id: only incidents tied to this SpellIndex.id.
        - kind: only incidents with this kind string.
        """
        with self._lock:
            self.check_cleaned()

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
