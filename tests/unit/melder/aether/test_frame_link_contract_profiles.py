import pytest

from melder.aether.nexus.rift.frame_link.frame_link_contract import (
    FrameLinkContract,
)


def test_frame_link_contract_requires_non_empty_rift_id() -> None:
    """
    Verify frame-link contracts reject empty Rift ids.

    Returns:
        None.
    """
    with pytest.raises(ValueError, match="rift_id cannot be empty"):
        FrameLinkContract(rift_id="")


def test_frame_link_contract_rejects_invalid_assigned_frame_names() -> None:
    """
    Verify frame-link contracts reject invalid assigned frame-name entries.

    Returns:
        None.
    """
    with pytest.raises(
            ValueError,
            match="assigned_frame_names must contain non-empty strings",
    ):
        FrameLinkContract(rift_id="rift-1", assigned_frame_names=("ops", ""))


def test_frame_link_contract_rejects_default_frame_outside_assignment() -> None:
    """
    Verify the default frame must be present in the assignment set.

    Returns:
        None.
    """
    with pytest.raises(
            ValueError,
            match="default_frame_name must be present in assigned_frame_names",
    ):
        FrameLinkContract(
            rift_id="rift-1",
            assigned_frame_names=("ops",),
            default_frame_name="finance",
        )


def test_frame_link_contract_deduplicates_assigned_frame_names_preserving_order() -> None:
    """
    Verify duplicate assigned frame names are normalized once in order.

    Returns:
        None.
    """
    contract = FrameLinkContract(
        rift_id="rift-1",
        assigned_frame_names=("ops", "ops", "finance", "ops"),
        default_frame_name="ops",
    )

    assert contract.assigned_frame_names == ("ops", "finance")
    assert contract.default_frame_name == "ops"


def test_frame_link_contract_list_and_has_frame_reflect_current_assignment() -> None:
    """
    Verify frame-list and membership helpers reflect the current assignment set.

    Returns:
        None.
    """
    contract = FrameLinkContract(
        rift_id="rift-1",
        assigned_frame_names=("ops", "finance"),
        default_frame_name="ops",
    )

    assert contract.list_frame_names() == ["ops", "finance"]
    assert contract.has_frame("ops") is True
    assert contract.has_frame("audit") is False


def test_frame_link_contract_register_frame_can_seed_and_replace_default() -> None:
    """
    Verify registering frames can seed and replace the default frame.

    Returns:
        None.
    """
    contract = FrameLinkContract(rift_id="rift-1")

    contract.register_frame("ops")
    contract.register_frame("finance", set_as_default=True)

    assert contract.assigned_frame_names == ("ops", "finance")
    assert contract.default_frame_name == "finance"


def test_frame_link_contract_remove_frame_updates_default_and_ignores_missing() -> None:
    """
    Verify removing frames updates the default and ignores missing names.

    Returns:
        None.
    """
    contract = FrameLinkContract(
        rift_id="rift-1",
        assigned_frame_names=("ops", "finance"),
        default_frame_name="ops",
    )

    contract.remove_frame("ops")
    contract.remove_frame("missing")

    assert contract.assigned_frame_names == ("finance",)
    assert contract.default_frame_name == "finance"


def test_frame_link_contract_helper_methods_reject_empty_frame_name_inputs() -> None:
    """
    Verify frame helper methods reject empty frame-name inputs.

    Returns:
        None.
    """
    contract = FrameLinkContract(rift_id="rift-1")

    with pytest.raises(ValueError, match="frame_name cannot be empty"):
        contract.has_frame("")

    with pytest.raises(ValueError, match="frame_name cannot be empty"):
        contract.register_frame("")

    with pytest.raises(ValueError, match="frame_name cannot be empty"):
        contract.remove_frame("")


def test_frame_link_contract_clone_detaches_metadata_and_assignment_state() -> None:
    """
    Verify cloned contracts detach the metadata and assignment state.

    Returns:
        None.
    """
    contract = FrameLinkContract(
        rift_id="rift-1",
        assigned_frame_names=("ops",),
        default_frame_name="ops",
        metadata={"source": "rift"},
    )

    cloned = contract.clone()
    cloned.register_frame("finance")

    assert cloned is not contract
    assert contract.assigned_frame_names == ("ops",)
    assert cloned.assigned_frame_names == ("ops", "finance")
    assert contract.metadata == {"source": "rift"}


def test_frame_link_contract_describe_summarizes_availability() -> None:
    """
    Verify the contract summary exposes the assigned-frame availability.

    Returns:
        None.
    """
    contract = FrameLinkContract(
        rift_id="rift-1",
        assigned_frame_names=("ops", "finance"),
        default_frame_name="ops",
    )

    assert contract.describe() == {
        "rift_id": "rift-1",
        "assigned_frame_names": ("ops", "finance"),
        "default_frame_name": "ops",
        "assigned_frame_count": 2,
    }


def test_frame_link_contract_cleanup_clears_owned_state() -> None:
    """
    Verify frame-link contract cleanup clears owned state.

    Returns:
        None.
    """
    contract = FrameLinkContract(
        rift_id="rift-1",
        assigned_frame_names=("ops",),
        default_frame_name="ops",
    )

    contract.cleanup()

    assert contract.cleaned is True
    assert contract._assigned_frame_names is None
    assert contract._default_frame_name is None
    assert contract._metadata is None
