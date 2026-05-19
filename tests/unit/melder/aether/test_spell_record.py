from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.nexus.frame_descriptor.spell_descriptor_payload import (
    SpellDescriptorPayload,
)
from melder.aether.nexus.frame_descriptor.spell_record import SpellRecord
from melder.aether.spellbook.existence.existence import Existence


def _build_payload() -> SpellDescriptorPayload:
    """
    Build one descriptor-safe spell payload for record tests.

    Returns:
        SpellDescriptorPayload: Fresh payload object.
    """
    return SpellDescriptorPayload(
        payload_type="general",
        binding_payload={"kind": "class"},
        resolution_payload={"requirements": []},
        metadata={"frame": "ops"},
    )


def test_spell_record_exposes_stable_public_fields_and_record_key() -> None:
    """
    Verify the record stores the expected publication metadata and key.

    Returns:
        None.
    """
    payload = _build_payload()
    record = SpellRecord(
        origin_spellbook_id="spellbook-1",
        frame_name="ops",
        owner_conduit_id="conduit-1",
        spell_id="spell-1",
        spell_index_id="lineage-1",
        spell_name="SpellOne",
        spellframe="LogicFrame",
        binding_name="spell_one",
        permissions=Permissions.create,
        existence=Existence.unique,
        payload=payload,
    )

    assert record.nexus_label == "default"
    assert record.nexus_version == "0.0.1"
    assert record.origin_spellbook_id == "spellbook-1"
    assert record.frame_name == "ops"
    assert record.owner_conduit_id == "conduit-1"
    assert record.spell_id == "spell-1"
    assert record.spell_index_id == "lineage-1"
    assert record.spell_name == "SpellOne"
    assert record.spellframe == "LogicFrame"
    assert record.binding_name == "spell_one"
    assert record.permissions is Permissions.create
    assert record.existence is Existence.unique
    assert record.payload is payload
    assert record.record_key == ("spellbook-1", "spell-1")


def test_spell_record_rejects_invalid_constructor_inputs() -> None:
    """
    Verify constructor validation rejects missing labels, versions, and payloads.

    Returns:
        None.
    """
    try:
        SpellRecord(
            nexus_label="",
            origin_spellbook_id="spellbook-1",
            frame_name="ops",
            owner_conduit_id=None,
            spell_id="spell-1",
            spell_index_id="lineage-1",
            spell_name="SpellOne",
            spellframe=None,
            binding_name="spell_one",
            permissions=Permissions.create,
            existence=Existence.unique,
            payload=_build_payload(),
        )
        raise AssertionError("Expected empty nexus_label to fail.")
    except ValueError as exc:
        assert "nexus_label cannot be empty" in str(exc)

    try:
        SpellRecord(
            nexus_version="",
            origin_spellbook_id="spellbook-1",
            frame_name="ops",
            owner_conduit_id=None,
            spell_id="spell-1",
            spell_index_id="lineage-1",
            spell_name="SpellOne",
            spellframe=None,
            binding_name="spell_one",
            permissions=Permissions.create,
            existence=Existence.unique,
            payload=_build_payload(),
        )
        raise AssertionError("Expected empty nexus_version to fail.")
    except ValueError as exc:
        assert "nexus_version cannot be empty" in str(exc)

    try:
        SpellRecord(
            origin_spellbook_id="spellbook-1",
            frame_name="ops",
            owner_conduit_id=None,
            spell_id="spell-1",
            spell_index_id="lineage-1",
            spell_name="SpellOne",
            spellframe=None,
            binding_name="spell_one",
            permissions=Permissions.create,
            existence=Existence.unique,
            payload=None,
        )
        raise AssertionError("Expected missing payload to fail.")
    except ValueError as exc:
        assert "payload cannot be None" in str(exc)

    try:
        SpellRecord(
            origin_spellbook_id="spellbook-1",
            frame_name="ops",
            owner_conduit_id=None,
            spell_id="spell-1",
            spell_index_id="lineage-1",
            spell_name="SpellOne",
            spellframe=None,
            binding_name="spell_one",
            permissions=Permissions.create,
            existence=Existence.unique,
            payload=object(),
        )
        raise AssertionError("Expected invalid payload type to fail.")
    except TypeError as exc:
        assert "payload must satisfy ISpellDescriptorPayload" in str(exc)


def test_spell_record_cleanup_is_idempotent_and_cleans_owned_payload() -> None:
    """
    Verify cleanup clears the record and cascades into the owned payload.

    Returns:
        None.
    """
    payload = _build_payload()
    record = SpellRecord(
        origin_spellbook_id="spellbook-1",
        frame_name="ops",
        owner_conduit_id="conduit-1",
        spell_id="spell-1",
        spell_index_id="lineage-1",
        spell_name="SpellOne",
        spellframe=None,
        binding_name="spell_one",
        permissions=Permissions.create,
        existence=Existence.unique,
        payload=payload,
    )

    record.cleanup()
    record.cleanup()

    assert record.cleaned is True
    assert payload.cleaned is True
