from melder.aether.structure_profiles.structure_profile_models import (
    ConduitStructureProfile,
    FrameStructureProfile,
    SpellStructureRecord,
    StructureHint,
)


class _ExplodingCleanableHint(StructureHint):
    def cleanup(self) -> None:
        raise RuntimeError("boom")


class _ExplodingSpellRecord(SpellStructureRecord):
    def cleanup(self) -> None:
        raise RuntimeError("boom")


class _ExplodingConduitProfile(ConduitStructureProfile):
    def cleanup(self) -> None:
        raise RuntimeError("boom")


def test_structure_hint_validates_confidence_and_copies_provenance() -> None:
    provenance = {"source": "unit"}
    hint = StructureHint(
        kind="demo",
        description="derived",
        confidence=0.7,
        provenance=provenance,
        scope="spell",
    )

    provenance["source"] = "mutated"

    assert hint.provenance == {"source": "unit"}


def test_structure_hint_rejects_out_of_range_confidence() -> None:
    try:
        StructureHint(
            kind="demo",
            description="derived",
            confidence=1.1,
            provenance={"source": "unit"},
            scope="spell",
        )
    except ValueError as exc:
        assert "confidence must be between 0.0 and 1.0" in str(exc)
    else:
        raise AssertionError("Expected ValueError for out-of-range confidence.")


def test_structure_hint_cleanup_is_idempotent() -> None:
    hint = StructureHint(
        kind="demo",
        description="derived",
        confidence=0.2,
        provenance={"source": "unit"},
        scope="spell",
    )

    hint.cleanup()
    hint.cleanup()

    assert hint.cleaned is True
    assert hint.kind is None
    assert hint.provenance is None


def test_spell_structure_record_copies_mutable_inputs_and_cleans_nested_hints() -> None:
    dependencies = {"direct_dependencies": ["a"], "direct_dependents": []}
    sockets = [{"spell_id": "s1", "target_spell_ids": ["a"]}]
    defaults = [{"binding_name": "demo"}]
    hint = StructureHint(
        kind="demo",
        description="derived",
        confidence=0.5,
        provenance={"source": "unit"},
        scope="spell",
    )
    record = SpellStructureRecord(
        spell_id="spell-1",
        lineage_id="lineage-1",
        owner_conduit_id="conduit-1",
        binding_key=("frame", "binding"),
        existence="unique",
        spell_type="SPELL",
        permissions="read",
        dependencies=dependencies,
        sockets=sockets,
        spellmap_defaults=defaults,
        derived_hints=[hint],
    )

    dependencies["new_key"] = ["b"]
    sockets.append({"spell_id": "s2"})
    defaults.append({"binding_name": "extra"})

    assert "new_key" not in record.dependencies
    assert len(record.sockets) == 1
    assert len(record.spellmap_defaults) == 1

    record.cleanup()
    record.cleanup()

    assert record.cleaned is True
    assert hint.cleaned is True
    assert record.dependencies is None
    assert record.sockets is None
    assert record.spellmap_defaults is None


def test_spell_structure_record_cleanup_swallows_nested_hint_cleanup_failures() -> None:
    hint = _ExplodingCleanableHint(
        kind="demo",
        description="derived",
        confidence=0.5,
        provenance={"source": "unit"},
        scope="spell",
    )
    record = SpellStructureRecord(
        spell_id="spell-1",
        lineage_id="lineage-1",
        owner_conduit_id="conduit-1",
        binding_key=("frame", "binding"),
        existence="unique",
        spell_type="SPELL",
        permissions="read",
        dependencies={"direct_dependencies": [], "direct_dependents": []},
        sockets=[],
        spellmap_defaults=[],
        derived_hints=[hint],
    )

    record.cleanup()

    assert record.cleaned is True
    assert record.derived_hints is None


def test_conduit_structure_profile_cleanup_cascades_records_and_hints() -> None:
    record = SpellStructureRecord(
        spell_id="spell-1",
        lineage_id="lineage-1",
        owner_conduit_id="conduit-1",
        binding_key=None,
        existence=None,
        spell_type=None,
        permissions=None,
        dependencies={"direct_dependencies": [], "direct_dependents": []},
        sockets=[],
        spellmap_defaults=[],
        derived_hints=[],
    )
    hint = StructureHint(
        kind="demo",
        description="derived",
        confidence=0.6,
        provenance={"source": "unit"},
        scope="conduit",
    )
    profile = ConduitStructureProfile(
        conduit_id="conduit-1",
        conduit_name="root",
        conduit_state="normal",
        dynamic_environment=False,
        aetheric_frame="ops",
        spell_records={"spell-1": record},
        derived_hints=[hint],
    )

    profile.cleanup()
    profile.cleanup()

    assert profile.cleaned is True
    assert record.cleaned is True
    assert hint.cleaned is True
    assert profile.spell_records is None
    assert profile.derived_hints is None


def test_conduit_structure_profile_cleanup_swallows_nested_cleanup_failures() -> None:
    record = _ExplodingSpellRecord(
        spell_id="spell-1",
        lineage_id="lineage-1",
        owner_conduit_id="conduit-1",
        binding_key=None,
        existence=None,
        spell_type=None,
        permissions=None,
        dependencies={"direct_dependencies": [], "direct_dependents": []},
        sockets=[],
        spellmap_defaults=[],
        derived_hints=[],
    )
    hint = _ExplodingCleanableHint(
        kind="demo",
        description="derived",
        confidence=0.6,
        provenance={"source": "unit"},
        scope="conduit",
    )
    profile = ConduitStructureProfile(
        conduit_id="conduit-1",
        conduit_name="root",
        conduit_state="normal",
        dynamic_environment=False,
        aetheric_frame="ops",
        spell_records={"spell-1": record},
        derived_hints=[hint],
    )

    profile.cleanup()

    assert profile.cleaned is True
    assert profile.spell_records is None
    assert profile.derived_hints is None


def test_frame_structure_profile_copies_inputs_and_cascades_cleanup() -> None:
    record = SpellStructureRecord(
        spell_id="spell-1",
        lineage_id="lineage-1",
        owner_conduit_id="conduit-1",
        binding_key=None,
        existence=None,
        spell_type=None,
        permissions=None,
        dependencies={"direct_dependencies": [], "direct_dependents": []},
        sockets=[],
        spellmap_defaults=[],
        derived_hints=[],
    )
    conduit_profile = ConduitStructureProfile(
        conduit_id="conduit-1",
        conduit_name="root",
        conduit_state="normal",
        dynamic_environment=False,
        aetheric_frame="ops",
        spell_records={"spell-1": record},
        derived_hints=[],
    )
    hint = StructureHint(
        kind="demo",
        description="derived",
        confidence=0.8,
        provenance={"source": "unit"},
        scope="frame",
    )
    clusters = [{"name": "alpha"}]
    profile = FrameStructureProfile(
        frame_id="frame-1",
        frame_name="ops",
        conduit_profiles={"conduit-1": conduit_profile},
        spell_records={"spell-1": record},
        clusters=clusters,
        max_related=7,
        derived_hints=[hint],
    )

    clusters.append({"name": "beta"})

    assert profile.clusters == [{"name": "alpha"}]

    profile.cleanup()
    profile.cleanup()

    assert profile.cleaned is True
    assert conduit_profile.cleaned is True
    assert record.cleaned is True
    assert hint.cleaned is True
    assert profile.clusters is None
    assert profile.max_related is None


def test_frame_structure_profile_cleanup_swallows_nested_cleanup_failures() -> None:
    record = _ExplodingSpellRecord(
        spell_id="spell-1",
        lineage_id="lineage-1",
        owner_conduit_id="conduit-1",
        binding_key=None,
        existence=None,
        spell_type=None,
        permissions=None,
        dependencies={"direct_dependencies": [], "direct_dependents": []},
        sockets=[],
        spellmap_defaults=[],
        derived_hints=[],
    )
    conduit_profile = _ExplodingConduitProfile(
        conduit_id="conduit-1",
        conduit_name="root",
        conduit_state="normal",
        dynamic_environment=False,
        aetheric_frame="ops",
        spell_records={"spell-1": record},
        derived_hints=[],
    )
    hint = _ExplodingCleanableHint(
        kind="demo",
        description="derived",
        confidence=0.8,
        provenance={"source": "unit"},
        scope="frame",
    )
    profile = FrameStructureProfile(
        frame_id="frame-1",
        frame_name="ops",
        conduit_profiles={"conduit-1": conduit_profile},
        spell_records={"spell-1": record},
        clusters=[{"name": "alpha"}],
        max_related=7,
        derived_hints=[hint],
    )

    profile.cleanup()

    assert profile.cleaned is True
    assert profile.conduit_profiles is None
    assert profile.spell_records is None
    assert profile.derived_hints is None
