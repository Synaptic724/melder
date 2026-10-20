"""
Correct the root-teardown wording in src_architecture and src_components (TASK-2026-10-19-correct_root_teardown_docs_wording).

Run from context_compass/ with any Python 3.10+:

    python artifacts/root_teardown_docs_20261018/scripts/correct_root_teardown_wording.py

What it does, all-or-nothing:
- Refuses unless each document matches its index's staleness proof (line count and sha256), so no other writer's
  edit is in flight.
- Replaces ten blocks the closed task wrote (TASK-2026-10-18-document_root_teardown_cleans_only_what_it_holds),
  each matched on its exact current text, which must occur once: the "open with the owner" and "Known, not fixed"
  framing goes, and the text says the root's teardown cleans what it holds - its stores' records and what its pools
  keep, the children recorded for objects still out included - and reports a disposal method that raises like any
  other. Today's behaviour, the order, the evidence lines and the measured cases stay.
- Writes before-copies to before_correction/, checks every new line against the 120-character cap, writes both
  documents through os.replace, and writes the preservation report: the lines removed and added must be exactly
  the blocks' old and new lines.
The indexes are regenerated afterwards by the index tool; this script never writes an index.
"""
import hashlib
import os
import re
import shutil
import sys
from collections import Counter
from pathlib import Path

LANE = Path("artifacts/root_teardown_docs_20261018")
ARCH = Path("system_docs/src_architecture.md")
COMP = Path("system_docs/src_components.md")

ARCH_EDITS = [
    ("A1 Runtime Model",
     "a scope teardown ends its stores, and a purge disposes what it retires. A root's teardown cleans only what the root\n"
     "holds (owner, 2026-10-18): what its stores record and the idle objects of its managed pools; an object a holder\n"
     "leased from a pool stays that holder's, with the `many` children recorded for it (two places where today's code\n"
     "differs are open with the owner: Operational Invariants). It does not police userland objects: it does\n",
     "a scope teardown ends its stores, and a purge disposes what it retires. A root's teardown cleans only what the root\n"
     "holds (owner, 2026-10-18): what its stores record and what its managed pools keep - their idle objects and the\n"
     "children recorded with their objects, out ones included; an object a holder leased from a pool stays that holder's\n"
     "(Operational Invariants). It does not police userland objects: it does\n"),
    ("A2 Cleanup sequence step 7",
     "   join the same group (0.2.8243). The root's ward (its lesser lineage) and SpellSpaces end before its store, so a\n"
     "   consumer held there gives a leased object back while the pools still take it; one the root's own store holds\n"
     "   meets an unregistered pool. The owner's rule that a root's teardown cleans only what it holds, and the two\n"
     "   places open with the owner, are under Operational Invariants (2026-10-18).\n",
     "   join the same group (0.2.8243). The root's ward (its lesser lineage) and SpellSpaces end before its store, so a\n"
     "   consumer held there gives a leased object back while the pools still take it; a consumer the root's own store\n"
     "   holds meets an unregistered pool, and the teardown reports that release's error like any disposal method that\n"
     "   raises. This follows the owner's rule that a root's teardown cleans only what it holds (Operational Invariants).\n"),
    ("A3 Operational invariant",
     "- A root's teardown cleans only what the root holds (2026-10-19; the owner's rule, chat 2026-10-18: \"if the root\n"
     "  cleans up it only cleans up whats held by the root\"; documentation only - the code is unchanged): what its stores\n"
     "  record and the idle objects of its managed pools, with the `many` children recorded for those objects. An object a\n"
     "  holder leased from a pool is the holder's: Melder keeps no reference to it, never disposes it at teardown, and a\n"
     "  release of it after the teardown no longer reaches that root's pool (Failure Modes and Error Paths). Today's\n"
     "  order: `Conduit._cleanup_normal_conduit` tears down the cluster facade, the Meld, the ward (the lesser lineage)\n"
     "  and the SpellSpaces before the root's own store, so a consumer held by a lesser conduit or a spellspace gives its\n"
     "  leased object back while the root's pools still take it; then `Creations.cleanup` detaches its maps under the\n"
     "  store lock, unregisters every pool from `ReleaseManagedSpell`, cleans the pools newest first and disposes its\n"
     "  registry newest first, raising one group; `ManagedSpellQuantity.cleanup` disposes each idle object, newest first,\n"
     "  with its recorded children, then the children recorded for objects still out, then the orphaned records. Two\n"
     "  places are open with the owner: (1) a consumer the root's own store holds whose disposal method gives its leased\n"
     "  object back meets a pool already unregistered - the release raises the not-managed ValueError inside that method,\n"
     "  the store collects it, the teardown raises ExceptionGroup \"Conduit torn down with disposal failures.\" and the\n"
     "  object is left undisposed (the owner asked why a cleanup that disposes should raise at all); (2) the pool disposes\n"
     "  the children recorded for an object still out, which the root does not hold, under the holder that keeps the\n"
     "  object. Measured on 0.2.8258 (3.14t, the GIL off and on): a root-held `many` handler whose `finish` releases its\n"
     "  pooled connection makes the teardown raise and leaves the connection open, the same handler in a lesser conduit\n"
     "  gives it back cleanly, and an out session's `many` cursor closes at teardown while the session stays open. Until\n"
     "  the owner decides, the cleanup sequence and the failure modes describe today's behaviour.\n",
     "- A root's teardown cleans only what the root holds (2026-10-19; the owner's rule, chat 2026-10-18: \"if the root\n"
     "  cleans up it only cleans up whats held by the root\"; documentation only - the code is unchanged): what its stores\n"
     "  record and what its managed pools keep - their idle objects and the `many` children recorded with their objects,\n"
     "  objects still out included, since the pool holds those children (`_children_by_object`). An object a holder\n"
     "  leased from a pool is the holder's: Melder keeps no reference to it, never disposes it at teardown, and a release\n"
     "  of it after the teardown no longer reaches that root's pool (Failure Modes and Error Paths). Today's order:\n"
     "  `Conduit._cleanup_normal_conduit` tears down the cluster facade, the Meld, the ward (the lesser lineage) and the\n"
     "  SpellSpaces before the root's own store, so a consumer held by a lesser conduit or a spellspace gives its leased\n"
     "  object back while the root's pools still take it; then `Creations.cleanup` detaches its maps under the store\n"
     "  lock, unregisters every pool from `ReleaseManagedSpell`, cleans the pools newest first and disposes its registry\n"
     "  newest first, raising one group; `ManagedSpellQuantity.cleanup` disposes each idle object, newest first, with its\n"
     "  recorded children, then the children recorded for objects still out, then the orphaned records. A consumer the\n"
     "  root's own store holds whose disposal method gives its leased object back therefore meets a pool already\n"
     "  unregistered: the release raises the not-managed ValueError inside that method, the store collects it as that\n"
     "  method's failure, and once everything else is disposed the teardown raises ExceptionGroup \"Conduit torn down\n"
     "  with disposal failures.\"; the leased object, which the root does not hold, is not disposed. Neither is a defect\n"
     "  (the owner's review, chat 2026-10-19): the pool holds the children of its objects, so the root disposes them;\n"
     "  resets run only when an object is given back and teardown runs only disposal methods; a disposal method that\n"
     "  raises is reported. Measured on 0.2.8258 (3.14t, the GIL off and on): a root-held `many` handler whose `finish`\n"
     "  releases its pooled connection makes the teardown raise and leaves the connection open, the same handler in a\n"
     "  lesser conduit gives it back cleanly, and an out session's `many` cursor closes at teardown while the session\n"
     "  stays open.\n"),
    ("A4 Failure mode",
     "- Known, not fixed (open with the owner, 2026-10-18): a root's teardown raises ExceptionGroup \"Conduit torn down with\n"
     "  disposal failures.\" when a consumer its own store holds gives a leased object back in its disposal method. The\n"
     "  store has already unregistered and cleaned its pools, so the release raises ValueError \"<Type> is not a managed\n"
     "  spell class in any live root: ...\" inside that method (when no other live root pools the class), collected as\n"
     "  RuntimeError \"Failed to dispose object ... using method '<name>': ...\" chained from it; the teardown still\n"
     "  finishes and the object is left undisposed. A consumer held by a lesser conduit or a spellspace gives the object\n"
     "  back cleanly, because those scopes end before the root's store. The owner questioned this raise with the rule\n"
     "  that a root's teardown cleans only what it holds (Operational Invariants); until the owner decides, give such\n"
     "  objects back before the root ends, or hold their consumers in a lesser conduit.\n",
     "- A root's teardown raises ExceptionGroup \"Conduit torn down with disposal failures.\" when a consumer its own store\n"
     "  holds gives a leased object back in its disposal method (documented 2026-10-19). The store has already\n"
     "  unregistered and cleaned its pools, so the release raises ValueError \"<Type> is not a managed spell class in any\n"
     "  live root: ...\" inside that method (when no other live root pools the class), collected as RuntimeError \"Failed\n"
     "  to dispose object ... using method '<name>': ...\" chained from it. It is reported like any disposal method that\n"
     "  raises, after the teardown has disposed everything the root holds; the leased object, which the root does not\n"
     "  hold, is not disposed. A consumer held by a lesser conduit or a spellspace gives the object back cleanly, because\n"
     "  those scopes end before the root's store. To keep the teardown quiet, give such objects back before the root\n"
     "  ends, or hold their consumers in a lesser conduit (Operational Invariants: a root's teardown cleans only what it\n"
     "  holds).\n"),
    ("A5 Handoff entry",
     "2026-10-19 a root's teardown cleans only what the root holds (documentation only; the owner's rule, in chat on\n"
     "2026-10-18): a sentence in the Runtime Model, the cleanup sequence (the unregister-first order, the ward and\n"
     "SpellSpaces ending before the store), a new operational invariant (the rule, today's order, two places open with the\n"
     "owner, measured on 0.2.8258), a Known-not-fixed failure mode (a consumer the root's own store holds that gives its\n"
     "object back in its disposal method makes the teardown raise) and the managed lease diagram's teardown order (it read\n"
     "\"pools first ... -> unregistered\"; the code unregisters first) carry it; the component map carries the per-component\n"
     "text. Open with the owner: whether the root-held consumer's release should be accepted at teardown instead of\n"
     "raising, and whether a pool should leave the children recorded for an object still out to that object's holder.\n"
     "Checked against `Conduit._cleanup_normal_conduit`, `Creations.cleanup`, `ManagedSpellQuantity.cleanup` and\n"
     "`ReleaseManagedSpell._resolve_pool`.\n",
     "2026-10-19 a root's teardown cleans only what the root holds (documentation only; the owner's rule, in chat on\n"
     "2026-10-18): a sentence in the Runtime Model, the cleanup sequence (the unregister-first order, the ward and\n"
     "SpellSpaces ending before the store), a new operational invariant (the rule, what the root holds, today's order,\n"
     "measured on 0.2.8258), a failure mode (a consumer the root's own store holds that gives its object back in its\n"
     "disposal method makes the teardown report that release's error) and the managed lease diagram's teardown order (it\n"
     "read \"pools first ... -> unregistered\"; the code unregisters first) carry it; the component map carries the\n"
     "per-component text. Corrected after the owner's review (chat 2026-10-19): the first wording left two behaviours\n"
     "as questions for the owner - a pool disposing the children it keeps for objects still out, and the reported\n"
     "release error - and neither is a defect: the pool holds those children, so the root disposes them, and a\n"
     "disposal method that raises is reported like any other. Checked against `Conduit._cleanup_normal_conduit`,\n"
     "`Creations.cleanup`, `ManagedSpellQuantity.cleanup` and `ReleaseManagedSpell._resolve_pool`.\n"),
]

COMP_EDITS = [
    ("C1 Creations and SpellSpace",
     "A root's teardown cleans only what the root holds (owner, 2026-10-18); the two places where this cleanup is open\n"
     "with the owner are under Component: Managed Spell Pools (Lifecycle/Cleanup).\n",
     "The cleanup follows the owner's rule that a root's teardown cleans only what the root holds (2026-10-18; see\n"
     "Component: Managed Spell Pools, Lifecycle/Cleanup).\n"),
    ("C2 Managed Spell Pools Lifecycle",
     "- A root's teardown cleans only what the root holds (the owner's rule, 2026-10-18): its stores' records and its\n"
     "  pools' idle objects with the children recorded for them; an object out is its holder's, with the children\n"
     "  recorded for it. Today the root's ward and SpellSpaces end first (`Conduit._cleanup_normal_conduit`), then\n"
     "  `Creations.cleanup` unregisters the pools, cleans them newest first and disposes its registry. Two places are\n"
     "  open with the owner (the code is unchanged): `ManagedSpellQuantity.cleanup` disposes the children recorded for\n"
     "  objects still out - an out session's `many` cursor closes at teardown while the session stays open (measured on\n"
     "  0.2.8258) - and a consumer the root's own store holds whose disposal method gives its object back meets the\n"
     "  unregistered pool (Failure Modes).\n",
     "- A root's teardown cleans only what the root holds (the owner's rule, 2026-10-18): its stores' records and what its\n"
     "  pools keep - their idle objects and the children recorded with their objects, objects still out included (an out\n"
     "  session's `many` cursor closes at teardown while the session stays open, measured on 0.2.8258); an object out is\n"
     "  its holder's. Today the root's ward and SpellSpaces end first (`Conduit._cleanup_normal_conduit`), then\n"
     "  `Creations.cleanup` unregisters the pools, cleans them newest first and disposes its registry, so a consumer the\n"
     "  root's own store holds whose disposal method gives its object back meets the unregistered pool and the teardown\n"
     "  reports the release's error like any disposal failure (Failure Modes). Both are cleanup working as intended (the\n"
     "  owner's review, chat 2026-10-19).\n"),
    ("C3 Managed Spell Pools failure mode",
     "- Known, not fixed (open with the owner, 2026-10-18): a consumer the root's own store holds whose disposal method\n"
     "  gives its leased object back makes the root's teardown raise ExceptionGroup \"Conduit torn down with disposal\n"
     "  failures.\": the release meets the unregistered pool and raises the not-managed ValueError inside that method,\n"
     "  collected as RuntimeError \"Failed to dispose object ... using method '<name>': ...\" chained from it, and the\n"
     "  object is left undisposed. The same consumer in a lesser conduit or a spellspace gives it back cleanly (measured\n"
     "  on 0.2.8258, the GIL off and on).\n",
     "- A consumer the root's own store holds whose disposal method gives its leased object back makes the root's\n"
     "  teardown raise ExceptionGroup \"Conduit torn down with disposal failures.\" (documented 2026-10-19): the release\n"
     "  meets the unregistered pool and raises the not-managed ValueError inside that method, collected as RuntimeError\n"
     "  \"Failed to dispose object ... using method '<name>': ...\" chained from it - reported like any disposal method\n"
     "  that raises; the leased object, which the root does not hold, is not disposed. The same consumer in a lesser\n"
     "  conduit or a spellspace gives it back cleanly (measured on 0.2.8258, the GIL off and on).\n"),
    ("C4 Managed lease flow step 5",
     "   The root's ward and SpellSpaces end before its store, so their consumers give objects back first; a consumer\n"
     "   the root's own store holds meets the unregistered pool (open with the owner, 2026-10-18; Component: Managed\n"
     "   Spell Pools).\n",
     "   The root's ward and SpellSpaces end before its store, so their consumers give objects back first; a consumer\n"
     "   the root's own store holds meets the unregistered pool, and the teardown reports the release's error like any\n"
     "   disposal failure (Component: Managed Spell Pools).\n"),
    ("C5 Handoff entry",
     "2026-10-19 a root's teardown cleans only what the root holds (documentation only; the owner's rule, in chat on\n"
     "2026-10-18): Creations and SpellSpace points at it; Managed Spell Pools carries the rule, today's teardown order and\n"
     "the two places open with the owner in Lifecycle/Cleanup, and the root-held consumer's ExceptionGroup as a\n"
     "Known-not-fixed failure mode; the managed lease flow's teardown step names the ward and SpellSpaces ending first.\n"
     "Open with the owner: the root-held consumer's release at teardown, and the children recorded for an object still\n"
     "out.\n",
     "2026-10-19 a root's teardown cleans only what the root holds (documentation only; the owner's rule, in chat on\n"
     "2026-10-18): Creations and SpellSpace points at it; Managed Spell Pools carries the rule, what the root holds and\n"
     "today's teardown order in Lifecycle/Cleanup, and the root-held consumer's reported ExceptionGroup as a failure\n"
     "mode; the managed lease flow's teardown step names the ward and SpellSpaces ending first. Corrected after the\n"
     "owner's review (chat 2026-10-19): the first wording left the children a pool keeps for objects still out, and the\n"
     "root-held consumer's release error, as questions for the owner; neither is a defect - the pool holds those\n"
     "children, and a disposal method that raises is reported like any other.\n"),
]


def index_proof(doc: Path) -> tuple:
    """Return (line_count, sha256) recorded in the document's index."""
    index = doc.with_name(doc.stem + "_index.md").read_text(encoding="utf-8")
    lines = int(re.search(r"\| line_count \| (\d+) \|", index).group(1))
    sha = re.search(r"\| content_sha256 \| `([0-9a-f]{64})` \|", index).group(1)
    return lines, sha


def check_against_index(doc: Path, raw: bytes) -> None:
    """Refuse unless the document's bytes match its index's staleness proof."""
    lines, sha = index_proof(doc)
    text = raw.decode("utf-8")
    count = text.count("\n") + (0 if text.endswith("\n") else 1)
    if count != lines or hashlib.sha256(raw).hexdigest() != sha:
        raise SystemExit(f"{doc}: differs from its index (another writer?); nothing applied.")


def apply_edits(doc: Path, text: str, edits: list) -> tuple:
    """Apply each (label, old, new) once; return the new text and the old and new lines applied."""
    removed, added = [], []
    for label, old, new in edits:
        count = text.count(old)
        if count != 1:
            raise SystemExit(f"{doc} {label}: old block must occur once, found {count}; nothing applied.")
        for line in new.splitlines():
            if len(line) > 120:
                raise SystemExit(f"{doc} {label}: new line over 120 characters ({len(line)}): {line!r}")
        text = text.replace(old, new, 1)
        removed.extend(old.splitlines())
        added.extend(new.splitlines())
    return text, removed, added


def preservation(before: str, after: str, removed: list, added: list) -> list:
    """Return report lines; raise unless the non-blank line multiset changed by exactly the blocks."""
    b = Counter(line for line in before.splitlines() if line.strip())
    a = Counter(line for line in after.splitlines() if line.strip())
    gone, came = b - a, a - b
    want_gone = Counter(line for line in removed if line.strip()) - Counter(line for line in added if line.strip())
    want_came = Counter(line for line in added if line.strip()) - Counter(line for line in removed if line.strip())
    if gone != want_gone or came != want_came:
        raise SystemExit("preservation: the document changed outside the edited blocks; nothing applied.")
    return [f"removed {sum(gone.values())} lines, added {sum(came.values())} lines; "
            f"no other non-blank line changed (multiset check)"]


def main() -> None:
    """Check, apply in memory, verify, then write both documents and the report."""
    report = []
    plans = []
    for doc, edits in ((ARCH, ARCH_EDITS), (COMP, COMP_EDITS)):
        raw = doc.read_bytes()
        check_against_index(doc, raw)
        before = raw.decode("utf-8")
        after, removed, added = apply_edits(doc, before, edits)
        for phrase in ("open with the owner", "Known, not fixed (open", "two places", "Until\n  the owner decides"):
            for label, old, new in edits:
                if phrase in new:
                    raise SystemExit(f"{doc} {label}: new text still says {phrase!r}")
        report.append(f"{doc}: {len(before.splitlines())} -> {len(after.splitlines())} lines; "
                      + preservation(before, after, removed, added)[0])
        plans.append((doc, raw, after))
    backup = LANE / "before_correction"
    backup.mkdir(exist_ok=True)
    for doc, raw, after in plans:
        target = backup / doc.name
        if target.exists():
            raise SystemExit(f"{target} exists: this correction was applied before; nothing applied.")
    for doc, raw, after in plans:
        (backup / doc.name).write_bytes(raw)
    for doc, raw, after in plans:
        tmp = doc.with_name(doc.name + ".m2tmp")
        tmp.write_text(after, encoding="utf-8")
        os.replace(tmp, doc)
        if doc.read_text(encoding="utf-8") != after:
            raise SystemExit(f"{doc}: read-back differs")
        report.append(f"{doc}: sha256 {hashlib.sha256(after.encode('utf-8')).hexdigest()}")
    runs = LANE / "runs"
    runs.mkdir(exist_ok=True)
    (runs / "preservation_correction.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
    sys.stdout.write("\n".join(report) + "\n")


if __name__ == "__main__":
    main()
