"""Graph descriptors for D-10 (melder_0, 2026-10-25; TASK-2026-10-10-deny-file-access-under-safe-codegen).

The extractor walks the whole tree, so it ran into a mirror (/tmp/m0s2/graph_mirror/graph, a copy of the repository's
descriptors taken at 2026-10-25T08:19Z, after the option-B source edits) and only this lane's seven descriptors come
back: stdlib_import_sets.json, the five codegen preset descriptors and codegen_system.json. For each, every authored
field of every node (and the file's authored edges and retired nodes) must equal the repository's copy - the mirror
differs only in the mechanical tier - and then the prose is brought to the source, read in full at 2026-10-25T08:3xZ:
the import-set module states `open` on the shared deny tuple and `io`/`os`/`pathlib` as permissive extras (its first
responsibility named a "safe" import-root set that does not exist - safe has imports off); each preset class states its
file posture; the permissive class's role and second responsibility said it denies mutation and unsafe reflection while
its build() allows both, so they are corrected; CodegenSystem states the no-projection safe posture and gains the
authored `uses` edge to the import-set module it now reads; safe_profile's `uses` edge said import-root constants where
it reads the denied-builtin tuple. Written as the extractor writes (indent=1, LF), refusing a repository descriptor
that changed since it was read. Usage: d10_graph_descriptors.py --check | --apply
"""
import json
import pathlib
import sys
from typing import Callable, Dict, List

REPO = pathlib.Path.home() / "mnt/melder_private/context_compass/system_docs/graph/melder"
MIRROR = pathlib.Path("/tmp/m0s2/graph_mirror/graph/melder")
AUTHORED_NODE = ("role", "responsibilities", "owns_state", "phases", "semantics_authored_against", "include")
AUTHORED_FILE = ("edges_authored", "nodes_retired")
PKG = "melder.nexus.acl.configurations.profiles.codegen"
SETS = PKG + ".stdlib_import_sets"
SYSTEM = "melder.nexus.rift.codegen_system.codegen_system.CodegenSystem"

SETS_OLD_FIRST = "defines reusable safe, hybrid, precision, and permissive import-root sets"
SETS_NEW_FIRST = (
    "defines the import-root allow lists the presets read - the common list hybrid uses, precision's narrower one "
    "and permissive's (the common list plus the permissive extras, sorted) - and the deny list hybrid and precision "
    "share")
SETS_OPEN = (
    "puts `open` on SAFE_DENIED_BUILTIN_NAMES, the one denied-builtin tuple safe, hybrid and precision share and the "
    "codegen engine's no-projection default reads (0.2.8270)")
SETS_EXTRAS = (
    "keeps `io`, `os` and `pathlib` among the permissive extras, so permissive's is the only allow list that admits "
    "them (0.2.8270)")
SAFE_FILES = (
    "hold a closed file posture (0.2.8270): `open` denied by its SAFE_DENIED_BUILTIN_NAMES rule and imports off, so "
    "`io`, `os` and `pathlib` are refused too - policy checked in the room's process, not isolation")
SAFE_EDGE_OLD = "The safe codegen profile factory uses the shared stdlib import-root constants."
SAFE_EDGE_NEW = "The safe codegen profile factory uses the shared denied-builtin tuple, SAFE_DENIED_BUILTIN_NAMES."
HYBRID_FILES = (
    "deny `open` (the safe tuple) and keep `io`, `os` and `pathlib` off its import allow list, since they are "
    "permissive extras (0.2.8270)")
PRECISION_FILES = "deny `open` (the safe tuple); its import allow list names none of `io`, `os` or `pathlib` (0.2.8270)"
PERMISSIVE_OLD_ROLE = (
    "Top standard rung of the codegen posture ladder: broadest conduit and spell operations still under capability "
    "gates.")
PERMISSIVE_NEW_ROLE = (
    "Top standard rung of the codegen posture ladder: the broadest conduit, spell and capability operations, with "
    "imports kept to an allowlist.")
PERMISSIVE_OLD_SECOND = "still deny the highest-risk capability gates - mutation and unsafe reflection"
PERMISSIVE_NEW_SECOND = (
    "allow every capability gate - dynamic access, contract override, mutation, unsafe reflection, dunder access and "
    "recursive codegen - keeping only its import allowlist as the guardrail versus full_access")
PERMISSIVE_FILES = (
    "keep an open file posture by design: `open` available and `io`, `os` and `pathlib` on its import allowlist "
    "(0.2.8270)")
FULL_ACCESS_FILES = "keep an open file posture by design: `open` available and imports unrestricted (0.2.8270)"
SYSTEM_DEFAULT = (
    "runs a request naming a frame the owning Rift holds no codegen projection for under the safe posture - imports "
    "off, no unsafe reflection, dunder access or recursive codegen, and `__import__` plus SAFE_DENIED_BUILTIN_NAMES "
    "denied, the tuple read from the preset module rather than copied (0.2.8270)")
SYSTEM_EDGE = {
    "from": SYSTEM,
    "to": SETS,
    "relation": "uses",
    "why": ("CodegenSystem's no-projection default posture denies `__import__` plus SAFE_DENIED_BUILTIN_NAMES, read "
            "from the preset module so the default and the safe preset cannot drift apart."),
    "cardinality": "many_to_one",
    "phase": ["runtime"],
    "strength": "borrowed",
}


def append_once(items: List[str], text: str) -> None:
    if text in items:
        raise SystemExit("already applied: " + text[:60])
    items.append(text)


def replace_once(items: List[str], old: str, new: str) -> None:
    if items.count(old) != 1:
        raise SystemExit("expected exactly one: " + old[:60])
    items[items.index(old)] = new


def sets_edit(d: dict) -> None:
    node = d["nodes"][SETS]
    replace_once(node["responsibilities"], SETS_OLD_FIRST, SETS_NEW_FIRST)
    append_once(node["responsibilities"], SETS_OPEN)
    append_once(node["responsibilities"], SETS_EXTRAS)


def safe_edit(d: dict) -> None:
    append_once(d["nodes"][PKG + ".safe_profile.SafeCodegenProfileStrategy"]["responsibilities"], SAFE_FILES)
    hits = [e for e in d["edges_authored"] if e["to"] == SETS and e["why"] == SAFE_EDGE_OLD]
    if len(hits) != 1:
        raise SystemExit("safe_profile uses-edge not found once")
    hits[0]["why"] = SAFE_EDGE_NEW


def hybrid_edit(d: dict) -> None:
    append_once(d["nodes"][PKG + ".hybrid_profile.HybridCodegenProfileStrategy"]["responsibilities"], HYBRID_FILES)


def precision_edit(d: dict) -> None:
    append_once(d["nodes"][PKG + ".precision.PrecisionCodegenProfileStrategy"]["responsibilities"], PRECISION_FILES)


def permissive_edit(d: dict) -> None:
    node = d["nodes"][PKG + ".permissive_profile.PermissiveCodegenProfileStrategy"]
    if node["role"] != PERMISSIVE_OLD_ROLE:
        raise SystemExit("permissive role is not the recorded one")
    node["role"] = PERMISSIVE_NEW_ROLE
    replace_once(node["responsibilities"], PERMISSIVE_OLD_SECOND, PERMISSIVE_NEW_SECOND)
    append_once(node["responsibilities"], PERMISSIVE_FILES)


def full_access_edit(d: dict) -> None:
    append_once(d["nodes"][PKG + ".full_access_profile.FullAccessCodegenProfileStrategy"]["responsibilities"],
                FULL_ACCESS_FILES)


def system_edit(d: dict) -> None:
    append_once(d["nodes"][SYSTEM]["responsibilities"], SYSTEM_DEFAULT)
    if any(e["from"] == SYSTEM and e["to"] == SETS for e in d["edges_authored"]):
        raise SystemExit("CodegenSystem -> stdlib_import_sets edge already present")
    d["edges_authored"].append(dict(SYSTEM_EDGE))


def one(rel: str, change: Callable[[dict], None], apply: bool) -> None:
    repo_path, mirror_path = REPO / rel, MIRROR / rel
    repo_raw = repo_path.read_bytes()
    mirror_raw = mirror_path.read_bytes()
    for raw in (repo_raw, mirror_raw):
        if b"\r" in raw:
            raise SystemExit("CR in " + rel)
    repo, mirror = json.loads(repo_raw.decode("utf-8")), json.loads(mirror_raw.decode("utf-8"))
    for raw, parsed in ((repo_raw, repo), (mirror_raw, mirror)):
        if (json.dumps(parsed, indent=1) + "\n").encode("utf-8") != raw:
            raise SystemExit("not in the extractor's format: " + rel)
    if set(repo["nodes"]) != set(mirror["nodes"]):
        raise SystemExit("node sets differ in " + rel)
    for node_id, node in repo["nodes"].items():
        for field in AUTHORED_NODE:
            if node.get(field) != mirror["nodes"][node_id].get(field):
                raise SystemExit(f"authored field {field} of {node_id} differs between the repository and the mirror")
    for field in AUTHORED_FILE:
        if repo.get(field) != mirror.get(field):
            raise SystemExit(f"authored file field {field} differs in {rel}")
    change(mirror)
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
    base = "nexus/acl/configurations/profiles/codegen/"
    one(base + "stdlib_import_sets.json", sets_edit, apply)
    one(base + "safe_profile.json", safe_edit, apply)
    one(base + "hybrid_profile.json", hybrid_edit, apply)
    one(base + "precision.json", precision_edit, apply)
    one(base + "permissive_profile.json", permissive_edit, apply)
    one(base + "full_access_profile.json", full_access_edit, apply)
    one("nexus/rift/codegen_system/codegen_system.json", system_edit, apply)
    print("applied" if apply else "checked")


if __name__ == "__main__":
    main()
