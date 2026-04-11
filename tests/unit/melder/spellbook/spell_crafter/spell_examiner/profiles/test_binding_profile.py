import pytest

from melder.spellbook.spell_crafter.spell_examiner.profiles.binding_profile import (
    CallableBindingProfile,
    CallableParameterBindingSummary,
    ClassBindingProfile,
    InstanceBindingProfile,
    OtherBindingProfile,
    SpellBindingKind,
    SpellBindingProfile,
)


def test_spell_binding_profile_stores_and_cleans():
    obj = object()
    profile = SpellBindingProfile(SpellBindingKind.CLASS, obj)
    assert profile.kind is SpellBindingKind.CLASS
    assert profile.original_object is obj
    profile.cleanup()
    assert profile.kind is None
    assert profile.original_object is None
    assert profile.cleaned is True
    # idempotent
    profile.cleanup()


def test_class_binding_profile_copies_mutable_inputs_and_cleanup():
    bases = ["Base"]
    mro = ["C", "Base"]
    ann = {"x": int}
    methods = ["f"]
    profile = ClassBindingProfile(
        kind=SpellBindingKind.CLASS,
        original_object=object(),
        name="C",
        qualname="C",
        module="mod",
        bases=bases,
        mro=mro,
        annotations=ann,
        origin_file="file.py",
        origin_line=10,
        source_preview="class C: ...",
        is_dataclass=True,
        decorated=True,
        method_names=methods,
    )

    # copies created
    assert profile.bases == bases and profile.bases is not bases
    assert profile.mro == mro and profile.mro is not mro
    assert profile.annotations == ann and profile.annotations is not ann
    assert profile.method_names == methods and profile.method_names is not methods

    bases.append("Mut")
    ann["x"] = str
    methods.append("g")
    assert profile.bases == ["Base"]
    assert profile.annotations == {"x": int}
    assert profile.method_names == ["f"]

    profile.cleanup()
    assert profile.bases is None
    assert profile.mro is None
    assert profile.annotations is None
    assert profile.method_names is None
    assert profile.name is None
    assert profile.cleaned is True
    profile.cleanup()


def test_callable_parameter_binding_summary_simple_storage():
    summary = CallableParameterBindingSummary(
        name="a", kind="POSITIONAL_ONLY", default_repr="1", annotation_repr="int"
    )
    assert summary.name == "a"
    assert summary.kind == "POSITIONAL_ONLY"
    assert summary.default_repr == "1"
    assert summary.annotation_repr == "int"


def test_callable_binding_profile_copies_parameters_and_cleanup():
    params = [
        CallableParameterBindingSummary("a", "positional", "1", "int"),
        CallableParameterBindingSummary("b", "kw", None, None),
    ]
    profile = CallableBindingProfile(
        kind=SpellBindingKind.CALLABLE,
        original_object=object(),
        name="fn",
        qualname="mod.fn",
        module="mod",
        object_id=123,
        type_name="function",
        repr_string="<fn>",
        signature="(a, b)",
        parameters=params,
        builtin_module=True,
        extension_module=False,
        lambda_function=True,
        abstract=True,
    )

    assert profile.parameters is not params
    assert len(profile.parameters) == 2
    params.clear()
    assert len(profile.parameters) == 2
    assert profile.builtin_module is True
    assert profile.extension_module is False
    assert profile.lambda_function is True
    assert profile.abstract is True

    profile.cleanup()
    assert profile.parameters is None
    assert profile.signature is None
    assert profile.repr_string is None
    assert profile.cleaned is True
    profile.cleanup()


def test_instance_binding_profile_stores_and_cleans():
    profile = InstanceBindingProfile(
        kind=SpellBindingKind.INSTANCE,
        original_object=object(),
        type_name="Service",
        module="pkg.mod",
        repr_string="<Service>",
    )

    assert profile.kind is SpellBindingKind.INSTANCE
    assert profile.type_name == "Service"
    assert profile.module == "pkg.mod"
    assert profile.repr_string == "<Service>"

    profile.cleanup()

    assert profile.type_name is None
    assert profile.module is None
    assert profile.repr_string is None
    assert profile.kind is None
    assert profile.original_object is None
    assert profile.cleaned is True
    profile.cleanup()


def test_other_binding_profile_stores_and_cleans():
    profile = OtherBindingProfile(
        kind=SpellBindingKind.OTHER,
        original_object=object(),
        type_name="OddThing",
        module="pkg.weird",
        repr_string="<OddThing>",
    )

    assert profile.kind is SpellBindingKind.OTHER
    assert profile.type_name == "OddThing"
    assert profile.module == "pkg.weird"
    assert profile.repr_string == "<OddThing>"

    profile.cleanup()

    assert profile.type_name is None
    assert profile.module is None
    assert profile.repr_string is None
    assert profile.kind is None
    assert profile.original_object is None
    assert profile.cleaned is True
    profile.cleanup()
