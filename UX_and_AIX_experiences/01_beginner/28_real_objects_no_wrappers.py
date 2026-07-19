"""
TIER: beginner (28)
GOAL: Melded objects are YOUR objects - no proxies, no wrappers, no
      magic subclasses. What comes back IS the instance: identity checks
      hold, isinstance holds, and it works everywhere a plain object
      works. Many DI containers wrap; melder hands you the real thing.
SURFACE EXERCISED: instance identity through meld
"""
import melder as md


class Engine:
    cylinders = 8


def main() -> None:
    book = md.Spellbook()
    book.bind(spell=Engine, existence="unique")
    conduit = book.conjure()

    engine = conduit.meld(spell=Engine)
    assert type(engine) is Engine
    assert isinstance(engine, Engine) and engine.cylinders == 8
    assert engine is conduit.meld(spell=Engine)
    print("the real object, every time:", type(engine).__name__)


if __name__ == "__main__":
    main()
