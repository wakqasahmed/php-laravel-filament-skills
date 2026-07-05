---
name: filament-conventions
description: Follow Filament conventions when building resources, forms, tables, actions, and widgets. Use when adding or changing Filament admin panels.
---

# Filament Conventions

Use this when building or changing Filament admin panel code.

## Resource Structure

- One resource per model, with a clear singular name.
- Keep form and table definitions in dedicated methods or classes.
- Use relation managers for related data, not custom inline tables.
- Prefer policies for authorization over inline gate checks.

## Forms

- Build forms with schema components, not raw HTML.
- Extract reusable field groups into custom components or form components.
- Validate with rules on fields; use Form Requests for complex cross-field validation.
- Keep form sections and tabs focused; group related fields.

## Tables

- Use built-in columns and filters before custom ones.
- Define actions, bulk actions, and filters declaratively.
- Keep table queries efficient; eager load and defer heavy columns.
- Use record URLs and actions consistently across resources.

## Actions and Widgets

- Implement custom actions as action classes, not inline closures.
- Keep widgets single-purpose and cache expensive data.
- Use action modals for confirmations and multi-step flows.

## Multi-Tenancy

- Centralize tenant scope in the panel provider or middleware.
- Apply tenant constraints at the query level, not scattered in resources.
- Keep tenant-aware resources explicit and test isolation carefully.

## Verification

- Run affected Pest/feature tests.
- Verify the panel renders without errors at `php artisan serve`.
- Check that authorization policies still enforce expected access.
