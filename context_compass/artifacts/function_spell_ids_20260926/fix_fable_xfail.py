"""Drop the strict xfail on the contract-payload cross-process signature case (fable_0 asked for this)."""
import pathlib, sys
p = pathlib.Path(sys.argv[1]) / "tests/component/melder/spellbook/test_codegen_signature_determinism.py"
raw = p.read_bytes().decode("utf-8")
nl = "\r\n" if "\r\n" in raw else "\n"
old_param = '''        pytest.param(
            "probe_contract_payload_book_signatures",
            marks=pytest.mark.xfail(
                strict=True,
                reason=(
                    "the consumer's SPELL ID is still process-local: Bind.sha256_profile hashes "
                    "the constructor signature text, and the SpellContract default's repr carries "
                    "the PayloadMarker's address, so root_spell_id (and with it the executor "
                    "signature) differs per process. Remove this marker when melder_1's spell-id "
                    "stabilization lands (tickets/tasks/2026-09-26_stabilize_function_spell_ids_"
                    "across_processes_task.md); the codegen signature path itself is deterministic "
                    "(unit + corpus tests)."
                ),
            ),
        ),
'''
new_param = '''        # Formerly xfail(strict=True): the consumer's spell id was process-local because the
        # SpellContract default's repr carried the PayloadMarker's address into the hashed
        # constructor signature. The bind fingerprint hashes address-free text since 2026-09-26.
        "probe_contract_payload_book_signatures",
'''
old_doc = '''    is the proof that object payloads no longer make the signature process-local - once the
    bind-side spell id of such a consumer is stable too (see the xfail marker).
'''
new_doc = '''    is the proof that object payloads no longer make the signature, or the consumer's bind-side
    spell id, process-local.
'''
for o, n in ((old_param, new_param), (old_doc, new_doc)):
    o2, n2 = o.replace("\n", nl), n.replace("\n", nl)
    assert raw.count(o2) == 1, o[:60]
    raw = raw.replace(o2, n2)
p.write_bytes(raw.encode("utf-8")); print("ok", repr(nl))
