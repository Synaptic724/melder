# Injected dependency direct-resolution evidence

This bundle accompanies EPIC-2026-09-30-injected_dependency_direct_resolution. It preserves the
observed installed-Melder failure and the surrounding MelderOps test context. It is diagnostic
evidence, not a patch to apply to Melder or a claim that the issue has been fixed.

- `test_native_dependency_lookup.py` is the exact failing plain-class diagnostic.
- `native_dependency_lookup.xml` is its red result; the service was successfully injected first.
- `focused.xml` and `dependency_lookup.xml` preserve the original failure and isolated rerun.
- `native_contracts.xml` contains 14 passing Toolbox contracts using repeated consumer construction
  for scope identity. That green result does not replace the direct-provider acceptance assertion.
- `regression.xml` records 1,794 passes, two skips and a separate missing-root_conduit fixture failure.
- `runtime_provenance.json` identifies Python 3.14.7t, GIL off, Melder 0.2.8212 and actual import origin.
- `source_snapshot/` preserves the relevant origin source and fixtures, including host construction.
- `installed_native/` preserves the three inspected installed files at the immediate failure boundary.
- `evidence_manifest.json` supplies original relative paths, byte counts and SHA-256 hashes.
- `results_summary.json` derives counts directly from the copied JUnit files.

The diagnostic imports Spectrum fixtures. Run it from the original MelderOps checkout using the
epic's command or `reproduce_from_melderops.ps1`. For a native-only regression, port the public test
body to Melder's existing isolated dynamic-root fixture; that reduction has not yet been executed.

The copied source snapshot is not a complete runnable checkout. HEAD alone does not identify the
tested worktree because the Toolbox and preceding Spectrum changes were uncommitted. Keep the
recorded host configuration and actual installed package distinct from the current Melder checkout.
