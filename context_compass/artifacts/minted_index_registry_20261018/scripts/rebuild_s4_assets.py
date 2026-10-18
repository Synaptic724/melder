"""Regenerate melder's build assets for S4 in a /tmp mirror and copy what changed back (melder_1; S9's procedure).

The asset runner cannot run in the repository: its system-documents writer unlinks its payloads before writing them
(`_system_documents/_builder.py`, the payload writer) and the connected folder refuses deletes. So it runs whole in a
mirror holding a copy of `src/` and `context_compass/system_docs/` - everything the three builders read (the bind
guard and agent documentation builders scan the package; the system-documents builder reads the system documents
under the repository root, which is the mirror's root here). Every file the run changed under
`src/melder/_build_assets/` is listed; with --apply each is written over its original and read back byte-equal.
Then the mirror's `src/` and system documents are compared with the repository's: after the copy nothing may
differ but files the runner does not read (reported, not refused). Caches (`__pycache__`, `__melder_cache__`) are
neither copied nor compared. The checks (`--check` of the runner and of the LLM bundles) run in the repository.
Paths are written to the log as <repo> and <mirror>.
Usage: rebuild_s4_assets.py --repo <root> --mirror </tmp/cc_res/...> --python <interpreter> --log <file> [--apply]
"""
import os
import pathlib
import shutil
import subprocess
import sys

CACHES = ("__pycache__", "__melder_cache__")
ASSETS = "src/melder/_build_assets"
READ_BY_RUNNER = ("src_architecture.md", "src_components.md", "src_graph.md")


def files_under(root: pathlib.Path) -> dict:
    """Map each file's path relative to `root` to its bytes, skipping cache directories."""
    found = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(name for name in dirnames if name not in CACHES)
        for name in sorted(filenames):
            path = pathlib.Path(dirpath) / name
            found[path.relative_to(root).as_posix()] = path.read_bytes()
    return found


def build_mirror(repo: pathlib.Path, mirror: pathlib.Path) -> None:
    """Copy `src/` and the system documents into a fresh mirror under /tmp/cc_res/."""
    if not str(mirror).startswith("/tmp/cc_res/"):
        raise SystemExit("the mirror must live under /tmp/cc_res/: %s" % mirror)
    if mirror.exists():
        shutil.rmtree(mirror)
    ignore = shutil.ignore_patterns(*CACHES)
    shutil.copytree(repo / "src", mirror / "src", ignore=ignore)
    shutil.copytree(repo / "context_compass/system_docs", mirror / "context_compass/system_docs", ignore=ignore)


def run_runner(mirror: pathlib.Path, python: str) -> str:
    """Run the asset runner from the mirror's root and return its output; refuse a non-zero exit."""
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONPATH"] = str(mirror / "src")
    done = subprocess.run([python, "src/melder/_build_assets/_build_asset_runner.py"], cwd=mirror, env=env,
                          capture_output=True, text=True, timeout=170)
    output = done.stdout + done.stderr
    if done.returncode != 0:
        raise SystemExit("asset runner exited %d:\n%s" % (done.returncode, output))
    return output


def changed_assets(repo: pathlib.Path, mirror: pathlib.Path) -> list:
    """List the asset files the run changed or added; refuse a file it removed (deletes are refused here)."""
    before = files_under(repo / ASSETS)
    after = files_under(mirror / ASSETS)
    removed = sorted(set(before) - set(after))
    if removed:
        raise SystemExit("the run removed files the repository cannot delete: %s" % ", ".join(removed))
    return sorted(rel for rel, data in after.items() if before.get(rel) != data)


def compare_trees(repo: pathlib.Path, mirror: pathlib.Path) -> list:
    """Return the differences left between the mirror and the repository; refuse one in what the runner reads."""
    notes = []
    for sub in ("src", "context_compass/system_docs"):
        ours = files_under(repo / sub)
        theirs = files_under(mirror / sub)
        for rel in sorted(set(ours) | set(theirs)):
            if ours.get(rel) == theirs.get(rel):
                continue
            where = "%s/%s" % (sub, rel)
            if sub == "src" or rel in READ_BY_RUNNER:
                raise SystemExit("mirror and repository differ in %s: the copy is stale; rebuild again" % where)
            notes.append("differs (not read by the runner): %s" % where)
    return notes


def main() -> None:
    """Build the mirror, run the runner, list the changes; copy them back and compare with --apply."""
    args = sys.argv[1:]
    apply = args[-1:] == ["--apply"]
    if apply:
        args = args[:-1]
    if len(args) != 8 or [args[0], args[2], args[4], args[6]] != ["--repo", "--mirror", "--python", "--log"]:
        raise SystemExit(__doc__)
    repo = pathlib.Path(args[1]).resolve()
    mirror = pathlib.Path(args[3])
    log_lines = []
    build_mirror(repo, mirror)
    output = run_runner(mirror, args[5])
    log_lines.extend(line for line in output.rstrip("\n").split("\n"))
    log_lines.append("")
    changes = changed_assets(repo, mirror)
    for rel in changes:
        source = mirror / ASSETS / rel
        target = repo / ASSETS / rel
        if apply:
            data = source.read_bytes()
            target.write_bytes(data)
            if target.read_bytes() != data:
                raise SystemExit("read-back mismatch: %s" % target)
            log_lines.append("copied %s/%s (byte-equal)" % (ASSETS, rel))
        else:
            log_lines.append("would copy %s/%s" % (ASSETS, rel))
    if apply:
        log_lines.extend(compare_trees(repo, mirror))
        log_lines.append("mirror src/ and the runner's system documents equal the repository's")
    text = "\n".join(log_lines).replace(str(mirror), "<mirror>").replace(str(repo), "<repo>") + "\n"
    pathlib.Path(args[7]).write_text(text, encoding="utf-8")
    sys.stdout.write(text)


main()
