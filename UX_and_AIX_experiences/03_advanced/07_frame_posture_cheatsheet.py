"""
TIER: advanced (07)
GOAL: THE FRAME POSTURE CHEATSHEET - every AethericFrameConfiguration
      knob and what it does, in one runnable page (the advanced twin of
      beginner 37). The posture is the WORLD's law book: set before the
      first conjure, frozen by it, inherited by everyone after.

      MODE
        system_state ("automatic"|"dynamic") - the world's mode. Public
          doors: configure_aether_frame OR first conjure(dynamic=True).
      AR ELIGIBILITY (lived at the expert tier)
        ai_native_enabled - required True for dynamic AR targeting.
        rift_enabled      - required True for ANY Rift attachment.
      SHARING
        shared_framewide_spellbook_configuration - one rich config
          shared by every book on the frame instead of per-book copies.
      CACHING
        system_caching_enabled - conjure-artifact caching (lesson 06).
        system_cache_root_path - where cached artifacts live.
      DEVOPS BRAKES (each one turns OFF a structural verb, world-wide)
        disable_linking / disable_bind / disable_conduit_cluster /
        disable_transfer_of_ownership / disable_contract_mutation /
        disable_mutations / disable_all_transactions_after_conjure
        - a gated verb refuses with a "disabled" RuntimeError at its
          own door. NOTE: staging these currently requires the private
          retained posture (no public door yet - recorded finding).
      TRANSACTION PATIENCE
        max_transaction_wait_time_in_seconds - how long a structural
          transaction waits on a busy scope before refusing, naming
          who held it.
      PRESETS
        automatic_defaults() / dynamic_defaults() / with_defaults()
      THE FREEZE LAW
        First successful bind of the posture freezes it. Every with_*
        on a frozen posture refuses. One world, one law book.
SURFACE EXERCISED: the posture vocabulary (reference lesson)
"""
import melder as md


def main() -> None:
    knobs = {
        "mode": ["system_state"],
        "ar eligibility": ["ai_native_enabled", "rift_enabled"],
        "sharing": ["shared_framewide_spellbook_configuration"],
        "caching": ["system_caching_enabled", "system_cache_root_path"],
        "devops brakes": [
            "disable_linking", "disable_bind", "disable_conduit_cluster",
            "disable_transfer_of_ownership", "disable_contract_mutation",
            "disable_mutations", "disable_all_transactions_after_conjure",
        ],
        "patience": ["max_transaction_wait_time_in_seconds"],
        "presets": ["automatic_defaults", "dynamic_defaults", "with_defaults"],
    }
    total = 0
    for family, names in knobs.items():
        print(f"{family}:")
        for name in names:
            print("   ", name)
            total += 1
    print("posture knobs mapped:", total)
    assert total == 15
    print("the law book is set before first conjure and frozen by it")


if __name__ == "__main__":
    main()
