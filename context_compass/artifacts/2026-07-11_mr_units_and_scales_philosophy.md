# MutationResearch: Units and Scales (the group layer philosophy)

- DATE: 2026-07-11
- AUTHOR: mutation_0 (owner-directed: "help me form the philosophy go all out")
- STATUS: RULED 2026-07-11 - sections 1-4.1 stand as drafted (grain laws,
  depth floor, comparison laws, crystal well); sections 5-7 REDRAFTED to
  the owner's GroupNode model (a group IS a node - the draft's
  groups-as-views registry was rejected: "having a concrete node with
  multiple spell_ids makes more sense... you actually get semantic
  behaviours that match our existing behaviours"). Build tracked by
  tickets/epics/2026-07-11_mr_group_nodes_epic.md.
- COMPANION: 2026-07-11_mutation_research_philosophy_v3.md (the record model
  this document extends upward and downward, without changing)

## 0. The Ask

Three questions arrived together and they are really one question:

1. Should the record gain ResearchGroup / ResearchGroupSet - multiple
   objects tracked as a group, mapped into larger units like a cluster, so
   changes can be tracked over a larger area?
2. Where does the MODULE sit in that picture - "the module should also be
   understood, like in the blast radius"?
3. How deeply do we examine things INSIDE the existing object?

The one question underneath: **what are the units of this record, and at
what scale should each kind of question be answered?**

## 1. Two Hierarchies, One Joint

The record has always had two hierarchies pretending to be one.

The LOGICAL hierarchy is about identity - about WHO a thing is over time:
part -> version -> object (lane) -> [the proposed group] -> record.

The PHYSICAL hierarchy is about matter - about WHAT a thing is made of
right now: source text -> top-level part -> module -> module world ->
the shared module space (the union of every recorded world).

They meet at exactly one place: **the version**. A ResearchNode is
simultaneously a point on an object's logical line (a lane node) and a
complete physical world (its custody crystal: modules, sources,
fingerprints, dependency edges). Every read the record offers is a walk
that starts at this joint and moves along one hierarchy or lifts across
to the other:

- `walk`/`history`/`heads` move along the logical axis.
- `source_view`/`module_graph_view` descend the physical axis.
- `impact_view` is the crossing move: it descends to modules, spreads
  through the shared module space, then LIFTS back up to logical truth
  (which spells, which lanes, which campaigns - and with groups: which
  subsystems).

Groups are not a new kind of thing. They are the next rung of the logical
hierarchy, and their entire value is that the crossing move (impact) can
lift one rung higher.

## 2. The Ladder of Units

Each unit earns its place by what it has and what it lacks:

| unit    | has a name? | has an identity? | what it is |
|---------|-------------|------------------|------------|
| part    | yes (def name) | NO             | a named region of one version's text |
| version | NO (sha only)  | yes            | one immutable full-object record |
| object  | yes (lane name)| yes (line of shas) | one identity moving through versions |
| group version | NO (sha only) | yes (content-addressed over members) | one immutable composition snapshot |
| subsystem | yes (lane name) | yes (line of group-node shas) | one composition moving through versions |
| record  | -              | -               | the space all of it lives in |

Two consequences worth stating hard:

- **Parts have names but no identity.** `cast()` in version A and `cast()`
  in version B are not "the same function with two versions" - they are two
  texts that happen to share a name. The record refuses to pretend
  otherwise, which is why surgical synthesis SELECTS parts by name but
  MINTS whole versions (multi-parent nodes) as the recorded outcome.
- **The ladder is self-similar (owner ruling 2026-07-11).** A subsystem is
  not a new kind of thing bolted beside the record - it is the SAME shape
  one rung up: a group node is an immutable full-composition record
  (identity = content sha over its sorted member spell_ids, exactly the
  discipline the NetworkVersioner already uses for organization
  snapshots), and a lane of group nodes is a subsystem's timeline exactly
  as a lane of spell nodes is an object's timeline. Same LAWS - lane,
  journal, twin, forward-only history - carried by a NEW NODE TYPE (owner
  correction: GroupNode is its own class, ResearchNode untouched), with
  the carrying code EXTENDED for it and grouped behavior arriving through
  a new strategy system.

## 3. The Grain Laws

The center of this philosophy. Every question a user or agent asks the
record has a NATURAL GRAIN, and the record must answer each question at
its own grain - never coarser (that loses the answer) and never finer
(that fabricates precision the substrate cannot honestly support):

- **Change is measured in PARTS.** The smallest thing an agent
  deliberately edits is a function or class. Diff and synthesis speak
  parts. (Statement-level change tracking is a compiler's business, not a
  record's.)
- **Identity is measured in OBJECTS.** The lane is the unit of "what is
  this thing over time". Residence, ancestry, join/archive - all
  object-grain.
- **Impact is measured in MODULES.** Python's import system makes the
  module the only honest consequence boundary: a module either is or is
  not in a world; a world either does or does not touch it. Any
  finer-grained impact claim ("only callers of cast() are affected")
  requires call-graph inference, which in Python is a guess - and the
  record NEVER GUESSES. This answers the "how deep do we examine" question
  from the impact side: we examine down to parts for composition, but we
  claim consequences only at module grain.
- **Comparison is measured in FULL MODULE TEXT.** When the record diffs
  two versions, the unit of comparison is the whole module's recorded
  text - synthetic and user-retained alike - never just the bound
  object's class text. The bound object is WHY the version exists; the
  module is WHAT the version is. An agent reading a string diff must see
  the imports, the module-level constants, the neighbor functions - the
  full physical context the change lives in - and may then NARROW to
  parts (structural diff) by choice. Owner ruling 2026-07-11: "we just
  want to see the full module, not just the class, when we track the
  string diffs, if the agent wants it."
- **Diffs read RECORDED text only - never the live disk.** Both sides of
  a version comparison would resolve the same module path to the same
  present-day file; a "diff" through the disk compares a thing with
  itself and lies about both versions. Live disk belongs to source_view
  and drift (present-tense questions); comparison is a past-tense
  question and custody is its only honest witness. Where recorded text
  is absent on a side, the diff says so (fingerprint-only rows), it does
  not improvise.
- **Work is measured in GROUPS.** Agents do not work on one object; they
  work on an area - "the persistence layer", "the diff family". The group
  is the unit of workspace selection, of "what happened here lately", and
  of "can I change things here without hurting elsewhere".
- **Intent is measured in CAMPAIGNS.** Already shipped, and deliberately
  ORTHOGONAL to groups: a campaign is WHEN/WHY (a stamp on work as it
  happens, crossing any structure); a group is WHERE (a structural claim
  that outlives any one effort). A campaign can cross groups; a group
  hosts many campaigns. The record can join them ("campaign apollo's
  activity inside group auth") precisely because neither owns the other.

## 4. Depth of Examination (the inside of the object)

How deep should the record understand one version?

- Depth 0 - identity: the sha. (shipped)
- Depth 1 - the world: module targets, dependency edges, load order,
  export surfaces. (shipped: module_graph_view)
- Depth 2 - the module: source text, sealed fingerprint, recorded path,
  drift marker. (shipped: source_view, source_drift_view)
- Depth 3 - the parts: top-level functions/classes, their names, their
  spans, their provenance in synthesis, structural diff between versions.
  (shipped: structural diff, preview defines, StructuralSynthesizer)
- Depth 4 - statements/expressions/call graphs: **deliberately refused.**

The floor is depth 3 and the philosophy says it stays there. Reasoning:
depth 3 is the deepest level at which the record can speak with CUSTODY
AUTHORITY - parts are literally recoverable from recorded text by parsing,
no inference. Depth 4 claims (who calls what, what a change "really"
affects inside a module) require semantic analysis that is unsound in a
dynamic language; putting unsound answers next to custody-true answers
would poison the trust model that makes foresight reads usable. An agent
that wants depth 4 has the composed source in hand - it can run its own
analysis and own the uncertainty.

One deliberate future exception (open direction, not now): a PART
FINGERPRINT INDEX - per-part content shas within each version - stays at
depth 3 (pure parsing, custody-true) while enabling sharper diffs
("which parts changed between these versions" as an index lookup instead
of a text walk). It sharpens CHANGE grain; it must never be sold as
sharpening IMPACT grain.

## 4.1 The Crystal Is the Well (query it directly)

Everything sections 3-4 promise is ALREADY RECORDED in the spell crystal:
synthetic module sources (always harvested), user module sources (opt-in
retention), physical fingerprints, module paths, dependency edges, export
surfaces, load order. The philosophy therefore demands a DIRECT read: one
verb that returns a spell's full MODULE DOSSIER straight off the crystal -
per module: the full text (synthetic or user-retained, labeled by kind),
fingerprint, recorded path, local dependencies and importers, export
surface, and present-tense drift. Today that dossier is smeared across
source_view + module_graph_view + source_drift_view; those stay (each
answers its one question at its one grain), but the agent asking "give me
everything the record knows about this module of this version" deserves
one call. Corollary already implied by the comparison law: the DIFF
MATERIAL resolver must drink from the same well - synthetic AND
user-retained recorded text (found gap: it currently reads synthetic
only, so user-module-backed spells diff as fingerprint-only even when
their full text is in custody) - while refusing the live disk.

## 5. The GroupNode (owner ruling 2026-07-11)

The draft proposed groups as a parallel view registry; the owner rejected
it for the stronger design: **a group IS a node.** "Having a concrete node
with multiple spell_ids makes more sense... you actually get semantic
behaviours that match our existing behaviours - we just extend the code
and provide separate strategies for grouped behaviours."

- **GroupedResearchNode is its OWN NODE TYPE** (owner ruling 2026-07-11:
  "make a GroupedResearchNode, and then extend everything" - NOT an
  optional field bolted onto ResearchNode). A distinct immutable class
  whose record is a COMPOSITION: a pinned list of member spell_ids, its
  own contract, its own describe()/from_payload() (payloads carry
  node_type="group"; untagged payloads hydrate as spell nodes -
  back-compat by absence). ResearchNode is untouched, byte for byte.
  Code duplication between the two node families is ACCEPTED by ruling -
  both options stay first-class; neither is folded into the other. Identity = content-addressed sha256 over the canonical
  sorted member list (the NetworkVersioner identity discipline, applied
  one rung up). No custody crystal exists or is expected for a group
  identity - the group node is PURELY INFORMATIONAL, that is its point.
- **A lane of group nodes is a subsystem's timeline.** The existing lane
  IS the container; nothing new holds groups. Twenty or thirty spells in
  one subsystem = one group node with 20-30 pinned members, living in the
  subsystem's lane.
- **Composition evolves the way everything evolves: forward.** The agent
  iterates - registers spells, keeps ADDING them into the composition -
  and each add mints a NEW group node whose parents point at the previous
  composition (the existing multi-parent machinery, unchanged). Removing
  a member is the same act with a smaller list. History is the lane walk;
  nothing is ever edited.
- **Pinned members + explicit recompose.** A group node pins member
  VERSIONS (that is what makes it a record). "The subsystem right now" is
  a deliberate act: compose a fresh group node from member tips. The
  companion drift read reports where pinned members' lanes have moved
  ("your composition is behind on 2 members") - honest present-tense
  signal, never silent mutation of a sealed record.
- **Single residence untouched.** A group node's content-addressed id
  claims residence like any node; member spells stay resident in their
  own lanes. References, not containment.

## 6. Grouped Behavior = A New Strategy System (mirrored)

GroupedResearchNode is a new type; the code that CARRIES nodes extends to
hold it (lanes accept both node types; payloads carry a type tag;
hydration dispatches on it), and everything a group node DOES gets its
OWN strategy system MIRRORING the normal one (owner ruling: "make a new
strategy system for it if you have one for the normal one") - a
GroupDiffEngine + GroupDiffStrategy family beside DiffEngine +
DiffStrategy, never special cases scattered through existing verbs:

- **Walk / history / heads / join / archive / journal / campaign stamps:**
  free, byte-identical - a group node is a node in a lane.
- **Diff:** a `members` strategy joins the family (source / structural /
  parts / members - the grain ladder complete): diff two group nodes ->
  which members were added, removed, or MOVED VERSIONS; every moved member
  descends into the existing per-spell grains (module text, class code,
  shape) on demand. One verb, four grains, agent's choice.
- **Impact:** a group node's radius = the union of member radii, lifted
  through residency; direction-split (internal vs outbound), CLOSURE (the
  fraction of consequences that stay inside the composition - the
  workspace-safety number) and ADJACENCY (which compositions share
  modules - the coupling map) are reads computed on top. These survive
  from the draft unchanged; they were read math all along.
- **Source/dossier reads:** dispatch on node kind - spell node answers
  from its crystal; group node answers the roster (members + per-member
  summaries) and fans out on request. Custody probes know group ids carry
  no crystal and say so instead of reporting a miss.
- **The twin and the bootloader:** group nodes ride lane payloads, so the
  composition twin, hydration, snapshots, and restore carry them with the
  SAME loop - but the loops' VALIDATORS must be extended, not assumed:
  the MR composition preflight strategy and the restore-engine
  adjudication currently reason "lane-held id -> custody expectations";
  they must learn that group identities are informational (no crystal
  expected, members validated for residence instead). That is the
  bootloader extension, and it is a named build step, not a hope.
  EXECUTED ADDENDA (2026-07-12, owner rulings): the twin carries the
  record as PROPER OBJECTS - MutationResearchCrystal derives flat
  DB-storable rows for BOTH node families from the composition at
  construction (blob and objects cannot disagree; storage maps rows to
  tables; hydration keeps the composition loop). And the DOCKING-LOOP
  LAW, learned from a live bug: configuration activation must CARRY the
  recorded composition forward into its twin - under replace-on-emit,
  an emitter that does not carry what it does not own DESTROYS it; the
  zero-mock rebirth test guards the loop permanently.

## 7. What Group Nodes Are NOT

- Not custody: a group id has no crystal and never will; members keep
  their own custody untouched.
- Not runtime clusters: melder's conduit clusters are live topology;
  compositions are recorded identity. A composition may be INSPIRED by a
  cluster (open direction), but the record never binds to runtime state.
- Not merge scopes, not execution units: joining lanes, binding, and
  promotion stay per-spell acts; a group node never executes, never
  binds, never gates. PURELY INFORMATIONAL is the design law, owner's
  words.
- Not ACLs, not ownership, not review gates. Maybe someday; not by
  default and not silently.

## 8. The Agent Story, Restated as a Session

An agent lands in a room and asks what exists: the lanes list shows
"persistence" (a subsystem lane whose tip is a group node pinning 24
members). It reads the composition: the roster, each member's lane state
and type. It asks whether the area is safe: closure on the tip -> 0.93,
leaking through pkg.shared.codec toward "diff-family"'s composition. It
asks what has been happening: walk the subsystem lane -> three
compositions this week, plus the members' own histories one hop away. It
asks what moved underneath: composition drift -> two pinned members'
lanes have new tips; it recomposes deliberately, minting the next group
node with parents pointing home. It works: source, parts, preview,
synthesize on members - every change it mocks reports impact lifted to
composition grain ("this escapes your workspace"). It finishes
and the record kept the whole story without the agent ever naming a module
by hand. That is the test: **an agent should be able to choose WHERE to
work, know WHAT happened there, and see what its change DOES to everyone
else - in group-grain verbs, with custody-true answers.**

## 9. Open Directions (recorded, not promised)

- Part fingerprint index (depth-3 sharpening of change grain; never sold
  as impact).
- Group nesting (membership entries typed lane-ref | group-ref).
- Cluster-derived group suggestions (runtime topology as a HINT for
  curation, never a binding).
- Group-aware policy (lane-type census gates, group-scoped campaign
  requirements) - only after the view layer proves itself.
- Impact-grain refinement IF Python ever gives an honest sub-module
  boundary (unlikely; recorded for completeness).

## 10. Where the Truth Lives

This document: the unit/scale laws and the group design frame. The record
model beneath it: 2026-07-11_mutation_research_philosophy_v3.md. The
build contract, when the owner rules: the mr_research_groups ticket.
