---
name: filament-plugin-first
description: Before building custom Filament components, search the plugin ecosystem and triage reuse vs. build. Use when implementing non-trivial Filament form fields, table columns/actions, dashboard widgets, import/export, settings pages, multi-tenancy, or notifications.
---

# Filament Plugin First

Use this when implementing non-trivial Filament functionality in a Laravel project.

## Stop-and-Search Triggers

Before writing custom code for these areas, search the ecosystem:

- Form fields, inputs, and form layouts
- Table columns, filters, bulk actions, and row actions
- Dashboard widgets, chart components, and KPI cards
- Import/export (CSV, Excel, PDF)
- Settings / configuration pages
- Multi-tenancy helpers
- Notifications, action modals, and wizards
- Authentication / authorization UI
- Spatie package integrations (roles, media, tags, activity log)

## Search Order

1. Filament official plugins: `filamentphp.com/plugins`
2. Awesome Filament list: `github.com/spekulatius/awesome-filament`
3. Packagist: `packagist.org` search `filamentphp`
4. GitHub code search for `filamentphp` + feature keyword

## Triage

For each candidate, verify:

- Filament major version compatibility (v3 vs v4)
- Maintenance signal (last release, issue/PR activity, response time)
- License compatibility with the project
- Required PHP / Laravel versions match the project

Then choose:

1. **Install directly** if compatible, maintained, and license matches.
2. **Fork/vendor and adapt** if close but needs changes. Record why adaptation is needed.
3. **Build from scratch** if no suitable candidate exists. Read 1-2 similar plugin sources first for implementation patterns.

## Guardrails

- Do not trust abandoned plugins for production features.
- Never add a dependency without verifying its source, maintenance status, and license. Require human approval for paid/proprietary plugins.
- Prefer packages with tests and documented upgrade paths.
- If building from scratch, keep the API surface narrow and match Filament conventions (resource classes, form schemas, table columns, action classes).
- Record the plugin decision and alternatives considered in the PR description.

## Plugin Authoring

When a reusable plugin is justified, inspect the target Filament major version and two comparable plugins first. Keep the public API small, register components through Filament's plugin contract, publish only necessary config/assets, and test installation plus the primary integration path in a clean Laravel application.

## Verification

- `composer show <vendor/package>` confirms installation.
- `php artisan about` or `composer why <vendor/package>` confirms no conflicts.
- Feature tests cover the implemented behavior regardless of whether it came from a plugin or custom code.
