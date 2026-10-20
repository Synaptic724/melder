"""melder_0, 2026-10-18: S1's statements sweep (the architecture patch, "Statements That Define the spell_id Today",
and the Binding Pipeline patch's Interface Deltas): the docstrings, comments and refusal texts that described the
spell_id as a fingerprint over the bind call now say it is the SHA256 of the registered object's code. No logic
changes; the two collision refusals add the colliding spell_id to their message. bind.py, spell.py, the binding
profiles, the cache files and the crystallizer files carry their own lists (edits_bind, edits_spell, edits_profiles,
edits_cache, edits_crystal)."""
from apply_common import Applier
from edits_profiles import scoped

SPELLBOOK = "src/melder/aether/spellbook/spellbook.py"
SPELL_INDEX = "src/melder/aether/spellbook/bind/spell_index.py"
LOOKUP = "src/melder/aether/aetheric_frame/lookup_container.py"
AETHER = "src/melder/aether/aether.py"
AETHER_CONFIGURATION = "src/melder/aether/aether_configuration.py"
STATES = "src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py"
MELD_DIR = "src/melder/aether/conduit/meld/"
DETAILS = "src/melder/aether/conduit/conduit_ward/contract/details.py"
INSPECTOR = "src/melder/aether/spellbook/spell_compiler/spell_examiner/inspectors/inspector_utility.py"

MELD_STRING_ARG = (
    "                - If a **string**, treated as the unique `spell_id` (typically the\n"
    "                  SHA256 structural fingerprint for the SpellIndex).\n",
    "                - If a **string**, treated as the unique `spell_id` (the SHA256 of\n"
    "                  the registered object's code that `bind` returned).\n")

INSPECT_DOCSTRING = (
    r"""              3. FINGERPRINT fallback - only if identity found nothing, the id is
                 re-derived from the object alone.
            - Stage 3 is a LEGACY path and rarely matches a registered binding. The spell
              fingerprint composes BIND-TIME facts (existence, disposal methods, binding
              name, spell name) that a bare class, function, or instance cannot supply, so
              an id re-derived from the object generally cannot equal the id recorded at
              bind. Identity matching exists precisely because of that.
""",
    r"""              3. CODE fallback - only if identity found nothing, the id is
                 re-derived from the object alone.
            - Stage 3 matches exactly: a spell_id is the SHA256 of the registered object's
              code (an existing object's class code plus its data) with nothing from the
              bind call, so the id re-derived from the object equals the id recorded at bind
              while the object's code and data are unchanged. Identity runs first: it is
              cheaper, and it still finds an object whose data changed after bind.
""")

INSPECT_FIRST_COMMENT = (
    r"""            # The spell fingerprint composes bind-time facts (existence,
            # disposal methods, binding name, spell name) that a bare
            # class/function/instance cannot supply, so re-deriving the
            # id from the object alone can never match a registered
            # binding. Resolve by object identity against this
            # Spellbook's registered spells first; fall back to the
            # legacy default-fact fingerprint for foreign objects so
            # cross-book inspection semantics stay unchanged.
""",
    r"""            # A spell_id is the object's code (SpellCodeDigest), so the id
            # re-derived from the object matches its registered binding
            # exactly while its code and data are what they were at bind.
            # Resolve by object identity against this Spellbook's
            # registered spells first - cheaper, and it still finds an
            # object whose data changed after bind - then frame-wide by
            # identity, and only then by the re-derived id (stage 3),
            # which the Aether registry confirms like the other stages.
""")

INSPECT_SECOND_COMMENT = (
    r"""            # Frame-wide object inspection: walk the frame's registered
            # conduits' spellbooks so foreign spells (cluster shares,
            # dynamic-link providers) remain inspectable by object, which
            # the legacy fingerprint path provided before bind-time facts
            # joined the id composition.
""",
    r"""            # Frame-wide object inspection: walk the frame's registered
            # conduits' spellbooks so foreign spells (cluster shares,
            # dynamic-link providers) are found by object identity too,
            # before stage 3 re-derives the id from the object's code
            # (an existing object whose data changed misses there).
""")

CONJURE_REFUSAL = (
    r"""            "A spell_id is a SHA256 over the bind-time fingerprint (structural profile, \n"
            "lookup signature, existence, and resolved disposal metadata) and does NOT \n"
            "include the frame, so two Spellbooks binding the same target with the same \n"
            "bind parameters mint the same id. That includes spells staged inactive \n"
            "by bind_inactive - a parked spell still holds its id. \n"
            "SCOPE: a spell_id is unique per PROCESS while "
            "`process_wide_unique_spell_ids` \n"
            "is on (the default), and per FRAME only when it is off. \n"
            "Fix: differentiate the binding with a distinct spellframe or "
            "binding_name. \n"
            "Moving to another aetheric frame is NOT a fix under the process-wide \n"
            "regime - the id follows the fingerprint, and the fingerprint has no frame \n"
            "in it."
""",
    r"""            "A spell_id is the SHA256 of the registered object's code (its methods, \n"
            "constructor, class-level values and base classes, or an existing object's \n"
            "class and data) and includes neither the frame nor the bind call, so two \n"
            "Spellbooks binding the same object mint the same id. That includes spells \n"
            "staged inactive by bind_inactive - a parked spell still holds its id. \n"
            "SCOPE: a spell_id is unique per PROCESS while "
            "`process_wide_unique_spell_ids` \n"
            "is on (the default), and per FRAME only when it is off. \n"
            "Fix: bind the object in one Spellbook and share it with the others (a link "
            "or a contract); one object is one spell. \n"
            "Moving to another aetheric frame is NOT a fix under the process-wide \n"
            "regime - the id follows the code, and the code has no frame \n"
            "in it."
""")

COLLISION_REFUSAL = (
    r"""                    raise RuntimeError(
                        "Spell ID collision detected. spell_id is computed from the spell's bind-time \n"
                        "fingerprint (e.g., structural profile, lookup signature, existence, and resolved \n"
                        "disposal metadata). The existing spell with this id is already registered in the \n"
                        "Spellbook or Aether for this frame. If you intended to register a distinct spell, ensure its \n"
                        "bind-time fingerprint differs so it produces a unique spell_id."
                    )
""",
    r"""                    raise RuntimeError(
                        "Spell ID collision detected: this object is already registered as spell_id "
                        f"{new_spell.spell_id}. A spell_id is the SHA256 of the object's code (its methods, \n"
                        "constructor, class-level values and base classes, or an existing object's class and \n"
                        "data), and one object is one spell: registering it again - under another binding \n"
                        "name, existence or spellframe, or in another Spellbook where spell_ids are unique \n"
                        "(the process by default, the frame under per-frame spell ids) - is refused. Use the \n"
                        "spell already registered (another conduit shares it through a link or a contract), \n"
                        "or cleanup_spell it and bind it again to change how it is bound. A changed method, \n"
                        "constructor, class-level value or base class is a new spell_id: stage it with \n"
                        "bind_inactive and notch to it."
                    )
""")


def spellbook(applier: Applier) -> None:
    """inspect_spell's stage 3, the conjure refusal, the research entry's Args and both collision refusals."""
    applier.edit(SPELLBOOK, [
        INSPECT_DOCSTRING,
        INSPECT_FIRST_COMMENT,
        INSPECT_SECOND_COMMENT,
        CONJURE_REFUSAL,
        ("                Binding-signature SHA256 entering the world.\n",
         "                The spell_id (the SHA256 of the registered object's code) entering the world.\n"),
    ], "spellbook")
    # The two refusals are the same text, one in each verb: each is replaced inside its own method.
    scoped(applier, SPELLBOOK, "    def bind_inactive(\n", "    def _record_research_world_entry(\n",
           [COLLISION_REFUSAL], "bind_inactive refusal")
    scoped(applier, SPELLBOOK, "    def bind(\n", "    def scan(self, module: ModuleType) -> list[str]:\n",
           [COLLISION_REFUSAL], "bind refusal")


def frame_and_registry(applier: Applier) -> None:
    """The frame's signature container, Aether's process-wide sweep, the regime default, the verdict docstring."""
    applier.edit(LOOKUP, [
        ("          method, so the two never diverge. The relationship is 1:1: the\n"
         "          binding signature is folded into the spell_id fingerprint, so a given\n"
         "          spell_id occupies exactly one signature.\n",
         "          method, so the two never diverge. The relationship is 1:1: one\n"
         "          object registers once (bind refuses a second registration of its\n"
         "          spell_id, the object's code), so a spell_id occupies one signature.\n"),
    ], "lookup_container")
    applier.edit(AETHER, [
        ("        # process-wide regime another frame still might, because spell_id is a\n"
         "        # SHA256 over the bind-time fingerprint and does NOT include the frame -\n"
         "        # the same target bound with the same parameters mints the same id\n"
         "        # everywhere. Owner ruling 2026-08-02: one spell_id means one spell,\n",
         "        # process-wide regime another frame still might, because spell_id is the\n"
         "        # SHA256 of the registered object's code and does NOT include the frame -\n"
         "        # the same object mints the same id everywhere, however it is bound.\n"
         "        # Owner ruling 2026-08-02: one spell_id means one spell,\n"),
    ], "aether")
    applier.edit(AETHER_CONFIGURATION, [
        ("            # DEFAULT ON. A spell_id is a SHA256 over the bind-time fingerprint\n"
         "            # and does not include the frame, so the same target bound with the\n"
         "            # same parameters mints the same id in every frame. Owner ruling\n",
         "            # DEFAULT ON. A spell_id is the SHA256 of the registered object's\n"
         "            # code and does not include the frame, so the same object mints the\n"
         "            # same id in every frame, however it is bound. Owner ruling\n"),
        ("              bind of the same fingerprint is refused anywhere in the process.\n",
         "              bind of the same object is refused anywhere in the process.\n"),
    ], "aether_configuration")
    applier.edit(STATES, [
        ("        same class at the same address mints the same id for a new Spell with\n",
         "        same class mints the same id (the class's code) for a new Spell with\n"),
    ], "spell_system_states")
    applier.edit(SPELL_INDEX, [
        ("              atomic. This property is the hottest fingerprint read in the\n",
         "              atomic. This property is the hottest spell_id read in the\n"),
    ], "spell_index")


def meld_and_contracts(applier: Applier) -> None:
    """The three meld doors' `spell` argument, Meld's resolvers, the contract rows' `has_spell`, `stable_repr`."""
    for name in ("conduit_meld.py", "meld.py", "spellspace_meld.py"):
        applier.edit(MELD_DIR + name, [MELD_STRING_ARG], name)
    applier.edit(MELD_DIR + "meld.py", [
        ("        1. A direct spell_id string (SHA256 fingerprint), or\n",
         "        1. A direct spell_id string (the SHA256 of the registered object's code), or\n"),
        ("                The SHA256 fingerprint associated with the spell.\n",
         "                The spell's spell_id - the SHA256 of the registered object's code.\n"),
    ], "meld resolvers")
    applier.edit(DETAILS, [
        ("            spell_id: SHA fingerprint to check within the index member history.\n",
         "            spell_id: Spell id (the SHA256 of an object's code) to check within the index member history.\n"),
        ("            spell_id: SHA fingerprint to check within the index member set.\n",
         "            spell_id: Spell id (the SHA256 of an object's code) to check within the index member set.\n"),
    ], "details")
    applier.edit(INSPECTOR, [
        ("            Give the bind fingerprint a representation that is identical in every process for the\n",
         "            Give the code digest behind a spell_id a representation that is identical in every process for the\n"),
    ], "inspector_utility")


def apply(applier: Applier) -> None:
    """Stage every statement edit."""
    spellbook(applier)
    frame_and_registry(applier)
    meld_and_contracts(applier)
