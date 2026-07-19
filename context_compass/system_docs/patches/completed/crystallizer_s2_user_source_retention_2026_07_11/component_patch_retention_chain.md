# Component Patch: S2 retention chain (record -> engine -> preflight)

- Patch ID: crystallizer_s2_user_source_retention_2026_07_11

## CrystallizerConfiguration
Before: no retention policy; user modules recorded as paths+fingerprints.
After: schema key "retain_user_sources" (bool) + with_defaults False +
retain_user_sources property + with_retain_user_sources fluent setter;
reload lane covers it automatically (schema-driven backfill).

## Crystallizer / SpellCrystal / CrystalAnalyzer (threading)
Additive kwargs, default False at every hop: the spell-crystal build seam
passes _configuration.retain_user_sources -> SpellCrystal ctor ->
CrystalAnalyzer ctor (new _retain_user_sources slot).

## Custody strategies (harvest)
Base SourceCustodyStrategy gains harvest_payload(module_name, module_path)
defaulting to None (most custody classes retain nothing; the synthetic
lane keeps its object-driven static). UserSourceCustodyStrategy overrides:
reads via the EXISTING _read_source_like_file + fingerprint helpers and
returns {source_text, source_sha256, module_path, is_package} or None.

## CrystalAnalysisResult / walk / payload round-trip
New _user_module_sources store + record_user_module_source +
user_module_sources property + describe key + cleanup del; the analyzer
walk harvests beside the M3 synthetic harvest (gated on flag AND
custody.kind == "user_source"); analyze_payload re-folds the key (absent
in pre-S2/retention-off payloads); SpellCrystal.describe() surfaces it
additively.

## RestoreEngine (rebuild lane)
_hydrate_target refactored: _import_qualified_target extraction; on
import failure, _rebuild_user_world runs ONCE - it rebuilds only retained
modules whose recorded backing path is ABSENT (live file always wins) and
not already in sys.modules, through the SyntheticModule lifecycle
(register -> publish -> execute; binding_signature sentinel
"user_source_retained"; parent derived from the dotted name; dot-depth
order; _built_stack teardown), filing
"user_module_rebuilt_synthetic_from_retained_source" per module; then the
import lane retries exactly once. No retention = byte-identical legacy
path.

## Preflight
hydration_strategy: absent-root-module blocker DOWNGRADES to info when
the payload retains that module's text. NEW UserSourceIntegrityStrategy
(registered 8th in the PersistenceAnalyzer default set): retained-text
sha mismatch = BLOCKER (tamper); live-file-vs-bind-fingerprint mismatch =
WARNING "user_source_drifted_since_seal" (live file wins; read_text
mirrors the custody read so CRLF files never false-drift); unreadable/
unfingerprinted = info.

## Validation Expectations
- Unit: flag default/fluent/reload; harvest payload happy + None lanes;
  result store/describe/re-fold round trip; integrity strategy tamper/
  drift/info rows; hydration downgrade row.
- Integration: seal with retention ON -> delete user tree -> restore
  rebuilds through the synthetic lane with the named shortfall;
  retention OFF stays byte-identical.
- Owner runs 3.14t; "Not run." until then.
