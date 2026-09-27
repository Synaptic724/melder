"""R2 tests: follow the retirement of the old normal emitters - retargets, removals, new coverage, deletions.

Usage: python apply_r2_test_edits.py <tree_root> [--check]

Tests whose subject is live behavior move to the code that still carries it: the positional-prefix, collection,
shareability and payload emission contracts run through `emit_specialized_step_plan_source` (a leading captured
`unique` row makes the specializer emit every other row as the retired generic emitter did); the row-validation
tests call `_hydrate_steps_from_rows`; the root-key test uses the many_only module's identical helper; the many_only
signature test targets `build_many_only_executor_signature`; the serialized-cache test checks the hydrated steps'
live disposal lists. Tests of removed code only are removed by name through the AST. New coverage replaces what the
removed executor tests pinned: live ordered disposal lists and lock-free unique hits in site plans, and plan-family
disposal order through real cleanup. DELETES lists two owner benchmarks that monkeypatch the removed
`_all_steps_inlinable` (the caller removes them). Every anchor must match exactly once (or the stated count) and
every named test must exist, or nothing is written. Engine: ../r1_staging/apply_r1_test_edits.py.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "r1_staging"))

from apply_r1_test_edits import _apply as _apply_r1
from apply_r1_test_edits import _prune_orphans

U = "tests/unit/melder/spellbook/spell_compiler/"
ODC = U + "test_ordered_disposal_compiler.py"
POS = U + "test_generalized_positional_emission.py"
EMI = U + "test_generalized_emission_contracts.py"
CORE = U + "test_codegen_creation_core.py"
COMP = U + "test_codegen_creation_compilers_core.py"
REFS = U + "shared_assets/test_contract_override_refs.py"
LOW = U + "shared_assets/test_site_plan_lowering.py"
BIND = "tests/component/melder/spellbook/test_ordered_disposal_binding.py"
DELETES = [
    "benchmarks/testing_other_di/test_unroll_locals_microbench.py",
    "benchmarks/testing_other_di/test_unroll_path_diagnostic.py",
]

ODC_SERIALIZED_OLD = '''        payload = marshal.loads(marshal.dumps(
            generalized_manifest._build_no_overrides_lane_payload(no_overrides_plan=plan),
        ))
        fresh_pool = {spell_id: _spell(spell_id, list(names)) for spell_id in pool}
        executor = hydrate_no_overrides_executor(
            rows=payload["steps_rows"],
            transient_schema=payload["transient_schema"],
            root_instance_key=payload["root_instance_key"],
            root_spell_id=payload["root_spell_id"],
            spell_lookup=fresh_pool,
        )
        store = _make_recording_creations()
        assert executor(_meld_for(store)) == "root:base"
        assert len(store.add_many_calls) == 2
        for args, kwargs in store.add_many_calls:
            assert kwargs["disposal_methods"] == names
            assert kwargs["disposal_methods"] is fresh_pool[args[0]].disposal_method_names
            assert kwargs["disposal_methods"] is not pool[args[0]].disposal_method_names
'''
ODC_SERIALIZED_NEW = '''        payload = marshal.loads(marshal.dumps(
            generalized_manifest._build_no_overrides_lane_payload(no_overrides_plan=plan),
        ))
        fresh_pool = {spell_id: _spell(spell_id, list(names)) for spell_id in pool}
        # Normal melds run the site-plan runtime over these hydrated steps; it binds each step's
        # `spell.disposal_method_names` (shared_assets/test_site_plan_lowering.py pins that).
        steps = generalized_no._hydrate_steps_from_rows(
            steps_rows=payload["steps_rows"], spell_lookup=fresh_pool,
        )
        assert [step.spell.spell_id for step in steps] == ["leaf", "root"]
        for step in steps:
            assert step.spell.disposal_method_names == names
            assert step.spell.disposal_method_names is fresh_pool[step.spell.spell_id].disposal_method_names
            assert step.spell.disposal_method_names is not pool[step.spell.spell_id].disposal_method_names
'''
ODC_SERIALIZED_DOC = (
    '    """A marshal-safe manifest keeps ordered values, while row hydration binds fresh live lists."""\n',
    '    """A marshal-safe manifest keeps ordered values, while row hydration binds the fresh pool\'s live lists."""\n',
)

POS_DOC = (
    "Unit tests for the positional-dependency prefix in the generalized no-overrides emitter.\n",
    "Unit tests for the positional-dependency prefix in the generalized singleton specializer's emission.\n",
)
POS_TYPING = (
    "from typing import TYPE_CHECKING, Any, Dict, Sequence, Tuple\n",
    "from typing import TYPE_CHECKING, Any, Dict, Optional, Sequence, Tuple\n",
)
POS_IMPORT = (
    "    emit_specialized_step_plan_source,\n    emit_step_plan_source,\n    positional_dependency_names,\n",
    "    emit_specialized_step_plan_source,\n    positional_dependency_names,\n",
)
POS_CLASS_OLD_START = '''    ROWS = (
        _row("d1", "many"),
        _row("d2", "many"),
        _row("root", "many", [("first", ["d1"]), ("second", ["d2"]), ("third", ["d1"])]),
    )
'''
POS_CLASS_OLD_STOP = '''    def test_specialized_emitter_threads_prefix_to_non_captured_steps(self) -> None:
        """Non-captured steps compile with the same positional prefix as in the generic body."""
'''
POS_CLASS_NEW = '''    ROWS = (
        _row("single", "unique"),
        _row("d1", "many"),
        _row("d2", "many"),
        _row("root", "many", [("first", ["d1"]), ("second", ["d2"]), ("third", ["d1"])]),
    )

    @classmethod
    def _emit(cls, positional_dependency_names: Optional[Tuple[Tuple[str, ...], ...]]) -> str:
        """
        Emit the specializer's body with the leading unique row captured.

        The generic step emitter this class used to call was retired (R2, 2026-09-26); the
        specializer emits every non-captured row through the same per-step emitters.
        """
        return emit_specialized_step_plan_source(
            rows=cls.ROWS,
            captured_step_indexes=(0,),
            root_instance_key=("root", None),
            positional_dependency_names=positional_dependency_names,
        )

    def test_prefix_emits_positional_arguments_before_keywords(self) -> None:
        """Prefix values are bare positional arguments in prefix order; the rest stay keywords."""
        source = self._emit(((), (), (), ("first", "second")))
        assert _call_arguments(source, 3) == (
            "instance_1,",
            "instance_2,",
            "third=instance_1,",
        )

    def test_none_keeps_keyword_emission_unchanged(self) -> None:
        """Without prefixes the source is byte-identical to the keyword-only emission."""
        keyword_source = emit_specialized_step_plan_source(
            rows=self.ROWS,
            captured_step_indexes=(0,),
            root_instance_key=("root", None),
        )
        assert self._emit(None) == keyword_source
        assert _call_arguments(keyword_source, 3) == (
            "first=instance_1,",
            "second=instance_2,",
            "third=instance_1,",
        )

    def test_length_mismatch_raises(self) -> None:
        """One prefix tuple per row is required."""
        with pytest.raises(RuntimeError, match="exactly one entry per row"):
            self._emit(((), ()))

    def test_unknown_prefix_name_raises(self) -> None:
        """A prefix name that is not an emitted dependency of the step fails fast."""
        with pytest.raises(RuntimeError, match="'fourth' is not an emitted dependency of step 3"):
            self._emit(((), (), (), ("first", "fourth")))

    def test_specialized_emitter_threads_prefix_to_non_captured_steps(self) -> None:
        """Non-captured steps compile with the positional prefix they are given."""
'''

EMI_DOC_OLD = '''Emission-contract tests for the generalized no-overrides lane.

Purpose:
    Pin the emitted-source contracts landed in patch lane
    `generalized_singleton_specialization_2026_07_01` so refactors cannot
    silently regress them:
    - singleton warm-tail specialization emission (guards, capture aliases,
      root-collapse, deopt tail-call),
    - collection-DI inlinable emission (list literals, flat-cursor dict mode),
    - transient-lane body shape (per-slot factory defaults, per-step handlers,
      no live bookkeeping),
    - factory-source shareability (identity-free emission).
'''
EMI_DOC_NEW = '''Emission-contract tests for the generalized singleton specializer.

Purpose:
    Pin the emitted-source contracts landed in patch lane
    `generalized_singleton_specialization_2026_07_01` so refactors cannot
    silently regress them:
    - singleton warm-tail specialization emission (guards, capture aliases,
      root-collapse, deopt tail-call),
    - collection-DI inlinable emission (list literals, flat-cursor dict mode),
    - factory-source shareability (identity-free emission).
    The generic step and transient emitters were retired (R2, 2026-09-26); the
    per-step contracts they shared are pinned through the specializer, which
    emits every non-captured row with them.
'''
EMI_IMPORT = (
    "    EXECUTOR_NAME,\n    SPECIALIZED_EXECUTOR_NAME,\n    emit_specialized_step_plan_source,\n"
    "    emit_step_plan_source,\n",
    "    SPECIALIZED_EXECUTOR_NAME,\n    emit_specialized_step_plan_source,\n",
)
EMI_COLL_DOC = (
    '''    """
    Collection-DI params compile to order-preserving list literals.
    """
''',
    '''    """
    Collection-DI params compile to order-preserving list literals.

    A captured `unique` row leads each graph, so the specializer emits every
    other row through the shared per-step emitters these tests pin.
    """
''',
)
EMI_LOCALS = (
    '''        rows = (
            _row("d1", "many"),
            _row("d2", "many"),
            _row("root", "many", [("handlers", ["d1", "d2"])]),
        )
        source = emit_step_plan_source(
            rows=rows,
            root_instance_key=("root", None),
        )
        assert "handlers=[instance_0, instance_1]," in source
''',
    '''        rows = (
            _row("u0", "unique"),
            _row("d1", "many"),
            _row("d2", "many"),
            _row("root", "many", [("handlers", ["d1", "d2"])]),
        )
        source = emit_specialized_step_plan_source(
            rows=rows,
            captured_step_indexes=(0,),
            root_instance_key=("root", None),
        )
        assert "handlers=[instance_1, instance_2]," in source
''',
)
EMI_DICT = (
    '''        rows = (
            _row("d1", "many"),
            _row("d2", "many"),
            _row("odd", "many", callable_spell=False),
            _row("root", "many", [("handlers", ["d1", "d2"])]),
        )
        source = emit_step_plan_source(
            rows=rows,
            root_instance_key=("root", None),
        )
        assert (
            "handlers=[instance_results[step_dep_keys_3[0]], "
            "instance_results[step_dep_keys_3[1]]],"
        ) in source
''',
    '''        rows = (
            _row("u0", "unique"),
            _row("d1", "many"),
            _row("d2", "many"),
            _row("odd", "many", callable_spell=False),
            _row("root", "many", [("handlers", ["d1", "d2"])]),
        )
        source = emit_specialized_step_plan_source(
            rows=rows,
            captured_step_indexes=(0,),
            root_instance_key=("root", None),
        )
        assert (
            "handlers=[instance_results[step_dep_keys_4[0]], "
            "instance_results[step_dep_keys_4[1]]],"
        ) in source
''',
)
EMI_SHAPE = (
    '''        source_a = emit_step_plan_source(
            rows=rows_a, root_instance_key=("bbb", None))
        source_b = emit_step_plan_source(
            rows=rows_b, root_instance_key=("yyy", None))
''',
    '''        source_a = emit_specialized_step_plan_source(
            rows=rows_a, captured_step_indexes=(0,),
            root_instance_key=("bbb", None))
        source_b = emit_specialized_step_plan_source(
            rows=rows_b, captured_step_indexes=(0,),
            root_instance_key=("yyy", None))
''',
)
EMI_PAYLOAD = (
    '''        rows = (
            _row("d1", "many"),
            _payload_row(
                "root", "many", deps=[("dep", ["d1"])],
                payload=[("cfg", "CFGVAL")], positional=("P0",),
                uses_positional=True,
            ),
        )
        source = emit_step_plan_source(
            rows=rows, root_instance_key=("root", None),
        )
        assert "instance_results" not in source
        assert "*positional_1," in source
        assert "cfg=contract_values_1[0]," in source
        assert "dep=instance_0," in source
        assert "positional_1 = step_positional_args[1]" in source
        assert "contract_values_1 = step_contract_values[1]" in source
''',
    '''        rows = (
            _row("u0", "unique"),
            _row("d1", "many"),
            _payload_row(
                "root", "many", deps=[("dep", ["d1"])],
                payload=[("cfg", "CFGVAL")], positional=("P0",),
                uses_positional=True,
            ),
        )
        source = emit_specialized_step_plan_source(
            rows=rows, captured_step_indexes=(0,),
            root_instance_key=("root", None),
        )
        assert "instance_results" not in source
        assert "*positional_2," in source
        assert "cfg=contract_values_2[0]," in source
        assert "dep=instance_1," in source
        assert "positional_2 = step_positional_args[2]" in source
        assert "contract_values_2 = step_contract_values[2]" in source
''',
)
EMI_ZERO = (
    '''        rows = (_payload_row("solo_p", "many", payload=[("x", 42)]),)
        source = emit_step_plan_source(
            rows=rows, root_instance_key=("solo_p", None),
        )
        assert "x=contract_values_0[0]," in source
        assert "target_0()" not in source
''',
    '''        rows = (
            _row("u0", "unique"),
            _payload_row("solo_p", "many", payload=[("x", 42)]),
        )
        source = emit_specialized_step_plan_source(
            rows=rows, captured_step_indexes=(0,),
            root_instance_key=("solo_p", None),
        )
        assert "x=contract_values_1[0]," in source
        assert "target_1()" not in source
''',
)

CORE_IMPORT_MODULE = (
    "import melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.steps."
    "many_only_no_overrides_codegen_creation_step as many_only_no_overrides_step_module\n",
    "import melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.manifest."
    "many_only_manifest as many_only_manifest_module\n",
)
CORE_IMPORT_STEP = (
    "from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.steps."
    "many_only_no_overrides_codegen_creation_step import (\n    ManyOnlyNoOverridesCodegenCreationStep,\n)\n",
    "",
)
CORE_SIGNATURE_START = '''def test_many_only_no_overrides_step_records_many_executor_and_signature(
'''
CORE_SIGNATURE_STOP = '''def test_solo_codegen_creation_strategy_builds_solo_owned_runtime_doors(
'''
CORE_SIGNATURE_NEW = '''def test_many_only_executor_signature_hashes_the_lane_parts_in_order(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    The many-only manifest signs its lane from plan data only, in a fixed part order.

    `build_many_only_executor_signature` was lifted from the retired eager step (R2,
    2026-09-26) and must hash the same parts in the same order, so existing manifests keep
    their signatures: root spell id, normalized root key, one row per step, call modes, root
    step index, per-step disposal flags.
    """
    first_step, second_step = object(), object()
    no_overrides_plan = SimpleNamespace(
        root_spell_id="root",
        root_instance_key=("root", None),
        steps=(first_step, second_step),
        step_call_modes=(0, 1),
        root_step_index=0,
        step_has_disposal_methods=(False, True),
    )
    helpers = many_only_manifest_module.ManyOnlyCodegenCreationHelpers
    monkeypatch.setattr(
        helpers, "build_no_overrides_step_signature_row", lambda step: ("step", id(step)),
    )
    monkeypatch.setattr(
        helpers, "normalize_instance_key", lambda instance_key: ("normalized", instance_key),
    )
    monkeypatch.setattr(helpers, "hash_signature", lambda *parts: parts)

    assert many_only_manifest_module.build_many_only_executor_signature(no_overrides_plan) == (
        "root",
        ("normalized", ("root", None)),
        (("step", id(first_step)), ("step", id(second_step))),
        (0, 1),
        0,
        (False, True),
    )


'''

COMP_REMOVED = [
    "test_no_overrides_compiler_requires_ir_payload",
    "test_no_overrides_compiler_returns_none_when_no_steps_exist",
    "test_no_overrides_compiler_from_plan_validates_plan_and_empty_steps",
    "test_no_overrides_compiler_supports_transient_unrolled_only_for_many_non_registering_steps",
    "test_no_overrides_compiler_normalizes_transient_schema_and_rejects_bad_lengths",
    "test_no_overrides_compiler_supports_schema_rows_execution",
    "test_no_overrides_compiler_uses_emitted_step_source_when_transient_source_unavailable",
    "test_no_overrides_compiler_spellspace_route_reuses_existing_spellspace_singleton",
    "test_no_overrides_compiler_existing_hit_skips_locks",
]
COMP_MODULE_IMPORT = (
    "import melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers."
    "generalized_no_overrides_codegen_creation_compiler as no_overrides_compiler_module\n",
    "import melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers."
    "generalized_no_overrides_codegen_creation_compiler as no_overrides_compiler_module\n"
    "import melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.compilers."
    "many_only_no_overrides_codegen_creation_compiler as many_only_compiler_module\n",
)
COMP_SUBALL = [
    ("def test_no_overrides_compiler_resolves_root_instance_key_preferentially() -> None:\n",
     "def test_many_only_row_hydration_resolves_root_instance_key_preferentially() -> None:\n", 1),
    ("no_overrides_compiler_module._resolve_root_instance_key(\n",
     "many_only_compiler_module._resolve_root_instance_key(\n", 3),
    ('''        no_overrides_compiler_module.compile_no_overrides_codegen_creation_executor(
            codegen_ir={
                "steps_rows": (row,),
                "root_spell_id": "root",
            },
            spell_lookup={"root": _make_spell("root")},
        )
''', '''        no_overrides_compiler_module._hydrate_steps_from_rows(
            steps_rows=(row,),
            spell_lookup={"root": _make_spell("root")},
        )
''', 2),
    ('''        no_overrides_compiler_module.compile_no_overrides_codegen_creation_executor(
            codegen_ir={
                "steps_rows": (_make_no_overrides_step_row("root"),),
                "root_spell_id": "root",
            },
            spell_lookup=None,
        )
''', '''        no_overrides_compiler_module._hydrate_steps_from_rows(
            steps_rows=(_make_no_overrides_step_row("root"),),
            spell_lookup=None,
        )
''', 1),
    ('''        no_overrides_compiler_module.compile_no_overrides_codegen_creation_executor(
            codegen_ir={
                "steps_rows": (_make_no_overrides_step_row("root"),),
                "root_spell_id": "root",
            },
            spell_lookup={},
        )
''', '''        no_overrides_compiler_module._hydrate_steps_from_rows(
            steps_rows=(_make_no_overrides_step_row("root"),),
            spell_lookup={},
        )
''', 1),
    ('    """Schema-row no-overrides compile should fail', '    """Manifest row hydration should fail', 4),
    ('    """Build a minimal schema row accepted by the no-overrides compiler hydration."""\n',
     '    """Build a minimal schema row accepted by the generalized row hydration."""\n', 1),
]

REFS_EDITS = [
    ("replace", "    assert ManyOnlyCodegenCreationHelpers.freeze_value(value) == value\n", ""),
    ("replace",
     '    """The many-only signature and override rows write scalars as-is and objects as references."""\n',
     '    """The many-only signature row writes scalars as-is and objects as references."""\n'),
    ("replace", "    override_row = ManyOnlyCodegenCreationHelpers.build_override_step_row(step)\n", ""),
    ("replace",
     '    assert override_row["contract_payload_items"] == (("level", 3), ("marker", refs["marker"]))\n'
     '    assert override_row["contract_positional_override"] == (1, refs["__args__"][1])\n', ""),
]

LOW_APPEND = '''

class _DisposalRecordingStore(FakeStore):
    """A FakeStore that also keeps the disposal list object each registration passed."""

    def __init__(self) -> None:
        """Start empty."""
        super().__init__()
        self.disposal_lists: List[Tuple[str, Optional[List[str]]]] = []

    def add_creation(self, key: str, item: Any, *, has_disposal_methods: bool = False,
                     disposal_methods: Optional[List[str]] = None) -> None:
        """Publish, then record the list passed."""
        super().add_creation(key, item, has_disposal_methods=has_disposal_methods, disposal_methods=disposal_methods)
        self.disposal_lists.append((key, disposal_methods))

    def add_many_creations(self, key: str, item: Any, *, has_disposal_methods: bool = False,
                           disposal_methods: Optional[List[str]] = None) -> None:
        """Record the many registration and the list passed."""
        super().add_many_creations(
            key, item, has_disposal_methods=has_disposal_methods, disposal_methods=disposal_methods,
        )
        self.disposal_lists.append((key, disposal_methods))


def test_registration_passes_each_spells_live_ordered_disposal_list() -> None:
    """A many dependency and a shared site both register with their Spell's own list object, order intact."""
    built: Counter = Counter()
    spells = {
        "d": _spell("d", built, disposal=("stop", "flush", "close")),
        "s": _spell("s", built, Existence.unique_per_conduit, disposal=("close", "stop")),
        "root": _spell("root", built),
    }
    steps = (
        _step(("d", 2), spells["d"]),
        _step(("s", None), spells["s"], ("d", (("d", 2),))),
        _step(("root", 0), spells["root"], ("s", (("s", None),))),
    )
    topologies = {
        "root": SpellLocalTopology("root", (_socket("root", "s", 0),)),
        "s": SpellLocalTopology("s", (_socket("s", "d", 0),)),
    }
    plan = _compile_plan(steps, topologies, ("root", 0))
    store = _DisposalRecordingStore()
    plan(SimpleNamespace(_spellspace_creations=None, _conduit_creations=store), {})
    assert [key for key, _passed in store.disposal_lists] == ["d", "s"]
    for key, passed in store.disposal_lists:
        assert passed == spells[key].disposal_method_names
        assert passed is spells[key].disposal_method_names


class _ExplodingGuard:
    """A lock stand-in whose acquisition fails the test."""

    def __enter__(self) -> None:
        """Fail: the path under test must not take a lock."""
        raise AssertionError("a warm hit must not take a lock")

    def __exit__(self, *exc_info: Any) -> None:
        """Nothing to release."""
        return None


def test_unique_warm_hit_takes_neither_the_spell_lock_nor_a_slot_guard() -> None:
    """A stored `unique` dependency is read from its owner store without the Spell lock or a slot guard."""
    built: Counter = Counter()
    spells = {"s": _spell("s", built, Existence.unique), "root": _spell("root", built)}
    stored = object()
    owner_store = spells["s"]._owner_creations
    owner_store._creations["s"] = stored
    owner_store.slot_guard = lambda spell_id: _ExplodingGuard()
    spells["s"]._lock = _ExplodingGuard()
    steps = (
        _step(("s", None), spells["s"], lock_hint=True),
        _step(("root", 0), spells["root"], ("s", (("s", None),))),
    )
    topologies = {"root": SpellLocalTopology("root", (_socket("root", "s", 0),))}
    plan = _compile_plan(steps, topologies, ("root", 0))
    result = plan(SimpleNamespace(_spellspace_creations=None, _conduit_creations=FakeStore()), {})
    assert result.args == (stored,)
    assert built == Counter({"root": 1})
'''

BIND_APPEND = '''

class OrderedDisposalConsumer:
    """Consume one disposal-bearing service, so a site plan (not the solo lane) builds the service."""

    def __init__(self, service: OrderedDisposalService) -> None:
        """Keep the injected service."""
        self.service = service


@pytest.mark.parametrize("service_existence", ["many", "unique_per_conduit"])
@pytest.mark.parametrize("priority,expected", [
    (False, ["stop", "flush", "close"]),
    (True, ["flush", "close", "stop"]),
])
def test_plan_families_dispose_dependencies_in_bound_order(
        service_existence: str,
        priority: bool,
        expected: list[str],
) -> None:
    """A dependency built by a site plan (many_only when all-many, generalized otherwise) disposes in bound order."""
    with configured_book(["flush", "close"], priority) as book:
        book.bind(
            spell=OrderedDisposalService, existence=service_existence, disposal_method_names=["close", "stop"],
        )
        consumer_id = book.bind(spell=OrderedDisposalConsumer, existence="many")
        conduit = book.conjure()
        consumer = conduit.meld(spell_id=consumer_id)
        conduit.permanent_cleanup()
        assert consumer.service.calls == expected
'''

EDITS = {
    ODC: [("defs", ["test_family_executors_register_current_lists"]),
          ("replace", ODC_SERIALIZED_OLD, ODC_SERIALIZED_NEW), ("replace",) + ODC_SERIALIZED_DOC],
    POS: [("replace",) + POS_DOC, ("replace",) + POS_TYPING, ("replace",) + POS_IMPORT,
          ("cut", POS_CLASS_OLD_START, POS_CLASS_OLD_STOP), ("insert_before", POS_CLASS_OLD_STOP, POS_CLASS_NEW)],
    EMI: [("replace", EMI_DOC_OLD, EMI_DOC_NEW), ("replace",) + EMI_IMPORT, ("defs", ["TestTransientBodyContract"]),
          ("replace",) + EMI_COLL_DOC, ("replace",) + EMI_LOCALS, ("replace",) + EMI_DICT, ("replace",) + EMI_SHAPE,
          ("replace",) + EMI_PAYLOAD, ("replace",) + EMI_ZERO],
    CORE: [("replace",) + CORE_IMPORT_MODULE, ("replace",) + CORE_IMPORT_STEP,
           ("cut", CORE_SIGNATURE_START, CORE_SIGNATURE_STOP),
           ("insert_before", CORE_SIGNATURE_STOP, CORE_SIGNATURE_NEW)],
    COMP: [("defs", COMP_REMOVED), ("replace",) + COMP_MODULE_IMPORT] + [("suball",) + sub for sub in COMP_SUBALL],
    REFS: REFS_EDITS,
    LOW: [("append", LOW_APPEND)],
    BIND: [("append", BIND_APPEND)],
}


def _nl_near(data: str, index: int) -> str:
    """Return the line ending of the line containing `index` (CRLF files and mixed files alike)."""
    end = data.find("\n", index)
    return "\r\n" if end > 0 and data[end - 1] == "\r" else "\n"


def _apply(data: str, edit: tuple, rel: str) -> str:
    """Apply one edit: `append`, `insert_before`, `cut`, `suball` here; everything else through the R1 engine."""
    kind = edit[0]
    if kind == "append":
        nl = "\r\n" if data.endswith("\r\n") else "\n"
        return data.rstrip("\r\n") + nl + edit[1].lstrip("\n").replace("\n", nl).rstrip("\r\n") + nl
    if kind == "insert_before":
        for variant in (edit[1].replace("\n", "\r\n"), edit[1]):
            if data.count(variant) == 1:
                index = data.index(variant)
                return data[:index] + edit[2].replace("\n", _nl_near(data, index)) + data[index:]
        raise SystemExit(f"{rel}: insert anchor not found exactly once: {edit[1][:60]!r}")
    if kind == "cut":
        for start, stop in ((edit[1].replace("\n", "\r\n"), edit[2].replace("\n", "\r\n")), (edit[1], edit[2])):
            if data.count(start) == 1 and data.count(stop) == 1 and data.index(start) < data.index(stop):
                return data[:data.index(start)] + data[data.index(stop):]
        raise SystemExit(f"{rel}: cut anchors not found exactly once, in order: {edit[1][:60]!r}")
    if kind == "suball":
        _, old, new, count = edit
        for variant_old, variant_new in ((old.replace("\n", "\r\n"), new.replace("\n", "\r\n")), (old, new)):
            if data.count(variant_old) == count:
                return data.replace(variant_old, variant_new)
        raise SystemExit(f"{rel}: expected {count} matches of {old[:60]!r}")
    return _apply_r1(data, edit, rel)


def main() -> None:
    """Check every anchor and every file to delete, then write every file (unless --check)."""
    root = pathlib.Path(sys.argv[1])
    check = "--check" in sys.argv[2:]
    for rel in DELETES:
        if not (root / rel).is_file():
            raise SystemExit(f"missing file to delete: {rel}")
    pending = {}
    for rel, edits in EDITS.items():
        path = root / rel
        original = path.read_bytes().decode("utf-8")
        data = original
        for edit in edits:
            data = _apply(data, edit, rel)
        data = _prune_orphans(original, data, rel)
        compile(data, rel, "exec")
        pending[path] = data
    for path, data in pending.items():
        if not check:
            path.write_bytes(data.encode("utf-8"))
        print(("checked " if check else "edited ") + str(path))
    for rel in DELETES:
        print("to delete: " + rel)


if __name__ == "__main__":
    main()
