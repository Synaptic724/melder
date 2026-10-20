"""Add the no-recursion regression tests (TimedGreeter, AMBIGUOUS_PROVIDER) to S8's integration file.

Every anchor must occur exactly once; the file must stay LF; nothing is written unless every edit applies.
Usage: add_ambiguous_provider_tests.py --check|--apply
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[4]
TARGET = ROOT / "tests/integration/melder/aether/conduit/test_notch_refused_at_commit_integration.py"

DOC_OLD = '''Phases 1-4 of a version that was never compiled run when it is notched in. Until 0.2.8256 they ran at the
transaction's commit, after the switch, and nothing undid the switch: `notch_spell` raised SpellbookValidationError
while the lender's index selected the broken version, its borrowers kept the old one, and the lender could not meld
the index by address. The notch now runs the check inside its window and, when the check fails, puts the structure
back before it raises: the owner's answer (a), "refuse it and throw and move on".

The broken version is `SelfMade`, whose constructor takes its own class (SELF_DEPENDENCY at Phase 4): it is only
checked once it is active, because a parked version is not in the pool Phase 3 resolves against.
'''
DOC_NEW = '''Phases 1-4 of a version that was never compiled run when it is notched in. Until the story's fix they ran at the
transaction's commit, after the switch, and nothing undid the switch: `notch_spell` raised SpellbookValidationError
while the lender's index selected the broken version, its borrowers kept the old one, and the lender could not meld
the index by address (measured on 0.2.8255, and on 0.2.8260, where a spell_id is the hash of the object's code).
With the fix the notch runs the check inside its window and, when the check fails, puts the structure back before
it raises: the owner's answer (a), "refuse it and throw and move on". Until it lands these tests fail.

Two broken versions are used. `SelfMade`'s constructor takes its own class (SELF_DEPENDENCY at Phase 4).
`TimedGreeter`'s constructor needs a `Clock` while two are registered (AMBIGUOUS_PROVIDER): nothing in it loops, so
it shows the half-switch follows any failing check, not recursion. Each is only checked once it is active, because
a parked version is not in the pool Phase 3 resolves against.
'''

CLASSES_ANCHOR = '''        self.greeter = greeter


def _reset_world() -> None:'''
CLASSES_NEW = '''        self.greeter = greeter


class Clock(Protocol):
    """What `TimedGreeter` needs; a world built with `clocks=True` registers two providers of it."""

    def now(self) -> str:
        """Return the time of day."""
        ...


class UtcClock:
    """One registered provider of `Clock`."""

    def now(self) -> str:
        """Return the time in UTC."""
        return "12:00 UTC"


class LocalClock:
    """A second registered provider of `Clock`, so a single `Clock` parameter has two candidates."""

    def now(self) -> str:
        """Return the local time."""
        return "06:00 local"


class TimedGreeter:
    """
    A broken version with no recursion: its constructor needs a `Clock` and two are registered
    (AMBIGUOUS_PROVIDER once it is active).
    """

    def __init__(self, clock: Clock) -> None:
        """
        Keep the clock.

        Args:
            clock: The clock to read; with `UtcClock` and `LocalClock` both registered no meld can pick one.
        """
        self.clock = clock

    def greet(self) -> str:
        """Return a greeting with the time."""
        return "hello at " + self.clock.now()


def _reset_world() -> None:'''

WORLD_OLD = '''@contextlib.contextmanager
def _world(frame: str, *, borrower: bool = False, rift_enabled: bool = False) -> Iterator[_World]:
    """
    English active on the lender's index; optionally a borrower that contracts the whole index.

    Args:
        frame: The frame for both Books.
        borrower: Build an index-linked borrower Book with a consumer (`Speaker`) of the index.
        rift_enabled: Make the frame publish passive Nexus records.

    Yields:
        _World: The handles; both roots are torn down on exit.
    """
    book = _make_spellbook(frame, configure_frame=True, rift_enabled=rift_enabled)
    borrower_book = _make_spellbook(frame, configure_frame=False) if borrower else None
    english_id = book.bind(
        spell=English, spellframe=Greeter, binding_name="greeter", existence=Existence.many, permissions="create",
    )
'''
WORLD_NEW = '''@contextlib.contextmanager
def _world(
    frame: str, *, borrower: bool = False, rift_enabled: bool = False, clocks: bool = False,
) -> Iterator[_World]:
    """
    English active on the lender's index; optionally a borrower that contracts the whole index.

    Args:
        frame: The frame for both Books.
        borrower: Build an index-linked borrower Book with a consumer (`Speaker`) of the index.
        rift_enabled: Make the frame publish passive Nexus records.
        clocks: Register `UtcClock` and `LocalClock` as `Clock` providers in the lender's Book, so `TimedGreeter`'s
            `clock` parameter has two candidates.

    Yields:
        _World: The handles; both roots are torn down on exit.
    """
    book = _make_spellbook(frame, configure_frame=True, rift_enabled=rift_enabled)
    borrower_book = _make_spellbook(frame, configure_frame=False) if borrower else None
    english_id = book.bind(
        spell=English, spellframe=Greeter, binding_name="greeter", existence=Existence.many, permissions="create",
    )
    if clocks:
        book.bind(
            spell=UtcClock, spellframe=Clock, binding_name="utc", existence=Existence.many, permissions="create",
        )
        book.bind(
            spell=LocalClock, spellframe=Clock, binding_name="local", existence=Existence.many, permissions="create",
        )
'''

TESTS_ANCHOR = '''def test_a_notch_back_after_a_refusal_changes_nothing() -> None:'''
TESTS_NEW = '''def test_a_notch_refused_for_an_ambiguous_provider_leaves_the_old_version_active() -> None:
    """
    Regression: the half-switch is not about recursion. TimedGreeter needs a Clock and two are registered, so its
    check fails with AMBIGUOUS_PROVIDER, and the lender then selected TimedGreeter and could not meld English.

    Contract:
        - The refusal names the real reason ([AMBIGUOUS_PROVIDER]); afterwards the index selects English, English
          is active and holds its claim and address, TimedGreeter is parked with no Phase-4 result, and English
          melds by address and by spell_id.
    """
    with _world("refused_ambiguous", clocks=True) as world:
        broken_id = world.stage(TimedGreeter)

        error = _refused_notch(world, broken_id)

        assert "[AMBIGUOUS_PROVIDER]" in str(error)
        _assert_english_stands(world, broken_id)


def test_a_notch_refused_for_an_ambiguous_provider_leaves_borrowers_on_the_lenders_version() -> None:
    """
    Regression: the borrower's consumer of the index (`Speaker`) was refused at its meld after the refused notch,
    while the borrower still held English active.

    Contract:
        - The borrower's copies are as before (English active, TimedGreeter parked), its consumer melds English and
          greets "hello", and the lender is on English too.
    """
    with _world("refused_ambiguous_borrower", borrower=True, clocks=True) as world:
        broken_id = world.stage(TimedGreeter)
        before = world.borrower_copies()

        _refused_notch(world, broken_id)

        assert world.borrower_copies() == before == ({world.english_id}, {broken_id})
        assert world.borrower is not None
        assert world.borrower.meld(spell_id=world.speaker_id).greeter.greet() == "hello"
        _assert_english_stands(world, broken_id)


def test_a_notch_back_after_a_refusal_changes_nothing() -> None:'''


def main() -> None:
    """Apply the four edits in memory, check them, write only with --apply."""
    if sys.argv[1:] not in (["--check"], ["--apply"]):
        raise SystemExit(__doc__)
    raw = TARGET.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("CRLF in the target")
    text = raw.decode("utf-8")
    for old, new in ((DOC_OLD, DOC_NEW), (CLASSES_ANCHOR, CLASSES_NEW), (WORLD_OLD, WORLD_NEW),
                     (TESTS_ANCHOR, TESTS_NEW)):
        if text.count(old) != 1:
            raise SystemExit("anchor found %d times: %r" % (text.count(old), old[:80]))
        text = text.replace(old, new)
    for number, line in enumerate(text.split("\n"), 1):
        if len(line) > 120:
            raise SystemExit("line %d over 120 chars" % number)
    compile(text, str(TARGET), "exec")
    print("lines before:", raw.decode("utf-8").count("\n"), "after:", text.count("\n"))
    if sys.argv[1] == "--apply":
        TARGET.write_bytes(text.encode("utf-8"))
        if TARGET.read_bytes().decode("utf-8") != text:
            raise SystemExit("read-back mismatch")
        print("applied")


main()
