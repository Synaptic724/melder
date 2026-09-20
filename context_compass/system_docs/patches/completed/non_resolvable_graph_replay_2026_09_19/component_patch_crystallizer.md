# Component Patch: Crystal capability preservation

<!-- BEGIN ENTRY: Captured capability and public replay -->
SpellCrystal snapshots the native bool and returns it from describe; cleanup releases its field.
RestoreEngine active/staged paths and all three GraftRunner binding paths forward the captured bool.
Absent legacy values use True; malformed supplied values reach Bind's strict bool validation.

RecordVersion.CURRENT becomes 2.0.0 through the existing major reader gate. A version-1 reader refuses
new records rather than treating False as an unknown optional field. Version-2 readers retain old
records and missing flags through the existing legacy lane. No alternate codec or runtime value store.

Validate capture, legacy/new versions, fresh-world replay, staged selection, graft and re-emission.
Restored graph references arise from source bindings and selected members through the normal compiler.
<!-- END ENTRY: Captured capability and public replay -->
