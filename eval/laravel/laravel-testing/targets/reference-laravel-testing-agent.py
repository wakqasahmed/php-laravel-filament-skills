#!/usr/bin/env python3
"""Deterministic reference target for the isolated laravel-testing outcome evaluation."""
import json
import sys
from pathlib import Path


CONVENTION_RULES = [
    {
        "keywords": ["Pest test using raw", "$this->assertTrue", "$this->assertEquals"],
        "negative_keywords": [],
        "decision": "apply_convention",
        "chosen_pattern": "use_pest_expect_syntax",
        "primary_reason": "prefer_pest_expect_assertions_for_readability",
    },
    {
        "keywords": ["outbound HTTP requests to api.openweathermap.org"],
        "negative_keywords": [],
        "decision": "apply_convention",
        "chosen_pattern": "use_http_fake",
        "primary_reason": "stub_outbound_http_calls_with_http_fake",
    },
    {
        "keywords": ["does not use any database cleanup trait", "lingering test records"],
        "negative_keywords": [],
        "decision": "apply_convention",
        "chosen_pattern": "use_refresh_database_trait",
        "primary_reason": "use_refresh_database_by_default_for_isolated_state",
    },
    {
        "keywords": ["creates 50 test users by executing database/seeders/DatabaseSeeder.php"],
        "negative_keywords": [],
        "decision": "apply_convention",
        "chosen_pattern": "use_model_factories",
        "primary_reason": "use_factories_for_per_test_fixtures_not_seeders",
    },
    {
        "keywords": ["triggers a real WelcomeEmailMailable via SMTP server"],
        "negative_keywords": [],
        "decision": "apply_convention",
        "chosen_pattern": "use_mail_fake",
        "primary_reason": "fake_mail_dispatch_and_assert_sent",
    },
    {
        "keywords": ["pure mathematical TaxCalculator class", "without booting Laravel's HTTP kernel"],
        "negative_keywords": [],
        "decision": "preserve_existing",
        "chosen_pattern": "keep_isolated_unit_tests",
        "primary_reason": "unit_tests_appropriate_for_pure_calculation_branching",
    },
    {
        "keywords": ["RolesAndPermissionsSeeder once in test setup to populate static system roles"],
        "negative_keywords": [],
        "decision": "preserve_existing",
        "chosen_pattern": "allow_reference_table_seeding",
        "primary_reason": "seeders_appropriate_for_static_lookup_and_permission_tables",
    },
    {
        "keywords": ["DB_DATABASE=app_production_snapshot"],
        "negative_keywords": [],
        "decision": "diagnose_fix",
        "chosen_pattern": "enforce_dedicated_test_database",
        "primary_reason": "test_database_must_clearly_contain_test_or_use_sqlite_memory",
    },
    {
        "keywords": ["live API requests to Stripe's sandbox server with test cards"],
        "negative_keywords": [],
        "decision": "diagnose_fix",
        "chosen_pattern": "mock_payment_gateway_client",
        "primary_reason": "never_let_unit_or_feature_tests_hit_live_network",
    },
    {
        "keywords": ["removes RefreshDatabase and replaces it with manual $user->delete()"],
        "negative_keywords": [],
        "decision": "diagnose_fix",
        "chosen_pattern": "use_refresh_database_or_transactions",
        "primary_reason": "never_rely_on_manual_cleanup_instead_of_transactions_or_refresh",
    },
    {
        "keywords": ["Test uploads PDF invoice to live S3 bucket"],
        "negative_keywords": [],
        "decision": "apply_convention",
        "chosen_pattern": "use_storage_fake",
        "primary_reason": "fake_storage_disks_in_tests",
    },
    {
        "keywords": ["Test asserts user registered event was dispatched"],
        "negative_keywords": [],
        "decision": "apply_convention",
        "chosen_pattern": "use_event_fake",
        "primary_reason": "fake_events_and_assert_dispatched",
    },
    {
        "keywords": ["Test duplicates same validation rule with 10 separate it() blocks"],
        "negative_keywords": [],
        "decision": "apply_convention",
        "chosen_pattern": "use_pest_datasets",
        "primary_reason": "use_datasets_for_multi_input_assertions",
    },
]


def outcome_for(prompt: str, enabled: bool) -> dict:
    if not enabled:
        return {
            "decision": "preserve_existing",
            "chosen_pattern": "unfaked_legacy_test",
            "primary_reason": "keep_default_test_hacks",
        }
    for rule in CONVENTION_RULES:
        if all(k in prompt for k in rule["keywords"]) and not any(k in prompt for k in rule["negative_keywords"]):
            return {
                "decision": rule["decision"],
                "chosen_pattern": rule["chosen_pattern"],
                "primary_reason": rule["primary_reason"],
            }
    return {
        "decision": "preserve_existing",
        "chosen_pattern": "unfaked_legacy_test",
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
