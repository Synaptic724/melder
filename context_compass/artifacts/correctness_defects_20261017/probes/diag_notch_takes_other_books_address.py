"""Diagnostic (melder_1, 2026-10-24): can a notch in Book L take an address Book O's active spell holds? Public calls."""
import sys
from typing import Protocol

import melder as md


class Greeter(Protocol):
    def greet(self) -> str: ...


class English:
    def greet(self) -> str:
        return "hello"


class Spanish:
    def greet(self) -> str:
        return "hola"


class French:
    def greet(self) -> str:
        return "bonjour"


class Italian:
    def greet(self) -> str:
        return "ciao"


def show(label, call):
    try:
        print("  %s -> %s" % (label, call()))
    except Exception as error:
        print("  %s -> raises %s: %s" % (label, type(error).__name__, str(error).splitlines()[0][:200]))


def bind(book, cls, name):
    return book.bind(spell=cls, spellframe=Greeter, binding_name=name, existence="many", permissions="create")


def greeting(conduit, **where):
    obj = conduit.meld(**where)
    return "%s says %r" % (type(obj).__name__, obj.greet())


compiled_before = len(sys.argv) > 1 and sys.argv[1] == "compiled"
book_o = md.Spellbook()
spanish_id = bind(book_o, Spanish, "spanish")
other = book_o.conjure(dynamic=True, name="other")
book_l = md.Spellbook()
english_id = bind(book_l, English, "greeter")
lender = book_l.conjure(dynamic=True, name="lender")
index = lender.get_spell_by_spell_id(english_id).spell_index
french_id = lender.bind_inactive(spell=French, spell_index=index, spellframe=Greeter, binding_name="spanish",
                                 existence="many", permissions="create")
print("case: Book O has Spanish active at 'spanish'; Book L stages French at 'spanish' on English's index"
      + (" (French compiled before)" if compiled_before else ""))
if compiled_before:
    show("Book L notch to French", lambda: lender.notch_spell(spell_index=index, spell_id=french_id).spell_name)
    show("Book L notch back to English", lambda: lender.notch_spell(spell_index=index, spell_id=english_id).spell_name)
show("Book L notch to French", lambda: lender.notch_spell(spell_index=index, spell_id=french_id).spell_name)
show("Book L meld at 'spanish'", lambda: greeting(lender, spellframe=Greeter, binding_name="spanish"))
show("Book O meld at 'spanish'", lambda: greeting(other, spellframe=Greeter, binding_name="spanish"))
show("a third Book binds Italian at 'spanish'", lambda: bind(md.Spellbook(), Italian, "spanish")[:12])
show("tear Book L's root down", lambda: lender.cleanup())
show("a third Book binds Italian at 'spanish' (after L's teardown)", lambda: bind(md.Spellbook(), Italian, "spanish")[:12])
show("Book O meld at 'spanish'", lambda: greeting(other, spellframe=Greeter, binding_name="spanish"))
