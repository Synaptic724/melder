"""Native CLEANED names, exact string values and historical lookup behavior."""

from enum import Enum, StrEnum
from typing import Tuple, Type, Union

import pytest

from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.crystallizer.crystals.recorded_unit_state import RecordedUnitState
from melder.utilities.helpers.general_helpers import EnumHelpers


@pytest.mark.parametrize(
    ("enum_type", "values"),
    [
        (SpellValidity, (1, 2, 3, 4, 5, 6)),
        (ConduitState, (1, 2, 3, 4)),
        (RecordedUnitState, ("enabled", "disabled", "cleaned")),
    ],
)
def test_cleaned_exact_string_values_keep_historical_by_value_inputs(
    enum_type: Type[Enum], values: Tuple[Union[int, str], ...],
) -> None:
    """Exact name values preserve the historical number/string-to-member mapping."""
    members = tuple(enum_type)
    assert issubclass(enum_type, StrEnum)
    assert tuple(member.value for member in members) == tuple(member.name for member in members)
    for old_value, member in zip(values, members):
        assert enum_type(old_value) is member


@pytest.mark.parametrize(
    ("enum_type", "names"),
    [
        (SpellValidity, ("unknown", "valid", "gated", "invalid", "disabled", "CLEANED")),
        (ConduitState, ("normal", "lesser", "pooled_lesser", "CLEANED")),
        (RecordedUnitState, ("enabled", "disabled", "CLEANED")),
    ],
)
def test_cleaned_has_one_canonical_python_name_and_keeps_other_names(
    enum_type: Type[Enum], names: Tuple[str, ...],
) -> None:
    """Only the terminal member is capitalized and no lowercase Python alias remains."""
    assert tuple(enum_type.__members__) == names
    assert enum_type["CLEANED"].name == "CLEANED"
    with pytest.raises(KeyError):
        enum_type["cleaned"]


@pytest.mark.parametrize("enum_type", [SpellValidity, ConduitState, RecordedUnitState])
@pytest.mark.parametrize("name", ["CLEANED", "cleaned", "ClEaNeD"])
def test_native_enum_helper_resolves_legacy_and_canonical_names(
    enum_type: Type[Enum], name: str,
) -> None:
    """All native terminal names resolve to the canonical member with unchanged value."""
    member = EnumHelpers.convert_enum_and_check(name, enum_type)
    assert member.name == "CLEANED"
    assert EnumHelpers.convert_enum_and_check(member, enum_type) is member


@pytest.mark.parametrize("name", ["CLEANED", "cleaned", "ClEaNeD"])
def test_conduit_resolve_keeps_lowercase_rendering_of_canonical_cleaned(name: str) -> None:
    """Public resolve accepts old and mixed spellings while logs retain lowercase output."""
    state = ConduitState.resolve(name)
    assert state.name == "CLEANED"
    assert state.value == "CLEANED"
    assert ConduitState(4) is state
    assert str(state) == "cleaned"


@pytest.mark.parametrize("value", [None, 4, RecordedUnitState.disabled])
def test_conduit_resolve_still_refuses_unsupported_types_and_foreign_family(value: object) -> None:
    """The name migration must not turn values or foreign families into conduit states."""
    with pytest.raises(ValueError):
        ConduitState.resolve(value)
