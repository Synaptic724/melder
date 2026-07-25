import threading
from typing import Dict, List, Optional, Any, Iterable, TYPE_CHECKING, ClassVar

# Melder imports
from melder.aether.aetheric_frame.dev_ops.devops_information_registry import (
    DevopsInformationRegistry,
)
from melder.aether.aetheric_frame.dev_ops.incident_manager.incident import Incident
from melder.utilities.general_base.cleanable import Cleanable
if TYPE_CHECKING:
    from melder.aether.aetheric_frame.dev_ops.incident_manager.incident_status import IncidentStatus
    from melder.aether.aetheric_frame.dev_ops.incident_manager.incident_severity import (
        IncidentSeverity,
    )



class IncidentManager(Cleanable):
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

    Threading:
        Registry mutation and id allocation are serialized internally.
        Sequential id allocation means ids are frame-local and monotonic, not
        globally unique across frames.

    Lifecycle / Cleanup:
        Owned by `DevOpsManager`. Cleanup cleans child incidents FIRST and only
        then clears the registry - children before container, matching the
        repo-wide teardown posture.

    Registration:
        MELDER KERNEL - guarded. Frame-owned; reached through `DevOpsManager`.

    Subsystem Context:
        The DESCRIPTIVE side of DevOps, deliberately opposite the decisive
        side. `RiskManager` and `ChangeControlManager` change what the runtime
        DOES; this manager only records what happened. Its records are read by
        tooling and agents, never by meld.

    System Context:
        "No policy decisions are made here" is the whole contract and it is
        worth respecting strictly. An incident registry that also gated
        behaviour would make recording a problem indistinguishable from
        reacting to one, and every diagnostic write would become a runtime
        risk. Keeping description inert means tooling can record freely -
        including speculative or noisy conditions - without any chance of
        perturbing resolution.
        This is also why the manager exposes filtering and lookup rather than
        subscriptions or hooks: consumers pull the current state when they want
        it, so an operator query can never inject latency into the runtime that
        produced the record.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Frame-local registry of `Incident` records. Melder kernel machinery: "
        "read it to understand the runtime, do not drive it directly."
    )

    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_incidents_by_id",
        "_next_numeric_id",
        "_devops_information_registry",
    ]

    def __init__(
            self,
            devops_information_registry: DevopsInformationRegistry,
    ) -> None:
        """
        Initialize the incident registry.

        Contract:
        - Starts with an empty `incident_id -> Incident` map.
        - Numeric incident ids begin at `inc-1` for a fresh manager lifetime.
        - Borrows the frame-owned dev-ops information registry for future
          reporting/enrichment consumers.

        Returns:
            None.
        """
        super().__init__()
        if devops_information_registry is None:
            raise ValueError("devops_information_registry cannot be None")
        self._lock: threading.RLock = threading.RLock()
        # incident_id -> Incident
        self._incidents_by_id: Dict[str, Incident] = {}
        self._next_numeric_id: int = 1
        self._devops_information_registry: DevopsInformationRegistry = (
            devops_information_registry
        )

    def cleanup(self) -> None:
        """
        Finalize the incident registry and its owned incidents.

        Contract:
        - Idempotent cleanup.
        - Cleans child `Incident` objects before clearing the registry.
        - Drops registry references and zeroes the numeric id counter.

        Returns:
            None.
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
            del self._devops_information_registry

        del self._lock

    @property
    def devops_information_registry(self) -> DevopsInformationRegistry:
        """
        Return the borrowed frame-owned dev-ops information registry.

        Returns:
            DevopsInformationRegistry:
                Borrowed topology/transaction registry for this frame.
        """
        
        with self._lock:
            return self._devops_information_registry

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
