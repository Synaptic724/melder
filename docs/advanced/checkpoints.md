# Create, seal, and read a checkpoint

Prerequisite: [configuration ownership](posture.md). These entry lessons introduce
recording without requiring the complete [Expert persistence guide](../expert/persistence.md).

Configure and activate Crystallizer before creating checkpoints. The creation
lesson gets a checkpoint ID, lists it, describes it, and confirms that another
checkpoint receives a different ID.

## Know which operation completed

| Operation | What you can conclude |
| --- | --- |
| `create_checkpoint(...)` | A checkpoint exists in the running record |
| `flush_checkpoint(...)` | The checkpoint is sealed locally; inspect remote delivery separately |
| `list_cached_checkpoint_ids()` | Which checkpoint IDs remain in the bounded local cache |
| `reload_cached_checkpoint(...)` | A cached record is read back into the record system |
| `verify_checkpoint_chain(...)` | A report about the recorded lineage |

A bounded cache can evict older entries. A successful local seal does not establish
remote durability. Reloading a record is also different from rebuilding its runtime
objects: use [restore and cold boot](../expert/restore.md) for that next step.
