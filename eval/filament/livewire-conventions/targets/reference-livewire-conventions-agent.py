#!/usr/bin/env python3
"""Deterministic reference target for the isolated livewire-conventions outcome evaluation."""
import json
import sys
from pathlib import Path


CONVENTION_RULES = [
    {
        "keywords": ["heavy full-text DB searches on every keystroke", "wire:model.live"],
        "negative_keywords": [],
        "decision": "diagnose_fix",
        "chosen_pattern": "add_debounce_modifier",
        "primary_reason": "debounce_live_search_input_to_collapse_rapid_requests",
    },
    {
        "keywords": ["$selectedTab", "local variable inside mount()"],
        "negative_keywords": [],
        "decision": "diagnose_fix",
        "chosen_pattern": "declare_public_property",
        "primary_reason": "state_must_be_public_property_to_survive_rehydration",
    },
    {
        "keywords": ["repeater", "index-based wire:key"],
        "negative_keywords": [],
        "decision": "diagnose_fix",
        "chosen_pattern": "use_model_id_for_wire_key",
        "primary_reason": "key_dynamic_loops_on_stable_primary_key_not_index",
    },
    {
        "keywords": ["10 text fields with wire:model.live", "validation only happens on submit"],
        "negative_keywords": [],
        "decision": "apply_convention",
        "chosen_pattern": "use_deferred_wire_model",
        "primary_reason": "defer_form_input_binding_until_action_or_submit",
    },
    {
        "keywords": ["raw script and stylesheet link tags manually", "Blade view"],
        "negative_keywords": [],
        "decision": "apply_convention",
        "chosen_pattern": "register_via_filament_asset",
        "primary_reason": "register_panel_assets_via_filament_asset_manager",
    },
    {
        "keywords": ["manual pagination, sorting, and search queries from scratch", "standard Table schema"],
        "negative_keywords": [],
        "decision": "preserve_existing",
        "chosen_pattern": "stay_in_declarative_filament_table",
        "primary_reason": "use_filament_declarative_schema_when_features_already_supported",
    },
    {
        "keywords": ["canvas or chart painter", "no Filament component equivalent"],
        "negative_keywords": [],
        "decision": "preserve_existing",
        "chosen_pattern": "use_custom_livewire_component",
        "primary_reason": "custom_livewire_component_warranted_for_canvas_ui",
    },
    {
        "keywords": ["deleteUserRecord action method", "without calling Gate::authorize()"],
        "negative_keywords": [],
        "decision": "diagnose_fix",
        "chosen_pattern": "authorize_action_explicitly",
        "primary_reason": "guard_sensitive_livewire_methods_explicitly_with_gate",
    },
    {
        "keywords": ["passes orderId to a child Livewire modal component in mount()"],
        "negative_keywords": [],
        "decision": "diagnose_fix",
        "chosen_pattern": "rekey_child_on_record_id",
        "primary_reason": "changing_wire_key_forces_clean_component_remount",
    },
    {
        "keywords": ["getFormSchema()", "raw Livewire properties rather than InteractsWithForms"],
        "negative_keywords": [],
        "decision": "diagnose_fix",
        "chosen_pattern": "implement_interacts_with_forms",
        "primary_reason": "use_filament_form_conventions_instead_of_raw_binding_mix",
    },
    {
        "keywords": ["validation feedback when user leaves email input", "without keystroke latency"],
        "negative_keywords": [],
        "decision": "apply_convention",
        "chosen_pattern": "use_wire_model_blur",
        "primary_reason": "sync_on_blur_for_validation_without_per_keystroke_request",
    },
    {
        "keywords": ["Developer expects mount() to execute on every Livewire button click"],
        "negative_keywords": [],
        "decision": "diagnose_fix",
        "chosen_pattern": "use_action_or_hydrate_hook",
        "primary_reason": "mount_runs_only_once_on_initial_render",
    },
    {
        "keywords": ["Repeater block items flicker and lose focus on add row without stable key"],
        "negative_keywords": [],
        "decision": "diagnose_fix",
        "chosen_pattern": "use_model_id_for_wire_key",
        "primary_reason": "key_dynamic_loops_on_stable_primary_key_not_index",
    },
]


def outcome_for(prompt: str, enabled: bool) -> dict:
    if not enabled:
        return {
            "decision": "preserve_existing",
            "chosen_pattern": "inline_component_logic",
            "primary_reason": "keep_raw_livewire_defaults",
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
        "chosen_pattern": "inline_component_logic",
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
