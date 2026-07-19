"""
TIER: beginner (33)
GOAL: A registry of ready-made objects - instances you built yourself,
      classified under one frame, resolved by name. The book as a
      typed, lifecycle-aware dict of singletons.
SURFACE EXERCISED: instance spells + spellframe classification
"""
import melder as md


class Palette:
    def __init__(self, name: str) -> None:
        self.name = name


def main() -> None:
    book = md.Spellbook()
    for palette in (Palette("dark"), Palette("light"), Palette("contrast")):
        book.bind(spell=palette, existence="unique",
                  permissions="read",
                  spellframe="palettes", binding_name=palette.name)
    conduit = book.conjure()

    dark = conduit.meld(spellframe="palettes", binding_name="dark")
    contrast = conduit.meld(spellframe="palettes", binding_name="contrast")
    assert dark.name == "dark" and contrast.name == "contrast"
    print("prebuilt registry served:", dark.name, "+", contrast.name)


if __name__ == "__main__":
    main()
