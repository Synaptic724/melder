# tests/spellbook/test_bind.py
import unittest
from unittest.mock import patch
import types

# SUT
from melder.spellbook.bind.bind import Bind
from melder.spellbook.spell import Spell
from melder.spellbook.existence.existence import Existence
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.spellbook.spell_types.spell_types import SpellType

# Profiles used by Bind.sha256_profile / type checks
from melder.spellbook.spell_crafter.old_spell_examiner.spell_examiner import (
    SpellExaminer, ClassProfile, MethodProfile
)


# ----------------------- Helpers to fabricate profiles -----------------------

def make_class_profile(
        *,
        name="Foo",
        qualname="Foo",
        module="m",
        bases=("object",),
        mro=("m.Foo", "builtins.object"),
        annotations=None,
        methods=None,
        source_preview="class Foo: pass",
):
    cp = ClassProfile.__new__(ClassProfile)
    cp.name = name
    cp.qualname = qualname
    cp.module = module
    cp.bases = list(bases)
    cp.mro = list(mro)
    cp.annotations = dict(annotations or {})
    cp.methods = dict(methods or {})
    cp.source_preview = source_preview
    return cp


def make_method_profile(
        *,
        name="f",
        qualname="Foo.f",
        module="m",
        signature="(x, y=1)",
        parameters=None,
        preview="def f(x, y=1): return x+y",
        lambda_fn=False,
):
    mp = MethodProfile.__new__(MethodProfile)
    mp.name = name
    mp.qualname = qualname
    mp.module = module
    mp.signature = signature
    mp.parameters = list(parameters or [{"name": "x", "kind": "POSITIONAL_OR_KEYWORD", "default": None},
                                        {"name": "y", "kind": "POSITIONAL_OR_KEYWORD", "default": 1}])
    mp.preview = preview
    mp.lambda_fn = lambda_fn
    return mp


class FakeClass:
    pass


def fake_instance():
    class X:
        pass
    return X()


# ====================================================================
# 1) sha256_profile + spell_id_inspector (7 tests)
# ====================================================================

class TestSha256AndInspector(unittest.TestCase):
    def test_sha256_identical_class_profiles_same_hash(self):
        p1 = make_class_profile(source_preview="class Foo: pass")
        p2 = make_class_profile(source_preview="class Foo: pass")
        h1 = Bind.sha256_profile(p1)
        h2 = Bind.sha256_profile(p2)
        self.assertEqual(h1, h2)

    def test_sha256_different_source_changes_hash(self):
        p1 = make_class_profile(source_preview="class Foo: pass")
        p2 = make_class_profile(source_preview="class Foo:\n    x=1")
        h1 = Bind.sha256_profile(p1)
        h2 = Bind.sha256_profile(p2)
        self.assertNotEqual(h1, h2)

    def test_sha256_method_profile_uses_signature_and_params(self):
        p1 = make_method_profile(signature="(x)", parameters=[{"name": "x", "kind": "PK", "default": None}])
        p2 = make_method_profile(signature="(x, y=1)", parameters=[{"name": "x", "kind": "PK", "default": None},
                                                                   {"name": "y", "kind": "PK", "default": 1}])
        self.assertNotEqual(Bind.sha256_profile(p1), Bind.sha256_profile(p2))

    @patch.object(SpellExaminer, "__init__", return_value=None)
    @patch.object(SpellExaminer, "inspect")
    def test_spell_id_inspector_uses_profile_hash(self, mock_inspect, _init):
        cp = make_class_profile()
        mock_inspect.return_value = cp
        obj = object()
        h = Bind.sha256_profile(cp)
        got = Bind.spell_id_inspector(obj)
        self.assertEqual(got, h)
        mock_inspect.assert_called_once()

    def test_sha256_prefix_tag_versioned(self):
        cp = make_class_profile()
        h = Bind.sha256_profile(cp)
        self.assertEqual(len(h), 64)  # sha256 hex length

    def test_sha256_class_profile_requires_fields(self):
        cp = make_class_profile()
        # Sanity: no exception here
        _ = Bind.sha256_profile(cp)

    def test_sha256_method_profile_requires_fields(self):
        mp = make_method_profile()
        _ = Bind.sha256_profile(mp)


# ====================================================================
# 2) _validate_binding rules (9 tests)
# ====================================================================

class TestValidateBinding(unittest.TestCase):
    def test_existence_check_accepts_enum(self):
        self.assertTrue(Bind._existence_check(Existence.unique))

    def test_existence_check_rejects_non_enum(self):
        with self.assertRaises(ValueError):
            Bind._existence_check("unique")  # not enum

    def test_instance_with_binding_name_rejected(self):
        cp = make_class_profile()
        with self.assertRaises(ValueError):
            Bind._validate_binding(cp, is_instance=True, binding_name="x", existence=Existence.unique)

    def test_lambda_without_name_rejected(self):
        mp = make_method_profile(lambda_fn=True)
        with self.assertRaises(ValueError):
            Bind._validate_binding(mp, is_instance=False, binding_name=None, existence=Existence.unique)

    def test_method_non_unique_existence_rejected(self):
        mp = make_method_profile(lambda_fn=False)
        with self.assertRaises(ValueError):
            Bind._validate_binding(mp, is_instance=False, binding_name="m", existence=Existence.many)

    def test_class_named_ok(self):
        cp = make_class_profile()
        # Should not raise
        Bind._validate_binding(cp, is_instance=False, binding_name="name", existence=Existence.unique)

    def test_class_instance_without_name_ok(self):
        cp = make_class_profile()
        # Should not raise
        Bind._validate_binding(cp, is_instance=True, binding_name=None, existence=Existence.unique)

    def test_weird_profile_type_treated_classlike_in_validate(self):
        # If profile is some object (not MethodProfile), no method-specific rejection applies
        odd = types.SimpleNamespace()
        # Should not raise
        Bind._validate_binding(odd, is_instance=False, binding_name=None, existence=Existence.unique)

    def test_method_with_unique_ok(self):
        mp = make_method_profile(lambda_fn=False)
        Bind._validate_binding(mp, is_instance=False, binding_name=None, existence=Existence.unique)


# ====================================================================
# 3) _determine_spell_type matrix (10 tests)
# ====================================================================

class TestDetermineSpellType(unittest.TestCase):
    def test_class_named_interfaced(self):
        cp = make_class_profile()
        t = Bind._determine_spell_type(FakeClass, cp, name="n", spellframe="IFoo", is_instance=False)
        self.assertEqual(t, SpellType.NAMED_INTERFACED)

    def test_class_normal_interfaced(self):
        cp = make_class_profile()
        t = Bind._determine_spell_type(FakeClass, cp, name=None, spellframe="IFoo", is_instance=False)
        self.assertEqual(t, SpellType.NORMAL_INTERFACED)

    def test_class_named(self):
        cp = make_class_profile()
        t = Bind._determine_spell_type(FakeClass, cp, name="n", spellframe=None, is_instance=False)
        self.assertEqual(t, SpellType.NAMED)

    def test_class_existing_instance(self):
        cp = make_class_profile()
        t = Bind._determine_spell_type(fake_instance(), cp, name=None, spellframe=None, is_instance=True)
        self.assertEqual(t, SpellType.EXISTING_CLASS)

    def test_class_normal(self):
        cp = make_class_profile()
        t = Bind._determine_spell_type(FakeClass, cp, name=None, spellframe=None, is_instance=False)
        self.assertEqual(t, SpellType.NORMAL)

    def test_method_named_lambda(self):
        mp = make_method_profile(lambda_fn=True)
        t = Bind._determine_spell_type(lambda x: x, mp, name="n", spellframe=None, is_instance=False)
        self.assertEqual(t, SpellType.NAMED_LAMBDA_METHOD)

    def test_method_named(self):
        mp = make_method_profile(lambda_fn=False)
        t = Bind._determine_spell_type(FakeClass.__dict__.get, mp, name="n", spellframe=None, is_instance=False)
        self.assertEqual(t, SpellType.NAMED_METHOD)

    def test_method_normal(self):
        mp = make_method_profile(lambda_fn=False)
        t = Bind._determine_spell_type(FakeClass.__dict__.get, mp, name=None, spellframe=None, is_instance=False)
        self.assertEqual(t, SpellType.NORMAL_METHOD)

    def test_fallback_existing_when_unknown_profile_and_instance(self):
        odd = object()
        t = Bind._determine_spell_type(object(), odd, name=None, spellframe=None, is_instance=True)
        self.assertEqual(t, SpellType.EXISTING_CLASS)

    def test_fallback_normal_when_unknown_profile_and_not_instance(self):
        odd = object()
        t = Bind._determine_spell_type(object, odd, name=None, spellframe=None, is_instance=False)
        self.assertEqual(t, SpellType.NORMAL)


# ====================================================================
# 4) bind() end-to-end with SpellExaminer stubs (10 tests)
# ====================================================================

class TestBindEndToEnd(unittest.TestCase):
    def setUp(self):
        self.bind = Bind()
        self.perm_create = Permissions.create
        self.perm_read = Permissions.read

    @patch.object(SpellExaminer, "__init__", return_value=None)
    @patch.object(SpellExaminer, "inspect")
    def test_bind_class_direct_returns_spell(self, mock_inspect, _init):
        cp = make_class_profile(name="Foo", qualname="Foo", module="m")
        mock_inspect.return_value = cp
        sp = self.bind.bind(
            permissions=self.perm_create,
            aetheric_frame="default",
            spell=FakeClass,
            spellframe="IFoo",
            binding_name="primary",
            existence=Existence.unique,
        )
        self.assertIsInstance(sp, Spell)
        self.assertEqual(sp.spell_name, "FakeClass")
        self.assertEqual(sp.spell_type, SpellType.NAMED_INTERFACED)
        self.assertEqual(sp.permissions, self.perm_create)
        self.assertEqual(sp.aetheric_frame, "default")
        self.assertEqual(sp.binding_name, "primary")
        self.assertEqual(sp.spellframe, "IFoo")
        self.assertEqual(sp.existence, Existence.unique)


    @patch.object(SpellExaminer, "__init__", return_value=None)
    @patch.object(SpellExaminer, "inspect")
    def test_bind_existing_instance_normal_type(self, mock_inspect, _init):
        cp = make_class_profile()
        mock_inspect.return_value = cp
        inst = fake_instance()
        sp = self.bind.bind(
            permissions=self.perm_create,
            aetheric_frame="frameX",
            spell=inst,
            existence=Existence.unique
        )
        self.assertIsInstance(sp, Spell)
        self.assertEqual(sp.spell_type, SpellType.EXISTING_CLASS)
        # instance path should resolve the name from the type(inst)
        self.assertEqual(sp.spell_name, type(inst).__name__)
        # no explicit assertions about storing the instance; behavior is container-internal


    @patch.object(SpellExaminer, "__init__", return_value=None)
    @patch.object(SpellExaminer, "inspect")
    def test_bind_method_named_unique_ok(self, mock_inspect, _init):
        mp = make_method_profile(lambda_fn=False)
        mock_inspect.return_value = mp
        sp = self.bind.bind(
            permissions=self.perm_read,
            aetheric_frame="default",
            spell=lambda x: x,  # object not used thanks to stub
            binding_name="handler",
            existence=Existence.unique
        )
        self.assertEqual(sp.spell_type, SpellType.NAMED_METHOD)

    @patch.object(SpellExaminer, "__init__", return_value=None)
    @patch.object(SpellExaminer, "inspect")
    def test_bind_method_non_unique_rejected_via_validate(self, mock_inspect, _init):
        mp = make_method_profile(lambda_fn=False)
        mock_inspect.return_value = mp
        with self.assertRaises(ValueError):
            self.bind.bind(
                permissions=self.perm_create,
                aetheric_frame="default",
                spell=lambda x: x,
                binding_name="m",
                existence=Existence.many  # invalid per _validate_binding
            )

    @patch.object(SpellExaminer, "__init__", return_value=None)
    @patch.object(SpellExaminer, "inspect")
    def test_bind_lambda_without_name_rejected(self, mock_inspect, _init):
        mp = make_method_profile(lambda_fn=True)
        mock_inspect.return_value = mp
        with self.assertRaises(ValueError):
            self.bind.bind(
                permissions=self.perm_create,
                aetheric_frame="default",
                spell=lambda x: x,
                existence=Existence.unique
            )

    @patch.object(SpellExaminer, "__init__", return_value=None)
    @patch.object(SpellExaminer, "inspect")
    def test_bind_instance_with_binding_name_rejected(self, mock_inspect, _init):
        cp = make_class_profile()
        mock_inspect.return_value = cp
        with self.assertRaises(ValueError):
            self.bind.bind(
                permissions=self.perm_create,
                aetheric_frame="default",
                spell=fake_instance(),
                binding_name="x",
                existence=Existence.unique
            )

    @patch.object(SpellExaminer, "__init__", return_value=None)
    @patch.object(SpellExaminer, "inspect")
    def test_bind_permissions_read_passthrough(self, mock_inspect, _init):
        cp = make_class_profile()
        mock_inspect.return_value = cp
        sp = self.bind.bind(
            permissions=Permissions.read,
            aetheric_frame="frame-1",
            spell=FakeClass
        )
        self.assertEqual(sp.permissions, Permissions.read)
        self.assertEqual(sp.aetheric_frame, "frame-1")

    @patch.object(SpellExaminer, "__init__", return_value=None)
    @patch.object(SpellExaminer, "inspect")
    def test_binding_sets_spell_name_from_object(self, mock_inspect, _init):
        cp = make_class_profile()
        mock_inspect.return_value = cp

        class Bar:
            pass

        sp = self.bind.bind(
            permissions=self.perm_create,
            aetheric_frame="default",
            spell=Bar
        )
        self.assertEqual(sp.spell_name, "Bar")

    @patch.object(SpellExaminer, "__init__", return_value=None)
    @patch.object(SpellExaminer, "inspect")
    def test_decorator_usage_returns_spell_object(self, mock_inspect, _init):
        cp = make_class_profile()
        mock_inspect.return_value = cp

        @self.bind.bind(Permissions.create, aetheric_frame="default", spellframe="I", binding_name="n")
        class Baz:
            pass

        # NOTE: Implementation returns a Spell (not the original Baz) in decorator mode.
        self.assertIsInstance(Baz, Spell)
        self.assertEqual(Baz.spell_type, SpellType.NAMED_INTERFACED)
        self.assertEqual(Baz.binding_name, "n")
        self.assertEqual(Baz.spellframe, "I")

    @patch.object(SpellExaminer, "__init__", return_value=None)
    @patch.object(SpellExaminer, "inspect")
    def test_spell_id_is_sha256_of_profile(self, mock_inspect, _init):
        cp = make_class_profile(name="Qux", source_preview="class Qux: pass")
        mock_inspect.return_value = cp
        sp = self.bind.bind(
            permissions=self.perm_create,
            aetheric_frame="default",
            spell=FakeClass
        )
        expected = Bind.sha256_profile(cp)
        self.assertEqual(sp.spell_id, expected)


# ====================================================================
# 5) Misc / edge behavior (4 tests)
# ====================================================================

class TestMiscEdgeBehavior(unittest.TestCase):
    @patch.object(SpellExaminer, "__init__", return_value=None)
    @patch.object(SpellExaminer, "inspect")
    def test_bind_with_spellframe_only_sets_interfaced(self, mock_inspect, _init):
        cp = make_class_profile()
        mock_inspect.return_value = cp
        sp = Bind().bind(
            permissions=Permissions.create,
            aetheric_frame="default",
            spell=FakeClass,
            spellframe="IOnly"
        )
        self.assertEqual(sp.spell_type, SpellType.NORMAL_INTERFACED)
        self.assertEqual(sp.spellframe, "IOnly")
        self.assertIsNone(sp.binding_name)

    @patch.object(SpellExaminer, "__init__", return_value=None)
    @patch.object(SpellExaminer, "inspect")
    def test_bind_with_name_only_sets_named(self, mock_inspect, _init):
        cp = make_class_profile()
        mock_inspect.return_value = cp
        sp = Bind().bind(
            permissions=Permissions.create,
            aetheric_frame="default",
            spell=FakeClass,
            binding_name="primary"
        )
        self.assertEqual(sp.spell_type, SpellType.NAMED)
        self.assertEqual(sp.binding_name, "primary")
        self.assertIsNone(sp.spellframe)

    @patch.object(SpellExaminer, "__init__", return_value=None)
    @patch.object(SpellExaminer, "inspect")
    def test_bind_method_named_lambda_sets_named_lambda_type(self, mock_inspect, _init):
        mp = make_method_profile(lambda_fn=True)
        mock_inspect.return_value = mp
        sp = Bind().bind(
            permissions=Permissions.create,
            aetheric_frame="default",
            spell=lambda x: x,
            binding_name="L"
        )
        self.assertEqual(sp.spell_type, SpellType.NAMED_LAMBDA_METHOD)

    @patch.object(SpellExaminer, "__init__", return_value=None)
    @patch.object(SpellExaminer, "inspect")
    def test_bind_method_no_name_normal_method(self, mock_inspect, _init):
        mp = make_method_profile(lambda_fn=False)
        mock_inspect.return_value = mp
        sp = Bind().bind(
            permissions=Permissions.create,
            aetheric_frame="default",
            spell=lambda x: x
        )
        self.assertEqual(sp.spell_type, SpellType.NORMAL_METHOD)


if __name__ == "__main__":
    unittest.main()
