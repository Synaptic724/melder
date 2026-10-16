"""Author the graph semantics of rule 2, D1-B, D2 and D3 (0.2.8250) in seven descriptors (melder_1, 2026-10-16).

usage (from the repository root): python <this script> [--check]
Edits only authored fields (responsibilities, owns_state); the extractor owns every other field. Each edit refuses
when the field does not hold the value it expects. Writes JSON the way the extractor does (indent=1, LF). The nodes
are accepted afterwards with graph_walker --accept, once their source was re-read.
"""
import json
import pathlib
import sys

CHECK = "--check" in sys.argv[1:]
G = pathlib.Path("context_compass/system_docs/graph")


def edit(rel, node_id, change):
    path = G / rel
    data = json.loads(path.read_text(encoding="utf-8"))
    change(data["nodes"][node_id])
    if not CHECK:
        path.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(("checked " if CHECK else "edited ") + rel)


def replace_one(items, old, new):
    assert items.count(old) == 1, (old, items)
    items[items.index(old)] = new


def spell_system_states(node):
    resp = node["responsibilities"]
    assert not any("binding key" in r for r in resp), resp
    resp.append(
        "records the binding key of each lineage's selected version in register_index (binding_key=..., kept when "
        "None, dropped by unregister_index and cleanup) and marks everything downstream of given lineages for "
        "revalidation - a lineage reached by a registry edge, frame-wide, as gated, impacted_by_dependency and "
        "transitively dirty; a SpellContract consumer, in any Book, of a reached lineage's binding key as gated + "
        "contract_unvalidated - visiting each lineage once and never a seed (mark_dependents_for_revalidation); "
        "mark_contract_dependents_dirty walks on the same way from the consumers it marks (0.2.8250)"
    )
    owned = node["owns_state"]
    assert "_binding_key_by_index" not in owned, owned
    owned.append("_binding_key_by_index")


def meld(node):
    resp = node["responsibilities"]
    replace_one(
        resp,
        "reads contract-default signatures without forcing evaluation of unavailable annotation names",
        "rechecks a SpellContract consumer only when a provider change marked it gated + contract_unvalidated: the "
        "structural branch, with Phase 4's presence check, is the recheck; the per-meld contract scan and its "
        "signature read are retired (0.2.8250)",
    )
    assert not any("_refresh_stale_dependencies" in r for r in resp), resp
    resp.append(
        "before a spell compiles at a meld (_may_compile), and first in the deferred lane, refreshes each stale "
        "dependency its plan expands - socket targets and contracted providers, at their lineage's current version - "
        "with that dependency's owner Book under its rebuild window and lock, then resets its plan so its own next "
        "meld runs a full target pass; a broken or still-gated dependency raises SpellbookValidationError naming it "
        "(_refresh_stale_dependencies, _refresh_dependency_structure, 0.2.8250)"
    )


def contract_presence(node):
    resp = node["responsibilities"]
    replace_one(
        resp,
        "read the Spellbook's contracted-spell maps and the frame system_state",
        "read one-call snapshots of the Spellbook's contracted-spell maps - this is the recheck a marked consumer's "
        "next meld runs, so a provider change may still be writing them under the Book lock (0.2.8250) - and the "
        "frame system_state",
    )
    assert not any("remedy" in r for r in resp), resp
    resp.append(
        "names the contract key and the remedy in its SPELL_CONTRACT_MISSING_PROVIDER warning, the one Phase 4 gates "
        "a lineage on, which SpellbookValidationError shows as the consumer's reason (0.2.8250)"
    )


def validation_error(node):
    resp = node["responsibilities"]
    replace_one(
        resp,
        "show errors only: warnings are counted; strategy sources, details payloads and spell ids are never printed",
        "show errors, and a spell's gating warnings (GATING_WARNING_CODES: SPELL_CONTRACT_MISSING_PROVIDER, the one "
        "Phase 4 gates a lineage on) as its reason when it shows no error; every other warning, and a gating one "
        "beside errors, is counted; strategy sources, details payloads and spell ids are never printed (gating "
        "reasons, 0.2.8250)",
    )


def spellbook(node):
    resp = node["responsibilities"]
    assert not any("_mark_contract_dependents_dirty" in r for r in resp), resp
    resp.append(
        "marks the SpellContract consumers of a changed active contracted copy's key once its Book lock is released - "
        "an add, park, reactivation, removal or clear of an active copy; never a parked copy or a change before "
        "conjure (_mark_contract_dependents_dirty in the five contracted-map mutators, 0.2.8250)"
    )
    resp.append(
        "passes each selected version's binding key to register_index at bind and notch, and after a notch's "
        "registration marks everything downstream of the notched lineage (mark_dependents_for_revalidation, 0.2.8250)"
    )


def conduit(node):
    resp = node["responsibilities"]
    assert not any("_activate_borrowed_spell" in r for r in resp), resp
    resp.append(
        "after a notch's transaction, between the deactivate fan-out and the index emission, has every linked peer "
        "make its parked copy of the incoming version active again, so a version grant is active exactly while its "
        "version is (_activate_borrowed_spell, 0.2.8250)"
    )


def conduit_ward(node):
    resp = node["responsibilities"]
    assert not any("add_spell_to_contract" in r for r in resp), resp
    resp.append(
        "grants one version per add_spell_to_contract - the borrower's copy active while that version is the "
        "lineage's active member, parked by a notch away and active again on a notch back - while an index link "
        "follows the lineage to every new version (_emit_index_notch); every change of a borrower's active copy ends "
        "in the borrower Book's marking mutators (0.2.8250)"
    )


edit("melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.json",
     "melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_states.SpellSystemStates",
     spell_system_states)
edit("melder/aether/conduit/meld/meld.json", "melder.aether.conduit.meld.meld.Meld", meld)
edit("melder/aether/spellbook/spell_compiler/validation/strategies/contract_provider_presence_strategy.json",
     "melder.aether.spellbook.spell_compiler.validation.strategies.contract_provider_presence_strategy."
     "ContractProviderPresenceStrategy", contract_presence)
edit("melder/utilities/custom_exceptions/spellbook_validation_error.json",
     "melder.utilities.custom_exceptions.spellbook_validation_error.SpellbookValidationError", validation_error)
edit("melder/aether/spellbook/spellbook.json", "melder.aether.spellbook.spellbook.Spellbook", spellbook)
edit("melder/aether/conduit/conduit.json", "melder.aether.conduit.conduit.Conduit", conduit)
edit("melder/aether/conduit/conduit_ward/conduit_ward.json",
     "melder.aether.conduit.conduit_ward.conduit_ward.ConduitWard", conduit_ward)
