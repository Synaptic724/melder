"""
Land the S9 lane's documentation on the tree: notch, release note, architecture, components (indexes are rebuilt
by the caller), patch docs archived. Run AFTER apply_s9.py --root <tree>.

Usage: python land_docs_s9.py --tree <repo root> --version <new version> [--skip-notch-and-note]
"""
import argparse
import pathlib
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / ".." / "executor_cache_world_stamp_20261003"))
from cc_helpers import now_utc, read_text, write_text, replace_once, check_line_lengths  # noqa: E402

PATCH_ID = "flat_warm_body_2026_10_03"
LOWERING = "src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py"


def _loc(path: pathlib.Path) -> int:
    return len(path.read_bytes().decode("utf-8").splitlines())


def notch(tree: pathlib.Path, old: str, new: str) -> None:
    path = tree / "src/melder/__version__.py"
    text, nl = read_text(str(path))
    text = replace_once(text, f'__version__ = "{old}"\n', f'__version__ = "{new}"\n', "version")
    write_text(str(path), text, nl)


def release_note(tree: pathlib.Path, old: str, new: str) -> None:
    path = tree / "release_docs/next_version_release.md"
    text, nl = read_text(str(path))
    text = replace_once(text, f"# Melder {old}\n", f"# Melder {new}\n", "header")
    section = """## Shared singleton sites read their store as a constant

When a compiled site plan reads a dependency of existence `unique` - a singleton its Spellbook owns - it used to
look that spell's owner store up on every creation (`c = spells[i]._owner_creations`) before reading the instance
out of it. In an automatic world that store cannot move after conjure, so the plan now binds it once, when the
plan is emitted at the first meld, and the warm read is the store lookup alone. A dynamic world keeps the
per-creation read, because an ownership transfer repoints a spell's owner store there. Same objects, same
errors, same locks; no API change; nothing changes on disk, since plans are emitted from the cached rows at
hydration and the creation-cache generation stays 19.

Directional numbers on the maintainers' VM (Python 3.14t, free-threaded), interleaved before/after medians of
three runs on the real compiled plans: a transient over one singleton 160 -> 148 ns per creation, a root over
five singletons 316 -> 277 ns, a wide root over eight singletons 447 -> 374 ns, a wide root over eight existing
objects 444 -> 368 ns (-7..-17%), and an eight-deep transient chain with one singleton 432 -> 428 ns. Roots with
no `unique` dependency are byte-identical.

"""
    anchor = "## Packaging and documentation\n"
    text = replace_once(text, anchor, "\n" + section + anchor, "packaging section")
    text = replace_once(
        text,
        f"- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for {old}.\n",
        "- The packaged system documents describe the owner-store constant of a `unique` site in an automatic world:\n"
        "  the eligible-site rule, the bound namespace name, the posture that keeps the read and the harness numbers;\n"
        "  the site-plan lowering's code-map extents are remeasured.\n"
        f"- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for {new}.\n",
        "rebuild line")
    bad = check_line_lengths(section)
    if bad:
        raise SystemExit(f"release note lines over cap: {bad}")
    # The annotation section used to run straight into the packaging heading; the blank line above fixes that.
    write_text(str(path), text, nl)


def architecture(tree: pathlib.Path, new: str, lowering_loc: int, ts: str) -> None:
    path = tree / "context_compass/system_docs/src_architecture.md"
    text, nl = read_text(str(path))
    invariant = f"""- Owner-store constants on the warm path (2026-10-03, {new}): a site plan's shared site of existence `unique` whose
  provider Spell is owned by an automatic conduit and already has an owner store reads that store as a plan
  constant (`c{{i}}`, bound in the namespace at emission) instead of `spells[i]._owner_creations` on every creation;
  the hit read `c{{i}}._creations.get(sid{{i}})`, the miss call and the miss body are unchanged, so a store swapped
  empty by cleanup is seen as before. An owned spell's owner store changes only through
  `Spell._add_owned_conduit` - at conjure and, in dynamic posture, at ownership transfer - and a notch or a late
  bind re-gates and recompiles the plan, so in an automatic world nothing repoints the store under a plan; a
  provider in a dynamic environment, one not yet owned, and every `meld.<store>` route keep the per-creation
  read. Plans are emitted at hydration from manifest rows (cold path and cache full hit alike), so no cache
  generation moves. Measured on the VM: -7..-17% of the plan on roots with `unique` providers (8-10 ns per site).
  EVIDENCE: `{LOWERING}:SitePlanEmission._owner_store_constant`
  and `SitePlanEmission._emit_shared_hit`.
"""
    text = replace_once(
        text,
        "## Operational Invariants\n- Per-conduit verdicts retire with their definition",
        "## Operational Invariants\n" + invariant + "- Per-conduit verdicts retire with their definition",
        "invariant anchor")
    text = replace_once(
        text,
        f"- path: `{LOWERING}`\n"
        "  start_line: 1\n"
        "  end_line: 1546\n"
        "  loc: 1546\n"
        "  verified_at: 2026-10-03T19:33:16Z\n"
        "  note: key-set plan lowering: site graph from steps, placement, emission, call shape.\n",
        f"- path: `{LOWERING}`\n"
        "  start_line: 1\n"
        f"  end_line: {lowering_loc}\n"
        f"  loc: {lowering_loc}\n"
        f"  verified_at: {ts}\n"
        "  note: key-set plan lowering: site graph from steps, placement, emission, call shape; an automatic\n"
        f"    world's `unique` sites read their owner store as a plan constant ({new}).\n",
        "lowering code map")
    handoff = f"""2026-10-03 owner-store constants ({new}): a `unique` site whose provider is owned by an automatic conduit reads its
owner store as a plan constant bound at emission instead of `spells[i]._owner_creations` per creation; dynamic
providers, unowned ones and the `meld.<store>` routes keep the read, and no cache generation moves because plans
are emitted from rows at hydration. The operational invariants and the code map carry it; the component map
carries the eligible-site rule and the emitted shape.

"""
    text = replace_once(
        text,
        "## Context / Handoff Summary\n\n2026-10-03 executor-cache world stamp (0.2.8220):",
        "## Context / Handoff Summary\n\n" + handoff + "2026-10-03 executor-cache world stamp (0.2.8220):",
        "handoff anchor")
    for block in (invariant, handoff):
        bad = check_line_lengths(block, exempt=r"^  (EVIDENCE: )?`src/")
        if bad:
            raise SystemExit(f"architecture lines over cap: {bad}")
    write_text(str(path), text, nl)


def components(tree: pathlib.Path, new: str, lowering_loc: int, ts: str) -> None:
    path = tree / "context_compass/system_docs/src_components.md"
    text, nl = read_text(str(path))
    bullet = f"""- Owner-store constants (2026-10-03, {new}): `SitePlanEmission._owner_store_constant(step)` is True for a
  shared site of existence `unique` - the one route that reads `spells[i]._owner_creations` - when the provider
  Spell is owned by an automatic conduit (`Spell._dynamic_environment` False) and already has an owner store;
  `_emit_shared_hit` then binds `c{{i}}` to `step.spell._owner_creations` in the plan namespace and emits no
  `c{{i}} = <route>` line, so the warm read is `v{{i}} = c{{i}}._creations.get(sid{{i}})` on a global. Every other
  shared site - the `meld.<store>` routes, a provider in a dynamic environment (ownership transfer repoints its
  store), a provider not yet owned - emits the line as before; the miss keeps its `c{{i}}` parameter and the warm
  call passes the global, so misses are byte-identical. `_dynamic_environment` and `_owner_creations` are Spell
  slots written by `_add_owned_conduit` (False and None before ownership), which `define_conduit_into_spells`
  calls at conjure before any plan is hydrated. The constant is the Creations OBJECT; its `_creations` dict is
  still read per creation. Plans are emitted at hydration from rows on the cold path and on a cache full hit, so
  no cache generation moves. Measured on the VM (interleaved medians): worker 160 -> 148 ns, context_root
  316 -> 277, wide8_unique 447 -> 374, wide8_existing 444 -> 368, chain8_transient 432 -> 428.
  EVIDENCE: `{LOWERING}:SitePlanEmission._owner_store_constant`,
  `SitePlanEmission._emit_shared_hit` and `src/melder/aether/spellbook/spell.py:Spell._add_owned_conduit`.
"""
    text = replace_once(
        text,
        "  `SitePlanEmission._place`.\n- Door-held root (2026-09-26, 0.2.73):",
        "  `SitePlanEmission._place`.\n" + bullet + "- Door-held root (2026-09-26, 0.2.73):",
        "lazy bullet end")
    text = replace_once(
        text,
        f"- path: `{LOWERING}`\n"
        "  start_line: 1\n"
        "  end_line: 1501\n"
        "  loc: 1501\n"
        "  verified_at: 2026-09-26T22:18:53Z\n",
        f"- path: `{LOWERING}`\n"
        "  start_line: 1\n"
        f"  end_line: {lowering_loc}\n"
        f"  loc: {lowering_loc}\n"
        f"  verified_at: {ts}\n",
        "lowering code map")
    handoff = f"""2026-10-03 owner-store constants ({new}): the SpellCompiler entry's emission bullets carry the eligible-site rule
(`_owner_store_constant`), the bound namespace name, the postures that keep the per-creation read and the harness
numbers; the lowering's code-map extent is remeasured (it was stale since 2026-09-26).

"""
    text = replace_once(
        text,
        "## Context / Handoff Summary\n\n2026-10-03 rebind after first meld (0.2.8219):",
        "## Context / Handoff Summary\n\n" + handoff + "2026-10-03 rebind after first meld (0.2.8219):",
        "handoff anchor")
    for block in (bullet, handoff):
        bad = check_line_lengths(block, exempt=r"^  (EVIDENCE: )?`src/")
        if bad:
            raise SystemExit(f"components lines over cap: {bad}")
    write_text(str(path), text, nl)


def archive_patch_docs(tree: pathlib.Path) -> None:
    active = tree / "context_compass/system_docs/patches/active" / PATCH_ID
    completed = tree / "context_compass/system_docs/patches/completed" / PATCH_ID
    if completed.exists():
        raise SystemExit("completed patch folder exists")
    shutil.move(str(active), str(completed))
    p = completed / "architecture_patch.md"
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
    lowering = tree / LOWERING
    assert "_owner_store_constant" in lowering.read_bytes().decode("utf-8"), "apply_s9.py has not run on the tree"
    ts = now_utc()
    if not args.skip_notch_and_note:
        notch(tree, old, args.version)
        release_note(tree, old, args.version)
    architecture(tree, args.version, _loc(lowering), ts)
    components(tree, args.version, _loc(lowering), ts)
    archive_patch_docs(tree)
    print("landed docs", old, "->", args.version, "lowering loc", _loc(lowering), ts)


if __name__ == "__main__":
    main()
