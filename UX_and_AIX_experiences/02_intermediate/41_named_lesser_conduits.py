"""
TIER: intermediate (41)
GOAL: Find a live job scope by name, then retire the name when that job ends.
      A name is a discovery address, not a new lifetime or a normal-root promotion.
      Names are exact, nonempty and unique within a frame. Supply them only when
      creating a lesser; prewarmed shells receive the new scope's name on acquisition.
      Cleanup removes the name before pool reuse. Keep the scope owner responsible
      for cleanup: a Cloud lookup borrows the object and does not extend its lifetime.
SURFACE EXERCISED: md.Spellbook.bind / conjure, md.Conduit.create_lesser_conduit /
                   get_conduit_cloud / meld / cleanup / prewarm_lesser_conduits,
                   ConduitCloud.get_conduit_by_name / has_conduit_name.
VERIFY: Runnable assertions cover lookup, collision, separate per-conduit values,
        retirement and fresh values after pooled reuse. No Nexus or recorder setup.
"""

import melder as md


class JobBuffer:
    """Own the mutable work list for one scope; naming does not select its lifetime."""

    def __init__(self) -> None:
        """Start every newly created job buffer with independent empty state."""
        self.items: list[str] = []


def main() -> None:
    """Run two jobs and reuse a finished scope under a new discovery name.

    Contract:
        Uses automatic mode to demonstrate that naming needs no dynamic mutation
        policy. The root owns cleanup of remaining children even if an assertion fails.
    Returns:
        None.
    """
    book = md.Spellbook(aetheric_frame="named-jobs")
    book.bind(spell=JobBuffer, existence="unique_per_conduit", permissions="create")
    root = book.conjure(name="job-owner")
    try:
        root.prewarm_lesser_conduits(2)
        cloud = root.get_conduit_cloud()
        first = root.create_lesser_conduit(name="job-41")
        second = root.create_lesser_conduit(name="job-42")
        assert cloud.get_conduit_by_name("job-41") is first
        assert cloud.get_conduit_by_name("job-42") is second

        first_buffer = first.meld("JobBuffer")
        second_buffer = second.meld("JobBuffer")
        first_buffer.items.append("prepare invoice")
        assert second_buffer is not first_buffer
        assert second_buffer.items == []
        print("Named lookup reaches the exact job; per-conduit values stay separate.")

        try:
            root.create_lesser_conduit(name="job-41")
        except ValueError:
            print("A duplicate active name is refused; the original job is still registered.")
        else:
            raise AssertionError("Duplicate active names must be rejected.")
        assert cloud.get_conduit_by_name("job-41") is first

        first.cleanup()
        assert not cloud.has_conduit_name("job-41")
        assert cloud.has_conduit_name("job-42")
        replacement = root.create_lesser_conduit(name="job-43")
        assert cloud.get_conduit_by_name("job-43") is replacement
        assert replacement.meld("JobBuffer").items == []
        assert not cloud.has_conduit_name("job-41")
        print("Cleanup retires the old name; the next job begins with fresh scoped state.")

        replacement.cleanup()
        anonymous = root.create_lesser_conduit()
        assert anonymous.name is None
        assert not cloud.has_conduit_name("job-43")
        anonymous.cleanup()
        second.cleanup()
        assert cloud.list_conduit_names() == ("job-owner",)
        print("Anonymous scopes need no discovery entry. Names are not lifetime-matching tags.")
    finally:
        root.permanent_cleanup()


if __name__ == "__main__":
    main()
