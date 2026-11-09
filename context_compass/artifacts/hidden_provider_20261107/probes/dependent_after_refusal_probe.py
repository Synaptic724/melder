"""Finding d (STEP 3 of patch hidden_provider_2026_11_07, implementation subagent of melder_0, 2026-11-07): does
a dependent melded while its dependency is refused stay invalid after the refusal lifts?

Two worlds, dynamic, caching off, each step printed with its outcome (read-only; any working directory):
    hidden    - SingleClass refused with HIDDEN_PROVIDER (English under Greeter); its index notched to French lifts it.
    ambiguous - ByProtocol refused with AMBIGUOUS_PROVIDER (English and French under Greeter); French disposed with
                cleanup_spell (announces nothing), then English's index notched to a version of English (announces
                "greeter") lifts it.
In each, a dependent (Upper / UpperP) is bound after the refusal and melded during it, and after the refusal lifts it
is melded again (LIVE) beside a fresh twin bound then (FRESH).
"""
import sys
from typing import Any, Callable, Protocol

import melder
from melder import Aether, Conduit, Spellbook
from melder.aether.spellbook.existence.existence import Existence


class Greeter(Protocol):
    def greet(self) -> str: ...


class English:
    def greet(self) -> str:
        return "hello"


class EnglishV2(English):
    version = 2

    def greet(self) -> str:
        return "hello v2"


EnglishV2.__name__ = "English"
EnglishV2.__qualname__ = "English"


class French:
    def greet(self) -> str:
        return "bonjour"


class SingleClass:
    def __init__(self, greeter: English) -> None:
        self.greeter = greeter


class Upper:
    def __init__(self, single: SingleClass) -> None:
        self.single = single


class LateUpper:
    def __init__(self, single: SingleClass) -> None:
        self.single = single


class ByProtocol:
    def __init__(self, greeter: Greeter) -> None:
        self.greeter = greeter


class UpperP:
    def __init__(self, by: ByProtocol) -> None:
        self.by = by


class LateUpperP:
    def __init__(self, by: ByProtocol) -> None:
        self.by = by


def outcome(call: Callable[[], Any]) -> str:
    try:
        value = call()
    except Exception as error:  # a probe records every failure
        text = " | ".join(line.strip() for line in str(error).splitlines())
        return f"raises {type(error).__name__}: {text[:400]}"
    return f"ok -> {value!r}"


def step(label: str, call: Callable[[], Any]) -> None:
    print(f"  {label:60} {outcome(call)}")


def reset() -> None:
    Aether._reset_singleton_for_tests()
    world = Aether()
    Spellbook._aether = world
    Conduit._aether = world


def book(frame: str) -> Spellbook:
    b = Spellbook(aetheric_frame=frame)
    b.get_configuration().set_property("phase_scheduler_workers_per_spellbook", 1)
    b.configure_aether_frame(system_state="dynamic", system_caching_enabled=False, disposal=None,
                             disposal_method_names=None)
    return b


def hidden_world() -> None:
    print("[hidden] SingleClass refused (HIDDEN_PROVIDER); Upper melded during the refusal; notch to French lifts it")
    reset()
    b = book("dep-hidden")
    english_id = b.bind(spell=English, existence=Existence.many, permissions="create", spellframe=Greeter,
                        binding_name="english")
    root = b.conjure(dynamic=True, name="root")
    index = b.find_spell_by_spell_id(english_id).spell_index
    french_id = root.bind_inactive(spell=French, spell_index=index, existence=Existence.many, permissions="create",
                                   spellframe=Greeter, binding_name="english")
    step("bind SingleClass", lambda: root.bind(spell=SingleClass, existence="many", permissions="create"))
    step("bind Upper", lambda: root.bind(spell=Upper, existence="many", permissions="create")[:12])
    step("meld Upper (during the refusal)", lambda: type(root.meld(Upper)).__name__)
    step("notch English's index to French", lambda: root.notch_spell(spell_index=index, spell_id=french_id))
    step("meld SingleClass (released?)", lambda: type(root.meld(SingleClass)).__name__)
    step("bind LateUpper (FRESH)", lambda: root.bind(spell=LateUpper, existence="many", permissions="create")[:12])
    step("meld LateUpper (FRESH)", lambda: type(root.meld(LateUpper)).__name__)
    step("meld Upper (LIVE)", lambda: type(root.meld(Upper)).__name__)
    step("meld Upper (LIVE) with override", lambda: type(root.meld(
        Upper, override={"single>greeter": English()}).single.greeter).__name__)
    step("meld LateUpper (FRESH) with override", lambda: type(root.meld(
        LateUpper, override={"single>greeter": English()}).single.greeter).__name__)
    root.cleanup()


def ambiguous_world() -> None:
    print("[ambiguous] ByProtocol refused (AMBIGUOUS_PROVIDER); UpperP melded during the refusal; French disposed, "
          "then English's index notched (announces 'greeter')")
    reset()
    b = book("dep-ambiguous")
    english_id = b.bind(spell=English, existence=Existence.many, permissions="create", spellframe=Greeter,
                        binding_name="english")
    french_id = b.bind(spell=French, existence=Existence.many, permissions="create", spellframe=Greeter,
                       binding_name="french")
    root = b.conjure(dynamic=True, name="root")
    index = b.find_spell_by_spell_id(english_id).spell_index
    v2_id = root.bind_inactive(spell=EnglishV2, spell_index=index, existence=Existence.many, permissions="create",
                               spellframe=Greeter, binding_name="english")
    step("bind ByProtocol", lambda: root.bind(spell=ByProtocol, existence="many", permissions="create"))
    step("bind UpperP", lambda: root.bind(spell=UpperP, existence="many", permissions="create")[:12])
    step("meld UpperP (during the refusal)", lambda: type(root.meld(UpperP)).__name__)
    step("cleanup_spell(French)", lambda: root.cleanup_spell(spell=b.find_spell_by_spell_id(french_id)))
    step("meld ByProtocol (after cleanup only)", lambda: type(root.meld(ByProtocol).greeter).__name__)
    step("meld UpperP (after cleanup only)", lambda: type(root.meld(UpperP)).__name__)
    step("notch English's index to EnglishV2", lambda: root.notch_spell(spell_index=index, spell_id=v2_id))
    step("meld ByProtocol (released?)", lambda: root.meld(ByProtocol).greeter.greet())
    step("bind LateUpperP (FRESH)", lambda: root.bind(spell=LateUpperP, existence="many", permissions="create")[:12])
    step("meld LateUpperP (FRESH)", lambda: root.meld(LateUpperP).by.greeter.greet())
    step("meld UpperP (LIVE)", lambda: root.meld(UpperP).by.greeter.greet())
    root.cleanup()


if __name__ == "__main__":
    print(f"melder {melder.__version__} from {melder.__file__}; GIL enabled: {sys._is_gil_enabled()}")
    worlds = sys.argv[1:] or ["hidden", "ambiguous"]
    if "hidden" in worlds:
        hidden_world()
    if "ambiguous" in worlds:
        ambiguous_world()
