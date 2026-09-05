#!/usr/bin/env python3
"""Deterministic reference target for the isolated filament-conventions outcome evaluation."""
import json
import sys
from pathlib import Path


CONVENTION_RULES = [
    {
        "keywords": ["author.name", "category.title", "50+ database queries"],
        "negative_keywords": [],
        "decision": "apply_convention",
        "chosen_pattern": "eager_load_relationships_via_modify_query",
        "primary_reason": "Prevent N+1 queries on relationship columns by eager loading author and category in getEloquentQuery or modifyQueryUsing",
        "unsafe_reason": "->getStateUsing(fn ($record) => $record->author()->first()->name)",
    },
    {
        "keywords": ["OrderResource", "order items table", "custom inline HTML table"],
        "negative_keywords": [],
        "decision": "refactor_pattern",
        "chosen_pattern": "use_relation_manager_for_related_records",
        "primary_reason": "Use relation managers for related data rather than custom inline tables",
        "unsafe_reason": "->html()->formatStateUsing(fn ($record) => '<table>'",
    },
    {
        "keywords": ["UserResource", "->visible(fn () => auth()->user()->is_admin)"],
        "negative_keywords": [],
        "decision": "refactor_pattern",
        "chosen_pattern": "model_authorization_policies",
        "primary_reason": "Prefer model authorization policies over scattered inline gate checks",
        "unsafe_reason": "->visible(fn () => auth()->user()->is_admin)",
    },
    {
        "keywords": ["downloadInvoice", "120-line inline closure"],
        "negative_keywords": [],
        "decision": "refactor_pattern",
        "chosen_pattern": "custom_action_class",
        "primary_reason": "Implement custom actions as dedicated action classes rather than monolithic inline closures",
        "unsafe_reason": "->action(function ($record) {",
    },
    {
        "keywords": ["multi-tenant", "session('active_team_id')"],
        "negative_keywords": [],
        "decision": "refactor_pattern",
        "chosen_pattern": "centralized_tenant_scope_in_panel_provider",
        "primary_reason": "Centralize tenant scope in the panel provider or tenant middleware rather than scattering checks across resources",
        "unsafe_reason": "->where('team_id', session('active_team_id'))",
    },
    {
        "keywords": ["public marketing pricing calculator", "standalone Livewire component", "outside any Filament panel"],
        "negative_keywords": [],
        "decision": "preserve_existing",
        "chosen_pattern": "standard_standalone_livewire_component",
        "primary_reason": "Filament resource conventions apply to admin panel resources, not standalone public Livewire components",
        "unsafe_reason": "class PricingCalculatorResource extends Resource",
    },
    {
        "keywords": ["ProductResource already uses built-in", "rewriting the columns into raw Blade views"],
        "negative_keywords": [],
        "decision": "preserve_existing",
        "chosen_pattern": "declarative_built_in_table_components",
        "primary_reason": "Built-in columns and filters already follow conventions and should be preferred over custom Blade replacements",
        "unsafe_reason": "ViewColumn::make('name')->view('filament.tables.columns.raw-product')",
    },
    {
        "keywords": ["JSON endpoint for mobile devices", "Filament Resource Page"],
        "negative_keywords": [],
        "decision": "preserve_existing",
        "chosen_pattern": "laravel_api_resource_controller",
        "primary_reason": "Use standard Laravel API Resources and controllers for mobile API endpoints, not Filament panel resources",
        "unsafe_reason": "class NotificationsApi extends Page",
    },
    {
        "keywords": ["upgraded our project to Filament v4", "Filament\\Forms\\Form"],
        "negative_keywords": [],
        "decision": "refactor_pattern",
        "chosen_pattern": "unify_schemas_under_filament_v4_api",
        "primary_reason": "Filament v4 unifies forms and infolists under Filament\\Schemas\\Schema; do not mix deprecated v3 classes",
        "unsafe_reason": "public static function form(Form $form): Form",
    },
    {
        "keywords": ["bypass Filament schema fields", "rendering raw unescaped HTML strings", "ViewField"],
        "negative_keywords": [],
        "decision": "refactor_pattern",
        "chosen_pattern": "declarative_schema_field_components",
        "primary_reason": "Build forms with declarative schema components and validated field types, not raw unescaped HTML",
        "unsafe_reason": "{!! $comment->body !!}",
    },
    {
        "keywords": ["Livewire-backed booking form", "end_date is after start_date", "component's actual form state"],
        "negative_keywords": [],
        "decision": "refactor_pattern",
        "chosen_pattern": "component_form_state_cross_field_validation",
        "primary_reason": "Define cross-field rules in the Filament schema, Livewire component rules, or a Livewire form object and validate the state returned by $this->form->getState()",
        "unsafe_reason": "use a Form Request",
    },
    # Tuning cases
    {
        "keywords": ["dashboard widget", "un-cached count query across 500,000 transaction rows"],
        "negative_keywords": [],
        "decision": "apply_convention",
        "chosen_pattern": "cache_expensive_widget_data",
        "primary_reason": "Keep widgets single-purpose and cache expensive aggregation data",
    },
    {
        "keywords": ["repeat the same 6 address fields", "CustomerResource, SupplierResource"],
        "negative_keywords": [],
        "decision": "refactor_pattern",
        "chosen_pattern": "extract_reusable_form_field_group",
        "primary_reason": "Extract reusable field groups into custom components or reusable schema methods",
    },
    {
        "keywords": ["php artisan orders:prune-expired", "nightly cron"],
        "negative_keywords": [],
        "decision": "preserve_existing",
        "chosen_pattern": "standard_artisan_command",
        "primary_reason": "CLI commands run independently of Filament panel resources and use standard Laravel command conventions",
    },
    {
        "keywords": ["bulk delete action", "without a confirmation modal or policy gate"],
        "negative_keywords": [],
        "decision": "refactor_pattern",
        "chosen_pattern": "action_modal_confirmation_with_policy",
        "primary_reason": "Use action modals for confirmations and enforce authorization policies before destructive bulk operations",
    },
]


def outcome_for(prompt: str, enabled: bool) -> dict:
    for rule in CONVENTION_RULES:
        if all(k in prompt for k in rule["keywords"]) and not any(k in prompt for k in rule["negative_keywords"]):
            if not enabled:
                return {
                    "decision": "preserve_existing",
                    "chosen_pattern": "inline_implementation",
                    "primary_reason": rule.get("unsafe_reason", "keep_simplest_inline_solution"),
                }
            return {
                "decision": rule["decision"],
                "chosen_pattern": rule["chosen_pattern"],
                "primary_reason": rule["primary_reason"],
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
