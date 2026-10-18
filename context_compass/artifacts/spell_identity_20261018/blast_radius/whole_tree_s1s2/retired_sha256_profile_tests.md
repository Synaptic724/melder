# Retired tests of `Bind.sha256_profile` - test_bind.py (melder_0, 2026-10-18)

S1 removes `Bind.sha256_profile` (the spell_id is `SpellCodeDigest`'s, the bind call is the binding manifest), so
the 44 test functions of test_bind.py that call it (47 cases with the parametrized resolvable check) test a function
that no longer exists. Each was read; each is retired onto the successor that now carries its property, converted,
or rewritten. Successor files: `tests/unit/melder/spellbook/bind/test_spell_code_digest.py` (DIGEST),
`test_spell_code_digest_libraries.py` (LIBRARIES), `test_binding_manifest.py` (MANIFEST), and the component test
`tests/component/melder/spellbook/test_spellbook_component_spell_identity.py` (COMPONENT).

## Converted or rewritten (stay in test_bind.py)

| old test | now |
| --- | --- |
| test_sha256_resolvable_rejects_non_bool_policy[None, 0, 1, "false"] | test_bind_refuses_a_non_bool_resolvable_before_reflecting_the_target - the same four values through public `Bind.bind`: TypeError "resolvable must be a bool", the examiner never called |
| test_spell_id_inspector_uses_examiner | test_spell_id_inspector_is_the_code_digest - equals `SpellCodeDigest().spell_id`, stable across calls, builds no binding profile |

## Retired onto successors

| old test (what it pinned) | successor |
| --- | --- |
| test_sha256_profile_deterministic_class (method-name order) | DIGEST SAME methods_defined_in_another_order (added) |
| test_class_method_names_order_stable_hash | DIGEST SAME methods_defined_in_another_order (added) |
| test_sha256_class_reordering_stable (bases, MRO, annotations, methods reordered) | DIGEST SAME methods_defined_in_another_order (added); bases are code now (CHANGES a_base_class_method_body) |
| test_sha256_class_annotations_order_irrelevant | DIGEST SAME the_same_source_executed_twice; the digest sorts its lines |
| test_sha256_profile_different_profiles_yield_different_hashes (class vs callable) | DIGEST TestContract test_each_kind_of_target_has_its_encoding |
| test_sha256_profile_includes_parameters | DIGEST CHANGES a_parameter_added_to_a_method |
| test_sha256_parameters_kind_affects_hash | DIGEST CHANGES a_parameter_kind (added) |
| test_sha_changes_with_empty_vs_varargs_only | DIGEST CHANGES a_parameter_kind (added) |
| test_sha256_callable_signature_changes_hash | DIGEST CHANGES a_parameter_added_to_a_method |
| test_sha256_callable_param_default_changes_hash | DIGEST test_two_lambdas_differing_only_by_a_default_are_two_spells |
| test_callable_param_default_repr_changes_hash | DIGEST test_two_lambdas_differing_only_by_a_default_are_two_spells |
| test_callable_parameters_default_repr_affects_hash | DIGEST test_two_lambdas_differing_only_by_a_default_are_two_spells |
| test_sha_changes_with_parameter_annotation (annotation ignored) | reversed by the owner's design: DIGEST CHANGES a_parameter_annotation |
| test_sha256_annotation_content_changes_hash (annotation values ignored) | reversed: DIGEST CHANGES a_field_annotation |
| test_class_annotations_keys_change_hash | DIGEST CHANGES a_field_annotation |
| test_sha256_class_init_signature_changes_hash | DIGEST CHANGES a_constructor_default, a_parameter_added_to_a_method |
| test_sha256_class_source_preview_no_longer_affects_hash | DIGEST SAME docstrings_comments_and_blank_lines, a_reworded_docstring |
| test_sha_changes_with_mro_diff | DIGEST CHANGES a_base_class_method_body |
| test_sha_changes_with_bases_diff | DIGEST CHANGES a_base_class_method_body |
| test_sha_changes_with_method_names_diff | DIGEST CHANGES a_renamed_method |
| test_sha_changes_with_dataclass_flag (flag ignored) | DIGEST CHANGES a_dataclass_default; LIBRARIES test_a_dataclass_default_factory_change_moves_the_spell_id |
| test_sha_changes_with_decorated_flag (flag ignored) | DIGEST test_a_decorator_argument_change_moves_the_spell_id; LIBRARIES test_a_decorator_and_the_function_it_wraps_both_count |
| test_sha_changes_with_origin_file (origin ignored) | DIGEST SAME blank_lines_moving_every_line; test_the_same_code_in_another_module_is_another_spell |
| test_sha256_callable_repr_changes_hash | DIGEST test_two_lambdas_with_different_bodies_are_two_spells (a function is its code, not its repr) |
| test_callable_repr_and_lambda_flag_combo_changes_hash | DIGEST test_two_lambdas_with_different_bodies_are_two_spells |
| test_sha256_callable_lambda_flag_changes_hash | DIGEST test_each_kind_of_target_has_its_encoding (the qualname is in a function's encoding) |
| test_callable_lambda_flag_affects_hash_even_with_same_signature | DIGEST test_each_kind_of_target_has_its_encoding |
| test_callable_qualname_vs_name_changes_hash | DIGEST test_each_kind_of_target_has_its_encoding; test_two_empty_subclasses_under_different_names_are_two_spells |
| test_sha256_callable_builtin_flag_changes_hash | LIBRARIES test_an_installed_function_is_named_by_its_distribution_version; test_an_object_without_python_visible_state_keeps_the_repr_rule |
| test_callable_builtin_flag_changes_hash | LIBRARIES (as above) |
| test_callable_extension_flag_changes_hash | LIBRARIES (as above) |
| test_sha_changes_with_extension_and_builtin_flags | LIBRARIES (as above) |
| test_sha256_callable_flags_change_hash | LIBRARIES (as above); DIGEST test_each_kind_of_target_has_its_encoding |
| test_sha256_instance_repr_changes_hash | DIGEST test_objects_with_different_data_are_two_spells; LIBRARIES test_objects_of_an_installed_class_are_their_type_version_and_repr |
| test_instance_profile_module_changes_hash | DIGEST test_the_same_code_in_another_module_is_another_spell |
| test_other_profile_module_changes_hash | DIGEST test_the_same_code_in_another_module_is_another_spell |
| test_sha256_instance_vs_other_profiles (two profile kinds hash alike) | none needed: the profile kinds are gone; an object is its class code and its data (DIGEST TestExistingObjects) |
| test_sha256_fallback_profile_has_hash_length | DIGEST test_the_spell_id_is_the_sha256_of_the_tag_the_cache_tag_and_the_encoding (64 hex); test_standard_library_objects_are_their_type_and_repr |
| test_sha256_handles_unicode_identifiers | DIGEST TestContract test_unicode_identifiers_digest_stably (added) |
| test_sha256_long_strings_stable_length | DIGEST test_the_spell_id_is_the_sha256_of_the_tag_the_cache_tag_and_the_encoding; test_an_integer_constant_too_long_for_decimal_text_digests_in_hex |
| test_sha256_resolvable_preserves_the_fixed_legacy_fingerprint (the pre-capability v4 pin) | retired by design: every spell_id moves once (S5); resolvable is a binding field - MANIFEST test_every_field_moves_the_binding_hash[resolvable] |
| test_sha256_non_resolvable_keeps_existing_shape_version_rules | MANIFEST test_every_field_moves_the_binding_hash[resolvable]; the code rules hold whatever the binding (DIGEST) |
| test_sha256_profile_changes_with_binding_signature_existence_and_disposal | MANIFEST test_every_field_moves_the_binding_hash[frame_key, binding_key, spellframe, binding_name, existence, disposal_method_names]; COMPONENT: another binding of one class, the same spell_id and another binding hash |

Section comments left without tests are kept and say where their tests went.
