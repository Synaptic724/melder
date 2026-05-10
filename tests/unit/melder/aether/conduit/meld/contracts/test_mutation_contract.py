import threading
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


def test_default_override_is_none() -> None:
    """
    Verify default overrides are None per instance.

    Contract:
        - spell_override defaults to None.

    Raises:
        AssertionError: If defaults are not None.
    """
    first = MutationContract(spell="alpha")
    second = MutationContract(spell="beta")
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
    contract = MutationContract(spell="alpha", spell_override=override)
    assert contract.spell_override is override


def test_spell_override_tuple_is_preserved() -> None:
    """
    Verify tuple overrides are preserved by reference.

    Contract:
        - spell_override retains tuple payloads as positional args.

    Raises:
        AssertionError: If the override is copied or replaced.
    """
    override = (1, 2)
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
    with pytest.raises(RuntimeError, match="cleaned"):
        _ = contract.spell
    with pytest.raises(RuntimeError, match="cleaned"):
        _ = contract.spellframe
    with pytest.raises(RuntimeError, match="cleaned"):
        _ = contract.binding_name
    with pytest.raises(RuntimeError, match="cleaned"):
        _ = contract.spell_override


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
    with pytest.raises(RuntimeError, match="cleaned"):
        _ = contract.spell
    with pytest.raises(RuntimeError, match="cleaned"):
        _ = contract.spellframe
    with pytest.raises(RuntimeError, match="cleaned"):
        _ = contract.binding_name
    with pytest.raises(RuntimeError, match="cleaned"):
        _ = contract.spell_override


def test_cleanup_leaves_tuple_override_intact() -> None:
    """
    Verify cleanup does not mutate tuple overrides.

    Contract:
        - tuple overrides remain unchanged after cleanup.
        - contract spell_override is set to None.

    Raises:
        AssertionError: If tuple overrides are mutated.
    """
    override = (1, 2)
    contract = MutationContract(
        spell="alpha",
        spell_override=override,
    )
    contract.cleanup()
    assert override == (1, 2)
    with pytest.raises(RuntimeError, match="cleaned"):
        _ = contract.spell_override


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
    with pytest.raises(RuntimeError, match="cleaned"):
        _ = contract.spell
    with pytest.raises(RuntimeError, match="cleaned"):
        _ = contract.spell_override


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


def test_update_contract_updates_fields_and_normalizes_binding_name() -> None:
    """
    Verify update_contract mutates the live descriptor through the supported path.

    Contract:
        - Updates spell, spellframe, binding_name, spell_override, and
          late_binding under the internal lock.
        - Normalizes the binding name when provided.
    """
    override = {"x": 1}
    contract = MutationContract(spell="alpha", binding_name="Primary")

    contract.update_contract(
        spell="beta",
        spellframe="frame",
        binding_name="Secondary",
        spell_override=override,
        late_binding=True,
    )

    assert contract.spell == "beta"
    assert contract.spellframe == "frame"
    assert contract.binding_name == "secondary"
    assert contract.spell_override is override
    assert contract.late_binding is True


def test_update_contract_rejects_clearing_spell_and_spellframe() -> None:
    """
    Verify update_contract preserves the identity guard.

    Contract:
        - At least one of spell or spellframe must remain populated after the
          update.
    """
    contract = MutationContract(spell="alpha")

    with pytest.raises(ValueError, match="requires at least one"):
        contract.update_contract(spell=None, spellframe=None)


@pytest.mark.parametrize(
    "operation",
    [
        lambda contract: contract.lookup_triplet,
        lambda contract: contract.canonical_key,
        lambda contract: contract.spell_key,
        lambda contract: contract.spell,
        lambda contract: contract.spellframe,
        lambda contract: contract.binding_name,
        lambda contract: contract.spell_override,
        lambda contract: contract.late_binding,
        lambda contract: repr(contract),
        lambda contract: contract.update_contract(binding_name="x"),
    ],
)
def test_public_methods_raise_after_cleanup(operation) -> None:
    """
    Verify supported public read/update paths fail fast after cleanup.
    """
    contract = MutationContract(spell="alpha")
    contract.cleanup()

    with pytest.raises(RuntimeError, match="cleaned"):
        operation(contract)


def test_update_contract_and_read_paths_are_thread_safe() -> None:
    """
    Verify supported reads and writes can interleave across threads without errors.
    """
    contract = MutationContract(spell="alpha", spellframe="frame", binding_name="primary")
    barrier = threading.Barrier(3)
    errors: list[str] = []

    def writer(index: int) -> None:
        try:
            barrier.wait()
            for _ in range(100):
                contract.update_contract(
                    spell="alpha",
                    spellframe="frame",
                    binding_name=f"variant_{index}",
                    spell_override=contract.spell_override,
                    late_binding=bool(index % 2),
                )
        except Exception as exc:  # pragma: no cover - failure capture
            errors.append(f"writer:{index}:{exc}")

    def reader() -> None:
        try:
            barrier.wait()
            for _ in range(100):
                _ = contract.lookup_triplet
                _ = contract.canonical_key
                _ = repr(contract)
        except Exception as exc:  # pragma: no cover - failure capture
            errors.append(f"reader:{exc}")

    threads = [
        threading.Thread(target=writer, args=(1,), daemon=True),
        threading.Thread(target=writer, args=(2,), daemon=True),
        threading.Thread(target=reader, daemon=True),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=2.0)
        assert thread.is_alive() is False

    assert errors == []
    assert contract.binding_name in {"variant_1", "variant_2"}


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
