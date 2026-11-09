# Scope prefix compatibility control flow

<!-- BEGIN ENTRY: "Exact old scope values and key projections" -->
## Enum by-value reads
The missing-value handler maps only world, frame and subsystem to the corresponding
members; foreign enum families and every other missing input are rejected.

## Key generation
Derive each historical lowercase key token from the relevant member name, not the new
uppercase value. Apply this to world, frame, subsystem and is_world together. Frame and
subsystem names and all existing invalid-name guards remain unchanged.

## Tests
Pin actual old pickles, both spellings, invalid and foreign legacy inputs, exact key
strings, real frame-create claim plans and conflicting claim admission. Preserve all
existing source and test behavior outside this family.
<!-- END ENTRY: "Exact old scope values and key projections" -->