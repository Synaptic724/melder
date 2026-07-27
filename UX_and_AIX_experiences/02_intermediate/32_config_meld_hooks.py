"""
TIER: intermediate (32)
GOAL: SpellbookConfiguration hooks, family 1: the MELD PIPELINE.
      add_hook(spellbook_id, name, fn) registers callbacks keyed to a
      BOOK - the configuration can serve many books, so hooks say whose
      melds they watch. Two hook points:
        on_meld_pre_resolve  - before resolution
        on_meld_post_resolve - after the instance is handed back
      Hooks observe; they do not replace resolution.
SURFACE EXERCISED: add_hook, on_meld_pre_resolve, on_meld_post_resolve
"""
import melder as md


class Watched:
    pass


def main() -> None:
    events = []

    book = md.Spellbook()
    config = book.get_configuration()
    config.add_hook(book.id, "on_meld_pre_resolve",
                    lambda *a, **k: events.append("pre"))
    config.add_hook(book.id, "on_meld_post_resolve",
                    lambda *a, **k: events.append("post"))

    book.bind(spell=Watched, existence="many")
    conduit = book.conjure()

    conduit.meld(spell=Watched)
    conduit.meld(spell=Watched)
    print("meld pipeline observed:", events)
    assert events.count("pre") >= 2 and events.count("post") >= 2
    print("every meld fired pre and post - the pipeline is watchable")


if __name__ == "__main__":
    main()
