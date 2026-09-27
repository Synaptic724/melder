# Retired site-plan graph descriptors

These descriptors are historical authored data from the completed override-site-plan work.
They are not inputs to the live source graph.

The previous nested source-path layout produced repository-relative filenames up to 272
characters long and failed Windows Git checkout. The twenty descriptors are now stored flat.
Their bytes are unchanged. The eight-character suffix derives from the original relative path
and disambiguates repeated basenames.

Use archive_index.json to map each original archive path to its current filename and SHA256.
The source paths and node IDs inside the JSON remain the historical identities. retired_edges.json
stays at its original location and retains the archived edges unchanged.

Relocation evidence: TASK-2026-09-26-repair-docs-build-blockers.