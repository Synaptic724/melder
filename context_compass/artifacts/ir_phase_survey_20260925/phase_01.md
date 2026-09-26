# Survey record: phase 1 (requirements)

Recorded 2026-09-25/26 by fable_0 (STORY-2026-08-03-phase-pipeline-survey, tranche task 1).
Status: COMPLETE. Read whole: `phases/compiler_phase_1.py` (207 lines),
`profiles/resolution_profile.py` (515), `spell_requirements_finder/spell_requirements_finder.py`
(1333, three chunks), `spell_requirements.py` (305), `spell_parameter_requirements.py` (311),
`parameter_di_shape.py` (70). All six files carry mtime 2026-08-29 (unchanged since read).
Ranges below without a file name are into `spell_requirements_finder.py`.

## Entry
- `CompilerPhase1.run(spell, artifact, cancel_event)` (phases/compiler_phase_1.py:105-165), called
  by `SpellCompiler.run_phase_requirements` (spell_compiler.py:129-158). Slot-only phase object.
- Delegate: `SpellRequirementsFinder(spell).build_requirements(cancel_event)` (:188-269), one finder
  per spell, result cached on the finder (:226-227, :268).

## Consumes
- `artifact._requirements` presence (idempotent: returns if already set) (compiler_phase_1.py:143-145).
- The bind-time profile chain `spell.profile.resolution_profile.requirements`, borrowed when live
  and keyed to the same `spell.spell_id` (compiler_phase_1.py:167-207). Bind ran the finder already
  via `SpellGeneralProfile.complete_with_spell` (docstring compiler_phase_1.py:172-176).
- Finder inputs, all read from the Spell: `spell.spell_type` (:236-240), `spell.spell` as the call
  target (:293-322), `spell.spell_index.selected_spell_id` (:253-257), `spell.existence`,
  `spell.spellframe`, `spell.binding_name` (:259-266); `spell.profile.binding_profile
  .original_object` / `.init_signature_object` for the borrowed Signature, identity-guarded by
  `original_object is call_target` (:324-349, :1019-1032).

## Produces
- `SpellRequirements(spell_id, spell_type, existence, spellframe, binding_name, parameters)`
  (:259-266; spell_requirements.py:71-114): ordered rows, one per signature parameter, including
  `self`/`cls`/`*args`/`**kwargs` marked IGNORE (:1061-1066). Each `SpellParameterRequirement`
  carries 13 fields (spell_parameter_requirements.py:73-146): name, position, kind
  (`inspect._ParameterKind`), annotation (normalized object or str), default_value (the exact
  object, or None), has_default, is_var_positional, is_var_keyword, is_keyword_only, is_optional,
  di_shape (`ParameterDIShape`), collection_element_annotation, spellmap_default (`SpellMap`).
- Existing-creation spell types yield an empty parameter list (:233-241). A call target without a
  usable signature (TypeError/ValueError from `inspect.signature`) also yields an empty list, silently
  (:1026-1032).
- Classification views on the artifact: `iter_di_parameters` (SINGLE_BY_ANNOTATION,
  COLLECTION_BY_ANNOTATION, SPELLMAP_DEFAULT) (spell_requirements.py:215-237),
  `iter_plain_parameters` (:239-259), `iter_required_holes` (PLAIN and no default) (:261-291).
  SPELL_CONTRACT rows are in neither view; their reader is UNKNOWN (phases 2-4).
- `artifact._requirements_shape_profile_phase1: Dict` - VALUE-ONLY: parameter_count,
  optional_parameter_count, per-shape counts, `di_shape_counts` as a sorted tuple of
  `(shape_name, count)` (compiler_phase_1.py:43-103). Deterministic by construction.
- Read later by: phase 2 (symbolic graph from requirements; driver docstring), strategy selection
  (shape profile; compiler_phase_1.py:48-52). Exact readers UNKNOWN until phases 2 and 8-9 are read.

## Holds (classified)
- `spell_id: str` (content SHA / selected id), `binding_name: Optional[str]`, `name: str`,
  `position: int`, the five bool flags -> VALUE.
- `spell_type: SpellType`, `existence: Existence`, `kind: inspect._ParameterKind`,
  `di_shape: ParameterDIShape` -> VALUE (enum names).
- `spellframe: Any` = a Protocol/interface TYPE, a str frame key, or None (spell_requirements.py:
  178-189) -> VALUE-EXPRESSIBLE as a type reference (module, qualname) or the string. Whether phases
  2-3 match it by object identity (`is`) rather than by name is UNKNOWN until they are read.
- `annotation: Any` and `collection_element_annotation: Any` = normalized typing object, bare class,
  or str (spell_parameter_requirements.py:210-219, :291-300). Normalization already reduces them to
  a closed grammar: list/set/frozenset/dict/tuple rebuilt through `__class_getitem__`, Optional as
  `Union[T, None]`, Union, ForwardRef to its name, unresolved strings kept (:774-840, :842-973)
  -> VALUE-EXPRESSIBLE as a type-ref tree whose leaves are (module, qualname) refs, unresolved
  strings, or literals. Today the leaves are LIVE user classes.
- `default_value: Any` = the EXACT default object for every parameter with a default, PLAIN ones
  included (:1051-1052, :1086). Three kinds: a `SpellContract` instance (di_shape SPELL_CONTRACT; the
  object stays in default_value) (:1163-1169); a `SpellMap` instance (SPELLMAP_DEFAULT; also copied to
  spellmap_default) (:1172-1178); anything else -> PLAIN, provider selection suppressed (:1183-1184).
  For PLAIN, whether any later phase PASSES the retained object (rather than letting Python apply
  the constructor's own default) is UNKNOWN and decides VALUE vs RUNTIME-ONLY. IDENTITY CANDIDATE
  #1: a PLAIN default that is a live instance, if a later phase passes it explicitly.
- `spellmap_default` / SpellContract default: Melder descriptor objects; value-expressibility
  depends on their fields (spell_map.py 344 lines, spell_contract.py 343 lines, unread) -> UNKNOWN.
- RUNTIME-ONLY baggage in the artifact itself: one `threading.RLock` per `SpellRequirements`
  (spell_requirements.py:106) and per `SpellParameterRequirement`
  (spell_parameter_requirements.py:132); Cleanable state; `.parameters` copies a fresh tuple on every
  read (spell_requirements.py:200-208).
- Finder-only, not in the artifact: `_spell: Spell` (:132), released at cleanup (:165-167).

## Mutates
- Nothing on Spell, Spellbook, SpellSystemStates or the frame. The finder reads the Spell and its
  profile only; "this finder never mutates the Spell" (:123-124) and no assignment to `spell` exists
  in the file. Its only write is `self._requirements` (:268). The phase-1 wrapper writes the
  artifact (compiler_phase_1.py:147-149, :161-162).

## Reflection points (reads of USER objects)
- `inspect.signature(call_target, annotation_format=Format.FORWARDREF)` unless the bind-time
  Signature is borrowed (:1025-1032; borrow :324-349).
- `get_annotations(annotation_target, format=Format.FORWARDREF)` on the class `__init__` or the
  callable (:472-484); `inspect.getmodule(call_target)` and its `__dict__`, `vars(call_target)`,
  `call_target.__globals__` as evaluation namespaces (:507-523).
- `inspect.get_annotations(..., eval_str=True, globals=, locals=)` EVALUATES string annotations in
  the user's module/class namespace; fallback FORWARDREF format; final fallback `{}` (:525-542).
- Name resolution walks namespaces and attribute chains with hasattr/getattr (:605-630, :706-719);
  `ast.parse` of annotation strings and rebuild of a safe subset (Name, Attribute, Constant, BitOr,
  Subscript) (:632-772); generics rebuilt via `__class_getitem__` on builtins and on arbitrary
  containers (:774-840, :925-973).
- Classification predicates: `inspect.isclass(annotation)` and `annotation.__module__`
  (:1324-1329); `get_origin`/`get_args` (:1191-1192, :1283-1284);
  `isinstance(default_value, SpellContract | SpellMap)` (:1163, :1172).
- Reflection is CONFINED to `_build_parameter_requirements` (per-parameter fact reads :1044-1059)
  and `_resolve_parameter_annotations` (:426-552). `_classify_parameter`, `_unwrap_optional` and
  `_looks_like_di_target` (:1100-1333) consume the results and perform no lookup beyond the
  type-shape predicates above.

## Python-callback points
- The user's callable, factory or hook is never invoked; `_resolve_call_target` returns
  `spell.spell` unchanged in all three branches (:293-322).
- User code CAN run indirectly: `eval_str=True` evaluates annotation expressions in the user's
  namespace (:525-531) and `container.__class_getitem__` invokes user generic machinery
  (:832-838). Both are best-effort and swallowed on failure (`except Exception` :532-542, :837-838).
- `cancel_event.throw_if_set()` (Melder-owned) between parameters (:275-291, :1045).

## World reads
- NONE. No Spellbook, registry, SpellSystemStates or frame lookup in any of the four finder files
  (each read whole). The only non-Spell read is the module-namespace lookup inside annotation
  evaluation, which is the user's module world, not Melder's.
- Consequence: phase 1 is already closed over (Spell facts, user module namespaces). Its closure test
  reduces to replaying the bind-time capture without re-importing the user module: true for the
  facts (signature, default kinds, annotation shapes), false for the live type objects unless they
  are re-resolved from (module, qualname) at hydration.

## Level-0 finding (epic open question: is reflection separable from classification?)
- YES, and it is an extraction, not a rename. The facts the classifier needs per parameter are:
  default_kind in {absent, spell_contract, spell_map, plain} (:1163-1184); annotation presence
  (:1187); the annotation as a tree of origin/args (:1191-1202, :1257-1285) with "list of one arg"
  (:1205) and the leaf tests `is typing.Any`, `in {int, float, str, bool, bytes, bytearray, complex,
  object, NoneType}`, `is ForwardRef`, `is str`, `isclass and __module__ != "builtins"`
  (:1310-1333). Every one is recordable as a value. `_classify_parameter` then becomes a pure
  function over that value tree; the shape enum and the three iterators already are pure
  (spell_requirements.py:215-291).
- The bind-time capture exists twice: `binding_profile.init_signature_object` (borrowed here,
  :324-349, proven only for class spells by the identity guard) and the profile-owned
  `SpellRequirements` that phase 1 borrows (compiler_phase_1.py:167-207). Level 0 value-shaped means
  replacing the object rows with value rows and re-resolving type refs where matching happens
  (phase 11, or phases 2-3 - UNKNOWN which).
- Unresolved names survive as strings and stay DI candidates (:1004-1007, :1316-1321): the IR needs
  an "unresolved reference" leaf, not only resolved refs.
- Determinism caveat for a hashed L0: annotation resolution depends on the module namespace at
  capture time (:507-523); the bind fingerprint (module fingerprint) is the staleness guard.

## Cost notes (counted from source; nothing measured - "Not run.")
- Per parameter row: 13 slots plus one RLock allocation; per artifact: one RLock; `.parameters`
  allocates a tuple per read (spell_requirements.py:208). Immutable value rows need no lock.

## Contradictions
- None against src_architecture.md (`:990-995`, PLAIN-default rule, confirmed at :1183-1184) or
  src_components.md (exact default object retained, confirmed at :1051-1052, :1086).
- `_resolve_call_target` documents three branches; all return `spell.spell` (:316-322). The
  docstring's "class -> the class object" holds only because `spell.spell` IS the class.

## Policy notes (recorded, not judged)
- `_borrow_bind_time_requirements` and `_borrow_bind_time_signature` wrap profile-chain reads in
  `try/except AttributeError` ("never raises") (compiler_phase_1.py:196-207; :338-349).
- `getattr(..., default)`/`hasattr` on user classes and modules (:474, :509, :512, :615-627, :717,
  :832, :1325) - external objects, permitted by the overlay. `except Exception` swallows
  annotation-evaluation failures (:532-542, :837-838) as documented best-effort.

## UNKNOWN (with where to look)
- Does any later phase pass a PLAIN `default_value` explicitly (value vs runtime-only)?
  phases/compiler_phase_3.py; codegen_creation_system emitters (tranche 3).
- Do phases 2-3 match `annotation`/`spellframe` by object identity or by name?
  phases/compiler_phase_2.py, phases/compiler_phase_3.py.
- Value-expressibility of SpellMap and SpellContract fields: conduit/meld/contracts/spell_map.py
  (1-344), spell_contract.py (1-343).
- Does `binding_profile` exist for method/lambda spells (borrow proven for class spells only)?
  spell_examiner/profiles/binding_profile.py, `_build_class_profile`.
- Who consumes SPELL_CONTRACT rows (excluded from both iterators)? phases 2-4 and the validation
  strategies (`contract_provider_presence_strategy.py`).
