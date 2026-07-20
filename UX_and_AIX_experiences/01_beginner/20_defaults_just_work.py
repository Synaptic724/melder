"""
TIER: beginner (20)
GOAL: Your constructor defaults ARE the configuration - a class with
      default arguments melds without any extra setup. melder calls
      YOUR __init__; Python fills the defaults.
SURFACE EXERCISED: plain constructor defaults through meld
"""
import melder as md


class HttpClient:
    def __init__(self, timeout: int = 30, retries: int = 3) -> None:
        self.timeout = timeout
        self.retries = retries


def main() -> None:
    book = md.Spellbook()
    book.bind(spell=HttpClient, existence="unique")
    conduit = book.conjure()

    client = conduit.meld(spell=HttpClient)
    assert (client.timeout, client.retries) == (30, 3)
    print("defaults arrived untouched:", client.timeout, client.retries)


if __name__ == "__main__":
    main()
