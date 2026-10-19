"""
Write the owner's teardown rule into src_architecture and src_components
(TASK-2026-10-18-document_root_teardown_cleans_only_what_it_holds).

Run from the repository root (any Python 3.10+):

    python context_compass/artifacts/root_teardown_docs_20261018/scripts/apply_root_teardown_docs.py

Refuses before writing anything unless, for each document, its sha256 and line count equal what its index records
(so no other writer is mid-pass) and every anchor occurs exactly once. Keeps a before-copy and the multiset of
non-blank, whitespace-normalised lines of each document under ../before/, writes each document in place (LF kept),
and writes a preservation report under ../runs/ listing every line whose count fell (must be only the replaced
lines). Regenerate both indexes afterwards with the index tool.
"""
import hashlib
import re
import sys
from collections import Counter
from pathlib import Path

LANE = Path("context_compass/artifacts/root_teardown_docs_20261018")
DOCS = Path("context_compass/system_docs")

ARCH_EDITS = [
    # E1 - Runtime Model: the rule, one sentence.
    ("replace",
     "a scope teardown ends its stores, and a purge disposes what it retires. It does not police userland objects: it does\n",
     "a scope teardown ends its stores, and a purge disposes what it retires. A root's teardown cleans only what the root\n"
     "holds (owner, 2026-10-18): what its stores record and the idle objects of its managed pools; an object a holder\n"
     "leased from a pool stays that holder's, with the `many` children recorded for it (two places where today's code\n"
     "differs are open with the owner: Operational Invariants). It does not police userland objects: it does\n"),
    # E2 - Sequence: Cleanup, step 7.
    ("replace",
     "   A root store cleans its managed pools first, newest first - their idle objects and the `many` children\n"
     "   recorded with every pooled object, out ones included - before its disposable registry, because a pool is\n"
     "   composed at conjure, before the uniques its objects hold; their failures join the same group (0.2.8243).\n",
     "   A root store unregisters its managed pools from `ReleaseManagedSpell`, then cleans them first, newest first -\n"
     "   their idle objects and the `many` children recorded with every pooled object, out ones included - before its\n"
     "   disposable registry, because a pool is composed at conjure, before the uniques its objects hold; their failures\n"
     "   join the same group (0.2.8243). The root's ward (its lesser lineage) and SpellSpaces end before its store, so a\n"
     "   consumer held there gives a leased object back while the pools still take it; one the root's own store holds\n"
     "   meets an unregistered pool. The owner's rule that a root's teardown cleans only what it holds, and the two\n"
     "   places open with the owner, are under Operational Invariants (2026-10-18).\n"),
    # E3 - Operational Invariants: a new top entry.
    ("insert_after",
     "\n## Operational Invariants\n",
     "- A root's teardown cleans only what the root holds (2026-10-18; the owner's rule in chat, \"if the root cleans up it\n"
     "  only cleans up whats held by the root\"; documentation only - the code is unchanged): what its stores record and\n"
     "  the idle objects of its managed pools, with the `many` children recorded for those objects. An object a holder\n"
     "  leased from a pool is the holder's: Melder keeps no reference to it, never disposes it at teardown, and a release\n"
     "  of it after the teardown no longer reaches that root's pool (Failure Modes and Error Paths). Today's order:\n"
     "  `Conduit._cleanup_normal_conduit` tears down the cluster facade, the Meld, the ward (the lesser lineage) and the\n"
     "  SpellSpaces before the root's own store, so a consumer held by a lesser conduit or a spellspace gives its leased\n"
     "  object back while the root's pools still take it; then `Creations.cleanup` detaches its maps under the store\n"
     "  lock, unregisters every pool from `ReleaseManagedSpell`, cleans the pools newest first and disposes its registry\n"
     "  newest first, raising one group; `ManagedSpellQuantity.cleanup` disposes each idle object, newest first, with its\n"
     "  recorded children, then the children recorded for objects still out, then the orphaned records. Two places are\n"
     "  open with the owner: (1) a consumer the root's own store holds whose disposal method gives its leased object\n"
     "  back meets a pool already unregistered - the release raises the not-managed ValueError inside that method, the\n"
     "  store collects it, the teardown raises ExceptionGroup \"Conduit torn down with disposal failures.\" and the\n"
     "  object is left undisposed (the owner asked why a cleanup that disposes should raise at all); (2) the pool\n"
     "  disposes the children recorded for an object still out, which the root does not hold, under the holder that\n"
     "  keeps the object. Measured on 0.2.8258 (3.14t, the GIL off and on): a root-held `many` handler whose `finish`\n"
     "  releases its pooled connection makes the teardown raise and leaves the connection open, the same handler in a\n"
     "  lesser conduit gives it back cleanly, and an out session's `many` cursor closes at teardown while the session\n"
     "  stays open. Until the owner decides, the cleanup sequence and the failure modes describe today's behaviour.\n"
     "  EVIDENCE: `src/melder/aether/conduit/conduit.py:Conduit._cleanup_normal_conduit`, `Conduit._permanent_cleanup`,\n"
     "  `src/melder/aether/conduit/creations/creations.py:Creations.cleanup`, `Creations._unregister_managed_quantities`,\n"
     "  `Creations._cleanup_managed_quantities`, `Creations._dispose_disposable_registry`,\n"
     "  `src/melder/aether/conduit/creations/managed_spell_quantity.py:ManagedSpellQuantity.cleanup`,\n"
     "  `ManagedSpellQuantity.put_back` and\n"
     "  `src/melder/aether/conduit/creations/release_managed_spell.py:ReleaseManagedSpell.release`,\n"
     "  `ReleaseManagedSpell._resolve_pool`.\n"),
    # E4 - Failure Modes: the root-held consumer's raise.
    ("insert_before",
     "- Bind refuses a managed binding before any registry change (0.2.8242): a `managed_spell_*` option on another\n",
     "- Known, not fixed (open with the owner, 2026-10-18): a root's teardown raises ExceptionGroup \"Conduit torn down with\n"
     "  disposal failures.\" when a consumer its own store holds gives a leased object back in its disposal method. The\n"
     "  store has already unregistered and cleaned its pools, so the release raises ValueError \"<Type> is not a managed\n"
     "  spell class in any live root: ...\" inside that method (when no other live root pools the class), collected as\n"
     "  RuntimeError \"Failed to dispose object ... using method '<name>': ...\" chained from it; the teardown still\n"
     "  finishes and the object is left undisposed. A consumer held by a lesser conduit or a spellspace gives the object\n"
     "  back cleanly, because those scopes end before the root's store. The owner questioned this raise with the rule\n"
     "  that a root's teardown cleans only what it holds (Operational Invariants); until the owner decides, give such\n"
     "  objects back before the root ends, or hold their consumers in a lesser conduit.\n"
     "  EVIDENCE: `src/melder/aether/conduit/creations/creations.py:Creations.cleanup`,\n"
     "  `src/melder/aether/conduit/conduit.py:Conduit._cleanup_normal_conduit` and\n"
     "  `src/melder/aether/conduit/creations/release_managed_spell.py:ReleaseManagedSpell._resolve_pool`.\n"),
    # E5 - Managed Lease and Release diagram: the code's teardown order.
    ("replace",
     "root teardown -> Creations.cleanup: pools first (idle objects + recorded children) -> unregistered\n",
     "root teardown -> ward, SpellSpaces -> Creations.cleanup: unregister the pools -> clean them (idle objects, every\n"
     "                 recorded child, out objects' included) -> the store's registry\n"),
    ("replace",
     "  T[Root teardown] --> C[Pools cleaned before the store's registry]\n",
     "  T[Root teardown] --> C[Pools unregistered, then cleaned before the store's registry]\n"),
    # E6 - Context / Handoff Summary entry.
    ("insert_after",
     "\n## Context / Handoff Summary\n\n",
     "2026-10-18 a root's teardown cleans only what the root holds (documentation only; the owner's rule, in chat): a\n"
     "sentence in the Runtime Model, the cleanup sequence (the unregister-first order, the ward and SpellSpaces ending\n"
     "before the store), a new operational invariant (the rule, today's order, two places open with the owner, measured\n"
     "on 0.2.8258), a Known-not-fixed failure mode (a consumer the root's own store holds that gives its object back in\n"
     "its disposal method makes the teardown raise) and the managed lease diagram's teardown order (it read \"pools\n"
     "first ... -> unregistered\"; the code unregisters first) carry it; the component map carries the per-component\n"
     "text. Open with the owner: whether the root-held consumer's release should be accepted at teardown instead of\n"
     "raising, and whether a pool should leave the children recorded for an object still out to that object's holder.\n"
     "Checked against `Conduit._cleanup_normal_conduit`, `Creations.cleanup`, `ManagedSpellQuantity.cleanup` and\n"
     "`ReleaseManagedSpell._resolve_pool`.\n"
     "\n"),
]

COMP_EDITS = [
    # C1 - Creations and SpellSpace: a pointer to the rule.
    ("insert_after",
     "pools' failures joining the store's ExceptionGroup: a pool is composed at conjure, before the uniques its objects hold.\n",
     "A root's teardown cleans only what the root holds (owner, 2026-10-18); the two places where this cleanup is open\n"
     "with the owner are under Component: Managed Spell Pools (Lifecycle/Cleanup).\n"),
    # C2 - Managed Spell Pools, Lifecycle/Cleanup: the rule and the two gaps.
    ("insert_after",
     "  leases it took for a holder that is never built.\n",
     "- A root's teardown cleans only what the root holds (the owner's rule, 2026-10-18): its stores' records and its\n"
     "  pools' idle objects with the children recorded for them; an object out is its holder's, with the children\n"
     "  recorded for it. Today the root's ward and SpellSpaces end first (`Conduit._cleanup_normal_conduit`), then\n"
     "  `Creations.cleanup` unregisters the pools, cleans them newest first and disposes its registry. Two places are\n"
     "  open with the owner (the code is unchanged): `ManagedSpellQuantity.cleanup` disposes the children recorded for\n"
     "  objects still out - an out session's `many` cursor closes at teardown while the session stays open (measured on\n"
     "  0.2.8258) - and a consumer the root's own store holds whose disposal method gives its object back meets the\n"
     "  unregistered pool (Failure Modes).\n"),
    # C3 - Managed Spell Pools, Failure Modes: the root-held consumer's raise.
    ("insert_after",
     "  them (corrected 2026-10-18: this named a release among the RuntimeError's sources).\n",
     "- Known, not fixed (open with the owner, 2026-10-18): a consumer the root's own store holds whose disposal method\n"
     "  gives its leased object back makes the root's teardown raise ExceptionGroup \"Conduit torn down with disposal\n"
     "  failures.\": the release meets the unregistered pool and raises the not-managed ValueError inside that method,\n"
     "  collected as RuntimeError \"Failed to dispose object ... using method '<name>': ...\" chained from it, and the\n"
     "  object is left undisposed. The same consumer in a lesser conduit or a spellspace gives it back cleanly (measured\n"
     "  on 0.2.8258, the GIL off and on).\n"),
    # C4 - Flow: Managed Lease -> Release, step 5.
    ("insert_after",
     "   child), then its disposable registry.\n",
     "   The root's ward and SpellSpaces end before its store, so their consumers give objects back first; a consumer\n"
     "   the root's own store holds meets the unregistered pool (open with the owner, 2026-10-18; Component: Managed\n"
     "   Spell Pools).\n"),
    # C5 - Context / Handoff Summary entry.
    ("insert_after",
     "\n## Context / Handoff Summary\n\n",
     "2026-10-18 a root's teardown cleans only what the root holds (documentation only; the owner's rule, in chat):\n"
     "Creations and SpellSpace points at it; Managed Spell Pools carries the rule, today's teardown order and the two\n"
     "places open with the owner in Lifecycle/Cleanup, and the root-held consumer's ExceptionGroup as a Known-not-fixed\n"
     "failure mode; the managed lease flow's teardown step names the ward and SpellSpaces ending first. Open with the\n"
     "owner: the root-held consumer's release at teardown, and the children recorded for an object still out.\n"
     "\n"),
]


def index_proof(doc: Path) -> tuple:
    """Return the (line_count, content_sha256) the document's index records."""
    index = doc.with_name(doc.stem + "_index.md").read_text(encoding="utf-8")
    line_count = int(re.search(r"\| line_count \| (\d+) \|", index).group(1))
    digest = re.search(r"\| content_sha256 \| `([0-9a-f]{64})` \|", index).group(1)
    return line_count, digest


def multiset(text: str) -> Counter:
    """Return the multiset of non-blank, whitespace-normalised lines."""
    return Counter(re.sub(r"\s+", " ", line).strip() for line in text.split("\n") if line.strip())


def apply(doc: Path, edits: list) -> tuple:
    """Check, apply and return (before_text, after_text) for one document; raises before any write."""
    raw = doc.read_bytes()
    text = raw.decode("utf-8")
    if "\r\n" in text:
        raise SystemExit(f"{doc}: CRLF found; this script writes LF documents only.")
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    want_lines, want_digest = index_proof(doc)
    digest = hashlib.sha256(raw).hexdigest()
    if (len(lines), digest) != (want_lines, want_digest):
        raise SystemExit(f"{doc}: {len(lines)} lines, sha256 {digest[:12]} - its index records {want_lines} lines, "
                         f"{want_digest[:12]}; another writer may be mid-pass. Nothing written.")
    after = text
    for kind, anchor, new in edits:
        count = after.count(anchor)
        if count != 1:
            raise SystemExit(f"{doc}: anchor must occur once, found {count}: {anchor[:90]!r}. Nothing written.")
        for line in new.split("\n"):
            if len(line) > 120:
                raise SystemExit(f"{doc}: new line over 120 characters ({len(line)}): {line[:60]!r}")
        if kind == "replace":
            after = after.replace(anchor, new)
        elif kind == "insert_after":
            after = after.replace(anchor, anchor + new)
        elif kind == "insert_before":
            after = after.replace(anchor, new + anchor)
        else:
            raise SystemExit(f"unknown edit kind {kind}")
    return text, after


def main() -> None:
    """Apply both documents' edits, or refuse with nothing written."""
    plans = []
    for name, edits in (("src_architecture.md", ARCH_EDITS), ("src_components.md", COMP_EDITS)):
        doc = DOCS / name
        before, after = apply(doc, edits)
        plans.append((doc, before, after))
    (LANE / "before").mkdir(exist_ok=True)
    (LANE / "runs").mkdir(exist_ok=True)
    for doc, before, after in plans:
        stem = doc.stem
        (LANE / "before" / doc.name).write_text(before, encoding="utf-8", newline="")
        old, new = multiset(before), multiset(after)
        removed = sorted((line, old[line] - new[line]) for line in old if new[line] < old[line])
        added = sorted((line, new[line] - old[line]) for line in new if new[line] > old[line])
        report = [f"{doc}: lines {before.count(chr(10))} -> {after.count(chr(10))}",
                  f"removed (count fell): {len(removed)}"]
        report += [f"  -{n} {line}" for line, n in removed]
        report += [f"added (count rose): {len(added)}"]
        report += [f"  +{n} {line}" for line, n in added]
        (LANE / "runs" / f"preservation_{stem}.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
        doc.write_text(after, encoding="utf-8", newline="")
        sys.stdout.write(f"applied: {doc} ({len(removed)} lines replaced, {len(added)} lines added)\n")


if __name__ == "__main__":
    main()
