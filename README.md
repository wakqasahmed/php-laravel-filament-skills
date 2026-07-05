# PHP, Laravel, and Filament Skills

Reusable technical skills for PHP engineering, Laravel conventions, and Filament admin panel development.

## Skills

- `php-principles` — core PHP engineering principles: DRY, SOLID, typing, dependency hygiene.
- `laravel-conventions` — Laravel defaults for models, validation, config, queues, and controllers.
- `filament-plugin-first` — search the Filament plugin ecosystem before building custom components.
- `filament-conventions` — Filament patterns for resources, forms, tables, actions, widgets, and multi-tenancy.

## Install

```bash
npx skills@latest add wakqasahmed/php-laravel-filament-skills
```

## Scope

This pack is intentionally narrow: it covers the PHP → Laravel → Filament stack. General engineering workflow guidance belongs in `ai-engineering-workflow-skills`.

## Verification

Each skill names the minimum verification commands. Run the smallest relevant checks for the layer you changed:

- PHP logic: static analysis + unit tests
- Laravel changes: feature tests + `php artisan about`
- Filament changes: feature tests + render checks
