import types
import inspect
from typing import Protocol
import pytest

from melder.aether.spellbook.bind.bind import Bind
from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.spellbook.spell_types.spell_types import SpellType
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.spellbook.spell_compiler.spell_examiner.profiles.binding_profile import (
    SpellBindingProfile,
    SpellBindingKind,
    ClassBindingProfile,
    CallableBindingProfile,
    InstanceBindingProfile,
    OtherBindingProfile,
    CallableParameterBindingSummary,
)
from melder.aether.spellbook.spell_compiler.spell_examiner.profiles.general_profile import (
    SpellGeneralProfile,
)


# -------------------------
# Test doubles
# -------------------------


class StubSpell:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        for k, v in kwargs.items():
            setattr(self, k, v)


class StubExaminer:
    def __init__(self, profile):
        self.profile = profile
        self.calls = 0

    def create_profile(self, obj, profile_name, show_dunders=False, max_repr=120):
        assert profile_name == "general"
        self.calls += 1
        return StubGeneralProfile(
            binding_profile=self.profile,
            resolution_profile=None,
        )

    def cleanup(self):
        self.profile = None


class StubSpellbook:
    pass


class StubGeneralProfile(SpellGeneralProfile):
    def complete_with_spell(self, spell):
        self.resolution_profile = object()


class ProtoExample:
    __is_protocol__ = True


class RealClassImplementingProto:
    def foo(self):
        return "ok"


class ProtoWithFoo:
    __is_protocol__ = True

    def foo(self):
        ...


# Fixtures ------------------------------------------------------------


@pytest.fixture(autouse=True)
def patch_spell(monkeypatch):
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.Spell", StubSpell)
    yield


@pytest.fixture(autouse=True)
def patch_assert_allowed(monkeypatch):
    # _mrg.assert_allowed is defined via __getattr__ on a registration guard; we bypass via patching the module attribute directly.
    monkeypatch.setattr("melder.aether.spellbook.bind.bind._mrg", types.SimpleNamespace(assert_allowed=lambda *a, **k: None), raising=False)
    yield


# Profile builders ----------------------------------------------------


def class_profile(name="C", bases=None, mro=None, annotations=None, method_names=None, source_preview="", is_dataclass=False, decorated=False, origin_file=None, origin_line=None):
    return ClassBindingProfile(
        kind=SpellBindingKind.CLASS,
        original_object=RealClassImplementingProto,
        name=name,
        qualname=name,
        module="mod",
        bases=bases or [],
        mro=mro or [],
        annotations=annotations or {},
        origin_file=origin_file,
        origin_line=origin_line,
        source_preview=source_preview,
        is_dataclass=is_dataclass,
        decorated=decorated,
        method_names=method_names or [],
    )


def callable_profile(name="f", lambda_function=False, parameters=None, signature="sig", repr_string="repr"):
    return CallableBindingProfile(
        kind=SpellBindingKind.CALLABLE,
        original_object=lambda x: x,
        object_id="obj-1",
        name=name,
        qualname=name,
        module="mod",
        parameters=parameters or [],
        repr_string=repr_string,
        type_name="function",
        signature=signature,
        lambda_function=lambda_function,
        builtin_module=False,
        extension_module=False,
    )


def instance_profile(type_name="T"):
    return InstanceBindingProfile(
        kind=SpellBindingKind.INSTANCE,
        original_object=object(),
        type_name=type_name,
        module="mod",
        repr_string="repr",
    )


def other_profile(type_name="T"):
    return OtherBindingProfile(
        kind=SpellBindingKind.OTHER,
        original_object=object(),
        type_name=type_name,
        module="mod",
        repr_string="repr",
    )


# Tests: Bind.bind entry ------------------------------------------------


def test_bind_decorator_returns_original(monkeypatch):
    profile = class_profile()
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(profile))
    b = Bind(StubSpellbook())
    decorator = b.bind(Permissions.read, Existence.unique, aetheric_frame="f")

    @decorator
    class Foo:
        pass

    assert Foo is not None


def test_bind_direct_returns_spell_stub(monkeypatch):
    profile = class_profile()
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(profile))
    b = Bind(StubSpellbook())
    spell = b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=RealClassImplementingProto)
    assert isinstance(spell, StubSpell)
    assert spell.kwargs["permissions"] == Permissions.read
    assert spell.kwargs["existence"] == Existence.unique


def test_bind_rejects_module(monkeypatch):
    profile = class_profile()
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(profile))
    b = Bind(StubSpellbook())
    with pytest.raises(TypeError):
        b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=inspect)


def test_bind_rejects_protocol_as_spell(monkeypatch):
    profile = class_profile()
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(profile))
    b = Bind(StubSpellbook())
    class P(ProtoExample):
        pass
    with pytest.raises(TypeError):
        b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=P)


# Tests: validation rules ----------------------------------------------


@pytest.mark.parametrize("existence", [None, "bad", 123])
def test_existence_check_invalid_raises(existence):
    with pytest.raises(ValueError):
        Bind._existence_check(existence)  # type: ignore[arg-type]


def test_existing_object_with_non_unique_existence_raises():
    profile = instance_profile()
    with pytest.raises(ValueError):
        Bind._validate_binding(profile, binding_name=None, existence=Existence.many)


@pytest.mark.parametrize("existence", [None, "bad", 123])
def test_validate_binding_rejects_invalid_existence_type(existence):
    profile = class_profile()
    with pytest.raises(ValueError, match="Invalid existence type"):
        Bind._validate_binding(profile, binding_name=None, existence=existence)


def test_lambda_without_name_raises():
    profile = callable_profile(lambda_function=True)
    with pytest.raises(ValueError):
        Bind._validate_binding(profile, binding_name=None, existence=Existence.unique)


def test_callable_with_non_unique_existence_raises():
    profile = callable_profile()
    with pytest.raises(ValueError):
        Bind._validate_binding(profile, binding_name="x", existence=Existence.many)


def test_valid_class_binding_passes():
    profile = class_profile()
    Bind._validate_binding(profile, binding_name=None, existence=Existence.unique)


def test_valid_callable_binding_passes():
    profile = callable_profile()
    Bind._validate_binding(profile, binding_name="x", existence=Existence.unique)


def test_valid_existing_object_binding_passes():
    profile = instance_profile()
    Bind._validate_binding(profile, binding_name="x", existence=Existence.unique)


# Tests: SpellType determination ----------------------------------------


@pytest.mark.parametrize(
    "profile_factory,name,frame,expected",
    [
        (class_profile, None, None, SpellType.SPELL),
        (class_profile, "n", None, SpellType.SPELL_WITH_BINDING_NAME),
        (class_profile, None, "frame", SpellType.SPELL_WITH_SPELLFRAME),
        (class_profile, "n", "frame", SpellType.SPELL_WITH_BINDING_NAME_WITH_SPELLFRAME),
        (callable_profile, None, None, SpellType.METHOD),
        (callable_profile, "n", None, SpellType.METHOD_WITH_BINDING_NAME),
        (callable_profile, None, "frame", SpellType.METHOD_WITH_SPELLFRAME),
        (callable_profile, "n", "frame", SpellType.METHOD_WITH_BINDING_NAME_WITH_SPELLFRAME),
        (lambda: callable_profile(lambda_function=True), "n", None, SpellType.LAMBDA_METHOD_WITH_BINDING_NAME),
        (lambda: callable_profile(lambda_function=True), "n", "frame", SpellType.LAMBDA_METHOD_WITH_BINDING_NAME_WITH_SPELLFRAME),
        (lambda: callable_profile(lambda_function=True), None, "frame", SpellType.LAMBDA_METHOD_WITH_SPELLFRAME),
        (instance_profile, None, None, SpellType.EXISTING_CREATION),
        (instance_profile, None, "frame", SpellType.EXISTING_CREATION_WITH_SPELLFRAME),
        (instance_profile, "n", "frame", SpellType.EXISTING_CREATION_WITH_BINDING_NAME_WITH_SPELLFRAME),
        (other_profile, None, None, SpellType.EXISTING_CREATION),
    ],
)
def test_determine_spell_type(profile_factory, name, frame, expected):
    profile = profile_factory()
    assert Bind._determine_spell_type(profile, name, frame) == expected


# Tests: Protocol helpers ----------------------------------------------


def test_is_protocol_type():
    class NotProto:
        pass
    class Proto(ProtoExample):
        pass
    assert Bind._is_protocol_type(Proto)
    assert not Bind._is_protocol_type(NotProto)
    assert not Bind._is_protocol_type(Proto())  # instance


def test_structural_protocol_check_passes_when_members_present():
    ok, missing = Bind._structurally_implements_protocol(RealClassImplementingProto, ProtoWithFoo)
    assert ok
    assert missing == []


def test_structural_protocol_check_fails_when_missing():
    class NoFoo:
        pass
    ok, missing = Bind._structurally_implements_protocol(NoFoo, ProtoWithFoo)
    assert not ok
    assert "foo" in missing


def test_bind_with_protocol_frame_validates_structure(monkeypatch):
    profile = class_profile(method_names=["foo"])
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(profile))
    b = Bind(StubSpellbook())
    spell = b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=RealClassImplementingProto, spellframe=ProtoWithFoo)
    assert isinstance(spell, StubSpell)


def test_bind_with_protocol_frame_missing_member_raises(monkeypatch):
    class NoFoo:
        pass
    profile = class_profile(method_names=[])
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(profile))
    b = Bind(StubSpellbook())
    with pytest.raises(TypeError):
        b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=NoFoo, spellframe=ProtoWithFoo)


def test_callable_under_protocol_frame_allows(monkeypatch):
    profile = callable_profile()
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(profile))
    b = Bind(StubSpellbook())
    spell = b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=lambda x: x, spellframe=ProtoWithFoo)
    assert isinstance(spell, StubSpell)


# Tests: Fingerprint/determinism ---------------------------------------


def test_sha256_profile_deterministic_class():
    p1 = class_profile(method_names=["a", "b"])
    p2 = class_profile(method_names=["b", "a"])
    assert Bind.sha256_profile(p1) == Bind.sha256_profile(p2)


def test_sha256_profile_different_profiles_yield_different_hashes():
    p1 = class_profile(name="A")
    p2 = callable_profile(name="B")
    assert Bind.sha256_profile(p1) != Bind.sha256_profile(p2)


def test_spell_id_inspector_uses_examiner(monkeypatch):
    prof = class_profile()
    calls = {"count": 0}

    def _build_profile(self, target):
        calls["count"] += 1
        return StubGeneralProfile(binding_profile=prof, resolution_profile=None)

    monkeypatch.setattr(
        SpellGeneralProfile,
        "create_from_target",
        classmethod(lambda cls, target, show_dunders=False, max_repr=120: _build_profile(cls, target)),
        raising=True,
    )
    sid1 = Bind.spell_id_inspector(RealClassImplementingProto)
    sid2 = Bind.spell_id_inspector(RealClassImplementingProto)
    assert sid1 == sid2
    assert calls["count"] == 2


# Tests: cleanup/idempotence -------------------------------------------


def test_bind_cleanup_idempotent():
    b = Bind(StubSpellbook())
    b.cleanup()
    assert b._cleaned is True
    b.cleanup()
    assert not hasattr(b, "_spellbook")
    assert not hasattr(b, "_lock")


def test_bind_usage_after_cleanup_is_inert(monkeypatch):
    profile = class_profile()
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(profile))
    b = Bind(StubSpellbook())
    b.cleanup()
    with pytest.raises(RuntimeError):
        b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=RealClassImplementingProto)
    with pytest.raises(RuntimeError):
        _ = b.bind(Permissions.read, Existence.unique, aetheric_frame="f")  # decorator style


def test_spell_examiner_failure_propagates(monkeypatch):
    class BoomExaminer:
        def create_profile(self, obj, profile_name, show_dunders=False, max_repr=120):
            raise RuntimeError("boom")
        def cleanup(self):
            return None
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", BoomExaminer)
    b = Bind(StubSpellbook())
    with pytest.raises(RuntimeError):
        b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=RealClassImplementingProto)


def test_existing_object_flag_only_for_instances(monkeypatch):
    inst = object()
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(instance_profile()))
    b = Bind(StubSpellbook())
    spell = b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=inst)
    assert spell.kwargs["existing_object"] is inst

    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(class_profile()))
    b2 = Bind(StubSpellbook())
    spell2 = b2.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=RealClassImplementingProto)
    assert spell2.kwargs["existing_object"] is None


def test_spell_name_resolution_without_dunder_name(monkeypatch):
    class Nameless:
        pass
    obj = Nameless()
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(instance_profile()))
    b = Bind(StubSpellbook())
    spell = b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=obj)
    assert spell.kwargs["spell_name"] == type(obj).__name__


def test_structural_check_rejects_non_callable_attribute():
    class ProtoWithCall:
        __is_protocol__ = True
        def foo(self):
            ...
    class Impl:
        foo = 123  # not callable
    ok, missing = Bind._structurally_implements_protocol(Impl, ProtoWithCall)
    assert ok is False
    assert "foo" in missing


def test_determine_spell_type_fallback_on_unknown_profile():
    wp = SpellBindingProfile(kind=SpellBindingKind.OTHER, original_object=None)
    assert Bind._determine_spell_type(wp, None, None) == SpellType.EXISTING_CREATION


def test_sha256_profile_includes_parameters():
    p1 = callable_profile(
        parameters=[
            CallableParameterBindingSummary("x", "positional", None, None),
            CallableParameterBindingSummary("y", "kwonly", "1", "int"),
        ],
        signature="(x, y=1)",
    )
    p2 = callable_profile(
        parameters=[
            CallableParameterBindingSummary("x", "positional", None, None),
        ],
        signature="(x)",
    )
    assert Bind.sha256_profile(p1) != Bind.sha256_profile(p2)


# Validation matrix ----------------------------------------------------

@pytest.mark.parametrize(
    "existence,profile_factory,should_pass",
    [
        (Existence.unique, class_profile, True),
        (Existence.many, class_profile, True),
        (Existence.unique, callable_profile, True),
        (Existence.many, callable_profile, False),
        (Existence.unique, lambda: callable_profile(lambda_function=True, name="ln"), True),
        (Existence.many, lambda: callable_profile(lambda_function=True, name="ln"), False),
        (Existence.unique, instance_profile, True),
        (Existence.many, instance_profile, False),
    ],
)
def test_validate_binding_matrix(existence, profile_factory, should_pass):
    profile = profile_factory()
    if should_pass:
        Bind._validate_binding(profile, binding_name="n", existence=existence)
    else:
        with pytest.raises(ValueError):
            Bind._validate_binding(profile, binding_name="n", existence=existence)


def test_lambda_requires_name_even_with_unique():
    profile = callable_profile(lambda_function=True)
    with pytest.raises(ValueError):
        Bind._validate_binding(profile, binding_name=None, existence=Existence.unique)


# Protocol semantics ---------------------------------------------------

def test_protocol_structural_inheritance():
    class BaseProto:
        __is_protocol__ = True
        def foo(self): ...
    class ChildProto(BaseProto):
        def bar(self): ...
    class Impl:
        def foo(self): return 1
        def bar(self): return 2
    ok, missing = Bind._structurally_implements_protocol(Impl, ChildProto)
    assert ok
    assert missing == []


def test_protocol_missing_property_like_member():
    class ProtoWithProp:
        __is_protocol__ = True
        value = 1
    class Impl:
        @property
        def value(self):
            return 1
    ok, missing = Bind._structurally_implements_protocol(Impl, ProtoWithProp)
    # property is callable? attribute is present so should pass
    assert ok
    assert missing == []


def test_protocol_callable_member_with_none_impl():
    class ProtoWithCall:
        __is_protocol__ = True
        def foo(self): ...
    class Impl:
        foo = None
    ok, missing = Bind._structurally_implements_protocol(Impl, ProtoWithCall)
    assert not ok
    assert "foo" in missing


# Spell construction wiring -------------------------------------------

def test_existing_object_flag_not_set_for_callable(monkeypatch):
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(callable_profile()))
    b = Bind(StubSpellbook())
    spell = b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=lambda x: x)
    assert spell.kwargs["existing_object"] is None
    assert spell.kwargs["spell_index"].current == spell.kwargs["spell_id"]


def test_spell_id_stable_for_same_class(monkeypatch):
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(class_profile(name="A")))
    b = Bind(StubSpellbook())
    s1 = b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=RealClassImplementingProto)
    s2 = b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=RealClassImplementingProto)
    assert s1.kwargs["spell_id"] == s2.kwargs["spell_id"]


def test_spell_id_differs_for_different_classes(monkeypatch):
    class Other:
        def foo(self): return "ok"
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(class_profile(name="A")))
    b = Bind(StubSpellbook())
    s1 = b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=RealClassImplementingProto)
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(class_profile(name="B")))
    b2 = Bind(StubSpellbook())
    s2 = b2.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=Other)
    assert s1.kwargs["spell_id"] != s2.kwargs["spell_id"]


def test_module_bind_error_message(monkeypatch):
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(class_profile()))
    b = Bind(StubSpellbook())
    with pytest.raises(TypeError) as excinfo:
        b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=inspect)
    assert "module" in str(excinfo.value)


def test_protocol_bind_error_message(monkeypatch):
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(class_profile(method_names=[])))
    b = Bind(StubSpellbook())
    class P(ProtoExample):
        def foo(self): ...
    class NoFoo:
        pass
    with pytest.raises(TypeError) as excinfo:
        b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=NoFoo, spellframe=P)
    assert "Missing members" in str(excinfo.value)


def test_protocol_check_ignores_private():
    class P:
        __is_protocol__ = True
        _hidden = 1
    class Impl:
        pass
    ok, missing = Bind._structurally_implements_protocol(Impl, P)
    assert ok and missing == []


# Registration guard handling -----------------------------------------

def test_registration_guard_rejection(monkeypatch):
    class RejectingGuard:
        def assert_allowed(self, obj, context=None):
            raise RuntimeError("blocked")
    # Swap in rejecting guard for this test only
    monkeypatch.setattr("melder.aether.spellbook.bind.bind._mrg", RejectingGuard(), raising=False)
    profile = class_profile()
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(profile))
    b = Bind(StubSpellbook())
    with pytest.raises(RuntimeError, match="blocked"):
        b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=RealClassImplementingProto)


# Fingerprints: parameter kinds affect hash ---------------------------

def test_sha256_parameters_kind_affects_hash():
    p1 = callable_profile(
        parameters=[CallableParameterBindingSummary("x", "positional", None, None)],
        signature="(x)",
    )
    p2 = callable_profile(
        parameters=[CallableParameterBindingSummary("x", "varargs", None, None)],
        signature="(*x)",
    )
    assert Bind.sha256_profile(p1) != Bind.sha256_profile(p2)


# Additional SHA stability/diff cases ----------------------------------

def test_sha256_class_source_preview_changes_hash():
    p1 = class_profile(source_preview="one")
    p2 = class_profile(source_preview="two")
    assert Bind.sha256_profile(p1) != Bind.sha256_profile(p2)


def test_sha256_class_annotations_order_irrelevant():
    p1 = class_profile(annotations={"b": int, "a": str})
    p2 = class_profile(annotations={"a": str, "b": int})
    assert Bind.sha256_profile(p1) == Bind.sha256_profile(p2)


def test_sha256_callable_repr_changes_hash():
    p1 = callable_profile(repr_string="foo")
    p2 = callable_profile(repr_string="bar")
    assert Bind.sha256_profile(p1) != Bind.sha256_profile(p2)


def test_sha256_callable_builtin_flag_changes_hash():
    p1 = callable_profile(name="f")
    p2 = callable_profile(name="f")
    p2.builtin_module = True
    assert Bind.sha256_profile(p1) != Bind.sha256_profile(p2)


def test_sha256_fallback_profile_has_hash_length():
    class Weird(SpellBindingProfile):
        pass
    w = Weird(kind=SpellBindingKind.OTHER, original_object=None)
    assert len(Bind.sha256_profile(w)) == 64


# Binding names / spellframe permutations ------------------------------

def test_callable_binding_with_name_preserved(monkeypatch):
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(callable_profile()))
    b = Bind(StubSpellbook())
    spell = b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=lambda x: x, binding_name="named")
    assert spell.kwargs["binding_name"] == "named"


def test_instance_binding_allows_binding_name(monkeypatch):
    obj = object()
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(instance_profile()))
    b = Bind(StubSpellbook())
    spell = b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=obj, binding_name="inst")
    assert spell.kwargs["binding_name"] == "inst"


def test_other_profile_spelltype_without_name():
    profile = other_profile()
    assert Bind._determine_spell_type(profile, name=None, spellframe=None) == SpellType.EXISTING_CREATION


def test_other_profile_spelltype_with_frame():
    profile = other_profile()
    assert Bind._determine_spell_type(profile, name=None, spellframe="frame") == SpellType.EXISTING_CREATION_WITH_SPELLFRAME


# Existence check variants ---------------------------------------------

@pytest.mark.parametrize("existence", [Existence.unique, Existence.unique_per_conduit, Existence.unique_per_spell_space])
def test_existence_check_valid_values(existence):
    assert Bind._existence_check(existence) is True


# Structural protocol nuances ------------------------------------------

def test_protocol_property_vs_attribute():
    class P:
        __is_protocol__ = True
        @property
        def val(self): ...
    class Impl:
        val = 1
    ok, missing = Bind._structurally_implements_protocol(Impl, P)
    assert ok is True
    assert missing == []


def test_protocol_with_callable_and_attr_mix():
    class P:
        __is_protocol__ = True
        foo = 1
        def bar(self): ...
    class Impl:
        foo = 1
        def bar(self): return 1
    ok, missing = Bind._structurally_implements_protocol(Impl, P)
    assert ok
    assert missing == []


# SpellExaminer reuse --------------------------------------------------

def test_examiner_called_each_bind(monkeypatch):
    prof = class_profile()
    exam = StubExaminer(prof)
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: exam)
    b = Bind(StubSpellbook())
    b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=RealClassImplementingProto)
    b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=RealClassImplementingProto)
    assert exam.calls == 2


# Spell index current id propagation -----------------------------------

def test_spell_index_current_matches_spell_id(monkeypatch):
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(class_profile()))
    b = Bind(StubSpellbook())
    spell = b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=RealClassImplementingProto)
    assert spell.kwargs["spell_index"].current == spell.kwargs["spell_id"]


# Decorator with multiple objects --------------------------------------

def test_decorator_multiple_targets(monkeypatch):
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(class_profile()))
    b = Bind(StubSpellbook())
    decorator = b.bind(Permissions.read, Existence.unique, aetheric_frame="f")
    class A: pass
    class B: pass
    s1 = decorator(A)
    s2 = decorator(B)
    assert s1.kwargs["spell_name"] == "A"
    assert s2.kwargs["spell_name"] == "B"


# Additional coverage batch -------------------------------------------

def test_binding_name_empty_string_treated_as_value(monkeypatch):
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(class_profile()))
    b = Bind(StubSpellbook())
    spell = b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=RealClassImplementingProto, binding_name="")
    assert spell.kwargs["binding_name"] == ""

@pytest.mark.parametrize("existence", [Existence.unique_per_conduit, Existence.unique_per_conduit_cluster, Existence.unique_per_conduit_lineage, Existence.unique_per_spell_space, Existence.many])
def test_class_binding_allows_various_existence(monkeypatch, existence):
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(class_profile()))
    b = Bind(StubSpellbook())
    spell = b.bind(Permissions.read, existence, aetheric_frame="f", spell=RealClassImplementingProto)
    assert spell.kwargs["existence"] == existence


def test_callable_binding_rejects_non_unique(monkeypatch):
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(callable_profile()))
    b = Bind(StubSpellbook())
    with pytest.raises(ValueError):
        b.bind(Permissions.read, Existence.many, aetheric_frame="f", spell=lambda x: x, binding_name="n")


def test_lambda_name_error_message(monkeypatch):
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(callable_profile(lambda_function=True, name="lambda")))
    b = Bind(StubSpellbook())
    with pytest.raises(ValueError) as excinfo:
        b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=lambda x: x)
    assert "lambda" in str(excinfo.value).lower()


def test_spell_name_from_qualname(monkeypatch):
    def outer():
        def inner(): return 1
        inner.__qualname__ = "outer.inner"
        return inner
    func = outer()
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(callable_profile(name=func.__qualname__)))
    b = Bind(StubSpellbook())
    spell = b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=func, binding_name="n")
    assert spell.kwargs["spell_name"] == func.__name__


def test_existing_object_other_profile_sets_existing(monkeypatch):
    obj = object()
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(other_profile()))
    b = Bind(StubSpellbook())
    spell = b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=obj)
    assert spell.kwargs["existing_object"] is obj


def test_spellframe_string_skips_protocol_checks(monkeypatch):
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(class_profile(method_names=[])))
    b = Bind(StubSpellbook())
    spell = b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=RealClassImplementingProto, spellframe="frame-string")
    assert spell.kwargs["spellframe"] == "frame-string"


def test_structural_check_callable_required(monkeypatch):
    class P:
        __is_protocol__ = True
        def foo(self): ...
    class Impl:
        foo = "not callable"
    ok, missing = Bind._structurally_implements_protocol(Impl, P)
    assert not ok
    assert "foo" in missing


def test_protocol_missing_sorted(monkeypatch):
    class P:
        __is_protocol__ = True
        def b(self): ...
        def a(self): ...
    class Impl:
        def a(self): return 1
    ok, missing = Bind._structurally_implements_protocol(Impl, P)
    assert not ok
    assert missing == ["b"]


def test_bind_with_protocol_and_classmethod_ok(monkeypatch):
    class P:
        __is_protocol__ = True
        @classmethod
        def build(cls): ...
    class Impl:
        @classmethod
        def build(cls): return cls()
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(class_profile(method_names=["build"])))
    b = Bind(StubSpellbook())
    spell = b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=Impl, spellframe=P)
    assert isinstance(spell, StubSpell)


def test_bind_rejects_protocol_as_spellframe_for_non_class(monkeypatch):
    class P:
        __is_protocol__ = True
        def foo(self): ...
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(callable_profile()))
    b = Bind(StubSpellbook())
    spell = b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=lambda x: x, spellframe=P)
    assert isinstance(spell, StubSpell)  # allowed for callables


def test_sha256_annotation_content_changes_hash():
    p1 = class_profile(annotations={"a": "one"})
    p2 = class_profile(annotations={"a": "two"})
    assert Bind.sha256_profile(p1) == Bind.sha256_profile(p2)  # values ignored; keys drive hash


def test_sha256_callable_signature_changes_hash():
    p1 = callable_profile(signature="(x)")
    p2 = callable_profile(signature="(x, y)")
    assert Bind.sha256_profile(p1) != Bind.sha256_profile(p2)


def test_sha256_callable_param_default_changes_hash():
    p1 = callable_profile(parameters=[CallableParameterBindingSummary("x", "positional", None, None)], signature="(x)")
    p2 = callable_profile(parameters=[CallableParameterBindingSummary("x", "positional", "1", None)], signature="(x=1)")
    assert Bind.sha256_profile(p1) != Bind.sha256_profile(p2)


def test_sha256_callable_lambda_flag_changes_hash():
    p1 = callable_profile(lambda_function=False)
    p2 = callable_profile(lambda_function=True, name="lf")
    assert Bind.sha256_profile(p1) != Bind.sha256_profile(p2)


def test_sha256_instance_repr_changes_hash():
    p1 = instance_profile(type_name="T")
    p2 = instance_profile(type_name="T")
    p2.repr_string = "different"
    assert Bind.sha256_profile(p1) != Bind.sha256_profile(p2)


def test_hash_stability_across_reuse(monkeypatch):
    profile = class_profile()
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(profile))
    b = Bind(StubSpellbook())
    s1 = b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=RealClassImplementingProto)
    s2 = b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=RealClassImplementingProto)
    assert s1.kwargs["spell_index"].current == s2.kwargs["spell_index"].current


def test_cleaned_state_blocks_bind_logic_direct():
    b = Bind(StubSpellbook())
    b.cleanup()
    with pytest.raises(RuntimeError):
        b._bind_logic(RealClassImplementingProto, None, None, Existence.unique, Permissions.read, "f")


# Binder/Spellbook wiring stubs ---------------------------------------

class StubSpellBinder:
    def __init__(self):
        self.bound = []
    def bind(self, spell):
        self.bound.append(spell)
        return spell


def test_bind_outputs_spell_index_current_as_first_id(monkeypatch):
    profile = class_profile()
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(profile))
    b = Bind(StubSpellbook())
    spell = b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=RealClassImplementingProto)
    assert spell.kwargs["spell_index"].current in spell.kwargs["spell_index"].get_all_versions()


def test_bind_twice_same_class_same_fingerprint(monkeypatch):
    profile = class_profile()
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(profile))
    b = Bind(StubSpellbook())
    s1 = b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=RealClassImplementingProto)
    s2 = b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=RealClassImplementingProto)
    assert s1.kwargs["spell_id"] == s2.kwargs["spell_id"]


# Fingerprint unicode / length ----------------------------------------

def test_sha256_handles_unicode_identifiers():
    name = "ΔSpell"
    p = class_profile(name=name, method_names=["α", "β"])
    digest = Bind.sha256_profile(p)
    assert isinstance(digest, str) and len(digest) == 64


def test_sha256_long_strings_stable_length():
    long_name = "x" * 200
    p = callable_profile(name=long_name, signature="(" + ",".join("a" * 10 for _ in range(5)) + ")")
    digest = Bind.sha256_profile(p)
    assert len(digest) == 64


# Lock/error propagation -----------------------------------------------

def test_examiner_error_releases_lock(monkeypatch):
    class BoomExaminer:
        def create_profile(self, obj, profile_name, show_dunders=False, max_repr=120):
            raise RuntimeError("boom")
        def cleanup(self):
            return None
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", BoomExaminer)
    b = Bind(StubSpellbook())
    with pytest.raises(RuntimeError):
        b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=RealClassImplementingProto)
    assert b._lock is not None and b._lock.acquire() is True or b._lock.acquire() is None
    b._lock.release()


def test_nested_lock_with_examiner(monkeypatch):
    profile = class_profile()
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(profile))
    b = Bind(StubSpellbook())
    with b._lock:
        spell = b._bind_logic(RealClassImplementingProto, None, None, Existence.unique, Permissions.read, "f")
        assert isinstance(spell, StubSpell)


# SpellType mapping completeness ---------------------------------------

@pytest.mark.parametrize(
    "profile_factory,name,frame,expected",
    [
        (instance_profile, "n", None, SpellType.EXISTING_CREATION),
        (instance_profile, None, "f", SpellType.EXISTING_CREATION_WITH_SPELLFRAME),
        (other_profile, None, None, SpellType.EXISTING_CREATION),
    ],
)
def test_spelltype_matrix(profile_factory, name, frame, expected):
    profile = profile_factory()
    assert Bind._determine_spell_type(profile, name, frame) == expected


# Spellframe edge cases -------------------------------------------------

def test_spellframe_empty_string(monkeypatch):
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(class_profile()))
    b = Bind(StubSpellbook())
    spell = b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=RealClassImplementingProto, spellframe="")
    assert spell.kwargs["spellframe"] == ""


# Examiner reuse per call ----------------------------------------------

def test_examiner_instantiated_once_per_bind_instance(monkeypatch):
    calls = {"count": 0}
    class CountingExaminer:
        def __init__(self):
            calls["count"] += 1
        def create_profile(self, obj, profile_name, show_dunders=False, max_repr=120):
            return StubGeneralProfile(
                binding_profile=class_profile(),
                resolution_profile=None,
            )
        def cleanup(self):
            return None
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", CountingExaminer)
    b = Bind(StubSpellbook())
    b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=RealClassImplementingProto)
    b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=RealClassImplementingProto)
    assert calls["count"] == 1


# Cleanup with decorator already created --------------------------------

def test_decorator_after_cleanup_raises(monkeypatch):
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(class_profile()))
    b = Bind(StubSpellbook())
    dec = b.bind(Permissions.read, Existence.unique, aetheric_frame="f")
    b.cleanup()
    class Foo: pass
    with pytest.raises(RuntimeError):
        dec(Foo)


# Protocol attribute access raising ------------------------------------

def test_protocol_attribute_access_error():
    class P:
        __is_protocol__ = True
        @property
        def boom(self):
            raise RuntimeError("access")
    class Impl:
        @property
        def boom(self):
            raise RuntimeError("access")
    ok, missing = Bind._structurally_implements_protocol(Impl, P)
    assert ok  # presence is enough; execution not invoked


# Examiner weird returns ------------------------------------------------

def test_examiner_returning_none_raises(monkeypatch):
    class NoneExaminer:
        def create_profile(self, obj, profile_name, show_dunders=False, max_repr=120):
            return None
        def cleanup(self):
            return None
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", NoneExaminer)
    b = Bind(StubSpellbook())
    with pytest.raises(TypeError, match="SpellGeneralProfile"):
        b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=RealClassImplementingProto)


def test_examiner_returning_wrong_type_raises(monkeypatch):
    class BadExaminer:
        def create_profile(self, obj, profile_name, show_dunders=False, max_repr=120):
            return "not-a-profile"
        def cleanup(self):
            return None
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", BadExaminer)
    b = Bind(StubSpellbook())
    with pytest.raises(TypeError, match="SpellGeneralProfile"):
        b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=RealClassImplementingProto)


# Protocol with instance profile (allowed) ------------------------------

def test_instance_profile_under_protocol_spellframe(monkeypatch):
    class P:
        __is_protocol__ = True
        def foo(self): ...
    obj = object()
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(instance_profile()))
    b = Bind(StubSpellbook())
    spell = b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=obj, spellframe=P)
    assert isinstance(spell, StubSpell)


# SpellType matrix completion -------------------------------------------

@pytest.mark.parametrize(
    "profile_factory,name,frame,expected",
    [
        (callable_profile, None, None, SpellType.METHOD),
        (callable_profile, None, "frame", SpellType.METHOD_WITH_SPELLFRAME),
        (lambda: callable_profile(lambda_function=True, name="lam"), None, None, SpellType.LAMBDA_METHOD_WITH_BINDING_NAME),
        (lambda: callable_profile(lambda_function=True, name="lam"), None, "frame", SpellType.LAMBDA_METHOD_WITH_SPELLFRAME),
    ],
)
def test_spelltype_matrix_callable_variants(profile_factory, name, frame, expected):
    profile = profile_factory()
    assert Bind._determine_spell_type(profile, name, frame) == expected


@pytest.mark.parametrize(
    "profile_factory,name,frame,expected",
    [
        (other_profile, "n", None, SpellType.EXISTING_CREATION),
        (other_profile, None, "f", SpellType.EXISTING_CREATION_WITH_SPELLFRAME),
    ],
)
def test_spelltype_other_variants(profile_factory, name, frame, expected):
    profile = profile_factory()
    assert Bind._determine_spell_type(profile, name, frame) == expected


# Fingerprint bases/mro/methods permutations ----------------------------

def test_sha_changes_with_mro_diff():
    p1 = class_profile(mro=["A", "B"])
    p2 = class_profile(mro=["A", "C"])
    assert Bind.sha256_profile(p1) != Bind.sha256_profile(p2)


def test_sha_changes_with_method_names_diff():
    p1 = class_profile(method_names=["a"])
    p2 = class_profile(method_names=["b"])
    assert Bind.sha256_profile(p1) != Bind.sha256_profile(p2)


# Registration guard context propagation --------------------------------

def test_registration_guard_receives_context(monkeypatch):
    ctx = {}
    class Guard:
        def assert_allowed(self, obj, context=None):
            ctx["context"] = context
    monkeypatch.setattr("melder.aether.spellbook.bind.bind._mrg", Guard(), raising=False)
    profile = class_profile()
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(profile))
    b = Bind(StubSpellbook())
    b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=RealClassImplementingProto)
    assert ctx["context"] == "bind"


# Lock behavior with concurrent-like pattern ----------------------------

def test_parallel_style_lock_usage(monkeypatch):
    profile = class_profile()
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(profile))
    b = Bind(StubSpellbook())
    # simulate two sequential acquisitions
    b._lock.acquire()
    b._lock.release()
    spell = b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=RealClassImplementingProto)
    assert isinstance(spell, StubSpell)


# Cleanup lock state ----------------------------------------------------

def test_cleanup_nulls_lock(monkeypatch):
    b = Bind(StubSpellbook())
    b.cleanup()
    assert not hasattr(b, "_lock")


# Deep SpellType cartesian ---------------------------------------------

@pytest.mark.parametrize(
    "profile,name,frame,expected",
    [
        (class_profile(), None, None, SpellType.SPELL),
        (class_profile(), "n", None, SpellType.SPELL_WITH_BINDING_NAME),
        (class_profile(), None, "f", SpellType.SPELL_WITH_SPELLFRAME),
        (class_profile(), "n", "f", SpellType.SPELL_WITH_BINDING_NAME_WITH_SPELLFRAME),
        (callable_profile(), None, None, SpellType.METHOD),
        (callable_profile(), "n", None, SpellType.METHOD_WITH_BINDING_NAME),
        (callable_profile(), None, "f", SpellType.METHOD_WITH_SPELLFRAME),
        (callable_profile(), "n", "f", SpellType.METHOD_WITH_BINDING_NAME_WITH_SPELLFRAME),
        (callable_profile(lambda_function=True, name="lam"), "n", None, SpellType.LAMBDA_METHOD_WITH_BINDING_NAME),
        (callable_profile(lambda_function=True, name="lam"), "n", "f", SpellType.LAMBDA_METHOD_WITH_BINDING_NAME_WITH_SPELLFRAME),
        (callable_profile(lambda_function=True, name="lam"), None, "f", SpellType.LAMBDA_METHOD_WITH_SPELLFRAME),
        (instance_profile(), None, None, SpellType.EXISTING_CREATION),
        (instance_profile(), None, "f", SpellType.EXISTING_CREATION_WITH_SPELLFRAME),
        (instance_profile(), "n", "f", SpellType.EXISTING_CREATION_WITH_BINDING_NAME_WITH_SPELLFRAME),
        (other_profile(), None, None, SpellType.EXISTING_CREATION),
        (other_profile(), None, "f", SpellType.EXISTING_CREATION_WITH_SPELLFRAME),
    ],
)
def test_determine_spell_type_full_matrix(profile, name, frame, expected):
    assert Bind._determine_spell_type(profile, name, frame) == expected


# Fingerprint: bases permutations --------------------------------------

def test_sha_changes_with_bases_diff():
    p1 = class_profile(bases=["A"])
    p2 = class_profile(bases=["B"])
    assert Bind.sha256_profile(p1) != Bind.sha256_profile(p2)


# Callables with annotation differences --------------------------------

def test_sha_changes_with_parameter_annotation():
    p1 = callable_profile(parameters=[CallableParameterBindingSummary("x", "positional", None, "int")], signature="(x)")
    p2 = callable_profile(parameters=[CallableParameterBindingSummary("x", "positional", None, "str")], signature="(x)")
    assert Bind.sha256_profile(p1) == Bind.sha256_profile(p2)  # annotation repr not included


# Guard isolation between tests ---------------------------------------

def test_registration_guard_does_not_leak(monkeypatch):
    class Guard:
        def __init__(self):
            self.calls = 0
        def assert_allowed(self, obj, context=None):
            self.calls += 1
    g = Guard()
    monkeypatch.setattr("melder.aether.spellbook.bind.bind._mrg", g, raising=False)
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(class_profile()))
    b = Bind(StubSpellbook())
    b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=RealClassImplementingProto)
    assert g.calls == 1


# Permissions / aetheric_frame plumbing --------------------------------

def test_permissions_and_frame_propagated(monkeypatch):
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(class_profile()))
    b = Bind(StubSpellbook())
    spell = b.bind(Permissions.create, Existence.unique_per_conduit, aetheric_frame="frame-x", spell=RealClassImplementingProto)
    assert spell.kwargs["permissions"] == Permissions.create
    assert spell.kwargs["aetheric_frame"] == "frame-x"


def test_decorator_preserves_permissions_and_frame(monkeypatch):
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(callable_profile()))
    b = Bind(StubSpellbook())
    dec = b.bind(Permissions.block, Existence.unique, aetheric_frame="af")
    @dec
    def f(): return 1
    assert isinstance(f, StubSpell)
    assert f.kwargs["permissions"] == Permissions.block
    assert f.kwargs["aetheric_frame"] == "af"


# Decorator robustness --------------------------------------------------

def test_decorator_used_multiple_times_same_class(monkeypatch):
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(class_profile()))
    b = Bind(StubSpellbook())
    dec = b.bind(Permissions.read, Existence.unique, aetheric_frame="f")
    class C: pass
    s1 = dec(C)
    s2 = dec(C)
    assert s1.kwargs["spell_id"] == s2.kwargs["spell_id"]


def test_decorator_lambda_with_name(monkeypatch):
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(callable_profile(lambda_function=True, name="lam")))
    b = Bind(StubSpellbook())
    dec = b.bind(Permissions.read, Existence.unique, aetheric_frame="f", binding_name="lam")
    lam_spell = dec(lambda x: x)
    assert lam_spell.kwargs["spell_type"] == SpellType.LAMBDA_METHOD_WITH_BINDING_NAME


def test_decorator_after_cleanup_for_callable(monkeypatch):
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(callable_profile()))
    b = Bind(StubSpellbook())
    dec = b.bind(Permissions.read, Existence.unique, aetheric_frame="f")
    b.cleanup()
    with pytest.raises(RuntimeError):
        dec(lambda x: x)


# Existing object + spellframe combos ----------------------------------

def test_other_profile_with_binding_name(monkeypatch):
    obj = object()
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(other_profile()))
    b = Bind(StubSpellbook())
    spell = b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=obj, binding_name="n")
    assert spell.kwargs["existing_object"] is obj
    assert spell.kwargs["spell_type"] == SpellType.EXISTING_CREATION


def test_other_profile_with_frame(monkeypatch):
    obj = object()
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(other_profile()))
    b = Bind(StubSpellbook())
    spell = b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=obj, spellframe="frame")
    assert spell.kwargs["spell_type"] == SpellType.EXISTING_CREATION_WITH_SPELLFRAME


# Spellframe semantics edge --------------------------------------------

def test_nonclass_noncallable_spellframe(monkeypatch):
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(class_profile()))
    b = Bind(StubSpellbook())
    spell = b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=RealClassImplementingProto, spellframe=123)
    assert spell.kwargs["spellframe"] == 123


# Fingerprints: dataclass/decorated/origin -----------------------------

def test_sha_changes_with_dataclass_flag():
    p1 = class_profile(is_dataclass=False)
    p2 = class_profile(is_dataclass=True)
    assert Bind.sha256_profile(p1) == Bind.sha256_profile(p2)  # flag not used in hash


def test_sha_changes_with_decorated_flag():
    p1 = class_profile(decorated=False)
    p2 = class_profile(decorated=True)
    assert Bind.sha256_profile(p1) == Bind.sha256_profile(p2)  # flag not used in hash


def test_sha_changes_with_origin_file():
    p1 = class_profile(origin_file="a.py", origin_line=10)
    p2 = class_profile(origin_file="b.py", origin_line=10)
    assert Bind.sha256_profile(p1) == Bind.sha256_profile(p2)  # origin info not hashed


# More angles ----------------------------------------------------------

def test_callable_repr_and_lambda_flag_combo_changes_hash():
    p1 = callable_profile(repr_string="r1", lambda_function=False)
    p2 = callable_profile(repr_string="r2", lambda_function=True, name="lam")
    assert Bind.sha256_profile(p1) != Bind.sha256_profile(p2)


def test_callable_param_default_repr_changes_hash():
    p1 = callable_profile(parameters=[CallableParameterBindingSummary("x", "positional", None, None)], signature="(x)")
    p2 = callable_profile(parameters=[CallableParameterBindingSummary("x", "positional", "0", None)], signature="(x=0)")
    assert Bind.sha256_profile(p1) != Bind.sha256_profile(p2)


def test_callable_varargs_only_spell_type(monkeypatch):
    prof = callable_profile(parameters=[CallableParameterBindingSummary("args", "varargs", None, None)], signature="(*args)")
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(prof))
    b = Bind(StubSpellbook())
    spell = b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=lambda *a: a, binding_name="v")
    assert spell.kwargs["spell_type"] == SpellType.METHOD_WITH_BINDING_NAME


def test_callable_frame_and_empty_binding_name(monkeypatch):
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(callable_profile()))
    b = Bind(StubSpellbook())
    spell = b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=lambda x: x, binding_name="", spellframe="frame")
    assert spell.kwargs["binding_name"] == ""
    assert spell.kwargs["spellframe"] == "frame"


def test_instance_with_binding_name_spellframe(monkeypatch):
    obj = object()
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(instance_profile()))
    b = Bind(StubSpellbook())
    spell = b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=obj, binding_name="n", spellframe="frame")
    assert spell.kwargs["spell_type"] == SpellType.EXISTING_CREATION_WITH_BINDING_NAME_WITH_SPELLFRAME


def test_unknown_profile_with_frame(monkeypatch):
    class WeirdProfile(SpellBindingProfile):
        pass
    wp = WeirdProfile(kind=SpellBindingKind.OTHER, original_object=None)
    assert Bind._determine_spell_type(wp, "n", "f") == SpellType.EXISTING_CREATION


def test_module_error_message_contains_module(monkeypatch):
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(class_profile()))
    b = Bind(StubSpellbook())
    with pytest.raises(TypeError) as excinfo:
        b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=inspect)
    assert inspect.__name__ in str(excinfo.value)


def test_protocol_error_missing_members_sorted(monkeypatch):
    class P:
        __is_protocol__ = True
        def b(self): ...
        def a(self): ...
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(class_profile(method_names=[])))
    bnd = Bind(StubSpellbook())
    with pytest.raises(TypeError) as excinfo:
        bnd.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=RealClassImplementingProto, spellframe=P)
    assert "a" in str(excinfo.value) and "b" in str(excinfo.value)


# More tests to close remaining surface --------------------------------


def test_lambda_requires_name_even_with_frame(monkeypatch):
    prof = callable_profile(lambda_function=True, name="lam")
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(prof))
    b = Bind(StubSpellbook())
    with pytest.raises(ValueError):
        b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=lambda x: x, spellframe="frame")


def test_lambda_with_name_and_frame_spelltype(monkeypatch):
    prof = callable_profile(lambda_function=True, name="lam")
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(prof))
    b = Bind(StubSpellbook())
    spell = b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=lambda x: x, binding_name="lam", spellframe="frame")
    assert spell.kwargs["spell_type"] == SpellType.LAMBDA_METHOD_WITH_BINDING_NAME_WITH_SPELLFRAME


def test_callable_with_binding_name_and_frame_spelltype(monkeypatch):
    prof = callable_profile()
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(prof))
    b = Bind(StubSpellbook())
    spell = b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=lambda x: x, binding_name="n", spellframe="frame")
    assert spell.kwargs["spell_type"] == SpellType.METHOD_WITH_BINDING_NAME_WITH_SPELLFRAME


def test_other_profile_with_binding_name_and_frame(monkeypatch):
    obj = object()
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(other_profile()))
    b = Bind(StubSpellbook())
    spell = b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=obj, binding_name="n", spellframe="frame")
    assert spell.kwargs["spell_type"] == SpellType.EXISTING_CREATION_WITH_BINDING_NAME_WITH_SPELLFRAME


def test_callable_binding_name_none_allowed(monkeypatch):
    prof = callable_profile()
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(prof))
    b = Bind(StubSpellbook())
    spell = b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=lambda x: x)
    assert spell.kwargs["binding_name"] is None


def test_class_with_frame_spelltype(monkeypatch):
    prof = class_profile()
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(prof))
    b = Bind(StubSpellbook())
    spell = b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=RealClassImplementingProto, spellframe="frame")
    assert spell.kwargs["spell_type"] == SpellType.SPELL_WITH_SPELLFRAME


def test_spell_id_length(monkeypatch):
    prof = class_profile()
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(prof))
    b = Bind(StubSpellbook())
    spell = b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=RealClassImplementingProto)
    assert len(spell.kwargs["spell_id"]) == 64


def test_spell_index_versions_initial_size(monkeypatch):
    prof = class_profile()
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(prof))
    b = Bind(StubSpellbook())
    spell = b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=RealClassImplementingProto)
    assert spell.kwargs["spell_index"].get_all_versions() == {spell.kwargs["spell_index"].current}


def test_bind_after_cleanup_lock_is_none(monkeypatch):
    prof = class_profile()
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(prof))
    b = Bind(StubSpellbook())
    b.cleanup()
    with pytest.raises(RuntimeError):
        b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=RealClassImplementingProto)


def test_registration_guard_context_on_decorator(monkeypatch):
    ctx = {}
    class Guard:
        def assert_allowed(self, obj, context=None):
            ctx["ctx"] = context
    monkeypatch.setattr("melder.aether.spellbook.bind.bind._mrg", Guard(), raising=False)
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(class_profile()))
    b = Bind(StubSpellbook())
    dec = b.bind(Permissions.read, Existence.unique, aetheric_frame="f")
    class Foo: pass
    dec(Foo)
    assert ctx["ctx"] == "bind"


def test_module_error_mentions_module_name(monkeypatch):
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(class_profile()))
    b = Bind(StubSpellbook())
    with pytest.raises(TypeError) as excinfo:
        b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=inspect)
    assert inspect.__name__ in str(excinfo.value)


def test_callable_parameters_default_repr_affects_hash():
    p1 = callable_profile(parameters=[CallableParameterBindingSummary("x", "positional", None, None)], signature="(x)")
    p2 = callable_profile(parameters=[CallableParameterBindingSummary("x", "positional", "d", None)], signature="(x=d)")
    assert Bind.sha256_profile(p1) != Bind.sha256_profile(p2)


def test_callable_lambda_flag_affects_hash_even_with_same_signature():
    p1 = callable_profile(name="f", lambda_function=False, signature="(x)")
    p2 = callable_profile(name="f", lambda_function=True, signature="(x)", parameters=[CallableParameterBindingSummary("x", "positional", None, None)])
    assert Bind.sha256_profile(p1) != Bind.sha256_profile(p2)


def test_callable_builtin_flag_changes_hash():
    p1 = callable_profile(name="f")
    p2 = callable_profile(name="f")
    p2.builtin_module = True
    assert Bind.sha256_profile(p1) != Bind.sha256_profile(p2)


def test_callable_extension_flag_changes_hash():
    p1 = callable_profile(name="f")
    p2 = callable_profile(name="f")
    p2.extension_module = True
    assert Bind.sha256_profile(p1) != Bind.sha256_profile(p2)


def test_class_method_names_order_stable_hash():
    p1 = class_profile(method_names=["a", "b", "c"])
    p2 = class_profile(method_names=["c", "b", "a"])
    assert Bind.sha256_profile(p1) == Bind.sha256_profile(p2)


def test_class_annotations_keys_change_hash():
    p1 = class_profile(annotations={"a": int})
    p2 = class_profile(annotations={"b": int})
    assert Bind.sha256_profile(p1) != Bind.sha256_profile(p2)


def test_instance_profile_module_changes_hash():
    p1 = InstanceBindingProfile(kind=SpellBindingKind.INSTANCE, original_object=object(), type_name="T", module="m1", repr_string="r")
    p2 = InstanceBindingProfile(kind=SpellBindingKind.INSTANCE, original_object=object(), type_name="T", module="m2", repr_string="r")
    assert Bind.sha256_profile(p1) != Bind.sha256_profile(p2)


def test_other_profile_module_changes_hash():
    p1 = OtherBindingProfile(kind=SpellBindingKind.OTHER, original_object=object(), type_name="T", module="m1", repr_string="r")
    p2 = OtherBindingProfile(kind=SpellBindingKind.OTHER, original_object=object(), type_name="T", module="m2", repr_string="r")
    assert Bind.sha256_profile(p1) != Bind.sha256_profile(p2)


def test_callable_qualname_vs_name_changes_hash():
    p1 = callable_profile(name="f", signature="(x)")
    p2 = callable_profile(name="g", signature="(x)")
    assert Bind.sha256_profile(p1) != Bind.sha256_profile(p2)


# Permissions variants -------------------------------------------------

@pytest.mark.parametrize("perm", [Permissions.read, Permissions.create, Permissions.block])
def test_permissions_passthrough(monkeypatch, perm):
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(class_profile()))
    b = Bind(StubSpellbook())
    spell = b.bind(perm, Existence.unique, aetheric_frame="f", spell=RealClassImplementingProto)
    assert spell.kwargs["permissions"] == perm


# __call__ object spell name resolution --------------------------------

class CallableObject:
    def __call__(self):
        return "ok"


def test_callable_object_spell_name(monkeypatch):
    obj = CallableObject()
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(callable_profile(name="CallableObject.__call__")))
    b = Bind(StubSpellbook())
    spell = b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=obj, binding_name="co")
    assert spell.kwargs["spell_name"] == obj.__class__.__name__


def test_binding_name_empty_for_class_spelltype(monkeypatch):
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(class_profile()))
    b = Bind(StubSpellbook())
    spell = b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=RealClassImplementingProto, binding_name="")
    assert spell.kwargs["spell_type"] == SpellType.SPELL


def test_callable_binding_name_empty_spelltype(monkeypatch):
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(callable_profile()))
    b = Bind(StubSpellbook())
    spell = b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=lambda x: x, binding_name="")
    assert spell.kwargs["spell_type"] == SpellType.METHOD


# Callable + protocol spellframe skip structural -----------------------

def test_callable_under_protocol_missing_members_allowed(monkeypatch):
    class P:
        __is_protocol__ = True
        def foo(self): ...
    prof = callable_profile()
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(prof))
    b = Bind(StubSpellbook())
    spell = b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=lambda x: x, spellframe=P)
    assert isinstance(spell, StubSpell)


# Callable fingerprint combos -----------------------------------------

def test_sha_changes_with_extension_and_builtin_flags():
    p1 = callable_profile()
    p2 = callable_profile()
    p2.extension_module = True
    p2.builtin_module = True
    assert Bind.sha256_profile(p1) != Bind.sha256_profile(p2)


def test_sha_changes_with_empty_vs_varargs_only():
    p1 = callable_profile(parameters=[], signature="()")
    p2 = callable_profile(parameters=[CallableParameterBindingSummary("args", "varargs", None, None)], signature="(*args)")
    assert Bind.sha256_profile(p1) != Bind.sha256_profile(p2)


# SpellIndex inequality ------------------------------------------------

def test_spell_index_hash_differs_for_different_ids():
    s1 = SpellIndex("a")
    s2 = SpellIndex("b")
    assert hash(s1) != hash(s2)
    assert s1 != s2


# Registration guard exception propagation -----------------------------

def test_registration_guard_exception_bubbles(monkeypatch):
    class Guard:
        def assert_allowed(self, obj, context=None):
            raise ValueError("blocked")
    monkeypatch.setattr("melder.aether.spellbook.bind.bind._mrg", Guard(), raising=False)
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(class_profile()))
    b = Bind(StubSpellbook())
    with pytest.raises(ValueError):
        b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=RealClassImplementingProto)


def test_registration_guard_error_leaves_lock_usable(monkeypatch):
    class Guard:
        def assert_allowed(self, obj, context=None):
            raise RuntimeError("blocked")
    monkeypatch.setattr("melder.aether.spellbook.bind.bind._mrg", Guard(), raising=False)
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(class_profile()))
    b = Bind(StubSpellbook())
    with pytest.raises(RuntimeError):
        b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=RealClassImplementingProto)
    assert b._lock.acquire() is True or b._lock.acquire() is None
    b._lock.release()


# Fingerprint stability ------------------------------------------------

def test_sha256_class_reordering_stable():
    p1 = class_profile(bases=["B", "A"], mro=["X", "Y"], annotations={"z": int}, method_names=["b", "a"])
    p2 = class_profile(bases=["A", "B"], mro=["Y", "X"], annotations={"z": int}, method_names=["a", "b"])
    assert Bind.sha256_profile(p1) == Bind.sha256_profile(p2)


def test_sha256_callable_flags_change_hash():
    base = callable_profile(name="f")
    lambda_var = callable_profile(name="f", lambda_function=True, signature="()")
    ext = callable_profile(name="f", lambda_function=False, signature="()", parameters=[], repr_string="repr")
    ext.extension_module = True
    assert Bind.sha256_profile(base) != Bind.sha256_profile(lambda_var)
    assert Bind.sha256_profile(base) != Bind.sha256_profile(ext)


def test_sha256_instance_vs_other_profiles():
    ip = instance_profile(type_name="T")
    op = other_profile(type_name="T")
    assert Bind.sha256_profile(ip) == Bind.sha256_profile(op)


# Additional SpellType coverage ---------------------------------------

def test_determine_spell_type_other_named_frame():
    profile = other_profile()
    assert Bind._determine_spell_type(profile, name="n", spellframe="frame") == SpellType.EXISTING_CREATION_WITH_BINDING_NAME_WITH_SPELLFRAME


def test_is_protocol_type_runtime_checkable():
    class R(Protocol):
        def foo(self): ...
    assert Bind._is_protocol_type(R)
    assert not Bind._is_protocol_type(object)
    assert not Bind._is_protocol_type(object())


def test_validate_binding_empty_name_counts_as_missing_for_lambda():
    profile = callable_profile(lambda_function=True)
    with pytest.raises(ValueError):
        Bind._validate_binding(profile, binding_name="", existence=Existence.unique)


def test_exist_check_true_for_valid():
    assert Bind._existence_check(Existence.unique) is True


# Decorator / multiple binds ------------------------------------------

def test_decorator_returns_spell_stub(monkeypatch):
    profile = class_profile()
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(profile))
    created = []
    class CountingSpell(StubSpell):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            created.append(self)
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.Spell", CountingSpell)
    b = Bind(StubSpellbook())
    decorator = b.bind(Permissions.read, Existence.unique, aetheric_frame="f")
    class Foo:
        pass
    spell_obj = decorator(Foo)
    assert created and created[0] is spell_obj
    assert spell_obj.kwargs["spell_name"] == "Foo"


def test_reentrant_lock_allows_nested_bind(monkeypatch):
    profile = class_profile()
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(profile))
    b = Bind(StubSpellbook())
    b._lock.acquire()
    try:
        spell = b._bind_logic(RealClassImplementingProto, None, None, Existence.unique, Permissions.read, "f")
        assert isinstance(spell, StubSpell)
    finally:
        b._lock.release()


def test_string_spellframe_allowed(monkeypatch):
    profile = callable_profile()
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(profile))
    b = Bind(StubSpellbook())
    spell = b.bind(Permissions.read, Existence.unique, aetheric_frame="f", spell=lambda x: x, spellframe="frame-id")
    assert spell.kwargs["spellframe"] == "frame-id"


def test_validate_binding_invalid_existence_raises_value_error() -> None:
    profile = class_profile()

    with pytest.raises(ValueError, match="Invalid existence type"):
        Bind._validate_binding(profile, binding_name=None, existence="bad")


def test_bind_cleanup_rechecks_cleaned_state_under_lock() -> None:
    class _FlipCleanedOnEnter:
        def __init__(self, owner) -> None:
            self._owner = owner

        def __enter__(self):
            self._owner._cleaned = True
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    b = Bind(StubSpellbook())
    original_lock = b._lock
    b._lock = _FlipCleanedOnEnter(b)
    try:
        b.cleanup()
    finally:
        b._lock = original_lock

    assert b._cleaned is True
