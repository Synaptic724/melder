"""
TIER: intermediate (39)
GOAL: Release objects you no longer need while their scope keeps working.
      This job buffer declares close as its disposal method, so Melder retains
      each many creation until explicit disposal. Pass an instance with
      purge_all=False to retire only that object. The default purge_all=True
      retires all retained objects for the selected binding in that scope.

      Purge returns the removed count, keeps the registration available, and
      lets later melds create fresh objects. A SpellSpace can purge its own
      objects without touching the conduit. Application-held Python references
      still point to the old objects: stop using their resources after disposal.
SURFACE EXERCISED: md.Spellbook.bind, md.Existence.many, md.Conduit.meld,
                  md.Conduit.purge, md.Conduit.enter_spellspace,
                  md.SpellSpace.meld, md.SpellSpace.purge, md.Conduit.cleanup
"""
import melder as md


class WorkBuffer:
    """Own a small job payload with observable, explicit disposal.

    The payload belongs to this object and is released by close. The public
    closed flag and close_calls counter remain as lesson diagnostics, so the
    example can check disposal without reaching into Melder's private state.
    """

    def __init__(self) -> None:
        """Allocate an open buffer; no file, network or background work is started."""
        self._payload: bytearray = bytearray(128)
        self.closed: bool = False
        self.close_calls: int = 0

    def close(self) -> None:
        """Release the payload once and count each actual disposal invocation.

        Repeated calls leave the resource closed. Diagnostic fields remain
        readable; the owned payload field is removed after its contents clear.
        """
        self.close_calls += 1
        if self.closed:
            return
        self._payload.clear()
        del self._payload
        self.closed = True


def main() -> None:
    """Verify early disposal, retained siblings, remelding and scope isolation.

    The book and conduit are cleaned in finally blocks. Each assertion checks
    an observable removal count, object identity or disposal callback result.
    """
    book = md.Spellbook()
    try:
        # many creates a fresh object each time. Declared disposal makes these
        # buffers retained resources that Melder can retire through purge.
        book.bind(
            spell=WorkBuffer,
            existence=md.Existence.many,
            disposal_method_names=["close"],
        )
        conduit = book.conjure()
        try:
            first: WorkBuffer = conduit.meld("WorkBuffer")
            second: WorkBuffer = conduit.meld("WorkBuffer")
            third: WorkBuffer = conduit.meld("WorkBuffer")

            # The first job finished. Keep the other two objects alive.
            removed = conduit.purge(first, purge_all=False)
            assert removed == 1
            assert first.closed and first.close_calls == 1
            assert not second.closed and not third.closed
            assert conduit.purge(first, purge_all=False) == 0
            print("one finished buffer removed; its siblings remain:", removed)

            # A name selects the binding. Default True removes all of its
            # remaining retained objects in this conduit, not just one.
            removed = conduit.purge("WorkBuffer")
            assert removed == 2
            assert second.closed and third.closed
            assert conduit.purge("WorkBuffer") == 0
            print("remaining buffers removed by name:", removed)

            # The binding and the conduit still work after the bucket is empty.
            replacement: WorkBuffer = conduit.meld("WorkBuffer")
            assert replacement is not first and not replacement.closed
            print("the same registration creates a fresh buffer:", not replacement.closed)

            with conduit.enter_spellspace() as space:
                local: WorkBuffer = space.meld("WorkBuffer")
                # An instance does not grant access to a different scope.
                assert space.purge(replacement, purge_all=False) == 0
                assert conduit.purge(local, purge_all=False) == 0
                assert space.purge(local, purge_all=False) == 1
                assert local.closed and not replacement.closed
                local_replacement: WorkBuffer = space.meld("WorkBuffer")
                assert local_replacement is not local and not local_replacement.closed

            # Managed space exit closes its remaining buffer, not the root's.
            assert local_replacement.closed and not replacement.closed
            print("spell-space purge and exit leave the conduit buffer open:", not replacement.closed)
        finally:
            conduit.cleanup()

        # Purged objects are no longer retained for later scope cleanup.
        resources = (first, second, third, replacement, local, local_replacement)
        assert all(resource.closed for resource in resources)
        assert all(resource.close_calls == 1 for resource in resources)
        print("every buffer was disposed exactly once:", len(resources))
    finally:
        book.cleanup()


if __name__ == "__main__":
    main()
