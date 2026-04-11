from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.aether.nexus.frame_descriptor.conduit_descriptor_payload import (
    ConduitDescriptorPayload,
)
from melder.aether.nexus.frame_descriptor.conduit_record import ConduitRecord


def _build_payload() -> ConduitDescriptorPayload:
    """
    Build one descriptor-safe conduit payload for record tests.

    Returns:
        ConduitDescriptorPayload: Fresh payload object.
    """
    return ConduitDescriptorPayload(
        conduit_name="root",
        conduit_state=ConduitState.normal,
        policy=Policies.default,
        peer_conduit_ids=("peer-1",),
    )


def test_conduit_record_exposes_stable_public_fields() -> None:
    """
    Verify the record stores the expected publication metadata and payload.

    Returns:
        None.
    """
    payload = _build_payload()
    record = ConduitRecord(
        conduit_id="conduit-1",
        root_conduit_id="root-1",
        frame_name="ops",
        origin_spellbook_id="spellbook-1",
        payload=payload,
    )

    assert record.nexus_label == "default"
    assert record.nexus_version == "0.0.1"
    assert record.conduit_id == "conduit-1"
    assert record.root_conduit_id == "root-1"
    assert record.frame_name == "ops"
    assert record.origin_spellbook_id == "spellbook-1"
    assert record.payload is payload


def test_conduit_record_rejects_invalid_constructor_inputs() -> None:
    """
    Verify constructor validation rejects missing labels, versions, and payloads.

    Returns:
        None.
    """
    try:
        ConduitRecord(
            nexus_label="",
            conduit_id="conduit-1",
            root_conduit_id="root-1",
            frame_name="ops",
            origin_spellbook_id=None,
            payload=_build_payload(),
        )
        raise AssertionError("Expected empty nexus_label to fail.")
    except ValueError as exc:
        assert "nexus_label cannot be empty" in str(exc)

    try:
        ConduitRecord(
            nexus_version="",
            conduit_id="conduit-1",
            root_conduit_id="root-1",
            frame_name="ops",
            origin_spellbook_id=None,
            payload=_build_payload(),
        )
        raise AssertionError("Expected empty nexus_version to fail.")
    except ValueError as exc:
        assert "nexus_version cannot be empty" in str(exc)

    try:
        ConduitRecord(
            conduit_id="conduit-1",
            root_conduit_id="root-1",
            frame_name="ops",
            origin_spellbook_id=None,
            payload=None,
        )
        raise AssertionError("Expected missing payload to fail.")
    except ValueError as exc:
        assert "payload cannot be None" in str(exc)

    try:
        ConduitRecord(
            conduit_id="conduit-1",
            root_conduit_id="root-1",
            frame_name="ops",
            origin_spellbook_id=None,
            payload=object(),
        )
        raise AssertionError("Expected invalid payload type to fail.")
    except TypeError as exc:
        assert "payload must satisfy IConduitDescriptorPayload" in str(exc)


def test_conduit_record_cleanup_is_idempotent_and_cleans_owned_payload() -> None:
    """
    Verify cleanup clears the record and cascades into the owned payload.

    Returns:
        None.
    """
    payload = _build_payload()
    record = ConduitRecord(
        conduit_id="conduit-1",
        root_conduit_id="root-1",
        frame_name="ops",
        origin_spellbook_id="spellbook-1",
        payload=payload,
    )

    record.cleanup()
    record.cleanup()

    assert record.cleaned is True
    assert payload.cleaned is True
