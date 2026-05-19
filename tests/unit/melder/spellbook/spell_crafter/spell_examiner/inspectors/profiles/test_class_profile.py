from melder.aether.spellbook.spell_crafter.spell_examiner.inspectors.profiles.class_profile import (
    ClassProfile,
)
from melder.aether.spellbook.spell_crafter.spell_examiner.inspectors.profiles.method_profile import (
    MethodProfile,
)
from melder.utilities.general_base.cleanable import Cleanable


def _method_profile(**overrides):
    base = dict(
        name="m",
        qualname="Q.m",
        module="mod",
        id=1,
        type="function",
        repr="<fn m>",
        builtin_mod=False,
        extension_mod=False,
        file="file.py",
        preview="def m(): pass",
        src_offset=10,
        signature="()",
        parameters=[{"name": "x"}],
        uninspectable=False,
        func=True,
        method=False,
        builtin=False,
        classmethod=False,
        staticmethod=False,
        generator=False,
        async_gen=False,
        coroutine=False,
        lambda_fn=False,
        abstract=False,
        closure=["y"],
        decorated=False,
        wrapped_repr=None,
    )
    base.update(overrides)
    return MethodProfile(**base)


def _class_profile(**overrides):
    base = dict(
        name="C",
        qualname="pkg.C",
        module="pkg",
        mro=["C", "object"],
        bases=["object"],
        annotations={"a": int},
        protocols={"call": True},
        slots=["a", "b"],
        origin_file="file.py",
        origin_line=5,
        source_preview="class C: ...",
        members={"a": {"kind": "data"}},
        methods={"m": _method_profile()},
        is_dataclass=False,
        decorated=True,
    )
    base.update(overrides)
    return ClassProfile(**base)


def test_init_copies_mutable_inputs():
    mro = ["A"]
    bases = ["Base"]
    annotations = {"x": 1}
    protocols = {"p": False}
    slots = ["s"]
    members = {"a": {"kind": "data"}}
    meth = _method_profile()
    methods = {"m": meth}

    profile = ClassProfile(
        name="C",
        qualname="C",
        module="mod",
        mro=mro,
        bases=bases,
        annotations=annotations,
        protocols=protocols,
        slots=slots,
        members=members,
        methods=methods,
    )

    # copies are made
    assert profile.mro is not mro and profile.mro == mro
    assert profile.bases is not bases and profile.bases == bases
    assert profile.annotations is not annotations and profile.annotations == annotations
    assert profile.protocols is not protocols and profile.protocols == protocols
    assert profile.members is not members and profile.members == members
    assert profile.methods is not methods and profile.methods == methods
    assert profile.methods["m"] is meth  # values preserved

    # altering original does not mutate profile
    mro.append("Mutated")
    annotations["x"] = 2
    members["a"]["mut"] = True
    assert profile.mro == ["A"]
    assert profile.annotations == {"x": 1}
    # shallow copy for member values is acceptable; only top-level mapping is copied
    assert profile.members["a"]["mut"] is True


def test_defaults_for_optional_fields():
    profile = ClassProfile(name="C", qualname="C", module="mod")
    assert profile.mro == []
    assert profile.bases == []
    assert profile.annotations == {}
    assert profile.protocols == {}
    assert profile.slots is None
    assert profile.origin_file is None
    assert profile.origin_line is None
    assert profile.origin_end_line is None
    assert profile.source_preview is None
    assert profile.source_text is None
    assert profile.members == {}
    assert profile.methods == {}
    assert profile.is_dataclass is False
    assert profile.decorated is False
    assert profile.docstring_raw is None
    assert profile.docstring_summary == ""
    assert profile.behavior_summary == ""
    assert profile.tags == []
    assert profile.dynamic_access == {}


def test_cleanup_cleans_nested_methods_and_collections():
    method = _method_profile()
    profile = _class_profile(methods={"m": method})

    profile.cleanup()

    assert method.cleaned is True
    assert not hasattr(profile, 'members')
    assert not hasattr(profile, 'methods')
    assert not hasattr(profile, 'mro')
    assert not hasattr(profile, 'bases')
    assert not hasattr(profile, 'annotations')
    assert not hasattr(profile, 'protocols')
    assert not hasattr(profile, 'slots')
    assert not hasattr(profile, 'origin_file')
    assert not hasattr(profile, 'origin_line')
    assert not hasattr(profile, 'origin_end_line')
    assert not hasattr(profile, 'source_preview')
    assert not hasattr(profile, 'source_text')
    assert not hasattr(profile, 'name')
    assert not hasattr(profile, 'docstring_raw')
    assert not hasattr(profile, 'docstring_summary')
    assert not hasattr(profile, 'behavior_summary')
    assert not hasattr(profile, 'tags')
    assert not hasattr(profile, 'dynamic_access')
    assert profile.cleaned is True

    # idempotent
    profile.cleanup()
    assert profile.cleaned is True


def test_cleanup_swallow_exceptions_from_nested_methods():
    class Exploding(Cleanable):
        def __init__(self):
            super().__init__()
            self.cleaned_called = False

        def cleanup(self):
            self.cleaned_called = True
            self._cleaned = True
            raise RuntimeError("boom")

    bad = Exploding()
    profile = _class_profile(methods={"bad": bad})
    profile.cleanup()  # should not raise

    assert bad.cleaned_called is True
    assert profile.cleaned is True


def test_slots_list_is_cleared_then_nulled_on_cleanup():
    profile = _class_profile(slots=["a", "b"])
    profile.cleanup()
    assert not hasattr(profile, 'slots')


def test_methods_and_members_can_be_none():
    profile = _class_profile(members=None, methods=None)
    assert profile.members == {}
    assert profile.methods == {}


def test_flags_and_provenance_preserved():
    profile = _class_profile(is_dataclass=True, decorated=False, origin_line=7)
    assert profile.is_dataclass is True
    assert profile.decorated is False
    assert profile.origin_line == 7


def test_decorated_and_dataclass_flags_clear_on_cleanup():
    profile = _class_profile(is_dataclass=True, decorated=True)
    profile.cleanup()
    assert not hasattr(profile, 'is_dataclass')
    assert not hasattr(profile, 'decorated')


def test_methods_dict_shallow_copy_only():
    meth = _method_profile()
    profile = _class_profile(methods={"m": meth})
    assert profile.methods["m"] is meth


def test_cleanup_sets_collections_to_none_even_if_empty():
    profile = _class_profile(mro=[], bases=[], annotations={}, protocols={}, members={}, methods={})
    profile.cleanup()
    assert not hasattr(profile, 'mro')
    assert not hasattr(profile, 'annotations')


def test_cleanup_does_not_reclean_already_cleaned_method_profiles():
    method = _method_profile()
    method.cleanup()
    profile = _class_profile(methods={"m": method})
    profile.cleanup()
    assert method.cleaned is True
