"""Graph descriptors for D-20 (melder_0, 2026-10-25; TASK-2026-10-10-refuse-materializing-over-live-modules).

Same procedure as d11_graph_descriptors.py: the extractor ran into a mirror of the repository's descriptors after the
D-20 source edits (/tmp/m0d20_graph), so the mirror's mechanical tier is current and its authored tier the
repository's; each of this lane's nine descriptors must match the repository on every authored field before its
prose is brought to the source, re-read at 2026-10-25T12:0xZ. CodegenCommandSystem gains the materialize name gate and
its `uses` edge to the import-set module (PROTECTED_GENERATION_MODULE_ROOTS); SyntheticModule its restoring exits;
CodegenSystem and CodegenNamespaceBuilder the builtins mapping; the compiler, compiled surface, validator and codegen
builder the `materialize_modules` rule and its two compiled fields; the import-set module the protected root. The
compiled-surface clones in nexus.py and static_frame_viewer.py are plumbing and keep their prose, as in D-11.
Usage: d20_graph_descriptors.py --check | --apply
"""
import json
import pathlib
import sys
from typing import Callable, List

REPO = pathlib.Path.home() / "mnt/melder_private/context_compass/system_docs/graph/melder"
MIRROR = pathlib.Path("/tmp/m0d20_graph/graph/melder")
AUTHORED_NODE = ("role", "responsibilities", "owns_state", "phases", "semantics_authored_against", "include")
AUTHORED_FILE = ("edges_authored", "nodes_retired")
SETS = "melder.nexus.acl.configurations.profiles.codegen.stdlib_import_sets"
VERB = "melder.nexus.rift.command_system.codegen_command_system.CodegenCommandSystem"
T = "(D-20, @D20_NOTCH@)"
EDITS = {
 "nexus/rift/command_system/codegen_command_system.json": (VERB,
  "refuses, in materialize_codegen after validation accepts and before anything is registered or published, a name "
  "already in sys.modules, under the protected core root `melder`, a standard-library root or an installed import "
  "name, and per the frame's compiled surface a name under a denied generation root or outside its declared ones; "
  "runs the module with the room's filtered builtins and cleans the module and the parent shells it created when "
  "materialize fails " + T),
 "crystallizer/synthetic_module.json": ("melder.crystallizer.synthetic_module.SyntheticModule",
  "records a non-synthetic module its publication displaces and a non-synthetic parent attribute its attachment "
  "displaces, and gives them back on unpublish, detach and cleanup while it still holds the slot; a displaced "
  "SyntheticModule is not restored " + T),
 "nexus/rift/codegen_system/codegen_system.json": ("melder.nexus.rift.codegen_system.codegen_system.CodegenSystem",
  "returns the room's filtered builtins mapping for an accepted materialize (build_materialize_builtins), the mapping "
  "execute_codegen gives room code, so a materialized module reaches what the room reaches " + T),
 "nexus/rift/codegen_system/namespace/codegen_namespace_builder.json": (
  "melder.nexus.rift.codegen_system.namespace.codegen_namespace_builder.CodegenNamespaceBuilder",
  "builds the builtins mapping alone (build_builtins) through its builtins strategy, for materialized code " + T),
 "nexus/acl/frame_acl_compiler.json": ("melder.nexus.acl.frame_acl_compiler.FrameACLCompiler",
  "compiles `materialize_modules` rules into `generation_module_roots` (None when no allow rule; else the allow roots "
  "intersected across allow-bearing rulesets minus the denied union) and `denied_generation_module_roots` " + T),
 "nexus/acl/frame_acl_compiled_access_surface.json": (
  "melder.nexus.acl.frame_acl_compiled_access_surface.CompiledFrameACLAccessSurface",
  "carries the frame's generation namespace for materialize_codegen - `generation_module_roots` (None when undeclared) "
  "and `denied_generation_module_roots` " + T),
 "nexus/acl/validator/frame_acl_validator.json": ("melder.nexus.acl.validator.frame_acl_validator.FrameACLValidator",
  "accepts the `materialize_modules` capability operation and requires its `module_roots` to be non-empty and "
  "dotted-identifier legal " + T),
 "nexus/acl/builder/frame_acl_codegen_builder.json": (
  "melder.nexus.acl.builder.frame_acl_codegen_builder.FrameACLCodegenBuilder",
  "merges generation-namespace roots into stable `materialize_modules` allow and deny rules "
  "(allow_materialize_module_roots, deny_materialize_module_roots) " + T),
 "nexus/acl/configurations/profiles/codegen/stdlib_import_sets.json": (SETS,
  "defines PROTECTED_GENERATION_MODULE_ROOTS (`melder`), the root materialize_codegen refuses under every posture " + T),
}
VERB_EDGE = {
    "from": VERB, "to": SETS, "relation": "uses",
    "why": "CodegenCommandSystem reads PROTECTED_GENERATION_MODULE_ROOTS for materialize_codegen's name gate.",
    "cardinality": "many_to_one", "phase": ["runtime"], "strength": "borrowed",
}


def append_once(items: List[str], text: str) -> None:
    if text in items:
        raise SystemExit("already applied: " + text[:60])
    items.append(text)


def add_edge_once(d: dict, edge: dict) -> None:
    if any(e.get("from") == edge["from"] and e.get("to") == edge["to"] and e.get("relation") == edge["relation"]
           for e in d["edges_authored"]):
        raise SystemExit("edge already present: " + edge["from"][:40] + " -> " + edge["to"][:40])
    d["edges_authored"].append(dict(edge))


def one(rel: str, change: Callable[[dict], None], apply: bool) -> None:
    repo_path, mirror_path = REPO / rel, MIRROR / rel
    repo_raw, mirror_raw = repo_path.read_bytes(), mirror_path.read_bytes()
    for raw in (repo_raw, mirror_raw):
        if b"\r" in raw:
            raise SystemExit("CR in " + rel)
    repo, mirror = json.loads(repo_raw.decode("utf-8")), json.loads(mirror_raw.decode("utf-8"))
    for raw, parsed in ((repo_raw, repo), (mirror_raw, mirror)):
        if (json.dumps(parsed, indent=1) + "\n").encode("utf-8") != raw:
            raise SystemExit("not in the extractor's format: " + rel)
    if set(repo["nodes"]) != set(mirror["nodes"]):
        raise SystemExit("node sets differ in " + rel)
    for nid, node in repo["nodes"].items():
        for field in AUTHORED_NODE:
            if node.get(field) != mirror["nodes"][nid].get(field):
                raise SystemExit(f"authored field {field} of {nid} differs between repository and mirror")
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


def make(rel):
    node_id, text = EDITS[rel]
    def change(d):
        append_once(d["nodes"][node_id]["responsibilities"], text)
        if node_id == VERB:
            add_edge_once(d, VERB_EDGE)
    return change


def main() -> None:
    if sys.argv[1:] not in (["--check"], ["--apply"]):
        raise SystemExit(__doc__)
    apply = sys.argv[1] == "--apply"
    for rel in EDITS:
        one(rel, make(rel), apply)
    print("applied" if apply else "checked")


if __name__ == "__main__":
    main()
