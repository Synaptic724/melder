from enum import Enum
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg



class NexusFrameMode(Enum):
    """
    Internal

    Topology mode for Nexus-assigned internal frames.

    Purpose:
        Define how many internal Nexus frames exist and how new workspaces
        obtain them.

    Members:
        single:
            One shared Nexus-assigned frame is reused for all workspaces.
        indexed:
            Nexus may manage multiple internal frames from an indexed pool and
            assign workspaces into that shared set.
        one_per_workspace:
            Each workspace receives its own dedicated Nexus-assigned internal
            frame.

    Threading:
        Immutable enum members; safe to read from any thread.

    Registration:
        MELDER KERNEL - guarded, readable by value. Nexus configuration
        vocabulary.

    Subsystem Context:
        One of the process-wide policy vocabularies stored in
        `NexusConfiguration`, alongside the other frame topology controls.

    System Context:
        The three modes answer how many internal frames exist and how workspaces obtain them: `single` shares one, `indexed` allows named frames shared by name, and `one_per_workspace` gives each Rift a private frame. The mode also constrains raw authoring - under `one_per_workspace` direct manager creation is REJECTED because that path has no Rift owner identity to attribute the frame to.
        Because this is PROCESS-WIDE policy frozen at configuration time, the
        choice applies uniformly to every Rift - which is the point. A gate that
        varied per Rift could be escaped by creating a differently configured
        one, so the governance that matters lives here rather than on the Rift.
    """
    __ast_helper_access__: str = "public"
    __agent_purpose__: str = (
        "access: public. Frame topology: single (one shared), indexed (named, shared by name), "
        "one_per_workspace (private per Rift). Note one_per_workspace REJECTS raw manager creation - "
        "use the Rift-scoped path."
    )

    __melder_internal__ = _mrg.sentinel
    single = "single"
    indexed = "indexed"
    one_per_workspace = "one_per_workspace"
