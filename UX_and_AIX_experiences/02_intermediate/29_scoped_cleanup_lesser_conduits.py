"""
TIER: intermediate (29)
GOAL: Scopes that END. A lesser conduit is a scope you can THROW AWAY:
      build one for a job, meld what the job needs, then cleanup() the
      child - its per-conduit creations are disposed through the book's
      disposal vocabulary, and the root keeps working untouched.
      THE LIFECYCLE LAW: with a DI runtime YOU own the lifecycles. The
      runtime holds references to what it built, so the GC cannot free
      what the world still holds - cleanup() is how memory comes back.
      (Beginner lesson 41 proves this with a weakref; here it becomes a
      working pattern.)
SURFACE EXERCISED: create_lesser_conduit as a disposable scope,
                   conduit.cleanup() on the child only,
                   disposal_method_names firing scope-locally
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))  # local helper (see _dynamic_world)
from _dynamic_world import dynamic_spellbook

import melder as md


class JobSession:
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True


def main() -> None:
    book = md.Spellbook()
    book.bind(spell=JobSession, existence="unique_per_conduit",
              disposal_method_names=["close"])
    root = book.conjure()

    # The long-lived scope holds its own session...
    root_session = root.meld(spell=JobSession)

    # ...and each job gets a THROWAWAY scope with its own.
    job = root.create_lesser_conduit()
    job_session = job.meld(spell=JobSession)
    assert job_session is not root_session  # per-conduit = per-scope

    # Job done: end the SCOPE, not the world.
    job.cleanup()
    print("job scope closed its session:", job_session.closed)
    print("root session untouched:", root_session.closed is False)

    # The root never noticed - it keeps resolving.
    assert root.meld(spell=JobSession) is root_session
    print("root still resolves after the child scope ended")

    # And when the whole world is done, the same verb one level up.
    root.cleanup()
    print("root cleanup closed its session too:", root_session.closed)


if __name__ == "__main__":
    main()
