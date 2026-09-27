# Melder roadmap: source inspection notes

Static inspection of the user-provided `melder.7z` snapshot. No Melder runtime or test suite was executed. Docstrings below describe intended contracts; they do not independently prove every claimed behavior. Line numbers refer to the extracted source, and hashes identify the exact inspected files.

These notes distinguish existing source contracts from proposals in `melder-roadmap-expanded.md`.

## AethericFrame

File: `src/melder/aether/aetheric_frame/aetheric_frame.py`  
SHA-256: `22438de3c9ce7cb6526a51e8232296301f65d61134eaaa4f42cb3d3792e4ecb8`  
Excerpt: lines 29–67.

```text
29:     """
30:     Manage one isolated runtime frame within `Aether`.
31: 
32:     `AethericFrame` is the per-frame ownership boundary beneath the global
33:     `Aether` singleton. It owns the frame-local conduit registry, spell/index
34:     registries, frame-level posture/config references, and the DevOps services
35:     tied to that frame. It also owns the frame-local `ConduitCloud`, which in
36:     turn owns the cluster registry and cluster lifecycle.
37: 
38:     Contract:
39:       - Owns root conduits and their spell registries.
40:       - Owns a stable root-conduit name index for per-frame lookup.
41:       - Owns the version registry for all `SpellIndex` lineages in this frame.
42:       - Owns one `DevOpsInformationRegistry` as the frame-local topology and
43:         transaction mirror for reporting and future strategy resolution.
44:       - Owns one `ConduitCloud` over the frame-local conduit registries.
45:       - Owns `SpellSystemStates` and `DevOpsManager` for this frame.
46:       - Owns one narrow frame-level AR posture object distinct from the richer
47:         shared Spellbook configuration object.
48:       - Detaches itself from `Aether` only after frame-owned cleanup completes.
49: 
50:     Threading / Concurrency:
51:       - Uses one frame-local `RLock` to guard cleanup and frame-owned registry
52:         mutation.
53:       - Relies on child objects to guard their own internal state.
54: 
55:     Threading:
56:         One frame-local `RLock` guards cleanup and frame-owned registry
57:         mutation; children guard their own state. The frame does NOT take a
58:         child's lock, which keeps the lock order strictly downward:
59:         frame -> child, never child -> frame.
60: 
61:     Lifecycle / Cleanup:
62:         Under V3 Horizon lazy frames, `import melder` creates ZERO frames - the
63:         first `Spellbook` births the frame it names via `_ensure_frame`
64:         (get-or-create is the intended semantic), and a collapsed configuration
65:         falls back to a lazily created "default". Teardown detaches from
66:         `Aether` only AFTER frame-owned cleanup completes, so a half-torn frame
67:         is never reachable from the global registry.
```

## DevOpsManager

File: `src/melder/aether/aetheric_frame/dev_ops/dev_ops_manager.py`  
SHA-256: `9984f1426364c2c08b254f8fa8b25e98bd10682a196968859006e1238f74e439`  
Excerpt: lines 25–63.

```text
25:     """
26:     Frame-level ownership root for DevOps and admission-control subsystems.
27: 
28:     `DevOpsManager` is the operational facade over the frame's health and
29:     control-plane services. It owns and exposes the managers that describe
30:     incidents, track dirty/pending change state, assess risk, and govern
31:     conduit creation-gate admission.
32: 
33:     Owned subsystems:
34:     - `IncidentManager`: descriptive incident recording
35:     - `ChangeControlManager`: pending-change and dirty-root coordination
36:     - `RiskManager`: risk posture tied back into spell-system state
37:     - `CreationGateController`: conduit and lineage admission governance
38:     - `SpellSystemStates`: frame-local state registry surfaced through this hub
39:     - borrowed `DevOpsInformationRegistry`: frame-owned topology and
40:       transaction mirror exposed through the manager boundary
41: 
42:     Contract:
43:     - One `DevOpsManager` owns one coherent set of frame-local operational
44:       managers.
45:     - The information registry is borrowed from the owning frame rather than
46:       created here, so runtime-object unregister flows are not coupled to
47:       manager cleanup order.
48:     - The manager is the intended boundary for higher-level tools or AI agents
49:       that need to inspect or manipulate frame health.
50:     - Cleanup is responsible for tearing down the owned manager graph in a
51:       deterministic order and then dropping the borrowed registry reference.
52: 
53:     Threading:
54:         Each owned manager guards its own state; this hub adds no lock of its
55:         own and never reaches into a child's internals, keeping the lock order
56:         strictly downward.
57: 
58:     Lifecycle / Cleanup:
59:         One instance per `AethericFrame`, constructed in the frame's `__init__`.
60:         Cleanup tears down the OWNED manager graph in deterministic order and
61:         only then drops the BORROWED registry reference - owned children die
62:         first, borrowed references are released last.
63: 
```

## IncidentManager

File: `src/melder/aether/aetheric_frame/dev_ops/incident_manager/incident_manager.py`  
SHA-256: `8b3b71796dc37deecf2294a9f0db1bc1250763a3163888fdaecf72ded1d3bcea`  
Excerpt: lines 19–57.

```text
19:     """
20:     Frame-local registry of `Incident` records.
21: 
22:     `IncidentManager` is the descriptive side of the DevOps surface. It owns
23:     the incident objects for one frame, allocates their ids, and provides the
24:     lookup/filtering entrypoints that tooling, operators, or higher-level
25:     automation can use to inspect that frame's incident history.
26: 
27:     Contract:
28:     - The manager owns every `Incident` it creates.
29:     - Incident ids are allocated sequentially for the lifetime of the manager.
30:     - Query methods return current registry state only; no policy decisions are
31:       made here.
32:     - Cleanup is idempotent and tears down child incidents before clearing the
33:       registry itself.
34: 
35:     Threading:
36:         Registry mutation and id allocation are serialized internally.
37:         Sequential id allocation means ids are frame-local and monotonic, not
38:         globally unique across frames.
39: 
40:     Lifecycle / Cleanup:
41:         Owned by `DevOpsManager`. Cleanup cleans child incidents FIRST and only
42:         then clears the registry - children before container, matching the
43:         repo-wide teardown posture.
44: 
45:     Registration:
46:         MELDER KERNEL - guarded. Frame-owned; reached through `DevOpsManager`.
47: 
48:     Subsystem Context:
49:         The DESCRIPTIVE side of DevOps, deliberately opposite the decisive
50:         side. `RiskManager` and `ChangeControlManager` change what the runtime
51:         DOES; this manager only records what happened. Its records are read by
52:         tooling and agents, never by meld.
53: 
54:     System Context:
55:         "No policy decisions are made here" is the whole contract and it is
56:         worth respecting strictly. An incident registry that also gated
57:         behaviour would make recording a problem indistinguishable from
```

## RiskManager

File: `src/melder/aether/aetheric_frame/dev_ops/risk_manager/risk_manager.py`  
SHA-256: `a3add707c9fc95e313056e42752efcef41ccac3173ed272f5fe96b7497d692b6`  
Excerpt: lines 94–132.

```text
94:     """
95:     DevOps risk tracking for meld validation gating.
96: 
97:     `RiskManager` is the conduit-local risk aggregator that feeds back into the
98:     spellbook-level "validation required" signal used by Meld-facing runtime
99:     flows. It does not validate spells itself. Instead, it watches validity
100:     state changes and folds them into one operational question per conduit:
101: 
102:     "Does this conduit currently own or see any lineage whose state means meld
103:     should not be trusted without another validation pass?"
104: 
105:     Risk model:
106:     - structural risk is tracked by lineage id
107:     - resolution risk is tracked by conduit-local lineage or spell id key
108:     - any non-`SpellValidity.valid` state is treated as risky
109:     - if either risk set is non-empty, the owning spellbook is marked as
110:       requiring validation
111: 
112:     Operational role:
113:     - register conduits and the spells they currently expose
114:     - react to structural and per-conduit resolution validity changes
115:     - keep conduit-local risk buckets current
116:     - push one distilled validation-required flag back onto each spellbook
117: 
118:     Threading:
119:     - Internal state is guarded by an `RLock`.
120:     - Callers may invoke methods concurrently across conduits; updates are
121:       folded into conduit-local buckets under the manager lock.
122: 
123:     Lifecycle:
124:     - Owned by `DevOpsManager` and cleaned from that ownership boundary.
125:     - After cleanup, public methods fail through `check_cleaned()`.
126: 
127:     Registration:
128:         MELDER KERNEL - guarded. Frame-owned control-plane service reached
129:         through `DevOpsManager`; never constructed by users.
130: 
131:     Subsystem Context:
132:         The AGGREGATOR of the control plane. `SpellSystemStates` holds the
```

## ChangeControlManager

File: `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py`  
SHA-256: `1444dde9957c097733fdc9b373c410752246d56a6c34339fabafff040750a312`  
Excerpt: lines 62–100.

```text
62:     """
63:     Change-control registry for an Aetheric Frame.
64: 
65:     Purpose:
66:         Provide DevOps-facing bookkeeping for spell lineages, dirty roots, and
67:         change-control admission helpers. This is the frame-level control-plane
68:         owner for admission, embargo, conflict, staging, and targeted
69:         revalidation bookkeeping; it is not the hot-path resolver itself.
70: 
71:     Contract:
72:         - Tracks pending change metadata by SpellIndex id.
73:         - Tracks per-conduit component-of and dirty root state for targeted revalidation.
74:         - Owns and coordinates the transaction/conflict/embargo/orchestrator
75:           helper managers used by change-control flows.
76:         - Exposes hook-registration seams for commit, abort, structural
77:           validation, and dirty-marking behavior.
78:         - Does not own SpellSystemStates lifecycle.
79:     Args:
80:         spell_system_states:
81:             Spell system state container for this frame.
82:     Returns:
83:         None.
84:     Raises:
85:         ValueError: If spell_system_states is None.
86:     Ownership:
87:         Owns internal registries and the change-control manager instances.
88: 
89:     Threading:
90:         All state mutations are guarded by an internal RLock.
91:     Lifecycle:
92:         cleanup() is idempotent and nulls internal references.
93: 
94:     Registration:
95:         MELDER KERNEL - guarded. The frame's DevOps control-plane owner:
96:         constructed and driven by the AethericFrame dev-ops layer; never
97:         user-constructed or bound.
98: 
99:     Subsystem Context:
100:         The top of the `change_control_manager` subsystem. It OWNS and wires the
```

## MutationResearch

File: `src/melder/mutation_research/mutation_research.py`  
SHA-256: `37b37cb10e0ae1d9d8e231e091082dec0d69d33e7c67548276720f53e4a55f36`  
Excerpt: lines 39–77.

```text
39:     """
40:     Singleton mutation-research root hosted by `Aether`.
41: 
42:     Purpose:
43:         Own the formal declaration record of research over the live spell
44:         world. The root manages `ResearchSet` networks by name (one
45:         guaranteed `default` set), carries the mutation-research
46:         configuration lifecycle, and is the ONLY object in the package that
47:         touches the crystallizer: sets emit detached payloads through an
48:         injected callback, and the root records them into the persistence
49:         layer as the `MutationResearchCrystal` composition payload.
50: 
51:     Contract:
52:         - Singleton, mirroring the hosting pattern used by `Nexus` and
53:           `Crystallizer`; hosted by `Aether`, not by `AethericFrame`.
54:         - Owns configuration state and the research-set registry.
55:         - Emission is replace-on-emit through `Crystallizer.emit(...)` and is
56:           a NO-OP while the crystallizer records nothing; lifecycle flips
57:           ride the `RecordedUnitState` switch as before.
58:         - Conduits and frames carry NO mutation dimension: the old
59:           conduit/frame facades and SpellIndex-keyed sessions are out of the
60:           model and gone.
61: 
62:     Threading:
63:         Class lock guards singleton identity; instance verbs serialize under
64:         the same reentrant lock. A dedicated reentrant emission lock makes
65:         the persistence emission atomic (snapshot build + replace-on-emit
66:         publication happen under one holder, so a paused emitter can never
67:         publish a stale composition over a newer one). Lock order is
68:         emission -> root -> set -> crystallizer, one-way: every path that
69:         can trigger an emission while holding the root lock (set creation,
70:         hydration) acquires the emission lock first.
71: 
72:     Lifecycle:
73:         `cleanup()` cascades into owned sets and configuration, emits the
74:         cleaned state while the record outlives the root, and resets
75:         singleton bookkeeping; idempotent.
76: 
77:     Registration:
```

## MutationResearch.preview_candidate

File: `src/melder/mutation_research/mutation_research.py`  
SHA-256: `37b37cb10e0ae1d9d8e231e091082dec0d69d33e7c67548276720f53e4a55f36`  
Excerpt: lines 2808–2846.

```text
2808:         """
2809:         Mock one candidate codegen and report what would happen next.
2810: 
2811:         Purpose:
2812:             The foresight centerpiece: BEFORE anything executes, binds, or
2813:             records, answer what the candidate code defines, what it
2814:             imports, how it differs from the version it would replace, and
2815:             what blast radius that replacement would have - so an agent can
2816:             guess what happens next instead of finding out.
2817: 
2818:         Contract:
2819:             - Read-only: nothing executes, binds, or records.
2820:             - Unparseable code answers honestly (`parse_error` row; the
2821:               analysis/diff/impact sections go None) - previewing broken
2822:               code is a legitimate question.
2823:             - With `against_spell_id`, the candidate text adopts that
2824:               spell's root module name so the would-be diff compares module
2825:               universes honestly; the impact section is that root module's
2826:               current blast radius joined with research residency.
2827:             - With only `module_name`, the impact section is that module's
2828:               radius; with neither, impact is None (nothing to center on).
2829: 
2830:         Args:
2831:             code:
2832:                 Candidate Python source text.
2833:             against_spell_id:
2834:                 Optional current version the candidate would replace.
2835:             module_name:
2836:                 Optional module identity for the candidate when no
2837:                 against-version exists.
2838:             set_name:
2839:                 Research set for the impact residency join.
2840: 
2841:         Returns:
2842:             Dict[str, object]:
2843:                 `{"candidate_sha256", "module_name", "parse_error",
2844:                 "defines", "import_roots", "diff", "impact",
2845:                 "against_spell_id"}`.
2846: 
```

## MutationResearch.record_world_entry

File: `src/melder/mutation_research/mutation_research.py`  
SHA-256: `37b37cb10e0ae1d9d8e231e091082dec0d69d33e7c67548276720f53e4a55f36`  
Excerpt: lines 1243–1272.

```text
1243:         """
1244:         Idempotently declare one world-entry into the default set.
1245: 
1246:         Purpose:
1247:             The runtime-seam facade: the spellbook's bind and bind_inactive
1248:             confirmation points call this on every dynamic-lane world entry
1249:             once the root is active. Rediscovery (identical content, same
1250:             SHA) is a quiet no-op - the runtime never fails on research
1251:             bookkeeping.
1252: 
1253:         Contract:
1254:             - CAMPAIGN DEFAULTS TO THE AMBIENT ONE: `campaign=None` inherits
1255:               `active_campaign` rather than meaning "no campaign".
1256:             - Records against the DEFAULT research set, not a named one.
1257: 
1258:         Args:
1259:             spell_id:
1260:                 Binding-signature SHA256 entering the world.
1261:             staged:
1262:                 True for parked (`bind_inactive`) entries.
1263:             author:
1264:                 Optional acting agent name.
1265:             reason:
1266:                 Optional reason line.
1267: 
1268:         Returns:
1269:             bool:
1270:                 True when a new declaration was recorded; False when the
1271:                 identity was already declared.
1272:         """
```

## MutationResearch.set_active_campaign

File: `src/melder/mutation_research/mutation_research.py`  
SHA-256: `37b37cb10e0ae1d9d8e231e091082dec0d69d33e7c67548276720f53e4a55f36`  
Excerpt: lines 1064–1089.

```text
1064:         """
1065:         Set the ambient research-campaign stamp.
1066: 
1067:         Purpose:
1068:             Multi-agent campaigns stamp work ACROSS lanes; once set, every
1069:             runtime auto-record routed through the root facades
1070:             (`record_world_entry` / `record_promotion` - i.e. every dynamic
1071:             bind, staged bind, and notch) carries this stamp until cleared,
1072:             so campaign membership never depends on remembering to pass it.
1073: 
1074:         Contract:
1075:             - Sets the AMBIENT DEFAULT that later group operations inherit when they pass
1076:               `campaign=None`. It does not retroactively attribute earlier operations.
1077:             - Rejects a non-string or empty campaign.
1078: 
1079:         Args:
1080:             campaign:
1081:                 Non-empty campaign name.
1082: 
1083:         Returns:
1084:             None.
1085: 
1086:         Raises:
1087:             ValueError:
1088:                 If campaign is empty.
1089:         """
```

## TransitionAct

File: `src/melder/mutation_research/research_set/transition_entry.py`  
SHA-256: `a9d0e76bc78c048cca1a0a0fab5fd2eb8cbb6e6f723e4d0d45c35559587690c2`  
Excerpt: lines 10–48.

```text
10:     """
11:     World-entry act vocabulary for the mutation-research journal.
12: 
13:     Purpose:
14:         Name the only events the research record acknowledges. The stream is
15:         forward-only and additive: history exists for understanding, never for
16:         time travel, so there are deliberately NO checkout/rollback acts.
17:         Returning to an old version is a NEW registration, not a rewind.
18: 
19:     Registration:
20:         VALUE VOCABULARY. An enum is compared and
21:         passed, never injected.
22: 
23:     Subsystem Context:
24:         The act vocabulary stamped onto every `TransitionEntry` in a
25:         `ResearchJournal`. The vocabulary is drawn from version control but is
26:         deliberately NOT git: there is no merge, no rebase, and no checkout,
27:         because those verbs all imply rewriting or relocating history that this
28:         model treats as permanent.
29: 
30:     System Context:
31:         The absent acts say more than the present ones. `promoted` changes what
32:         is LIVE without changing which lane holds a version, and `restored`
33:         rebuilds organization while itself being journalled - so even a rewind
34:         of structure appears in history as a forward event. There is no act in
35:         this enum that removes anything.
36: 
37:     Contract:
38:         - `lane_created`: a research lane entered the network (optionally
39:           anchored onto another lane's node).
40:         - `registered`: a bound version was formally declared research and
41:           landed in a lane (the world-entry moment; active bind-side).
42:         - `staged`: a version entered the world PARKED (`bind_inactive`);
43:           same declaration mechanics as `registered`, different runtime
44:           posture at entry.
45:         - `promoted`: the runtime selection moved (a notch repointed the
46:           SpellIndex active member); journal-only - promotion changes what
47:           is live, never which lane holds the version.
48:         - `attached` / `detached`: a lane's ancestry anchor was organized onto
```

## Continuity is not arbitrary state rollback

The architecture document distinguishes structural checkpoint reconstruction from live version promotion. It also states that not every live value or callable can be reconstructed from data alone.

Source: `architecture_and_design/02_architecture/continuity_and_evolution.md`, sections "Continuity Path" and "Tradeoffs"; and `architecture_and_design/03_usage/preserve_and_evolve.md`, sections "Continuity Workflow" and "Evolution Workflow".

## External terminology sources checked

Checked on 2026-09-27. These sources support terminology and the distinction between a roadmap target and formal accreditation; they are not a complete ITIL practice-guide assessment.

- [PeopleCert: ITIL 4 Practitioner — Change Enablement](https://www.peoplecert.org/browse-certifications/it-governance-and-service-management/ITIL-1/itil-4-practitioner-change-enablement-3794): risk assessment, authorization, change scheduling, roles, and practice outcomes.
- [PeopleCert: ITIL Foundation Bridge (Version 5)](https://www.peoplecert.org/browse-mock-exams/it-governance-and-service-management/ITIL-1/ITIL-Foundation-Bridge-Version-5-Mock-exam-4159): establishes that a newer ITIL baseline exists, so compatibility should name a version.
- [PeopleCert: ITIL-Accredited Tool Vendors programme](https://atv.peoplecert.org/): describes formal assessment of tool alignment and vendor expertise.
- [PeopleCert: accreditation model](https://atv.peoplecert.org/accreditation/accreditation-model/): describes the practice-based tool/vendor assessment model.
