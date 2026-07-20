"""
TIER: intermediate (21)
GOAL: Configuring a dynamic world END TO END, in the open - melder has
      TWO configuration layers and dynamic mode is where you meet both:
      the WORLD posture (AethericFrameConfiguration: is this world
      allowed to be dynamic?) and the BOOK configuration
      (SpellbookConfiguration: how does this book behave?). Then link()
      opens a contract and add_spell_to_contract shares one spell
      across it. Later lessons wrap this ritual in a helper so they can
      focus - THIS lesson is the ritual.
SURFACE EXERCISED: md.AethericFrameConfiguration, md.SystemState,
                   md.SpellbookConfiguration, conjure(dynamic=True),
                   link, add_spell_to_contract
"""
import melder as md


class SharedDirectory:
    def lookup(self) -> str:
        return "found"


def build_dynamic_book() -> md.Spellbook:
    # LAYER 1 - the world posture. Dynamic behavior is a WORLD decision,
    # not a book decision: the hosting world must allow it before any
    # book can conjure dynamically. system_state is the switch.
    posture = md.AethericFrameConfiguration(
        origin_spellbook_id=None,
        system_state=md.SystemState.dynamic,
        ai_native_enabled=False,   # AI-native rooms are a later tier
        rift_enabled=False,        # AR is a later tier
    )
    md.Aether()._ensure_frame("default").bind_frame_configuration(posture)

    # LAYER 2 - the book configuration. Defaults, then any knobs you
    # want (lesson 19 covers these); conjure freezes it.
    configuration = md.SpellbookConfiguration()
    configuration.with_defaults()
    return md.Spellbook(configuration=configuration)


def main() -> None:
    owner_book = build_dynamic_book()
    spell_id = owner_book.bind(spell=SharedDirectory, existence="unique")
    owner = owner_book.conjure(dynamic=True, name="owner")

    borrower = build_dynamic_book().conjure(dynamic=True, name="borrower")
    assert owner.link(borrower) is True
    owner.add_spell_to_contract(spell_id=spell_id, conduit=borrower,
                                permissions="create")

    shared = borrower.meld(spell=SharedDirectory)
    print("borrower melded the owner's spell:", shared.lookup())
    print("two config layers: world posture (dynamic) + book config (frozen)")


if __name__ == "__main__":
    main()
