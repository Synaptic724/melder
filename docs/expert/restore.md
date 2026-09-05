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

## Follow both demonstrations

Expert 24 walks the checkpoint verbs while holding the existing world. Expert 27
flushes, tears down the root, creates a new runtime, and reads the cache again.
The latter deliberately reports an admission refusal if the bundle is incomplete.
A script finishing successfully therefore does not, on its own, prove a complete
world was restored. Read the reported status, built resources, and shortfalls.

`CrystallizerBootstrap` packages the restart sequence into a one-shot operation:
activate, attach configured storage, reload, verify, load, report. Its empty-history
case differs from a broken chain. Use the pod-boot lesson for its complete setup.
