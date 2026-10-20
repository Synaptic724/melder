"""Rewrite the UX examples the one-object rule breaks or misteaches (melder_0, 2026-10-18).

S1 of EPIC-2026-10-18-spell_identity_is_the_code: a spell_id is the SHA256 of the registered object's code, with
nothing from the bind call in it, so one object registers once. Ten example rows bind one class twice (in a second
frame or Book, under another binding_name) and six files teach the retired rule in text. This script carries the
rewrite planned in S1's PLAN note of 2026-10-18T22:28:21Z: one class per world or Book, `_pair` binding nothing,
the three identity contract probes asserting the new contract, a probe of the per-frame regime, and every
comment, docstring and lesson text that states the retired rule rewritten, never deleted.

Usage: python rewrite_ux_examples.py <repository root> [--write] [--diff <path>]

Every edit is an anchored (old, new) pair that must occur exactly once in its file at its turn. Each file is read
as bytes and its line ending detected (CRLF or LF; mixed endings refuse); the edits run on LF text and the file
is written back with its own ending. All-or-nothing: nothing is written unless every edit of every file applies,
and nothing at all without --write. With --diff the unified diff of the whole change goes to that path.
"""
import difflib
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


class UxEdits:
    """The anchored edits, one method per file; each returns its (old, new) pairs in application order."""

    def files(self) -> dict[str, list[tuple[str, str]]]:
        """Map each repository-relative path to its edits."""
        ux = "UX_and_AIX_experiences/"
        return {
            ux + "03_advanced/02_frames_as_worlds.py": self.lesson_02(),
            ux + "03_advanced/16_ward_policies.py": self.ward_policies(),
            ux + "04_expert/11_pointing_a_rift_at_your_own_frame.py": self.rift_targets(),
            ux + "04_expert/16_rewiring_a_running_world.py": self.rewiring(),
            ux + "02_intermediate/31_spellbook_config_defined.py": self.config_defined(),
            ux + "02_intermediate/37_the_frame_conduit_cloud.py": self.conduit_cloud(),
            ux + "pytest_examples/test_advanced_probes.py": self.advanced_probes(),
            ux + "pytest_examples/test_contract_probes.py": self.contract_probes(),
            ux + "pytest_examples/test_intermediate_probes.py": self.intermediate_probes(),
            ux + "01_beginner/18_bootstrap_pattern.py": self.bootstrap_text(),
            ux + "01_beginner/24_same_class_many_names.py": self.same_class_text(),
            ux + "01_beginner/30_double_bind_outcome.py": self.double_bind_text(),
            ux + "04_expert/13_one_workshop_many_worlds.py": self.workshop_text(),
            ux + "04_expert/26_codegen_create_modify_iterate.py": self.codegen_text(),
            ux + "AGENTS.md": self.agents_text(),
        }

    def lesson_02(self) -> list[tuple[str, str]]:
        """Advanced 02: one subclass per world at one address; the text names the code rule and the regime."""
        goal_old = '''\
      A spell_id is a SHA256 over the BIND FINGERPRINT - structural
      profile, lookup signature, existence, resolved disposal metadata.
      READ THAT LIST AGAIN AND NOTICE WHAT IS ABSENT: the frame. So two
      books on two different frames binding the same class with the same
      parameters mint THE SAME ID, and the second conjure is refused
      process-wide. Moving to another frame is not a fix, because the id
      follows the fingerprint and the fingerprint has no frame in it.

      The fix is to make the BINDINGS different, not the worlds:
      `binding_name=` or `spellframe=`. Once you do, everything you
      expect from a world wall holds - `unique` is one instance PER
      FRAME, each world reuses its own singleton forever, and nothing
      leaks across.
'''
        goal_new = '''\
      A spell_id is the SHA256 of the registered object's CODE - its
      methods and constructor, its class-level values, its bases - and
      of nothing from the bind call. READ THAT AGAIN AND NOTICE WHAT IS
      ABSENT: the frame, the spellframe, the binding_name. So two books
      on two different frames binding the same class mint THE SAME ID,
      whatever names they give it, and the second registration is
      refused process-wide. Moving to another frame is not a fix, and
      neither is another binding_name: one object is one spell.

      The fix is to make the CLASSES different, not the worlds or the
      names: one subclass per world. A subclass is a new class, so a new
      spell_id, and every world can then keep it at the SAME address.
      Once you do, everything you expect from a world wall holds -
      `unique` is one instance PER FRAME, each world reuses its own
      singleton forever, and nothing leaks across.

      THE OTHER WAY is a regime, not a binding: with
      `process_wide_unique_spell_ids` turned off before the first frame
      exists, a spell_id is unique per FRAME, and one class may live in
      several worlds. That is Aether configuration, and a lesson never
      installs it - lessons share one interpreter (advanced 07). The
      probe suite pins it in a reset world.
'''
        surface_old = '''\
SURFACE EXERCISED: Spellbook(aetheric_frame=...), binding_name as the
                   identity differentiator, per-frame instance isolation
'''
        surface_new = '''\
SURFACE EXERCISED: Spellbook(aetheric_frame=...), one class per world at
                   one address, per-frame instance isolation
'''
        history_old = '''\
retire exactly that claim. S2 landed. The claim is retired, and the
lesson now teaches the line instead of the half of it that survived.
"""
'''
        history_new = '''\
retire exactly that claim. S2 landed. The claim is retired, and the
lesson now teaches the line instead of the half of it that survived.

0.2.8257: a spell_id became the SHA256 of the object's code, with nothing
from the bind call in it, so a binding_name no longer makes one class two
spells. The lesson used to bind TenantCache in both worlds under two
binding_names; each world now binds its own subclass at one address.
"""
'''
        classes_old = '''\
class TenantCache:
    pass


def main() -> None:
'''
        classes_new = '''\
class TenantCache:
    pass


class TenantACache(TenantCache):
    """Tenant A's cache - a new class, so its own spell_id."""


class TenantBCache(TenantCache):
    """Tenant B's cache - a new class, so its own spell_id."""


def main() -> None:
'''
        return [(goal_old, goal_new), (surface_old, surface_new), (history_old, history_new),
                (classes_old, classes_new), self._lesson_02_main()]

    def _lesson_02_main(self) -> tuple[str, str]:
        """Advanced 02's main(): bind, meld and the third-world refusal on the per-world classes."""
        old = '''\
    # THE SAME CLASS IN BOTH WORLDS - but the BINDINGS must differ.
    # Bind these two identically and the second conjure is refused: the
    # fingerprint would be byte-identical and the frame is not in it.
    book_a.bind(spell=TenantCache, existence="unique", binding_name="tenant-a")
    book_b.bind(spell=TenantCache, existence="unique", binding_name="tenant-b")

    conduit_a = book_a.conjure(name="cache-a")
    conduit_b = book_b.conjure(name="cache-b")

    cache_a = conduit_a.meld("TenantCache", binding_name="tenant-a")
    cache_b = conduit_b.meld("TenantCache", binding_name="tenant-b")

    # "unique" = one instance per FRAME. Two frames, two singletons.
    assert type(cache_a) is type(cache_b) is TenantCache
    assert cache_a is not cache_b
    print("one class, two worlds, two singletons:", cache_a is not cache_b)

    # Each world reuses ITS OWN singleton, forever.
    assert conduit_a.meld("TenantCache", binding_name="tenant-a") is cache_a
    assert conduit_b.meld("TenantCache", binding_name="tenant-b") is cache_b
    print("per-frame reuse holds; nothing leaked across the wall")

    # THE LINE, PROVEN. A third world binding the SAME class the SAME way
    # as tenant-a is refused - and the refusal names the id, not the
    # frame, because the frame was never what made them different.
    book_c = md.Spellbook(aetheric_frame="tenant-c")
    try:
        book_c.bind(spell=TenantCache, existence="unique",
                    binding_name="tenant-a")
        book_c.conjure(name="cache-c")
        raise AssertionError("expected a process-wide spell_id refusal")
    except RuntimeError as error:
        assert "spell_id" in str(error) or "Spell ID" in str(error)
        print()
        print("a third frame with an IDENTICAL binding was refused:")
        print("  frames isolate instances; they do not namespace identity")
'''
        new = '''\
    # ONE ADDRESS IN BOTH WORLDS, ONE CLASS PER WORLD. Binding TenantCache
    # itself in both would be refused: its spell_id is its code, the same
    # in every frame, and neither the frame nor a binding_name is in it.
    book_a.bind(spell=TenantACache, existence="unique",
                spellframe="tenant", binding_name="cache")
    book_b.bind(spell=TenantBCache, existence="unique",
                spellframe="tenant", binding_name="cache")

    conduit_a = book_a.conjure(name="cache-a")
    conduit_b = book_b.conjure(name="cache-b")

    # The same address melds each world's own class.
    cache_a = conduit_a.meld(spellframe="tenant", binding_name="cache")
    cache_b = conduit_b.meld(spellframe="tenant", binding_name="cache")

    # "unique" = one instance per FRAME. Two frames, two singletons.
    assert type(cache_a) is TenantACache
    assert type(cache_b) is TenantBCache
    assert isinstance(cache_a, TenantCache) and isinstance(cache_b, TenantCache)
    assert cache_a is not cache_b
    print("one shape, two worlds, two singletons:", cache_a is not cache_b)

    # Each world reuses ITS OWN singleton, forever.
    assert conduit_a.meld(spellframe="tenant", binding_name="cache") is cache_a
    assert conduit_b.meld(spellframe="tenant", binding_name="cache") is cache_b
    print("per-frame reuse holds; nothing leaked across the wall")

    # THE LINE, PROVEN. A third world binding tenant A's class - under a
    # binding_name of its own - is refused, and the refusal names the
    # spell_id: neither the frame nor the name was ever part of it.
    book_c = md.Spellbook(aetheric_frame="tenant-c")
    try:
        book_c.bind(spell=TenantACache, existence="unique",
                    binding_name="another-name")
        book_c.conjure(name="cache-c")
        raise AssertionError("expected a process-wide spell_id refusal")
    except RuntimeError as error:
        assert "spell_id" in str(error) or "Spell ID" in str(error)
        print()
        print("a third frame binding the SAME class was refused:")
        print("  frames isolate instances; they do not namespace identity")
'''
        return old, new

    def ward_policies(self) -> list[tuple[str, str]]:
        """Advanced 16: the dynamic world binds its own Payload subclass."""
        class_old = '''\
class Payload:
    """A spell to give the ward something to be a policy about."""


MODES = ("default", "whitelist_all", "block_all",
'''
        class_new = '''\
class Payload:
    """A spell to give the ward something to be a policy about."""


class DynamicPayload(Payload):
    """The dynamic world's own Payload - a new class, so its own spell_id."""


MODES = ("default", "whitelist_all", "block_all",
'''
        comment_old = '''\
    # binding_name differs per frame ON PURPOSE. A spell_id is a hash of
    # the BIND FINGERPRINT and the frame is not in it, so the same class
    # bound identically in two frames mints the same id and the second
    # conjure is refused process-wide. Frames isolate instances, not
    # identity - see advanced 02.
'''
        comment_new = '''\
    # Each world binds its OWN class. A spell_id is the SHA256 of the
    # class's code and neither the frame nor the binding_name is in it,
    # so the same class bound in two frames is one spell_id and the
    # second registration is refused process-wide. Frames isolate
    # instances, not identity - see advanced 02.
'''
        bind_old = '''\
    book.bind(spell=Payload, existence="unique", binding_name="dynamic")
'''
        bind_new = '''\
    book.bind(spell=DynamicPayload, existence="unique", binding_name="dynamic")
'''
        return [(class_old, class_new), (comment_old, comment_new), (bind_old, bind_new)]

    def rift_targets(self) -> list[tuple[str, str]]:
        """Expert 11: a Ledger subclass per frame, passed into `_postured_frame`."""
        helper_old = '''\
class Ledger:
    pass


def _postured_frame(frame_name: str, *, dynamic: bool = False) -> None:
    """Build one frame with the posture AR needs, then settle it."""
    book = md.Spellbook(aetheric_frame=frame_name)
    # binding_name keeps the spell_id distinct per frame - identity is
    # process-wide and the frame is not in the fingerprint (advanced 02).
    book.bind(spell=Ledger, existence="unique", binding_name=frame_name)
'''
        helper_new = '''\
class Ledger:
    pass


class ClosedLedger(Ledger):
    """closed-world's own Ledger - a new class, so its own spell_id."""


class ObservableLedger(Ledger):
    """observable's own Ledger - a new class, so its own spell_id."""


class UnlistedLedger(Ledger):
    """unlisted's own Ledger - a new class, so its own spell_id."""


class WorkshopLedger(Ledger):
    """workshop's own Ledger - a new class, so its own spell_id."""


def _postured_frame(frame_name: str, spell: type[Ledger], *,
                    dynamic: bool = False) -> None:
    """Build one frame with the posture AR needs, bind that frame's own
    Ledger class in it, then settle it."""
    book = md.Spellbook(aetheric_frame=frame_name)
    # Each frame binds its OWN Ledger class: a spell_id is the SHA256 of
    # the class's code, with neither the frame nor the binding_name in
    # it, so one class bound in two frames is refused (advanced 02).
    book.bind(spell=spell, existence="unique", binding_name=frame_name)
'''
        closed_old = '''\
    closed.bind(spell=Ledger, existence="unique", binding_name="closed-world")
'''
        closed_new = '''\
    closed.bind(spell=ClosedLedger, existence="unique",
                binding_name="closed-world")
'''
        calls_old = '''\
    _postured_frame("observable")
    _postured_frame("unlisted")
    _postured_frame("workshop", dynamic=True)
'''
        calls_new = '''\
    _postured_frame("observable", ObservableLedger)
    _postured_frame("unlisted", UnlistedLedger)
    _postured_frame("workshop", WorkshopLedger, dynamic=True)
'''
        return [(helper_old, helper_new), (closed_old, closed_new), (calls_old, calls_new)]

    def rewiring(self) -> list[tuple[str, str]]:
        """Expert 16: `_pair` builds two empty books; the posture gate refuses before any spell is read."""
        pair_old = '''\
def _pair(frame_name: str, **posture):
    """An owner and a borrower in one world, each from its own book."""
    owner_book = md.Spellbook(aetheric_frame=frame_name)
    borrower_book = md.Spellbook(aetheric_frame=frame_name)
    service_id = owner_book.bind(
        spell=Service, existence="unique", permissions="create",
        binding_name=f"{frame_name}-service",
    )
    borrower_book.bind(
        spell=Consumer, existence="unique", permissions="create",
        binding_name=f"{frame_name}-consumer",
    )
    if posture:
'''
        pair_new = '''\
def _pair(frame_name: str, **posture: object) -> tuple[md.Conduit, md.Conduit]:
    """An owner and a borrower in one world, each from its own book.

    Both books are EMPTY on purpose. link() asks the frame posture before
    it reads a single spell, so these worlds need nothing bound to be
    refused - and Service and Consumer are already one spell each in
    rewire-world: a spell_id is the SHA256 of the class's code, so
    binding them again here, under any binding_name, would be refused
    before the posture gate ever spoke (advanced 02)."""
    owner_book = md.Spellbook(aetheric_frame=frame_name)
    borrower_book = md.Spellbook(aetheric_frame=frame_name)
    if posture:
'''
        return_old = '''\
    return owner, borrower, service_id
'''
        return_new = '''\
    return owner, borrower
'''
        braked_old = '''\
    braked_owner, braked_borrower, _ = _pair(
'''
        braked_new = '''\
    braked_owner, braked_borrower = _pair(
'''
        static_old = '''\
    static_owner, static_borrower, _ = _pair("rewire-static")
'''
        static_new = '''\
    static_owner, static_borrower = _pair("rewire-static")
'''
        return [(pair_old, pair_new), (return_old, return_new), (braked_old, braked_new),
                (static_old, static_new)]

    def config_defined(self) -> list[tuple[str, str]]:
        """Intermediate 31: LAW 4's bare book binds its own class."""
        class_old = '''\
class Service:
    pass


def main() -> None:
'''
        class_new = '''\
class Service:
    pass


class BareService:
    """LAW 4's book's own spell - Service already belongs to the first book."""


def main() -> None:
'''
        bare_old = '''\
    bare_book = md.Spellbook(configuration=md.SpellbookConfiguration())
    bare_book.bind(spell=Service, existence="unique", binding_name="bare")
'''
        bare_new = '''\
    # It binds its own class: one class registers once (a spell_id is the
    # SHA256 of its code), and Service is the first book's.
    bare_book = md.Spellbook(configuration=md.SpellbookConfiguration())
    bare_book.bind(spell=BareService, existence="unique")
'''
        return [(class_old, class_new), (bare_old, bare_new)]

    def conduit_cloud(self) -> list[tuple[str, str]]:
        """Intermediate 37: the other frame binds its own Ledger subclass."""
        class_old = '''\
class Ledger:
    """Something to bind so the frame has real work in it."""


def main() -> None:
'''
        class_new = '''\
class Ledger:
    """Something to bind so the frame has real work in it."""


class OtherLedger(Ledger):
    """The other frame's own Ledger - a new class, so its own spell_id."""


def main() -> None:
'''
        other_old = '''\
    # A DIFFERENT FRAME IS A DIFFERENT WORLD, and so a different cloud.
    # A DIFFERENT binding_name, because a spell_id does not carry the
    # frame - the same class bound identically in two frames collides
    # process-wide. The CLOUD is still per-frame; identity is not.
    other_book = md.Spellbook(aetheric_frame="cloud-other")
    other_book.bind(spell=Ledger, existence="unique", binding_name="other")
'''
        other_new = '''\
    # A DIFFERENT FRAME IS A DIFFERENT WORLD, and so a different cloud.
    # It binds its OWN class: a spell_id is the SHA256 of the class's
    # code and carries neither the frame nor the binding_name, so Ledger
    # bound here as well would be refused process-wide. The CLOUD is
    # still per-frame; identity is not.
    other_book = md.Spellbook(aetheric_frame="cloud-other")
    other_book.bind(spell=OtherLedger, existence="unique", binding_name="other")
'''
        return [(class_old, class_new), (other_old, other_new)]

    def advanced_probes(self) -> list[tuple[str, str]]:
        """The advanced probes: lesson 02's row on the code rule, and a new row for the per-frame regime."""
        old = '''\
class Payload:
    pass


def test_probe_frames_isolate_instances_but_not_identity():
    """Lesson 02 contract, REWRITTEN 2026-08-03. This row used to pin the
    README claim that "two frames bind the SAME class with zero
    collision". EPIC-2026-08-02 S2 retired that: a spell_id hashes the
    bind fingerprint and the FRAME IS NOT IN IT, so identical bindings on
    different frames mint one id and the second conjure is refused.

    What survived is the half that was always the real point - once the
    BINDINGS differ, `unique` is one instance PER FRAME and the wall
    holds. Both halves are asserted here so neither can drift alone."""
    book_a = Spellbook(aetheric_frame="probe-tenant-a")
    book_b = Spellbook(aetheric_frame="probe-tenant-b")
    book_a.bind(spell=Payload, existence="unique", binding_name="tenant-a")
    book_b.bind(spell=Payload, existence="unique", binding_name="tenant-b")
    a = book_a.conjure().meld(spell=Payload, binding_name="tenant-a")
    b = book_b.conjure().meld(spell=Payload, binding_name="tenant-b")
    assert a is not b
    print("frame isolation pinned: same class, two worlds, two singletons")
'''
        new = '''\
class Payload:
    pass


class TenantAPayload(Payload):
    """probe-tenant-a's own Payload - a new class, so its own spell_id."""


class TenantBPayload(Payload):
    """probe-tenant-b's own Payload - a new class, so its own spell_id."""


def test_probe_frames_isolate_instances_but_not_identity():
    """Lesson 02 contract, REWRITTEN 2026-08-03 and again at 0.2.8257.
    This row used to pin the README claim that "two frames bind the SAME
    class with zero collision". EPIC-2026-08-02 S2 retired that, and
    0.2.8257 finished it: a spell_id is the SHA256 of the class's CODE,
    with neither the frame nor anything from the bind call in it, so the
    same class in two frames is one spell_id under any binding_name and
    the second conjure is refused (the second bind, once the first book
    is conjured). Until 0.2.8257 a binding_name per frame told them apart.

    What survived is the half that was always the real point - one class
    PER FRAME, even at one address, and `unique` is one instance per
    frame and the wall holds. Both halves are asserted here so neither
    can drift alone."""
    same_a = Spellbook(aetheric_frame="probe-same-a")
    same_b = Spellbook(aetheric_frame="probe-same-b")
    same_a.bind(spell=Payload, existence="unique", binding_name="tenant-a")
    same_b.bind(spell=Payload, existence="unique", binding_name="tenant-b")
    same_a.conjure()
    with pytest.raises(RuntimeError, match="Conjure refused"):
        same_b.conjure()

    book_a = Spellbook(aetheric_frame="probe-tenant-a")
    book_b = Spellbook(aetheric_frame="probe-tenant-b")
    book_a.bind(spell=TenantAPayload, existence="unique",
                spellframe="tenant", binding_name="payload")
    book_b.bind(spell=TenantBPayload, existence="unique",
                spellframe="tenant", binding_name="payload")
    a = book_a.conjure().meld(spellframe="tenant", binding_name="payload")
    b = book_b.conjure().meld(spellframe="tenant", binding_name="payload")
    assert type(a) is TenantAPayload and type(b) is TenantBPayload
    assert a is not b
    print("frame isolation pinned: one address, a class per world, two "
          "singletons; one class in two worlds is refused")


def test_probe_per_frame_spell_ids_let_one_class_live_in_two_worlds():
    """Lesson 02's other way, pinned. With `process_wide_unique_spell_ids`
    off, a spell_id is unique per FRAME rather than per process, so ONE
    class registers in several worlds - here Payload in two frames, one
    spell_id, one singleton each. It is Aether configuration, installed
    before any frame exists (the first frame seals the regime), which is
    why a lesson never does it and this row may: the fixture resets the
    world around it."""
    policy = md.AetherConfiguration().with_defaults()
    policy.with_process_wide_unique_spell_ids(False)
    policy.activate()
    Aether().activate(policy)
    assert Aether().process_wide_unique_spell_ids is False

    book_a = Spellbook(aetheric_frame="per-frame-a")
    book_b = Spellbook(aetheric_frame="per-frame-b")
    id_a = book_a.bind(spell=Payload, existence="unique")
    id_b = book_b.bind(spell=Payload, existence="unique")
    assert id_a == id_b
    a = book_a.conjure().meld(spell=Payload)
    b = book_b.conjure().meld(spell=Payload)
    assert type(a) is type(b) is Payload
    assert a is not b
    print("per-frame spell ids pinned: one class, two worlds, two singletons")
'''
        return [(old, new)]

    def contract_probes(self) -> list[tuple[str, str]]:
        """The contract probes: the with-book row binds a second class; the three identity rows flip and rename."""
        with_old = '''\
def test_probe_with_book_is_lock_only_not_cleanup():
    """__exit__ releases the lock; the book must remain USABLE after."""
    book = md.Spellbook()
    with book:
        book.bind(spell=Probe, existence="unique")
    # if the with-block had cleaned the book, this second bind would raise
    second = book.bind(spell=Probe, existence="many", binding_name="again")
    assert isinstance(second, str)
'''
        with_new = '''\
def test_probe_with_book_is_lock_only_not_cleanup():
    """__exit__ releases the lock; the book must remain USABLE after."""
    class AfterWith:
        """A second spell for the book. Probe again would be refused
        whether or not the book was cleaned: one class registers once,
        because its spell_id is the SHA256 of its code (0.2.8257)."""

    book = md.Spellbook()
    with book:
        book.bind(spell=Probe, existence="unique")
    # if the with-block had cleaned the book, this second bind would raise
    second = book.bind(spell=AfterWith, existence="many", binding_name="again")
    assert isinstance(second, str)
'''
        return [(with_old, with_new), self._potato_probe(), self._rebind_probe(), self._spellframe_probe()]

    def _potato_probe(self) -> tuple[str, str]:
        """Same-named classes with different code: refused once, two spells now."""
        old = '''\
def test_probe_same_name_different_internals_currently_refused():
    """
    DIVERGENCE FLAG (runs 1-2): owner design intent says spells are
    SHA256 content-matched and same-name/different-internals passes WITH
    binding names. The runtime REFUSES it: DuplicateSpellNameStrategy
    keys on the bare name and ignores the binding_name/spellframe
    disambiguation its own error message recommends. This probe pins
    CURRENT behavior; flip it to the pass-assertion when the strategy is
    fixed (tracked on the UX/AIX beginner epic as a runtime bug).
    """
    book = md.Spellbook()
    book.bind(spell=_make_potato("russet"), existence="unique",
              binding_name="russet")
    book.bind(spell=_make_potato("yukon"), existence="many",
              binding_name="yukon")
    with pytest.raises(md.SpellbookValidationError):
        book.conjure()
    print("same-name diff-SHA with binding names: REFUSED (intent: pass)")
'''
        new = '''\
def test_probe_same_name_different_internals_are_two_spells():
    """
    FLIPPED (0.2.8206, 0.2.8257): two classes NAMED Potato with different
    internals are two spells, each at its own address. A spell_id is the
    SHA256 of each class's code - here a different class-level value and
    a different closure value - so the ids differ, and since 0.2.8206
    Phase 4 checks the full (spellframe, binding_name) address instead of
    the bare name, so conjure accepts both.

    This row used to pin the refusal under a DIVERGENCE FLAG: owner design
    intent said spells are SHA256 content-matched and same-name/different-
    internals passes WITH binding names, while DuplicateSpellNameStrategy
    keyed on the bare name. The intent is the behavior now; the flag is
    closed.
    """
    book = md.Spellbook()
    book.bind(spell=_make_potato("russet"), existence="unique",
              binding_name="russet")
    book.bind(spell=_make_potato("yukon"), existence="many",
              binding_name="yukon")
    conduit = book.conjure()
    russet = conduit.meld(spell="Potato", binding_name="russet")
    yukon = conduit.meld(spell="Potato", binding_name="yukon")
    assert russet.describe() == "potato:russet"
    assert yukon.describe() == "potato:yukon"
    print("same-name diff-SHA with binding names: two spells (the intent)")
'''
        return old, new

    def _rebind_probe(self) -> tuple[str, str]:
        """The same class rebound by binding_name: a conjure refusal once, a bind refusal now."""
        old = '''\
def test_probe_same_class_rebind_without_frames_fails_conjure():
    """
    The observed run truth: the SAME class (same SHA) bound twice with
    only binding_names to tell them apart dies at conjure with
    DUPLICATE_SPELL_NAME.
    """
    book = md.Spellbook()
    book.bind(spell=Probe, existence="unique", binding_name="first")
    book.bind(spell=Probe, existence="many", binding_name="second")
    with pytest.raises(md.SpellbookValidationError):
        book.conjure()
    print("same-SHA rebind without frames: conjure refused (as observed)")
'''
        new = '''\
def test_probe_same_class_rebind_is_refused_at_bind():
    """
    The SAME class bound twice in one book, told apart only by
    binding_name, is refused at the second BIND (0.2.8257): a spell_id is
    the SHA256 of the class's code and of nothing from the bind call, so
    both binds name one spell, and one object registers once. This row
    used to pin the observed run truth before that - the binding_name made
    a second spell_id and conjure refused the pair with
    DUPLICATE_SPELL_NAME.
    """
    book = md.Spellbook()
    book.bind(spell=Probe, existence="unique", binding_name="first")
    with pytest.raises(RuntimeError, match="Spell ID collision"):
        book.bind(spell=Probe, existence="many", binding_name="second")
    print("same class rebound by binding_name: refused at bind")
'''
        return old, new

    def _spellframe_probe(self) -> tuple[str, str]:
        """The same class rebound in another spellframe: refused at bind, whatever the frame."""
        old = '''\
def test_probe_same_class_rebind_with_distinct_frames():
    """
    ANSWERED (run 2): frame separation does NOT legalize same-name
    rebinds - the name strategy ignores frames entirely. Part of the
    same divergence flag as the potato probe.
    """
    book = md.Spellbook()
    book.bind(spell=Probe, existence="unique",
              spellframe="pool-a", binding_name="first")
    book.bind(spell=Probe, existence="many",
              spellframe="pool-b", binding_name="second")
    with pytest.raises(md.SpellbookValidationError):
        book.conjure()
    print("same-SHA rebind across frames: REFUSED (frames do not "
          "disambiguate the name strategy either - same divergence flag)")
'''
        new = '''\
def test_probe_same_class_rebind_across_spellframes_is_refused_at_bind():
    """
    ANSWERED (0.2.8257): another spellframe does not make the same class
    a second spell either. The spell_id is the class's code, so the
    second bind is refused whatever spellframe or binding_name it names.
    This row used to pin a conjure refusal from the name strategy, which
    ignored frames (run 2) - part of the potato row's divergence flag,
    now closed.
    """
    book = md.Spellbook()
    book.bind(spell=Probe, existence="unique",
              spellframe="pool-a", binding_name="first")
    with pytest.raises(RuntimeError, match="Spell ID collision"):
        book.bind(spell=Probe, existence="many",
                  spellframe="pool-b", binding_name="second")
    print("same class rebound in another spellframe: refused at bind")
'''
        return old, new

    def intermediate_probes(self) -> list[tuple[str, str]]:
        """The intermediate probes: LAW 4's bare book and the second cloud frame bind classes of their own."""
        bare_old = '''\
    bare = Spellbook(configuration=md.SpellbookConfiguration())
    bare.bind(spell=Payload, existence="unique", binding_name="bare")
'''
        bare_new = '''\
    # The bare book binds its own class: one class registers once (a
    # spell_id is the SHA256 of its code), and Payload is the first book's.
    class BarePayload:
        """The bare book's own spell."""

    bare = Spellbook(configuration=md.SpellbookConfiguration())
    bare.bind(spell=BarePayload, existence="unique")
'''
        ledger_old = '''\
class _Ledger:
    pass


def test_probe_conduit_cloud_is_frame_owned_and_shared():
'''
        ledger_new = '''\
class _Ledger:
    pass


class _OtherLedger(_Ledger):
    """The second frame's own ledger - a new class, so its own spell_id."""


def test_probe_conduit_cloud_is_frame_owned_and_shared():
'''
        cloud_old = '''\
    # binding_name differs because a spell_id does not carry the frame -
    # identical bindings on two frames collide process-wide. The CLOUD is
    # what this row is about, and it IS per-frame.
    first = Spellbook(aetheric_frame="probe-cloud-a")
    first.bind(spell=_Ledger, existence="unique", binding_name="cloud-a")
    second = Spellbook(aetheric_frame="probe-cloud-b")
    second.bind(spell=_Ledger, existence="unique", binding_name="cloud-b")
'''
        cloud_new = '''\
    # The second frame binds its OWN class: a spell_id is the SHA256 of
    # the class's code and carries neither the frame nor the binding_name,
    # so _Ledger bound in both frames would be refused process-wide. The
    # CLOUD is what this row is about, and it IS per-frame.
    first = Spellbook(aetheric_frame="probe-cloud-a")
    first.bind(spell=_Ledger, existence="unique", binding_name="cloud-a")
    second = Spellbook(aetheric_frame="probe-cloud-b")
    second.bind(spell=_OtherLedger, existence="unique", binding_name="cloud-b")
'''
        return [(bare_old, bare_new), (ledger_old, ledger_new), (cloud_old, cloud_new)]

    def bootstrap_text(self) -> list[tuple[str, str]]:
        """Beginner 18: why the same objects cannot register twice."""
        old = '''\
      melder worlds do not "switch environments" - the same objects
      cannot register twice (spells are content-fingerprinted), so your
      MODULE decides what to build, once, at the root.
'''
        new = '''\
      melder worlds do not "switch environments" - the same objects
      cannot register twice (a spell_id is the SHA256 of an object's code
      and data), so your MODULE decides what to build, once, at the root.
'''
        return [(old, new)]

    def same_class_text(self) -> list[tuple[str, str]]:
        """Beginner 24: one class, one spell; the name rule it taught retired at 0.2.8206."""
        old = '''\
GOAL: One spell name, one visible spell - CURRENT RUNTIME TRUTH (probe-
      proven): conjure refuses ANY two spells sharing a name, even
      across frames, even with different internals. The working pattern
      for one shape in many roles: tiny subclasses, one name each.
      (The probe suite flags the intended SHA-content semantics as an
      open runtime question - the lesson here is what works TODAY.)
'''
        new = '''\
GOAL: One class, one spell - a spell_id is the SHA256 of the class's
      code, so the SAME class registers once, whatever binding name or
      lifecycle you give it (beginner 30). The working pattern for one
      shape in many roles: tiny subclasses, one per role - each is a new
      class, so its own spell, at its own address. (Same-NAMED classes
      with different code may also coexist at different addresses since
      0.2.8206; the contract probes pin both rules.)
'''
        return [(old, new)]

    def double_bind_text(self) -> list[tuple[str, str]]:
        """Beginner 30: the refusal is the one-object law, not a fingerprint."""
        goal_old = '''\
GOAL: Binding the SAME class twice is refused - spells are
      content-fingerprinted and one fingerprint registers once. When one
      shape must serve two roles, make two shapes: subclass it (see 24).
SURFACE EXERCISED: the one-fingerprint law at bind time
'''
        goal_new = '''\
GOAL: Binding the SAME class twice is refused - a spell_id is the
      SHA256 of the class's code, and one object registers once, under
      any binding name or lifecycle. When one shape must serve two
      roles, make two shapes: subclass it (see 24).
SURFACE EXERCISED: the one-object law at bind time
'''
        print_old = '''\
        print("same fingerprint refused:", type(err).__name__)
'''
        print_new = '''\
        print("same object refused:", type(err).__name__)
'''
        fix_old = '''\
    # the fix: a subclass IS a different fingerprint (and a different name)
'''
        fix_new = '''\
    # the fix: a subclass IS a new class - a new spell_id (and a new name)
'''
        return [(goal_old, goal_new), (print_old, print_new), (fix_old, fix_new)]

    def workshop_text(self) -> list[tuple[str, str]]:
        """Expert 13: a distinct class per frame is what keeps the worlds apart, not the binding_name."""
        old = '''\
    # A distinct binding_name per frame: spell_id is process-wide and the
    # frame is NOT in the fingerprint (advanced 02), so identical bindings
    # across worlds would collide.
'''
        new = '''\
    # A distinct class per frame: a spell_id is the SHA256 of the class's
    # code, process-wide by default, with neither the frame nor the
    # binding_name in it (advanced 02), so one class bound in two worlds
    # would be refused. The binding_name only names each world's address.
'''
        return [(old, new)]

    def codegen_text(self) -> list[tuple[str, str]]:
        """Expert 26: one spell_id - a version's code - lives in one lane."""
        old = '''\
      One binding-signature SHA256 lives in exactly ONE lane, network
      wide, permanently - there is no release verb. `bind_inactive`
      already declared the staged version onto `default`, so
      `register_spell(..., lane=...)` for that id raises the REDISCOVERY
      signal naming the holding lane. That raise is a signal, not a
      failure: identical content rebinds to the same SHA, and this is the
      system saying "you built this before, here".
'''
        new = '''\
      One spell_id - the SHA256 of a version's code - lives in exactly
      ONE lane, network wide, permanently - there is no release verb.
      `bind_inactive` already declared the staged version onto `default`,
      so `register_spell(..., lane=...)` for that id raises the
      REDISCOVERY signal naming the holding lane. That raise is a signal,
      not a failure: identical code always mints the same SHA, and this
      is the system saying "you built this before, here".
'''
        return [(old, new)]

    def agents_text(self) -> list[tuple[str, str]]:
        """The examples' AGENTS.md: the divergence flag closes into the identity law."""
        old = '''\
- Spell NAMES are unique per book at conjure - CURRENT behavior refuses any
  name collision regardless of binding names, frames, or content SHA.
  DIVERGENCE FLAG: owner design intent (twice stated) is SHA256 content
  matching with binding-name disambiguation; DuplicateSpellNameStrategy
  ignores the disambiguators its own error message recommends. Tracked as a
  runtime bug candidate on the beginner epic. Until fixed: subclass-per-role
  (24) and collection-as-spell registries (33) are the working patterns.
'''
        new = '''\
- SPELL IDENTITY IS THE CODE (0.2.8257): a spell_id is the SHA256 of the
  registered object's code - its methods and constructor (bodies included),
  class-level values and bases, or an existing object's class and data -
  and of nothing from the bind call. One object registers once: binding it
  again under any binding_name, existence or spellframe is refused at bind
  ("Spell ID collision"), or at conjure when another Book holds it
  ("Conjure refused"). A changed class is a new spell_id: stage it with
  bind_inactive and notch. Same-NAMED classes with different code coexist
  at different addresses (0.2.8206). Working patterns: subclass-per-role
  (24) and collection-as-spell registries (33).
  History: this bullet carried a DIVERGENCE FLAG - spell NAMES unique per
  book at conjure, refused regardless of binding names, frames or content
  SHA, against the owner's stated intent of SHA256 content matching.
  0.2.8206 made Phase 4 check the full address and 0.2.8257 made the
  spell_id the code; the flag is closed.
'''
        return [(old, new)]


class UxRewrite:
    """Apply `UxEdits` to one repository root, all-or-nothing, each file keeping its own line ending."""

    def __init__(self, root: Path) -> None:
        """
        Args:
            root: The repository root (the folder holding UX_and_AIX_experiences/).
        """
        self._root = root
        self._staged: dict[str, tuple[bytes, bytes]] = {}

    @staticmethod
    def _ending(rel: str, text: str) -> str:
        """Return the file's one line ending, refusing mixed or bare-CR endings."""
        crlf = text.count("\r\n")
        bare_lf = text.count("\n") - crlf
        if "\r" in text.replace("\r\n", ""):
            sys.exit(f"ENDING {rel}: a bare CR; refusing")
        if crlf and bare_lf:
            sys.exit(f"ENDING {rel}: {crlf} CRLF and {bare_lf} LF line endings; refusing a mixed file")
        return "\r\n" if crlf else "\n"

    def stage(self) -> None:
        """Apply every edit in memory; exit naming the first anchor that does not occur exactly once."""
        for rel, pairs in UxEdits().files().items():
            raw = (self._root / rel).read_bytes()
            text = raw.decode("utf-8")
            ending = self._ending(rel, text)
            body = text.replace("\r\n", "\n")
            for number, (old, new) in enumerate(pairs, 1):
                count = body.count(old)
                if count != 1:
                    sys.exit(f"ANCHOR {rel} #{number}: {count} occurrences of {old.splitlines()[0]!r}")
                body = body.replace(old, new)
            out = body.replace("\n", "\r\n") if ending == "\r\n" else body
            self._staged[rel] = (raw, out.encode("utf-8"))

    def diff(self) -> str:
        """The unified diff (LF) of every staged file."""
        chunks: list[str] = []
        for rel, (before, after) in self._staged.items():
            old = before.decode("utf-8").replace("\r\n", "\n").splitlines(keepends=True)
            new = after.decode("utf-8").replace("\r\n", "\n").splitlines(keepends=True)
            chunks.extend(difflib.unified_diff(old, new, fromfile="a/" + rel, tofile="b/" + rel))
        return "".join(chunks)

    def summary(self) -> list[str]:
        """One line per staged file: its ending and its line counts before and after."""
        lines: list[str] = []
        for rel, (before, after) in self._staged.items():
            ending = "CRLF" if b"\r\n" in before else "LF"
            lines.append(f"{rel}: {ending} {before.count(b'\n')} -> {after.count(b'\n')} lines")
        return lines

    def write(self, backup: Path) -> None:
        """Write every staged file after checking none changed since staging; keep the originals in `backup`."""
        for rel, (before, _) in self._staged.items():
            if (self._root / rel).read_bytes() != before:
                sys.exit(f"CHANGED {rel}: the file moved since staging; nothing written")
        for rel, (before, _) in self._staged.items():
            target = backup / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(before)
        for rel, (_, after) in self._staged.items():
            (self._root / rel).write_bytes(after)
        for rel, (_, after) in self._staged.items():
            if (self._root / rel).read_bytes() != after:
                sys.exit(f"READBACK {rel}: the written bytes differ; originals in {backup}")


def main() -> None:
    """Stage, report, and write only with --write."""
    if len(sys.argv) < 2:
        sys.exit("usage: rewrite_ux_examples.py <repository root> [--write] [--diff <path>]")
    root = Path(sys.argv[1]).resolve()
    rewrite = UxRewrite(root)
    rewrite.stage()
    diff_path: Optional[str] = None
    if "--diff" in sys.argv:
        diff_path = sys.argv[sys.argv.index("--diff") + 1]
        Path(diff_path).write_text(rewrite.diff(), encoding="utf-8")
    for line in rewrite.summary():
        print(line)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if "--write" not in sys.argv:
        print("CHECK OK", now, root, "diff:", diff_path)
        return
    backup = Path("/tmp/m0_mq/bak_ux") / now.replace(":", "")
    rewrite.write(backup)
    print("WROTE", len(rewrite.summary()), "files under", root, "originals in", backup)


if __name__ == "__main__":
    main()
