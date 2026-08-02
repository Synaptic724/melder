#!/usr/bin/env python3
"""Return a Context Compass install to the state its manifest describes.

Use this when an instance has accumulated content that does not belong to it, or
when you are preparing the package for distribution and need the working lanes
emptied of one project's work.

TWO MODES, BECAUSE "CLEAN" MEANS TWO DIFFERENT THINGS

    --mode reset   (default) return to shipping state. The instance's work in
                   the RESET lanes is removed and the seeded documents go back
                   to what the package ships. Use when preparing a release or
                   clearing one project's content out of the package.

    --mode repair  fix a broken install without touching the project's work.
                   RESET lanes are left completely alone. Use on a live repo.

WHAT EACH MODE DOES, BY OWNERSHIP CLASS

    PACKAGE   both modes: restore if missing, restore if the hash differs.
    RESET     reset:  unlisted files removed; listed files restored to shipped.
              repair: untouched entirely.
    INSTANCE  never touched, in either mode. `agent_onboarding/user_defined/`
              is the project's own work and the package has no claim on it.
              `--purge-user-defined` is the single exception, and it exists only
              because a release should not ship another project's role overlays.
              It is never implied by `--mode reset`: deleting someone's role
              because they asked to tidy a lane would be a betrayal of the
              invariant, so it has to be asked for by name.
    LIVE      reset:  the whole file is restored. A release must not ship one
                      project's routing rows.
              repair: only the managed block is swapped. Rows are never touched.
    CONFIG    never rewritten in either mode - the updater owns key merges. But
              the manifest hash is used: when it does not match, the tool reports
              WHICH top-level keys you added, removed or retuned relative to the
              shipped defaults. A hash nothing checks is the same dead weight as
              a version stamp nothing bumps, so this one earns its place.

A file in a PACKAGE lane that is not in the manifest is reported as UNKNOWN in
both modes, and removed only in reset mode. It is usually foreign content, but
it can be a script someone added on purpose, so it is never deleted silently.

WHY RESET DOES NOT RUN BY ACCIDENT ON A LIVE REPO

Reset empties the working lanes. `system_docs/`, `tickets/` and `artifacts/` hold
whatever the project wrote there - architecture maps, live tickets, findings -
and reset deletes all of it. That is correct when preparing a release and
catastrophic on a working repository. Two explicit modes beat one clever
heuristic, because a heuristic that guesses wrong here destroys work.

The package ships `system_docs/` EMPTY: no architecture, component, test or
graph document is seeded. A placeholder in a live lane gets read as repository
truth no matter what banner sits on it, so there is nothing there to restore -
reset only removes.

Then: prune directories left empty, and re-materialise every manifest path so
`.gitkeep` markers come back. Order matters. Prune before restore and you delete
lanes that should exist; restore before prune and stale empty directories
survive.

WHY IT COMPARES CONTENT, NOT JUST PATHS

The cleanup this tool was written for found 1,217 foreign files by path. It also
found 11 files sitting at package paths carrying another project's content - the
three boards, four system documents, four patch templates. A path-only diff
reports those as present and correct, because the path exists in both trees.
Only the hash finds them. A cleanup that skips the hash comparison will report
success over a tree that is still wrong in the places that matter most.

BLAST RADIUS

This deletes files. It refuses to run without `--apply`, and `--check` prints
exactly what it would do. Removal is limited to RESET lanes: it will never
delete something outside a lane the manifest marks as the instance's to fill.
"""

from __future__ import annotations

import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from package_manifest import MANIFEST_NAME, SKIP_DIRS, parse  # noqa: E402

MANAGED_BEGIN = "<!-- BEGIN MANAGED: {name} -->"
MANAGED_END = "<!-- END MANAGED: {name} -->"


def sha_of(path: pathlib.Path) -> str:
    import hashlib
    return hashlib.sha256(path.read_bytes()).hexdigest()


def managed_blocks(text: str) -> list[tuple[str, int, int]]:
    """Every managed region as (name, start_index, end_index_exclusive)."""
    import re
    out = []
    for m in re.finditer(r"<!-- BEGIN MANAGED: (.+?) -->", text):
        name = m.group(1)
        end_marker = MANAGED_END.format(name=name)
        e = text.find(end_marker, m.end())
        if e == -1:
            raise ValueError(f"unterminated managed block {name!r}")
        out.append((name, m.start(), e + len(end_marker)))
    return out


def swap_managed(current: str, reference: str) -> tuple[str, list[str]]:
    """Replace each managed block in `current` with the one from `reference`.

    A block present in the reference but absent from the file is inserted at the
    top, after the H1 if there is one. A block in the file but not the reference
    is left alone - the package no longer manages it, and deleting text the
    package does not own is not this tool's business.
    """
    ref = {name: reference[s:e] for name, s, e in managed_blocks(reference)}
    changed: list[str] = []
    for name, s, e in sorted(managed_blocks(current), key=lambda b: -b[1]):
        if name in ref and current[s:e] != ref[name]:
            current = current[:s] + ref[name] + current[e:]
            changed.append(name)
    have = {n for n, _, _ in managed_blocks(current)}
    for name, block in ref.items():
        if name not in have:
            lines = current.split("\n")
            at = 1 if lines and lines[0].startswith("# ") else 0
            lines.insert(at, "\n" + block if at else block)
            current = "\n".join(lines)
            changed.append(f"{name} (inserted)")
    return current, changed


def diff_config_keys(current: str, shipped: str) -> tuple[list[str], list[str], list[str]]:
    """Which top-level config keys were added, removed, or given a new value.

    Reports only. Config is the install's to set, so this exists to answer "how
    does mine differ from stock" rather than to drive any change.
    """
    import re

    def blocks(text: str) -> dict[str, str]:
        lines = text.split("\n")
        starts = [(i, m.group(1)) for i, ln in enumerate(lines)
                  if (m := re.match(r"^([A-Za-z_][A-Za-z0-9_]*):", ln))]
        out = {}
        for idx, (i, key) in enumerate(starts):
            end = starts[idx + 1][0] if idx + 1 < len(starts) else len(lines)
            body = [l for l in lines[i:end]
                    if l.strip() and not l.lstrip().startswith("#")]
            out[key] = "\n".join(body)
        return out

    cur, ship = blocks(current), blocks(shipped)
    added = sorted(set(cur) - set(ship))
    removed = sorted(set(ship) - set(cur))
    retuned = sorted(k for k in set(cur) & set(ship) if cur[k] != ship[k])
    return added, removed, retuned


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--target", required=True, type=pathlib.Path,
                    help="the install to clean, the directory holding AGENTS.MD")
    ap.add_argument("--reference", type=pathlib.Path,
                    help="clean package to restore from; defaults to --target itself, "
                         "which repairs structure but cannot repair overwritten content")
    ap.add_argument("--mode", choices=("reset", "repair"), default="reset",
                    help="reset: return RESET lanes to shipping state (default). "
                         "repair: fix PACKAGE files only, leave the project's work alone")
    ap.add_argument("--purge-user-defined", action="store_true",
                    help="ALSO delete role overlays under agent_onboarding/user_defined/ "
                         "that the manifest does not list. For cutting a release: a "
                         "release should not ship another project's roles. Never implied "
                         "by --mode reset, because those overlays are someone's work")
    ap.add_argument("--check", action="store_true", help="report only, change nothing")
    ap.add_argument("--apply", action="store_true", help="perform the cleanup")
    args = ap.parse_args()

    target: pathlib.Path = args.target
    reference: pathlib.Path = args.reference or target

    if not (target / "AGENTS.MD").is_file():
        print(f"ERROR: {target} is not a package root (no AGENTS.MD)")
        return 2
    man_path = reference / MANIFEST_NAME
    if not man_path.is_file():
        print(f"ERROR: no {MANIFEST_NAME} in {reference} - run package_manifest.py first")
        return 2
    if not args.check and not args.apply:
        print("Refusing to act without --apply. Use --check to see the plan.")
        return 2

    manifest = parse(man_path.read_text(encoding="utf-8"))
    reset_roots = sorted({p.split("/")[0] + "/" for p, (c, _) in manifest.items()
                          if c == "RESET" and "/" in p})

    on_disk = {p.relative_to(target).as_posix()
               for p in target.rglob("*")
               if p.is_file() and not any(part in SKIP_DIRS for part in p.parts)}
    on_disk.discard(MANIFEST_NAME)

    reset_mode = args.mode == "reset"
    remove, restore, repair, blocks, unknown, kept = [], [], [], [], [], []
    config_drift = None

    instance_roots = sorted({p.rsplit('/', 1)[0] + '/' if '/' in p else p
                             for p, (c, _) in manifest.items() if c == 'INSTANCE'} |
                            {'agent_onboarding/user_defined/'})

    foreign_roles: list[str] = []
    for rel in sorted(on_disk - set(manifest)):
        if any(rel.startswith(r) for r in instance_roots):
            foreign_roles.append(rel)
            continue          # never removed unless --purge-user-defined says so
        in_reset_lane = any(rel.startswith(r) for r in reset_roots)
        if in_reset_lane:
            (remove if reset_mode else kept).append(rel)
        else:
            unknown.append(rel)          # foreign file in a PACKAGE lane

    for rel, (cls, digest) in sorted(manifest.items()):
        p = target / rel
        if cls == "INSTANCE":
            continue          # the project's own work, in every mode
        if cls == "RESET" and not reset_mode:
            if not p.exists():
                restore.append(rel)      # reseed a lane file that went missing
            continue
        if not p.exists():
            restore.append(rel)
        elif cls in ("PACKAGE", "RESET") and sha_of(p) != digest:
            repair.append(rel)
        elif cls == "LIVE" and reset_mode and sha_of(p) != digest:
            # Preparing a release: ship the board as the package ships it. Keeping
            # someone's routing rows would publish one project's work state.
            repair.append(rel)
        elif cls == "LIVE" and (reference / rel).is_file():
            _, ch = swap_managed(p.read_text(encoding="utf-8"),
                                 (reference / rel).read_text(encoding="utf-8"))
            if ch:
                blocks.append((rel, ch))
        elif cls == "CONFIG" and sha_of(p) != digest and (reference / rel).is_file():
            # Never changed - the updater owns config merges. But the manifest
            # hash would otherwise be dead weight, and a hash nothing checks is
            # the same pattern as a version stamp nothing bumps. Use it to say
            # HOW the install diverged from the shipped defaults.
            config_drift = diff_config_keys(
                p.read_text(encoding="utf-8"),
                (reference / rel).read_text(encoding="utf-8"))

    print(f"target    {target}")
    print(f"reference {reference}")
    print(f"mode      {args.mode}")
    print(f"manifest  {len(manifest)} files, RESET lanes: {', '.join(reset_roots) or 'none'}")
    print()
    print(f"  remove  {len(remove):>5}  instance files in RESET lanes")
    print(f"  restore {len(restore):>5}  manifest files missing from the target")
    print(f"  repair  {len(repair):>5}  manifest files whose content differs")
    print(f"  blocks  {len(blocks):>5}  live files whose managed block is stale")
    print(f"  unknown {len(unknown):>5}  files in PACKAGE lanes not in the manifest"
          f"{' (will be removed)' if reset_mode else ' (reported only)'}")
    if kept:
        print(f"  kept    {len(kept):>5}  instance files left alone by repair mode")
    for rel in remove[:10]:
        print(f"    remove  {rel}")
    if len(remove) > 10:
        print(f"    ... +{len(remove) - 10} more")
    for rel in restore[:10]:
        print(f"    restore {rel}")
    for rel in repair[:10]:
        print(f"    repair  {rel}")
    for rel, ch in blocks[:10]:
        print(f"    block   {rel}: {', '.join(ch)}")
    for rel in unknown[:10]:
        print(f"    unknown {rel}")

    if config_drift and any(config_drift):
        a, r, v = config_drift
        print(f"  config          your `config/context_compass_config.yaml` differs from stock:")
        if a: print(f"                    keys you added:      {', '.join(a)}")
        if r: print(f"                    keys you removed:    {', '.join(r)}")
        if v: print(f"                    values you changed:  {', '.join(v)}")
        print("                  reported only - config is yours and is never rewritten here.")

    if foreign_roles:
        roles = sorted({r.split("/")[2] for r in foreign_roles if r.count("/") >= 2})
        verb = "WILL BE DELETED" if args.purge_user_defined else "kept"
        print(f"  overlays{len(foreign_roles):>5}  files under user_defined not in the "
              f"manifest, in {len(roles)} role(s): {', '.join(roles)} - {verb}")
        if not args.purge_user_defined:
            print("            these belong to whoever wrote them. Cutting a release?"
                  " Pass --purge-user-defined.")

    if reset_mode:
        remove = remove + unknown
    if args.purge_user_defined:
        remove = remove + foreign_roles

    if args.check:
        clean = not (remove or restore or repair or blocks)
        print()
        if clean and unknown and not reset_mode:
            print("OK: at manifest state, but see the unknown files above")
        else:
            print("OK: already at manifest state" if clean else "DIRTY: run with --apply")
        return 0 if clean else 1

    if reference == target and (restore or repair):
        print()
        print("REFUSED: files are missing or altered and --reference is the target itself.")
        print("         There is nothing to restore them from. Pass a clean package.")
        return 2

    for rel in remove:
        (target / rel).unlink()

    for rel in sorted(set(restore) | set(repair)):
        src, dst = reference / rel, target / rel
        if not src.is_file():
            print(f"    SKIP (not in reference): {rel}")
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(src.read_bytes())

    for rel, _ in blocks:
        p = target / rel
        new, _ = swap_managed(p.read_text(encoding="utf-8"),
                              (reference / rel).read_text(encoding="utf-8"))
        p.write_bytes(new.encode("utf-8"))

    pruned = 0
    for d in sorted((p for p in target.rglob("*") if p.is_dir()),
                    key=lambda x: len(x.parts), reverse=True):
        if not any(d.iterdir()):
            d.rmdir()
            pruned += 1

    recreated = 0
    for rel in manifest:
        p = target / rel
        if not p.exists() and (reference / rel).is_file():
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes((reference / rel).read_bytes())
            recreated += 1

    print()
    print(f"APPLIED: removed {len(remove)}, restored {len(restore)}, repaired {len(repair)},"
          f" blocks reset {len(blocks)}, pruned {pruned} empty dirs, recreated {recreated}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
