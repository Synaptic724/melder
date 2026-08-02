#!/usr/bin/env python3
"""Upgrade an installed Context Compass to a newer version of the package.

Point it at a new package and an existing install. It decides, per file, whether
replacing is safe - and refuses rather than guessing when it is not.

THE THREE-HASH RULE

One hash tells you a file changed. It cannot tell you WHO changed it, and that is
the only question that matters when deciding whether to overwrite.

    shipped   what the installed version's manifest recorded
    current   what is on disk in the install right now
    new       what the incoming version ships

    current == shipped, new != shipped   -> clean update, replace
    current == shipped, new == shipped   -> already current, skip
    current != shipped, new == shipped   -> the user edited it, package did not:
                                            KEEP their version
    current != shipped, new != shipped   -> both moved: CONFLICT, report, do not
                                            touch. A merge here is a guess, and a
                                            wrong guess destroys work silently.

Without `shipped` you cannot separate rows three and four from row one, so you
either overwrite the user's edits or never update anything. There is no version
of this that works with a single hash.

WHAT IS NEVER TOUCHED

    RESET lanes   tickets, artifacts, system docs, project instructions.
                  The install owns these outright. An upgrade that rewrites
                  someone's architecture map is not an upgrade.
    INSTANCE      `agent_onboarding/user_defined/`. Role overlays belong to
                  whoever wrote them. Never replaced, never restored, never
                  removed - not even a role the package originally shipped as a
                  sample, because by the time it is in someone's repo it is
                  theirs to edit.

WHAT GETS SPECIAL HANDLING

    LIVE files    the boards. Only the text between MANAGED markers is swapped.
                  Routing rows are the install's, and survive.
    CONFIG        merged key by key: new keys are added with package defaults, a
                  value the user already set is never overwritten, and keys the
                  new version dropped are reported rather than deleted.
"""

from __future__ import annotations

import argparse
import hashlib
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from package_manifest import MANIFEST_NAME, parse  # noqa: E402
from cleanup_context_compass import swap_managed   # noqa: E402


def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def top_level_keys(yaml_text: str) -> dict[str, tuple[int, int]]:
    """Map each top-level YAML key to its (start_line, end_line_exclusive).

    Deliberately not a YAML parser. This tool only needs to know where a
    top-level block begins and ends so it can append a missing one verbatim,
    comments and all. Parsing and re-emitting would reformat the user's file and
    drop their comments, which is a worse outcome than not merging at all.
    """
    lines = yaml_text.split("\n")
    starts = [(i, m.group(1)) for i, ln in enumerate(lines)
              if (m := re.match(r"^([A-Za-z_][A-Za-z0-9_]*):", ln))]
    out: dict[str, tuple[int, int]] = {}
    for idx, (i, key) in enumerate(starts):
        end = starts[idx + 1][0] if idx + 1 < len(starts) else len(lines)
        while end > i + 1 and lines[end - 1].strip() == "":
            end -= 1
        out[key] = (i, end)
    return out


def merge_config(current: str, new: str) -> tuple[str, list[str], list[str]]:
    """Add top-level keys the install lacks. Never overwrite one it has."""
    cur_keys = top_level_keys(current)
    new_keys = top_level_keys(new)
    new_lines = new.split("\n")

    added, dropped = [], []
    additions: list[str] = []
    for key, (s, e) in new_keys.items():
        if key not in cur_keys:
            block = "\n".join(new_lines[s:e])
            # carry the comment block immediately above the key
            lead = s
            while lead > 0 and (new_lines[lead - 1].startswith("#")
                                or new_lines[lead - 1].strip() == ""):
                lead -= 1
                if new_lines[lead].strip() == "" and lead < s - 1:
                    break
            comment = "\n".join(new_lines[lead:s]).strip("\n")
            additions.append((comment + "\n" + block) if comment else block)
            added.append(key)
    for key in cur_keys:
        if key not in new_keys:
            dropped.append(key)

    if additions:
        current = current.rstrip("\n") + "\n\n" + "\n\n".join(additions) + "\n"
    return current, added, dropped


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--install", required=True, type=pathlib.Path,
                    help="the existing install to upgrade")
    ap.add_argument("--new", required=True, type=pathlib.Path,
                    help="the new package version")
    ap.add_argument("--check", action="store_true", help="report only, change nothing")
    ap.add_argument("--apply", action="store_true", help="perform the upgrade")
    ap.add_argument("--force-conflicts", action="store_true",
                    help="take the new version for conflicted files, discarding local edits")
    args = ap.parse_args()

    install, new = args.install, args.new
    for label, root in (("install", install), ("new", new)):
        if not (root / "AGENTS.MD").is_file():
            print(f"ERROR: --{label} {root} is not a package root")
            return 2
    if not (new / MANIFEST_NAME).is_file():
        print(f"ERROR: --new {new} has no {MANIFEST_NAME} - run package_manifest.py on it")
        return 2
    if not args.check and not args.apply:
        print("Refusing to act without --apply. Use --check to see the plan.")
        return 2

    incoming = parse((new / MANIFEST_NAME).read_text(encoding="utf-8"))

    # An install predating the manifest has no shipped hashes, so for every file
    # that differs we cannot tell a local edit from an upstream change. Guessing
    # would overwrite real work. Treat every difference as a conflict instead:
    # identical files still skip, missing files are still added, and the user
    # gets an explicit list of what to review rather than a silent overwrite.
    first_adoption = not (install / MANIFEST_NAME).is_file()
    shipped = {} if first_adoption else parse(
        (install / MANIFEST_NAME).read_text(encoding="utf-8"))
    if first_adoption:
        print(f"NOTE: {install} has no {MANIFEST_NAME}, so this is its first")
        print("      manifest-aware upgrade. Without shipped hashes a local edit and an")
        print("      upstream change are indistinguishable, so every differing file is")
        print("      reported as a conflict rather than replaced. Review them, then")
        print("      re-run with --force-conflicts to take the new version wholesale.")
        print()

    def version_of(root: pathlib.Path) -> str:
        man = root / MANIFEST_NAME
        if not man.is_file():
            return "unknown (no manifest)"
        for line in man.read_text(encoding="utf-8").splitlines():
            if line.startswith("| package_version |"):
                return line.split("|")[2].strip()
        return "?"

    replace, skip, keep, conflict, added, gone = [], [], [], [], [], []
    blocks, cfg = [], None

    for rel, (cls, new_sha) in sorted(incoming.items()):
        p = install / rel
        old_sha = shipped.get(rel, (None, None))[1]

        if cls in ("RESET", "INSTANCE"):
            continue                                   # the install owns these
        if cls == "CONFIG":
            if p.is_file():
                merged, a, d = merge_config(p.read_text(encoding="utf-8"),
                                            (new / rel).read_text(encoding="utf-8"))
                cfg = (rel, merged, a, d)
            else:
                added.append(rel)
            continue
        if not p.is_file():
            added.append(rel)
            continue

        cur_sha = sha_bytes(p.read_bytes())
        if cls == "LIVE":
            _, ch = swap_managed(p.read_text(encoding="utf-8"),
                                 (new / rel).read_text(encoding="utf-8"))
            if ch:
                blocks.append((rel, ch))
            continue
        if cur_sha == new_sha:
            skip.append(rel)
        elif old_sha is None:
            conflict.append(rel)                       # not in the old manifest
        elif cur_sha == old_sha:
            replace.append(rel)
        elif new_sha == old_sha:
            keep.append(rel)
        else:
            conflict.append(rel)

    for rel, (cls, _) in sorted(shipped.items()):
        if rel not in incoming and cls not in ("RESET", "INSTANCE") and (install / rel).exists():
            gone.append(rel)

    print(f"install {install}  (version {version_of(install)})")
    print(f"new     {new}  (version {version_of(new)})")
    print()
    print(f"  replace  {len(replace):>5}  package changed, install untouched")
    print(f"  skip     {len(skip):>5}  already current")
    print(f"  keep     {len(keep):>5}  locally edited, package unchanged")
    print(f"  conflict {len(conflict):>5}  BOTH changed - not touched")
    print(f"  added    {len(added):>5}  new files in this version")
    print(f"  removed  {len(gone):>5}  dropped upstream, still present locally")
    print(f"  blocks   {len(blocks):>5}  managed blocks to swap in live files")
    if cfg:
        print(f"  config   {len(cfg[2])} keys to add, {len(cfg[3])} dropped upstream")
    for rel in conflict[:15]:
        print(f"    CONFLICT {rel}")
    for rel in keep[:10]:
        print(f"    keep     {rel}")
    for rel in added[:10]:
        print(f"    added    {rel}")
    for rel in gone[:10]:
        print(f"    removed  {rel}")
    for rel, ch in blocks[:10]:
        print(f"    block    {rel}: {', '.join(ch)}")
    if cfg and cfg[2]:
        print(f"    config   add keys: {', '.join(cfg[2])}")
    if cfg and cfg[3]:
        print(f"    config   dropped upstream (kept): {', '.join(cfg[3])}")

    if args.check:
        print()
        print(f"{'CONFLICTS - resolve before applying' if conflict else 'READY'}")
        return 1 if conflict else 0

    for rel in replace + added + (conflict if args.force_conflicts else []):
        src, dst = new / rel, install / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(src.read_bytes())

    for rel, _ in blocks:
        p = install / rel
        merged, _ = swap_managed(p.read_text(encoding="utf-8"),
                                 (new / rel).read_text(encoding="utf-8"))
        p.write_bytes(merged.encode("utf-8"))

    if cfg:
        rel, merged, a, _ = cfg
        if a:
            (install / rel).write_bytes(merged.encode("utf-8"))

    (install / MANIFEST_NAME).write_bytes((new / MANIFEST_NAME).read_bytes())

    print()
    print(f"APPLIED: replaced {len(replace)}, added {len(added)}, "
          f"blocks {len(blocks)}, config keys {len(cfg[2]) if cfg else 0}, "
          f"kept {len(keep)} local edits, "
          f"{'forced' if args.force_conflicts else 'left'} {len(conflict)} conflicts")
    if conflict and not args.force_conflicts:
        print("         Conflicted files were NOT changed. Resolve them by hand.")
    if gone:
        print(f"         {len(gone)} files dropped upstream are still present; remove by hand if wanted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
