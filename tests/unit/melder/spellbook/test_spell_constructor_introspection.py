"""Keep Spell constructor reflection usable by early Python 3.14 mock specifications."""

import inspect
from collections.abc import Callable
from typing import Optional
from unittest.mock import MagicMock, Mock

import pytest

from melder.aether.spellbook.existence.managed_spell_mode import ManagedSpellMode
from melder.aether.spellbook.spell import Spell


@pytest.mark.parametrize("target", [Spell, Spell.__init__], ids=["class", "constructor"])
def test_spell_constructor_signature_resolves_managed_mode(
        target: Callable[..., object],
) -> None:
    """
    Read the managed-mode option without evaluating an unavailable annotation name.

    Contract:
        Default VALUE-format reflection keeps the concrete optional enum, its None
        default and keyword-only calling convention on the class and constructor.
    """
    signature = inspect.signature(target)
    parameter = signature.parameters["managed_spell_mode"]

    assert parameter.annotation == Optional[ManagedSpellMode]
    assert parameter.default is None
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
    assert signature.bind_partial(managed_spell_mode=ManagedSpellMode.queue).arguments == {
        "managed_spell_mode": ManagedSpellMode.queue,
    }


@pytest.mark.parametrize("mock_type", [Mock, MagicMock], ids=["mock", "magic-mock"])
def test_spell_mock_spec_retains_method_calls_and_rejects_unknown_members(
        mock_type: type[Mock],
) -> None:
    """
    Build the real Spell specification used by ward and state-registry fixtures.

    Contract:
        The mock records a declared method call and refuses an undeclared member.
        Python 3.14.0-3.14.3 reads the constructor's VALUE annotations at creation.
    """
    spell = mock_type(spec=Spell)

    spell.cleanup()

    spell.cleanup.assert_called_once_with()
    with pytest.raises(AttributeError):
        spell.undefined_spell_member()
