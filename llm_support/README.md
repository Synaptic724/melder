# LLM Support

## Use ContextCompass First

ContextCompass is the repository's authoritative policy, navigation, work-state,
and re-entry system.

Before using these files:

1. Read `context_compass/AGENTS.MD`.
2. Complete the required ContextCompass onboarding or re-onboarding flow.
3. Use `context_compass/system_docs/` indexes and active tickets for focused,
   current work.

The files in this directory are generated bulk-export snapshots. They are useful
for external tools, offline review, retrieval systems, and runtimes that cannot
navigate the checkout. They do not override source code or ContextCompass.

## Generated Assets

| corpus | bundle | index | contents |
| --- | --- | --- | --- |
| source | `llm_full_src.txt` | `llm_full_src_index.md` | tracked Python source under `src/`, excluding generated payload/manifests |
| tests | `llm_full_tests.txt` | `llm_full_tests_index.md` | tracked test code and small text fixtures under `tests/` |
| other | `llm_full_other.txt` | `llm_full_other_index.md` | architecture docs, UX, workflows, benchmarks, and remaining stable text outside ContextCompass |

`manifest.json` is the shared machine-readable truth for input fingerprints,
per-file content hashes/encodings, and bundle/index output proofs.

Do not edit any bundle, index, or manifest manually.

## Reading

Prefer an index and one file range over loading a whole bundle.

Print one indexed source file after verifying the corpus:

~~~powershell
python llm_support/_builder.py --slice src src/melder/aether/aether.py
~~~

List current inputs, exclusions, line counts, and normalized bytes:

~~~powershell
python llm_support/_builder.py --list
~~~

The `other` corpus intentionally excludes the entire `context_compass/`
tree. Read ContextCompass directly so a generated snapshot cannot become a
competing or immediately stale source of truth.

## Building

Regenerate only stale corpora:

~~~powershell
python llm_support/_builder.py
~~~

Verify committed outputs and write nothing:

~~~powershell
python llm_support/_builder.py --check
~~~

Build or check one corpus:

~~~powershell
python llm_support/_builder.py --corpus src
python llm_support/_builder.py --check --corpus tests
~~~

New files must normally be staged before generation because discovery starts
from `git ls-files`. During an explicit initial/bootstrap build only:

~~~powershell
python llm_support/_builder.py --include-untracked
~~~

That flag includes every nonignored untracked eligible file. Review those files
before using it; it also treats missing cached paths as unstaged deletions.
The normal and CI paths remain tracked-only and fail loudly on missing inputs.

## Inclusion And Exclusion

The source corpus includes tracked `.py` and `.pyi` files under `src/`.
Generated build-asset `manifest/` and `payloads/` Python files are excluded
because they duplicate canonical documents and data rather than source logic.

The test corpus includes tracked Python, JSON, Markdown, text, common config,
and `.gitignore` files under `tests/`.

The other corpus includes eligible tracked text outside `src/`, `tests/`,
and `llm_support/`. It excludes:

- the entire `context_compass/` tree;
- rendered SVG files;
- `.gitkeep` placeholders;
- unsupported extensions;
- this directory, preventing recursive output capture.

Git discovery naturally excludes pycache, virtual environments, build outputs,
runtime caches, IDE state, ignored results, and other untracked noise.

## Encoding And Trust

Inputs are decoded without `errors="ignore"`. Supported forms are UTF-8,
UTF-8 BOM, UTF-16LE/BE BOM, and the measured mixed UTF-8/CP1252 historical
fallback. NUL-bearing inputs without a UTF-16 BOM fail loudly.

Generated files are UTF-8 without BOM and LF-only. Content hashes cover the
normalized UTF-8/LF view, while the manifest records the detected source
encoding. Checkout-only CRLF/LF differences therefore do not create Windows/
Linux drift.

Each index carries:

- source fingerprint;
- generator/schema version;
- bundle SHA256, line count, and line-ending proof;
- exact entry and content ranges for every included path.

Check and slice operations refuse missing, stale, tampered, or malformed output.

## Incremental Behavior

Every run hashes all eligible input text. The measured repository input is about
22.6 MB, so this is cheap. Unchanged corpora verify their committed bundle/index
hashes and are not rendered or rewritten.

A changed monolithic corpus is rewritten atomically because every later line
range may move. The manifest is written atomically and last.

## GitHub Actions

- `build-src-assets` checks Melder's package-internal durable assets.
- `build-repo-assets` checks these repository-wide LLM support assets.

Both workflows are check-only. GitHub Actions run after a commit exists, so they
cannot repair that same commit. Regenerate locally and commit inputs plus changed
outputs together; CI refuses stale or hand-edited assets.

The workflows require no repository write permission and install no dependencies.
