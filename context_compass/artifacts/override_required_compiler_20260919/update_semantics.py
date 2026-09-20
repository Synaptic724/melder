"""Apply manually authored S3 graph deltas; do not infer semantics or renew unread class stamps."""

import json
from pathlib import Path


def main() -> None:
    """Preserve prior prose while recording the source-backed compiler capability additions."""
    root = Path(__file__).resolve().parents[3] / "context_compass/system_docs/graph"
    additions = {
        "melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_states.SpellSystemStates":
            "indexes OVERRIDE_REQUIRED consumers alongside collection frame watchers without adding construction edges",
        "melder.aether.conduit.meld.meld.Meld":
            "gates conduit-local resolution after structural recompilation so changed selection rebuilds its executor",
        "melder.aether.spellbook.spellbook_creation_system.SpellbookCreationSystem":
            "excludes non-resolvable definitions from executable cache payload and plan-phase eligibility",
        "melder.aether.spellbook.spell_compiler.topology.spell_local_topology.SpellSocketDescriptor":
            "retains descriptive referenced_spell_ids and parameter_kind separately from executable target_spell_ids",
        "melder.aether.spellbook.spell_compiler.phases.compiler_phase_3.CompilerPhase3":
            "selects resolvable providers or OVERRIDE_REQUIRED references while preserving declarations and False-root topology",
        "melder.aether.spellbook.spell_compiler.phases.compiler_phase_5.CompilerPhase5":
            "limits executable snapshots and blueprints to resolvable registrations while local descriptive topology stays owned by state",
        "melder.aether.spellbook.spell_compiler.phases.compiler_phase_8.CompilerPhase8":
            "skips non-resolvable definitions before executable occurrence analysis",
        "melder.aether.spellbook.spell_compiler.phases.compiler_phase_9.CompilerPhase9":
            "skips non-resolvable definitions before executable model fitting",
        "melder.aether.spellbook.spell_compiler.phases.compiler_phase_10.CompilerPhase10":
            "skips non-resolvable definitions before lazy planner creation or model consumption",
        "melder.aether.spellbook.spell_compiler.phases.compiler_phase_11.CompilerPhase11":
            "skips non-resolvable definitions before lazy codegen creation or executable artifact consumption",
        "melder.aether.spellbook.spell_compiler.phases.shared_compiler_executions.SharedCompilerExecutions":
            "exports required-input position, kind and reference IDs in override_required injection rows without changing ordinary row shapes",
        "melder.aether.spellbook.spell_compiler.validation.strategies.required_holes_strategy.RequiredHolesStrategy":
            "reports resolved OVERRIDE_REQUIRED inputs using durable local topology; descriptive roots have no construction obligations",
        "melder.aether.spellbook.spell_compiler.validation.strategies.binding_resolution_cycle_strategy.BindingResolutionCycleStrategy":
            "omits non-resolvable constructors and OVERRIDE_REQUIRED sockets from construction-cycle reconstruction",
        "melder.aether.spellbook.spell_compiler.validation.strategies.annotation_shape_guard_strategy.AnnotationShapeGuardStrategy":
            "retains ordinary Python annotation shapes on non-resolvable definitions without enforcing constructor-DI limits",
        "melder.aether.spellbook.spell_compiler.validation.strategies.parameter_policy_strategy.ParameterPolicyStrategy":
            "applies constructor-DI restrictions only to resolvable registrations",
        "melder.aether.spellbook.spell_compiler.validation.strategies.contract_provider_presence_strategy.ContractProviderPresenceStrategy":
            "caches provider IDs and capability together, rejects a selected False provider and skips False-root provider obligations",
        "melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_injection_analysis.SpellInjectionParamSource":
            "carries override_required position, parameter kind and descriptive references without dependency instance keys",
        "melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_injection_analysis.SpellInjectionInstanceSpec":
            "freezes required_override_params as name, position, kind and reference-ID value tuples",
        "melder.aether.spellbook.spell_compiler.artifact_processor.strategies.spell_injection_processor_strategy.SpellInjectionProcessorStrategy":
            "emits required supplied-input sources from local topology even without occurrence dependency entries",
        "melder.aether.spellbook.spell_compiler.codegen_planner.data.spell_generalized_codegen_lane_plan.SpellGeneralizedCodegenPlanStep":
            "retains required_override_params independently of optional override metadata in either lane",
        "melder.aether.spellbook.spell_compiler.codegen_planner.data.many_only_codegen_plan.ManyOnlyCodegenPlanStep":
            "retains required_override_params as plain values for either many-only lane",
        "melder.aether.spellbook.spell_compiler.spell_analyzer.strategies.spell_occurrence_graph_analyzer_strategy.SpellOccurrenceGraphAnalyzerStrategy":
            "signs complete required-input topology and refuses non-resolvable providers during late contract expansion",
    }
    for node_id, prose in additions.items():
        module_id = node_id.rsplit(".", 1)[0]
        path = root / (module_id.replace(".", "/") + ".json")
        document = json.loads(path.read_text(encoding="utf-8"))
        node = document["nodes"][node_id]
        responsibilities = node.setdefault("responsibilities", [])
        if prose not in responsibilities:
            responsibilities.append(prose)
        path.write_text(json.dumps(document, indent=1) + "\n", encoding="utf-8", newline="\n")

    for module_id, node_name, members in (
        ("melder.aether.spellbook.spell_compiler.dag.socket_kind", "SocketKind",
         ["NORMAL", "SPELL_CONTRACT", "OVERRIDE_REQUIRED"]),
        ("melder.aether.spellbook.spell_compiler.spell_requirements_finder.parameter_di_shape", "ParameterDIShape",
         ["IGNORE", "PLAIN", "SINGLE_BY_ANNOTATION", "COLLECTION_BY_ANNOTATION", "SPELLMAP_DEFAULT", "SPELL_CONTRACT"]),
    ):
        path = root / (module_id.replace(".", "/") + ".json")
        document = json.loads(path.read_text(encoding="utf-8"))
        node = document["nodes"][f"{module_id}.{node_name}"]
        node["owns_state"] = members
        node["responsibilities"] = ["labels the current " + ", ".join(members) + " categories"]
        path.write_text(json.dumps(document, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("Updated authored S3 responsibilities and corrected the two enum inventories.")


if __name__ == "__main__":
    main()
