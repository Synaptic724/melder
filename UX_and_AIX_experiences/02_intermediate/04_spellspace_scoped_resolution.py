"""
TIER: intermediate (04)
GOAL: Spellspaces are entered resolution rooms - one conduit can open
      many, and unique_per_spell_space pins one instance per room:
      stable inside a space, separate across spaces.
SURFACE EXERCISED: md.Conduit.enter_spellspace, md.SpellSpace,
                   md.Existence.unique_per_spell_space
"""
import melder as md


class RoomState:
    pass


def main() -> None:
    book = md.Spellbook()
    book.bind(spell=RoomState, existence=md.Existence.unique_per_spell_space)
    conduit = book.conjure()

    space_one = conduit.enter_spellspace()
    space_two = conduit.enter_spellspace()
    assert isinstance(space_one, md.SpellSpace)

    one_a = space_one.meld(spell=RoomState)
    one_b = space_one.meld(spell=RoomState)
    two_a = space_two.meld(spell=RoomState)
    print("stable within a space:", one_a is one_b)
    print("separate across spaces:", one_a is not two_a)


if __name__ == "__main__":
    main()
