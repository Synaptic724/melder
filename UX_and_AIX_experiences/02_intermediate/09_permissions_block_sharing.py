"""
TIER: intermediate (09)
GOAL: block, the third permission - declared today, felt when sharing
      and contracting exist (intermediate+). A beginner learns the word
      and that the book accepts it.
SURFACE EXERCISED: md.Permissions.block (declaration only)
"""
import melder as md


class PrivateInternals:
    pass


def main() -> None:
    book = md.Spellbook()
    spell_id = book.bind(spell=PrivateInternals,
                         existence="unique",
                         permissions="block")
    assert isinstance(spell_id, str)
    print("block-permission binding accepted:", spell_id[:8])
    print("NOTE: block guards SHARING flows (contracts and links) - those")
    print("      live in later tiers; local melding stays a local matter.")


if __name__ == "__main__":
    main()
