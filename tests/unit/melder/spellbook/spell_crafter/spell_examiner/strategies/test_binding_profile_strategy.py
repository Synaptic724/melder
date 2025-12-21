from melder.spellbook.spell_crafter.spell_examiner.profiles.binding_profile import (
    SpellBindingKind,
    ClassBindingProfile,
    CallableBindingProfile,
    InstanceBindingProfile,
)
from melder.spellbook.spell_crafter.spell_examiner.strategies.binding_profile_strategy import (
    BindingProfileStrategy,
)


class _SampleService:
    """
    Purpose:
        Provide a class candidate for binding profile tests.
    Contract:
        Exposes a callable method to appear in method_names.
    """
    def run(self, value: int) -> int:
        """
        Purpose:
            Provide a simple instance method for inspection.
        Contract:
            Returns the input value.
        Args:
            value: Input value.
        Returns:
            int: The same value passed in.
        """
        return value


def _sample_function(value: int, other: int = 2) -> int:
    """
    Purpose:
        Provide a callable candidate for binding profile tests.
    Contract:
        Returns the sum of value and other.
    Args:
        value: Primary input value.
        other: Optional addend.
    Returns:
        int: Sum of value and other.
    """
    return value + other


def test_binding_profile_strategy_builds_class_profile() -> None:
    """
    Purpose:
        Verify class candidates produce ClassBindingProfile outputs.
    Contract:
        The profile kind is CLASS and includes method names.
    Returns:
        None.
    Raises:
        AssertionError: If class profile fields are missing or incorrect.
    """
    strategy = BindingProfileStrategy()
    profile = strategy.build_profile(_SampleService)

    assert isinstance(profile, ClassBindingProfile)
    assert profile.kind is SpellBindingKind.CLASS
    assert "run" in profile.method_names


def test_binding_profile_strategy_builds_callable_profile() -> None:
    """
    Purpose:
        Verify callable candidates produce CallableBindingProfile outputs.
    Contract:
        The profile kind is CALLABLE and captures a signature string.
    Returns:
        None.
    Raises:
        AssertionError: If callable profile fields are missing or incorrect.
    """
    strategy = BindingProfileStrategy()
    profile = strategy.build_profile(_sample_function)

    assert isinstance(profile, CallableBindingProfile)
    assert profile.kind is SpellBindingKind.CALLABLE
    assert profile.signature is not None
    assert "other=2" in profile.signature


def test_binding_profile_strategy_builds_instance_profile() -> None:
    """
    Purpose:
        Verify instance candidates produce InstanceBindingProfile outputs.
    Contract:
        The profile kind is INSTANCE and reflects the instance type.
    Returns:
        None.
    Raises:
        AssertionError: If instance profile fields are missing or incorrect.
    """
    strategy = BindingProfileStrategy()
    instance = _SampleService()
    profile = strategy.build_profile(instance)

    assert isinstance(profile, InstanceBindingProfile)
    assert profile.kind is SpellBindingKind.INSTANCE
    assert profile.type_name == "_SampleService"
