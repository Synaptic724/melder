"""
TIER: advanced (02)
GOAL: Deep spell_override - the ">"-path form. A path of parameter
      names walks the dependency graph from the melded root and
      REPLACES the actual object at that socket:
          spell_override={"transport>credentials": my_object}
      Untargeted sockets keep their DI-resolved defaults; a path that
      matches nothing refuses. This is the surgical form - injecting a
      fixture or a variant into the MIDDLE of a real graph at meld time
      without rebinding anything. The simple top-level form (flat dict
      into the root's own constructor) is intermediate lesson 08.
SURFACE EXERCISED: meld(spell_override={"path>to>socket": object})
"""
import melder as md


class Credentials:
    def __init__(self) -> None:
        self.source = "vault"


class Transport:
    def __init__(self, credentials: Credentials) -> None:
        self.credentials = credentials


class MailPipeline:
    def __init__(self, transport: Transport) -> None:
        self.transport = transport


def main() -> None:
    book = md.Spellbook()
    book.bind(spell=Credentials, existence="unique")
    book.bind(spell=Transport, existence="unique")
    book.bind(spell=MailPipeline, existence="unique")
    conduit = book.conjure()

    # The path walks parameter names from the melded root:
    # MailPipeline(transport=...) -> Transport(credentials=...).
    test_credentials = Credentials()
    test_credentials.source = "test-fixture"
    pipeline = conduit.meld(
        spell=MailPipeline,
        spell_override={"transport>credentials": test_credentials},
    )
    assert pipeline.transport.credentials is test_credentials
    print("replaced a spell two levels deep:",
          pipeline.transport.credentials.source)

    # Untouched melds keep the DI-built world.
    plain = conduit.meld(spell=Transport)
    assert plain.credentials.source == "vault"
    print("untargeted resolution untouched:", plain.credentials.source)


if __name__ == "__main__":
    main()
