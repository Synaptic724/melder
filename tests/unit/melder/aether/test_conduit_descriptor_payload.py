from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.aether.nexus.frame_descriptor.conduit_descriptor_payload import (
    ConduitDescriptorPayload,
)


def test_conduit_descriptor_payload_exposes_stable_fields() -> None:
    """
    Verify the payload stores the expected descriptor-facing conduit metadata.

    Returns:
        None.
    """
    payload = ConduitDescriptorPayload(
        conduit_name="root",
        conduit_state=ConduitState.normal,
        policy=Policies.default,
        peer_conduit_ids=("peer-2", "peer-1"),
        parent_conduit_id=None,
        lineage_depth=0,
    )

    assert payload.payload_version == "0.0.1"
    assert payload.conduit_name == "root"
    assert payload.conduit_state is ConduitState.normal
    assert payload.policy is Policies.default
    assert payload.peer_conduit_ids == ("peer-2", "peer-1")
    assert payload.parent_conduit_id is None
    assert payload.lineage_depth == 0


def test_conduit_descriptor_payload_supports_lesser_lineage_fields() -> None:
    """
    Verify lesser-conduit lineage hints are preserved in the payload.

    Returns:
        None.
    """
    payload = ConduitDescriptorPayload(
        conduit_name="lesser",
        conduit_state=ConduitState.lesser,
        policy=Policies.default,
        peer_conduit_ids=tuple(),
        parent_conduit_id="parent-1",
        lineage_depth=2,
    )

    assert payload.conduit_state is ConduitState.lesser
    assert payload.parent_conduit_id == "parent-1"
    assert payload.lineage_depth == 2


def test_conduit_descriptor_payload_rejects_empty_version_and_negative_depth() -> None:
    """
    Verify invalid payload-version and lineage-depth inputs fail fast.

    Returns:
        None.
    """
    try:
        ConduitDescriptorPayload(
            conduit_name="root",
            conduit_state=ConduitState.normal,
            policy=Policies.default,
            peer_conduit_ids=tuple(),
            payload_version="",
        )
        raise AssertionError("Expected empty payload_version to fail.")
    except ValueError as exc:
        assert "payload_version cannot be empty" in str(exc)

    try:
        ConduitDescriptorPayload(
            conduit_name="root",
            conduit_state=ConduitState.normal,
            policy=Policies.default,
            peer_conduit_ids=tuple(),
            lineage_depth=-1,
        )
        raise AssertionError("Expected negative lineage_depth to fail.")
    except ValueError as exc:
        assert "lineage_depth cannot be negative" in str(exc)


def test_conduit_descriptor_payload_cleanup_is_idempotent() -> None:
    """
    Verify cleanup clears the payload and can be called repeatedly.

    Returns:
        None.
    """
    payload = ConduitDescriptorPayload(
        conduit_name="root",
        conduit_state=ConduitState.normal,
        policy=Policies.default,
        peer_conduit_ids=("peer-1",),
        parent_conduit_id="parent-1",
        lineage_depth=1,
    )

    payload.cleanup()
    payload.cleanup()

    assert payload.cleaned is True
