"""Scratch check: is the stuck consumer specific to meld(spell_id=...)? Meld it by spell_id, by class and by name."""
import sys

import melder as md


class English:
    """The provider."""

    def greet(self) -> str:
        """Return the greeting."""
        return "hello"


class ByClass:
    """The consumer: asks for English by class annotation."""

    def __init__(self, greeter: English) -> None:
        self.greeter = greeter


def show(label, call):
    """Print what call returns, or the exception type it raises."""
    try:
        print("  %-46s -> %s" % (label, call()))
    except Exception as error:
        print("  %-46s -> raises %s" % (label, type(error).__name__))


def melds(world, consumer_id, english_id=None):
    """Meld the consumer three ways, and the provider by its spell_id when given."""
    show("meld(spell_id=<ByClass id>)", lambda: type(world.meld(spell_id=consumer_id).greeter).__name__)
    show("meld(ByClass)          [by class]", lambda: type(world.meld(ByClass).greeter).__name__)
    show("meld('ByClass')        [by name]", lambda: type(world.meld("ByClass").greeter).__name__)
    if english_id is not None:
        show("meld(spell_id=<English id>)  [the provider]", lambda: type(world.meld(spell_id=english_id)).__name__)


shape = sys.argv[1]
book = md.Spellbook()
consumer_id = book.bind(spell=ByClass, existence="many", permissions="create")
world = book.conjure(dynamic=True, name="world")
print("%s, GIL %s - before English is bound:" % (shape, "on" if sys._is_gil_enabled() else "off"))
melds(world, consumer_id)
frame = {"spellframe": "langs"} if shape == "category" else {}
english_id = world.bind(spell=English, existence="many", permissions="create", **frame)
print("after binding English %s:" % ("under the category 'langs'" if frame else "bare"))
melds(world, consumer_id, english_id)
