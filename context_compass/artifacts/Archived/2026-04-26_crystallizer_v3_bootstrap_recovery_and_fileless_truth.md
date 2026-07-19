# Crystallizer V3 Bootstrap Recovery And Fileless Truth

## Metadata
- Artifact ID: ART-2026-04-26-crystallizer-v3-bootstrap-recovery-and-fileless-truth
- Parent Epic: EPIC-2026-04-26-design-crystallizer-asset-provenance-layer
- Status: active
- Created: 2026-04-26T18:25:40Z
- Updated: 2026-04-26T19:17:32Z

## Purpose
Capture the V3 direction for Crystallizer after:
- V1 single-unit `SpellCrystal` storage
- V2 synthetic module graph and requirements semantics

V3 is the layer where the stored graph stops being only preserved truth and
becomes something that can be:
- restored
- loaded into a live world
- bound into Melder
- optionally treated as the primary bootstrap source of a system

This is the first place where the design starts to answer:

**what does it mean for software to live primarily as crystallized graph truth
instead of as userland files on disk?**

## V3 Thesis
Crystallizer V3 should define how crystallized software packages move between:
- stored JSON truth
- live synthetic module graphs
- bound Melder capabilities
- optional file materialization later

That means V3 is not mainly about better storage.
It is about **recovery semantics**.

V3 answers:
- how software comes back from a cold boot
- how synthetic modules are restored into a conduit/world
- how selected exports become spells again
- how a fileless application layer could exist

## Fileless Application Truth
The strongest V3 possibility is:
- external packages remain installed normally
- the application layer itself is not primarily userland files
- the application layer is primarily a crystallized synthetic module graph
- boot means restoring that graph and rebinding it into Melder

This does not mean files are forbidden.
It means files are no longer the only or primary authority.

The core idea is:

**physical files become optional projections of a software graph whose primary
truth may live in Crystallizer.**

That is the real V3 jump.

## What V3 Adds Beyond V2
V2 already says:
- synthetic modules are first-class
- graphs matter
- AST import analysis matters
- a requirements view matters

V3 adds:
- boot semantics
- restore semantics
- binding semantics
- activation semantics
- optional fileless primary truth

So V2 says:
- "what is this software graph?"

V3 says:
- "how does this graph become a living system again?"

## JSON As The Exchange Contract
Crystallizer should not own DB calls, table definitions, or storage-engine
setup.

The exchange boundary should be:
- JSON in
- JSON out

That means:
- export one crystallized package/graph as JSON
- import one crystallized package/graph from JSON
- let external systems decide where that JSON lives:
  - DB
  - file
  - service
  - cache

This keeps Crystallizer clean:
- it defines software graph truth
- it does not become a database framework

## External Table Shapes And Adapters
The concrete persistence expectation should now be stated plainly:

- the user or host system must define the persistence table shapes
- Crystallizer does not create or migrate those tables
- Crystallizer is configured with adapters/callback locations that know how to
  consume and emit those table shapes
- reads happen through explicit calls into those adapters
- writes happen by emitting crystallizer transaction or snapshot objects that
  the adapters persist into the configured table shapes

So the setup burden is:
- define the interfaced tables
- provide the adapter contract
- let Crystallizer consume those tables through that contract

This is the real V3 persistence boundary.

## Dependency Bootstrap Policy
V3 should inherit the V2 dependency direction:

- `uv` is the preferred and fully supported environment recovery path
- `pip` is only a fallback through a user-supplied script/subprocess path
- Crystallizer does not become a package manager
- Crystallizer only needs to know:
  - what the graph requires
  - what environment snapshot or requirement view should be restored
  - which configured adapter to call before module recovery continues

This means a V3 bootstrap flow can include:
1. parse JSON package
2. inspect requirement state
3. call `uv` recovery first when configured
4. fall back to the user-provided `pip` script only when configured
5. continue synthetic-module restoration after environment recovery

## Core V3 Records
Without locking down final implementation names, V3 likely needs these
conceptual records:

### `SpellCrystal`
- one managed code unit
- may represent:
  - synthetic module
  - physical module
  - later perhaps mirrored external authority

### `SpellCrystalGraph`
- one connected synthetic software graph
- roots
- members
- dependency edges

### `BindingSignature`
- how a stored unit becomes a spell again
- what export is bound
- with what spellframe
- with what binding name
- with what existence and permissions

### `BootstrapPackage`
- one import/export JSON package
- enough to reconstruct the graph and its binding plan

## Binding Signatures Matter
V3 is where binding signatures become essential.

It is not enough to restore source text and synthetic modules.
To rebuild a usable world, the loader must also know:
- what modules are support-only
- what modules export runtime capabilities
- what exports should become spells
- how those spell bindings should look

So a crystallized package should not just say:
- "here are the modules"

It should also say:
- "here is how these modules are manifested back into Melder"

That is the missing bridge between:
- synthetic software graph
and
- live spell world

## The Bootstrap Story
V3 introduces an optional crystallizer bootstrap story.

The basic shape is:

1. obtain JSON package
2. parse and validate package
3. reconstruct the synthetic module graph
4. restore modules into a target synthetic module space
5. resolve binding signatures
6. bind selected exports into a target frame/conduit
7. activate the recovered world

This is important because it means:
- a conduit/world can be restored from crystallized truth
- not just from files

## Cold Boot Workflow
One concrete V3 workflow is cold boot.

Story:
- system starts empty or mostly empty
- bootstrap package is loaded
- software graph is restored
- selected exports are rebound into Melder
- the system becomes operational

Important point:
- the restored graph may include software that never existed as physical files

That is the thing that makes V3 powerful.

## Live Restore Workflow
Another V3 workflow is not cold boot, but live restore.

Story:
- a system is already running
- an agent or operator loads a crystallized package
- modules are restored into a target world
- selected exports are bound
- the world gains new capabilities without full reboot

This is important because not every restore is startup.

## Export Workflow
V3 also includes the reverse move:

Story:
- live synthetic modules exist
- selected exports are already bound
- agent or operator wants to preserve the system
- crystallizer exports one JSON package

This package should contain:
- module graph
- source text
- metadata
- requirements view
- binding signatures
- bootstrap metadata

That becomes the durable handoff or persistence artifact.

## Optional File Materialization
V3 does **not** require a fileless world only.
It only says fileless truth is allowed.

So a recovered graph may later be:
- materialized into a real directory tree
- emitted as `.py` files
- turned into a userland package projection

This matters because some users or workflows may still want:
- physical files
- editors
- human inspection
- preproduction promotion through a real project tree

So files become:
- an optional projection
- not the mandatory authority

## What The Loader Actually Does
The loader is the crucial new concept in V3.

Its responsibilities are:
- accept a crystallized package JSON string
- build `SpellCrystal` and graph records
- restore synthetic modules in dependency-respecting order
- resolve and apply binding signatures
- target a chosen frame or conduit
- activate the resulting live capabilities

What it should **not** own:
- persistent DB wiring
- direct package-manager internals
- product workflow policy

So the loader is a **runtime graph recovery operator**, not a package manager.

The same applies to persistence:
- Crystallizer is not the table owner
- Crystallizer is the consumer and producer of adapter-facing records
- the host system is the table owner

## Relationship To External Packages
Even in a fileless or crystal-first application model, external packages still
exist normally.

So V3 assumes:
- external environment support may still come from normal installed packages
- Crystallizer does not replace that
- the application/software graph is what becomes fileless or crystal-first

This is why fileless application truth is plausible:
- you do not need to make the entire world synthetic
- only your own application/software layer

## Why This Is A Big Break
If V3 works, then the system gains a new property:

software can be:
- built dynamically
- persisted as graph truth
- restored into a live runtime
- rebound into the world
- optionally projected back to files later

That is a major break from normal development where:
- files are primary
- runtime is secondary

V3 inverts that:
- graph truth can become primary
- files become one possible projection

## What V3 Does Not Yet Finalize
V3 still does not force final answers for:
- exact local/shared synthetic module scopes
- cycle semantics
- exact file-materialization layout rules
- version conflict rules
- whether one package can be partially restored or only fully restored
- whether all restored exports are immediately bound or selectively activated
- the exact external table schema names and vendor-specific layout

Those remain later design decisions.

But V3 does lock down the right question:

**How does crystallized software become living runtime again?**

## V3 Summary
If V1 is:
- single-unit string truth

and V2 is:
- graph and import truth

then V3 is:
- boot and recovery truth

In one sentence:

Crystallizer V3 should define how a crystallized synthetic software graph moves
from JSON package truth into restored synthetic modules and rebound Melder
capabilities, allowing fileless application truth when desired and optional
file projection later.
