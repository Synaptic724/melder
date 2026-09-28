# Melder — Ordered Cleanup, Read the Docs, and Release Automation

This release brings three major improvements to Melder: predictable disposal ordering,
a new documentation site built around practical examples, and a more rigorous path from
development to tested Python packages.

## Predictable disposal ordering

Disposal methods now run in the order you declare them. That order is preserved from
Spellbook configuration and binding through creation, runtime cleanup, and Crystallizer
recording and replay.

- **Per-spell control:** each binding keeps its own disposal methods. Configuring one spell
  does not silently configure later bindings.
- **Spellbook-wide policy:** matching methods from `SpellbookConfiguration` form an ordered
  block alongside the spell's own methods.
- **Configurable priority:** by default, spell-only methods run first and the Spellbook's
  block runs last. `with_enforce_priority_disposal_methods(True)` moves the book's block first.
- **Deterministic overlaps:** shared names belong to the Spellbook block and follow its order.
  Duplicate names execute once, and names that do not match are omitted.
- **Resolved at bind time:** matching and composition happen once when the Spell is created,
  rather than being rediscovered during every cleanup.

For example, if a spell declares `flush, close` and its Spellbook declares `close, shutdown`:

```text
Default:       flush → close → shutdown
Book priority: close → shutdown → flush
```

The change preserves the existing teardown order between objects and scopes. It makes the
method sequence within each creation explicit, without redesigning the overall cleanup cascade.
Existing failure handling remains: a failing method stops that object's remaining methods,
while cleanup continues with other objects and aggregates failures.

Configuration transport, compiled creation paths, cache hydration, Crystallizer restore,
and SpellIndex grafting were updated and tested against the ordered contract. Restore applies
the receiving Spellbook's policy through the normal binding path.

## A new Read the Docs experience

Melder now has a dedicated documentation site with four learning levels:
**Beginner, Intermediate, Advanced, and Expert**.

The site brings together:

- **133 example lessons** connected to their runnable source, with individual and collection downloads.
- Guided chapters that take readers from basic binding and lifetimes into composition,
  Nexus, Rift, Crystallizer, and MutationResearch.
- API reference material, architecture diagrams, configuration guidance, a glossary, and troubleshooting.
- A full table of contents, searchable documentation, and a filterable example catalog.
- Improved small-screen navigation, keyboard focus, diagram viewing, and long-code readability.
- Offline documentation builds in HTML, PDF, and EPUB formats.

The documentation build also checks internal links, images, and example-source consistency,
with a maintainer guide covering updates and recovery from documentation regressions.

Start with the [documentation](https://melder.readthedocs.io/en/latest/),
browse the [examples](https://melder.readthedocs.io/en/latest/examples/index.html),
or explore the [full contents](https://melder.readthedocs.io/en/latest/contents.html).

## GitHub Actions and release qualification

The repository now has a structured promotion route:

```text
dev → preprod → release_candidate → prod
```

Reusable workflows separate runtime tests, documentation, source assets, repository assets,
and distribution verification. A central `CI / merge-ready` check evaluates the required
results and branch policy before promotion.

Key additions include:

- **Free-threaded runtime checks** on Linux, Windows, and macOS using Python 3.14t, with
  verification that the actual test process runs with the GIL disabled.
- **Package verification** for wheels and source distributions, including isolated installed-wheel
  checks that exercise the package outside the source checkout.
- **TestPyPI qualification** for the selected release candidate, followed by fresh-install probes
  across all three operating systems.
- **Exact candidate identity checks:** promotion verifies the tested source revision, package
  version, and distribution hashes rather than accepting an unrelated earlier successful run.
- **Fresh final-release checks:** publication reruns qualification and rechecks the release tag
  and current production revision before uploading to PyPI.
- **Explicit retry handling:** existing TestPyPI files must match the expected bytes; different
  package contents cannot be silently accepted under an existing version.

The candidate-proof check now runs at the end of the merge-ready job, after the other required
checks. macOS setup was also corrected so the no-GIL setting applies to qualification steps
without interfering with Python installation tools.

## Regression coverage and maintenance

New coverage exercises disposal ordering through configuration, binding, actual method calls,
compiled paths, cache behavior, and persistence/replay. Workflow tests cover branch routing,
candidate identity, publication guards, and setup behavior. Documentation checks cover builds,
navigation, source-linked examples, and offline outputs.

One intermittent cold-start cluster/revalidation concurrency test is temporarily skipped while
its investigation remains open. This release does not claim a runtime fix for that case.

Together, these changes make cleanup behavior easier to control, Melder easier to learn,
and release artifacts easier to verify before they reach users.
