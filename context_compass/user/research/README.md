# research

Purpose
- Store human-authored research artifacts used to enrich context stores.
- Keep artifacts organized by lifecycle buckets for deterministic intake.

Buckets
- pending/: newly dropped artifacts awaiting review.
- ready/: vetted artifacts ready for consumption.
- active/: artifacts currently in use for context enrichment.
- archived/: historical artifacts retained for traceability.
- delete/: artifacts marked for deletion prior to removal.

Usage
- Store markdown files when possible for direct reading.
- Move artifacts between buckets with `context_compass/system/ai_restricted/context_management/research_move.py`.
- Delete artifacts with `context_compass/system/ai_restricted/context_management/research_delete.py` after review.
