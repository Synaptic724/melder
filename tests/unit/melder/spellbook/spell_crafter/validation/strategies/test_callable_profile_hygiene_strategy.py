import pytest

from melder.spellbook.spell_crafter.spell_examiner.profiles.binding_profile import (
    CallableBindingProfile,
    ClassBindingProfile,
    InstanceBindingProfile,
    OtherBindingProfile,
    SpellBindingKind,
)
from melder.spellbook.spell_crafter.spell_examiner.profiles.detailed_profile import (
    SpellDetailedProfile,
)
from melder.spellbook.spell_crafter.spell_examiner.profiles.general_profile import (
    SpellGeneralProfile,
)
from melder.spellbook.spell_crafter.validation.strategies.callable_profile_hygiene_strategy import (
    CallableProfileHygieneStrategy,
)


class _Cancel:
    @property
    def is_set(self):
        return True

    def throw_if_set(self):
        raise RuntimeError("cancelled")


class _Spell:
    def __init__(
        self,
        *,
        profile,
        spell,
        spell_name: str = "spell",
        is_existing_creation: bool = False,
        has_existing_object: bool = False,
        is_class_spell: bool = False,
        is_method_spell: bool = False,
        is_lambda_spell: bool = False,
    ) -> None:
        self.profile = profile
        self.spell = spell
        self.spell_name = spell_name
        self.is_existing_creation = is_existing_creation
        self.has_existing_object = has_existing_object
        self.is_class_spell = is_class_spell
        self.is_method_spell = is_method_spell
        self.is_lambda_spell = is_lambda_spell


class _Context:
    def __init__(self, *, spell, cancel_event=None) -> None:
        self.spell = spell
        self.cancel_event = cancel_event
        self.issues = []


def _class_profile() -> ClassBindingProfile:
    return ClassBindingProfile(
        kind=SpellBindingKind.CLASS,
        original_object=object(),
        name="Svc",
        qualname="Svc",
        module="tests",
    )


def _callable_profile() -> CallableBindingProfile:
    return CallableBindingProfile(
        kind=SpellBindingKind.CALLABLE,
        original_object=lambda: None,
        name="build",
        qualname="build",
        module="tests",
        object_id=1,
        type_name="function",
        repr_string="<function build>",
        signature="()",
    )


def _instance_profile() -> InstanceBindingProfile:
    return InstanceBindingProfile(
        kind=SpellBindingKind.INSTANCE,
        original_object=object(),
        type_name="Service",
        module="tests",
        repr_string="<Service instance>",
    )


def _other_profile() -> OtherBindingProfile:
    return OtherBindingProfile(
        kind=SpellBindingKind.OTHER,
        original_object=object(),
        type_name="Other",
        module="tests",
        repr_string="<Other>",
    )


def test_callable_profile_hygiene_honors_cancellation() -> None:
    strategy = CallableProfileHygieneStrategy()
    context = _Context(
        spell=_Spell(profile=None, spell=object()),
        cancel_event=_Cancel(),
    )

    with pytest.raises(RuntimeError, match="cancelled"):
        strategy.validate(context)


def test_callable_profile_hygiene_existing_creation_reports_missing_instance_and_profile_mismatch() -> None:
    strategy = CallableProfileHygieneStrategy()
    context = _Context(
        spell=_Spell(
            profile=_class_profile(),
            spell=object(),
            spell_name="existing",
            is_existing_creation=True,
            has_existing_object=False,
        )
    )

    strategy.validate(context)

    assert [issue.code for issue in context.issues] == [
        "EXISTING_CREATION_MISSING_INSTANCE",
        "EXISTING_CREATION_PROFILE_MISMATCH",
    ]


@pytest.mark.parametrize("profile_factory", [_instance_profile, _other_profile])
def test_callable_profile_hygiene_existing_creation_accepts_instanceish_profiles(profile_factory) -> None:
    strategy = CallableProfileHygieneStrategy()
    wrapped_profile = SpellGeneralProfile(binding_profile=profile_factory())
    context = _Context(
        spell=_Spell(
            profile=wrapped_profile,
            spell=object(),
            spell_name="existing",
            is_existing_creation=True,
            has_existing_object=True,
        )
    )

    strategy.validate(context)

    assert context.issues == []


def test_callable_profile_hygiene_class_spell_reports_target_and_profile_mismatch() -> None:
    strategy = CallableProfileHygieneStrategy()
    context = _Context(
        spell=_Spell(
            profile=_callable_profile(),
            spell=object(),
            spell_name="classy",
            is_class_spell=True,
        )
    )

    strategy.validate(context)

    assert [issue.code for issue in context.issues] == [
        "NON_CLASS_SPELL_TARGET",
        "CLASS_PROFILE_MISSING",
    ]


def test_callable_profile_hygiene_class_spell_accepts_real_class_with_wrapped_profile() -> None:
    strategy = CallableProfileHygieneStrategy()

    class _Service:
        pass

    wrapped_profile = SpellGeneralProfile(binding_profile=_class_profile())
    context = _Context(
        spell=_Spell(
            profile=wrapped_profile,
            spell=_Service,
            spell_name="classy",
            is_class_spell=True,
        )
    )

    strategy.validate(context)

    assert context.issues == []


def test_callable_profile_hygiene_callable_spell_reports_target_and_profile_mismatch() -> None:
    strategy = CallableProfileHygieneStrategy()
    context = _Context(
        spell=_Spell(
            profile=_class_profile(),
            spell=object(),
            spell_name="cally",
            is_method_spell=True,
        )
    )

    strategy.validate(context)

    assert [issue.code for issue in context.issues] == [
        "NON_CALLABLE_SPELL_TARGET",
        "CALLABLE_PROFILE_MISSING",
    ]


def test_callable_profile_hygiene_callable_spell_accepts_wrapped_detailed_profile() -> None:
    strategy = CallableProfileHygieneStrategy()
    wrapped_profile = SpellDetailedProfile(binding_profile=_callable_profile())
    context = _Context(
        spell=_Spell(
            profile=wrapped_profile,
            spell=lambda: None,
            spell_name="cally",
            is_lambda_spell=True,
        )
    )

    strategy.validate(context)

    assert context.issues == []
