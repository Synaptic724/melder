from __future__ import annotations

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_integration() -> None:
    """
    Purpose:
        Ensure integration tests start with a clean Aether singleton.
    Contract:
        - Resets the Aether singleton before the test runs.
        - Rebinds Spellbook._aether and Conduit._aether to the new instance.
        - Resets the singleton again after the test for isolation.
    Returns:
        None.
    """
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def test_meld_by_spell_name_string_resolves_default_binding() -> None:
    """
    Purpose:
        Validate Conduit.meld resolves a spell by its logical spell_name string.
    Contract:
        - A spell_name lookup resolves the default binding when no binding_name is provided.
    Returns:
        None.
    Raises:
        AssertionError: If the resolved instance is incorrect.
    """
    class _Service:
        """
        Purpose:
            Provide a class spell for spell_name resolution.
        Contract:
            Stores a stable marker for assertions.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the marker for spell_name resolution.
            Contract:
                Sets marker to "by-name".
            Returns:
                None.
            """
            self.marker = "by-name"

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_Service,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell_name=_Service.__name__)
        assert isinstance(instance, _Service)
        assert instance.marker == "by-name"
    finally:
        conduit.cleanup()


def test_meld_by_spell_name_with_binding_name_resolves_named_binding() -> None:
    """
    Purpose:
        Validate spell_name resolution honors an explicit binding_name.
    Contract:
        - A non-default binding can be resolved via spell_name + binding_name.
        - binding_name normalization is case-insensitive for resolution.
    Returns:
        None.
    Raises:
        AssertionError: If the binding-specific spell does not resolve.
    """
    class _Service:
        """
        Purpose:
            Provide a class spell bound under a named binding.
        Contract:
            Stores a stable marker for binding-specific assertions.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the binding-specific marker.
            Contract:
                Sets marker to "named".
            Returns:
                None.
            """
            self.marker = "named"

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_Service,
        existence=Existence.unique,
        permissions="create",
        binding_name="primary",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell_name=_Service.__name__, binding_name="PRIMARY")
        assert isinstance(instance, _Service)
        assert instance.marker == "named"
    finally:
        conduit.cleanup()


def test_meld_by_spell_name_string_is_case_insensitive() -> None:
    """
    Purpose:
        Validate spell_name resolution is case-insensitive.
    Contract:
        - Normalized spell_name strings resolve regardless of case.
    Returns:
        None.
    Raises:
        AssertionError: If the case-insensitive lookup fails.
    """
    class _Service:
        """
        Purpose:
            Provide a class spell for case-insensitive name resolution.
        Contract:
            Stores a stable marker for assertions.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the case-insensitive marker.
            Contract:
                Sets marker to "case".
            Returns:
                None.
            """
            self.marker = "case"

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_Service,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        spell_name = _Service.__name__
        instance = conduit.meld(spell_name=spell_name.swapcase())
        assert isinstance(instance, _Service)
        assert instance.marker == "case"
    finally:
        conduit.cleanup()


def test_meld_by_spell_name_missing_raises_key_error() -> None:
    """
    Purpose:
        Validate spell_name lookups fail clearly when no spell is registered.
    Contract:
        - A missing spell_name raises KeyError from the resolution pipeline.
    Returns:
        None.
    Raises:
        AssertionError: If the KeyError is not raised or does not match.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    conduit = spellbook.conjure(name="root")
    try:
        with pytest.raises(
            KeyError,
            match=r"No spell found for frame='.*', binding='__default__'",
        ):
            conduit.meld(spell_name="MissingService")
    finally:
        conduit.cleanup()
