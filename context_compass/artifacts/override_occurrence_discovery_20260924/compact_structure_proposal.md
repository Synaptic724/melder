# Compact construction graph proposal

Date: 2026-09-24. Author: updater_1. Lead: updater_0.
Task: tickets/tasks/2026-09-24_discover_override_occurrence_slicing_task.md.
Status: bounded representation, hydration and codegen proof; native lifecycle contract still separate.

## Recommendation

Replace the compiler's dependency on enumerated logical override paths with a compact construction
graph and request-specific selector states. The owner explicitly allows a better structure to be
proposed while Melder is in alpha. This is a candidate replacement, not an obligation to keep fitting
new behavior into the existing occurrence/path dictionaries.

Keep one ordinary construction description. An input shape produces a small program that changes
its operand sources, cuts satisfied dependency edges, and retains conditional reuse branches.
Lower ordinary and overridden calls from the same argument/constructor representation. Existing
lifetime stores remain authoritative until the lead's native boundary is resolved.

The new artifacts demonstrate this without editing production code:

- compact_alias_plan.py: physical graph, selector progress, conditional sources and value-only payload.
- compact_alias_emitter.py: direct Python constructor calls and necessary guard branches.
- compact_alias_probe.py: equivalence, hydration, selector validation, scaling and pruning checks.
- compact_alias_results.json: final measured receipt and exact source/artifact fingerprints.
- compact_claim_prelude.py: generated demanded-site callback protocol for the native adapter.
- compact_claim_prelude_results.json: twelve callback-contract cases, including hydration and contention.

## Why another representation is justified

The previous fully expanded alias model proved semantics but is not a suitable general storage
strategy. A shared node can be reachable through exponentially many paths while needing only one
constructor. Enumerating all paths makes the addressing model grow with aliases instead of work.

Current source has two separate views:

- Physical instance/injection rows already describe parent parameters and dependency instance keys.
- Override targeting iterates every rooted socket ref, storing exact paths and wildcard target tuples.

The new diagnostic reads the former directly, without creating the earlier uncollapsed SliceProbe
graph. It uses the expanded model afterward only as an independent small-fixture oracle.

Source:
- src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_instance_processor_strategy.py:134-215
- src/melder/aether/spellbook/spell_compiler/artifact_processor/data/spell_injection_analysis.py:9-161
- src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_override_targeting_processor_strategy.py:43-127

## Three internal layers

### 1. Base construction graph

Store each physical constructor site once, with named parameter edges and ordered member positions.
Shared providers have several incoming edges to one site. A many child belongs to its physical
parent/socket/member position. Logical access through two aliases does not multiply that child.

The production row needs more than the bounded proof's row:

- selected provider/version and existing lifetime/store operation;
- parameter name, kind, position, collection membership and ordinary-default omission policy;
- executable dependency sites and separate required-input/descriptor readiness facts;
- contract-source provenance where it can change selection or supplied operand precedence;
- base structural signature and the existing invalidation epoch.

Application constructors and caller values remain runtime bindings, outside the value-only graph.
The graph must be built directly from declarations and resolved provider facts in production. Adapting
after today's full native compilation, as this diagnostic does, cannot remove its earlier costs.

The contract payload requirement is specifically an incoming-edge source. Current contract processing
resolves the provider from book-visible contracted maps, then records the declaring consumer parameter's
payload on its child occurrence. Injection merges all payloads for a shared provider and can reject them
before per-call cuts exist. The replacement must retain consumer/socket payload-source references and
their demand guards before adjudicating shared inputs. Do not store only that early merged result on
the shared site. Preserve __args__ and descriptor readiness explicitly; bind live declaration values
through runtime operand slots instead of serializing arbitrary application objects into graph rows.

Source:
- src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_contract_processor_strategy.py:166-341
- src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_injection_processor_strategy.py:119-358

### 2. Prepared request program

Keep the existing TargetSpec parser and PATH > UNIQUE > BROADCAST precedence. For exact paths,
advance a small (selector, consumed-prefix) state through named parameter edges. Merge matching
incoming states with an OR guard. Do not enumerate each complete path to a shared node.

Broadcast rules attach to matching parameter names under active site demand. UNIQUE validation
counts declared logical paths before cuts or reuse; a shared physical socket reached through two
paths is still two declared matches. The count can be computed over the DAG without storing paths.
Invalid selectors remain invalid even when another input removes their would-be ancestor.

Each physical parameter retains guarded ranked candidate inputs and its conditional default edge:

```text
incoming demand -> physical site
                 -> existing reuse result OR construction branch
construction branch + active selector states -> candidate operands
no active supplied operand -> default provider edge becomes live
```

Cache this program by the base signature plus the complete selector/operand layout. Values and live
reuse outcomes are per-call inputs. A winner chosen during one call must never become the cache key
or permanent binding when another call can activate a different alias.

Top-level constructor inputs can lower directly to root operand slots in this representation. That
gives the common case a distinct internal preparation path without requiring a new public init={}
surface. Whether to add that spelling can be decided independently after measuring the actual path.

### 3. Generated execution

Emit direct constructor calls in dependency order, with only the conditional decisions that remain.
Static many-only cuts remove code entirely. Shared reuse requires guarded inputs and default edges,
whose lifetime/lock authority is owned by the native runtime integration.

The prototype emits no graph walk, selector scan or site-table loop during its generated call.
Its boundary still checks the raw selector keys and extracts current values; production may supply
already-normalized operand slots after existing request admission. Some conditional plain parameters
use a kwargs mapping. This is codegen viability evidence, not a final hot-path optimization claim.

The same value payload hydrates into the interpreter or the emitter. A native family envelope must
still enforce its existing release/interpreter/base-signature lifecycle; this experiment does not
replace cache admission. Incompatible experimental schema values are explicitly rejected.

## Evidence

Forty-two scenario evaluations match the earlier conditional oracle through four forms each:
compact interpretation, generated execution, hydrated interpretation, and hydrated generation.
The comparisons assert values, meaningful shared/distinct identities and constructor counts.
They include static cuts, cut-alias exclusion, active conflicts, specificity, falsey values, unequal
depth, distinct many parents, reuse transitions and restored default dependencies.

Constructor order is recorded but native ordering guarantees are not qualified by this proof.
All comparisons preserve native manifest bytes and prepared payload contents across evaluations.

The original structural examples now lower to actual reduced generated source:

| Workload | Base sites | Emitted constructor calls | Executed constructors | Source bytes |
| --- | ---: | ---: | ---: | ---: |
| Five dependencies, three supplied | 6 | 3 | 3 | 433 |
| Deep ordinary control | 511 | 511 | 511 | 21,598 |
| Deep left supplied | 511 | 256 | 256 | 10,992 |
| Both deep root branches supplied | 511 | 1 | 1 | 339 |

The deep-all source directly calls the root with the supplied left and right. It does not retain
510 inactive constructor blocks. Its source is retained in compact_deep_all_generated.py.

A synthetic chain with two aliases at each shared level demonstrates representation growth:

| Shared depth | Logical leaf paths | Physical sites | Exact-selector states | Payload bytes |
| --- | ---: | ---: | ---: | ---: |
| 8 | 256 | 9 | 9 | 1,526 |
| 20 | 1,048,576 | 21 | 21 | 3,529 |
| 32 | 4,294,967,296 | 33 | 33 | 5,533 |
| 64 | 18,446,744,073,709,551,616 | 65 | 65 | 10,880 |

This synthetic benchmark starts from the compact graph. It does not claim that native Melder
currently compiles those huge logical path sets efficiently. The payload contains fixture metadata,
not the richer full production policy rows described above. Single preparation durations are retained
as diagnostics only; neither a native throughput gain nor a stable latency ratio is asserted.

## Production change boundary

The owner can select this as the structural direction while the lead resolves native integration.
Implement it as a coherent internal change rather than adding an independent cache/runtime owner:

1. Define complete base socket/provider/readiness rows, including contract and positional cases.
2. Build physical construction sites and retain incoming-edge provenance without full path expansion.
3. Replace eager exact/wildcard path tables with graph-backed selector preparation and declared counts.
4. Prepare request-specific sources, default edges and guards under the base context lifecycle.
5. Lower both ordinary and override plans through shared constructor argument emission.
6. Integrate the lead's admission, retention and store-lock contract on Conduit and Space doors.
7. Qualify native correctness, cold/warm/hydrated execution, constructor/disposal counts and throughput.

Phases 8-11 are the central implementation area. Earlier blueprint/socket indexing must also stop
materializing the old path inventory if it would otherwise remain an upstream cost. Keep Phase-3
declaration facts and baseline validity separate from call-specific readiness; do not make a supplied
request globally validate an otherwise incomplete graph.

## Open boundaries

The compiler/native interface should be a demand-driven claim prelude, not a snapshot of every
possible store entry. In consumer-before-provider order, evaluate site demand, acquire a settled
hit/miss for a demanded shared site, retain that claim, and activate descendant demand only for its
construction branch. All incoming consumers must settle before the shared child's operands are chosen.
Finish this prelude before the first application constructor; contention may release claims and retry
the prelude, but must never replay application constructors.

CompactClaimPrelude(plan).prepare(select) now implements the compiler side. select(site_index)
returns (found, object) while the native adapter retains its claim. The generated prelude calls it
only for demanded shared sites, consumer first, and returns a fresh hit mapping. Twelve cases prove
callback omission after cuts/reuse, complete incoming fan-in, falsey hit identity, cache hydration,
zero application constructors, no input-value comparisons and unchanged exception propagation.
The owner of select releases partial claims and handles retries; the prelude owns no locks or stores.
The lead is integrating that callback with native incremental claims and constructor publication.

The first native bridge now passes seven lead-run scenarios: actual store reuse/publication, purge
and recreation, alias input selection, competing publication, constructor failure without replay,
and dynamic Conduit/Space gate behavior. This is a separate experimental adapter over prevalidated
fixtures, not a production Meld change. Evidence: the lead's native_compact_results.json and
native_compact_adapter.py under artifacts/override_structural_discovery_20260924/.

The original bridge created a constructor-wrapper tuple over every base Spell on each call. A separate
direct-publication adapter now binds constructors cold and passes a call-local publisher to emitted
shared misses. Eight lead-run cases pass, including the deep 511->1 case with catalog iteration
explicitly forbidden. The original bridge/receipt remain preserved. Retain this boundary in production;
do not put a full base-plan loop back around the pruned code. Native throughput is still unmeasured.

Final joint recommendation: artifacts/override_structural_discovery_20260924/joint_alpha_proposal.md.
The peer cross-reviewed that proposal and both native bridge variants, including matching receipt hashes.

The generated program must borrow native store selection and claim authority. It must not grow its
own lifetime registry. Ordinary creation, override creation and purge must participate in the same
writer protocol if that protocol is selected; integrating it on just one override route is insufficient.

- Native reuse/purge/construction synchronization: the lead is investigating actual store authority.
  A pre-read dictionary of reuse hits is not a production lock or retention contract.
- Contract payloads need incoming consumer/socket source provenance and guarded input selection,
  including positional payloads and explicit provider-readiness obligations. The bounded adapter
  refuses them instead of silently merging them. This is now a source-backed representation boundary.
- Multi-provider collection addressing, positional-only/variadic inputs, methods/existing objects,
  hooks and disposal are outside this adapter. Ordinary named class arguments and one-provider
  collections are qualified here. Production must cover the full supported declaration surface.
- Equal-rank arbitrary-object equality remains a semantic choice. This proof retains scalar-style
  comparison; it does not establish safe arbitrary user-defined equality behavior.
- Generated execution order must be qualified against actual side-effect and hook contracts.
- No production performance promise follows from fewer constructors alone. Measure full native
  request overhead and ordinary-creation controls after integration.

## Reproduce

```powershell
$env:PYTHONPATH = "$PWD/src;$PWD"
& .venv_new/Scripts/python.exe context_compass/artifacts/override_occurrence_discovery_20260924/compact_alias_probe.py
& .venv_new/Scripts/python.exe -m ruff check context_compass/artifacts/override_occurrence_discovery_20260924/compact_alias_plan.py context_compass/artifacts/override_occurrence_discovery_20260924/compact_alias_emitter.py context_compass/artifacts/override_occurrence_discovery_20260924/compact_alias_probe.py --ignore UP045,S102
```

UP045 is excluded for the required Optional typing style; S102 for intentional, permitted codegen.
Final scoped checks pass. Production source and the earlier proof artifacts retain matching hashes.
