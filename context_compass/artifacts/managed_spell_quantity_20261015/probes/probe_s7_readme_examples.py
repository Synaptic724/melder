"""S7 docs probe: run the README examples the D5 edit adds or corrects, and assert what their prose claims.

1. The lifetimes section's managed example: a limited_quantity binding with a reset and a disposal method; a meld
   leases, `ReleaseManagedSpell().release` resets and pools the object, `managed_spell_meld` leases the same object
   again and gives it back at the end of the `with`; a ninth lease of a pool with eight out raises
   ManagedSpellExhaustedError; the root's teardown disposes the idle objects and leaves the ones out alone.
2. The teardown section's disposal sentence: a failing disposal method does not stop the methods after it; each
   failure is a RuntimeError chained from what the method raised; the failures are raised together as one
   ExceptionGroup once the teardown has finished; creations are disposed newest first.
Run from a scratch directory (creation caches stay out of the tree):
  cd /tmp/m0_mq && PYTHONPATH=<repo>/src python -X gil=0|1 <this file>
"""
import melder as md


class ChannelLogger:
    """The README's managed example class; records every call."""

    built = 0
    log: list = []

    def __init__(self) -> None:
        ChannelLogger.built += 1
        self.lines: list = []

    def write(self, line: str) -> None:
        self.lines.append(line)

    def flush(self) -> None:
        ChannelLogger.log.append(("flush", id(self)))

    def close(self) -> None:
        ChannelLogger.log.append(("close", id(self)))


def check_managed_example() -> None:
    """The lifetimes section's example and the claims around it."""
    book = md.Spellbook()
    book.bind(
        spell=ChannelLogger,
        existence="managed_spell_quantity",
        managed_spell_mode="limited_quantity",
        managed_spell_limit=8,
        managed_spell_reset_methods=["flush"],
        disposal_method_names=["close"],
    )
    conduit = book.conjure()

    logger = conduit.meld(ChannelLogger)
    logger.write("ready")
    md.ReleaseManagedSpell().release(logger)
    assert ChannelLogger.log == [("flush", id(logger))], ChannelLogger.log

    with conduit.managed_spell_meld(ChannelLogger) as again:
        assert again is logger, "the pooled logger is leased again"
        again.write("again")
    assert ChannelLogger.log[-1] == ("flush", id(logger)), "given back (reset) when the block ends"
    assert ChannelLogger.built == 1

    out = [conduit.meld(ChannelLogger) for _ in range(8)]
    assert ChannelLogger.built == 8 and out[0] is logger
    try:
        conduit.meld(ChannelLogger)
    except md.ManagedSpellExhaustedError as exc:
        print("ninth lease refused:", exc)
    else:
        raise AssertionError("a ninth lease of a pool with eight out must refuse")

    rows = md.ReleaseManagedSpell().describe(ChannelLogger)
    print("describe:", {k: rows[0][k] for k in ("mode", "limit", "count") if k in rows[0]})
    for obj in out[:3]:
        md.ReleaseManagedSpell().release(obj)
    closes_before = [entry for entry in ChannelLogger.log if entry[0] == "close"]
    assert not closes_before, "a release never disposes"
    conduit.cleanup()
    closed = {oid for kind, oid in ChannelLogger.log if kind == "close"}
    assert closed == {id(obj) for obj in out[:3]}, "teardown disposes the idle objects only"
    print("managed example: OK (built", ChannelLogger.built, "closed", len(closed), "of the 3 idle; 5 out untouched)")


class Connection:
    """Two disposal methods; the first one raises."""

    calls: list = []

    def close(self) -> None:
        Connection.calls.append("close")
        raise OSError("socket already gone")

    def shutdown(self) -> None:
        Connection.calls.append("shutdown")


class Worker:
    """Built after its Connection, so torn down before it."""

    calls: list = []

    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def shutdown(self) -> None:
        Worker.calls.append(("worker", list(Connection.calls)))


def check_disposal_sentence() -> None:
    """The teardown section's corrected sentence."""
    book = md.Spellbook()
    book.bind(spell=Connection, existence="unique", disposal_method_names=["close", "shutdown"])
    book.bind(spell=Worker, existence="unique", disposal_method_names=["shutdown"])
    conduit = book.conjure()
    conduit.meld(Worker)
    try:
        conduit.cleanup()
    except BaseExceptionGroup as group:
        leaves = []

        def walk(g: BaseExceptionGroup) -> None:
            for e in g.exceptions:
                if isinstance(e, BaseExceptionGroup):
                    walk(e)
                else:
                    leaves.append(e)

        walk(group)
        print("raised:", type(group).__name__, repr(group.message), "leaves:",
              [(type(e).__name__, type(e.__cause__).__name__) for e in leaves])
        assert len(leaves) == 1 and isinstance(leaves[0], RuntimeError)
        assert isinstance(leaves[0].__cause__, OSError), "chained from what the method raised"
    else:
        raise AssertionError("a failing disposal method must surface as an ExceptionGroup")
    assert Connection.calls == ["close", "shutdown"], Connection.calls
    assert Worker.calls == [("worker", [])], "newest first: the worker before its connection"
    print("disposal sentence: OK (close raised, shutdown still ran; worker torn down before its connection)")


check_managed_example()
check_disposal_sentence()
