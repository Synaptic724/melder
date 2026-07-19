"""
TIER: beginner (16)
GOAL: Type hints and melding are friends - annotate what you meld and
      your editor (and your agent) knows every attribute from there on.
      melder ships py.typed, so checkers see real types, not Any.
SURFACE EXERCISED: meld with annotations, the typed root namespace
"""
import melder as md


class WeatherService:
    def today(self) -> str:
        return "sunny, 24C"


def main() -> None:
    book: md.Spellbook = md.Spellbook()
    book.bind(spell=WeatherService, existence="unique")
    conduit: md.Conduit = book.conjure()

    weather: WeatherService = conduit.meld(spell=WeatherService)
    report: str = weather.today()
    assert report == "sunny, 24C"
    print("typed end to end:", report)
    print("hint: annotate melds - autocomplete does the remembering for you")


if __name__ == "__main__":
    main()
