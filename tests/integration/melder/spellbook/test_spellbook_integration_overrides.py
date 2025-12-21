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


def test_meld_overrides_path_targets_root_params() -> None:
    """
    Purpose:
        Validate path overrides target root constructor parameters.
    Contract:
        - spell_override path keys map onto root constructor parameters.
        - Instance fields reflect the provided override values.
    Returns:
        None.
    Raises:
        AssertionError: If override values are not applied.
    """
    class _Service:
        """
        Purpose:
            Provide a class spell with explicit constructor parameters.
        Contract:
            Stores constructor arguments for assertions.
        """
        def __init__(self, value: int, label: str) -> None:
            """
            Purpose:
                Capture constructor arguments for assertions.
            Contract:
                Stores value and label on the instance.
            Args:
                value: Numeric value passed to the constructor.
                label: String label passed to the constructor.
            Returns:
                None.
            """
            self.value = value
            self.label = label

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spell_id = spellbook.bind(
        spell=_Service,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(
            spell=spell_id,
            spell_override={"value": 7, "label": "dict"},
        )
        assert instance.value == 7
        assert instance.label == "dict"
    finally:
        conduit.cleanup()


def test_meld_overrides_unique_targets_dependency() -> None:
    """
    Purpose:
        Validate unique overrides target a dependency socket by name.
    Contract:
        - spell_override uses "*param" to target a single dependency.
        - Instance receives the overridden dependency object.
    Returns:
        None.
    Raises:
        AssertionError: If positional overrides are not applied.
    """
    class _Dependency:
        """
        Purpose:
            Provide a dependency spell that can be overridden.
        Contract:
            Stores the supplied label for assertions.
        """
        def __init__(self, label: str) -> None:
            """
            Purpose:
                Capture a label for assertions.
            Contract:
                Stores the label on the instance.
            Args:
                label: Label assigned to the dependency.
            Returns:
                None.
            """
            self.label = label

    class _Service:
        """
        Purpose:
            Provide a class spell that depends on a single dependency.
        Contract:
            Stores the dependency instance for assertions.
        """
        def __init__(self, dep: _Dependency) -> None:
            """
            Purpose:
                Capture the dependency for assertions.
            Contract:
                Stores the dependency on the instance.
            Args:
                dep: Dependency resolved by the DI system.
            Returns:
                None.
            """
            self.dep = dep

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_Dependency,
        existence=Existence.many,
        permissions="create",
    )
    spell_id = spellbook.bind(
        spell=_Service,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        override_dep = _Dependency(label="override")
        instance = conduit.meld(
            spell=spell_id,
            spell_override={"*dep": override_dep},
        )
        assert instance.dep is override_dep
    finally:
        conduit.cleanup()
