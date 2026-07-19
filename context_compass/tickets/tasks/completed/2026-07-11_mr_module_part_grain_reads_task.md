# Task: MR module/part-grain reads (crystal well: full-module diffs, part diffs, dossier)

## Metadata
- Task ID: TASK-2026-07-11-mr-module-part-grain-reads
- Story: owner ruling 2026-07-11 on units-and-scales decision point 8
  ("the spell_crystal should have the source if its from the physical or
  synthetic and this is what your diffs should be using now... class diffs
  or module diffs and the blast radius of those things... lets fix the
  first thing then discuss the 2nd")
- Status: done (owner-run 3.14t green; closed 2026-07-11T23:20:16Z)
- Owner: cowork
- Agent Name: mutation_0
- Priority: p1
- Created: 2026-07-11T21:30:00Z
- Updated: 2026-07-11T21:30:00Z

## Objective
Make the crystal the single well for every comparison grain:
1. FIX: `_resolve_diff_material` reads synthetic_module_sources ONLY -
   user-retained (physical) module text never enters diff material. It
   must drink both recorded carriers (synthetic first, user fills gaps)
   and keep refusing the live disk (comparison law: both sides would read
   the same present-day file and lie).
2. MODULE DOSSIER: `module_view(spell_id, module_name)` - everything the
   crystal knows about one module in one call (text labeled by kind
   synthetic/user/live_disk, fingerprint, path, deps, local importers,
   export surface, drift).
3. PART READS: `part_view` (one named top-level function/class's text +
   span + carrying module; present-tense, source_view resolution rules)
   and `part_diff` (unified text diff of one named part between two
   versions; RECORDED text only; carries the module-centered blast radius
   automatically - "the blast radius of those things").
4. Rooms: research_module / research_part / research_part_diff - all
   READS, both room types, advertised in the presentation tuples.

## Ticket Contract
- ENTRY_GATE: owner ruling above; philosophy artifact section 3
  (comparison laws) + 4.1 (crystal well).
- EXECUTION_BOUNDARY: mutation_research/** (root + synthesizer public
  extract verb) + both command systems + matching tests (incl. the
  inventory equality test). NO crystallizer edits, NO execute/bind.
- EXIT_GATE: harness green; owner-run 3.14t; docs/graph counts synced;
  boards synced.
- FAILURE_ESCALATION: CONFLICT if part extraction would need custody
  shapes the crystal does not carry.

## Notes
- DATETIME: 2026-07-11T21:30:00Z
  TYPE: PLAN
  CLAIM: Verified before build: StructuralDiffStrategy ALREADY reports
    part-grain change aspects (added/removed/changed functions, classes,
    methods w/ signature/docstring/body flags) - the missing grain is the
    part TEXT diff. Both diff strategies operate on material `sources`, so
    the material fix instantly widens string AND structural diffs to full
    physical modules. StructuralSynthesizer._top_level_index/_segment
    already own part-span math - gains a public extract_part(source, name,
    kind=None) and the root reuses its lazily-owned synthesizer. part_diff
    reads RECORDED material only (comparison law); part_view reads
    present-tense (source_view resolution incl. live-disk w/ drift).
    Impact rides part_diff automatically, centered on the carrying module
    (impact stays module-grain per the grain laws - a part's radius IS its
    module's radius, stated honestly).
  EVIDENCE:
  - src/melder/mutation_research/mutation_research.py:988-1004 (the synthetic-only gap)
  - src/melder/mutation_research/diff/strategies/structural_diff_strategy.py:54-109
  - src/melder/mutation_research/synthesis/structural_synthesizer.py (_top_level_index/_segment)
  IMPACT: Additive reads + one custody-true material widening; zero new
    subsystem edges.
  NEXT: material fix -> extract_part -> root verbs -> rooms/tuples ->
    tests -> docs/graph.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-11T22:05:00Z
  TYPE: IMPLEMENTATION
  CLAIM: All four slices SHIPPED. (1) MATERIAL FIX: _resolve_diff_material
    drinks both recorded carriers (synthetic first, user-retained fills
    gaps; live disk explicitly refused w/ the comparison-law comment) -
    string AND structural diffs instantly widened to full physical
    modules. (2) DOSSIER: root module_view (text labeled by kind via the
    enriched _resolve_module_source rows - now carry "kind"
    synthetic/user/live_disk additively, source_view rows gain it free -
    fingerprint, path, deps both ways, exports, drift; unknown_module
    honest). (3) PARTS: StructuralSynthesizer.extract_part public query
    (span incl. decorators, kind filter, None miss, loud on unparseable/
    bad kind - LOGIC SANDBOX-VERIFIED standalone; the mount replica of the
    grown file froze at 262 lines mid-except and CANNOT be exec-verified -
    file-tool confirms 314+ lines intact); root part_view (present-tense
    resolution, searches root module first, per-module parse errors
    collected, honest miss) + part_diff (RECORDED material only via
    _locate_recorded_part, difflib unified diff, per-side found/module/
    kind truth, AUTOMATIC module-grain radius via impact_view) +
    _get_synthesizer lazy owner. (4) ROOMS: research_module/research_part/
    research_part_diff on BOTH systems (all reads), tuples codegen 24 /
    capability 13, inventory equality test extended, split test reads
    updated. TESTS: foresight +4 (user-carrier diff material, dossier +
    honest miss, part_view + kind-filter miss + bad-kind loud, part_diff
    change + radius + one-sided honesty), synthesizer +2 (extract spans w/
    decorators, loud arms), room loops extended (dossier/part in foresight
    loop; part_diff w/ radius in synthesis loop). DOCS+GRAPH: both C-docs
    (24/13 counts, crystal-well + comparison-law bullets), both graphs
    530/992 held (MR + synthesizer responsibilities, 2 borrows whys).
  EVIDENCE:
  - src/melder/mutation_research/mutation_research.py (material fix + 3 verbs + helpers)
  - src/melder/mutation_research/synthesis/structural_synthesizer.py (extract_part)
  - src/melder/nexus/rift/command_system/{codegen,capability}_command_system.py
  - tests (foresight/synthesizer/room integration/test_nexus inventory)
  IMPACT: Agents get every grain the owner named: module diffs over full
    physical-or-synthetic text, class/part diffs, and the blast radius
    riding each - all off the crystal, one call per question.
  NEXT: owner-run 3.14t; then the ResearchGroup base-unit discussion
    (units-and-scales ticket).
  REREAD: NOT_REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-11T22:40:00Z
  TYPE: IMPLEMENTATION (owner refinement: grain is the AGENT'S CHOICE)
  CLAIM: Owner corrected the default posture ("optional module or classes
    not just default modules... extend the code to offer the options of
    the class code or the module"). SHIPPED: (1) NEW PartDiffStrategy
    ("parts", third DEFAULT in the DiffEngine family) - per common module,
    top-level classes/functions compare as individual code regions: added/
    removed parts WITH full text, changed parts as unified diffs,
    identical by name, and a <module_body> residue region (imports/
    constants) so nothing escapes; parse errors per module naming the
    side; text-less modules honest. SANDBOX-VERIFIED LIVE (all arms:
    added/removed/changed/residue/identical/unavailable/broken). So
    research_diff(left, right, strategy=) now OFFERS source (whole-module
    text) / structural (shape) / parts (class code) - grain by choice, no
    new signature. preview_candidate composes all three. (2) NEW
    StructuralSynthesizer.list_parts (inventory companion, source order,
    loud on unparseable) + root parts_view(spell_id, module_name=None)
    (every top-level part per module WITH code, per-module honesty) +
    research_parts room command (both rooms). Tuples codegen 25 /
    capability 14; inventory equality test + split test extended; engine
    default-family test updated to ["parts","source","structural"];
    unknown-strategy test regex-safe (verified). TESTS: NEW
    test_part_diff_strategy.py (3), foresight +2 (parts_view inventory,
    diff_research parts grain) + preview parts-key assert, synthesizer +1
    (list_parts), room loops +2 spots (inventory in foresight loop; parts-
    grain research_diff in synthesis loop). DOCS+GRAPH: counts 25/14 and
    grain-choice law in both C-docs; graphs 530/992 -> 531/995
    (PartDiffStrategy node + owns/creates/specializes edges, DiffEngine
    role names the three-grain family, synthesizer + borrows whys
    refreshed) - file-tool-verified.
  EVIDENCE:
  - src/melder/mutation_research/diff/strategies/part_diff_strategy.py (new)
  - src/melder/mutation_research/diff/diff_engine.py (third default)
  - src/melder/mutation_research/mutation_research.py (parts_view + preview parts)
  - src/melder/mutation_research/synthesis/structural_synthesizer.py (list_parts)
  - rooms/tuples/tests as named
  IMPACT: For one spell_id the agent now chooses the lens per call:
    whole-module text, class-code inventory, named part, part diff w/
    radius, or whole-version diff at any of three grains.
  NEXT: owner-run 3.14t; then the ResearchGroup twin/bootstrap discussion.
  REREAD: NOT_REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-11T23:20:16Z
  TYPE: STATE_TRANSITION
  CLAIM: in_progress -> DONE (owner-run 3.14t green, owner confirmation
    "yeah they all passed"). Completed on its own terms: both owner
    passes shipped and verified - diff material drinks both recorded
    carriers (comparison law enforced: live disk refused), the crystal
    well answers in one call (research_module dossier), part grain is
    fully served (research_part named read, research_parts inventory
    [now w/ part fingerprints], research_part_diff w/ automatic
    module-grain radius), and the whole-version diff offers the grain
    CHOICE (source/structural/parts strategies, preview composes all
    three). Later lanes extended on top (part shas, composition lift on
    impact) - all green in the same run.
  EVIDENCE: owner message 2026-07-11; epic/tickets note trails.
  IMPACT: The single-spell_id lens family the owner specified is live.
  NEXT: none.
  REREAD: NOT_REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Owner-ruled first slice of the units-and-scales philosophy: full-module
diff material from both recorded carriers, the module dossier verb, and
part-grain text diffs with automatic module-grain radius. Groups discussion
follows separately.
