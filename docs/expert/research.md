# Read versions, residency, and recorded code

Prerequisites: [recording setup](persistence.md) and [room authority](agent-rooms.md).
MutationResearch organizes version history. A `ResearchSet` has its own lanes,
residency, journal, and snapshots; another set can investigate the same live world
without sharing that organization.

## Separate place, lifecycle, and purpose

Lane state answers whether the lane is open, joined, or archived. Lane type names
the kind of work. Residency identifies the lane holding a declared version inside
one set. A campaign attributes work across lanes.

The campaign lesson demonstrates an important default: an omitted campaign on an
eligible write inherits the ambient campaign. Clear it to stop that attribution.
An omitted campaign on a history query instead leaves the read unfiltered.

## Read at the grain of the question

| Question | Starting read |
| --- | --- |
| What happened recently? | `research_recent` |
| Where is this version recorded? | `research_residency` |
| What code was recorded? | `research_source` |
| What is in one module? | `research_module` |
| Which top-level pieces exist? | `research_parts`, then `research_part` |
| What changed between versions? | `research_diff` or `research_part_diff` |

Comparisons use recorded material so two versions can remain distinct. Current
disk text cannot stand in for both versions of a historical diff. Select the
strategy explicitly when text, structural shape, and individual parts would answer
different questions. Foresight reads require custody to be available.

Room commands operate over their supported set surface. The plural-set lesson
uses the public MutationResearch/ResearchSet APIs to select independent sets
explicitly; do not assume every room command accepts `set_name`.
