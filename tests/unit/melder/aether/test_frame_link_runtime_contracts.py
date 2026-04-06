from melder.aether.nexus.rift.frame_link.frame_link import FrameLink
from melder.aether.nexus.rift.frame_link.frame_link_contract import (
    FrameLinkContract,
)


class _ExplodingFrameLinkContract(FrameLinkContract):
    """
    Test helper contract that raises during cleanup.
    """

    def cleanup(self) -> None:
        raise RuntimeError("boom")


def test_frame_link_defaults_display_name_to_source_id() -> None:
    """
    Verify frame links default the display name to the source id.

    Returns:
        None.
    """
    link = FrameLink(
        frame_name="ops",
        source_kind="spell",
        source_id="spell-1",
    )

    assert link.display_name == "spell-1"


def test_frame_link_preserves_explicit_display_name_and_metadata_copy() -> None:
    """
    Verify frame links preserve explicit display names and detach metadata input.

    Returns:
        None.
    """
    metadata = {"source": "compiled"}
    link = FrameLink(
        frame_name="ops",
        source_kind="conduit",
        source_id="conduit-1",
        display_name="default",
        metadata=metadata,
    )
    metadata["mutated"] = True

    assert link.display_name == "default"
    assert link.metadata == {"source": "compiled"}


def test_frame_link_cleanup_cascades_to_contract() -> None:
    """
    Verify frame-link cleanup cascades into the owned contract.

    Returns:
        None.
    """
    contract = FrameLinkContract(
        frame_name="ops",
        allowed_kinds=("frame",),
    )
    link = FrameLink(
        frame_name="ops",
        source_kind="frame",
        source_id="ops",
        contract=contract,
    )

    link.cleanup()

    assert contract.cleaned is True
    assert link.cleaned is True
    assert link._contract is None
    assert link._metadata is None


def test_frame_link_cleanup_swallows_contract_cleanup_failures() -> None:
    """
    Verify frame-link cleanup still clears link state if contract cleanup fails.

    Returns:
        None.
    """
    link = FrameLink(
        frame_name="ops",
        source_kind="frame",
        source_id="ops",
        contract=_ExplodingFrameLinkContract(frame_name="ops"),
    )

    link.cleanup()

    assert link.cleaned is True
    assert link._frame_name is None
    assert link._source_kind is None
    assert link._source_id is None
    assert link._display_name is None
