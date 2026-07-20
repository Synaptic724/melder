"""
Support helper for the dynamic-mode lessons. The FULL setup ritual is
written out and taught in lesson 21 (both configuration layers, in the
open); this helper repeats it verbatim so lessons 22-25 stay focused on
their own subject. Deeper substrate mechanics remain tier-03 material.
"""
import melder as md


def dynamic_spellbook(frame: str = "default") -> md.Spellbook:
    """Return a Spellbook whose world allows dynamic conjure."""
    hosting_frame = md.Aether()._ensure_frame(frame)
    hosting_frame.bind_frame_configuration(md.AethericFrameConfiguration(
        origin_spellbook_id=None,
        system_state=md.SystemState.dynamic,
        ai_native_enabled=False,
        rift_enabled=False,
    ))
    configuration = md.SpellbookConfiguration()
    configuration.with_defaults()
    return md.Spellbook(configuration=configuration)
