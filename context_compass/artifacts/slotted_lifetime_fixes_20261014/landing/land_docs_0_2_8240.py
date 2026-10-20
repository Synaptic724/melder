"""
Land the slotted_lifetime lane (0.2.8236-0.2.8240) and the owner's runtime model in the system documents
(EPIC-2026-10-14-slotted_lifetime_ownership_fixes). Edits src_architecture.md, src_components.md and tests_components.md
with anchored replacements (each anchor must match exactly once; the documents stay LF ASCII) and remeasures the
code-map entries of the files the lane changed. Regenerate the three indexes afterwards (index_document.py, --check).

Run from the repository root: python land_docs_0_2_8240.py <verified_at UTC timestamp>
"""
import pathlib
import re
import sys

STAMP = sys.argv[1]
DOCS = pathlib.Path("context_compass/system_docs")
CHANGED = [
    "src/melder/aether/aetheric_frame/aetheric_frame.py",
    "src/melder/aether/aetheric_frame/conduit_cloud.py",
    "src/melder/aether/conduit/conduit.py",
    "src/melder/aether/conduit/conduit_cluster.py",
    "src/melder/aether/conduit/conduit_ward/conduit_ward.py",
    "src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py",
    "src/melder/aether/conduit/creations/cluster_creations.py",
    "src/melder/aether/conduit/creations/creations.py",
    "src/melder/aether/conduit/meld/conduit_meld.py",
    "src/melder/aether/conduit/meld/spellspace_meld.py",
    "src/melder/aether/conduit/spell_space/spell_space.py",
    "src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py",
    "src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py",
]


def loc(path: str) -> int:
    """Count a file's lines with splitlines(), as the code maps are measured."""
    return len(pathlib.Path(path).read_bytes().decode("utf-8").splitlines())


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    assert count == 1, (label, count)
    return text.replace(old, new)


def insert_after_once(text: str, anchor: str, addition: str, label: str) -> str:
    return replace_once(text, anchor, anchor + addition, label)


def insert_before_once(text: str, anchor: str, addition: str, label: str) -> str:
    return replace_once(text, anchor, addition + anchor, label)


def remeasure(text: str, path: str, label: str) -> str:
    """Update one code-map entry's extent and stamp when the document carries it."""
    pattern = re.compile(
        r"(- path: `" + re.escape(path) + r"`\n  start_line: 1\n  end_line: )\d+(\n  loc: )\d+(\n  verified_at: )\S+")
    count = len(pattern.findall(text))
    assert count <= 1, (label, path, count)
    if count == 0:
        return text
    n = loc(path)
    return pattern.sub(lambda m: f"{m.group(1)}{n}{m.group(2)}{n}{m.group(3)}{STAMP}", text)


RUNTIME_MODEL = """## Runtime Model: Structure Is the Contract

Owner ruling (2026-10-14). Melder is a runtime that agents work inside, not a container that owns every object it
hands out. An agent loads its world into the Python runtime and iterates there: it binds a tool, melds it in a
conduit, tries it, binds a new version and notches to the one it wants, tears scopes down, records the blueprint and
builds the next thing - sometimes the subsystem it is working in. Codegen is iterative, so the iteration happens in
the runtime, not outside it.

What must be correct is the structure: bindings, spell indexes and their versions, which conduit owns which spell,
contracts and links, lineage and clusters, verdicts, and the record the Crystallizer keeps of them. That is what
Melder validates, gates, records and restores; a restore rebuilds structure with fresh identities and no saved
application objects.

Generated objects are working material. An object may be superseded by a newer version, left pending after a
transfer or a contract change, or kept by application code after Melder lets go of it, and agents clean such objects
up when they choose. Melder's infrastructure cleans up its own state: a store disposes what it records when it ends,
a scope teardown ends its stores, and a purge disposes what it retires. It does not police userland objects: it does
not dispose an object because something else changed (a transfer, a contract change, a removed definition), and an
object it lets go of is not a leak. A transfer hands over stewardship, not a working setup (Sequence: Transfer Spell
Ownership).

So a defect is structure that is wrong or stuck: a record that names the wrong owner, so the wrong teardown disposes
an object (a cluster's shared object recorded in its leader's store, a moved holder's `many` children left in the old
root's store), or state an agent cannot get past (a torn-down root still recorded in its cluster). An object that
still references something its owner has since disposed - after a transfer, a contract change or a teardown - is
pending work for the agent, not a defect.

"""

ARCH_INVARIANTS = """- Ownership transfer moves by default and disposes nothing (2026-10-14, 0.2.8239-0.2.8240, owner ruling):
  `Conduit.transfer_spell_ownership` and `ConduitWard._transfer_spell_ownership` default to `move_creations=True`, so
  `TransferOfOwnership._move_creations` extracts every index member's entries from the source root's store and
  restores them into the target's - a `unique` stays one object and a holder's adopted children travel in its row -
  while `move_creations=False` (`_teardown_creations`) takes the active member's entries out and keeps them only for
  the transfer's rollback. A moved entry replaces what the target's store holds under that id, undisposed; lineage
  instances stay where they were resolved; spellspace and cluster instances are not in a conduit store. No step of a
  transfer disposes anything, and it hands over stewardship, not a working setup: the spells the transferred one
  depends on stay with the source unless `include_dependencies` moves the direct ones, so once the source tears down
  the target purges what it does not want, binds what it needs and melds its own version. `TransferOfOwnership`'s own
  constructor keeps `move_creations=False`; the public verbs always pass the value.
  EVIDENCE: `src/melder/aether/conduit/conduit.py:Conduit.transfer_spell_ownership`,
  `src/melder/aether/conduit/conduit_ward/conduit_ward.py:ConduitWard._transfer_spell_ownership`,
  `src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:TransferOfOwnership.execute`,
  `TransferOfOwnership._move_creations` and `TransferOfOwnership._teardown_creations`.
- Holder records (2026-10-14, 0.2.8238): a slotted holder's disposal-bearing `many` children are recorded with the
  holder. Right after a miss publishes holder i, under its build lock, it calls `c{i}.adopt_children(sid{i}, v{i},
  ((sidK, vK), ...))`, and `Creations.adopt_children` moves those children out of their spells' `many` buckets into
  the holder's `HolderDisposalEntry` (a holder without disposal methods gets one with `methods=[]`); a child is in
  exactly one place. Every store verb keyed by the holder reaches its children with one dict read: purging the holder
  disposes it, then its children newest first; `extract_spell_creations` / `restore_spell_creations` carry them, so an
  ownership move takes them along; whole-store disposal runs the holder's methods, then its children's. A `many` purge
  or live-creation probe of the child's spell counts only children no holder adopted. The store lock stays a leaf,
  adoption is cold-path only, and every warm `_site_plan_executor` body is byte-identical (emission 0.2.8235 ->
  0.2.8240: the only change is the adoption line in the misses).
  EVIDENCE: `src/melder/aether/conduit/creations/creations.py:HolderDisposalEntry`, `Creations.adopt_children`,
  `Creations.purge`, `Creations.extract_spell_creations`, `Creations.restore_spell_creations` and
  `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:SitePlanEmission._emit_miss`.
- The cluster owns its team store (2026-10-14, 0.2.8237): `ConduitCluster._team_store` is a `Creations` the cluster
  owns (owner and scope id the cluster id). `bind_elected_leader` binds every member root's `ClusterCreations` facade
  to it with the elected leader's id, which is the purge authority (`ConduitMeld._get_purge_creations`), and a root
  that joins while a leader is elected is bound the same way (`bind_member`); unelect, a leader's leave and a
  leader's teardown unbind the facades and keep the store, so the next election serves the same instances. The
  cluster's cleanup - `ConduitCloud.delete_cluster`, or the cloud's cleanup in frame teardown - disposes the store
  once; `delete_cluster` raises its disposal failures after the cluster is deleted, and frame teardown logs them.
  While no leader is elected `resolved_store()` raises, as before.
  EVIDENCE: `src/melder/aether/conduit/conduit_cluster.py:ConduitCluster.bind_elected_leader`,
  `ConduitCluster.bind_member`, `ConduitCluster.cleanup`,
  `src/melder/aether/conduit/creations/cluster_creations.py:ClusterCreations.resolved_store`,
  `src/melder/aether/aetheric_frame/conduit_cloud.py:ConduitCloud.delete_cluster` and
  `src/melder/aether/aetheric_frame/aetheric_frame.py:AethericFrame._cleanup_data_structures`.
- A root's teardown leaves its cluster (2026-10-14, 0.2.8236): `Conduit._cleanup_normal_conduit` first calls
  `_leave_cluster_for_teardown`, which finds the root's cluster through the frame's DevOps conduit->cluster index (one
  keyed read; membership is exclusive) and, while the frame is live, runs `ConduitCluster.release_member`: unelect
  first when the root leads, then one CLUSTER_LEAVE transaction that leaves `members` and unshares both directions
  while the share record is still present, then `remove_member`. During frame teardown, when no transaction can
  start, or when the exit raises (logged), `ConduitCluster.drop_member` makes the same changes without transactions
  (unbind the leader's facades, remove the membership, unbind its own facade; the ward's cleanup severs its
  contracts). `ConduitCloud.remove_conduit_from_cluster` takes the same ordered exit, so a leaver's shared roots no
  longer stay contracted to the remaining members, and `get_clusters_for_conduit` answers from the membership index
  through the cloud's `_cluster_names_by_id` map. No meld path changes.
  EVIDENCE: `src/melder/aether/conduit/conduit.py:Conduit._leave_cluster_for_teardown`,
  `Conduit._cleanup_normal_conduit`, `src/melder/aether/conduit/conduit_cluster.py:ConduitCluster.release_member`,
  `ConduitCluster.drop_member`,
  `src/melder/aether/aetheric_frame/conduit_cloud.py:ConduitCloud.remove_conduit_from_cluster` and
  `ConduitCloud.get_clusters_for_conduit`.
"""

ARCH_FAILURES = """- A transfer's new owner can start out broken, by design (documented in 0.2.8240): once the source tears down, a
  moved instance may hold dependencies the source disposed, and a meld that must build the spell again without them
  raises `UnresolvedInputError` naming each missing input ("<Spell>.<param> expects <Type>, but nothing registered
  provides it and this meld did not supply it. ... or bind a provider for <Type>."). Bind the providers (or transfer
  with `include_dependencies=True`) and meld again.
  EVIDENCE: `src/melder/aether/conduit/conduit.py:Conduit.transfer_spell_ownership` and
  `src/melder/utilities/custom_exceptions/unresolved_input_error.py:UnresolvedInputError`.
- Breaking (0.2.8239): `transfer_spell_ownership` defaults to `move_creations=True`. Pass `False` for the old
  behaviour: the active member's instances leave the source store, neither moved nor disposed, and the target builds
  its own - for a `unique`, a second instance.
  EVIDENCE: `src/melder/aether/conduit/conduit.py:Conduit.transfer_spell_ownership`.
- Purging a holder disposes the `many` children built for it, after it, and raises their disposal failures with its
  own; through 0.2.8237 they stayed registered and open until their store ended. An ownership move carries them;
  through 0.2.8237 the old root's teardown disposed them under the moved holder (0.2.8238).
  EVIDENCE: `src/melder/aether/conduit/creations/creations.py:Creations.purge` and `Creations.extract_spell_creations`.
- A cluster's shared object survives a leader change and is disposed once, by the cluster's deletion or its frame's
  teardown (0.2.8237); `delete_cluster` raises ExceptionGroup "Conduit cluster cleaned with disposal failures." after
  deleting the cluster. Through 0.2.8236 a leader change built a second object and the old leader's teardown disposed
  the first while members still used it.
  EVIDENCE: `src/melder/aether/conduit/conduit_cluster.py:ConduitCluster.cleanup` and
  `src/melder/aether/aetheric_frame/conduit_cloud.py:ConduitCloud.delete_cluster`.
- A torn-down root no longer stays in its cluster (0.2.8236): through 0.2.8235 `unelect_leader()` then failed
  part-way, `elect_leader()` refused because the dead leader was still recorded, adding a conduit raised, and
  `delete_cluster()` removed the cluster and then raised before cleaning it up; an explicit leave left the leaver's
  roots contracted to every remaining member.
  EVIDENCE: `src/melder/aether/conduit/conduit.py:Conduit._leave_cluster_for_teardown` and
  `src/melder/aether/conduit/conduit_cluster.py:ConduitCluster.release_member`.
"""

ARCH_HANDOFF = """2026-10-14 slotted lifetimes and the runtime model (0.2.8236-0.2.8240): the new section "Runtime Model: Structure
Is the Contract" records the owner's ruling - correctness lives in the structure; generated objects are working
material agents iterate on, leave pending and clean up; Melder's infrastructure cleans up its own state, not
userland objects. A root's teardown leaves its cluster (0.2.8236), the cluster owns its team store (0.2.8237), a
holder's `many` children are recorded with it (0.2.8238), and a transfer moves by default, disposes nothing
(0.2.8239) and hands over stewardship, not a working setup (0.2.8240). The transfer sequence, the operational
invariants, the failure modes and the code map carry it; the component map carries the per-component rules, and
the 0.2.8235 invariant's cluster-store and purge sentences point at the newer entries. Contract invalidation (a
retired consumer leaves the root's store undisposed; lessers keep theirs) is intended behaviour by the same ruling
and is not listed as a failure.

"""


def architecture(text: str) -> str:
    text = insert_before_once(text, "## Entrypoints and Runtime Guardrails\n", RUNTIME_MODEL, "arch runtime model")
    text = replace_once(
        text,
        "   - Moves or tears down creations.\n",
        "   - With `move_creations=True` (the default since 0.2.8239) moves the source store's instances of every index\n"
        "     member into the target's store, a holder's adopted `many` children with it (0.2.8238); with `False` takes\n"
        "     the active member's instances out of the source store, neither moved nor disposed. Lineage instances stay\n"
        "     where they were resolved. A transfer disposes nothing.\n",
        "arch transfer step",
    )
    text = insert_after_once(
        text,
        "   - Optionally transfers or dirties dependencies.\n   - Marks lineage dirty/gated for revalidation.\n",
        "4. The target receives stewardship, not a working setup (0.2.8240). The spells the transferred one depends on\n"
        "   stay with the source unless `include_dependencies` moves the direct ones, so once the source tears down, a\n"
        "   moved instance can hold dependencies that were just disposed; the target purges what it does not want, binds\n"
        "   what it needs (`UnresolvedInputError` names each missing input) and melds its own version.\n",
        "arch transfer handover",
    )
    text = insert_after_once(text, "## Operational Invariants\n", ARCH_INVARIANTS, "arch invariants")
    text = replace_once(
        text,
        "the lineage root's, the elected cluster leader's.\n",
        "the lineage root's, the cluster's team\n  store (0.2.8237; the elected leader's own store before).\n",
        "arch 0.2.8235 cluster store",
    )
    text = replace_once(
        text,
        "  is unchanged; a lost cold race's children stay in the holder's store until it is disposed. Purge semantics are\n"
        "  unchanged: purging a holder disposes the holder only, and a `many` purge or live-creation probe finds the\n"
        "  children at the holder's owner. The opt-in singleton specializer, whose straight-line body would rebuild a\n"
        "  captured holder's child on every warm meld, declines graphs in which a `many` step feeds a non-`many` step and\n",
        "  is unchanged; a lost cold race's children stay in the holder's store until it is disposed. Purge semantics\n"
        "  changed in 0.2.8238 (Holder records, above): purging a holder disposes its children too. The opt-in singleton\n"
        "  specializer, whose straight-line body would rebuild a captured holder's child on every warm meld, declines\n"
        "  graphs in which a `many` step feeds a non-`many` step and\n",
        "arch 0.2.8235 purge",
    )
    text = insert_after_once(text, "## Failure Modes and Error Paths\n", ARCH_FAILURES, "arch failures")
    text = replace_once(
        text,
        "    root's ConduitPool elastic, baseline 20 / max 256 (0.2.8234).\n",
        "    root's ConduitPool elastic, baseline 20 / max 256 (0.2.8234); a root's teardown leaves its cluster first\n"
        "    (0.2.8236); `transfer_spell_ownership` defaults to `move_creations=True` (0.2.8239) and documents the\n"
        "    handover (0.2.8240).\n",
        "arch map conduit",
    )
    text = replace_once(text, "  note: cluster auto-sharing.\n",
                        "  note: cluster auto-sharing; the ordered leave (0.2.8236) and the team store the cluster owns (0.2.8237).\n"
                        "- path: `src/melder/aether/conduit/creations/cluster_creations.py`\n"
                        "  start_line: 1\n"
                        f"  end_line: {loc(CHANGED[6])}\n"
                        f"  loc: {loc(CHANGED[6])}\n"
                        f"  verified_at: {STAMP}\n"
                        "  note: a member root's facade over the cluster's team store; the elected leader's id is the purge\n"
                        "    authority (0.2.8237).\n",
                        "arch map cluster")
    text = replace_once(text, "  note: dynamic conduit registry.\n",
                        "  note: dynamic conduit registry; explicit leaves take the cluster's ordered exit, cluster lookups read the\n"
                        "    membership index (0.2.8236), `delete_cluster` raises disposal failures after deleting (0.2.8237).\n",
                        "arch map cloud")
    text = replace_once(text, "  note: instance registry; `ManyDisposalBucket` and `register_many` (0.2.8216).\n",
                        "  note: instance registry; `ManyDisposalBucket` and `register_many` (0.2.8216); `HolderDisposalEntry` and\n"
                        "    `adopt_children` (0.2.8238).\n",
                        "arch map creations")
    text = replace_once(text, "  note: ownership transfer.\n",
                        "  note: ownership transfer; moves by default and disposes nothing (0.2.8239).\n",
                        "arch map transfer")
    text = replace_once(text, "    `many` children register in that site's store (0.2.8235).\n",
                        "    `many` children register in that site's store (0.2.8235) and its miss records them with the holder\n"
                        "    (`adopt_children`, 0.2.8238).\n",
                        "arch map lowering")
    text = replace_once(text, "  note: per-frame state and control plane; cleanup-safe probes, the frame lock kept after cleanup (0.2.8231).\n",
                        "  note: per-frame state and control plane; cleanup-safe probes, the frame lock kept after cleanup (0.2.8231);\n"
                        "    frame teardown logs the cloud's cluster disposal failures (0.2.8237).\n",
                        "arch map frame")
    sources_start = text.index("## Information Sources\n")
    sources_end = text.index("## Context / Handoff Summary\n")
    sources = text[sources_start:sources_end]
    for path in ("src/melder/aether/aetheric_frame/conduit_cloud.py", "src/melder/aether/conduit/creations/cluster_creations.py"):
        if f"- `{path}`\n" not in sources:
            sources = replace_once(sources, "- `src/melder/aether/conduit/conduit_cluster.py`\n",
                                   "- `src/melder/aether/conduit/conduit_cluster.py`\n" + f"- `{path}`\n", "arch sources " + path)
    text = text[:sources_start] + sources + text[sources_end:]
    text = insert_after_once(text, "## Context / Handoff Summary\n\n", ARCH_HANDOFF, "arch handoff")
    for path in CHANGED:
        text = remeasure(text, path, "arch")
    return text


COMP_TRANSFER = """Contract/Interface:
- `Conduit.transfer_spell_ownership(...)` and `_transfer_spell_ownership(...)`; both default to `move_creations=True`
  since 0.2.8239 (`TransferOfOwnership`'s own constructor keeps False; the verbs always pass the value).
- `move_creations=True`: `_move_creations` extracts every index member's entries from the source root's store and
  restores them into the target's - a `unique` stays one object and a holder's row carries its adopted `many` children
  (0.2.8238) - replacing, undisposed, whatever the target held under that id. `False`: `_teardown_creations` takes the
  active member's entries out of the source store and keeps them only for the transfer's rollback; parked members'
  entries stay. Lineage instances are skipped either way. Nothing is disposed.
- Stewardship, not a working setup (0.2.8240): dependency spells stay with the source unless `include_dependencies`
  transfers each direct dependency the source owns with the same options; once the source tears down, the target
  purges what it does not want, binds what it needs (`UnresolvedInputError` names each missing input) and melds its
  own version. That is the expected path in a runtime agents iterate in (src_architecture, Runtime Model).
"""

COMP_CLUSTER = """- `release_member` is every leave's ordered exit (0.2.8236): unelect first when the conduit leads, then
  `handle_leave` unshares both directions while the share record exists, then `remove_member`; `drop_member` makes
  the same changes without transactions for a root torn down with its frame or whose exit failed. Root teardown calls
  it through `Conduit._leave_cluster_for_teardown`.
- The team store (0.2.8237): `_team_store`, a `Creations` the cluster owns (owner and scope id the cluster id), holds
  the `unique_per_conduit_cluster` instances. `bind_elected_leader` binds each member root's `ClusterCreations`
  facade to it with the leader's id (the purge authority) and `bind_member` binds a root that joins while a leader is
  elected; unelect and a leader's exit unbind the facades and keep the store; `cleanup` disposes it once and raises
  ExceptionGroup "Conduit cluster cleaned with disposal failures."
"""

COMP_ADOPTION = """- Holder records (2026-10-14, 0.2.8238): right after a miss publishes holder i, under its build lock, it emits
  `c{i}.adopt_children(sid{i}, v{i}, ((sidK, vK), ...))` naming the disposal-bearing `many` children it registered in
  `c{i}` for the holder; `Creations.adopt_children` moves them into the holder's `HolderDisposalEntry`, so purge,
  extract/restore and disposal of the holder take them along (Subcomponent: Creations Disposal Pipeline). Only misses
  change; every `_site_plan_executor` body is byte-identical.
  EVIDENCE: `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:SitePlanEmission._emit_miss`.
"""

COMP_HANDOFF = """2026-10-14 slotted lifetimes (0.2.8236-0.2.8240): ConduitCluster Auto-Sharing carries the ordered exit and the team
store, ConduitCloud Registry the membership-index lookup and `delete_cluster`'s raise, Ownership Transfer with its
flow and diagram the default move, the absence of disposal and the handover (stewardship, not a working setup),
Creations Disposal Pipeline the holder records, the SpellCompiler the adoption line, Meld Resolution Runtime the
team-store selection, and Conduit Runtime that a root leaves its cluster first. The code-map extents of the files the
lane changed are remeasured. The runtime model behind the transfer and invalidation rulings (structure is the
contract; objects are working material) lives in src_architecture.

"""


def components(text: str) -> str:
    text = replace_once(
        text,
        "Contract/Interface:\n- `Conduit.transfer_spell_ownership(...)` and `_transfer_spell_ownership(...)`.\n",
        COMP_TRANSFER,
        "comp transfer contract",
    )
    text = replace_once(
        text,
        "  cluster-created contracts.\nData Structures:\n- `members` set and `shared_spells` map.\n",
        "  cluster-created contracts.\n" + COMP_CLUSTER + "Data Structures:\n"
        "- `members` set, `shared_spells` map and the owned `_team_store` (0.2.8237).\n",
        "comp cluster",
    )
    text = replace_once(
        text,
        "- Cluster operations still use borrowed normal-root maps and retain dynamic admission.\n",
        "- Cluster operations still use borrowed normal-root maps and retain dynamic admission.\n"
        "- `remove_conduit_from_cluster` runs `ConduitCluster.release_member` (0.2.8236); `get_clusters_for_conduit` reads\n"
        "  the frame's membership index and names clusters through `_cluster_names_by_id`; `delete_cluster` raises the\n"
        "  deleted cluster's disposal failures after it is gone (0.2.8237).\n",
        "comp cloud contract",
    )
    text = replace_once(
        text,
        "- Owned `_named_conduits`, `_conduit_names_by_id`, `_reserved_conduit_names` and clusters.\n",
        "- Owned `_named_conduits`, `_conduit_names_by_id`, `_reserved_conduit_names`, clusters and\n"
        "  `_cluster_names_by_id` (0.2.8236).\n",
        "comp cloud data",
    )
    text = replace_once(
        text,
        "  aggregated into one `ExceptionGroup` (0.2.80).\nData Structures:\n",
        "  aggregated into one `ExceptionGroup` (0.2.80).\n"
        "- Holder records (0.2.8238): `Creations.adopt_children` moves a just-published slotted holder's disposal-bearing\n"
        "  `many` children from their buckets into its `HolderDisposalEntry(item, methods, children)`; disposal runs the\n"
        "  holder's methods, then each child's, newest child first (`_dispose_holder_entry`); purging the holder disposes\n"
        "  its children after it; a `many` purge or probe of a child's spell sees only children no holder adopted;\n"
        "  extract/restore rows carry the children.\n"
        "Data Structures:\n",
        "comp disposal contract",
    )
    text = replace_once(
        text,
        "  list (0.2.8216); unique keys keep their `(object, methods)` tuple.\n",
        "  list (0.2.8216); unique keys keep their `(object, methods)` tuple.\n"
        "- `HolderDisposalEntry` per slotted holder that adopted children (0.2.8238), in place of its tuple.\n",
        "comp disposal data",
    )
    text = replace_once(
        text,
        "   - Moves or tears down creations and adjusts contracts/clusters.\n",
        "   - Moves the source store's entries of every index member to the target (`move_creations=True`, the default\n"
        "     since 0.2.8239; holder rows carry their adopted children) or takes the active member's out (`False`);\n"
        "     disposes nothing; adjusts contracts/clusters.\n",
        "comp transfer flow",
    )
    text = insert_before_once(
        text,
        "\n### Flow: SpellSpace Scoped Meld\n",
        "4. The target can start out broken once the source tears down; it binds what it needs and melds its own\n"
        "   version (0.2.8240).\n",
        "comp transfer flow handover",
    )
    text = replace_once(
        text,
        "  TO->>SC: move/teardown creations\n",
        "  TO->>TC: move creations (default), dispose nothing\n"
        "  TO->>SC: or take the active member's out (move_creations=False)\n",
        "comp mermaid",
    )
    text = replace_once(
        text,
        "store, lineage from the lineage root and cluster from the elected leader (not live without one). Only a\n"
        "disposal-bearing `many` is stored - in the innermost scope - so a `many` without disposal methods probes\n"
        "as 0. CORRECTED 2026-09-28: the SpellSpace door read `many` from the owner conduit's store, missing what\n"
        "the space held and counting what the conduit held. Since 0.2.8235 a `many` built as a shared site's child is\n"
        "stored with that site (the holder's owner), so the probe counts it there - the root for a `unique` holder, the\n"
        "conduit for a per-conduit holder melded in its space, the lineage root, the cluster leader - and not at the\n"
        "lesser or space that melded the holder first.\n",
        "store, lineage from the lineage root and cluster from the cluster's team store (0.2.8237; not live without an\n"
        "elected leader). Only a disposal-bearing `many` is stored - in the innermost scope - so a `many` without\n"
        "disposal methods probes as 0. CORRECTED 2026-09-28: the SpellSpace door read `many` from the owner conduit's\n"
        "store, missing what the space held and counting what the conduit held. Since 0.2.8235 a `many` built as a\n"
        "shared site's child is stored with that site (the holder's owner), so the probe counts it there - the root\n"
        "for a `unique` holder, the conduit for a per-conduit holder melded in its space, the lineage root, the\n"
        "cluster's team store - and not at the lesser or space that melded the holder first. Since 0.2.8238 such a\n"
        "child is recorded with its holder (`HolderDisposalEntry`), so a `many` probe of the child's spell counts only\n"
        "children no holder adopted.\n",
        "comp probe cluster",
    )
    text = replace_once(
        text,
        "  `unique_per_conduit_lineage` the lineage-root store and `unique_per_conduit_cluster` the elected leader's;\n"
        "  `unique_per_conduit` the (owner) conduit's store; `unique_per_spell_space` the space's; a disposal-bearing\n"
        "  `many` the innermost scope's (the space's through a SpellSpace door, else the conduit's) when it is the root\n"
        "  or a `many` root's child, and its holder's store when a shared site needs it (0.2.8235: a slotted holder's\n"
        "  `many` children belong to the holder's owner); a `many` without disposal methods is not stored. The old\n"
        "  text put cluster and lineage in `spell._owner_creations` and every per-conduit lifetime in \"caller creations\".\n",
        "  `unique_per_conduit_lineage` the lineage-root store and `unique_per_conduit_cluster` the cluster's team store\n"
        "  through the member root's facade (0.2.8237; the elected leader's own store before); `unique_per_conduit` the\n"
        "  (owner) conduit's store; `unique_per_spell_space` the space's; a disposal-bearing `many` the innermost\n"
        "  scope's (the space's through a SpellSpace door, else the conduit's) when it is the root or a `many` root's\n"
        "  child, and its holder's store when a shared site needs it (0.2.8235: a slotted holder's `many` children belong\n"
        "  to the holder's owner; 0.2.8238: recorded with the holder); a `many` without disposal methods is not stored.\n"
        "  The old text put cluster and lineage in `spell._owner_creations` and every per-conduit lifetime in \"caller\n"
        "  creations\".\n",
        "comp meld store selection",
    )
    text = replace_once(
        text,
        "  conduit's for `unique_per_conduit`, the space's for `unique_per_spell_space`, the lineage root's, the elected\n"
        "  leader's. So a slotted holder's `many` children are recorded with whatever owns the holder and disposed with\n"
        "  that store, never by a lesser's pool return, a spellspace exit or a borrowing root's teardown that happened to\n"
        "  meld the holder first (through 0.2.8234 they went to the innermost scope, whose end ran their disposal under a\n",
        "  conduit's for `unique_per_conduit`, the space's for `unique_per_spell_space`, the lineage root's, the\n"
        "  cluster's team store (0.2.8237; the elected leader's before). So a slotted holder's `many` children are\n"
        "  recorded with whatever owns the holder and disposed with that store, never by a lesser's pool return, a\n"
        "  spellspace exit or a borrowing root's teardown that happened to meld the holder first (through 0.2.8234 they\n"
        "  went to the innermost scope, whose end ran their disposal under a\n",
        "comp emission cluster",
    )
    text = insert_before_once(
        text,
        "- Holder-owned many children (2026-10-14, 0.2.8235): a disposal-bearing many step registers in the store that owns\n",
        COMP_ADOPTION,
        "comp adoption",
    )
    text = replace_once(
        text,
        "logging every other step error, and raises them after hooks, logger and field deletes. `enter_spellspace`\n"
        "pushes onto the owned thread stack inline. `Cleanable.using_cleanup()`, the dispose helper every Cleanable\n"
        "carries, now lets the cleanup error propagate instead of swallowing it.\n",
        "logging every other step error, and raises them after hooks, logger and field deletes. A root's teardown first\n"
        "leaves its cluster (`_leave_cluster_for_teardown`, 0.2.8236; Subcomponent: ConduitCluster Auto-Sharing).\n"
        "`enter_spellspace` pushes onto the owned thread stack inline. `Cleanable.using_cleanup()`, the dispose helper\n"
        "every Cleanable carries, now lets the cleanup error propagate instead of swallowing it.\n",
        "comp conduit teardown",
    )
    text = replace_once(
        text,
        "`Conduit.enter_spellspace` and\n`src/melder/utilities/general_base/cleanable.py:Cleanable._CleanupContext.__exit__`.\n",
        "`Conduit.enter_spellspace`, `Conduit._leave_cluster_for_teardown` and\n"
        "`src/melder/utilities/general_base/cleanable.py:Cleanable._CleanupContext.__exit__`.\n",
        "comp conduit teardown evidence",
    )
    text = insert_after_once(text, "## Context / Handoff Summary\n\n", COMP_HANDOFF, "comp handoff")
    for path in CHANGED:
        text = remeasure(text, path, "comp")
    return text


TESTS_PROTECTS = """- cluster lifetimes (0.2.8236-0.2.8237): a torn-down member or leader leaves its cluster (unelect and elect work,
  the cluster stays deletable, a failed transactional leave still drops it), an explicit leave unshares the leaver's
  roots from every member, the cluster's object survives a leader change and is disposed once by deletion or frame
  teardown, a failing disposal is raised after the deletion, and only the elected leader purges it
- holder records (0.2.8238): purging a holder disposes its `many` child after it (also for a holder without disposal
  methods, in a spellspace and by the owner of a `unique`), nothing accumulates over purge-and-meld cycles, a `many`
  purge of the child's spell leaves a live holder's child open, and an ownership move carries the child
- transfer default (0.2.8239): a default transfer keeps a `unique` as one object and moves a tracked `many` object;
  `move_creations=False` builds a new instance on the target
"""

TESTS_HANDOFF = """2026-10-14 slotted lifetimes (0.2.8236-0.2.8240): the Conduit Integration Cluster gains
`test_conduit_integration_cluster_member_lifetime.py` (eleven cluster-lifetime cases) and
`test_conduit_integration_holder_children_lifetime.py` (ten holder-record cases), and
`test_conduit_integration_transfer_ownership.py` pins the transfer default; the unit tier gains
`test_creations_holder_children.py` (thirteen record cases), and the cluster, cloud, facade, creations and site-plan
modules gained cases. Only the three integration code-map entries were measured.

"""


def tests(text: str) -> str:
    text = replace_once(
        text,
        "  holder first melded by a member keep their disposal-bearing `many` child open until the holder's owner ends\n"
        "Key Files (C1):\n",
        "  holder first melded by a member keep their disposal-bearing `many` child open until the holder's owner ends\n"
        + TESTS_PROTECTS + "Key Files (C1):\n",
        "tests protects",
    )
    text = replace_once(
        text,
        "- `tests/integration/melder/conduit/test_conduit_integration_many_child_disposed_with_its_holder.py` (2026-10-14)\n\n",
        "- `tests/integration/melder/conduit/test_conduit_integration_many_child_disposed_with_its_holder.py` (2026-10-14)\n"
        "- `tests/integration/melder/conduit/test_conduit_integration_cluster_member_lifetime.py` (2026-10-14)\n"
        "- `tests/integration/melder/conduit/test_conduit_integration_holder_children_lifetime.py` (2026-10-14)\n\n",
        "tests key files",
    )
    many_entry = re.search(
        r"- path: `tests/integration/melder/conduit/test_conduit_integration_many_child_disposed_with_its_holder\.py`\n"
        r"  start_line: 1\n  end_line: \d+\n  loc: \d+\n  verified_at: \S+\n", text)
    assert many_entry is not None
    added = ""
    for path in ("tests/integration/melder/conduit/test_conduit_integration_cluster_member_lifetime.py",
                 "tests/integration/melder/conduit/test_conduit_integration_holder_children_lifetime.py"):
        n = loc(path)
        added += f"- path: `{path}`\n  start_line: 1\n  end_line: {n}\n  loc: {n}\n  verified_at: {STAMP}\n"
    text = text[:many_entry.end()] + added + text[many_entry.end():]
    text = remeasure(text, "tests/integration/melder/conduit/test_conduit_integration_transfer_ownership.py", "tests")
    text = insert_after_once(text, "## Context / Handoff Summary\n\n", TESTS_HANDOFF, "tests handoff")
    return text


def non_ascii(text: str) -> int:
    """Count characters outside ASCII; the documents carry a few (box drawing, an en dash) and the landing adds none."""
    return sum(1 for ch in text if ord(ch) > 127)


DRY_RUN = len(sys.argv) > 2 and sys.argv[2] == "--dry-run"
landed = []
for name, fn in (("src_architecture.md", architecture), ("src_components.md", components), ("tests_components.md", tests)):
    path = DOCS / name
    raw = path.read_bytes().decode("utf-8")
    assert "\r\n" not in raw
    new = fn(raw)
    assert non_ascii(new) == non_ascii(raw), (name, non_ascii(raw), non_ascii(new))
    landed.append((path, raw, new))
for path, raw, new in landed:
    if not DRY_RUN:
        path.write_bytes(new.encode("utf-8"))
    print("dry-run" if DRY_RUN else "landed", path.name, len(raw.splitlines()), "->", len(new.splitlines()))
