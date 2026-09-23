# Intermediate purge lesson validation

- Lesson: UX_and_AIX_experiences/02_intermediate/39_purge_unneeded_objects.py.
- Lesson 38 remains withdrawn; catalog now contains 38 intermediate lessons and 134 total.
- Runtime interpreter: Python 3.14.7 free-threading with GIL disabled.
- Standalone script passes: single removal 1, remaining-bucket removal 2, fresh melding,
  spell-space isolation, and exactly one disposal invocation for each of six buffers.
- Existing intermediate harness: 38 passed in 0.97s. One optional pytest-cache write warning
  came from sandbox permissions; no test failed and the JUnit report was written.
- Existing documentation unit tests: 39 passed in 6.110s.
- Input/navigation validation: 295 pages and 54 assets.
- Strict HTML build: 295 pages, successful Sphinx warning-as-error run.
- Site verification: 35,679 local links; source/download checks passed.
- Targeted publication audit: lesson identity and reciprocal scopes-guide link verified;
  generated source/HTML downloads and both collection ZIP payloads match the saved script bytes.
- Source SHA256: f58966c91b80400c760b84b142d964883a50cc1c2942531211fdc562b4e23a8a.
- Scoped correctness Ruff and scoped git diff --check pass.
- All three source asset groups were current. Rebuilt only the changed other corpus
  (360 inputs) and manifest; final src/tests/other corpus checks all pass.
- Registered only the new lesson with git intent-to-add for tracked-input discovery;
  its contents are not staged. No commit, hosted build or deployment was performed.
- Full runtime suite and coverage: Not run; this delivery changes an example and documentation.

Evidence is retained beside this summary in lesson.log, intermediate.xml, docs-tests.log,
html-build.log, site-check.log, publication-audit.json and all-corpora-final-check.log.
