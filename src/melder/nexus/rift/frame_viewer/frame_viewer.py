"""
Public Rift-backed viewer host for frame, conduit, spell, and descriptor reads.

This module owns the top-level viewer facade that routes all read-only viewer
behavior through current `Rift` projection state instead of viewer-local
projection caches.
"""
from contextlib import contextmanager
import threading
from typing import TYPE_CHECKING, Any, Callable, Dict, Iterator, List, Optional, Tuple

from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.nexus.rift.frame_viewer.view_conduit import (
    ViewConduit,
)
from melder.nexus.rift.frame_viewer.view_action_hooks import (
    decorate_public_view_actions,
    noop_action_scope,
)
from melder.nexus.rift.frame_viewer.view_frame import (
    ViewFrame,
)
from melder.nexus.rift.frame_viewer.view_multiframe import (
    ViewMultiFrame,
)
from melder.nexus.rift.frame_viewer.view_spell import (
    ViewSpell,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.class_surface_ast_describer import (
    ClassSurfaceAstDescriber,
)
from melder.utilities.helpers.id_builder import IDBuilder
if TYPE_CHECKING:
    from melder.nexus.acl.frame_acl_compiled_access_surface import (
        CompiledFrameACLAccessSurface,
    )
    from melder.nexus.acl.frame_acl_configuration import FrameACLConfiguration
    from melder.nexus.frame_descriptor.conduit_record import ConduitRecord
    from melder.nexus.frame_descriptor.frame_descriptor import FrameDescriptor
    from melder.nexus.frame_descriptor.spell_record import SpellRecord
    from melder.nexus.rift.rift import Rift
    from melder.nexus.rift.frame_link.frame_link import FrameLink
    from melder.nexus.rift.projection.view_projection import ViewProjection


@decorate_public_view_actions
class FrameViewer(Cleanable):
    """

    Purpose:
        Hold one durable viewer asset that reads current frame truth from the
        Rift-owned projection bundle plus the viewer helper surfaces used to
        inspect that state.

    Contract:
        - Holds one borrowed `Rift` reference and reads current view
          projections from that owner on demand.
        - Treats descriptor/config/surface state as Rift-owned, not
          viewer-owned.
        - Owns the public viewer feature surface directly.
        - Creates helper objects on demand for the
          view/frame/conduit/spell families rather than caching bound helper
          state on the viewer itself.
        - Exposes descriptor-only multi-frame host methods directly on the
          viewer.
        - Exposes frame-local ACL/payload-aware behavior through the viewer's
          helper surfaces without a separate profile layer or generic dispatch
          entrypoint.
        - Does not expose raw runtime objects or any direct code-execution
          behavior.

    Threading:
        Uses one instance `threading.RLock` to serialize cleanup and
        multi-step viewer-state mutation and teardown.

    Lifecycle:
        Cleanup clears only viewer-owned references. It does not cleanup the
        owning `Rift` or any Rift-owned projection objects because those are
        borrowed runtime inputs.

    Registration:
        MELDER KERNEL. The one subclass, `StaticFrameViewer`, is melder-internal and
        created by static rooms during room init; no injection seam exists.

    Subsystem Context:
        The READ surface of a room, opposite `CommandSystem` (the mediated
        action surface) and `Workstation` (the binding canvas). It creates
        view/frame/conduit/spell helper objects ON DEMAND rather than caching
        bound helper state, which is what keeps it truthful when projections
        refresh underneath it.

    System Context:
        This class is a VIEW, not a cache, and that is the whole design. It
        holds a borrowed `Rift` reference and reads current projections from it
        on demand; descriptor, config, and surface state are Rift-owned. A
        viewer that cached projections would answer confidently with stale truth
        after an ACL change, which is precisely the failure the Nexus refresh
        fan-out exists to prevent.
        The final contract line is the security boundary: it exposes NO raw
        runtime objects and NO direct code execution. Everything reachable
        through a viewer is a projection, so a read can never become a write.
        That is what makes the viewer safe to hand to a static room and to
        agents.
        Cleanup mirrors the borrow: it clears viewer-owned references ONLY and
        never touches the owning Rift or its projection objects, because those
        are borrowed inputs whose lifetime belongs to someone else.
    """

    __ast_helper_access__: str = "public"
    __agent_purpose__: str = (
        "access: public. Multi-frame descriptor host for the Rift viewer path. Use this object to inspect hosted "
        "frames, compare descriptor records, and call the explicit viewer methods for frame-local behavior."
    )
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_rift",
        "_action_hook_scope_factory",
    ]

    def __init__(
            self,
            *,
            rift: Rift,
            action_hook_scope_factory: Optional[Callable[..., Any]] = None,
    ) -> None:
        """
        Initialize one Rift-backed projection-native frame viewer.

        Contract:
            - REQUIRES a rift; `None` raises `TypeError` immediately. The viewer
              has no standalone mode - every projection it serves comes from the
              rift's ACL-filtered view.
            - BORROWS the rift rather than owning it. Cleaning this viewer does
              not clean the rift, and the rift outlives the viewer.
            - Holds NO cached projection. Descriptors, ACL configuration and
              access surfaces are resolved per call, which is what lets the
              viewer stay correct as the frame changes - and why each facade call
              re-resolves rather than reusing.
            - The optional action-hook scope factory is stored as supplied and is
              not validated here.

        Owned State:
            Owns `_lock` and `_id`. Borrows `_rift` and the action-hook scope
            factory.

        Threading:
            Creates the reentrant lock used by later viewer operations;
            construction itself needs no synchronization because the object is
            not yet shared.

        Lifecycle / Cleanup:
            Born ready - there is no separate activation step. Sub-viewers are
            built on demand and never retained.

        Args:
            rift:
                Owning `Rift` that exposes the current view projections.
            action_hook_scope_factory:
                Optional factory used to wrap view actions in a hook scope.

        Returns:
            None.

        Raises:
            TypeError: If `rift` is None.
        """
        super().__init__()
        if rift is None:
            raise TypeError("rift cannot be None.")
        self._lock: threading.RLock = threading.RLock()
        self._id: str = IDBuilder.create_id()
        self._rift: Rift = rift
        self._action_hook_scope_factory: Optional[Callable[..., Any]] = (
            action_hook_scope_factory
        )

    def cleanup(self) -> None:
        """
        Idempotently clear viewer-owned state.

        Contract:
            - Safe to call more than once.
            - Clears only viewer-owned references.
            - Does not cleanup the owning `Rift` because the viewer borrows
              that runtime object.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            del self._rift
            del self._action_hook_scope_factory
            del self._id
        del self._lock

    @property
    def id(self) -> str:
        """
        Return the stable viewer identifier.

        Contract:
            - Identifies THIS VIEWER OBJECT, not the rift and not the frame. A new
              viewer over the same rift carries a different id.
            - Assigned at construction and stable for the object's life.

        Threading:
            Unsynchronized read of a write-once slot; safe from any thread.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the viewer has been cleaned.

        Returns:
            str: Stable viewer id.
        """
        self.check_cleaned()
        return self._id

    def list_frame_names(self) -> List[str]:
        """
        Return the currently linked frame names in deterministic order.

        Contract:
            - FACADE PASS-THROUGH to `ViewMultiFrame.list_frame_names(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_multiframe()` constructs a new
              ViewMultiFrame per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - Descriptor-hosted and CROSS-FRAME: the multi-frame helper is not bound
              to a single frame, so no frame selection happens here.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            List[str]: Sorted linked frame names.
        """
        self.check_cleaned()
        return self.get_view_multiframe().list_frame_names()

    def list_linked_frame_names(self) -> List[str]:
        """
        Return the currently linked frame names in deterministic order.

        Contract:
            - FACADE PASS-THROUGH to `ViewMultiFrame.list_linked_frame_names(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_multiframe()` constructs a new
              ViewMultiFrame per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - Descriptor-hosted and CROSS-FRAME: the multi-frame helper is not bound
              to a single frame, so no frame selection happens here.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            List[str]: Sorted linked frame names.
        """
        self.check_cleaned()
        return self.get_view_multiframe().list_linked_frame_names()

    def list_nexus_frame_names(self) -> List[str]:
        """
        Return the currently accessible Nexus-managed frame names.

        Contract:
            - FACADE PASS-THROUGH to `ViewMultiFrame.list_nexus_frame_names(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_multiframe()` constructs a new
              ViewMultiFrame per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - Descriptor-hosted and CROSS-FRAME: the multi-frame helper is not bound
              to a single frame, so no frame selection happens here.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            List[str]: Sorted accessible Nexus-managed frame names.
        """
        self.check_cleaned()
        return self.get_view_multiframe().list_nexus_frame_names()

    def list_non_nexus_frame_names(self) -> List[str]:
        """
        Return the currently accessible published non-Nexus frame names.

        Contract:
            - FACADE PASS-THROUGH to `ViewMultiFrame.list_non_nexus_frame_names(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_multiframe()` constructs a new
              ViewMultiFrame per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - Descriptor-hosted and CROSS-FRAME: the multi-frame helper is not bound
              to a single frame, so no frame selection happens here.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            List[str]: Sorted accessible published non-Nexus frame names.
        """
        self.check_cleaned()
        return self.get_view_multiframe().list_non_nexus_frame_names()

    def count_frames(self) -> int:
        """
        Return the number of hosted frame descriptors.

        Contract:
            - FACADE PASS-THROUGH to `ViewMultiFrame.count_frames(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_multiframe()` constructs a new
              ViewMultiFrame per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - Descriptor-hosted and CROSS-FRAME: the multi-frame helper is not bound
              to a single frame, so no frame selection happens here.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            int: Hosted frame count.
        """
        self.check_cleaned()
        return self.get_view_multiframe().count_frames()

    def describe_available_views(self) -> List[Dict[str, object]]:
        """
        Return a simple host-level description of the hosted frames.

        Contract:
            This is a host-only descriptor surface. It does not expose payload
            data or ACL-shaped visibility details.

        Contract:
            - Lists ONLY frame names, one single-key dict per reachable frame. It is a
              directory of what can be viewed, not a description of any frame's
              contents - use the `ViewFrame` helpers for that.
            - Scoped to the rift's reachable frames, so a frame absent here is
              invisible to this viewer entirely.
            - The single-key dict shape is deliberate: it leaves room for more fields
              without changing the return type.

        Returns:
            List[Dict[str, object]]: Hosted frame descriptions.
        """
        self.check_cleaned()
        described_frames: List[Dict[str, object]] = []
        for frame_name in self.list_frame_names():
            described_frames.append(
                {
                    "frame_name": frame_name,
                }
            )
        return described_frames

    def count_root_conduits(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> int:
        """
        Return the number of root conduit records.

        Args:
            frame_name:
                Optional frame name. When omitted, counts across all hosted
                frames.

        Contract:
            - FACADE PASS-THROUGH to `ViewMultiFrame.count_root_conduits(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_multiframe()` constructs a new
              ViewMultiFrame per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - Descriptor-hosted and CROSS-FRAME: the multi-frame helper is not bound
              to a single frame, so no frame selection happens here.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            int: Root conduit record count.
        """
        self.check_cleaned()
        return self.get_view_multiframe().count_root_conduits(frame_name=frame_name)

    def count_spell_records(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> int:
        """
        Return the number of spell records.

        Args:
            frame_name:
                Optional frame name. When omitted, counts across all hosted
                frames.

        Contract:
            - FACADE PASS-THROUGH to `ViewMultiFrame.count_spell_records(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_multiframe()` constructs a new
              ViewMultiFrame per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - Descriptor-hosted and CROSS-FRAME: the multi-frame helper is not bound
              to a single frame, so no frame selection happens here.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            int: Spell record count.
        """
        self.check_cleaned()
        return self.get_view_multiframe().count_spell_records(frame_name=frame_name)

    def describe_frame(self, frame_name: str) -> Dict[str, object]:
        """
        Return a descriptor-level summary for one hosted frame.

        Contract:
            This host-level summary is limited to descriptor structure and
            published record identity. It does not expose payload bodies or
            ACL-shaped payload visibility.

        Contract:
            - FACADE PASS-THROUGH to `ViewMultiFrame.describe_frame(...)`. Filtering, ordering and raise
              behaviour are that method's; this adds no logic of its own.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL: `get_view_multiframe()` constructs a new
              ViewMultiFrame against a newly resolved descriptor snapshot, so a loop of
              facade calls rebuilds the projection each time and TWO FACADE CALLS NEED
              NOT SEE THE SAME FRAME STATE. Hold one sub-viewer when results must be
              mutually consistent.
            - VISIBILITY-FILTERED: absence means "not visible to this rift" OR "not
              present" - never proof of non-existence.
            - Descriptor-hosted and CROSS-FRAME: no frame selection happens here.

        Args:
            frame_name:
                Hosted frame name to summarize.

        Returns:
            Dict[str, object]: Descriptor-level frame summary.
        """
        self.check_cleaned()
        return self.get_view_multiframe().describe_frame(frame_name)

    def describe_frames(self) -> Dict[str, Dict[str, object]]:
        """
        Return descriptor-level summaries for all hosted frames.

        Contract:
            - FACADE PASS-THROUGH to `ViewMultiFrame.describe_frames(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_multiframe()` constructs a new
              ViewMultiFrame per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - Descriptor-hosted and CROSS-FRAME: the multi-frame helper is not bound
              to a single frame, so no frame selection happens here.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            Dict[str, Dict[str, object]]: Hosted frame summaries keyed by frame
            name.
        """
        self.check_cleaned()
        return self.get_view_multiframe().describe_frames()

    def describe_frame_brief(self, frame_name: str) -> Dict[str, object]:
        """
        Return one compact descriptor-level frame summary.

        Purpose:
            Give the operator a smaller "start here" frame summary than
            `describe_frame(...)` while staying entirely on descriptor-owned
            host data.

        Contract:
            - Uses only descriptor/record identity and count data.
            - Does not expose payload bodies or ACL-shaped visibility details.
            - Always includes the frame's Nexus contract and top-level record
              counts.

        Args:
            frame_name:
                Hosted frame name to summarize.

        Returns:
            Dict[str, object]: Compact descriptor-level frame summary.
        """
        self.check_cleaned()
        return self.get_view_multiframe().describe_frame_brief(frame_name)

    def describe_host_inventory(self) -> Dict[str, object]:
        """
        Return one compact host-level inventory summary.

        Purpose:
            Give the operator a quick overview of what the `FrameViewer` host
            is carrying without forcing a deeper descriptor walk.

        Contract:
            - Aggregates only descriptor-owned counts, names, and record-level
              identities.
            - Does not expose payload bodies or ACL-shaped detail.

        Returns:
            Dict[str, object]: Compact host-level inventory summary.
        """
        self.check_cleaned()
        return self.get_view_multiframe().describe_host_inventory()

    def describe_viewer(self) -> Dict[str, object]:
        """
        Return one compact summary of the `FrameViewer` host itself.

        Purpose:
            Give the operator one host-level summary of what this viewer is
            currently carrying without walking frame-local helper surfaces.

        Contract:
            - Returns host identity, default routing state, and descriptor-only
              inventory posture.
            - Does not expose payload bodies, ACL-shaped data, or frame-local
              helper output.

        Returns:
            Dict[str, object]: Compact host summary for this viewer.
        """
        self.check_cleaned()
        return {
            "id": self.id,
            "frame_count": self.count_frames(),
            "frame_names": tuple(self.list_frame_names()),
            "host_boundary": "descriptor_only",
        }

    def describe_frames_inventory(self) -> Dict[str, Dict[str, object]]:
        """
        Return one compact per-frame descriptor inventory summary.

        Purpose:
            Give the operator a small inventory table across hosted frames
            without exposing anything deeper than descriptor-owned counts and
            stable record identity.

        Contract:
            - Multi-frame output stays shallow and descriptor-only.
            - Does not expose payload bodies or ACL-shaped visibility detail.
            - Includes only per-frame counts and stable host identity fields.

        Returns:
            Dict[str, Dict[str, object]]: Per-frame compact inventories keyed
            by frame name.
        """
        self.check_cleaned()
        return self.get_view_multiframe().describe_frames_inventory()

    def describe_viewer_method_surface(self) -> Dict[str, object]:
        """
        Return one curated summary of the host-side viewer method surface.

        Purpose:
            Explain how to use the `FrameViewer` host without forcing the
            operator to read the raw AST-described class surface first.

        Contract:
            - Describes only the curated host-side method groups.
            - Keeps the host boundary explicit: descriptor-oriented viewer
              methods on the host, with explicit helper-backed methods exposed
              directly on the viewer surface.

        Returns:
            Dict[str, object]: Curated host method-surface summary.
        """
        self.check_cleaned()
        return {
            "host_boundary": "descriptor_only",
            "default_entrypoints": (
                "describe_viewer",
                "describe_host_inventory",
            "describe_frames_inventory",
        ),
        "frame_summary_methods": (
            "list_frame_names",
            "describe_frame",
            "describe_frames",
            "describe_frame_brief",
        ),
            "comparison_methods": (
                "compare_frames",
                "compare_frames_brief",
                "compare_frame_conduits",
                "compare_frame_spells",
            ),
            "record_methods": (
                "describe_conduit_records",
                "describe_spell_records",
                "describe_spell_record",
            ),
            "frame_local_method_entrypoints": (
                "describe_visible_surface",
                "list_targets",
                "describe_conduits",
                "describe_spells",
            ),
        }

    def compare_frames(
            self,
            left_frame_name: str,
            right_frame_name: str,
    ) -> Dict[str, object]:
        """
        Compare two hosted frame descriptors at the record-identity level.

        Purpose:
            Give the operator one descriptor-only diff between two hosted
            frames so they can see what differs without manually comparing the
            individual host list methods.

        Contract:
            - Uses descriptor-owned identities, counts, and normalized values
              only.
            - Does not expose payload bodies or ACL-shaped detail.
            - Returns shared sets plus left-only/right-only deltas for the most
              important descriptor-level inventories.

        Args:
            left_frame_name:
                Left hosted frame name.
            right_frame_name:
                Right hosted frame name.

        Returns:
            Dict[str, object]: Descriptor-level comparison summary.
        """
        self.check_cleaned()
        return self.get_view_multiframe().compare_frames(left_frame_name, right_frame_name)

    def compare_frames_brief(
            self,
            left_frame_name: str,
            right_frame_name: str,
    ) -> Dict[str, object]:
        """
        Return one compact descriptor-only comparison summary for two frames.

        Purpose:
            Provide a smaller "what materially differs?" answer than the full
            `compare_frames(...)` payload.

        Contract:
            - Uses only descriptor-level comparison data derived from the full
              frame comparison.
            - Keeps multi-frame output shallow and count-focused.

        Args:
            left_frame_name:
                Left hosted frame name.
            right_frame_name:
                Right hosted frame name.

        Returns:
            Dict[str, object]: Compact descriptor-level frame comparison.
        """
        self.check_cleaned()
        return self.get_view_multiframe().compare_frames_brief(left_frame_name, right_frame_name)

    def compare_frame_conduits(
            self,
            left_frame_name: str,
            right_frame_name: str,
    ) -> Dict[str, object]:
        """
        Compare the conduit-record inventories of two hosted frames.

        Args:
            left_frame_name:
                Left hosted frame name.
            right_frame_name:
                Right hosted frame name.

        Contract:
            - FACADE PASS-THROUGH to `ViewMultiFrame.compare_frame_conduits(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_multiframe()` constructs a new
              ViewMultiFrame per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - Descriptor-hosted and CROSS-FRAME: the multi-frame helper is not bound
              to a single frame, so no frame selection happens here.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            Dict[str, object]: Conduit-record comparison summary.
        """
        self.check_cleaned()
        return self.get_view_multiframe().compare_frame_conduits(left_frame_name, right_frame_name)

    def compare_frame_spells(
            self,
            left_frame_name: str,
            right_frame_name: str,
    ) -> Dict[str, object]:
        """
        Compare the spell-record inventories of two hosted frames.

        Args:
            left_frame_name:
                Left hosted frame name.
            right_frame_name:
                Right hosted frame name.

        Contract:
            - FACADE PASS-THROUGH to `ViewMultiFrame.compare_frame_spells(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_multiframe()` constructs a new
              ViewMultiFrame per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - Descriptor-hosted and CROSS-FRAME: the multi-frame helper is not bound
              to a single frame, so no frame selection happens here.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            Dict[str, object]: Spell-record comparison summary.
        """
        self.check_cleaned()
        return self.get_view_multiframe().compare_frame_spells(left_frame_name, right_frame_name)

    def describe_binding_name_collisions(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, Tuple[str, ...]]:
        """
        Return binding-name collisions in the selected descriptor scope.

        Purpose:
            Surface visible ambiguity at the record-identity level when the
            same binding name is attached to multiple published spell records.

        Contract:
            - FACADE PASS-THROUGH to `ViewMultiFrame.describe_binding_name_collisions(...)`. Filtering, ordering and raise
              behaviour are that method's; this adds no logic of its own.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL: `get_view_multiframe()` constructs a new
              ViewMultiFrame against a newly resolved descriptor snapshot, so a loop of
              facade calls rebuilds the projection each time and TWO FACADE CALLS NEED
              NOT SEE THE SAME FRAME STATE. Hold one sub-viewer when results must be
              mutually consistent.
            - VISIBILITY-FILTERED: absence means "not visible to this rift" OR "not
              present" - never proof of non-existence.
            - Descriptor-hosted and CROSS-FRAME: no frame selection happens here.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, scans all hosted
                frames.

        Returns:
            Dict[str, Tuple[str, ...]]: Binding names mapped to the colliding
            spell source ids.
        """
        self.check_cleaned()
        return self.get_view_multiframe().describe_binding_name_collisions(frame_name=frame_name)

    def describe_spell_name_collisions(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, Tuple[str, ...]]:
        """
        Return spell-name collisions in the selected descriptor scope.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, scans all hosted
                frames.

        Contract:
            - FACADE PASS-THROUGH to `ViewMultiFrame.describe_spell_name_collisions(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_multiframe()` constructs a new
              ViewMultiFrame per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - Descriptor-hosted and CROSS-FRAME: the multi-frame helper is not bound
              to a single frame, so no frame selection happens here.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            Dict[str, Tuple[str, ...]]: Spell names mapped to the colliding
            spell source ids.
        """
        self.check_cleaned()
        return self.get_view_multiframe().describe_spell_name_collisions(frame_name=frame_name)

    def describe_index_groups(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, Tuple[str, ...]]:
        """
        Return spell-index groups in the selected descriptor scope.

        Purpose:
            Surface all published spell source ids grouped by spell-index id,
            even when an index currently has only one visible member.

        Contract:
            - FACADE PASS-THROUGH to `ViewMultiFrame.describe_index_groups(...)`. Filtering, ordering and raise
              behaviour are that method's; this adds no logic of its own.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL: `get_view_multiframe()` constructs a new
              ViewMultiFrame against a newly resolved descriptor snapshot, so a loop of
              facade calls rebuilds the projection each time and TWO FACADE CALLS NEED
              NOT SEE THE SAME FRAME STATE. Hold one sub-viewer when results must be
              mutually consistent.
            - VISIBILITY-FILTERED: absence means "not visible to this rift" OR "not
              present" - never proof of non-existence.
            - Descriptor-hosted and CROSS-FRAME: no frame selection happens here.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, scans all hosted
                frames.

        Returns:
            Dict[str, Tuple[str, ...]]: Spell-index ids mapped to published spell
            source ids.
        """
        self.check_cleaned()
        return self.get_view_multiframe().describe_index_groups(frame_name=frame_name)

    def describe_spellframe_groups(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, Tuple[str, ...]]:
        """
        Return spellframe groups in the selected descriptor scope.

        Purpose:
            Group published spells by normalized spellframe value so frame-wide
            spellframe overlaps are obvious.

        Contract:
            - FACADE PASS-THROUGH to `ViewMultiFrame.describe_spellframe_groups(...)`. Filtering, ordering and raise
              behaviour are that method's; this adds no logic of its own.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL: `get_view_multiframe()` constructs a new
              ViewMultiFrame against a newly resolved descriptor snapshot, so a loop of
              facade calls rebuilds the projection each time and TWO FACADE CALLS NEED
              NOT SEE THE SAME FRAME STATE. Hold one sub-viewer when results must be
              mutually consistent.
            - VISIBILITY-FILTERED: absence means "not visible to this rift" OR "not
              present" - never proof of non-existence.
            - Descriptor-hosted and CROSS-FRAME: no frame selection happens here.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, scans all hosted
                frames.

        Returns:
            Dict[str, Tuple[str, ...]]: Spellframe values mapped to published
            spell source ids.
        """
        self.check_cleaned()
        return self.get_view_multiframe().describe_spellframe_groups(frame_name=frame_name)

    def describe_spellbook_permission_mismatches(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, Dict[str, object]]:
        """
        Return spellbook groups whose permission posture is not uniform.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, scans all hosted
                frames.

        Contract:
            - FACADE PASS-THROUGH to `ViewMultiFrame.describe_spellbook_permission_mismatches(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_multiframe()` constructs a new
              ViewMultiFrame per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - Descriptor-hosted and CROSS-FRAME: the multi-frame helper is not bound
              to a single frame, so no frame selection happens here.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            Dict[str, Dict[str, object]]: Spellbook ids mapped to permission
            mismatch summaries.
        """
        self.check_cleaned()
        return self.get_view_multiframe().describe_spellbook_permission_mismatches(frame_name=frame_name)

    def describe_spellbook_existence_mismatches(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, Dict[str, object]]:
        """
        Return spellbook groups whose existence posture is not uniform.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, scans all hosted
                frames.

        Contract:
            - FACADE PASS-THROUGH to `ViewMultiFrame.describe_spellbook_existence_mismatches(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_multiframe()` constructs a new
              ViewMultiFrame per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - Descriptor-hosted and CROSS-FRAME: the multi-frame helper is not bound
              to a single frame, so no frame selection happens here.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            Dict[str, Dict[str, object]]: Spellbook ids mapped to existence
            mismatch summaries.
        """
        self.check_cleaned()
        return self.get_view_multiframe().describe_spellbook_existence_mismatches(frame_name=frame_name)

    def compare_spell_records(
            self,
            left_spell_source_id: str,
            right_spell_source_id: str,
            *,
            left_frame_name: Optional[str] = None,
            right_frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Compare two published spell records.

        Purpose:
            Give the operator one record-level spell diff without requiring them
            to manually compare multiple identity, provenance, and posture
            methods.

        Contract:
            - FACADE PASS-THROUGH to `ViewMultiFrame.compare_spell_records(...)`. Filtering, ordering and raise
              behaviour are that method's; this adds no logic of its own.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL: `get_view_multiframe()` constructs a new
              ViewMultiFrame against a newly resolved descriptor snapshot, so a loop of
              facade calls rebuilds the projection each time and TWO FACADE CALLS NEED
              NOT SEE THE SAME FRAME STATE. Hold one sub-viewer when results must be
              mutually consistent.
            - VISIBILITY-FILTERED: absence means "not visible to this rift" OR "not
              present" - never proof of non-existence.
            - Descriptor-hosted and CROSS-FRAME: no frame selection happens here.

        Args:
            left_spell_source_id:
                Left published spell source id.
            right_spell_source_id:
                Right published spell source id.
            left_frame_name:
                Optional hosted frame constraint for the left spell.
            right_frame_name:
                Optional hosted frame constraint for the right spell.

        Returns:
            Dict[str, object]: Record-level spell comparison summary.
        """
        self.check_cleaned()
        return self.get_view_multiframe().compare_spell_records(left_spell_source_id, right_spell_source_id, left_frame_name=left_frame_name, right_frame_name=right_frame_name)

    def compare_conduit_records(
            self,
            left_conduit_id: str,
            right_conduit_id: str,
            *,
            left_frame_name: Optional[str] = None,
            right_frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Compare two published conduit records.

        Args:
            left_conduit_id:
                Left published conduit id.
            right_conduit_id:
                Right published conduit id.
            left_frame_name:
                Optional hosted frame constraint for the left conduit.
            right_frame_name:
                Optional hosted frame constraint for the right conduit.

        Contract:
            - FACADE PASS-THROUGH to `ViewMultiFrame.compare_conduit_records(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_multiframe()` constructs a new
              ViewMultiFrame per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - Descriptor-hosted and CROSS-FRAME: the multi-frame helper is not bound
              to a single frame, so no frame selection happens here.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            Dict[str, object]: Record-level conduit comparison summary.
        """
        self.check_cleaned()
        return self.get_view_multiframe().compare_conduit_records(left_conduit_id, right_conduit_id, left_frame_name=left_frame_name, right_frame_name=right_frame_name)

    def list_spell_source_ids_for_frame(self, frame_name: str) -> List[str]:
        """
        Return spell source ids for one hosted frame.

        Purpose:
            Provide the canonical published spell identities for one hosted
            descriptor in deterministic order.

        Contract:
            - FACADE PASS-THROUGH to `ViewMultiFrame.list_spell_source_ids_for_frame(...)`. Filtering, ordering and raise
              behaviour are that method's; this adds no logic of its own.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL: `get_view_multiframe()` constructs a new
              ViewMultiFrame against a newly resolved descriptor snapshot, so a loop of
              facade calls rebuilds the projection each time and TWO FACADE CALLS NEED
              NOT SEE THE SAME FRAME STATE. Hold one sub-viewer when results must be
              mutually consistent.
            - VISIBILITY-FILTERED: absence means "not visible to this rift" OR "not
              present" - never proof of non-existence.
            - Descriptor-hosted and CROSS-FRAME: no frame selection happens here.

        Args:
            frame_name:
                Hosted frame name whose spell source ids should be returned.

        Returns:
            List[str]: Spell source ids for the frame.
        """
        self.check_cleaned()
        return self.get_view_multiframe().list_spell_source_ids_for_frame(frame_name)

    def list_frame_ids(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return published frame ids for the selected descriptor scope.

        Purpose:
            Surface the stable published frame identifiers without exposing any
            payload body data.

        Contract:
            - Reads only `FrameRecord` identity fields.
            - Returns ids in deterministic frame-order.
            - Omits frames that do not currently expose a `frame_overview`
              record.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, returns frame ids
                across all hosted descriptors.

        Returns:
            List[str]: Published frame ids in deterministic order.
        """
        self.check_cleaned()
        return self.get_view_multiframe().list_frame_ids(frame_name=frame_name)

    def list_nexus_contracts(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[Dict[str, str]]:
        """
        Return the published Nexus dataset contracts for hosted frames.

        Purpose:
            Give the operator a direct host-level view of the record contracts
            currently attached to the selected descriptor scope.

        Contract:
            - Uses only record-level `nexus_label` / `nexus_version`.
            - Does not expose payload body content.
            - Returns one contract entry per frame that currently exposes a
              `frame_overview` record.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, returns contract
                entries across all hosted frames.

        Returns:
            List[Dict[str, str]]: Nexus contract entries in deterministic frame
            order.
        """
        self.check_cleaned()
        return self.get_view_multiframe().list_nexus_contracts(frame_name=frame_name)

    def count_conduit_records(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> int:
        """
        Return the number of published conduit records.

        Purpose:
            Surface conduit-record inventory at the descriptor host level
            without reaching into conduit payload bodies.

        Contract:
            - FACADE PASS-THROUGH to `ViewMultiFrame.count_conduit_records(...)`. Filtering, ordering and raise
              behaviour are that method's; this adds no logic of its own.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL: `get_view_multiframe()` constructs a new
              ViewMultiFrame against a newly resolved descriptor snapshot, so a loop of
              facade calls rebuilds the projection each time and TWO FACADE CALLS NEED
              NOT SEE THE SAME FRAME STATE. Hold one sub-viewer when results must be
              mutually consistent.
            - VISIBILITY-FILTERED: absence means "not visible to this rift" OR "not
              present" - never proof of non-existence.
            - Descriptor-hosted and CROSS-FRAME: no frame selection happens here.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, counts conduit
                records across all hosted frames.

        Returns:
            int: Published conduit-record count.
        """
        self.check_cleaned()
        return self.get_view_multiframe().count_conduit_records(frame_name=frame_name)

    def list_conduit_record_ids(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return published conduit record ids for the selected scope.

        Purpose:
            Expose the conduit ids owned by the selected frame descriptor scope
            without surfacing payload details.

        Contract:
            - FACADE PASS-THROUGH to `ViewMultiFrame.list_conduit_record_ids(...)`. Filtering, ordering and raise
              behaviour are that method's; this adds no logic of its own.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL: `get_view_multiframe()` constructs a new
              ViewMultiFrame against a newly resolved descriptor snapshot, so a loop of
              facade calls rebuilds the projection each time and TWO FACADE CALLS NEED
              NOT SEE THE SAME FRAME STATE. Hold one sub-viewer when results must be
              mutually consistent.
            - VISIBILITY-FILTERED: absence means "not visible to this rift" OR "not
              present" - never proof of non-existence.
            - Descriptor-hosted and CROSS-FRAME: no frame selection happens here.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, returns conduit ids
                across all hosted frames.

        Returns:
            List[str]: Conduit ids in deterministic order.
        """
        self.check_cleaned()
        return self.get_view_multiframe().list_conduit_record_ids(frame_name=frame_name)

    def list_root_conduit_ids(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return root conduit ids for the selected descriptor scope.

        Purpose:
            Surface conduit-root topology at the host level using record
            identity only.

        Contract:
            - FACADE PASS-THROUGH to `ViewMultiFrame.list_root_conduit_ids(...)`. Filtering, ordering and raise
              behaviour are that method's; this adds no logic of its own.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL: `get_view_multiframe()` constructs a new
              ViewMultiFrame against a newly resolved descriptor snapshot, so a loop of
              facade calls rebuilds the projection each time and TWO FACADE CALLS NEED
              NOT SEE THE SAME FRAME STATE. Hold one sub-viewer when results must be
              mutually consistent.
            - VISIBILITY-FILTERED: absence means "not visible to this rift" OR "not
              present" - never proof of non-existence.
            - Descriptor-hosted and CROSS-FRAME: no frame selection happens here.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, returns unique root
                conduit ids across all hosted frames.

        Returns:
            List[str]: Deterministically sorted root conduit ids.
        """
        self.check_cleaned()
        return self.get_view_multiframe().list_root_conduit_ids(frame_name=frame_name)

    def count_spellbooks(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> int:
        """
        Return the number of distinct published origin spellbooks.

        Purpose:
            Surface spellbook provenance breadth at the descriptor host level.

        Contract:
            - FACADE PASS-THROUGH to `ViewMultiFrame.count_spellbooks(...)`. Filtering, ordering and raise
              behaviour are that method's; this adds no logic of its own.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL: `get_view_multiframe()` constructs a new
              ViewMultiFrame against a newly resolved descriptor snapshot, so a loop of
              facade calls rebuilds the projection each time and TWO FACADE CALLS NEED
              NOT SEE THE SAME FRAME STATE. Hold one sub-viewer when results must be
              mutually consistent.
            - VISIBILITY-FILTERED: absence means "not visible to this rift" OR "not
              present" - never proof of non-existence.
            - Descriptor-hosted and CROSS-FRAME: no frame selection happens here.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, counts distinct
                spellbook ids across all hosted frames.

        Returns:
            int: Distinct origin spellbook count.
        """
        self.check_cleaned()
        return self.get_view_multiframe().count_spellbooks(frame_name=frame_name)

    def list_origin_spellbook_ids(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return distinct origin spellbook ids for the selected scope.

        Purpose:
            Expose the spellbook provenance ids attached to the hosted spell
            records.

        Contract:
            - FACADE PASS-THROUGH to `ViewMultiFrame.list_origin_spellbook_ids(...)`. Filtering, ordering and raise
              behaviour are that method's; this adds no logic of its own.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL: `get_view_multiframe()` constructs a new
              ViewMultiFrame against a newly resolved descriptor snapshot, so a loop of
              facade calls rebuilds the projection each time and TWO FACADE CALLS NEED
              NOT SEE THE SAME FRAME STATE. Hold one sub-viewer when results must be
              mutually consistent.
            - VISIBILITY-FILTERED: absence means "not visible to this rift" OR "not
              present" - never proof of non-existence.
            - Descriptor-hosted and CROSS-FRAME: no frame selection happens here.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, returns distinct
                spellbook ids across all hosted frames.

        Returns:
            List[str]: Distinct spellbook ids in deterministic order.
        """
        self.check_cleaned()
        return self.get_view_multiframe().list_origin_spellbook_ids(frame_name=frame_name)

    def list_spell_record_ids(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return published spell record ids for the selected scope.

        Purpose:
            Expose spell ids directly from `SpellRecord` ownership without
            surfacing payload bodies.

        Contract:
            - FACADE PASS-THROUGH to `ViewMultiFrame.list_spell_record_ids(...)`. Filtering, ordering and raise
              behaviour are that method's; this adds no logic of its own.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL: `get_view_multiframe()` constructs a new
              ViewMultiFrame against a newly resolved descriptor snapshot, so a loop of
              facade calls rebuilds the projection each time and TWO FACADE CALLS NEED
              NOT SEE THE SAME FRAME STATE. Hold one sub-viewer when results must be
              mutually consistent.
            - VISIBILITY-FILTERED: absence means "not visible to this rift" OR "not
              present" - never proof of non-existence.
            - Descriptor-hosted and CROSS-FRAME: no frame selection happens here.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, returns spell ids
                across all hosted frames.

        Returns:
            List[str]: Spell ids in deterministic record order.
        """
        self.check_cleaned()
        return self.get_view_multiframe().list_spell_record_ids(frame_name=frame_name)

    def list_spell_record_keys(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[Tuple[str, str]]:
        """
        Return canonical spell record keys for the selected scope.

        Purpose:
            Surface the exact `(spellbook_id, spell_id)` storage identities
            attached to the selected descriptors.

        Contract:
            - FACADE PASS-THROUGH to `ViewMultiFrame.list_spell_record_keys(...)`. Filtering, ordering and raise
              behaviour are that method's; this adds no logic of its own.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL: `get_view_multiframe()` constructs a new
              ViewMultiFrame against a newly resolved descriptor snapshot, so a loop of
              facade calls rebuilds the projection each time and TWO FACADE CALLS NEED
              NOT SEE THE SAME FRAME STATE. Hold one sub-viewer when results must be
              mutually consistent.
            - VISIBILITY-FILTERED: absence means "not visible to this rift" OR "not
              present" - never proof of non-existence.
            - Descriptor-hosted and CROSS-FRAME: no frame selection happens here.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, returns record keys
                across all hosted frames.

        Returns:
            List[Tuple[str, str]]: Spell record keys in deterministic order.
        """
        self.check_cleaned()
        return self.get_view_multiframe().list_spell_record_keys(frame_name=frame_name)

    def list_spell_names(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return published spell names for the selected scope.

        Purpose:
            Expose spell-name inventory directly from `SpellRecord` metadata.

        Contract:
            - FACADE PASS-THROUGH to `ViewMultiFrame.list_spell_names(...)`. Filtering, ordering and raise
              behaviour are that method's; this adds no logic of its own.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL: `get_view_multiframe()` constructs a new
              ViewMultiFrame against a newly resolved descriptor snapshot, so a loop of
              facade calls rebuilds the projection each time and TWO FACADE CALLS NEED
              NOT SEE THE SAME FRAME STATE. Hold one sub-viewer when results must be
              mutually consistent.
            - VISIBILITY-FILTERED: absence means "not visible to this rift" OR "not
              present" - never proof of non-existence.
            - Descriptor-hosted and CROSS-FRAME: no frame selection happens here.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, returns spell names
                across all hosted frames.

        Returns:
            List[str]: Spell names in deterministic record order.
        """
        self.check_cleaned()
        return self.get_view_multiframe().list_spell_names(frame_name=frame_name)

    def list_binding_names(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return published binding names for the selected scope.

        Purpose:
            Expose the spell binding identities currently represented in the
            hosted descriptors.

        Contract:
            - FACADE PASS-THROUGH to `ViewMultiFrame.list_binding_names(...)`. Filtering, ordering and raise
              behaviour are that method's; this adds no logic of its own.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL: `get_view_multiframe()` constructs a new
              ViewMultiFrame against a newly resolved descriptor snapshot, so a loop of
              facade calls rebuilds the projection each time and TWO FACADE CALLS NEED
              NOT SEE THE SAME FRAME STATE. Hold one sub-viewer when results must be
              mutually consistent.
            - VISIBILITY-FILTERED: absence means "not visible to this rift" OR "not
              present" - never proof of non-existence.
            - Descriptor-hosted and CROSS-FRAME: no frame selection happens here.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, returns binding names
                across all hosted frames.

        Returns:
            List[str]: Non-empty binding names in deterministic record order.
        """
        self.check_cleaned()
        return self.get_view_multiframe().list_binding_names(frame_name=frame_name)

    def list_index_ids(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return spell-index ids for the selected descriptor scope.

        Purpose:
            Expose SpellIndex identity directly from `SpellRecord` metadata.

        Contract:
            - FACADE PASS-THROUGH to `ViewMultiFrame.list_index_ids(...)`. Filtering, ordering and raise
              behaviour are that method's; this adds no logic of its own.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL: `get_view_multiframe()` constructs a new
              ViewMultiFrame against a newly resolved descriptor snapshot, so a loop of
              facade calls rebuilds the projection each time and TWO FACADE CALLS NEED
              NOT SEE THE SAME FRAME STATE. Hold one sub-viewer when results must be
              mutually consistent.
            - VISIBILITY-FILTERED: absence means "not visible to this rift" OR "not
              present" - never proof of non-existence.
            - Descriptor-hosted and CROSS-FRAME: no frame selection happens here.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, returns spell-index ids
                across all hosted frames.

        Returns:
            List[str]: Spell-index ids in deterministic record order.
        """
        self.check_cleaned()
        return self.get_view_multiframe().list_index_ids(frame_name=frame_name)

    def list_spellframes(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return normalized spellframe values for the selected scope.

        Purpose:
            Surface the logical spellframe inventory directly from
            `SpellRecord.spellframe` without exposing payload data.

        Contract:
            - FACADE PASS-THROUGH to `ViewMultiFrame.list_spellframes(...)`. Filtering, ordering and raise
              behaviour are that method's; this adds no logic of its own.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL: `get_view_multiframe()` constructs a new
              ViewMultiFrame against a newly resolved descriptor snapshot, so a loop of
              facade calls rebuilds the projection each time and TWO FACADE CALLS NEED
              NOT SEE THE SAME FRAME STATE. Hold one sub-viewer when results must be
              mutually consistent.
            - VISIBILITY-FILTERED: absence means "not visible to this rift" OR "not
              present" - never proof of non-existence.
            - Descriptor-hosted and CROSS-FRAME: no frame selection happens here.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, returns unique
                spellframe values across all hosted frames.

        Returns:
            List[str]: Distinct normalized spellframe values in deterministic
            order.
        """
        self.check_cleaned()
        return self.get_view_multiframe().list_spellframes(frame_name=frame_name)

    def list_permissions(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return distinct spell permission names for the selected scope.

        Purpose:
            Surface the spell permission posture currently represented in the
            hosted descriptors.

        Contract:
            - FACADE PASS-THROUGH to `ViewMultiFrame.list_permissions(...)`. Filtering, ordering and raise
              behaviour are that method's; this adds no logic of its own.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL: `get_view_multiframe()` constructs a new
              ViewMultiFrame against a newly resolved descriptor snapshot, so a loop of
              facade calls rebuilds the projection each time and TWO FACADE CALLS NEED
              NOT SEE THE SAME FRAME STATE. Hold one sub-viewer when results must be
              mutually consistent.
            - VISIBILITY-FILTERED: absence means "not visible to this rift" OR "not
              present" - never proof of non-existence.
            - Descriptor-hosted and CROSS-FRAME: no frame selection happens here.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, returns permission
                names across all hosted frames.

        Returns:
            List[str]: Distinct permission names in deterministic order.
        """
        self.check_cleaned()
        return self.get_view_multiframe().list_permissions(frame_name=frame_name)

    def list_existence_kinds(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return distinct spell existence kinds for the selected scope.

        Purpose:
            Surface spell lifetime categories directly from `SpellRecord`
            metadata.

        Contract:
            - FACADE PASS-THROUGH to `ViewMultiFrame.list_existence_kinds(...)`. Filtering, ordering and raise
              behaviour are that method's; this adds no logic of its own.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL: `get_view_multiframe()` constructs a new
              ViewMultiFrame against a newly resolved descriptor snapshot, so a loop of
              facade calls rebuilds the projection each time and TWO FACADE CALLS NEED
              NOT SEE THE SAME FRAME STATE. Hold one sub-viewer when results must be
              mutually consistent.
            - VISIBILITY-FILTERED: absence means "not visible to this rift" OR "not
              present" - never proof of non-existence.
            - Descriptor-hosted and CROSS-FRAME: no frame selection happens here.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, returns existence
                kinds across all hosted frames.

        Returns:
            List[str]: Distinct existence-kind names in deterministic order.
        """
        self.check_cleaned()
        return self.get_view_multiframe().list_existence_kinds(frame_name=frame_name)

    def describe_descriptor_inventory(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return a descriptor-only inventory summary for the selected scope.

        Purpose:
            Give the operator one compact host-level answer to "what descriptors
            do I have here?" without crossing into payload bodies.

        Contract:
            - Uses only `FrameRecord`, `ConduitRecord`, and `SpellRecord`
              identity/provenance fields.
            - May summarize one frame or the entire hosted viewer scope.
            - Does not expose payload body contents.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, summarizes all hosted
                descriptors together.

        Returns:
            Dict[str, object]: Descriptor-only inventory summary.
        """
        self.check_cleaned()
        return self.get_view_multiframe().describe_descriptor_inventory(frame_name=frame_name)

    def describe_descriptor_topology(self, frame_name: str) -> Dict[str, object]:
        """
        Return descriptor-topology groupings for one hosted frame.

        Purpose:
            Surface the descriptor-owned conduit/spell index structure in one
            place so the operator can understand how records are grouped before
            moving into payload-aware helper methods.

        Contract:
            - Uses only descriptor-owned indexes and record identity fields.
            - Does not expose payload body contents.
            - Requires one concrete hosted frame.

        Args:
            frame_name:
                Hosted frame name whose descriptor topology should be
                summarized.

        Returns:
            Dict[str, object]: Descriptor topology summary for the frame.
        """
        self.check_cleaned()
        return self.get_view_multiframe().describe_descriptor_topology(frame_name)

    def describe_conduit_records(self, frame_name: str) -> List[Dict[str, object]]:
        """
        Return descriptor-only conduit record descriptions for one frame.

        Purpose:
            Surface the conduit record identities and lineage grouping owned by
            one frame descriptor without exposing conduit payload bodies.

        Contract:
            - FACADE PASS-THROUGH to `ViewMultiFrame.describe_conduit_records(...)`. Filtering, ordering and raise
              behaviour are that method's; this adds no logic of its own.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL: `get_view_multiframe()` constructs a new
              ViewMultiFrame against a newly resolved descriptor snapshot, so a loop of
              facade calls rebuilds the projection each time and TWO FACADE CALLS NEED
              NOT SEE THE SAME FRAME STATE. Hold one sub-viewer when results must be
              mutually consistent.
            - VISIBILITY-FILTERED: absence means "not visible to this rift" OR "not
              present" - never proof of non-existence.
            - Descriptor-hosted and CROSS-FRAME: no frame selection happens here.

        Args:
            frame_name:
                Hosted frame name whose conduit records should be described.

        Returns:
            List[Dict[str, object]]: Conduit record descriptions.
        """
        self.check_cleaned()
        return self.get_view_multiframe().describe_conduit_records(frame_name)

    def describe_spell_records(self, frame_name: str) -> List[Dict[str, object]]:
        """
        Return descriptor-only spell record descriptions for one frame.

        Purpose:
            Surface spell record identities and provenance directly from
            `SpellRecord` without crossing into spell payload bodies.

        Contract:
            - FACADE PASS-THROUGH to `ViewMultiFrame.describe_spell_records(...)`. Filtering, ordering and raise
              behaviour are that method's; this adds no logic of its own.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL: `get_view_multiframe()` constructs a new
              ViewMultiFrame against a newly resolved descriptor snapshot, so a loop of
              facade calls rebuilds the projection each time and TWO FACADE CALLS NEED
              NOT SEE THE SAME FRAME STATE. Hold one sub-viewer when results must be
              mutually consistent.
            - VISIBILITY-FILTERED: absence means "not visible to this rift" OR "not
              present" - never proof of non-existence.
            - Descriptor-hosted and CROSS-FRAME: no frame selection happens here.

        Args:
            frame_name:
                Hosted frame name whose spell records should be described.

        Returns:
            List[Dict[str, object]]: Spell record descriptions.
        """
        self.check_cleaned()
        return self.get_view_multiframe().describe_spell_records(frame_name)

    def describe_spell_record(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return one descriptor-only spell record description.

        Purpose:
            Give the operator one exact spell-record view built strictly from
            record identity and provenance fields.

        Contract:
            - Uses only `SpellRecord` fields and normalized spellframe values.
            - Does not expose payload body content.
            - When `frame_name` is omitted, searches the hosted frames for a
              unique matching spell source id.

        Args:
            spell_source_id:
                Published spell source id in `spellbook_id:spell_id` form.
            frame_name:
                Optional hosted frame name to constrain the lookup.

        Returns:
            Dict[str, object]: Descriptor-only spell record description.
        """
        self.check_cleaned()
        return self.get_view_multiframe().describe_spell_record(spell_source_id, frame_name=frame_name)

    def list_spells_by_owner_conduit(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return spell source ids owned by one conduit.

        Purpose:
            Expose spell ownership at the descriptor host level without
            requiring a payload-aware helper path.

        Contract:
            - FACADE PASS-THROUGH to `ViewMultiFrame.list_spells_by_owner_conduit(...)`. Filtering, ordering and raise
              behaviour are that method's; this adds no logic of its own.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL: `get_view_multiframe()` constructs a new
              ViewMultiFrame against a newly resolved descriptor snapshot, so a loop of
              facade calls rebuilds the projection each time and TWO FACADE CALLS NEED
              NOT SEE THE SAME FRAME STATE. Hold one sub-viewer when results must be
              mutually consistent.
            - VISIBILITY-FILTERED: absence means "not visible to this rift" OR "not
              present" - never proof of non-existence.
            - Descriptor-hosted and CROSS-FRAME: no frame selection happens here.

        Args:
            conduit_id:
                Required owner conduit id.
            frame_name:
                Optional hosted frame name. When omitted, scans all hosted
                frames.

        Returns:
            List[str]: Matching spell source ids in deterministic order.
        """
        self.check_cleaned()
        return self.get_view_multiframe().list_spells_by_owner_conduit(conduit_id, frame_name=frame_name)

    def list_spells_by_spellbook_id(
            self,
            spellbook_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return spell source ids published by one origin spellbook.

        Args:
            spellbook_id:
                Required origin spellbook id.
            frame_name:
                Optional hosted frame name. When omitted, scans all hosted
                frames.

        Contract:
            - FACADE PASS-THROUGH to `ViewMultiFrame.list_spells_by_spellbook_id(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_multiframe()` constructs a new
              ViewMultiFrame per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - Descriptor-hosted and CROSS-FRAME: the multi-frame helper is not bound
              to a single frame, so no frame selection happens here.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            List[str]: Matching spell source ids in deterministic order.
        """
        self.check_cleaned()
        return self.get_view_multiframe().list_spells_by_spellbook_id(spellbook_id, frame_name=frame_name)

    def list_spells_by_permission(
            self,
            permission: str,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return spell source ids with one permission posture.

        Args:
            permission:
                Required permission name.
            frame_name:
                Optional hosted frame name. When omitted, scans all hosted
                frames.

        Contract:
            - FACADE PASS-THROUGH to `ViewMultiFrame.list_spells_by_permission(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_multiframe()` constructs a new
              ViewMultiFrame per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - Descriptor-hosted and CROSS-FRAME: the multi-frame helper is not bound
              to a single frame, so no frame selection happens here.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            List[str]: Matching spell source ids in deterministic order.
        """
        self.check_cleaned()
        return self.get_view_multiframe().list_spells_by_permission(permission, frame_name=frame_name)

    def list_spells_by_existence(
            self,
            existence: str,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return spell source ids with one existence posture.

        Args:
            existence:
                Required existence-kind name.
            frame_name:
                Optional hosted frame name. When omitted, scans all hosted
                frames.

        Contract:
            - FACADE PASS-THROUGH to `ViewMultiFrame.list_spells_by_existence(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_multiframe()` constructs a new
              ViewMultiFrame per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - Descriptor-hosted and CROSS-FRAME: the multi-frame helper is not bound
              to a single frame, so no frame selection happens here.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            List[str]: Matching spell source ids in deterministic order.
        """
        self.check_cleaned()
        return self.get_view_multiframe().list_spells_by_existence(existence, frame_name=frame_name)

    def list_spells_by_spellframe(
            self,
            spellframe_name: str,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return spell source ids with one normalized spellframe value.

        Args:
            spellframe_name:
                Required normalized spellframe name.
            frame_name:
                Optional hosted frame name. When omitted, scans all hosted
                frames.

        Contract:
            - FACADE PASS-THROUGH to `ViewMultiFrame.list_spells_by_spellframe(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_multiframe()` constructs a new
              ViewMultiFrame per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - Descriptor-hosted and CROSS-FRAME: the multi-frame helper is not bound
              to a single frame, so no frame selection happens here.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            List[str]: Matching spell source ids in deterministic order.
        """
        self.check_cleaned()
        return self.get_view_multiframe().list_spells_by_spellframe(spellframe_name, frame_name=frame_name)

    def clone(self) -> "FrameViewer":
        """
        Return a detached copy of the viewer host.

        Purpose:
            Preserve the borrowed Rift reference while creating a detached
            viewer object with no additional local state.

        Contract:
            - Produces a NEW viewer over THE SAME rift and the same action-hook scope
              factory - it copies the wiring, NOT any state, because a viewer holds no
              cached projection to copy.
            - The clone is INDEPENDENTLY OWNED: cleaning it does not clean this viewer,
              and both remain valid over the shared rift.
            - Useful for handing a viewer to another thread without sharing this one;
              it is not a snapshot and will see the same live frame state.

        Returns:
            FrameViewer: Detached viewer clone.
        """
        self.check_cleaned()
        with self._lock:
            return FrameViewer(
                rift=self._rift,
                action_hook_scope_factory=self._action_hook_scope_factory,
            )



    def get_view_frame(
            self,
            frame_name: Optional[str] = None,
    ) -> ViewFrame:
        """
        Return one frame helper bound to the requested frame.

        Args:
            frame_name:
                Required hosted frame name.

        Contract:
            - CONSTRUCTS A FRESH `ViewFrame` ON EVERY CALL. Nothing is cached, so
              two calls return two distinct objects over two distinct descriptor
              snapshots. HOLD THE RESULT if you want a stable view or want to make
              several queries against one consistent snapshot.
            - `frame_name` is a SELECTOR here - it resolves which hosted frame to
              bind. Inside the returned helper the same parameter becomes an
              ASSERTION that must match this binding. Passing None resolves the
              viewer's currently selected frame.
            - Binds the descriptor, ACL configuration and compiled access surface
              together at construction, so the returned helper is internally
              consistent even if the frame changes afterwards.
            - Built at `detailed` detail level and wired to this viewer's action
              hook scope.

        Threading:
            Takes a descriptor snapshot at construction; the returned helper does
            not track later frame changes.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The returned helper is owned by the
            CALLER; this viewer does not retain or clean it.

        Raises:
            RuntimeError: If the frame cannot be resolved, or the viewer has been
                cleaned.

        Returns:
            ViewFrame: Selected-frame helper surface.
        """
        self.check_cleaned()
        selected_frame_name = self._get_required_selected_frame_name(frame_name)
        return ViewFrame(
            frame_name=selected_frame_name,
            frame_descriptor=self._get_required_frame_descriptor(selected_frame_name),
            frame_acl_configuration=self._get_required_frame_acl_configuration(
                selected_frame_name
            ),
            compiled_access_surface=self._get_required_compiled_access_surface(
                selected_frame_name
            ),
            default_detail_level="detailed",
            action_hook_scope_factory=self._entered_view_action,
        )

    def get_view_conduit(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> ViewConduit:
        """
        Return one conduit helper bound to the requested frame.

        Args:
            frame_name:
                Required hosted frame name.

        Contract:
            - CONSTRUCTS A FRESH `ViewConduit` ON EVERY CALL, and a fresh `ViewFrame`
              beneath it. Two calls therefore cost two full projections; hold the
              result when making several conduit queries.
            - The returned helper BORROWS its frame view - it does not own it - so
              the two share one descriptor snapshot and stay mutually consistent.
            - `frame_name` is a SELECTOR here and becomes an ASSERTION inside the
              helper.
            - Does NOT call `check_cleaned()` itself; the guard comes from the
              `get_view_frame(...)` call it delegates to.

        Threading:
            Snapshot-bound at construction; does not track later frame changes.

        Lifecycle / Cleanup:
            The returned helper is owned by the CALLER.

        Raises:
            RuntimeError: If the frame cannot be resolved, or the viewer has been
                cleaned.

        Returns:
            ViewConduit: Bound conduit helper surface.
        """
        return ViewConduit(
            frame_view=self.get_view_frame(frame_name=frame_name),
        )

    def get_view_spell(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> ViewSpell:
        """
        Return one spell helper bound to the requested frame.

        Args:
            frame_name:
                Required hosted frame name.

        Contract:
            - CONSTRUCTS A FRESH `ViewSpell` ON EVERY CALL, and a fresh `ViewFrame`
              beneath it. Two calls cost two full projections; hold the result when
              making several spell queries.
            - The returned helper BORROWS its frame view - it does not own it - so
              the two share one descriptor snapshot and stay mutually consistent.
            - `frame_name` is a SELECTOR here and becomes an ASSERTION inside the
              helper.
            - Does NOT call `check_cleaned()` itself; the guard comes from the
              `get_view_frame(...)` call it delegates to.

        Threading:
            Snapshot-bound at construction; does not track later frame changes.

        Lifecycle / Cleanup:
            The returned helper is owned by the CALLER.

        Raises:
            RuntimeError: If the frame cannot be resolved, or the viewer has been
                cleaned.

        Returns:
            ViewSpell: Bound spell helper surface.
        """
        return ViewSpell(
            frame_view=self.get_view_frame(frame_name=frame_name),
        )

    def get_view_multiframe(self) -> ViewMultiFrame:
        """
        Return one descriptor-hosted multi-frame helper.

        Contract:
            - CONSTRUCTS A FRESH `ViewMultiFrame` ON EVERY CALL; nothing is cached.
            - CROSS-FRAME by design, so it takes no frame selector and is not bound
              to one frame's snapshot. It reaches back through THIS viewer for each
              frame it inspects, which is why it is the one helper that can compare
              across frames.
            - Because it holds this viewer rather than a snapshot, its reads are
              resolved later rather than frozen at construction - the opposite of
              the single-frame helpers.

        Threading:
            Resolves per query rather than from one snapshot, so two of its calls
            can observe different frame states.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. It BORROWS this viewer, so it must not
            outlive it; the returned helper is owned by the CALLER.

        Raises:
            RuntimeError: If the viewer has been cleaned.

        Returns:
            ViewMultiFrame: Fresh helper for cross-frame and descriptor-hosted
            inventory/comparison logic.
        """
        self.check_cleaned()
        return ViewMultiFrame(viewer=self)

    def list_viewer_method_names_ast_json(
            self,
            *,
            include_private: bool = False,
            include_dunder: bool = False,
    ) -> str:
        """
        Return a minified JSON list of `FrameViewer` class method names.

        Purpose:
            Give the agent a source-defined list of host methods available on
            the viewer itself without inspecting method bodies or runtime
            internals.

        Contract:
            - Reports THIS VIEWER'S OWN method names, not the frame's contents, so it
              carries no frame data and needs no ACL filtering.
            - `include_private` and `include_dunder` widen the surface; both default to
              the narrow agent-facing view.
            - Returned MINIFIED as JSON for token efficiency - it is meant to be handed
              to an agent rather than read by a human.

        Args:
            include_private:
                Whether `_private` methods should be included.
            include_dunder:
                Whether `__dunder__` methods should be included.

        Returns:
            str: Minified JSON list of source-defined `FrameViewer` methods.
        """
        self.check_cleaned()
        return ClassSurfaceAstDescriber.list_class_method_names_ast_json(
            self,
            include_private=include_private,
            include_dunder=include_dunder,
        )

    def describe_agent_onboarding_json(self) -> str:
        """
        Return the shared first-time onboarding hint for Melder agents.

        Contract:
            - STATIC CONTENT: the onboarding hint is produced by
              `ClassSurfaceAstDescriber` and is identical for every viewer and every
              frame. It describes how to drive Melder's agent surface, NOT anything
              about this rift's contents, so it leaks no frame data and needs no ACL
              filtering.
            - Returned MINIFIED for token efficiency - it is meant to be handed to
              an agent, not read by a human.

        Threading:
            No viewer state is read beyond the cleaned check.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the viewer has been cleaned.

        Returns:
            str: Minified JSON onboarding hint for Melder agents.
        """
        self.check_cleaned()
        return ClassSurfaceAstDescriber.describe_agent_onboarding_json()

    def describe_viewer_agent_purpose_json(self) -> str:
        """
        Return the minified JSON agent-purpose surface for the viewer host.

        Contract:
            - Describes THIS VIEWER'S OWN callable surface - the agent-facing
              contract of the object you are holding - not the frame it projects.
              It is built from the class's `__agent_purpose__` and
              `__ast_helper_access__` markers by `ClassSurfaceAstDescriber`.
            - Reports the SHAPE of the API, so it carries no frame contents and
              needs no ACL filtering.
            - Returned MINIFIED for token efficiency.

        Threading:
            Reflects over the class, not over frame state.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the viewer has been cleaned.

        Returns:
            str: Minified JSON agent-purpose surface for this viewer.
        """
        self.check_cleaned()
        return ClassSurfaceAstDescriber.describe_agent_purpose_json(self)

    def describe_viewer_class_surface_ast_json(
            self,
            *,
            include_private: bool = False,
            include_dunder: bool = False,
    ) -> str:
        """
        Return a minified JSON description of the `FrameViewer` class surface.

        Purpose:
            Expose the source-defined `FrameViewer` class surface, including
            method signatures, properties, and docstrings, for direct agent
            consumption.

        Contract:
            - Describes THIS VIEWER'S CALLABLE SURFACE - signatures and the agent
              markers on the class - rather than the frame it projects, so it is safe
              regardless of ACL.
            - Richer than `list_viewer_method_names_ast_json`, which returns names only.
            - Returned MINIFIED as JSON for token efficiency.

        Args:
            include_private:
                Whether `_private` members should be included.
            include_dunder:
                Whether `__dunder__` members should be included.

        Returns:
            str: Minified JSON description of the `FrameViewer` class surface.
        """
        self.check_cleaned()
        return ClassSurfaceAstDescriber.describe_class_surface_ast_json(
            self,
            include_private=include_private,
            include_dunder=include_dunder,
        )



    def _get_required_selected_frame_name(
            self,
            frame_name: Optional[str] = None,
    ) -> str:
        """
        Return one explicitly requested hosted frame name.

        Args:
            frame_name:
                Required hosted frame name. `None` is rejected because the
                viewer no longer supports default-frame routing for
                frame-local operations.

        Returns:
            str: Selected hosted frame name.
        """
        if frame_name is None:
            raise ValueError("frame_name is required.")
        if not frame_name:
            raise ValueError("frame_name cannot be empty.")
        self._get_required_frame_descriptor(frame_name)
        return frame_name

    def _get_frame_names_for_query(
            self,
            frame_name: Optional[str] = None,
    ) -> Tuple[str, ...]:
        """
        Return the concrete hosted frame names for one query.

        Args:
            frame_name:
                Optional hosted frame name filter.

        Returns:
            Tuple[str, ...]: Hosted frame names for the query.
        """
        if frame_name is not None:
            return (self._get_required_selected_frame_name(frame_name),)
        return tuple(self.list_frame_names())

    def _iter_conduit_records(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Iterator[ConduitRecord]:
        """
        Yield descriptor-owned conduit records for the selected frame scope.

        Args:
            frame_name:
                Optional hosted frame name filter.

        Yields:
            ConduitRecord: Descriptor-owned conduit records.
        """
        for current_frame_name in self._get_frame_names_for_query(frame_name):
            descriptor = self._get_required_frame_descriptor(current_frame_name)
            for conduit_id in sorted(descriptor.conduit_records_by_id.keys()):
                yield descriptor.conduit_records_by_id[conduit_id]

    def _iter_spell_records(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Iterator[SpellRecord]:
        """
        Yield descriptor-owned spell records for the selected frame scope.

        Args:
            frame_name:
                Optional hosted frame name filter.

        Yields:
            SpellRecord: Descriptor-owned spell records.
        """
        for current_frame_name in self._get_frame_names_for_query(frame_name):
            descriptor = self._get_required_frame_descriptor(current_frame_name)
            for record_key in sorted(descriptor.spell_records_by_key.keys()):
                yield descriptor.spell_records_by_key[record_key]

    @staticmethod
    def _build_spell_source_id(spell_record: SpellRecord) -> str:
        """
        Build the published spell source id for one spell record.

        Args:
            spell_record:
                Descriptor-owned spell record.

        Returns:
            str: Published spell source id in `spellbook_id:spell_id` form.
        """
        return "{0}:{1}".format(
            spell_record.origin_spellbook_id,
            spell_record.spell_id,
        )

    @staticmethod
    def _normalize_spellframe_value(spellframe: object) -> Optional[str]:
        """
        Return one stable string view of a spellframe value.

        Args:
            spellframe:
                Raw spellframe value.

        Returns:
            Optional[str]: Normalized spellframe name when present.
        """
        if spellframe is None:
            return None
        if isinstance(spellframe, str):
            return spellframe
        if isinstance(spellframe, type):
            return spellframe.__name__
        return str(spellframe)

    @staticmethod
    def _normalize_policy_name(policy: Optional[Policies]) -> Optional[str]:
        """
        Return one stable string view of a conduit policy value.

        Args:
            policy:
                Raw conduit policy value.

        Returns:
            Optional[str]: Normalized conduit policy name when present.
        """
        if policy is None:
            return None
        return policy.name

    @staticmethod
    def _parse_spell_source_id(spell_source_id: str) -> Tuple[str, str]:
        """
        Parse one published spell source id into its canonical record key.

        Args:
            spell_source_id:
                Published spell source id in `spellbook_id:spell_id` form.

        Returns:
            Tuple[str, str]: `(spellbook_id, spell_id)` key.
        """
        parts = spell_source_id.split(":", 1)
        if len(parts) != 2:
            raise ValueError(
                "spell_source_id '{0}' must be in 'spellbook_id:spell_id' form.".format(
                    spell_source_id
                )
            )
        return parts[0], parts[1]

    def _get_required_spell_record(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Tuple[str, SpellRecord]:
        """
        Return one descriptor-owned spell record plus its hosted frame.

        Args:
            spell_source_id:
                Published spell source id in `spellbook_id:spell_id` form.
            frame_name:
                Optional hosted frame name to constrain the lookup.

        Returns:
            Tuple[str, SpellRecord]: `(frame_name, spell_record)` for the
            resolved record.
        """
        if not spell_source_id:
            raise ValueError("spell_source_id cannot be empty.")
        spellbook_id, spell_id = self._parse_spell_source_id(spell_source_id)
        matching_records: List[Tuple[str, SpellRecord]] = []
        for current_frame_name in self._get_frame_names_for_query(frame_name):
            descriptor = self._get_required_frame_descriptor(current_frame_name)
            record = descriptor.spell_records_by_key.get((spellbook_id, spell_id))
            if record is None:
                continue
            matching_records.append((current_frame_name, record))
        if len(matching_records) == 0:
            raise ValueError(
                "Spell source id '{0}' was not found.".format(spell_source_id)
            )
        if len(matching_records) > 1:
            raise ValueError(
                "Spell source id '{0}' is ambiguous across hosted frames.".format(
                    spell_source_id
                )
            )
        return matching_records[0]

    def _get_required_conduit_record(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> ConduitRecord:
        """
        Return one descriptor-owned conduit record or raise.

        Args:
            conduit_id:
                Published conduit id.
            frame_name:
                Optional hosted frame name to constrain the lookup.

        Returns:
            ConduitRecord: Descriptor-owned conduit record.
        """
        if not conduit_id:
            raise ValueError("conduit_id cannot be empty.")
        matching_records: List[ConduitRecord] = []
        for current_frame_name in self._get_frame_names_for_query(frame_name):
            descriptor = self._get_required_frame_descriptor(current_frame_name)
            conduit_record = descriptor.conduit_records_by_id.get(conduit_id)
            if conduit_record is None:
                continue
            matching_records.append(conduit_record)
        if len(matching_records) == 0:
            raise ValueError("Conduit id '{0}' was not found.".format(conduit_id))
        if len(matching_records) > 1:
            raise ValueError(
                "Conduit id '{0}' is ambiguous across hosted frames.".format(
                    conduit_id
                )
            )
        return matching_records[0]

    def _describe_spell_value_groups(
            self,
            *,
            frame_name: Optional[str],
            value_getter: Callable[[object], Optional[object]],
    ) -> Dict[str, Tuple[str, ...]]:
        """
        Group spell source ids by one normalized spell-record value.

        Args:
            frame_name:
                Optional hosted frame name filter.
            value_getter:
                Callable that extracts the grouping value from one spell
                record.

        Returns:
            Dict[str, Tuple[str, ...]]: Grouping value mapped to spell source
            ids.
        """
        return self.get_view_multiframe()._describe_spell_value_groups(
            frame_name=frame_name,
            value_getter=value_getter,
        )

    def describe_visible_surface(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return the current visible frame-local surface in one summary.

        Purpose:
            Give the operator a single "what can I actually see right now?"
            entry point over the selected frame without making them manually
            merge inventory, topology, and access-contract calls.

        Contract:
            - Uses only the selected frame descriptor plus the compiled ACL
              surface.
            - Summarizes the currently visible target ids, grouped inventory,
              visible topology, and access contract.
            - Remains frame-local; it never spans multiple hosted frames.

        Args:
            frame_name:
                Optional hosted frame name override.

        Returns:
            Dict[str, object]: Summary of the currently visible frame-local
            surface.
        """
        return self.get_view_frame(frame_name=frame_name).describe_visible_surface(
            frame_name=frame_name,
        )

    def describe_missing_surface(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return what is currently hidden or absent from the selected frame
        surface.

        Purpose:
            Help the operator answer "what am I not seeing right now?" by
            comparing descriptor-owned records and payload fields against the
            currently visible ACL-shaped surface.

        Contract:
            - Uses descriptor truth plus the compiled ACL surface only.
            - Distinguishes hidden frame payload fields, hidden conduit/spell
              records, and payload sections not currently visible.
            - Does not expose hidden payload bodies.

        Args:
            frame_name:
                Optional hosted frame name override.

        Returns:
            Dict[str, object]: Missing/hidden surface summary.
        """
        return self.get_view_frame(frame_name=frame_name).describe_missing_surface(
            frame_name=frame_name,
        )

    def describe_frame_brief_local(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return one compact operator-oriented frame summary.

        Purpose:
            Give the operator a smaller "start here" summary than the richer
            frame surface methods while still reflecting visible inventory and
            ACL posture.

        Contract:
            - FACADE PASS-THROUGH to `ViewFrame.describe_frame_brief(...)`. Filtering, ordering and raise
              behaviour are that method's; this adds no logic of its own.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL: `get_view_frame()` constructs a new
              ViewFrame against a newly resolved descriptor snapshot, so a loop of
              facade calls rebuilds the projection each time and TWO FACADE CALLS NEED
              NOT SEE THE SAME FRAME STATE. Hold one sub-viewer when results must be
              mutually consistent.
            - VISIBILITY-FILTERED: absence means "not visible to this rift" OR "not
              present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and becomes an ASSERTION
              inside the sub-viewer. Passing None resolves the selected frame.

        Args:
            frame_name:
                Optional hosted frame name override.

        Returns:
            Dict[str, object]: Compact frame-local summary.
        """
        return self.get_view_frame(frame_name=frame_name).describe_frame_brief(
            frame_name=frame_name,
        )

    def describe_visible_inventory_by_kind(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, Dict[str, object]]:
        """
        Return visible inventory grouped by target kind.

        Purpose:
            Provide a frame-local grouped inventory over visible targets so the
            operator can see counts, source ids, and names without manually
            regrouping raw links.

        Contract:
            - FACADE PASS-THROUGH to `ViewFrame.describe_visible_inventory_by_kind(...)`. Filtering, ordering and raise
              behaviour are that method's; this adds no logic of its own.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL: `get_view_frame()` constructs a new
              ViewFrame against a newly resolved descriptor snapshot, so a loop of
              facade calls rebuilds the projection each time and TWO FACADE CALLS NEED
              NOT SEE THE SAME FRAME STATE. Hold one sub-viewer when results must be
              mutually consistent.
            - VISIBILITY-FILTERED: absence means "not visible to this rift" OR "not
              present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and becomes an ASSERTION
              inside the sub-viewer. Passing None resolves the selected frame.

        Args:
            frame_name:
                Optional hosted frame name override.

        Returns:
            Dict[str, Dict[str, object]]: Inventory grouped by target kind.
        """
        return self.get_view_frame(
            frame_name=frame_name,
        ).describe_visible_inventory_by_kind(frame_name=frame_name)

    def describe_frame_topology(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return the visible conduit/spell topology for the selected frame.

        Purpose:
            Summarize how the currently visible conduits and spells relate to
            each other so the operator can navigate the frame structure without
            reading each target individually first.

        Contract:
            - FACADE PASS-THROUGH to `ViewFrame.describe_frame_topology(...)`. Filtering, ordering and raise
              behaviour are that method's; this adds no logic of its own.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL: `get_view_frame()` constructs a new
              ViewFrame against a newly resolved descriptor snapshot, so a loop of
              facade calls rebuilds the projection each time and TWO FACADE CALLS NEED
              NOT SEE THE SAME FRAME STATE. Hold one sub-viewer when results must be
              mutually consistent.
            - VISIBILITY-FILTERED: absence means "not visible to this rift" OR "not
              present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and becomes an ASSERTION
              inside the sub-viewer. Passing None resolves the selected frame.

        Args:
            frame_name:
                Optional hosted frame name override.

        Returns:
            Dict[str, object]: Visible frame-local topology summary.
        """
        return self.get_view_frame(frame_name=frame_name).describe_frame_topology(
            frame_name=frame_name,
        )

    def list_visible_target_ids(
            self,
            *,
            frame_name: Optional[str] = None,
            source_kind: Optional[str] = None,
    ) -> List[str]:
        """
        Return visible target ids for the selected frame.

        Purpose:
            Provide a compact id-only view over the currently visible target
            surface.

        Contract:
            - FACADE PASS-THROUGH to `ViewFrame.list_visible_target_ids(...)`. Filtering, ordering and raise
              behaviour are that method's; this adds no logic of its own.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL: `get_view_frame()` constructs a new
              ViewFrame against a newly resolved descriptor snapshot, so a loop of
              facade calls rebuilds the projection each time and TWO FACADE CALLS NEED
              NOT SEE THE SAME FRAME STATE. Hold one sub-viewer when results must be
              mutually consistent.
            - VISIBILITY-FILTERED: absence means "not visible to this rift" OR "not
              present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and becomes an ASSERTION
              inside the sub-viewer. Passing None resolves the selected frame.

        Args:
            frame_name:
                Optional hosted frame name override.
            source_kind:
                Optional target-kind filter.

        Returns:
            List[str]: Visible target ids in deterministic order.
        """
        return self.get_view_frame(frame_name=frame_name).list_visible_target_ids(
            frame_name=frame_name,
            source_kind=source_kind,
        )

    def list_visible_target_ids_by_kind(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, Tuple[str, ...]]:
        """
        Return visible target ids grouped by target kind.

        Args:
            frame_name:
                Optional hosted frame name override.

        Contract:
            - FACADE PASS-THROUGH to `ViewFrame.list_visible_target_ids_by_kind(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_frame()` constructs a new
              ViewFrame per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and then becomes an
              ASSERTION inside the sub-viewer. Same parameter name, two different
              meanings by layer. Passing None resolves the viewer's selected frame.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            Dict[str, Tuple[str, ...]]: Visible target ids grouped by kind.
        """
        return self.get_view_frame(
            frame_name=frame_name,
        ).list_visible_target_ids_by_kind(frame_name=frame_name)

    def list_visible_conduit_ids(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return visible conduit ids for the selected frame.

        Args:
            frame_name:
                Optional hosted frame name override.

        Contract:
            - FACADE PASS-THROUGH to `ViewFrame.list_visible_conduit_ids(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_frame()` constructs a new
              ViewFrame per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and then becomes an
              ASSERTION inside the sub-viewer. Same parameter name, two different
              meanings by layer. Passing None resolves the viewer's selected frame.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            List[str]: Visible conduit ids in deterministic order.
        """
        return self.get_view_frame(frame_name=frame_name).list_visible_conduit_ids(
            frame_name=frame_name,
        )

    def list_visible_spell_source_ids(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return visible spell source ids for the selected frame.

        Args:
            frame_name:
                Optional hosted frame name override.

        Contract:
            - FACADE PASS-THROUGH to `ViewFrame.list_visible_spell_source_ids(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_frame()` constructs a new
              ViewFrame per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and then becomes an
              ASSERTION inside the sub-viewer. Same parameter name, two different
              meanings by layer. Passing None resolves the viewer's selected frame.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            List[str]: Visible spell source ids in deterministic order.
        """
        return self.get_view_frame(
            frame_name=frame_name,
        ).list_visible_spell_source_ids(frame_name=frame_name)

    def list_visible_root_conduits(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[FrameLink]:
        """
        Return visible conduit links that are also root conduits.

        Args:
            frame_name:
                Optional hosted frame name override.

        Contract:
            - FACADE PASS-THROUGH to `ViewFrame.list_visible_root_conduits(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_frame()` constructs a new
              ViewFrame per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and then becomes an
              ASSERTION inside the sub-viewer. Same parameter name, two different
              meanings by layer. Passing None resolves the viewer's selected frame.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            List[FrameLink]: Visible root conduit links.
        """
        return self.get_view_frame(frame_name=frame_name).list_visible_root_conduits(
            frame_name=frame_name,
        )

    def list_visible_binding_names(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return visible spell binding names for the selected frame.

        Args:
            frame_name:
                Optional hosted frame name override.

        Contract:
            - FACADE PASS-THROUGH to `ViewFrame.list_visible_binding_names(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_frame()` constructs a new
              ViewFrame per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and then becomes an
              ASSERTION inside the sub-viewer. Same parameter name, two different
              meanings by layer. Passing None resolves the viewer's selected frame.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            List[str]: Visible binding names in deterministic spell order.
        """
        return self.get_view_frame(frame_name=frame_name).list_visible_binding_names(
            frame_name=frame_name,
        )

    def list_visible_spell_names(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return visible spell names for the selected frame.

        Args:
            frame_name:
                Optional hosted frame name override.

        Contract:
            - FACADE PASS-THROUGH to `ViewFrame.list_visible_spell_names(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_frame()` constructs a new
              ViewFrame per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and then becomes an
              ASSERTION inside the sub-viewer. Same parameter name, two different
              meanings by layer. Passing None resolves the viewer's selected frame.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            List[str]: Visible spell names in deterministic spell order.
        """
        return self.get_view_frame(frame_name=frame_name).list_visible_spell_names(
            frame_name=frame_name,
        )

    def list_visible_spellframes(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return visible normalized spellframe values for the selected frame.

        Args:
            frame_name:
                Optional hosted frame name override.

        Contract:
            - FACADE PASS-THROUGH to `ViewFrame.list_visible_spellframes(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_frame()` constructs a new
              ViewFrame per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and then becomes an
              ASSERTION inside the sub-viewer. Same parameter name, two different
              meanings by layer. Passing None resolves the viewer's selected frame.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            List[str]: Distinct visible spellframe values in deterministic
            order.
        """
        return self.get_view_frame(frame_name=frame_name).list_visible_spellframes(
            frame_name=frame_name,
        )

    def list_visible_index_ids(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return visible spell-index ids for the selected frame.

        Args:
            frame_name:
                Optional hosted frame name override.

        Contract:
            - FACADE PASS-THROUGH to `ViewFrame.list_visible_index_ids(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_frame()` constructs a new
              ViewFrame per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and then becomes an
              ASSERTION inside the sub-viewer. Same parameter name, two different
              meanings by layer. Passing None resolves the viewer's selected frame.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            List[str]: Visible spell-index ids in deterministic spell order.
        """
        return self.get_view_frame(frame_name=frame_name).list_visible_index_ids(
            frame_name=frame_name,
        )

    def describe_visible_spell_ownership(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, Tuple[str, ...]]:
        """
        Return visible spell ownership grouped by conduit id.

        Args:
            frame_name:
                Optional hosted frame name override.

        Contract:
            - FACADE PASS-THROUGH to `ViewFrame.describe_visible_spell_ownership(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_frame()` constructs a new
              ViewFrame per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and then becomes an
              ASSERTION inside the sub-viewer. Same parameter name, two different
              meanings by layer. Passing None resolves the viewer's selected frame.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            Dict[str, Tuple[str, ...]]: Visible spell source ids grouped by
            owner conduit id.
        """
        return self.get_view_frame(frame_name=frame_name).describe_visible_spell_ownership(
            frame_name=frame_name,
        )

    def describe_visible_conduit_tree(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, Tuple[str, ...]]:
        """
        Return visible conduit ids grouped by root conduit id.

        Args:
            frame_name:
                Optional hosted frame name override.

        Contract:
            - FACADE PASS-THROUGH to `ViewFrame.describe_visible_conduit_tree(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_frame()` constructs a new
              ViewFrame per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and then becomes an
              ASSERTION inside the sub-viewer. Same parameter name, two different
              meanings by layer. Passing None resolves the viewer's selected frame.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            Dict[str, Tuple[str, ...]]: Visible conduit ids grouped by root
            conduit id.
        """
        return self.get_view_frame(frame_name=frame_name).describe_visible_conduit_tree(
            frame_name=frame_name,
        )

    def search_targets_contains(
            self,
            text: str,
            *,
            frame_name: Optional[str] = None,
            source_kind: Optional[str] = None,
    ) -> List[FrameLink]:
        """
        Return visible targets whose identity contains one text fragment.

        Purpose:
            Provide a forgiving search path over visible target display names
            and source ids.

        Contract:
            - FACADE PASS-THROUGH to `ViewFrame.search_targets_contains(...)`. Filtering, ordering and raise
              behaviour are that method's; this adds no logic of its own.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL: `get_view_frame()` constructs a new
              ViewFrame against a newly resolved descriptor snapshot, so a loop of
              facade calls rebuilds the projection each time and TWO FACADE CALLS NEED
              NOT SEE THE SAME FRAME STATE. Hold one sub-viewer when results must be
              mutually consistent.
            - VISIBILITY-FILTERED: absence means "not visible to this rift" OR "not
              present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and becomes an ASSERTION
              inside the sub-viewer. Passing None resolves the selected frame.

        Args:
            text:
                Case-insensitive text fragment to search for.
            frame_name:
                Optional hosted frame name override.
            source_kind:
                Optional target-kind filter.

        Returns:
            List[FrameLink]: Matching visible targets in deterministic order.
        """
        return self.get_view_frame(frame_name=frame_name).search_targets_contains(
            text,
            frame_name=frame_name,
            source_kind=source_kind,
        )

    def search_targets_prefix(
            self,
            prefix: str,
            *,
            frame_name: Optional[str] = None,
            source_kind: Optional[str] = None,
    ) -> List[FrameLink]:
        """
        Return visible targets whose identity starts with one prefix.

        Args:
            prefix:
                Case-insensitive prefix to match against display names and
                source ids.
            frame_name:
                Optional hosted frame name override.
            source_kind:
                Optional target-kind filter.

        Contract:
            - FACADE PASS-THROUGH to `ViewFrame.search_targets_prefix(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_frame()` constructs a new
              ViewFrame per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and then becomes an
              ASSERTION inside the sub-viewer. Same parameter name, two different
              meanings by layer. Passing None resolves the viewer's selected frame.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            List[FrameLink]: Matching visible targets in deterministic order.
        """
        matching_targets: List[FrameLink] = [
            link
            for link in self.get_view_frame(
                frame_name=frame_name
            ).search_targets_prefix(
            prefix,
            frame_name=frame_name,
            source_kind=source_kind,
            )
        ]
        return matching_targets

    def group_targets_by_kind(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, List[FrameLink]]:
        """
        Return visible targets grouped by target kind.

        Args:
            frame_name:
                Optional hosted frame name override.

        Contract:
            - FACADE PASS-THROUGH to `ViewFrame.group_targets_by_kind(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_frame()` constructs a new
              ViewFrame per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and then becomes an
              ASSERTION inside the sub-viewer. Same parameter name, two different
              meanings by layer. Passing None resolves the viewer's selected frame.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            Dict[str, List[FrameLink]]: Visible targets grouped by source kind.
        """
        return self.get_view_frame(frame_name=frame_name).group_targets_by_kind(
            frame_name=frame_name,
        )

    def describe_target_brief(
            self,
            *,
            source_kind: str,
            source_id: str,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return one compact summary for a visible target.

        Purpose:
            Give the operator a quick identity/access snapshot for one visible
            target without forcing the richer identity or payload-specific
            methods immediately.

        Contract:
            - FACADE PASS-THROUGH to `ViewFrame.describe_target_brief(...)`. Filtering, ordering and raise
              behaviour are that method's; this adds no logic of its own.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL: `get_view_frame()` constructs a new
              ViewFrame against a newly resolved descriptor snapshot, so a loop of
              facade calls rebuilds the projection each time and TWO FACADE CALLS NEED
              NOT SEE THE SAME FRAME STATE. Hold one sub-viewer when results must be
              mutually consistent.
            - VISIBILITY-FILTERED: absence means "not visible to this rift" OR "not
              present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and becomes an ASSERTION
              inside the sub-viewer. Passing None resolves the selected frame.

        Args:
            source_kind:
                Required target kind.
            source_id:
                Required target source id.
            frame_name:
                Optional hosted frame name override.

        Returns:
            Dict[str, object]: Compact visible target summary.
        """
        return self.get_view_frame(frame_name=frame_name).describe_target_brief(
            frame_name=frame_name,
            source_kind=source_kind,
            source_id=source_id,
        )

    def describe_target_identity(
            self,
            *,
            source_kind: str,
            source_id: str,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return a compact identity summary for one visible target.

        Purpose:
            Give the operator a stable identity/provenance snapshot for one
            currently visible target without forcing a wider payload dump.

        Contract:
            - FACADE PASS-THROUGH to `ViewFrame.describe_target_identity(...)`. Filtering, ordering and raise
              behaviour are that method's; this adds no logic of its own.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL: `get_view_frame()` constructs a new
              ViewFrame against a newly resolved descriptor snapshot, so a loop of
              facade calls rebuilds the projection each time and TWO FACADE CALLS NEED
              NOT SEE THE SAME FRAME STATE. Hold one sub-viewer when results must be
              mutually consistent.
            - VISIBILITY-FILTERED: absence means "not visible to this rift" OR "not
              present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and becomes an ASSERTION
              inside the sub-viewer. Passing None resolves the selected frame.

        Args:
            source_kind:
                Required target kind.
            source_id:
                Required target source id.
            frame_name:
                Optional hosted frame name override.

        Returns:
            Dict[str, object]: Visible target identity summary.
        """
        return self.get_view_frame(frame_name=frame_name).describe_target_identity(
            frame_name=frame_name,
            source_kind=source_kind,
            source_id=source_id,
        )

    def describe_visible_collisions(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return visible identity collisions for the selected frame.

        Purpose:
            Make visible ambiguity explicit at the frame-local surface so the
            operator can see where multiple visible spells share the same
            binding name, spell name, lineage, or spellframe.

        Contract:
            - FACADE PASS-THROUGH to `ViewFrame.describe_visible_collisions(...)`. Filtering, ordering and raise
              behaviour are that method's; this adds no logic of its own.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL: `get_view_frame()` constructs a new
              ViewFrame against a newly resolved descriptor snapshot, so a loop of
              facade calls rebuilds the projection each time and TWO FACADE CALLS NEED
              NOT SEE THE SAME FRAME STATE. Hold one sub-viewer when results must be
              mutually consistent.
            - VISIBILITY-FILTERED: absence means "not visible to this rift" OR "not
              present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and becomes an ASSERTION
              inside the sub-viewer. Passing None resolves the selected frame.

        Args:
            frame_name:
                Optional hosted frame name override.

        Returns:
            Dict[str, object]: Visible collision and grouping summary.
        """
        return self.get_view_frame(frame_name=frame_name).describe_visible_collisions(
            frame_name=frame_name,
        )

    def describe_frame_payload(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return the ACL-filtered frame payload for the selected frame.

        Purpose:
            Surface the real `FrameRecord.payload` content the viewer can use
            after the compiled ACL surface has already reduced it to the
            currently visible frame fields.

        Contract:
            - Uses the selected `FrameDescriptor` and compiled ACL surface
              only.
            - Returns only fields present in
              `CompiledFrameACLAccessSurface.frame_payload_fields`.
            - Raises when the selected frame does not expose `frame_overview`.

        Args:
            frame_name:
                Optional hosted frame name override.

        Returns:
            Dict[str, object]: ACL-filtered frame payload description.
        """
        return self.get_view_frame(frame_name=frame_name).describe_frame_payload(
            frame_name=frame_name,
        )

    def describe_frame_inventory(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return a compact inventory of the selected frame surface.

        Purpose:
            Give the main viewer operator a fast answer to "what is in this
            frame right now?" without forcing a full target dump first.

        Contract:
            - Counts only ACL-visible conduits and spells.
            - Preserves the currently visible target ids and source ids.

        Args:
            frame_name:
                Optional hosted frame name override.

        Returns:
            Dict[str, object]: Compact frame inventory summary.
        """
        return self.get_view_frame(frame_name=frame_name).describe_frame_inventory(
            frame_name=frame_name,
        )

    def describe_frame_access_contract(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return the selected ACL access contract for the frame surface.

        Purpose:
            Surface the effective view/codegen posture and visible frame
            payload fields so the viewer operator can understand why certain
            data is or is not available.

        Contract:
            - FACADE PASS-THROUGH to `ViewFrame.describe_frame_access_contract(...)`. Filtering, ordering and raise
              behaviour are that method's; this adds no logic of its own.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL: `get_view_frame()` constructs a new
              ViewFrame against a newly resolved descriptor snapshot, so a loop of
              facade calls rebuilds the projection each time and TWO FACADE CALLS NEED
              NOT SEE THE SAME FRAME STATE. Hold one sub-viewer when results must be
              mutually consistent.
            - VISIBILITY-FILTERED: absence means "not visible to this rift" OR "not
              present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and becomes an ASSERTION
              inside the sub-viewer. Passing None resolves the selected frame.

        Args:
            frame_name:
                Optional hosted frame name override.

        Returns:
            Dict[str, object]: Effective ACL access contract summary.
        """
        return self.get_view_frame(
            frame_name=frame_name,
        ).describe_frame_access_contract(frame_name=frame_name)

    def get_frame_payload_field(
            self,
            field_name: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return one ACL-visible frame payload field or raise.

        Purpose:
            Provide a fail-fast, field-level access path for agent use when the
            caller needs one specific frame payload field instead of the whole
            filtered payload map.

        Contract:
            - Requires the field to be visible in the compiled ACL surface.
            - Returns the normalized field value from the selected frame
              payload.

        Args:
            field_name:
                Required frame payload field name.
            frame_name:
                Optional hosted frame name override.

        Returns:
            object: ACL-visible frame payload field value.
        """
        return self.get_view_frame(frame_name=frame_name).get_frame_payload_field(
            field_name,
            frame_name=frame_name,
        )

    def find_target_by_display_name(
            self,
            display_name: str,
            *,
            frame_name: Optional[str] = None,
            source_kind: Optional[str] = None,
    ) -> List[FrameLink]:
        """
        Return visible targets whose display name matches exactly.

        Purpose:
            Give the operator a fast exact-name lookup path over the currently
            visible target surface without forcing a manual target scan.

        Contract:
            - FACADE PASS-THROUGH to `ViewFrame.find_target_by_display_name(...)`. Filtering, ordering and raise
              behaviour are that method's; this adds no logic of its own.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL: `get_view_frame()` constructs a new
              ViewFrame against a newly resolved descriptor snapshot, so a loop of
              facade calls rebuilds the projection each time and TWO FACADE CALLS NEED
              NOT SEE THE SAME FRAME STATE. Hold one sub-viewer when results must be
              mutually consistent.
            - VISIBILITY-FILTERED: absence means "not visible to this rift" OR "not
              present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and becomes an ASSERTION
              inside the sub-viewer. Passing None resolves the selected frame.

        Args:
            display_name:
                Exact display name to match.
            frame_name:
                Optional hosted frame name override.
            source_kind:
                Optional target-kind filter.

        Returns:
            List[FrameLink]: Matching visible targets.
        """
        return self.get_view_frame(frame_name=frame_name).find_target_by_display_name(
            display_name,
            frame_name=frame_name,
            source_kind=source_kind,
        )

    def explain_target_access(
            self,
            *,
            source_kind: str,
            source_id: str,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Explain whether one target is visible and what ACL data is exposed.

        Purpose:
            Make the effective access posture explicit for one frame, conduit,
            or spell target instead of forcing the operator to infer it from
            missing results or partial payloads.

        Contract:
            - FACADE PASS-THROUGH to `ViewFrame.explain_target_access(...)`. Filtering, ordering and raise
              behaviour are that method's; this adds no logic of its own.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL: `get_view_frame()` constructs a new
              ViewFrame against a newly resolved descriptor snapshot, so a loop of
              facade calls rebuilds the projection each time and TWO FACADE CALLS NEED
              NOT SEE THE SAME FRAME STATE. Hold one sub-viewer when results must be
              mutually consistent.
            - VISIBILITY-FILTERED: absence means "not visible to this rift" OR "not
              present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and becomes an ASSERTION
              inside the sub-viewer. Passing None resolves the selected frame.

        Args:
            source_kind:
                Target kind to inspect.
            source_id:
                Target source id to inspect.
            frame_name:
                Optional hosted frame name override.

        Returns:
            Dict[str, object]: Visibility and section/field explanation for the
            requested target.
        """
        return self.get_view_frame(frame_name=frame_name).explain_target_access(
            frame_name=frame_name,
            source_kind=source_kind,
            source_id=source_id,
        )

    def list_targets(
            self,
            *,
            frame_name: Optional[str] = None,
            source_kind: Optional[str] = None,
    ) -> List[FrameLink]:
        """
        Return the currently visible targets for the selected frame.

        Contract:
            - Builds links from the selected descriptor plus compiled ACL
              surface.
            - Optionally filters that visible set down to one source kind.
            - Returns a fresh snapshot for this call.

        Args:
            frame_name:
                Optional hosted frame name override.
            source_kind:
                Optional target-kind filter (`frame`, `conduit`, or `spell`).

        Returns:
            List[FrameLink]: Ordered ACL-filtered targets.
        """
        return self.get_view_frame(frame_name=frame_name).list_targets(
            frame_name=frame_name,
            source_kind=source_kind,
        )

    def describe_targets(
            self,
            *,
            frame_name: Optional[str] = None,
            source_kind: Optional[str] = None,
    ) -> List[Dict[str, object]]:
        """
        Return summary descriptions for the current visible target snapshot.

        Contract:
            - Preserves the same target visibility as `list_targets(...)`.
            - Includes link metadata only when the helper is in `detailed`
              posture.

        Args:
            frame_name:
                Optional hosted frame name override.
            source_kind:
                Optional target-kind filter.

        Returns:
            List[Dict[str, object]]: ACL-filtered target descriptions.
        """
        return self.get_view_frame(frame_name=frame_name).describe_targets(
            frame_name=frame_name,
            source_kind=source_kind,
        )

    def list_conduits(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[FrameLink]:
        """
        Return the currently visible conduit links for the selected frame.

        Contract:
            - Delegates visibility decisions to the selected-frame helper and
              its
              compiled ACL surface.
            - Returns a fresh link snapshot for this call.

        Args:
            frame_name:
                Optional hosted frame name override.

        Returns:
            List[FrameLink]: Conduit links for the selected frame.
        """
        return self.get_view_conduit(frame_name=frame_name).list_conduits(
            frame_name=frame_name,
        )

    def list_root_conduits(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[FrameLink]:
        """
        Return visible conduit links that are root conduits.

        Args:
            frame_name:
                Optional hosted frame name override.

        Contract:
            - FACADE PASS-THROUGH to `ViewConduit.list_root_conduits(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_conduit()` constructs a new
              ViewConduit (and a new ViewFrame beneath it) per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and then becomes an
              ASSERTION inside the sub-viewer. Same parameter name, two different
              meanings by layer. Passing None resolves the viewer's selected frame.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            List[FrameLink]: Visible root conduit links.
        """
        return self.get_view_conduit(frame_name=frame_name).list_root_conduits(
            frame_name=frame_name,
        )

    def describe_conduits(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[Dict[str, object]]:
        """
        Return record-aware descriptions for every visible conduit.

        Contract:
            - Materializes one `describe_conduit(...)` result per currently
              visible conduit.
            - Preserves the active ACL filtering on payload sections.

        Args:
            frame_name:
                Optional hosted frame name override.

        Returns:
            List[Dict[str, object]]: Conduit descriptions.
        """
        return self.get_view_conduit(frame_name=frame_name).describe_conduits(
            frame_name=frame_name,
        )

    def get_conduit(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> FrameLink:
        """
        Return one conduit link by conduit id or raise.

        Args:
            conduit_id:
                Published conduit id.
            frame_name:
                Optional hosted frame name override.

        Contract:
            - FACADE PASS-THROUGH to `ViewConduit.get_required_conduit(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_conduit()` constructs a new
              ViewConduit (and a new ViewFrame beneath it) per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and then becomes an
              ASSERTION inside the sub-viewer. Same parameter name, two different
              meanings by layer. Passing None resolves the viewer's selected frame.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            FrameLink: Matching conduit link.
        """
        return self.get_view_conduit(frame_name=frame_name).get_required_conduit(
            conduit_id,
            frame_name=frame_name,
        )

    def describe_conduit(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return a record-aware conduit description for one conduit.

        Purpose:
            Surface one `ConduitRecord` through the currently active ACL
            sections instead of only returning the flattened `FrameLink`
            metadata view.

        Contract:
            - Requires the conduit to be visible in the compiled ACL surface.
            - Returns only the conduit payload sections currently visible for
              that conduit id.

        Args:
            conduit_id:
                Published conduit id.
            frame_name:
                Optional hosted frame name override.

        Returns:
            Dict[str, object]: ACL-filtered conduit description.
        """
        return self.get_view_conduit(frame_name=frame_name).describe_conduit(
            conduit_id,
            frame_name=frame_name,
        )

    def describe_conduit_brief(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return one compact operator-oriented conduit summary.

        Purpose:
            Give the operator a smaller "start here" conduit summary than the
            richer inventory and relationship methods.

        Contract:
            - FACADE PASS-THROUGH to `ViewConduit.describe_conduit_brief(...)`. Filtering, ordering and raise
              behaviour are that method's; this adds no logic of its own.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL: `get_view_conduit()` constructs a new
              ViewConduit (and a new ViewFrame beneath it) against a newly resolved descriptor snapshot, so a loop of
              facade calls rebuilds the projection each time and TWO FACADE CALLS NEED
              NOT SEE THE SAME FRAME STATE. Hold one sub-viewer when results must be
              mutually consistent.
            - VISIBILITY-FILTERED: absence means "not visible to this rift" OR "not
              present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and becomes an ASSERTION
              inside the sub-viewer. Passing None resolves the selected frame.

        Args:
            conduit_id:
                Published conduit id.
            frame_name:
                Optional hosted frame name override.

        Returns:
            Dict[str, object]: Compact conduit summary.
        """
        return self.get_view_conduit(frame_name=frame_name).describe_conduit_brief(
            conduit_id,
            frame_name=frame_name,
        )

    def describe_conduit_inventory(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return a compact inventory summary for one conduit.

        Purpose:
            Give the operator one quick conduit-local inventory view covering
            owned spells, peer links, and visible payload sections.

        Contract:
            - FACADE PASS-THROUGH to `ViewConduit.describe_conduit_inventory(...)`. Filtering, ordering and raise
              behaviour are that method's; this adds no logic of its own.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL: `get_view_conduit()` constructs a new
              ViewConduit (and a new ViewFrame beneath it) against a newly resolved descriptor snapshot, so a loop of
              facade calls rebuilds the projection each time and TWO FACADE CALLS NEED
              NOT SEE THE SAME FRAME STATE. Hold one sub-viewer when results must be
              mutually consistent.
            - VISIBILITY-FILTERED: absence means "not visible to this rift" OR "not
              present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and becomes an ASSERTION
              inside the sub-viewer. Passing None resolves the selected frame.

        Args:
            conduit_id:
                Published conduit id.
            frame_name:
                Optional hosted frame name override.

        Returns:
            Dict[str, object]: Compact conduit inventory summary.
        """
        return self.get_view_conduit(frame_name=frame_name).describe_conduit_inventory(
            conduit_id,
            frame_name=frame_name,
        )

    def describe_conduit_relationships(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return the visible relationship posture for one conduit.

        Purpose:
            Make the conduit root grouping, peer links, and owned visible
            spells explicit in one relationship-oriented view.

        Contract:
            - FACADE PASS-THROUGH to `ViewConduit.describe_conduit_relationships(...)`. Filtering, ordering and raise
              behaviour are that method's; this adds no logic of its own.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL: `get_view_conduit()` constructs a new
              ViewConduit (and a new ViewFrame beneath it) against a newly resolved descriptor snapshot, so a loop of
              facade calls rebuilds the projection each time and TWO FACADE CALLS NEED
              NOT SEE THE SAME FRAME STATE. Hold one sub-viewer when results must be
              mutually consistent.
            - VISIBILITY-FILTERED: absence means "not visible to this rift" OR "not
              present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and becomes an ASSERTION
              inside the sub-viewer. Passing None resolves the selected frame.

        Args:
            conduit_id:
                Published conduit id.
            frame_name:
                Optional hosted frame name override.

        Returns:
            Dict[str, object]: Visible conduit relationship summary.
        """
        return self.get_view_conduit(
            frame_name=frame_name,
        ).describe_conduit_relationships(conduit_id, frame_name=frame_name)

    def describe_conduit_missing_sections(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return the conduit payload sections not currently visible.

        Purpose:
            Make the conduit-local "what is hidden?" answer explicit instead of
            forcing the operator to infer it from missing payload keys.

        Contract:
            - FACADE PASS-THROUGH to `ViewConduit.describe_conduit_missing_sections(...)`. Filtering, ordering and raise
              behaviour are that method's; this adds no logic of its own.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL: `get_view_conduit()` constructs a new
              ViewConduit (and a new ViewFrame beneath it) against a newly resolved descriptor snapshot, so a loop of
              facade calls rebuilds the projection each time and TWO FACADE CALLS NEED
              NOT SEE THE SAME FRAME STATE. Hold one sub-viewer when results must be
              mutually consistent.
            - VISIBILITY-FILTERED: absence means "not visible to this rift" OR "not
              present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and becomes an ASSERTION
              inside the sub-viewer. Passing None resolves the selected frame.

        Args:
            conduit_id:
                Published conduit id.
            frame_name:
                Optional hosted frame name override.

        Returns:
            Dict[str, object]: Missing conduit-section summary.
        """
        return self.get_view_conduit(
            frame_name=frame_name,
        ).describe_conduit_missing_sections(conduit_id, frame_name=frame_name)

    def describe_conduit_crosswalk(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return the related visible objects around one conduit.

        Purpose:
            Give the operator one direct conduit crosswalk from the conduit to
            its root, peers, owned spells, and frame context.

        Contract:
            - FACADE PASS-THROUGH to `ViewConduit.describe_conduit_crosswalk(...)`. Filtering, ordering and raise
              behaviour are that method's; this adds no logic of its own.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL: `get_view_conduit()` constructs a new
              ViewConduit (and a new ViewFrame beneath it) against a newly resolved descriptor snapshot, so a loop of
              facade calls rebuilds the projection each time and TWO FACADE CALLS NEED
              NOT SEE THE SAME FRAME STATE. Hold one sub-viewer when results must be
              mutually consistent.
            - VISIBILITY-FILTERED: absence means "not visible to this rift" OR "not
              present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and becomes an ASSERTION
              inside the sub-viewer. Passing None resolves the selected frame.

        Args:
            conduit_id:
                Published conduit id.
            frame_name:
                Optional hosted frame name override.

        Returns:
            Dict[str, object]: Conduit crosswalk summary.
        """
        return self.get_view_conduit(frame_name=frame_name).describe_conduit_crosswalk(
            conduit_id,
            frame_name=frame_name,
        )

    def list_conduit_spells(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> List[FrameLink]:
        """
        Return the ACL-visible spells owned by one conduit.

        Purpose:
            Give the viewer operator a direct conduit-to-spell traversal path
            instead of forcing a full spell scan and manual filtering.

        Contract:
            - FACADE PASS-THROUGH to `ViewConduit.list_conduit_spells(...)`. Filtering, ordering and raise
              behaviour are that method's; this adds no logic of its own.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL: `get_view_conduit()` constructs a new
              ViewConduit (and a new ViewFrame beneath it) against a newly resolved descriptor snapshot, so a loop of
              facade calls rebuilds the projection each time and TWO FACADE CALLS NEED
              NOT SEE THE SAME FRAME STATE. Hold one sub-viewer when results must be
              mutually consistent.
            - VISIBILITY-FILTERED: absence means "not visible to this rift" OR "not
              present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and becomes an ASSERTION
              inside the sub-viewer. Passing None resolves the selected frame.

        Args:
            conduit_id:
                Published conduit id.
            frame_name:
                Optional hosted frame name override.

        Returns:
            List[FrameLink]: ACL-visible spells owned by the conduit.
        """
        return self.get_view_conduit(frame_name=frame_name).list_conduit_spells(
            conduit_id,
            frame_name=frame_name,
        )

    def describe_conduit_topology(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return the visible topology around one conduit.

        Purpose:
            Show the conduit peer links plus the visible spells currently owned
            by that conduit in one compact description.

        Contract:
            - FACADE PASS-THROUGH to `ViewConduit.describe_conduit_topology(...)`. Filtering, ordering and raise
              behaviour are that method's; this adds no logic of its own.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL: `get_view_conduit()` constructs a new
              ViewConduit (and a new ViewFrame beneath it) against a newly resolved descriptor snapshot, so a loop of
              facade calls rebuilds the projection each time and TWO FACADE CALLS NEED
              NOT SEE THE SAME FRAME STATE. Hold one sub-viewer when results must be
              mutually consistent.
            - VISIBILITY-FILTERED: absence means "not visible to this rift" OR "not
              present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and becomes an ASSERTION
              inside the sub-viewer. Passing None resolves the selected frame.

        Args:
            conduit_id:
                Published conduit id.
            frame_name:
                Optional hosted frame name override.

        Returns:
            Dict[str, object]: Visible conduit topology summary.
        """
        return self.get_view_conduit(frame_name=frame_name).describe_conduit_topology(
            conduit_id,
            frame_name=frame_name,
        )

    def compare_conduits(
            self,
            left_conduit_id: str,
            right_conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Compare two visible conduits inside the selected frame.

        Args:
            left_conduit_id:
                Left visible conduit id.
            right_conduit_id:
                Right visible conduit id.
            frame_name:
                Optional hosted frame name override.

        Contract:
            - FACADE PASS-THROUGH to `ViewConduit.compare_conduits(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_conduit()` constructs a new
              ViewConduit (and a new ViewFrame beneath it) per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and then becomes an
              ASSERTION inside the sub-viewer. Same parameter name, two different
              meanings by layer. Passing None resolves the viewer's selected frame.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            Dict[str, object]: Visible conduit comparison summary.
        """
        return self.get_view_conduit(frame_name=frame_name).compare_conduits(
            left_conduit_id,
            right_conduit_id,
            frame_name=frame_name,
        )

    def is_root_conduit(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> bool:
        """
        Return whether one visible conduit is its own root.

        Args:
            conduit_id:
                Published conduit id.
            frame_name:
                Optional hosted frame name override.

        Contract:
            - FACADE PASS-THROUGH to `ViewConduit.is_root_conduit(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_conduit()` constructs a new
              ViewConduit (and a new ViewFrame beneath it) per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and then becomes an
              ASSERTION inside the sub-viewer. Same parameter name, two different
              meanings by layer. Passing None resolves the viewer's selected frame.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            bool: True when the conduit is a root conduit.
        """
        return self.get_view_conduit(frame_name=frame_name).is_root_conduit(
            conduit_id,
            frame_name=frame_name,
        )

    def get_root_conduit_id(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> str:
        """
        Return the root conduit id for one visible conduit.

        Args:
            conduit_id:
                Published conduit id.
            frame_name:
                Optional hosted frame name override.

        Contract:
            - FACADE PASS-THROUGH to `ViewConduit.get_root_conduit_id(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_conduit()` constructs a new
              ViewConduit (and a new ViewFrame beneath it) per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and then becomes an
              ASSERTION inside the sub-viewer. Same parameter name, two different
              meanings by layer. Passing None resolves the viewer's selected frame.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            str: Root conduit id for the conduit.
        """
        return self.get_view_conduit(frame_name=frame_name).get_root_conduit_id(
            conduit_id,
            frame_name=frame_name,
        )

    def list_conduits_by_root_id(
            self,
            root_conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> List[FrameLink]:
        """
        Return visible conduits grouped under one root conduit id.

        Args:
            root_conduit_id:
                Required root conduit id.
            frame_name:
                Optional hosted frame name override.

        Contract:
            - FACADE PASS-THROUGH to `ViewConduit.list_conduits_by_root_id(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_conduit()` constructs a new
              ViewConduit (and a new ViewFrame beneath it) per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and then becomes an
              ASSERTION inside the sub-viewer. Same parameter name, two different
              meanings by layer. Passing None resolves the viewer's selected frame.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            List[FrameLink]: Visible conduits whose root lineage matches.
        """
        return self.get_view_conduit(frame_name=frame_name).list_conduits_by_root_id(
            root_conduit_id,
            frame_name=frame_name,
        )

    def list_conduits_by_policy(
            self,
            policy_name: str,
            *,
            frame_name: Optional[str] = None,
    ) -> List[FrameLink]:
        """
        Return visible conduits with one conduit policy value.

        Args:
            policy_name:
                Required conduit policy name.
            frame_name:
                Optional hosted frame name override.

        Contract:
            - FACADE PASS-THROUGH to `ViewConduit.list_conduits_by_policy(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_conduit()` constructs a new
              ViewConduit (and a new ViewFrame beneath it) per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and then becomes an
              ASSERTION inside the sub-viewer. Same parameter name, two different
              meanings by layer. Passing None resolves the viewer's selected frame.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            List[FrameLink]: Visible conduits whose payload policy matches.
        """
        return self.get_view_conduit(frame_name=frame_name).list_conduits_by_policy(
            policy_name,
            frame_name=frame_name,
        )

    def list_conduits_by_state(
            self,
            state_name: str,
            *,
            frame_name: Optional[str] = None,
    ) -> List[FrameLink]:
        """
        Return visible conduits with one conduit-state value.

        Args:
            state_name:
                Required conduit-state name.
            frame_name:
                Optional hosted frame name override.

        Contract:
            - FACADE PASS-THROUGH to `ViewConduit.list_conduits_by_state(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_conduit()` constructs a new
              ViewConduit (and a new ViewFrame beneath it) per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and then becomes an
              ASSERTION inside the sub-viewer. Same parameter name, two different
              meanings by layer. Passing None resolves the viewer's selected frame.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            List[FrameLink]: Visible conduits whose payload state matches.
        """
        return self.get_view_conduit(frame_name=frame_name).list_conduits_by_state(
            state_name,
            frame_name=frame_name,
        )

    def list_peer_conduits(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> List[FrameLink]:
        """
        Return visible peer conduit links for one conduit.

        Args:
            conduit_id:
                Published conduit id.
            frame_name:
                Optional hosted frame name override.

        Contract:
            - FACADE PASS-THROUGH to `ViewConduit.list_peer_conduits(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_conduit()` constructs a new
              ViewConduit (and a new ViewFrame beneath it) per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and then becomes an
              ASSERTION inside the sub-viewer. Same parameter name, two different
              meanings by layer. Passing None resolves the viewer's selected frame.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            List[FrameLink]: Visible peer conduit links.
        """
        return self.get_view_conduit(frame_name=frame_name).list_peer_conduits(
            conduit_id,
            frame_name=frame_name,
        )

    def list_peer_conduit_ids(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Tuple[str, ...]:
        """
        Return visible peer conduit ids for one conduit.

        Args:
            conduit_id:
                Published conduit id.
            frame_name:
                Optional hosted frame name override.

        Contract:
            - FACADE PASS-THROUGH to `ViewConduit.list_peer_conduit_ids(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_conduit()` constructs a new
              ViewConduit (and a new ViewFrame beneath it) per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and then becomes an
              ASSERTION inside the sub-viewer. Same parameter name, two different
              meanings by layer. Passing None resolves the viewer's selected frame.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            Tuple[str, ...]: Visible peer conduit ids in deterministic order.
        """
        return self.get_view_conduit(frame_name=frame_name).list_peer_conduit_ids(
            conduit_id,
            frame_name=frame_name,
        )

    def list_spell_source_ids_for_conduit(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Tuple[str, ...]:
        """
        Return visible spell source ids owned by one conduit.

        Args:
            conduit_id:
                Published conduit id.
            frame_name:
                Optional hosted frame name override.

        Contract:
            - FACADE PASS-THROUGH to `ViewConduit.list_spell_source_ids_for_conduit(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_conduit()` constructs a new
              ViewConduit (and a new ViewFrame beneath it) per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and then becomes an
              ASSERTION inside the sub-viewer. Same parameter name, two different
              meanings by layer. Passing None resolves the viewer's selected frame.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            Tuple[str, ...]: Visible spell source ids owned by the conduit.
        """
        return self.get_view_conduit(
            frame_name=frame_name,
        ).list_spell_source_ids_for_conduit(conduit_id, frame_name=frame_name)

    def list_binding_names_for_conduit(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Tuple[str, ...]:
        """
        Return visible spell binding names owned by one conduit.

        Args:
            conduit_id:
                Published conduit id.
            frame_name:
                Optional hosted frame name override.

        Contract:
            - FACADE PASS-THROUGH to `ViewConduit.list_binding_names_for_conduit(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_conduit()` constructs a new
              ViewConduit (and a new ViewFrame beneath it) per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and then becomes an
              ASSERTION inside the sub-viewer. Same parameter name, two different
              meanings by layer. Passing None resolves the viewer's selected frame.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            Tuple[str, ...]: Visible binding names owned by the conduit.
        """
        return self.get_view_conduit(
            frame_name=frame_name,
        ).list_binding_names_for_conduit(conduit_id, frame_name=frame_name)

    def list_spell_names_for_conduit(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Tuple[str, ...]:
        """
        Return visible spell names owned by one conduit.

        Args:
            conduit_id:
                Published conduit id.
            frame_name:
                Optional hosted frame name override.

        Contract:
            - FACADE PASS-THROUGH to `ViewConduit.list_spell_names_for_conduit(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_conduit()` constructs a new
              ViewConduit (and a new ViewFrame beneath it) per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and then becomes an
              ASSERTION inside the sub-viewer. Same parameter name, two different
              meanings by layer. Passing None resolves the viewer's selected frame.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            Tuple[str, ...]: Visible spell names owned by the conduit.
        """
        return self.get_view_conduit(
            frame_name=frame_name,
        ).list_spell_names_for_conduit(conduit_id, frame_name=frame_name)

    def describe_conduit_access_summary(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return one compact access/inventory summary for a conduit.

        Args:
            conduit_id:
                Published conduit id.
            frame_name:
                Optional hosted frame name override.

        Contract:
            - FACADE PASS-THROUGH to `ViewConduit.describe_conduit_access_summary(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_conduit()` constructs a new
              ViewConduit (and a new ViewFrame beneath it) per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and then becomes an
              ASSERTION inside the sub-viewer. Same parameter name, two different
              meanings by layer. Passing None resolves the viewer's selected frame.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            Dict[str, object]: Compact conduit access summary.
        """
        return self.get_view_conduit(
            frame_name=frame_name,
        ).describe_conduit_access_summary(conduit_id, frame_name=frame_name)

    def find_conduit_by_name(
            self,
            conduit_name: str,
            *,
            frame_name: Optional[str] = None,
    ) -> List[FrameLink]:
        """
        Return visible conduits whose display name matches exactly.

        Args:
            conduit_name:
                Exact conduit display name.
            frame_name:
                Optional hosted frame name override.

        Contract:
            - FACADE PASS-THROUGH to `ViewConduit.find_conduit_by_name(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_conduit()` constructs a new
              ViewConduit (and a new ViewFrame beneath it) per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and then becomes an
              ASSERTION inside the sub-viewer. Same parameter name, two different
              meanings by layer. Passing None resolves the viewer's selected frame.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            List[FrameLink]: Matching visible conduit links.
        """
        return self.get_view_conduit(frame_name=frame_name).find_conduit_by_name(
            conduit_name,
            frame_name=frame_name,
        )

    def explain_conduit_access(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Explain the effective ACL access posture for one conduit.

        Args:
            conduit_id:
                Published conduit id.
            frame_name:
                Optional hosted frame name override.

        Contract:
            - FACADE PASS-THROUGH to `ViewConduit.explain_conduit_access(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_conduit()` constructs a new
              ViewConduit (and a new ViewFrame beneath it) per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and then becomes an
              ASSERTION inside the sub-viewer. Same parameter name, two different
              meanings by layer. Passing None resolves the viewer's selected frame.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            Dict[str, object]: Conduit visibility and section explanation.
        """
        return self.get_view_conduit(frame_name=frame_name).explain_conduit_access(
            conduit_id,
            frame_name=frame_name,
        )

    def get_conduit_payload_field(
            self,
            conduit_id: str,
            field_name: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return one ACL-visible conduit payload field or raise.

        Args:
            conduit_id:
                Published conduit id.
            field_name:
                Required conduit payload field name.
            frame_name:
                Optional hosted frame name override.

        Contract:
            - FACADE PASS-THROUGH to `ViewConduit.get_conduit_payload_field(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_conduit()` constructs a new
              ViewConduit (and a new ViewFrame beneath it) per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and then becomes an
              ASSERTION inside the sub-viewer. Same parameter name, two different
              meanings by layer. Passing None resolves the viewer's selected frame.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            object: ACL-visible conduit payload field value.
        """
        return self.get_view_conduit(frame_name=frame_name).get_conduit_payload_field(
            conduit_id,
            field_name,
            frame_name=frame_name,
        )

    def list_spells(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[FrameLink]:
        """
        Return the currently visible spell links for the selected frame.

        Contract:
            - Delegates visibility decisions to the selected-frame helper and
              its
              compiled ACL surface.
            - Returns a fresh link snapshot for this call.

        Args:
            frame_name:
                Optional hosted frame name override.

        Returns:
            List[FrameLink]: Spell links for the selected frame.
        """
        return self.get_view_spell(frame_name=frame_name).list_spells(
            frame_name=frame_name,
        )

    def describe_spells(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[Dict[str, object]]:
        """
        Return record-aware descriptions for every visible spell.

        Contract:
            - Materializes one `describe_spell(...)` result per currently
              visible spell link.
            - Preserves the active ACL filtering and payload-type degradation
              semantics of the spell helper.

        Args:
            frame_name:
                Optional hosted frame name override.

        Returns:
            List[Dict[str, object]]: Spell descriptions.
        """
        return self.get_view_spell(frame_name=frame_name).describe_spells(
            frame_name=frame_name,
        )

    def get_spell(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> FrameLink:
        """
        Return one spell link by published source id or raise.

        Args:
            spell_source_id:
                Published spell source id.
            frame_name:
                Optional hosted frame name override.

        Contract:
            - FACADE PASS-THROUGH to `ViewSpell.get_required_spell(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_spell()` constructs a new
              ViewSpell (and a new ViewFrame beneath it) per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and then becomes an
              ASSERTION inside the sub-viewer. Same parameter name, two different
              meanings by layer. Passing None resolves the viewer's selected frame.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            FrameLink: Matching spell link.
        """
        return self.get_view_spell(frame_name=frame_name).get_required_spell(
            spell_source_id,
            frame_name=frame_name,
        )

    def describe_spell(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return a record-aware spell description for one spell.

        Purpose:
            Surface one `SpellRecord` through the currently active ACL sections
            while gracefully degrading when the published spell payload is only
            `general` and therefore lacks richer `detailed` payload content.

        Contract:
            - Requires the spell to be visible in the compiled ACL surface.
            - Returns only the spell payload sections currently visible for the
              spell record key.
            - Omits richer fields when the payload does not actually publish
              them, even if a more permissive ACL would have allowed them.

        Args:
            spell_source_id:
                Published spell source id in `spellbook_id:spell_id` form.
            frame_name:
                Optional hosted frame name override.

        Returns:
            Dict[str, object]: ACL-filtered spell description.
        """
        return self.get_view_spell(frame_name=frame_name).describe_spell(
            spell_source_id,
            frame_name=frame_name,
        )

    def describe_spell_brief(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return one compact operator-oriented spell summary.

        Purpose:
            Give the operator a smaller spell summary than the richer identity,
            access, and detail methods when they just need the essentials.

        Contract:
            - FACADE PASS-THROUGH to `ViewSpell.describe_spell_brief(...)`. Filtering, ordering and raise
              behaviour are that method's; this adds no logic of its own.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL: `get_view_spell()` constructs a new
              ViewSpell (and a new ViewFrame beneath it) against a newly resolved descriptor snapshot, so a loop of
              facade calls rebuilds the projection each time and TWO FACADE CALLS NEED
              NOT SEE THE SAME FRAME STATE. Hold one sub-viewer when results must be
              mutually consistent.
            - VISIBILITY-FILTERED: absence means "not visible to this rift" OR "not
              present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and becomes an ASSERTION
              inside the sub-viewer. Passing None resolves the selected frame.

        Args:
            spell_source_id:
                Published spell source id.
            frame_name:
                Optional hosted frame name override.

        Returns:
            Dict[str, object]: Compact spell summary.
        """
        return self.get_view_spell(frame_name=frame_name).describe_spell_brief(
            spell_source_id,
            frame_name=frame_name,
        )

    def describe_spell_origin(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return the publication-origin fields for one visible spell.

        Purpose:
            Surface where the spell came from in frame/spellbook/conduit terms
            so the operator can reason about provenance before reading payload
            sections.

        Contract:
            - FACADE PASS-THROUGH to `ViewSpell.describe_spell_origin(...)`. Filtering, ordering and raise
              behaviour are that method's; this adds no logic of its own.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL: `get_view_spell()` constructs a new
              ViewSpell (and a new ViewFrame beneath it) against a newly resolved descriptor snapshot, so a loop of
              facade calls rebuilds the projection each time and TWO FACADE CALLS NEED
              NOT SEE THE SAME FRAME STATE. Hold one sub-viewer when results must be
              mutually consistent.
            - VISIBILITY-FILTERED: absence means "not visible to this rift" OR "not
              present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and becomes an ASSERTION
              inside the sub-viewer. Passing None resolves the selected frame.

        Args:
            spell_source_id:
                Published spell source id.
            frame_name:
                Optional hosted frame name override.

        Returns:
            Dict[str, object]: Publication-origin fields for the visible spell.
        """
        return self.get_view_spell(frame_name=frame_name).describe_spell_origin(
            spell_source_id,
            frame_name=frame_name,
        )

    def describe_spell_index(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return spell-index grouping information for one visible spell.

        Purpose:
            Expose all visible and descriptor-local siblings that share the
            same spell-index id so the operator can understand the spell-index
            context inside the current frame.

        Contract:
            - FACADE PASS-THROUGH to `ViewSpell.describe_spell_index(...)`. Filtering, ordering and raise
              behaviour are that method's; this adds no logic of its own.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL: `get_view_spell()` constructs a new
              ViewSpell (and a new ViewFrame beneath it) against a newly resolved descriptor snapshot, so a loop of
              facade calls rebuilds the projection each time and TWO FACADE CALLS NEED
              NOT SEE THE SAME FRAME STATE. Hold one sub-viewer when results must be
              mutually consistent.
            - VISIBILITY-FILTERED: absence means "not visible to this rift" OR "not
              present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and becomes an ASSERTION
              inside the sub-viewer. Passing None resolves the selected frame.

        Args:
            spell_source_id:
                Published spell source id.
            frame_name:
                Optional hosted frame name override.

        Returns:
            Dict[str, object]: Spell-index grouping summary for the spell.
        """
        return self.get_view_spell(frame_name=frame_name).describe_spell_index(
            spell_source_id,
            frame_name=frame_name,
        )

    def describe_spell_payload(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return only the ACL-filtered spell payload body.

        Purpose:
            Give the main viewer operator a stable, payload-focused spell read
            surface without the wider record wrapper.

        Contract:
            - FACADE PASS-THROUGH to `ViewSpell.describe_spell_payload(...)`. Filtering, ordering and raise
              behaviour are that method's; this adds no logic of its own.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL: `get_view_spell()` constructs a new
              ViewSpell (and a new ViewFrame beneath it) against a newly resolved descriptor snapshot, so a loop of
              facade calls rebuilds the projection each time and TWO FACADE CALLS NEED
              NOT SEE THE SAME FRAME STATE. Hold one sub-viewer when results must be
              mutually consistent.
            - VISIBILITY-FILTERED: absence means "not visible to this rift" OR "not
              present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and becomes an ASSERTION
              inside the sub-viewer. Passing None resolves the selected frame.

        Args:
            spell_source_id:
                Published spell source id.
            frame_name:
                Optional hosted frame name override.

        Returns:
            Dict[str, object]: Spell payload summary.
        """
        return self.get_view_spell(frame_name=frame_name).describe_spell_payload(
            spell_source_id,
            frame_name=frame_name,
        )

    def describe_spell_detail(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return the richer detail posture for one spell when available.

        Args:
            spell_source_id:
                Published spell source id.
            frame_name:
                Optional hosted frame name override.

        Contract:
            - FACADE PASS-THROUGH to `ViewSpell.describe_spell_detail(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_spell()` constructs a new
              ViewSpell (and a new ViewFrame beneath it) per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and then becomes an
              ASSERTION inside the sub-viewer. Same parameter name, two different
              meanings by layer. Passing None resolves the viewer's selected frame.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            Dict[str, object]: Rich detail status and payload.
        """
        return self.get_view_spell(frame_name=frame_name).describe_spell_detail(
            spell_source_id,
            frame_name=frame_name,
        )

    def describe_spell_identity(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return the stable identity fields for one visible spell.

        Args:
            spell_source_id:
                Published spell source id.
            frame_name:
                Optional hosted frame name override.

        Contract:
            - FACADE PASS-THROUGH to `ViewSpell.describe_spell_identity(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_spell()` constructs a new
              ViewSpell (and a new ViewFrame beneath it) per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and then becomes an
              ASSERTION inside the sub-viewer. Same parameter name, two different
              meanings by layer. Passing None resolves the viewer's selected frame.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            Dict[str, object]: Stable identity fields for the visible spell.
        """
        return self.get_view_spell(frame_name=frame_name).describe_spell_identity(
            spell_source_id,
            frame_name=frame_name,
        )

    def describe_spell_binding(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return the binding-facing summary for one visible spell.

        Args:
            spell_source_id:
                Published spell source id.
            frame_name:
                Optional hosted frame name override.

        Contract:
            - FACADE PASS-THROUGH to `ViewSpell.describe_spell_binding(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_spell()` constructs a new
              ViewSpell (and a new ViewFrame beneath it) per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and then becomes an
              ASSERTION inside the sub-viewer. Same parameter name, two different
              meanings by layer. Passing None resolves the viewer's selected frame.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            Dict[str, object]: Binding-facing spell summary.
        """
        return self.get_view_spell(frame_name=frame_name).describe_spell_binding(
            spell_source_id,
            frame_name=frame_name,
        )

    def describe_spell_resolution(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return the resolution-facing summary for one visible spell.

        Args:
            spell_source_id:
                Published spell source id.
            frame_name:
                Optional hosted frame name override.

        Contract:
            - FACADE PASS-THROUGH to `ViewSpell.describe_spell_resolution(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_spell()` constructs a new
              ViewSpell (and a new ViewFrame beneath it) per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and then becomes an
              ASSERTION inside the sub-viewer. Same parameter name, two different
              meanings by layer. Passing None resolves the viewer's selected frame.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            Dict[str, object]: Resolution-facing spell summary.
        """
        return self.get_view_spell(frame_name=frame_name).describe_spell_resolution(
            spell_source_id,
            frame_name=frame_name,
        )

    def describe_spell_metadata(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return the metadata-facing summary for one visible spell.

        Args:
            spell_source_id:
                Published spell source id.
            frame_name:
                Optional hosted frame name override.

        Contract:
            - FACADE PASS-THROUGH to `ViewSpell.describe_spell_metadata(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_spell()` constructs a new
              ViewSpell (and a new ViewFrame beneath it) per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and then becomes an
              ASSERTION inside the sub-viewer. Same parameter name, two different
              meanings by layer. Passing None resolves the viewer's selected frame.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            Dict[str, object]: Metadata-facing spell summary.
        """
        return self.get_view_spell(frame_name=frame_name).describe_spell_metadata(
            spell_source_id,
            frame_name=frame_name,
        )

    def describe_spell_class_profile(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return the class-profile summary for one visible detailed spell.

        Args:
            spell_source_id:
                Published spell source id.
            frame_name:
                Optional hosted frame name override.

        Contract:
            - FACADE PASS-THROUGH to `ViewSpell.describe_spell_class_profile(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_spell()` constructs a new
              ViewSpell (and a new ViewFrame beneath it) per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and then becomes an
              ASSERTION inside the sub-viewer. Same parameter name, two different
              meanings by layer. Passing None resolves the viewer's selected frame.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            Dict[str, object]: Class-profile summary.
        """
        return self.get_view_spell(
            frame_name=frame_name,
        ).describe_spell_class_profile(spell_source_id, frame_name=frame_name)

    def describe_spell_callable_profile(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return the callable-profile summary for one visible detailed spell.

        Args:
            spell_source_id:
                Published spell source id.
            frame_name:
                Optional hosted frame name override.

        Contract:
            - FACADE PASS-THROUGH to `ViewSpell.describe_spell_callable_profile(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_spell()` constructs a new
              ViewSpell (and a new ViewFrame beneath it) per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and then becomes an
              ASSERTION inside the sub-viewer. Same parameter name, two different
              meanings by layer. Passing None resolves the viewer's selected frame.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            Dict[str, object]: Callable-profile summary.
        """
        return self.get_view_spell(
            frame_name=frame_name,
        ).describe_spell_callable_profile(spell_source_id, frame_name=frame_name)

    def describe_spell_instance_members(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return the instance-member summary for one visible detailed spell.

        Args:
            spell_source_id:
                Published spell source id.
            frame_name:
                Optional hosted frame name override.

        Contract:
            - FACADE PASS-THROUGH to `ViewSpell.describe_spell_instance_members(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_spell()` constructs a new
              ViewSpell (and a new ViewFrame beneath it) per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and then becomes an
              ASSERTION inside the sub-viewer. Same parameter name, two different
              meanings by layer. Passing None resolves the viewer's selected frame.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            Dict[str, object]: Instance-member summary.
        """
        return self.get_view_spell(
            frame_name=frame_name,
        ).describe_spell_instance_members(spell_source_id, frame_name=frame_name)

    def describe_spell_dynamic_access(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return the dynamic-access summary for one visible detailed spell.

        Args:
            spell_source_id:
                Published spell source id.
            frame_name:
                Optional hosted frame name override.

        Contract:
            - FACADE PASS-THROUGH to `ViewSpell.describe_spell_dynamic_access(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_spell()` constructs a new
              ViewSpell (and a new ViewFrame beneath it) per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and then becomes an
              ASSERTION inside the sub-viewer. Same parameter name, two different
              meanings by layer. Passing None resolves the viewer's selected frame.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            Dict[str, object]: Dynamic-access availability and normalized data.
        """
        return self.get_view_spell(
            frame_name=frame_name,
        ).describe_spell_dynamic_access(spell_source_id, frame_name=frame_name)

    def list_spell_dunder_member_names(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Tuple[str, ...]:
        """
        Return dunder member names visible in detailed spell data.

        Args:
            spell_source_id:
                Published spell source id.
            frame_name:
                Optional hosted frame name override.

        Contract:
            - FACADE PASS-THROUGH to `ViewSpell.list_spell_dunder_member_names(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_spell()` constructs a new
              ViewSpell (and a new ViewFrame beneath it) per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and then becomes an
              ASSERTION inside the sub-viewer. Same parameter name, two different
              meanings by layer. Passing None resolves the viewer's selected frame.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            Tuple[str, ...]: Visible dunder member names.
        """
        return self.get_view_spell(
            frame_name=frame_name,
        ).list_spell_dunder_member_names(spell_source_id, frame_name=frame_name)

    def describe_spell_dunder_members(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return the visible dunder members surfaced by detailed spell data.

        Args:
            spell_source_id:
                Published spell source id.
            frame_name:
                Optional hosted frame name override.

        Contract:
            - FACADE PASS-THROUGH to `ViewSpell.describe_spell_dunder_members(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_spell()` constructs a new
              ViewSpell (and a new ViewFrame beneath it) per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and then becomes an
              ASSERTION inside the sub-viewer. Same parameter name, two different
              meanings by layer. Passing None resolves the viewer's selected frame.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            Dict[str, object]: Visible dunder member summary.
        """
        return self.get_view_spell(
            frame_name=frame_name,
        ).describe_spell_dunder_members(spell_source_id, frame_name=frame_name)

    def list_spells_by_payload_type(
            self,
            payload_type: str,
            *,
            frame_name: Optional[str] = None,
    ) -> List[FrameLink]:
        """
        Return visible spells whose published payload type matches exactly.

        Args:
            payload_type:
                Required spell payload type.
            frame_name:
                Optional hosted frame name override.

        Contract:
            - FACADE PASS-THROUGH to `ViewSpell.list_spells_by_payload_type(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_spell()` constructs a new
              ViewSpell (and a new ViewFrame beneath it) per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and then becomes an
              ASSERTION inside the sub-viewer. Same parameter name, two different
              meanings by layer. Passing None resolves the viewer's selected frame.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            List[FrameLink]: Matching visible spell links.
        """
        return self.get_view_spell(frame_name=frame_name).list_spells_by_payload_type(
            payload_type,
            frame_name=frame_name,
        )

    def find_spell_by_binding_name(
            self,
            binding_name: str,
            *,
            frame_name: Optional[str] = None,
    ) -> List[FrameLink]:
        """
        Return visible spells whose binding name matches exactly.

        Args:
            binding_name:
                Exact published binding name.
            frame_name:
                Optional hosted frame name override.

        Contract:
            - FACADE PASS-THROUGH to `ViewSpell.find_spell_by_binding_name(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_spell()` constructs a new
              ViewSpell (and a new ViewFrame beneath it) per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and then becomes an
              ASSERTION inside the sub-viewer. Same parameter name, two different
              meanings by layer. Passing None resolves the viewer's selected frame.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            List[FrameLink]: Matching visible spell links.
        """
        return self.get_view_spell(frame_name=frame_name).find_spell_by_binding_name(
            binding_name,
            frame_name=frame_name,
        )

    def list_spells_by_index_id(
            self,
            spell_index_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> List[FrameLink]:
        """
        Return visible spells sharing one spell-index id.

        Args:
            spell_index_id:
                Required spell-index id.
            frame_name:
                Optional hosted frame name override.

        Contract:
            - FACADE PASS-THROUGH to `ViewSpell.list_spells_by_index_id(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_spell()` constructs a new
              ViewSpell (and a new ViewFrame beneath it) per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and then becomes an
              ASSERTION inside the sub-viewer. Same parameter name, two different
              meanings by layer. Passing None resolves the viewer's selected frame.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            List[FrameLink]: Matching visible spell links.
        """
        return self.get_view_spell(frame_name=frame_name).list_spells_by_index_id(
            spell_index_id,
            frame_name=frame_name,
        )

    def list_spells_by_spell_name(
            self,
            spell_name: str,
            *,
            frame_name: Optional[str] = None,
    ) -> List[FrameLink]:
        """
        Return visible spells whose spell name matches exactly.

        Args:
            spell_name:
                Required spell name.
            frame_name:
                Optional hosted frame name override.

        Contract:
            - FACADE PASS-THROUGH to `ViewSpell.list_spells_by_spell_name(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_spell()` constructs a new
              ViewSpell (and a new ViewFrame beneath it) per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and then becomes an
              ASSERTION inside the sub-viewer. Same parameter name, two different
              meanings by layer. Passing None resolves the viewer's selected frame.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            List[FrameLink]: Matching visible spell links.
        """
        return self.get_view_spell(frame_name=frame_name).list_spells_by_spell_name(
            spell_name,
            frame_name=frame_name,
        )

    def search_spells_contains(
            self,
            text: str,
            *,
            frame_name: Optional[str] = None,
    ) -> List[FrameLink]:
        """
        Return visible spells whose identity contains one text fragment.

        Args:
            text:
                Case-insensitive text fragment to match.
            frame_name:
                Optional hosted frame name override.

        Contract:
            - FACADE PASS-THROUGH to `ViewSpell.search_spells_contains(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_spell()` constructs a new
              ViewSpell (and a new ViewFrame beneath it) per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and then becomes an
              ASSERTION inside the sub-viewer. Same parameter name, two different
              meanings by layer. Passing None resolves the viewer's selected frame.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            List[FrameLink]: Matching visible spell links.
        """
        return self.get_view_spell(frame_name=frame_name).search_spells_contains(
            text,
            frame_name=frame_name,
        )

    def search_spells_prefix(
            self,
            prefix: str,
            *,
            frame_name: Optional[str] = None,
    ) -> List[FrameLink]:
        """
        Return visible spells whose identity starts with one prefix.

        Args:
            prefix:
                Case-insensitive prefix to match.
            frame_name:
                Optional hosted frame name override.

        Contract:
            - FACADE PASS-THROUGH to `ViewSpell.search_spells_prefix(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_spell()` constructs a new
              ViewSpell (and a new ViewFrame beneath it) per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and then becomes an
              ASSERTION inside the sub-viewer. Same parameter name, two different
              meanings by layer. Passing None resolves the viewer's selected frame.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            List[FrameLink]: Matching visible spell links.
        """
        matching_spells: List[FrameLink] = [
            link
            for link in self.get_view_spell(
                frame_name=frame_name
            ).search_spells_prefix(
            prefix,
            frame_name=frame_name,
            )
        ]
        return matching_spells

    def explain_spell_access(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Explain the effective ACL access posture for one spell.

        Args:
            spell_source_id:
                Published spell source id.
            frame_name:
                Optional hosted frame name override.

        Contract:
            - FACADE PASS-THROUGH to `ViewSpell.explain_spell_access(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_spell()` constructs a new
              ViewSpell (and a new ViewFrame beneath it) per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and then becomes an
              ASSERTION inside the sub-viewer. Same parameter name, two different
              meanings by layer. Passing None resolves the viewer's selected frame.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            Dict[str, object]: Spell visibility, section, and detail posture
            explanation.
        """
        return self.get_view_spell(frame_name=frame_name).explain_spell_access(
            spell_source_id,
            frame_name=frame_name,
        )

    def describe_spell_access_summary(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return one compact access/identity/detail summary for a spell.

        Args:
            spell_source_id:
                Published spell source id.
            frame_name:
                Optional hosted frame name override.

        Contract:
            - FACADE PASS-THROUGH to `ViewSpell.describe_spell_access_summary(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_spell()` constructs a new
              ViewSpell (and a new ViewFrame beneath it) per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and then becomes an
              ASSERTION inside the sub-viewer. Same parameter name, two different
              meanings by layer. Passing None resolves the viewer's selected frame.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            Dict[str, object]: Compact spell access summary.
        """
        return self.get_view_spell(
            frame_name=frame_name,
        ).describe_spell_access_summary(spell_source_id, frame_name=frame_name)

    def get_spell_payload_section(
            self,
            spell_source_id: str,
            section_name: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return one ACL-visible spell payload section or raise.

        Args:
            spell_source_id:
                Published spell source id.
            section_name:
                Required spell payload section name.
            frame_name:
                Optional hosted frame name override.

        Contract:
            - FACADE PASS-THROUGH to `ViewSpell.get_spell_payload_section(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_spell()` constructs a new
              ViewSpell (and a new ViewFrame beneath it) per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and then becomes an
              ASSERTION inside the sub-viewer. Same parameter name, two different
              meanings by layer. Passing None resolves the viewer's selected frame.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            object: ACL-visible spell payload section value.
        """
        return self.get_view_spell(frame_name=frame_name).get_spell_payload_section(
            spell_source_id,
            section_name,
            frame_name=frame_name,
        )

    def describe_spell_missing_sections(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return the spell payload sections not currently visible or published.

        Purpose:
            Make the spell-local "what is missing and why?" answer explicit
            instead of forcing the operator to infer it from absent detail
            fields.

        Contract:
            - FACADE PASS-THROUGH to `ViewSpell.describe_spell_missing_sections(...)`. Filtering, ordering and raise
              behaviour are that method's; this adds no logic of its own.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL: `get_view_spell()` constructs a new
              ViewSpell (and a new ViewFrame beneath it) against a newly resolved descriptor snapshot, so a loop of
              facade calls rebuilds the projection each time and TWO FACADE CALLS NEED
              NOT SEE THE SAME FRAME STATE. Hold one sub-viewer when results must be
              mutually consistent.
            - VISIBILITY-FILTERED: absence means "not visible to this rift" OR "not
              present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and becomes an ASSERTION
              inside the sub-viewer. Passing None resolves the selected frame.

        Args:
            spell_source_id:
                Published spell source id.
            frame_name:
                Optional hosted frame name override.

        Returns:
            Dict[str, object]: Missing spell-section summary.
        """
        return self.get_view_spell(
            frame_name=frame_name,
        ).describe_spell_missing_sections(spell_source_id, frame_name=frame_name)

    def describe_spell_crosswalk(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return the related visible objects around one spell.

        Purpose:
            Give the operator one direct spell crosswalk from the spell to its
            conduit, root conduit, peer conduits, spellbook, lineage, and
            visible sibling spells.

        Contract:
            - FACADE PASS-THROUGH to `ViewSpell.describe_spell_crosswalk(...)`. Filtering, ordering and raise
              behaviour are that method's; this adds no logic of its own.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL: `get_view_spell()` constructs a new
              ViewSpell (and a new ViewFrame beneath it) against a newly resolved descriptor snapshot, so a loop of
              facade calls rebuilds the projection each time and TWO FACADE CALLS NEED
              NOT SEE THE SAME FRAME STATE. Hold one sub-viewer when results must be
              mutually consistent.
            - VISIBILITY-FILTERED: absence means "not visible to this rift" OR "not
              present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and becomes an ASSERTION
              inside the sub-viewer. Passing None resolves the selected frame.

        Args:
            spell_source_id:
                Published spell source id.
            frame_name:
                Optional hosted frame name override.

        Returns:
            Dict[str, object]: Spell crosswalk summary.
        """
        return self.get_view_spell(frame_name=frame_name).describe_spell_crosswalk(
            spell_source_id,
            frame_name=frame_name,
        )

    def compare_spells(
            self,
            left_spell_source_id: str,
            right_spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Compare two visible spells inside the selected frame.

        Args:
            left_spell_source_id:
                Left visible spell source id.
            right_spell_source_id:
                Right visible spell source id.
            frame_name:
                Optional hosted frame name override.

        Contract:
            - FACADE PASS-THROUGH to `ViewSpell.compare_spells(...)`. The filtering, ordering
              and raise behaviour are that method's; this adds no logic of its own,
              so read its contract for the details that matter.
            - BUILDS A FRESH SUB-VIEWER ON EVERY CALL. `get_view_spell()` constructs a new
              ViewSpell (and a new ViewFrame beneath it) per invocation against a freshly resolved
              descriptor snapshot. A loop of facade calls therefore rebuilds the
              projection each time; hold the sub-viewer yourself when making several
              calls against one frame.
            - Because each call re-resolves the descriptor, two facade calls are NOT
              guaranteed to see the same frame state. Use one held sub-viewer when
              results must be mutually consistent.
            - VISIBILITY-FILTERED PROJECTION. Absence means "not visible to this
              rift" OR "not present" - never proof of non-existence.
            - `frame_name` SELECTS the frame at THIS layer and then becomes an
              ASSERTION inside the sub-viewer. Same parameter name, two different
              meanings by layer. Passing None resolves the viewer's selected frame.

        Threading:
            Each call takes its own descriptor snapshot; concurrent frame changes
            are not reflected in an already-returned result.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The sub-viewer it builds is transient and
            owned by the call, not retained by this viewer.

        Returns:
            Dict[str, object]: Visible spell comparison summary.
        """
        return self.get_view_spell(frame_name=frame_name).compare_spells(
            left_spell_source_id,
            right_spell_source_id,
            frame_name=frame_name,
        )

    def _get_required_frame_descriptor(self, frame_name: str) -> FrameDescriptor:
        """
        Return the current frame descriptor for one hosted frame.

        Args:
            frame_name:
                Hosted frame name whose descriptor should be returned.

        Returns:
            FrameDescriptor: Current descriptor published for the frame.
        """
        return self._get_required_view_projection(frame_name).frame_descriptor

    def _get_required_compiled_access_surface(
            self,
            frame_name: str,
    ) -> CompiledFrameACLAccessSurface:
        """
        Return the current compiled ACL surface for one hosted frame.

        Args:
            frame_name:
                Hosted frame name whose compiled ACL surface should be
                returned.

        Returns:
            CompiledFrameACLAccessSurface: Current compiled ACL surface for the
            frame.

        Raises:
            ValueError:
                If the frame does not currently expose a view projection or
                compiled ACL surface.
        """
        try:
            return self._get_required_view_projection(frame_name).compiled_access_surface
        except ValueError as exc:
            raise ValueError(
                "Compiled access surface for frame '{0}' was not found.".format(
                    frame_name
                )
            ) from exc

    def _get_required_frame_acl_configuration(
            self,
            frame_name: str,
    ) -> FrameACLConfiguration:
        """
        Return the current frame ACL configuration for one hosted frame.

        Args:
            frame_name:
                Hosted frame name whose frame ACL configuration should be
                returned.

        Returns:
            FrameACLConfiguration: Current frame ACL configuration for the
            frame.

        Raises:
            ValueError:
                If the frame does not currently expose a view projection or
                frame ACL configuration.
        """
        try:
            return self._get_required_view_projection(frame_name).frame_acl_configuration
        except ValueError as exc:
            raise ValueError(
                "Frame ACL configuration for frame '{0}' was not found.".format(
                    frame_name
                )
            ) from exc

    def _get_required_view_projection(self, frame_name: str) -> ViewProjection:
        """
        Return one required view projection by frame name.

        Returns:
            ViewProjection: View projection for the frame.
        """
        return self._rift._get_required_view_projection(frame_name)

    @contextmanager
    def _entered_view_action(self, *, action_name: str) -> Any:
        """
        Enter one viewer action hook scope through the owning room.

        Args:
            action_name:
                Stable viewer action name.

        Returns:
            Any: Viewer hook scope context manager.
        """
        self.check_cleaned()
        if self._action_hook_scope_factory is None:
            action_scope = noop_action_scope()
        else:
            action_scope = self._action_hook_scope_factory(
                category="viewer",
                action_name=action_name,
            )
        with action_scope:
            yield

