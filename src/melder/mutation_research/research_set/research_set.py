import threading
from datetime import datetime, timezone
from typing import Callable, ClassVar, Dict, List, Optional

from melder.mutation_research.research_set.network_versioner import (
    NetworkVersioner,
)
from melder.mutation_research.research_set.research_journal import (
    ResearchJournal,
)
from melder.mutation_research.research_set.research_lane import (
    LaneState,
    ResearchLane,
)
from melder.mutation_research.research_set.research_node import ResearchNode
from melder.mutation_research.research_set.residence_registry import (
    ResidenceRegistry,
)
from melder.mutation_research.research_set.transition_entry import (
    TransitionAct,
    TransitionEntry,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class ResearchSet(Cleanable):
    """
    The overarching research network: every lane, one journal, one partition.

    Purpose:
        The single agent-facing surface of MutationResearch. Agents formally
        declare bound versions as research (`register_spell`), organize lanes
        (`create_lane`, `attach`, `detach`), finish lines (`join`), retire
        dead ends (`archive`), and read the record (`walk`, `history`,
        `heads`). The organization itself is version-controlled
        (`snapshot_network` / `restore_network`) because objects are
        indestructible - only their arrangement is at risk.

    Contract:
        - SINGLE RESIDENCE: one binding-signature SHA256 lives in exactly ONE
          lane network-wide, permanently (through archive). Identical content
          rebinds to the same SHA and surfaces as a rediscovery error naming
          the holding lane.
        - Forward-only history: every verb journals a world-entry event; the
          journal is append-only and SURVIVES network restore.
        - A guaranteed `default` lane exists from birth; `register_spell`
          without an explicit lane records there (no orphan binds, no
          history holes).
        - Every mutating verb re-snapshots the organization and fires the
          injected `on_mutation` callback (the persistence emission seam) -
          this object itself never touches the crystallizer (dependency
          rule: only the MutationResearch root emits).
        - No merge/rebase primitives exist: content combination happens in
          the codegen workshop and re-enters as a multi-parent
          `register_spell`; `attach` covers the organizational
          "move my line onto that base" act.

    Threading:
        Instance `RLock` serializes verbs; child structures carry their own
        locks; lock order is set -> child, one-way.

    Lifecycle:
        Owned by exactly one `MutationResearch` root; `cleanup()` cascades
        into lanes, journal, residence, and versioner; idempotent; lock
        released last.
    """

    DEFAULT_LANE_NAME: ClassVar[str] = "default"

    __slots__ = Cleanable.__slots__ + [
        "_set_id",
        "_name",
        "_lanes_by_id",
        "_lane_id_by_name",
        "_journal",
        "_residence",
        "_versioner",
        "_on_mutation",
        "_created_at",
        "_lock",
    ]

    def __init__(
            self,
            name: str = "default",
            *,
            max_network_snapshots: int = 64,
            on_mutation: Optional[Callable[[], None]] = None,
    ) -> None:
        """
        Initialize one research set with its guaranteed default lane.

        Args:
            name:
                Set name (uniqueness enforced by the owning root registry).
            max_network_snapshots:
                FIFO retention bound for organization snapshots.
            on_mutation:
                Optional callback fired after every successful mutating verb
                (the root installs its persistence emission closure here; the
                set stays crystallizer-free and standalone-testable).

        Raises:
            ValueError:
                If name is empty.
        """
        super().__init__()
        if not isinstance(name, str) or not name:
            raise ValueError("name must be a non-empty string.")
        self._set_id: str = IDBuilder.create_id()
        self._name: str = name
        self._lanes_by_id: Dict[str, ResearchLane] = {}
        self._lane_id_by_name: Dict[str, str] = {}
        self._journal: ResearchJournal = ResearchJournal()
        self._residence: ResidenceRegistry = ResidenceRegistry()
        self._versioner: NetworkVersioner = NetworkVersioner(
            max_snapshots=max_network_snapshots,
        )
        self._on_mutation: Optional[Callable[[], None]] = on_mutation
        self._created_at: str = datetime.now(timezone.utc).isoformat()
        self._lock: threading.RLock = threading.RLock()
        with self._lock:
            self._create_lane_locked(ResearchSet.DEFAULT_LANE_NAME)
            self._snapshot_locked()
        self._notify_mutation()

    def cleanup(self) -> None:
        """
        Cascade cleanup into owned structures and mark the set cleaned.

        Contract:
            - Idempotent; del posture (no tombstones); lock last.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            for lane in self._lanes_by_id.values():
                try:
                    lane.cleanup()
                except Exception:
                    pass
            self._lanes_by_id.clear()
            self._lane_id_by_name.clear()
            try:
                self._journal.cleanup()
            except Exception:
                pass
            try:
                self._residence.cleanup()
            except Exception:
                pass
            try:
                self._versioner.cleanup()
            except Exception:
                pass
            del self._lanes_by_id
            del self._lane_id_by_name
            del self._journal
            del self._residence
            del self._versioner
            del self._on_mutation
            del self._created_at
            del self._name
            del self._set_id
        del self._lock

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _notify_mutation(self) -> None:
        """
        Fire the injected mutation callback, when installed.

        Contract:
            - Called after the verb's own state is fully committed and
              journaled; callback failures propagate (recording problems are
              never silent).
        """
        callback = self._on_mutation
        if callback is not None:
            callback()

    def _resolve_lane_locked(self, lane_ref: str) -> ResearchLane:
        """
        Resolve one lane by name first, then by id (caller holds the lock).

        Args:
            lane_ref:
                Lane name or lane id.

        Returns:
            ResearchLane:
                Resolved lane.

        Raises:
            KeyError:
                If nothing matches; the error names the known lanes.
        """
        lane_id = self._lane_id_by_name.get(lane_ref)
        if lane_id is not None:
            return self._lanes_by_id[lane_id]
        lane = self._lanes_by_id.get(lane_ref)
        if lane is not None:
            return lane
        known = sorted(self._lane_id_by_name.keys())
        raise KeyError(
            f"Research set '{self._name}' has no lane '{lane_ref}'. "
            f"Known lanes: {known}."
        )

    def _create_lane_locked(
            self,
            name: str,
            *,
            metadata: Optional[Dict[str, object]] = None,
    ) -> ResearchLane:
        """
        Create and index one open lane (caller holds the lock).

        Args:
            name:
                Unique lane name within this set.
            metadata:
                Optional value-typed annotations.

        Returns:
            ResearchLane:
                Newly created lane.

        Raises:
            ValueError:
                If the name is already taken.
        """
        if name in self._lane_id_by_name:
            raise ValueError(
                f"Research set '{self._name}' already has a lane named "
                f"'{name}'."
            )
        lane = ResearchLane(name, metadata=metadata)
        self._lanes_by_id[lane.lane_id] = lane
        self._lane_id_by_name[name] = lane.lane_id
        return lane

    def _organization_payload_locked(self) -> Dict[str, object]:
        """
        Build the detached organization payload (caller holds the lock).

        Contract:
            - Organization only: lanes (with nodes) + residence. The journal
              is excluded by design so restore never rewinds history.

        Returns:
            Dict[str, object]:
                Detached organization payload.
        """
        return {
            "set_id": self._set_id,
            "name": self._name,
            "created_at": self._created_at,
            "lanes": [
                self._lanes_by_id[lane_id].describe()
                for lane_id in sorted(self._lanes_by_id.keys())
            ],
            "residence": self._residence.describe(),
        }

    def _snapshot_locked(self) -> str:
        """
        Snapshot the current organization (caller holds the lock).

        Returns:
            str:
                Content address of the organization snapshot.
        """
        return self._versioner.snapshot(self._organization_payload_locked())

    # ------------------------------------------------------------------
    # Identity and reads
    # ------------------------------------------------------------------

    @property
    def set_id(self) -> str:
        """
        Return the stable set id (ULID).

        Returns:
            str:
                Set id.
        """
        self.check_cleaned()
        return self._set_id

    @property
    def name(self) -> str:
        """
        Return the set name.

        Returns:
            str:
                Set name.
        """
        self.check_cleaned()
        return self._name

    @property
    def default_lane(self) -> ResearchLane:
        """
        Return the guaranteed default lane.

        Returns:
            ResearchLane:
                The set's default lane.
        """
        self.check_cleaned()
        with self._lock:
            return self._resolve_lane_locked(ResearchSet.DEFAULT_LANE_NAME)

    @property
    def journal(self) -> ResearchJournal:
        """
        Return the set-level forward-only journal.

        Returns:
            ResearchJournal:
                Owned journal (append-only; callers read, never edit).
        """
        self.check_cleaned()
        return self._journal

    def get_lane(self, lane_ref: str) -> ResearchLane:
        """
        Return one lane by name or id.

        Args:
            lane_ref:
                Lane name or lane id.

        Returns:
            ResearchLane:
                Resolved lane.

        Raises:
            KeyError:
                If nothing matches.
        """
        self.check_cleaned()
        with self._lock:
            return self._resolve_lane_locked(lane_ref)

    def lane_names(self) -> List[str]:
        """
        Return every lane name in this set, sorted.

        Returns:
            List[str]:
                Sorted lane names.
        """
        self.check_cleaned()
        with self._lock:
            return sorted(self._lane_id_by_name.keys())

    def residence_of(self, spell_sha: str) -> Optional[str]:
        """
        Return the lane id holding one identity, when resident.

        Args:
            spell_sha:
                Identity to look up.

        Returns:
            Optional[str]:
                Holding lane id or None.
        """
        self.check_cleaned()
        return self._residence.residence_of(spell_sha)

    def heads(self) -> Dict[str, Optional[str]]:
        """
        Return the tip identity of every OPEN lane.

        Returns:
            Dict[str, Optional[str]]:
                lane name -> tip SHA256 (None for empty lanes).
        """
        self.check_cleaned()
        with self._lock:
            result: Dict[str, Optional[str]] = {}
            for name, lane_id in self._lane_id_by_name.items():
                lane = self._lanes_by_id[lane_id]
                if lane.state is LaneState.open:
                    result[name] = lane.tip_sha
            return result

    def walk(self, lane_ref: str) -> List[Dict[str, object]]:
        """
        Return one lane's line of versions with its ancestry hop.

        Purpose:
            The read verb for "tell me this object's story": ordered
            full-object records plus the anchor pointer that lets the caller
            hop into the transitive network.

        Args:
            lane_ref:
                Lane name or lane id.

        Returns:
            List[Dict[str, object]]:
                Ordered node payloads; each carries `lane_id`, `lane_name`,
                `anchor_lane_id`, and `anchor_sha` alongside the node fields.
        """
        self.check_cleaned()
        with self._lock:
            lane = self._resolve_lane_locked(lane_ref)
            steps: List[Dict[str, object]] = []
            for node in lane.nodes():
                step = node.describe()
                step["lane_id"] = lane.lane_id
                step["lane_name"] = lane.name
                step["anchor_lane_id"] = lane.anchor_lane_id
                step["anchor_sha"] = lane.anchor_sha
                steps.append(step)
            return steps

    def history(self, spell_sha: str) -> Dict[str, object]:
        """
        Return everything the record knows about one identity.

        Args:
            spell_sha:
                Identity to report on.

        Returns:
            Dict[str, object]:
                Payload with the holding lane, the node record, and every
                journal event touching the identity.

        Raises:
            KeyError:
                If the identity is not resident in this set.
        """
        self.check_cleaned()
        with self._lock:
            lane_id = self._residence.residence_of(spell_sha)
            if lane_id is None:
                raise KeyError(
                    f"Identity '{spell_sha}' is not resident in research "
                    f"set '{self._name}'."
                )
            lane = self._lanes_by_id[lane_id]
            return {
                "spell_sha": spell_sha,
                "lane_id": lane_id,
                "lane_name": lane.name,
                "lane_state": lane.state.value,
                "node": lane.get_node(spell_sha).describe(),
                "transitions": [
                    entry.describe()
                    for entry in self._journal.entries_for_sha(spell_sha)
                ],
            }

    # ------------------------------------------------------------------
    # Mutating verbs
    # ------------------------------------------------------------------

    def create_lane(
            self,
            name: str,
            *,
            attach_to: Optional[str] = None,
            attach_at_sha: Optional[str] = None,
            actor: Optional[str] = None,
            campaign: Optional[str] = None,
            reason: Optional[str] = None,
            metadata: Optional[Dict[str, object]] = None,
    ) -> ResearchLane:
        """
        Create one open lane, optionally anchored onto an existing node.

        Args:
            name:
                Unique lane name within this set.
            attach_to:
                Optional lane (name or id) to anchor onto; requires
                attach_at_sha.
            attach_at_sha:
                Node identity within `attach_to` to anchor at.
            actor:
                Optional acting agent name.
            campaign:
                Optional research-campaign stamp.
            reason:
                Optional reason line.
            metadata:
                Optional value-typed annotations.

        Returns:
            ResearchLane:
                Newly created lane.

        Raises:
            ValueError:
                If the name is taken, or anchor arguments are half-supplied.
            KeyError:
                If `attach_to` does not resolve, or the anchor node is not
                held by that lane.
        """
        self.check_cleaned()
        if (attach_to is None) != (attach_at_sha is None):
            raise ValueError(
                "attach_to and attach_at_sha must be supplied together."
            )
        with self._lock:
            anchor_lane: Optional[ResearchLane] = None
            if attach_to is not None:
                anchor_lane = self._resolve_lane_locked(attach_to)
                if not anchor_lane.has_node(attach_at_sha):
                    raise KeyError(
                        f"Lane '{anchor_lane.name}' holds no identity "
                        f"'{attach_at_sha}' to anchor at."
                    )
            lane = self._create_lane_locked(name, metadata=metadata)
            entry_metadata: Dict[str, object] = {}
            if anchor_lane is not None:
                lane.set_anchor(anchor_lane.lane_id, attach_at_sha)
                entry_metadata["anchor_lane_id"] = anchor_lane.lane_id
                entry_metadata["anchor_lane_name"] = anchor_lane.name
            self._journal.record(
                TransitionAct.lane_created,
                lane.lane_id,
                from_sha=attach_at_sha,
                actor=actor,
                campaign=campaign,
                reason=reason,
                metadata=entry_metadata,
            )
            self._snapshot_locked()
        self._notify_mutation()
        return lane

    def register_spell(
            self,
            spell_sha: str,
            *,
            lane: Optional[str] = None,
            module_sha: Optional[str] = None,
            parent_shas: Optional[List[str]] = None,
            author: Optional[str] = None,
            campaign: Optional[str] = None,
            reason: Optional[str] = None,
            metadata: Optional[Dict[str, object]] = None,
    ) -> ResearchNode:
        """
        Formally declare one bound version as research.

        Purpose:
            The world-entry verb: the version already exists (it was bound;
            its SHA is minted; custody rides the crystal that shares the same
            id). This records that the version is part of a research stream.

        Args:
            spell_sha:
                Binding-signature SHA256 (doubles as the custody crystal id).
            lane:
                Optional lane (name or id); the guaranteed default lane
                records the version when omitted.
            module_sha:
                Optional module-version SHA256 the version binds against.
            parent_shas:
                Optional ancestry; every parent must already be resident in
                this set (multi-parent = codegen-workshop composition).
            author:
                Optional registering agent name.
            campaign:
                Optional research-campaign stamp.
            reason:
                Optional reason line.
            metadata:
                Optional value-typed annotations.

        Returns:
            ResearchNode:
                The recorded version node.

        Raises:
            RuntimeError:
                Rediscovery - the identity already resides in a lane (the
                error names it); or the target lane is not open.
            ValueError:
                If a parent identity is unknown to this set.
        """
        self.check_cleaned()
        with self._lock:
            target = self._resolve_lane_locked(
                lane if lane is not None else ResearchSet.DEFAULT_LANE_NAME,
            )
            parents = list(parent_shas) if parent_shas else []
            for parent_sha in parents:
                if not self._residence.is_resident(parent_sha):
                    raise ValueError(
                        f"Parent identity '{parent_sha}' is not resident in "
                        f"research set '{self._name}'; ancestry must "
                        f"reference formally declared versions."
                    )
            node = ResearchNode(
                spell_sha,
                module_sha=module_sha,
                parent_shas=parents,
                author=author,
                reason=reason,
                campaign=campaign,
                metadata=metadata,
            )
            self._residence.claim(spell_sha, target.lane_id)
            target.add_node(node)
            self._journal.record(
                TransitionAct.registered,
                target.lane_id,
                to_sha=spell_sha,
                actor=author,
                campaign=campaign,
                reason=reason,
                metadata={"module_sha": module_sha, "parent_shas": parents},
            )
            self._snapshot_locked()
        self._notify_mutation()
        return node

    def attach(
            self,
            lane_ref: str,
            *,
            onto: str,
            at_sha: str,
            actor: Optional[str] = None,
            campaign: Optional[str] = None,
            reason: Optional[str] = None,
    ) -> None:
        """
        Anchor one lane's ancestry onto another lane's node.

        Contract:
            - Organization only: content never moves; `onto`/`at_sha` are
              mandatory so the act is never scope-blind.

        Args:
            lane_ref:
                Lane (name or id) being organized.
            onto:
                Lane (name or id) to anchor onto.
            at_sha:
                Node identity within `onto` to anchor at.
            actor:
                Optional acting agent name.
            campaign:
                Optional research-campaign stamp.
            reason:
                Optional reason line.

        Raises:
            RuntimeError:
                If the subject lane is not open, or anchoring onto itself.
            KeyError:
                If lanes or the anchor node do not resolve.
        """
        self.check_cleaned()
        with self._lock:
            lane = self._resolve_lane_locked(lane_ref)
            target = self._resolve_lane_locked(onto)
            if lane.lane_id == target.lane_id:
                raise RuntimeError(
                    f"Lane '{lane.name}' cannot anchor onto itself."
                )
            if not target.has_node(at_sha):
                raise KeyError(
                    f"Lane '{target.name}' holds no identity '{at_sha}' to "
                    f"anchor at."
                )
            lane.set_anchor(target.lane_id, at_sha)
            self._journal.record(
                TransitionAct.attached,
                lane.lane_id,
                to_sha=at_sha,
                actor=actor,
                campaign=campaign,
                reason=reason,
                metadata={
                    "anchor_lane_id": target.lane_id,
                    "anchor_lane_name": target.name,
                },
            )
            self._snapshot_locked()
        self._notify_mutation()

    def detach(
            self,
            lane_ref: str,
            *,
            actor: Optional[str] = None,
            campaign: Optional[str] = None,
            reason: Optional[str] = None,
    ) -> None:
        """
        Remove one lane's ancestry anchor.

        Args:
            lane_ref:
                Lane (name or id) being organized.
            actor:
                Optional acting agent name.
            campaign:
                Optional research-campaign stamp.
            reason:
                Optional reason line.

        Raises:
            RuntimeError:
                If the lane is not open or holds no anchor.
        """
        self.check_cleaned()
        with self._lock:
            lane = self._resolve_lane_locked(lane_ref)
            previous_anchor = lane.anchor_sha
            lane.clear_anchor()
            self._journal.record(
                TransitionAct.detached,
                lane.lane_id,
                from_sha=previous_anchor,
                actor=actor,
                campaign=campaign,
                reason=reason,
            )
            self._snapshot_locked()
        self._notify_mutation()

    def join(
            self,
            lane_ref: str,
            *,
            into: str,
            collapse: bool = False,
            force: bool = False,
            actor: Optional[str] = None,
            campaign: Optional[str] = None,
            reason: Optional[str] = None,
    ) -> ResearchLane:
        """
        Finish one lane into a receiving lane; the source archives.

        Contract:
            - Divergence-aware: the clean path requires the source to be
              anchored onto `into` with the receiving tip still AT the
              anchor. Any other arrangement (moved tip, foreign anchor, no
              anchor) is a divergent join and requires `force=True` - the
              explicit supersede. Reconciliation-by-content is not a join
              concern: compose in the codegen workshop, register the
              multi-parent result, then join.
            - `collapse=False` (default) folds the source's full line into
              the receiver; `collapse=True` moves only the tip, leaving the
              rest readable in the joined (terminal) source container.
            - Residence transfers with the moved records; the source is
              marked joined and accepts no further work.

        Args:
            lane_ref:
                Source lane (name or id) to finish.
            into:
                Receiving lane (name or id).
            collapse:
                Move only the tip when True.
            force:
                Permit a divergent join (explicit supersede).
            actor:
                Optional acting agent name.
            campaign:
                Optional research-campaign stamp.
            reason:
                Optional reason line.

        Returns:
            ResearchLane:
                The receiving lane.

        Raises:
            RuntimeError:
                On self-join, non-open lanes, or unforced divergence (the
                error names both tips).
        """
        self.check_cleaned()
        with self._lock:
            source = self._resolve_lane_locked(lane_ref)
            target = self._resolve_lane_locked(into)
            if source.lane_id == target.lane_id:
                raise RuntimeError(
                    f"Lane '{source.name}' cannot join into itself."
                )
            if target.state is not LaneState.open:
                raise RuntimeError(
                    f"Receiving lane '{target.name}' is "
                    f"{target.state.value}; join requires an open receiver."
                )
            clean = (
                source.anchor_lane_id == target.lane_id
                and source.anchor_sha is not None
                and target.tip_sha == source.anchor_sha
            )
            if not clean and not force:
                raise RuntimeError(
                    f"Divergent join: lane '{source.name}' anchors at "
                    f"'{source.anchor_sha}' on lane "
                    f"'{source.anchor_lane_id}' while receiver "
                    f"'{target.name}' tips at '{target.tip_sha}'. Compose a "
                    f"reconciling version in the codegen workshop and "
                    f"register it, or pass force=True to supersede."
                )
            previous_target_tip = target.tip_sha
            moved_shas: List[str] = []
            if source.node_count > 0:
                if collapse:
                    moved_shas = [source.tip_sha]
                else:
                    moved_shas = source.node_shas()
                for node in source.detach_nodes(moved_shas):
                    target.add_node(node)
                self._residence.transfer(moved_shas, target.lane_id)
            source.mark_joined(target.lane_id)
            self._journal.record(
                TransitionAct.joined,
                target.lane_id,
                from_sha=previous_target_tip,
                to_sha=target.tip_sha,
                actor=actor,
                campaign=campaign,
                reason=reason,
                metadata={
                    "joined_lane_id": source.lane_id,
                    "joined_lane_name": source.name,
                    "collapse": collapse,
                    "forced": bool(not clean),
                    "moved_shas": moved_shas,
                },
            )
            self._snapshot_locked()
        self._notify_mutation()
        return target

    def archive(
            self,
            lane_ref: str,
            *,
            actor: Optional[str] = None,
            campaign: Optional[str] = None,
            reason: Optional[str] = None,
    ) -> None:
        """
        Retire one dead-end lane from the active view.

        Contract:
            - The default lane never archives.
            - Residence stays permanent: rediscovery keeps pointing at the
              archived container; network snapshots can restore views that
              contained it.

        Args:
            lane_ref:
                Lane (name or id) to archive.
            actor:
                Optional acting agent name.
            campaign:
                Optional research-campaign stamp.
            reason:
                Optional reason line.

        Raises:
            RuntimeError:
                If targeting the default lane or a non-open lane.
        """
        self.check_cleaned()
        with self._lock:
            lane = self._resolve_lane_locked(lane_ref)
            if lane.name == ResearchSet.DEFAULT_LANE_NAME:
                raise RuntimeError(
                    "The default lane is the guaranteed world-entry record "
                    "and never archives."
                )
            lane.mark_archived()
            self._journal.record(
                TransitionAct.archived,
                lane.lane_id,
                actor=actor,
                campaign=campaign,
                reason=reason,
            )
            self._snapshot_locked()
        self._notify_mutation()

    # ------------------------------------------------------------------
    # Network version control
    # ------------------------------------------------------------------

    def snapshot_network(self) -> str:
        """
        Explicitly snapshot the current organization.

        Returns:
            str:
                Content address of the organization snapshot (mutating verbs
                already snapshot automatically; this is the manual seal).
        """
        self.check_cleaned()
        with self._lock:
            return self._snapshot_locked()

    def network_snapshot_shas(self) -> List[str]:
        """
        Return retained organization snapshot addresses, oldest first.

        Returns:
            List[str]:
                Detached ordered address list.
        """
        self.check_cleaned()
        return self._versioner.snapshot_shas()

    @property
    def latest_network_snapshot(self) -> Optional[str]:
        """
        Return the newest retained organization snapshot address.

        Returns:
            Optional[str]:
                Newest address or None.
        """
        self.check_cleaned()
        return self._versioner.latest_sha

    def restore_network(
            self,
            snapshot_sha: str,
            *,
            actor: Optional[str] = None,
            reason: Optional[str] = None,
    ) -> None:
        """
        Rebuild the organization from one content-addressed snapshot.

        Contract:
            - Recovery mechanic for organizational mistakes: lanes and
              residence rebuild wholesale from the snapshot; the journal is
              untouched (history is never rewound) and the restore itself is
              journaled forward as a `restored` event.

        Args:
            snapshot_sha:
                Content address to restore.
            actor:
                Optional acting agent name.
            reason:
                Optional reason line.

        Raises:
            KeyError:
                If the address is unknown (possibly aged out of retention).
        """
        self.check_cleaned()
        with self._lock:
            payload = self._versioner.get(snapshot_sha)
            lane_payloads = payload.get("lanes")
            residence_payload = payload.get("residence")
            if not isinstance(lane_payloads, list) or not isinstance(
                    residence_payload, dict
            ):
                raise ValueError(
                    f"Snapshot '{snapshot_sha}' carries an invalid "
                    f"organization payload."
                )
            rebuilt_lanes: Dict[str, ResearchLane] = {}
            rebuilt_names: Dict[str, str] = {}
            for lane_payload in lane_payloads:
                lane = ResearchLane.from_payload(lane_payload)
                rebuilt_lanes[lane.lane_id] = lane
                rebuilt_names[lane.name] = lane.lane_id
            rebuilt_residence = ResidenceRegistry.from_payload(
                residence_payload,
            )
            for lane in self._lanes_by_id.values():
                try:
                    lane.cleanup()
                except Exception:
                    pass
            try:
                self._residence.cleanup()
            except Exception:
                pass
            self._lanes_by_id = rebuilt_lanes
            self._lane_id_by_name = rebuilt_names
            self._residence = rebuilt_residence
            self._journal.record(
                TransitionAct.restored,
                self._set_id,
                to_sha=snapshot_sha,
                actor=actor,
                reason=reason,
            )
            self._snapshot_locked()
        self._notify_mutation()

    # ------------------------------------------------------------------
    # Payload seams
    # ------------------------------------------------------------------

    def describe_composition(
            self,
            *,
            recent_transitions: Optional[int] = 200,
    ) -> Dict[str, object]:
        """
        Return the detached persistence payload for this set.

        Purpose:
            The twin feed: full organization plus a bounded recent journal
            window (checkpoints capture the deltas over time, so the twin
            never needs the unbounded stream).

        Args:
            recent_transitions:
                Journal window bound; None includes the full stream.

        Returns:
            Dict[str, object]:
                Plain-value payload with `organization`, `journal`, and
                `network_snapshot_shas`.
        """
        self.check_cleaned()
        with self._lock:
            return {
                "organization": self._organization_payload_locked(),
                "journal": self._journal.describe(recent=recent_transitions),
                "network_snapshot_shas": self._versioner.snapshot_shas(),
            }

    def describe(self) -> Dict[str, object]:
        """
        Return the default detached snapshot of this set.

        Returns:
            Dict[str, object]:
                `describe_composition()` with the default journal window.
        """
        return self.describe_composition()

    @classmethod
    def from_payload(
            cls,
            payload: Dict[str, object],
            *,
            on_mutation: Optional[Callable[[], None]] = None,
    ) -> "ResearchSet":
        """
        Rebuild one set from a `describe_composition()` payload.

        Purpose:
            The hydration seam: a recorded composition (from the
            MutationResearchCrystal twin) rebuilds into a live set. The
            journal rebuilds from the recorded window and continues minting
            beyond the recorded `next_sequence`.

        Args:
            payload:
                Detached payload produced by `describe_composition()`.
            on_mutation:
                Optional callback installed on the rebuilt set.

        Returns:
            ResearchSet:
                Reconstructed set.

        Raises:
            ValueError:
                If the payload shape is invalid.
        """
        if not isinstance(payload, dict):
            raise ValueError(
                "payload must be a dict produced by describe_composition()."
            )
        organization = payload.get("organization")
        journal_payload = payload.get("journal")
        if not isinstance(organization, dict) or not isinstance(
                journal_payload, dict
        ):
            raise ValueError(
                "payload is missing 'organization'/'journal' values."
            )
        name = organization.get("name")
        set_id = organization.get("set_id")
        lane_payloads = organization.get("lanes")
        residence_payload = organization.get("residence")
        if not isinstance(name, str) or not isinstance(lane_payloads, list):
            raise ValueError(
                "organization payload is missing 'name'/'lanes' values."
            )
        research_set = cls(name, on_mutation=None)
        with research_set._lock:
            for lane in research_set._lanes_by_id.values():
                try:
                    lane.cleanup()
                except Exception:
                    pass
            try:
                research_set._residence.cleanup()
            except Exception:
                pass
            try:
                research_set._journal.cleanup()
            except Exception:
                pass
            research_set._lanes_by_id = {}
            research_set._lane_id_by_name = {}
            for lane_payload in lane_payloads:
                lane = ResearchLane.from_payload(lane_payload)
                research_set._lanes_by_id[lane.lane_id] = lane
                research_set._lane_id_by_name[lane.name] = lane.lane_id
            research_set._residence = (
                ResidenceRegistry.from_payload(residence_payload)
                if isinstance(residence_payload, dict)
                else ResidenceRegistry()
            )
            research_set._journal = ResearchJournal.from_payload(
                journal_payload,
            )
            if isinstance(set_id, str) and set_id:
                research_set._set_id = set_id
            recorded_created_at = organization.get("created_at")
            if isinstance(recorded_created_at, str) and recorded_created_at:
                research_set._created_at = recorded_created_at
            research_set._snapshot_locked()
            research_set._on_mutation = on_mutation
        return research_set
