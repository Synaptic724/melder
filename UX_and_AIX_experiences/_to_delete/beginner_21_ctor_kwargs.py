"""
TIER: beginner (21)
GOAL: Constructor arguments travel WITH the registration - bind-time kwargs
      are handed to __init__ at meld time. Configuration lives at the
      bind site, not the call site.
SURFACE EXERCISED: bind(**ctor_kwargs)
"""
import melder as md


class SmtpMailer:
    def __init__(self, host: str = "", port: int = 0) -> None:
        self.host = host
        self.port = port


def main() -> None:
    book = md.Spellbook()
    book.bind(
        spell=SmtpMailer,
        existence="unique",
        host="smtp.example.com",
        port=2525,
    )
    conduit = book.conjure()
    mailer = conduit.meld(spell=SmtpMailer)
    assert (mailer.host, mailer.port) == ("smtp.example.com", 2525)
    print("bind-site kwargs arrived in __init__:", mailer.host, mailer.port)


if __name__ == "__main__":
    main()
