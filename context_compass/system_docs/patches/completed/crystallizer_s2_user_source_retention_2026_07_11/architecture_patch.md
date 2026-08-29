# Architecture Patch: S2 physical custody - opt-in user-source retention

- Patch ID: crystallizer_s2_user_source_retention_2026_07_11
- Ticket: STORY-2026-07-11-physical-custody-user-source-retention
  (epic: crystallizer_v3_horizon_iteration, tranche S2)
- Status: active

## Objective
Fresh-pod rebuilds for spells whose source lives in USER FILES: an
OPT-IN policy retains the TEXT of user-owned modules inside the
SpellCrystal (mirroring the shipped M3 synthetic_module_sources lane at
every layer), and the restore engine rebuilds ABSENT user modules through
the synthetic module lane - the sanctioned from-text path (owner law:
normal verbs only, no special loaders; configurations excepted).

## Non-goals
- No retention by default (retain_user_sources=False is byte-identical
  to today at every surface).
- No override of live files: retained text is a FALLBACK for absent
  files only (owner-recommended drift rule: the live file wins).
- No site-package retention (third-party dists are provenance, not
  custody).

## Invariants
- Facades stay byte-compatible supersets (additive params/keys only).
- Shortfall honesty: every substitution is named
  ("user_module_rebuilt_synthetic_from_retained_source").
- physical_module_fingerprints (bind-time sha256, already shipped) stay
  the integrity anchor; retained text carries its own sha256 and must
  match the fingerprint at preflight (tamper = blocker).

## Interface Deltas (all additive)
- CrystallizerConfiguration: schema key "retain_user_sources" (bool,
  default False) + property + with_retain_user_sources fluent setter;
  rides the existing reload lane via available_properties.
- Crystallizer spell-crystal seam: passes
  retain_user_sources=self._configuration.retain_user_sources.
- SpellCrystal(spell, ..., retain_user_sources=False): threads to the
  analyzer; describe() gains "user_module_sources" (possibly empty).
- CrystalAnalyzer(..., retain_user_sources=False): walk loop harvests
  text+sha256+path+package for every module whose custody kind is
  user_source (ALL reachable user modules - exact synthetic mirror;
  owner-accepted scope); analyze_payload re-folds the key.
- CrystalAnalysisResult: _user_module_sources store +
  record_user_module_source + user_module_sources property + describe key.
- UserSourceCustodyStrategy.harvest_payload(module_path): static text
  read (utf-8, sha256) returning None for unreadable/non-file targets.
- RestoreEngine: custody hydration gains the retained-text fallback lane
  for ABSENT user files (synthetic-lane rebuild + shortfall); existing
  behavior untouched when no retention rides the payload.
- Preflight: hydration_strategy upgrades absent-user-file findings to
  info when retained text exists; NEW user_source_integrity_strategy
  (retained sha vs recorded fingerprint = blocker on mismatch; disk
  drift vs fingerprint = warning "user_source_drifted_since_seal").

## Migration Order
1. Config flag -> 2. threading (Crystallizer -> SpellCrystal ->
CrystalAnalyzer) -> 3. harvest + result store + describe -> 4. engine
fallback lane -> 5. preflight rows -> 6. tests (unit: flag/harvest/
payload round-trip/integrity; integration: seal -> delete tree ->
rebuild).

## Rollback
All deltas additive; flag off = today's behavior byte-identical.
