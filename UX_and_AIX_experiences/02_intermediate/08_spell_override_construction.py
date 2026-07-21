"""
TIER: intermediate (08)
GOAL: Two honest ways to construct with configuration: a factory that
      closes over its config (bind-site), and spell_override at meld -
      a FLAT dict of keyword overrides for the melded spell's OWN
      constructor. Simple and top-level on purpose; targeting objects
      DEEPER in the graph is an advanced-tier lesson.
      (bind(**kwargs) is a different channel entirely: it lands on
      spell.metadata - lesson 06.)
SURFACE EXERCISED: factory spells, meld(spell_override={...})
"""
import melder as md


class SmtpMailer:
    def __init__(self, host: str = "localhost", port: int = 25) -> None:
        self.host = host
        self.port = port


def production_mailer() -> SmtpMailer:
    return SmtpMailer(host="smtp.example.com", port=2525)


def main() -> None:
    book = md.Spellbook()
    book.bind(spell=production_mailer, existence="unique",
              spellframe="mail", binding_name="mailer")
    book.bind(spell=SmtpMailer, existence="many",
              spellframe="mail", binding_name="raw-mailer")
    conduit = book.conjure()

    mailer = conduit.meld(spellframe="mail", binding_name="mailer")
    assert (mailer.host, mailer.port) == ("smtp.example.com", 2525)
    print("factory-configured:", mailer.host, mailer.port)

    overridden = conduit.meld(
        spellframe="mail", binding_name="raw-mailer",
        spell_override={"host": "smtp.test.local", "port": 1025},
    )
    assert (overridden.host, overridden.port) == ("smtp.test.local", 1025)
    print("meld-site override:", overridden.host, overridden.port)


if __name__ == "__main__":
    main()
