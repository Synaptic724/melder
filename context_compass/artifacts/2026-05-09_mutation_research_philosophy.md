# Mutation Research Philosophy

## Metadata
- Artifact ID: ART-2026-05-09-mutation-research-philosophy
- Parent Epic: EPIC-2026-05-03-general-open-questions
- Status: superseded (archived 2026-07-11; owner-directed salvage read done)
- Superseded-where-conflicting by: `2026-07-01_mutation_research_philosophy_v2.md` (2026-07-01 tool-model refinement;
  that document wins on any disagreement)
- Superseded outright by: `2026-07-11_mutation_research_philosophy_v3.md`
  (the canonical model of the BUILT system; the salvageable unbuilt ideas
  from this document - surgical synthesis, runtime recomposition, and the
  blast-radius promotion policy - are recorded there as Open Directions;
  MutationConduit/MutationFrame were ruled out; the module-integrity goals
  now live in custody fingerprints + the impact engine)
- Created: 2026-05-09T10:31:56Z
- Updated: 2026-07-11T19:45:00Z

## Purpose
Capture the current forward mutation-research philosophy in one durable
artifact instead of leaving the newer lane/head/index/merge model only in
conversation fragments.

This artifact is intentionally broader than `IMPORTANT_CONSIDERATION.md`.
That artifact remains the narrow pressure file for mutation semantics around
forks, non-active versions, and what may be linked or melded.

This artifact is for the larger structure:
- what a mutation node is
- how lanes and heads work
- why snapshots matter more than diffs
- how `SpellIndex` relates to MutationResearch
- how structural diffs, surgical mutation, merge, rebase, prune, collapse,
  and runtime recomposition fit together

## Core Thesis
MutationResearch is the runtime-native research/history structure for evolving
object systems.

It is not:
- Git with different names
- diff-first source control
- a passive audit log

It is:
- a graph of candidate runtime futures
- built from full snapshots
- organized into research lanes
- converged through merge/rebase/surgical mutation
- promoted into authoritative runtime heads when accepted

The important rule is:
- each meaningful mutation result is a whole structural candidate
- not just a text patch

## Module Integrity And Module Versions
MutationResearch needs an explicit module-integrity rule because Python class
behavior is not isolated from module context.

This is the key world-first problem:
- a spell may target one class
- but that class may depend on module-local truth
- and module-local truth may be shared with other spells in the same module

So mutation cannot be understood only as:
- "did the target class change?"

It must also ask:
- "did the shared module world change in ways that affect other spell-facing
  surfaces?"

### Why modules matter even when classes are the mutation targets
In Python, a class may depend on:
- module attrs/constants
- module helper functions
- module imports
- sibling classes
- names captured through the defining module namespace

And importing modules may keep old references alive after a module is changed.

That means:
- one class mutation can change shared module truth
- sibling spells in the same module may be impacted even when they were not the
  declared mutation target
- the same canonical module name cannot cleanly host many active published
  versions at once in the normal import world

So the system must separate:
- spell mutation truth
- module version truth
- active published module-world truth

### What the current class `spell_id` is and is not
The current class `spell_id` remains useful, but it is not enough for module
integrity.

It is:
- a spell-facing structural fingerprint
- good for deciding whether a specific class/method/function binding changed

It is not:
- a full module hash
- a full module provenance/version key
- a complete detector of module-context behavior change

This matters because module-level helper or import changes can alter runtime
behavior without changing the target spell fingerprint.

### Module version SHA256
MutationResearch therefore needs module versions with their own SHA256
integrity/version identity at full-module-text scope.

That module SHA should answer:
- what exact module text version did this mutation produce?

This is a different question from:
- what exact spell-facing class fingerprint does this target produce?

So the split should be:
- spell fingerprint
  - spell-facing mutation identity
- module version SHA
  - software-truth / module-integrity identity

The important point is:
- text is version content
- SHA is version fingerprint
- neither alone is the whole conceptual module lineage

### Spell-to-module association
The important association rule is:
- spells associate to modules by module-version identity
- not by canonical module name alone

That means a spell-facing surface should be understood as attached to:
- one spell lineage/version identity
- one module lineage
- one concrete module version SHA

The canonical module name still matters for publication and import semantics,
but it is not enough to identify which exact module world a spell came from.

This is necessary because:
- the same conceptual module name may have many candidate versions
- classes in that module may depend on module-local helpers, attrs, imports,
  and sibling spell surfaces
- a spell can remain in the same spell lineage while the module world behind
  it changes

So the clean statement is:
- module name is the publication/import handle
- module version SHA is the concrete software-truth association
- spell lineage/version sits above that and points into it

### Stable conceptual module identity
The system should treat the conceptual module as something that persists across
many versions.

That means we need to think in terms of:
- one conceptual module lineage
- many candidate or historical module versions under that lineage
- one currently active published module world for the canonical module name

This is a lighter version-control story than full object mutation, but it is
still real version control.

### Restricted and unrestricted module mutation modes
The system should explicitly allow two different mutation postures:

#### `restricted_module_mutations`
This is the safe default.

Rules:
- one active published module world per canonical module name at a time
- candidate module versions may exist before promotion
- AST/module-integrity sweep is required
- target-only promotion is blocked when sibling or unknown blast radius is
  detected
- import consistency is preserved through the canonical module name

Why:
- safer
- easier to reason about
- better for preserving module integrity when many spells share one module
- cleaner snapshot/bootstrap story

#### `unrestricted_module_mutations`
This is the faster, riskier research mode.

Rules:
- module mutation does not have to stay under the same canonical module name
- candidate module versions may be renamed and republished
- AST/module-integrity sweep is not required by default
- the mutation result itself may become the source of truth for that lane
- multiple active module versions can coexist when they no longer collide on
  published module name

Why:
- much faster iteration
- easier to keep many competing module worlds alive at once
- useful for aggressive research/refactor workflows

Risks:
- weaker integrity guarantees
- import rewrites or aliasing may be needed
- spell-binding coexistence becomes more complex
- snapshots/bootstrap become more dynamic and less canonical

This mode should be treated as:
- explicit
- opt-in
- research-oriented

not as the safe default for ordinary mutation work.

The practical difference is:
- restricted mode favors consistency and integrity analysis
- unrestricted mode favors speed and experimentation

So unrestricted mode is faster iteration, but riskier by design.

### One active published module world per canonical module name
Under `restricted_module_mutations`, the safe baseline is:
- one active published module world per canonical module name at a time

This does not forbid many candidate module versions from existing.
It means:
- only one version should occupy the active published import world under the
  canonical module name

Why:
- import consistency should remain stable
- class/function/module globals depend on a specific module namespace world
- simultaneous active published versions under one name would make that world
  incoherent

### Candidate module versions are allowed
The restriction above is only about active published truth in restricted mode.

The system should still allow:
- many candidate module versions in research
- many candidate spell mutations that point into those candidate module worlds
- retention of rejected or unpromoted candidates for later comparison

So when a mutation happens, the new module version can exist immediately as a
candidate even though:
- the active module head has not moved
- the active spell heads have not moved

### Shared-module mutation baseline
If a module contains many spell-facing classes, the safe baseline should be:
- one active mutation lane per module lineage at a time

This does not mean:
- one mutation in the whole system

It means:
- one active mutation campaign for one shared module world

because:
- multiple simultaneous spell mutations inside one shared module are likely to
  step on the same module truth
- sibling classes can be impacted accidentally
- import/global/module-context collisions become much harder to classify

Parallel mutation is still fine across:
- different modules
- different module lineages
- different conduit/world slices that do not share the same active module truth

Under `unrestricted_module_mutations`, parallel work may also keep multiple
live module versions active at once, but those versions must no longer be
treated as sharing one canonical published module-name slot.

### Authoring guidance for integrity
The runtime can support shared modules, but the safest authoring template is
still:
- one spell per module when possible
- one class per file when practical
- minimal module-level helper/attr/import state when the file is expected to
  participate in mutation-heavy workflows

This is guidance only.
It is not a forced global rule.

The reason it helps is simple:
- fewer shared surfaces means less blast radius
- fewer sibling spell surfaces means clearer integrity sweeps
- fewer module-level helpers/attrs means fewer hidden behavior changes that do
  not show up in one class fingerprint

So the practical guidance is:
- shared modules are supported
- but mutation integrity is strongest when files are narrow and spell-focused

### Candidate module version flow
When a spell mutation changes code inside a shared module:
1. create a candidate module version
2. compute its full-module SHA256
3. create any candidate spell versions implied by the mutation
4. keep the active module head unchanged until integrity review completes
5. keep active spell heads unchanged until integrity review completes

So a mutation can create:
- a new candidate spell version
- and a new candidate module version

without immediately promoting either one into the active world.

### Module integrity sweep
If one module contains multiple spell-facing classes, mutation should not
assume that changing one target spell changed only that spell.

The system should run a module integrity sweep:
1. identify all spells sourced from the mutated module
2. recompute spell fingerprints for those spells
3. diff old module text and new module text
4. detect whether sibling spells changed too
5. detect whether module-context truth changed in ways that can affect those
   spells
6. classify blast radius

### What the sweep is really checking
The sweep is not trying to solve perfect Python provenance.
It is trying to answer the practical integrity question:
- did the mutation stay inside its declared target set?

That means the sweep should check at least:
- target spell fingerprint changed or did not change
- sibling spell fingerprints changed or did not change
- module-level helpers/imports/attrs changed
- whether those changed module elements are referenced by target or sibling
  spell surfaces

### AST as the first practical tool
AST is likely the right first tool for the integrity sweep.

Why:
- spell mutation is class/object-facing
- but module integrity depends on shared module surfaces
- AST can map:
  - top-level classes
  - top-level functions
  - top-level assignments/constants
  - imports
  - which names are referenced inside class methods

So the integrity sweep can use AST to answer:
- which module-local things changed?
- which spell-facing classes reference those things?
- whether a sibling spell is impacted even when its own class fingerprint did
  not move

This is probably the best practical v1 mechanism.

### Blast-radius classes
Useful outcome classes are:
- `target_only`
  - only the intended spell changed
- `sibling_spell_impact`
  - one or more other spells in the same module also changed
- `module_context_impact`
  - helper/import/attr/module-level context changed in ways that may affect
    spell integrity even if a sibling spell fingerprint did not move
- `mixed`
  - sibling spell and module-context impact are both present
- `unknown`
  - current analysis cannot prove whether sibling/module impact occurred

### Promotion rule for shared modules
The current safe rule is:
- target-only promotion is allowed only when module integrity says the mutation
  stayed inside the declared target set

If the integrity sweep detects sibling impact:
- the target-only mutation is rejected or widened-review-required
- no active spell head moves yet
- no active module head moves yet

At that point the agent must either:
- narrow the change until only the declared target spell changes
- or explicitly widen the mutation set to include the impacted sibling spells

If the integrity sweep says `unknown`:
- keep the candidate module version
- keep the candidate spell version
- do not promote target-only mutation yet

This keeps candidate work possible without pretending unknown blast radius is
safe active truth.

Under `unrestricted_module_mutations`, that strict promotion rule can be
relaxed because the lane explicitly accepts faster iteration with weaker module
integrity guarantees. In that mode, the cost is pushed onto:
- later validation
- orchestration awareness
- snapshot/rollback discipline

So the mode split is:
- restricted: slower, safer, integrity-first
- unrestricted: faster, riskier, iteration-first

### What happens when sibling spells are intentionally widened
If the agent decides the blast radius is acceptable and wants to widen the
mutation set:
- the mutation becomes a coordinated mutation over the impacted spell set
- all declared impacted spells may notch forward together
- the candidate module version can then promote as the module truth that backs
  that coordinated spell change set

This is the clean way to avoid lying about target-only mutation when the module
world actually changed more broadly.

### What the system should not do
The system should not:
- silently move unchanged sibling spells onto a new module world
- silently promote unknown-impact module versions
- pretend module-local helper/import changes do not matter because the target
  class fingerprint changed cleanly
- allow many active published module versions under the same canonical name

### Practical summary
The safest practical model is:
- classes/methods/lambdas remain the mutation targets
- modules are the software-truth containers those mutations depend on
- module versions get full-module SHA256 integrity/version control
- one active published module world exists per canonical module name
- candidate module versions may exist before promotion
- every shared-module mutation runs a module integrity sweep
- target-only promotion is blocked when sibling or unknown blast radius is
  detected

That is the current best world-first rule set for shared-module mutation.

## Why It Is Not Git
There is one narrow similarity to Git:
- a new version exists as a node
- heads move
- merges create new nodes

That is where the similarity stops being useful.

Git is fundamentally:
- file/tree history
- diff ancestry
- human-facing source control

MutationResearch is fundamentally:
- runtime/object history
- full snapshot comparison
- agent-facing system evolution

Git asks:
- what source changed?

MutationResearch asks:
- what system future exists now?
- which candidate future should dominate?
- what structural parts from one future should move into another?

## Snapshot-First Model
The central design rule is:
- nodes are full snapshots, not diff chains

That means:
- a node contains the whole relevant state for that mutation result
- later nodes do not need earlier diffs replayed to make sense
- any two nodes can be compared directly
- pruning one node removes one candidate snapshot, not the meaning of every
  later node

This gives the system several benefits:
- restore and inspection are simpler
- agents reason over whole candidates instead of patch ancestry
- historical nodes can be merged or surgically mined without caring whether
  they are directly adjacent in a diff chain
- the graph becomes a research structure instead of a patch ledger

## Mutation Creates A New Spell Immediately
When mutation produces a new result, it builds a new `Spell`.

That means immediately:
- a new concrete `spell_id` exists
- that `spell_id` is a SHA256-backed snapshot identity
- the new version can be referenced, inspected, diffed, merged from, tested,
  or projected into runtime surfaces right away

So promotion does not create the version.
Promotion decides what that version means:
- lane head
- dominant head
- authoritative runtime future
- superseded or pruned candidate

## SpellIndex Is A Runtime Index, Not Research Truth
`SpellIndex` still matters because runtime work needs a resolvable handle.

But `SpellIndex` is not the main mutation authority; it only holds the active
selected spell.

The split is:
- `MutationResearch`
  - version/history/research truth
  - lane structure
  - heads
  - merge/rebase/collapse decisions
- `SpellIndex`
  - a stable index (ULID) that categorizes and targets spells
  - holds the one active selected spell as the live runtime handle

This is why many `SpellIndex` entries are acceptable:
- multiple research lanes can exist against the same conceptual object
- each may need its own index holding its active selected spell
- the version history lives in MutationResearch, not in the index; the index
  only carries the currently selected spell

## Lanes And Heads
The meaningful structure is:
- one conceptual mutation/research lineage
- many research lanes
- one active head per lane
- one or more dominant/authoritative lanes depending on policy

Useful lane roles include:
- dominant lane
  - the current preferred future for a conceptual object or object cluster
- experimental lane
  - active research path exploring another future
- merge lane
  - temporary convergence space when combining other lanes

The important rule is:
- "one head" applies per lane
- not globally for every candidate future in the system

## Multi-Agent Use
MutationResearch is explicitly meant for collaborative research over large
systems, not just one user mutating one object.

At scale:
- hundreds or thousands of objects may be in play
- dozens of agents may be working together
- multiple agents may contribute to one broader mutation campaign
- multiple lanes may coexist for one conceptual object or object cluster

The graph exists to make this manageable:
- parallel candidates exist without collapsing into one mutable mess
- candidates can be tested independently
- later they can converge into new authoritative futures

## Structured Diff Instead Of Raw Patch Thinking
At base, diffs are still string diffs.

But the useful layer is structural mapping around Python object systems.

The system should map changes around:
- objects
- classes
- methods
- attributes
- docstrings
- comments

So the operative view is:
- raw string diff is the transport layer
- structural member/object diff is the reasoning layer

That means agents can ask:
- which methods changed?
- which attrs changed?
- which docs/comments changed?
- which object surfaces moved or diverged?

instead of living inside patch hunks.

## Surgical Mutation
"Cherry-pick" is the familiar term, but the better native term is:
- surgical mutation

The flow is:
1. diff two nodes
2. produce a structured report of changed methods/attrs/docs/comments
3. let the agent choose what stays and what goes
4. synthesize a new merged node from those structural selections

This is the right fit for a snapshot/object system because the useful unit is:
- named structural parts
not:
- diff hunks alone

## Merge
Merge must create a new node.

It must not:
- rewrite an existing node
- pretend the merged state already existed

Why:
- the merge result is itself new truth
- provenance must remain explicit
- parentage and convergence must be visible in the graph

So a merge node:
- points back to the participating lane heads or historic nodes
- contains the merged snapshot state
- may later become a lane head or dominant head

## Historic Node Merge
Because nodes are full snapshots, merges do not need to be limited to direct
branch heads.

The system can:
- diff any two meaningful nodes
- compare historic candidates
- selectively merge from old nodes into a new future
- preserve that as a fresh node

This is one of the strongest differences from strict diff-ancestry models.

## Rebase
Rebase still makes sense, but it is not patch replay in the Git sense.

In this system, rebase is closer to:
- choose another base
- synthesize a new derived snapshot on top of it
- then collapse or supersede the old path if desired

Because snapshots are whole-state candidates, rebase is more about:
- recomposition on a new base
than:
- replaying fragile text patches

## Prune And Collapse
Pruning and collapse are normal operations here.

Because nodes are full snapshots:
- pruning removes one candidate state
- not the meaning of all later states

This makes pruning useful for:
- clarity
- lane cleanup
- reducing irrelevant history
- keeping the research graph understandable

Collapse is the stronger operation:
- many exploratory nodes can be folded into a smaller retained structure
- one or a few authoritative results survive
- the rest become unnecessary research history

The key reason to prune/collapse is not storage.
It is intelligibility.

## Runtime Recomposition
One of the most important future runtime operations is dynamic recomposition.

The intended shape is something like:
- `conduit.mutation_recomposition(obj, target_object)`

Meaning:
- take one current live object
- take one target structural reference/template
- move or reapply compatible state into the new structural shape
- let the runtime adopt the recomposed result

This is not:
- a text merge
- or blind in-place object surgery

It is:
- runtime structural evolution through explicit recomposition

This is why whole-snapshot nodes make sense:
- each node is a complete candidate structural future
- recomposition can choose between complete futures

## Relationship To Crystallizer And Synthetic Modules
MutationResearch is not the same thing as Crystallizer, but they fit together.

The rough split is:
- `SyntheticModule`
  - live in-memory module embodiment
- `SpellCrystal`
  - durable module/source/dependency truth
- `MutationResearch`
  - lane/head/history authority for runtime futures

The mutation surface currently makes the most sense on:
- classes
- objects
- spell-facing capability surfaces

not on raw module namespaces as the primary unit.

That is a useful constraint:
- modules are software truth
- classes/objects are mutation truth

## Relationship To Snapshots And Bootstrap
MutationResearch does not replace system snapshots.
It interacts with them.

Snapshots can carry:
- the relevant spell/module world
- lane/head references
- optional mutation manifest state
- enough context to rebuild the world coherently

That means MutationResearch contributes to:
- what future was active
- what candidate lanes existed
- what should be restored or promoted later

without needing to become the entire bootstrap system itself.

## Workspace And Promotion
The system likely needs to separate:
- live mutable workspaces/labs
- promoted immutable history nodes

The authoritative research/history structure should be built from immutable
snapshot nodes.

Live work can still happen in more fluid workspaces, but once the result is
recorded as a mutation step:
- it becomes a concrete spell snapshot
- with a concrete SHA256 identity
- that the graph can reason about explicitly

Promotion then does not create the version.
Promotion:
- moves lane authority
- advances heads
- and later may trigger recomposition into live runtime truth

## Community And Enterprise Topology
The archived MutationResearch bundle already covers:
- safe lane vs mutation lane
- workspace-first mutation
- control-plane gates
- lifecycle stages
- community vs enterprise topology

This philosophy does not replace those.
It extends them with the newer graph/lane/head/snapshot structure.

So the current combined understanding is:
- workspace/lab first
- explicit mutation lane
- immutable snapshot nodes for concrete mutation steps
- many lanes
- one head per lane
- merge/rebase/surgical mutation over snapshots
- later runtime promotion/recomposition

## What This Is Not Trying To Solve Yet
This philosophy does not finalize:
- exact runtime APIs
- exact lane metadata fields
- exact merge conflict UI/report format
- exact live-object migration hooks
- final dominance rules across many lanes

It does establish the model strongly enough that later implementation can stop
thinking in Git/file terms and start thinking in runtime/object terms.

## Runtime Surface Direction
The public runtime mutation interaction surface should move up above `Spell`.

This does not mean:
- put everything directly on the already-large `Conduit`

It means:
- `Spell`
  - keeps low-level mutation primitives and spell-owned state changes
- higher mutation runtime surfaces
  - orchestrate transactions, gates, and coordination

This is the cleaner split because:
- spell-owned helpers are not the same thing as runtime mutation operations
- spell mutation may need transaction/gate/embargo semantics
- conduit- or frame-scoped mutation work should not be reduced to local spell
  helper calls

### Spell still matters
`Spell` should still own the smallest mutation mechanics, likely as private or
low-level helpers:
- persistent overlay apply/clear
- live contract mutation helpers
- spell-owned `CreationContext` cleanup
- structural dirty marking

But the public runtime interaction should sit above it.

## Move MutationResearch Up First
The first implementation-order rule is:
- move `MutationResearch` out of frame-local ownership and up toward `Aether`
  first
- only then build the richer runtime mutation surfaces

Why:
- the current code still hosts `MutationResearch` under `AethericFrame`
- the broader design direction now treats mutation truth as larger than
  frame-local ownership
- if runtime mutation facades are added before that ownership move, they risk
  wiring themselves to the wrong root

So the order should be:
1. lift MutationResearch toward Aether-level ownership
2. keep conduit/frame mutation facades thin and orchestration-only
3. then widen the runtime mutation APIs

## MutationConduit
`MutationConduit` is the current best name for the conduit-scoped mutation
runtime surface.

It should be:
- available only when dynamic mode is enabled
- linked back to:
  - the underlying `Conduit`
  - `MutationResearch`
  - `SpellSystemStates`
  - `ChangeControlManager`
  - spell-index creation-gate control

It should not:
- become the owner of those systems
- replace `Conduit`
- absorb all MutationResearch semantics into itself

Its job is orchestration:
- begin/end mutation transactions
- close/drain/reopen the targeted spell-index gate
- coordinate declaration mutation or other spell/index mutation work
- clear spell-owned runtime shape at the right time
- synchronize change-control and spell-system-state updates

This makes `MutationConduit` a mutation-facing conduit facade, not a second
runtime root.

## MutationFrame
`MutationFrame` is more tentative.

Current direction:
- it does **not** own conduits
- it is a frame-scoped mutation transaction/orchestration surface
- it exists only if frame-level mutation operations prove real enough to need
  one explicit facade

Possible uses later:
- coordinate broader frame mutation transactions
- synchronize many conduit- or spell-index-level mutations together
- manage noisier or more chaotic frame-scoped mutation campaigns

But this is explicitly still a go/no-go question.

The important rule is:
- do not pretend `MutationFrame` is mandatory yet
- define it as a possible future frame transaction surface only

## Transaction Layering
Different mutation classes should live at different runtime transaction scopes.

### Spell / SpellIndex transaction
This is the smallest practical mutation scope.

Good fit for:
- declaration-surface mutation such as live `MutationContract` edits
- other spell/index-local structural mutation work

Expected responsibilities:
- close targeted spell-index gate
- wait for active formation to drain
- mutate live declaration/runtime state
- clear spell-owned `CreationContext`
- mark the spell/index structurally dirty
- reopen the gate

### Conduit transaction
This is the current best general mutation runtime scope.

Good fit for:
- many spell/index mutations together
- conduit-local orchestration
- operations that need change-control admission and gate coordination

### Frame transaction
Tentative broader scope.

Good fit later only if needed for:
- many conduit-local changes moving together
- higher-chaos mutation operations that exceed conduit-local scope

## Gate Granularity
The important gate distinction is:
- not conduit-wide gate by default
- spell-index / creation-context gate for spell-local mutation work

This matters because the target is:
- stop new formations of the affected spell/index
- wait for current formation work to drain
- mutate safely

That is a finer-grained operation than closing the whole conduit.

## Overlay Mutation Versus Declaration Mutation
The current model should keep two different mutation classes visible:

### Persistent overlay mutation
- `mutation_override`
- persistent spell-level overlay
- still different from one-call `spell_override`

### Declaration mutation
- live `MutationContract` edits
- mutate the live declaration object in memory
- stronger and more durable than overlay state

The runtime transaction burden may differ between these classes, but the
important point is that they should not be conflated.

## Summary
In one sentence:

MutationResearch is a snapshot-first runtime research graph for evolving object
systems, where concrete mutated spells exist immediately as SHA256 snapshots,
many research lanes can coexist with their own heads and runtime index handles,
structural diffs enable surgical mutation and merge/rebase over whole-state
candidates, pruning and collapse preserve clarity, and later promotion plus
runtime recomposition turn selected futures into the living authoritative
world, while future runtime surfaces like `MutationConduit` and a tentative
`MutationFrame` orchestrate mutation transactions above spell-local helpers
after MutationResearch itself moves up toward Aether-level ownership.
