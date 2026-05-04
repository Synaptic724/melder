import threading
from typing import runtime_checkable, Protocol, Optional, List, Dict, Any, Iterable

from melder.utilities.interfaces.assets.icleanable import ICleanable


@runtime_checkable
class IIncidentManager(ICleanable, Protocol):
    """
    Protocol for the DevOps incident registry.

    - Creates and stores Incident objects.
    - Provides simple lookup/filtering.
    - Does not enforce any policies; it is purely descriptive.
    """
    _lock: threading.RLock
    _incidents_by_id: 'Dict[str, Incident]'
    _next_numeric_id: int
    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def create_incident(
            self,
            *,
            kind: str,
            severity: 'IncidentSeverity',
            summary: str,
            spell_index_id: Optional[str] = None,
            root_ids: Optional[Iterable[str]] = None,
            details: Optional[Dict[str, Any]] = None,
    ) -> 'Incident':
        """
        Create and register a new Incident. Returns the instance so callers
        can attach it to logs/tests or stash the id.
        """
        ...

    def get_incident(self, incident_id: str) -> Optional['Incident']:
        """
        Look up a single incident by id. Returns None if not found.
        """
        ...

    def list_incidents(
            self,
            *,
            status: Optional['IncidentStatus'] = None,
            spell_index_id: Optional[str] = None,
            kind: Optional[str] = None,
    ) -> List['Incident']:
        """
        Basic filtering; returns a snapshot list of matching incidents.

        Filters:
        - status: only incidents with this IncidentStatus.
        - spell_index_id: only incidents tied to this SpellIndex.id.
        - kind: only incidents with this kind string.
        """
        ...
