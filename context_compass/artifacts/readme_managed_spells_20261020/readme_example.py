import melder as md


class ReportBuffer:
    """Reusable report state; reset on release, closed only when disposed."""

    def __init__(self) -> None:
        """Start empty and open; closed is a diagnostic flag for this example."""
        self.lines: list[str] = []
        self.closed: bool = False

    def reset(self) -> None:
        """Remove the previous request's data before the next lease."""
        self.lines.clear()

    def close(self) -> None:
        """Dispose the buffer; retain closed so the example can check teardown."""
        self.lines.clear()
        self.closed = True


class ReportJob:
    """Hold one injected buffer until the request scope disposes this job."""

    def __init__(self, buffer: ReportBuffer) -> None:
        """Borrow one pooled buffer; this job must release it exactly once."""
        self.buffer: ReportBuffer = buffer
        self.finished: bool = False

    def finish(self) -> None:
        """Give the buffer back once; the job must stop using it afterwards."""
        if self.finished:
            return
        self.finished = True
        md.ReleaseManagedSpell().release(self.buffer)


def main() -> None:
    """Return a request's buffer, reuse it reset, then dispose the idle buffer."""
    book = md.Spellbook()
    try:
        book.bind(
            spell=ReportBuffer,
            existence="managed_spell_quantity",
            managed_spell_mode="limited_quantity",
            managed_spell_limit=2,                  # at most two alive: idle + leased
            managed_spell_reset_methods=["reset"],  # every return, before reuse
            disposal_method_names=["close"],        # only when the pool destroys one
        )
        book.bind(spell=ReportJob, existence="many", disposal_method_names=["finish"])

        with book.conjure() as root:
            with root.enter_lesser_conduit() as request:
                job: ReportJob = request.meld("ReportJob")
                job.buffer.lines.append("Sales: 120")
                previous = job.buffer  # retain identity only to demonstrate reuse
            # Request exit called job.finish(): the buffer is reset and pooled.

            with root.managed_spell_meld("ReportBuffer") as reused:
                assert reused is previous
                assert reused.lines == [] and not reused.closed
                reused.lines.append("Sales: 240")
            # The lease block returns and resets the buffer again.

        assert previous.closed  # root exit disposed the idle buffer
    finally:
        book.cleanup()


if __name__ == "__main__":
    main()
