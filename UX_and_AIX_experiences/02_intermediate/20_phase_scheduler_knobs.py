"""
TIER: intermediate (20)
GOAL: Conjure runs the compile pipeline (phases 1-11) through the
      PhaseScheduler - a worker pool with a barrier timeout. Two config
      knobs tune it: workers per spellbook and the barrier timeout.
      Slow CI boxes raise the timeout; tiny worlds run one worker.
SURFACE EXERCISED: phase_scheduler_workers_per_spellbook,
                   phase_scheduler_barrier_timeout_milliseconds
"""
import melder as md


class Alpha:
    pass


class Beta:
    def __init__(self, alpha: Alpha) -> None:
        self.alpha = alpha


def main() -> None:
    configuration = md.SpellbookConfiguration()
    configuration.with_defaults()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    configuration.set_property(
        "phase_scheduler_barrier_timeout_milliseconds", 30_000
    )

    book = md.Spellbook(configuration=configuration)
    book.bind(spell=Alpha, existence="unique")
    book.bind(spell=Beta, existence="unique")
    conduit = book.conjure()  # phases run under the tuned scheduler

    beta = conduit.meld(spell=Beta)
    assert isinstance(beta.alpha, Alpha)
    print("compiled on one worker with a generous barrier; DI intact")
    print("if conjure ever raises PhaseTimeoutError, this timeout knob is why")


if __name__ == "__main__":
    main()
