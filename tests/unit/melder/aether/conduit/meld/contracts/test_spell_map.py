from unittest.mock import patch

import pytest

from melder.aether.conduit.meld.contracts.spell_map import SpellMap


def test_init_requires_spell_or_spellframe_raises_valueerror() -> None:
    """
    Verify SpellMap rejects empty descriptors.

    Contract:
        - At least one of spell or spellframe must be provided.

    Raises:
        AssertionError: If the missing-input guard does not raise.
    """
    with pytest.raises(ValueError, match="requires at least one"):
        SpellMap()


def test_init_accepts_spell_only_sets_fields() -> None:
    """
    Verify SpellMap accepts a spell-only descriptor.

    Contract:
        - spell is retained.
        - spellframe and binding_name default to None.

    Raises:
        AssertionError: If fields are not initialized correctly.
    """
    mapping = SpellMap(spell="alpha")
    assert mapping.spell == "alpha"
    assert mapping.spellframe is None
    assert mapping.binding_name is None


def test_init_accepts_spellframe_only_sets_fields() -> None:
    """
    Verify SpellMap accepts a frame-only descriptor.

    Contract:
        - spell is None.
        - spellframe is retained.

    Raises:
        AssertionError: If fields are not initialized correctly.
    """
    mapping = SpellMap(spellframe="frame")
    assert mapping.spell is None
    assert mapping.spellframe == "frame"


def test_init_accepts_spell_frame_binding() -> None:
    """
    Verify SpellMap retains spell, frame, and binding.

    Contract:
        - spell, spellframe, and binding_name are preserved as provided.

    Raises:
        AssertionError: If any field is not preserved.
    """
    mapping = SpellMap(
        spell="alpha",
        spellframe="frame",
        binding_name="primary",
    )
    assert mapping.spell == "alpha"
    assert mapping.spellframe == "frame"
    assert mapping.binding_name == "primary"


def test_init_normalizes_binding_name_when_provided() -> None:
    """
    Verify SpellMap normalizes binding names when provided.

    Contract:
        - binding_name is lowercased for case-insensitive matching.

    Raises:
        AssertionError: If binding_name is not normalized.
    """
    mapping = SpellMap(
        spell="alpha",
        spellframe="frame",
        binding_name="Primary",
    )
    assert mapping.binding_name == "primary"


def test_default_override_is_none() -> None:
    """
    Verify default overrides are None per instance.

    Contract:
        - spell_override defaults to None.

    Raises:
        AssertionError: If defaults are not None.
    """
    first = SpellMap(spell="alpha")
    second = SpellMap(spell="beta")
    assert first.spell_override is None
    assert second.spell_override is None


def test_spell_override_dict_is_preserved() -> None:
    """
    Verify dict overrides are preserved by reference.

    Contract:
        - spell_override references the provided dict.

    Raises:
        AssertionError: If the override is copied or replaced.
    """
    override = {"x": 1}
    mapping = SpellMap(spell="alpha", spell_override=override)
    assert mapping.spell_override is override


def test_spell_override_tuple_is_preserved() -> None:
    """
    Verify tuple overrides are preserved by reference.

    Contract:
        - spell_override retains tuple payloads as positional args.

    Raises:
        AssertionError: If the override is copied or replaced.
    """
    override = (1, 2)
    mapping = SpellMap(spell="alpha", spell_override=override)
    assert mapping.spell_override is override


def test_cleanup_clears_dict_override_and_nulls_fields() -> None:
    """
    Verify cleanup clears dict overrides and nulls references.

    Contract:
        - dict overrides are cleared.
        - spell, spellframe, binding_name, and spell_override become None.

    Raises:
        AssertionError: If cleanup leaves state behind.
    """
    override = {"x": 1}
    mapping = SpellMap(
        spell="alpha",
        spellframe="frame",
        binding_name="primary",
        spell_override=override,
    )
    mapping.cleanup()
    assert override == {}
    assert mapping.spell is None
    assert mapping.spellframe is None
    assert mapping.binding_name is None
    assert mapping.spell_override is None


def test_cleanup_clears_list_override_and_nulls_fields() -> None:
    """
    Verify cleanup clears list overrides and nulls references.

    Contract:
        - list overrides are cleared.
        - spell, spellframe, binding_name, and spell_override become None.

    Raises:
        AssertionError: If cleanup leaves state behind.
    """
    override = [1, 2]
    mapping = SpellMap(
        spell="alpha",
        spell_override=override,
    )
    mapping.cleanup()
    assert override == []
    assert mapping.spell is None
    assert mapping.spellframe is None
    assert mapping.binding_name is None
    assert mapping.spell_override is None


def test_cleanup_is_idempotent() -> None:
    """
    Verify cleanup can be called multiple times safely.

    Contract:
        - Subsequent cleanup calls do not raise.
        - State remains cleaned after repeated calls.

    Raises:
        AssertionError: If cleanup is not idempotent.
    """
    mapping = SpellMap(spell="alpha")
    mapping.cleanup()
    mapping.cleanup()
    assert mapping.spell is None
    assert mapping.spell_override is None


def test_lookup_triplet_reflects_fields() -> None:
    """
    Verify lookup_triplet reflects current attributes.

    Contract:
        - lookup_triplet returns (spell, spellframe, binding_name).

    Raises:
        AssertionError: If the tuple does not match the inputs.
    """
    mapping = SpellMap(
        spell="alpha",
        spellframe="frame",
        binding_name="primary",
    )
    assert mapping.lookup_triplet == ("alpha", "frame", "primary")


def test_lookup_triplet_for_frame_only() -> None:
    """
    Verify lookup_triplet preserves frame-only descriptors.

    Contract:
        - spell is None for frame-only maps.
        - spellframe and binding_name remain set.

    Raises:
        AssertionError: If lookup_triplet is incorrect for frame-only inputs.
    """
    mapping = SpellMap(spell=None, spellframe="frame", binding_name="primary")
    assert mapping.lookup_triplet == (None, "frame", "primary")


def test_canonical_key_delegates_to_normalize_spell_key() -> None:
    """
    Verify canonical_key delegates to SpellInputUtils.normalize_spell_key.

    Contract:
        - normalize_spell_key is called with spell, spellframe, binding_name.
        - The returned tuple is surfaced as canonical_key.

    Raises:
        AssertionError: If delegation or return value is incorrect.
    """
    mapping = SpellMap(
        spell="alpha",
        spellframe="frame",
        binding_name="primary",
    )
    with patch(
        "melder.utilities.helpers.general_helpers.SpellInputUtils.normalize_spell_key",
        return_value=("frame", "primary"),
    ) as normalize:
        result = mapping.canonical_key
    normalize.assert_called_once_with(
        spell="alpha",
        spellframe="frame",
        binding_name="primary",
    )
    assert result == ("frame", "primary")


def test_spell_key_aliases_canonical_key() -> None:
    """
    Verify spell_key mirrors canonical_key output.

    Contract:
        - spell_key returns the same tuple as canonical_key.

    Raises:
        AssertionError: If spell_key diverges from canonical_key.
    """
    mapping = SpellMap(spell="alpha")
    with patch(
        "melder.utilities.helpers.general_helpers.SpellInputUtils.normalize_spell_key",
        return_value=("frame", "default"),
    ):
        assert mapping.spell_key == mapping.canonical_key


def test_repr_includes_fields() -> None:
    """
    Verify __repr__ includes the primary fields.

    Contract:
        - Representation includes spell, spellframe, and binding_name.

    Raises:
        AssertionError: If the representation omits key fields.
    """
    mapping = SpellMap(
        spell="alpha",
        spellframe="frame",
        binding_name="primary",
        spell_override={"x": 1},
    )
    rendered = repr(mapping)
    assert "alpha" in rendered
    assert "frame" in rendered
    assert "primary" in rendered
