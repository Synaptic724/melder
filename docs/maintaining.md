# Maintain and publish the documentation

The website is generated from an explicit set of public inputs. The learning order
is **Beginner → Intermediate → Advanced → Expert**; examples stay in their existing
numbered source collections. Full Contents and the sidebar use the same page model.

## Build locally

Use Python 3.14 and an isolated documentation environment. Activate it before the
commands below. Documentation dependencies are separate from Melder's runtime.

```bash
python -m venv docs/.venv
```

On Windows, activate with `docs\.venv\Scripts\Activate.ps1`; on POSIX shells use
`source docs/.venv/bin/activate`. Then install and build:

```bash
python -m pip install -r docs/requirements.txt
python -m unittest discover -s docs/tests -q
python docs/tools/build_docs.py check
python docs/tools/build_docs.py build
python docs/tools/check_site.py
```

Preview the generated site:

```bash
python -m http.server 8765 --bind 127.0.0.1 --directory docs/_build/html
```

The source and HTML directories under `docs/_build` are generated. The builder
validates inputs before replacing its source output and refuses redirected cleanup
paths. Each build also refreshes Sphinx's reference environment so changed API
import paths cannot reuse stale source-page backlinks. Edit canonical inputs, not generated pages.

Local previews include your uncommitted edits, while GitHub source links identify
the checkout's current commit. Qualify the intended committed revision in CI and
Read the Docs before treating that preview as a published release.

## Search metadata and crawler files

The site's short browser-title suffix is `Melder`. Keep visible page headings and the
existing learning structure separate from this suffix.

Descriptions have one source owner:

- Authored Markdown pages use `myst.html_meta.description` in their YAML frontmatter.
- README-derived chapters may set `description` in `docs/curriculum.toml`.
- Saved lessons may set `description` in a `[[lesson]]` override in `docs/catalog.toml`.

When changing a published lesson title, set its previous heading fragment in `legacy_anchor`
so existing deep links still resolve. The target accepts lowercase letters, digits and hyphens.

Generated descriptions must be nonempty strings when supplied. Authored chapters cannot also
declare a manifest description. The generators validate and escape metadata before publishing it;
they retain the canonical prose and downloaded example bytes.

`docs/seo.toml` lists the reviewed pages whose descriptions are required. Add a page there after
authoring its specific summary. Other missing descriptions are warnings, so broader coverage can
grow without treating every unedited reference page as a publication failure.

For a local publication audit, set `READTHEDOCS_CANONICAL_URL` before the HTML build. In PowerShell:

```powershell
$env:READTHEDOCS_CANONICAL_URL = "https://melder.readthedocs.io/en/latest/"
python docs/tools/build_docs.py build
python docs/tools/check_site.py
python docs/tools/check_seo.py docs/_build/html --base-url $env:READTHEDOCS_CANONICAL_URL --policy docs/seo.toml --json docs/_build/seo-report.json
```

On POSIX shells, use `export READTHEDOCS_CANONICAL_URL="https://melder.readthedocs.io/en/latest/"`
and pass `--base-url "$READTHEDOCS_CANONICAL_URL"`. CI supplies this audit base explicitly. Read the
Docs supplies its own version-specific value; do not replace that value in the hosted configuration.

The SEO check validates titles, description ownership, canonical links, sitemap inclusion and
indexing directives. Exit codes are 0 for no policy errors, 1 for policy errors, and 2 for unreadable
inputs. It reports optional descriptions and H1/language conventions as warnings. External RTD
previews may retain intentional `noindex`; other intentional previews use `--allow-noindex`.
The checker reads local HTML/XML only and does not claim Google indexing or ranking results.

Read the Docs already serves the project's `robots.txt` at
`https://melder.readthedocs.io/robots.txt`. Its generated file allows public versions, handles hidden
versions, and advertises the root sitemap. Keep this platform-managed file unless a deliberate
crawler-policy change calls for a custom replacement. A local build need not contain `robots.txt`.
After publication, verify that root endpoint and `https://melder.readthedocs.io/sitemap.xml` return
the intended rules and URLs. Local metadata checks do not verify those remote responses.

## Add a chapter or page

- Add a guide to `docs/curriculum.toml`: its stable page ID, exact learning level,
  title, one authored source or exact README heading, and related lesson IDs.
- Add a standalone reference/support page to `docs/navigation.toml` with one parent.
- Keep existing IDs stable. Add contextual cross-links instead of giving a page
  multiple parents or moving a saved example to a different level.
- The README section selector rejects missing/duplicate headings and preserves code
  fences. A source heading change needs an intentional selector update.

## Add or change a saved example

Keep executable source under `UX_and_AIX_experiences`. Update the corresponding
collection in `docs/catalog.toml`; add editorial title/ID overrides only when useful.
The catalog reconciles every numbered script and includes local Python helper
modules in each collection download.

Keep TIER, GOAL, and SURFACE metadata accurate. Link the lesson from an appropriate
guide through `docs/curriculum.toml`. Guides and lessons receive reciprocal links;
recognized public names in lesson surface metadata also link to the API reference.

Teach human-facing resolution with quoted registered names: `conduit.meld("Service")`.
Keep class/function/object references in registration and returned-object type annotations.
Use `spell_id=` explicitly for machine identities, and retain frame/binding selectors when needed.
When updating a prebuilt or generated-object example, verify its registered name rather than
quoting the local variable that holds it.

Run the applicable existing example harness on **Python 3.14t with the GIL disabled**.
Example execution is separate from Sphinx rendering. Check the asserted result and
handled refusal paths; a passing script is not proof of every historical prose claim.

## Maintain the API and architecture references

`docs/api.toml` assigns every name in the package's literal `__all__` to a topic and
disposition. New or duplicate exports fail the inventory check until that selection
is updated. Returned command/document surfaces are selected explicitly. Autodoc
renders signatures and contracts from the real Python source.

The docstring presentation bridge preserves code while making documented list,
section, and example boundaries valid reStructuredText. Repair an actual source
typo at its source. Do not suppress warnings to make the build pass.

Architecture pages come from `architecture_and_design/manifest.json`. Their prose,
SVGs, and Mermaid companions remain canonical in that collection. Source links
are pinned to the build revision; image/full-size/download links are adapted for
the site. Mermaid source checks normalize Git's Windows line endings; SVG hashes
remain byte-exact. Changed diagrams require the architecture collection's normal
review/render process.

## Build offline formats

```bash
python docs/tools/build_docs.py handbook --builder epub
python docs/tools/install_tectonic.py
python docs/tools/build_docs.py handbook --builder pdf
python docs/tools/build_docs.py archive
```

The installer verifies the official pinned Tectonic archive and places one compiler
under `docs/_build/tools`. An explicit `--tectonic PATH` selects another installation;
an existing `latexmk`/XeLaTeX toolchain is also supported. The normal CI and RTD jobs
use Tectonic 0.17.0. Its initial TeX support download needs network access; the cache
stays under `docs/_build/tectonic-cache`.

The handbook selection is explicit in `docs/handbook.toml`. It contains all guide
chapters, the glossary, and selected full examples. The complete HTML archive
contains the entire site, API references, drawings, and source downloads. Rebuild
HTML before archiving it. Inspect PDF pages and ePub navigation after content or
formatting changes.

## CI and Read the Docs

The reusable docs workflow runs from CI's mandatory `documentation` job. Its result
is included in `CI / merge-ready`; skipped, missing, cancelled, or failed docs
evidence cannot pass that gate. Runtime tests retain their separate workflow.

`.readthedocs.yaml` uses Python 3.14, the same dependency lock, and the same build
commands. Each format is staged into the service's `READTHEDOCS_OUTPUT` directory.
Staging only copies local outputs; it is not an account connection or publication claim.

In the Read the Docs project, verify these settings against the intended repository:

1. Connect `Synaptic724/melder` and choose the public branch for `latest` (`prod` is
   the publication branch used by this repository's source links and promotion flow).
2. Enable a docs-bearing release for `stable`; do not advertise older tags that
   lack buildable docs. Choose the default version after its build succeeds.
3. Enable pull-request previews and review the preview's exact revision.
4. Enable the version/search/notification addons that fit the project. Keep the
   local Sphinx search route available as well.
5. Verify the served canonical URLs, sitemap, downloads, and a representative old-link redirect.

Service settings require access to the actual project. A YAML file cannot establish
ownership, Git integration, active versions, or successful hosted builds.

## Change a published URL

First preserve the old page ID when practical. If a move is needed, add the redirect
in the Read the Docs project only after the destination exists in the supported
versions. Check both the old URL and the destination on the hosted site. Keep the
mapping in the change's review notes; never invent redirects for unknown old pages.

## Recover a failed build

Read the first concrete failure. A missing source, export disposition, changed
diagram hash, broken link, or docstring parse failure needs a source correction.
Dependency or compiler download failures need a working build environment. Keep
those outcomes separate; do not turn a network failure into a content exception.

When source or release metadata changes, run the existing generated-asset checks:

```bash
python src/melder/_build_assets/_build_asset_runner.py --check
python llm_support/_builder.py --check
```

Regenerate stale assets through their existing builders, then rerun the checks.
Do not hand-edit generated manifests or copy broad internal work records into the site.

## Recover a published regression

Record the affected project/version, build ID, and Git commit before changing its
publication settings. Rebuild the last known-good revision in a separate checkout
with the commands above, and run its link and download checks.

For a moving branch, restore the required content through a reviewed recovery
commit and the repository's normal branch promotion flow. For a tagged version,
prepare a corrected release with an accurate version label. Review the resulting
Read the Docs build before changing the default version or redirect destinations.

Check the homepage, Full Contents, a runnable example, an API source link, canonical
URL, and each available download against the recovered build's actual revision.
Keep the failure and recovery build IDs together in the release review so the next
maintainer can establish which site readers received.

Platform references: [configuration](https://docs.readthedocs.com/platform/stable/config-file/v2.html),
[custom builds](https://docs.readthedocs.com/platform/stable/build-customization.html),
[versions](https://docs.readthedocs.com/platform/stable/versions.html), and
[offline formats](https://docs.readthedocs.com/platform/stable/downloadable-documentation.html).
