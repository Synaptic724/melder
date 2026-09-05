# Troubleshooting by symptom

Start with the operation that refused and the boundary named by its error. Keep
the complete exception or report while diagnosing; an empty result, unavailable
surface, and denied operation can mean different things.

| Symptom | Check | Next step |
| --- | --- | --- |
| Import warns about Python or the GIL | The interpreter selected by your shell or environment | [Install and first run](../beginner/install.md) |
| A meld cannot find a named registration | Spellframe, binding name, and whether the target is a human name or explicit ID | [Address law](../beginner/addresses.md) |
| A second bind or conjure is refused | Existing registration and the one-root-per-book rule | [Errors](../beginner/errors.md) |
| Identical bindings collide across worlds | Process-wide spell identity; the frame is not part of that distinction | [World boundaries](../advanced/worlds.md) |
| Constructor configuration seems ignored | Bind parameters versus meld overrides or a configured factory | [Flat overrides](../intermediate/overrides.md) |
| Configuration edits fail | Defaults/set-once properties and whether conjure froze the object | [Configuration](../intermediate/configuration.md) |
| A child scope retains memory | The actual owner and whether its cleanup ran | [Scopes that end](../intermediate/scopes.md) |
| A linked borrower cannot resolve a spell | Both roots exist, the borrower pulled from the actual owner, and permissions fit | [Links and permissions](../intermediate/permissions.md) |
| A late-bound constructor still has a descriptor | Complete provider → consumer → link → pull → meld for each edge | [Connected systems](../intermediate/connected-subsystems.md) |
| A cluster reports no creations store | Linking, membership, and leader election order | [Clusters](../advanced/clusters.md) |
| An override is refused or affects later calls | Match count/path grammar and the target's lifetime | [Deep overrides](../advanced/overrides.md) |
| A Rift cannot attach to a frame | Observer policy, frame posture, descriptor publication, and target budget | [Agent room setup](../expert/agent-rooms.md) |
| Viewer fields seem missing | Selected frame and visible versus withheld sections | [Viewer reads](../advanced/viewers.md) |
| Codegen returns a rejected result | Validation issues, execution errors, and the explicit target frame | [Codegen](../expert/codegen.md) |
| Research appears unavailable | Root activation, custody setup, and the selected record/set | [Research](../expert/research.md) |
| A clean flush has no remote copy | Store wiring, failure counters, and remote delivery policy | [External storage](../expert/external-storage.md) |
| Restore refuses before building | Complete chain, source drift, collisions, and the admission report | [Restore](../expert/restore.md) |
| A research join refuses | Anchor, receiver tip, and whether a supersede is actually intended | [Governed change](../expert/governed-change.md) |

The [public error reference](api/errors.md) describes catchable exception types.
Use the [complete examples](../examples/index.md) to compare your setup with a
small runnable case before changing a larger application.
