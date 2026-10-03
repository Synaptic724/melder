"""
Land the lane's documentation on the tree: notch, release note, architecture, components (+ indexes are
rebuilt by the caller), patch docs archived. Run AFTER apply_world_stamp.py --root <tree>.

Usage: python land_docs.py --tree <repo root> --version <new version>
"""
import argparse
import datetime as _dt
import os
import pathlib
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from cc_helpers import now_utc, read_text, write_text, replace_once, check_line_lengths  # noqa: E402

PATCH_ID = "executor_cache_world_stamp_2026_10_03"


def _loc(path: pathlib.Path) -> int:
    return len(path.read_bytes().decode("utf-8").splitlines())


def _line_of(path: pathlib.Path, needle: str) -> int:
    for number, line in enumerate(path.read_bytes().decode("utf-8").splitlines(), 1):
        if line.startswith(needle):
            return number
    raise SystemExit(f"{needle!r} not found in {path}")


def notch(tree: pathlib.Path, old: str, new: str) -> None:
    path = tree / "src/melder/__version__.py"
    text, nl = read_text(str(path))
    text = replace_once(text, f'__version__ = "{old}"\n', f'__version__ = "{new}"\n', "version")
    write_text(str(path), text, nl)


def release_note(tree: pathlib.Path, old: str, new: str) -> None:
    path = tree / "release_docs/next_version_release.md"
    text, nl = read_text(str(path))
    text = replace_once(text, f"# Melder {old}\n", f"# Melder {new}\n", "header")
    section = f"""## Fixed: a warm creation cache no longer replays an executor compiled in another world

With system caching on, a conduit's creation-cache bundle was admitted as a full hit whenever every cached spell
was still bound, without checking the rest of the world. An existing object or a non-resolvable definition
carries no cached executor, so a world that only added one - say a provider for a parameter nobody had provided,
bound bare as an existing object - or removed one was still a full hit: the consumer's executor compiled without
the provider was replayed and its first meld raised `TypeError: ... missing 1 required positional argument`, or
a plan naming a spell the world no longer has raised `RuntimeError: generalized manifest references unknown
spell_id`, while a cold cache resolved the same world correctly.

The bundle now records the world its executors were compiled in - the same stamp the structural tier already
uses (the bound spell ids, the frame posture and the borrowed spells) - and a full hit requires it. A changed
world recompiles phases 8-11 once and re-stages the bundle; a repeat world is still a full hit that leaves the
file untouched. A world that only removed a spell is a changed world too and recompiles once (before, surplus
cached ids were ignored). Creation-cache generation 19 retires bundles written without the stamp; they rebuild
on the next conjure.

```python
service = Service()
book.bind(spell=service, existence="unique", permissions="create")   # added since the cached run
book.bind(spell=Worker, existence="many", permissions="create")       # Worker(service: Service)
conduit = book.conjure(name="root")
conduit.meld(spell=Worker).service is service                         # True; TypeError before {new}
```

What stays the same: caching off, the structural tier and its replay, what is staged per spell, every meld path.

"""
    anchor = "## Transient creations with disposal methods register faster\n"
    text = replace_once(text, anchor, section + anchor, "transient section")
    text = replace_once(
        text,
        f"- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for {old}.\n",
        "- The packaged system documents describe the executor-cache world stamp: the envelope field, the full-hit\n"
        "  rule, the staging write and the retired surplus full hit; the conjure sequence's line citations into\n"
        "  `spellbook_creation_system.py` are remeasured.\n"
        f"- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for {new}.\n",
        "rebuild line")
    bad = check_line_lengths(section)
    if bad:
        raise SystemExit(f"release note lines over cap: {bad}")
    write_text(str(path), text, nl)


def architecture(tree: pathlib.Path, new: str, stamp_end: int, creation_loc: int, caching_loc: int, ts: str) -> None:
    path = tree / "context_compass/system_docs/src_architecture.md"
    text, nl = read_text(str(path))
    text = replace_once(
        text,
        "   - Classify the creation cache BEFORE the conduit phases: the live set of\n"
        "     resolvable, non-existing-creation spell ids is compared with the cached\n"
        "     ids, giving `disabled`, `full_hit`, `mixed` or `full_miss`.\n",
        "   - Classify the creation cache BEFORE the conduit phases: the live set of\n"
        "     resolvable, non-existing-creation spell ids is compared with the cached\n"
        "     ids, and the bundle's recorded world stamp with the live one (0.2.8220),\n"
        "     giving `disabled`, `full_hit` (every live id cached AND the stamps equal),\n"
        "     `mixed` or `full_miss`.\n",
        "conjure classify bullet")
    text = replace_once(
        text,
        "     - src/melder/aether/spellbook/spellbook_creation_system.py:616-721\n",
        f"     - src/melder/aether/spellbook/spellbook_creation_system.py:616-{stamp_end}\n",
        "conjure evidence")
    invariant = f"""- Executor-cache world stamp (2026-10-03, {new}): the conduit creation-cache bundle records the world its executor
  payloads were staged in - the structural tier's world stamp (sorted pool ids, posture, sorted borrowed ids) - and
  the executor tier admits a full hit only when the live world carries it. A world that differs only by an existing
  creation or a non-resolvable definition (ids the executor tier never counts, because they carry no payload)
  recompiles phases 8-11 and re-stages the bundle, as a missing live spell does; a repeat world is still a
  byte-identical full hit; a world that only removed a spell recompiles once (the former surplus-id full hit is
  retired). Generation 19 retires bundles without the field; "" (an empty store, a bundle written without the
  field) never matches, so the rule fails closed.
  EVIDENCE: `src/melder/aether/spellbook/spellbook_creation_system.py:SpellbookCreationSystem._build_conjure_cache_state`,
  `SpellbookCreationSystem._stage_spell_payloads_at_conjure_end` and
  `src/melder/utilities/caching_system/caching_system.py:CachingSystem.set_world_stamp`.
"""
    text = replace_once(
        text,
        "- Annotation matching by address key (2026-10-03, 0.2.8218): Phase 3 matches",
        invariant + "- Annotation matching by address key (2026-10-03, 0.2.8218): Phase 3 matches",
        "invariant anchor")
    failure = f"""- A warm creation cache no longer replays an executor compiled in another world (fixed in {new}): a world that
  differs only by an existing creation or a non-resolvable definition used to be a full hit, so a consumer's
  executor compiled without a provider raised TypeError ("missing 1 required positional argument") at its first
  meld after the provider was bound, and a plan naming a removed provider raised RuntimeError ("generalized
  manifest references unknown spell_id"); both worlds now recompile and resolve as a cold cache does.
  EVIDENCE: `src/melder/aether/spellbook/spellbook_creation_system.py:SpellbookCreationSystem._build_conjure_cache_state`.
"""
    text = replace_once(
        text,
        "## Failure Modes and Error Paths\n- A definition melded, removed with `cleanup_spell`",
        "## Failure Modes and Error Paths\n" + failure + "- A definition melded, removed with `cleanup_spell`",
        "failure anchor")
    text = replace_once(
        text,
        "- path: `src/melder/aether/spellbook/spellbook_creation_system.py`\n"
        "  start_line: 1\n"
        "  end_line: 3453\n"
        "  loc: 3453\n"
        "  verified_at: 2026-09-30T19:57:20Z\n"
        "  note: conjure and target-local resolution orchestration; a successful target pass flags the owned\n"
        "    dependencies it compiled without a plan of their own (0.2.8215).\n",
        "- path: `src/melder/aether/spellbook/spellbook_creation_system.py`\n"
        "  start_line: 1\n"
        f"  end_line: {creation_loc}\n"
        f"  loc: {creation_loc}\n"
        f"  verified_at: {ts}\n"
        "  note: conjure and target-local resolution orchestration; a successful target pass flags the owned\n"
        "    dependencies it compiled without a plan of their own (0.2.8215); the executor-cache full hit requires\n"
        f"    the recorded world stamp ({new}).\n",
        "creation code map")
    text = replace_once(
        text,
        "- path: `src/melder/utilities/caching_system/caching_system.py`\n"
        "  start_line: 1\n"
        "  end_line: 818\n"
        "  loc: 818\n"
        "  verified_at: 2026-10-03T19:33:16Z\n"
        "  note: release-bound creation-cache admission and atomic envelope persistence.\n",
        "- path: `src/melder/utilities/caching_system/caching_system.py`\n"
        "  start_line: 1\n"
        f"  end_line: {caching_loc}\n"
        f"  loc: {caching_loc}\n"
        f"  verified_at: {ts}\n"
        "  note: release-bound creation-cache admission, the envelope's world stamp and atomic persistence.\n",
        "caching code map")
    handoff = f"""2026-10-03 executor-cache world stamp ({new}): the creation-cache bundle records the world its executors were
staged in and a full hit requires it, so a world that only added or removed an existing creation (or a
non-resolvable definition) recompiles instead of replaying a stale executor; the conjure sequence, the operational
invariants, the failure modes and the code map carry it, the component map carries the envelope field, the rule
and the staging write. The former "surplus cached id still full-hits" contract is retired (one recompile).

"""
    text = replace_once(
        text,
        "## Context / Handoff Summary\n\n2026-10-03 rebind after first meld (0.2.8219):",
        "## Context / Handoff Summary\n\n" + handoff + "2026-10-03 rebind after first meld (0.2.8219):",
        "handoff anchor")
    text = replace_once(text, "- Updated: 2026-10-03\n", "- Updated: 2026-10-03\n", "metadata date")  # unchanged day
    for block in (invariant, failure, handoff):
        bad = check_line_lengths(block, exempt=r"^  (EVIDENCE: )?`src/")
        if bad:
            raise SystemExit(f"architecture lines over cap: {bad}")
    write_text(str(path), text, nl)


def components(tree: pathlib.Path, new: str, stamp_end: int) -> None:
    path = tree / "context_compass/system_docs/src_components.md"
    text, nl = read_text(str(path))
    bullet = f"""- Generation 19 (2026-10-03, `executor_world_stamp`, {new}): the envelope records the structural tier's world
  stamp once, `world_stamp`, written by `_stage_spell_payloads_at_conjure_end` through
  `CachingSystem.set_world_stamp` after every live spell is re-staged (the conjure-end emit is flagged when it
  changed), and `_build_conjure_cache_state` admits an executor full hit only when the recorded stamp equals the
  live `StructuralSnapshot.world_stamp` (`world_matches`; every payload matched under another stamp is the mixed
  path, nothing matched the full miss, an empty live set the full miss as before). The executor rule counted
  payload ids only, and an existing creation or a non-resolvable definition carries no payload, so a world that
  differed only by one - a provider added as a bare existing object, or removed - was a full hit: the consumer's
  executor compiled when nothing provided the parameter was replayed (TypeError at its first meld), or a plan
  naming a spell outside the world ran ("generalized manifest references unknown spell_id"), while a cold cache
  resolved it. Now both tiers miss on the same worlds and the world is recompiled once; a repeat world is still a
  byte-identical full hit; a world that only removed a spell is a changed world (one recompile; the former
  surplus-id full hit is retired). "" (an empty store, a bundle written without the field) never matches, so the
  rule fails closed; the field is optional on load and a non-str value is a cold cache.
  EVIDENCE: `src/melder/utilities/caching_system/caching_system.py:CachingSystem.set_world_stamp` and
  `src/melder/aether/spellbook/spellbook_creation_system.py:SpellbookCreationSystem._build_conjure_cache_state`.
"""
    text = replace_once(
        text,
        "  `src/melder/utilities/caching_system/caching_system.py:CachingSystem.upsert_structural_payload`.\n"
        "EVIDENCE: `src/melder/utilities/caching_system/caching_system.py:CachingSystem`,\n",
        "  `src/melder/utilities/caching_system/caching_system.py:CachingSystem.upsert_structural_payload`.\n"
        + bullet +
        "EVIDENCE: `src/melder/utilities/caching_system/caching_system.py:CachingSystem`,\n",
        "hydrate bullet end")
    text = replace_once(
        text,
        "   - Classifies the creation cache (`_build_conjure_cache_state`): live\n"
        "     resolvable, non-existing-creation spell ids vs cached ids ->\n"
        "     `disabled` | `full_hit` | `mixed` | `full_miss`.\n",
        "   - Classifies the creation cache (`_build_conjure_cache_state`): live\n"
        "     resolvable, non-existing-creation spell ids vs cached ids, and the\n"
        f"     bundle's recorded world stamp vs the live one ({new}) ->\n"
        "     `disabled` | `full_hit` | `mixed` | `full_miss`.\n",
        "flow classify")
    text = replace_once(
        text,
        "     `src/melder/aether/spellbook/spellbook_creation_system.py:616-721`.\n",
        f"     `src/melder/aether/spellbook/spellbook_creation_system.py:616-{stamp_end}`.\n",
        "flow evidence")
    bad = check_line_lengths(bullet, exempt=r"^  (EVIDENCE: )?`src/")
    if bad:
        raise SystemExit(f"components lines over cap: {bad}")
    write_text(str(path), text, nl)


def archive_patch_docs(tree: pathlib.Path) -> None:
    active = tree / "context_compass/system_docs/patches/active" / PATCH_ID
    completed = tree / "context_compass/system_docs/patches/completed" / PATCH_ID
    if completed.exists():
        raise SystemExit("completed patch folder exists")
    shutil.move(str(active), str(completed))
    for name in ("architecture_patch.md",):
        p = completed / name
        t, nl = read_text(str(p))
        t = replace_once(t, "- Status: active (entry gate for", "- Status: promoted and archived (was the entry gate for", "status")
        write_text(str(p), t, nl)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tree", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--skip-notch-and-note", action="store_true")
    args = parser.parse_args()
    tree = pathlib.Path(args.tree).resolve()
    version_path = tree / "src/melder/__version__.py"
    old = None
    for line in version_path.read_bytes().decode("utf-8").splitlines():
        if line.startswith("__version__ = "):
            old = line.split('"')[1]
    if args.skip_notch_and_note:
        assert old == args.version, (old, args.version)
    else:
        assert old is not None and old != args.version, (old, args.version)
    ts = now_utc()
    creation = tree / "src/melder/aether/spellbook/spellbook_creation_system.py"
    caching = tree / "src/melder/utilities/caching_system/caching_system.py"
    stamp_end = _line_of(creation, "    def _load_cached_spell_payloads_for_conjure(") - 3
    assert _line_of(creation, "    def _build_conjure_cache_state(") == 616
    if not args.skip_notch_and_note:
        notch(tree, old, args.version)
        release_note(tree, old, args.version)
    architecture(tree, args.version, stamp_end, _loc(creation), _loc(caching), ts)
    components(tree, args.version, stamp_end)
    archive_patch_docs(tree)
    print("landed docs", old, "->", args.version, "stamp_end", stamp_end, "loc", _loc(creation), _loc(caching), ts)


if __name__ == "__main__":
    main()
