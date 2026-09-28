# Calls of one warm `conduit.meld(spell_id=root_id)` (root many)

solo:
    py  Conduit.meld (conduit.py:4417)
    C   dict.get                              # fast-door lookup by spell id
    py  _creation_context_execute_no_overrides_only (creation-context template lane)
    py  _solo_no_overrides_codegen_creation_executor (the compiled executor)
    py  solo_Root.__init__

wide8_singleton:
    py  Conduit.meld
    C   dict.get                              # fast-door lookup
    py  _creation_context_execute_no_overrides_only
    py  _site_plan_executor                   # the compiled site plan
    C   dict.get x 8                          # one store read per singleton dependency
    py  wide8_singleton_Root.__init__

Reading: the door is two Python frames plus one dict.get before the executor; the executor is one frame;
constructors are one frame each; every singleton dependency is one dict.get. Transient dependencies add
no calls beyond their constructors.
