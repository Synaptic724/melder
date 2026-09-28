# LLM Support Compilation Pipeline Discovery

## Metadata

- Status: implementation-ready recommendation
- Owner: project owner
- Agent: codex_1
- Date: 2026-08-30
- Ticket: TASK-2026-08-30-llm-support-compilation-pipeline-discovery

## Outcome

Build one deterministic, stdlib-only generator that owns three committed text
bundles, three addressable Markdown indexes, and one shared JSON manifest under
the top-level llm_support directory.

Recommended tree:

~~~text
llm_support/
    README.md
    _builder.py
    manifest.json
    llm_full_src.txt
    llm_full_src_index.md
    llm_full_tests.txt
    llm_full_tests_index.md
    llm_full_other.txt
    llm_full_other_index.md
.github/workflows/llm-support.yml
tests/unit/llm_support/test_builder.py
~~~

The generator builds only corpora whose input fingerprint moved. CI checks the
committed results on every pushed tree and pull request; it does not create bot
commits.

## Authority And Reader Contract

The llm_support README must begin with the authority rule:

1. Use context_compass/AGENTS.MD and complete ContextCompass onboarding first.
2. Use context_compass system-document indexes and active tickets for focused,
   current repository work.
3. Use the llm_support indexes and bundles only for bulk export, external tools,
   offline review, or runtimes that cannot navigate the repository directly.

The bundles are derived snapshots. They never supersede ContextCompass policy,
boards, active tickets, or source files. ContextCompass is excluded from bundle
inputs entirely and must be read directly.

## Evidence And Measured Scale

| corpus | included files | normalized UTF-8 bytes | content lines |
| --- | ---: | ---: | ---: |
| src | 584 | 10,399,426 | 270,707 |
| tests | 794 | 10,092,802 | 298,909 |
| other | 262 | 2,111,280 | 55,572 |
| total | 1,640 | 22,603,508 | 625,188 |

A read-only eligibility, byte-read, decode, newline-normalization, and line-count
pass over the former 42 MB candidate set completed in about 2.25 seconds
locally; the accepted ContextCompass exclusion reduces the live input to about
22.6 MB.
Correct full input hashing is therefore cheap enough for every CI run.

Measured exclusions:

| exclusion | files | bytes | reason |
| --- | ---: | ---: | --- |
| ContextCompass | 2,621 | about 21.8 MB | read directly; generated copies conflict with live work state |
| generated source manifests/payloads | 8 | 3,797,075 | duplicate durable documents/data, not source code |
| rendered SVG and placeholder assets outside ContextCompass | 27 | measured by builder | non-LLM rendering |
| non-code files inside src | 8 | 48,732 | diagrams, README, and py.typed are not source code |

## Discovery Source

Input discovery uses sorted Git paths, not os.walk:

~~~text
git ls-files --cached -z
~~~

Why:

- ignored caches, virtual environments, pycache, build outputs, and local IDE
  state never enter the candidate set;
- ordering is deterministic across Windows and Linux;
- only repository-owned material can be duplicated into committed bundles;
- output files under llm_support cannot recursively ingest themselves.

The builder reads working-tree bytes for those tracked paths. A newly created
file must be staged before generation so git ls-files can see it. Untracked
nonignored files are deliberately excluded to avoid accidentally copying local
scratch or secrets into a committed aggregate.

All currently tracked entries use regular-file Git mode 100644. The builder
must fail loudly if a future eligible entry is a symlink, submodule, missing
path, or another unsupported mode.

## Corpus Contract

### llm_full_src

Include:

- tracked files under src/ with extension .py or .pyi;
- hand-written runtime code, build-time builders, loaders, and package wrappers.

Exclude:

- every path under a build-asset manifest/ directory;
- every path under a build-asset payloads/ directory;
- py.typed, Mermaid sources, SVG renders, and build-asset diagram README files;
- cache content, which is already untracked/ignored.

This keeps the bundle named full_src honest as full source code, not a second
copy of generated documentation embedded as Python literals.

### llm_full_tests

Include every tracked text file under tests/ with one of:

- .py or .pyi
- .json
- .md or .txt
- .toml, .yaml, .yml, .ini, or .cfg
- .gitignore

The current set is 783 Python tests plus ten small fixture/support text files.

### llm_full_other

Include every eligible tracked text file outside src/, tests/, and llm_support/,
including:

- architecture_and_design documentation and Mermaid sources;
- UX_and_AIX_experiences code, probes, and concept maps;
- benchmark source;
- GitHub workflows, root README, roadmap, package metadata, ignore/EOL policy,
  requirements, licenses, and notices.

Exclude:

- the entire context_compass directory;
- rendered SVG files;
- .gitkeep placeholders;
- the entire llm_support directory;
- any extension outside the explicit text allowlist.

ContextCompass remains available directly through its own indexes and is never
duplicated into llm_full_other.

## Text Decoding And Normalization

Never use errors=ignore.

Supported source encodings, in order:

1. UTF-8 with BOM
2. UTF-16LE or UTF-16BE with BOM
3. strict UTF-8
4. CP1252 fallback only when strict UTF-8 fails and no NUL byte is present

Measured current input:

- 3,534 strict UTF-8 files
- 110 UTF-8 BOM files
- two UTF-16LE BOM artifacts
- one CP1252 Markdown ticket containing the byte spelling of façade

Any other decoding shape fails the build with the path and byte offset. NUL
bytes without a recognized UTF-16 BOM are treated as binary and refused.

Bundle output is UTF-8 without BOM and LF-only. The manifest retains each
source file's detected encoding plus normalized UTF-8/LF content SHA256, so
semantic content or encoding changes move the fingerprint while checkout-only
EOL spelling does not.

## Bundle Format

Each bundle begins with a short generated warning and corpus metadata. Each
file then appears in sorted repository-relative POSIX-path order:

~~~text
================================================================================
BEGIN FILE: src/melder/example.py
CONTENT SHA256: <normalized UTF-8/LF sha256>
SOURCE ENCODING: utf-8
================================================================================
<the complete decoded file, normalized only to LF>
================================================================================
END FILE: src/melder/example.py
================================================================================
~~~

No Markdown fences wrap source content because source files may contain their
own fences. The builder tracks ranges while writing rather than re-parsing the
finished bundle.

For every non-empty file, the index records:

- entry start/end line;
- content start/end line;
- detected source encoding;
- normalized UTF-8 byte count, SHA256, and line count;
- repository-relative path.

Empty files use a dash for the content range and remain represented in the
manifest.

## Index Format

Each index is Markdown and follows the ContextCompass trust model:

~~~text
# llm_full_src_index

## Staleness proof
| field | value |
| bundle | llm_full_src.txt |
| schema_version | 1.0.0 |
| source_fingerprint | ... |
| bundle_sha256 | ... |
| bundle_line_count | ... |
| bundle_line_ending | lf |
| files | 584 |

## Files
| entry lines | content lines | content bytes | source encoding | content sha256 | path |
~~~

Ranges are 1-based and inclusive. Index generation validates that every entry
range starts at its matching BEGIN FILE marker, ends at its matching END FILE
marker, stays in bounds, and is monotonically ordered.

The index carries the bundle hash rather than its own hash. The manifest carries
both bundle and index hashes, avoiding a circular self-hash.

## Manifest Contract

Path: llm_support/manifest.json

The manifest is deterministic JSON: UTF-8, LF, sorted keys, stable indentation,
and no volatile generation timestamp.

Recommended shape:

~~~json
{
  "schema_version": "1.0.0",
  "policy_version": "1.0.0",
  "generator_sha256": "...",
  "corpora": {
    "src": {
      "source_fingerprint": "...",
      "file_count": 584,
      "content_bytes": 10399426,
      "files": {
        "src/melder/example.py": {
          "source_encoding": "utf-8",
          "content_sha256": "...",
          "content_bytes": 1200,
          "content_lines": 42
        }
      },
      "bundle": {
        "path": "llm_support/llm_full_src.txt",
        "sha256": "...",
        "bytes": 0,
        "lines": 0
      },
      "index": {
        "path": "llm_support/llm_full_src_index.md",
        "sha256": "...",
        "bytes": 0,
        "lines": 0
      }
    }
  }
}
~~~

Per-file line ranges live only in the index. Omitting them from the manifest
prevents one early-file line insertion from rewriting every later manifest
entry; only the index must absorb the unavoidable range shift.

The generator fingerprint covers _builder.py and the policy/schema constants.
A generator-fingerprint or schema change makes all three corpora stale because
the output contract may have changed.

## Incremental Algorithm

For each run:

1. Resolve the repository root and enumerate sorted tracked paths.
2. Classify each eligible path into exactly one corpus or one explicit
   exclusion reason.
3. Read exact bytes, detect encoding, decode strictly, normalize line endings,
   and compute per-file exact and normalized hashes.
4. Compute each corpus fingerprint over policy version plus sorted path,
   source encoding, normalized content SHA256, byte count, and line count.
5. Compare generator, schema, and corpus fingerprints with manifest.json.
6. For unchanged corpora:
   - hash the committed bundle and index;
   - verify both against manifest;
   - do not render or rewrite either file.
7. For changed corpora in build mode:
   - stream the full corpus to a temporary bundle while collecting line ranges;
   - render and validate its temporary index;
   - atomically replace only that corpus's bundle and index.
8. Write the manifest atomically, last, only when its deterministic content
   differs.

In check mode, any input or output mismatch reports STALE and writes nothing.
It should list added, removed, and changed source paths by comparing the current
per-file map with the manifest.

Corpus-level regeneration is the finest safe write granularity. One changed
file moves every later line range in a monolithic bundle, so patching only one
segment would sacrifice atomicity and index correctness.

## Builder CLI

Recommended commands:

~~~text
python llm_support/_builder.py
python llm_support/_builder.py --check
python llm_support/_builder.py --list
python llm_support/_builder.py --corpus src
python llm_support/_builder.py --slice src src/melder/aether/aether.py
~~~

Behavior:

- default: regenerate only stale corpora;
- --check: verify inputs, output hashes, manifest, and index ranges; write nothing;
- --list: report corpus membership, exclusions, sizes, and fingerprints;
- --corpus: restrict an explicit local build/check;
- --slice: verify the selected bundle/index first, then print one file's
  content range.

The implementation should use one policy class for constants and small pure
helpers for classification, decoding, hashing, rendering, and validation.
It requires no third-party dependency and must not import melder.

## GitHub Actions Contract

Path: .github/workflows/llm-support.yml

Triggers:

- push to every branch;
- pull_request;
- workflow_dispatch.

No path filter is recommended because the owner asked for every committed tree
to be checked, generated-only edits must not bypass hand-edit detection, and the
measured full scan is cheap.

Job:

1. checkout;
2. setup Python 3.14;
3. run python llm_support/_builder.py --check;
4. on failure, print the exact local regeneration command.

Use per-ref concurrency with cancel-in-progress. Grant no write permission and
install no dependencies.

### Why CI Must Not Auto-Commit

A GitHub Action runs after a commit exists. It cannot make that same commit
self-contained; a bot write-back creates a second commit, requires contents
write permission, recurses into another workflow run, conflicts with protected
branches/forks, and can race with the developer's next push.

Recommended contract:

- regenerate locally before commit;
- commit source plus changed bundle/index/manifest together;
- let CI refuse stale committed output.

If true local commit-time automation is later required, add a separate,
explicitly approved pre-commit integration. It is not necessary for the MRP and
should not be smuggled into the GitHub workflow.

## README Contract

llm_support/README.md should contain:

1. ContextCompass-first authority and onboarding links.
2. A table describing src, tests, and other.
3. Exact inclusion/exclusion rules.
4. Bundle and index format.
5. Trust/staleness fields and the manifest role.
6. Build, check, list, and slice commands.
7. CI behavior and the no-auto-commit explanation.
8. Warning that bundles are generated and must never be edited manually.
9. Explanation that ContextCompass is excluded and must be read directly.

## Failure Behavior

Fail loudly on:

- Git discovery failure;
- unsupported Git mode, missing tracked file, or path outside the repo root;
- ambiguous or duplicate corpus membership;
- unsupported encoding or NUL-bearing binary input;
- source read failure;
- duplicate path or malformed bundle marker;
- stale/missing manifest, bundle, or index in check mode;
- bundle/index hash mismatch;
- line-range, marker, monotonicity, or bounds validation failure;
- failed atomic replacement.

Never skip a file after it has passed eligibility. An included file that cannot
be decoded is a failed build, not an informational warning.

## Validation Matrix

Unit tests:

- deterministic path ordering across input order;
- exact corpus classification and every exclusion family;
- self-output recursion exclusion;
- UTF-8, UTF-8 BOM, UTF-16LE/BE BOM, and CP1252 decoding;
- unsupported/NUL input refusal;
- full-file markers and newline behavior, including empty/no-final-newline files;
- index range round-trip for first, middle, last, and empty entries;
- fingerprints move on content, rename, add, and delete;
- unchanged corpus files retain byte content and modification time;
- one changed corpus rewrites only its bundle/index and manifest entry;
- manual bundle or index edits fail check mode;
- generator/schema change invalidates all corpora;
- manifest and output writes are atomic;
- slice refuses stale output and returns the exact indexed content.

Repository checks:

- generated corpus counts match 584/794/262 under the accepted policy;
- all 1,640 eligible files appear exactly once;
- every excluded tracked file has one explicit exclusion reason;
- generated outputs contain no llm_support input path;
- two consecutive builds are byte-identical and the second writes nothing;
- check mode is clean immediately after generation;
- Windows and Linux output hashes match;
- git diff hygiene passes.

Workflow checks:

- YAML has push, pull_request, and workflow_dispatch;
- action permissions are read-only;
- Python is 3.14;
- check mode is the only CI builder invocation;
- failure text gives the local regeneration command.

## Implementation File Plan

| file | purpose |
| --- | --- |
| llm_support/_builder.py | classification, decoding, fingerprinting, rendering, validation, CLI |
| llm_support/README.md | ContextCompass-first consumer and maintainer contract |
| llm_support/manifest.json | generated schema, per-file fingerprints, output proofs |
| llm_support/llm_full_src.txt | generated source corpus |
| llm_support/llm_full_src_index.md | generated source line-range index |
| llm_support/llm_full_tests.txt | generated test corpus |
| llm_support/llm_full_tests_index.md | generated test line-range index |
| llm_support/llm_full_other.txt | generated remaining tracked-text corpus |
| llm_support/llm_full_other_index.md | generated other line-range index |
| tests/unit/llm_support/test_builder.py | deterministic unit/contract coverage |
| .github/workflows/llm-support.yml | check-only push/PR/manual gate |

## Decisions Recommended For Implementation

- Exclude ContextCompass entirely and direct capable agents to it from README.
- Exclude generated source payload/manifests.
- Use Markdown indexes and plain-text bundles.
- Use one deterministic JSON manifest with per-file fingerprints.
- Normalize aggregate output to UTF-8 LF and hash normalized content plus source encoding.
- Regenerate only changed corpora.
- Run check-only CI; do not auto-commit from GitHub Actions.
- Keep the generator stdlib-only and outside the melder package/runtime.

## Owner Decision Before Implementation

Confirm the check-only GitHub Action recommendation. If the owner explicitly
wants bot write-back instead, that is a different pipeline with repository write
permissions, branch-policy implications, recursion controls, and race handling;
it should be designed as a separate, consciously accepted risk.
