"""
TIER: beginner (41)
GOAL: YOU own the memory now - not the GC. A DI runtime HOLDS what it
      builds: your `unique` instance lives in the conduit's creations
      store, so dropping YOUR variable frees nothing - Python's garbage
      collector cannot collect what the world still references. This is
      the trade every DI-style tool makes: the runtime manages your
      objects, so YOU must end their lifecycles. cleanup() is not
      ceremony - it is how memory comes back.
      This lesson PROVES it with a weakref (a watcher that answers
      "is the object still alive?" without keeping it alive).
SURFACE EXERCISED: the lifecycle law - meld, del, cleanup, and who
                   really holds the object
"""
import gc
import weakref

import melder as md


class HeavyThing:
    pass


def main() -> None:
    book = md.Spellbook()
    book.bind(spell=HeavyThing, existence="unique")
    conduit = book.conjure()

    thing = conduit.meld(spell=HeavyThing)
    watcher = weakref.ref(thing)   # watches WITHOUT holding

    # Drop OUR reference. In plain Python this object would now die...
    del thing
    gc.collect()
    print("after del, object alive?", watcher() is not None)
    assert watcher() is not None   # ...but the RUNTIME still holds it.

    # cleanup() releases the world's grip - THIS is what frees memory.
    conduit.cleanup()
    gc.collect()
    print("after cleanup, object alive?", watcher() is not None)
    assert watcher() is None

    print("the lifecycle law: the runtime holds what it builds;")
    print("cleanup() is how you give memory back")


if __name__ == "__main__":
    main()
