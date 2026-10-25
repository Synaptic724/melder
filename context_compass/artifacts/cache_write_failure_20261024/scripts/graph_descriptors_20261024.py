"""Graph descriptors for the cache-save fix (melder_0, 2026-10-24; F5).

The extractor walks the whole tree, and melder_1's in-flight files would be refreshed with it, so it runs into a
mirror (/tmp/m0_mq/f5/graph_mirror/graph, a copy of the repository's descriptors) and only this lane's three
descriptors come back: caching_system.json, spellbook.json and spell.json. For each, every authored field of every
node (and the file's authored edges and retired nodes) must equal the repository's copy - the mirror differs only in
the mechanical tier - and then the class nodes gain one responsibility each, read against the source: CachingSystem's
best-effort save (and its new owned slot `_refused_save_logged`), Spellbook's save seam, Spell's explicit save.
Written as the extractor writes (indent=1, LF), refusing a repository descriptor that changed since it was read.
Usage: graph_descriptors_20261024.py --check | --apply
"""
import json
import pathlib
import sys
from typing import Callable, Dict, List

REPO = pathlib.Path.home() / "mnt/melder_private/context_compass/system_docs/graph/melder"
MIRROR = pathlib.Path("/tmp/m0_mq/f5/graph_mirror/graph/melder")
AUTHORED_NODE = ("role", "responsibilities", "owns_state", "phases", "semantics_authored_against", "include")
AUTHORED_FILE = ("edges_authored", "nodes_retired")

CACHE_SAVE = (
    "saves best-effort (emit -> bool, 0.2.8266): the folder, this writer's temp file "
    "(<conduit>.meldercache.<pid>.<thread id>.tmp) and the rename in one try under the instance lock; on Windows "
    "(RETRY_REFUSED_RENAME) a PermissionError of the rename is retried up to REPLACE_ATTEMPTS attempts, "
    "REPLACE_RETRY_DELAY_SECONDS times the attempt apart; any OSError refuses the save - its temp file removed (one "
    "that cannot be removed is logged), the bundle on disk and every staged payload kept, False returned and the "
    "refusal logged at WARNING the first time for the instance, DEBUG after (_refused_save_logged)")
BOOK_SAVE = (
    "saves its creation-cache bundle through one seam (_emit_cache_file_if_required): clears the emit flag under the "
    "Book lock before the save, returns the save's bool and leaves the flag cleared after a refusal, so no meld door, "
    "conjure end or explicit save fails on or retries a refused save; any other exception restores the flag and "
    "propagates (0.2.8266)")
SPELL_SAVE = (
    "saves its Book's cache on request (emit_cache_file -> bool): False when caching is off, nothing was staged since "
    "the last save or the operating system refused the save, which no longer raises (0.2.8266)")


def append_once(items: List[str], text: str) -> None:
    if text in items:
        raise SystemExit("already applied: " + text[:60])
    items.append(text)


def cache_edit(nodes: Dict[str, dict]) -> None:
    node = nodes["melder.utilities.caching_system.caching_system.CachingSystem"]
    append_once(node["responsibilities"], CACHE_SAVE)
    if "_refused_save_logged" in node["owns_state"]:
        raise SystemExit("owns_state already has _refused_save_logged")
    node["owns_state"].insert(node["owns_state"].index("_logger"), "_refused_save_logged")


def book_edit(nodes: Dict[str, dict]) -> None:
    append_once(nodes["melder.aether.spellbook.spellbook.Spellbook"]["responsibilities"], BOOK_SAVE)


def spell_edit(nodes: Dict[str, dict]) -> None:
    append_once(nodes["melder.aether.spellbook.spell.Spell"]["responsibilities"], SPELL_SAVE)


def one(rel: str, change: Callable[[Dict[str, dict]], None], apply: bool) -> None:
    repo_path, mirror_path = REPO / rel, MIRROR / rel
    repo_raw = repo_path.read_bytes()
    mirror_raw = mirror_path.read_bytes()
    for raw in (repo_raw, mirror_raw):
        if b"\r" in raw:
            raise SystemExit("CR in " + rel)
    repo, mirror = json.loads(repo_raw.decode("utf-8")), json.loads(mirror_raw.decode("utf-8"))
    if set(repo["nodes"]) != set(mirror["nodes"]):
        raise SystemExit("node sets differ in " + rel)
    for node_id, node in repo["nodes"].items():
        for field in AUTHORED_NODE:
            if node.get(field) != mirror["nodes"][node_id].get(field):
                raise SystemExit(f"authored field {field} of {node_id} differs between the repository and the mirror")
    for field in AUTHORED_FILE:
        if repo.get(field) != mirror.get(field):
            raise SystemExit(f"authored file field {field} differs in {rel}")
    change(mirror["nodes"])
    text = json.dumps(mirror, indent=1) + "\n"
    print(rel, "->", len(text.splitlines()), "lines")
    if not apply:
        return
    if repo_path.read_bytes() != repo_raw:
        raise SystemExit("RACE " + rel)
    repo_path.write_bytes(text.encode("utf-8"))
    if repo_path.read_bytes().decode("utf-8") != text:
        raise SystemExit("read-back mismatch " + rel)


def main() -> None:
    if sys.argv[1:] not in (["--check"], ["--apply"]):
        raise SystemExit(__doc__)
    apply = sys.argv[1] == "--apply"
    one("utilities/caching_system/caching_system.json", cache_edit, apply)
    one("aether/spellbook/spellbook.json", book_edit, apply)
    one("aether/spellbook/spell.json", spell_edit, apply)
    print("applied" if apply else "checked")


if __name__ == "__main__":
    main()
