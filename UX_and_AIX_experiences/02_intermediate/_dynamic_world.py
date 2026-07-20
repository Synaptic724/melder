"""
Support helper for the dynamic-mode lessons. The full setup is taught in
lesson 21. KEY SEMANTIC: the world's posture is set ONCE and locks -
this helper postures the world only if it is not already dynamic, and
every later call just builds a book into the already-postured world.
"""
import melder as md


def ensure_dynamic_world(frame: str = "default") -> None:
    """Posture the world dynamic ONCE; no-op when already dynamic."""
    hosting_frame = md.Aether()._ensure_frame(frame)
    current = md.Aether()._get_aetheric_frame_configuration(frame)
    if current is not None and current.system_state == md.SystemState.dynamic:
        return  # already postured; the frame locks - never rebind
    hosting_frame.bind_frame_configuration(md.AethericFrameConfiguration(
        origin_spellbook_id=None,
        system_state=md.SystemState.dynamic,
        ai_native_enabled=False,
        rift_enabled=False,
    ))


def dynamic_spellbook(frame: str = "default") -> md.Spellbook:
    """Build a book in a dynamic world (posturing it first if needed)."""
    ensure_dynamic_world(frame)
    configuration = md.SpellbookConfiguration()
    configuration.with_defaults()
    return md.Spellbook(configuration=configuration)
