"""Graph descriptors for D-11 (melder_0, 2026-10-25; TASK-2026-10-10-enforce-import-policy-on-dynamic-imports).

The extractor (extract_graph.py) was run against a mirror of the repository's descriptors taken at
2026-10-25T10:3xZ, after the D-11 source edits, so the mirror's mechanical tier is current while its authored tier
is the repository's. For each of this lane's eight descriptors every authored field of every node (and the file's
authored edges and retired nodes) must equal the repository's copy - the mirror differs only in the mechanical tier -
and then the authored prose is brought to the source, re-read in full at 2026-10-25T10:3xZ: the import-set module
gains IMPORT_BUILTIN_NAMES; the compiler marks `static_only_denied_builtin_names` on the compiled surface; the
surface carries that field beside `denied_builtin_names`; the namespace configuration carries it to the strategies;
CodegenSystem reads it off the projection's compiled surface (empty for the no-projection default); the builtin and
name-resolution gates unite it with `denied_builtin_names`; and the builtins strategy installs the runtime
`__import__` wrapper. The compiler and the builtins strategy each gain the authored `uses` edge to the import-set
module they now read IMPORT_BUILTIN_NAMES from. The import-set module node stays unstamped (UNVERIFIED), as D-10 left
it. Written as the extractor writes (indent=1, LF), refusing a repository descriptor that changed since it was read.
Usage: d11_graph_descriptors.py --check | --apply
"""
import json
import pathlib
import sys
from typing import Callable, List

REPO = pathlib.Path.home() / "mnt/melder_private/context_compass/system_docs/graph/melder"
MIRROR = pathlib.Path("/tmp/m0d11_graph/graph/melder")
AUTHORED_NODE = ("role", "responsibilities", "owns_state", "phases", "semantics_authored_against", "include")
AUTHORED_FILE = ("edges_authored", "nodes_retired")

SETS = "melder.nexus.acl.configurations.profiles.codegen.stdlib_import_sets"
COMPILER = "melder.nexus.acl.frame_acl_compiler.FrameACLCompiler"
SURFACE = "melder.nexus.acl.frame_acl_compiled_access_surface.CompiledFrameACLAccessSurface"
NSCFG = "melder.nexus.rift.codegen_system.namespace.codegen_namespace_configuration.CodegenNamespaceConfiguration"
SYSTEM = "melder.nexus.rift.codegen_system.codegen_system.CodegenSystem"
BUILTIN_POLICY = ("melder.nexus.rift.codegen_system.validation.strategies."
                  "codegen_builtin_policy_strategy.CodegenBuiltinPolicyStrategy")
NAME_RES = ("melder.nexus.rift.codegen_system.validation.strategies."
            "codegen_name_resolution_strategy.CodegenNameResolutionStrategy")
BUILTINS = ("melder.nexus.rift.codegen_system.namespace.strategies."
            "codegen_builtins_strategy.CodegenBuiltinsStrategy")

R_SETS = (
    "defines IMPORT_BUILTIN_NAMES, the `__import__` name the compiler marks static-only denied wherever a preset "
    "enables imports with a list, so the validation gates refuse a `__import__` call or reference while the name "
    "stays in the runtime builtins for import statements (0.2.8271)")
R_COMPILER = (
    "compiles `static_only_denied_builtin_names` - `set(IMPORT_BUILTIN_NAMES)` when imports are on and an allow or "
    "deny list applies, empty otherwise - onto the compiled surface, so a `__import__` call or reference is refused "
    "at validation while import statements keep `__import__` (D-11, 0.2.8271)")
R_SURFACE = (
    "carries `static_only_denied_builtin_names`, the import-gate names denied at validation only and never stripped "
    "from the runtime builtins, beside `denied_builtin_names` (D-11, 0.2.8271)")
R_NSCFG = (
    "carries `static_only_denied_builtin_names` from the compiled surface to the builtin-policy, name-resolution and "
    "builtins strategies (D-11, 0.2.8271)")
R_SYSTEM = (
    "reads `static_only_denied_builtin_names` off the projection's compiled surface into the namespace "
    "configuration, empty for the no-projection default, so the codegen import gate reaches every built namespace "
    "(D-11, 0.2.8271)")
R_BUILTIN_POLICY = (
    "refuses a call of any name in `denied_builtin_names` united with `static_only_denied_builtin_names`, so a "
    "`__import__` call is refused wherever an import list applies (D-11, 0.2.8271)")
R_NAME_RES = (
    "drops `denied_builtin_names` united with `static_only_denied_builtin_names` from the allowed builtin names, so "
    "a bare `__import__` reference is refused wherever an import list applies (D-11, 0.2.8271)")
R_BUILTINS = (
    "installs a runtime `__import__` wrapper when imports are on and an import list applies, raising ImportError for "
    "a denied or unlisted root and delegating an allowed root to the real import; full_access and safe install none "
    "(D-11, 0.2.8271)")

COMPILER_EDGE = {
    "from": COMPILER, "to": SETS, "relation": "uses",
    "why": ("FrameACLCompiler reads IMPORT_BUILTIN_NAMES to mark the `__import__` name static-only denied on the "
            "compiled surface wherever a preset enables imports with a list."),
    "cardinality": "many_to_one", "phase": ["runtime"], "strength": "borrowed",
}
BUILTINS_EDGE = {
    "from": BUILTINS, "to": SETS, "relation": "uses",
    "why": ("CodegenBuiltinsStrategy reads IMPORT_BUILTIN_NAMES to replace the room's runtime `__import__` with a "
            "root-checking wrapper wherever an import list applies."),
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


def sets_edit(d): append_once(d["nodes"][SETS]["responsibilities"], R_SETS)
def surface_edit(d): append_once(d["nodes"][SURFACE]["responsibilities"], R_SURFACE)
def nscfg_edit(d): append_once(d["nodes"][NSCFG]["responsibilities"], R_NSCFG)
def system_edit(d): append_once(d["nodes"][SYSTEM]["responsibilities"], R_SYSTEM)
def builtin_policy_edit(d): append_once(d["nodes"][BUILTIN_POLICY]["responsibilities"], R_BUILTIN_POLICY)
def name_res_edit(d): append_once(d["nodes"][NAME_RES]["responsibilities"], R_NAME_RES)


def compiler_edit(d):
    append_once(d["nodes"][COMPILER]["responsibilities"], R_COMPILER)
    add_edge_once(d, COMPILER_EDGE)


def builtins_edit(d):
    append_once(d["nodes"][BUILTINS]["responsibilities"], R_BUILTINS)
    add_edge_once(d, BUILTINS_EDGE)


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


def main() -> None:
    if sys.argv[1:] not in (["--check"], ["--apply"]):
        raise SystemExit(__doc__)
    apply = sys.argv[1] == "--apply"
    one("nexus/acl/configurations/profiles/codegen/stdlib_import_sets.json", sets_edit, apply)
    one("nexus/acl/frame_acl_compiler.json", compiler_edit, apply)
    one("nexus/acl/frame_acl_compiled_access_surface.json", surface_edit, apply)
    one("nexus/rift/codegen_system/namespace/codegen_namespace_configuration.json", nscfg_edit, apply)
    one("nexus/rift/codegen_system/codegen_system.json", system_edit, apply)
    one("nexus/rift/codegen_system/validation/strategies/codegen_builtin_policy_strategy.json",
        builtin_policy_edit, apply)
    one("nexus/rift/codegen_system/validation/strategies/codegen_name_resolution_strategy.json",
        name_res_edit, apply)
    one("nexus/rift/codegen_system/namespace/strategies/codegen_builtins_strategy.json", builtins_edit, apply)
    print("applied" if apply else "checked")


if __name__ == "__main__":
    main()
