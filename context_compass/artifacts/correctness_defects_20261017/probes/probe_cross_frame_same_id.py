"""
Under process-wide spell ids (the default), what happens when one class is bound at one address in two frames:
at bind, and at the second frame's conjure. Checks the claim in S6's patch docs ("now a duplicate, as for any other
spell") before the release note repeats it.

C1 a plain unique class, equal options, both frames conjured.
C2 a managed class with equal settings, both frames conjured.
C3 a managed class with another limit in frame b (one spell_id since 0.2.8254), both frames conjured.
C4 the same, frame a conjured before frame b binds: bind's cross-frame check refuses it.
Run from this artifacts folder with PYTHONPATH=<repo>/src, under -X gil=0 and -X gil=1.
"""
import melder as md
from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.spellbook import Spellbook


class Plain:
    """A plain unique class."""


class Parser:
    """A managed class."""


def fresh_world() -> None:
    """Install a fresh Aether so each case starts from nothing."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def case(label: str, options_a: dict, options_b: dict) -> None:
    """Bind in frame 'a' and 'b', then conjure both; print where (if anywhere) it is refused."""
    fresh_world()
    book_a = md.Spellbook(aetheric_frame="a")
    book_b = md.Spellbook(aetheric_frame="b")
    roots = []
    try:
        sid_a = book_a.bind(**options_a)
        try:
            sid_b = book_b.bind(**options_b)
        except RuntimeError as error:
            print(label, "bind in b refused:", str(error).split(".")[0] + ".")
            return
        print(label, "bound in both; same spell_id:", sid_a == sid_b)
        for name, book in (("a", book_a), ("b", book_b)):
            try:
                roots.append(book.conjure(name=f"root-{name}"))
                print(label, f"conjure {name}: ok")
            except Exception as error:  # report the type and first line, whatever it is
                print(label, f"conjure {name} raised {type(error).__name__}:", str(error).splitlines()[0][:150])
        for root in roots:
            print(label, f"meld through {root.name}:", type(root.meld(spell_id=sid_a)).__name__)
    finally:
        for root in roots:
            root.cleanup()
        book_b.cleanup()
        book_a.cleanup()


def case_c4(options_a: dict, options_b: dict) -> None:
    """Conjure frame a's Book first, then bind in frame b: the cross-frame check sees the conjured spell."""
    fresh_world()
    book_a = md.Spellbook(aetheric_frame="a")
    book_a.bind(**options_a)
    root_a = book_a.conjure(name="root-a")
    book_b = md.Spellbook(aetheric_frame="b")
    try:
        book_b.bind(**options_b)
        print("C4 managed other limit, a conjured first: bind in b accepted")
    except RuntimeError as error:
        print("C4 managed other limit, a conjured first: bind in b refused:", str(error).split(".")[0] + ".")
    finally:
        book_b.cleanup()
        root_a.cleanup()
        book_a.cleanup()


if __name__ == "__main__":
    print("process-wide spell ids:", Aether().process_wide_unique_spell_ids)
    plain = dict(spell=Plain, existence="unique")
    case("C1 plain", plain, plain)
    managed_1 = dict(spell=Parser, existence="managed_spell_quantity",
                     managed_spell_mode="limited_quantity", managed_spell_limit=1)
    managed_2 = dict(managed_1, managed_spell_limit=2)
    case("C2 managed equal", managed_1, managed_1)
    case("C3 managed other limit", managed_1, managed_2)
    case_c4(managed_1, managed_2)
