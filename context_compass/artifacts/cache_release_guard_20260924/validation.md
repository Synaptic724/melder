# Release-version cache invalidation delivery

Implemented exact Melder release admission in the persisted creation-cache envelope. Canonical
package version is 0.2.51; cache generation is 9. The independent Crystallizer record format is unchanged.

## Runtime contract

- Import the canonical version from melder.__version__.
- Stamp new envelopes, reject incompatible/missing release fields before adoption, preserve accepted
  stamps through normalization and atomic emission.
- Use the existing cold-cache path and normal conjure compilation/staging/emission.
- Only CachingSystem runtime code changed. Ordinary meld, compiler phases, spell IDs, live objects
  and persistent world records retain their existing contracts.

## Regression evidence

- red.log/xml: seven intended failures, nineteen passing controls before the runtime change.
- green.log/xml: all 63 utility/schema/runtime cases pass after implementation.
- qualified.log/xml: all 138 affected tests pass at 0.2.50 before the release increment.
- final_version.log/xml: 137 pass at 0.2.51; one generated-asset stamp case was deferred until rebuilding.
- final_metadata.log/xml: all four package metadata checks pass after generation, including that
  deferred case. Together these qualify 138 unique tests on the final 0.2.51 source.
- The runtime release matrix covers upgrade, downgrade, prerelease and local-version changes in
  automatic and dynamic modes. Binding IDs and format remain fixed; old context publication is
  forbidden on mismatch, and the next same-release run must resolve without rebuilding plan phases.
- The old invalid-file unit matrix wrote unused JSON paths. Replaced it with actual .melc marshal
  input and a populated matching control, preserving supported schema/interpreter/payload refusals.
- Scoped fatal lint and whitespace checks pass. No full-repository suite or coverage claim.

## Compatibility and scope

compatibility_probe.json records fresh-process source import, a generation-8 reader rejecting a
new generation-9 bundle, and unchanged build-asset accelerator reuse/invalidation behavior.
The isolated normalization microbenchmark measured 328.29 ns baseline and 392.35 ns with the release
guard (seven repeats of 100,000 empty-envelope calls). This excludes IO and conjure and says nothing
about meld throughput. The new comparison is on cache loading, not the meld path.

documentation_and_scope.json proves only CachingSystem and version metadata changed among 595 source
and stub files before generated assets. Canonical map changes preserve all previous prose; only
metadata dates were replaced and the before-images are retained. Source graph extraction reports no
skipped or orphaned nodes. Only the cache class's reread semantics were accepted; unrelated existing
staleness remains honest. This is a scoped documentation update, not a repository-wide quality audit.

The next-release draft was empty with 0.2.50.md already present. It now contains public 0.2.51 notes
about automatic cold rebuild, same-release reuse, legacy compatibility and retained durable records.
Temporary probe/pytest directories and the eight new release-test cache folders were removed.

The package and LLM generators and their checks run after source/documentation changes. Following
owner direction, the final repetition runs after turn-in tracking too, with no subsequent edits and
no separate build task. Final build results are reported in command output.

All three package builders completed for 0.2.51 and all package/LLM currentness checks passed before
turn-in. The final repetition after tracking changes is the last operation of this delivery.

All implementation inputs are tracked. The final LLM build uses its standard tracked-input mode;
the unrelated untracked tests/experimentation/test_melder_creation_overrides_performance.py is left
unchanged and outside that bundle. Adding it to the tracked corpus later requires the usual rebuild.
