from enum import Enum, auto


class Policies(Enum):
    """
    Access policies (evaluated only when system_state is dynamic):

    - default: normal per-spell rules/whitelist metadata.
    - whitelist_all: expose all local spells regardless of per-spell whitelist flags.
    - block_all: expose only spells explicitly marked with `meta["whitelist"] = True`.
    - inbound_only: accept inbound links/borrows but do not initiate outbound links.
    - outbound_only: initiate outbound links but reject inbound link requests.
    """
    default = auto()
    whitelist_all = auto()
    block_all = auto()
    inbound_only = auto()
    outbound_only = auto()
