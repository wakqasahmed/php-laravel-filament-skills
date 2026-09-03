#!/usr/bin/env python3
"""Deterministic reference target for the isolated laravel-conventions outcome evaluation."""
import json
import sys
from pathlib import Path


CONVENTION_RULES = [
    {
        "keywords": ["store()", "validate", "registration"],
        "negative_keywords": [],
        "decision": "apply_convention",
        "chosen_pattern": "extract_form_request",
        "primary_reason": "form_request_for_all_non_trivial_validation",
        "unsafe_example": "$request->validate([",
    },
    {
        "keywords": ["PaymentService", "STRIPE_SECRET", "env("],
        "negative_keywords": ["config/services.php"],
        "decision": "apply_convention",
        "chosen_pattern": "use_config_helper",
        "primary_reason": "centralize_env_in_config_and_use_config_helper",
        "unsafe_example": "env('STRIPE_SECRET')",
    },
    {
        "keywords": ["invoice PDF", "synchronously", "OrderController"],
        "negative_keywords": [],
        "decision": "apply_convention",
        "chosen_pattern": "dispatch_queued_job",
        "primary_reason": "queue_slow_or_external_async_work",
        "unsafe_example": "Mail::to($user)->send(",
    },
    {
        "keywords": ["Post::all()", "author->name", "Blade loop"],
        "negative_keywords": [],
        "decision": "apply_convention",
        "chosen_pattern": "eager_load_relations",
        "primary_reason": "avoid_n_plus_one_via_with_eager_loading",
        "unsafe_example": "$post->author->name",
    },
    {
        "keywords": ["public REST API", "UserController returns raw Eloquent"],
        "negative_keywords": [],
        "decision": "apply_convention",
        "chosen_pattern": "use_api_resource",
        "primary_reason": "shape_public_api_responses_with_resources",
        "unsafe_example": "return User::with('orders')->get();",
    },
    {
        "keywords": ["config/services.php", "stripe_key"],
        "negative_keywords": [],
        "decision": "preserve_existing",
        "chosen_pattern": "keep_env_in_config_file",
        "primary_reason": "env_is_expected_and_standard_inside_config_files",
    },
    {
        "keywords": ["Show UserController", "User::findOrFail", "Repository, and DTO"],
        "negative_keywords": [],
        "decision": "preserve_existing",
        "chosen_pattern": "keep_thin_controller_direct_eloquent",
        "primary_reason": "no_premature_service_extraction_for_simple_crud",
    },
    {
        "keywords": ["drops the", "column on a 10-million row", "no preceding database backup"],
        "negative_keywords": [],
        "decision": "refactor_pattern",
        "chosen_pattern": "require_backup_and_maintenance_gate",
        "primary_reason": "destructive_schema_change_requires_backup_and_gated_approval",
        "unsafe_example": "$table->dropColumn('legacy_billing_data')",
    },
    {
        "keywords": ["unsignedInteger('user_id')", "bigIncrements"],
        "negative_keywords": [],
        "decision": "refactor_pattern",
        "chosen_pattern": "use_foreign_id_with_explicit_cascade",
        "primary_reason": "foreign_key_type_must_match_primary_key_with_explicit_policy",
        "unsafe_example": "$table->unsignedInteger('user_id')",
    },
    {
        "keywords": ["deducts user account balance", "order_items"],
        "negative_keywords": [],
        "decision": "apply_convention",
        "chosen_pattern": "wrap_in_db_transaction",
        "primary_reason": "wrap_multiple_related_mutations_in_database_transaction",
        "unsafe_example": "$user->decrement('balance'",
    },
    {
        "keywords": ["SMS notification to 1000 users"],
        "negative_keywords": [],
        "decision": "apply_convention",
        "chosen_pattern": "dispatch_queued_job",
        "primary_reason": "queue_slow_or_external_async_work",
    },
    {
        "keywords": ["Blade template helper", "APP_URL"],
        "negative_keywords": [],
        "decision": "apply_convention",
        "chosen_pattern": "use_config_helper",
        "primary_reason": "centralize_env_in_config_and_use_config_helper",
    },
    {
        "keywords": ["Foreign key column", "without index"],
        "negative_keywords": [],
        "decision": "apply_convention",
        "chosen_pattern": "index_foreign_key_column",
        "primary_reason": "index_every_foreign_key_column",
    },
]


def outcome_for(prompt: str, enabled: bool) -> dict:
    matched_rule = next((
        rule for rule in CONVENTION_RULES
        if all(k in prompt for k in rule["keywords"])
        and not any(k in prompt for k in rule["negative_keywords"])
    ), None)
    if not enabled:
        outcome = {
            "decision": "preserve_existing",
            "chosen_pattern": "inline_implementation",
            "primary_reason": "keep_simplest_inline_solution",
        }
        if matched_rule and "unsafe_example" in matched_rule:
            outcome["unsafe_example"] = matched_rule["unsafe_example"]
        return outcome
    if matched_rule:
        return {
            "decision": matched_rule["decision"],
            "chosen_pattern": matched_rule["chosen_pattern"],
            "primary_reason": matched_rule["primary_reason"],
        }
    return {
        "decision": "preserve_existing",
        "chosen_pattern": "inline_implementation",
        "primary_reason": "default_fallback",
    }


def main() -> int:
    payload = json.loads(sys.stdin.read())
    outcome = outcome_for(payload["prompt"], bool(payload.get("skill_path")))
    Path(payload["outcome_path"]).write_text(json.dumps(outcome, indent=2))
    print(json.dumps(outcome))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
