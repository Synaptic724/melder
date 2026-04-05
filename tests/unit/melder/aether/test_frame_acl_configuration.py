import json

import pytest

from melder.aether.nexus.acl.frame_acl_configuration import FrameACLConfiguration


def test_frame_acl_configuration_create_default_sets_expected_baseline() -> None:
    """
    Verify default configuration builds a stable empty ACL payload.

    Returns:
        None.
    """
    configuration = FrameACLConfiguration.create_default("ops")

    payload = configuration.to_json_dict()

    assert configuration.frame_name == "ops"
    assert configuration.previous_configuration_id is None
    assert payload["frame_name"] == "ops"
    assert payload["view_acl"] == {}
    assert payload["codegen_acl"] == {}


def test_frame_acl_configuration_from_json_normalizes_payload_order() -> None:
    """
    Verify JSON payloads are normalized into deterministic sorted-key strings.

    Returns:
        None.
    """
    json_payload = '{"codegen_acl":{},"frame_name":"ops","view_acl":{"visible":true}}'

    configuration = FrameACLConfiguration.from_json_configuration_string(
        frame_name="ops",
        json_configuration_string=json_payload,
        source_configuration_id=None,
        previous_configuration_id="cfg-1",
        reason="from-json",
        locked=True,
    )

    assert configuration.previous_configuration_id == "cfg-1"
    assert configuration.reason == "from-json"
    assert configuration.locked is True
    assert configuration.normalized_json_configuration_string == json.dumps(
        json.loads(json_payload),
        sort_keys=True,
    )


def test_frame_acl_configuration_init_rejects_invalid_inputs() -> None:
    """
    Verify configuration construction rejects invalid frame names and payload
    types.

    Returns:
        None.
    """
    with pytest.raises(ValueError, match="frame_name cannot be empty"):
        FrameACLConfiguration(
            frame_name="",
            normalized_json_configuration_string="{}",
            source_configuration_id=None,
            previous_configuration_id=None,
            reason="invalid",
            locked=True,
        )

    with pytest.raises(TypeError, match="normalized_json_configuration_string must be a string"):
        FrameACLConfiguration(
            frame_name="ops",
            normalized_json_configuration_string=None,
            source_configuration_id=None,
            previous_configuration_id=None,
            reason="invalid",
            locked=True,
        )

    with pytest.raises(ValueError, match="reason cannot be empty"):
        FrameACLConfiguration(
            frame_name="ops",
            normalized_json_configuration_string="{}",
            source_configuration_id=None,
            previous_configuration_id=None,
            reason="",
            locked=True,
        )


def test_frame_acl_configuration_from_json_rejects_invalid_payloads() -> None:
    """
    Verify JSON-loading rejects invalid payload types and malformed JSON.

    Returns:
        None.
    """
    with pytest.raises(TypeError, match="json_configuration_string must be a string"):
        FrameACLConfiguration.from_json_configuration_string(
            frame_name="ops",
            json_configuration_string=None,
            source_configuration_id=None,
            previous_configuration_id=None,
            reason="invalid",
            locked=False,
        )

    with pytest.raises(ValueError, match="must be valid JSON"):
        FrameACLConfiguration.from_json_configuration_string(
            frame_name="ops",
            json_configuration_string="{not-json}",
            source_configuration_id=None,
            previous_configuration_id=None,
            reason="invalid",
            locked=False,
        )


def test_frame_acl_configuration_create_new_from_acl_configuration_copies_payload() -> None:
    """
    Verify create_new_from_acl_configuration copies the payload into a new draft
    config node.

    Returns:
        None.
    """
    source = FrameACLConfiguration.create_default("ops")

    copied = FrameACLConfiguration.create_new_from_acl_configuration(
        source,
        reason="copy",
    )

    assert copied.frame_name == "ops"
    assert copied.source_configuration_id == source.configuration_id
    assert copied.previous_configuration_id is None
    assert copied.locked is False
    assert copied.to_json_string() == source.to_json_string()


def test_frame_acl_configuration_finalize_and_previous_pointer_rules() -> None:
    """
    Verify finalize locks the config and previous-pointer updates are only
    allowed before locking.

    Returns:
        None.
    """
    configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        FrameACLConfiguration.create_default("ops"),
        reason="draft",
    )

    configuration.set_previous_configuration_id("cfg-1")
    assert configuration.previous_configuration_id == "cfg-1"

    configuration.finalize()
    assert configuration.locked is True

    with pytest.raises(RuntimeError, match="Cannot change previous_configuration_id"):
        configuration.set_previous_configuration_id("cfg-2")


def test_frame_acl_configuration_set_json_configuration_string_normalizes_payload() -> None:
    """
    Verify mutable configs can accept and normalize JSON payload updates before
    finalize.

    Returns:
        None.
    """
    configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        FrameACLConfiguration.create_default("ops"),
        reason="draft",
    )

    configuration.set_json_configuration_string(
        '{"codegen_acl":{},"view_acl":{"visible":true},"frame_name":"ops"}'
    )

    assert configuration.to_json_dict() == {
        "codegen_acl": {},
        "frame_name": "ops",
        "view_acl": {"visible": True},
    }


def test_frame_acl_configuration_cleanup_clears_fields() -> None:
    """
    Verify cleanup nulls all owned configuration fields.

    Returns:
        None.
    """
    configuration = FrameACLConfiguration.create_default("ops")

    configuration.cleanup()

    assert configuration.cleaned is True
    assert configuration._configuration_id is None
    assert configuration._frame_name is None
    assert configuration._source_configuration_id is None
    assert configuration._previous_configuration_id is None
    assert configuration._created_at is None
    assert configuration._reason is None
    assert configuration._locked is None
    assert configuration._normalized_json_configuration_string is None
