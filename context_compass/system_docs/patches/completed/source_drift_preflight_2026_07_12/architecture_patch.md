# Architecture Patch: source drift at load-time preflight

- Patch ID: source_drift_preflight_2026_07_12
- Ticket: TASK-2026-07-12-source-drift-preflight (owner: "send it" on the
  offered improvement - a restore should TELL you your working tree
  diverged from the sealed world before it builds anything)
- Status: active

## Objective
Every load's preflight now checks EVERY bind-time fingerprint against
disk - not just retained-text modules. Today only
UserSourceIntegrityStrategy drift-checks, and only for modules carried in
user_module_sources (retention ON); retention-OFF worlds restore blind to
divergence even though physical_module_fingerprints ships in every
crystal. New SourceDriftStrategy (10th default row) owns ALL disk-vs-seal
comparison; UserSourceIntegrityStrategy narrows to TAMPER only (retained
text vs its own recorded sha - record self-consistency), removing the
double-report overlap.

## Interface Deltas
- NEW preflight/source_drift_strategy.py - SourceDriftStrategy
  ("source_drift"): per custody crystal, for each
  physical_module_fingerprints entry with a recorded module_to_path:
  absent file -> warning (import may still resolve via sys.path - honest
  wording); sha differs (CRLF-safe read_text re-hash) -> warning
  "user_source_drifted_since_seal"; unreadable -> info; unchanged ->
  silent. Deduplicates per (module, path) across crystals.
- UserSourceIntegrityStrategy: drift/absent/no-fingerprint branches
  REMOVED (SourceDriftStrategy owns them); keeps the retained-text
  tamper BLOCKER only; docstrings updated.
- PersistenceAnalyzer default set: SourceDriftStrategy registered 10th.
- Adjudication unchanged: drift is real signal at every scope (warnings
  never block; verdict semantics untouched).

## Rollback
Unregister + delete the strategy; restore the integrity strategy's
drift branch.
