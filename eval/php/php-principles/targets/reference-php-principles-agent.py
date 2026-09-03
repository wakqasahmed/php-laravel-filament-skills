#!/usr/bin/env python3
"""Deterministic reference target for the isolated php-principles outcome evaluation."""
import json
import sys
from pathlib import Path


CONVENTION_RULES = [
    {
        "keywords": ["UserManager", "password hashing", "CSV", "cURL"],
        "negative_keywords": [],
        "decision": "refactor_smell",
        "chosen_pattern": "split_by_single_responsibility",
        "primary_reason": "split_manager_class_doing_unrelated_tasks",
        "unsafe_alternative": "keep class UserManager and call curl_exec( directly",
    },
    {
        "keywords": ["NotificationSender", "match($type)"],
        "negative_keywords": [],
        "decision": "refactor_smell",
        "chosen_pattern": "extract_interface_and_polymorphic_handlers",
        "primary_reason": "replace_growing_type_match_with_polymorphic_implementations",
        "unsafe_alternative": "keep match($type), for example match ($type) { with another arm",
    },
    {
        "keywords": ["OrderPricingEngine", "new StripeApiClient()"],
        "negative_keywords": [],
        "decision": "refactor_smell",
        "chosen_pattern": "inject_dependencies_via_constructor",
        "primary_reason": "inject_collaborator_dependencies_rather_than_calling_new",
        "unsafe_alternative": "continue using new StripeApiClient() and new CurrencyConverter()",
    },
    {
        "keywords": ["Order entity uses untyped string constants", "draft"],
        "negative_keywords": [],
        "decision": "apply_principle",
        "chosen_pattern": "use_backed_enum_for_domain_states",
        "primary_reason": "use_enums_for_finite_domain_states_with_native_typing",
        "unsafe_alternative": "keep public const STATUS_DRAFT = 'draft' and compare $status === 'paid'",
    },
    {
        "keywords": ["DocumentHandler", "SimplePdfRenderer", "UnsupportedOperationException"],
        "negative_keywords": [],
        "decision": "refactor_smell",
        "chosen_pattern": "split_into_role_specific_interfaces",
        "primary_reason": "split_fat_interface_forcing_empty_or_throwing_methods",
        "unsafe_alternative": "keep implements DocumentHandler and throw new UnsupportedOperationException",
    },
    {
        "keywords": ["Two independent domain classes in Billing and Support", "abstract BaseEntity"],
        "negative_keywords": [],
        "decision": "preserve_existing",
        "chosen_pattern": "avoid_premature_dry_extraction",
        "primary_reason": "do_not_dry_prematurely_when_reasons_to_change_differ",
    },
    {
        "keywords": ["UserRegistrationService", "register", "micro-classes"],
        "negative_keywords": [],
        "decision": "preserve_existing",
        "chosen_pattern": "keep_focused_single_responsibility_service",
        "primary_reason": "service_is_focused_on_single_responsibility_with_injected_dependencies",
    },
    {
        "keywords": ["composer.json using wildcard", "vendor/payment-lib"],
        "negative_keywords": [],
        "decision": "refactor_smell",
        "chosen_pattern": "pin_semver_constraint_and_audit",
        "primary_reason": "avoid_wildcard_dependencies_and_run_composer_audit",
        "unsafe_alternative": "run composer require vendor/payment-lib:* and composer update --no-audit",
    },
    {
        "keywords": ["ReadOnlyRepository extends WritableDatabaseRepository", "BadMethodCallException"],
        "negative_keywords": [],
        "decision": "refactor_smell",
        "chosen_pattern": "favor_composition_over_broken_inheritance",
        "primary_reason": "hierarchy_is_wrong_when_subclass_throws_on_inherited_methods",
        "unsafe_alternative": "keep extends WritableDatabaseRepository and throw new BadMethodCallException",
    },
    {
        "keywords": ["calculates tax by reading global $_SESSION", "HelperClass::getGlobalExchangeRate()"],
        "negative_keywords": [],
        "decision": "refactor_smell",
        "chosen_pattern": "eliminate_global_state_and_inject_parameters",
        "primary_reason": "avoid_global_state_and_static_helpers_in_domain_logic",
        "unsafe_alternative": "read global $_SESSION and call HelperClass::getGlobalExchangeRate()",
    },
    {
        "keywords": ["repeats 5 constructor parameters and assigns 5 properties manually"],
        "negative_keywords": [],
        "decision": "apply_principle",
        "chosen_pattern": "use_constructor_property_promotion",
        "primary_reason": "use_constructor_promotion_for_clear_dependencies",
    },
    {
        "keywords": ["Single-line if statement without braces"],
        "negative_keywords": [],
        "decision": "apply_principle",
        "chosen_pattern": "use_braces_for_control_blocks",
        "primary_reason": "use_braces_for_every_control_flow_block",
    },
    {
        "keywords": ["Method returns untyped array of Order objects"],
        "negative_keywords": [],
        "decision": "apply_principle",
        "chosen_pattern": "document_array_shape_with_phpdoc",
        "primary_reason": "document_generic_collections_with_phpdoc",
    },
]


def outcome_for(prompt: str, enabled: bool) -> dict:
    for rule in CONVENTION_RULES:
        if all(k in prompt for k in rule["keywords"]) and not any(k in prompt for k in rule["negative_keywords"]):
            if not enabled:
                return {
                    "decision": "preserve_existing",
                    "chosen_pattern": "monolithic_implementation",
                    "primary_reason": rule.get("unsafe_alternative", "keep_naive_code"),
                }
            return {
                "decision": rule["decision"],
                "chosen_pattern": rule["chosen_pattern"],
                "primary_reason": rule["primary_reason"],
            }
    return {
        "decision": "preserve_existing",
        "chosen_pattern": "monolithic_implementation",
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
