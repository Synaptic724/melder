from melder.aether.nexus.frame_descriptor.spell_descriptor_payload import (
    SpellDescriptorPayload,
)
from melder.aether.spellbook.spell_crafter.spell_examiner.profiles.binding_profile import (
    CallableBindingProfile,
    ClassBindingProfile,
    InstanceBindingProfile,
    OtherBindingProfile,
    SpellBindingKind,
)


def test_spell_descriptor_payload_exposes_stable_public_fields() -> None:
    """
    Verify the payload stores the expected spell-facing descriptor fields.

    Returns:
        None.
    """
    payload = SpellDescriptorPayload(
        payload_type="detailed",
        binding_payload={"kind": "class"},
        resolution_payload={"requirements": []},
        class_profile={"methods": ["run"]},
        callable_profile={"signature": "() -> None"},
        metadata={"frame": "ops"},
        instance_members={"state": {"type": "str"}},
        dynamic_access={"has_getattr": False},
        source_profile_name="detailed",
        source_profile_version="0.0.1",
    )

    assert payload.payload_type == "detailed"
    assert payload.payload_version == "0.0.1"
    assert payload.source_profile_name == "detailed"
    assert payload.source_profile_version == "0.0.1"
    assert payload.binding_payload == {"kind": "class"}
    assert payload.resolution_payload == {"requirements": []}
    assert payload.class_profile == {"methods": ["run"]}
    assert payload.callable_profile == {"signature": "() -> None"}
    assert payload.metadata == {"frame": "ops"}
    assert payload.instance_members == {"state": {"type": "str"}}
    assert payload.dynamic_access == {"has_getattr": False}


def test_spell_descriptor_payload_rejects_invalid_profile_metadata() -> None:
    """
    Verify payload validation rejects missing type/version combinations.

    Returns:
        None.
    """
    try:
        SpellDescriptorPayload(
            payload_type="",
            binding_payload={},
            resolution_payload={},
        )
        raise AssertionError("Expected empty payload_type to fail.")
    except ValueError as exc:
        assert "payload_type cannot be empty" in str(exc)

    try:
        SpellDescriptorPayload(
            payload_type="general",
            payload_version="",
            binding_payload={},
            resolution_payload={},
        )
        raise AssertionError("Expected empty payload_version to fail.")
    except ValueError as exc:
        assert "payload_version cannot be empty" in str(exc)

    try:
        SpellDescriptorPayload(
            payload_type="general",
            binding_payload={},
            resolution_payload={},
            source_profile_version="0.0.1",
        )
        raise AssertionError("Expected orphaned source_profile_version to fail.")
    except ValueError as exc:
        assert "source_profile_version requires source_profile_name" in str(exc)


def test_spell_descriptor_payload_from_spell_profile_sanitizes_binding_profile() -> None:
    """
    Verify `from_spell_profile` strips live object refs and preserves safe fields.

    Returns:
        None.
    """
    original_object = object()
    binding_profile = ClassBindingProfile(
        kind=SpellBindingKind.CLASS,
        original_object=original_object,
        name="BasicService",
        qualname="BasicService",
        module="tests.example",
        bases=["object"],
        mro=["BasicService", "object"],
        annotations={"value": "str"},
        origin_file="example.py",
        origin_line=10,
        source_preview="class BasicService: ...",
        is_dataclass=False,
        decorated=False,
        method_names=["run"],
    )

    payload = SpellDescriptorPayload.from_spell_profile(
        "detailed",
        "0.0.1",
        binding_profile,
        resolution_payload={"requirements": []},
        metadata={"frame": "ops"},
    )

    assert payload.payload_type == "detailed"
    assert payload.payload_version == "0.0.1"
    assert payload.source_profile_name == "detailed"
    assert payload.source_profile_version == "0.0.1"
    assert payload.binding_payload["kind"] == "CLASS"
    assert payload.binding_payload["name"] == "BasicService"
    assert payload.binding_payload["module"] == "tests.example"
    assert payload.binding_payload["method_names"] == ["run"]
    assert "original_object" not in payload.binding_payload


def test_spell_descriptor_payload_from_spell_profile_sanitizes_other_profile_kinds() -> None:
    callable_payload = SpellDescriptorPayload.from_spell_profile(
        "general",
        "0.0.1",
        CallableBindingProfile(
            kind=SpellBindingKind.CALLABLE,
            original_object=lambda value: value,
            object_id="callable-1",
            name="run",
            qualname="run",
            module="tests.example",
            parameters=[{"name": "value"}],
            repr_string="<function run>",
            type_name="function",
            signature="(value)",
            lambda_function=False,
            builtin_module=False,
            extension_module=False,
        ),
        resolution_payload={},
    )
    instance_payload = SpellDescriptorPayload.from_spell_profile(
        "general",
        "0.0.1",
        InstanceBindingProfile(
            kind=SpellBindingKind.INSTANCE,
            original_object=object(),
            type_name="Service",
            module="tests.example",
            repr_string="<Service>",
        ),
        resolution_payload={},
    )
    other_payload = SpellDescriptorPayload.from_spell_profile(
        "general",
        "0.0.1",
        OtherBindingProfile(
            kind=SpellBindingKind.OTHER,
            original_object=object(),
            type_name="Opaque",
            module="tests.example",
            repr_string="<Opaque>",
        ),
        resolution_payload={},
    )

    assert callable_payload.binding_payload == {
        "kind": "CALLABLE",
        "name": "run",
        "qualname": "run",
        "module": "tests.example",
        "object_id": "callable-1",
        "type_name": "function",
        "repr_string": "<function run>",
        "signature": "(value)",
        "parameters": [{"name": "value"}],
        "builtin_module": False,
        "extension_module": False,
        "lambda_function": False,
        "abstract": False,
    }
    assert instance_payload.binding_payload == {
        "kind": "INSTANCE",
        "type_name": "Service",
        "module": "tests.example",
        "repr_string": "<Service>",
    }
    assert other_payload.binding_payload == {
        "kind": "OTHER",
        "type_name": "Opaque",
        "module": "tests.example",
        "repr_string": "<Opaque>",
    }


def test_spell_descriptor_payload_cleanup_is_idempotent() -> None:
    """
    Verify cleanup clears the payload and can be called repeatedly.

    Returns:
        None.
    """
    payload = SpellDescriptorPayload(
        payload_type="general",
        binding_payload={"kind": "class"},
        resolution_payload={"requirements": []},
        metadata={"frame": "ops"},
        instance_members={"state": {"type": "str"}},
        dynamic_access={"has_getattr": False},
    )

    payload.cleanup()
    payload.cleanup()

    assert payload.cleaned is True
