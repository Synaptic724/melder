# UX_and_AIX_experiences (AGENTS.md)

Purpose: the living exploration of how HUMANS (UX) and AGENTS (AIX) use melder,
tiered beginner -> intermediate -> advanced -> expert (matched to the
README ladder, owner ruling 2026-07-22). Every example is written
against `import melder as md` ONLY - any example forced to reach a deep path is,
by definition, an init-surface gap and must be recorded on the owning epic.

Layout:
- 01_beginner/      first-contact + registration: bind, SpellBinder fluent, meld, lifecycles,
                    hooks, disposal, frames, errors, agent first-read.
                    TIER LAW: static conjure only - no dynamic, no Nexus, no MutationResearch,
                    no spellspaces. Existences: unique, many, unique_per_conduit
                    ONLY (lineage/spellspace -> tier 02; cluster -> tier 03).
                    DESIGN PRINCIPLE: teach a 4B-model agent with a 64k window
                    to be USEFUL - shared/fresh/scoped, dict-style frame ADDRESSING (frames are
                    grouping/contract keys, not dicts), typed
                    melds, Protocols, one bootstrap function. Fun and simple
                    beats complete.
- 02_intermediate/  linking + dynamic mode + configurations (owner fence:
                    NO Nexus, NO MutationResearch, NO crystallizer, and NO
                    AethericFrame objects - substrate stays invisible; the
                    _dynamic_world helper is a black box by design)
- 03_advanced/      frames as worlds, static rooms, clusters, deep overrides
- 04_expert/        AR rooms, transactions, checkpoints, governed mutation, external DB meshes

Laws:
- Examples are RUNNABLE scripts (3.14t) with a main() and honest printed asserts.
- Each file header states TIER / GOAL / SURFACE EXERCISED (the md.* names used).
- Examples never import melder submodule paths. md.* or it does not exist.
- Findings (gaps, awkward verbs, missing exports) go on the tier's epic ticket,
  then flow into the init composition story - examples are the evidence.

Tickets: context_compass/tickets/epics/2026-07-19_ux_aix_{tier}_experience_epic.md

## Verification harness

pytest_examples/ runs every example plus contract probes on 3.14t:

    pytest UX_and_AIX_experiences/pytest_examples -v

LAW (2026-07-19, after the bind(**kwargs) miss): examples may only assert
behavior VERIFIED in source or PROVEN by a probe row. Uncertain contracts get
a probe here first; the probe's printed outcome then hardens the example.

## Curriculum arc: categories (owner-directed 2026-07-20)

- The category idea threads the tiers. BEGINNER 25: spellframes as
  categories - organize spells WITHIN one world; (category, name) is the
  full address. INTERMEDIATE 26: conduits as categories - a wider frame;
  each category is its own world with an OWNER, and permissions +
  contracts + links set the resolution conditions at the category
  boundary. Same idea, organized differently: manage who owns what.

## Discovered runtime laws (harness run 3, 2026-07-20)

- SHARING IS A PULL: `X.add_spell_to_contract(spell_id=S, conduit=Y)` means
  "X pulls S from Y" - the conduit NAMED in the call must OWN the spell
  (ConduitWard._check_spell_if_eligible ownership check). Owner-pushes are
  refused with "not owned by this conduit".
- ONE ACTIVE SPELL PER SIGNATURE: the frame-wide LookupContainer claims one
  (frame_key, binding_name) per spell - collection-DI providers sharing a
  spellframe MUST carry distinct binding_names.
- CLUSTER STORE = ELECTED LEADER: unique_per_conduit_cluster melds hard-error
  ("cluster_creations is disabled") until `cluster.elect_leader(conduit_id)`
  runs; membership alone does not arm the team store.
- ONE BOOK, ONE CONJURE holds for lineage too: a second family is a second
  book; lineages GROW via create_lesser_conduit, never via re-conjure.
- SPELLCONTRACT ORDER OF OPERATIONS (owner ruling 2026-07-20, "the code is
  fine"): per dependency edge - 1) conjure the PROVIDER conduit, 2) conjure
  the CONSUMER conduit, 3) link() only AFTER both are built, 4) the consumer
  pulls the provider spell into the contract, 5) MELD after the fact - the
  meld completes the late binding for that world's products. Chains assemble
  edge by edge in dependency order. Skipping the cycle (e.g. never melding a
  middle world before handing its spell downstream) is USAGE ERROR: the
  un-melded consumer constructs with its Python default (the descriptor) -
  that is the misuse outcome, not a runtime gap.
- NORMAL CODE ONLY (owner ruling 2026-07-20): curriculum code never pulls
  mediator transactions into user flow - no transaction("link", ...) windows
  around add_spell_to_contract (the verb SELF-ADMITS its own transaction,
  conduit.py:4956) and no validate_contracts_and_define ceremony in lessons.
  The user surface is link / add_spell_to_contract / meld.
- HARNESS IMPORT LAW: spec-loaded lesson modules must be registered in
  sys.modules BEFORE exec_module - scan lessons look themselves up via
  sys.modules[__name__].

## Discovered runtime laws (harness runs 1-2, 2026-07-19)

- Callable spells (functions, lambdas, methods) are ALWAYS unique; lambdas
  additionally REQUIRE a binding_name. Fresh-per-meld factories are CLASSES
  bound "many".
- THE ADDRESS LAW: every spell lives at exactly one (frame_key, binding_key)
  address - frame_key = spellframe else normalized spell name; binding_key =
  binding_name else the default slot. Public positional strings and `spell=`
  strings are human SpellNames; classes/Protocols remain supported; opaque SHA
  identity uses explicit `spell_id=`. Human-name/class forms derive the frame key
  from the NAME (so they miss framed binds), and a bind with binding_name answers
  only when the meld carries the same binding_name. binding_name alone is refused.
- Spell NAMES are unique per book at conjure - CURRENT behavior refuses any
  name collision regardless of binding names, frames, or content SHA.
  DIVERGENCE FLAG: owner design intent (twice stated) is SHA256 content
  matching with binding-name disambiguation; DuplicateSpellNameStrategy
  ignores the disambiguators its own error message recommends. Tracked as a
  runtime bug candidate on the beginner epic. Until fixed: subclass-per-role
  (24) and collection-as-spell registries (33) are the working patterns.
- One book conjures ONE conduit ever (RuntimeError on the second); scopes are
  lesser conduits, extra roots are extra books.
- Unregistered meld raises one stable KeyError. Same-spell double-bind is
  refused at BIND time (RuntimeError).
- bind(**kwargs) is the hook channel and SWALLOWS unknown keys silently
  (flagged as a fail-fast design question); constructor config rides
  factories, prebuilt instances, or meld(override={...}).
- Disposal (disposal_method_names) fires at conduit.cleanup().
- Harness isolation: reset the Aether singleton + rebind Spellbook/
  Conduit._aether around every test (component-suite fixture, verbatim).
