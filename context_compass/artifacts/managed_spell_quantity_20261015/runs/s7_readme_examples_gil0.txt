ninth lease refused: [MELD] Execution failed for spell 'ChannelLogger' (0c1bae692a3db85ead9edbbe783783680b557c2cbc64d6921e3bc0b2a82ef62d): Managed spell 'ChannelLogger' (limited_quantity, limit 8) has all 8 objects out. Release one with ReleaseManagedSpell().release(obj) before melding another, or bind it with a higher managed_spell_limit.
describe: {'mode': 'limited_quantity', 'limit': 8, 'count': 8}
managed example: OK (built 8 closed 3 of the 3 idle; 5 out untouched)
raised: ExceptionGroup 'Conduit torn down with disposal failures.' leaves: [('RuntimeError', 'OSError')]
disposal sentence: OK (close raised, shutdown still ran; worker torn down before its connection)
