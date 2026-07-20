"""
TIER: intermediate (21)
GOAL: Configuring a dynamic world END TO END, in the open. Three ideas:
      1) The WORLD is postured dynamic ONCE - and it locks. You never
         configure the world again; every book after that just attaches.
      2) Each BOOK carries its own SpellbookConfiguration (lesson 19).
      3) conjure(dynamic=True) is the PER-CONDUIT opt-in: it registers
         the named root in the world's phone book and arms link/sever
         for that conduit. World permission once; conduit opt-in each.
      Then link() opens a contract and add_spell_to_contract shares one
      spell across it. Lessons 22-25 wrap step 1 in a helper.
SURFACE EXERCISED: md.AethericFrameConfiguration (once), md.SystemState,
                   md.SpellbookConfiguration, conjure(dynamic=True),
                   link, add_spell_to_contract
"""
import melder as md


class SharedDirectory:
    def lookup(self) -> str:
        return "found"


def posture_world_dynamic() -> None:
    # STEP 1 - ONCE PER WORLD, then it locks. Dynamic is a world
    # decision; the world must permit it before any conduit can opt in.
    md.Aether()._ensure_frame("default").bind_frame_configuration(
        md.AethericFrameConfiguration(
            origin_spellbook_id=None,
            system_state=md.SystemState.dynamic,
            ai_native_enabled=False,   # later tier
            rift_enabled=False,        # later tier
        )
    )


def build_book() -> md.Spellbook:
    # STEP 2 - per book: its own configuration (see lesson 19).
    configuration = md.SpellbookConfiguration()
    configuration.with_defaults()
    return md.Spellbook(configuration=configuration)


def main() -> None:
    posture_world_dynamic()  # once - the world is now permanently dynamic

    owner_book = build_book()
    spell_id = owner_book.bind(spell=SharedDirectory, existence="unique")
    # STEP 3 - per conduit: dynamic=True opts THIS root in (named +
    # linkable); a permissive world can still host plain static roots.
    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower = build_book().conjure(dynamic=True, name="borrower")

    assert owner.link(borrower) is True
    owner.add_spell_to_contract(spell_id=spell_id, conduit=borrower,
                                permissions="create")
    shared = borrower.meld(spell=SharedDirectory)
    print("borrower melded the owner's spell:", shared.lookup())
    print("world postured once (locked); each conduit opted in at conjure")


if __name__ == "__main__":
    main()
