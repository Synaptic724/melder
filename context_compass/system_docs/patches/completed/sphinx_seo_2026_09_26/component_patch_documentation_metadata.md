# Component patch: Documentation sources and renderers

## Purpose / boundary
The builder assembles authored pages, README-derived chapters, examples and references into Sphinx
source. It owns generated output; source documents and runnable lesson bytes remain canonical.

## Before / after
- Before: shared browser suffix repeats the slogan; chapters/lessons have no description model.
- After: suffix is Melder; selected pages emit explicit descriptions; visible homepage stays intact.
- Before: README cleanup carries a GitHub configuration link into the website.
- After: the website link uses the corresponding local chapter while README bytes stay unchanged.

## Interfaces
- PageMetadata.description(value, owner) accepts absent metadata or a nonempty string; malformed
  supplied data raises a named ValueError before generated output is replaced.
- PageMetadata.frontmatter(description) returns empty text for no description or one YAML block.
- Lesson gains one default-empty string field; existing constructors remain compatible.
- An optional default-empty legacy_anchor preserves a published heading fragment when an editorial
  title changes. It must be a lowercase alphanumeric/hyphen target and is emitted before the H1.
- Catalog overrides accept description; chapter descriptions are allowed only for README selectors.
- Authored chapter metadata must remain inside the authored file, preventing dual ownership.

## State / lifecycle
Only value metadata is retained. No handles, runtime objects, caches or new lifecycle owners.

## Failure deltas
Invalid descriptions fail source validation. Formatter escapes quotes/control characters through
a JSON string literal valid in YAML. Ordinary Markdown/code bodies are retained verbatim.

## Dependency / ordering
Add the formatter, consume it in the two generators, add selected metadata, then render and test.
Preserve compiler/runtime source; no source-graph refresh is required for documentation-only modules.

## Validation
- Valid descriptions appear once in final HTML with exact human text after escaping.
- Missing optional descriptions leave existing renderer behavior.
- Invalid metadata fails with the owning page/source named.
- Authored pages cannot acquire competing manifest descriptions.
- Cleanup's generated configuration route is local, while README remains unchanged.
- Existing homepage/template and source-fidelity tests continue to pass.

## Open decisions
None for this scope. Extend description coverage later from reader/search evidence.
