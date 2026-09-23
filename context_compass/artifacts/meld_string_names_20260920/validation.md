# Quoted meld names: documentation validation

Task: tickets/tasks/2026-09-20_teach_meld_string_names_task.md.
Recorded: 2026-09-20T09:22:39Z.

## Corrected teaching examples

- Initial audit found 140 reference targets in saved lessons, plus the Worker guide and package quickstart.
- Codemod converted 138 calls across 61 lesson files using declared class/function names or reviewed mappings.
- The batch-registration lesson now resolves Users, Orders and Invoices with three explicit string calls.
- The address-law lesson compares quoted-name and explicit-ID resolution; its object-form call/prose is removed.
- Watched hooks now demonstrate conduit.meld("Watched") twice.
- Prebuilt variables resolve as "AlreadyBuilt" and "PublishedConfig", preserving the original objects.
- Codegen examples resolve "Tokenizer", "Counter", "Reporter" and "Worker" by their declared names.
- README, beginner registration and maintainer guidance explain registration references vs named resolution.
- Worker guide and MyService quickstart use quoted names; return annotations and explicit IDs stay intact.
- Runtime API implementations and test-only coverage of reference inputs were not changed.

## Executed checks

- Audited all 137 published Python sources/helpers; every positional meld target is a string literal.
- Codemod AST comparison accepts only the planned argument substitutions; repeat checks propose zero edits.
- Existing complete lesson harness: 133 passed in 19.06s, zero failures/errors/skips.
- Runtime: Python 3.14.7 free-threaded, PYTHON_GIL=0, Melder source version 0.2.44.
- Tests used task-owned temporary/pytest-cache paths with filesystem access. No cache reset was needed.
- Existing documentation tests: 39 passed in 4.492s.
- Strict Sphinx HTML build: 294 pages passed with warnings treated as errors.
- Site check: 294 pages, 35,513 local links and source/download fidelity passed.
- Rendered teaching audit: 495 code blocks on 294 pages contain no reference-target calls.
- Download audit: 137 Python files and four ZIPs containing 137 Python members contain no reference targets.
- Source assets and src/other corpora were regenerated and their freshness checks pass for 0.2.44.
- Scoped whitespace check and editorial diff review passed.

## Evidence

- codemod.py, dry-run.json, changes.json, idempotence.json: exact source mappings and automated edit inventory.
- documentation.diff: complete source/editorial diff for review.
- examples.xml and examples.log: all 133 saved examples, including the owner's hook example.
- docs-tests.log, html-build.log, site-check.log: documentation build checks.
- publication-audit.json: generated page/code/download/archive sweep.
- source-assets-build.log and source-assets-check.log: package documentation asset regeneration.
- corpora-build.log and corpora-check.log: derived source and repository corpus refresh.

Changes remain local for owner review and signing. No hosted Read the Docs deployment was performed.
