# Code contract: Default-first classification

<!-- BEGIN ENTRY: "Default classification gate" -->
## Control flow
Leave both existing descriptor-return branches first. Immediately afterward, check has_default and
return PLAIN with optional=True and no collection/SpellMap metadata for ordinary defaults.
Do not check default_value truthiness. Do not move or alter the Optional-unwrapping logic for
parameters without a default. Do not relax Phase-3 zero/multiple-provider checks to implement this fix.

## Failure and cache behavior
Default-bearing parameters no longer fail for absent inferred providers because they no longer request
inferred DI. Required-provider and descriptor errors retain their existing paths. Cache version 8
invalidates older semantic plans before any payload can be selected by a still-matching bind SHA.

## Mapping
- Classifier branch -> the 20 red default/PLAIN cases plus unit/DI-shape tests.
- Existing branches -> the 20 preservation controls and requirements/descriptor suites.
- Cache version -> existing version-history contract and automatic invalidation.
- Context update -> authored docs, paired indexes and regenerated source descriptors/graph.
<!-- END ENTRY: "Default classification gate" -->
