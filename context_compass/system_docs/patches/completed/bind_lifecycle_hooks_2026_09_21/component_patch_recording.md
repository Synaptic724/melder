# Bind hook recording component patch

## Before
SpellbookConfiguration.freeze emits SpellbookCrystal only with origin identity, dynamic posture and
an active recorder. It enumerates conduit/meld hook names. The crystal and all downstream readers
already accept arbitrary string markers and report missing hook code honestly on full restore.

## After
Add optional value-only origin_bind_hook_names to freeze and its private emitter, defaulting empty.
Book passes current Bind marker names at origin freeze/re-freeze. Live registration changes after
conjure refresh the whole Book twin through the same emitter, retaining existing configuration and
conduit/meld names. Bind storage does not move into configuration; books remain isolated.

Stages are represented by bind:pre, bind:activation, bind:post when their lists are nonempty.
No callback source, object, identity or count is serialized. Marker payload work remains behind
existing active-recorder/dynamic gates. No world sweep or new schema version is introduced.

## Existing consumers
SpellbookCrystal, PersistenceProfile, PersistenceCrystal, JSON cache, formations and external tap
carry the generic field. ConfigurationLossStrategy and RestoreEngine report code participation.
Graft uses public bind on a receiving Book. Add tests; do not fork these into new hook-aware pipelines.

## Validation mapping
Freeze/re-freeze; all three markers mixed with current hooks; late append/clear and replacement;
automatic/inactive recorder gates; checkpoint/formation payload transport; generic restore shortfalls;
receiving-book graft execution. Native source capture still precedes post and follows activation.
