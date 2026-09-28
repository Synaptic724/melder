"""Minimal reproduction: Phase 4 DUPLICATE_SPELL_NAME refuses same-named classes at distinct addresses.

Run with Melder installed (Python 3.14t):  python repro_duplicate_spell_name.py.txt
Depends on melder only. Every case uses a fresh book in its own aetheric frame, binds the classes, conjures a
dynamic root and, when the conjure succeeds, melds each class back by its explicit address.

Two classes both named Repo (different __qualname__, like two modules that each define a Repo) are bound at
addresses that differ in spellframe, in binding name or in both. Melder resolves by the normalized
(frame_key, bind_key) pair, and bind already refuses a second active spell on one pair, so none of these
addresses is ambiguous - yet conjure fails. Controls: two different class names pass; a true signature
collision (same spellframe and binding name) is refused at bind, as it should be. A last case binds one Repo
at its default address and melds by the other Repo class object, to show that an unaddressed class meld is keyed
by the class name - the one situation in which a same-named twin really is hazardous.
"""
import json
import sys

import melder
from melder import Spellbook
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration


class ModuleA:
    """Stands in for module a.py."""

    class Repo:
        """Repo as defined in module a."""

        def __init__(self) -> None:
            self.origin = "a"


class ModuleB:
    """Stands in for module b.py."""

    class Repo:
        """A different class that happens to share the name Repo."""

        def __init__(self) -> None:
            self.origin = "b"


class Other:
    """A differently named class, for the control case."""

    def __init__(self) -> None:
        self.origin = "other"


def new_book(tag: str) -> Spellbook:
    """Return a configured, frozen book in a fresh dynamic aetheric frame named after the case."""
    configuration = SpellbookConfiguration(aether_frame=f"repro-{tag}")
    configuration.with_defaults()
    book = Spellbook(aetheric_frame=f"repro-{tag}", configuration=configuration)
    book.configure_aether_frame(system_state="dynamic", ai_native=False, rift_enabled=False,
                                system_caching_enabled=False, disposal=None, disposal_method_names=None)
    book.get_configuration().freeze()
    return book


def short(error: BaseException) -> str:
    """Return the error type and the first 600 characters of its message."""
    return f"{type(error).__name__}: {str(error)[:600]}"


def run(tag: str, plan: list) -> dict:
    """Bind every (class, spellframe, binding_name, resolvable) of plan into one book, conjure, meld each back."""
    result: dict = {"binds": [], "conjure": None, "melds": []}
    book = new_book(tag)
    root = None
    try:
        for spell, spellframe, binding_name, resolvable in plan:
            entry = {"class": spell.__qualname__, "spellframe": spellframe, "binding_name": binding_name,
                     "resolvable": resolvable}
            try:
                book.bind(spell=spell, existence="many", spellframe=spellframe, binding_name=binding_name,
                          resolvable=resolvable, disposal_method_names=[])
                entry["bind"] = "ok"
            except Exception as error:
                entry["bind"] = short(error)
            result["binds"].append(entry)
        try:
            root = book.conjure(dynamic=True, name=f"repro-root-{tag}")
            result["conjure"] = "ok"
        except Exception as error:
            result["conjure"] = short(error)
            return result
        for (spell, spellframe, binding_name, resolvable), bound in zip(plan, result["binds"]):
            if not resolvable or bound["bind"] != "ok":
                continue
            try:
                obj = root.meld(spellframe=spellframe, binding_name=binding_name)
                result["melds"].append({"address": [spellframe, binding_name], "origin": obj.origin})
            except Exception as error:
                result["melds"].append({"address": [spellframe, binding_name], "error": short(error)})
    finally:
        if root is not None:
            root.cleanup()
        book.cleanup()
    return result


cases = {
    # Bug: distinct spellframes, default binding names.
    "distinct_spellframes": [(ModuleA.Repo, "users", None, True), (ModuleB.Repo, "orders", None, True)],
    # Bug: one spellframe, distinct binding names (what the DUPLICATE_SPELL_NAME message itself advises).
    "distinct_binding_names": [(ModuleA.Repo, "repos", "a_repo", True), (ModuleB.Repo, "repos", "b_repo", True)],
    # Bug: both discriminators at once.
    "distinct_spellframes_and_binding_names": [(ModuleA.Repo, "users", "one", True),
                                               (ModuleB.Repo, "orders", "two", True)],
    # Bug: the twin is discoverable (resolvable=False), so meld can never select it, yet it still collides.
    "discoverable_twin": [(ModuleA.Repo, "users", None, True), (ModuleB.Repo, "orders", None, False)],
    # Control: two different class names at comparable addresses - passes.
    "control_different_names": [(ModuleA.Repo, "users", None, True), (Other, "orders", None, True)],
    # Control: a real signature collision (same spellframe, same binding name) - refused at bind, correctly.
    "control_same_signature": [(ModuleA.Repo, "repos", "repo", True), (ModuleB.Repo, "repos", "repo", True)],
}


def class_meld_by_name() -> dict:
    """Bind only ModuleA.Repo at its default address, then meld by the OTHER class object, ModuleB.Repo.

    Shows why the default address matters: a meld by class object with no spellframe or binding name is keyed
    by the class NAME ("repo", "__default__"), so it can return an instance of a different class of that name.
    """
    result: dict = {}
    book = new_book("class-meld")
    root = None
    try:
        book.bind(spell=ModuleA.Repo, existence="many", disposal_method_names=[])
        root = book.conjure(dynamic=True, name="repro-root-class-meld")
        obj = root.meld(spell=ModuleB.Repo)
        result["meld(spell=ModuleB.Repo)"] = {"returned_class": type(obj).__qualname__, "origin": obj.origin}
    except Exception as error:
        result["error"] = short(error)
    finally:
        if root is not None:
            root.cleanup()
        book.cleanup()
    return result


report = {"melder": melder.__version__, "python": sys.version.split()[0], "gil_enabled": sys._is_gil_enabled()}
for name, plan in cases.items():
    report[name] = run(name, plan)
report["class_meld_resolves_by_name"] = class_meld_by_name()
print(json.dumps(report, indent=1))