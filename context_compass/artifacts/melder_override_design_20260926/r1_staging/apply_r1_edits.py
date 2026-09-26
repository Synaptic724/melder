"""R1: retire the targeting surface the per-path overlay fed - anchored source edits and deletions.

Usage: python apply_r1_edits.py <tree_root> [--check]

dag_index.py keeps PathRegistry only; RootResolutionBlueprint owns a PathRegistry and loses the SocketRef/DagIndex API;
the Phase-5 builder stops installing an index; Phase 6 drops SocketRefSanityStrategy and the validation error drops
its four codes; the Phase-8 reuse key drops the socket rows; the dormant phase2-5 capture drops its socket rows; the
binding resolvers drop resolve_path_registry. DELETES lists files the caller removes after the edits land (the
script only checks they exist). Each anchor must match exactly once or nothing is written. Engine:
../s3_staging/apply_s3b1_edits.py.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "s3_staging"))

from apply_s3b1_edits import _apply_one

SC = "src/melder/aether/spellbook/spell_compiler/"
DAG = SC + "dag/dag_index.py"
BP = SC + "blueprints/root_resolution_blueprint.py"
BUILDER = SC + "system/spell_system_root_blueprint_builder.py"
PHASE6 = SC + "phases/compiler_phase_6.py"
ANALYZER = SC + "spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py"
SHARED = SC + "phases/shared_compiler_executions.py"
RESOLVER = SC + "codegen_creation_system/strategies/generalized/hydration/generalized_binding_resolver.py"
VERROR = "src/melder/utilities/custom_exceptions/spellbook_validation_error.py"
DELETES = [
    SC + "system/validation/socket_ref_sanity_strategy.py",
    "src/melder/aether/conduit/meld/overrides/spell_overrider.py",
]

DAG_IMPORTS_OLD = """from dataclasses import dataclass, field
from typing import (
    TYPE_CHECKING,
    Dict,
    List,
    Iterable,
    Callable,
    Sequence,
    Tuple,
    Optional,
    ClassVar,
)



from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind
from melder.aether.spellbook.spell_compiler.dag.target_spec import TargetSpecKind
from melder.aether.spellbook.spell_compiler.topology.spell_local_topology import (
    SpellSocketDescriptor,
)
from melder.utilities.general_base.cleanable import Cleanable
if TYPE_CHECKING:
    from melder.aether.spellbook.spell_compiler.dag.target_spec import TargetSpec
"""
DAG_IMPORTS_NEW = """from typing import (
    Dict,
    List,
    Sequence,
    Tuple,
    Optional,
)

from melder.utilities.general_base.cleanable import Cleanable
"""
DAG_CTX_OLD = """    Subsystem Context:
        The path-interning substrate of the `dag` package; `DagIndex` owns one and
        keys `SocketRef`s by the PathIds it mints.

    System Context:
        Phase 3/5 DAG index construction of the conjure pipeline.
"""
DAG_CTX_NEW = """    Subsystem Context:
        The path-interning substrate of the `dag` package. Every Phase-5
        `RootResolutionBlueprint` owns one, and Phase 8 mints its occurrence
        paths into it.

    System Context:
        Phase 5 (blueprints) and Phase 8 (occurrence paths) of the conjure pipeline.
"""

BP_IMPORT_OLD = "import threading\nfrom typing import List, Optional, Sequence, ClassVar\n"
BP_IMPORT_NEW = "from typing import List, Optional, Sequence, ClassVar\n"
BP_DAG_IMPORT_OLD = "from melder.aether.spellbook.spell_compiler.dag.dag_index import DagIndex, PathRegistry, SocketRef\n"
BP_DAG_IMPORT_NEW = "from melder.aether.spellbook.spell_compiler.dag.dag_index import PathRegistry\n"
BP_CLASS_OLD = """    ids into, for system validation, change-control/component-of wiring, and
    Phase 8-10 planning. Compiled blueprints record no SocketRefs (the Phase-5
    per-path overlay was retired on 2026-09-26); the socket collection and its
    targeting index hold only refs a caller adds through `add_socket_ref`.
"""
BP_CLASS_NEW = """    ids into, for system validation, change-control/component-of wiring, and
    Phase 8-10 planning. (The Phase-5 per-path socket overlay and its targeting
    index were retired on 2026-09-26; no reader needed them.)
"""
BP_OWNS_OLD = """        - The blueprint owns its DAG, socket reference collection, and
          targeting index.
"""
BP_OWNS_NEW = """        - The blueprint owns its DAG and its PathRegistry.
"""
BP_SLOTS_OLD = """        "_socket_refs",
        "_dag_index",
        "_dag_index_build_lock",
"""
BP_SLOTS_NEW = """        "_path_registry",
"""
BP_SIG_OLD = """            requires_spellspace_request: bool = False,
            socket_refs: Optional[Sequence[SocketRef]] = None,
            dag_index: Optional[DagIndex] = None,
    ) -> None:
"""
BP_SIG_NEW = """            requires_spellspace_request: bool = False,
            path_registry: Optional[PathRegistry] = None,
    ) -> None:
"""
BP_ARGS_OLD = """            socket_refs:
                Optional prebuilt socket-reference collection for targeting.
            dag_index:
                Optional prebuilt targeting index. When omitted, a fresh empty
                `DagIndex` is allocated.
"""
BP_ARGS_NEW = """            requires_spellspace_request:
                Whether the rooted graph contains spellspace-scoped work.
            path_registry:
                Optional PathRegistry to own. When omitted, a fresh one is
                allocated; Phase 8 mints occurrence paths into it.
"""
BP_NONNONE_OLD = "            - The blueprint always owns a non-None `DagIndex`.\n"
BP_NONNONE_NEW = "            - The blueprint always owns a non-None `PathRegistry`.\n"
BP_INIT_OLD = """        # Socket metadata; Phase 5 records none, direct callers may add refs.
        self._socket_refs: List[SocketRef] = list(socket_refs) if socket_refs else []

        # Targeting index; always non-None for consumers.
        self._dag_index: DagIndex = dag_index if dag_index is not None else DagIndex()
        self._dag_index_build_lock: threading.Lock = threading.Lock()
"""
BP_INIT_NEW = """        # Root-relative path ids; Phase 8 mints occurrence paths into it.
        self._path_registry: PathRegistry = (
            path_registry if path_registry is not None else PathRegistry()
        )
"""
BP_CLEAN_DOC_OLD = """            * Cleans up the DAG and index if present.
            * Drops references to node ids and socket refs to help GC.
"""
BP_CLEAN_DOC_NEW = """            * Cleans up the DAG and the PathRegistry.
            * Drops references to node ids.
"""
BP_CLEAN_OLD = """        if self._dag_index is not None:
            self._dag_index.cleanup()

        self._socket_refs.clear()
        self._ordered_node_ids.clear()

        del self._dag_index_build_lock
        del self._ordered_node_ids
        del self._requires_spellspace_request
        del self._dag_index
        del self._socket_refs
        del self._dag
"""
BP_CLEAN_NEW = """        self._path_registry.cleanup()

        self._ordered_node_ids.clear()

        del self._ordered_node_ids
        del self._requires_spellspace_request
        del self._path_registry
        del self._dag
"""
BP_TAIL = '''
    @property
    def path_registry(self) -> PathRegistry:
        """
        Return the PathRegistry that interns root-relative parameter paths for
        this blueprint.

        Contract:
            Phase 8 mints the path id of every occurrence below the root into
            this registry; the blueprint owns it and cleans it.
        """
        self.check_cleaned()
        return self._path_registry
'''

BUILDER_IMPORT = "from melder.aether.spellbook.spell_compiler.dag.dag_index import DagIndex\n"
BUILDER_DOC_OLD = """        * Each blueprint gets a fresh DagIndex and PathRegistry and records no
          SocketRefs. Phase 8 mints the root-relative path ids of its
          occurrences into that registry. Nothing here walks logical paths, so
          the cost follows spells and edges, never the number of paths (the
          per-path socket overlay that ran here had no reader that needed it
          and was retired on 2026-09-26).
"""
BUILDER_DOC_NEW = """        * Each blueprint owns a fresh PathRegistry; Phase 8 mints the
          root-relative path ids of its occurrences into it. Nothing here walks
          logical paths, so the cost follows spells and edges, never the number
          of paths (the per-path socket overlay that ran here had no reader
          that needed it and was retired on 2026-09-26).
"""
BUILDER_ROOTS_OLD = """
                socket_refs=None,              # compiled blueprints record no SocketRefs
                dag_index=None,                # _install_fresh_index installs it below
            )
            self._install_fresh_index(blueprint)
"""
BUILDER_ROOTS_NEW = """
            )
"""
BUILDER_SINGLE_OLD = """
            socket_refs=None,              # compiled blueprints record no SocketRefs
            dag_index=None,                # _install_fresh_index installs it below
        )
        self._install_fresh_index(blueprint)
"""
BUILDER_SINGLE_NEW = """
        )
"""
BUILDER_SDOC_OLD = """            - The blueprint gets a fresh DagIndex and PathRegistry and records
              no SocketRefs; Phase 8 mints the path ids it needs.
"""
BUILDER_SDOC_NEW = """            - The blueprint owns a fresh PathRegistry; Phase 8 mints the path
              ids it needs.
"""

PHASE6_IMPORT = """from melder.aether.spellbook.spell_compiler.system.validation.socket_ref_sanity_strategy import (
    SocketRefSanityStrategy,
)
"""
PHASE6_ENTRY_OLD = """            RootViabilityStrategy(),
            SocketRefSanityStrategy(),
        ]
"""
PHASE6_ENTRY_NEW = """            RootViabilityStrategy(),
        ]
"""

VERROR_A = '        "dag_index_orphan_socket",\n'
VERROR_B = '        "socket_ref_duplicate",\n        "socket_ref_missing_in_index",\n        "socket_ref_missing_in_index_name",\n'

AN_IMPORT = """    from melder.aether.spellbook.spell_compiler.dag.dag_index import (
        DagIndex,
        SocketRef,
    )
"""
AN_TYPE_OLD = "Optional[Tuple[Tuple[Any, ...], int, Tuple[Any, ...]]]"
AN_TYPE_NEW = "Optional[Tuple[Tuple[Any, ...], int]]"
AN_FAST_DOC_OLD = """            - Key shape: `(root_spell_id, ordered_node_ids, id(path_registry),
              blueprint_socket_rows, pool_digest)`. The root-specific rows are
              built once by the caller (`_build_root_blueprint_rows`) and the
              pool-wide rows are represented by their pass digest, so the key
              holds no pool-sized tuple and compares in time proportional to
              the root's own blueprint.
"""
AN_FAST_DOC_NEW = """            - Key shape: `(root_spell_id, ordered_node_ids, id(path_registry),
              pool_digest)`. The root-specific rows are built once by the
              caller (`_build_root_blueprint_rows`) and the pool-wide rows are
              represented by their pass digest, so the key holds no pool-sized
              tuple. The pool digest covers every spell's topology sockets, so
              no per-root socket rows are needed (the Phase-5 socket overlay
              that produced them was retired on 2026-09-26).
"""
AN_FAST_OLD = """        ordered_node_ids, path_registry_identity, blueprint_socket_rows = root_rows
        return (
            root_blueprint.root_spell_id,
            ordered_node_ids,
            path_registry_identity,
            blueprint_socket_rows,
            pool_digest,
        )
"""
AN_FAST_NEW = """        ordered_node_ids, path_registry_identity = root_rows
        return (
            root_blueprint.root_spell_id,
            ordered_node_ids,
            path_registry_identity,
            pool_digest,
        )
"""
AN_SIG_DOC_OLD = "            - Hashes exactly the five parts the fast key tracks, in the same\n"
AN_SIG_DOC_NEW = "            - Hashes exactly the four parts the fast key tracks, in the same\n"
AN_SIG_OLD = """        ordered_node_ids, path_registry_identity, blueprint_socket_rows = root_rows
        return SharedCompilerExecutions.hash_codegen_signature(
            root_blueprint.root_spell_id,
            ordered_node_ids,
            path_registry_identity,
            blueprint_socket_rows,
            pool_digest,
        )
"""
AN_SIG_NEW = """        ordered_node_ids, path_registry_identity = root_rows
        return SharedCompilerExecutions.hash_codegen_signature(
            root_blueprint.root_spell_id,
            ordered_node_ids,
            path_registry_identity,
            pool_digest,
        )
"""
AN_ROWS_OLD = """            path_registry_identity = id(root_blueprint.path_registry)
            blueprint_socket_rows = tuple(
                (
                    socket_ref.node_id,
                    socket_ref.param_name,
                    socket_ref.param_path_id,
                    socket_ref.socket_kind.value,
                )
                for socket_ref in (root_blueprint.socket_refs or ())
            )
        except Exception:
            return None
        return ordered_node_ids, path_registry_identity, blueprint_socket_rows
"""
AN_ROWS_NEW = """            path_registry_identity = id(root_blueprint.path_registry)
        except Exception:
            return None
        return ordered_node_ids, path_registry_identity
"""

SH_DEF_NEXT = "    def build_phase5_dag_edge_rows(\n"
SH_INIT_OLD = """        phase5_socket_ref_count = 0
        phase5_socket_rows: Tuple[Tuple[Any, ...], ...] = ()
"""
SH_FILL_OLD = """            phase5_socket_ref_count = len(artifact._root_blueprint_phase5.socket_refs)
            phase5_socket_rows = SharedCompilerExecutions.build_phase5_socket_rows(
                artifact
            )
"""
SH_SIG_OLD = """            phase5_socket_ref_count,
            phase5_socket_rows,
            phase5_dag_edge_rows,
"""
SH_SIG_NEW = """            phase5_dag_edge_rows,
"""
SH_PAY_OLD = """            "phase5_socket_ref_count": phase5_socket_ref_count,
            "phase5_socket_rows": phase5_socket_rows,
"""

RS_MODULE_OLD = """  - `SpellbookBindingResolver` backs the cache-load path, resolving spells
    from the live Spellbook pool and the phase-5 root blueprint.
"""
RS_MODULE_NEW = """  - `SpellbookBindingResolver` backs the cache-load path, resolving spells
    from the live Spellbook pool.
"""
RS_TYPING_OLD = "from typing import Any, Dict, Optional\n"
RS_TYPING_NEW = "from typing import Any, Dict\n"
RS_PLAN_DOC_OLD = """        - Resolves the path registry from analyzer graph-shape truth; `None`
          is a valid result and downstream override compilation tolerates it.
"""
RS_PLAN_LIFE_OLD = """        - `cleanup()` is idempotent and deletes the reference maps; the spells
          and registry are referenced, never owned.
"""
RS_PLAN_LIFE_NEW = """        - `cleanup()` is idempotent and deletes the reference maps; the spells
          are referenced, never owned.
"""
RS_SLOTS_OLD = """        "_spells_by_id",
        "_path_registry",
    ]
"""
RS_SLOTS_NEW = """        "_spells_by_id",
    ]
"""
RS_INIT_DOC_OLD = """            map harvested from both lane plans' steps (first occurrence wins),
            and the analyzer graph-shape path registry (None when absent).
"""
RS_INIT_DOC_NEW = """            map harvested from both lane plans' steps (first occurrence wins).
"""
RS_INIT_OLD = """        self._spells_by_id = spells_by_id

        graph_shape = spell_codegen_model.graph_shape
        self._path_registry = (
            None if graph_shape is None else graph_shape.path_registry
        )
"""
RS_INIT_NEW = """        self._spells_by_id = spells_by_id
"""
RS_DEL_OLD = """        del self._spells_by_id
        del self._path_registry
"""
RS_DEL_NEW = """        del self._spells_by_id
"""
RS_BOOK_DOC_OLD = """        - Resolves the path registry from the live phase-5 root blueprint,
          which conjure builds and `reset_phase_artifacts` preserves.
"""

EDITS = {
    DAG: [
        ("replace", DAG_IMPORTS_OLD, DAG_IMPORTS_NEW),
        ("replace", DAG_CTX_OLD, DAG_CTX_NEW),
        ("cut", "@dataclass(frozen=True, slots=True)\nclass SocketRef:", None),
    ],
    BP: [
        ("replace", BP_IMPORT_OLD, BP_IMPORT_NEW),
        ("replace", BP_DAG_IMPORT_OLD, BP_DAG_IMPORT_NEW),
        ("replace", BP_CLASS_OLD, BP_CLASS_NEW),
        ("replace", BP_OWNS_OLD, BP_OWNS_NEW),
        ("replace", BP_SLOTS_OLD, BP_SLOTS_NEW),
        ("replace", BP_SIG_OLD, BP_SIG_NEW),
        ("replace", BP_ARGS_OLD, BP_ARGS_NEW),
        ("replace", BP_NONNONE_OLD, BP_NONNONE_NEW),
        ("replace", BP_INIT_OLD, BP_INIT_NEW),
        ("replace", BP_CLEAN_DOC_OLD, BP_CLEAN_DOC_NEW),
        ("replace", BP_CLEAN_OLD, BP_CLEAN_NEW),
        ("cut", "    @property\n    def socket_refs(self) -> List[SocketRef]:", None),
        ("append", BP_TAIL),
    ],
    BUILDER: [
        ("replace", BUILDER_IMPORT, ""),
        ("replace", BUILDER_DOC_OLD, BUILDER_DOC_NEW),
        ("replace", BUILDER_ROOTS_OLD, BUILDER_ROOTS_NEW),
        ("replace", BUILDER_SINGLE_OLD, BUILDER_SINGLE_NEW),
        ("replace", BUILDER_SDOC_OLD, BUILDER_SDOC_NEW),
        ("cut", "    @staticmethod\n    def _install_fresh_index(", None),
    ],
    PHASE6: [
        ("replace", PHASE6_IMPORT, ""),
        ("replace", PHASE6_ENTRY_OLD, PHASE6_ENTRY_NEW),
    ],
    VERROR: [
        ("replace", VERROR_A, ""),
        ("replace", VERROR_B, ""),
    ],
    ANALYZER: [
        ("replace", AN_IMPORT, ""),
        ("replace", "    def _build_occurrence_graph_fast_key(\n            self,\n            *,\n"
                    "            root_blueprint: \"RootResolutionBlueprint\",\n            root_rows: " + AN_TYPE_OLD,
         "    def _build_occurrence_graph_fast_key(\n            self,\n            *,\n"
         "            root_blueprint: \"RootResolutionBlueprint\",\n            root_rows: " + AN_TYPE_NEW),
        ("replace", "    def _build_occurrence_graph_input_signature(\n            self,\n            *,\n"
                    "            root_blueprint: \"RootResolutionBlueprint\",\n            root_rows: " + AN_TYPE_OLD,
         "    def _build_occurrence_graph_input_signature(\n            self,\n            *,\n"
         "            root_blueprint: \"RootResolutionBlueprint\",\n            root_rows: " + AN_TYPE_NEW),
        ("replace", "    ) -> " + AN_TYPE_OLD + ":", "    ) -> " + AN_TYPE_NEW + ":"),
        ("replace", AN_FAST_DOC_OLD, AN_FAST_DOC_NEW),
        ("replace", AN_FAST_OLD, AN_FAST_NEW),
        ("replace", AN_SIG_DOC_OLD, AN_SIG_DOC_NEW),
        ("replace", AN_SIG_OLD, AN_SIG_NEW),
        ("replace", AN_ROWS_OLD, AN_ROWS_NEW),
    ],
    SHARED: [
        ("cut", "    @staticmethod\n    def build_phase5_socket_rows(", "    def build_phase5_dag_edge_rows("),
        ("replace", SH_DEF_NEXT, "    @staticmethod\n" + SH_DEF_NEXT),
        ("replace", SH_INIT_OLD, ""),
        ("replace", SH_FILL_OLD, ""),
        ("replace", SH_SIG_OLD, SH_SIG_NEW),
        ("replace", SH_PAY_OLD, ""),
    ],
    RESOLVER: [
        ("replace", RS_MODULE_OLD, RS_MODULE_NEW),
        ("replace", RS_TYPING_OLD, RS_TYPING_NEW),
        ("replace", RS_PLAN_DOC_OLD, ""),
        ("replace", RS_PLAN_LIFE_OLD, RS_PLAN_LIFE_NEW),
        ("replace", RS_SLOTS_OLD, RS_SLOTS_NEW),
        ("replace", RS_INIT_DOC_OLD, RS_INIT_DOC_NEW),
        ("replace", RS_INIT_OLD, RS_INIT_NEW),
        ("replace", RS_DEL_OLD, RS_DEL_NEW),
        ("cut", "    def resolve_path_registry(self) -> Optional[Any]:\n        \"\"\"\n        Return the phase-5 path registry, or",
         "class SpellbookBindingResolver(Cleanable):"),
        ("replace", "        return spell\n\nclass SpellbookBindingResolver(Cleanable):",
         "        return spell\n\n\nclass SpellbookBindingResolver(Cleanable):"),
        ("replace", RS_BOOK_DOC_OLD, ""),
        ("cut", "    def resolve_path_registry(self) -> Optional[Any]:", None),
    ],
}


def _apply(data: str, edit: tuple, rel: str) -> str:
    """Apply one edit; `append` adds text after the file's last line in its line ending."""
    if edit[0] != "append":
        return _apply_one(data, edit, rel)
    nl = "\r\n" if data.endswith("\r\n") else "\n"
    return data + edit[1].replace("\n", nl)


def main() -> None:
    """Check every anchor and every file to delete, then write every file (unless --check)."""
    root = pathlib.Path(sys.argv[1])
    check = "--check" in sys.argv[2:]
    for rel in DELETES:
        if not (root / rel).is_file():
            raise SystemExit(f"missing file to delete: {rel}")
    pending = {}
    for rel, edits in EDITS.items():
        path = root / rel
        data = path.read_bytes().decode("utf-8")
        for edit in edits:
            data = _apply(data, edit, rel)
        compile(data, rel, "exec")
        pending[path] = data
    for path, data in pending.items():
        if not check:
            path.write_bytes(data.encode("utf-8"))
        print(("checked " if check else "edited ") + str(path))
    for rel in DELETES:
        print("to delete: " + rel)


if __name__ == "__main__":
    main()
