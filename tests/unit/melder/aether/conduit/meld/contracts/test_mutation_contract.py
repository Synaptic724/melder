from unittest.mock import patch

import pytest

from melder.aether.conduit.meld.contracts.mutation_contract import MutationContract


def test_init_requires_spell_or_spellframe_raises_valueerror() -> None:
    """
    Verify MutationContract rejects empty descriptors.

    Contract:
        - At least one of spell or spellframe must be provided.

    Raises:
        AssertionError: If the missing-input guard does not raise.
    """
    with pytest.raises(ValueError, match="requires at least one"):
        MutationContract()


def test_init_accepts_spell_only_sets_fields() -> None:
    """
    Verify MutationContract accepts a spell-only descriptor.

    Contract:
        - spell is retained.
        - spellframe and binding_name default to None.

    Raises:
        AssertionError: If fields are not initialized correctly.
    """
    contract = MutationContract(spell="alpha")
    assert contract.spell == "alpha"
    assert contract.spellframe is None
    assert contract.binding_name is None


def test_init_accepts_spellframe_only_sets_fields() -> None:
    """
    Verify MutationContract accepts a frame-only descriptor.

    Contract:
        - spell is None.
        - spellframe is retained.

    Raises:
        AssertionError: If fields are not initialized correctly.
    """
    contract = MutationContract(spellframe="frame")
    assert contract.spell is None
    assert contract.spellframe == "frame"


def test_init_accepts_spell_frame_binding() -> None:
    """
    Verify MutationContract retains spell, frame, and binding.

    Contract:
        - spell, spellframe, and binding_name are preserved as provided.

    Raises:
        AssertionError: If any field is not preserved.
    """
    contract = MutationContract(
        spell="alpha",
        spellframe="frame",
        binding_name="primary",
    )
    assert contract.spell == "alpha"
    assert contract.spellframe == "frame"
    assert contract.binding_name == "primary"


def test_init_normalizes_binding_name_when_provided() -> None:
    """
    Verify MutationContract normalizes binding names when provided.

    Contract:
        - binding_name is lowercased for case-insensitive matching.

    Raises:
        AssertionError: If binding_name is not normalized.
    """
    contract = MutationContract(
        spell="alpha",
        spellframe="frame",
        binding_name="Primary",
    )
    assert contract.binding_name == "primary"


def test_default_override_is_distinct_dict() -> None:
    """
    Verify default overrides are independent per instance.

    Contract:
        - spell_override defaults to an empty dict.
        - Each instance receives a distinct dict.

    Raises:
        AssertionError: If defaults are shared across instances.
    """
    first = MutationContract(spell="alpha")
    second = MutationContract(spell="beta")
    assert first.spell_override == {}
    assert second.spell_override == {}
    assert first.spell_override is not second.spell_override


def test_spell_override_dict_is_preserved() -> None:
    """
    Verify dict overrides are preserved by reference.

    Contract:
        - spell_override references the provided dict.

    Raises:
        AssertionError: If the override is copied or replaced.
    """
    override = {"x": 1}
    contract = MutationContract(spell="alpha", spell_override=override)
    assert contract.spell_override is override


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
    contract = MutationContract(
        spell="alpha",
        spellframe="frame",
        binding_name="primary",
        spell_override=override,
    )
    contract.cleanup()
    assert override == {}
    assert contract.spell is None
    assert contract.spellframe is None
    assert contract.binding_name is None
    assert contract.spell_override is None


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
    contract = MutationContract(
        spell="alpha",
        spell_override=override,
    )
    contract.cleanup()
    assert override == []
    assert contract.spell is None
    assert contract.spellframe is None
    assert contract.binding_name is None
    assert contract.spell_override is None


def test_cleanup_is_idempotent() -> None:
    """
    Verify cleanup can be called multiple times safely.

    Contract:
        - Subsequent cleanup calls do not raise.
        - State remains cleaned after repeated calls.

    Raises:
        AssertionError: If cleanup is not idempotent.
    """
    contract = MutationContract(spell="alpha")
    contract.cleanup()
    contract.cleanup()
    assert contract.spell is None
    assert contract.spell_override is None


def test_lookup_triplet_reflects_fields() -> None:
    """
    Verify lookup_triplet reflects current attributes.

    Contract:
        - lookup_triplet returns (spell, spellframe, binding_name).

    Raises:
        AssertionError: If the tuple does not match the inputs.
    """
    contract = MutationContract(
        spell="alpha",
        spellframe="frame",
        binding_name="primary",
    )
    assert contract.lookup_triplet == ("alpha", "frame", "primary")


def test_canonical_key_delegates_to_normalize_spell_key() -> None:
    """
    Verify canonical_key delegates to SpellInputUtils.normalize_spell_key.

    Contract:
        - normalize_spell_key is called with spell, spellframe, binding_name.
        - The returned tuple is surfaced as canonical_key.

    Raises:
        AssertionError: If delegation or return value is incorrect.
    """
    contract = MutationContract(
        spell="alpha",
        spellframe="frame",
        binding_name="primary",
    )
    with patch(
        "melder.utilities.helpers.general_helpers.SpellInputUtils.normalize_spell_key",
        return_value=("frame", "primary"),
    ) as normalize:
        result = contract.canonical_key
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
    contract = MutationContract(spell="alpha")
    with patch(
        "melder.utilities.helpers.general_helpers.SpellInputUtils.normalize_spell_key",
        return_value=("frame", "default"),
    ):
        assert contract.spell_key == contract.canonical_key


def test_late_binding_defaults_to_false() -> None:
    """
    Verify late_binding defaults to False.

    Contract:
        - late_binding is False when not provided.

    Raises:
        AssertionError: If the default is not False.
    """
    contract = MutationContract(spell="alpha")
    assert contract.late_binding is False


def test_late_binding_true_is_preserved() -> None:
    """
    Verify late_binding preserves a True input.

    Contract:
        - late_binding is True when provided.

    Raises:
        AssertionError: If the flag is not preserved.
    """
    contract = MutationContract(spell="alpha", late_binding=True)
    assert contract.late_binding is True


def test_repr_includes_fields() -> None:
    """
    Verify __repr__ includes the primary fields.

    Contract:
        - Representation includes spell, spellframe, binding_name, and late_binding.

    Raises:
        AssertionError: If the representation omits key fields.
    """
    contract = MutationContract(
        spell="alpha",
        spellframe="frame",
        binding_name="primary",
        late_binding=True,
        spell_override={"x": 1},
    )
    rendered = repr(contract)
    assert "alpha" in rendered
    assert "frame" in rendered
    assert "primary" in rendered
    assert "late_binding=True" in rendered
