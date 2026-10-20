"""
Release-note check for S6 part A (0.2.8254): the example in the managed section runs as written, and the
cross-frame claim holds under process-wide spell ids.

E1  the release-note example: limited_quantity limit 1, cleanup_spell, bind again with limit 2 -> the same
    spell_id, a second object leases, the first goes back to the same pool, counted.
E2  a settings-only re-stage on the index is refused ("Spell ID collision detected") and nothing changes.
X1  process-wide spell ids (the default): the same managed class at the same address bound in a second frame with
    another limit is refused as a duplicate.
X2  the same with equal settings (the pre-existing rule for any spell).
Run from this artifacts folder with PYTHONPATH=<repo>/src, under -X gil=0 and -X gil=1.
"""
import melder as md
from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.spellbook import Spellbook


class Parser:
    """The managed class of the example."""

    def close(self) -> None:
        """A disposal method, as a pooled class would have."""


def fresh_world() -> None:
    """Install a fresh Aether so each case starts from nothing."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def case_e1() -> None:
    """The release-note example, as written there."""
    fresh_world()
    book = md.Spellbook()
    sid = book.bind(spell=Parser, existence="managed_spell_quantity",
                    managed_spell_mode="limited_quantity", managed_spell_limit=1)
    root = book.conjure(dynamic=True, name="parsers")

    parser = root.meld(spell_id=sid)
    root.cleanup_spell(spell=root.get_spell_by_spell_id(sid))   # the pool stays, with the parser out
    assert root.bind(spell=Parser, existence="managed_spell_quantity",
                     managed_spell_mode="limited_quantity", managed_spell_limit=2) == sid   # the same spell
    second = root.meld(spell_id=sid)                  # limit 2 now: a second parser
    md.ReleaseManagedSpell().release(parser)          # back to the same pool, counted

    (entry,) = md.ReleaseManagedSpell().describe(Parser)
    print("E1 same spell_id: True; second is a new object:", second is not parser,
          "; describe:", {key: entry[key] for key in ("limit", "count", "idle_count", "out_count")})
    root.cleanup()
    book.cleanup()


def case_e2() -> None:
    """A settings-only re-stage on the index is the same spell: refused, nothing changes."""
    fresh_world()
    book = md.Spellbook()
    sid = book.bind(spell=Parser, existence="managed_spell_quantity",
                    managed_spell_mode="limited_quantity", managed_spell_limit=1)
    root = book.conjure(dynamic=True, name="parsers")
    index = root.get_spell_by_spell_id(sid).spell_index
    try:
        root.bind_inactive(spell=Parser, spell_index=index, existence="managed_spell_quantity",
                           managed_spell_mode="limited_quantity", managed_spell_limit=2)
        print("E2 NOT refused")
    except RuntimeError as error:
        print("E2 refused:", str(error).split(".")[0] + ".", "; members unchanged:",
              index.spells_in_index() == {sid})
    root.cleanup()
    book.cleanup()


def case_cross_frame(label: str, second_limit: int) -> None:
    """Bind Parser managed at one address in frame 'a', then in frame 'b' with `second_limit`."""
    fresh_world()
    first = md.Spellbook(aetheric_frame="a")
    sid = first.bind(spell=Parser, existence="managed_spell_quantity",
                     managed_spell_mode="limited_quantity", managed_spell_limit=1)
    second = md.Spellbook(aetheric_frame="b")
    try:
        other = second.bind(spell=Parser, existence="managed_spell_quantity",
                            managed_spell_mode="limited_quantity", managed_spell_limit=second_limit)
        print(label, "NOT refused; same spell_id:", other == sid)
    except RuntimeError as error:
        print(label, "refused:", str(error).split(".")[0] + ".")
    second.cleanup()
    first.cleanup()


if __name__ == "__main__":
    print("process-wide spell ids:", Aether().process_wide_unique_spell_ids)
    case_e1()
    case_e2()
    case_cross_frame("X1 (another limit)", 2)
    case_cross_frame("X2 (equal settings)", 1)
