from enum import Enum, auto
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class Permissions(Enum):
    """
    Capability ceiling for a spell lineage in ward-local and contracted views.

    `ConduitWard` uses this enum in two related places:

    - on the spell itself, as the local maximum capability the owning conduit
      is willing to expose
    - on each contract detail, as the capability actually granted to a peer for
      that lineage

    The values are ordered by how much downstream behavior they permit, and the
    ward logic deliberately never escalates a contracted lineage beyond the
    spell's own local permission.

    - `read`:
      the lineage may be resolved and inspected through a contract, but it
      cannot be used as a creation-capable dependency when propagating work
      into another conduit.

    - `create`:
      the lineage may participate in creation-capable dependency resolution and
      therefore also implies ordinary read/resolve access.

    - `block`:
      the lineage should not be contractable in normal flows. The ward treats
      this as a hard stop unless a broader override policy such as
      `Policies.whitelist_all` explicitly allows exposure.
    """
    __melder_internal__ = _mrg.sentinel
    read = auto()   # Allows read/resolve access only.
    create = auto() # Allows creation-capable use and implies read.
    block = auto()  # Blocks sharing/contracting in normal flows.
