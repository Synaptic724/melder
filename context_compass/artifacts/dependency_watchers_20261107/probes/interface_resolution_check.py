"""Scratch check: how Melder resolves a spell filed under a Protocol spellframe - by frame, by class, by injection."""
import sys
from typing import Protocol

import melder as md


class Greeter(Protocol):
    """The interface."""

    def greet(self) -> str: ...


class English:
    """Implementation 1."""

    def greet(self) -> str:
        """Return the English greeting."""
        return "hello"


class French:
    """Implementation 2."""

    def greet(self) -> str:
        """Return the French greeting."""
        return "bonjour"


class ByProtocol:
    """Injected by the interface."""

    def __init__(self, greeter: Greeter) -> None:
        self.greeter = greeter


class ByClass:
    """Injected by the concrete class."""

    def __init__(self, greeter: English) -> None:
        self.greeter = greeter


def show(label, call):
    """Print what call returns, or the exception type, first line and codes it raises."""
    try:
        print("  %-58s -> %s" % (label, call()))
    except Exception as error:
        text = str(error)
        code = text[text.rfind("[") + 1:text.rfind("]")] if "]" in text[-60:] else ""
        print("  %-58s -> raises %s%s" % (label, type(error).__name__, (" [%s]" % code) if code else ""))


def name(obj):
    """Class name of an object."""
    return type(obj).__name__


def bind(target, spell, **frame):
    """Bind as many/create."""
    return target.bind(spell=spell, existence="many", permissions="create", **frame)


case = sys.argv[1]
print(case)
book = md.Spellbook()
if case == "one_impl_no_binding_name":
    bind(book, English, spellframe=Greeter)
elif case == "one_impl_with_binding_name":
    bind(book, English, spellframe=Greeter, binding_name="english")
elif case == "two_impls_with_binding_names":
    bind(book, English, spellframe=Greeter, binding_name="english")
    bind(book, French, spellframe=Greeter, binding_name="french")
elif case == "two_impls_no_binding_names":
    bind(book, English, spellframe=Greeter)
    show("bind French under Greeter too (no binding name)", lambda: (bind(book, French, spellframe=Greeter), "ok")[1])
world = book.conjure(dynamic=True, name="world")
show("meld(spellframe=Greeter)", lambda: name(world.meld(spellframe=Greeter)))
if case != "one_impl_no_binding_name":
    show("meld(spellframe=Greeter, binding_name='english')",
         lambda: name(world.meld(spellframe=Greeter, binding_name="english")))
show("meld(English)  [the concrete class]", lambda: name(world.meld(English)))
show("bind ByProtocol (greeter: Greeter), meld it",
     lambda: (bind(world, ByProtocol), name(world.meld(ByProtocol).greeter))[1])
show("bind ByClass (greeter: English), meld it",
     lambda: (bind(world, ByClass), name(world.meld(ByClass).greeter))[1])
