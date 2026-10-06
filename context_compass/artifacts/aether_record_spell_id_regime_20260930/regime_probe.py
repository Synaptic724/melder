"""
Probe: what happens when a world recorded under one spell-id regime is restored in a fresh process.

Two processes per case, because Melder's roots are process singletons:
    python regime_probe.py record <world> <cache_dir>            -> prints the checkpoint id and the Aether twin
    python regime_probe.py restore <world> <cache_dir> <id> <mode>
worlds: perframe_same_class, perframe_distinct, processwide_distinct
modes:  plain (fresh process, nothing configured) | perframe_first (host installs per-frame ids before restoring)
Every result line is JSON prefixed with RESULT; the cache root is redirected into <cache_dir>.
"""
import json
import pathlib
import sys
import traceback

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))


def _redirect_cache(cache_dir: str) -> None:
    """Point the crystallizer cache at the probe's own directory (the integration tests do the same)."""
    from melder.crystallizer.asset_management import crystallizer_cache

    root = pathlib.Path(cache_dir) / "__melder_cache__" / "__crystallizer_cache__"
    crystallizer_cache.CrystallizerCache.resolve_cache_root_path = staticmethod(lambda: root)


def _per_frame_ids() -> None:
    """Install and activate a per-frame spell-id policy before any frame exists."""
    from melder import Aether, AetherConfiguration

    policy = AetherConfiguration().with_defaults().with_process_wide_unique_spell_ids(False)
    Aether().configure(policy)
    policy.activate()
    Aether().activate()


def _crystallizer_on():
    """Activate the Aether-hosted crystallizer with default knobs."""
    from melder import Aether, CrystallizerConfiguration

    crystallizer = Aether().crystallizer
    policy = CrystallizerConfiguration().with_defaults()
    crystallizer.configure(policy)
    policy.activate()
    crystallizer.activate()
    return crystallizer


def _book(frame: str, cls: type, name: str) -> None:
    """One Book in a frame postured dynamic BEFORE its bind (the recorded lane), one bind, one named conjure.

    configure_aether_frame is the public pre-settlement door: it sets the frame's system_state and freezes the
    Book's rich configuration, so the bind runs in a dynamic frame under a finalized configuration and records.
    """
    from melder import Spellbook, SpellbookConfiguration

    book = Spellbook(aetheric_frame=frame, configuration=SpellbookConfiguration(frame).with_defaults())
    book.configure_aether_frame(system_state="dynamic", disposal=None, disposal_method_names=None)
    book.bind(spell=cls, existence="many")
    book.conjure(name=name, dynamic=True)


def _emit(**fields: object) -> None:
    """Print one JSON result line."""
    print("RESULT " + json.dumps(fields, default=str, sort_keys=True))


def record(world: str, cache_dir: str) -> None:
    """Build and record one world, flush its checkpoint to the cache, print the id and the Aether twin payload."""
    import melder
    from melder import Aether
    from regime_services import OtherService, TenantService

    _redirect_cache(cache_dir)
    if world.startswith("perframe"):
        _per_frame_ids()
    crystallizer = _crystallizer_on()
    _book("tenant_a", TenantService, "root_a")
    _book("tenant_b", TenantService if world == "perframe_same_class" else OtherService, "root_b")
    checkpoint_id = crystallizer.create_checkpoint()
    crystallizer.flush_checkpoint(checkpoint_id)
    replay = crystallizer.checkpoint_replay_data(checkpoint_id)
    (pathlib.Path(cache_dir) / "replay.json").write_text(json.dumps(replay, default=str, indent=1))
    aether_twin = replay.get("payloads", {}).get("aether")
    _emit(step="record", world=world, melder=melder.__version__, melder_file=melder.__file__,
          regime_in_force=Aether()._process_wide_unique_spell_ids,
          reported_regime=Aether().configuration.process_wide_unique_spell_ids,
          frames=sorted(Aether().list_frame_names()), checkpoint_id=checkpoint_id,
          replay_keys=sorted(replay.keys()) if isinstance(replay, dict) else type(replay).__name__,
          aether_twin=aether_twin, profile=crystallizer.describe_profile())


def restore(world: str, cache_dir: str, checkpoint_id: str, mode: str) -> None:
    """Restore one recorded world in this fresh process and report outcome, regime and a follow-up bind."""
    from melder import Aether, Spellbook, SpellbookConfiguration
    from regime_services import TenantService

    _redirect_cache(cache_dir)
    if mode == "perframe_first":
        _per_frame_ids()
    crystallizer = _crystallizer_on()
    crystallizer.reload_cached_checkpoint(checkpoint_id)
    try:
        report = crystallizer.load_checkpoint(checkpoint_id)
    except Exception as error:
        chain = []
        cause = error
        while cause is not None and len(chain) < 4:
            chain.append(f"{type(cause).__name__}: {str(cause).splitlines()[0][:200]}")
            cause = cause.__cause__ or cause.__context__
        _emit(step="restore", world=world, mode=mode, outcome="raised", chain=chain,
              frames_after=sorted(Aether().list_frame_names()),
              regime_in_force=Aether()._process_wide_unique_spell_ids)
        return
    shortfalls = report.get("shortfalls")
    _emit(step="restore", world=world, mode=mode, outcome=report.get("status"), report_keys=sorted(report.keys()),
          built_counts=report.get("built_counts"),
          aether_shortfalls=[s for s in (shortfalls or []) if "aether" in json.dumps(s, default=str)],
          frames_after=sorted(Aether().list_frame_names()), configured=Aether().configured,
          regime_in_force=Aether()._process_wide_unique_spell_ids,
          reported_regime=Aether().configuration.process_wide_unique_spell_ids)
    # Follow-up: the multi-tenant move the recorded world allowed - bind the tenant class into tenant_b.
    try:
        book = Spellbook(aetheric_frame="tenant_b",
                         configuration=SpellbookConfiguration("tenant_b").with_defaults().finalize())
        book.bind(spell=TenantService, existence="many")
        followup = "accepted"
    except Exception as error:
        followup = f"refused: {type(error).__name__}: {str(error).splitlines()[0][:120]}"
    _emit(step="followup_bind_tenant_class_into_tenant_b", world=world, mode=mode, result=followup)
    # Second follow-up: does tenant_a still hold the tenant class? Binding it there is accepted only when tenant_a
    # came back without it and ids are per frame (under process-wide ids another frame's copy refuses it).
    try:
        book_a = Spellbook(aetheric_frame="tenant_a",
                           configuration=SpellbookConfiguration("tenant_a").with_defaults().finalize())
        book_a.bind(spell=TenantService, existence="many")
        followup_a = "accepted"
    except Exception as error:
        followup_a = f"refused: {type(error).__name__}: {str(error).splitlines()[0][:120]}"
    _emit(step="followup_bind_tenant_class_into_tenant_a", world=world, mode=mode, result=followup_a)


if __name__ == "__main__":
    try:
        if sys.argv[1] == "record":
            record(sys.argv[2], sys.argv[3])
        else:
            restore(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    except Exception:
        _emit(step="probe_error", trace=traceback.format_exc()[-1500:])
        raise
