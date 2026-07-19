"""
TIER: beginner (33)
GOAL: A registry of ready-made same-typed objects. Spell names must be
      unique per book (probe-proven), so N instances of one class bind
      as ONE registry spell - the dict is the spell, lookup stays yours.
SURFACE EXERCISED: collection-as-instance-spell, read permission
"""
import melder as md


class Palette:
    def __init__(self, name: str) -> None:
        self.name = name


def main() -> None:
    book = md.Spellbook()
    palettes = {p.name: p for p in
                (Palette("dark"), Palette("light"), Palette("contrast"))}
    book.bind(spell=palettes, existence="unique",
              spellframe="ui", binding_name="palettes")
    conduit = book.conjure()

    registry = conduit.meld(spellframe="ui", binding_name="palettes")
    assert registry is palettes
    assert registry["dark"].name == "dark"
    print("registry spell served:", sorted(registry))


if __name__ == "__main__":
    main()
