# Connect storage through your callables

Prerequisite: [persistence](persistence.md). Melder calls your storage functions;
the example uses an in-memory dictionary so the complete integration can run
without a database service or credentials.

| Handler | Arguments | Responsibility |
| --- | --- | --- |
| Store | kind, profile name, unit ID, payload | Store a plain record |
| Fetch | kind, unit ID | Return the stored payload or a known absence |
| List | kind, profile name | Enumerate unit IDs for the requested partition |
| Delete | kind, unit ID | Remove the explicitly identified stored unit |

Configure the needed handlers on `ExternalPersistenceManagerConfiguration`, then
attach it through Crystallizer. Inspect `describe_external_persistence_manager()`
for the installed wiring and failure counts; `describe_external_interface()`
describes the integration contract.

## Verify the remote leg separately

A successful local flush does not establish remote delivery under the default
lenient write policy. The failure lesson deliberately raises in a store handler,
checks the local cache, and checks the increased failure count. Missing read lanes
refuse rather than report an empty remote record.

The JSON lesson also shows the serialized payload crossing a callable boundary.
For record round trips, use strict JSON serialization so unsupported values fail
instead of being silently converted into lossy strings.
