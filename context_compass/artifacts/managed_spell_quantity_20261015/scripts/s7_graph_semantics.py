"""S7: author the graph semantics of the managed lane (EPIC-2026-10-14-managed_spell_quantity).

Run from the repository root: python s7_graph_semantics.py [--dry-run]

- The five new modules: module and class nodes authored from the modules read whole on 0.2.8246.
- The 22 nodes this lane's diff moved (AUTHORED against 0.2.8240): the lane's facts appended, read from every changed
  hunk of their spans (runs/s7_graph_prose_by_lane.txt); accepted afterwards with graph_walker --accept.
- The 8 nodes in this lane's files that were already stale at 0.2.8240: the lane's facts appended
  (runs/s7_graph_prose_pre_lane.txt); NOT accepted - their older claims were never verified.
Every edit asserts the state it expects, so a second run refuses instead of duplicating. Writes descriptors the way the
extractor does (indent=1, LF); the walker's --accept and the next extraction rewrite them anyway.
"""
import json
import pathlib
import sys

GRAPH = pathlib.Path("context_compass/system_docs/graph")
DRY = "--dry-run" in sys.argv

SPELL = "melder.aether.spellbook.spell.Spell"
SPELL_INDEX = "melder.aether.spellbook.bind.spell_index.SpellIndex"
CONDUIT = "melder.aether.conduit.conduit.Conduit"
CREATIONS = "melder.aether.conduit.creations.creations.Creations"
POOL_MOD = "melder.aether.conduit.creations.managed_spell_quantity"
POOL = POOL_MOD + ".ManagedSpellQuantity"
REG_MOD = "melder.aether.conduit.creations.release_managed_spell"
REG = REG_MOD + ".ReleaseManagedSpell"
LEASE_MOD = "melder.aether.conduit.creations.managed_spell_lease"
LEASE = LEASE_MOD + ".ManagedSpellLease"
MODE_MOD = "melder.aether.spellbook.existence.managed_spell_mode"
MODE = MODE_MOD + ".ManagedSpellMode"
ERR_MOD = "melder.utilities.custom_exceptions.managed_spell_exhausted_error"
ERR = ERR_MOD + ".ManagedSpellExhaustedError"


def edge(src, dst, relation, why, cardinality, phase, strength):
    return {"from": src, "to": dst, "relation": relation, "why": why, "cardinality": cardinality,
            "phase": phase, "strength": strength}


NEW_NODES = {
    POOL_MOD: {
        "include": True,
        "role": "Module holding ManagedSpellQuantity, the pool of one managed spell version in its owner root's store.",
        "responsibilities": [
            "exports ManagedSpellQuantity to Creations (which composes and holds the pools), ReleaseManagedSpell, "
            "ManagedSpellLease and the emitted plans' managed sites"],
        "phases": ["runtime", "cleanup"],
    },
    POOL: {
        "include": True,
        "role": "The pool of one Existence.managed_spell_quantity version in its owner root's Creations: idle objects "
                "for reuse, a count of the objects alive, and the version's mode applied when a lease misses.",
        "responsibilities": [
            "keeps the idle objects in the base pool's _idle deque (newest last); the emitted plan leases with an "
            "inline _idle.pop() and only an empty pool calls reserve() - the pool never builds (create_object and "
            "acquire refuse)",
            "reserve(): elastic counts a place and records pressure (_note_miss); limited_quantity counts a place "
            "below its limit, else serves an object released since the plan's pop, else raises "
            "ManagedSpellExhaustedError; queue waits on its condition for a place or a released object until a "
            "deadline taken once at the call, then raises it; a torn-down pool raises RuntimeError",
            "put_back(obj): runs the reset names in order outside every lock; a raising reset destroys the object and "
            "propagates (one ExceptionGroup when its disposal fails too); otherwise appends the object, wakes one queue "
            "waiter and, above baseline_idle, runs the base pool's elastic band (stretch, timed decay, trim of the "
            "oldest idle objects destroyed outside the lock)",
            "is sized by mode: elastic keeps baseline min(20, limit) and at most limit idle with the kernel pools' "
            "retention defaults; limited_quantity and queue are fixed at their limit, so count never exceeds it and "
            "nothing is evicted",
            "keeps no reference to an object that is out (identity is not tracked): only id(obj) keys the record of "
            "the disposal-bearing many children adopt() records for it, and a record whose id was reused moves to "
            "the orphaned records",
            "abandon(children, error): a failed build gives its place back, wakes one waiter and disposes the "
            "children it built, each failure added as a note on the build's error",
            "destroy_object: the Spell's disposal methods, then the object's recorded children newest first, count "
            "down by one and one waiter woken; disposal never runs on a plain release",
            "cleanup(): under the lock drains the idle objects, swaps the children maps for empty ones, deletes the "
            "borrowed Spell and wakes every waiter; outside it disposes the idle objects with their children, then "
            "the children of objects still out, then the orphans, failures as one ExceptionGroup; other fields stay "
            "as tombstones",
            "describe(): the base retention keys without in_use_count, plus identity, policy, count, out_count and "
            "children_recorded"],
        "owns_state": ["_count", "_condition", "_children_by_object", "_orphaned_children", "_managed_class",
                       "_mode", "_limit", "_timeout_seconds", "_reset_method_names", "_notify_on_return",
                       "_spell (borrowed)", "_disposal_method_names (borrowed)"],
        "phases": ["init", "runtime", "cleanup"],
    },
    REG_MOD: {
        "include": True,
        "role": "Module holding ReleaseManagedSpell, the Aether-owned registry managed objects are given back through.",
        "responsibilities": [
            "exports ReleaseManagedSpell; Aether builds the instance at boot and ReleaseManagedSpell() returns it"],
        "phases": ["init", "runtime", "cleanup"],
    },
    REG: {
        "include": True,
        "role": "Process singleton Aether builds last and owns: the class-keyed registry of the managed pools live root "
                "stores hold, through which a managed object is given back to its pool.",
        "responsibilities": [
            "has the hosted roots' singleton shape: a double-checked __new__ under a class lock, a once-only "
            "__init__(*, aether=...) that refuses a first construction without its host and resets the bookkeeping, "
            "cleanup(), _reset_singleton_for_tests() and _live_instance() (the stores' teardown lookup; never "
            "constructs)",
            "keeps two copy-on-write maps republished whole under a leaf lock held only to publish: _pools_by_class "
            "(class -> tuple of pools, read lock-free by release) and _registrations (id(pool) -> class and holding "
            "root id)",
            "register / unregister are called by Creations only, outside the store lock, as a store takes (ensure, "
            "restore) or gives up (extract, discard, cleanup) a pool; register is idempotent, moves a pool's root on "
            "a restore and re-keys a rebind's new class object; unregister does nothing once cleaned",
            "release(obj): one dict get by type(obj) and the pool's put_back when exactly one pool matches and no "
            "filter is given; otherwise the cold resolver keeps the pools of spell_id and of the conduit's root (a "
            "lesser names its root), prefers the version its index selects and raises a ValueError naming every "
            "candidate unless exactly one remains",
            "managed(obj) resolves the pool the same way and returns a ManagedSpellLease; release_all releases every "
            "object and raises the failures as one ExceptionGroup; describe(cls) returns each pool's snapshot plus "
            "holding_conduit_id and active_version",
            "borrows the pools and never cleans or disposes one; trusts every release (identity is not tracked); a "
            "release needs neither a conduit nor Aether",
            "cleanup() publishes empty maps as tombstones, keeps _lock and resets the singleton bookkeeping; release, "
            "managed, release_all, describe and register then raise the cleaned RuntimeError"],
        "owns_state": ["_pools_by_class", "_registrations", "_lock"],
        "phases": ["init", "runtime", "cleanup"],
    },
    LEASE_MOD: {
        "include": True,
        "role": "Module holding ManagedSpellLease, one leased managed object and its way back.",
        "responsibilities": [
            "exports ManagedSpellLease and the ManagedObjectT type variable that ReleaseManagedSpell.managed and "
            "Conduit.managed_spell_meld are typed with"],
        "phases": ["runtime"],
    },
    LEASE: {
        "include": True,
        "role": "One object leased from a managed spell's pool, paired with that pool so it is given back exactly once.",
        "responsibilities": [
            "holds the leased object and its pool, both borrowed; created by ReleaseManagedSpell.managed and "
            "Conduit.managed_spell_meld",
            "release() gives the object back once (pool.put_back: the resets, then idle for the next lease) and drops "
            "both references; later calls do nothing, and the lease counts as released even when the put-back "
            "raised, so nothing goes back twice",
            "object answers the leased object until the lease is released, then raises RuntimeError; `with lease as "
            "obj:` binds it and the exit releases it whether or not the block raised, never suppressing",
            "a class, not a generator (a generator context manager measured about 600 ns more per use); one lease is "
            "not thread-safe, different leases are independent"],
        "owns_state": ["_released", "_object (borrowed)", "_pool (borrowed)"],
        "phases": ["runtime"],
    },
    MODE_MOD: {
        "include": True,
        "role": "Module holding the ManagedSpellMode enum a managed binding chooses its pool policy from.",
        "responsibilities": [
            "exports ManagedSpellMode to Bind, Spell, the pool, SpellBinder, scan_bind and the package root"],
        "phases": ["init", "runtime"],
    },
    MODE: {
        "include": True,
        "role": "Pool policy of a managed spell, chosen at bind with managed_spell_mode: what a lease does when no idle "
                "object is waiting.",
        "responsibilities": [
            "elastic: a miss always builds; managed_spell_limit is the most idle objects kept (default 256), trimmed "
            "like the kernel pools' idle objects; never refuses",
            "limited_quantity: managed_spell_limit (required) is the most objects alive at once, idle plus out; a miss "
            "at the limit refuses before building anything",
            "queue: like limited_quantity, but a miss at the limit waits up to managed_spell_timeout_seconds "
            "(required) for a release, which serves the waiter, and refuses at the deadline",
            "identity data: with the limit, the timeout and the reset names it is hashed into a managed spell's id, "
            "recorded by name in its crystal and replayed by restore and graft; __str__ returns the bare name"],
        "owns_state": ["elastic", "limited_quantity", "queue"],
        "phases": ["init", "runtime"],
    },
    ERR_MOD: {
        "include": True,
        "role": "Module holding ManagedSpellExhaustedError, the refusal of a managed pool with no place.",
        "responsibilities": [
            "exports the error; it imports only MeldExecutionError, so the pool depends on it and not the reverse"],
        "phases": ["runtime"],
    },
    ERR: {
        "include": True,
        "role": "MeldExecutionError raised at meld when a managed pool has no place: limited_quantity with every "
                "object out, or queue after its timeout.",
        "responsibilities": [
            "built only through limited(...) and queue(...), which own the message texts: the spell, the mode, the "
            "limit (and the queue timeout printed with :g) and the remedies - release an object through "
            "ReleaseManagedSpell, or bind a higher managed_spell_limit or managed_spell_timeout_seconds",
            "raised by ManagedSpellQuantity.reserve before anything is built, the pool's count unchanged; elastic "
            "pools never raise it",
            "keeps every MeldExecutionError field (spell_id and spell_name set; node_id, param_name and inner None), "
            "so a handler of MeldExecutionError keeps catching it; exported at the package root"],
        "owns_state": ["mode", "limit", "timeout_seconds"],
        "phases": ["runtime"],
    },
}

NEW_EDGES = [
    edge(POOL, SPELL, "borrows",
         "The pool reads the managed options and the disposal list from its version's Spell at construction and keeps "
         "the Spell borrowed (a rebind under the same id re-points it); it never cleans it.",
         "many_to_one", ["init", "runtime"], "borrowed"),
    edge(POOL, MODE, "uses",
         "The mode decides what a miss does - build, refuse or wait - and how the pool is sized.",
         "many_to_one", ["init", "runtime"], "borrowed"),
    edge(POOL, ERR, "creates",
         "reserve() raises ManagedSpellExhaustedError.limited or .queue when its mode refuses a lease; nothing has "
         "been built by then.",
         "one_to_many", ["runtime"], "hard"),
    edge(REG, POOL, "borrows",
         "The registry holds every live pool under its managed class and calls its put_back; the pools belong to "
         "their root stores, and the registry never cleans one.",
         "one_to_many", ["runtime"], "borrowed"),
    edge(REG, LEASE, "creates",
         "managed(obj) wraps the object and the pool it resolved in a lease.",
         "one_to_many", ["runtime"], "hard"),
    edge(REG, SPELL_INDEX, "uses",
         "The cold resolver prefers the pool whose version its index selects, read through the cleanup-safe "
         "_is_selected_unless_cleaned.",
         "many_to_one", ["runtime"], "borrowed"),
    edge(REG, CONDUIT, "uses",
         "A conduit filter names its root (_root_conduit_id); the registry keeps no conduit.",
         "many_to_one", ["runtime"], "borrowed"),
    edge(LEASE, POOL, "borrows",
         "The lease gives its object back through the pool's put_back exactly once, then drops both references.",
         "many_to_one", ["runtime"], "borrowed"),
]

# Lane-moved (AUTHORED against 0.2.8240) and pre-stale nodes: appended responsibilities, owns_state, edges, edits.
APPEND = {
    "melder.aether.aether.Aether": [
        "hosts ReleaseManagedSpell, the class-keyed registry of managed pools: builds it last at boot "
        "(ReleaseManagedSpell(aether=self), after Nexus) and cleans it right after the frames, whose root stores "
        "unregister their pools as they are torn down (0.2.8244)"],
    "melder.aether.spellbook.bind.bind.Bind": [
        "validates and normalizes a managed binding's four options once (_normalize_managed_options: classes only, the "
        "mode defaulting to elastic, the limit, the queue-only timeout and callable reset names; every refusal before "
        "a Spell or index exists), appends one managed:<mode>:<limit>:<timeout>:<reset names> part to a managed "
        "binding's fingerprint only, so no other spell id moves, and hands the normalized values to the Spell "
        "(0.2.8242)"],
    "melder.aether.spellbook.bind.scan.Scan": [
        "replays each declaration's four managed options into Spellbook.bind with its other target options "
        "(0.2.8242)"],
    "melder.aether.spellbook.bind.scan.ScanBindMetadata": [
        "carries the four managed options as declared (the reset group as a tuple) and replays them unchanged; Bind "
        "validates them when the module is scanned, and their names are reserved metadata keys (0.2.8242)"],
    "melder.aether.spellbook.bind.spell_index.SpellIndex": [
        "answers whether it selects a version without ever raising (_is_selected_unless_cleaned, under its lock; "
        "False once cleaned) for ReleaseManagedSpell's cold resolver (0.2.8244)"],
    "melder.aether.spellbook.existence.existence.Existence": [
        "managed_spell_quantity (0.2.8241): objects leased from a pool the owning root keeps per version and released "
        "back explicitly - the only member whose objects come back to Melder, and only when their holder releases "
        "them"],
    "melder.aether.spellbook.resolution_style_matrix.ResolutionStyleMatrix": [
        "counts seven existences; managed_spell_quantity is supported by the class-based family only - the callable "
        "and existing-object families list it unsupported (0.2.8241)"],
    "melder.aether.spellbook.spell.Spell": [
        "retains a managed binding's normalized options read-only per version (managed_spell_mode, limit, timeout, "
        "reset methods; None, None, None and () on other existences) and, when an owner stamp carries a store, ensures "
        "the version's pool there (_add_owned_conduit -> Creations.ensure_managed_quantity, 0.2.8242-0.2.8243)"],
    "melder.aether.spellbook.spell_compiler.artifact_processor.spell_artifact_processor.SpellArtifactProcessor": [
        "maps each spell's existence to its door route family and raises for an unknown member; "
        "managed_spell_quantity maps to \"managed\" (0.2.8241)"],
    "melder.aether.spellbook.spell_compiler.artifact_processor.strategies.spell_occurrence_instance_processor_strategy"
    ".SpellOccurrenceInstanceProcessorStrategy": [
        "treats many and managed_spell_quantity as per path (_is_shared_existence False): each occurrence keeps its "
        "own instance key, so every injection of a managed spell is its own lease (0.2.8245)"],
    "melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.site_plan_lowering.SitePlanLowering": [
        "lowers a managed_spell_quantity step as a per-path site leased from its pool, leasing or fresh (see "
        "SitePlanEmission); the warm lease takes no lock and the miss only the pool's leaf lock (0.2.8245)"],
    "melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.site_plan_lowering"
    ".SitePlanRuntimeHelpers": [
        "return_leases(error, leases): puts back every lease a plan took for a holder that was never built, each "
        "failing put-back added as a note on the propagating error (0.2.8245)",
        "return_unused_leases(leases): puts back the leases of a shared holder whose cold race another meld won, every "
        "pair attempted, failures raised as one ExceptionGroup (0.2.8245)",
        "raise_missing_managed_pool(spell): the named MeldExecutionError of a managed site whose pool cannot be read "
        "- its owner root torn down, or a version staged before conjure (0.2.8245)"],
    "melder.aether.spellbook.spell_compiler.spell_analyzer.strategies.spell_occurrence_graph_analyzer_strategy"
    ".SpellOccurrenceGraphAnalyzerStrategy": [
        "treats many and managed_spell_quantity as per path when collapsing shared occurrences (_is_shared_existence "
        "False), so each injection of a managed spell is its own occurrence (0.2.8245)"],
    "melder.aether.spellbook.spell_compiler.system.validation.scope_ordering_strategy.ScopeOrderingStrategy": [
        "ranks managed_spell_quantity 0 with unique: a managed spell may depend on unique, managed and many spells, and "
        "any holder may depend on it (0.2.8241)"],
    "melder.aether.spellbook.spellbook.Spellbook": [
        "forwards a managed binding's four options through bind and bind_inactive to Bind, where they are validated "
        "and become part of the spell id; a parked managed version keeps its own (0.2.8242)"],
    "melder.crystallizer.crystal_loader_system.graft_runner.GraftRunner": [
        "replays a managed member's recorded options (record 4.2.0, SpellCrystal.managed_bind_options) at the "
        "selected, parked and merged bind sites (0.2.8242)"],
    "melder.crystallizer.crystal_loader_system.restore_engine.RestoreEngine": [
        "replays a managed spell's recorded options through the active and staged binds (record 4.2.0, "
        "SpellCrystal.managed_bind_options), so it rebinds with its own options and spell id (0.2.8242)"],
    "melder.crystallizer.crystals.spell_crystal.SpellCrystal": [
        "records a managed spell's options as plain values - the mode by name, the limit, the queue timeout and the "
        "reset names - only for managed_spell_quantity, so every other payload is unchanged (record 4.2.0, "
        "0.2.8242); managed_spell_options returns them, and the static managed_bind_options(payload) is the one "
        "reader the restore and graft lanes replay them through"],
    "melder.crystallizer.persistence.record_version.RecordVersion": [
        "uses minor 4.2.0 for a managed spell's recorded options on its spell crystal (0.2.8242); 4.1 readers ignore "
        "them and a 4.1 record holds none"],
    "melder.nexus.rift.command_system.static_command_system.StaticCommandSystem": [
        "treats many, unique_per_spell_space and managed_spell_quantity spells as having no single stored object to "
        "hand out - a managed spell's objects are leased from a pool (0.2.8243)"],
    "melder.nexus.rift.frame_viewer.static_frame_viewer.StaticFrameViewer": [
        "reports a many, unique_per_spell_space or managed_spell_quantity spell as never live statically - a managed "
        "spell's objects are leased from a pool (0.2.8243)"],
    # Already stale at 0.2.8240: the lane's facts only; not accepted.
    "melder.aether.conduit.conduit.Conduit": [
        "forwards a managed binding's four options through both binding facades unchanged (0.2.8242)",
        "leases a managed spell through managed_spell_meld (0.2.8245): resolves the target as meld does, refuses "
        "another existence and a version with no pool before melding, melds the version by id and returns "
        "ManagedSpellLease(object, pool)"],
    "melder.aether.conduit.conduit_ward.transfer.transfer_of_ownership.TransferOfOwnership": [
        "makes the owner stamp follow the lineage both ways (0.2.8246): the flip and _migrate_inactive_members stamp "
        "every member that carries a stamp onto the target through _restamp, which registers the stamp-back to the "
        "source first and, for a managed version whose pool the target store did not hold, the discard of the pool "
        "its stamp composed (_discard_composed_pool); a managed version's pool moves as a store row with its idle "
        "objects and count"],
    "melder.aether.conduit.creations.creations.Creations": [
        "keeps one ManagedSpellQuantity per managed version a root store owns in _managed_quantities, a map of its "
        "own, so lookups, live probes and purge never meet a pool: ensure_managed_quantity composes it at an owner "
        "stamp (idempotent; a rebind re-points it), get_managed_quantity is a lock-free read, "
        "discard_managed_quantity gives up an identity-checked pool without cleaning it (0.2.8243-0.2.8246)",
        "cleans its pools first at cleanup, newest first, before the disposable registry - a pool is composed at "
        "conjure, before the uniques its objects hold - their failures joining the store's group; extract/restore "
        "carry a pool as a managed row, a restore cleaning the pool it replaced after the lock; purge returns 0 for "
        "a managed spell (0.2.8243)",
        "registers every pool it takes and unregisters every pool it gives up with ReleaseManagedSpell, outside the "
        "store lock, so the registry holds exactly the pools live stores hold (0.2.8244)"],
    "melder.aether.conduit.meld.conduit_meld.ConduitMeld": [
        "routes a managed spell's purge to the caller's own store, where Creations.purge returns 0, and answers its "
        "live-creation probe from the owner store's pool (0.2.8243)"],
    "melder.aether.conduit.meld.meld.Meld": [
        "answers the live-creation probe of a managed spell for both doors from its owner store's pool "
        "(_describe_managed_pool_status: live while the count is above 0, creation_count the count, storage scope "
        "managed_pool; 0 without a store or a pool) (0.2.8243)"],
    "melder.aether.conduit.meld.spellspace_meld.SpellSpaceMeld": [
        "answers a managed spell's live-creation probe from the owner root's pool, as the conduit door does - a "
        "managed object is never space-local (0.2.8243)"],
    "melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.site_plan_lowering.SitePlanEmission": [
        "emits managed sites (0.2.8245): a leasing site (no winning key on its own parameters) has its own miss and "
        "exactly one consumer, and its lease - an inline pop of a plan-constant pool on an automatic owner, else a "
        "per-creation pool read whose miss raises the named missing-pool error - is emitted in its consumer's lease "
        "group; the miss checks unresolved inputs, reserves, builds the children and the object inside a try whose "
        "handler abandons, then adopts the disposal-bearing many children; a fresh site (a winning key on its own "
        "parameters) is built like a many step and never pooled",
        "puts every lease of a consumer back when its construction region raises (_return_leases) and returns a lost "
        "cold race's unused leases (_return_unused_leases); a plan without a managed step is byte-identical and binds "
        "none of the three helpers (0.2.8245)"],
    "melder.aether.spellbook.spellbinder.SpellBinder": [
        "stages a managed binding through as_managed_spell_quantity(mode, limit=, timeout_seconds=, reset_methods=): "
        "sets the existence and the four options in the passthrough payload finalize sends to Spellbook.bind "
        "(0.2.8242)"],
}

OWNS_STATE = {
    "melder.aether.spellbook.existence.existence.Existence": ["managed_spell_quantity"],
    "melder.aether.spellbook.spell.Spell": ["_managed_spell_mode", "_managed_spell_limit",
                                            "_managed_spell_timeout_seconds", "_managed_spell_reset_methods"],
    "melder.crystallizer.crystals.spell_crystal.SpellCrystal": [
        "_managed_spell_mode_name, _managed_spell_limit, _managed_spell_timeout_seconds, _managed_spell_reset_methods "
        "(recorded managed options)"],
    "melder.aether.conduit.creations.creations.Creations": ["_managed_quantities"],
    "melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.site_plan_lowering.SitePlanEmission": [
        "_leasing", "_fresh", "_has_miss", "_leases_by_consumer"],
}

ROLE_EDITS = {
    "melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.site_plan_lowering"
    ".SitePlanRuntimeHelpers": (
        "Cold-path helpers emitted plans call: generic construction with supplied values and the plans' refusals.",
        "Cold-path helpers emitted plans call: generic construction with supplied values, the plans' refusals and the "
        "managed lease returns."),
    "melder.crystallizer.persistence.record_version.RecordVersion": (
        "Static record-schema version authority (stamp 4.1.0; readers gate on MAJOR; absent stamps read 0.0.0).",
        "Static record-schema version authority (stamp 4.2.0; readers gate on MAJOR; absent stamps read 0.0.0)."),
}

RESPONSIBILITY_EDITS = {
    "melder.aether.spellbook.spell_compiler.codegen_planner.codegen_plan_discovery_system.strategies"
    ".solo_codegen_plan_discovery_strategy.SoloCodegenPlanDiscoveryStrategy": (
        "claims models whose visible spell count is exactly one",
        "claims models whose visible spell count is exactly one and that hold no managed_spell_quantity spell - a "
        "managed object is leased through the generalized family's site plan (0.2.8245)"),
}

LANE_EDGES = [
    edge("melder.aether.aether.Aether", REG, "owns_lifecycle_of",
         "Aether builds the release registry last at boot and cleans it right after its frames; "
         "ReleaseManagedSpell() returns the instance it hosts.",
         "one_to_one", ["init", "runtime", "cleanup"], "hard"),
    edge("melder.aether.spellbook.bind.bind.Bind", MODE, "uses",
         "Bind normalizes a managed binding's mode to a ManagedSpellMode member before hashing it into the spell id.",
         "many_to_one", ["runtime"], "borrowed"),
    edge(SPELL, CREATIONS, "uses",
         "An owner stamp of a managed version ensures the version's pool in the stamped store "
         "(ensure_managed_quantity).",
         "many_to_one", ["runtime"], "borrowed"),
    edge("melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.site_plan_lowering"
         ".SitePlanRuntimeHelpers", POOL, "uses",
         "The lease returns put leased objects back through the pool's put_back.",
         "many_to_one", ["runtime"], "borrowed"),
    edge(CONDUIT, LEASE, "creates",
         "managed_spell_meld melds a managed version and returns its object as a lease over the version's pool.",
         "one_to_many", ["runtime"], "hard"),
    edge(CREATIONS, POOL, "owns_lifecycle_of",
         "A root store composes one pool per managed version it owns (ensure_managed_quantity), cleans its pools "
         "first at teardown, and gives a pool up only through extract (an ownership move) or discard (a transfer's "
         "rollback).",
         "one_to_many", ["init", "runtime", "cleanup"], "hard"),
    edge(CREATIONS, REG, "uses",
         "The store registers each pool it takes and unregisters each pool it gives up, outside its lock.",
         "many_to_one", ["runtime", "cleanup"], "borrowed"),
    edge("melder.aether.conduit.conduit_ward.transfer.transfer_of_ownership.TransferOfOwnership", CREATIONS, "uses",
         "A failed transfer's rollback takes back the empty pool its stamp composed in the target store "
         "(discard_managed_quantity) and cleans it.",
         "many_to_one", ["runtime"], "borrowed"),
    edge("melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.site_plan_lowering"
         ".SitePlanEmission", POOL, "uses",
         "An automatic owner's leasing site binds the pool and its _idle.pop as plan constants.",
         "many_to_one", ["runtime"], "borrowed"),
]


def descriptor_path(node_id: str) -> pathlib.Path:
    parts = node_id.split(".")
    # A class node id ends with its class name; a module node id is the module itself.
    for cut in (len(parts), len(parts) - 1):
        candidate = GRAPH.joinpath(*parts[:cut]).with_suffix(".json")
        if candidate.is_file():
            data = json.loads(candidate.read_text(encoding="utf-8"))
            if node_id in data.get("nodes", {}):
                return candidate
    raise SystemExit(f"no descriptor holds {node_id}")


def main() -> None:
    loaded = {}

    def load(path):
        if path not in loaded:
            loaded[path] = json.loads(path.read_text(encoding="utf-8"))
        return loaded[path]

    changes = 0
    for nid, fields in NEW_NODES.items():
        node = load(descriptor_path(nid))["nodes"][nid]
        assert not any(k in node for k in ("include", "role", "responsibilities", "owns_state", "phases")), nid
        node.update(fields)
        changes += 1
    for nid, items in APPEND.items():
        node = load(descriptor_path(nid))["nodes"][nid]
        resp = node.setdefault("responsibilities", [])
        for item in items:
            assert item not in resp, (nid, item[:40])
            resp.append(item)
            changes += 1
    for nid, items in OWNS_STATE.items():
        node = load(descriptor_path(nid))["nodes"][nid]
        owned = node.setdefault("owns_state", [])
        for item in items:
            assert item not in owned, (nid, item)
            owned.append(item)
            changes += 1
    for nid, (old, new) in ROLE_EDITS.items():
        node = load(descriptor_path(nid))["nodes"][nid]
        assert node.get("role") == old, (nid, node.get("role"))
        node["role"] = new
        changes += 1
    for nid, (old, new) in RESPONSIBILITY_EDITS.items():
        node = load(descriptor_path(nid))["nodes"][nid]
        resp = node["responsibilities"]
        assert resp.count(old) == 1, (nid, resp)
        resp[resp.index(old)] = new
        changes += 1
    for e in NEW_EDGES + LANE_EDGES:
        d = load(descriptor_path(e["from"]))
        authored = d.setdefault("edges_authored", [])
        assert not any(x.get("from") == e["from"] and x.get("to") == e["to"] and x.get("relation") == e["relation"]
                       for x in authored), (e["from"], e["to"])
        authored.append(e)
        changes += 1
    for path, data in loaded.items():
        if not DRY:
            path.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"{'DRY RUN: ' if DRY else ''}{changes} edits in {len(loaded)} descriptors")
    for path in sorted(loaded):
        print("  ", path)


if __name__ == "__main__":
    main()
