"""
TIER: advanced (01)
GOAL: Deep spell_override - the ">"-path form. A path of parameter
      names walks the dependency graph from the melded root and
      REPLACES the actual object at that socket:
          spell_override={"transport>credentials": my_object}
      Untargeted sockets keep their DI-resolved defaults WITHIN the call; a
      path that matches nothing refuses. But read the second half of this
      lesson before you reach for it: under a singleton lifetime the
      overridden meld BUILDS the singleton, so the substitution outlives the
      call that made it. This is the surgical form - injecting a
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

    # THE SHARP EDGE - the half of this surface that will bite you.
    # Every spell here is bound `unique`: one instance per frame. The meld
    # above did not build a private throwaway graph. It CONSTRUCTED the
    # singleton Transport - around your fixture - and registered it as the
    # canonical one. The override therefore did not end when the call did.
    plain = conduit.meld(spell=Transport)
    assert plain is pipeline.transport
    assert plain.credentials.source == "test-fixture"
    print("the override BUILT the singleton; later melds reuse it:",
          plain.credentials.source)

    # THE RULE: an override is surgical in WHERE it reaches, not in HOW LONG
    # it lasts. Its lifetime is the lifetime of whatever it helped build.
    # Override into `unique` and you have changed the world; override into
    # `many` and you have changed one call. If you want a fixture that cannot
    # escape, bind the target `many` so every meld constructs its own.


if __name__ == "__main__":
    main()
