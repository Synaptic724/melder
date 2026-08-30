"""
TIER: advanced (19)
GOAL: THE OTHER TWO OVERRIDE FORMS. Lesson 01 taught the PATH form -
      "transport>credentials" - which names a socket exactly. There are
      three targeting forms in total, and melder states all of them:

        PATH       a>b>c     name the socket exactly
        UNIQUE     *param    "there is exactly one of these, find it"
        BROADCAST  **param   "hit every one"

      You still pass a plain dict to meld(override=...). The
      grammar lives in the KEY.

      WHY THE OTHER TWO EXIST
      A path requires you to know the shape of a graph you did not build.
      `*credentials` says "somewhere below this root there is exactly one
      credentials socket - I do not care where". `**credentials` says
      "there may be several and I mean all of them".

      AND HERE IS THE PART THAT MAKES THEM SAFE TO USE.

      THE MATCH COUNTS ARE ENFORCED, NOT ADVISORY.
        *param   requires EXACTLY ONE match
        **param  requires AT LEAST ONE match
      Miss the count and resolution REFUSES. It does not apply your
      override to the first thing it found, and it does not quietly do
      nothing.

      melder's own reasoning, which is worth reading twice:

        "a `*param` that silently matched three sockets, or zero, would
         apply the caller's intent to the wrong object or to nothing at
         all, and BOTH FAIL INVISIBLY AT RUNTIME rather than at
         resolution. Failing loudly at map time is the whole point of
         resolving specs up front instead of during construction."

      That is the never-substitute rule (lessons 06/11/12/15/16) applied
      to targeting. A wildcard that guessed would be the worst kind of
      bug: your fixture lands on the wrong object and everything appears
      to work.

      PRECEDENCE
      A `**param` broadcast and an exact `a>b>c` path can both name the
      same socket. When they overlap, specificity decides - the exact
      path wins over the broadcast. Being more specific means being more
      authoritative, which is the only ordering that would not surprise
      someone.

      THE LIFETIME RULE STILL APPLIES (lesson 01's sharp edge)
      An override is surgical in WHERE it reaches, not in HOW LONG it
      lasts. Override into `unique` and you have changed the world.
      Everything below is bound `many` so each meld builds its own graph
      and the fixtures cannot escape the call.
SURFACE EXERCISED: meld(override={"*param": obj}) and {"**param": obj}
VERIFY: rides the owner's 3.14t run; asserts are the contract.

NOTE ON WHAT IS NOT TAUGHT HERE: `SpellOverrider` is the runtime helper
that maps this payload onto real sockets. It is marked AGENT_ACCESS:
internal - "users supply the override PAYLOAD, never this object" - so
this lesson teaches the DICT and never touches the class.
"""
import melder as md


class Credentials:
    def __init__(self) -> None:
        self.source = "vault"


class Transport:
    def __init__(self, credentials: Credentials) -> None:
        self.credentials = credentials


class Archive:
    def __init__(self, credentials: Credentials) -> None:
        self.credentials = credentials


class MailPipeline:
    """One credentials socket below the root, reached through transport."""

    def __init__(self, transport: Transport) -> None:
        self.transport = transport


class BackupPipeline:
    """TWO credentials sockets below the root - transport and archive."""

    def __init__(self, transport: Transport, archive: Archive) -> None:
        self.transport = transport
        self.archive = archive


def _book() -> md.Spellbook:
    # `many` throughout: every meld builds its own graph, so the fixtures
    # below cannot outlive the call that used them (lesson 01's edge).
    book = md.Spellbook(aetheric_frame="override-grammar")
    for spell in (Credentials, Transport, Archive, MailPipeline,
                  BackupPipeline):
        book.bind(spell=spell, existence="many")
    return book


def main() -> None:
    conduit = _book().conjure(name="override-root")

    fixture = Credentials()
    fixture.source = "test-fixture"

    # UNIQUE - *param. MailPipeline has exactly ONE credentials socket
    # under it, so the wildcard resolves without naming the path.
    mail = conduit.meld(
        spell=MailPipeline,
        override={"*credentials": fixture},
    )
    assert mail.transport.credentials is fixture
    print("*credentials found the single socket:",
          mail.transport.credentials.source)

    # ...and the same spec against a root with TWO matching sockets is
    # REFUSED. "exactly one" is a requirement, not a preference - this is
    # the whole reason the form is safe to reach for.
    try:
        conduit.meld(
            spell=BackupPipeline,
            override={"*credentials": fixture},
        )
        raise AssertionError("expected a refusal - *param matched twice")
    except Exception as error:
        print("*credentials refused two matches:", type(error).__name__)

    # BROADCAST - **param. Same graph, and now hitting every match is
    # exactly what was asked for.
    backup = conduit.meld(
        spell=BackupPipeline,
        override={"**credentials": fixture},
    )
    assert backup.transport.credentials is fixture
    assert backup.archive.credentials is fixture
    print("**credentials hit both sockets:",
          backup.transport.credentials.source,
          "/", backup.archive.credentials.source)

    # A broadcast that matches NOTHING is refused too - "at least one" is
    # also enforced. A no-op override is a caller mistake, not a default.
    try:
        conduit.meld(
            spell=MailPipeline,
            override={"**nosuchparam": fixture},
        )
        raise AssertionError("expected a refusal - **param matched nothing")
    except Exception as error:
        print("**nosuchparam refused zero matches:", type(error).__name__)

    # PRECEDENCE. Broadcast everything, then name one socket exactly - the
    # exact path is MORE SPECIFIC and wins where the two overlap.
    specific = Credentials()
    specific.source = "archive-only"
    mixed = conduit.meld(
        spell=BackupPipeline,
        override={
            "**credentials": fixture,
            "archive>credentials": specific,
        },
    )
    assert mixed.transport.credentials is fixture
    assert mixed.archive.credentials is specific
    print("overlap resolved by specificity - transport:",
          mixed.transport.credentials.source,
          "| archive:", mixed.archive.credentials.source)

    # `many` kept the blast radius inside the call: a plain meld gets a
    # clean graph with no fixture in it.
    clean = conduit.meld(spell=BackupPipeline)
    assert clean.transport.credentials is not fixture
    assert clean.archive.credentials.source == "vault"
    print("plain meld is untouched:", clean.archive.credentials.source)

    print()
    print("three forms: exact path, *one, **all - the grammar is in the key")
    print("match counts are ENFORCED - a guessing wildcard would fail silently")


if __name__ == "__main__":
    main()
