"""
TIER: beginner (17)
GOAL: unique_per_spell_space - DECLARED here, LIVED later: spellspaces
      are entered resolution rooms (an intermediate-tier feature). The
      beginner takeaway is only the vocabulary: this mode pins one
      instance per room, and the book accepts the declaration today.
SURFACE EXERCISED: md.Existence.unique_per_spell_space (declaration only)
"""
import melder as md


class RoomState:
    pass


def main() -> None:
    book = md.Spellbook()
    spell_id = book.bind(
        spell=RoomState,
        existence=md.Existence.unique_per_spell_space,
    )
    assert isinstance(spell_id, str)
    print("space-scoped binding accepted at bind time:", spell_id[:8])
    print("NOTE: entering spellspaces and melding inside them is the")
    print("      intermediate tier - beginner stays with plain conduits.")


if __name__ == "__main__":
    main()
