#!/usr/bin/env python3
"""Deterministic reference target for the isolated laravel-security outcome evaluation."""
import json
import sys
from pathlib import Path


CONVENTION_RULES = [
    {
        "keywords": ["$user->update($request->all())", "is_admin"],
        "negative_keywords": [],
        "decision": "enforce_security",
        "chosen_pattern": "pass_validated_request_data",
        "primary_reason": "pass_request_validated_or_explicit_array_to_prevent_mass_assignment",
        "unsafe_pattern": "$user->update($request->all())",
    },
    {
        "keywords": ["whereRaw(\"title LIKE '%\" . $request->search"],
        "negative_keywords": [],
        "decision": "enforce_security",
        "chosen_pattern": "use_parameterized_query_bindings",
        "primary_reason": "pass_user_values_as_bindings_in_where_raw",
        "unsafe_pattern": "DB::table('products')->whereRaw(\"title LIKE '%\" . $request->search . \"%'\")",
    },
    {
        "keywords": ["renders user submitted bio comments using {!! $comment->body !!"],
        "negative_keywords": [],
        "decision": "enforce_security",
        "chosen_pattern": "use_blade_html_escaping",
        "primary_reason": "use_double_curly_escaping_or_purify_html_before_render",
        "unsafe_pattern": "{!! $comment->body !!}",
    },
    {
        "keywords": ["->orderByRaw($request->sort_col . ' ' . $request->sort_dir)"],
        "negative_keywords": [],
        "decision": "enforce_security",
        "chosen_pattern": "allowlist_dynamic_sort_identifiers",
        "primary_reason": "allowlist_column_and_direction_identifiers_against_permitted_set",
        "unsafe_pattern": "orderByRaw($request->sort_col . ' ' . $request->sort_dir)",
    },
    {
        "keywords": ["Invoice $invoice", "$this->authorize('update', $invoice)", "IDOR"],
        "negative_keywords": [],
        "decision": "enforce_security",
        "chosen_pattern": "enforce_explicit_policy_authorization",
        "primary_reason": "explicitly_authorize_model_ownership_via_policy_check",
        "unsafe_pattern": "route model binding authorizes access automatically",
    },
    {
        "keywords": ["marketing footer view renders hardcoded system legal copyright", "{!! $sanitizedLegalHtml !!"],
        "negative_keywords": [],
        "decision": "preserve_existing",
        "chosen_pattern": "allow_purified_trusted_raw_rendering",
        "primary_reason": "raw_echo_acceptable_for_server_purified_trusted_content",
    },
    {
        "keywords": ["protected $fillable = ['title', 'description', 'price']", "passes $request->validated()"],
        "negative_keywords": [],
        "decision": "preserve_existing",
        "chosen_pattern": "keep_fillable_allowlist",
        "primary_reason": "fillable_allowlist_with_validated_request_is_sufficient",
    },
    {
        "keywords": ["protected $guarded = [] on the User model", "passes $request->all()"],
        "negative_keywords": [],
        "decision": "refactor_vulnerability",
        "chosen_pattern": "replace_guarded_with_fillable_allowlist",
        "primary_reason": "guarded_empty_disables_protection_replace_with_fillable",
        "unsafe_pattern": "protected $guarded = []",
    },
    {
        "keywords": ["VerifyCsrfToken $except array", "without verifying the provider's HMAC signature"],
        "negative_keywords": [],
        "decision": "refactor_vulnerability",
        "chosen_pattern": "enforce_webhook_signature_verification",
        "primary_reason": "csrf_excluded_webhooks_must_verify_cryptographic_signatures",
        "unsafe_pattern": "fulfill the order without verifying the HMAC signature",
    },
    {
        "keywords": ["$user->forceFill($request->only('role', 'is_admin'))"],
        "negative_keywords": [],
        "decision": "refactor_vulnerability",
        "chosen_pattern": "restrict_forcefill_to_internal_values",
        "primary_reason": "forcefill_must_never_accept_values_derived_from_request_input",
        "unsafe_pattern": "$user->forceFill($request->only('role', 'is_admin'))->save()",
    },
    {
        "keywords": ["Implement an update endpoint for a tenant invoice", "choosing any plausible access rule"],
        "negative_keywords": [],
        "decision": "hold_for_clarification",
        "chosen_pattern": "request_authorization_requirements",
        "primary_reason": "authorization_rule_missing_do_not_guess_access_policy",
        "unsafe_pattern": "return $user !== null;",
    },
    {
        "keywords": ["FormRequest authorize() returns true without checking route model"],
        "negative_keywords": [],
        "decision": "enforce_security",
        "chosen_pattern": "authorize_route_model_in_form_request",
        "primary_reason": "authorize_route_model_explicitly_inside_form_request",
    },
    {
        "keywords": ["Filament resource uses inline ->visible(fn() => ...) instead of model policy"],
        "negative_keywords": [],
        "decision": "enforce_security",
        "chosen_pattern": "register_model_policy_for_filament",
        "primary_reason": "prefer_model_policies_over_inline_filament_visibility_closures",
    },
    {
        "keywords": ["Blade outputs user string directly inside inline script tag"],
        "negative_keywords": [],
        "decision": "enforce_security",
        "chosen_pattern": "use_js_json_encode_context_escaping",
        "primary_reason": "use_json_encode_or_js_directive_for_script_context_escaping",
    },
]


def outcome_for(prompt: str, enabled: bool) -> dict:
    for rule in CONVENTION_RULES:
        if all(k in prompt for k in rule["keywords"]) and not any(k in prompt for k in rule["negative_keywords"]):
            if not enabled:
                return {
                    "decision": "preserve_existing",
                    "chosen_pattern": rule.get("unsafe_pattern", "unvalidated_input_pattern"),
                    "primary_reason": "keep_naive_implementation",
                }
            return {
                "decision": rule["decision"],
                "chosen_pattern": rule["chosen_pattern"],
                "primary_reason": rule["primary_reason"],
            }
    return {
        "decision": "preserve_existing",
        "chosen_pattern": "unvalidated_input_pattern",
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
