"""
Probe: what a root conduit's teardown disposes, against the owner's rule that it cleans only what it holds.

Purpose:
    TASK-2026-10-18-document_root_teardown_cleans_only_what_it_holds. The system documents may only state
    teardown behaviour verified in source or measured here. Three cases, each in a fresh world, through the public
    `melder` surface:
      R1  a consumer the root's own store holds gives its leased object back in its disposal method (S1's P17,
          rerun on the current tree);
      R2  a pooled object with a disposal-bearing `many` child is out at teardown, another is idle;
      R3  control: the same consumer held by a lesser conduit gives its object back at the lesser's exit.

Run from the repository root on 3.14t (GIL off, then on):
    PYTHONPATH=src python probe_root_teardown_scope.py
    PYTHONPATH=src PYTHON_GIL=1 python probe_root_teardown_scope.py

The fresh-world reset copies S1's probe (the example harness's conftest), which needs one deep import.
"""
import sys
import traceback
from typing import Callable, List, Tuple

import melder as md
from melder.aether.spellbook.spellbook import Spellbook as _HarnessSpellbook


def fresh_world() -> None:
    """Reset the process-wide roots and Aether, as the example harness does between examples."""
    md.MutationResearch._reset_singleton_for_tests()
    md.Crystallizer._reset_singleton_for_tests()
    md.Nexus._reset_singleton_for_tests()
    md.Aether._reset_singleton_for_tests()
    aether = md.Aether()
    _HarnessSpellbook._aether = aether
    md.Conduit._aether = aether


RESULTS: List[Tuple[str, str]] = []


def row(case: str, text: str) -> None:
    """Print one probe row and keep it for the summary."""
    RESULTS.append((case, text))
    print(f"[{case}] {text}")


def run(case: str, body: Callable[[], None]) -> None:
    """Run one case in a fresh world; a raise is reported as a FAILED row, never hidden."""
    fresh_world()
    try:
        body()
    except Exception as error:
        row(case, f"FAILED {type(error).__name__}: {error}")
        traceback.print_exc()
    finally:
        fresh_world()


def counts(cls: type) -> str:
    """Return count / idle / out of a class's one pool as text."""
    (snapshot,) = md.ReleaseManagedSpell().describe(cls)
    return f"count={snapshot['count']} idle={snapshot['idle_count']} out={snapshot['out_count']}"


def chain(error: BaseException) -> List[str]:
    """Flatten an exception group into leaf texts, each with its cause's type."""
    if isinstance(error, BaseExceptionGroup):
        leaves: List[str] = []
        for inner in error.exceptions:
            leaves.extend(chain(inner))
        return leaves
    cause = error.__cause__
    suffix = f" <- {type(cause).__name__}: {str(cause)[:120]}" if cause is not None else ""
    return [f"{type(error).__name__}: {str(error)[:120]}{suffix}"]


class Connection:
    """A pooled object with an observable close (its disposal method)."""

    def __init__(self) -> None:
        self.closed: bool = False

    def close(self) -> None:
        self.closed = True


class RequestHandler:
    """A many consumer that receives a pooled Connection and gives it back in its disposal method."""

    def __init__(self, connection: Connection) -> None:
        self.connection: Connection = connection
        self.done: bool = False

    def finish(self) -> None:
        if self.done:
            return
        self.done = True
        md.ReleaseManagedSpell().release(self.connection)


class Cursor:
    """A disposal-bearing `many` child of a pooled Session."""

    def __init__(self) -> None:
        self.closed: bool = False

    def close(self) -> None:
        self.closed = True


class Session:
    """A pooled object that holds a `many` Cursor built with it."""

    def __init__(self, cursor: Cursor) -> None:
        self.cursor: Cursor = cursor
        self.closed: bool = False

    def close(self) -> None:
        self.closed = True


def r1_root_held_consumer_releases_in_disposal() -> None:
    book = md.Spellbook()
    book.bind(spell=Connection, existence=md.Existence.managed_spell_quantity, disposal_method_names=["close"])
    book.bind(spell=RequestHandler, existence=md.Existence.many, disposal_method_names=["finish"])
    root = book.conjure()
    handler: RequestHandler = root.meld("RequestHandler")
    row("R1", f"a handler melded on the root holds a lease: {counts(Connection)}")
    try:
        root.cleanup()
        row("R1", "root teardown raised nothing")
    except BaseException as error:
        row("R1", f"root teardown raised {type(error).__name__}: {error}")
        for leaf in chain(error):
            row("R1", f"  leaf: {leaf}")
    row("R1", f"handler.done={handler.done} (its disposal ran) connection.closed={handler.connection.closed}")
    book.cleanup()


def r2_children_of_an_out_object() -> None:
    book = md.Spellbook()
    book.bind(spell=Cursor, existence=md.Existence.many, disposal_method_names=["close"])
    book.bind(spell=Session, existence=md.Existence.managed_spell_quantity, disposal_method_names=["close"])
    root = book.conjure()
    idle: Session = root.meld("Session")
    out: Session = root.meld("Session")
    md.ReleaseManagedSpell().release(idle)
    (snapshot,) = md.ReleaseManagedSpell().describe(Session)
    row("R2", f"before teardown: {counts(Session)} children_recorded={snapshot['children_recorded']}")
    try:
        root.cleanup()
        row("R2", "root teardown raised nothing")
    except BaseException as error:
        row("R2", f"root teardown raised {type(error).__name__}: {error}")
    row("R2", f"idle session closed={idle.closed} its cursor closed={idle.cursor.closed}")
    row("R2", f"out session closed={out.closed} its cursor closed={out.cursor.closed}")
    book.cleanup()


def r3_lesser_held_consumer_control() -> None:
    book = md.Spellbook()
    book.bind(spell=Connection, existence=md.Existence.managed_spell_quantity, disposal_method_names=["close"])
    book.bind(spell=RequestHandler, existence=md.Existence.many, disposal_method_names=["finish"])
    root = book.conjure()
    with root.enter_lesser_conduit() as request:
        handler: RequestHandler = request.meld("RequestHandler")
    row("R3", f"the lesser's exit disposed the handler, which gave its lease back: done={handler.done} "
              f"{counts(Connection)}")
    try:
        root.cleanup()
        row("R3", f"root teardown raised nothing; the idle connection closed={handler.connection.closed}")
    except BaseException as error:
        row("R3", f"root teardown raised {type(error).__name__}: {error}")
    book.cleanup()


def main() -> None:
    print(f"python {sys.version.split()[0]} gil_enabled={sys._is_gil_enabled()} melder {md.__version__}")
    for case, body in (
        ("R1", r1_root_held_consumer_releases_in_disposal),
        ("R2", r2_children_of_an_out_object),
        ("R3", r3_lesser_held_consumer_control),
    ):
        run(case, body)
    failed = [text for _case, text in RESULTS if text.startswith("FAILED")]
    print(f"rows={len(RESULTS)} failed={len(failed)}")


if __name__ == "__main__":
    main()
