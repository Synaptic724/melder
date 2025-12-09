import pytest

from melder.utilities.custom_exceptions.spell_space_scope_error import SpellSpaceScopeError


def test_spell_space_scope_error_is_runtime_error():
    err = SpellSpaceScopeError("scope violation")
    assert isinstance(err, RuntimeError)
    assert "scope violation" in str(err)


def test_spell_space_scope_error_raises():
    with pytest.raises(SpellSpaceScopeError):
        raise SpellSpaceScopeError("no active scope")
