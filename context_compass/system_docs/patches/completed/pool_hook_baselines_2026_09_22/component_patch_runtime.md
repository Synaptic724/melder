# Runtime hook baseline owners

## Conduit
Normal construction copies configuration containers once. Lessers borrow root-owned maps, including
the shared empty maps. Local lifecycle overlays remain separate. Registration/set validate and split
families before mutation, with existing Conduit lock before Meld mutation lock. Only a normal root may
publish shared updates. A public read reports whether local lifecycle/Meld state differs.

Lesser cleanup resets changed Meld hooks after disposing its Spaces and creations, then publishes the
shell back to ConduitPool. Stable shared maps mean unchanged lesser acquisition needs no refresh scan.

## Meld
Own an effective-map reference, a baseline-map reference and one divergence bool. Constructor starts
on its supplied baseline. Local mutation creates copied containers on the rare path. Shared updates
preserve the root baseline dictionary and replace event lists under the existing writer lock. Pool
reset takes that lock only after the bool reports divergence, then restores the baseline reference.
Cleanup deletes all three hook-state fields without disposing callbacks or clearing borrowed maps.

## SpellSpace / SpellSpacePool
Construction captures the owner's baseline and current effective map; identity difference sets the
divergence bool. Both acquire routes check the owner's divergence bool and adopt its temporary map
only when needed. Both return routes dispose/reset creations first, then restore changed hooks before
pool release. This drops temporary callback references from idle Spaces in a recycled lesser's pool.
Conduit.prewarm_spellspaces applies the same restoration before directly publishing its idle shells.
Permanent Space destruction explicitly cleans its owned Meld before dropping that reference.

## Graduation integration
Book-owned existing-conduit conjure uses the same root baseline initialization rule, then binds both
baseline and effective pointers on retained Conduit/Space Meld runtimes. The completed independent
Book/configuration contract remains unchanged.

## Validation
Qualify empty/populated root updates, add/set/clear/re-add, local isolation, invalid mixed batches,
manual/managed/prewarmed Space leases, inherited local maps, sibling/other-root isolation, retained
callback release, graduation followed by reuse, and unchanged warm hook dispatch. Benchmark unchanged
pool cycles before/after; no numerical speed promise without measurements.
