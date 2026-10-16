"""Print the spell ids of a fixed synthetic class/callable/instance profile for every existing Existence member.

Run from the repository root with PYTHONPATH=src. S2 pins these values (computed on 0.2.8241, before the managed
options existed) in tests/unit/melder/spellbook/bind/test_bind_managed_spell_options.py.
"""
from melder.aether.spellbook.bind.bind import Bind
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.spell_examiner.profiles.binding_profile import (
    SpellBindingKind, ClassBindingProfile, CallableBindingProfile, InstanceBindingProfile,
)


class Target:
    def reset(self) -> None:
        pass


def class_profile() -> ClassBindingProfile:
    return ClassBindingProfile(kind=SpellBindingKind.CLASS, original_object=Target, name="Pooled", qualname="Pooled",
        module="golden_mod", bases=["object"], mro=["Pooled", "object"], annotations={"size": int},
        origin_file=None, origin_line=None, init_signature="(self, size: int = 1)", source_preview="",
        is_dataclass=False, decorated=False, method_names=["reset", "close"])


def callable_profile() -> CallableBindingProfile:
    return CallableBindingProfile(kind=SpellBindingKind.CALLABLE, original_object=lambda: None, object_id="obj-1",
        name="factory", qualname="factory", module="golden_mod", parameters=[], repr_string="<function factory>",
        type_name="function", signature="()", lambda_function=False, builtin_module=False, extension_module=False)


def instance_profile() -> InstanceBindingProfile:
    return InstanceBindingProfile(kind=SpellBindingKind.INSTANCE, original_object=object(), type_name="Pooled",
        module="golden_mod", repr_string="<Pooled>")


out = {}
profile = class_profile()
for member in Existence:
    if member.name == "managed_spell_quantity":
        continue
    for resolvable in (True, False):
        out[f"class/{member.name}/{resolvable}"] = Bind.sha256_profile(
            profile, spell_name="Pooled", existence=member, resolvable=resolvable)
out["class/unique/frame+name+disposal"] = Bind.sha256_profile(profile, spell_name="Pooled", spellframe="pools",
    binding_name="primary", existence=Existence.unique, disposal_method_names=["close"])
out["callable/unique/True"] = Bind.sha256_profile(callable_profile(), spell_name="factory", existence=Existence.unique)
out["instance/unique/True"] = Bind.sha256_profile(instance_profile(), spell_name="Pooled", existence=Existence.unique)
out["class/managed_spell_quantity/no_options"] = Bind.sha256_profile(
    profile, spell_name="Pooled", existence=Existence.managed_spell_quantity)
for key, value in out.items():
    print(f"{key} {value}")
