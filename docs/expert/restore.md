# Restore and cold boot

Prerequisite: [persistence and custody](persistence.md). Keep the record operations
separate from rebuilding a runtime:

1. `create_checkpoint` records the checkpoint in the in-process ledger.
2. `flush_checkpoint` seals it to the local cache.
3. `reload_cached_checkpoint` brings cached record data back into the ledger.
4. `load_checkpoint` attempts to rebuild the selected world through its public operations.

## Inspect the report

A restore report carries status, built counts, shortfalls, and identity translation.
Runtime identities are rebuilt; the translation information connects recorded and
new identities. The separate research-record JSON lesson preserves the identity
of the record it hydrates. Those are different contracts.

Preflight can refuse an incomplete chain before construction. Preserve the full
required profile chain when preparing a cold start; reloading a single checkpoint
does not imply every predecessor has been reloaded.

## Restore named lesser structure

Run [Named scopes in Nexus and restore](../examples/expert/38-named-scopes-in-nexus-and-restore.md)
for a successful replay with assertions. It records a named job beneath an unnamed
parent, tears down the live roots and restores from the retained in-memory checkpoint.
This is different from a process restart, which also needs the flush/reload steps above.

Dynamic named scopes carry their name, parent and root relationships. Required
unnamed ancestry is saved as supporting values inside named records. Restoring
rebuilds one shared Book/root and its children in parent order with fresh IDs;
unnamed support stays outside Cloud discovery. Scope names do not restore the
mutable contents of previously created objects. A later `meld` creates fresh state.

Released names disappear from later checkpoints while earlier sealed checkpoints
retain their earlier structure. Formations rooted at a named lesser include its
required ancestry and selected subtree. Record schema **3.0.0** makes older
root-only readers refuse safely; valid older root-only records remain readable.

Quiesce ordinary lesser/SpellSpace creation, cleanup and lineage changes during
live restore. Transaction load authority does not drain those pool cycles.

## Follow both demonstrations

Expert 24 keeps the recorder alive and retires the original root before rebuilding it. Expert 27
flushes, tears down the root, creates a new runtime, and reads the cache again.
The latter deliberately reports an admission refusal if the bundle is incomplete.
A script finishing successfully therefore does not, on its own, prove a complete
world was restored. Read the reported status, built resources, and shortfalls.

`CrystallizerBootstrap` packages the restart sequence into a one-shot operation:
activate, attach configured storage, reload, verify, load, report. Its empty-history
case differs from a broken chain. Use the pod-boot lesson for its complete setup.
