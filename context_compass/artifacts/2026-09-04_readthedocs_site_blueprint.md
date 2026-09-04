# Melder Read the Docs Site Blueprint

- Design ID: RTD-DESIGN-2026-09-04
- Owner: codex_2
- Status: defined for implementation planning; implementation not started
- Created: 2026-09-04T21:30:46Z
- Epic: ../tickets/epics/2026-09-04_readthedocs_documentation_epic.md
- Authority: owner's latest four-level instruction, README level table, saved example corpus

## 1. Product Contract
The learning structure is exactly **Beginner -> Intermediate -> Advanced -> Expert**. Preserve those
names, order, and green/yellow/orange/blue identifiers from the README. Each is a first-class section
with its own contents, guides, examples, and clear learning outcome. Do not insert another taxonomy
above them. The simple application path remains complete without studying advanced runtime features.

The website provides three simultaneous ways to read: follow a level in order, jump through a complete
table of contents, or start with a runnable example. The example collection is prominent throughout.
The README remains the repository/package tour; the website expands that tour into addressable pages.

Evidence: README.md:229-260; UX_and_AIX_experiences/AGENTS.md:1-44; owner instruction on 2026-09-04.

## 2. Primary Navigation and Homepage
Persistent learning navigation, in order:

| Learning section | Promise | Initial example inventory |
| --- | --- | --- |
| Green Beginner | Build and own a useful object graph with a small public vocabulary | 41 |
| Yellow Intermediate | Configure, compose, and connect independently owned subsystems | 37 |
| Orange Advanced | Isolate worlds and inspect or target more complex runtime structures | 19 |
| Blue Expert | Operate agent surfaces, persistence, research, and governed structural change | 36 |

Adjacent discovery/reference entries: **All Examples**, **Full Contents**, **Architecture & Drawings**,
**API Reference**, **Glossary**, **Troubleshooting**, and **Releases & Migration**. These are supporting
routes, not additional learning levels. Keep all four levels visible at the first sidebar depth.

Homepage content, in reading order:
1. Melder identity, short purpose, install/prerequisite link, and bind -> conjure -> meld.
2. Immediate actions: Start Beginner, Browse Examples, Full Contents.
3. Four level cards with the README's audience description and direct Guide / Examples links.
4. Featured runnable work: Hello Melder, beginner capstone, connected subsystems, and a verified
   expert demonstration. Each card says what the reader will accomplish.
5. Concise audience routes for application builders, system integrators, and agent/runtime builders.
6. Architecture/drawing entry, API lookup, current documentation version, and release notes.

Keep the README's concrete teaching voice. Define terms before using them. Explain optional features
at their level and link prerequisites without making the earlier path depend on the later one.

## 3. Complete Table of Contents and Free Exploration
- `/contents/` lists every level landing page, guide, lesson page, reference section, and release guide.
- Use one authoritative navigation model to generate the sidebar, complete contents, breadcrumbs,
  level contents, and previous/next ordering. Topic shortcuts link into it without creating duplicates.
- The full contents page exposes the complete hierarchy, including hidden-toctree children. It is
  directly reachable from every page, and works with JavaScript disabled.
- Every content page has a stable URL, heading permalinks, breadcrumb, visible level when applicable,
  an on-page contents list, related examples, and an obvious route back to its level.
- On mobile, keep Contents and Examples available through a labeled navigation control. Preserve
  keyboard focus and the current position when opening/closing navigation.
- Search supports both task words and public names: cleanup/disposal, request scope/SpellSpace,
  category/spellframe, isolated world/aetheric frame, checkpoint/restore, and agent room/Rift.
- Search results distinguish guide, example, and API content in their titles/context. The example
  catalog adds level and topic filters with a complete static list as its baseline.
- A page has one canonical parent. Cross-level links never duplicate the page or silently change its
  level. Prerequisites are guidance, never access restrictions.
- Acceptance: no orphan learning/example pages; every planned topic and numbered lesson appears in
  the contents; deep links load directly; navigation remains usable at 200% zoom and on narrow screens.

Sphinx supplies hierarchical contents and previous/next relationships through
[toctree](https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-toctree).

## 4. Beginner Curriculum
Entry: ordinary Python classes/functions, installation, and a supported interpreter.
Exit: the reader can compose a small application, resolve its objects, select basic lifetimes, and
clean up the runtime with an understanding of ownership and errors.

Required guide chapters, in order:
1. Installation and first run: Python 3.14, free-threaded example setup, import melder as md.
2. Hello Melder: the first class, spellbook, conduit, and resolved instance.
3. The rhythm: bind, conjure once, meld repeatedly; what each step is for.
4. What can be bound: classes, functions, existing instances, and small factories.
5. The address law: names, binding names, spellframes, and explicit identity lookup.
6. Spellframes as categories: strings, Protocol shapes, grouping, and typed resolution.
7. The beginner lifetimes: unique, many, unique_per_conduit; observable identity contrasts.
8. Child scopes and application bootstrap: where the conduit is passed and who owns it.
9. Disposal and memory ownership: registration vocabulary, explicit cleanup, and useful failure messages.
10. Common mistakes: duplicate registration, missing addresses, and attempted second conjure.
11. Beginner capstone: one useful application combining the level's ideas.
12. Complete Beginner examples and vocabulary reference.

Boundary: keep the first path static. Dynamic linking, spell spaces, Nexus, persistence, and research
are taught in their own levels. Additional detail is a link, not a prerequisite paragraph.
Examples: all 41 files in 01_beginner; include the full lesson list and topic routes from its concept map.
Evidence: README.md:274-477; UX_and_AIX_experiences/01_beginner/_concept_map.txt:1-54.

## 5. Intermediate Curriculum
Entry: Beginner addressing, ownership, lifetimes, and one-book/one-conjure rhythm.
Exit: the reader can configure a system and compose cooperating scopes/subsystems through documented
public registration, linking, permission, and late-binding operations.

Required chapters:
1. Fluent registration with SpellBinder and module registration with scan_bind/book.scan.
2. Constructor DI, explicit SpellMap targets, and collection DI.
3. Spellbook configuration: defaults, finalization/freeze, disposal configuration, scheduling knobs.
4. Registration, meld, conduit, and link lifecycle hooks.
5. Spell spaces, lineage lifetimes, child-scope cleanup, and lesser-conduit promotion.
6. Flat overrides and targeted instance reuse/inspection.
7. Dynamic posture and its setup/inheritance sequence.
8. Link two conduits: ownership, permissions, borrowing, and sharing as a pull.
9. SpellContract late binding: provider -> consumer -> link -> pull -> meld, composed per edge.
10. Conduits as categories/factories; named cloud lookup; transfer and sever operations.
11. Connected-subsystem walkthrough plus complete Intermediate example index.

Examples: all 37 files in 02_intermediate. Preserve the existing source locations and helper files.
Some established lessons overlap a higher-level guide (for example cluster usage); expose a related
link from that guide without moving or renumbering the saved lesson.
Evidence: README.md:478-597; UX_and_AIX_experiences/02_intermediate/_concept_map.txt:1-177.

## 6. Advanced Curriculum
Entry: Intermediate composition and the distinction between addresses, scopes, and ownership.
Exit: the reader can choose isolation boundaries, inspect a running world, and use more precise
runtime targeting while understanding the authority and lifecycle involved.

Required chapters:
1. Aetheric frames as isolated worlds; compare spellframe, conduit, and aetheric frame explicitly.
2. Frame posture/configuration and initialization order; root utility/logging setup.
3. Deep, wildcard, and broadcast overrides with clear match-count and overlap behavior.
4. Conduit clusters and coordinated lifetimes, linked to the existing cluster lesson.
5. Nexus setup and opening a Rift: configuration ownership and lifecycle.
6. Static rooms for health/admin/debug views; visible data and withheld/missing data.
7. Viewer navigation: frame, conduit, spell, and the describe/detail progression.
8. Workstation ownership and static/capability boundaries, with links to Expert operations.
9. Ward policies and failure cases readers can diagnose.
10. Checkpoint/restore entry points at the scope already taught by Advanced examples; link deeper
    persistence/record machinery to Expert rather than duplicating it here.
11. Multi-world inspection walkthrough and complete Advanced example index.

Examples: all 19 files in 03_advanced. Preserve topic overlap where the established curriculum uses it.
Evidence: README.md:598-670; UX_and_AIX_experiences/03_advanced/_concept_map.txt:1-321.

## 7. Expert Curriculum
Entry: Advanced world/room boundaries and explicit ownership; prerequisites stated per chapter.
Exit: the reader can understand and operate the agent-facing and continuity surfaces, including
authority, record/restore, research, and governed changes, with reproducible examples and limits.

Required chapters:
1. Package self-documentation: architecture, components, graph/network details, and targeted reads.
2. Agent rooms: capability/codegen authority, workstation, commands, and controlled execution.
3. Codegen workflow: validate, materialize, import, bind, meld; a working generated application.
4. DevOps and concurrent structural changes: transaction families, admission, observation, failure.
5. Persistence model: configuration, profile/checkpoint records, source custody, and digital twins.
6. Restore/cold boot: public replay, identity translation, rollback, drift, and honest shortfalls.
7. External storage integration: callable boundaries, local/remote behavior, and complete setup examples.
8. MutationResearch: sets, lanes, residency, campaigns, recorded source, diffs, and impact.
9. Compositions and candidate previews; stage -> notch -> meld; rollback and explicit retirement.
10. Multiple agents/worlds and free-threaded coordination, with observable outcomes.
11. Operational walkthroughs, glossary links, and complete Expert example index.

Examples: all 36 files in 04_expert, including later lessons absent from older concept-map counts.
Use actual source metadata and current verification records as publication inputs. The expert map is
a curation aid; only its first 150 lines were read in discovery and its historical run notes are not
current proof. Full per-lesson review belongs to the Expert story.
Evidence: README.md:683-1030; 04_expert/36_an_agent_builds_a_working_system.py:1-247 (under the example root).

## 8. Example Publication Contract
Coverage floor: 133 numbered scripts at design time (41/37/19/36); derive current coverage at build time.
Every discovered numbered script must map to exactly one stable published lesson or an explicit,
owner-reviewed disposition. Helper modules are packaged when needed, never mistaken for lessons.

Each example page contains:
- A human title, stable lesson identifier, level, one-sentence goal, and meaningful topic tags.
- Required prior concepts, supported runtime, local helper/download requirements, and exact run command.
- A short explanation, source-included code, highlighted important lines when useful, and a full-file view.
- Expected outcomes and assertions explained; captured output is tied to a real run/revision.
- Links to source at the matching Git revision, related level guides, relevant public APIs, and next lesson.
- A copy button that does not copy terminal prompts or output into executable commands.

Catalog behavior: browse by level, filter by topic/name, preserve numeric learning order, and deep-link
to the same canonical lesson from every entry point. Feature Hello Melder and complete applications
on the homepage. Publish all lesson pages without requiring a reader to visit GitHub to understand them.

Source model: scripts remain under UX_and_AIX_experiences. A deterministic catalog builder extracts
identity/metadata without importing or executing lessons. Authored explanatory wrappers can add context;
the code comes from the actual files through literalinclude or equivalent source inclusion.
Metadata errors, duplicates, missing sources, missing helper bundles, and dropped scripts fail catalog checks.
Preserve the public md.* example style and existing source numbering. Do not transplant AGENTS files,
concept-map history, test internals, or ContextCompass notes into public lesson prose.

Verification: use the existing pytest_examples suite on 3.14t against the documented commit. Validate
each advertised outcome; smoke success/header presence alone does not establish teaching correctness.
Record failed or unverified lessons honestly and resolve launch dispositions explicitly. Do not silently
omit difficult lessons or label the whole corpus verified based on old comments.

Evidence: UX_and_AIX_experiences/pytest_examples/test_example_contract.py:1-121.
Supported presentation: [Sphinx source inclusion](https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-literalinclude),
[copy buttons](https://sphinx-copybutton.readthedocs.io/en/latest/).

## 9. Architecture, API, and Lookup References
- Architecture/drawings consume the existing canonical Markdown and SVGs, maintaining captions,
  explanatory text, accessible SVG metadata, full-size access, and source/diagram links.
- Public API is curated by task: binding/configuration, resolution/scopes, links/permissions, frame
  setup, Nexus/Rift/viewers, persistence, research, and public errors/helpers.
- Inventory public exports and documented returned surfaces; each is documented or explicitly
  classified with rationale. Avoid duplicate object anchors and broken public-name aliases.
- API pages show signature, purpose, parameters, returns/errors, lifecycle/threading contracts when
  relevant, examples, and source links. Python docstrings remain their canonical contract source.
- Add a glossary with the real Melder vocabulary and common aliases; keep distinct frame meanings clear.
- Troubleshooting is symptom -> likely condition -> corrective action -> relevant guide/example/API.
- Releases/migration explain user-visible behavior and docs-version selection. Display package version
  from canonical metadata, avoiding a second hand-maintained release literal.
- Agent-facing reference explains the existing packaged documents and existing llm_support routes.
  Any public downloadable machine-readable corpus uses an explicit public-content selection and version;
  audit it first rather than exposing an existing broad bundle by assumption.

## 10. Visual and Interaction Quality
- Use readable measure/typography, a consistent four-level badge system, and visible level words.
- Use responsive cards for levels/examples and tabs only for useful alternatives such as shell syntax.
- Keep important prerequisites and failure semantics visible; collapse optional long output/code details.
- Support keyboard navigation, visible focus, semantic headings, descriptive links, image alternatives,
  high contrast, 200% zoom, narrow screens, and reduced motion. Color never carries meaning alone.
- Provide copyable code/commands, source/permalink actions, and useful empty/filter/search states.
- Keep tables readable on mobile; large diagrams offer full-size views and adjacent textual explanations.
- Essential navigation and the complete example list work without custom JavaScript.
- UI labels describe Melder concepts and user actions, not the build pipeline's implementation details.

Presentation components can use [sphinx-design](https://sphinx-design.readthedocs.io/en/latest/).

## 11. Sphinx and Build Architecture
Baseline: Sphinx, MyST, sphinx_rtd_theme, autodoc, napoleon, viewcode, intersphinx, sphinx-design,
and sphinx-copybutton. Select/pin a compatible dependency set after a real Python 3.14 build.
Each extension has a defined purpose; version compatibility is a build result, not an assumption.

Canonical inputs:
- docs/: site-specific guide prose, navigation/catalog policy, configuration, API selectors, styles.
- README.md: public framing, learning-level names, and source tour.
- UX_and_AIX_experiences/: runnable code and lesson metadata.
- architecture_and_design/: authored architecture/diagrams with its existing manifest.
- src/melder/: selected public API docstrings and package version metadata.

One docs command validates inputs, composes an explicit public source tree under docs/_build/source,
and invokes Sphinx. Preserve relative layout where practical; map local source/test links to the matching
public Git revision and page links to real site pages. Do not hand-maintain mirrored example code.
Output directories are generated/ignored. Catalog sorting, page IDs, source links, and TOCs are deterministic.

First real build exercises the homepage, all four level landings, complete contents skeleton, Hello
Melder, one architecture SVG, and one public API page. Check Melder import side effects and Python 3.14
deferred annotations; do not alter runtime contracts or weaken typing merely to satisfy docs tooling.
Version lookup itself must not boot Melder. Keep dependencies in the docs environment, outside runtime deps.

Keep package/example execution tests separate from Sphinx rendering. Cross-check existing source/LLM
asset workflows before changing their inputs. Normalize/define line-ending treatment for diagram hash
checks; the investigation found a Windows CRLF/LF mismatch and did not regenerate diagrams.

MyST support: https://myst-parser.readthedocs.io/en/latest/intro.html.
Autodoc import behavior: https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html.

## 12. Read the Docs Capabilities and Ownership
Use supported platform capabilities with explicit setup and verification:

| Capability | Implementation/verification responsibility |
| --- | --- |
| Git-triggered builds | Link the intended public repository and prove a commit-triggered build |
| PR previews and visual diff | Enable/review the integration and inspect a representative preview |
| Version switcher | Expose successful supported versions and preserve page context where supported |
| Version notifications | Mark development/older-version context accurately |
| Search as you type | Integrate the hosted addon; keep the Sphinx search route usable locally/offline |
| HTML/PDF/ePub downloads | Publish tested outputs with explicit contents and version identity |
| Canonical URLs and sitemap | Use the platform canonical URL and verify the served sitemap/version links |
| Redirects | Maintain mappings when published URLs change; test old links against intended pages |
| Search/traffic feedback | Review available platform analytics for missing topics and failed searches |

Account settings are external state, not proven by checked-in YAML. Owner/project permissions, exact
repository/branch association, custom-domain preference, and service feature availability are to be
verified at setup. Do not invent credentials, purchase plans, or require paid analytics for core navigation.

Recommended release policy: latest tracks the selected public development/publication branch; stable
tracks the latest accepted release that contains buildable docs. Make stable the default once that
release exists. Older tags without documentation configuration do not become supported versions by magic;
explicitly decide support and redirects. Pin source links to the built revision so old docs show old code.

Offline scope: complete zipped HTML; a clearly labeled handbook containing the four level guides,
glossary, and selected complete examples for PDF/ePub. Test long code, SVG conversion, Unicode level
badges, contents/bookmarks, and links. The handbook must state its scope and link to the full catalog.

Primary capability references:
- https://docs.readthedocs.com/platform/stable/config-file/v2.html
- https://docs.readthedocs.com/platform/stable/pull-requests.html
- https://docs.readthedocs.com/platform/stable/addons.html
- https://docs.readthedocs.com/platform/stable/versions.html
- https://docs.readthedocs.com/platform/stable/downloadable-documentation.html
- https://docs.readthedocs.com/platform/stable/canonical-urls.html
- https://docs.readthedocs.com/platform/stable/reference/sitemaps.html
- https://docs.readthedocs.com/platform/stable/guides/redirects.html

## 13. Delivery Parts and Dependencies
All stories are defined below the owning epic. Story IDs use the 2026-09-04 date.

| Part | Story slug | Deliverable | Prerequisites |
| --- | --- | --- | --- |
| S1 | rtd-navigation-and-site-shell | Local Sphinx foundation, homepage, four levels, full contents, navigation contract | Blueprint |
| S2 | rtd-example-catalog | Deterministic 133-lesson catalog, source inclusion, lesson template, topic routes | S1 |
| S3 | rtd-beginner-curriculum | Beginner chapters and all 41 saved lessons | S1, S2 |
| S4 | rtd-intermediate-curriculum | Intermediate chapters and all 37 saved lessons | S1, S2; Beginner vocabulary |
| S5 | rtd-advanced-curriculum | Advanced chapters and all 19 saved lessons | S1, S2; Intermediate vocabulary |
| S6 | rtd-expert-curriculum | Expert chapters and all 36 saved lessons | S1, S2; Advanced vocabulary |
| S7 | rtd-reference-and-architecture | Public API, existing architecture/drawings, glossary, troubleshooting | S1, S2; curriculum link map |
| S8 | rtd-build-and-hosting | CI parity, RTD setup, previews, versions, downloads, canonical links | S1-S7 |
| S9 | rtd-quality-and-launch | Complete content/navigation/example/accessibility audit, launch and maintenance runbook | S1-S8 |

Start one routed implementation task at a time under its story. Define exact source symbols when the
task is opened. This decomposition is not authorization to spawn agents or start simultaneous work.

## 14. File and State Boundaries
Proposed site files: docs/conf.py, docs/requirements.txt, docs/index.md, docs/contents.rst,
docs/navigation.toml, docs/catalog.toml, docs/beginner/, docs/intermediate/, docs/advanced/, docs/expert/,
docs/examples/, docs/reference/, docs/_static/, docs/tools/build_docs.py, .readthedocs.yaml,
.github/workflows/docs.yml, and docs/maintaining.md. Final tools may be split at clear responsibilities.

navigation.toml is the site-order/URL/parent registry; catalog.toml supplies editorial example metadata
and topic relations. Discovery from source verifies coverage; neither registry stores duplicated code.
Reuse architecture_and_design/manifest.json for its registered inputs rather than creating rival truth.

Changes to existing lessons, README, architecture prose, and API docstrings are scoped corrections with
source evidence. Runtime behavior changes found during docs work become separately owned tasks.
Keep codex_1's disposal work isolated; refresh affected docs/examples only against its settled contract.
ContextCompass records and private working material remain outside the public build inputs.

## 15. Acceptance and Release Gates
1. The four learning sections have exactly the owner-selected names/order/colors and distinct outcomes.
2. Homepage provides immediate access to four levels, Examples, and Full Contents.
3. Every selected guide, all numbered lessons, and each public reference page is discoverable in contents.
4. Catalog reconciliation has zero unexplained missing/duplicate lesson mappings or unresolved helpers.
5. Every lesson's source matches the documented revision; advertised results are supported by real runs.
6. All four curricula have complete chapters, prerequisites, concepts/examples/API links, and useful errors.
7. Public API coverage has an explicit inventory and no unexplained exclusions or import/typing failures.
8. Strict HTML build succeeds; local references/anchors, images, downloads, and source links are checked.
9. Representative desktop/mobile/keyboard/zoom flows pass; drawings and long code remain usable.
10. RTD preview and intended public version build from the correct repository/revision; version identity
    and redirects are correct. Confirm canonical URL, search, and offline output on the hosted site.
11. Existing example verification runs on 3.14t; failures are resolved or specifically ruled on by the owner.
12. A maintenance guide explains adding a lesson/page/API, rebuilding, versioning, previews, and fixing drift.

No blanket warning suppression, fabricated execution output, or silent omissions to reach a green build.
Network-dependent external link checks are separated from deterministic content checks and report their
own failures. A prior unsuccessful dependency fetch does not block definition of this blueprint.

## 16. Current Evidence and Remaining Verification
Completed: full 1,081-line README read; reference Sphinx/RTD investigation; 133-file inventory; complete
Beginner/Intermediate/Advanced maps; Expert map lines 1-150; three complete representative scripts;
example structural contract test; current official platform/extension capability documentation.

Not run: Sphinx build and example suite for this design. Earlier dependency installation failed at the
network/proxy layer; its isolated environment is retained under the discovery task. This blueprint
defines the work and gates; it does not claim site implementation, hosting configuration, or release.

Open at execution: compatible pinned dependency set, current per-example correctness, full public API
inventory, RTD project ownership/branch settings, optional custom domain, and exact download build costs.
Resolve each in its assigned story; the four-level hierarchy and prominent examples are already fixed.
