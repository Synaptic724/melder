# Component Patch: Conduit

## Before
- conduit can report whether a spell is live
- conduit does not expose a narrow helper for retrieving the already-live spell
  runtime object through current live storage

## After
- conduit owns a narrow internal helper for returning the already-live spell
  runtime object from existing creation storage

## Interface Deltas
- helper is internal/supporting only
- no broad new public runtime surface is required for this patch

## State / Failure Deltas
- static command retrieval can now use runtime truth directly instead of
  blanket denial
- non-live or ambiguous cases fail fast without creating anything
