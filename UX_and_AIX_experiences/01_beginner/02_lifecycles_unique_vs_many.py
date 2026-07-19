"""
TIER: beginner (02)
GOAL: The one decision every binding makes - where does instance reuse
      stop? unique = one shared instance; many = fresh construction per
      meld. This is Existence, the heart of the bind vocabulary.
SURFACE EXERCISED: md.Spellbook, md.Existence.unique, md.Existence.many
"""
import melder as md


class SharedCache:
    pass


class RequestScratchpad:
    pass


def main() -> None:
    book = md.Spellbook()
    book.bind(spell=SharedCache, existence=md.Existence.unique)
    book.bind(spell=RequestScratchpad, existence=md.Existence.many)
    conduit = book.conjure()

    cache_a = conduit.meld(spell=SharedCache)
    cache_b = conduit.meld(spell=SharedCache)
    assert cache_a is cache_b
    print("unique: one instance, shared -", cache_a is cache_b)

    pad_a = conduit.meld(spell=RequestScratchpad)
    pad_b = conduit.meld(spell=RequestScratchpad)
    assert pad_a is not pad_b
    print("many: fresh instance per meld -", pad_a is not pad_b)


if __name__ == "__main__":
    main()
