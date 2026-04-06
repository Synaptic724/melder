import pytest

from melder.aether.nexus.rift.frame_link.frame_link import FrameLink
from melder.aether.nexus.rift.frame_link.frame_link_contract import (
    FrameLinkContract,
)
from melder.aether.nexus.rift.frame_viewer.frame_view import FrameView
from melder.aether.nexus.rift.frame_viewer.frame_viewer import FrameViewer


def _build_link(
        *,
        frame_name: str,
        source_kind: str,
        source_id: str,
        display_name: str,
) -> FrameLink:
    """
    Build one simple frame link for viewer tests.

    Args:
        frame_name:
            Owning frame name.
        source_kind:
            Source kind label.
        source_id:
            Stable source identifier.
        display_name:
            Viewer-facing display name.

    Returns:
        FrameLink:
            Constructed frame link.
    """
    return FrameLink(
        frame_name=frame_name,
        source_kind=source_kind,
        source_id=source_id,
        display_name=display_name,
        contract=FrameLinkContract(
            frame_name=frame_name,
            allowed_kinds=(source_kind,),
        ),
    )


def _build_view(
        *,
        frame_name: str,
        links: list[FrameLink],
) -> FrameView:
    """
    Build one frame view from the supplied links.

    Args:
        frame_name:
            Owning frame name.
        links:
            Links to place in the view.

    Returns:
        FrameView:
            Constructed frame view.
    """
    return FrameView(
        frame_name=frame_name,
        links_by_id={link.link_id: link for link in links},
    )


def test_frame_viewer_views_snapshot_is_detached() -> None:
    """
    Verify viewer view snapshots are detached from future mutation.

    Returns:
        None.
    """
    viewer = FrameViewer()
    view = _build_view(
        frame_name="ops",
        links=[_build_link(
            frame_name="ops",
            source_kind="frame",
            source_id="frame-1",
            display_name="ops",
        )],
    )
    viewer.add_view(view)

    snapshot = viewer.views_by_frame_name
    snapshot.clear()

    assert viewer.list_frame_names() == ["ops"]


def test_frame_viewer_available_views_snapshot_is_detached() -> None:
    """
    Verify available-view snapshots are detached from future mutation.

    Returns:
        None.
    """
    viewer = FrameViewer()
    view = _build_view(
        frame_name="ops",
        links=[_build_link(
            frame_name="ops",
            source_kind="frame",
            source_id="frame-1",
            display_name="ops",
        )],
    )
    viewer.add_available_view(view)

    snapshot = viewer.available_views_by_frame_name
    snapshot.clear()

    assert viewer.list_frame_names() == ["ops"]


def test_frame_viewer_metadata_snapshot_is_detached() -> None:
    """
    Verify viewer metadata snapshots are detached from future mutation.

    Returns:
        None.
    """
    viewer = FrameViewer(metadata={"source": "viewer"})

    snapshot = viewer.metadata
    snapshot["mutated"] = True

    assert viewer.metadata == {"source": "viewer"}


def test_frame_viewer_lists_enabled_helpers_from_selected_profile() -> None:
    """
    Verify the viewer exposes the enabled helper set selected by profile.

    Returns:
        None.
    """
    viewer = FrameViewer(
        profile_name="general",
        profile_version="0.0.1",
        enabled_helpers=["list_frame_names", "list_links"],
    )

    assert viewer.profile_name == "general"
    assert viewer.profile_version == "0.0.1"
    assert viewer.list_enabled_helpers() == ("list_frame_names", "list_links")
    assert viewer.list_available_tools() == ("list_frame_names", "list_links")
    assert viewer.has_enabled_helper("list_links") is True
    assert viewer.has_enabled_helper("describe_frames") is False


def test_frame_viewer_seeds_default_active_profile_and_can_register_more() -> None:
    """
    Verify the viewer seeds a default active profile and can register another one.

    Returns:
        None.
    """
    from melder.aether.nexus.rift.frame_viewer.profiles.frame_viewer_profile import (
        FrameViewerProfile,
    )

    viewer = FrameViewer()
    custom_profile = FrameViewerProfile(
        "inspection",
        tool_handler_names_by_name={"inventory": "list_links"},
    )

    viewer.register_active_profile(custom_profile)

    assert viewer.list_active_profile_names() == ["general", "inspection"]
    assert viewer.get_required_active_profile("inspection") is custom_profile


def test_frame_viewer_helper_queries_reject_empty_helper_names() -> None:
    """
    Verify enabled-helper queries reject empty helper ids.

    Returns:
        None.
    """
    viewer = FrameViewer()

    with pytest.raises(ValueError, match="helper_name cannot be empty"):
        viewer.has_enabled_helper("")

    with pytest.raises(ValueError, match="tool_name cannot be empty"):
        viewer.execute_tool("")


def test_frame_viewer_add_view_rejects_invalid_type() -> None:
    """
    Verify viewer registration rejects invalid view objects.

    Returns:
        None.
    """
    with pytest.raises(TypeError, match="frame_view must be a FrameView"):
        FrameViewer().add_view(None)


def test_frame_viewer_list_links_returns_deterministic_order_across_frames() -> None:
    """
    Verify link listing is deterministic across attached views.

    Returns:
        None.
    """
    finance_links = [
        _build_link(
            frame_name="finance",
            source_kind="spell",
            source_id="spell-2",
            display_name="beta",
        ),
        _build_link(
            frame_name="finance",
            source_kind="frame",
            source_id="frame-2",
            display_name="finance",
        ),
    ]
    ops_links = [
        _build_link(
            frame_name="ops",
            source_kind="conduit",
            source_id="conduit-1",
            display_name="root",
        ),
        _build_link(
            frame_name="ops",
            source_kind="frame",
            source_id="frame-1",
            display_name="ops",
        ),
    ]
    viewer = FrameViewer(
        views_by_frame_name={
            "ops": _build_view(frame_name="ops", links=ops_links),
            "finance": _build_view(frame_name="finance", links=finance_links),
        }
    )

    listed_links = viewer.list_links()

    assert [link.frame_name for link in listed_links] == [
        "finance",
        "finance",
        "ops",
        "ops",
    ]


def test_frame_viewer_disabled_helper_raises_when_called() -> None:
    """
    Verify disabled helpers fail fast under the selected profile surface.

    Returns:
        None.
    """
    viewer = FrameViewer(
        profile_name="minimal",
        enabled_helpers=["list_frame_names"],
        views_by_frame_name={
            "ops": _build_view(
                frame_name="ops",
                links=[
                    _build_link(
                        frame_name="ops",
                        source_kind="frame",
                        source_id="frame-1",
                        display_name="ops",
                    )
                ],
            )
        },
    )

    with pytest.raises(ValueError, match="FrameViewer helper 'list_links' is not enabled"):
        viewer.list_links()


def test_frame_viewer_execute_tool_routes_through_profile_owned_tool_mapping() -> None:
    """
    Verify the viewer hosts profile-owned tools and routes execution through them.

    Returns:
        None.
    """
    viewer = FrameViewer(
        profile_name="inspection",
        enabled_helpers=["list_links"],
        views_by_frame_name={
            "ops": _build_view(
                frame_name="ops",
                links=[
                    _build_link(
                        frame_name="ops",
                        source_kind="frame",
                        source_id="frame-1",
                        display_name="ops",
                    )
                ],
            )
        },
    )

    assert [link.source_id for link in viewer.execute_tool("list_links")] == ["frame-1"]


def test_frame_viewer_execute_tool_uses_explicit_profile_handler_alias() -> None:
    """
    Verify explicit profile-owned tool aliases resolve to host-side handlers.

    Returns:
        None.
    """
    from melder.aether.nexus.rift.frame_viewer.profiles.frame_viewer_profile import (
        FrameViewerProfile,
    )

    viewer = FrameViewer(
        profile=FrameViewerProfile(
            "inspection",
            tool_handler_names_by_name={"inventory": "list_links"},
        ),
        views_by_frame_name={
            "ops": _build_view(
                frame_name="ops",
                links=[
                    _build_link(
                        frame_name="ops",
                        source_kind="frame",
                        source_id="frame-1",
                        display_name="ops",
                    )
                ],
            )
        },
    )

    assert [link.source_id for link in viewer.execute_tool("inventory")] == ["frame-1"]


def test_frame_viewer_execute_tool_rejects_missing_profile_and_handler() -> None:
    """
    Verify tool execution fails fast when no hosted profile or no handler exists.

    Returns:
        None.
    """
    from melder.aether.nexus.rift.frame_viewer.profiles.frame_viewer_profile import (
        FrameViewerProfile,
    )

    with pytest.raises(ValueError, match="FrameViewer has no hosted profile"):
        FrameViewer(active_profiles_by_name={}).execute_tool("inventory")

    viewer = FrameViewer(
        profile=FrameViewerProfile(
            "broken",
            tool_handler_names_by_name={"inventory": "missing_handler"},
        )
    )

    with pytest.raises(ValueError, match="targets missing handler"):
        viewer.execute_tool("inventory")


def test_frame_viewer_execute_tool_can_target_non_default_active_profile() -> None:
    """
    Verify tool execution can target a non-default active profile explicitly.

    Returns:
        None.
    """
    from melder.aether.nexus.rift.frame_viewer.profiles.frame_viewer_profile import (
        FrameViewerProfile,
    )

    viewer = FrameViewer(
        active_profiles_by_name={
            "general": FrameViewerProfile.create_general(),
            "inspection": FrameViewerProfile(
                "inspection",
                tool_handler_names_by_name={"inventory": "list_links"},
            ),
        },
        available_views_by_frame_name={
            "ops": _build_view(
                frame_name="ops",
                links=[
                    _build_link(
                        frame_name="ops",
                        source_kind="frame",
                        source_id="frame-1",
                        display_name="ops",
                    )
                ],
            )
        },
    )

    assert [link.source_id for link in viewer.execute_tool(
        "inventory",
        profile_name="inspection",
    )] == ["frame-1"]


def test_frame_viewer_list_links_can_scope_to_single_frame() -> None:
    """
    Verify link listing can be scoped to one frame.

    Returns:
        None.
    """
    ops_view = _build_view(
        frame_name="ops",
        links=[
            _build_link(
                frame_name="ops",
                source_kind="frame",
                source_id="frame-1",
                display_name="ops",
            ),
            _build_link(
                frame_name="ops",
                source_kind="spell",
                source_id="spell-1",
                display_name="spell_one",
            ),
        ],
    )
    viewer = FrameViewer(views_by_frame_name={"ops": ops_view})

    listed_links = viewer.list_links(frame_name="ops")

    assert len(listed_links) == 2
    assert {link.source_kind for link in listed_links} == {"frame", "spell"}


def test_frame_viewer_list_links_grouped_by_frame_is_deterministic() -> None:
    """
    Verify links are grouped deterministically by frame name.

    Returns:
        None.
    """
    viewer = FrameViewer(
        views_by_frame_name={
            "ops": _build_view(
                frame_name="ops",
                links=[
                    _build_link(
                        frame_name="ops",
                        source_kind="frame",
                        source_id="frame-1",
                        display_name="ops",
                    ),
                    _build_link(
                        frame_name="ops",
                        source_kind="spell",
                        source_id="spell-1",
                        display_name="spell_one",
                    ),
                ],
            ),
            "finance": _build_view(
                frame_name="finance",
                links=[
                    _build_link(
                        frame_name="finance",
                        source_kind="frame",
                        source_id="frame-2",
                        display_name="finance",
                    )
                ],
            ),
        }
    )

    grouped = viewer.list_links_grouped_by_frame()

    assert list(grouped.keys()) == ["finance", "ops"]
    assert [link.frame_name for link in grouped["ops"]] == ["ops", "ops"]


def test_frame_viewer_list_links_by_kind_filters_across_views() -> None:
    """
    Verify kind filtering works across every attached view.

    Returns:
        None.
    """
    viewer = FrameViewer(
        views_by_frame_name={
            "ops": _build_view(
                frame_name="ops",
                links=[
                    _build_link(
                        frame_name="ops",
                        source_kind="frame",
                        source_id="frame-1",
                        display_name="ops",
                    ),
                    _build_link(
                        frame_name="ops",
                        source_kind="spell",
                        source_id="spell-1",
                        display_name="spell_one",
                    ),
                ],
            ),
            "finance": _build_view(
                frame_name="finance",
                links=[
                    _build_link(
                        frame_name="finance",
                        source_kind="spell",
                        source_id="spell-2",
                        display_name="spell_two",
                    )
                ],
            ),
        }
    )

    spell_links = viewer.list_links_by_kind("spell")

    assert len(spell_links) == 2
    assert {link.source_id for link in spell_links} == {"spell-1", "spell-2"}


def test_frame_viewer_list_links_grouped_by_kind_is_deterministic() -> None:
    """
    Verify links are grouped deterministically by source kind.

    Returns:
        None.
    """
    viewer = FrameViewer(
        views_by_frame_name={
            "ops": _build_view(
                frame_name="ops",
                links=[
                    _build_link(
                        frame_name="ops",
                        source_kind="spell",
                        source_id="spell-1",
                        display_name="spell_one",
                    ),
                    _build_link(
                        frame_name="ops",
                        source_kind="frame",
                        source_id="frame-1",
                        display_name="ops",
                    ),
                ],
            ),
            "finance": _build_view(
                frame_name="finance",
                links=[
                    _build_link(
                        frame_name="finance",
                        source_kind="conduit",
                        source_id="conduit-1",
                        display_name="root",
                    )
                ],
            ),
        }
    )

    grouped = viewer.list_links_grouped_by_kind()

    assert list(grouped.keys()) == ["conduit", "frame", "spell"]
    assert grouped["conduit"][0].source_id == "conduit-1"
    assert grouped["frame"][0].source_id == "frame-1"
    assert grouped["spell"][0].source_id == "spell-1"


def test_frame_viewer_list_links_by_kind_rejects_empty_kind() -> None:
    """
    Verify kind filtering rejects empty source-kind inputs.

    Returns:
        None.
    """
    with pytest.raises(ValueError, match="source_kind cannot be empty"):
        FrameViewer().list_links_by_kind("")


def test_frame_viewer_get_required_link_by_source_returns_matching_link() -> None:
    """
    Verify direct source lookup returns the matching frame link.

    Returns:
        None.
    """
    link = _build_link(
        frame_name="ops",
        source_kind="spell",
        source_id="spell-1",
        display_name="spell_one",
    )
    viewer = FrameViewer(
        views_by_frame_name={"ops": _build_view(frame_name="ops", links=[link])}
    )

    fetched = viewer.get_required_link_by_source(
        frame_name="ops",
        source_kind="spell",
        source_id="spell-1",
    )

    assert fetched is link


def test_frame_viewer_get_required_link_by_source_rejects_empty_inputs() -> None:
    """
    Verify direct source lookup rejects empty kind and source-id inputs.

    Returns:
        None.
    """
    viewer = FrameViewer()

    with pytest.raises(ValueError, match="source_kind cannot be empty"):
        viewer.get_required_link_by_source(
            frame_name="ops",
            source_kind="",
            source_id="spell-1",
        )

    with pytest.raises(ValueError, match="source_id cannot be empty"):
        viewer.get_required_link_by_source(
            frame_name="ops",
            source_kind="spell",
            source_id="",
        )


def test_frame_viewer_get_required_link_by_source_raises_when_missing() -> None:
    """
    Verify direct source lookup fails fast when no matching link exists.

    Returns:
        None.
    """
    viewer = FrameViewer(
        views_by_frame_name={
            "ops": _build_view(
                frame_name="ops",
                links=[
                    _build_link(
                        frame_name="ops",
                        source_kind="frame",
                        source_id="frame-1",
                        display_name="ops",
                    )
                ],
            )
        }
    )

    with pytest.raises(ValueError, match="FrameLink 'spell:spell-1' was not found"):
        viewer.get_required_link_by_source(
            frame_name="ops",
            source_kind="spell",
            source_id="spell-1",
        )


def test_frame_viewer_list_display_names_can_filter_by_frame_and_kind() -> None:
    """
    Verify display-name listing can be filtered by frame and source kind.

    Returns:
        None.
    """
    viewer = FrameViewer(
        views_by_frame_name={
            "ops": _build_view(
                frame_name="ops",
                links=[
                    _build_link(
                        frame_name="ops",
                        source_kind="frame",
                        source_id="frame-1",
                        display_name="ops",
                    ),
                    _build_link(
                        frame_name="ops",
                        source_kind="spell",
                        source_id="spell-1",
                        display_name="spell_one",
                    ),
                ],
            ),
            "finance": _build_view(
                frame_name="finance",
                links=[
                    _build_link(
                        frame_name="finance",
                        source_kind="spell",
                        source_id="spell-2",
                        display_name="spell_two",
                    )
                ],
            ),
        }
    )

    assert viewer.list_display_names() == ["spell_two", "ops", "spell_one"]
    assert viewer.list_display_names(frame_name="ops") == ["ops", "spell_one"]
    assert viewer.list_display_names(source_kind="spell") == [
        "spell_two",
        "spell_one",
    ]


def test_frame_viewer_count_links_can_filter_by_frame_and_kind() -> None:
    """
    Verify link counts can be filtered by frame and source kind.

    Returns:
        None.
    """
    viewer = FrameViewer(
        views_by_frame_name={
            "ops": _build_view(
                frame_name="ops",
                links=[
                    _build_link(
                        frame_name="ops",
                        source_kind="frame",
                        source_id="frame-1",
                        display_name="ops",
                    ),
                    _build_link(
                        frame_name="ops",
                        source_kind="spell",
                        source_id="spell-1",
                        display_name="spell_one",
                    ),
                ],
            ),
            "finance": _build_view(
                frame_name="finance",
                links=[
                    _build_link(
                        frame_name="finance",
                        source_kind="spell",
                        source_id="spell-2",
                        display_name="spell_two",
                    )
                ],
            ),
        }
    )

    assert viewer.count_links() == 3
    assert viewer.count_links(frame_name="ops") == 2
    assert viewer.count_links(source_kind="spell") == 2
    assert viewer.count_links(frame_name="ops", source_kind="spell") == 1


def test_frame_viewer_describe_frame_summarizes_one_projected_view() -> None:
    """
    Verify frame summaries expose link counts, kinds, and metadata.

    Returns:
        None.
    """
    view = _build_view(
        frame_name="ops",
        links=[
            _build_link(
                frame_name="ops",
                source_kind="frame",
                source_id="frame-1",
                display_name="ops",
            ),
            _build_link(
                frame_name="ops",
                source_kind="spell",
                source_id="spell-1",
                display_name="spell_one",
            ),
        ],
    )
    viewer = FrameViewer(
        views_by_frame_name={"ops": view},
        metadata={"source": "viewer"},
    )

    summary = viewer.describe_frame("ops")

    assert summary["frame_name"] == "ops"
    assert summary["link_count"] == 2
    assert summary["available_kinds"] == ("frame", "spell")
    assert summary["link_counts_by_kind"] == {"frame": 1, "spell": 1}


def test_frame_viewer_describe_frames_summarizes_every_attached_view() -> None:
    """
    Verify multi-frame summaries are keyed deterministically by frame name.

    Returns:
        None.
    """
    viewer = FrameViewer(
        views_by_frame_name={
            "ops": _build_view(
                frame_name="ops",
                links=[
                    _build_link(
                        frame_name="ops",
                        source_kind="frame",
                        source_id="frame-1",
                        display_name="ops",
                    )
                ],
            ),
            "finance": _build_view(
                frame_name="finance",
                links=[
                    _build_link(
                        frame_name="finance",
                        source_kind="spell",
                        source_id="spell-2",
                        display_name="spell_two",
                    )
                ],
            ),
        }
    )

    summaries = viewer.describe_frames()

    assert list(summaries.keys()) == ["finance", "ops"]
    assert summaries["finance"]["available_kinds"] == ("spell",)
    assert summaries["ops"]["available_kinds"] == ("frame",)


def test_frame_viewer_cleanup_cascades_into_owned_views_and_links() -> None:
    """
    Verify viewer cleanup cascades through owned views and links.

    Returns:
        None.
    """
    link = _build_link(
        frame_name="ops",
        source_kind="frame",
        source_id="frame-1",
        display_name="ops",
    )
    view = _build_view(frame_name="ops", links=[link])
    viewer = FrameViewer(views_by_frame_name={"ops": view})

    viewer.cleanup()

    assert viewer.cleaned is True
    assert view.cleaned is True
    assert link.cleaned is True
    assert viewer._views_by_frame_name is None


def test_frame_viewer_clone_returns_detached_views_and_metadata() -> None:
    """
    Verify viewer clones detach the projected views and metadata map.

    Returns:
        None.
    """
    viewer = FrameViewer(
        views_by_frame_name={
            "ops": _build_view(
                frame_name="ops",
                links=[
                    _build_link(
                        frame_name="ops",
                        source_kind="frame",
                        source_id="frame-1",
                        display_name="ops",
                    )
                ],
            )
        },
        metadata={"source": "viewer"},
    )

    cloned = viewer.clone()

    assert cloned is not viewer
    assert cloned.metadata == {"source": "viewer"}
    assert cloned.get_view("ops") is not viewer.get_view("ops")
    assert cloned.list_enabled_helpers() == viewer.list_enabled_helpers()
