import pytest

from melder.aether.conduit.conduit_state.conduit_state import ConduitState


def test_conduit_state_str_returns_lowercase_name() -> None:
    """ConduitState stringification should expose lowercase member names."""
    assert str(ConduitState.normal) == "normal"
    assert str(ConduitState.lesser) == "lesser"
    assert str(ConduitState.cleaned) == "cleaned"


def test_conduit_state_resolve_accepts_enum_members() -> None:
    """resolve should return enum members unchanged."""
    assert ConduitState.resolve(ConduitState.normal) is ConduitState.normal
    assert ConduitState.resolve(ConduitState.lesser) is ConduitState.lesser


def test_conduit_state_resolve_accepts_lowercase_strings() -> None:
    """resolve should normalize lowercase string names into enum members."""
    assert ConduitState.resolve("normal") is ConduitState.normal
    assert ConduitState.resolve("lesser") is ConduitState.lesser
    assert ConduitState.resolve("cleaned") is ConduitState.cleaned


def test_conduit_state_resolve_rejects_none() -> None:
    """resolve should reject None explicitly."""
    with pytest.raises(ValueError, match="cannot be None"):
        ConduitState.resolve(None)


def test_conduit_state_resolve_rejects_invalid_values() -> None:
    """resolve should reject unknown string values."""
    with pytest.raises(ValueError, match="Invalid value"):
        ConduitState.resolve("invalid")
