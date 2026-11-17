import copy
from typing import TYPE_CHECKING, Dict, List

from melder.utilities.general_base.cleanable import Cleanable

if TYPE_CHECKING:
    from melder.mutation_research.research_set.research_set import SetCompositionView


class ResearchCompositionView(Cleanable):
    """
    The research composition as references, materialized into a detached payload when first read (#331).

    Purpose:
        The MutationResearch root re-emits its persistence twin after every
        mutating verb. Built from `describe_research_composition()`, each
        emission described every node of every set again, so a configure's world
        entries cost time quadratic in its binds. This object holds instead what
        each `ResearchSet._composition_view()` returned - references to the
        sets' append-only payload parts with their lengths - and turns them into
        the composition payload only when the twin is read (a checkpoint seal, a
        flush, a record description, the emission tap).

    Contract:
        - `materialize()` returns {set name -> payload} equal to what each set's
          `describe_composition(recent_transitions=journal_window)` returned when
          its view was taken: organization (lanes in `lane_id` order, each with
          its nodes and tip, and the residence mapping), the journal window with
          `entry_count` and `next_sequence`, and the undo ring as of its last
          mint.
        - Fully DETACHED: every node and journal payload, lane metadata, list and
          the ring payload are copied, so mutating the result reaches neither the
          live research nor a later materialization.
        - Holds plain values and lists of plain-value dicts the research
          structures never edit in place once handed out; it holds no research
          object, lock or callback.

    Threading:
        No lock of its own: the parts it reads are only appended to, replaced
        or dropped by their owners, and a list prefix read (`parts[:length]`) is
        safe against a concurrent append. The owning twin serializes reads of
        this object.

    Lifecycle / Cleanup:
        Owned by the twin that received it; the twin cleans it after its first
        materialization or at its own cleanup. Idempotent; deletes its fields.

    Registration:
        MELDER KERNEL - guarded. Built by the MutationResearch root for its twin;
        never user-constructed or bound.

    Subsystem Context:
        Beside the four bookkeeping structures of a `ResearchSet` (lanes,
        journal, residence, versioner), each of which keeps the append-only
        payload part this view references.

    System Context:
        The hinge of the constant-cost world entry: the research side pays one
        node payload per append, and the crystallizer side pays a full
        description only when it actually reads the twin.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. The research composition as references, materialized for the persistence
        twin when read. Melder kernel machinery: read it to understand the runtime, do not drive it
        directly.
    """

    __slots__ = Cleanable.__slots__ + [
        "_set_views",
        "_journal_window",
    ]

    def __init__(self, set_views: Dict[str, SetCompositionView], journal_window: int) -> None:
        """
        Hold one composition view.

        Contract:
            - Keeps a shallow copy of the name -> view mapping; the views
              themselves are tuples of strings, ints and references to parts their
              owners never edit in place.

        Args:
            set_views:
                Set name -> `ResearchSet._composition_view()` result.
            journal_window:
                How many newest journal entries a materialized set carries (the
                twin's window, `ResearchSet.TWIN_JOURNAL_WINDOW`); >= 0.

        Raises:
            ValueError:
                If journal_window is not an int >= 0.

        Returns:
            None.
        """
        super().__init__()
        if not isinstance(journal_window, int) or journal_window < 0:
            raise ValueError("journal_window must be an int >= 0.")
        self._set_views: Dict[str, SetCompositionView] = dict(set_views)
        self._journal_window: int = journal_window

    def cleanup(self) -> None:
        """
        Drop the views and mark this object cleaned.

        Contract:
            - Idempotent. Deletes its fields (no tombstones); never clears the
              parts it referenced - they belong to the research structures and to
              any other view still holding them.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        del self._set_views
        del self._journal_window

    def materialize(self) -> Dict[str, object]:
        """
        Build the detached composition payload the views stand for.

        Returns:
            Dict[str, object]:
                Set name -> the `describe_composition()` payload of that set as of
                its view.

        Raises:
            RuntimeError:
                If this object has been cleaned.
        """
        self.check_cleaned()
        return {
            set_name: ResearchCompositionView._materialize_set(set_view, self._journal_window)
            for set_name, set_view in self._set_views.items()
        }

    @staticmethod
    def _materialize_set(set_view: SetCompositionView, journal_window: int) -> Dict[str, object]:
        """
        Build one set's detached `describe_composition()` payload from its view.

        Contract:
            - Lanes keep the view's (`lane_id`) order; each lane's nodes are the
              first `length` payloads of its part, copied; the residence mapping
              is the claim log's first `length` pairs; the journal window is the
              newest `journal_window` of the first `length` entry payloads, copied,
              exactly as `ResearchJournal.describe(recent=journal_window)` slices.

        Args:
            set_view:
                (set_id, name, created_at, lane views, residence, journal and ring
                views).
            journal_window:
                The journal window size.

        Returns:
            Dict[str, object]:
                Detached payload with `organization`, `journal`,
                `network_snapshot_shas` and `network_versioner`.
        """
        set_id, name, created_at, lane_views, residence_view, journal_view, ring_view = set_view
        lanes: List[Dict[str, object]] = []
        for header, node_payloads, node_count in lane_views:
            lane_payload: Dict[str, object] = dict(header)
            lane_payload["metadata"] = ResearchCompositionView._detached_value(header["metadata"])
            lane_payload["nodes"] = [
                ResearchCompositionView._detached_payload(node_payload)
                for node_payload in node_payloads[:node_count]
            ]
            lanes.append(lane_payload)
        claim_log, claim_count = residence_view
        entry_payloads, entry_count, next_sequence = journal_view
        window_start = entry_count - journal_window if journal_window < entry_count else 0
        snapshot_shas, versioner_payload = ring_view
        return {
            "organization": {
                "set_id": set_id,
                "name": name,
                "created_at": created_at,
                "lanes": lanes,
                "residence": {"lane_id_by_spell_id": dict(claim_log[:claim_count])},
            },
            "journal": {
                "entries": [
                    ResearchCompositionView._detached_payload(entry_payload)
                    for entry_payload in entry_payloads[window_start:entry_count]
                ],
                "entry_count": entry_count,
                "next_sequence": next_sequence,
            },
            "network_snapshot_shas": list(snapshot_shas),
            "network_versioner": ResearchCompositionView._detached_value(versioner_payload),
        }

    @staticmethod
    def _detached_payload(payload: Dict[str, object]) -> Dict[str, object]:
        """
        Copy one node or journal payload so the copy shares nothing mutable with it.

        Contract:
            - Strings, numbers, booleans and None are shared (immutable); lists
              and dicts are copied, an empty one as a new empty one, a non-empty
              one deeply.

        Args:
            payload:
                A `describe()` payload kept by a research structure.

        Returns:
            Dict[str, object]: The detached copy.
        """
        return {
            key: ResearchCompositionView._detached_value(value)
            for key, value in payload.items()
        }

    @staticmethod
    def _detached_value(value: object) -> object:
        """
        Copy one payload value if it is mutable.

        Args:
            value:
                A plain payload value.

        Returns:
            object: The value itself when immutable; a (deep) copy of a list or dict.
        """
        if isinstance(value, (list, dict)):
            return copy.deepcopy(value) if value else type(value)()
        return value
