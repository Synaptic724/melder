import threading
from datetime import datetime, timezone
from typing import Callable, ClassVar, Dict, List, Optional

from melder.mutation_research.research_set.network_versioner import (
    NetworkVersioner,
)
from melder.mutation_research.research_set.research_journal import (
    ResearchJournal,
)
from melder.mutation_research.research_set.grouped_research_node import (
    GroupedResearchNode,
)
from melder.mutation_research.research_set.research_lane import (
    LaneState,
    LaneType,
    ResearchLane,
    node_identity,
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

    Registration:
        MELDER KERNEL - guarded. Obtained through `MutationResearch.research_set()`
        or `create_research_set()`; a user drives it rather than registering it.

    WHY LANES ARE READ-ONLY IN PUBLIC HANDS:
        `ResearchLane` objects are handed out LIVE, but every lane mutator is
        set-internal. That is not encapsulation for its own sake: residence
        claims, journal entries, organization snapshots, and persistence
        emission all hang off THIS object. A public lane mutator would let a
        caller change the network while bypassing all four, leaving the
        partition, the history, and the record disagreeing about what happened.

        So the rule is: public callers read lanes, the owning set writes them.

    Subsystem Context:
        The agent-facing surface of the whole package, composing four
        bookkeeping structures that each answer one question -
        `ResidenceRegistry` (is this identity already somewhere),
        `ResearchJournal` (what happened, in order), `NetworkVersioner` (what
        the organization used to look like), and the lanes themselves (where
        things are now). It deliberately never touches the crystallizer: it
        fires `on_mutation` and the ROOT does the emitting.

    System Context:
        This is where the model's central conviction lives - full-object records
        rather than diffs. A version is stored whole, so understanding change is
        a derived READ through the diff engines rather than a reconstruction.
        The absence of merge and rebase follows from the same conviction:
        combining content happens in the codegen workshop and re-enters as a
        multi-parent `register_spell`, so the record only ever gains facts. It
        never rewrites them.

    AGENT_ACCESS: public

    AGENT_PURPOSE:
        access: public. One research network - lanes, journal, residence partition. Use
        register_spell/register_group, create_lane, attach/detach, join, archive,
        walk/history/heads, campaign_view, snapshot_network/restore_network.
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
        "_lane_type_enforcement",
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

        Contract:
            - CREATES THE DEFAULT LANE EAGERLY and snapshots once, so the
              guaranteed-default-lane invariant holds from construction - every
              other verb can assume the default lane exists.
            - The default lane is typed `development`; freeform lanes created
              later default to `experiment`. The difference is deliberate.
            - CONFIGURATION-FREE BY DESIGN. The set owns no configuration object;
              `on_mutation` and `lane_type_enforcement` are pushed in from
              outside (the root installs its persistence-emission closure as
              `on_mutation`). This is what makes a `ResearchSet` constructible
              and testable without a live crystallizer or configuration.
            - `on_mutation` FIRES ONCE DURING CONSTRUCTION, after the default
              lane and its snapshot land. A callback installed here must tolerate
              being called before the caller finishes wiring the set up.
            - Name UNIQUENESS is NOT enforced here - that is the owning root
              registry's job. This constructor only rejects an empty name.

        Owned State:
            Owns its id, name, lane maps, journal, residence registry, network
            versioner, lock, and the `on_mutation` reference. Every one is torn
            down in `cleanup`.

        Threading:
            The default-lane creation and first snapshot run under the freshly
            created `self._lock`; construction is otherwise unsynchronized
            because the object is not yet shared.

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

        Returns:
            None.
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
        self._lane_type_enforcement: bool = False
        self._created_at: str = datetime.now(timezone.utc).isoformat()
        self._lock: threading.RLock = threading.RLock()
        with self._lock:
            self._create_lane_locked(
                ResearchSet.DEFAULT_LANE_NAME,
                lane_type=LaneType.development.value,
            )
            self._snapshot_locked()
        self._notify_mutation()

    def cleanup(self) -> None:
        """
        Cascade cleanup into owned structures and mark the set cleaned.

        Contract:
            - IDEMPOTENT under double-checked locking: the `_cleaned` flag is
              tested before AND after taking the lock, so concurrent callers
              cannot both run teardown.
            - CHILDREN FIRST, in dependency order: every lane, then the journal,
              residence registry and versioner, each under its own best-effort
              `try/except` so one failing child cannot strand the rest.
            - DELETE-NOT-NULL posture. Owned fields are removed with `del`, not
              set to None - there are no retained tombstones, so any use after
              cleanup raises `AttributeError` rather than reading a stale value.
            - THE LOCK IS DELETED LAST, outside the guarded block, after every
              owned reference is gone. That ordering means the object is fully
              stripped before the lock that protected the teardown disappears.
            - Does NOT fire `on_mutation`. Cleanup is a teardown, not a mutating
              verb, so no persistence emission is triggered.

        Threading:
            The teardown body runs under `self._lock`; the final `del self._lock`
            is the one step outside it.

        Returns:
            None.
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
            del self._lane_type_enforcement
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

    def _resident_node_kind_locked(self, identity: str) -> Optional[str]:
        """
        Classify one identity's resident node kind (caller holds the lock).

        Purpose:
            Spell and composition identities live in separate namespaces:
            spell nodes carry source/custody state; composition
            (GroupedResearchNode) identities are purely informational.
            Ancestry and membership validation uses this classifier so the
            two namespaces cannot accept each other's IDs.

        Args:
            identity:
                Spell or composition identity to classify.

        Returns:
            Optional[str]:
                "group" when the resident node is a GroupedResearchNode,
                "spell" when it is a spell ResearchNode, None when the
                identity is not resident in this set.
        """
        lane_id = self._residence.residence_of(identity)
        if lane_id is None:
            return None
        node = self._lanes_by_id[lane_id].get_node(identity)
        return (
            "group" if isinstance(node, GroupedResearchNode) else "spell"
        )

    @staticmethod
    def _validate_campaign(campaign: Optional[str]) -> None:
        """
        Refuse campaign stamps the public query API cannot address.

        Purpose:
            Write/read agreement (BUG-047): `campaign_view` rejects empty
            identifiers, so the write seams must refuse them too - a public
            write may never create a record the public query API cannot
            reach.

        Args:
            campaign:
                Optional research-campaign stamp to validate.

        Raises:
            ValueError:
                If a campaign is supplied but is not a non-empty string.
        """
        if campaign is not None and (
                not isinstance(campaign, str) or not campaign
        ):
            raise ValueError(
                "campaign must be a non-empty string when supplied; an "
                "empty stamp would be unqueryable through campaign_view."
            )

    def _create_lane_locked(
            self,
            name: str,
            *,
            lane_type: Optional[str] = None,
            metadata: Optional[Dict[str, object]] = None,
    ) -> ResearchLane:
        """
        Create and index one open lane (caller holds the lock).

        Args:
            name:
                Unique lane name within this set.
            lane_type:
                Optional policy vocabulary word (`LaneType` value);
                `experiment` when omitted.
            metadata:
                Optional value-typed annotations.

        Returns:
            ResearchLane:
                Newly created lane.

        Raises:
            ValueError:
                If the name is already taken, or the lane_type is unknown.
        """
        if name in self._lane_id_by_name:
            raise ValueError(
                f"Research set '{self._name}' already has a lane named "
                f"'{name}'."
            )
        lane = ResearchLane(name, lane_type=lane_type, metadata=metadata)
        self._lanes_by_id[lane.lane_id] = lane
        self._lane_id_by_name[name] = lane.lane_id
        return lane

    # ------------------------------------------------------------------
    # Lane-type policy posture
    # ------------------------------------------------------------------

    @property
    def lane_type_enforcement(self) -> bool:
        """
        Return whether type-mixing joins currently require force.

        Contract:
            - Reports whether lane-type rules are enforced for this set. When off,
              lane-type mismatches are permitted rather than rejected, so a set can
              hold members its lane types would otherwise refuse.

        Threading:
            Reads under `self._lock`, so the result is a coherent snapshot.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the research set has been cleaned.

        Returns:
            bool:
                True when the join gate is armed.
        """
        self.check_cleaned()
        with self._lock:
            return self._lane_type_enforcement

    def set_lane_type_enforcement(self, enabled: bool) -> None:
        """
        Arm or disarm the lane-type join gate.

        Purpose:
            The root propagates the configured `lane_type_enforcement`
            posture here at activation (and onto sets created afterwards);
            the set itself stays configuration-free and standalone-testable.

        Contract:
            - GATES ONLY `join`. Arming this does not retroactively touch lanes
              or members already placed; it changes what a FUTURE type-mixing
              join requires (force=True). Existing mixed content stays.
            - COERCES to bool with `bool(enabled)` rather than type-checking, so
              any truthy value arms the gate. It never raises on argument type.
            - The set holds this flag itself and owns no configuration object -
              the root pushes the posture in, which is what keeps a `ResearchSet`
              constructible and testable without a live configuration. Two sets
              can therefore carry different enforcement postures.
            - Idempotent: setting the same value again is a harmless re-write.

        Threading:
            The assignment happens under `self._lock`, so a concurrent `join`
            reads a fully-written flag rather than a torn value.

        Args:
            enabled:
                Whether type-mixing joins require force=True.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self._lane_type_enforcement = bool(enabled)

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

        Contract:
            - Identifies THIS RESEARCH SET OBJECT and is distinct from `name` - the id
              is stable machine identity, the name is the human-facing key used for
              lookups.

        Threading:
            Unsynchronized read of a slot fixed at construction.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the research set has been cleaned.

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

        Contract:
            - The human-facing registry key for this set, distinct from `set_id`.
              Lookups on `MutationResearch` are by NAME, not by id.

        Threading:
            Unsynchronized read of a slot fixed at construction.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the research set has been cleaned.

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

        Contract:
            - Resolves the set's DEFAULT lane by its well-known name, so it is a
              lookup rather than a stored reference - the default lane is whatever
              currently answers to that name.
            - Operations that omit a lane land here.

        Threading:
            Reads under `self._lock`, so the result is a coherent snapshot.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the research set has been cleaned.

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

        Contract:
            - Exposes the set's journal BY REFERENCE. It is owned by this set and
              becomes invalid once the set is cleaned; do not clean it separately.

        Threading:
            Unsynchronized read of a slot fixed at construction.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the research set has been cleaned.

        Returns:
            ResearchJournal:
                Owned journal (append-only; callers read, never edit).
        """
        self.check_cleaned()
        return self._journal

    def get_lane(self, lane_ref: str) -> ResearchLane:
        """
        Return one lane by name or id.

        Contract:
            - Returns the LIVE lane object, not a copy or snapshot. Its contents
              change as the set changes.
            - THE LANE IS A READ SURFACE ONLY. Every mutator on `ResearchLane`
              is set-internal (`_add_node`, `_detach_nodes`, `_set_anchor`,
              `_mark_joined`, `_mark_archived`), so holding this object does not
              let a caller move nodes, re-anchor, or terminate the lane behind
              the set's back. Residence claims, the journal, snapshots and
              persistence emission cannot be bypassed through it. All state
              change goes through set verbs.
            - Resolves by NAME or ID; a miss raises `KeyError` rather than
              returning None, so the return value never needs a null check.

        Threading:
            Resolution happens under `self._lock`, but the returned object is
            live - subsequent reads of it are not covered by that lock.

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

        Contract:
            - SORTED, so iteration order is deterministic across calls and processes.
            - Lists ALL lanes regardless of state, including joined and archived ones
              - unlike `heads()`, which reports open lanes only.

        Threading:
            Reads under `self._lock`, so the result is a coherent snapshot.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the research set has been cleaned.

        Returns:
            List[str]:
                Sorted lane names.
        """
        self.check_cleaned()
        with self._lock:
            return sorted(self._lane_id_by_name.keys())

    def residence_of(self, spell_id: str) -> Optional[str]:
        """
        Return the lane id holding one identity, when resident.

        Args:
            spell_id:
                Identity to look up.

        Contract:
            - Returns the lane an identity currently RESIDES in. `None` means it
              has no residence in this set - a normal answer, not an error, and
              the reason this returns `Optional[str]` while `history(...)` raises
              for the same condition.
            - SINGLE-RESIDENCE INVARIANT: an identity lives in exactly ONE lane
              network-wide, permanently. There is no release verb, so a non-None
              answer here never becomes None again for that identity; it can only
              change lane through a set verb that transfers residence.
            - Answers residence only. It does not assert the holding lane still
              carries the node, nor that the lane is open - pair it with
              `history(...)` when lane state matters.

        Threading:
            Does NOT take the set lock. It delegates to `ResidenceRegistry`,
            which serializes the lookup under its own lock, so the answer is a
            point-in-time read of the residence partition rather than a snapshot
            consistent with the set's lanes.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()` here, and again inside the registry.

        Raises:
            RuntimeError: If the research set has been cleaned.

        Returns:
            Optional[str]:
                Holding lane id or None.
        """
        self.check_cleaned()
        return self._residence.residence_of(spell_id)

    def heads(self) -> Dict[str, Optional[str]]:
        """
        Return the tip identity of every OPEN lane.

        Contract:
            - OPEN LANES ONLY. Joined and archived lanes are OMITTED entirely, so the
              key set here is a subset of `lane_names()` and a missing name means
              "not open", not "does not exist".
            - A value of None means the lane is open but has NO TIP yet - distinct
              from the lane being absent. Both cases exist and mean different things.

        Threading:
            Reads under `self._lock`, so the result is a coherent snapshot.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the research set has been cleaned.

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
                    result[name] = lane.tip_spell_id
            return result

    def walk(self, lane_ref: str) -> List[Dict[str, object]]:
        """
        Return one lane's line of versions with its ancestry hop.

        Purpose:
            The read verb for "tell me this object's story": ordered
            full-object records plus the anchor pointer that lets the caller
            hop into the transitive network.

        Contract:
            - ONE LANE ONLY. This does not traverse ancestry. Every returned row
              carries `anchor_lane_id` / `anchor_spell_id` so the caller can make
              the next hop deliberately, but walking the transitive network is
              the caller's loop, not this verb's.
            - Rows are DETACHED payloads built from `node.describe()`, then
              stamped with the four lane/anchor fields. Mutating a row cannot
              affect the record.
            - Order is the lane's own node order - declaration order, oldest
              first.
            - An UNANCHORED lane still returns rows; its `anchor_lane_id` and
              `anchor_spell_id` are simply empty, so absence of an anchor is
              data rather than an error.
            - Accepts either a lane NAME or a lane ID; resolution failure raises
              rather than returning an empty list, so `[]` unambiguously means
              "this lane exists and holds no versions".

        Threading:
            Resolves and materializes the whole list under `self._lock`, so the
            returned sequence is a coherent snapshot rather than a live view.

        Args:
            lane_ref:
                Lane name or lane id.

        Returns:
            List[Dict[str, object]]:
                Ordered node payloads; each carries `lane_id`, `lane_name`,
                `anchor_lane_id`, and `anchor_spell_id` alongside the node fields.
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
                step["anchor_spell_id"] = lane.anchor_spell_id
                steps.append(step)
            return steps

    def history(self, spell_id: str) -> Dict[str, object]:
        """
        Return everything the record knows about one identity.

        Contract:
            - RESIDENCE-KEYED. The identity must be resident in THIS set; a
              non-resident id raises `KeyError` naming the set rather than
              returning an empty payload, so there is no ambiguity between
              "unknown here" and "known but empty".
            - Joins three sources into one detached payload: the holding lane's
              identity/state/type, the node record itself, and EVERY journal
              entry touching the identity - including events recorded while the
              identity sat in a different lane, because the journal is queried by
              spell id rather than by lane.
            - `lane_state` and `lane_type` are emitted as their enum `.value`
              strings, not enum members, so the payload stays JSON-safe.
            - Read-only: it resolves, materializes and returns; nothing is
              claimed, journalled or snapshotted.

        Threading:
            Residence lookup, lane read, node describe and journal scan all run
            under `self._lock`, so the returned payload is internally consistent.

        Args:
            spell_id:
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
            lane_id = self._residence.residence_of(spell_id)
            if lane_id is None:
                raise KeyError(
                    f"Identity '{spell_id}' is not resident in research "
                    f"set '{self._name}'."
                )
            lane = self._lanes_by_id[lane_id]
            return {
                "spell_id": spell_id,
                "lane_id": lane_id,
                "lane_name": lane.name,
                "lane_state": lane.state.value,
                "lane_type": lane.lane_type.value,
                "node": lane.get_node(spell_id).describe(),
                "transitions": [
                    entry.describe()
                    for entry in self._journal.entries_for_spell_id(spell_id)
                ],
            }

    def campaign_view(self, campaign: str) -> Dict[str, object]:
        """
        Return everything the record knows about one research campaign.

        Purpose:
            Campaigns stamp work ACROSS lanes (multi-agent research); this
            read gathers the stamped version records and journal events into
            one detached payload without any organizational side effects.

        Contract:
            - JOURNAL ORDER IS THE CAMPAIGN'S STORY, and that is deliberate, not
              incidental. Nodes are sequenced by walking journal entries rather
              than by iterating lanes, because lane iteration tie-breaks
              same-millisecond ULIDs on their RANDOM component - that produced a
              non-deterministic full-tree flake. Do not "optimize" this into a
              lane walk.
            - TRANSITIONS AND NODES ARE NOT THE SAME SET. Every stamped journal
              entry becomes a transition, but only four acts contribute a node:
              `registered`, `staged`, `group_registered`, `group_recomposed`.
              A campaign of pure organizational moves yields transitions with an
              empty node list, which is correct rather than a gap.
            - MISSING IDENTITIES ARE REPORTED, NOT HIDDEN. An identity that was
              journalled but is absent from the CURRENT organization - a network
              restore rewound past its declaration, for instance - still emits a
              node entry carrying `missing_from_current_organization: True` with
              null lane fields. The read never silently drops a stamped event.
            - `lane_names` unions lanes seen from BOTH sides: the lane each
              journal entry was recorded against, and the lane currently holding
              each resolved node. Those can differ after a move.
            - Read-only. No claim, journal write, or snapshot occurs.
            - An empty or non-string campaign raises `ValueError` up front.

        Threading:
            The whole gather runs under `self._lock`, so transitions and nodes
            cannot disagree about the organization mid-read.

        Args:
            campaign:
                Campaign stamp to gather.

        Returns:
            Dict[str, object]:
                Payload with `campaign`, stamped `nodes` (each carrying its
                holding lane), stamped `transitions`, and the sorted
                `lane_names` involved.
        """
        self.check_cleaned()
        if not isinstance(campaign, str) or not campaign:
            raise ValueError("campaign must be a non-empty string.")
        with self._lock:
            nodes: List[Dict[str, object]] = []
            transitions: List[Dict[str, object]] = []
            involved: set = set()
            # Journal order IS the campaign's story: declaration events
            # sequence the nodes deterministically (lane iteration would
            # tie-break same-millisecond ULIDs on their random component -
            # the owner-run full-tree flake of 2026-07-11).
            for entry in self._journal.entries():
                if entry.campaign != campaign:
                    continue
                transitions.append(entry.describe())
                entry_lane = self._lanes_by_id.get(entry.lane_id)
                if entry_lane is not None:
                    involved.add(entry_lane.name)
                if entry.act not in (
                        TransitionAct.registered,
                        TransitionAct.staged,
                        TransitionAct.group_registered,
                        TransitionAct.group_recomposed,
                ):
                    continue
                spell_id = entry.to_spell_id
                holder_id = (
                    self._residence.residence_of(spell_id)
                    if spell_id
                    else None
                )
                holder = (
                    self._lanes_by_id.get(holder_id)
                    if holder_id is not None
                    else None
                )
                if holder is not None and holder.has_node(spell_id):
                    node_payload = holder.get_node(spell_id).describe()
                    node_payload["lane_id"] = holder.lane_id
                    node_payload["lane_name"] = holder.name
                    nodes.append(node_payload)
                    involved.add(holder.name)
                else:
                    # Journaled but absent from the CURRENT organization
                    # (e.g. a network restore rewound past the declaration);
                    # report honestly instead of hiding the event.
                    nodes.append(
                        {
                            "spell_id": spell_id,
                            "lane_id": None,
                            "lane_name": None,
                            "missing_from_current_organization": True,
                        }
                    )
            return {
                "campaign": campaign,
                "nodes": nodes,
                "transitions": transitions,
                "lane_names": sorted(involved),
            }

    # ------------------------------------------------------------------
    # Mutating verbs
    # ------------------------------------------------------------------

    def create_lane(
            self,
            name: str,
            *,
            lane_type: Optional[str] = None,
            attach_to: Optional[str] = None,
            attach_at_spell_id: Optional[str] = None,
            actor: Optional[str] = None,
            campaign: Optional[str] = None,
            reason: Optional[str] = None,
            metadata: Optional[Dict[str, object]] = None,
    ) -> ResearchLane:
        """
        Create one open lane, optionally anchored onto an existing node.

        Contract:
            - ANCHORING IS ALL-OR-NOTHING. `attach_to` and `attach_at_spell_id`
              must be supplied together; exactly one of them raises `ValueError`
              before the lock is taken. There is no "anchor to the lane's tip"
              shorthand - the anchor node is always named explicitly.
            - The anchor node must be held by the named lane. A lane that exists
              but does not hold that identity raises `KeyError` naming both, so a
              wrong-lane anchor cannot silently produce an unanchored lane.
            - Anchoring records ANCESTRY ONLY. The new lane starts EMPTY; no node
              is copied or moved from the anchor, and the anchor lane is
              untouched.
            - Lane NAMES are freeform and unique per set; lane TYPE is the policy
              word. Omitting `lane_type` yields `experiment`, not the default
              lane's `development` - a freshly created lane is an experiment
              until stated otherwise.
            - The journal entry records the anchor identity as `from_spell_id`
              and carries `lane_type` plus the anchor lane's id and name in
              metadata, so the lane's origin survives in history even if the
              anchor lane is later archived.
            - Ordering is validate -> resolve anchor -> create -> set anchor ->
              journal -> snapshot. A failure at any step leaves no lane, no
              journal entry and no snapshot.

        Threading:
            Campaign and anchor-argument validation run outside the lock; lane
            creation, anchoring, journalling and snapshotting run under
            `self._lock`. `_notify_mutation()` fires after release.

        Args:
            name:
                Unique lane name within this set.
            lane_type:
                Optional policy vocabulary word (`LaneType` value:
                development/experiment/production/test); `experiment` when
                omitted. Names stay freeform; the type is the policy word.
            attach_to:
                Optional lane (name or id) to anchor onto; requires
                attach_at_spell_id.
            attach_at_spell_id:
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
                If the name is taken, the lane_type is unknown, or anchor
                arguments are half-supplied.
            KeyError:
                If `attach_to` does not resolve, or the anchor node is not
                held by that lane.
        """
        self.check_cleaned()
        self._validate_campaign(campaign)
        if (attach_to is None) != (attach_at_spell_id is None):
            raise ValueError(
                "attach_to and attach_at_spell_id must be supplied together."
            )
        with self._lock:
            anchor_lane: Optional[ResearchLane] = None
            if attach_to is not None:
                anchor_lane = self._resolve_lane_locked(attach_to)
                if not anchor_lane.has_node(attach_at_spell_id):
                    raise KeyError(
                        f"Lane '{anchor_lane.name}' holds no identity "
                        f"'{attach_at_spell_id}' to anchor at."
                    )
            lane = self._create_lane_locked(
                name,
                lane_type=lane_type,
                metadata=metadata,
            )
            entry_metadata: Dict[str, object] = {
                "lane_type": lane.lane_type.value,
            }
            if anchor_lane is not None:
                lane._set_anchor(anchor_lane.lane_id, attach_at_spell_id)
                entry_metadata["anchor_lane_id"] = anchor_lane.lane_id
                entry_metadata["anchor_lane_name"] = anchor_lane.name
            self._journal.record(
                TransitionAct.lane_created,
                lane.lane_id,
                from_spell_id=attach_at_spell_id,
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
            spell_id: str,
            *,
            lane: Optional[str] = None,
            module_source_sha256: Optional[str] = None,
            parent_spell_ids: Optional[List[str]] = None,
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

        Contract:
            - DECLARES, never creates. The version must already have been bound;
              this writes the research record for it and mints no runtime state.
            - Omitting `lane` targets the guaranteed default lane rather than
              failing, so the common call needs no lane vocabulary at all.
            - ANCESTRY IS VALIDATED IN TWO STAGES, both `ValueError`. A parent
              that is not resident in this set is rejected outright. A parent
              that IS resident but names a COMPOSITION rather than a spell
              version is rejected separately: compositions are informational and
              carry no source or custody state, so there is nothing for a spell
              version to inherit from one.
            - CLAIM-THEN-ADD WITH COMPENSATION. Residence is claimed before the
              node is added to the lane, and a failed add rolls that claim back
              before re-raising. Lanes are handed out live, so a direct
              terminal-state call can race between the two steps under real
              threads; without the rollback a refused add would strand the claim
              and corrupt the residence partition.
            - Journals `TransitionAct.registered` and snapshots the organization
              only after the add succeeds - a refused registration leaves no
              journal entry and no snapshot.
            - Mutation subscribers are notified AFTER the set lock is released,
              which is what keeps the one-way lock order intact.

        Threading:
            The campaign check runs outside the lock; lane resolution, ancestry
            validation, the claim/add pair, journalling and snapshotting all run
            under `self._lock`. The `_notify_mutation()` fan-out is deliberately
            outside it.

        Args:
            spell_id:
                Binding-signature SHA256 (doubles as the custody crystal id).
            lane:
                Optional lane (name or id); the guaranteed default lane
                records the version when omitted.
            module_source_sha256:
                Optional module-version SHA256 the version binds against.
            parent_spell_ids:
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
                If a parent identity is unknown to this set, or names a
                composition (group) identity instead of a spell version.
        """
        self.check_cleaned()
        self._validate_campaign(campaign)
        with self._lock:
            target = self._resolve_lane_locked(
                lane if lane is not None else ResearchSet.DEFAULT_LANE_NAME,
            )
            parents = list(parent_spell_ids) if parent_spell_ids else []
            for parent_sha in parents:
                parent_kind = self._resident_node_kind_locked(parent_sha)
                if parent_kind is None:
                    raise ValueError(
                        f"Parent identity '{parent_sha}' is not resident in "
                        f"research set '{self._name}'; ancestry must "
                        f"reference formally declared versions."
                    )
                if parent_kind != "spell":
                    raise ValueError(
                        f"Parent identity '{parent_sha}' is a composition "
                        f"(group) identity; spell ancestry must reference "
                        f"declared spell versions only. Compositions are "
                        f"informational and carry no source or custody "
                        f"state to inherit."
                    )
            node = ResearchNode(
                spell_id,
                module_source_sha256=module_source_sha256,
                parent_spell_ids=parents,
                author=author,
                reason=reason,
                campaign=campaign,
                metadata=metadata,
            )
            self._residence.claim(spell_id, target.lane_id)
            # Threadsafety compensation: lanes are handed out live, so a
            # direct terminal-state call can race between the claim and the
            # add under real threads - a refused add must not strand the
            # claim (partition corruption).
            try:
                target._add_node(node)
            except Exception:
                self._residence._rollback_claim(spell_id, target.lane_id)
                raise
            self._journal.record(
                TransitionAct.registered,
                target.lane_id,
                to_spell_id=spell_id,
                actor=author,
                campaign=campaign,
                reason=reason,
                metadata={"module_source_sha256": module_source_sha256, "parent_spell_ids": parents},
            )
            self._snapshot_locked()
        self._notify_mutation()
        return node

    def register_group(
            self,
            member_spell_ids: List[str],
            *,
            lane: Optional[str] = None,
            parent_group_ids: Optional[List[str]] = None,
            author: Optional[str] = None,
            campaign: Optional[str] = None,
            reason: Optional[str] = None,
            metadata: Optional[Dict[str, object]] = None,
    ) -> GroupedResearchNode:
        """
        Formally declare one subsystem composition (GroupedResearchNode).

        Purpose:
            The grouped world-entry verb (owner ruling 2026-07-11): pin a
            set of already-declared versions as ONE composition record.
            Purely informational - members keep their own lanes, custody,
            and runtime posture untouched; the composition gates nothing.

        Contract:
            - Every member must already be formally declared (resident) in
              this set AND be a spell version - the spell/group namespaces
              are enforced separately, so a composition identity can never
              ride as a member or as spell ancestry.
            - Identity is content-addressed over the member set: an
              identical roster IS the same identity, so re-registering an
              unchanged composition surfaces the rediscovery error naming
              the holding lane (not a new fact).
            - `parent_group_ids` must reference resident compositions
              (composition ancestry, separate from spell ancestry).

        Args:
            member_spell_ids:
                Non-empty member identities to pin.
            lane:
                Optional lane (name or id); the guaranteed default lane
                records the composition when omitted (subsystems deserve
                their own lane - create one and pass it here).
            parent_group_ids:
                Optional previous composition identities.
            author:
                Optional registering agent name.
            campaign:
                Optional research-campaign stamp.
            reason:
                Optional reason line.
            metadata:
                Optional value-typed annotations.

        Returns:
            GroupedResearchNode:
                The recorded composition node.

        Raises:
            RuntimeError:
                Rediscovery - the composition identity already resides in
                a lane (the error names it); or the target lane is not
                open.
            ValueError:
                If a member or parent composition is unknown to this set,
                if a member names a composition identity, or if a parent
                composition names a spell identity.
        """
        self.check_cleaned()
        self._validate_campaign(campaign)
        with self._lock:
            target = self._resolve_lane_locked(
                lane if lane is not None else ResearchSet.DEFAULT_LANE_NAME,
            )
            members = list(member_spell_ids) if member_spell_ids else []
            for member in members:
                member_kind = self._resident_node_kind_locked(member)
                if member_kind is None:
                    raise ValueError(
                        f"Member identity '{member}' is not resident in "
                        f"research set '{self._name}'; compositions pin "
                        f"formally declared versions only."
                    )
                if member_kind != "spell":
                    raise ValueError(
                        f"Member identity '{member}' is a composition "
                        f"(group) identity; compositions pin declared "
                        f"spell versions only - nesting one composition "
                        f"inside another is not part of the model."
                    )
            parents = list(parent_group_ids) if parent_group_ids else []
            for parent in parents:
                parent_kind = self._resident_node_kind_locked(parent)
                if parent_kind is None:
                    raise ValueError(
                        f"Parent composition '{parent}' is not resident in "
                        f"research set '{self._name}'; composition ancestry "
                        f"must reference recorded compositions."
                    )
                if parent_kind != "group":
                    raise ValueError(
                        f"Parent composition '{parent}' is a spell "
                        f"identity; composition ancestry must reference "
                        f"recorded compositions, not spell versions."
                    )
            node = GroupedResearchNode(
                members,
                parent_group_ids=parents,
                author=author,
                reason=reason,
                campaign=campaign,
                metadata=metadata,
            )
            # Composition-grade rediscovery (teach before the raw claim
            # signal): identity is content-addressed over the member set,
            # so ANY roster that matches an existing composition - even a
            # recompose cycling back to an ancestor's exact roster - IS
            # that composition, not a new fact.
            existing_lane = self._residence.residence_of(node.group_id)
            if existing_lane is not None:
                raise RuntimeError(
                    f"Rediscovery: this exact member set is already "
                    f"recorded as composition '{node.group_id[:12]}...' "
                    f"in lane '{existing_lane}'. An identical roster IS "
                    f"the same composition (content-addressed identity); "
                    f"evolve from the existing composition instead of "
                    f"re-recording it."
                )
            self._residence.claim(node.group_id, target.lane_id)
            # Same compensation as register_spell: a refused add must not
            # strand the claim.
            try:
                target._add_node(node)
            except Exception:
                self._residence._rollback_claim(
                    node.group_id, target.lane_id,
                )
                raise
            self._journal.record(
                TransitionAct.group_recomposed
                if parents else TransitionAct.group_registered,
                target.lane_id,
                from_spell_id=parents[0] if parents else None,
                to_spell_id=node.group_id,
                actor=author,
                campaign=campaign,
                reason=reason,
                metadata={
                    "member_spell_ids": node.member_spell_ids,
                    "parent_group_ids": parents,
                },
            )
            self._snapshot_locked()
        self._notify_mutation()
        return node

    def recompose_group(
            self,
            previous_group_id: str,
            *,
            add: Optional[List[str]] = None,
            remove: Optional[List[str]] = None,
            author: Optional[str] = None,
            campaign: Optional[str] = None,
            reason: Optional[str] = None,
            metadata: Optional[Dict[str, object]] = None,
    ) -> GroupedResearchNode:
        """
        Evolve one composition forward (the iterate-and-add flow).

        Purpose:
            The agent loop the owner described: keep adding spells into
            the composition. Reads the previous roster, applies adds and
            removes, and registers the NEW composition into the SAME lane
            with `parent_group_ids=[previous]` - forward-only; nothing is
            edited.

        Contract:
            - FORWARD-ONLY. The previous composition is never mutated; a NEW
              GroupedResearchNode is registered with the previous as its single
              parent. History is append; there is no in-place edit.
            - CONTENT-ADDRESSED IDENTITY MAKES A NO-OP AN ERROR. A roster that
              resolves back to the previous member set is the SAME identity
              (content-addressed), so it raises rather than recording a
              duplicate. Removing then re-adding the same members is a no-op and
              is rejected.
            - REMOVE IS STRICT, ADD IS PERMISSIVE-BUT-VALIDATED. A `remove` of a
              member not in the previous roster raises; an `add` of a member not
              resident in the set raises (via the delegated `register_group`).
              Removes are applied before adds.
            - The result must pin at least one member; an empty roster raises.
            - Lands in the SAME lane the previous composition resides in - a
              recompose stays on its subsystem timeline rather than starting a
              new one.
            - RELEASES THE SET LOCK BEFORE DELEGATING. Validation runs under the
              lock; the actual registration re-enters through the public
              `register_group`, which takes the lock again. The operation is
              therefore two locked sections, not one - a concurrent mutation can
              interleave between the roster computation and the registration, and
              `register_group` re-validates residence at that point.

        Threading:
            Roster validation runs under `self._lock`; the lock is released and
            `register_group` re-acquires it for the write. Not a single atomic
            critical section.

        Args:
            previous_group_id:
                The composition being evolved (must be resident).
            add:
                Member identities to add (must be resident).
            remove:
                Member identities to drop (must be in the previous roster).
            author:
                Optional acting agent name.
            campaign:
                Optional research-campaign stamp.
            reason:
                Optional reason line.
            metadata:
                Optional value-typed annotations.

        Returns:
            GroupedResearchNode:
                The new composition node.

        Raises:
            RuntimeError:
                If the identity is unknown, the resident node is not a
                composition, the resulting roster is unchanged (identical
                member set = same content address = the SAME composition;
                nothing new to record), or the holding lane is not open.
            ValueError:
                If a removed member is not in the previous roster, an
                added member is not resident, or the resulting roster is
                empty.
        """
        self.check_cleaned()
        self._validate_campaign(campaign)
        with self._lock:
            lane_id = self._residence.residence_of(previous_group_id)
            if lane_id is None:
                raise RuntimeError(
                    f"Composition '{previous_group_id}' is not resident in "
                    f"research set '{self._name}'."
                )
            holding_lane = self._lanes_by_id[lane_id]
            previous = holding_lane.get_node(previous_group_id)
            if not isinstance(previous, GroupedResearchNode):
                raise RuntimeError(
                    f"Identity '{previous_group_id}' is a spell version, "
                    f"not a composition; recompose_group evolves "
                    f"GroupedResearchNodes only."
                )
            roster = set(previous.member_spell_ids)
            for member in list(remove) if remove else []:
                if member not in roster:
                    raise ValueError(
                        f"Cannot remove '{member}': not in the previous "
                        f"composition's roster."
                    )
                roster.discard(member)
            for member in list(add) if add else []:
                roster.add(member)
            if not roster:
                raise ValueError(
                    "The resulting composition would be empty; a "
                    "composition pins at least one member."
                )
            if roster == set(previous.member_spell_ids):
                raise RuntimeError(
                    f"The resulting roster is identical to composition "
                    f"'{previous_group_id[:12]}...'; an identical member "
                    f"set IS the same identity (content-addressed) - "
                    f"nothing new to record."
                )
            lane_ref = holding_lane.lane_id
        return self.register_group(
            sorted(roster),
            lane=lane_ref,
            parent_group_ids=[previous_group_id],
            author=author,
            campaign=campaign,
            reason=reason,
            metadata=metadata,
        )

    def group_history(
            self,
            group_id: str,
            *,
            campaign: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return everything the journal knows about one subsystem area.

        Purpose:
            The temporal composition read ("track changes in a larger
            area to see what happened"): every journal event that touches
            the composition's OWN lane (the subsystem timeline), any
            pinned member identity, or any lane a pinned member resides
            in - in journal order, campaign stamps intact. With a
            `campaign` the story narrows to one effort inside the area
            (the WHERE x WHEN join: groups are structure, campaigns are
            intent; neither owns the other, so the record joins them).

        Contract:
            - THREE-SOURCE WATCH SET. An event is included if it touches the
              composition's OWN lane, any member identity it pins, OR any lane a
              pinned member currently resides in. The returned `watched_lane_ids`
              names exactly the lanes that widened the search, so the scope is
              inspectable rather than implicit.
            - The subject must be a COMPOSITION. A resident id that is a spell
              version raises `RuntimeError`; an unknown id raises too. It never
              returns an empty payload for a wrong-kind subject.
            - `campaign` is an AND filter, not a selector: it narrows the already
              composition-scoped events to one campaign. Omitting it returns the
              full area story; supplying an unstamped campaign yields entries
              empty rather than raising.
            - Events are in JOURNAL ORDER (declaration order), and the payload is
              fully detached - describing entries, not live journal objects.
            - Read-only: no claim, journal write or snapshot.

        Threading:
            Resolves the composition, computes the watch set and scans the
            journal under `self._lock`, so the member roster and the events
            cannot disagree mid-read.

        Args:
            group_id:
                Composition identity to gather around.
            campaign:
                Optional campaign stamp to narrow to.

        Returns:
            Dict[str, object]:
                `{"group_id", "lane_id", "member_spell_ids",
                "watched_lane_ids", "campaign", "entries"}` - entries in
                journal order.

        Raises:
            RuntimeError:
                If the identity is unknown, or resident but a spell
                version.
        """
        self.check_cleaned()
        self._validate_campaign(campaign)
        with self._lock:
            lane_id = self._residence.residence_of(group_id)
            if lane_id is None:
                raise RuntimeError(
                    f"Composition '{group_id}' is not resident in "
                    f"research set '{self._name}'."
                )
            node = self._lanes_by_id[lane_id].get_node(group_id)
            if not isinstance(node, GroupedResearchNode):
                raise RuntimeError(
                    f"Identity '{group_id}' is a spell version, not a "
                    f"composition; group_history gathers "
                    f"GroupedResearchNodes only."
                )
            members = set(node.member_spell_ids)
            watched_lanes = {lane_id}
            for member in members:
                member_lane = self._residence.residence_of(member)
                if member_lane is not None:
                    watched_lanes.add(member_lane)
            entries = [
                entry
                for entry in self._journal.describe()["entries"]
                if (
                    entry.get("lane_id") in watched_lanes
                    or entry.get("to_spell_id") in members
                    or entry.get("from_spell_id") in members
                    or entry.get("to_spell_id") == group_id
                    or entry.get("from_spell_id") == group_id
                )
                and (campaign is None or entry.get("campaign") == campaign)
            ]
            return {
                "group_id": group_id,
                "lane_id": lane_id,
                "member_spell_ids": sorted(members),
                "watched_lane_ids": sorted(watched_lanes),
                "campaign": campaign,
                "entries": entries,
            }

    def record_world_entry(
            self,
            spell_id: str,
            *,
            staged: bool = False,
            lane: Optional[str] = None,
            module_source_sha256: Optional[str] = None,
            parent_spell_ids: Optional[List[str]] = None,
            author: Optional[str] = None,
            campaign: Optional[str] = None,
            reason: Optional[str] = None,
            metadata: Optional[Dict[str, object]] = None,
    ) -> Optional[ResearchNode]:
        """
        Idempotently declare one world-entry (the runtime-seam verb).

        Purpose:
            The bind/bind_inactive seams call this on EVERY dynamic-lane
            world entry: identical content rebinds to the same SHA, so an
            already-resident identity is a quiet no-op here (the runtime
            must never fail on research bookkeeping), while a fresh identity
            registers exactly like `register_spell` - with the `staged` act
            when the entry was parked.

        Contract:
            - IDEMPOTENT BY DESIGN, and this is the ONLY difference in spirit
              from `register_spell`: an already-resident identity returns `None`
              instead of raising. Rediscovery is the expected steady state on a
              runtime seam - identical content rebinds to the same SHA - and the
              runtime must never fail because bookkeeping already happened.
            - THE RESIDENCE CHECK IS FIRST, before lane resolution and before
              ancestry validation. A rediscovery therefore costs one lookup and
              validates nothing; it will NOT raise on a bad lane or a bad parent
              that a fresh registration would have rejected.
            - `staged` selects the journal act only: `staged` for
              `bind_inactive` parks, `registered` for active binds. It does not
              change residence, lane placement, or node shape.
            - Ancestry rules mirror `register_spell` exactly - unknown parent
              raises, composition-as-parent raises - and this is the path the
              root's staged-ancestry stamp travels for synthesis mints.
            - Carries the same CLAIM-THEN-ADD compensation: residence is claimed
              before the add and rolled back if the add is refused, so a race
              cannot strand a claim and corrupt the residence partition.

        Threading:
            The residence probe, lane resolution, ancestry validation, claim/add
            pair, journalling and snapshotting all run under `self._lock`;
            `_notify_mutation()` fires after release.

        Args:
            spell_id:
                Binding-signature SHA256 entering the world.
            staged:
                True for `bind_inactive` entries (journals `staged`);
                False for active binds (journals `registered`).
            lane:
                Optional lane (name or id); default lane when omitted.
            module_source_sha256:
                Optional module-version SHA256.
            parent_spell_ids:
                Optional ancestry (the synthesis-mint lane: the root's
                staged-ancestry stamp routes through here); every parent
                must already be resident in this set, mirroring
                `register_spell`.
            author:
                Optional acting agent name.
            campaign:
                Optional research-campaign stamp.
            reason:
                Optional reason line.
            metadata:
                Optional value-typed annotations.

        Returns:
            Optional[ResearchNode]:
                The new version node, or None when the identity was already
                declared (rediscovery is not an error on this verb).

        Raises:
            ValueError:
                If a parent identity is unknown to this set, or names a
                composition (group) identity instead of a spell version.
        """
        self.check_cleaned()
        self._validate_campaign(campaign)
        with self._lock:
            if self._residence.is_resident(spell_id):
                return None
            target = self._resolve_lane_locked(
                lane if lane is not None else ResearchSet.DEFAULT_LANE_NAME,
            )
            parents = list(parent_spell_ids) if parent_spell_ids else []
            for parent_sha in parents:
                parent_kind = self._resident_node_kind_locked(parent_sha)
                if parent_kind is None:
                    raise ValueError(
                        f"Parent identity '{parent_sha}' is not resident in "
                        f"research set '{self._name}'; ancestry must "
                        f"reference formally declared versions."
                    )
                if parent_kind != "spell":
                    raise ValueError(
                        f"Parent identity '{parent_sha}' is a composition "
                        f"(group) identity; spell ancestry must reference "
                        f"declared spell versions only. Compositions are "
                        f"informational and carry no source or custody "
                        f"state to inherit."
                    )
            node = ResearchNode(
                spell_id,
                module_source_sha256=module_source_sha256,
                parent_spell_ids=parents,
                author=author,
                reason=reason,
                campaign=campaign,
                metadata=metadata,
            )
            self._residence.claim(spell_id, target.lane_id)
            # Same compensation as register_spell: a refused add must not
            # strand the claim.
            try:
                target._add_node(node)
            except Exception:
                self._residence._rollback_claim(spell_id, target.lane_id)
                raise
            self._journal.record(
                TransitionAct.staged if staged else TransitionAct.registered,
                target.lane_id,
                to_spell_id=spell_id,
                actor=author,
                campaign=campaign,
                reason=reason,
                metadata={"module_source_sha256": module_source_sha256, "parent_spell_ids": parents},
            )
            self._snapshot_locked()
        self._notify_mutation()
        return node

    def record_promotion(
            self,
            from_spell_id: Optional[str],
            to_spell_id: str,
            *,
            actor: Optional[str] = None,
            campaign: Optional[str] = None,
            reason: Optional[str] = None,
            metadata: Optional[Dict[str, object]] = None,
    ) -> TransitionEntry:
        """
        Record one runtime selection change (notch) as a forward event.

        Contract:
            - Journal-only: promotion changes what is LIVE, never which lane
              holds a version, so the organization does not re-snapshot.
            - `to_spell_id` must be a declared identity; `from_spell_id` may be None
              (first selection) or an identity outside the record (honest
              passthrough - pre-MR history is not fabricated).

        Args:
            from_spell_id:
                Previously selected identity, when known.
            to_spell_id:
                Newly selected identity (must be resident).
            actor:
                Optional acting agent name.
            campaign:
                Optional research-campaign stamp.
            reason:
                Optional reason line.
            metadata:
                Optional value-typed annotations.

        Returns:
            TransitionEntry:
                The recorded `promoted` event.

        Raises:
            KeyError:
                If `to_spell_id` is not resident in this set.
        """
        self.check_cleaned()
        self._validate_campaign(campaign)
        with self._lock:
            to_lane_id = self._residence.residence_of(to_spell_id)
            if to_lane_id is None:
                raise KeyError(
                    f"Identity '{to_spell_id}' is not declared in research set "
                    f"'{self._name}'; declare the world entry before "
                    f"recording its promotion."
                )
            entry = self._journal.record(
                TransitionAct.promoted,
                to_lane_id,
                from_spell_id=from_spell_id,
                to_spell_id=to_spell_id,
                actor=actor,
                campaign=campaign,
                reason=reason,
                metadata=metadata,
            )
        self._notify_mutation()
        return entry

    def attach(
            self,
            lane_ref: str,
            *,
            onto: str,
            at_spell_id: str,
            actor: Optional[str] = None,
            campaign: Optional[str] = None,
            reason: Optional[str] = None,
    ) -> None:
        """
        Anchor one lane's ancestry onto another lane's node.

        Contract:
            - Organization only: content never moves; `onto`/`at_spell_id` are
              mandatory so the act is never scope-blind.
            - REPOINTS RATHER THAN APPENDS. A lane holds at most ONE anchor, so
              attaching a lane that is already anchored silently replaces the
              previous anchor. Ancestry here is a single pointer, not a list;
              use the journal to recover where a lane used to hang.
            - SELF-ANCHORING IS REFUSED by lane id, not by name, so two names
              resolving to the same lane are still caught.
            - The anchor node must be held by `onto`. A lane that resolves but
              does not hold the identity raises `KeyError` naming both.
            - The journal records the anchor identity as `to_spell_id` (the
              direction that distinguishes it from `detach`, which records the
              vacated anchor as `from_spell_id`) plus the anchor lane's id and
              name in metadata.
            - Snapshots the organization on success, so an anchor change is
              recoverable through `restore_network`.

        Threading:
            Both lane resolutions, the self-anchor check, the anchor write,
            journalling and snapshotting run under `self._lock`;
            `_notify_mutation()` fires after release.

        Args:
            lane_ref:
                Lane (name or id) being organized.
            onto:
                Lane (name or id) to anchor onto.
            at_spell_id:
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

        Returns:
            None.
        """
        self.check_cleaned()
        self._validate_campaign(campaign)
        with self._lock:
            lane = self._resolve_lane_locked(lane_ref)
            target = self._resolve_lane_locked(onto)
            if lane.lane_id == target.lane_id:
                raise RuntimeError(
                    f"Lane '{lane.name}' cannot anchor onto itself."
                )
            if not target.has_node(at_spell_id):
                raise KeyError(
                    f"Lane '{target.name}' holds no identity '{at_spell_id}' to "
                    f"anchor at."
                )
            lane._set_anchor(target.lane_id, at_spell_id)
            self._journal.record(
                TransitionAct.attached,
                lane.lane_id,
                to_spell_id=at_spell_id,
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

        Contract:
            - Organization only. The lane keeps every node it holds; only the
              ancestry pointer is cleared, so a detached lane becomes a root of
              its own line rather than losing content.
            - NOT IDEMPOTENT. Detaching a lane that holds no anchor raises
              `RuntimeError` rather than returning quietly, so a redundant
              detach is a caller error rather than a silent no-op.
            - The vacated anchor is captured BEFORE the clear and journalled as
              `from_spell_id`, which is what makes the detach reversible from
              history - the pointer would otherwise be unrecoverable.
            - Snapshots the organization on success.

        Threading:
            Resolution, anchor capture, clear, journalling and snapshotting run
            under `self._lock`; `_notify_mutation()` fires after release.

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

        Returns:
            None.
        """
        self.check_cleaned()
        self._validate_campaign(campaign)
        with self._lock:
            lane = self._resolve_lane_locked(lane_ref)
            previous_anchor = lane.anchor_spell_id
            lane.clear_anchor()
            self._journal.record(
                TransitionAct.detached,
                lane.lane_id,
                from_spell_id=previous_anchor,
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
        self._validate_campaign(campaign)
        with self._lock:
            source = self._resolve_lane_locked(lane_ref)
            target = self._resolve_lane_locked(into)
            if source.lane_id == target.lane_id:
                raise RuntimeError(
                    f"Lane '{source.name}' cannot join into itself."
                )
            # Receiver custody (BUG-037): hold the receiver's own reentrant
            # lane lock across the ENTIRE commit (open-check through journal
            # + snapshot), so a direct lane-surface state flip (for example
            # _mark_archived racing from another set verb) serializes entirely before
            # or entirely after the join - the open-receiver contract holds
            # through commit. Lock order set -> lane is the one-way order
            # every set verb already uses; lanes never call back into the
            # set, so no inversion exists.
            with target._lock:
                self._join_locked(
                    source,
                    target,
                    collapse=collapse,
                    force=force,
                    actor=actor,
                    campaign=campaign,
                    reason=reason,
                )
        self._notify_mutation()
        return target

    def _join_locked(
            self,
            source: ResearchLane,
            target: ResearchLane,
            *,
            collapse: bool,
            force: bool,
            actor: Optional[str],
            campaign: Optional[str],
            reason: Optional[str],
    ) -> None:
        """
        Run the join commit (caller holds the set AND receiver lane locks).

        Contract:
            - The receiver's open state is checked and then HELD true by the
              caller-owned receiver lock until the journal record and
              snapshot land; a concurrent direct archive can never
              interleave mid-commit.

        Args:
            source:
                Resolved source lane.
            target:
                Resolved receiving lane (its lock is held by the caller).
            collapse:
                Move only the tip when True.
            force:
                Permit a divergent or type-mixing join.
            actor:
                Optional acting agent name.
            campaign:
                Optional research-campaign stamp.
            reason:
                Optional reason line.

        Raises:
            RuntimeError:
                On non-open receiver, unforced type-mixing, or unforced
                divergence (the error names both tips).
        """
        if target.state is not LaneState.open:
            raise RuntimeError(
                f"Receiving lane '{target.name}' is "
                f"{target.state.value}; join requires an open receiver."
            )
        type_mixing = (
            self._lane_type_enforcement
            and source.lane_type is not target.lane_type
        )
        if type_mixing and not force:
            raise RuntimeError(
                f"Type-mixing join: lane '{source.name}' is "
                f"'{source.lane_type.value}' while receiver "
                f"'{target.name}' is '{target.lane_type.value}', and "
                f"lane-type enforcement is on. Pass force=True to "
                f"supersede the type policy explicitly."
            )
        clean = (
            source.anchor_lane_id == target.lane_id
            and source.anchor_spell_id is not None
            and target.tip_spell_id == source.anchor_spell_id
        )
        if not clean and not force:
            raise RuntimeError(
                f"Divergent join: lane '{source.name}' anchors at "
                f"'{source.anchor_spell_id}' on lane "
                f"'{source.anchor_lane_id}' while receiver "
                f"'{target.name}' tips at '{target.tip_spell_id}'. Compose a "
                f"reconciling version in the codegen workshop and "
                f"register it, or pass force=True to supersede."
            )
        previous_target_tip = target.tip_spell_id
        moved_spell_ids: List[str] = []
        if source.node_count > 0:
            if collapse:
                moved_spell_ids = [source.tip_spell_id]
            else:
                moved_spell_ids = source.node_spell_ids()
            detached = source._detach_nodes(moved_spell_ids)
            # Threadsafety compensation: a mid-loop refusal (direct
            # terminal-state race on the receiver) must not leave
            # detached records in limbo - everything returns to the
            # still-open source in original order, then the failure
            # re-raises. Residence transfers only after EVERY add
            # landed, so the partition stays all-or-nothing.
            added: List[str] = []
            try:
                for node in detached:
                    target._add_node(node)
                    added.append(node_identity(node))
            except Exception:
                if added:
                    target._detach_nodes(added)
                for node in detached:
                    source._add_node(node)
                raise
            self._residence.transfer(moved_spell_ids, target.lane_id)
        source._mark_joined(target.lane_id)
        self._journal.record(
            TransitionAct.joined,
            target.lane_id,
            from_spell_id=previous_target_tip,
            to_spell_id=target.tip_spell_id,
            actor=actor,
            campaign=campaign,
            reason=reason,
            metadata={
                "joined_lane_id": source.lane_id,
                "joined_lane_name": source.name,
                "collapse": collapse,
                # Audit truth (BUG-040): forced records whether ANY policy
                # was overridden - divergence OR the armed lane-type gate -
                # not merely divergence.
                "forced": bool(not clean or type_mixing),
                "moved_spell_ids": moved_spell_ids,
            },
        )
        self._snapshot_locked()

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

        Returns:
            None.
        """
        self.check_cleaned()
        self._validate_campaign(campaign)
        with self._lock:
            lane = self._resolve_lane_locked(lane_ref)
            if lane.name == ResearchSet.DEFAULT_LANE_NAME:
                raise RuntimeError(
                    "The default lane is the guaranteed world-entry record "
                    "and never archives."
                )
            lane._mark_archived()
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

        Contract:
            - Builds a full network snapshot under the lock, so it is internally
              consistent - but it is a point-in-time copy that does not track later
              changes.
            - Cost scales with the network, so this is a deliberate operation rather
              than a cheap accessor.

        Threading:
            Reads under `self._lock`, so the result is a coherent snapshot.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the research set has been cleaned.

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

        Contract:
            - Returns the versioner's recorded snapshot digests, which identify
              snapshots WITHOUT materializing them - use it to detect change
              cheaply instead of calling `snapshot_network()` repeatedly.
            - Ordered OLDEST FIRST, matching the FIFO retention ring, so the
              tail is the newest and `[-1]` equals `latest_network_snapshot`.
            - A DETACHED copy of the address list; mutating it cannot affect the
              retention ring.
            - Lists only RETAINED addresses. The ring is bounded, so an address
              observed earlier can age out and later return `KeyError` from
              `restore_network` - presence here is the honest liveness test.

        Threading:
            Does NOT take the set lock. It delegates to `NetworkVersioner`, which
            serializes the read under its own lock, so the result is a
            point-in-time view of the retention ring rather than a snapshot
            consistent with the set's live lanes.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()` here; the versioner guards its own read.

        Raises:
            RuntimeError: If the research set has been cleaned.

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

        Contract:
            - The most recent snapshot digest. Comparing it against a previously
              held value is the cheap way to ask "has the network changed since I
              looked", with no snapshot build required.
            - `None` means NO snapshot has ever been taken - a fresh set before
              its first organizing verb - not an error.
            - Equals the last element of `network_snapshot_shas()`.
            - Content-addressed, so an organization that changes and then reverts
              to a previous shape reports the SAME digest again: this detects
              SHAPE change, not event count. Two structurally identical
              organizations are indistinguishable here by design.

        Threading:
            Does NOT take the set lock. It delegates to `NetworkVersioner`, which
            serializes the read under its own lock; the answer is a point-in-time
            read of the retention ring.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()` here; the versioner guards its own read.

        Raises:
            RuntimeError: If the research set has been cleaned.

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
            - VALIDATE-THEN-DESTROY. The incoming payload is parsed, every lane
              rebuilt, and the guaranteed default lane confirmed present BEFORE
              a single live lane is torn down. A malformed payload, or one
              lacking the default lane, raises with LIVE ORGANIZATION UNTOUCHED.
              A restore therefore never half-lands.
            - The default-lane gate exists because `default_lane` resolves by
              well-known name: installing a network without it would leave the
              set unable to serve its own default, so the invariant is checked
              at the door rather than discovered later.
            - WHOLESALE REPLACEMENT, not a merge. Lanes, the name index and the
              residence partition are all swapped for the rebuilt objects; any
              lane or residence claim created after the snapshot is discarded.
            - Old lanes and the old residence registry are cleaned best-effort
              during the swap - a failure to clean one does not abort the
              restore, because the replacement is already validated.
            - The restore target is a NETWORK SNAPSHOT ADDRESS, not a spell
              identity, so it rides `metadata["snapshot_address"]` rather than a
              typed endpoint field. The typed fields never carry something that
              is not an identity.
            - Snapshots again on success, so the pre-restore organization is
              itself addressable afterwards.

        Threading:
            The entire validate-teardown-swap-journal sequence runs under
            `self._lock`, so no reader observes a half-swapped organization.
            `_notify_mutation()` fires after release.

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
            ValueError:
                If the snapshot's organization payload is invalid or lacks
                the guaranteed default lane (live state stays untouched).

        Returns:
            None.
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
            # Core-invariant gate (BUG-038): the guaranteed default lane
            # must exist in the incoming organization BEFORE any live state
            # is torn down - a restore can never install a network that
            # `default_lane` immediately refuses to serve.
            if ResearchSet.DEFAULT_LANE_NAME not in rebuilt_names:
                raise ValueError(
                    f"Snapshot '{snapshot_sha}' carries no "
                    f"'{ResearchSet.DEFAULT_LANE_NAME}' default lane; the "
                    f"guaranteed-default-lane invariant refuses the "
                    f"restore. Live organization is untouched."
                )
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
            # Honesty: the restore target is a NETWORK SNAPSHOT address, not
            # a spell identity - it rides metadata so the typed endpoint
            # fields never lie about what they carry.
            self._journal.record(
                TransitionAct.restored,
                self._set_id,
                actor=actor,
                reason=reason,
                metadata={"snapshot_address": snapshot_sha},
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

        Contract:
            - The ORGANIZATION is captured in full, but the JOURNAL is a bounded
              WINDOW (default 200 recent entries). This is deliberate: the twin
              carries current structure completely, while journal HISTORY is left
              to the checkpoint sequence, which records deltas over time. Passing
              `recent_transitions=None` includes the full stream when a complete
              history is genuinely needed.
            - Carries the NETWORK VERSIONER's own state (`network_versioner`), so
              a set rebuilt from this payload can still `restore_network` to
              pre-death organization shapes - the undo ring survives the round
              trip, bounded by its retention.
            - PLAIN-VALUE THROUGHOUT. Every nested value is JSON-safe, so the
              payload crosses the persistence boundary losslessly and rebuilds
              via `from_payload`.
            - A detached copy: mutating the returned dict cannot affect the set.
            - Read-only; no snapshot or journal write occurs.

        Threading:
            The whole payload is assembled under `self._lock`, so organization,
            journal window and versioner state are mutually consistent.

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
                # The undo ring rides the record (owner dial 2026-07-11) so
                # restore_network reaches pre-death organization states on a
                # rebuilt pod; bounded by the ring's own retention.
                "network_versioner": self._versioner.describe(),
            }

    def describe(self) -> Dict[str, object]:
        """
        Return the default detached snapshot of this set.

        Contract:
            - ALIAS for `describe_composition()`, delegating in full and adding
              nothing. It carries no guard of its own; the cleaned-state check comes
              from the method it delegates to.

        Threading:
            Inherited from `describe_composition()`.

        Lifecycle / Cleanup:
            Guarded indirectly, via the delegate.

        Raises:
            RuntimeError: If the research set has been cleaned.

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

        Contract:
            - BUILDS FRESH, THEN REPLACES. It constructs a normal set (which
              eagerly makes a default lane), then tears that scaffolding down and
              swaps in the rebuilt lanes, residence, journal and versioner. The
              transient default lane exists only to satisfy the constructor and
              does not survive.
            - `on_mutation` IS SUPPRESSED DURING REBUILD. The set is constructed
              with `on_mutation=None` so hydration emits nothing, and the
              caller's callback is installed only at the very end. A rebuild is
              therefore silent - it does not re-fire persistence for every
              recorded node.
            - RECORDED IDENTITY IS PRESERVED. The rebuilt set restores the
              recorded `set_id` and `created_at` rather than minting new ones, so
              a hydrated set is the SAME identity it was sealed as.
            - PARTIAL PAYLOADS DEGRADE, they do not crash: a missing residence
              payload rebuilds an empty registry, a missing versioner payload
              keeps the fresh one. Only `organization` and `journal` are hard
              requirements; their absence or wrong type raises `ValueError`.
            - The journal continues minting BEYOND the recorded window's
              `next_sequence`, so sequence numbers never collide across a rebuild.
            - Snapshots once at the end, so the rebuilt organization is
              immediately addressable.

        Threading:
            The rebuilt set is not shared until this returns; the swap runs under
            the new set's own lock.

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
            versioner_payload = payload.get("network_versioner")
            if isinstance(versioner_payload, dict):
                try:
                    research_set._versioner.cleanup()
                except Exception:
                    pass
                research_set._versioner = NetworkVersioner.from_payload(
                    versioner_payload,
                )
            if isinstance(set_id, str) and set_id:
                research_set._set_id = set_id
            recorded_created_at = organization.get("created_at")
            if isinstance(recorded_created_at, str) and recorded_created_at:
                research_set._created_at = recorded_created_at
            research_set._snapshot_locked()
            research_set._on_mutation = on_mutation
        return research_set
