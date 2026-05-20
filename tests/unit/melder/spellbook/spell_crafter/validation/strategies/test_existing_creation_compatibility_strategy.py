import pytest

from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.spell_examiner.profiles.binding_profile import (
    InstanceBindingProfile,
    OtherBindingProfile,
    SpellBindingKind,
)
from melder.aether.spellbook.spell_compiler.spell_examiner.profiles.detailed_profile import (
    SpellDetailedProfile,
)
from melder.aether.spellbook.spell_compiler.spell_examiner.profiles.general_profile import (
    SpellGeneralProfile,
)
from melder.aether.spellbook.spell_compiler.validation.strategies.existing_creation_compatibility_strategy import (
    ExistingCreationCompatibilityStrategy,
)


class _Cancel:
    @property
    def is_set(self):
        return True

    def throw_if_set(self):
        raise RuntimeError("cancelled")


class _Requirements:
    def __init__(self, parameters):
        self.parameters = parameters


class _Spell:
    def __init__(
        self,
        *,
        profile,
        spell_name: str = "existing",
        is_existing_creation: bool = True,
        has_existing_object: bool = True,
        existence=Existence.unique,
    ) -> None:
        self.profile = profile
        self.spell_name = spell_name
        self.is_existing_creation = is_existing_creation
        self.has_existing_object = has_existing_object
        self.existence = existence


class _Context:
    def __init__(self, *, spell, requirements=None, cancel_event=None) -> None:
        self.spell = spell
        self.requirements = requirements
        self.cancel_event = cancel_event
        self.issues = []


def _instance_profile() -> InstanceBindingProfile:
    return InstanceBindingProfile(
        kind=SpellBindingKind.INSTANCE,
        original_object=object(),
        type_name="Service",
        module="tests",
        repr_string="<Service>",
    )


def _other_profile() -> OtherBindingProfile:
    return OtherBindingProfile(
        kind=SpellBindingKind.OTHER,
        original_object=object(),
        type_name="Other",
        module="tests",
        repr_string="<Other>",
    )


def test_existing_creation_compatibility_honors_cancellation() -> None:
    strategy = ExistingCreationCompatibilityStrategy()
    context = _Context(
        spell=_Spell(profile=_instance_profile()),
        cancel_event=_Cancel(),
    )

    with pytest.raises(RuntimeError, match="cancelled"):
        strategy.validate(context)


def test_existing_creation_compatibility_skips_non_existing_creation_spell() -> None:
    strategy = ExistingCreationCompatibilityStrategy()
    context = _Context(
        spell=_Spell(profile=_instance_profile(), is_existing_creation=False),
    )

    strategy.validate(context)

    assert context.issues == []


def test_existing_creation_compatibility_reports_invalid_existence() -> None:
    strategy = ExistingCreationCompatibilityStrategy()
    context = _Context(
        spell=_Spell(
            profile=_instance_profile(),
            existence=Existence.unique_per_conduit,
        ),
    )

    strategy.validate(context)

    assert [issue.code for issue in context.issues] == [
        "EXISTING_CREATION_INVALID_EXISTENCE",
    ]


def test_existing_creation_compatibility_reports_profile_mismatch() -> None:
    strategy = ExistingCreationCompatibilityStrategy()
    bad_profile = SpellGeneralProfile(binding_profile=None)
    context = _Context(spell=_Spell(profile=bad_profile))

    strategy.validate(context)

    assert [issue.code for issue in context.issues] == [
        "EXISTING_CREATION_PROFILE_MISMATCH",
    ]


def test_existing_creation_compatibility_accepts_wrapped_instance_profiles() -> None:
    strategy = ExistingCreationCompatibilityStrategy()
    general = SpellGeneralProfile(binding_profile=_instance_profile())
    detailed = SpellDetailedProfile(binding_profile=_other_profile())

    for profile in (general, detailed):
        context = _Context(spell=_Spell(profile=profile))
        strategy.validate(context)
        assert context.issues == []


def test_existing_creation_compatibility_reports_parameters_present() -> None:
    strategy = ExistingCreationCompatibilityStrategy()
    context = _Context(
        spell=_Spell(profile=_instance_profile()),
        requirements=_Requirements(parameters=[object(), object()]),
    )

    strategy.validate(context)

    assert [issue.code for issue in context.issues] == [
        "EXISTING_CREATION_PARAMETERS_PRESENT",
    ]
    assert context.issues[0].details["parameter_count"] == 2


def test_existing_creation_compatibility_can_emit_multiple_issues() -> None:
    strategy = ExistingCreationCompatibilityStrategy()
    context = _Context(
        spell=_Spell(
            profile=SpellGeneralProfile(binding_profile=None),
            has_existing_object=False,
            existence=Existence.unique_per_conduit,
        ),
        requirements=_Requirements(parameters=[object()]),
    )

    strategy.validate(context)

    assert [issue.code for issue in context.issues] == [
        "EXISTING_CREATION_MISSING_INSTANCE",
        "EXISTING_CREATION_INVALID_EXISTENCE",
        "EXISTING_CREATION_PROFILE_MISMATCH",
        "EXISTING_CREATION_PARAMETERS_PRESENT",
    ]
